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
from src.evaluation.evaluator import Evaluator
from src.models.registry import build_model
from src.training.trainer import Trainer
from src.utils.checkpoint import load_checkpoint
from src.utils.config import save_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed
from src.utils.visualization import plot_training_curves

logger = get_logger(__name__)


@hydra.main(config_path="../configs", config_name="config", version_base=None)
def main(cfg: DictConfig) -> None:
    set_seed(cfg.seed, deterministic=cfg.get("cudnn_deterministic", True))

    # Hydra emits cfg in struct mode; merging in a new top-level "model" key
    # below would otherwise raise ConfigKeyError.
    OmegaConf.set_struct(cfg, False)
    teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})

    fold = int(cfg.data.get("fold", 0))
    run_dir = Path(cfg.output_dir) / "teacher" / cfg.teacher.name / f"fold_{fold}"
    run_dir.mkdir(parents=True, exist_ok=True)
    save_config(teacher_cfg, run_dir / "config.yaml")

    logger.info(f"Training teacher: {cfg.teacher.name} (fold {fold})")

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

    best_ckpt = run_dir / "checkpoints" / "best_model.pth"
    if best_ckpt.exists():
        logger.info(f"Evaluating best checkpoint on held-out test set: {best_ckpt}")
        load_checkpoint(str(best_ckpt), model, device=cfg.device)
        evaluator = Evaluator(model, device=cfg.device)
        test_metrics = evaluator.evaluate(
            datamodule.test_dataloader(), sources=datamodule.test_sources()
        )
        evaluator.save_metrics(test_metrics, run_dir / "test_metrics.json")
        evaluator.save_predictions(test_metrics, run_dir / "predictions.csv")
        # Calibration fit-set: val predictions. The val loader uses NO
        # undersampler (datamodule.val_dataloader), so it preserves the true
        # ~0.39% prevalence — the correct distribution to fit a Platt / isotonic
        # calibrator on. scripts/compute_calibration.py consumes val_predictions.csv
        # (fit) + predictions.csv (apply on test). No sources arg: val has no
        # per-domain source method (only test_sources() exists).
        val_metrics = evaluator.evaluate(datamodule.val_dataloader())
        evaluator.save_predictions(val_metrics, run_dir / "val_predictions.csv")
    else:
        logger.warning(f"No best checkpoint at {best_ckpt}; skipping test-set evaluation.")


if __name__ == "__main__":
    main()
