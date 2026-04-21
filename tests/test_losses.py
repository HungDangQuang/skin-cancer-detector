import torch
import pytest
from omegaconf import OmegaConf

from src.training.losses import BinaryFocalLoss, build_loss
from src.training.distillation import BinaryDistillationLoss


def make_loss_cfg(name: str, **kwargs):
    return OmegaConf.create({
        "training": {
            "loss": {"name": name, **kwargs}
        }
    })


def test_binary_focal_loss_shape():
    loss_fn = BinaryFocalLoss(gamma=2.0, alpha=0.25)
    logits = torch.randn(4)
    labels = torch.randint(0, 2, (4,)).float()
    loss = loss_fn(logits, labels)
    assert loss.ndim == 0  # scalar


def test_binary_focal_loss_nonnegative():
    loss_fn = BinaryFocalLoss(gamma=2.0, alpha=0.25)
    logits = torch.randn(8)
    labels = torch.randint(0, 2, (8,)).float()
    assert loss_fn(logits, labels).item() >= 0


def test_build_focal_loss():
    cfg = make_loss_cfg("focal_loss", gamma=2.0, alpha=0.25)
    loss_fn = build_loss(cfg)
    logits = torch.randn(4)
    labels = torch.randint(0, 2, (4,)).float()
    assert build_loss(cfg)(logits, labels).item() >= 0


def test_build_bce_loss():
    cfg = make_loss_cfg("bce")
    loss_fn = build_loss(cfg)
    logits = torch.randn(4)
    labels = torch.randint(0, 2, (4,)).float()
    assert loss_fn(logits, labels).item() >= 0


def test_unknown_loss_raises():
    cfg = make_loss_cfg("unsupported_loss")
    with pytest.raises(ValueError, match="Unknown loss"):
        build_loss(cfg)


def test_distillation_loss_components():
    loss_fn = BinaryDistillationLoss(temperature=4.0, alpha=0.3)
    student_logits = torch.randn(4)
    teacher_logits = torch.randn(4)
    labels = torch.randint(0, 2, (4,))
    loss, components = loss_fn(student_logits, teacher_logits, labels)
    assert loss.ndim == 0
    assert "hard_loss" in components and "soft_loss" in components
    assert components["total_loss"] >= 0


def test_distillation_alpha_weighting():
    """Total loss should be alpha*hard + (1-alpha)*soft."""
    alpha = 0.3
    loss_fn = BinaryDistillationLoss(temperature=4.0, alpha=alpha)
    student_logits = torch.randn(4)
    teacher_logits = torch.randn(4)
    labels = torch.randint(0, 2, (4,))
    _, components = loss_fn(student_logits, teacher_logits, labels)
    expected = alpha * components["hard_loss"] + (1 - alpha) * components["soft_loss"]
    assert abs(components["total_loss"] - expected) < 1e-5
