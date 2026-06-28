import torch

from .base_model import BaseModel
from .heads import build_head, create_timm_backbone, infer_backbone_out_dim


class MobileViTModel(BaseModel):
    """MobileViT-S backbone with binary classification head (via timm)."""

    def __init__(self, cfg):
        super().__init__()
        backbone_name = cfg.model.get("backbone", "mobilevit_s")
        pretrained = cfg.model.get("pretrained", True)
        dropout = cfg.model.head.get("dropout", 0.1)
        drop_path_rate = cfg.model.get("drop_path_rate", 0.0)

        self.backbone = create_timm_backbone(backbone_name, pretrained=pretrained, drop_path_rate=drop_path_rate)
        in_features = infer_backbone_out_dim(self.backbone)
        self.head = build_head(in_features, dropout=dropout)

        if cfg.model.get("freeze_backbone", False):
            self.freeze_backbone()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Returns shape (B,) — raw logit for BCEWithLogitsLoss
        return self.head(self.backbone(x)).squeeze(1)
