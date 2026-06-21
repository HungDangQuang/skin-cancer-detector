"""
Step 2 — Train a student model via knowledge distillation from the teacher.

Usage:
    python scripts/train_student.py student=efficientnet_b0
    python scripts/train_student.py student=mobilenetv3_large
    python scripts/train_student.py student=mobilevit_s

The teacher checkpoint must exist (run train_teacher.py first).
Override the teacher checkpoint path with:
    python scripts/train_student.py teacher_checkpoint=path/to/best_model.pth
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import hydra
from omegaconf import DictConfig, OmegaConf

from src.data.datamodule import SkinLesionDataModule
from src.evaluation.evaluator import Evaluator
from src.models.registry import build_model
from src.training.kd_trainer import KDTrainer
from src.training.trainer import Trainer
from src.utils.checkpoint import load_checkpoint
from src.utils.config import save_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed
from src.utils.visualization import plot_training_curves

logger = get_logger(__name__)


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    set_seed(cfg.seed)

    fold = int(cfg.data.get("fold", 0))
    # use_kd gates the controlled comparison: True -> KDTrainer + frozen teacher
    # (distillation branch); False -> plain Trainer + focal loss (baseline branch).
    # configs/training/{distillation,baseline}.yaml set this flag.
    use_kd = bool(cfg.training.get("use_kd", True))
    student_name = cfg.student.name
    # Optional tag to fork an ablation into its own run-dir subtree (e.g.
    # "__samp_off", "__ratio3") so it never overwrites the main 30-run results.
    # Set via Hydra CLI: run_suffix=__samp_off (forwarded by the ablation slurm).
    run_suffix = str(cfg.get("run_suffix", "") or "")

    # Hydra emits cfg in struct mode; merging in a new top-level "model" key
    # below would otherwise raise ConfigKeyError.
    OmegaConf.set_struct(cfg, False)
    student_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.student, resolve=True)})

    student = build_model(student_cfg)
    logger.info(f"Student parameters: {student.num_parameters():,}")
    datamodule = SkinLesionDataModule(student_cfg)

    if use_kd:
        teacher_ckpt = cfg.get(
            "teacher_checkpoint",
            f"{cfg.output_dir}/teacher/{cfg.teacher.name}/fold_{fold}/checkpoints/best_model.pth"
        )
        if not Path(teacher_ckpt).exists():
            logger.error(
                f"Teacher checkpoint not found: {teacher_ckpt}\n"
                f"Run scripts/train_teacher.py for fold {fold} first."
            )
            sys.exit(1)

        run_dir = Path(cfg.output_dir) / f"kd_{cfg.teacher.name}_to_{student_name}{run_suffix}" / f"fold_{fold}"
        run_dir.mkdir(parents=True, exist_ok=True)
        save_config(cfg, run_dir / "config.yaml")

        teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})
        teacher = build_model(teacher_cfg)
        load_checkpoint(teacher_ckpt, teacher, device=cfg.device)
        logger.info(f"KD: {cfg.teacher.name} -> {student_name} (fold {fold}); teacher={teacher_ckpt}")

        trainer = KDTrainer(cfg, teacher, student, datamodule, run_dir=run_dir)
    else:
        # Baseline (no KD): the controlled-comparison branch. Identical student,
        # data, hyperparameters, and seed as the KD branch — only the loss
        # differs (focal-only via Trainer, no teacher/soft labels).
        run_dir = Path(cfg.output_dir) / f"baseline_{student_name}{run_suffix}" / f"fold_{fold}"
        run_dir.mkdir(parents=True, exist_ok=True)
        save_config(cfg, run_dir / "config.yaml")
        logger.info(f"Baseline (no KD): {student_name} (fold {fold})")

        trainer = Trainer(cfg, student, datamodule, run_dir=run_dir)

    history = trainer.fit()

    plot_training_curves(
        history["train_loss"],
        history["val_loss"],
        history["val_pauc"],
        save_path=str(run_dir / "training_curves.png"),
    )
    logger.info(f"Training complete ({'KD' if use_kd else 'baseline'}). "
                f"Checkpoint: {run_dir / 'checkpoints' / 'best_model.pth'}")

    best_ckpt = run_dir / "checkpoints" / "best_model.pth"
    if best_ckpt.exists():
        logger.info(f"Evaluating best student checkpoint on held-out test set: {best_ckpt}")
        load_checkpoint(str(best_ckpt), student, device=cfg.device)
        evaluator = Evaluator(student, device=cfg.device)
        test_metrics = evaluator.evaluate(
            datamodule.test_dataloader(), sources=datamodule.test_sources()
        )
        evaluator.save_metrics(test_metrics, run_dir / "test_metrics.json")
        evaluator.save_predictions(test_metrics, run_dir / "predictions.csv")
    else:
        logger.warning(f"No best checkpoint at {best_ckpt}; skipping test-set evaluation.")


if __name__ == "__main__":
    main()
