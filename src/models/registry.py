from omegaconf import OmegaConf, open_dict

from .efficientnet import EfficientNetModel
from .mobilenet import MobileNetV3Model
from .mobilevit import MobileViTModel

MODEL_REGISTRY: dict = {
    # Teacher
    "efficientnet_b4": EfficientNetModel,
    # Students
    "efficientnet_b0": EfficientNetModel,
    "mobilenetv3_large": MobileNetV3Model,
    "mobilevit_s": MobileViTModel,
}


def build_model(cfg):
    """Instantiate the model specified in cfg.model.name."""
    name = cfg.model.name
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model '{name}'. Available: {list(MODEL_REGISTRY.keys())}")
    return MODEL_REGISTRY[name](cfg)


def build_model_from_name(model_name: str, base_cfg) -> tuple:
    """
    Convenience helper for scripts that need to build a model by name.

    Looks up the model config in cfg.teacher or cfg.student,
    merges it into base_cfg under 'model', and returns (model, merged_cfg).

    Args:
        model_name: One of the keys in MODEL_REGISTRY.
        base_cfg: The full Hydra config (must have cfg.teacher and cfg.student).
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model '{model_name}'. Available: {list(MODEL_REGISTRY.keys())}")

    if base_cfg.teacher.name == model_name:
        model_subcfg = base_cfg.teacher
    elif base_cfg.student.name == model_name:
        model_subcfg = base_cfg.student
    else:
        raise ValueError(
            f"Model '{model_name}' not found in cfg.teacher or cfg.student. "
            f"Teacher: {base_cfg.teacher.name}, Student: {base_cfg.student.name}"
        )

    with open_dict(base_cfg):
        merged_cfg = OmegaConf.merge(base_cfg, {"model": OmegaConf.to_container(model_subcfg, resolve=True)})
    model = MODEL_REGISTRY[model_name](merged_cfg)
    return model, merged_cfg
