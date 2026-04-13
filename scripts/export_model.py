"""
Export trained model to ONNX or TorchScript.

Usage:
    python scripts/export_model.py --checkpoint path/to/best_model.pth --format onnx
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import torch

from src.models.registry import build_model
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--format", choices=["onnx", "torchscript"], default="onnx")
    parser.add_argument("--output", default="exports/model")
    parser.add_argument("--config", default="configs/config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    model = build_model(cfg)
    load_checkpoint(args.checkpoint, model)
    model.eval()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    dummy = torch.randn(1, 3, cfg.data.image_size, cfg.data.image_size)

    if args.format == "onnx":
        out_path = args.output + ".onnx"
        torch.onnx.export(
            model, dummy, out_path,
            input_names=["image"], output_names=["logits"],
            dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}},
            opset_version=17,
        )
    else:
        out_path = args.output + ".pt"
        scripted = torch.jit.script(model)
        scripted.save(out_path)

    logger.info(f"Model exported to {out_path}")


if __name__ == "__main__":
    main()
