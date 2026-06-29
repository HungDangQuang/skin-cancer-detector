"""
Build a FIXED benchmark input set from the internal held-out test split.

One small, reproducible set of samples reused for ALL of:
  - PC latency benchmark (scripts/benchmark.py)   -> feed the same inputs
  - Android on-device latency benchmark           -> push the same inputs
  - PC<->mobile parity check                       -> compare logits on the same inputs

The proposal does not pin a dataset for the on-device benchmark; this uses the
internal test split (ISIC 2024 + PAD-UFES-20), i.e. the non-dermoscopic /
smartphone-like deployment domain — the most defensible choice for the thesis.

Preprocessing is produced by the project's own val/test path
(build_transforms(cfg, "val") + SkinLesionDataset), so it is byte-for-byte the
same as evaluation: Resize(image_size) -> Normalize(ImageNet, /255) -> CHW tensor.

Outputs (default data/benchmark_set/):
  images/<id>__<source>__y<label>.<ext>   original image (for the app to run its
                                          OWN preprocessing -> parity layer 2)
  inputs/<id>.bin                          fully-preprocessed float32, C-order,
                                          shape (3,H,W) NCHW-without-batch, RGB
                                          (feed directly -> parity layer 1)
  inputs.npy                               stacked (N,3,H,W) float32 (PC convenience)
  manifest.csv                             id,image_file,input_bin,label,source,src_path
  meta.json                                image_size, mean/std, dtype, layout, counts
  ref_<model>.csv                          (only with --model-name/--checkpoint)
                                          id,label,source,logit,prob  reference outputs

Usage (in the training venv, on the cluster):
    python scripts/make_benchmark_set.py --n 100
    # also dump reference logits for parity:
    python scripts/make_benchmark_set.py --n 100 \\
        --model-name efficientnet_b0 \\
        --checkpoint experiments/runs/kd_..._to_efficientnet_b0/fold_0/checkpoints/best_model.pth
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch

from src.data.dataset import SkinLesionDataset
from src.data.datamodule import source_from_path
from src.data.transforms import build_transforms
from src.models.registry import MODEL_REGISTRY, build_model_from_name
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ImageNet stats — the project's Normalize op (transforms.py). Recorded in
# meta.json so the Android app can replicate the exact preprocessing.
_MEAN = [0.485, 0.456, 0.406]
_STD = [0.229, 0.224, 0.225]


def _select_indices(labels, n, n_malignant, seed):
    """Deterministic, label-stratified pick: up to n_malignant positives, rest
    benign. Malignant is rare (~0.39%), so we oversample it relative to the test
    prevalence on purpose — parity wants inputs across the model's logit range."""
    labels = np.asarray(labels)
    rng = np.random.default_rng(seed)
    mal = np.where(labels == 1)[0]
    ben = np.where(labels == 0)[0]
    rng.shuffle(mal)
    rng.shuffle(ben)
    n_mal = min(n_malignant if n_malignant is not None else n // 2, len(mal))
    take_mal = mal[:n_mal]
    take_ben = ben[: max(0, n - len(take_mal))]
    sel = np.concatenate([take_mal, take_ben])
    rng.shuffle(sel)  # mix classes so order isn't all-positives-first
    return sel.tolist()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--test-csv", default=None,
                        help="Override test split CSV (default: <splits_dir>/test_split.csv)")
    parser.add_argument("--output-dir", default="data/benchmark_set")
    parser.add_argument("--n", type=int, default=100, help="Total samples")
    parser.add_argument("--n-malignant", type=int, default=None,
                        help="Positives to include (default n//2, capped at available)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Selection seed (default: cfg.seed)")
    # Optional: also dump per-model reference logits for the parity check.
    parser.add_argument("--model-name", default=None, choices=sorted(MODEL_REGISTRY.keys()))
    parser.add_argument("--checkpoint", default=None)
    args = parser.parse_args()

    if bool(args.model_name) != bool(args.checkpoint):
        parser.error("--model-name and --checkpoint must be given together (or neither).")

    cfg = load_config(args.config)
    seed = args.seed if args.seed is not None else int(cfg.seed)
    image_size = int(cfg.data.image_size)

    test_csv = Path(args.test_csv) if args.test_csv else Path(cfg.data.splits_dir) / "test_split.csv"
    if not test_csv.exists():
        raise SystemExit(
            f"Test split not found at {test_csv}. Run scripts/prepare_data.py "
            "(or slurm/10_prepare_data.slurm) first."
        )

    # Identical preprocessing to evaluation — same builder, same dataset class.
    val_transform = build_transforms(cfg, split="val")
    ds = SkinLesionDataset(test_csv, transform=val_transform)
    logger.info(f"Test split: {len(ds)} rows | malignant={ds.class_counts.get(1, 0)}")

    sel = _select_indices(ds.labels, args.n, args.n_malignant, seed)

    out = Path(args.output_dir)
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "inputs").mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    tensors = []
    for i, idx in enumerate(sel):
        tensor, label = ds[idx]  # tensor: float32 (3,H,W), already normalized
        src_path = str(ds.df.iloc[idx][ds.image_col])
        source = source_from_path(src_path)
        sample_id = f"{i:04d}"
        ext = Path(src_path).suffix or ".png"

        img_file = f"{sample_id}__{source}__y{label}{ext}"
        shutil.copy(src_path, out / "images" / img_file)

        arr = tensor.numpy().astype(np.float32)  # (3,H,W), C-contiguous
        bin_file = f"{sample_id}.bin"
        arr.tofile(out / "inputs" / bin_file)
        tensors.append(arr)

        manifest_rows.append({
            "id": sample_id, "image_file": img_file, "input_bin": bin_file,
            "label": int(label), "source": source, "src_path": src_path,
        })

    inputs = np.stack(tensors, axis=0)  # (N,3,H,W)
    np.save(out / "inputs.npy", inputs)

    import csv
    with open(out / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
        w.writeheader()
        w.writerows(manifest_rows)

    n_mal = sum(r["label"] == 1 for r in manifest_rows)
    src_counts = {}
    for r in manifest_rows:
        src_counts[r["source"]] = src_counts.get(r["source"], 0) + 1
    meta = {
        "count": len(manifest_rows),
        "n_malignant": n_mal,
        "n_benign": len(manifest_rows) - n_mal,
        "source_counts": src_counts,
        "seed": seed,
        "image_size": image_size,
        "channel_order": "RGB",
        "dtype": "float32",
        "input_shape": [3, image_size, image_size],
        "layout": "CHW (no batch dim); add leading 1 for (1,3,H,W) at inference",
        "normalization": "x/255 then (x-mean)/std",
        "mean": _MEAN,
        "std": _STD,
        "note": ("inputs/*.bin are FULLY preprocessed (already normalized) — feed "
                 "directly for parity layer 1. images/* are originals — preprocess "
                 "them in-app for parity layer 2."),
    }
    with open(out / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    logger.info(
        f"Wrote {len(manifest_rows)} samples ({n_mal} malignant) to {out} | "
        f"sources={src_counts}"
    )

    # ---- Optional: reference logits for the parity check ----
    if args.model_name:
        model, _ = build_model_from_name(args.model_name, cfg)
        load_checkpoint(args.checkpoint, model, device="cpu")
        model.eval()
        with torch.no_grad():
            logits = model(torch.from_numpy(inputs)).numpy().reshape(-1)
        probs = 1.0 / (1.0 + np.exp(-logits))
        ref_path = out / f"ref_{args.model_name}.csv"
        with open(ref_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "label", "source", "logit", "prob"])
            for r, lg, pr in zip(manifest_rows, logits, probs):
                w.writerow([r["id"], r["label"], r["source"],
                            f"{float(lg):.6f}", f"{float(pr):.6f}"])
        logger.info(f"Wrote reference logits for {args.model_name} -> {ref_path}")


if __name__ == "__main__":
    main()
