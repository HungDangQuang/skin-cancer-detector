"""
Knowledge Distillation loss for binary classification.

Formula (Hinton et al. 2015, adapted for binary):
    L_total = alpha * L_hard + (1 - alpha) * L_soft

Where:
    L_hard  = FocalLoss(student_logit, true_label)
    alpha   = 0.3   (weight of hard-label loss)
    T       = 4.0   (temperature — softens distributions)

The soft term has two selectable variants (``soft_loss_type``):
    "bce" (default) = T^2 * BCE(sigmoid(student_logit / T), sigmoid(teacher_logit / T))
                      — the original Hinton-style soft loss at temperature T.
    "mse"           = MSE(student_logit, teacher_logit) [Kim et al. 2021] — matches
                      raw logits directly (~ KL at large T); no temperature, no T^2.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class BinaryDistillationLoss(nn.Module):
    """
    Combined KD loss for binary sigmoid classification.

    Args:
        temperature: T — divides both teacher and student logits before
                     computing soft targets. Higher T = softer distributions.
        alpha: Weight for the hard-label (focal) loss component.
               (1 - alpha) is the weight for the soft-label KD component.
               From proposal: alpha=0.3, so 30% hard + 70% soft.
        soft_loss_type: "bce" (default, original T^2-scaled soft BCE) or "mse"
               (Kim et al. 2021 — MSE on raw logits, no temperature/T^2).
        hard_loss_fn: Hard-label loss (BinaryFocalLoss).
    """

    def __init__(
        self,
        temperature: float = 4.0,
        alpha: float = 0.3,
        soft_loss_type: str = "bce",
        hard_loss_fn: nn.Module | None = None,
    ):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.soft_loss_type = soft_loss_type
        self.hard_loss_fn = hard_loss_fn or nn.BCEWithLogitsLoss()

    def forward(
        self,
        student_logits: torch.Tensor,
        teacher_logits: torch.Tensor,
        labels: torch.Tensor,
    ) -> tuple[torch.Tensor, dict]:
        """
        Args:
            student_logits: Raw student output, shape (B,).
            teacher_logits: Raw teacher output, shape (B,) — no gradient.
            labels: Binary integer labels, shape (B,).

        Returns:
            total_loss: Scalar tensor.
            components: Dict with 'hard_loss', 'soft_loss', 'total_loss'.
        """
        T = self.temperature

        # Hard-label loss: FocalLoss(student, true_labels)
        hard_loss = self.hard_loss_fn(student_logits, labels.float())

        # Soft-label loss — two variants (see class/module docstring):
        if self.soft_loss_type == "mse":
            # Kim et al. 2021: MSE on raw logits ~ KL at large T. Direct logit
            # matching, so NO temperature division and NO T^2 rescaling.
            soft_loss = F.mse_loss(student_logits, teacher_logits)
        else:  # "bce" — original behaviour
            # p_teacher = sigmoid(teacher_logit / T)
            # L_soft = BCE(sigmoid(student_logit / T), p_teacher) * T^2
            with torch.no_grad():
                soft_targets = torch.sigmoid(teacher_logits / T)
            soft_loss = F.binary_cross_entropy_with_logits(
                student_logits / T, soft_targets
            ) * (T ** 2)

        total_loss = self.alpha * hard_loss + (1.0 - self.alpha) * soft_loss

        return total_loss, {
            "hard_loss": hard_loss.item(),
            "soft_loss": soft_loss.item(),
            "total_loss": total_loss.item(),
        }
