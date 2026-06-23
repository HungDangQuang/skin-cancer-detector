#!/bin/bash
# ============================================================================
# Step 2 (FULL) — train ONE teacher across all 5 CV folds in a SINGLE job.
# The 5 folds run sequentially inside this one job (no Slurm array), so one
# model = one job. Pick the teacher via TEACHER (default: efficientnet_b4).
# Prereq:  10_prepare_data finished.
# Submit:  bash slurm/submit.sh slurm/11_train_teacher.slurm                       # baseline B4
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=efficientnetv2_m   # SOTA
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=convnextv2_base
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=maxvit_base
# Subset of folds (e.g. to split a heavy teacher under the 72 h cap into two jobs):
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=maxvit_base FOLDS="0 1 2"
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=maxvit_base FOLDS="3 4"
# Output:  experiments/runs/teacher/${TEACHER}/fold_{0..4}/
#          ├── checkpoints/best_model.pth
#          └── test_metrics.json
# Aggregate after all 5 folds finish:
#          bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#              RUN_DIR=experiments/runs/teacher/efficientnet_b4
# ============================================================================
#SBATCH --job-name=train_teacher
#SBATCH --output=logs/train_teacher_%j.out
#SBATCH --error=logs/train_teacher_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=mps:l40:4
#SBATCH --mem=16G
#SBATCH --time=72:00:00      # 5 folds run sequentially in one job — use the cap

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 20480      # ~20 GB headroom: covers baseline B4 and the larger SOTA
                       # teachers (convnextv2_base / maxvit_base) at batch 32.
                       # If a SOTA teacher still OOMs, reduce batch via
                       # `... TEACHER=maxvit_base` + edit/override training.batch_size.
setup_mps

TEACHER="${TEACHER:-efficientnet_b4}"
FOLDS="${FOLDS:-0 1 2 3 4}"
# Anti-overfit knobs (single-token → safe through submit.sh --export). Defaults
# reproduce the original behavior (augmentation=light, drop_path_rate=0.0).
#   AUG=heavy DROP_PATH=0.2   → stronger aug + stochastic depth on the teacher.
AUG="${AUG:-light}"
DROP_PATH="${DROP_PATH:-0.0}"
# Extra Hydra overrides (space-separated), passed verbatim — e.g. for maxvit_base:
#   EXTRA="cudnn_deterministic=false training.batch_size=16"
# Deliberately UNquoted at the call site so multiple overrides word-split.
EXTRA="${EXTRA:-}"
echo "[job] Training teacher (full) | teacher ${TEACHER} | folds ${FOLDS} | aug=${AUG} drop_path=${DROP_PATH} | extra='${EXTRA}'"
nvidia-smi || true
for FOLD in ${FOLDS}; do
    echo "[job] === teacher ${TEACHER} | fold ${FOLD} (start $(date '+%F %T')) ==="
    python scripts/train_teacher.py "teacher=${TEACHER}" "data.fold=${FOLD}" "augmentation=${AUG}" "teacher.drop_path_rate=${DROP_PATH}" ${EXTRA}
done

echo "[job] DONE"
