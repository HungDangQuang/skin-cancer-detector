#!/usr/bin/env bash
# ============================================================================
# Download the raw bytes of the EXTERNAL, EVALUATION-ONLY datasets —
# HAM10000 (cross-domain) and Fitzpatrick17k (fairness). Neither is ever
# trained on. This script only FETCHES; the processing + leakage guard is the
# next step, run/prepare_external.sh.
#
#   HAM10000        Harvard Dataverse, ~2.8 GB, one open host, md5-verified.
#   Fitzpatrick17k  a CSV of ~16.5k third-party atlas URLs. Expect PARTIAL
#                   coverage: the links are a decade old and one host going
#                   offline removes its whole share of the set. The per-host
#                   success rate this prints is a thesis-reportable limitation
#                   of the fairness analysis, not a bug to hide.
#
# Usage:
#   bash run/download_external.sh DATASET=ham10000 RM_ZIP=1
#   bash run/download_external.sh DATASET=fitzpatrick17k SAMPLE=60   # trial first
#   bash run/download_external.sh DATASET=fitzpatrick17k
#   bash run/download_external.sh DATASET=both RM_ZIP=1
#
# Args (KEY=VALUE):
#   DATASET    ham10000 | fitzpatrick17k | both      (default both)
#   RM_ZIP     1 = delete each HAM10000 zip after extracting (default 0)
#   SKIP_IMAGES 1 = HAM10000 metadata only           (default 0)
#   SAMPLE     Fitzpatrick trial over N random rows  (default 0 = full run)
#   WORKERS    parallel Fitzpatrick downloads        (default 8)
#   MD5_CHECK  strict | warn | off                   (default strict)
#
# Long job — launch it under tmux:  tmux new -s dl 'bash run/download_external.sh ...'
# Next step: bash run/prepare_external.sh DATASET=<same>
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done
start_log "download_external"
activate_venv

DATASET="${DATASET:-both}"
RM_ZIP="${RM_ZIP:-0}"
SKIP_IMAGES="${SKIP_IMAGES:-0}"
SAMPLE="${SAMPLE:-0}"
WORKERS="${WORKERS:-8}"
MD5_CHECK="${MD5_CHECK:-strict}"

# Network + unzip work only — never occupy a GPU with it.
export CUDA_VISIBLE_DEVICES=""
# Keep every temp byte inside the project (shared boxes have run / to 100%).
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
mkdir -p "${TMPDIR}"

# Space guard: HAM10000 needs ~2.8 GB of zips + ~2.8 GB extracted (less with
# RM_ZIP=1, which frees each zip as soon as it is unpacked).
AVAIL_GB="$(df -Pk . | awk 'NR==2 {print int($4/1024/1024)}')"
echo "[run] free space here: ${AVAIL_GB} GB | TMPDIR=${TMPDIR}"
if [ "${DATASET}" != "fitzpatrick17k" ] && [ "${AVAIL_GB}" -lt 8 ]; then
    echo "ERROR: HAM10000 needs ~6 GB free (${AVAIL_GB} GB available). Free space or use RM_ZIP=1."
    exit 1
fi

download_ham() {
    echo "[run] Downloading HAM10000 (cross-domain evaluation set) from Harvard Dataverse"
    HAM_FLAGS=""
    [ "${RM_ZIP}" = "1" ] && HAM_FLAGS="${HAM_FLAGS} --rm-zip"
    [ "${SKIP_IMAGES}" = "1" ] && HAM_FLAGS="${HAM_FLAGS} --skip-images"
    # shellcheck disable=SC2086
    python scripts/download_ham10000.py ${HAM_FLAGS}
}

download_fitz() {
    echo "[run] Downloading Fitzpatrick17k (fairness evaluation set) | workers=${WORKERS} md5=${MD5_CHECK} sample=${SAMPLE}"
    FITZ_FLAGS="--fetch-metadata --workers ${WORKERS} --md5-check ${MD5_CHECK}"
    [ "${SAMPLE}" != "0" ] && FITZ_FLAGS="${FITZ_FLAGS} --sample ${SAMPLE}"
    # exit 2 = the md5 probe aborted (the release's hash column is not the image
    # md5). Surface it as guidance instead of a bare non-zero exit.
    # shellcheck disable=SC2086
    if ! python scripts/download_fitzpatrick17k.py ${FITZ_FLAGS}; then
        echo "[run] Fitzpatrick17k download stopped — see the message above."
        echo "      If it was the md5 probe, re-run with MD5_CHECK=warn and RECORD"
        echo "      that choice in the fairness section of the report."
        exit 2
    fi
}

case "${DATASET}" in
    ham10000)       download_ham ;;
    fitzpatrick17k) download_fitz ;;
    both)           download_ham; download_fitz ;;
    *) echo "ERROR: DATASET must be ham10000 | fitzpatrick17k | both (got '${DATASET}')"; exit 1 ;;
esac

echo "[run] DONE — next: bash run/prepare_external.sh DATASET=${DATASET}"
