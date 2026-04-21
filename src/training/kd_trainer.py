"""
Knowledge Distillation Trainer.
Teacher is always frozen. Student is trained with BinaryDistillationLoss.
"""
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm

from src.training.distillation import BinaryDistillationLoss
from src.training.losses import build_loss
from src.training.optimizers import build_optimizer
from src.training.schedulers import build_scheduler
from src.training.callbacks import EarlyStopping, ModelCheckpoint
from src.utils.logger import get_logger

logger = get_logger(__name__)


class KDTrainer:
    """
    Trains a student model guided by a frozen teacher via knowledge distillation.

    Usage:
        trainer = KDTrainer(cfg, teacher, student, datamodule, run_dir)
        trainer.fit()
    """

    def __init__(
        self,
        cfg,
        teacher: nn.Module,
        student: nn.Module,
        datamodule,
        run_dir: str | Path,
    ):
        self.cfg = cfg
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.device = torch.device(cfg.device if torch.cuda.is_available() else "cpu")

        # Teacher: frozen, eval only
        self.teacher = teacher.to(self.device).eval()
        for param in self.teacher.parameters():
            param.requires_grad = False

        self.student = student.to(self.device)
        self.datamodule = datamodule
        self._setup_training()

    def _setup_training(self) -> None:
        hard_loss_fn = build_loss(self.cfg)

        kd_cfg = self.cfg.training.distillation
        self.criterion = BinaryDistillationLoss(
            temperature=kd_cfg.temperature,
            alpha=kd_cfg.alpha,
            hard_loss_fn=hard_loss_fn,
        )

        self.optimizer = build_optimizer(self.cfg, self.student)
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

        self.history = {
            "train_loss": [], "val_loss": [],
            "train_hard_loss": [], "train_soft_loss": [],
            "val_pauc": [],
        }

    def fit(self) -> dict:
        self.datamodule.setup()
        train_loader = self.datamodule.train_dataloader()
        val_loader = self.datamodule.val_dataloader()
        epochs = self.cfg.training.epochs

        for epoch in range(1, epochs + 1):
            self.datamodule.set_epoch(epoch)

            train_metrics = self._train_epoch(train_loader, epoch, epochs)
            val_metrics = self._val_epoch(val_loader)

            self.scheduler.step()

            self.history["train_loss"].append(train_metrics["loss"])
            self.history["train_hard_loss"].append(train_metrics["hard_loss"])
            self.history["train_soft_loss"].append(train_metrics["soft_loss"])
            self.history["val_loss"].append(val_metrics["loss"])
            self.history["val_pauc"].append(val_metrics.get("pauc_at_tpr80", 0.0))

            logger.info(
                f"Epoch {epoch}/{epochs} | "
                f"train_loss={train_metrics['loss']:.4f} "
                f"(hard={train_metrics['hard_loss']:.4f}, soft={train_metrics['soft_loss']:.4f}) | "
                f"val_loss={val_metrics['loss']:.4f} "
                f"val_pauc={val_metrics.get('pauc_at_tpr80', 0):.4f}"
            )

            if self.checkpoint:
                monitor_val = val_metrics.get("pauc_at_tpr80", val_metrics["loss"])
                self.checkpoint.step(monitor_val, self.student, self.optimizer, epoch, val_metrics)

            if self.early_stopping and self.early_stopping.step(val_metrics["loss"]):
                logger.info("Early stopping triggered.")
                break

        return self.history

    def _train_epoch(self, loader, epoch: int, total_epochs: int) -> dict:
        self.student.train()
        self.teacher.eval()
        total_loss, soft_sum, hard_sum, total = 0.0, 0.0, 0.0, 0

        pbar = tqdm(loader, desc=f"KD Train [{epoch}/{total_epochs}]", leave=False)
        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)

            with torch.no_grad():
                teacher_logits = self.teacher(images)

            self.optimizer.zero_grad()
            student_logits = self.student(images)

            loss, components = self.criterion(student_logits, teacher_logits, labels)
            loss.backward()

            grad_clip = self.cfg.training.get("grad_clip", None)
            if grad_clip:
                nn.utils.clip_grad_norm_(self.student.parameters(), grad_clip)

            self.optimizer.step()

            n = images.size(0)
            total_loss += components["total_loss"] * n
            hard_sum += components["hard_loss"] * n
            soft_sum += components["soft_loss"] * n
            total += n
            pbar.set_postfix(loss=f"{components['total_loss']:.4f}")

        return {
            "loss": total_loss / total,
            "hard_loss": hard_sum / total,
            "soft_loss": soft_sum / total,
        }

    @torch.no_grad()
    def _val_epoch(self, loader) -> dict:
        from src.evaluation.metrics import compute_metrics

        self.student.eval()
        total_loss, total = 0.0, 0
        all_labels, all_probs = [], []

        for images, labels in tqdm(loader, desc="Val", leave=False):
            images = images.to(self.device)
            teacher_logits = self.teacher(images)
            student_logits = self.student(images)

            loss, _ = self.criterion(student_logits, teacher_logits, labels.to(self.device))
            total_loss += loss.item() * images.size(0)
            total += images.size(0)
            all_probs.extend(torch.sigmoid(student_logits).cpu().numpy())
            all_labels.extend(labels.numpy())

        metrics = compute_metrics(all_labels, np.array(all_probs))
        metrics["loss"] = total_loss / total
        return metrics
