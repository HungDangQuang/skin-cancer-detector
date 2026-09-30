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

That reproduces the POPULATION exactly: 372,242 rows, confirmed against the
surviving runs (62,040 test + 310,202 dev summed over the five
`val_predictions.csv`).

WHAT IT DELIBERATELY DOES *NOT* REPRODUCE (decision 2026-09-22)
---------------------------------------------------------------
The original splits were **not patient-grouped**, and this script does not
recreate that. The fold-size fingerprint settles it:

    patient-grouped   val sizes 59,722 / 67,041 / 75,117 / 50,847 / 60,422  (spread 24,270)
    per-row           val sizes 62,040 / 62,041 / 62,040 / 62,040 / 62,040  (spread 1)
    ORIGINAL          val sizes 62,041 / 62,040 / 62,041 / 62,040 / 62,040  (spread 1)

Grouping 1,042 ISIC patients of ~355 images each cannot yield folds that differ
by one row. So `patient_id` was effectively unique per row when the original
splits were generated, and the same patient's lesions sat on both sides of every
train/test comparison — the 140 fold-run matrix's in-domain metrics are inflated
by patient leakage. (Cross-domain HAM10000/Fitzpatrick17k results are unaffected:
separate datasets, no shared patients.)

This script therefore writes CORRECT, patient-grouped splits and verifies the
disjointness it asserts. The consequence is accepted, not hidden: runs on these
splits are **not** comparable with the existing 140 — any new arm must retrain
its own control.

This script NEVER opens, writes or deletes an image. It only calls `Path.exists()`.

USAGE
-----
    python scripts/rebuild_splits.py --dry-run   # report only, write nothing
    python scripts/rebuild_splits.py             # write + verify disjointness
    python scripts/rebuild_splits.py --force     # replace a non-empty splits_dir

It refuses to run if the group column turns out near-unique per row (that would
silently recreate the leaked split), and refuses to overwrite a non-empty
splits_dir without --force. Back the result up immediately: with the raw HDF5
gone, data/splits/ cannot be regenerated once data/processed/ drifts.
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


def check_patient_disjoint(splits_dir: Path, n_folds: int) -> bool:
    """
    The whole point of the regeneration: assert no patient_id is shared between
    the held-out test set and the dev pool, or between a fold's train and val.

    This is what the ORIGINAL splits silently failed to do — their folds differed
    by 1 row (a per-row split), not by thousands as patient grouping forces, so
    the same patient's ~355 lesions sat on both sides of every comparison.
    """
    test = pd.read_csv(splits_dir / "test_split.csv", usecols=["patient_id"])
    test_pat = set(test["patient_id"])
    ok = True

    for fold in range(n_folds):
        fd = splits_dir / f"fold_{fold}"
        tr = pd.read_csv(fd / "train_split.csv", usecols=["patient_id"])
        va = pd.read_csv(fd / "val_split.csv", usecols=["patient_id"])
        tr_pat, va_pat = set(tr["patient_id"]), set(va["patient_id"])

        for name, other in (("train", tr_pat), ("val", va_pat)):
            shared = test_pat & other
            if shared:
                ok = False
                logger.error(
                    f"LEAK fold_{fold}: {len(shared)} patient(s) in BOTH test and {name} "
                    f"(e.g. {sorted(shared)[:3]})"
                )
        shared = tr_pat & va_pat
        if shared:
            ok = False
            logger.error(
                f"LEAK fold_{fold}: {len(shared)} patient(s) in BOTH train and val "
                f"(e.g. {sorted(shared)[:3]})"
            )
        logger.info(
            f"  fold_{fold}: train {len(tr):>7} rows / {len(tr_pat):>5} patients | "
            f"val {len(va):>6} rows / {len(va_pat):>5} patients | disjoint: "
            f"{'yes' if not (tr_pat & va_pat) and not (test_pat & tr_pat) and not (test_pat & va_pat) else 'NO'}"
        )

    logger.info(f"  test: {len(test):>7} rows / {len(test_pat):>5} patients")
    return ok


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="report the reconstruction; write no splits")
    p.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing splits_dir (refused by default — splits are irreplaceable)",
    )
    args = p.parse_args()

    cfg = load_config("configs/config.yaml")
    set_seed(cfg.seed)

    isic_raw = Path(cfg.data.raw_dir)
    isic_processed = Path(cfg.data.processed_dir)
    splits_dir = Path(cfg.data.splits_dir)
    group_col = cfg.data.get("group_col", "patient_id")

    df_isic = build_isic_df(isic_raw, isic_processed, cfg.data.image_id_col, cfg.data.label_col)

    pad_processed = Path("data/processed/pad_ufes_20")
    pad_raw = Path("data/raw/pad_ufes_20")
    if not pad_processed.exists():
        logger.error(
            "data/processed/pad_ufes_20 is missing. PAD contributes the bulk of the "
            "malignant signal (1,077 of 1,448 positives). Refusing to build an "
            "ISIC-only split under the same name."
        )
        sys.exit(1)
    df_pad = build_pad_df(pad_raw, pad_processed)

    # Concat order matches prepare_data.py: ISIC first, then PAD.
    df_combined = pd.concat([df_isic, df_pad], ignore_index=True)
    n_pat = df_combined[group_col].nunique()
    n_pos = int((df_combined["label"] == 1).sum())
    logger.info(
        f"Combined: {len(df_combined)} images | {group_col}: {n_pat} | "
        f"positives: {n_pos} ({100*n_pos/len(df_combined):.3f}%)"
    )

    # A per-row group column would silently reproduce the leaked split this
    # regeneration exists to replace, so refuse it outright.
    if n_pat > 0.5 * len(df_combined):
        logger.error(
            f"'{group_col}' is near-unique per row ({n_pat} groups for {len(df_combined)} rows). "
            f"Grouping would be a no-op and the split would leak patients — exactly the "
            f"defect found on 2026-09-22. Refusing."
        )
        sys.exit(2)

    if args.dry_run:
        logger.info("--dry-run: nothing written.")
        return

    if splits_dir.exists() and any(splits_dir.iterdir()) and not args.force:
        logger.error(
            f"{splits_dir} already exists and is not empty. Splits are irreplaceable — "
            f"back them up, then re-run with --force if you really mean to replace them."
        )
        sys.exit(3)

    logger.info(f"Writing patient-grouped splits to {splits_dir} ...")
    generate_group_kfold_splits(
        df=df_combined,
        splits_dir=splits_dir,
        n_splits=cfg.data.get("num_folds", 5),
        group_col=group_col,
        label_col="label",
        seed=cfg.seed,
        test_holdout_splits=cfg.data.get("test_holdout_splits", 6),
    )

    logger.info("Verifying patient disjointness ...")
    if not check_patient_disjoint(splits_dir, int(cfg.data.get("num_folds", 5))):
        logger.error("LEAKAGE DETECTED in the splits just written. Do not train on them.")
        sys.exit(4)
    logger.info("Patient disjointness verified — no patient spans test/dev or train/val.")
    logger.info(
        "BACK THESE UP NOW: data/splits/ cannot be regenerated once data/processed/ drifts "
        "(the raw HDF5 is gone). rsync them to the Mac before launching any job."
    )


if __name__ == "__main__":
    main()
