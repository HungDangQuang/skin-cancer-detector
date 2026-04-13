"""
Training entry point.

Usage:
    python scripts/train.py
    python scripts/train.py model=resnet50
    python scripts/train.py training=finetuning augmentation=heavy
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import hydra
from omegaconf import DictConfig

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

    run_dir = Path(cfg.output_dir) / cfg.experiment_name
    run_dir.mkdir(parents=True, exist_ok=True)
    save_config(cfg, run_dir / "config.yaml")

    logger.info(f"Experiment: {cfg.experiment_name}")
    logger.info(f"Model: {cfg.model.name}")
    logger.info(f"Run dir: {run_dir}")

    datamodule = SkinLesionDataModule(cfg)
    model = build_model(cfg)

    logger.info(f"Model parameters: {model.num_parameters():,}")

    trainer = Trainer(cfg, model, datamodule, run_dir=run_dir)
    history = trainer.fit()

    plot_training_curves(
        history["train_loss"], history["val_loss"],
        history["train_acc"], history["val_acc"],
        save_path=str(run_dir / "training_curves.png"),
    )
    logger.info("Training complete.")


if __name__ == "__main__":
    main()
