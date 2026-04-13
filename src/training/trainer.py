from pathlib import Path

import torch
import torch.nn as nn
from tqdm import tqdm

from src.utils.logger import get_logger

logger = get_logger(__name__)


class Trainer:
    """
    Manages the training and validation loop.

    Usage:
        trainer = Trainer(cfg, model, datamodule, run_dir)
        trainer.fit()
    """

    def __init__(self, cfg, model: nn.Module, datamodule, run_dir: str | Path):
        self.cfg = cfg
        self.model = model
        self.datamodule = datamodule
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.device = torch.device(cfg.device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self._setup_training()

    def _setup_training(self) -> None:
        from src.training.losses import build_loss
        from src.training.optimizers import build_optimizer
        from src.training.schedulers import build_scheduler
        from src.training.callbacks import EarlyStopping, ModelCheckpoint
        from src.utils.class_weights import compute_weights_from_csv

        splits_dir = Path(self.cfg.data.splits_dir)
        class_weights = compute_weights_from_csv(splits_dir / "train_split.csv").to(self.device)

        self.criterion = build_loss(self.cfg, class_weights)
        self.optimizer = build_optimizer(self.cfg, self.model)
        self.scheduler = build_scheduler(self.cfg, self.optimizer)

        cb_cfg = self.cfg.training.callbacks
        self.early_stopping = EarlyStopping(
            patience=cb_cfg.early_stopping.patience,
            mode=cb_cfg.early_stopping.mode,
        ) if cb_cfg.early_stopping.enabled else None

        self.checkpoint = ModelCheckpoint(
            checkpoint_dir=self.run_dir / "checkpoints",
            monitor=cb_cfg.checkpoint.monitor,
            mode=cb_cfg.checkpoint.mode,
            save_last=cb_cfg.checkpoint.save_last,
        ) if cb_cfg.checkpoint.enabled else None

        self.history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    def fit(self) -> dict:
        """Run full training loop. Returns training history."""
        self.datamodule.setup()
        train_loader = self.datamodule.train_dataloader()
        val_loader = self.datamodule.val_dataloader()
        epochs = self.cfg.training.epochs

        for epoch in range(1, epochs + 1):
            train_metrics = self._train_epoch(train_loader, epoch, epochs)
            val_metrics = self._val_epoch(val_loader)

            self.scheduler.step()

            self.history["train_loss"].append(train_metrics["loss"])
            self.history["val_loss"].append(val_metrics["loss"])
            self.history["train_acc"].append(train_metrics["acc"])
            self.history["val_acc"].append(val_metrics["acc"])

            logger.info(
                f"Epoch {epoch}/{epochs} | "
                f"train_loss={train_metrics['loss']:.4f} train_acc={train_metrics['acc']:.4f} | "
                f"val_loss={val_metrics['loss']:.4f} val_acc={val_metrics['acc']:.4f}"
            )

            monitor_val = val_metrics.get(
                self.checkpoint.monitor.replace("val_", ""), val_metrics["loss"]
            ) if self.checkpoint else val_metrics["loss"]

            if self.checkpoint:
                self.checkpoint.step(
                    monitor_val, self.model, self.optimizer, epoch,
                    {**train_metrics, **{f"val_{k}": v for k, v in val_metrics.items()}}
                )

            if self.early_stopping and self.early_stopping.step(val_metrics["loss"]):
                logger.info("Early stopping triggered.")
                break

        return self.history

    def _train_epoch(self, loader, epoch: int, total_epochs: int) -> dict:
        self.model.train()
        total_loss, correct, total = 0.0, 0, 0
        grad_clip = self.cfg.training.get("grad_clip", None)

        pbar = tqdm(loader, desc=f"Train [{epoch}/{total_epochs}]", leave=False)
        for images, labels in pbar:
            images, labels = images.to(self.device), labels.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(images)
            loss = self.criterion(logits, labels)
            loss.backward()

            if grad_clip:
                nn.utils.clip_grad_norm_(self.model.parameters(), grad_clip)

            self.optimizer.step()

            total_loss += loss.item() * images.size(0)
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += images.size(0)
            pbar.set_postfix(loss=f"{loss.item():.4f}")

        return {"loss": total_loss / total, "acc": correct / total}

    @torch.no_grad()
    def _val_epoch(self, loader) -> dict:
        self.model.eval()
        total_loss, correct, total = 0.0, 0, 0

        for images, labels in tqdm(loader, desc="Val", leave=False):
            images, labels = images.to(self.device), labels.to(self.device)
            logits = self.model(images)
            loss = self.criterion(logits, labels)

            total_loss += loss.item() * images.size(0)
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += images.size(0)

        return {"loss": total_loss / total, "acc": correct / total}
