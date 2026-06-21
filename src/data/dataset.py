from pathlib import Path

import pandas as pd
from PIL import Image
from torch.utils.data import Dataset


class SkinLesionDataset(Dataset):
    """
    Binary skin lesion dataset for ISIC 2024 + PAD-UFES-20.

    Reads image paths and labels from a split CSV file.
    CSV must have columns: 'image_path', 'label' (0=benign, 1=malignant).

    Labels are returned as float for BCEWithLogitsLoss compatibility.
    """

    def __init__(
        self,
        split_csv: str | Path,
        transform=None,
        image_col: str = "image_path",
        label_col: str = "label",
    ):
        self.df = pd.read_csv(split_csv)
        self.transform = transform
        self.image_col = image_col
        self.label_col = label_col

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> tuple:
        row = self.df.iloc[idx]
        image = Image.open(row[self.image_col]).convert("RGB")
        label = int(row[self.label_col])

        if self.transform:
            image = self.transform(image)

        return image, label

    @property
    def labels(self) -> list[int]:
        return self.df[self.label_col].tolist()

    @property
    def class_counts(self) -> dict[int, int]:
        return self.df[self.label_col].value_counts().to_dict()

    def malignant_ratio(self) -> float:
        counts = self.class_counts
        total = sum(counts.values())
        return counts.get(1, 0) / total if total > 0 else 0.0
