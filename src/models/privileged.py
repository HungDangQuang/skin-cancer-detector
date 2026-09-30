import torch
import torch.nn as nn

from src.utils.logger import get_logger

from .heads import build_head, infer_backbone_out_dim
from .timm_backbone import TimmBackboneModel

logger = get_logger(__name__)


class PrivilegedTimmBackboneModel(TimmBackboneModel):
    """Privileged (LUPI) teacher: image backbone ⊕ tabular metadata -> 1 logit.

    Direction A of docs/metadata_training_plan.md. A timm image backbone (built
    by ``TimmBackboneModel``) is fused with a small MLP over the standardized
    privileged metadata (ISIC ``tbp_lv_*``). Only the TEACHER sees metadata; the
    image-only student distills the FUSED feature structure via RKD
    (``src/training/feature_distillation.py`` — projector-free, so the teacher's
    larger fused dim vs the student's image dim is fine), so nothing on the
    student / ``.pte`` / benchmark path changes. This is the whole point of LUPI:
    ``tbp_lv_*`` (undeployable, needs Vectra 3D-TBP) leaks into the student only
    as relational structure, never as a student input.

    ``accepts_metadata = True`` tells ``Trainer`` / ``KDTrainer`` to feed
    ``(images, meta, mask)`` into ``forward`` / ``forward_features``.

    Config contract (``configs/teacher/<name>_privileged.yaml`` + ``data.metadata_cols``):
      * ``cfg.data.metadata_cols`` — the privileged columns; ``len`` is the tabular
        input dim (single source of truth; must be non-empty or ``__init__`` raises).
      * ``cfg.model.tab_hidden`` / ``cfg.model.tab_out`` — tabular MLP widths (default 64 / 64).
    """

    # Capability flag read by the trainers (BaseModel/TimmBackboneModel default
    # is image-only, i.e. no such attribute -> getattr(..., False)).
    accepts_metadata = True

    def __init__(self, cfg):
        super().__init__(cfg)  # builds self.backbone + self.head(image_dim)

        metadata_cols = cfg.data.get("metadata_cols", None) if "data" in cfg else None
        if not metadata_cols:
            raise ValueError(
                "PrivilegedTimmBackboneModel requires a non-empty data.metadata_cols "
                "(the privileged tabular inputs). Set it, or use a plain teacher."
            )
        self.n_meta = len(list(metadata_cols))
        tab_hidden = int(cfg.model.get("tab_hidden", 64))
        tab_out = int(cfg.model.get("tab_out", 64))
        dropout = cfg.model.head.get("dropout", 0.2)
        image_dim = infer_backbone_out_dim(self.backbone)

        self.tab_encoder = nn.Sequential(
            nn.Linear(self.n_meta, tab_hidden),
            nn.ReLU(inplace=True),
            nn.Linear(tab_hidden, tab_out),
            nn.ReLU(inplace=True),
        )
        # Rebuild the head for the FUSED dim — super() sized it for image-only.
        self.head = build_head(image_dim + tab_out, dropout=dropout)
        logger.info(
            "PrivilegedTimmBackboneModel: image_dim=%d + tab_out=%d (n_meta=%d) -> fused head.",
            image_dim, tab_out, self.n_meta,
        )

    def _encode_tab(self, x: torch.Tensor, meta, mask) -> torch.Tensor:
        """Tabular branch, masked so fully-absent rows (PAD) never contribute.

        meta is already standardized with NaN->0 by the dataset; mask is 1 where a
        column was present. A row with no present column (every PAD sample) is
        zeroed AFTER the encoder, so no gradient flows into the tabular MLP from
        it and the fused head sees ``img_feat ⊕ 0``.
        """
        if meta is None:
            meta = x.new_zeros((x.size(0), self.n_meta))
        tab = self.tab_encoder(meta)
        if mask is not None:
            sample_valid = (mask.sum(dim=1, keepdim=True) > 0).to(tab.dtype)
            tab = tab * sample_valid
        return tab

    def forward(self, x: torch.Tensor, meta=None, mask=None) -> torch.Tensor:
        img_feat = self.backbone(x)
        fused = torch.cat([img_feat, self._encode_tab(x, meta, mask)], dim=1)
        return self.head(fused).squeeze(1)

    def forward_features(self, x: torch.Tensor, meta=None, mask=None):
        """Return ``(fused_feat (B, image_dim+tab_out), logit (B,))``.

        MUST override BaseModel.forward_features (whose default assumes the plain
        ``head(backbone(x))`` layout) so RKD taps the FUSED feature and the logit
        stays bit-identical to ``forward``.
        """
        img_feat = self.backbone(x)
        fused = torch.cat([img_feat, self._encode_tab(x, meta, mask)], dim=1)
        return fused, self.head(fused).squeeze(1)
