import numpy as np
import torch
from torch.utils.data import Sampler

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Allowed values of data.sampler_stratify_by. None = the historical sampler.
STRATIFY_MODES = (None, "source")


class DynamicUndersampledSampler(Sampler):
    """
    Dynamic undersampling sampler for extreme class imbalance.

    Samples all malignant examples + (ratio × num_malignant) benign examples
    per epoch. Benign samples are randomly re-drawn each epoch, ensuring
    the model sees diverse benign samples over training.

    From proposal: ratio=5 (1:5 malignant:benign per epoch).

    Source-stratified mode (``stratify_by="source"``, opt-in): the uniform draw
    takes benign rows from the whole pool regardless of origin, so a minority
    source is almost absent (PAD-UFES-20: 809 of 252,521 benign rows in fold 0 of
    the pre-DDI v2 splits -> ~14.5 PAD benign per epoch against 669 PAD malignant). In this mode the
    TOTAL benign per epoch is unchanged; every source except the largest benign
    pool gets ``min(ratio × n_malignant_s, n_benign_s)`` benign rows, and the
    largest pool (ISIC) fills the remainder. Default ``None`` keeps the
    historical draw exactly (same RNG calls, same indices).

    Args:
        labels: List/array of binary labels (0=benign, 1=malignant).
        ratio: Number of benign samples per malignant sample.
        seed: Base seed; actual seed = seed + epoch for epoch-level variation.
        sources: Optional per-row origin tag (row-aligned with ``labels``). Only
            used for the per-epoch (source × label) log unless ``stratify_by``
            is set.
        stratify_by: ``None`` (default) or ``"source"``.
    """

    def __init__(
        self,
        labels: list[int],
        ratio: int = 5,
        seed: int = 42,
        sources: list[str] | None = None,
        stratify_by: str | None = None,
    ):
        if stratify_by not in STRATIFY_MODES:
            raise ValueError(f"sampler_stratify_by={stratify_by!r}; expected one of {STRATIFY_MODES}")
        if stratify_by == "source" and sources is None:
            raise ValueError("sampler_stratify_by='source' needs per-row sources")
        if sources is not None and len(sources) != len(labels):
            raise ValueError(f"sources has {len(sources)} rows but labels has {len(labels)}")

        self.labels = np.array(labels)
        self.ratio = ratio
        self.seed = seed
        self.epoch = 0
        self.stratify_by = stratify_by
        self.sources = None if sources is None else np.asarray(sources, dtype=str)

        self.malignant_idx = np.where(self.labels == 1)[0]
        self.benign_idx = np.where(self.labels == 0)[0]

        self.n_malignant = len(self.malignant_idx)
        self.n_benign_per_epoch = min(self.n_malignant * ratio, len(self.benign_idx))

        # {source: (benign index pool, rows drawn per epoch)}, insertion-ordered
        # by sorted source name so the RNG call order is deterministic.
        self.benign_quota = None
        if stratify_by == "source":
            self.benign_quota = self._source_quotas()
            self.n_benign_per_epoch = sum(n for _, n in self.benign_quota.values())

    def _source_quotas(self) -> dict[str, tuple[np.ndarray, int]]:
        target = self.n_benign_per_epoch
        benign_src = self.sources[self.benign_idx]
        mal_src = self.sources[self.malignant_idx]
        names = sorted(set(benign_src.tolist()))
        pools = {s: self.benign_idx[benign_src == s] for s in names}
        n_mal = {s: int(np.sum(mal_src == s)) for s in names}

        # The largest benign pool absorbs the remainder (ties -> first by name).
        residual = max(names, key=lambda s: len(pools[s]))
        quota = {s: min(self.ratio * n_mal[s], len(pools[s])) for s in names if s != residual}
        rest = target - sum(quota.values())
        assert rest >= 0, (target, quota)  # sum(quota) <= ratio × n_mal <= target
        quota[residual] = min(rest, len(pools[residual]))

        n_benign = len(self.benign_idx)
        drawn = sum(quota.values())
        logger.info(
            f"Sampler stratify_by=source: {self.n_malignant} malignant -> "
            f"{target} benign/epoch target, {drawn} drawn; residual source = {residual}."
        )
        for s in names:
            uniform = target * len(pools[s]) / n_benign
            change = (quota[s] - uniform) / uniform * 100 if uniform else float("nan")
            logger.info(
                f"  {s}: malignant {n_mal[s]}, benign pool {len(pools[s])}, "
                f"benign/epoch {quota[s]} (uniform draw expected {uniform:.1f}, {change:+.1f}%)"
            )
        if drawn != target:
            logger.warning(f"Sampler stratify_by=source drew {drawn} benign/epoch, not the {target} target.")
        return {s: (pools[s], quota[s]) for s in names}

    def set_epoch(self, epoch: int) -> None:
        """Call this at the start of each epoch to reshuffle benign samples."""
        self.epoch = epoch

    def __iter__(self):
        rng = np.random.default_rng(self.seed + self.epoch)

        # Always include all malignant samples
        # Randomly subsample benign to maintain ratio
        if self.benign_quota is None:
            benign_sample = rng.choice(self.benign_idx, size=self.n_benign_per_epoch, replace=False)
        else:
            benign_sample = np.concatenate(
                [rng.choice(pool, size=n, replace=False) for pool, n in self.benign_quota.values()]
            )

        indices = np.concatenate([self.malignant_idx, benign_sample])
        indices = rng.permutation(indices)

        if self.sources is not None:
            self._log_epoch(indices)
        return iter(indices.tolist())

    def _log_epoch(self, indices: np.ndarray) -> None:
        src = self.sources[indices]
        lab = self.labels[indices]
        parts = [
            f"{s} mal={int(np.sum((src == s) & (lab == 1)))} ben={int(np.sum((src == s) & (lab == 0)))}"
            for s in sorted(set(src.tolist()))
        ]
        logger.info(f"Sampler epoch {self.epoch} ({len(indices)} rows): " + " | ".join(parts))

    def __len__(self) -> int:
        return self.n_malignant + self.n_benign_per_epoch
