"""
Single-image inference script.

Usage:
    python scripts/predict.py --image path/to/image.jpg \\
        --model-name efficientnet_b0 --checkpoint path/to/best_model.pth
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image

from src.data.transforms import build_transforms
from src.inference.predictor import Predictor
from src.models.registry import MODEL_REGISTRY, build_model_from_name
from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--model-name", required=True,
                        choices=sorted(MODEL_REGISTRY.keys()))
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Decision threshold (use Youden threshold from evaluation)")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    model, model_cfg = build_model_from_name(args.model_name, cfg)
    transform = build_transforms(model_cfg, split="val")

    predictor = Predictor(
        model=model,
        checkpoint_path=args.checkpoint,
        transform=transform,
        device=cfg.device,
        threshold=args.threshold,
    )

    image = Image.open(args.image).convert("RGB")
    result = predictor.predict(image)

    print(f"\nPrediction : {result['class']}")
    print(f"Probability: {result['probability']:.4f}")
    print(f"Threshold  : {result['threshold']:.4f}")


if __name__ == "__main__":
    main()
