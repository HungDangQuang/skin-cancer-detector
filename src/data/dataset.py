from pathlib import Path

import pandas as pd
from PIL import Image
from torch.utils.data import Dataset


class SkinLesionDataset(Dataset):
    """
    Dataset for skin lesion classification.

    Reads image paths and labels from a CSV split file.
    CSV must have columns: 'image_path', 'label' (integer).
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
        """Return all labels (for weighted sampler)."""
        return self.df[self.label_col].tolist()

    @property
    def class_counts(self) -> dict[int, int]:
        return self.df[self.label_col].value_counts().to_dict()
