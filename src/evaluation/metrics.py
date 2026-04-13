import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    roc_auc_score,
)


def compute_metrics(
    y_true: list[int],
    y_pred: list[int],
    y_prob: np.ndarray,
    class_names: list[str],
) -> dict:
    """
    Compute all evaluation metrics.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted class indices.
        y_prob: Predicted probabilities, shape (N, num_classes).
        class_names: List of class name strings.

    Returns:
        Dictionary of metric name -> value.
    """
    metrics = {}
    metrics["accuracy"] = accuracy_score(y_true, y_pred)
    metrics["balanced_accuracy"] = balanced_accuracy_score(y_true, y_pred)
    metrics["f1_macro"] = f1_score(y_true, y_pred, average="macro", zero_division=0)
    metrics["f1_weighted"] = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    # Multi-class AUC (OvR)
    try:
        metrics["auc_macro"] = roc_auc_score(y_true, y_prob, multi_class="ovr", average="macro")
        metrics["auc_weighted"] = roc_auc_score(y_true, y_prob, multi_class="ovr", average="weighted")
    except ValueError:
        metrics["auc_macro"] = float("nan")
        metrics["auc_weighted"] = float("nan")

    # Per-class F1
    per_class_f1 = f1_score(y_true, y_pred, average=None, zero_division=0)
    for i, name in enumerate(class_names):
        metrics[f"f1_{name}"] = float(per_class_f1[i])

    # Full classification report (string)
    metrics["classification_report"] = classification_report(
        y_true, y_pred, target_names=class_names, zero_division=0
    )

    return metrics
