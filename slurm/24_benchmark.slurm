#!/bin/bash
# ============================================================================
# Full computational profile of a checkpoint (PC + device-independent).
#
# Superset of slurm/21_benchmark_mobile.slurm: also measures FLOPs, GPU
# latency, batch-throughput sweep and percentile latencies. The CPU @ batch=1
# latency proxy is ALWAYS measured (single-thread, phone-comparable); the GPU
# numbers are added when a GPU is allocated.
#
# Submit (with GPU — gets CPU + GPU numbers):
#   bash slurm/submit.sh slurm/24_benchmark.slurm \
#       MODEL=efficientnet_b0 \
#       CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/fold_0/checkpoints/best_model.pth
#
# CPU-only (skip GPU; faster to queue):
#   bash slurm/submit.sh slurm/24_benchmark.slurm MODEL=... CKPT=... DEVICE=cpu
#
# Output (default): reports/benchmark/<MODEL>.json
# ============================================================================
#SBATCH --job-name=benchmark
#SBATCH --output=logs/benchmark_%j.out
#SBATCH --error=logs/benchmark_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=mps:l40:1
#SBATCH --mem=8G
#SBATCH --time=00:30:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env

: "${MODEL:?MODEL env var required (e.g. efficientnet_b0)}"
: "${CKPT:?CKPT env var required (path to best_model.pth)}"
DEVICE="${DEVICE:-auto}"
OUT="${OUT:-reports/benchmark/${MODEL}.json}"
BATCH_SIZES="${BATCH_SIZES:-1 8 32}"

# Only grab a GPU when we actually intend to use it.
if [ "${DEVICE}" != "cpu" ]; then
    acquire_gpu 4096
    setup_mps
fi

echo "[job] Benchmarking ${MODEL} from ${CKPT} (device=${DEVICE}) -> ${OUT}"
python scripts/benchmark.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --device "${DEVICE}" \
    --batch-sizes ${BATCH_SIZES} \
    --output "${OUT}"

echo "[job] DONE"
