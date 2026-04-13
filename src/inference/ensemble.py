from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image

from src.utils.checkpoint import load_checkpoint
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Ensemble:
    """
    Combine predictions from multiple model checkpoints via probability averaging.
    """

    def __init__(
        self,
        models: list[nn.Module],
        checkpoint_paths: list[str | Path],
        class_names: list[str],
        transform,
        device: str = "cpu",
    ):
        assert len(models) == len(checkpoint_paths)
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.class_names = class_names
        self.transform = transform
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
        all_probs = []

        for model in self.models:
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
            all_probs.append(probs)

        mean_probs = np.mean(all_probs, axis=0)
        class_idx = int(np.argmax(mean_probs))

        return {
            "class": self.class_names[class_idx],
            "class_idx": class_idx,
            "confidence": float(mean_probs[class_idx]),
            "probabilities": {name: float(mean_probs[i]) for i, name in enumerate(self.class_names)},
        }
