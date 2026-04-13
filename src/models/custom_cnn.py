import torch
import torch.nn as nn

from .base_model import BaseModel
from .heads import build_head


class ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, padding=kernel_size // 2, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class CustomCNN(BaseModel):
    """Baseline CNN built from scratch — no pretrained weights."""

    def __init__(self, cfg):
        super().__init__()
        num_classes = cfg.model.num_classes
        dropout = cfg.model.head.get("dropout", 0.5)
        hidden_dim = cfg.model.head.get("hidden_dim", 512)

        layer_cfgs = cfg.model.get("layers", [
            {"out_channels": 32, "kernel_size": 3},
            {"out_channels": 64, "kernel_size": 3},
            {"out_channels": 128, "kernel_size": 3},
            {"out_channels": 256, "kernel_size": 3},
        ])

        blocks = []
        in_channels = 3
        for lc in layer_cfgs:
            blocks.append(ConvBlock(in_channels, lc["out_channels"], lc.get("kernel_size", 3)))
            in_channels = lc["out_channels"]

        self.features = nn.Sequential(*blocks)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.head = build_head(in_channels, num_classes, dropout=dropout, hidden_dim=hidden_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.pool(x).flatten(1)
        return self.head(x)
