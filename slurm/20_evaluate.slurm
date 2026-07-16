#!/bin/bash
# ============================================================================
# Evaluate a checkpoint on the held-out test split.
# Submit:
#   bash slurm/submit.sh slurm/20_evaluate.slurm \
#       MODEL=efficientnetv2_m \
#       CKPT=experiments/runs/teacher/efficientnetv2_m/checkpoints/best_model.pth \
#       OUT=reports/results/teacher.json
# ============================================================================
#SBATCH --job-name=evaluate
#SBATCH --output=logs/evaluate_%j.out
#SBATCH --error=logs/evaluate_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=mps:l40:1
#SBATCH --mem=8G
#SBATCH --time=01:00:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 6144
setup_mps

: "${MODEL:?MODEL env var required (e.g. mobilenetv4_conv_medium)}"
: "${CKPT:?CKPT env var required (path to .pth)}"
OUT="${OUT:-reports/results/${MODEL}_metrics.json}"

echo "[job] Evaluating ${MODEL} from ${CKPT} → ${OUT}"
python scripts/evaluate.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --output "${OUT}"

echo "[job] DONE"
