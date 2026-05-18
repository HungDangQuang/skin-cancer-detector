import torch
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


@torch.no_grad()
def infer_backbone_out_dim(backbone: nn.Module, image_size: int = 224) -> int:
    """
    Run a 1-sample forward pass to discover the actual feature dim emitted
    by ``backbone(x)``. ``backbone.num_features`` is unreliable on some timm
    architectures (e.g. MobileNetV3-Large reports 960 but ``forward`` returns
    1280 after the ``conv_head`` expansion), so derive it from the forward
    output directly.
    """
    was_training = backbone.training
    backbone.eval()
    try:
        dummy = torch.zeros(1, 3, image_size, image_size)
        out = backbone(dummy)
        return int(out.shape[1])
    finally:
        backbone.train(was_training)
