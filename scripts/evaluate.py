"""
Evaluation entry point.

Usage:
    python scripts/evaluate.py --model-name efficientnet_b4 --checkpoint path/to/best_model.pth
    python scripts/evaluate.py --model-name efficientnet_b0  --checkpoint path/to/best_model.pth
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.datamodule import SkinLesionDataModule
from src.evaluation.confusion_matrix import plot_confusion_matrix
from src.evaluation.evaluator import Evaluator
from src.models.registry import build_model_from_name
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True,
                        choices=["efficientnet_b4", "efficientnet_b0", "mobilenetv3_large", "mobilevit_s"],
                        help="Model architecture to evaluate")
    parser.add_argument("--checkpoint", required=True, help="Path to model checkpoint (.pth)")
    parser.add_argument("--fold", type=int, default=0, help="Which fold's test split to use")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--output", default="reports/results/test_metrics.json")
    args = parser.parse_args()

    cfg = load_config(args.config)
    set_seed(cfg.seed)

    model, model_cfg = build_model_from_name(args.model_name, cfg)
    load_checkpoint(args.checkpoint, model, device=cfg.device)

    datamodule = SkinLesionDataModule(model_cfg, fold=args.fold)
    datamodule.setup()

    evaluator = Evaluator(model, device=cfg.device)
    metrics = evaluator.evaluate(
        datamodule.test_dataloader(), sources=datamodule.test_sources()
    )
    evaluator.save_metrics(metrics, args.output)
    evaluator.save_predictions(
        metrics, Path(args.output).with_name(Path(args.output).stem + "_predictions.csv")
    )

    plot_confusion_matrix(
        y_true=metrics["_y_true"],
        y_pred=metrics["_y_pred"],
        class_names=list(cfg.data.classes),
        save_path="reports/figures/confusion_matrix.png",
    )


if __name__ == "__main__":
    main()
