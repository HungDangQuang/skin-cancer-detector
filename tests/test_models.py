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
    ("efficientnetv2_m", "tf_efficientnetv2_m.in21k_ft_in1k", 0.3),          # teacher
    ("mobilenetv4_conv_medium", "mobilenetv4_conv_medium.e500_r224_in1k", 0.2),  # student
    ("fastvit_sa12", "fastvit_sa12.apple_in1k", 0.1),                        # student
    ("efficientformerv2_s2", "efficientformerv2_s2.snap_dist_in1k", 0.1),    # student
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
    # Teachers (high-capacity, frozen during KD)
    assert "efficientnetv2_m" in MODEL_REGISTRY
    assert "convnextv2_base" in MODEL_REGISTRY
    assert "maxvit_base" in MODEL_REGISTRY
    # Students (mobile-/on-device-latency-optimized)
    assert "mobilenetv4_conv_medium" in MODEL_REGISTRY
    assert "fastvit_sa12" in MODEL_REGISTRY
    assert "efficientformerv2_s2" in MODEL_REGISTRY


def test_unknown_model_raises():
    cfg = make_cfg("nonexistent_model", "nonexistent_model")
    with pytest.raises(ValueError, match="Unknown model"):
        build_model(cfg)


def test_num_parameters():
    cfg = make_cfg("mobilenetv4_conv_medium", "mobilenetv4_conv_medium.e500_r224_in1k")
    model = build_model(cfg)
    assert model.num_parameters() > 0


def test_sigmoid_output_range():
    """After sigmoid, output must be in [0, 1]."""
    cfg = make_cfg("mobilenetv4_conv_medium", "mobilenetv4_conv_medium.e500_r224_in1k")
    model = build_model(cfg)
    model.eval()
    x = torch.randn(4, 3, 224, 224)
    with torch.no_grad():
        probs = torch.sigmoid(model(x))
    assert probs.min() >= 0.0 and probs.max() <= 1.0
