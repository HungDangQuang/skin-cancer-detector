#!/usr/bin/env bash
# ============================================================================
# Preprocess ISIC 2024 (+ optional PAD-UFES-20) and generate 5-fold CV splits.
# Non-Slurm analogue of slurm/10_prepare_data.slurm — CPU-only, no GPU needed.
#
# Prereq: raw data under data/raw/ (see run/README.md § Data). At minimum:
#   data/raw/isic2024/train-image.hdf5
#   data/raw/isic2024/train-metadata.csv
# Optional extra malignants:
#   data/raw/pad_ufes_20/{images/,metadata.csv}   (stage with scripts/setup_pad_ufes_20.sh)
#
# Usage:  bash run/prepare_data.sh
# Output: data/processed/... + data/splits/isic2024/fold_{0..4}/ + test_split.csv
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
start_log "prepare_data"
activate_venv

if [ ! -f data/raw/isic2024/train-metadata.csv ]; then
    echo "ERROR: data/raw/isic2024/train-metadata.csv not found."
    echo "       Download ISIC 2024 first — see run/README.md § Data."
    exit 1
fi

echo "[run] Preprocessing datasets and generating CV splits"
python scripts/prepare_data.py

echo "[run] DONE"
