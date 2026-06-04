#!/bin/bash
# ============================================================================
# Step 1 (FULL) — preprocess ISIC 2024 + PAD-UFES-20 and generate 5-fold splits.
# Prereq:  raw data downloaded to data/raw/isic2024/ (and optionally pad_ufes_20).
# Submit:  bash slurm/submit.sh slurm/10_prepare_data.slurm
# Output:  data/processed/isic2024/{benign,malignant}/, excluded_images.csv
#          (dropped corrupt/small/blank/duplicate), data/splits/isic2024/fold_{0..4}/
#          + test_split.csv.  Cleaning + augmentation spec: docs/PREPROCESSING.md
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

echo "[job] Preprocessing real datasets and generating CV splits"
python scripts/prepare_data.py

echo "[job] DONE"
