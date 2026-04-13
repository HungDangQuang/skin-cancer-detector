"""
Single-image inference script.

Usage:
    python scripts/predict.py --image path/to/image.jpg --checkpoint path/to/best_model.pth
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image

from src.data.transforms import build_transforms
from src.inference.predictor import Predictor
from src.models.registry import build_model
from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--checkpoint", required=True, help="Path to model checkpoint")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    model = build_model(cfg)
    transform = build_transforms(cfg, split="val")

    predictor = Predictor(
        model=model,
        checkpoint_path=args.checkpoint,
        class_names=list(cfg.data.classes),
        transform=transform,
        device=cfg.device,
    )

    image = Image.open(args.image).convert("RGB")
    result = predictor.predict(image)

    print(f"\nPrediction: {result['class']} (confidence: {result['confidence']:.2%})")
    print("Probabilities:")
    for cls, prob in sorted(result["probabilities"].items(), key=lambda x: -x[1]):
        print(f"  {cls:8s}: {prob:.4f}")


if __name__ == "__main__":
    main()
