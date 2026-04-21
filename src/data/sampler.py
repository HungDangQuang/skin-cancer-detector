import numpy as np
import torch
from torch.utils.data import Sampler


class DynamicUndersampledSampler(Sampler):
    """
    Dynamic undersampling sampler for extreme class imbalance.

    Samples all malignant examples + (ratio × num_malignant) benign examples
    per epoch. Benign samples are randomly re-drawn each epoch, ensuring
    the model sees diverse benign samples over training.

    From proposal: ratio=5 (1:5 malignant:benign per epoch).

    Args:
        labels: List/array of binary labels (0=benign, 1=malignant).
        ratio: Number of benign samples per malignant sample.
        seed: Base seed; actual seed = seed + epoch for epoch-level variation.
    """

    def __init__(self, labels: list[int], ratio: int = 5, seed: int = 42):
        self.labels = np.array(labels)
        self.ratio = ratio
        self.seed = seed
        self.epoch = 0

        self.malignant_idx = np.where(self.labels == 1)[0]
        self.benign_idx = np.where(self.labels == 0)[0]

        self.n_malignant = len(self.malignant_idx)
        self.n_benign_per_epoch = min(self.n_malignant * ratio, len(self.benign_idx))

    def set_epoch(self, epoch: int) -> None:
        """Call this at the start of each epoch to reshuffle benign samples."""
        self.epoch = epoch

    def __iter__(self):
        rng = np.random.default_rng(self.seed + self.epoch)

        # Always include all malignant samples
        # Randomly subsample benign to maintain ratio
        benign_sample = rng.choice(self.benign_idx, size=self.n_benign_per_epoch, replace=False)

        indices = np.concatenate([self.malignant_idx, benign_sample])
        indices = rng.permutation(indices)

        return iter(indices.tolist())

    def __len__(self) -> int:
        return self.n_malignant + self.n_benign_per_epoch
