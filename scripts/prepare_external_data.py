#!/usr/bin/env python
"""
Prepare the EXTERNAL, EVALUATION-ONLY datasets — HAM10000 (cross-domain) and
Fitzpatrick17k (fairness). These are never trained on.

Deliberately separate from scripts/prepare_data.py: that script owns the
TRAINING path (ISIC 2024 + PAD-UFES-20 + StratifiedGroupKFold) and is left
untouched. There are no folds here — each dataset yields a single held-out test
CSV (plus sensitivity variants), written in the same schema the internal
test_split.csv uses, so SkinLesionDataset reads them unchanged.

Prereqs:
  HAM10000        data/raw/ham10000/HAM10000_metadata.csv + the image zips extracted
  Fitzpatrick17k  python scripts/download_fitzpatrick17k.py   (fetches the images)

Usage:
    python scripts/prepare_external_data.py --dataset ham10000
    python scripts/prepare_external_data.py --dataset fitzpatrick17k
    python scripts/prepare_external_data.py --dataset ham10000 --skip-md5-overlap

Output (per dataset):
    data/processed/<ds>/{benign,malignant}/*.jpg
    data/processed/<ds>/excluded_images.csv    <- tier 1, dropped (integrity)
    data/processed/<ds>/quality_flags.csv      <- tier 2, KEPT (uninformative/dup)
    data/splits/<ds>/test_split.csv            <- headline variant
    data/splits/<ds>/test_split_*.csv          <- sensitivity variants
    reports/external_overlap_check.md          <- leakage guard vs internal splits

Variants written:
    ham10000        test_split.csv           one image per lesion (headline)
                    test_split_full.csv      every image (appendix / literature)
                    test_split_no_akiec.csv  akiec dropped (label-convention check)
    fitzpatrick17k  test_split.csv           benign vs malignant only (headline)
                    test_split_with_nonneo.csv  non-neoplastic merged into benign

Exit code 2 = the overlap check found external images inside the internal
splits. Do NOT run the cross-domain evaluation in that case: an overlapping
image is data the model may have trained on, and the "generalization" number
would be inflated.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd
from PIL import Image
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessing import process_fitzpatrick17k, process_ham10000  # noqa: E402
from src.utils.config import load_config  # noqa: E402
from src.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__, log_file="experiments/prepare_external_data.log")

# Columns every split CSV must carry (SkinLesionDataset needs image_path+label;
# the rest ride along for per-domain / per-subgroup analysis of predictions.csv).
BASE_COLS = ["image_id", "patient_id", "image_path", "label", "class_name", "source"]


# ----------------------------------------------------------------------
# Leakage guard
# ----------------------------------------------------------------------

def _internal_split_csvs(splits_dir: Path) -> list[Path]:
    """Every internal split CSV (held-out test + all fold train/val files)."""
    return sorted(splits_dir.rglob("*_split.csv"))


def _column_as_set(csvs: list[Path], col: str) -> set[str]:
    values: set[str] = set()
    for csv_path in csvs:
        df = pd.read_csv(csv_path, usecols=lambda c: c == col)
        if col in df.columns:
            values.update(df[col].astype(str))
    return values


def _pixel_md5(image_path: str | Path) -> str | None:
    """md5 of the decoded RGB pixels of an already-processed 224x224 image."""
    try:
        with Image.open(image_path) as im:
            return hashlib.md5(im.convert("RGB").tobytes()).hexdigest()
    except (OSError, ValueError, Image.DecompressionBombError):
        return None


def check_overlap(
    external_df: pd.DataFrame,
    dataset: str,
    internal_splits_dir: Path,
    report_path: Path,
    do_md5: bool = True,
) -> int:
    """Verify no external image also lives in the internal ISIC/PAD splits.

    Two layers:
      1. **id layer** (HAM10000 only, and decisive): HAM10000 is distributed
         through the ISIC Archive and keeps ``ISIC_*`` ids, while ISIC 2024 is
         the separate SLICE-3D collection — so a plain id intersection settles
         it. Not meaningful for Fitzpatrick17k, whose ids are md5-derived.
      2. **pixel layer**: md5 over decoded pixels against the internal held-out
         TEST split only (the set the reported numbers come from). Catches the
         same picture republished under a different id.

    Returns the number of overlapping images and writes a markdown report.
    """
    internal_csvs = _internal_split_csvs(internal_splits_dir)
    lines = [
        f"# External-vs-internal overlap check — `{dataset}`",
        "",
        f"- internal splits scanned: `{internal_splits_dir}` ({len(internal_csvs)} CSV files)",
        f"- external images checked: {len(external_df)}",
        "",
    ]
    if not internal_csvs:
        lines += [
            "> ⚠️ No internal split CSVs found — the check could not run. Prepare the "
            "internal data first (`scripts/prepare_data.py`), then re-run this.",
            "",
        ]
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines))
        return 0

    id_overlap: set[str] = set()
    if dataset == "ham10000":
        internal_ids = _column_as_set(internal_csvs, "image_id")
        id_overlap = set(external_df["image_id"].astype(str)) & internal_ids
        lines += [
            "## Layer 1 — image_id intersection",
            "",
            f"- internal image_ids: {len(internal_ids)}",
            f"- **overlapping ids: {len(id_overlap)}**",
            "",
        ]
    else:
        lines += [
            "## Layer 1 — image_id intersection",
            "",
            "- skipped: this dataset's ids are md5-derived and share no namespace "
            "with the internal ISIC/PAD ids.",
            "",
        ]

    pixel_overlap: list[tuple[str, str]] = []
    if do_md5:
        test_csv = internal_splits_dir / "test_split.csv"
        if test_csv.is_file():
            internal_test = pd.read_csv(test_csv)
            internal_hashes: dict[str, str] = {}
            for _, r in tqdm(internal_test.iterrows(), total=len(internal_test),
                             desc="Hashing internal test split"):
                h = _pixel_md5(r["image_path"])
                if h is not None:
                    internal_hashes.setdefault(h, str(r.get("image_id", r["image_path"])))
            for _, r in tqdm(external_df.iterrows(), total=len(external_df),
                             desc="Hashing external images"):
                h = _pixel_md5(r["image_path"])
                if h is not None and h in internal_hashes:
                    pixel_overlap.append((str(r["image_id"]), internal_hashes[h]))
            lines += [
                "## Layer 2 — decoded-pixel md5 vs internal held-out test split",
                "",
                f"- internal test images hashed: {len(internal_hashes)}",
                f"- **overlapping images: {len(pixel_overlap)}**",
                "",
            ]
        else:
            lines += [
                "## Layer 2 — decoded-pixel md5",
                "",
                f"- skipped: `{test_csv}` not found.",
                "",
            ]
    else:
        lines += ["## Layer 2 — decoded-pixel md5", "", "- skipped (--skip-md5-overlap).", ""]

    total = len(id_overlap) + len(pixel_overlap)
    if total == 0:
        lines += ["## Verdict", "", "✅ **No overlap.** Safe to use as an external test set.", ""]
    else:
        lines += [
            "## Verdict",
            "",
            f"❌ **{total} overlapping image(s) found — STOP.** These images may have been "
            "trained on, so any cross-domain / fairness number computed over this set is "
            "inflated. Exclude them (or the whole dataset) before evaluating.",
            "",
            "### Offending ids",
            "",
        ]
        lines += [f"- id-match: `{i}`" for i in sorted(id_overlap)[:100]]
        lines += [f"- pixel-match: `{ext}` == internal `{internal}`"
                  for ext, internal in pixel_overlap[:100]]
        if total > 200:
            lines.append(f"- … ({total} total, first 100 of each layer shown)")
        lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines))
    return total


# ----------------------------------------------------------------------
# Split writing
# ----------------------------------------------------------------------

def _write_split(df: pd.DataFrame, path: Path, extra_cols: list[str]) -> None:
    cols = BASE_COLS + [c for c in extra_cols if c in df.columns]
    path.parent.mkdir(parents=True, exist_ok=True)
    df[cols].to_csv(path, index=False)


def _summarize(name: str, df: pd.DataFrame) -> str:
    n, mal = len(df), int((df["label"] == 1).sum())
    flagged = int((df.get("quality_flags", pd.Series([""] * n)).fillna("") != "").sum())
    return (f"  {name:<28} n={n:>6} | malignant={mal:>5} | "
            f"prevalence={mal / n if n else 0:.4f} | tier-2 flagged (kept)={flagged}")


def prepare_ham10000(cfg, args) -> pd.DataFrame:
    label_mapping = (
        {str(k): int(v) for k, v in cfg.label_mapping.items()}
        if "label_mapping" in cfg else None
    )
    df = process_ham10000(
        raw_dir=cfg.raw_dir,
        processed_dir=cfg.processed_dir,
        image_size=cfg.get("image_size", 224),
        label_mapping=label_mapping,
    )

    splits_dir = Path(cfg.splits_dir)
    extra = ["dx", "lesion_id", "is_lesion_representative", "quality_flags"]
    rep = df[df["is_lesion_representative"]]

    _write_split(rep, splits_dir / "test_split.csv", extra)
    _write_split(df, splits_dir / "test_split_full.csv", extra)
    _write_split(rep[rep["dx"] != "akiec"], splits_dir / "test_split_no_akiec.csv", extra)

    print("\nHAM10000 splits written:")
    print(_summarize("test_split.csv (headline)", rep))
    print(_summarize("test_split_full.csv", df))
    print(_summarize("test_split_no_akiec.csv", rep[rep["dx"] != "akiec"]))
    print("\n  per-dx counts (headline variant):")
    for dx, n in rep["dx"].value_counts().items():
        print(f"    {dx:<8} {n}")
    return df


def prepare_fitzpatrick17k(cfg, args) -> pd.DataFrame:
    label_mapping = (
        {str(k): int(v) for k, v in cfg.label_mapping.items()}
        if "label_mapping" in cfg else None
    )
    df = process_fitzpatrick17k(
        raw_dir=cfg.raw_dir,
        processed_dir=cfg.processed_dir,
        image_size=cfg.get("image_size", 224),
        tone_col=args.tone_col or cfg.get("tone_col", "fitzpatrick_scale"),
        label_mapping=label_mapping,
    )

    # Map the Fitzpatrick scale to the report's tone groups (config-driven, so the
    # grouping used in the fairness table is never hard-coded here).
    groups = {g: list(v) for g, v in cfg.get("skin_type_groups", {}).items()}
    scale_to_group = {int(s): g for g, vals in groups.items() for s in vals}
    df["tone_group"] = df["fitzpatrick_scale"].map(scale_to_group).fillna("unknown")

    splits_dir = Path(cfg.splits_dir)
    extra = ["fitzpatrick_scale", "tone_group", "three_partition_label", "quality_flags"]
    headline = df[df["three_partition_label"] != "non-neoplastic"]

    _write_split(headline, splits_dir / "test_split.csv", extra)
    _write_split(df, splits_dir / "test_split_with_nonneo.csv", extra)

    print("\nFitzpatrick17k splits written:")
    print(_summarize("test_split.csv (headline)", headline))
    print(_summarize("test_split_with_nonneo.csv", df))
    print("\n  tone_group x label (headline variant) — check the dark group has enough")
    print("  malignant cases BEFORE evaluating; a near-empty cell means the fairness")
    print("  gap for that group is not measurable, only quotable with a wide CI:")
    print(pd.crosstab(headline["tone_group"], headline["label"]).to_string())
    return df


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--dataset", required=True, choices=["ham10000", "fitzpatrick17k"])
    ap.add_argument("--config-dir", type=Path, default=Path("configs/data"))
    ap.add_argument("--internal-splits-dir", type=Path, default=None,
                    help="internal split dir for the leakage guard "
                         "(default: read splits_dir from configs/data/isic2024.yaml)")
    ap.add_argument("--tone-col", default=None,
                    help="Fitzpatrick17k skin-tone column to group by; overrides the "
                         "config's tone_col (some releases also ship 'fitzpatrick_centaur')")
    ap.add_argument("--skip-md5-overlap", action="store_true",
                    help="skip the pixel-level overlap layer (faster; keeps the id layer)")
    ap.add_argument("--overlap-report", type=Path, default=None,
                    help="default: reports/external_overlap_check_<dataset>.md")
    args = ap.parse_args()

    cfg = load_config(args.config_dir / f"{args.dataset}.yaml")
    for key in ("raw_dir", "processed_dir", "splits_dir"):
        if key not in cfg:
            sys.exit(f"ERROR: configs/data/{args.dataset}.yaml is missing '{key}'.")
    if not Path(cfg.raw_dir).exists():
        sys.exit(f"ERROR: raw dir not found: {cfg.raw_dir} — see this script's docstring.")

    logger.info(f"Preparing external evaluation dataset: {args.dataset}")
    if args.dataset == "ham10000":
        df = prepare_ham10000(cfg, args)
    else:
        df = prepare_fitzpatrick17k(cfg, args)

    internal_splits_dir = args.internal_splits_dir or Path(
        load_config(args.config_dir / "isic2024.yaml").splits_dir
    )
    report_path = args.overlap_report or Path(
        f"reports/external_overlap_check_{args.dataset}.md"
    )
    n_overlap = check_overlap(
        external_df=df,
        dataset=args.dataset,
        internal_splits_dir=Path(internal_splits_dir),
        report_path=report_path,
        do_md5=not args.skip_md5_overlap,
    )
    print(f"\nOverlap report: {report_path}")
    if n_overlap:
        sys.exit(
            f"ERROR: {n_overlap} external image(s) overlap the internal splits — "
            f"see {report_path}. Do not evaluate until this is resolved."
        )
    print("Overlap check clean. External test set ready.")


if __name__ == "__main__":
    main()
