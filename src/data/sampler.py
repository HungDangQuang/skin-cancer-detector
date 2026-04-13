from torch.utils.data import WeightedRandomSampler

from src.utils.class_weights import compute_sample_weights


def build_weighted_sampler(dataset, num_classes: int) -> WeightedRandomSampler:
    """
    Build a WeightedRandomSampler to handle class imbalance.
    Each epoch samples len(dataset) items with replacement.
    """
    labels = dataset.labels
    sample_weights = compute_sample_weights(labels, num_classes)
    return WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True,
    )
