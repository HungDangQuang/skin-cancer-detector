"""
Hyperparameter optimization with Optuna.

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
from src.training.trainer import Trainer
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__)


def objective(trial: optuna.Trial, base_cfg) -> float:
    cfg = OmegaConf.structured(OmegaConf.to_container(base_cfg, resolve=True))

    # Search space
    cfg.training.optimizer.lr = trial.suggest_float("lr", 1e-5, 1e-3, log=True)
    cfg.training.optimizer.weight_decay = trial.suggest_float("weight_decay", 1e-5, 1e-2, log=True)
    cfg.training.batch_size = trial.suggest_categorical("batch_size", [16, 32])
    cfg.model.head.dropout = trial.suggest_float("dropout", 0.2, 0.5)
    cfg.training.epochs = 10  # short run for HPO

    set_seed(cfg.seed)
    datamodule = SkinLesionDataModule(cfg)
    model = build_model(cfg)

    run_dir = Path("experiments/hpo") / f"trial_{trial.number}"
    trainer = Trainer(cfg, model, datamodule, run_dir=run_dir)
    history = trainer.fit()

    return min(history["val_loss"])  # minimize val loss


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-trials", type=int, default=20)
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)

    storage = "sqlite:///experiments/hpo/optuna_study.db"
    study = optuna.create_study(
        direction="minimize",
        study_name="skin-cancer-hpo",
        storage=storage,
        load_if_exists=True,
    )

    study.optimize(lambda trial: objective(trial, cfg), n_trials=args.n_trials)

    logger.info(f"Best trial: {study.best_trial.number}")
    logger.info(f"Best params: {study.best_trial.params}")
    logger.info(f"Best val_loss: {study.best_trial.value:.4f}")


if __name__ == "__main__":
    main()
