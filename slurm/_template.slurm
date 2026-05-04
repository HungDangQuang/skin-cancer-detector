#!/bin/bash
# ============================================================================
# UIT Slurm template — copy this and customize for each training/eval job.
# Submit with: sbatch slurm/<your_script>.slurm
# Logs: logs/<job-name>_<jobid>.out / .err
# ============================================================================
#SBATCH --job-name=skin_template
#SBATCH --output=logs/template_%j.out
#SBATCH --error=logs/template_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=mps:2          # mps:2 generic, or mps:l40:2 / mps:a100:2 for specific cards
#SBATCH --mem=4G
#SBATCH --time=00:30:00       # HH:MM:SS — max 72:00:00

REQUIRED_VRAM=4096            # MB — must be < 44000 (L40) or < 80000 (A100)

# ============================================================================
# ENVIRONMENT
# ============================================================================
module clear -f
module load shared python312

# Activate project venv (created by slurm/setup_env.sh on first use)
source /datastore/${USER}/venv/bin/activate

# Let gpu_check.sh decide which GPU to bind
unset CUDA_VISIBLE_DEVICES

# ============================================================================
# GPU SELECTION (returns 10 → requeue, 11 → fatal after 5 retries)
# ============================================================================
CHECK_OUT=$(/usr/local/bin/gpu_check.sh $REQUIRED_VRAM $SLURM_JOB_ID)
EXIT_CODE=$?
if [ $EXIT_CODE -eq 10 ]; then
    echo "$CHECK_OUT"
    exit 0
elif [ $EXIT_CODE -eq 11 ]; then
    echo "$CHECK_OUT"
    exit 1
fi
BEST_GPU=$CHECK_OUT
echo "Job $SLURM_JOB_ID running on GPU: $BEST_GPU"

# ============================================================================
# PRIVATE MPS SERVER (per-job pipe)
# ============================================================================
export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps-job$SLURM_JOB_ID
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-mps-log-job$SLURM_JOB_ID
rm -rf  $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
mkdir -p $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
export CUDA_VISIBLE_DEVICES=$BEST_GPU

# ============================================================================
# RUN
# ============================================================================
cd ${SLURM_SUBMIT_DIR}
echo "Working dir: $(pwd)"
nvidia-smi

# REPLACE WITH YOUR COMMAND:
python -c "import torch; print('torch:', torch.__version__, '| cuda:', torch.cuda.is_available())"
