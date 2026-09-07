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
    ("repvit_m1_0", "repvit_m1_0.dist_in1k", 0.1),                           # student
    ("panderm", "vit_base_patch16_224", 0.3),                               # foundation teacher
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
    assert "panderm" in MODEL_REGISTRY  # domain-foundation teacher (out-of-timm)
    # Students (mobile-/on-device-latency-optimized)
    assert "mobilenetv4_conv_medium" in MODEL_REGISTRY
    assert "fastvit_sa12" in MODEL_REGISTRY
    assert "efficientformerv2_s2" in MODEL_REGISTRY
    assert "repvit_m1_0" in MODEL_REGISTRY


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


def make_panderm_cfg(weights_path=None, min_weight_match=0.5):
    cfg = make_cfg("panderm", "vit_base_patch16_224", dropout=0.3)
    cfg.model.weights_path = weights_path
    cfg.model.min_weight_match = min_weight_match
    return cfg


def test_panderm_loads_matching_foundation_weights(tmp_path):
    """A PanDerm-style checkpoint (backbone.* keys) loads into the ViT backbone."""
    ref = build_model(make_panderm_cfg())  # random-init, no weights
    # Fake a PanDerm checkpoint: container key "model", "backbone." prefix.
    fake = {"model": {f"backbone.{k}": torch.randn_like(v)
                      for k, v in ref.backbone.state_dict().items()}}
    ckpt_path = tmp_path / "panderm_fake.pth"
    torch.save(fake, ckpt_path)

    model = build_model(make_panderm_cfg(weights_path=str(ckpt_path), min_weight_match=0.9))
    # Every backbone tensor should now equal the checkpoint's (100% match).
    for k, v in model.backbone.state_dict().items():
        assert torch.allclose(v, fake["model"][f"backbone.{k}"]), f"{k} not loaded"


def test_panderm_raises_on_arch_mismatch(tmp_path):
    """A checkpoint that matches almost nothing must RAISE, not silently no-op."""
    bad = {"model": {"totally.unrelated.key": torch.zeros(3)}}
    ckpt_path = tmp_path / "panderm_bad.pth"
    torch.save(bad, ckpt_path)

    with pytest.raises(RuntimeError, match="matched only"):
        build_model(make_panderm_cfg(weights_path=str(ckpt_path), min_weight_match=0.5))
