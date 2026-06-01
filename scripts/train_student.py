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

    student_name = cfg.student.name
    run_dir = Path(cfg.output_dir) / f"kd_{cfg.teacher.name}_to_{student_name}" / f"fold_{fold}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Hydra emits cfg in struct mode; merging in a new top-level "model" key
    # below would otherwise raise ConfigKeyError.
    OmegaConf.set_struct(cfg, False)
    teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})
    student_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.student, resolve=True)})

    save_config(cfg, run_dir / "config.yaml")
    logger.info(f"KD: {cfg.teacher.name} -> {student_name} (fold {fold})")

    teacher = build_model(teacher_cfg)
    load_checkpoint(teacher_ckpt, teacher, device=cfg.device)
    logger.info(f"Teacher loaded from {teacher_ckpt}")

    student = build_model(student_cfg)
    logger.info(f"Student parameters: {student.num_parameters():,}")

    datamodule = SkinLesionDataModule(student_cfg)

    trainer = KDTrainer(cfg, teacher, student, datamodule, run_dir=run_dir)
    history = trainer.fit()

    plot_training_curves(
        history["train_loss"],
        history["val_loss"],
        history["val_pauc"],
        save_path=str(run_dir / "training_curves.png"),
    )
    logger.info(f"KD training complete. Checkpoint: {run_dir / 'checkpoints' / 'best_model.pth'}")

    best_ckpt = run_dir / "checkpoints" / "best_model.pth"
    if best_ckpt.exists():
        logger.info(f"Evaluating best student checkpoint on held-out test set: {best_ckpt}")
        load_checkpoint(str(best_ckpt), student, device=cfg.device)
        evaluator = Evaluator(student, device=cfg.device)
        test_metrics = evaluator.evaluate(datamodule.test_dataloader())
        evaluator.save_metrics(test_metrics, run_dir / "test_metrics.json")
    else:
        logger.warning(f"No best checkpoint at {best_ckpt}; skipping test-set evaluation.")


if __name__ == "__main__":
    main()
