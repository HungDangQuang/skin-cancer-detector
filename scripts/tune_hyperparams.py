"""
Ablation / HPO study for KD hyperparameters (temperature, alpha).
Runs on EfficientNet-B0 student, fold 0 only (as per proposal).

Usage:
    python scripts/tune_hyperparams.py --n-trials 50
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import optuna
from omegaconf import OmegaConf

from src.data.datamodule import SkinLesionDataModule
from src.models.registry import build_model
from src.training.kd_trainer import KDTrainer
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__)


def objective(trial: optuna.Trial, base_cfg, teacher_ckpt: str) -> float:
    cfg = OmegaConf.create(OmegaConf.to_container(base_cfg, resolve=True))

    # KD hyperparameter search space (from proposal ablation)
    cfg.training.distillation.temperature = trial.suggest_categorical("temperature", [1.0, 2.0, 4.0, 8.0])
    cfg.training.distillation.alpha = trial.suggest_categorical("alpha", [0.1, 0.3, 0.5, 0.7])
    cfg.training.epochs = 10  # short run for HPO

    set_seed(cfg.seed)

    teacher_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.teacher, resolve=True)})
    student_cfg = OmegaConf.merge(cfg, {"model": OmegaConf.to_container(cfg.student, resolve=True)})

    teacher = build_model(teacher_cfg)
    load_checkpoint(teacher_ckpt, teacher, device=cfg.device)

    student = build_model(student_cfg)
    datamodule = SkinLesionDataModule(student_cfg, fold=0)

    run_dir = Path("experiments/hpo") / f"trial_{trial.number}"
    trainer = KDTrainer(cfg, teacher, student, datamodule, run_dir=run_dir)
    history = trainer.fit()

    return max(history["val_pauc"]) if history["val_pauc"] else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", type=int, default=16)
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--teacher-checkpoint", required=True,
                        help="Path to trained teacher checkpoint")
    args = parser.parse_args()

    cfg = load_config(args.config)

    Path("experiments/hpo").mkdir(parents=True, exist_ok=True)
    storage = "sqlite:///experiments/hpo/optuna_study.db"
    study = optuna.create_study(
        direction="maximize",
        study_name="kd-ablation",
        storage=storage,
        load_if_exists=True,
    )

    study.optimize(
        lambda trial: objective(trial, cfg, args.teacher_checkpoint),
        n_trials=args.n_trials,
    )

    logger.info(f"Best trial: {study.best_trial.number}")
    logger.info(f"Best params: {study.best_trial.params}")
    logger.info(f"Best val_pauc: {study.best_trial.value:.4f}")


if __name__ == "__main__":
    main()
