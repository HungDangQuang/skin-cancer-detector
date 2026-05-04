#!/bin/bash
# ============================================================================
# Step 2 (POC) — train teacher (EfficientNet-B4) for 2 epochs on synthetic data.
# Submit:  sbatch slurm/02_poc_teacher.slurm
# Output:  experiments/poc/teacher/efficientnet_b4/checkpoints/best_model.pth
# ============================================================================
#SBATCH --job-name=poc_teacher
#SBATCH --output=logs/poc_teacher_%j.out
#SBATCH --error=logs/poc_teacher_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=mps:l40:2
#SBATCH --mem=8G
#SBATCH --time=01:00:00

REQUIRED_VRAM=8192    # B4 + batch 16 on synthetic 224x224

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
python scripts/train_teacher.py --config-name config_poc
