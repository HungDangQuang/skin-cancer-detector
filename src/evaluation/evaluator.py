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
    """

    def __init__(self, model: torch.nn.Module, device: str, class_names: list[str]):
        self.model = model
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.class_names = class_names

    @torch.no_grad()
    def evaluate(self, loader) -> dict:
        """
        Run inference on loader and return metrics dict.
        """
        from src.evaluation.metrics import compute_metrics

        self.model.eval()
        all_labels, all_preds, all_probs = [], [], []

        for images, labels in tqdm(loader, desc="Evaluating"):
            images = images.to(self.device)
            logits = self.model(images)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            preds = logits.argmax(dim=1).cpu().numpy()

            all_labels.extend(labels.numpy())
            all_preds.extend(preds)
            all_probs.append(probs)

        all_probs = np.concatenate(all_probs, axis=0)
        metrics = compute_metrics(all_labels, all_preds, all_probs, self.class_names)

        logger.info(f"Accuracy: {metrics['accuracy']:.4f} | AUC: {metrics['auc_macro']:.4f}")
        logger.info("\n" + metrics["classification_report"])

        return metrics

    def save_metrics(self, metrics: dict, path: str | Path) -> None:
        """Save metrics to JSON (excludes non-serializable entries)."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        serializable = {k: v for k, v in metrics.items() if not isinstance(v, str)}
        with open(path, "w") as f:
            json.dump(serializable, f, indent=2)
        logger.info(f"Metrics saved to {path}")
