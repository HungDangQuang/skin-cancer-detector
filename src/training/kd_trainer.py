"""
Knowledge Distillation Trainer.
Teacher is always frozen. Student is trained with BinaryDistillationLoss.
"""
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm

from src.training.distillation import BinaryDistillationLoss
from src.training.feature_distillation import RKDLoss
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
            soft_loss_type=kd_cfg.get("soft_loss_type", "bce"),
            hard_loss_fn=hard_loss_fn,
        )

        # Optional feature-based (relational) KD — opt-in via a `feature_kd` block
        # in the training config (present only in distillation_rkd.yaml). Absent
        # -> self.rkd is None -> the trainer behaves exactly like plain logit KD.
        fk = kd_cfg.get("feature_kd", None)
        self.rkd = RKDLoss(fk.weight_dist, fk.weight_angle) if fk else None
        if self.rkd is not None:
            logger.info(
                f"Feature KD enabled: RKD(weight_dist={fk.weight_dist}, "
                f"weight_angle={fk.weight_angle})"
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

        # train_rkd_loss is ALWAYS declared and ALWAYS appended each epoch (0.0
        # when RKD is off), so the history lists never desync — the trainer's
        # historical shape-mismatch gotcha. It is not plotted / read elsewhere,
        # so a plain-KD run's observable behaviour is unchanged.
        self.history = {
            "train_loss": [], "val_loss": [],
            "train_hard_loss": [], "train_soft_loss": [],
            "train_rkd_loss": [],
            "val_pauc": [],
        }
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
            self.history["train_hard_loss"].append(train_metrics["hard_loss"])
            self.history["train_soft_loss"].append(train_metrics["soft_loss"])
            self.history["train_rkd_loss"].append(train_metrics["rkd_loss"])
            self.history["val_loss"].append(val_metrics["loss"])
            self.history["val_pauc"].append(val_metrics.get("pauc_at_tpr80", 0.0))

            logger.info(
                f"Epoch {epoch}/{epochs} | "
                f"train_loss={train_metrics['loss']:.4f} "
                f"(hard={train_metrics['hard_loss']:.4f}, soft={train_metrics['soft_loss']:.4f}, "
                f"rkd={train_metrics['rkd_loss']:.4f}) | "
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
                self.checkpoint.step(monitor_val, self.student, self.optimizer, epoch, val_metrics)

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
        self.student.train()
        self.teacher.eval()
        total_loss, soft_sum, hard_sum, rkd_sum, total = 0.0, 0.0, 0.0, 0.0, 0

        pbar = tqdm(loader, desc=f"KD Train [{epoch}/{total_epochs}]", leave=False)
        for images, labels in pbar:
            images = images.to(self.device)
            labels = labels.to(self.device)

            # Feature KD needs the penultimate features -> forward_features; plain
            # logit KD uses the cheaper forward(). Teacher is always frozen/no_grad.
            with torch.no_grad():
                if self.rkd is not None:
                    teacher_feat, teacher_logits = self.teacher.forward_features(images)
                else:
                    teacher_logits = self.teacher(images)

            self.optimizer.zero_grad()
            if self.rkd is not None:
                student_feat, student_logits = self.student.forward_features(images)
            else:
                student_logits = self.student(images)

            loss, components = self.criterion(student_logits, teacher_logits, labels)
            rkd_val = 0.0
            if self.rkd is not None:
                rkd_loss = self.rkd(student_feat, teacher_feat)
                loss = loss + rkd_loss  # gradient now includes the relational term
                rkd_val = rkd_loss.item()
            loss.backward()

            grad_clip = self.cfg.training.get("grad_clip", None)
            if grad_clip:
                nn.utils.clip_grad_norm_(self.student.parameters(), grad_clip)

            self.optimizer.step()

            n = images.size(0)
            # total_loss keeps its historical meaning (the logit-KD component); the
            # RKD term is tracked separately so plain-KD runs report identically.
            total_loss += components["total_loss"] * n
            hard_sum += components["hard_loss"] * n
            soft_sum += components["soft_loss"] * n
            rkd_sum += rkd_val * n
            total += n
            pbar.set_postfix(loss=f"{components['total_loss'] + rkd_val:.4f}")

        return {
            "loss": total_loss / total,
            "hard_loss": hard_sum / total,
            "soft_loss": soft_sum / total,
            "rkd_loss": rkd_sum / total,
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
