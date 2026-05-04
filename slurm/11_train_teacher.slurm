#!/bin/bash
# ============================================================================
# Step 2 (FULL) — train teacher EfficientNet-B4 (50 epochs, batch 32).
# Prereq:  10_prepare_data finished (splits exist under data/splits/isic2024/).
# Submit:  sbatch slurm/11_train_teacher.slurm
# Output:  experiments/runs/teacher/efficientnet_b4/checkpoints/best_model.pth
# ============================================================================
#SBATCH --job-name=train_teacher
#SBATCH --output=logs/train_teacher_%j.out
#SBATCH --error=logs/train_teacher_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=mps:l40:4
#SBATCH --mem=16G
#SBATCH --time=24:00:00

REQUIRED_VRAM=14336    # ~14 GB: B4 + batch 32 @ 224, AdamW state, augmentations

module clear -f
module load shared python312
source /datastore/${USER}/venv/bin/activate
unset CUDA_VISIBLE_DEVICES

CHECK_OUT=$(/usr/local/bin/gpu_check.sh $REQUIRED_VRAM $SLURM_JOB_ID)
EXIT_CODE=$?
[ $EXIT_CODE -eq 10 ] && { echo "$CHECK_OUT"; exit 0; }
[ $EXIT_CODE -eq 11 ] && { echo "$CHECK_OUT"; exit 1; }
BEST_GPU=$CHECK_OUT
echo "Job $SLURM_JOB_ID running on GPU: $BEST_GPU"

export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps-job$SLURM_JOB_ID
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-mps-log-job$SLURM_JOB_ID
rm -rf  $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
mkdir -p $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
export CUDA_VISIBLE_DEVICES=$BEST_GPU

cd ${SLURM_SUBMIT_DIR}
nvidia-smi
python scripts/train_teacher.py
