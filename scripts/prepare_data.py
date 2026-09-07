"""
Data preparation script — ISIC 2024 + PAD-UFES-20.

Steps before running:
  1. Download ISIC 2024 from Kaggle:
       https://www.kaggle.com/competitions/isic-2024-challenge/data
     Extract to: data/raw/isic2024/
       data/raw/isic2024/train-image.hdf5
       data/raw/isic2024/train-metadata.csv

  2. (Optional) Download PAD-UFES-20 for extra malignant samples:
       https://data.mendeley.com/datasets/zr7vgbcyr2/1
     Stage it with the helper (extracts the nested imgs_part_*.zip and
     arranges the layout below automatically):
       bash scripts/setup_pad_ufes_20.sh <zr7vgbcyr2-1.zip>
     Resulting layout (what process_pad_ufes_20 reads):
       data/raw/pad_ufes_20/images/        <- <img_id>.png
       data/raw/pad_ufes_20/metadata.csv   <- cols: img_id, diagnostic
     If this dir is absent, prepare runs ISIC-only. Adding it regenerates
     ALL fold/test splits, so any prior checkpoints must be retrained.

  3. Run:
       python scripts/prepare_data.py

Output:
  data/processed/isic2024/{benign,malignant}/*.jpg
  data/processed/pad_ufes_20/{benign,malignant}/*.jpg
  data/splits/isic2024/fold_0/train_split.csv
  data/splits/isic2024/fold_0/val_split.csv
  ... (5 folds)
  data/splits/isic2024/test_split.csv   <- held-out, never changed
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessing import (
    generate_group_kfold_splits,
    process_isic2024,
    process_pad_ufes_20,
)
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__, log_file="experiments/prepare_data.log")


def main():
    parser = argparse.ArgumentParser(description="Preprocess ISIC 2024 + PAD-UFES-20 and build CV splits.")
    parser.add_argument(
        "--metadata-cols", default=None,
        help="Comma-separated metadata columns to carry into the split CSVs "
             "(overrides data.metadata_cols). E.g. for the privileged teacher: "
             "'tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color'. Forbidden: "
             "iddx_*/mel_* (leakage — process_isic2024 raises).",
    )
    args = parser.parse_args()

    cfg = load_config("configs/config.yaml")
    set_seed(cfg.seed)

    # CLI override for metadata_cols (the key already exists in isic2024.yaml, so
    # this assignment is allowed even in Hydra struct mode).
    if args.metadata_cols:
        cfg.data.metadata_cols = [c.strip() for c in args.metadata_cols.split(",") if c.strip()]

    isic_raw = Path(cfg.data.raw_dir)
    isic_processed = Path(cfg.data.processed_dir)
    splits_dir = Path(cfg.data.splits_dir)

    # --- ISIC 2024 ---
    if not isic_raw.exists():
        logger.error(f"ISIC 2024 raw dir not found: {isic_raw}")
        sys.exit(1)

    # Optional extra metadata columns to carry into the split CSVs (privileged
    # teacher / subgroup calibration). null (default) keeps the 6-column schema
    # so existing image-only runs are byte-for-byte unchanged.
    metadata_cols = cfg.data.get("metadata_cols", None)
    metadata_cols = list(metadata_cols) if metadata_cols else None
    if metadata_cols:
        logger.info(f"Keeping metadata columns in splits: {metadata_cols}")

    logger.info("Processing ISIC 2024 (HDF5)...")
    df_isic = process_isic2024(
        raw_dir=isic_raw,
        processed_dir=isic_processed,
        image_size=cfg.data.image_size,
        image_id_col=cfg.data.image_id_col,
        label_col=cfg.data.label_col,
        metadata_cols=metadata_cols,
    )

    # --- PAD-UFES-20 (optional — augment malignant class) ---
    pad_raw = Path("data/raw/pad_ufes_20")
    if pad_raw.exists():
        logger.info("Processing PAD-UFES-20...")
        df_pad = process_pad_ufes_20(
            raw_dir=pad_raw,
            processed_dir=Path("data/processed/pad_ufes_20"),
            image_size=cfg.data.image_size,
            metadata_cols=metadata_cols,
        )
        df_combined = pd.concat([df_isic, df_pad], ignore_index=True)
        logger.info(f"Combined dataset: {len(df_combined)} images")
    else:
        logger.warning("PAD-UFES-20 not found — using ISIC 2024 only.")
        df_combined = df_isic

    # --- StratifiedGroupKFold splits ---
    logger.info("Generating StratifiedGroupKFold splits (patient-level)...")
    # NB: cfg.data.label_col is the column name in the RAW ISIC metadata
    # ("target"), used by process_isic2024 above. The processed df returned
    # from process_isic2024 stores the same value under the column "label",
    # which is what SkinLesionDataset and the rest of the pipeline expect —
    # so pass that name here, not cfg.data.label_col.
    generate_group_kfold_splits(
        df=df_combined,
        splits_dir=splits_dir,
        n_splits=cfg.data.get("num_folds", 5),
        group_col=cfg.data.get("group_col", "patient_id"),
        label_col="label",
        seed=cfg.seed,
        test_holdout_splits=cfg.data.get("test_holdout_splits", 6),
    )
    logger.info("Data preparation complete.")


if __name__ == "__main__":
    main()
