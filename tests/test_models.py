import pytest
import torch
from omegaconf import OmegaConf

from src.models.registry import MODEL_REGISTRY, build_model


def make_cfg(model_name: str, backbone: str, dropout: float = 0.2):
    return OmegaConf.create({
        "model": {
            "name": model_name,
            "backbone": backbone,
            "num_classes": 1,
            "pretrained": False,
            "freeze_backbone": False,
            "head": {"dropout": dropout},
        },
        "device": "cpu",
    })


@pytest.mark.parametrize("model_name,backbone,dropout", [
    ("efficientnet_b4", "efficientnet_b4", 0.3),
    ("efficientnet_b0", "efficientnet_b0", 0.3),
    ("mobilenetv3_large", "mobilenetv3_large_100", 0.2),
    ("mobilevit_s", "mobilevit_s", 0.1),
])
def test_model_forward_shape(model_name, backbone, dropout):
    """Model output must be (B,) — raw logit for BCEWithLogitsLoss."""
    cfg = make_cfg(model_name, backbone, dropout)
    model = build_model(cfg)
    model.eval()
    x = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (2,), f"Expected (2,), got {out.shape}"


def test_model_registry_keys():
    assert "efficientnet_b4" in MODEL_REGISTRY   # teacher
    assert "efficientnet_b0" in MODEL_REGISTRY   # student 1
    assert "mobilenetv3_large" in MODEL_REGISTRY  # student 2
    assert "mobilevit_s" in MODEL_REGISTRY        # student 3


def test_unknown_model_raises():
    cfg = make_cfg("nonexistent_model", "nonexistent_model")
    with pytest.raises(ValueError, match="Unknown model"):
        build_model(cfg)


def test_num_parameters():
    cfg = make_cfg("efficientnet_b0", "efficientnet_b0")
    model = build_model(cfg)
    assert model.num_parameters() > 0


def test_sigmoid_output_range():
    """After sigmoid, output must be in [0, 1]."""
    cfg = make_cfg("efficientnet_b0", "efficientnet_b0")
    model = build_model(cfg)
    model.eval()
    x = torch.randn(4, 3, 224, 224)
    with torch.no_grad():
        probs = torch.sigmoid(model(x))
    assert probs.min() >= 0.0 and probs.max() <= 1.0
