"""
Evaluation entry point.

Usage:
    python scripts/evaluate.py --checkpoint experiments/runs/skin-cancer-baseline/checkpoints/best_model.pth
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.datamodule import SkinLesionDataModule
from src.evaluation.confusion_matrix import plot_confusion_matrix
from src.evaluation.evaluator import Evaluator
from src.models.registry import build_model
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, help="Path to model checkpoint (.pth)")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--output", default="reports/results/test_metrics.json")
    args = parser.parse_args()

    cfg = load_config(args.config)
    set_seed(cfg.seed)

    datamodule = SkinLesionDataModule(cfg)
    datamodule.setup()

    model = build_model(cfg)
    load_checkpoint(args.checkpoint, model, device=cfg.device)

    evaluator = Evaluator(model, device=cfg.device, class_names=cfg.data.classes)
    metrics = evaluator.evaluate(datamodule.test_dataloader())
    evaluator.save_metrics(metrics, args.output)

    plot_confusion_matrix(
        y_true=metrics.get("_y_true", []),
        y_pred=metrics.get("_y_pred", []),
        class_names=cfg.data.classes,
        save_path="reports/figures/confusion_matrix.png",
    )


if __name__ == "__main__":
    main()
