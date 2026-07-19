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
#   # Carry metadata columns into the split CSVs (direction D subgroup calibration
#   # or direction A privileged teacher — comma-separated, NO spaces, no iddx_*/mel_*):
#   bash run/prepare_data.sh META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
# Output: data/processed/... + data/splits/isic2024/fold_{0..4}/ + test_split.csv
#         Splits are seed-deterministic, so adding META_COLS only ADDS columns
#         (rows/order identical) — existing checkpoints stay valid.
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
# Accept KEY=VALUE positional args (e.g. META_COLS=...), same style as the others.
for arg in "$@"; do export "${arg?}"; done
start_log "prepare_data"
activate_venv

if [ ! -f data/raw/isic2024/train-metadata.csv ]; then
    echo "ERROR: data/raw/isic2024/train-metadata.csv not found."
    echo "       Download ISIC 2024 first — see run/README.md § Data."
    exit 1
fi

# Optional metadata columns to keep in the split CSVs (comma-separated, no spaces).
META_COLS="${META_COLS:-}"
echo "[run] Preprocessing datasets and generating CV splits | meta_cols='${META_COLS}'"
if [ -n "${META_COLS}" ]; then
    python scripts/prepare_data.py --metadata-cols "${META_COLS}"
else
    python scripts/prepare_data.py
fi

echo "[run] DONE"
