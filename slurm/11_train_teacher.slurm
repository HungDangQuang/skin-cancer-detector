#!/bin/bash
# ============================================================================
# Step 2 (FULL) — train ONE teacher across all 5 CV folds in a SINGLE job.
# The 5 folds run sequentially inside this one job (no Slurm array), so one
# model = one job. Pick the teacher via TEACHER (default: efficientnetv2_m).
# Prereq:  10_prepare_data finished.
# Submit:  bash slurm/submit.sh slurm/11_train_teacher.slurm                       # baseline B4
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=efficientnetv2_m   # SOTA
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=convnextv2_base
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=maxvit_base
#          # panderm (foundation): pass the downloaded checkpoint via EXTRA
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=panderm \
#              EXTRA="teacher.weights_path=/abs/path/panderm_bb_data6_checkpoint-499.pth"
#          # privileged (LUPI) teacher (direction A) — needs prepare run with the
#          # SAME META_COLS, and a *_privileged teacher name:
#          bash slurm/submit.sh slurm/11_train_teacher.slurm \
#              TEACHER=efficientnetv2_m_privileged PRIVILEGED=1 \
#              META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
# Subset of folds (e.g. to split a heavy teacher under the 72 h cap into two jobs):
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=maxvit_base FOLDS="0 1 2"
#          bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=maxvit_base FOLDS="3 4"
# Output:  experiments/runs/teacher/${TEACHER}/fold_{0..4}/
#          ├── checkpoints/best_model.pth
#          └── test_metrics.json
# Aggregate after all 5 folds finish:
#          bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#              RUN_DIR=experiments/runs/teacher/efficientnetv2_m
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

TEACHER="${TEACHER:-efficientnetv2_m}"
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
# Privileged (LUPI) teacher (direction A): PRIVILEGED=1 feeds metadata into the
# teacher (requires TEACHER=<name>_privileged and prepare run with the same
# META_COLS). META_COLS must be comma-separated with NO spaces (word-split safe).
PRIVILEGED="${PRIVILEGED:-0}"
META_COLS="${META_COLS:-tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color,tbp_lv_areaMM2,tbp_lv_eccentricity,tbp_lv_deltaLBnorm}"
PRIV_ARGS=""
if [ "${PRIVILEGED}" = "1" ]; then
    PRIV_ARGS="data.metadata_as_input=true data.metadata_cols=[${META_COLS}]"
fi
echo "[job] Training teacher (full) | teacher ${TEACHER} | folds ${FOLDS} | aug=${AUG} drop_path=${DROP_PATH} | privileged=${PRIVILEGED} | extra='${EXTRA}'"
nvidia-smi || true
# noglob so the unquoted ${PRIV_ARGS} 'data.metadata_cols=[...]' bracket token
# is passed to Hydra verbatim (word-split on spaces, never pathname-expanded).
set -f
for FOLD in ${FOLDS}; do
    echo "[job] === teacher ${TEACHER} | fold ${FOLD} (start $(date '+%F %T')) ==="
    python scripts/train_teacher.py "teacher=${TEACHER}" "data.fold=${FOLD}" "augmentation=${AUG}" "teacher.drop_path_rate=${DROP_PATH}" ${PRIV_ARGS} ${EXTRA}
done
set +f

echo "[job] DONE"
