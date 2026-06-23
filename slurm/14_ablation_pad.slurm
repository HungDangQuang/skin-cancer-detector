#!/bin/bash
# ============================================================================
# Ablation B — PAD-UFES-20 mixing (data-strategy proof).
# Trains the student with vs without PAD in the TRAIN+VAL data, on the IDENTICAL
# held-out combined test, to prove (or refute) that adding PAD smartphone images
# improves performance — especially on the PAD (smartphone) portion of the test.
#
# WHY BASELINE (no KD) BY DEFAULT: a KD teacher trained on ISIC+PAD would leak
# PAD knowledge into the "ISIC-only" arm via soft labels, contaminating the
# comparison. Baseline (focal loss, no teacher) isolates the single variable =
# whether PAD is in the student's training data. (KD is ablated separately.)
# If you DO run KD here, train a matched ISIC-only teacher first or the result
# is confounded — see docs/SLURM.md.
#
# The held-out TEST is left fully combined (ISIC+PAD) for BOTH arms; its PAD
# portion is never trained on by either arm. Per-domain numbers come from the
# `source` column in predictions.csv (analyze with the per-domain breakdown).
#
# ARM selects training data + a distinct run-dir suffix:
#   ARM=isic_only -> data.train_sources=[isic2024]   (PAD removed from train+val)
#   ARM=isic_pad  -> all sources (PAD kept)           (the current strategy)
#
# Submit both arms (each kicks off 5 folds, <=2 concurrent):
#   bash slurm/submit.sh slurm/14_ablation_pad.slurm ARM=isic_only
#   bash slurm/submit.sh slurm/14_ablation_pad.slurm ARM=isic_pad
#
# Output: experiments/runs/baseline_<student>__train_<arm>/fold_${TASK}/
#           ├── test_metrics.json   (combined test; incl. auprc + sens_at_*spec)
#           └── predictions.csv     (y_true,y_prob,y_pred,source  <- per-domain)
# Aggregate each arm then compare ISIC-only vs ISIC+PAD (focus: PAD-source rows):
#   bash slurm/submit.sh slurm/22_aggregate_folds.slurm \
#       RUN_DIR=experiments/runs/baseline_mobilenetv3_large__train_isic_only
# ============================================================================
#SBATCH --job-name=ablation_pad
#SBATCH --output=logs/ablation_pad_%A_%a.out
#SBATCH --error=logs/ablation_pad_%A_%a.err
#SBATCH --array=0-4%2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:l40:1      # exclusive whole GPU — Slurm holds the job in PD until one is free, so it never shares/contends VRAM with another job (replaces mps:l40:N)
#SBATCH --mem=16G
#SBATCH --time=18:00:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env
acquire_gpu 12288      # baseline student only (no teacher), batch 64
# No setup_mps: this job owns the GPU exclusively (--gres=gpu), so MPS is unneeded.

STUDENT="${STUDENT:-mobilenetv3_large}"
TRAINING="${TRAINING:-baseline}"
ARM="${ARM:-isic_pad}"
FOLD="${SLURM_ARRAY_TASK_ID:-0}"

# Map ARM -> train-source override + run-dir suffix (keeps arms isolated on disk).
case "${ARM}" in
  isic_only) ARM_OVERRIDES="data.train_sources=[isic2024]"; SUFFIX="__train_isic_only" ;;
  isic_pad)  ARM_OVERRIDES="data.train_sources=null";        SUFFIX="__train_isic_pad" ;;
  *)         echo "[job] ERROR: unknown ARM='${ARM}' (use isic_only|isic_pad)"; exit 1 ;;
esac

echo "[job] Ablation PAD | student=${STUDENT} training=${TRAINING} ARM=${ARM} (${SUFFIX}) | fold ${FOLD}"
command -v nvidia-smi >/dev/null && nvidia-smi || true

# ${ARM_OVERRIDES} is intentionally unquoted so it stays a single Hydra arg here.
python scripts/train_student.py \
    "student=${STUDENT}" "training=${TRAINING}" \
    "data.fold=${FOLD}" "${ARM_OVERRIDES}" "run_suffix=${SUFFIX}"

echo "[job] DONE"
