import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
from PIL import Image

# Albumentations ops this project allows in the augmentation config. The
# pipeline is built from configs/augmentation/{light,heavy}.yaml (NOT hard-coded
# here) so the augmentation strength is a tunable knob. Each entry maps an op
# `name` -> a builder that consumes the remaining keys of the config dict as
# kwargs. Keep this to geometric/photometric, per-image, label-preserving ops.
_TRANSFORM_BUILDERS = {
    "HorizontalFlip": lambda p=0.5, **k: A.HorizontalFlip(p=p),
    "VerticalFlip": lambda p=0.5, **k: A.VerticalFlip(p=p),
    "RandomRotate90": lambda p=0.5, **k: A.RandomRotate90(p=p),
    "Rotate": lambda limit=180, p=0.5, **k: A.Rotate(limit=limit, p=p),
    "ShiftScaleRotate": lambda shift_limit=0.1, scale_limit=0.2, rotate_limit=180, p=0.5, **k: A.ShiftScaleRotate(
        shift_limit=shift_limit, scale_limit=scale_limit, rotate_limit=rotate_limit, p=p
    ),
    "RandomScale": lambda scale_limit=0.2, p=0.5, **k: A.RandomScale(scale_limit=scale_limit, p=p),
    "ColorJitter": lambda brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5, **k: A.ColorJitter(
        brightness=brightness, contrast=contrast, saturation=saturation, hue=hue, p=p
    ),
    "CLAHE": lambda clip_limit=2.0, p=0.2, **k: A.CLAHE(clip_limit=clip_limit, p=p),
    "GaussianBlur": lambda blur_limit=(3, 7), p=0.2, **k: A.GaussianBlur(blur_limit=tuple(blur_limit), p=p),
    "GaussNoise": lambda var_limit=(10.0, 50.0), p=0.3, **k: A.GaussNoise(var_limit=tuple(var_limit), p=p),
    "Normalize": lambda mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225), **k: A.Normalize(
        mean=list(mean), std=list(std)
    ),
}

# Augmentations the proposal/docs deliberately rejected for this problem
# (harmful for the rare class / inconsistent with KD soft targets). Enforced
# here so they cannot be silently re-introduced via the YAML config — see
# docs/PREPROCESSING.md. To revisit, update the docs first, then add a builder.
_FORBIDDEN_OPS = {"MixUp", "CutMix", "CoarseDropout", "Cutout", "GridDropout"}

# Default ImageNet normalization, used if the config omits a Normalize op.
_IMAGENET_NORMALIZE = A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])


def _build_op(entry: dict):
    """Map one config entry ({'name': ..., **params}) to an Albumentations op."""
    name = entry.get("name")
    if name is None:
        raise ValueError(f"Augmentation entry missing 'name': {entry}")
    if name in _FORBIDDEN_OPS:
        raise ValueError(
            f"Augmentation '{name}' is intentionally excluded for this project "
            f"(harmful for the rare class / inconsistent with KD) — see "
            f"docs/PREPROCESSING.md. Remove it from the augmentation config."
        )
    if name not in _TRANSFORM_BUILDERS:
        raise ValueError(
            f"Unknown augmentation '{name}'. Supported: {sorted(_TRANSFORM_BUILDERS)}. "
            f"(Forbidden by design: {sorted(_FORBIDDEN_OPS)}.)"
        )
    params = {k: v for k, v in entry.items() if k != "name"}
    return _TRANSFORM_BUILDERS[name](**params)


def build_transforms(cfg, split: str = "train"):
    """
    Build an Albumentations transform pipeline from the augmentation config.

    The op list comes from ``cfg.augmentation[split]`` (configs/augmentation/
    {light,heavy}.yaml), so augmentation strength is a tunable knob rather than
    hard-coded here. ``Resize`` is always prepended and ``ToTensorV2`` always
    appended; ``Normalize`` falls back to ImageNet stats if the config omits it.

    Args:
        cfg: full Hydra config (reads cfg.data.image_size and cfg.augmentation).
        split: 'train', 'val', or 'test'.

    Returns:
        A callable that accepts a PIL Image and returns a tensor.
    """
    data_cfg = getattr(cfg, "data", None)
    image_size = int(getattr(data_cfg, "image_size", 224)) if data_cfg is not None else 224

    aug_cfg = cfg.augmentation if hasattr(cfg, "augmentation") else None
    # val/test never use the train-time augmentation list.
    cfg_split = split if split == "train" else "val"

    ops = [A.Resize(image_size, image_size)]
    entries = None
    if aug_cfg is not None and hasattr(aug_cfg, cfg_split):
        entries = getattr(aug_cfg, cfg_split)

    if entries:
        has_normalize = False
        for entry in entries:
            # OmegaConf entries behave like dicts; normalize to a plain dict.
            entry = dict(entry)
            op = _build_op(entry)
            ops.append(op)
            if entry.get("name") == "Normalize":
                has_normalize = True
        if not has_normalize:
            ops.append(_IMAGENET_NORMALIZE)
    else:
        # No config (e.g. eval scripts without an augmentation group): bare
        # Resize -> Normalize -> ToTensorV2, matching the old val/test path.
        ops.append(_IMAGENET_NORMALIZE)

    ops.append(ToTensorV2())
    transform = A.Compose(ops)

    def apply(image: Image.Image):
        img_np = np.array(image)
        result = transform(image=img_np)
        return result["image"]

    return apply
