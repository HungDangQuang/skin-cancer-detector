#!/bin/bash
# ============================================================================
# Step 3 (POC) — KD-train EfficientNet-B0 student from the POC teacher.
# Prereq:  slurm/02_poc_teacher.slurm completed (teacher checkpoint exists).
# Submit:  sbatch slurm/03_poc_student.slurm
# Override student via --export:
#     sbatch --export=ALL,STUDENT=mobilenetv3_large slurm/03_poc_student.slurm
# ============================================================================
#SBATCH --job-name=poc_student
#SBATCH --output=logs/poc_student_%j.out
#SBATCH --error=logs/poc_student_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=mps:l40:2
#SBATCH --mem=8G
#SBATCH --time=01:00:00

REQUIRED_VRAM=10240   # teacher (frozen) + student + grads, batch 16

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
STUDENT=${STUDENT:-efficientnet_b0}
echo "KD student: ${STUDENT}"
python scripts/train_student.py --config-name config_poc student=${STUDENT}
