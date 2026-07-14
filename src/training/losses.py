import torch
import torch.nn as nn
import torch.nn.functional as F


class BinaryFocalLoss(nn.Module):
    """
    Binary focal loss for class-imbalanced binary classification.

    L = -alpha * (1-p)^gamma * log(p)       for y=1
      - (1-alpha) * p^gamma * log(1-p)       for y=0

    Operates on raw logits (no sigmoid needed on model output).
    Reference: Lin et al., "Focal Loss for Dense Object Detection" (2017)

    Args:
        gamma: Focusing parameter. Higher = more focus on hard examples.
        alpha: Weight in [0, 1] on the POSITIVE (malignant) class; the negative
               class gets (1 - alpha). The default 0.25 is the RetinaNet value
               (Lin et al. 2017): it *down-weights* the positive class and relies
               on gamma to concentrate loss on hard (mostly positive) examples.
               Here it stacks on the 1:5 DynamicUndersampledSampler, so the net
               positive weighting is (undersampler up-weight) x alpha -- the
               alpha=0.25-vs-0.75 ablation validates keeping 0.25. This is NOT the
               class prior (~0.004) and NOT 1 - prevalence.
    """

    def __init__(self, gamma: float = 2.0, alpha: float = 0.25):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: Raw model output, shape (B,).
            targets: Binary float labels, shape (B,). Must be float.
        """
        targets = targets.float()
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
        probs = torch.sigmoid(logits)
        pt = torch.where(targets == 1, probs, 1 - probs)
        alpha_t = torch.where(targets == 1,
                              torch.full_like(pt, self.alpha),
                              torch.full_like(pt, 1 - self.alpha))
        focal_loss = alpha_t * (1 - pt) ** self.gamma * bce
        return focal_loss.mean()


def build_loss(cfg) -> nn.Module:
    """
    Build the hard-label loss function from config.

    Supported: focal_loss, bce
    """
    loss_cfg = cfg.training.loss
    name = loss_cfg.name

    if name == "focal_loss":
        return BinaryFocalLoss(
            gamma=loss_cfg.get("gamma", 2.0),
            alpha=loss_cfg.get("alpha", 0.25),
        )
    elif name == "bce":
        return nn.BCEWithLogitsLoss()
    else:
        raise ValueError(f"Unknown loss '{name}'. Supported: focal_loss, bce")
