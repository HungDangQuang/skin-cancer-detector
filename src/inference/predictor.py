from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image

from src.utils.checkpoint import load_checkpoint
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Predictor:
    """
    Load a trained model and run inference on single images or batches.
    """

    def __init__(
        self,
        model: nn.Module,
        checkpoint_path: str | Path,
        class_names: list[str],
        transform,
        device: str = "cpu",
    ):
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.class_names = class_names
        self.transform = transform

        load_checkpoint(checkpoint_path, model, device=str(self.device))
        self.model = model.to(self.device)
        self.model.eval()
        logger.info(f"Loaded checkpoint from {checkpoint_path}")

    @torch.no_grad()
    def predict(self, image: Image.Image) -> dict:
        """
        Predict the class of a single PIL image.

        Returns:
            {
                "class": "mel",
                "class_idx": 0,
                "confidence": 0.87,
                "probabilities": {"mel": 0.87, "nv": 0.05, ...}
            }
        """
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        logits = self.model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze().cpu()

        class_idx = probs.argmax().item()
        return {
            "class": self.class_names[class_idx],
            "class_idx": class_idx,
            "confidence": probs[class_idx].item(),
            "probabilities": {name: probs[i].item() for i, name in enumerate(self.class_names)},
        }

    @torch.no_grad()
    def predict_batch(self, images: list[Image.Image]) -> list[dict]:
        """Predict a list of PIL images."""
        return [self.predict(img) for img in images]
