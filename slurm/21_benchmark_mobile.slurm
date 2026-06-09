#!/bin/bash
# ============================================================================
# Benchmark a checkpoint for mobile deployability (CPU-only, ~1 min).
#
# Reports params + FP32 size + single-core CPU latency. No GPU is requested:
# the latency proxy is measured single-threaded on CPU, so a GPU allocation
# would only slow the queue down for no benefit.
#
# Submit:
#   bash slurm/submit.sh slurm/21_benchmark_mobile.slurm \
#       MODEL=efficientnet_b0 \
#       CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/fold_0/checkpoints/best_model.pth
#
# Output (default): reports/mobile_benchmark/<MODEL>.json
# ============================================================================
#SBATCH --job-name=benchmark_mobile
#SBATCH --output=logs/benchmark_mobile_%j.out
#SBATCH --error=logs/benchmark_mobile_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:15:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
# No GPU — single-core CPU latency proxy is the point of this job.

: "${MODEL:?MODEL env var required (e.g. efficientnet_b0)}"
: "${CKPT:?CKPT env var required (path to best_model.pth)}"
OUT="${OUT:-reports/mobile_benchmark/${MODEL}.json}"

echo "[job] Benchmarking ${MODEL} from ${CKPT} -> ${OUT}"
python scripts/benchmark_mobile.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --output "${OUT}"

echo "[job] DONE"
