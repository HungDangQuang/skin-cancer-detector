#!/bin/bash
# ============================================================================
# Step 3 (POC) — KD-train one student from the POC teacher.
# Prereq:  Step 2 completed for the SAME TEACHER (its best_model.pth exists).
# Submit:
#   bash slurm/submit.sh slurm/03_poc_student.slurm
#   bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv4_conv_medium
#   bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=efficientformerv2_s2
#   # Smoke-test a SOTA pair (TEACHER must match the one POC-trained in step 2):
#   bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv4_conv_medium TEACHER=convnextv2_base
#   STUDENT in {mobilenetv4_conv_medium, mobilenetv4_conv_medium, efficientformerv2_s2,
#               mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2}
#   TEACHER in {efficientnetv2_m, efficientnetv2_m, convnextv2_base, maxvit_base}
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
acquire_gpu 14336    # teacher (frozen, incl. SOTA convnextv2/maxvit) + student + grads, batch 16
setup_mps

STUDENT="${STUDENT:-mobilenetv4_conv_medium}"
TEACHER="${TEACHER:-efficientnetv2_m}"
# Extra Hydra overrides (space-separated), passed verbatim — e.g. with a maxvit
# teacher: EXTRA="cudnn_deterministic=false".
# Deliberately UNquoted at the call site so multiple overrides word-split.
EXTRA="${EXTRA:-}"
echo "[job] POC KD: ${TEACHER} -> ${STUDENT} | extra='${EXTRA}'"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
else
    echo "[job] nvidia-smi not on PATH — checking via PyTorch"
    python -c "import torch; print('cuda available:', torch.cuda.is_available(), '| devices:', torch.cuda.device_count(), '| name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'n/a')"
fi

python scripts/train_student.py --config-name config_poc student="${STUDENT}" "teacher=${TEACHER}" ${EXTRA}

echo "[job] DONE"
