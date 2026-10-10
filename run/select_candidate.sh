#!/usr/bin/env bash
# ============================================================================
# Apply a candidate round's pre-registered, VALIDATION-ONLY selection rule
# (docs/PREREG_CANDIDATE2_2026-10-02.md §4 + §7.1): pick the pair by mean 5-fold
# AUPRC on the PAD rows of val (tie rule §7.1), then the ship fold by median
# all-val AUPRC. CPU only. Reads ONLY val files.
#
# Commit OUT_DIR before opening any test file of the candidates or running any
# external evaluation (prereg §7.2).
#
# Usage:
#   bash run/select_candidate.sh OUT_DIR=reports/<date>_candidate2_selection \
#     CANDIDATES="P0=experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp \
#                 P1=experiments/runs_newsplit_ddi/kd_convnextv2_base_to_mobilenetv4_conv_medium__srcsamp \
#                 P2=experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_repvit_m1_0__srcsamp"
#
# Args (KEY=VALUE):
#   CANDIDATES   space-separated NAME=RUN_DIR, in pre-registered order  [required]
#   OUT_DIR      where selection.json + selection.md go                 [required]
#   SPLITS_DIR   default data/splits/isic2024
#   CKPT_TAG     "" or _auprc                    (default _auprc, prereg §4.2)
#   TIE          tie margin                      (default 0.005, prereg §7.1)
#   FORCE        1 = overwrite selection.json    (default 0)
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done
start_log "select_candidate"
activate_venv
# CPU only; keep it off a card a training job may be using.
export CUDA_VISIBLE_DEVICES=""

: "${CANDIDATES:?CANDIDATES required (NAME=RUN_DIR ..., in pre-registered order)}"
: "${OUT_DIR:?OUT_DIR required}"
SPLITS_DIR="${SPLITS_DIR:-data/splits/isic2024}"
CKPT_TAG="${CKPT_TAG-_auprc}"
TIE="${TIE:-0.005}"
FORCE="${FORCE:-0}"

ARGS=(--splits-dir "${SPLITS_DIR}" --ckpt-tag "${CKPT_TAG}" --tie "${TIE}" --out-dir "${OUT_DIR}")
for c in ${CANDIDATES}; do ARGS+=(--candidate "${c}"); done
if [ "${FORCE}" = "1" ]; then ARGS+=(--force); fi

echo "[run] select candidate | candidates=${CANDIDATES} out=${OUT_DIR} ckpt_tag='${CKPT_TAG}'"
python scripts/select_candidate.py "${ARGS[@]}"
echo "[run] DONE"
