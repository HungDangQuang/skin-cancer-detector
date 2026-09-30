"""
Add DDI (Diverse Dermatology Images, Stanford) to the TRAIN side of the existing
splits — without touching `test_split.csv`, any `val_split.csv`, or the processed
ISIC/PAD trees.

WHY IT WORKS THIS WAY
---------------------
`scripts/prepare_data.py` cannot be re-run on this box: `data/raw/isic2024/train-image.hdf5`
and `data/raw/pad_ufes_20/` are gone, and both `process_isic2024` and
`process_pad_ufes_20` carry a `dst.exists()` fast-path that `unlink()`s any
processed image that now trips the quality filter — with the raw bytes gone, that
loss is permanent (CLAUDE.md, "Never 'fix' a missing split by re-running prepare").
Re-partitioning would also invalidate the 30 fold-run arm already trained on the
current splits.

So this script does the narrow thing instead:

  1. process DDI into its OWN tree, `data/processed/ddi/{benign,malignant}/*.jpg`
     (nothing else is read or written, so nothing existing can be destroyed);
  2. APPEND those rows to each `fold_*/train_split.csv`.

`test_split.csv` and every `val_split.csv` are left byte-for-byte identical. That
is the point: the already-trained `runs_newsplit_light` arm stays a valid paired
control, so measuring "does DDI help?" costs 15 fold-run, not 30.

CONSEQUENCE, STATED PLAINLY: DDI is therefore never scored on. Its contribution
is measured indirectly — on the unchanged in-domain test set and on the external
Fitzpatrick17k tone groups. If DDI is ever wanted IN the evaluation pool, this
script is the wrong tool: that needs a full split regeneration (and a retrained
control), plus a patient grouping DDI does not ship (see `process_ddi`).

Usage:
    python scripts/prepare_ddi.py --dry-run      # report, write nothing
    python scripts/prepare_ddi.py                # process + append
    python scripts/prepare_ddi.py --force        # re-append after a partial run
"""
import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.preprocessing import process_ddi
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__, log_file="experiments/prepare_ddi.log")

SPLIT_COLS = ["image_id", "patient_id", "image_path", "label", "class_name", "source"]


def main() -> None:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--raw-dir", type=Path, default=Path("data/raw/DDI"))
    p.add_argument("--processed-dir", type=Path, default=Path("data/processed/ddi"))
    p.add_argument("--dry-run", action="store_true", help="report only; write no CSV")
    p.add_argument(
        "--force",
        action="store_true",
        help="append even if DDI rows are already present (drops the old ones first)",
    )
    args = p.parse_args()

    cfg = load_config("configs/config.yaml")
    set_seed(cfg.seed)
    splits_dir = Path(cfg.data.splits_dir)
    image_size = int(cfg.data.get("image_size", 224))

    fold_dirs = sorted(splits_dir.glob("fold_*"))
    if not fold_dirs:
        sys.exit(f"ERROR: no fold_* under {splits_dir}. Nothing to append to.")

    # --- Guard: never silently double-append -------------------------------
    already = {}
    for fd in fold_dirs:
        csv_path = fd / "train_split.csv"
        if not csv_path.exists():
            sys.exit(f"ERROR: missing {csv_path}")
        n = int((pd.read_csv(csv_path, usecols=["source"])["source"] == "ddi").sum())
        if n:
            already[fd.name] = n
    if already and not args.force:
        sys.exit(
            f"ERROR: DDI rows already present: {already}\n"
            f"       Re-running would double-count them. Pass --force to replace."
        )

    df, tone_df = process_ddi(
        raw_dir=args.raw_dir, processed_dir=args.processed_dir, image_size=image_size
    )
    df = df[SPLIT_COLS]

    n_pos = int((df["label"] == 1).sum())
    logger.info(
        f"DDI ready: {len(df)} images | {n_pos} malignant | "
        f"tone FST {tone_df.groupby('skin_tone').size().to_dict()}"
    )

    # --- Report the effect on each fold BEFORE writing ---------------------
    for fd in fold_dirs:
        tr = pd.read_csv(fd / "train_split.csv", usecols=["label", "source"])
        base_pos = int((tr["label"] == 1).sum())
        logger.info(
            f"  {fd.name}: train {len(tr)} rows / {base_pos} pos "
            f"-> {len(tr) + len(df)} rows / {base_pos + n_pos} pos "
            f"(+{100 * n_pos / base_pos:.1f}% positives)"
        )

    if args.dry_run:
        logger.info("--dry-run: nothing written.")
        return

    # --- Side-car: tone/disease stay OUT of the split CSVs -----------------
    args.processed_dir.mkdir(parents=True, exist_ok=True)
    tone_path = args.processed_dir / "ddi_tone_map.csv"
    tone_df.to_csv(tone_path, index=False)
    logger.info(f"Wrote {tone_path} ({len(tone_df)} rows) — tone axis for later analysis")

    # --- Append to every fold's TRAIN csv only ----------------------------
    backup_root = Path("reports/_ddi_backup") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root.mkdir(parents=True, exist_ok=True)

    for fd in fold_dirs:
        csv_path = fd / "train_split.csv"
        shutil.copy2(csv_path, backup_root / f"{fd.name}_train_split.csv")

        tr = pd.read_csv(csv_path)
        if list(tr.columns) != SPLIT_COLS:
            sys.exit(
                f"ERROR: {csv_path} has columns {list(tr.columns)}, expected {SPLIT_COLS}. "
                f"Appending would misalign the schema."
            )
        if args.force:
            tr = tr[tr["source"] != "ddi"]
        out = pd.concat([tr, df], ignore_index=True)
        out.to_csv(csv_path, index=False)
        logger.info(f"  {csv_path}: {len(tr)} -> {len(out)} rows")

    logger.info(f"Backups of the original train CSVs: {backup_root}")
    logger.info(
        "test_split.csv and every val_split.csv were NOT touched — the existing "
        "runs_newsplit_light arm remains a valid paired control."
    )


if __name__ == "__main__":
    main()
