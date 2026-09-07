from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset


class SkinLesionDataset(Dataset):
    """
    Binary skin lesion dataset for ISIC 2024 + PAD-UFES-20.

    Reads image paths and labels from a split CSV file.
    CSV must have columns: 'image_path', 'label' (0=benign, 1=malignant).

    Labels are returned as float for BCEWithLogitsLoss compatibility.

    Privileged metadata (opt-in, direction A / LUPI):
        When ``metadata_cols`` is given, ``__getitem__`` returns the 4-tuple
        ``(image, meta_tensor, meta_mask, label)`` instead of ``(image, label)``:
          * ``meta_tensor`` (float32, ``len(metadata_cols)``) — the standardized
            metadata (NaN / missing -> 0 after masking).
          * ``meta_mask`` (float32, same length) — 1.0 where the raw value was
            present, 0.0 where it was NaN (e.g. every PAD-UFES-20 row, which has
            no ``tbp_lv_*``). The privileged model zeroes the tabular branch for
            fully-masked rows so PAD never trains the tabular path.
        Default (``metadata_cols=None``) keeps the historical 2-tuple exactly, so
        every image-only run is byte-for-byte unchanged.

    The standardization stats (mean/std) are NOT computed here — they must be fit
    on the TRAIN fold only and pushed in via ``set_meta_scaler`` (the datamodule
    does this), so val/test never leak into the scaler.
    """

    def __init__(
        self,
        split_csv: str | Path,
        transform=None,
        image_col: str = "image_path",
        label_col: str = "label",
        metadata_cols: list[str] | None = None,
    ):
        self.df = pd.read_csv(split_csv)
        self.transform = transform
        self.image_col = image_col
        self.label_col = label_col
        self.metadata_cols = list(metadata_cols) if metadata_cols else None

        # Precompute the raw (unscaled) metadata matrix + presence mask once, so
        # __getitem__ stays cheap and the datamodule can fit the scaler from
        # self._meta_raw. Non-numeric / missing values coerce to NaN -> masked.
        self._meta_raw = None
        self._meta_mask = None
        self._meta_mean = None
        self._meta_std = None
        if self.metadata_cols:
            missing = [c for c in self.metadata_cols if c not in self.df.columns]
            if missing:
                raise KeyError(
                    f"metadata_cols {missing} not in split CSV {split_csv}. "
                    f"Re-run prepare_data.py with data.metadata_cols set."
                )
            self._build_meta()

    def _build_meta(self) -> None:
        """(Re)derive the raw metadata matrix + presence mask from ``self.df``.

        Call after any in-place ``self.df`` row change (e.g. the datamodule's
        train_sources filter) so ``_meta_raw`` stays row-aligned with ``df``.
        """
        raw = self.df[self.metadata_cols].apply(pd.to_numeric, errors="coerce")
        self._meta_raw = raw.to_numpy(dtype=float)  # (N, n_meta), NaN = missing
        self._meta_mask = (~np.isnan(self._meta_raw)).astype(np.float32)

    def set_meta_scaler(self, mean: np.ndarray, std: np.ndarray) -> None:
        """Install the train-fold standardization stats (mean/std per column)."""
        self._meta_mean = np.asarray(mean, dtype=float)
        self._meta_std = np.asarray(std, dtype=float)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> tuple:
        row = self.df.iloc[idx]
        image = Image.open(row[self.image_col]).convert("RGB")
        label = int(row[self.label_col])

        if self.transform:
            image = self.transform(image)

        if self.metadata_cols is None:
            return image, label

        m = self._meta_raw[idx].copy()
        mask = self._meta_mask[idx]
        if self._meta_mean is not None:
            m = (m - self._meta_mean) / self._meta_std
        # Masked / NaN entries -> 0 (the mask tells the model they are absent).
        m = np.nan_to_num(m, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
        return image, torch.from_numpy(m), torch.from_numpy(mask), label

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
