#!/usr/bin/env bash
# ============================================================================
# Build the mobile-evaluation bundle (one zip of images + manifest) that BOTH
# the server arm and the phone arm score. CPU-only, no GPU needed.
#
# Contract: docs/MOBILE_EVAL_PIPELINE.md. Manifest row order = scoring order =
# each dataset's test_split.csv in FILE order. No shuffling, no balancing.
#
# Prereqs: data/processed/ images present, and for the external sets
#   bash run/prepare_external.sh DATASET=<ds>
#
# Args (KEY=VALUE):
#   DATASETS  space-separated NAME[:VARIANT] list
#             (default "indomain ham10000 fitzpatrick17k")
#   OUTDIR    bundle directory        (default data/mobile_eval_bundle)
#   GATE_N    pre-normalised .bin rows for the parity gate   (default 100)
#   ZIP       1 = also write <OUTDIR>.zip                    (default 1)
#   LIMIT     TESTING ONLY: first N rows per dataset         (default unset)
#
# Usage:
#   bash run/make_mobile_eval_bundle.sh
#   bash run/make_mobile_eval_bundle.sh DATASETS="indomain ham10000" GATE_N=100
#   bash run/make_mobile_eval_bundle.sh LIMIT=50 ZIP=0      # quick shape check
#
# Output: $OUTDIR/{manifest.csv,meta.json,images/,l1_gate/,SHA256SUMS} + .zip
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "make_mobile_eval_bundle"
activate_venv
export CUDA_VISIBLE_DEVICES=""          # pure file copying + PIL, no GPU

DATASETS="${DATASETS:-indomain ham10000 fitzpatrick17k}"
OUTDIR="${OUTDIR:-data/mobile_eval_bundle}"
GATE_N="${GATE_N:-100}"
ZIP="${ZIP:-1}"

ARGS=(--output-dir "${OUTDIR}" --gate-n "${GATE_N}")
for ds in ${DATASETS}; do ARGS+=(--dataset "${ds}"); done
if [ "${ZIP}" = "1" ]; then ARGS+=(--zip); fi
if [ -n "${LIMIT:-}" ]; then ARGS+=(--limit-per-dataset "${LIMIT}"); fi

echo "[run] Bundle: datasets='${DATASETS}' -> ${OUTDIR} (gate=${GATE_N}, zip=${ZIP})"
python scripts/make_mobile_eval_bundle.py "${ARGS[@]}"
