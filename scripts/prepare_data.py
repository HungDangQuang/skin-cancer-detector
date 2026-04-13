"""
Data preparation script.

Usage:
    python scripts/prepare_data.py

Downloads should be done manually:
  1. Go to https://www.kaggle.com/datasets/kmader/skin-lesion-analysis-toward-melanoma-detection
  2. Download and extract to data/raw/
  3. Run this script
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessing import generate_splits, process_ham10000
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__, log_file="experiments/prepare_data.log")


def main():
    cfg = load_config("configs/config.yaml")
    set_seed(cfg.seed)

    raw_dir = Path(cfg.data.raw_dir)
    processed_dir = Path(cfg.data.processed_dir)
    splits_dir = Path(cfg.data.splits_dir)
    metadata_csv = raw_dir / "HAM10000_metadata.csv"

    if not metadata_csv.exists():
        logger.error(
            f"Metadata CSV not found at {metadata_csv}.\n"
            "Please download HAM10000 dataset and place it in data/raw/."
        )
        sys.exit(1)

    logger.info("Processing HAM10000 images...")
    df = process_ham10000(
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        metadata_csv=metadata_csv,
        image_size=cfg.data.image_size,
    )
    logger.info(f"Processed {len(df)} images.")

    logger.info("Generating train/val/test splits...")
    generate_splits(
        df=df,
        splits_dir=splits_dir,
        train_ratio=cfg.data.split_ratios.train,
        val_ratio=cfg.data.split_ratios.val,
        seed=cfg.seed,
    )
    logger.info("Data preparation complete.")


if __name__ == "__main__":
    main()
