import numpy as np
import pytest

from src.evaluation.metrics import compute_metrics, pauc_at_tpr, youden_threshold


def test_pauc_perfect_classifier():
    y_true = np.array([0] * 100 + [1] * 10)
    # Perfect: malignant gets prob=1, benign gets prob=0
    y_prob = np.array([0.0] * 100 + [1.0] * 10)
    pauc = pauc_at_tpr(y_true, y_prob, min_tpr=0.80)
    assert pauc > 0.9  # should be close to 1.0


def test_pauc_random_classifier():
    rng = np.random.default_rng(42)
    y_true = np.array([0] * 100 + [1] * 10)
    y_prob = rng.random(110)
    pauc = pauc_at_tpr(y_true, y_prob, min_tpr=0.80)
    assert 0.0 <= pauc <= 1.0


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
    for key in ["pauc_at_tpr80", "auc_roc", "sensitivity", "specificity", "f1_score", "threshold"]:
        assert key in metrics


def test_compute_metrics_perfect():
    y_true = [0, 0, 0, 1, 1, 1]
    y_prob = np.array([0.0, 0.1, 0.2, 0.8, 0.9, 1.0])
    metrics = compute_metrics(y_true, y_prob)
    assert metrics["sensitivity"] == pytest.approx(1.0)
    assert metrics["specificity"] == pytest.approx(1.0)
    assert metrics["auc_roc"] == pytest.approx(1.0)
