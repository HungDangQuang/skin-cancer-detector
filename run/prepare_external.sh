#!/usr/bin/env bash
# ============================================================================
# Prepare the EXTERNAL, EVALUATION-ONLY datasets — HAM10000 (cross-domain) and
# Fitzpatrick17k (fairness). Neither is ever trained on.
#
# Separate from run/prepare_data.sh on purpose: that one owns the training path
# (ISIC 2024 + PAD + 5-fold splits). This one writes a single held-out test CSV
# per dataset (plus sensitivity variants) and runs the leakage guard.
#
# Prereqs:
#   HAM10000        data/raw/ham10000/HAM10000_metadata.csv + extracted image zips
#   Fitzpatrick17k  data/raw/fitzpatrick17k/fitzpatrick17k.csv   (URLs; images are
#                   fetched by this script — they are NOT in the release)
#
# Usage:
#   bash run/prepare_external.sh DATASET=ham10000
#   bash run/prepare_external.sh DATASET=fitzpatrick17k
#   bash run/prepare_external.sh DATASET=fitzpatrick17k DOWNLOAD_LIMIT=50   # trial first
#   bash run/prepare_external.sh DATASET=both
#
# Args (KEY=VALUE):
#   DATASET         ham10000 | fitzpatrick17k | both   (default both)
#   DOWNLOAD_LIMIT  fetch only N Fitzpatrick URLs      (default 0 = all)
#   MD5_CHECK       strict | warn | off                (default strict)
#   WORKERS         parallel downloads                 (default 8)
#   SKIP_DOWNLOAD   1 = images already fetched         (default 0)
#   SKIP_MD5_OVERLAP 1 = skip the pixel-level leakage layer (faster)
#   CROP_FRACS      Fitzpatrick17k framing variants: comma-separated centre-crop
#                   fractions (e.g. "0.7,0.5"), or "none" to skip them.
#                   Default = the config's crop_variants: block (crop70 + crop50).
#
# Exit 2 from the prepare step = the overlap check found external images inside
# the internal splits. Do NOT evaluate until that is resolved.
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done
start_log "prepare_external"
activate_venv

DATASET="${DATASET:-both}"
DOWNLOAD_LIMIT="${DOWNLOAD_LIMIT:-0}"
MD5_CHECK="${MD5_CHECK:-strict}"
WORKERS="${WORKERS:-8}"
SKIP_DOWNLOAD="${SKIP_DOWNLOAD:-0}"
SKIP_MD5_OVERLAP="${SKIP_MD5_OVERLAP:-0}"
CROP_FRACS="${CROP_FRACS:-}"

# CPU-only work — never touch a GPU here.
export CUDA_VISIBLE_DEVICES=""

OVERLAP_FLAG=""
if [ "${SKIP_MD5_OVERLAP}" = "1" ]; then
    OVERLAP_FLAG="--skip-md5-overlap"
fi

# Empty = let configs/data/fitzpatrick17k.yaml decide (crop70 + crop50).
CROP_FLAG=""
if [ -n "${CROP_FRACS}" ]; then
    CROP_FLAG="--center-crop-fracs ${CROP_FRACS}"
fi

prepare_ham() {
    if [ ! -f data/raw/ham10000/HAM10000_metadata.csv ] && [ ! -f data/raw/ham10000/metadata.csv ]; then
        echo "ERROR: data/raw/ham10000/HAM10000_metadata.csv not found."
        echo "       Download HAM10000 (Harvard Dataverse) and extract the image zips there."
        exit 1
    fi
    echo "[run] Preparing HAM10000 (cross-domain evaluation set)"
    python scripts/prepare_external_data.py --dataset ham10000 ${OVERLAP_FLAG}
}

prepare_fitz() {
    if [ ! -f data/raw/fitzpatrick17k/fitzpatrick17k.csv ]; then
        echo "ERROR: data/raw/fitzpatrick17k/fitzpatrick17k.csv not found."
        echo "       Place the release metadata CSV (md5hash,url,fitzpatrick_scale,...) there."
        exit 1
    fi
    if [ "${SKIP_DOWNLOAD}" != "1" ]; then
        echo "[run] Downloading Fitzpatrick17k images | limit=${DOWNLOAD_LIMIT} md5=${MD5_CHECK}"
        LIMIT_FLAG=""
        if [ "${DOWNLOAD_LIMIT}" != "0" ]; then
            LIMIT_FLAG="--limit ${DOWNLOAD_LIMIT}"
        fi
        python scripts/download_fitzpatrick17k.py \
            --workers "${WORKERS}" --md5-check "${MD5_CHECK}" ${LIMIT_FLAG}
    fi
    echo "[run] Preparing Fitzpatrick17k (fairness evaluation set)"
    # shellcheck disable=SC2086
    python scripts/prepare_external_data.py --dataset fitzpatrick17k ${OVERLAP_FLAG} ${CROP_FLAG}
}

case "${DATASET}" in
    ham10000)       prepare_ham ;;
    fitzpatrick17k) prepare_fitz ;;
    both)           prepare_ham; prepare_fitz ;;
    *) echo "ERROR: DATASET must be ham10000 | fitzpatrick17k | both (got '${DATASET}')"; exit 1 ;;
esac

echo "[run] DONE — check reports/external_overlap_check_*.md before evaluating."
