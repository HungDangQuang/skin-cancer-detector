import torch.nn as nn


def build_head(in_features: int, dropout: float = 0.3) -> nn.Module:
    """
    Build a binary classification head.

    Outputs a single raw logit (no activation).
    Use BCEWithLogitsLoss during training, torch.sigmoid() at inference.

    Args:
        in_features: Input feature dimension from backbone.
        dropout: Dropout probability before the linear layer.
    """
    return nn.Sequential(
        nn.Dropout(p=dropout),
        nn.Linear(in_features, 1),
    )
