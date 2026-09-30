import torch

from src.utils.logger import get_logger

from .timm_backbone import TimmBackboneModel

logger = get_logger(__name__)

# state_dict wrapper keys PanDerm / BEiT-style checkpoints nest the weights under.
_CKPT_CONTAINER_KEYS = ("model", "module", "state_dict", "model_ema")
# key prefixes to strip so a `backbone.blocks.0...` checkpoint matches a bare
# timm `blocks.0...` backbone state_dict.
_STRIP_PREFIXES = ("backbone.", "encoder.", "module.", "model.")


class PanDermModel(TimmBackboneModel):
    """PanDerm dermatology-foundation teacher (ViT-B/16, BEiT-style).

    PanDerm (Nature Medicine 2025, github.com/SiyuanYan1/PanDerm) is pretrained
    on ~2.1M skin images and is the project's domain-foundation teacher. It is
    **not** a ``timm`` model name — it ships as a BEiT-style ViT-B/16 checkpoint
    (``panderm_bb_data6_checkpoint-499.pth``, Google Drive, CC-BY-NC-4.0), so
    ``TimmBackboneModel`` (which calls ``timm.create_model`` by name) cannot load
    it directly.

    This wrapper reuses the whole ``TimmBackboneModel`` machinery — it builds a
    structurally-compatible timm ViT-B/16 backbone (``cfg.model.backbone``,
    ``num_classes=0`` -> pooled 768-d feature) plus the standard
    ``Dropout -> Linear(768, 1)`` head, so ``forward`` / ``forward_features``
    (used by RKD) are inherited unchanged — and then loads the PanDerm foundation
    weights on top of the backbone with a **loud, tolerant remapping loader**.

    Config contract (``configs/teacher/panderm.yaml``):

    * ``pretrained: false``   — PanDerm weights replace timm ImageNet init.
    * ``weights_path``        — abs path to the downloaded PanDerm checkpoint on
      the server, or ``null`` to skip the foundation load. When null AND
      ``pretrained`` is false the backbone is **random-initialized**; this is the
      correct state only when a fine-tuned ``best_model.pth`` is loaded over the
      model afterwards (the KD / eval build path in ``train_student.py`` /
      ``evaluate.py``). For the teacher-*training* run ``weights_path`` MUST be
      set, else the "foundation teacher" is a random net — hence the explicit
      warning below.
    * ``min_weight_match``    — raise if fewer than this fraction of backbone
      tensors match the checkpoint (catches a wrong ``backbone`` arch instead of
      silently training an almost-random net).

    Architecture / normalization must be verified on the server against the real
    checkpoint before a full run — see docs/SOTA_MODEL_DECISION_2026-07.md §5.
    """

    def __init__(self, cfg):
        super().__init__(cfg)  # timm ViT backbone (num_classes=0) + build_head

        weights_path = cfg.model.get("weights_path", None)
        pretrained = cfg.model.get("pretrained", False)
        if weights_path:
            min_match = float(cfg.model.get("min_weight_match", 0.5))
            self._load_panderm_weights(str(weights_path), min_match=min_match)
        elif not pretrained:
            # Neither timm-pretrained nor a PanDerm checkpoint: the backbone is
            # random-initialized. Fine ONLY when best_model.pth is loaded over it
            # (KD/eval); a silent scientific defect for teacher training.
            logger.warning(
                "PanDermModel built with pretrained=false and weights_path=null -> "
                "backbone is RANDOM-INITIALIZED. This is correct only for the KD/eval "
                "build (a fine-tuned best_model.pth is loaded over it). For the "
                "teacher-TRAINING run, set teacher.weights_path to the downloaded "
                "PanDerm checkpoint (docs/SOTA_MODEL_DECISION_2026-07.md §5)."
            )

    def _load_panderm_weights(self, weights_path: str, min_match: float = 0.5) -> None:
        """Load PanDerm foundation weights into ``self.backbone``.

        Unwraps the common checkpoint container keys, strips backbone/encoder
        prefixes, keeps only tensors whose name AND shape match the timm backbone,
        loads them (``strict=False``), logs the match ratio, and raises if the
        ratio is below ``min_match`` (a wrong ``cfg.model.backbone`` arch would
        otherwise load ~nothing and leave a near-random "foundation" teacher).
        """
        # weights_only=False: a third-party foundation checkpoint carries non-tensor
        # metadata (args / epoch / optimizer). torch>=2.6 defaults weights_only=True,
        # which would raise on those; we only pull tensors out below. (kwarg exists
        # since torch 1.13, so this is safe on the cluster's older torch too.)
        ckpt = torch.load(weights_path, map_location="cpu", weights_only=False)
        for key in _CKPT_CONTAINER_KEYS:
            if isinstance(ckpt, dict) and isinstance(ckpt.get(key), dict):
                ckpt = ckpt[key]
                break

        remapped = {}
        for k, v in ckpt.items():
            name = k
            for prefix in _STRIP_PREFIXES:
                if name.startswith(prefix):
                    name = name[len(prefix):]
                    break
            remapped[name] = v

        backbone_sd = self.backbone.state_dict()
        matched = {
            k: v for k, v in remapped.items()
            if k in backbone_sd and v.shape == backbone_sd[k].shape
        }
        ratio = len(matched) / max(len(backbone_sd), 1)

        result = self.backbone.load_state_dict(matched, strict=False)
        logger.info(
            "PanDerm foundation weights: matched %d/%d backbone tensors (%.1f%%) from %s "
            "| missing=%d unexpected=%d",
            len(matched), len(backbone_sd), 100.0 * ratio, weights_path,
            len(result.missing_keys), len(result.unexpected_keys),
        )
        if ratio < min_match:
            backbone_name = self.backbone.__class__.__name__
            raise RuntimeError(
                f"PanDerm weight load matched only {ratio:.1%} of the backbone "
                f"(< min_weight_match={min_match:.0%}). The timm arch "
                f"(cfg.model.backbone -> {backbone_name}) likely does not match the "
                f"checkpoint layout. If PanDerm is BEiT-style, try "
                f"backbone=beit_base_patch16_224; otherwise verify the checkpoint keys "
                f"on the server (docs/SOTA_MODEL_DECISION_2026-07.md §5)."
            )
