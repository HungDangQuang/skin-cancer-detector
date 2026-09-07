#!/usr/bin/env bash
# ============================================================================
# Attach ISIC metadata columns to existing split CSVs + prediction CSVs.
# CPU-only, no inference, no re-training — this is the cheap path to direction D
# (subgroup calibration) on checkpoints that were already trained image-only.
#
# It replaces "re-run prepare with data.metadata_cols=[...] then re-evaluate",
# which would need train-image.hdf5 AND data/raw/pad_ufes_20/ — without the PAD
# raw dir prepare_data.py drops every PAD row and writes DIFFERENT splits than
# the ones every finished run was trained/tested on. Here only columns are
# added, so fold membership is provably unchanged.
#
# Requires: data/raw/isic2024/train-metadata.csv on this machine (246 MB; the
# only source of these columns). Images / HDF5 are NOT needed.
#
# Args are KEY=VALUE OR env vars:
#   COLS        comma-separated ISIC metadata columns
#                                       (default anatom_site_general,sex)
#   STAGE       splits | predictions | both            (default both)
#   META_CSV    raw ISIC metadata CSV   (default data/raw/isic2024/train-metadata.csv)
#   SPLITS_DIR  split tree              (default data/splits/isic2024)
#   RUNS_DIR    run-dir tree            (default experiments/runs)
#   BACKUP_DIR  copies of every file touched
#                                       (default reports/_metadata_backup/<ts>)
#   DRY_RUN     1 = report only, write nothing         (default 0)
#
# Usage:
#   bash run/attach_metadata.sh DRY_RUN=1              # preview first
#   bash run/attach_metadata.sh
#   bash run/attach_metadata.sh STAGE=splits COLS=anatom_site_general,sex,age_approx
#
# Then, per run-dir:
#   python scripts/compute_calibration.py --run-dir <run> --subgroup anatom_site_general
#
# Writes are additive, atomic and idempotent; every file touched is copied to
# BACKUP_DIR first. A run-dir whose predictions.csv fails the row-count / label /
# source alignment guards is SKIPPED and the script exits non-zero.
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "attach_metadata"
activate_venv
# Pure stdlib csv over existing files — stays runnable while a training job owns
# the GPU.
export CUDA_VISIBLE_DEVICES=""
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
mkdir -p "${TMPDIR}"

COLS="${COLS:-anatom_site_general,sex}"
STAGE="${STAGE:-both}"
META_CSV="${META_CSV:-data/raw/isic2024/train-metadata.csv}"
SPLITS_DIR="${SPLITS_DIR:-data/splits/isic2024}"
RUNS_DIR="${RUNS_DIR:-experiments/runs}"
DRY_RUN="${DRY_RUN:-0}"

if [ ! -f "${META_CSV}" ]; then
    echo "[run] ERROR: METADATA CSV not found: ${META_CSV}" >&2
    echo "[run]   copy data/raw/isic2024/train-metadata.csv onto this box first." >&2
    exit 2
fi
if [ ! -d "${SPLITS_DIR}" ]; then
    echo "[run] ERROR: SPLITS_DIR not found: ${SPLITS_DIR}" >&2
    exit 2
fi

ARGS=(--cols "${COLS}" --stage "${STAGE}" --meta-csv "${META_CSV}"
      --splits-dir "${SPLITS_DIR}" --runs-dir "${RUNS_DIR}")
if [ -n "${BACKUP_DIR:-}" ]; then
    ARGS+=(--backup-dir "${BACKUP_DIR}")
fi
if [ "${DRY_RUN}" != "0" ]; then
    ARGS+=(--dry-run)
fi

echo "[run] attach metadata | cols=${COLS} stage=${STAGE} runs=${RUNS_DIR} dry_run=${DRY_RUN}"
python scripts/attach_metadata.py "${ARGS[@]}"

echo "[run] DONE"
