#!/bin/bash
# ============================================================================
# Evaluate a checkpoint on the held-out test split.
# Submit:
#   sbatch --export=ALL,MODEL=efficientnet_b4,CKPT=experiments/runs/teacher/efficientnet_b4/checkpoints/best_model.pth,OUT=reports/results/teacher_metrics.json \
#       slurm/20_evaluate.slurm
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

REQUIRED_VRAM=6144

module clear -f
module load shared python312
source /datastore/${USER}/venv/bin/activate
unset CUDA_VISIBLE_DEVICES

CHECK_OUT=$(/usr/local/bin/gpu_check.sh $REQUIRED_VRAM $SLURM_JOB_ID)
EXIT_CODE=$?
[ $EXIT_CODE -eq 10 ] && { echo "$CHECK_OUT"; exit 0; }
[ $EXIT_CODE -eq 11 ] && { echo "$CHECK_OUT"; exit 1; }
BEST_GPU=$CHECK_OUT

export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps-job$SLURM_JOB_ID
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-mps-log-job$SLURM_JOB_ID
rm -rf  $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
mkdir -p $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
export CUDA_VISIBLE_DEVICES=$BEST_GPU

: "${MODEL:?MODEL env var required (e.g. efficientnet_b0)}"
: "${CKPT:?CKPT env var required (path to .pth)}"
OUT=${OUT:-reports/results/${MODEL}_metrics.json}

cd ${SLURM_SUBMIT_DIR}
echo "Evaluating ${MODEL} from ${CKPT} → ${OUT}"
python scripts/evaluate.py \
    --model-name "${MODEL}" \
    --checkpoint "${CKPT}" \
    --output "${OUT}"
