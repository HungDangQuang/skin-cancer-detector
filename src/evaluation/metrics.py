import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    roc_auc_score,
    roc_curve,
)


def pauc_at_tpr(y_true: np.ndarray, y_prob: np.ndarray, min_tpr: float = 0.80) -> float:
    """
    Partial AUC above a minimum TPR threshold — the ISIC 2024 official metric.

    Implements the competition's exact formulation: relabel/flip so the
    "TPR >= min_tpr" region of the original ROC maps to the "FPR <= max_fpr"
    region (max_fpr = 1 - min_tpr), take sklearn's McClish-corrected partial
    AUC, then invert the McClish scaling to recover the true partial-area value.

    Args:
        y_true: Binary ground truth labels (0/1).
        y_prob: Predicted probabilities for the positive class.
        min_tpr: Minimum TPR threshold (default 0.80).

    Returns:
        Partial AUC in [0.5*max_fpr**2, max_fpr] — i.e. ~[0.02, 0.20] for
        min_tpr=0.80: random ≈ 0.02, perfect = 0.20.
    """
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)

    # Undefined with a single class present — roc_auc_score would raise.
    if len(np.unique(y_true)) < 2:
        return 0.0

    max_fpr = 1.0 - min_tpr
    # Flip labels and scores: TPR >= min_tpr (original) == FPR <= max_fpr here.
    v_gt = 1 - y_true
    v_pred = -y_prob
    scaled = roc_auc_score(v_gt, v_pred, max_fpr=max_fpr)  # McClish-corrected, in [0.5, 1]

    # Invert McClish: scaled = 0.5*(1 + (pAUC - min_area)/(max_area - min_area)),
    # with min_area = 0.5*max_fpr**2 (area under the diagonal) and max_area = max_fpr.
    min_area = 0.5 * max_fpr ** 2
    return float(min_area + (max_fpr - min_area) / 0.5 * (scaled - 0.5))


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


def class_prevalence_baselines(labels: list[int] | np.ndarray) -> dict:
    """
    Reference baselines a binary classifier must beat to add value.

    Returns class counts + the accuracy you'd get by predicting the majority
    class everywhere (the floor that "good accuracy" claims must clear).
    """
    labels = np.asarray(labels)
    n = int(len(labels))
    n_pos = int((labels == 1).sum())
    n_neg = n - n_pos
    majority = max(n_pos, n_neg)
    return {
        "n_total": n,
        "n_positive": n_pos,
        "n_negative": n_neg,
        "positive_rate": float(n_pos / n) if n > 0 else 0.0,
        "majority_class_accuracy": float(majority / n) if n > 0 else 0.0,
    }


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
    metrics["precision"] = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0    # PPV
    metrics["recall"] = metrics["sensitivity"]                                # alias for clarity
    metrics["f1_score"] = float(f1_score(y_true, y_pred, zero_division=0))
    total = tp + fp + tn + fn
    metrics["accuracy"] = float((tp + tn) / total) if total > 0 else 0.0
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
