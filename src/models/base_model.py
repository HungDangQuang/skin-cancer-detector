from abc import ABC, abstractmethod

import torch
import torch.nn as nn


class BaseModel(nn.Module, ABC):
    """Abstract base class for all models in the registry."""

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. Returns logits of shape (batch, num_classes)."""
        ...

    def num_parameters(self, trainable_only: bool = True) -> int:
        if trainable_only:
            return sum(p.numel() for p in self.parameters() if p.requires_grad)
        return sum(p.numel() for p in self.parameters())

    def freeze_backbone(self) -> None:
        """Freeze all layers except the classification head."""
        for name, param in self.named_parameters():
            if "head" not in name and "classifier" not in name and "fc" not in name:
                param.requires_grad = False

    def unfreeze(self) -> None:
        """Unfreeze all parameters."""
        for param in self.parameters():
            param.requires_grad = True
