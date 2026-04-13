import numpy as np
import pytest

from src.evaluation.metrics import compute_metrics

CLASS_NAMES = ["mel", "nv", "bcc", "akiec", "bkl", "df", "vasc"]


def test_perfect_predictions():
    y_true = [0, 1, 2, 3]
    y_pred = [0, 1, 2, 3]
    y_prob = np.eye(7)[:4]  # one-hot
    metrics = compute_metrics(y_true, y_pred, y_prob, CLASS_NAMES)
    assert metrics["accuracy"] == 1.0
    assert metrics["f1_macro"] == pytest.approx(1.0, abs=0.01)


def test_metrics_keys():
    y_true = [0, 1, 2]
    y_pred = [0, 1, 1]
    y_prob = np.random.dirichlet(np.ones(7), size=3)
    metrics = compute_metrics(y_true, y_pred, y_prob, CLASS_NAMES)
    for key in ["accuracy", "balanced_accuracy", "f1_macro", "f1_weighted", "auc_macro"]:
        assert key in metrics


def test_per_class_f1_keys():
    y_true = [0, 1]
    y_pred = [0, 1]
    y_prob = np.eye(7)[:2]
    metrics = compute_metrics(y_true, y_pred, y_prob, CLASS_NAMES)
    for name in CLASS_NAMES:
        assert f"f1_{name}" in metrics
