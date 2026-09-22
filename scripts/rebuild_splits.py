"""
Rebuild data/splits/ from the ALREADY-PROCESSED images, without re-running the
image pipeline.

WHY THIS EXISTS (incident 2026-09-22)
-------------------------------------
`data/splits/` was lost on the training box while `data/processed/` survived —
but `data/raw/isic2024/train-image.hdf5` and `data/raw/pad_ufes_20/` were gone
too, so `scripts/prepare_data.py` could not be re-run:

  * `process_isic2024` raises if the HDF5 is missing;
  * `process_pad_ufes_20` is skipped entirely when `data/raw/pad_ufes_20/` does
    not exist — which silently re-partitions the folds over an ISIC-only
    population, so the new `test_split.csv` is no longer the test set the
    existing checkpoints were scored on. That breaks every paired comparison in
    the 140 fold-run matrix.

It is also **destructive to attempt**: both processing functions carry a
`dst.exists()` fast-path that re-runs the quality filter and `unlink()`s any
image that now trips `is_uninformative`/duplicate. With the HDF5 gone, a deleted
processed image is gone for good.

WHAT THIS DOES INSTEAD
----------------------
The set of images that made it into the original dataframe is exactly the set
that was written to `data/processed/`. So the dataframe can be reconstructed
without decoding a single pixel:

  for each row of the ORIGINAL metadata CSV, in its ORIGINAL order:
      include it iff its processed .jpg exists on disk

That reproduces `df_combined` — same rows, same order, same `patient_id`
grouping — and `generate_group_kfold_splits` is deterministic given that
dataframe plus `cfg.seed`. Row order matters: the splitter runs
`StratifiedGroupKFold(shuffle=True, random_state=seed)` and then indexes with
`df.iloc[...]`.

This script NEVER opens, writes or deletes an image. It only calls `Path.exists()`.

USAGE
-----
    # 1. verify the reconstruction WITHOUT writing anything
    python scripts/rebuild_splits.py --dry-run

    # 2. write data/splits/ once the counts match the expected anchor
    python scripts/rebuild_splits.py

The default anchor comes from the surviving `predictions.csv` of the existing
runs (any fold of any run-dir — they all share one test set):
62,040 test rows | 241 positives | isic2024 61,663 + pad_ufes_20 377.
A mismatch means the reconstruction is NOT the original split — the script exits
non-zero and writes nothing.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from src.data.preprocessing import generate_group_kfold_splits
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__)

# Must mirror process_pad_ufes_20's mapping exactly.
PAD_LABEL_MAP = {"BCC": 1, "SCC": 1, "MEL": 1, "ACK": 0, "NEV": 0, "SEK": 0}
CLASS_NAMES = {0: "benign", 1: "malignant"}


def build_isic_df(raw_dir: Path, processed_dir: Path, image_id_col: str, label_col: str) -> pd.DataFrame:
    """Replay process_isic2024's record construction from disk (no image IO)."""
    metadata_csv = raw_dir / "train-metadata.csv"
    if not metadata_csv.exists():
        raise FileNotFoundError(
            f"ISIC metadata not found: {metadata_csv}. This file is required — it "
            f"defines both the row ORDER and the patient_id grouping."
        )
    metadata = pd.read_csv(metadata_csv, low_memory=False)

    records, missing = [], 0
    for _, row in metadata.iterrows():
        image_id = row[image_id_col]
        label = int(row[label_col])
        class_name = CLASS_NAMES[label]
        dst = processed_dir / class_name / f"{image_id}.jpg"
        if not dst.exists():
            # Excluded by the original quality filter (corrupt/too small/
            # uninformative/duplicate) — it was never written, so it was never
            # in the dataframe either.
            missing += 1
            continue
        records.append(
            {
                "image_id": image_id,
                "patient_id": str(row.get("patient_id", image_id)),
                "image_path": str(dst),
                "label": label,
                "class_name": class_name,
                "source": "isic2024",
            }
        )

    df = pd.DataFrame(records)
    logger.info(
        f"ISIC 2024 — metadata rows: {len(metadata)} | on disk: {len(df)} "
        f"(benign {(df['label']==0).sum()}, malignant {(df['label']==1).sum()}) | "
        f"not on disk (originally excluded): {missing}"
    )
    return df


def build_pad_df(raw_dir: Path, processed_dir: Path) -> pd.DataFrame:
    """Replay process_pad_ufes_20's record construction from disk (no image IO)."""
    metadata_csv = raw_dir / "metadata.csv"
    if not metadata_csv.exists():
        raise FileNotFoundError(
            f"PAD metadata not found: {metadata_csv}. Recover it with:\n"
            f"  curl -L -K .kaggle/curlrc "
            f"'https://www.kaggle.com/api/v1/datasets/download/mahdavi1202/skin-cancer/metadata.csv' "
            f"-o {metadata_csv}\n"
            f"The IMAGES are not needed — only this CSV, which carries patient_id."
        )
    metadata = pd.read_csv(metadata_csv)

    records, missing = [], 0
    for _, row in metadata.iterrows():
        diagnostic = str(row["diagnostic"]).upper()
        label = PAD_LABEL_MAP.get(diagnostic)
        if label is None:
            continue
        stem = Path(str(row["img_id"])).stem
        class_name = CLASS_NAMES[label]
        dst = processed_dir / class_name / f"pad_{stem}.jpg"
        if not dst.exists():
            missing += 1
            continue
        records.append(
            {
                "image_id": f"pad_{stem}",
                # Namespaced exactly as process_pad_ufes_20 does — an un-namespaced
                # PAD patient_id could collide with an ISIC one and leak across folds.
                "patient_id": f"pad_{row.get('patient_id', stem)}",
                "image_path": str(dst),
                "label": label,
                "class_name": class_name,
                "source": "pad_ufes_20",
            }
        )

    df = pd.DataFrame(records)
    logger.info(
        f"PAD-UFES-20 — metadata rows: {len(metadata)} | on disk: {len(df)} "
        f"(benign {(df['label']==0).sum()}, malignant {(df['label']==1).sum()}) | "
        f"not on disk (originally excluded): {missing}"
    )
    return df


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="verify only; write nothing")
    p.add_argument("--expect-test-rows", type=int, default=62040)
    p.add_argument("--expect-test-pos", type=int, default=241)
    p.add_argument("--expect-test-isic", type=int, default=61663)
    p.add_argument("--expect-test-pad", type=int, default=377)
    p.add_argument(
        "--no-verify",
        action="store_true",
        help="skip the anchor check (ONLY if you have no surviving predictions.csv to anchor against)",
    )
    args = p.parse_args()

    cfg = load_config("configs/config.yaml")
    set_seed(cfg.seed)

    isic_raw = Path(cfg.data.raw_dir)
    isic_processed = Path(cfg.data.processed_dir)
    splits_dir = Path(cfg.data.splits_dir)

    df_isic = build_isic_df(isic_raw, isic_processed, cfg.data.image_id_col, cfg.data.label_col)

    pad_processed = Path("data/processed/pad_ufes_20")
    pad_raw = Path("data/raw/pad_ufes_20")
    if not pad_processed.exists():
        logger.error(
            "data/processed/pad_ufes_20 is missing. The original splits DID include "
            "PAD (377 of the 62,040 test rows). Rebuilding without it would produce a "
            "different population and silently invalidate every existing run. Refusing."
        )
        sys.exit(1)
    df_pad = build_pad_df(pad_raw, pad_processed)

    # Concat order must match prepare_data.py: ISIC first, then PAD.
    df_combined = pd.concat([df_isic, df_pad], ignore_index=True)
    logger.info(f"Combined: {len(df_combined)} images | patients: {df_combined['patient_id'].nunique()}")

    # --- Verify against the anchor BEFORE writing anything ---------------
    # generate_group_kfold_splits writes as it goes, so the test split is
    # recomputed here first, in memory, and compared to the known-good numbers.
    from sklearn.model_selection import StratifiedGroupKFold

    holdout = StratifiedGroupKFold(
        n_splits=cfg.data.get("test_holdout_splits", 6), shuffle=True, random_state=cfg.seed
    )
    _, test_idx = next(
        holdout.split(df_combined, df_combined["label"].values, df_combined["patient_id"].values)
    )
    test_preview = df_combined.iloc[test_idx]
    by_source = test_preview["source"].value_counts().to_dict()
    n_rows, n_pos = len(test_preview), int((test_preview["label"] == 1).sum())

    logger.info(
        f"RECONSTRUCTED test split — rows: {n_rows} | positives: {n_pos} | by source: {by_source}"
    )

    if not args.no_verify:
        expected = {
            "rows": args.expect_test_rows,
            "positives": args.expect_test_pos,
            "isic2024": args.expect_test_isic,
            "pad_ufes_20": args.expect_test_pad,
        }
        actual = {
            "rows": n_rows,
            "positives": n_pos,
            "isic2024": by_source.get("isic2024", 0),
            "pad_ufes_20": by_source.get("pad_ufes_20", 0),
        }
        if actual != expected:
            logger.error("ANCHOR MISMATCH — the reconstruction is NOT the original split.")
            for k in expected:
                mark = "ok" if actual[k] == expected[k] else "MISMATCH"
                logger.error(f"  {k:12s} expected {expected[k]:>7} | got {actual[k]:>7}  [{mark}]")
            logger.error(
                "Nothing was written. Do NOT train on a mismatched split: every metric "
                "would be incomparable with the existing runs. Investigate first."
            )
            sys.exit(2)
        logger.info("Anchor check PASSED — reconstruction matches the original test set exactly.")

    if args.dry_run:
        logger.info("--dry-run: verified only, no files written.")
        return

    logger.info(f"Writing splits to {splits_dir} ...")
    generate_group_kfold_splits(
        df=df_combined,
        splits_dir=splits_dir,
        n_splits=cfg.data.get("num_folds", 5),
        group_col=cfg.data.get("group_col", "patient_id"),
        label_col="label",
        seed=cfg.seed,
        test_holdout_splits=cfg.data.get("test_holdout_splits", 6),
    )
    logger.info("Splits rebuilt.")


if __name__ == "__main__":
    main()
