#!/bin/bash
# ============================================================================
# Step 3 (POC) — KD-train one student from the POC teacher.
# Prereq:  Step 2 completed (teacher best_model.pth exists).
# Submit:
#   bash slurm/submit.sh slurm/03_poc_student.slurm
#   bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv3_large
#   bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilevit_s
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

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 10240    # teacher (frozen) + student + grads, batch 16
setup_mps

STUDENT="${STUDENT:-efficientnet_b0}"
echo "[job] KD student: ${STUDENT}"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
else
    echo "[job] nvidia-smi not on PATH — checking via PyTorch"
    python -c "import torch; print('cuda available:', torch.cuda.is_available(), '| devices:', torch.cuda.device_count(), '| name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'n/a')"
fi

python scripts/train_student.py --config-name config_poc student="${STUDENT}"

echo "[job] DONE"
