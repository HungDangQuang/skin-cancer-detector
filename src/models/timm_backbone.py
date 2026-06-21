import timm
import torch

from .base_model import BaseModel
from .heads import build_head, infer_backbone_out_dim


class TimmBackboneModel(BaseModel):
    """Generic timm-backbone wrapper with a binary classification head.

    All of this repo's model wrappers are functionally identical: load a timm
    backbone with ``num_classes=0`` (features only), discover the true output
    dim via ``infer_backbone_out_dim`` (``backbone.num_features`` is unreliable
    on some architectures — see CLAUDE.md), and attach ``Dropout -> Linear(.,1)``.
    The only per-arch differences (backbone name, dropout) come from ``cfg``,
    so one generic class covers every SOTA backbone we register.

    Used for the SOTA model set (EfficientNetV2-M / ConvNeXtV2-Base / MaxViT-Base
    teachers; MobileNetV4 / FastViT / EfficientFormerV2 students). The older
    family-specific wrappers (EfficientNetModel, MobileNetV3Model, MobileViTModel)
    are kept for the baseline comparison runs.
    """

    def __init__(self, cfg):
        super().__init__()
        backbone_name = cfg.model.backbone
        pretrained = cfg.model.get("pretrained", True)
        dropout = cfg.model.head.get("dropout", 0.2)

        self.backbone = timm.create_model(backbone_name, pretrained=pretrained, num_classes=0)
        in_features = infer_backbone_out_dim(self.backbone)
        self.head = build_head(in_features, dropout=dropout)

        if cfg.model.get("freeze_backbone", False):
            self.freeze_backbone()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Returns shape (B,) — raw logit for BCEWithLogitsLoss
        return self.head(self.backbone(x)).squeeze(1)
