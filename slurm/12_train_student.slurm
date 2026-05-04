#!/bin/bash
# ============================================================================
# Step 3 (FULL) — KD-train one student from the trained teacher.
# Generic dispatcher — pass STUDENT and (optionally) TRAINING via --export.
#
# Prereq:  11_train_teacher finished (best_model.pth exists).
# Submit:
#   sbatch --export=ALL,STUDENT=efficientnet_b0      slurm/12_train_student.slurm
#   sbatch --export=ALL,STUDENT=mobilenetv3_large    slurm/12_train_student.slurm
#   sbatch --export=ALL,STUDENT=mobilevit_s          slurm/12_train_student.slurm
#
# For the controlled comparison (no KD baseline):
#   sbatch --export=ALL,STUDENT=efficientnet_b0,TRAINING=baseline slurm/12_train_student.slurm
# ============================================================================
#SBATCH --job-name=train_student
#SBATCH --output=logs/train_student_%j.out
#SBATCH --error=logs/train_student_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=mps:l40:4
#SBATCH --mem=16G
#SBATCH --time=18:00:00

REQUIRED_VRAM=18432    # teacher (frozen) + student + grads, batch 64

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
TRAINING=${TRAINING:-distillation}
echo "Student: ${STUDENT} | Training mode: ${TRAINING}"
nvidia-smi
python scripts/train_student.py student=${STUDENT} training=${TRAINING}
