import numpy as np
import pandas as pd
import torch
from sklearn.utils.class_weight import compute_class_weight


def compute_weights_from_csv(split_csv: str, label_col: str = "label") -> torch.Tensor:
    """Compute inverse-frequency class weights from a split CSV."""
    df = pd.read_csv(split_csv)
    labels = df[label_col].values
    classes = np.unique(labels)
    weights = compute_class_weight("balanced", classes=classes, y=labels)
    return torch.tensor(weights, dtype=torch.float32)


def compute_sample_weights(labels: list[int], num_classes: int) -> torch.Tensor:
    """Compute per-sample weights for WeightedRandomSampler."""
    class_counts = torch.zeros(num_classes)
    for label in labels:
        class_counts[label] += 1
    class_weights = 1.0 / class_counts.clamp(min=1)
    sample_weights = torch.tensor([class_weights[label] for label in labels])
    return sample_weights
