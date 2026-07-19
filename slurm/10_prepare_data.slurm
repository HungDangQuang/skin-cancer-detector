#!/bin/bash
# ============================================================================
# Step 1 (FULL) — preprocess ISIC 2024 + PAD-UFES-20 and generate 5-fold splits.
# Prereq:  raw data downloaded to data/raw/isic2024/ (and optionally pad_ufes_20).
# Submit:  bash slurm/submit.sh slurm/10_prepare_data.slurm
#   # Carry metadata columns into the split CSVs (direction D subgroup calibration
#   # or direction A privileged teacher — comma-separated, NO spaces, no iddx_*/mel_*):
#   bash slurm/submit.sh slurm/10_prepare_data.slurm \
#       META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
# Output:  data/processed/isic2024/{benign,malignant}/, excluded_images.csv
#          (dropped corrupt/small/blank/duplicate), data/splits/isic2024/fold_{0..4}/
#          + test_split.csv.  Cleaning + augmentation spec: docs/PREPROCESSING.md
#          Splits are seed-deterministic, so adding META_COLS only ADDS columns
#          (rows/order identical) — existing checkpoints stay valid.
# ============================================================================
#SBATCH --job-name=prepare_data
#SBATCH --output=logs/prepare_data_%j.out
#SBATCH --error=logs/prepare_data_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=04:00:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env

# Optional metadata columns to keep in the split CSVs (comma-separated, no spaces).
# Empty (default) reproduces the original 6-column schema exactly.
META_COLS="${META_COLS:-}"
echo "[job] Preprocessing real datasets and generating CV splits | meta_cols='${META_COLS}'"
if [ -n "${META_COLS}" ]; then
    python scripts/prepare_data.py --metadata-cols "${META_COLS}"
else
    python scripts/prepare_data.py
fi

echo "[job] DONE"
