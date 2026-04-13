import torch
import pytest
from omegaconf import OmegaConf

from src.training.losses import FocalLoss, build_loss


def make_loss_cfg(name: str, **kwargs):
    return OmegaConf.create({
        "training": {
            "loss": {"name": name, "use_class_weights": False, **kwargs}
        }
    })


def test_cross_entropy_loss():
    cfg = make_loss_cfg("cross_entropy", label_smoothing=0.0)
    loss_fn = build_loss(cfg)
    logits = torch.randn(4, 7)
    labels = torch.randint(0, 7, (4,))
    loss = loss_fn(logits, labels)
    assert loss.item() > 0


def test_focal_loss_shape():
    loss_fn = FocalLoss(gamma=2.0)
    logits = torch.randn(4, 7)
    labels = torch.randint(0, 7, (4,))
    loss = loss_fn(logits, labels)
    assert loss.ndim == 0  # scalar


def test_focal_loss_with_config():
    cfg = make_loss_cfg("focal", gamma=2.0)
    loss_fn = build_loss(cfg)
    logits = torch.randn(4, 7)
    labels = torch.randint(0, 7, (4,))
    loss = loss_fn(logits, labels)
    assert loss.item() >= 0


def test_unknown_loss_raises():
    cfg = make_loss_cfg("unsupported_loss")
    with pytest.raises(ValueError, match="Unknown loss"):
        build_loss(cfg)
