"""
Offline preprocessing script helpers.
Run via: python scripts/prepare_data.py
"""
from pathlib import Path

import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
from tqdm import tqdm


def resize_and_save(src_path: Path, dst_path: Path, size: tuple[int, int] = (224, 224)) -> None:
    """Resize a single image and save to destination."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(src_path).convert("RGB")
    img = img.resize(size, Image.LANCZOS)
    img.save(dst_path)


def process_ham10000(
    raw_dir: str | Path,
    processed_dir: str | Path,
    metadata_csv: str | Path,
    image_size: int = 224,
) -> pd.DataFrame:
    """
    Resize all HAM10000 images and return a DataFrame with processed paths + labels.

    Args:
        raw_dir: Directory containing HAM10000_images_part1 and part2.
        processed_dir: Target directory for resized images.
        metadata_csv: Path to HAM10000_metadata.csv.
        image_size: Target image size (square).

    Returns:
        DataFrame with columns: image_id, image_path, label, dx (class name).
    """
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    metadata = pd.read_csv(metadata_csv)

    # Build image_id -> source path mapping
    image_paths = {}
    for part in ["HAM10000_images_part1", "HAM10000_images_part2"]:
        part_dir = raw_dir / part
        if part_dir.exists():
            for p in part_dir.glob("*.jpg"):
                image_paths[p.stem] = p

    class_to_idx = {
        "mel": 0, "nv": 1, "bcc": 2,
        "akiec": 3, "bkl": 4, "df": 5, "vasc": 6
    }

    records = []
    for _, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing images"):
        image_id = row["image_id"]
        dx = row["dx"]
        label = class_to_idx.get(dx)
        if label is None or image_id not in image_paths:
            continue

        src = image_paths[image_id]
        dst = processed_dir / dx / f"{image_id}.jpg"
        resize_and_save(src, dst, size=(image_size, image_size))

        records.append({
            "image_id": image_id,
            "image_path": str(dst),
            "label": label,
            "dx": dx,
        })

    return pd.DataFrame(records)


def generate_splits(
    df: pd.DataFrame,
    splits_dir: str | Path,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> None:
    """
    Stratified split into train/val/test and save as CSV files.

    Splits are saved to splits_dir/{train,val,test}_split.csv.
    These files are committed to git for reproducibility.
    """
    splits_dir = Path(splits_dir)
    splits_dir.mkdir(parents=True, exist_ok=True)

    test_ratio = 1.0 - train_ratio - val_ratio

    train_df, temp_df = train_test_split(
        df, test_size=(val_ratio + test_ratio),
        stratify=df["label"], random_state=seed
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=test_ratio / (val_ratio + test_ratio),
        stratify=temp_df["label"], random_state=seed
    )

    train_df.to_csv(splits_dir / "train_split.csv", index=False)
    val_df.to_csv(splits_dir / "val_split.csv", index=False)
    test_df.to_csv(splits_dir / "test_split.csv", index=False)

    print(f"Splits saved to {splits_dir}")
    print(f"  Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
