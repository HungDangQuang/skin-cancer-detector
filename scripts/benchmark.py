"""
Full computational profile of a trained checkpoint (PC + device-independent).

This is the *superset* benchmark used for the thesis "deployment story". It
complements scripts/benchmark_mobile.py (which is the narrow single-core CPU
latency proxy) by also reporting FLOPs, GPU latency, batch-throughput sweeps,
percentile latencies and peak memory.

Three groups of numbers are produced:

  1. Device-independent (report once per architecture):
       - parameter count (total + trainable, millions)
       - FLOPs / MACs for one 1x3xHxW forward (GFLOPs)
       - FP32 model size (MB, raw state-dict tensor bytes)

  2. Latency @ batch=1 (real-time / on-device scenario), per device:
       - mean / std / median / p90 / p95 / p99 (ms)
       - CPU is measured single-threaded so it is comparable to a phone CPU
         and to benchmark_mobile.py; GPU (if present) uses CUDA events + sync.

  3. Throughput sweep (batch processing scenario), per device:
       - images/sec at each requested batch size + peak GPU memory (MB).

Quantization is intentionally de-scoped: every number here is FP32. Always
quote results together with the hardware they were measured on (printed in the
JSON under "device_info").

Usage:
    python scripts/benchmark.py --model-name efficientnet_b0 \\
        --checkpoint experiments/runs/kd_..._to_efficientnet_b0/fold_0/checkpoints/best_model.pth
    python scripts/benchmark.py --model-name efficientnetv2_m --checkpoint ... \\
        --device cuda --batch-sizes 1 8 32 64
"""
import argparse
import json
import platform
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


def _latency_stats(latencies_ms: list[float]) -> dict:
    """Summarize a list of per-call latencies (ms) into mean/std/percentiles."""
    arr = np.asarray(latencies_ms, dtype=np.float64)
    return {
        "mean": round(float(arr.mean()), 3),
        "std": round(float(arr.std()), 3),
        "median": round(float(np.median(arr)), 3),
        "p90": round(float(np.percentile(arr, 90)), 3),
        "p95": round(float(np.percentile(arr, 95)), 3),
        "p99": round(float(np.percentile(arr, 99)), 3),
        "min": round(float(arr.min()), 3),
        "max": round(float(arr.max()), 3),
    }


def _count_flops(model: torch.nn.Module, dummy: torch.Tensor) -> float | None:
    """One-forward FLOPs via torch's built-in counter (no extra dependency).

    Returns total FLOPs, or None if the counter is unavailable (older torch)
    or fails for this architecture — the rest of the benchmark still runs.
    """
    try:
        from torch.utils.flop_counter import FlopCounterMode
    except ImportError:
        logger.warning("torch.utils.flop_counter unavailable — skipping FLOPs.")
        return None
    try:
        counter = FlopCounterMode(display=False)
        with counter, torch.no_grad():
            model(dummy)
        return float(counter.get_total_flops())
    except Exception as exc:  # noqa: BLE001 - FLOP counting is best-effort
        logger.warning(f"FLOP counting failed ({exc}) — skipping FLOPs.")
        return None


def _measure_latency(model, dummy, device, warmup, iters) -> dict:
    """Per-call latency @ the dummy's batch size on `device`."""
    is_cuda = device.type == "cuda"
    with torch.no_grad():
        for _ in range(warmup):
            model(dummy)
        if is_cuda:
            torch.cuda.synchronize()
        latencies_ms = []
        for _ in range(iters):
            if is_cuda:
                start = torch.cuda.Event(enable_timing=True)
                end = torch.cuda.Event(enable_timing=True)
                start.record()
                model(dummy)
                end.record()
                torch.cuda.synchronize()
                latencies_ms.append(start.elapsed_time(end))
            else:
                t0 = time.perf_counter()
                model(dummy)
                latencies_ms.append((time.perf_counter() - t0) * 1000.0)
    return _latency_stats(latencies_ms)


def _measure_throughput(model, device, image_size, batch_sizes, warmup, iters) -> list[dict]:
    """images/sec at each batch size; peak GPU memory if on CUDA."""
    is_cuda = device.type == "cuda"
    results = []
    for bs in batch_sizes:
        dummy = torch.randn(bs, 3, image_size, image_size, device=device)
        if is_cuda:
            torch.cuda.reset_peak_memory_stats(device)
        with torch.no_grad():
            for _ in range(warmup):
                model(dummy)
            if is_cuda:
                torch.cuda.synchronize()
            t0 = time.perf_counter()
            for _ in range(iters):
                model(dummy)
            if is_cuda:
                torch.cuda.synchronize()
            elapsed = time.perf_counter() - t0
        images_per_sec = (bs * iters) / elapsed
        entry = {
            "batch_size": bs,
            "images_per_sec": round(images_per_sec, 2),
            "ms_per_batch": round(elapsed / iters * 1000.0, 3),
        }
        if is_cuda:
            entry["peak_mem_mb"] = round(
                torch.cuda.max_memory_allocated(device) / 1024 ** 2, 2
            )
        results.append(entry)
    return results


def main():
    parser = argparse.ArgumentParser()
    # Drive choices from the registry so new architectures are benchmarkable
    # without editing this list.
    parser.add_argument("--model-name", required=True,
                        choices=sorted(MODEL_REGISTRY.keys()))
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", default=None,
                        help="JSON path (default: reports/benchmark/<model>.json)")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto",
                        help="Latency/throughput device. 'auto' = cuda if available, "
                             "but CPU @ batch=1 is ALWAYS measured for the mobile proxy.")
    parser.add_argument("--cpu-threads", type=int, default=1,
                        help="torch threads for the CPU latency proxy (1 = phone-like).")
    parser.add_argument("--warmup", type=int, default=10, help="Warmup forward passes (untimed)")
    parser.add_argument("--iters", type=int, default=100, help="Timed forward passes")
    parser.add_argument("--batch-sizes", type=int, nargs="+", default=[1, 8, 32],
                        help="Batch sizes for the throughput sweep")
    args = parser.parse_args()

    cuda_available = torch.cuda.is_available()
    use_cuda = args.device == "cuda" or (args.device == "auto" and cuda_available)
    if args.device == "cuda" and not cuda_available:
        logger.warning("--device cuda requested but no GPU visible — falling back to CPU.")
        use_cuda = False

    cfg = load_config(args.config)
    image_size = int(cfg.data.image_size)

    # ---- Device-independent metrics (built once, on CPU) ----
    model, _ = build_model_from_name(args.model_name, cfg)
    load_checkpoint(args.checkpoint, model, device="cpu")
    model.eval()

    n_params = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    size_bytes = sum(t.numel() * t.element_size() for t in model.state_dict().values())
    cpu_dummy_b1 = torch.randn(1, 3, image_size, image_size)
    flops = _count_flops(model, cpu_dummy_b1)

    result = {
        "model_name": args.model_name,
        "checkpoint": args.checkpoint,
        "image_size": image_size,
        "params_millions": round(n_params / 1e6, 3),
        "trainable_params_millions": round(n_trainable / 1e6, 3),
        "fp32_size_mb": round(size_bytes / 1024 ** 2, 3),
        "gflops": round(flops / 1e9, 3) if flops is not None else None,
        "gmacs": round(flops / 2e9, 3) if flops is not None else None,
        "iters": args.iters,
        "warmup": args.warmup,
        "device_info": {
            "platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "torch_version": torch.__version__,
            "cuda_available": cuda_available,
            "gpu_name": torch.cuda.get_device_name(0) if cuda_available else None,
        },
        "latency_batch1": {},
        "throughput": {},
    }

    # ---- CPU latency @ batch=1 (mobile-comparable proxy) — always measured ----
    torch.set_num_threads(args.cpu_threads)
    cpu_device = torch.device("cpu")
    model.to(cpu_device)
    result["latency_batch1"]["cpu"] = _measure_latency(
        model, cpu_dummy_b1.to(cpu_device), cpu_device, args.warmup, args.iters
    )
    result["latency_batch1"]["cpu"]["threads"] = args.cpu_threads

    # ---- GPU latency @ batch=1 + throughput sweep ----
    if use_cuda:
        gpu_device = torch.device("cuda")
        model.to(gpu_device)
        gpu_dummy_b1 = torch.randn(1, 3, image_size, image_size, device=gpu_device)
        result["latency_batch1"]["cuda"] = _measure_latency(
            model, gpu_dummy_b1, gpu_device, args.warmup, args.iters
        )
        result["throughput"]["cuda"] = _measure_throughput(
            model, gpu_device, image_size, args.batch_sizes, args.warmup, args.iters
        )
    else:
        # No GPU → throughput sweep on CPU so the field is never empty.
        result["throughput"]["cpu"] = _measure_throughput(
            model, cpu_device, image_size, args.batch_sizes, args.warmup, args.iters
        )

    cpu_med = result["latency_batch1"]["cpu"]["median"]
    gpu_med = result["latency_batch1"].get("cuda", {}).get("median")
    logger.info(
        f"{args.model_name}: {result['params_millions']}M params | "
        f"{result['gflops']} GFLOPs | {result['fp32_size_mb']} MB | "
        f"CPU b1 {cpu_med} ms"
        + (f" | GPU b1 {gpu_med} ms" if gpu_med is not None else "")
    )

    out_path = args.output or f"reports/benchmark/{args.model_name}.json"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    logger.info(f"Benchmark saved to {out_path}")


if __name__ == "__main__":
    main()
