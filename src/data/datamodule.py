from pathlib import Path

from torch.utils.data import DataLoader

from .dataset import SkinLesionDataset
from .sampler import DynamicUndersampledSampler
from .transforms import build_transforms


class SkinLesionDataModule:
    """
    DataModule for 5-fold cross-validation with StratifiedGroupKFold splits.

    Directory structure expected:
        splits_dir/
          fold_0/train_split.csv
          fold_0/val_split.csv
          fold_1/train_split.csv
          ...
          test_split.csv       <- held-out test set (fold 0 val)
    """

    def __init__(self, cfg, fold: int = 0):
        self.cfg = cfg
        self.data_cfg = cfg.data
        self.train_cfg = cfg.training
        self.splits_dir = Path(self.data_cfg.splits_dir)
        self.fold = fold

        self._train_dataset = None
        self._val_dataset = None
        self._test_dataset = None
        self._train_sampler = None

    def setup(self) -> None:
        train_transform = build_transforms(self.cfg, split="train")
        val_transform = build_transforms(self.cfg, split="val")

        fold_dir = self.splits_dir / f"fold_{self.fold}"

        self._train_dataset = SkinLesionDataset(
            split_csv=fold_dir / "train_split.csv",
            transform=train_transform,
        )
        self._val_dataset = SkinLesionDataset(
            split_csv=fold_dir / "val_split.csv",
            transform=val_transform,
        )
        self._test_dataset = SkinLesionDataset(
            split_csv=self.splits_dir / "test_split.csv",
            transform=val_transform,
        )

        # Dynamic undersampling sampler (1:5 ratio, resampled each epoch)
        if self.data_cfg.get("use_weighted_sampler", True):
            self._train_sampler = DynamicUndersampledSampler(
                labels=self._train_dataset.labels,
                ratio=self.data_cfg.get("undersample_ratio", 5),
                seed=self.cfg.seed,
            )

    def set_epoch(self, epoch: int) -> None:
        """Call at the start of each epoch to reshuffle undersampled benign pool."""
        if self._train_sampler is not None:
            self._train_sampler.set_epoch(epoch)

    def train_dataloader(self) -> DataLoader:
        return DataLoader(
            self._train_dataset,
            batch_size=self.train_cfg.batch_size,
            sampler=self._train_sampler,
            shuffle=(self._train_sampler is None),
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
