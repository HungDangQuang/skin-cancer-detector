import json
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm

from src.utils.batch import unpack_batch
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
    def evaluate(
        self,
        loader,
        sources: list[str] | None = None,
        metadata: dict[str, list] | None = None,
    ) -> dict:
        """
        Run inference on loader and return metrics dict.
        Model outputs raw logits (B,); sigmoid applied here.

        Args:
            loader: eval DataLoader. Must be shuffle=False if ``sources`` or
                ``metadata`` is given, so the per-sample tags stay row-aligned.
            sources: optional per-sample origin tag (e.g. "isic2024"/"pad_ufes_20"),
                aligned to the loader's iteration order. Persisted with the raw
                predictions so callers can compute per-domain breakdowns offline.
            metadata: optional ``{column: per-sample values}`` (e.g.
                ``anatom_site_general`` / ``sex``), each list row-aligned to the
                loader order. Persisted as extra columns in predictions.csv for
                offline SUBGROUP calibration (direction D). Ranking metrics are
                unaffected — this is display/analysis metadata only.
        """
        from src.evaluation.metrics import compute_metrics

        self.model.eval()
        all_labels, all_probs = [], []
        # A privileged (LUPI) teacher's own eval batch carries (meta, mask); an
        # image-only model gets just (images). The student is always image-only.
        accepts_meta = getattr(self.model, "accepts_metadata", False)

        for batch in tqdm(loader, desc="Evaluating"):
            images, meta, mask, labels = unpack_batch(batch)
            images = images.to(self.device)
            if accepts_meta and meta is not None:
                meta, mask = meta.to(self.device), mask.to(self.device)
                logits = self.model(images, meta, mask)
            else:
                logits = self.model(images)
            probs = torch.sigmoid(logits).cpu().numpy()

            all_labels.extend(labels.numpy())
            all_probs.extend(probs)

        all_probs = np.array(all_probs)
        metrics = compute_metrics(all_labels, all_probs, threshold=self.threshold)

        # Store raw arrays so callers can persist predictions / plot curves.
        # Underscore-prefixed keys are stripped by save_metrics (JSON stays scalar)
        # but consumed by save_predictions for offline PR-curve/AUPRC/bootstrap.
        thresh = metrics["threshold"]
        metrics["_y_true"] = [int(y) for y in all_labels]
        metrics["_y_prob"] = all_probs.astype(float).tolist()
        metrics["_y_pred"] = (all_probs >= thresh).astype(int).tolist()
        if sources is not None:
            if len(sources) != len(all_labels):
                raise ValueError(
                    f"sources length ({len(sources)}) != n_samples ({len(all_labels)}); "
                    "ensure the eval loader uses shuffle=False and sources is row-aligned."
                )
            metrics["_source"] = list(sources)
        if metadata:
            for col, vals in metadata.items():
                if len(vals) != len(all_labels):
                    raise ValueError(
                        f"metadata['{col}'] length ({len(vals)}) != n_samples "
                        f"({len(all_labels)}); ensure the eval loader uses "
                        "shuffle=False and metadata is row-aligned."
                    )
            metrics["_metadata"] = {col: list(vals) for col, vals in metadata.items()}

        logger.info(
            f"pAUC@TPR80={metrics['pauc_at_tpr80']:.4f} | "
            f"AUC={metrics['auc_roc']:.4f} | "
            f"AUPRC={metrics['auprc']:.4f} (base={metrics['prevalence']:.4f}) | "
            f"Acc={metrics['accuracy']:.4f} | "
            f"Prec={metrics['precision']:.4f} | "
            f"Recall={metrics['recall']:.4f} | "
            f"Sens={metrics['sensitivity']:.4f} | "
            f"Spec={metrics['specificity']:.4f} | "
            f"Sens@90spec={metrics['sens_at_90spec']:.4f} | "
            f"Sens@95spec={metrics['sens_at_95spec']:.4f} | "
            f"F1={metrics['f1_score']:.4f} | "
            f"Threshold={thresh:.4f}"
        )
        return metrics

    def save_metrics(self, metrics: dict, path: str | Path) -> None:
        """Save metrics dict to JSON (scalar fields only; raw arrays stripped)."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        serializable = {k: v for k, v in metrics.items() if isinstance(v, (int, float, str))}
        with open(path, "w") as f:
            json.dump(serializable, f, indent=2)
        logger.info(f"Metrics saved to {path}")

    def save_predictions(self, metrics: dict, path: str | Path) -> None:
        """
        Persist row-aligned raw predictions to CSV
        (y_true, y_prob, y_pred[, source][, <metadata columns>]).

        This is the enabler for honest imbalance metrics: AUPRC / PR-curve,
        fixed-specificity operating points, per-domain breakdowns, offline
        subgroup calibration and bootstrap CIs can all be recomputed from this
        file without re-running inference. No-op if ``evaluate`` was not run
        first (no raw arrays).
        """
        if "_y_true" not in metrics or "_y_prob" not in metrics:
            logger.warning("save_predictions: no raw arrays in metrics; skipping.")
            return
        import csv

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        y_true = metrics["_y_true"]
        y_prob = metrics["_y_prob"]
        y_pred = metrics["_y_pred"]
        source = metrics.get("_source")
        # Extra per-sample metadata columns (e.g. anatom_site_general / sex) for
        # offline subgroup calibration. Order-stable so the header matches rows.
        meta = metrics.get("_metadata") or {}
        meta_cols = list(meta.keys())
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            header = ["y_true", "y_prob", "y_pred"] + (["source"] if source else []) + meta_cols
            writer.writerow(header)
            for i in range(len(y_true)):
                row = [y_true[i], y_prob[i], y_pred[i]] + ([source[i]] if source else [])
                row += [meta[c][i] for c in meta_cols]
                writer.writerow(row)
        logger.info(f"Predictions saved to {path} ({len(y_true)} rows)")
