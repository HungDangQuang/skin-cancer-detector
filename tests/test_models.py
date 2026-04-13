import pytest
import torch
from omegaconf import OmegaConf

from src.models.registry import MODEL_REGISTRY, build_model


def make_cfg(model_name: str):
    return OmegaConf.create({
        "model": {
            "name": model_name,
            "num_classes": 7,
            "pretrained": False,
            "freeze_backbone": False,
            "head": {"dropout": 0.3, "hidden_dim": None},
        },
        "device": "cpu",
    })


@pytest.mark.parametrize("model_name", ["custom_cnn"])
def test_model_forward_shape(model_name):
    cfg = make_cfg(model_name)
    model = build_model(cfg)
    model.eval()
    x = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (2, 7), f"Expected (2, 7), got {out.shape}"


def test_model_registry_keys():
    assert "custom_cnn" in MODEL_REGISTRY
    assert "efficientnet_b3" in MODEL_REGISTRY
    assert "resnet50" in MODEL_REGISTRY


def test_unknown_model_raises():
    cfg = make_cfg("nonexistent_model")
    with pytest.raises(ValueError, match="Unknown model"):
        build_model(cfg)


def test_num_parameters():
    cfg = make_cfg("custom_cnn")
    model = build_model(cfg)
    assert model.num_parameters() > 0
