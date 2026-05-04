"""
Generate synthetic fixture data for running the POC pipeline end-to-end
WITHOUT downloading the 30 GB ISIC 2024 dataset.

Produces:
  data/processed/poc/benign/<id>.jpg     (N_BENIGN images)
  data/processed/poc/malignant/<id>.jpg  (N_MALIGNANT images)
  data/splits/poc/fold_0/train_split.csv
  data/splits/poc/fold_0/val_split.csv
  data/splits/poc/test_split.csv

Images are 224x224 random RGB noise with a class-conditioned color bias
(benign → greenish, malignant → reddish). This bias is learnable so the
POC model should achieve AUC > 0.5, confirming the training loop works.

Usage:
    python scripts/prepare_poc_data.py
    python scripts/prepare_poc_data.py --n-benign 200 --n-malignant 40
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_synthetic_image(label: int, size: int, rng: np.random.Generator) -> Image.Image:
    """Random RGB noise with a class-dependent color bias (learnable signal)."""
    arr = rng.integers(0, 255, size=(size, size, 3), dtype=np.uint8)
    if label == 1:
        arr[..., 0] = np.clip(arr[..., 0].astype(int) + 40, 0, 255).astype(np.uint8)
    else:
        arr[..., 1] = np.clip(arr[..., 1].astype(int) + 40, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def build_split_df(samples: list[tuple[str, int, str]]) -> pd.DataFrame:
    return pd.DataFrame(samples, columns=["image_path", "label", "patient_id"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-benign", type=int, default=150,
                        help="Number of benign synthetic samples.")
    parser.add_argument("--n-malignant", type=int, default=30,
                        help="Number of malignant synthetic samples.")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--processed-dir", default="data/processed/poc")
    parser.add_argument("--splits-dir", default="data/splits/poc")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)

    processed_dir = Path(args.processed_dir)
    splits_dir = Path(args.splits_dir) / "fold_0"
    test_path = Path(args.splits_dir) / "test_split.csv"

    (processed_dir / "benign").mkdir(parents=True, exist_ok=True)
    (processed_dir / "malignant").mkdir(parents=True, exist_ok=True)
    splits_dir.mkdir(parents=True, exist_ok=True)

    all_samples: list[tuple[str, int, str]] = []
    patient_counter = 0

    # Generate benign
    for i in range(args.n_benign):
        img = generate_synthetic_image(label=0, size=args.image_size, rng=rng)
        path = processed_dir / "benign" / f"poc_benign_{i:05d}.jpg"
        img.save(path, quality=85)
        all_samples.append((str(path), 0, f"patient_{patient_counter:04d}"))
        patient_counter += 1

    # Generate malignant
    for i in range(args.n_malignant):
        img = generate_synthetic_image(label=1, size=args.image_size, rng=rng)
        path = processed_dir / "malignant" / f"poc_malignant_{i:05d}.jpg"
        img.save(path, quality=85)
        all_samples.append((str(path), 1, f"patient_{patient_counter:04d}"))
        patient_counter += 1

    df = build_split_df(all_samples)

    # 60 / 20 / 20 stratified split
    rng_split = np.random.default_rng(args.seed + 1)
    df_shuffled = df.sample(frac=1.0, random_state=args.seed + 1).reset_index(drop=True)

    train_parts, val_parts, test_parts = [], [], []
    for label_val, group in df_shuffled.groupby("label"):
        n = len(group)
        n_train = int(n * 0.6)
        n_val = int(n * 0.2)
        train_parts.append(group.iloc[:n_train])
        val_parts.append(group.iloc[n_train:n_train + n_val])
        test_parts.append(group.iloc[n_train + n_val:])

    train_df = pd.concat(train_parts, ignore_index=True).sample(frac=1.0, random_state=args.seed + 2).reset_index(drop=True)
    val_df = pd.concat(val_parts, ignore_index=True).reset_index(drop=True)
    test_df = pd.concat(test_parts, ignore_index=True).reset_index(drop=True)

    train_df.to_csv(splits_dir / "train_split.csv", index=False)
    val_df.to_csv(splits_dir / "val_split.csv", index=False)
    test_df.to_csv(test_path, index=False)

    def counts(d: pd.DataFrame) -> str:
        c = d["label"].value_counts().to_dict()
        return f"benign={c.get(0, 0)}, malignant={c.get(1, 0)}"

    print(f"Generated {args.n_benign + args.n_malignant} synthetic images under {processed_dir}")
    print(f"  train ({len(train_df)}): {counts(train_df)}  →  {splits_dir / 'train_split.csv'}")
    print(f"  val   ({len(val_df)}):   {counts(val_df)}  →  {splits_dir / 'val_split.csv'}")
    print(f"  test  ({len(test_df)}):  {counts(test_df)}  →  {test_path}")
    print("\nReady to run: make poc-all")


if __name__ == "__main__":
    main()
