"""
Offline preprocessing script helpers.
Run via: python scripts/prepare_data.py
"""
import hashlib
import io
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import StratifiedGroupKFold
from tqdm import tqdm


def resize_and_save(src: Image.Image | Path, dst_path: Path, size: tuple[int, int] = (224, 224)) -> None:
    """Resize a PIL image (or path) and save to destination."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    img = (Image.open(src).convert("RGB") if isinstance(src, Path) else src)
    img = img.resize(size, Image.LANCZOS)
    img.save(dst_path)


def is_uninformative(
    img: Image.Image,
    std_threshold: float = 8.0,
    extreme_frac_threshold: float = 0.97,
) -> bool:
    """Heuristic check for blank / near-uniform / no-signal images.

    Operates on the (already resized) RGB image. Returns True when the image
    carries essentially no usable signal and should be dropped:
      - global grayscale std < std_threshold  → flat / near-uniform tile, or
      - > extreme_frac_threshold of pixels are near-black or near-white
        → all-dark vignette crops and blown-out / washed-out tiles.

    Thresholds are intentionally conservative (drop only the clearly bad) and
    are tunable from the call site; verify the drop list on the cluster.
    """
    gray = np.asarray(img.convert("L"), dtype=np.float32)
    if gray.std() < std_threshold:
        return True
    extreme_frac = float((gray <= 10).mean() + (gray >= 245).mean())
    return extreme_frac > extreme_frac_threshold


# ------------------------------------------------------------------
# ISIC 2024 SLICE-3D
# ------------------------------------------------------------------

def process_isic2024(
    raw_dir: str | Path,
    processed_dir: str | Path,
    image_size: int = 224,
    image_id_col: str = "isic_id",
    label_col: str = "target",
    min_size: int = 32,
) -> pd.DataFrame:
    """
    Extract and resize images from ISIC 2024 HDF5 archive.

    Raw structure expected:
        raw_dir/
          train-image.hdf5     <- HDF5 with keys = isic_id, values = JPEG bytes
          train-metadata.csv   <- isic_id, patient_id, target (0/1), ...

    Returns:
        DataFrame with columns: image_id, patient_id, image_path, label, class_name.
    """
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    hdf5_path = raw_dir / "train-image.hdf5"
    metadata_csv = raw_dir / "train-metadata.csv"

    if not hdf5_path.exists():
        raise FileNotFoundError(f"HDF5 not found: {hdf5_path}")
    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_csv}")

    metadata = pd.read_csv(metadata_csv, low_memory=False)
    class_names = {0: "benign", 1: "malignant"}
    records = []
    excluded = []  # (image_id, reason) for corrupt / small / dup / uninformative images
    seen_hashes: set[str] = set()  # exact-duplicate detection across the dataset
    skipped = 0  # number of rows where the resized JPG already existed on disk

    with h5py.File(hdf5_path, "r") as hdf:
        for _, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing ISIC 2024"):
            image_id = row[image_id_col]
            label = int(row[label_col])
            patient_id = str(row.get("patient_id", image_id))
            class_name = class_names[label]
            dst = processed_dir / class_name / f"{image_id}.jpg"

            try:
                if dst.exists():
                    # Fast-path: a previous run already resized this image, so
                    # skip the HDF5 read + resize. Still load it back so the
                    # quality filter runs (a pre-filter run may have written a
                    # bad image to disk).
                    img = Image.open(dst).convert("RGB")
                    is_new = False
                else:
                    if image_id not in hdf:
                        continue
                    # HDF5 stores JPEG bytes as a byte string dataset
                    jpeg_bytes = hdf[image_id][()]
                    img = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
                    if min(img.size) < min_size:
                        # Native crop too small to carry detail once upscaled to
                        # image_size. Only checkable on the fresh decode — the
                        # fast-path image on disk is already resized to 224.
                        excluded.append({"image_id": image_id, "reason": f"too_small: {img.size}"})
                        continue
                    img = img.resize((image_size, image_size), Image.LANCZOS)
                    is_new = True
            except (OSError, ValueError, Image.DecompressionBombError) as e:
                excluded.append({"image_id": image_id, "reason": f"corrupt: {e}"})
                continue

            if is_uninformative(img):
                excluded.append({"image_id": image_id, "reason": "uninformative"})
                # Drop a previously-saved bad image so the on-disk dataset
                # stays consistent with the split CSVs.
                if not is_new and dst.exists():
                    dst.unlink()
                continue

            # Exact-duplicate detection on the resized pixels: first occurrence
            # kept, later identical images dropped so the same lesion cannot land
            # in two folds.
            img_hash = hashlib.md5(img.tobytes()).hexdigest()
            if img_hash in seen_hashes:
                excluded.append({"image_id": image_id, "reason": "duplicate"})
                if not is_new and dst.exists():
                    dst.unlink()
                continue
            seen_hashes.add(img_hash)

            if is_new:
                dst.parent.mkdir(parents=True, exist_ok=True)
                img.save(dst)
            else:
                skipped += 1

            records.append({
                "image_id": image_id,
                "patient_id": patient_id,
                "image_path": str(dst),
                "label": label,
                "class_name": class_name,
                "source": "isic2024",
            })

    if excluded:
        processed_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(excluded).to_csv(processed_dir / "excluded_images.csv", index=False)

    df = pd.DataFrame(records)
    print(
        f"ISIC 2024 — total: {len(df)} | "
        f"benign: {(df['label']==0).sum()} | malignant: {(df['label']==1).sum()} | "
        f"skipped (already-on-disk): {skipped} | "
        f"excluded (corrupt/small/dup/uninformative): {len(excluded)}"
    )
    return df


# ------------------------------------------------------------------
# PAD-UFES-20
# ------------------------------------------------------------------

def process_pad_ufes_20(
    raw_dir: str | Path,
    processed_dir: str | Path,
    image_size: int = 224,
    min_size: int = 32,
) -> pd.DataFrame:
    """
    Process PAD-UFES-20 dataset and map 6 classes to binary labels.

    Raw structure expected:
        raw_dir/
          images/          <- JPEG files
          metadata.csv     <- img_id, diagnostic (BCC/SCC/MEL/ACK/NEV/SEK), ...

    Label mapping (from proposal):
        Malignant (1): BCC, SCC, MEL
        Benign    (0): ACK, NEV, SEK

    Returns:
        DataFrame with columns: image_id, patient_id, image_path, label, class_name, source.
    """
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    images_dir = raw_dir / "images"
    metadata_csv = raw_dir / "metadata.csv"

    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_csv}")

    metadata = pd.read_csv(metadata_csv)

    LABEL_MAP = {
        "BCC": 1, "SCC": 1, "MEL": 1,
        "ACK": 0, "NEV": 0, "SEK": 0,
    }
    class_names = {0: "benign", 1: "malignant"}
    records = []
    excluded = []  # (image_id, reason) for corrupt / small / dup / uninformative images
    seen_hashes: set[str] = set()  # exact-duplicate detection across the dataset
    skipped = 0

    for _, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing PAD-UFES-20"):
        img_id = str(row["img_id"])
        diagnostic = str(row["diagnostic"]).upper()
        label = LABEL_MAP.get(diagnostic)

        if label is None:
            continue

        class_name = class_names[label]
        dst = processed_dir / class_name / f"pad_{img_id}.jpg"

        try:
            if dst.exists():
                # Fast-path: already processed; reload it so the filter runs.
                img = Image.open(dst).convert("RGB")
                is_new = False
            else:
                src = images_dir / f"{img_id}.png"
                if not src.exists():
                    src = images_dir / f"{img_id}.jpg"
                if not src.exists():
                    continue
                img = Image.open(src).convert("RGB")
                if min(img.size) < min_size:
                    excluded.append({"image_id": f"pad_{img_id}", "reason": f"too_small: {img.size}"})
                    continue
                img = img.resize((image_size, image_size), Image.LANCZOS)
                is_new = True
        except (OSError, ValueError, Image.DecompressionBombError) as e:
            excluded.append({"image_id": f"pad_{img_id}", "reason": f"corrupt: {e}"})
            continue

        if is_uninformative(img):
            excluded.append({"image_id": f"pad_{img_id}", "reason": "uninformative"})
            if not is_new and dst.exists():
                dst.unlink()
            continue

        img_hash = hashlib.md5(img.tobytes()).hexdigest()
        if img_hash in seen_hashes:
            excluded.append({"image_id": f"pad_{img_id}", "reason": "duplicate"})
            if not is_new and dst.exists():
                dst.unlink()
            continue
        seen_hashes.add(img_hash)

        if is_new:
            dst.parent.mkdir(parents=True, exist_ok=True)
            img.save(dst)
        else:
            skipped += 1

        records.append({
            "image_id": f"pad_{img_id}",
            # Namespace the group key so a PAD patient_id can never collide with
            # an ISIC patient_id and leak across folds in StratifiedGroupKFold.
            "patient_id": f"pad_{row.get('patient_id', img_id)}",
            "image_path": str(dst),
            "label": label,
            "class_name": class_name,
            "source": "pad_ufes_20",
        })

    if excluded:
        processed_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(excluded).to_csv(processed_dir / "excluded_images.csv", index=False)

    df = pd.DataFrame(records)
    print(
        f"PAD-UFES-20 — total: {len(df)} | "
        f"benign: {(df['label']==0).sum()} | malignant: {(df['label']==1).sum()} | "
        f"skipped (already-on-disk): {skipped} | "
        f"excluded (corrupt/small/dup/uninformative): {len(excluded)}"
    )
    return df


# ------------------------------------------------------------------
# Stratified GroupKFold splits
# ------------------------------------------------------------------

def generate_group_kfold_splits(
    df: pd.DataFrame,
    splits_dir: str | Path,
    n_splits: int = 5,
    group_col: str = "patient_id",
    label_col: str = "label",
    seed: int = 42,
    test_holdout_splits: int = 6,
) -> list[dict]:
    """
    Leak-free split layout:
      1. Carve a patient-disjoint, label-stratified **held-out test set** —
         1/test_holdout_splits of the data (~17% with the default 6) — that NO
         fold ever trains or validates on.
      2. Run StratifiedGroupKFold(n_splits) on the remaining dev pool for the
         train/val folds.

    Both steps group by `group_col` (no patient leakage) and stratify by
    `label_col` (benign:malignant ratio preserved). Because every fold's model
    is later evaluated on the SAME independent test_split, the per-fold test
    metrics are unbiased and directly comparable (e.g. paired KD vs baseline).

    NOTE: this replaces the previous design where test_split.csv was fold 0's
    val set — under which folds 1..4 trained on the test samples (leakage; their
    test metrics were optimistically inflated).

    Saves:
      splits_dir/test_split.csv                 <- independent held-out test
      splits_dir/fold_{i}/{train,val}_split.csv

    Returns:
        List of dicts with 'fold', 'train_df', 'val_df' for each fold.
    """
    splits_dir = Path(splits_dir)
    splits_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: held-out test = first fold of a group-stratified split ---
    holdout = StratifiedGroupKFold(n_splits=test_holdout_splits, shuffle=True, random_state=seed)
    dev_idx, test_idx = next(holdout.split(df, df[label_col].values, df[group_col].values))
    dev_df = df.iloc[dev_idx].reset_index(drop=True)
    test_df = df.iloc[test_idx].reset_index(drop=True)
    test_df.to_csv(splits_dir / "test_split.csv", index=False)

    # --- Step 2: n_splits-fold CV on the dev pool only (test patients excluded) ---
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    dev_groups = dev_df[group_col].values
    dev_labels = dev_df[label_col].values

    folds = []
    for fold_idx, (train_idx, val_idx) in enumerate(sgkf.split(dev_df, dev_labels, dev_groups)):
        fold_dir = splits_dir / f"fold_{fold_idx}"
        fold_dir.mkdir(exist_ok=True)

        train_df = dev_df.iloc[train_idx].reset_index(drop=True)
        val_df = dev_df.iloc[val_idx].reset_index(drop=True)

        train_df.to_csv(fold_dir / "train_split.csv", index=False)
        val_df.to_csv(fold_dir / "val_split.csv", index=False)

        folds.append({"fold": fold_idx, "train_df": train_df, "val_df": val_df})

        print(
            f"Fold {fold_idx} — train: {len(train_df)} "
            f"(mal={(train_df[label_col]==1).sum()}) | "
            f"val: {len(val_df)} "
            f"(mal={(val_df[label_col]==1).sum()})"
        )

    print(
        f"\nHeld-out test: {len(test_df)} samples "
        f"(mal={(test_df[label_col]==1).sum()}) — patient-disjoint + stratified, "
        f"1/{test_holdout_splits} of data, independent of all {n_splits} folds"
    )

    return folds
