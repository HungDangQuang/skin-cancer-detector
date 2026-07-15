"""
Benchmark a trained checkpoint for mobile deployability.

Reports the three architecture-level deployability numbers (fold-independent):
  - parameter count (millions)
  - FP32 model size (MB, raw state-dict tensor bytes)
  - single-core CPU inference latency (median + p90, ms) on a 1x3xHxW input

The latency is a *proxy* — it is measured single-threaded on the cluster CPU,
not on a phone, but it ranks the architectures consistently and supports the
"runs on mobile as-is" claim (INT8/TFLite quantization is intentionally
de-scoped; backbones run FP32).

Usage:
    python scripts/benchmark_mobile.py --model-name mobilenetv4_conv_medium \\
        --checkpoint experiments/runs/kd_..._to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch

from src.models.registry import MODEL_REGISTRY, build_model_from_name
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    # Drive choices from the registry so new architectures (e.g. the mobile-SOTA
    # students) are benchmarkable without editing this list — it was stale before.
    parser.add_argument("--model-name", required=True,
                        choices=sorted(MODEL_REGISTRY.keys()))
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", default=None,
                        help="JSON path (default: reports/mobile_benchmark/<model>.json)")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup forward passes (untimed)")
    parser.add_argument("--iters", type=int, default=100, help="Timed forward passes")
    args = parser.parse_args()

    # Single-core → stable, comparable latency proxy across architectures.
    torch.set_num_threads(1)

    cfg = load_config(args.config)
    model, _ = build_model_from_name(args.model_name, cfg)
    load_checkpoint(args.checkpoint, model, device="cpu")
    model.eval()

    n_params = sum(p.numel() for p in model.parameters())
    state_dict = model.state_dict()
    size_bytes = sum(t.numel() * t.element_size() for t in state_dict.values())

    image_size = int(cfg.data.image_size)
    dummy = torch.randn(1, 3, image_size, image_size)

    with torch.no_grad():
        for _ in range(args.warmup):
            model(dummy)
        latencies_ms = []
        for _ in range(args.iters):
            t0 = time.perf_counter()
            model(dummy)
            latencies_ms.append((time.perf_counter() - t0) * 1000.0)

    latencies_ms = np.array(latencies_ms)
    result = {
        "model_name": args.model_name,
        "checkpoint": args.checkpoint,
        "params_millions": round(n_params / 1e6, 3),
        "fp32_size_mb": round(size_bytes / 1024 ** 2, 3),
        "image_size": image_size,
        "cpu_latency_ms_median": round(float(np.median(latencies_ms)), 3),
        "cpu_latency_ms_p90": round(float(np.percentile(latencies_ms, 90)), 3),
        "cpu_threads": 1,
        "iters": args.iters,
    }

    logger.info(
        f"{args.model_name}: {result['params_millions']}M params | "
        f"{result['fp32_size_mb']} MB | "
        f"{result['cpu_latency_ms_median']} ms median (p90 {result['cpu_latency_ms_p90']} ms)"
    )

    out_path = args.output or f"reports/mobile_benchmark/{args.model_name}.json"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    logger.info(f"Benchmark saved to {out_path}")


if __name__ == "__main__":
    main()
