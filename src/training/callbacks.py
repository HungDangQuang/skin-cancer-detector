from pathlib import Path

import torch

from src.utils.logger import get_logger

logger = get_logger(__name__)


class EarlyStopping:
    """Stop training when a monitored metric stops improving."""

    def __init__(self, patience: int = 10, mode: str = "min", delta: float = 1e-4):
        self.patience = patience
        self.mode = mode
        self.delta = delta
        self.best = float("inf") if mode == "min" else float("-inf")
        self.counter = 0
        self.should_stop = False

    def step(self, value: float) -> bool:
        improved = (self.mode == "min" and value < self.best - self.delta) or \
                   (self.mode == "max" and value > self.best + self.delta)
        if improved:
            self.best = value
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
                logger.info(f"Early stopping triggered after {self.counter} epochs without improvement.")
        return self.should_stop


class ModelCheckpoint:
    """Save model checkpoint when a monitored metric improves."""

    def __init__(self, checkpoint_dir: str, monitor: str = "val_loss", mode: str = "min", save_last: bool = True):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor
        self.mode = mode
        self.save_last = save_last
        self.best = float("inf") if mode == "min" else float("-inf")

    def step(self, value: float, model: torch.nn.Module, optimizer, epoch: int, metrics: dict) -> bool:
        from src.utils.checkpoint import save_checkpoint

        improved = (self.mode == "min" and value < self.best) or \
                   (self.mode == "max" and value > self.best)

        if self.save_last:
            save_checkpoint(self.checkpoint_dir / "last_model.pth", model, optimizer, epoch, metrics)

        if improved:
            self.best = value
            save_checkpoint(self.checkpoint_dir / "best_model.pth", model, optimizer, epoch, metrics)
            logger.info(f"Saved best model (epoch {epoch}, {self.monitor}={value:.4f})")

        return improved
