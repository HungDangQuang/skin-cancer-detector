from pathlib import Path

from torch.utils.data import DataLoader

from .dataset import SkinLesionDataset
from .sampler import build_weighted_sampler
from .transforms import build_transforms


class SkinLesionDataModule:
    """
    Encapsulates all DataLoader construction for train/val/test splits.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        self.data_cfg = cfg.data
        self.train_cfg = cfg.training
        self.splits_dir = Path(self.data_cfg.splits_dir)

        self._train_dataset = None
        self._val_dataset = None
        self._test_dataset = None

    def setup(self) -> None:
        train_transform = build_transforms(self.cfg, split="train")
        val_transform = build_transforms(self.cfg, split="val")

        self._train_dataset = SkinLesionDataset(
            split_csv=self.splits_dir / "train_split.csv",
            transform=train_transform,
        )
        self._val_dataset = SkinLesionDataset(
            split_csv=self.splits_dir / "val_split.csv",
            transform=val_transform,
        )
        self._test_dataset = SkinLesionDataset(
            split_csv=self.splits_dir / "test_split.csv",
            transform=val_transform,
        )

    def train_dataloader(self) -> DataLoader:
        sampler = None
        shuffle = True
        if self.data_cfg.get("use_weighted_sampler", False):
            sampler = build_weighted_sampler(self._train_dataset, self.data_cfg.num_classes)
            shuffle = False

        return DataLoader(
            self._train_dataset,
            batch_size=self.train_cfg.batch_size,
            sampler=sampler,
            shuffle=shuffle,
            num_workers=self.cfg.num_workers,
            pin_memory=True,
        )

    def val_dataloader(self) -> DataLoader:
        return DataLoader(
            self._val_dataset,
            batch_size=self.train_cfg.batch_size,
            shuffle=False,
            num_workers=self.cfg.num_workers,
            pin_memory=True,
        )

    def test_dataloader(self) -> DataLoader:
        return DataLoader(
            self._test_dataset,
            batch_size=self.train_cfg.batch_size,
            shuffle=False,
            num_workers=self.cfg.num_workers,
            pin_memory=True,
        )
