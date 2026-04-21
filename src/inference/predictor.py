from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image

from src.utils.checkpoint import load_checkpoint
from src.utils.logger import get_logger

logger = get_logger(__name__)

CLASSES = ["benign", "malignant"]


class Predictor:
    """
    Load a trained binary model and run inference on single images.
    Model outputs a raw logit (B,); sigmoid is applied here.
    """

    def __init__(
        self,
        model: nn.Module,
        checkpoint_path: str | Path,
        transform,
        device: str = "cpu",
        threshold: float = 0.5,
    ):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.transform = transform
        self.threshold = threshold

        load_checkpoint(checkpoint_path, model, device=str(self.device))
        self.model = model.to(self.device)
        self.model.eval()
        logger.info(f"Loaded checkpoint from {checkpoint_path}")

    @torch.no_grad()
    def predict(self, image: Image.Image) -> dict:
        """
        Predict malignancy probability for a single PIL image.

        Returns:
            {
                "class": "malignant",
                "probability": 0.87,
                "threshold": 0.5,
            }
        """
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        logit = self.model(tensor)
        prob = torch.sigmoid(logit).item()
        predicted_class = CLASSES[int(prob >= self.threshold)]

        return {
            "class": predicted_class,
            "probability": prob,
            "threshold": self.threshold,
        }

    @torch.no_grad()
    def predict_batch(self, images: list[Image.Image]) -> list[dict]:
        return [self.predict(img) for img in images]
