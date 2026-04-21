import json
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm

from src.utils.logger import get_logger

logger = get_logger(__name__)


class Evaluator:
    """
    Run a full evaluation pass on a DataLoader and compute all metrics.
    Designed for binary classification with sigmoid output.
    """

    def __init__(self, model: torch.nn.Module, device: str, threshold: float | None = None):
        self.model = model
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.threshold = threshold  # if None, computed via Youden's J on the eval set

    @torch.no_grad()
    def evaluate(self, loader) -> dict:
        """
        Run inference on loader and return metrics dict.
        Model outputs raw logits (B,); sigmoid applied here.
        """
        from src.evaluation.metrics import compute_metrics

        self.model.eval()
        all_labels, all_probs = [], []

        for images, labels in tqdm(loader, desc="Evaluating"):
            images = images.to(self.device)
            logits = self.model(images)
            probs = torch.sigmoid(logits).cpu().numpy()

            all_labels.extend(labels.numpy())
            all_probs.extend(probs)

        all_probs = np.array(all_probs)
        metrics = compute_metrics(all_labels, all_probs, threshold=self.threshold)

        # Store raw arrays so callers can plot confusion matrix etc.
        thresh = metrics["threshold"]
        metrics["_y_true"] = all_labels
        metrics["_y_pred"] = (all_probs >= thresh).astype(int).tolist()

        logger.info(
            f"pAUC@TPR80={metrics['pauc_at_tpr80']:.4f} | "
            f"AUC={metrics['auc_roc']:.4f} | "
            f"Sensitivity={metrics['sensitivity']:.4f} | "
            f"Specificity={metrics['specificity']:.4f} | "
            f"Threshold={thresh:.4f}"
        )
        return metrics

    def save_metrics(self, metrics: dict, path: str | Path) -> None:
        """Save metrics dict to JSON."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        serializable = {k: v for k, v in metrics.items() if isinstance(v, (int, float, str))}
        with open(path, "w") as f:
            json.dump(serializable, f, indent=2)
        logger.info(f"Metrics saved to {path}")
