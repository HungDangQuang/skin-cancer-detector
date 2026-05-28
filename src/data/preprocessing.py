"""
Offline preprocessing script helpers.
Run via: python scripts/prepare_data.py
"""
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


# ------------------------------------------------------------------
# ISIC 2024 SLICE-3D
# ------------------------------------------------------------------

def process_isic2024(
    raw_dir: str | Path,
    processed_dir: str | Path,
    image_size: int = 224,
    image_id_col: str = "isic_id",
    label_col: str = "target",
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
    skipped = 0  # number of rows where the resized JPG already existed on disk

    with h5py.File(hdf5_path, "r") as hdf:
        for _, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing ISIC 2024"):
            image_id = row[image_id_col]
            label = int(row[label_col])
            patient_id = str(row.get("patient_id", image_id))
            class_name = class_names[label]
            dst = processed_dir / class_name / f"{image_id}.jpg"

            if dst.exists():
                # Fast-path: a previous run already resized this image. Skip
                # the HDF5 read + PIL decode + resize + write — the most
                # expensive part. Still record the row so the returned df is
                # complete and downstream split generation sees every sample.
                skipped += 1
            else:
                if image_id not in hdf:
                    continue
                # HDF5 stores JPEG bytes as a byte string dataset
                jpeg_bytes = hdf[image_id][()]
                img = Image.open(__import__("io").BytesIO(jpeg_bytes)).convert("RGB")
                resize_and_save(img, dst, size=(image_size, image_size))

            records.append({
                "image_id": image_id,
                "patient_id": patient_id,
                "image_path": str(dst),
                "label": label,
                "class_name": class_name,
                "source": "isic2024",
            })

    df = pd.DataFrame(records)
    print(
        f"ISIC 2024 — total: {len(df)} | "
        f"benign: {(df['label']==0).sum()} | malignant: {(df['label']==1).sum()} | "
        f"skipped (already-on-disk): {skipped}"
    )
    return df


# ------------------------------------------------------------------
# PAD-UFES-20
# ------------------------------------------------------------------

def process_pad_ufes_20(
    raw_dir: str | Path,
    processed_dir: str | Path,
    image_size: int = 224,
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
    skipped = 0

    for _, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing PAD-UFES-20"):
        img_id = str(row["img_id"])
        diagnostic = str(row["diagnostic"]).upper()
        label = LABEL_MAP.get(diagnostic)

        if label is None:
            continue

        class_name = class_names[label]
        dst = processed_dir / class_name / f"pad_{img_id}.jpg"

        if dst.exists():
            # Fast-path: already processed in a previous run.
            skipped += 1
        else:
            src = images_dir / f"{img_id}.png"
            if not src.exists():
                src = images_dir / f"{img_id}.jpg"
            if not src.exists():
                continue
            resize_and_save(src, dst, size=(image_size, image_size))

        records.append({
            "image_id": f"pad_{img_id}",
            "patient_id": str(row.get("patient_id", img_id)),
            "image_path": str(dst),
            "label": label,
            "class_name": class_name,
            "source": "pad_ufes_20",
        })

    df = pd.DataFrame(records)
    print(
        f"PAD-UFES-20 — total: {len(df)} | "
        f"benign: {(df['label']==0).sum()} | malignant: {(df['label']==1).sum()} | "
        f"skipped (already-on-disk): {skipped}"
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
) -> list[dict]:
    """
    Generate StratifiedGroupKFold splits ensuring:
      - All images of the same patient stay in the same fold (no leakage)
      - Each fold preserves the benign:malignant ratio

    Saves fold CSVs to splits_dir/fold_{i}/{train,val}_split.csv
    Also saves a held-out test split (fold 0 val) to splits_dir/test_split.csv

    Returns:
        List of dicts with 'fold', 'train_df', 'val_df' for each fold.
    """
    splits_dir = Path(splits_dir)
    splits_dir.mkdir(parents=True, exist_ok=True)

    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    groups = df[group_col].values
    labels = df[label_col].values

    folds = []
    for fold_idx, (train_idx, val_idx) in enumerate(sgkf.split(df, labels, groups)):
        fold_dir = splits_dir / f"fold_{fold_idx}"
        fold_dir.mkdir(exist_ok=True)

        train_df = df.iloc[train_idx].reset_index(drop=True)
        val_df = df.iloc[val_idx].reset_index(drop=True)

        train_df.to_csv(fold_dir / "train_split.csv", index=False)
        val_df.to_csv(fold_dir / "val_split.csv", index=False)

        folds.append({"fold": fold_idx, "train_df": train_df, "val_df": val_df})

        print(
            f"Fold {fold_idx} — train: {len(train_df)} "
            f"(mal={( train_df[label_col]==1).sum()}) | "
            f"val: {len(val_df)} "
            f"(mal={(val_df[label_col]==1).sum()})"
        )

    # Use fold 0 val as held-out test set (committed to git, never changed)
    folds[0]["val_df"].to_csv(splits_dir / "test_split.csv", index=False)
    print(f"\nTest split saved: {len(folds[0]['val_df'])} samples (fold 0 val)")

    return folds
