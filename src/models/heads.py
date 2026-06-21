import timm
import torch
import torch.nn as nn


def create_timm_backbone(backbone_name: str, pretrained: bool = True, drop_path_rate: float = 0.0) -> nn.Module:
    """
    Create a timm feature backbone (``num_classes=0``), optionally with
    stochastic depth.

    ``drop_path_rate`` (stochastic depth) is a regularizer that helps fight
    overfitting, strongest on deep ViT/ConvNeXt backbones. It is passed to
    ``timm.create_model`` ONLY when > 0, so backbones whose constructor doesn't
    accept the kwarg are not broken at the default (0.0). An arch that does not
    support it WITH ``drop_path_rate > 0`` raises a clear ``TypeError`` —
    verify per-arch on the cluster before a full run.
    """
    kwargs = {"pretrained": pretrained, "num_classes": 0}
    if drop_path_rate and drop_path_rate > 0:
        kwargs["drop_path_rate"] = drop_path_rate
    return timm.create_model(backbone_name, **kwargs)


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
