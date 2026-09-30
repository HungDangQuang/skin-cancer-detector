#!/usr/bin/env python
"""
Build the mobile-evaluation bundle: one zip holding every image to be scored on
the phone, plus the manifest that fixes the scoring order.

Contract: docs/MOBILE_EVAL_PIPELINE.md. The manifest's row order IS the scoring
order — the concatenation of each dataset's test_split.csv in FILE order, with
no shuffling, no class balancing and no subsampling. This is deliberately
different from scripts/make_benchmark_set.py, which draws a small balanced
sample for latency/parity work and whose ids are therefore not stable between
calls (docs/GOTCHAS.md).

Images are copied byte-for-byte out of data/processed/; they are already
224x224 (resized at prepare time with Image.LANCZOS), so nothing is re-encoded
and no resampling happens here.

Optionally also writes l1_gate/: pre-normalised float32 tensors for the first
--gate-n manifest rows, used to separate "the export is wrong" from "the app's
decoding is wrong" (pipeline spec section 5).

Usage:
    # every dataset the thesis reports, headline variants:
    python scripts/make_mobile_eval_bundle.py \
        --dataset indomain --dataset ham10000 --dataset fitzpatrick17k \
        --output-dir data/mobile_eval_bundle

    # add the Fitzpatrick framing variants and a 100-row parity gate:
    python scripts/make_mobile_eval_bundle.py \
        --dataset indomain --dataset ham10000 \
        --dataset fitzpatrick17k:headline --dataset fitzpatrick17k:crop70 \
        --gate-n 100 --zip

Output (default data/mobile_eval_bundle/, plus <dir>.zip with --zip):
    manifest.csv   sample_id,dataset,image_file,image_id,label,source
    meta.json      preprocessing constants + per-dataset row counts
    images/<sample_id>.jpg
    l1_gate/inputs/<sample_id>.bin      (only with --gate-n)
    SHA256SUMS
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd

from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# The project's Normalize op (src/data/transforms.py). Recorded in meta.json so
# the phone replicates the exact arithmetic instead of guessing.
_MEAN = [0.485, 0.456, 0.406]
_STD = [0.229, 0.224, 0.225]
_IMAGE_SIZE = 224

# "indomain" is not an external dataset: its split lives under the root config's
# data.splits_dir, not under configs/data/<ds>.yaml.
_INDOMAIN = "indomain"


def parse_dataset_arg(spec: str) -> tuple[str, str | None]:
    """'fitzpatrick17k:crop70' -> ('fitzpatrick17k', 'crop70'); 'ham10000' -> (.., None)."""
    if ":" in spec:
        name, variant = spec.split(":", 1)
        return name, variant
    return spec, None


def resolve_split_csv(
    name: str, variant: str | None, root_cfg, config_dir: Path
) -> tuple[Path, str]:
    """Return (test_split.csv path, dataset key used in the manifest)."""
    if name == _INDOMAIN:
        if variant:
            raise SystemExit(f"'{_INDOMAIN}' has no variants (got '{variant}')")
        return Path(root_cfg.data.splits_dir) / "test_split.csv", _INDOMAIN

    ds_cfg = load_config(config_dir / f"{name}.yaml")
    splits_dir = Path(ds_cfg.splits_dir)
    # prepare_external_data.py writes the headline split as test_split.csv and
    # each variant as test_split_<variant>.csv.
    if variant in (None, "headline"):
        return splits_dir / "test_split.csv", f"{name}_headline"
    return splits_dir / f"test_split_{variant}.csv", f"{name}_{variant}"


def load_rows(split_csv: Path) -> pd.DataFrame:
    if not split_csv.is_file():
        raise SystemExit(
            f"ERROR: split CSV not found: {split_csv}\n"
            "External splits are produced by run/prepare_external.sh and live on "
            "the server; this script must run there, not on the Mac."
        )
    df = pd.read_csv(split_csv)
    for col in ("image_path", "label"):
        if col not in df.columns:
            raise SystemExit(f"ERROR: {split_csv} has no '{col}' column (got {list(df.columns)})")
    return df


def normalise_to_tensor(path: Path) -> np.ndarray:
    """Steps 2-6 of the pipeline spec, host side. Returns (3,H,W) float32."""
    from PIL import Image

    img = Image.open(path).convert("RGB")
    if img.size != (_IMAGE_SIZE, _IMAGE_SIZE):
        raise ValueError(f"{path} is {img.size}, expected ({_IMAGE_SIZE}, {_IMAGE_SIZE})")
    arr = np.asarray(img, dtype=np.float32) / 255.0  # HWC in [0,1]
    arr = (arr - np.asarray(_MEAN, dtype=np.float32)) / np.asarray(_STD, dtype=np.float32)
    return np.ascontiguousarray(arr.transpose(2, 0, 1))  # CHW


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--dataset",
        action="append",
        required=True,
        metavar="NAME[:VARIANT]",
        help=f"repeatable. '{_INDOMAIN}', 'ham10000', 'fitzpatrick17k[:crop70|crop50|...]'",
    )
    ap.add_argument("--config", default="configs/config.yaml")
    ap.add_argument("--config-dir", type=Path, default=Path("configs/data"))
    ap.add_argument("--output-dir", type=Path, default=Path("data/mobile_eval_bundle"))
    ap.add_argument(
        "--gate-n",
        type=int,
        default=0,
        help="also dump this many pre-normalised .bin tensors for the parity gate (0 = none)",
    )
    ap.add_argument("--zip", action="store_true", help="also write <output-dir>.zip")
    ap.add_argument(
        "--limit-per-dataset",
        type=int,
        default=None,
        help="TESTING ONLY: keep the first N rows per dataset. A bundle built with "
        "this flag is NOT comparable to a full-set server run.",
    )
    args = ap.parse_args()

    root_cfg = load_config(args.config)
    out = args.output_dir
    img_dir = out / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    counts: dict[str, dict] = {}
    missing: list[str] = []
    sample_idx = 0

    for spec in args.dataset:
        name, variant = parse_dataset_arg(spec)
        split_csv, key = resolve_split_csv(name, variant, root_cfg, args.config_dir)
        df = load_rows(split_csv)
        if args.limit_per_dataset is not None:
            df = df.head(args.limit_per_dataset)

        logger.info(f"{key}: {len(df)} rows from {split_csv}")
        n_pos = 0
        n_rows = 0
        for _, row in df.iterrows():
            src = Path(row["image_path"])
            sample_id = f"{sample_idx:06d}"
            dst = img_dir / f"{sample_id}{src.suffix or '.jpg'}"
            if not src.is_file():
                missing.append(str(src))
                continue
            shutil.copy2(src, dst)  # byte-for-byte; never re-encode
            label = int(row["label"])
            n_pos += label
            manifest.append(
                {
                    "sample_id": sample_id,
                    "dataset": key,
                    "image_file": f"images/{dst.name}",
                    "image_id": row.get("image_id", src.stem),
                    "label": label,
                    "source": row.get("source", key),
                }
            )
            sample_idx += 1
            n_rows += 1
        if key in counts:
            raise SystemExit(f"ERROR: dataset '{key}' passed twice — manifest keys must be unique.")
        counts[key] = {
            "split_csv": str(split_csv),
            "n": n_rows,
            "n_positive": n_pos,
        }

    if missing:
        raise SystemExit(
            f"ERROR: {len(missing)} image(s) listed in a split CSV are not on disk, "
            f"first few: {missing[:3]}. Refusing to write a bundle whose rows do not "
            "match the split the server scores."
        )
    if not manifest:
        raise SystemExit("ERROR: no rows selected.")

    # ---- manifest ----
    fields = ["sample_id", "dataset", "image_file", "image_id", "label", "source"]
    with open(out / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(manifest)

    # ---- optional parity gate ----
    if args.gate_n > 0:
        gate_dir = out / "l1_gate" / "inputs"
        gate_dir.mkdir(parents=True, exist_ok=True)
        for rec in manifest[: args.gate_n]:
            tensor = normalise_to_tensor(out / rec["image_file"])
            tensor.astype(np.float32).tofile(gate_dir / f"{rec['sample_id']}.bin")
        logger.info(f"l1_gate: {min(args.gate_n, len(manifest))} pre-normalised tensors")

    # ---- meta ----
    meta = {
        "bundle_version": 1,
        "spec": "docs/MOBILE_EVAL_PIPELINE.md",
        "n_total": len(manifest),
        "datasets": counts,
        "image_size": _IMAGE_SIZE,
        "channel_order": "RGB",
        "dtype": "float32",
        "input_shape": [3, _IMAGE_SIZE, _IMAGE_SIZE],
        "batch_size": 1,
        "layout": "CHW (no batch dim); add leading 1 for (1,3,H,W) at inference",
        "normalization": "x/255 then (x-mean)/std",
        "mean": _MEAN,
        "std": _STD,
        "resize": "NONE — images are already 224x224; assert and error, do not scale",
        "note": (
            "images/* are the bytes to score (pipeline steps 1-8). l1_gate/inputs/* "
            "are already normalised — feed them straight to the model (steps 7-8) to "
            "isolate the runtime from the JPEG decoder."
        ),
        "limit_per_dataset": args.limit_per_dataset,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2))

    # ---- checksums ----
    with open(out / "SHA256SUMS", "w") as f:
        for p in sorted(out.rglob("*")):
            if p.is_file() and p.name != "SHA256SUMS":
                h = hashlib.sha256(p.read_bytes()).hexdigest()
                f.write(f"{h}  {p.relative_to(out)}\n")

    logger.info(f"Bundle: {len(manifest)} images -> {out}")
    for k, v in counts.items():
        logger.info(f"  {k:34s} n={v['n']:6d}  positives={v['n_positive']:5d}")

    if args.zip:
        zip_path = out.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=1) as z:
            for p in sorted(out.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(out.parent))
        logger.info(f"Zip: {zip_path} ({zip_path.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
