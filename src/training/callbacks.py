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

    def __init__(
        self,
        checkpoint_dir: str,
        monitor: str = "val_loss",
        mode: str = "min",
        save_last: bool = True,
        filename: str = "best_model.pth",
    ):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor
        self.mode = mode
        self.save_last = save_last
        self.filename = filename
        self.best = float("inf") if mode == "min" else float("-inf")

    def step(self, value: float, model: torch.nn.Module, optimizer, epoch: int, metrics: dict) -> bool:
        from src.utils.checkpoint import save_checkpoint

        improved = (self.mode == "min" and value < self.best) or \
                   (self.mode == "max" and value > self.best)

        if self.save_last:
            save_checkpoint(self.checkpoint_dir / "last_model.pth", model, optimizer, epoch, metrics)

        if improved:
            self.best = value
            save_checkpoint(self.checkpoint_dir / self.filename, model, optimizer, epoch, metrics)
            # The default line is grepped by eval-results/assess-training.md — keep it.
            what = "best model" if self.filename == "best_model.pth" else self.filename
            logger.info(f"Saved {what} (epoch {epoch}, {self.monitor}={value:.4f})")

        return improved


# Val metrics an extra checkpoint may track. All are higher-is-better, so the
# extra checkpoints always use mode="max".
EXTRA_MONITOR_KEYS = ("auprc", "auc_roc", "pauc_at_tpr80", "sens_at_90spec", "sens_at_95spec")


class ExtraCheckpoints:
    """Additional best-by-<metric> checkpoints alongside the main best_model.pth.

    ``training.callbacks.checkpoint.extra_monitors: [auprc]`` keeps, for each
    listed val metric, ``checkpoints/best_model_<m>.pth`` (the first epoch that
    reaches the best value, like ``best_model.pth``) and writes the matching
    best-epoch val metrics to ``run_dir/val_metrics_<m>.json``. Empty list (the
    default) -> no extra file is written and nothing else changes.
    """

    def __init__(self, monitors, checkpoint_dir: str | Path, run_dir: str | Path):
        monitors = list(monitors or [])
        bad = [m for m in monitors if m not in EXTRA_MONITOR_KEYS]
        if bad:
            raise ValueError(f"extra_monitors {bad} not supported; allowed: {EXTRA_MONITOR_KEYS}")
        self.run_dir = Path(run_dir)
        self.checkpoints = {
            m: ModelCheckpoint(checkpoint_dir, monitor=m, mode="max", save_last=False,
                               filename=f"best_model_{m}.pth")
            for m in monitors
        }
        self.best_val_metrics = {m: None for m in monitors}

    def step(self, val_metrics: dict, model: torch.nn.Module, optimizer, epoch: int) -> None:
        for m, ckpt in self.checkpoints.items():
            if ckpt.step(val_metrics[m], model, optimizer, epoch, val_metrics):
                self.best_val_metrics[m] = {**val_metrics, "best_epoch": epoch}

    def save_val_metrics(self) -> None:
        import json

        for m, best in self.best_val_metrics.items():
            if best is None:
                continue
            path = self.run_dir / f"val_metrics_{m}.json"
            with open(path, "w") as f:
                json.dump({k: v for k, v in best.items() if isinstance(v, (int, float, str))}, f, indent=2)
            logger.info(f"Best-by-{m} val metrics saved to {path} (epoch {best['best_epoch']})")
