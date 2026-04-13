import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """
    Focal loss for class-imbalanced multi-class classification.
    Reference: https://arxiv.org/abs/1708.02002
    """

    def __init__(self, gamma: float = 2.0, weight: torch.Tensor | None = None, reduction: str = "mean"):
        super().__init__()
        self.gamma = gamma
        self.weight = weight
        self.reduction = reduction

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(inputs, targets, weight=self.weight, reduction="none")
        pt = torch.exp(-ce_loss)
        focal_loss = (1 - pt) ** self.gamma * ce_loss

        if self.reduction == "mean":
            return focal_loss.mean()
        elif self.reduction == "sum":
            return focal_loss.sum()
        return focal_loss


def build_loss(cfg, class_weights: torch.Tensor | None = None) -> nn.Module:
    """
    Build loss function from config.

    Supported: cross_entropy, focal, label_smoothing
    """
    loss_cfg = cfg.training.loss
    name = loss_cfg.name
    use_weights = loss_cfg.get("use_class_weights", True)
    weight = class_weights if use_weights and class_weights is not None else None

    if name == "cross_entropy":
        smoothing = loss_cfg.get("label_smoothing", 0.0)
        return nn.CrossEntropyLoss(weight=weight, label_smoothing=smoothing)

    elif name == "focal":
        gamma = loss_cfg.get("gamma", 2.0)
        return FocalLoss(gamma=gamma, weight=weight)

    else:
        raise ValueError(f"Unknown loss '{name}'. Supported: cross_entropy, focal")
