#!/bin/bash
# ============================================================================
# Ablation A — imbalance-SAMPLING strategy (data-strategy proof).
# Re-trains the BEST student (KD: efficientnet_b4 -> mobilenetv3_large) varying
# ONLY the DynamicUndersampledSampler, holding teacher/seed/folds/hparams/loss
# fixed. Isolates the sampler's contribution so we can prove (or refute) that
# 1:5 dynamic undersampling beats its alternatives.
#
# The teacher is REUSED (frozen soft-label source, NOT retrained) from
# experiments/runs/teacher/${TEACHER}/fold_${FOLD}/checkpoints/best_model.pth,
# so 11_train_teacher must already be done. run_suffix forks each arm into its
# own run-dir subtree so the main 30 runs are never overwritten.
#
# SAMP selects the arm -> (sampler overrides + distinct run-dir suffix):
#   SAMP=off  -> data.use_weighted_sampler=false   (no resampling; natural ~1018:1)
#   SAMP=3    -> 1:3 malignant:benign
#   SAMP=10   -> 1:10
#   SAMP=5    == the MAIN run (kd_..._to_mobilenetv3_large); already trained.
#               Re-run only if you want a __ratio5 copy; otherwise reuse the main.
#
# Submit one arm (kicks off 5 folds, <=2 concurrent):
#   bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=off
#   bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=3
#   bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=10
#
# Output: experiments/runs/kd_<teacher>_to_<student>__<suffix>/fold_${TASK}/
#           ├── checkpoints/best_model.pth
#           ├── test_metrics.json   (now incl. auprc + sens_at_90/95spec)
#           └── predictions.csv     (y_true,y_prob,y_pred,source)
# Aggregate each arm, then compare to the main ratio-5 run with analyze-evaluation:
#   bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#       RUN_DIR=experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large__samp_off
# ============================================================================
#SBATCH --job-name=ablation_sampler
#SBATCH --output=logs/ablation_sampler_%A_%a.out
#SBATCH --error=logs/ablation_sampler_%A_%a.err
#SBATCH --array=0-4%2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:l40:1      # exclusive whole GPU — Slurm holds the job in PD until one is free, so it never shares/contends VRAM with another job (replaces mps:l40:N)
#SBATCH --mem=16G
#SBATCH --time=18:00:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 18432      # teacher (frozen) + student + grads, batch 64
# No setup_mps: this job owns the GPU exclusively (--gres=gpu), so MPS is unneeded.

STUDENT="${STUDENT:-mobilenetv3_large}"
TEACHER="${TEACHER:-efficientnet_b4}"
SAMP="${SAMP:-off}"
FOLD="${SLURM_ARRAY_TASK_ID:-0}"

# Map SAMP -> sampler overrides + run-dir suffix (keeps each arm isolated on disk).
case "${SAMP}" in
  off) SAMP_OVERRIDES="data.use_weighted_sampler=false"; SUFFIX="__samp_off" ;;
  3)   SAMP_OVERRIDES="data.use_weighted_sampler=true data.undersample_ratio=3";  SUFFIX="__ratio3" ;;
  5)   SAMP_OVERRIDES="data.use_weighted_sampler=true data.undersample_ratio=5";  SUFFIX="__ratio5" ;;
  10)  SAMP_OVERRIDES="data.use_weighted_sampler=true data.undersample_ratio=10"; SUFFIX="__ratio10" ;;
  *)   echo "[job] ERROR: unknown SAMP='${SAMP}' (use off|3|5|10)"; exit 1 ;;
esac

echo "[job] Ablation sampler | student=${STUDENT} teacher=${TEACHER} SAMP=${SAMP} (${SUFFIX}) | fold ${FOLD}"
command -v nvidia-smi >/dev/null && nvidia-smi || true

# ${SAMP_OVERRIDES} is intentionally unquoted: it must split into separate Hydra args.
python scripts/train_student.py \
    "student=${STUDENT}" "teacher=${TEACHER}" "training=distillation" \
    "data.fold=${FOLD}" ${SAMP_OVERRIDES} "run_suffix=${SUFFIX}"

echo "[job] DONE"
