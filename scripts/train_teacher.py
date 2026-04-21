"""
Step 1 — Train the teacher model (EfficientNet-B4) standalone.

Usage:
    python scripts/train_teacher.py
    python scripts/train_teacher.py training=default
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import hydra
from omegaconf import DictConfig, OmegaConf

from src.data.datamodule import SkinLesionDataModule
from src.models.registry import build_model
from src.training.trainer import Trainer
from src.utils.config import save_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed
from src.utils.visualization import plot_training_curves

logger = get_logger(__name__)


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    set_seed(cfg.seed)

    teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})

    run_dir = Path(cfg.output_dir) / "teacher" / cfg.teacher.name
    run_dir.mkdir(parents=True, exist_ok=True)
    save_config(teacher_cfg, run_dir / "config.yaml")

    logger.info(f"Training teacher: {cfg.teacher.name}")

    datamodule = SkinLesionDataModule(teacher_cfg)
    model = build_model(teacher_cfg)
    logger.info(f"Teacher parameters: {model.num_parameters():,}")

    trainer = Trainer(teacher_cfg, model, datamodule, run_dir=run_dir)
    history = trainer.fit()

    plot_training_curves(
        history["train_loss"],
        history["val_loss"],
        history["val_pauc"],
        save_path=str(run_dir / "training_curves.png"),
    )
    logger.info(f"Teacher training complete. Checkpoint: {run_dir / 'checkpoints' / 'best_model.pth'}")


if __name__ == "__main__":
    main()
