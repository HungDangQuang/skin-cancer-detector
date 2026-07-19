from pathlib import Path

import numpy as np
from torch.utils.data import DataLoader

from src.utils.logger import get_logger

from .dataset import SkinLesionDataset
from .sampler import DynamicUndersampledSampler
from .transforms import build_transforms

logger = get_logger(__name__)


def source_from_path(image_path: str) -> str:
    """
    Tag a processed image with its origin dataset from its path.

    Processed images live under data/processed/<dataset>/<class>/..., so the
    dataset name is recoverable from the path. Used to compute per-domain
    (ISIC vs PAD) eval breakdowns — the key metric for the PAD ablation.
    """
    p = str(image_path).replace("\\", "/")
    if "/isic2024/" in p or "isic2024" in p:
        return "isic2024"
    if "/pad_ufes_20/" in p or "pad_ufes_20" in p:
        return "pad_ufes_20"
    if "/ham10000/" in p or "ham10000" in p:
        return "ham10000"
    if "/fitzpatrick17k/" in p or "fitzpatrick" in p:
        return "fitzpatrick17k"
    return "unknown"


class SkinLesionDataModule:
    """
    DataModule for 5-fold cross-validation with StratifiedGroupKFold splits.

    Directory structure expected:
        splits_dir/
          fold_0/train_split.csv
          fold_0/val_split.csv
          fold_1/train_split.csv
          ...
          test_split.csv       <- independent held-out test (patient-disjoint from all folds)
    """

    def __init__(self, cfg, fold: int | None = None):
        self.cfg = cfg
        self.data_cfg = cfg.data
        self.train_cfg = cfg.training
        self.splits_dir = Path(self.data_cfg.splits_dir)
        # Explicit kwarg wins; otherwise read from Hydra config (cfg.data.fold).
        # Default to 0 if neither is set (back-compat for old configs).
        self.fold = fold if fold is not None else int(self.data_cfg.get("fold", 0))

        self._train_dataset = None
        self._val_dataset = None
        self._test_dataset = None
        self._train_sampler = None
        # Train-fold metadata scaler (privileged teacher / direction A). None
        # unless data.metadata_cols is set.
        self.meta_mean = None
        self.meta_std = None

    def setup(self) -> None:
        train_transform = build_transforms(self.cfg, split="train")
        val_transform = build_transforms(self.cfg, split="val")

        fold_dir = self.splits_dir / f"fold_{self.fold}"

        # Privileged metadata as MODEL INPUT (direction A). Two conditions must
        # both hold, else datasets return (image, label) exactly as before:
        #   - data.metadata_cols is a non-empty list, AND
        #   - data.metadata_as_input is true (a privileged teacher run).
        # Direction D sets metadata_cols but NOT metadata_as_input -> the columns
        # ride in the split CSVs / predictions.csv side-channel only, model stays
        # image-only, and this stays None (dataset 2-tuple).
        metadata_cols = self.data_cfg.get("metadata_cols", None)
        metadata_cols = list(metadata_cols) if metadata_cols else None
        if not self.data_cfg.get("metadata_as_input", False):
            metadata_cols = None

        self._train_dataset = SkinLesionDataset(
            split_csv=fold_dir / "train_split.csv",
            transform=train_transform,
            metadata_cols=metadata_cols,
        )
        self._val_dataset = SkinLesionDataset(
            split_csv=fold_dir / "val_split.csv",
            transform=val_transform,
            metadata_cols=metadata_cols,
        )
        self._test_dataset = SkinLesionDataset(
            split_csv=self.splits_dir / "test_split.csv",
            transform=val_transform,
            metadata_cols=metadata_cols,
        )

        # PAD ablation: optionally restrict TRAIN+VAL to a subset of source
        # datasets (e.g. ["isic2024"] to train ISIC-only). The TEST set is left
        # untouched on purpose, so both the ISIC-only and ISIC+PAD arms are
        # judged on the identical held-out test (its PAD portion is never trained
        # on by either arm) — that is what makes the PAD comparison fair.
        train_sources = self.data_cfg.get("train_sources", None)
        if train_sources:
            keep = list(train_sources)
            self._filter_to_sources(self._train_dataset, keep, "train")
            self._filter_to_sources(self._val_dataset, keep, "val")

        # Fit the metadata scaler on the TRAIN fold ONLY (after any train_sources
        # filter), then push it to all three splits so val/test never leak into
        # the standardization stats.
        if metadata_cols:
            self._fit_meta_scaler()

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

    def _fit_meta_scaler(self) -> None:
        """Fit per-column mean/std on the TRAIN fold's raw metadata (NaN-aware)
        and install it on all three splits, so val/test never leak into the
        standardization stats. PAD rows are all-NaN and ignored by nanmean/nanstd;
        a fully-NaN or zero-variance column falls back to mean 0 / std 1."""
        raw = self._train_dataset._meta_raw
        with np.errstate(invalid="ignore", all="ignore"):
            mean = np.nanmean(raw, axis=0)
            std = np.nanstd(raw, axis=0)
        mean = np.nan_to_num(mean, nan=0.0)
        std = np.where(~np.isfinite(std) | (std == 0.0), 1.0, std)
        self.meta_mean, self.meta_std = mean, std
        for ds in (self._train_dataset, self._val_dataset, self._test_dataset):
            ds.set_meta_scaler(mean, std)
        n_present = int(np.isfinite(raw).any(axis=1).sum())
        logger.info(
            f"Metadata scaler fit on {len(raw)} train rows "
            f"({n_present} with any present value), {raw.shape[1]} columns."
        )

    def _filter_to_sources(self, dataset: SkinLesionDataset, keep: list[str], split: str) -> None:
        """Drop rows whose origin dataset is not in ``keep`` (in place, row-reset).

        Used by the PAD ablation to train ISIC-only without re-running prepare.
        Mutating ``dataset.df`` here is intentional and must happen BEFORE the
        sampler is built, so the sampler sees the filtered label distribution.
        """
        col = dataset.image_col
        srcs = dataset.df[col].astype(str).map(source_from_path)
        mask = srcs.isin(keep)
        n0 = len(dataset.df)
        dataset.df = dataset.df[mask].reset_index(drop=True)
        n1 = len(dataset.df)
        if n1 == 0:
            raise ValueError(
                f"train_sources={keep} filtered the {split} split to 0 rows "
                f"(had {n0}). Check the source tags / paths in the split CSV."
            )
        # Keep the precomputed metadata matrix row-aligned with the filtered df.
        if dataset.metadata_cols:
            dataset._build_meta()
        logger.info(
            f"train_sources={keep}: {split} split filtered {n0} -> {n1} rows "
            f"({n0 - n1} dropped)."
        )

    def test_sources(self) -> list[str]:
        """
        Per-sample origin tag for the test set, row-aligned to test_dataloader()
        (shuffle=False). Lets Evaluator.save_predictions record a `source` column
        so ISIC-vs-PAD per-domain metrics can be computed offline.
        """
        col = self._test_dataset.image_col
        return [source_from_path(p) for p in self._test_dataset.df[col].astype(str)]

    def test_metadata(self, cols: list[str] | None) -> dict[str, list] | None:
        """
        Per-sample raw metadata columns for the test set, row-aligned to
        test_dataloader() (shuffle=False). Parallels test_sources(): lets
        Evaluator.save_predictions record extra columns in predictions.csv for
        offline SUBGROUP calibration (direction D — e.g. anatom_site_general / sex).

        Only columns actually present in the test split CSV are returned; a
        column absent because metadata_cols was null at prepare-time is skipped.
        Returns None when cols is falsy so callers stay on the image-only path.
        """
        if not cols:
            return None
        df = self._test_dataset.df
        return {c: df[c].tolist() for c in cols if c in df.columns} or None
