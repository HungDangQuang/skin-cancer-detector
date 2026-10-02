#!/usr/bin/env bash
# ============================================================================
# Generate the Android app's per-model config.json (docs/ANDROID_APP_SPEC.md §3.2)
# from a trained run. CPU only. Guide: docs/APP_CONFIG_GUIDE.md.
#
# Thresholds are chosen on VALIDATION only (phone point on the PAD rows, global
# point on all rows) and their sensitivity/specificity are reported on TEST.
# Two modes (docs/ANDROID_APP_SPEC.md §3.4a): leave PHONE_PREVALENCE, GLOBAL_PREVALENCE and
# PI_TARGET all unset for a BINARY config (decision only, no % / risk band / PPV), or set all
# three for a CALIBRATED one — they are decisions, so they have no default.
#
# Usage:
#   bash run/make_app_config.sh \
#     RUN_DIR=experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp \
#     FOLD=4 CKPT_TAG=_auprc PTE=exports/executorch_srcsamp/<model>.pte EXECUTORCH_VERSION=1.5.1 \
#     MODEL_ID=<id> MODEL_VERSION=v1.0.0 DISPLAY_NAME="..." \
#     SKIP_GLOBAL_OP=1 OUT=<dir>/config.json                        # binary
#     (calibrated: add PHONE_PREVALENCE=<p> GLOBAL_PREVALENCE=<p> PI_TARGET=<p>)
#
# Args (KEY=VALUE):
#   RUN_DIR, FOLD, PTE, EXECUTORCH_VERSION, MODEL_ID, MODEL_VERSION, DISPLAY_NAME, OUT  [required]
#   PHONE_PREVALENCE, GLOBAL_PREVALENCE, PI_TARGET   all or none  (none = binary mode)
#   SKIP_GLOBAL_OP     1 = leave out the global_youden point      (default 0)
#   CKPT_TAG           "" or _auprc                              (default _auprc)
#   PHONE_SENS_TARGET  sensitivity target of the phone point     (default 0.90)
#   DEFAULT_OP         default operating point id                (default: the phone point)
#   BENCHMARK_JSON     params/GFLOPs/size source  (default reports/benchmark/<student>.json of the run)
#   PI_TRAIN           training prior for the prior shift  (default 1/(1+undersample_ratio); guide §1)
#   BACKEND            xnnpack | portable                  (default xnnpack)
#   THRESHOLD_NOTE     provenance appended to the phone point (e.g. a report path)
#   FORCE              1 = overwrite OUT                         (default 0)
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done
start_log "make_app_config"
activate_venv
# CPU only; keep it off a card a training job may be using.
export CUDA_VISIBLE_DEVICES=""

: "${RUN_DIR:?RUN_DIR required}"
: "${FOLD:?FOLD required}"
: "${PTE:?PTE required (the exported .pte this config describes)}"
: "${EXECUTORCH_VERSION:?EXECUTORCH_VERSION required (version of the export venv)}"
: "${MODEL_ID:?MODEL_ID required}"
: "${MODEL_VERSION:?MODEL_VERSION required}"
: "${DISPLAY_NAME:?DISPLAY_NAME required}"
: "${OUT:?OUT required}"
CKPT_TAG="${CKPT_TAG-_auprc}"
PHONE_SENS_TARGET="${PHONE_SENS_TARGET:-0.90}"
DEFAULT_OP="${DEFAULT_OP:-}"
BENCHMARK_JSON="${BENCHMARK_JSON:-}"
PHONE_PREVALENCE="${PHONE_PREVALENCE:-}"
GLOBAL_PREVALENCE="${GLOBAL_PREVALENCE:-}"
PI_TARGET="${PI_TARGET:-}"
SKIP_GLOBAL_OP="${SKIP_GLOBAL_OP:-0}"
PI_TRAIN="${PI_TRAIN:-}"
BACKEND="${BACKEND:-xnnpack}"
THRESHOLD_NOTE="${THRESHOLD_NOTE:-}"
FORCE="${FORCE:-0}"

ARGS=(--run-dir "${RUN_DIR}" --fold "${FOLD}" --ckpt-tag "${CKPT_TAG}" --pte "${PTE}"
      --executorch-version "${EXECUTORCH_VERSION}" --model-id "${MODEL_ID}"
      --model-version "${MODEL_VERSION}" --display-name "${DISPLAY_NAME}"
      --phone-sens-target "${PHONE_SENS_TARGET}" --out "${OUT}"
      --backend "${BACKEND}" --threshold-note "${THRESHOLD_NOTE}")
if [ -n "${DEFAULT_OP}" ]; then ARGS+=(--default-op "${DEFAULT_OP}"); fi
if [ -n "${BENCHMARK_JSON}" ]; then ARGS+=(--benchmark-json "${BENCHMARK_JSON}"); fi
if [ -n "${PHONE_PREVALENCE}" ]; then ARGS+=(--phone-prevalence "${PHONE_PREVALENCE}"); fi
if [ -n "${GLOBAL_PREVALENCE}" ]; then ARGS+=(--global-prevalence "${GLOBAL_PREVALENCE}"); fi
if [ -n "${PI_TARGET}" ]; then ARGS+=(--pi-target "${PI_TARGET}"); fi
if [ "${SKIP_GLOBAL_OP}" = "1" ]; then ARGS+=(--skip-global-op); fi
if [ -n "${PI_TRAIN}" ]; then ARGS+=(--pi-train "${PI_TRAIN}"); fi
if [ "${FORCE}" = "1" ]; then ARGS+=(--force); fi

echo "[run] app config | run=${RUN_DIR} fold=${FOLD} ckpt_tag='${CKPT_TAG}' out=${OUT}"
python scripts/make_app_config.py "${ARGS[@]}"
echo "[run] DONE"
