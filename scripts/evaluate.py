"""
Evaluation entry point.

Usage:
    python scripts/evaluate.py --model-name efficientnetv2_m --checkpoint path/to/best_model.pth
    python scripts/evaluate.py --model-name mobilenetv4_conv_medium  --checkpoint path/to/best_model.pth
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from src.data.datamodule import SkinLesionDataModule
from src.evaluation.confusion_matrix import plot_confusion_matrix
from src.evaluation.evaluator import Evaluator
from src.evaluation.metrics import metrics_at_frozen_threshold, youden_threshold
from src.models.registry import MODEL_REGISTRY, build_model_from_name
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.seed import set_seed

logger = get_logger(__name__)


def _val_predictions_for(checkpoint: str, explicit: str | None) -> Path | None:
    """--threshold-from if given (must exist); else the trainer's own file for
    this checkpoint: <fold>/checkpoints/best_model<tag>.pth -> <fold>/val_predictions<tag>.csv."""
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise FileNotFoundError(f"--threshold-from not found: {path}")
        return path
    ckpt = Path(checkpoint)
    tag = ckpt.stem[len("best_model"):] if ckpt.stem.startswith("best_model") else None
    if tag is None or ckpt.parent.name != "checkpoints":
        return None
    path = ckpt.parent.parent / f"val_predictions{tag}.csv"
    return path if path.is_file() else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True,
                        choices=sorted(MODEL_REGISTRY.keys()),
                        help="Model architecture to evaluate")
    parser.add_argument("--checkpoint", required=True, help="Path to model checkpoint (.pth)")
    parser.add_argument("--fold", type=int, default=0, help="Which fold's test split to use")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--output", default="reports/results/test_metrics.json")
    parser.add_argument("--threshold-from", default=None,
                        help="val_predictions*.csv of the SAME checkpoint; adds valthr_* keys "
                             "(default: <fold>/val_predictions<tag>.csv next to "
                             "<fold>/checkpoints/best_model<tag>.pth, when it exists)")
    args = parser.parse_args()
    # Resolve (and fail on a missing --threshold-from) BEFORE the test-set pass.
    val_pred = _val_predictions_for(args.checkpoint, args.threshold_from)

    cfg = load_config(args.config)
    set_seed(cfg.seed)

    model, model_cfg = build_model_from_name(args.model_name, cfg)
    load_checkpoint(args.checkpoint, model, device=cfg.device)

    datamodule = SkinLesionDataModule(model_cfg, fold=args.fold)
    datamodule.setup()

    evaluator = Evaluator(model, device=cfg.device)
    # metadata (site/sex) recorded into predictions.csv only when
    # data.metadata_cols is set (direction D); null -> None -> unchanged CSV.
    test_meta = datamodule.test_metadata(model_cfg.data.get("metadata_cols", None))
    metrics = evaluator.evaluate(
        datamodule.test_dataloader(),
        sources=datamodule.test_sources(),
        metadata=test_meta,
    )
    # The plain sensitivity/specificity/f1/threshold keys use Youden's J fitted
    # on this test set (optimistic); add the same rates at the val-Youden
    # threshold of the same checkpoint as valthr_* when its val predictions exist.
    if val_pred is not None:
        val = pd.read_csv(val_pred)
        val_thr = youden_threshold(val["y_true"].values, val["y_prob"].values)
        metrics.update(metrics_at_frozen_threshold(metrics["_y_true"], metrics["_y_prob"], val_thr))
        logger.info(f"valthr_* added from {val_pred} (threshold={val_thr:.4f})")
    else:
        logger.warning("No val_predictions for this checkpoint: valthr_* not written; "
                       "sensitivity/specificity use a threshold fitted on the test set.")
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
