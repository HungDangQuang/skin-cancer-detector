import timm
import torch
import torch.nn as nn

from .base_model import BaseModel
from .heads import build_head


class EfficientNetModel(BaseModel):
    """EfficientNet backbone with custom classification head (via timm)."""

    def __init__(self, cfg):
        super().__init__()
        backbone_name = cfg.model.get("backbone", "efficientnet_b3")
        num_classes = cfg.model.num_classes
        pretrained = cfg.model.get("pretrained", True)
        dropout = cfg.model.head.get("dropout", 0.3)
        hidden_dim = cfg.model.head.get("hidden_dim", None)

        self.backbone = timm.create_model(backbone_name, pretrained=pretrained, num_classes=0)
        in_features = self.backbone.num_features

        self.head = build_head(in_features, num_classes, dropout=dropout, hidden_dim=hidden_dim)

        if cfg.model.get("freeze_backbone", False):
            self.freeze_backbone()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)
        return self.head(features)
