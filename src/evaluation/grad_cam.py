"""
Grad-CAM visualization using pytorch-grad-cam library.
Install: pip install grad-cam
"""
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from PIL import Image


def get_target_layer(model: nn.Module) -> nn.Module:
    """
    Heuristically find the last convolutional layer for Grad-CAM.
    Override this for custom architectures.
    """
    # For EfficientNet/ResNet via timm
    if hasattr(model, "backbone"):
        backbone = model.backbone
        # Try common attribute names
        for attr in ["blocks", "layer4", "stages"]:
            if hasattr(backbone, attr):
                layer = getattr(backbone, attr)
                if isinstance(layer, nn.Sequential):
                    return layer[-1]
                return layer
    raise ValueError("Could not automatically find target layer. Pass it explicitly.")


def generate_grad_cam(
    model: nn.Module,
    image: Image.Image,
    transform: Callable,
    target_class: int | None = None,
    target_layer: nn.Module | None = None,
    device: str = "cpu",
) -> np.ndarray:
    """
    Generate a Grad-CAM heatmap for a single image.

    Returns:
        heatmap: numpy array of shape (H, W), values in [0, 1].
    """
    try:
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
    except ImportError:
        raise ImportError("Install grad-cam: pip install grad-cam")

    if target_layer is None:
        target_layer = get_target_layer(model)

    input_tensor = transform(image).unsqueeze(0).to(device)
    model.eval()

    targets = [ClassifierOutputTarget(target_class)] if target_class is not None else None

    with GradCAM(model=model, target_layers=[target_layer]) as cam:
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets)

    return grayscale_cam[0]  # (H, W)


def visualize_grad_cam(
    image: Image.Image,
    heatmap: np.ndarray,
    title: str = "",
    save_path: str | None = None,
) -> None:
    """Overlay Grad-CAM heatmap on the original image."""
    from pytorch_grad_cam.utils.image import show_cam_on_image

    img_np = np.array(image.resize((224, 224))).astype(float) / 255.0
    visualization = show_cam_on_image(img_np, heatmap, use_rgb=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.imshow(image)
    ax1.set_title("Original")
    ax1.axis("off")
    ax2.imshow(visualization)
    ax2.set_title(f"Grad-CAM {title}")
    ax2.axis("off")
    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
