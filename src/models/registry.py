from .custom_cnn import CustomCNN
from .efficientnet import EfficientNetModel
from .resnet import ResNetModel

MODEL_REGISTRY: dict = {
    "custom_cnn": CustomCNN,
    "efficientnet_b3": EfficientNetModel,
    "efficientnet_b4": EfficientNetModel,
    "efficientnet_b5": EfficientNetModel,
    "resnet50": ResNetModel,
    "resnet34": ResNetModel,
}


def build_model(cfg):
    """Instantiate the model specified in cfg.model.name."""
    name = cfg.model.name
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model '{name}'. Available: {list(MODEL_REGISTRY.keys())}")
    return MODEL_REGISTRY[name](cfg)
