import numpy as np
import pytest

from src.evaluation.metrics import (
    class_prevalence_baselines,
    compute_metrics,
    pauc_at_tpr,
    youden_threshold,
)


def test_pauc_perfect_classifier():
    y_true = np.array([0] * 100 + [1] * 10)
    # Perfect: malignant gets prob=1, benign gets prob=0
    y_prob = np.array([0.0] * 100 + [1.0] * 10)
    pauc = pauc_at_tpr(y_true, y_prob, min_tpr=0.80)
    # ISIC 2024 metric: perfect classifier reaches the max partial area = max_fpr = 0.2.
    assert pauc == pytest.approx(0.2, abs=1e-6)


def test_pauc_random_classifier():
    rng = np.random.default_rng(42)
    y_true = np.array([0] * 100 + [1] * 10)
    y_prob = rng.random(110)
    pauc = pauc_at_tpr(y_true, y_prob, min_tpr=0.80)
    # Bounded by [0.5*max_fpr**2, max_fpr] = [0.02, 0.20]; random sits near 0.02.
    assert 0.0 <= pauc <= 0.2 + 1e-6


def test_youden_threshold_range():
    rng = np.random.default_rng(0)
    y_true = np.array([0] * 50 + [1] * 50)
    y_prob = rng.random(100)
    thresh = youden_threshold(y_true, y_prob)
    assert 0.0 <= thresh <= 1.0


def test_compute_metrics_keys():
    y_true = [0, 0, 1, 1]
    y_prob = np.array([0.1, 0.2, 0.8, 0.9])
    metrics = compute_metrics(y_true, y_prob)
    for key in [
        "pauc_at_tpr80", "auc_roc",
        "sensitivity", "specificity", "precision", "recall",
        "f1_score", "accuracy", "threshold",
    ]:
        assert key in metrics


def test_recall_equals_sensitivity():
    y_true = [0, 0, 0, 1, 1, 1]
    y_prob = np.array([0.1, 0.2, 0.9, 0.8, 0.4, 0.95])
    metrics = compute_metrics(y_true, y_prob, threshold=0.5)
    assert metrics["recall"] == pytest.approx(metrics["sensitivity"])


def test_precision_matches_tp_fp_definition():
    # 3 positives at threshold>=0.5: idx 3, 5 are TP; idx 2 is FP (benign w/ prob 0.9)
    y_true = [0, 0, 0, 1, 1, 1]
    y_prob = np.array([0.1, 0.2, 0.9, 0.8, 0.4, 0.95])
    metrics = compute_metrics(y_true, y_prob, threshold=0.5)
    expected = metrics["tp"] / (metrics["tp"] + metrics["fp"])
    assert metrics["precision"] == pytest.approx(expected)
    assert metrics["precision"] == pytest.approx(2 / 3)


def test_precision_zero_when_no_positives_predicted():
    y_true = [0, 0, 1, 1]
    y_prob = np.array([0.1, 0.2, 0.3, 0.4])  # all below 0.5
    metrics = compute_metrics(y_true, y_prob, threshold=0.5)
    assert metrics["precision"] == 0.0  # tp + fp = 0 → safe-divide branch


def test_compute_metrics_perfect():
    y_true = [0, 0, 0, 1, 1, 1]
    y_prob = np.array([0.0, 0.1, 0.2, 0.8, 0.9, 1.0])
    metrics = compute_metrics(y_true, y_prob)
    assert metrics["sensitivity"] == pytest.approx(1.0)
    assert metrics["specificity"] == pytest.approx(1.0)
    assert metrics["auc_roc"] == pytest.approx(1.0)
    assert metrics["accuracy"] == pytest.approx(1.0)


def test_class_prevalence_baselines_imbalanced():
    labels = [0] * 95 + [1] * 5
    b = class_prevalence_baselines(labels)
    assert b["n_total"] == 100
    assert b["n_positive"] == 5
    assert b["n_negative"] == 95
    assert b["positive_rate"] == pytest.approx(0.05)
    assert b["majority_class_accuracy"] == pytest.approx(0.95)


def test_class_prevalence_baselines_empty():
    b = class_prevalence_baselines([])
    assert b["n_total"] == 0
    assert b["positive_rate"] == 0.0
    assert b["majority_class_accuracy"] == 0.0


def test_compute_metrics_accuracy_matches_tp_tn():
    # 3 benign correct, 1 benign misclassified; 2 malignant correct, 0 missed
    y_true = [0, 0, 0, 0, 1, 1]
    y_prob = np.array([0.1, 0.2, 0.3, 0.9, 0.8, 0.95])
    metrics = compute_metrics(y_true, y_prob, threshold=0.5)
    expected = (metrics["tp"] + metrics["tn"]) / (
        metrics["tp"] + metrics["fp"] + metrics["tn"] + metrics["fn"]
    )
    assert metrics["accuracy"] == pytest.approx(expected)
    assert metrics["accuracy"] == pytest.approx(5 / 6)
