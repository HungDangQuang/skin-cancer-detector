import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    roc_auc_score,
    roc_curve,
)


def pauc_at_tpr(y_true: np.ndarray, y_prob: np.ndarray, min_tpr: float = 0.80) -> float:
    """
    Partial AUC above a minimum TPR threshold (ISIC 2024 official metric).

    Computes the area under the ROC curve restricted to the region where
    TPR >= min_tpr, then normalizes to [0, max_possible_pauc].

    Args:
        y_true: Binary ground truth labels (0/1).
        y_prob: Predicted probabilities for the positive class.
        min_tpr: Minimum TPR threshold (default 0.80).

    Returns:
        Normalized pAUC in [0.0, 0.2] (for min_tpr=0.80).
    """
    fpr, tpr, _ = roc_curve(y_true, y_prob)

    # Keep only the region where TPR >= min_tpr
    mask = tpr >= min_tpr
    if mask.sum() < 2:
        return 0.0

    fpr_clipped = fpr[mask]
    tpr_clipped = tpr[mask]

    # Numerical integration (trapezoidal). np.trapz was removed in NumPy 2.0;
    # np.trapezoid is the supported name from 2.0 onwards.
    raw_pauc = float(np.trapezoid(tpr_clipped, fpr_clipped))

    # Normalize: max possible pAUC in the unrestricted region = 1.0 * (max_fpr - min_fpr)
    # For the standardized score, normalize by (1 - min_tpr)
    max_pauc = 1.0 - min_tpr
    return raw_pauc / max_pauc if max_pauc > 0 else 0.0


def youden_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """
    Find the optimal decision threshold using Youden's J statistic.

    J = sensitivity + specificity - 1 = TPR - FPR
    Select threshold that maximizes J.
    """
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    j_scores = tpr - fpr
    best_idx = int(np.argmax(j_scores))
    return float(thresholds[best_idx])


def compute_metrics(
    y_true: list[int],
    y_prob: np.ndarray,
    threshold: float | None = None,
    min_tpr: float = 0.80,
) -> dict:
    """
    Compute all evaluation metrics for binary classification.

    Args:
        y_true: Ground truth binary labels (0=benign, 1=malignant).
        y_prob: Predicted probabilities for malignant class, shape (N,).
        threshold: Decision threshold. If None, computed via Youden's J.
        min_tpr: TPR threshold for pAUC computation.

    Returns:
        Dictionary of metric name -> value.
    """
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)

    if threshold is None:
        threshold = youden_threshold(y_true, y_prob)

    y_pred = (y_prob >= threshold).astype(int)

    metrics = {}

    # Primary metric (ISIC 2024 official)
    metrics["pauc_at_tpr80"] = pauc_at_tpr(y_true, y_prob, min_tpr=min_tpr)

    # Standard metrics
    metrics["auc_roc"] = float(roc_auc_score(y_true, y_prob))
    metrics["threshold"] = threshold

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    metrics["sensitivity"] = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0  # recall / TPR
    metrics["specificity"] = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0  # TNR
    metrics["f1_score"] = float(f1_score(y_true, y_pred, zero_division=0))
    metrics["tp"] = int(tp)
    metrics["fp"] = int(fp)
    metrics["tn"] = int(tn)
    metrics["fn"] = int(fn)

    return metrics


def compute_kd_delta(metrics_no_kd: dict, metrics_with_kd: dict) -> dict:
    """
    Compute KD effectiveness delta metrics between baseline and KD-trained student.
    """
    return {
        "delta_pauc": metrics_with_kd["pauc_at_tpr80"] - metrics_no_kd["pauc_at_tpr80"],
        "delta_auc": metrics_with_kd["auc_roc"] - metrics_no_kd["auc_roc"],
        "delta_sensitivity": metrics_with_kd["sensitivity"] - metrics_no_kd["sensitivity"],
        "delta_specificity": metrics_with_kd["specificity"] - metrics_no_kd["specificity"],
    }
