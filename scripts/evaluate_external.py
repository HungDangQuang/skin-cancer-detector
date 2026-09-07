#!/usr/bin/env python
"""
Evaluate trained checkpoints on the EXTERNAL, EVALUATION-ONLY datasets —
HAM10000 (cross-domain) and Fitzpatrick17k (fairness).

Deliberately separate from scripts/evaluate.py: that one reads the INTERNAL
5-fold layout through SkinLesionDataModule (train/val/test of ISIC+PAD). Here
there are no folds in the data — one held-out CSV per dataset — while there are
still 5 model folds, so the loop is inverted: one dataset split, evaluated by
each fold's checkpoint, aggregated to mean ± std the same way as the internal
runs.

THE DECISION THRESHOLD IS FROZEN, NOT REFIT. It is taken from the run's own
internal validation fold (Youden's J over ``val_predictions.csv``), because
picking a threshold on the external set would be selecting on the test data —
`configs/data/{ham10000,fitzpatrick17k}.yaml` list `threshold_selection` under
`do_not_use_for`. Ranking metrics (pAUC / AUC / AUPRC) are threshold-free and
unaffected; sensitivity / specificity / F1 are exactly the numbers a deployed
model would produce, which is the point of a cross-domain test.

Usage:
    python scripts/evaluate_external.py --dataset ham10000 \
        --run-dir experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium

    # several runs, every split variant, three folds:
    python scripts/evaluate_external.py --dataset fitzpatrick17k --variants all \
        --folds 0,1,2 --run-dir experiments/runs/baseline_fastvit_sa12 \
        --run-dir experiments/runs/kd_efficientnetv2_m_to_fastvit_sa12

Output (per run × variant):
    reports/external/<dataset>/<variant>/<run_tag>/fold_N/test_metrics.json
    reports/external/<dataset>/<variant>/<run_tag>/fold_N/predictions.csv
    reports/external/<dataset>/<variant>/<run_tag>/fold_N/subgroup_metrics.json
    reports/external/<dataset>/<variant>/<run_tag>/aggregated.{json,md}

Nothing is ever written inside experiments/runs/ — training run-dirs stay
byte-for-byte as the training job left them.

The output tree mirrors experiments/runs/ (teacher runs stay nested under
`teacher/`), so the existing cross-run comparison works on it as-is:

    python scripts/compare_kd_results.py --runs-dir reports/external/ham10000/headline

which answers "did KD help OUT of domain?" the same way it does in-domain.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))  # appended: reuse the fold aggregator
                                             # without letting scripts/ shadow imports

from aggregate_folds import aggregate, load_fold_metrics, write_markdown_summary  # noqa: E402

from src.data.dataset import SkinLesionDataset  # noqa: E402
from src.data.datamodule import source_from_path  # noqa: E402
from src.data.transforms import build_transforms  # noqa: E402
from src.evaluation.evaluator import Evaluator  # noqa: E402
from src.evaluation.metrics import compute_metrics, youden_threshold  # noqa: E402
from src.models.registry import build_model_from_name  # noqa: E402
from src.utils.checkpoint import load_checkpoint  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from src.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)

# Columns carried into predictions.csv (when present in the split CSV) so every
# breakdown below is recomputable offline without re-running inference.
EXTRA_COLS = {
    "ham10000": ["image_id", "dx", "lesion_id"],
    "fitzpatrick17k": ["image_id", "tone_group", "fitzpatrick_scale", "three_partition_label"],
}
# Columns the per-subgroup table is built over.
SUBGROUP_COLS = {
    "ham10000": ["dx"],                 # per-diagnosis recall (mel / bcc / akiec / ...)
    "fitzpatrick17k": ["tone_group"],   # the fairness axis
}


# ----------------------------------------------------------------------
# Model + threshold
# ----------------------------------------------------------------------

def resolve_model_name(run_dir: Path, cfg, override: str | None) -> str:
    """Which architecture the checkpoints in ``run_dir`` hold.

    The saved config carries both a `teacher` and a `student` block (it is the
    whole composed config), so the run-dir tells us which one was trained:
    `experiments/runs/teacher/<name>` is a teacher, everything else
    (`kd_<teacher>_to_<student>`, `baseline_<student>`) is a student. A wrong
    guess cannot pass silently — load_checkpoint's strict state_dict load fails.
    """
    if override:
        return override
    if run_dir.parent.name == "teacher":
        return str(cfg.teacher.name)
    return str(cfg.student.name)


def frozen_threshold(fold_dir: Path) -> tuple[float, str]:
    """Decision threshold from the run's own INTERNAL validation fold.

    Preference order — first the raw val predictions (recompute Youden's J
    exactly as training did), then the threshold recorded in val_metrics.json.
    The external set is never consulted; see this module's docstring.
    """
    val_preds = fold_dir / "val_predictions.csv"
    if val_preds.is_file():
        df = pd.read_csv(val_preds)
        if {"y_true", "y_prob"}.issubset(df.columns) and df["y_true"].nunique() > 1:
            thr = youden_threshold(df["y_true"].to_numpy(), df["y_prob"].to_numpy())
            return float(thr), "internal val_predictions.csv (Youden J)"

    val_metrics = fold_dir / "val_metrics.json"
    if val_metrics.is_file():
        recorded = json.loads(val_metrics.read_text()).get("threshold")
        if isinstance(recorded, (int, float)):
            return float(recorded), "internal val_metrics.json (recorded threshold)"

    raise FileNotFoundError(
        f"No internal validation threshold for {fold_dir}: neither val_predictions.csv "
        f"nor a 'threshold' in val_metrics.json. Refusing to fall back to a threshold "
        f"fitted on the external set — that would be selecting on the test data."
    )


# ----------------------------------------------------------------------
# Subgroup breakdown
# ----------------------------------------------------------------------

def _safe_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> dict:
    """compute_metrics, but degrading gracefully on a single-class subgroup.

    Fitzpatrick's dark-tone cells and HAM's rarer diagnoses can hold one class
    only, where AUC/pAUC/AUPRC are undefined. Those groups still carry the most
    interesting number (recall at the deployed threshold), so report it rather
    than dropping the row.
    """
    n_pos = int((y_true == 1).sum())
    n_neg = int((y_true == 0).sum())
    if n_pos and n_neg:
        m = compute_metrics(list(y_true), y_prob, threshold=threshold)
        m = {k: v for k, v in m.items() if not k.startswith("_")}
    else:
        y_pred = (y_prob >= threshold).astype(int)
        m = {
            "threshold": float(threshold),
            "prevalence": float(n_pos / max(n_pos + n_neg, 1)),
            "sensitivity": float((y_pred[y_true == 1] == 1).mean()) if n_pos else None,
            "specificity": float((y_pred[y_true == 0] == 0).mean()) if n_neg else None,
            "note": "single-class subgroup — ranking metrics (AUC/pAUC/AUPRC) undefined",
        }
    m["n"] = n_pos + n_neg
    m["n_malignant"] = n_pos
    m["n_benign"] = n_neg
    return m


def subgroup_breakdown(
    y_true: np.ndarray, y_prob: np.ndarray, frame: pd.DataFrame, cols: list[str], threshold: float
) -> dict:
    """{column: {group_value: metrics}} at the SAME frozen threshold as the headline."""
    out: dict = {}
    for col in cols:
        if col not in frame.columns:
            continue
        per_group: dict = {}
        series = frame[col].astype(str)
        for value in sorted(series.unique()):
            # positional row ids — y_true/y_prob come back in loader order, and
            # the loader iterates the frame top to bottom (shuffle=False).
            rows = np.flatnonzero((series == value).to_numpy())
            per_group[value] = _safe_metrics(y_true[rows], y_prob[rows], threshold)
        out[col] = per_group
    return out


# ----------------------------------------------------------------------
# Evaluation
# ----------------------------------------------------------------------

def build_loader(cfg, split_csv: Path, batch_size: int, num_workers: int) -> DataLoader:
    """Eval loader over an external split CSV, using the RUN's own val transform.

    Reading the transform from the checkpoint's saved config (not from the
    current configs/) keeps preprocessing identical to what the model was
    validated with — resize and normalization included.
    """
    dataset = SkinLesionDataset(split_csv=split_csv, transform=build_transforms(cfg, split="val"))
    # shuffle=False is load-bearing: sources / metadata / subgroup rows below are
    # matched to predictions by position.
    return DataLoader(
        dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True
    )


def evaluate_fold(
    run_dir: Path,
    fold: int,
    dataset_name: str,
    split_csv: Path,
    out_dir: Path,
    args,
) -> dict | None:
    """Evaluate one fold's checkpoint on one external split. Returns its metrics."""
    fold_dir = run_dir / f"fold_{fold}"
    ckpt = fold_dir / "checkpoints" / "best_model.pth"
    cfg_path = fold_dir / "config.yaml"
    if not ckpt.is_file() or not cfg_path.is_file():
        logger.warning(f"skipping {fold_dir}: missing best_model.pth or config.yaml")
        return None

    cfg = load_config(cfg_path)
    model_name = resolve_model_name(run_dir, cfg, args.model_name)
    model, model_cfg = build_model_from_name(model_name, cfg)
    if getattr(model, "accepts_metadata", False):
        raise ValueError(
            f"{model_name} is a privileged (LUPI) model that consumes tabular metadata, "
            f"which the external sets do not carry. Evaluate the image-only student instead."
        )

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    load_checkpoint(ckpt, model, device=device)
    threshold, threshold_source = frozen_threshold(fold_dir)

    loader = build_loader(model_cfg, split_csv, args.batch_size, args.num_workers)
    frame = loader.dataset.df
    extra = [c for c in EXTRA_COLS.get(dataset_name, []) if c in frame.columns]

    evaluator = Evaluator(model, device=device, threshold=threshold)
    metrics = evaluator.evaluate(
        loader,
        sources=[source_from_path(p) for p in frame["image_path"].astype(str)],
        metadata={c: frame[c].tolist() for c in extra} or None,
    )

    metrics["dataset"] = dataset_name
    metrics["split_csv"] = str(split_csv)
    metrics["run"] = str(run_dir)
    # string on purpose: a fold id is provenance, and the aggregator averages
    # every numeric field it finds (a "mean fold = 2.0" row helps nobody).
    metrics["fold"] = f"fold_{fold}"
    metrics["model_name"] = model_name
    metrics["n_samples"] = len(frame)
    metrics["threshold_source"] = threshold_source

    fold_out = out_dir / f"fold_{fold}"
    evaluator.save_metrics(metrics, fold_out / "test_metrics.json")
    evaluator.save_predictions(metrics, fold_out / "predictions.csv")

    y_true = np.asarray(metrics["_y_true"])
    y_prob = np.asarray(metrics["_y_prob"])
    breakdown = subgroup_breakdown(
        y_true, y_prob, frame, args.subgroup_cols or SUBGROUP_COLS.get(dataset_name, []), threshold
    )
    if breakdown:
        (fold_out / "subgroup_metrics.json").write_text(json.dumps(breakdown, indent=2))
    return metrics


def resolve_variants(cfg, requested: str) -> dict[str, str]:
    """{variant_key: split_csv_name} from the dataset config's `splits:` block."""
    available = {str(k): str(v) for k, v in cfg.get("splits", {}).items()}
    if not available:
        sys.exit("ERROR: the dataset config has no `splits:` block — re-run prepare_external.")
    if requested == "all":
        return available
    chosen = {}
    for key in [k.strip() for k in requested.split(",") if k.strip()]:
        if key not in available:
            sys.exit(f"ERROR: unknown variant '{key}'. Available: {sorted(available)}")
        chosen[key] = available[key]
    return chosen


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--dataset", required=True, choices=["ham10000", "fitzpatrick17k"])
    ap.add_argument("--run-dir", action="append", required=True, type=Path,
                    help="training run-dir holding fold_*/checkpoints/best_model.pth "
                         "(repeatable)")
    ap.add_argument("--folds", default="0,1,2,3,4", help="comma-separated fold ids")
    ap.add_argument("--variants", default="headline",
                    help="split variants from the dataset config's `splits:` block, "
                         "comma-separated, or 'all' (default: headline)")
    ap.add_argument("--config-dir", type=Path, default=Path("configs/data"))
    ap.add_argument("--out-root", type=Path, default=Path("reports/external"))
    ap.add_argument("--model-name", default=None,
                    help="override the architecture inferred from the run-dir")
    ap.add_argument("--subgroup-cols", default=None,
                    help="comma-separated columns for the per-subgroup table "
                         "(default: dx for HAM10000, tone_group for Fitzpatrick17k)")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--num-workers", type=int, default=8)
    ap.add_argument("--device", default=None, help="cuda | cpu (default: cuda when available)")
    args = ap.parse_args()

    args.subgroup_cols = (
        [c.strip() for c in args.subgroup_cols.split(",") if c.strip()]
        if args.subgroup_cols else None
    )
    folds = [int(f) for f in args.folds.split(",") if f.strip() != ""]

    ds_cfg = load_config(args.config_dir / f"{args.dataset}.yaml")
    splits_dir = Path(ds_cfg.splits_dir)
    variants = resolve_variants(ds_cfg, args.variants)

    runs_root = Path("experiments/runs")
    failures: list[str] = []
    for run_dir in args.run_dir:
        if not run_dir.is_dir():
            sys.exit(f"ERROR: run-dir not found: {run_dir}")
        try:
            # Keep the run-dir's own shape (`teacher/<name>` stays nested): that is
            # exactly the tree compare_kd_results.py knows how to parse, so the
            # KD-vs-baseline delta table works on the external results unmodified.
            run_tag = str(run_dir.resolve().relative_to(runs_root.resolve()))
        except ValueError:
            run_tag = run_dir.name

        for variant_key, csv_name in variants.items():
            split_csv = splits_dir / csv_name
            if not split_csv.is_file():
                sys.exit(
                    f"ERROR: split not found: {split_csv}\n"
                    f"       Run first: bash run/prepare_external.sh DATASET={args.dataset}"
                )
            out_dir = args.out_root / args.dataset / variant_key / run_tag
            logger.info(f"=== {run_tag} | {args.dataset}:{variant_key} | folds {folds} ===")
            for fold in folds:
                # One unusable fold (missing val threshold, arch mismatch, OOM)
                # must not take down a 90-fold sweep. Failures are collected and
                # reprinted at the end, and aggregated.json records which folds
                # actually contributed, so a short aggregate is never silent.
                try:
                    evaluate_fold(run_dir, fold, args.dataset, split_csv, out_dir, args)
                except Exception as e:
                    failures.append(f"{run_tag} | {variant_key} | fold_{fold}: "
                                    f"{type(e).__name__}: {e}")
                    logger.error(f"fold_{fold} of {run_tag} failed: {type(e).__name__}: {e}")

            per_fold = load_fold_metrics(out_dir)
            if not per_fold:
                logger.warning(f"no fold metrics produced under {out_dir}")
                continue
            agg = aggregate(per_fold)
            (out_dir / "aggregated.json").write_text(json.dumps(agg, indent=2))
            write_markdown_summary(agg, out_dir, out_dir / "aggregated.md")
            headline = agg["metrics"]
            logger.info(
                f"{run_tag} | {args.dataset}:{variant_key} | {agg['n_folds']} folds | "
                f"pAUC {headline['pauc_at_tpr80']['mean']:.4f}±{headline['pauc_at_tpr80']['std']:.4f} | "
                f"AUC {headline['auc_roc']['mean']:.4f}±{headline['auc_roc']['std']:.4f} | "
                f"AUPRC {headline['auprc']['mean']:.4f}±{headline['auprc']['std']:.4f} | "
                f"Sens {headline['sensitivity']['mean']:.4f}±{headline['sensitivity']['std']:.4f}"
            )
            print(f"Wrote {out_dir}/aggregated.md")

    if failures:
        print(f"\n{len(failures)} fold(s) did NOT produce metrics:")
        for f in failures:
            print(f"  - {f}")
        # Non-zero so a runner / caller notices a partial sweep instead of
        # reading the aggregates as if every fold had contributed.
        sys.exit(1)


if __name__ == "__main__":
    main()
