#!/bin/bash
# ============================================================================
# Step 1 (POC) — generate synthetic fixtures (CPU-only, but Slurm requires
# a GPU declaration so we ask for the smallest slot).
# Submit:  sbatch slurm/01_prepare_poc.slurm
# Output:  data/processed/poc/, data/splits/poc/
# ============================================================================
#SBATCH --job-name=prepare_poc
#SBATCH --output=logs/prepare_poc_%j.out
#SBATCH --error=logs/prepare_poc_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=mps:1
#SBATCH --mem=4G
#SBATCH --time=00:15:00

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
python scripts/prepare_poc_data.py
