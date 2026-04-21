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

    teacher_ckpt = cfg.get(
        "teacher_checkpoint",
        f"{cfg.output_dir}/teacher/{cfg.teacher.name}/checkpoints/best_model.pth"
    )

    if not Path(teacher_ckpt).exists():
        logger.error(
            f"Teacher checkpoint not found: {teacher_ckpt}\n"
            "Run scripts/train_teacher.py first."
        )
        sys.exit(1)

    student_name = cfg.student.name
    run_dir = Path(cfg.output_dir) / f"kd_{cfg.teacher.name}_to_{student_name}"
    run_dir.mkdir(parents=True, exist_ok=True)

    teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})
    student_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.student, resolve=True)})

    save_config(cfg, run_dir / "config.yaml")
    logger.info(f"KD: {cfg.teacher.name} -> {student_name}")

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


if __name__ == "__main__":
    main()
