from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_training_curves(
    train_losses: list[float],
    val_losses: list[float],
    train_accs: list[float],
    val_accs: list[float],
    save_path: str | None = None,
) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    epochs = range(1, len(train_losses) + 1)
    ax1.plot(epochs, train_losses, label="Train")
    ax1.plot(epochs, val_losses, label="Val")
    ax1.set_title("Loss")
    ax1.set_xlabel("Epoch")
    ax1.legend()

    ax2.plot(epochs, train_accs, label="Train")
    ax2.plot(epochs, val_accs, label="Val")
    ax2.set_title("Accuracy")
    ax2.set_xlabel("Epoch")
    ax2.legend()

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def plot_class_distribution(class_counts: dict[str, int], save_path: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    names = list(class_counts.keys())
    counts = list(class_counts.values())
    bars = ax.bar(names, counts, color="steelblue")
    ax.bar_label(bars)
    ax.set_title("Class Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Count")
    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def show_sample_grid(
    images: list,
    labels: list[str],
    nrow: int = 4,
    save_path: str | None = None,
) -> None:
    n = len(images)
    ncols = nrow
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3, nrows * 3))
    axes = np.array(axes).flatten()

    for i, (img, label) in enumerate(zip(images, labels)):
        axes[i].imshow(img)
        axes[i].set_title(label, fontsize=9)
        axes[i].axis("off")

    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
