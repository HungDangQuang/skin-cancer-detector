#!/bin/bash
# ============================================================================
# Build the FIXED benchmark input set from the internal held-out test split.
# CPU-only (~100 images, no GPU). Output is reused for PC + mobile latency
# benchmarks and the PC<->mobile parity check.
#
# Submit (input set only):
#   bash slurm/submit.sh slurm/26_make_benchmark_set.slurm N=100
#
# Also dump per-model reference logits for parity (optional):
#   bash slurm/submit.sh slurm/26_make_benchmark_set.slurm N=100 \
#       MODEL=efficientnet_b0 \
#       CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/fold_0/checkpoints/best_model.pth
#
# Output (default): data/benchmark_set/  (rsync to the Mac/phone; do not commit)
# ============================================================================
#SBATCH --job-name=make_benchmark_set
#SBATCH --output=logs/make_benchmark_set_%j.out
#SBATCH --error=logs/make_benchmark_set_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:20:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
# No GPU: reference logits (if requested) run on CPU — ~100 images is trivial.

N="${N:-100}"
OUTDIR="${OUTDIR:-data/benchmark_set}"

ARGS=(--n "${N}" --output-dir "${OUTDIR}")
# MODEL + CKPT are optional; pass both or neither.
if [ -n "${MODEL:-}" ] && [ -n "${CKPT:-}" ]; then
    ARGS+=(--model-name "${MODEL}" --checkpoint "${CKPT}")
elif [ -n "${MODEL:-}" ] || [ -n "${CKPT:-}" ]; then
    echo "ERROR: pass BOTH MODEL and CKPT (or neither) to dump reference logits."
    exit 2
fi

echo "[job] Building benchmark set (N=${N}) -> ${OUTDIR}"
python scripts/make_benchmark_set.py "${ARGS[@]}"

echo "[job] DONE"
