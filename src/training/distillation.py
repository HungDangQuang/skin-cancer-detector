"""
Knowledge Distillation loss for binary classification.

Formula (Hinton et al. 2015, adapted for binary):
    L_total = alpha * L_hard + (1 - alpha) * T^2 * L_soft

Where:
    L_hard  = FocalLoss(student_logit, true_label)
    L_soft  = BCE(sigmoid(student_logit / T), sigmoid(teacher_logit / T))
    alpha   = 0.3   (weight of hard-label loss)
    T       = 4.0   (temperature — softens distributions)
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
        hard_loss_fn: Hard-label loss (BinaryFocalLoss).
    """

    def __init__(
        self,
        temperature: float = 4.0,
        alpha: float = 0.3,
        hard_loss_fn: nn.Module | None = None,
    ):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
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

        # Soft-label loss: BCE with soft targets from teacher
        # p_teacher = sigmoid(teacher_logit / T)
        # p_student = sigmoid(student_logit / T)
        # L_soft = BCE(student_soft, teacher_soft) * T^2
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
