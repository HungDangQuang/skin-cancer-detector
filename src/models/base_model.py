from abc import ABC, abstractmethod

import torch
import torch.nn as nn


class BaseModel(nn.Module, ABC):
    """Abstract base class for all models in the registry."""

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. Returns raw logit of shape (batch,) for binary classification."""
        ...

    def forward_features(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Return ``(features (B, C), logit (B,))`` from a single backbone pass.

        Used by feature-based / relational KD (src/training/feature_distillation.py).
        The default assumes the ``head(backbone(x)).squeeze(1)`` layout shared by
        every wrapper in this repo — the timm backbone (``num_classes=0``) emits a
        pooled ``(B, C)`` vector and ``head`` is ``Dropout -> Linear(C, 1)``. A
        subclass whose ``forward`` deviates from this layout MUST override this too,
        keeping the returned logit bit-identical to ``forward(x)``.
        """
        features = self.backbone(x)
        return features, self.head(features).squeeze(1)

    def num_parameters(self, trainable_only: bool = True) -> int:
        if trainable_only:
            return sum(p.numel() for p in self.parameters() if p.requires_grad)
        return sum(p.numel() for p in self.parameters())

    def freeze_backbone(self) -> None:
        """Freeze all layers except the classification head."""
        for name, param in self.named_parameters():
            if "head" not in name:
                param.requires_grad = False

    def unfreeze(self) -> None:
        """Unfreeze all parameters."""
        for param in self.parameters():
            param.requires_grad = True
