#!/usr/bin/env bash
# ============================================================================
# Add DDI (Diverse Dermatology Images) to the TRAIN side of the existing splits.
#
# Processes data/raw/DDI/images/ -> data/processed/ddi/{benign,malignant}/*.jpg,
# then APPENDS those rows to every fold_*/train_split.csv.
#
# test_split.csv and every val_split.csv are left untouched, on purpose: that
# keeps the already-trained experiments/runs_newsplit_light arm valid as a paired
# control, so "does DDI help?" costs 15 fold-run instead of 30.
#
# This does NOT re-run scripts/prepare_data.py — that is forbidden on this box
# (the ISIC HDF5 and PAD raw are gone, and prepare's dst.exists() fast-path
# unlinks processed images permanently). See scripts/prepare_ddi.py's docstring.
#
# Prereq — the release zip unpacked so that this path exists:
#   data/raw/DDI/images/ddi_metadata.csv   (+ 000001.png ... 000656.png)
#
# Args (KEY=VALUE):
#   DRY_RUN   1 = report only, write nothing        (default 0)
#   FORCE     1 = replace DDI rows already present  (default 0)
#   RAW_DIR   DDI raw dir                           (default data/raw/DDI)
#
# Usage:
#   bash run/prepare_ddi.sh DRY_RUN=1
#   bash run/prepare_ddi.sh
#
# Output:
#   data/processed/ddi/{benign,malignant}/*.jpg
#   data/processed/ddi/ddi_tone_map.csv      <- skin_tone side-car (NOT in splits)
#   reports/_ddi_backup/<ts>/fold_*_train_split.csv   <- pre-append backups
# ============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=run/common.sh
source "${SCRIPT_DIR}/common.sh"

for arg in "$@"; do export "${arg?}"; done

DRY_RUN="${DRY_RUN:-0}"
FORCE="${FORCE:-0}"
RAW_DIR="${RAW_DIR:-data/raw/DDI}"

start_log "prepare_ddi"
activate_venv

# CPU-only: stays runnable while a training process owns the card.
export CUDA_VISIBLE_DEVICES=""
# The server root / has hit 100% before — keep PIL's temp files in-project.
export TMPDIR="${TMPDIR:-$(pwd)/.tmp}"
mkdir -p "${TMPDIR}"

ARGS=(--raw-dir "${RAW_DIR}")
[ "${DRY_RUN}" = "1" ] && ARGS+=(--dry-run)
[ "${FORCE}" = "1" ] && ARGS+=(--force)

echo "[run] Adding DDI to the TRAIN side | raw=${RAW_DIR} dry_run=${DRY_RUN} force=${FORCE}"
python scripts/prepare_ddi.py "${ARGS[@]}"

echo "[run] DONE"
