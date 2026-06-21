#!/bin/bash
# ============================================================================
# Step 2 (POC) — train teacher for 2 epochs on synthetic data.
# Prereq:  Step 1 completed (data/splits/poc/ exists).
# Submit:  bash slurm/submit.sh slurm/02_poc_teacher.slurm                       # default efficientnet_b4
#          bash slurm/submit.sh slurm/02_poc_teacher.slurm TEACHER=convnextv2_base   # smoke-test a SOTA teacher
#   TEACHER in {efficientnet_b4, efficientnetv2_m, convnextv2_base, maxvit_base}
# Output:  experiments/poc/teacher/${TEACHER}/checkpoints/best_model.pth
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

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 12288    # 12 GB: covers SOTA teachers (convnextv2/maxvit) at batch 16 @ 224
setup_mps

TEACHER="${TEACHER:-efficientnet_b4}"
echo "[job] POC teacher: ${TEACHER}"

echo "[job] GPU info"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
else
    echo "[job] nvidia-smi not on PATH — checking via PyTorch"
    python -c "import torch; print('cuda available:', torch.cuda.is_available(), '| devices:', torch.cuda.device_count(), '| name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'n/a')"
fi

echo "[job] Training POC teacher"
python scripts/train_teacher.py --config-name config_poc "teacher=${TEACHER}"

echo "[job] DONE"
