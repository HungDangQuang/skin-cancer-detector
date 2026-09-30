import json
from pathlib import Path

import torch
import torch.nn as nn
from tqdm import tqdm

from src.utils.batch import unpack_batch
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Trainer:
    """
    Standalone trainer for the teacher model (no distillation).
    Uses binary focal loss and sigmoid output.
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

        self.criterion = build_loss(self.cfg)
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

        self.history = {"train_loss": [], "val_loss": [], "val_pauc": []}
        # Best-epoch val metrics (aligned to the checkpoint monitor) — persisted
        # as val_metrics.json so the val-vs-test gap (overfitting signal) is
        # computable per fold without re-running inference.
        self.best_val_metrics = None
        self._best_monitor_val = None

    def fit(self) -> dict:
        from src.evaluation.metrics import class_prevalence_baselines

        self.datamodule.setup()
        train_loader = self.datamodule.train_dataloader()
        val_loader = self.datamodule.val_dataloader()
        epochs = self.cfg.training.epochs

        val_prev = class_prevalence_baselines(self.datamodule._val_dataset.labels)
        logger.info(
            f"Val set: {val_prev['n_negative']} benign + {val_prev['n_positive']} malignant "
            f"({val_prev['positive_rate']*100:.2f}% positive) | "
            f"majority-class baseline acc={val_prev['majority_class_accuracy']:.4f} | "
            f"random-classifier AUC=0.5000"
        )

        for epoch in range(1, epochs + 1):
            self.datamodule.set_epoch(epoch)

            train_metrics = self._train_epoch(train_loader, epoch, epochs)
            val_metrics = self._val_epoch(val_loader)

            self.scheduler.step()

            self.history["train_loss"].append(train_metrics["loss"])
            self.history["val_loss"].append(val_metrics["loss"])
            self.history["val_pauc"].append(val_metrics.get("pauc_at_tpr80", 0.0))

            logger.info(
                f"Epoch {epoch}/{epochs} | "
                f"train_loss={train_metrics['loss']:.4f} | "
                f"val_loss={val_metrics['loss']:.4f} "
                f"val_pauc={val_metrics.get('pauc_at_tpr80', 0):.4f} "
                f"acc={val_metrics.get('accuracy', 0):.4f} "
                f"prec={val_metrics.get('precision', 0):.4f} "
                f"sens={val_metrics.get('sensitivity', 0):.4f} "
                f"spec={val_metrics.get('specificity', 0):.4f} "
                f"f1={val_metrics.get('f1_score', 0):.4f}"
            )

            monitor_val = val_metrics.get("pauc_at_tpr80", val_metrics["loss"])
            if self.checkpoint:
                self.checkpoint.step(monitor_val, self.model, self.optimizer, epoch, val_metrics)

            # Track best-epoch val metrics (higher pauc is better), aligned to
            # the checkpoint's best_model.pth so val_metrics.json describes the
            # checkpoint that test_metrics.json later evaluates.
            if self._best_monitor_val is None or monitor_val > self._best_monitor_val:
                self._best_monitor_val = monitor_val
                self.best_val_metrics = {**val_metrics, "best_epoch": epoch}

            if self.early_stopping and self.early_stopping.step(val_metrics["loss"]):
                logger.info("Early stopping triggered.")
                break

        self._save_val_metrics()
        return self.history

    def _save_val_metrics(self) -> None:
        """Write best-epoch val metrics to run_dir/val_metrics.json (scalars only)."""
        if self.best_val_metrics is None:
            return
        serializable = {k: v for k, v in self.best_val_metrics.items() if isinstance(v, (int, float, str))}
        path = self.run_dir / "val_metrics.json"
        with open(path, "w") as f:
            json.dump(serializable, f, indent=2)
        logger.info(f"Best-epoch val metrics saved to {path}")

    def _train_epoch(self, loader, epoch: int, total_epochs: int) -> dict:
        self.model.train()
        total_loss, total = 0.0, 0
        grad_clip = self.cfg.training.get("grad_clip", None)

        pbar = tqdm(loader, desc=f"Train [{epoch}/{total_epochs}]", leave=False)
        for batch in pbar:
            images, meta, mask, labels = unpack_batch(batch)
            images = images.to(self.device)
            labels = labels.float().to(self.device)
            if meta is not None:
                meta, mask = meta.to(self.device), mask.to(self.device)

            self.optimizer.zero_grad()
            # Privileged teacher (direction A) takes (images, meta, mask); the
            # image-only path is unchanged.
            logits = self.model(images, meta, mask) if meta is not None else self.model(images)
            loss = self.criterion(logits, labels)
            loss.backward()

            if grad_clip:
                nn.utils.clip_grad_norm_(self.model.parameters(), grad_clip)

            self.optimizer.step()
            total_loss += loss.item() * images.size(0)
            total += images.size(0)
            pbar.set_postfix(loss=f"{loss.item():.4f}")

        return {"loss": total_loss / total}

    @torch.no_grad()
    def _val_epoch(self, loader) -> dict:
        import numpy as np
        from src.evaluation.metrics import compute_metrics

        self.model.eval()
        total_loss, total = 0.0, 0
        all_labels, all_probs = [], []

        for batch in tqdm(loader, desc="Val", leave=False):
            images, meta, mask, labels = unpack_batch(batch)
            images = images.to(self.device)
            labels_float = labels.float().to(self.device)
            if meta is not None:
                meta, mask = meta.to(self.device), mask.to(self.device)

            logits = self.model(images, meta, mask) if meta is not None else self.model(images)
            loss = self.criterion(logits, labels_float)

            total_loss += loss.item() * images.size(0)
            total += images.size(0)
            all_probs.extend(torch.sigmoid(logits).cpu().numpy())
            all_labels.extend(labels.numpy())

        metrics = compute_metrics(all_labels, np.array(all_probs))
        metrics["loss"] = total_loss / total
        return metrics
