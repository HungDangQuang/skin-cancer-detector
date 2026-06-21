from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image

from src.utils.checkpoint import load_checkpoint
from src.utils.logger import get_logger

logger = get_logger(__name__)

CLASSES = ["benign", "malignant"]


class Ensemble:
    """
    Combine predictions from multiple binary model checkpoints via probability averaging.
    """

    def __init__(
        self,
        models: list[nn.Module],
        checkpoint_paths: list[str | Path],
        transform,
        device: str = "cpu",
        threshold: float = 0.5,
    ):
        assert len(models) == len(checkpoint_paths)
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.transform = transform
        self.threshold = threshold
        self.models = []

        for model, ckpt_path in zip(models, checkpoint_paths):
            load_checkpoint(ckpt_path, model, device=str(self.device))
            model.to(self.device).eval()
            self.models.append(model)

        logger.info(f"Loaded {len(self.models)} models for ensemble.")

    @torch.no_grad()
    def predict(self, image: Image.Image) -> dict:
        """Mean probability ensemble prediction for a single image."""
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        probs = []

        for model in self.models:
            logit = model(tensor)
            probs.append(torch.sigmoid(logit).item())

        mean_prob = float(np.mean(probs))
        predicted_class = CLASSES[int(mean_prob >= self.threshold)]

        return {
            "class": predicted_class,
            "probability": mean_prob,
            "threshold": self.threshold,
        }
