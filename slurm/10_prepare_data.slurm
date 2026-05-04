#!/bin/bash
# ============================================================================
# Step 1 (FULL) — preprocess ISIC 2024 + PAD-UFES-20 and generate 5-fold splits.
# Prereq:  raw data downloaded to data/raw/isic2024/ (and optionally pad_ufes_20).
# Submit:  sbatch slurm/10_prepare_data.slurm
# Output:  data/processed/isic2024/, data/splits/isic2024/fold_{0..4}/
# ============================================================================
#SBATCH --job-name=prepare_data
#SBATCH --output=logs/prepare_data_%j.out
#SBATCH --error=logs/prepare_data_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=mps:1
#SBATCH --mem=16G
#SBATCH --time=04:00:00       # ~30GB HDF5 decode is I/O bound

REQUIRED_VRAM=2048

module clear -f
module load shared python312
source /datastore/${USER}/venv/bin/activate
unset CUDA_VISIBLE_DEVICES

CHECK_OUT=$(/usr/local/bin/gpu_check.sh $REQUIRED_VRAM $SLURM_JOB_ID)
EXIT_CODE=$?
[ $EXIT_CODE -eq 10 ] && { echo "$CHECK_OUT"; exit 0; }
[ $EXIT_CODE -eq 11 ] && { echo "$CHECK_OUT"; exit 1; }
export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps-job$SLURM_JOB_ID
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-mps-log-job$SLURM_JOB_ID
rm -rf  $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
mkdir -p $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
export CUDA_VISIBLE_DEVICES=$CHECK_OUT

cd ${SLURM_SUBMIT_DIR}
python scripts/prepare_data.py
