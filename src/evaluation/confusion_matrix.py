from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix


def plot_confusion_matrix(
    y_true: list[int],
    y_pred: list[int],
    class_names: list[str],
    normalize: bool = True,
    save_path: str | None = None,
) -> np.ndarray:
    """
    Plot and optionally save a confusion matrix.

    Returns the raw (or normalized) confusion matrix array.
    """
    cm = confusion_matrix(y_true, y_pred)
    if normalize:
        cm_plot = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)
        fmt = ".2f"
    else:
        cm_plot = cm
        fmt = "d"

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        cm_plot,
        annot=True,
        fmt=fmt,
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion Matrix" + (" (Normalized)" if normalize else ""))
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")

    plt.show()
    return cm
