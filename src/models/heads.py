import torch.nn as nn


def build_head(in_features: int, num_classes: int, dropout: float = 0.3, hidden_dim: int | None = None) -> nn.Module:
    """
    Build a classification head.

    Args:
        in_features: Input feature dimension (from backbone).
        num_classes: Number of output classes.
        dropout: Dropout probability.
        hidden_dim: If provided, adds a hidden FC layer before the classifier.
    """
    layers = [nn.Dropout(p=dropout)]

    if hidden_dim is not None:
        layers += [
            nn.Linear(in_features, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(hidden_dim, num_classes),
        ]
    else:
        layers.append(nn.Linear(in_features, num_classes))

    return nn.Sequential(*layers)
