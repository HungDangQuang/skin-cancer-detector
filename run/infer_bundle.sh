#!/usr/bin/env bash
# ============================================================================
# Score the mobile-eval bundle on the HOST, one image at a time on CPU, emitting
# the same sample_id,logit,error CSV the phone emits.
#
# Contract: docs/MOBILE_EVAL_PIPELINE.md §4 — CPU + batch 1 is mandatory, not a
# performance choice. run/evaluate_external.sh defaults to CUDA + batch 64, and
# comparing that against a phone number mixes four divergence sources into one.
#
# Picks the venv by arm: CKPT -> training venv; PTE -> isolated export venv.
#
# Args (KEY=VALUE):
#   BUNDLE    bundle dir                    (default data/mobile_eval_bundle)
#   OUT       output CSV                    [required]
#   MODEL     model name (with CKPT)
#   CKPT      checkpoint .pth               (PyTorch eager arm)
#   PTE       .pte file                     (ExecuTorch arm)
#   GATE      1 = read l1_gate/inputs/*.bin instead of JPEGs   (default 0)
#   THREADS   CPU threads for the PyTorch arm            (default 8)
#             NOT all cores: batch-1 inference measured 723 ms/img with 64 threads
#             vs 29 ms with 8 and 43 ms with 1 on a 64-core box.
#   START/END manifest row range, for sharding           (default whole file)
#   EXPORT_VENV_DIR  override export venv   (default ./.venv-export)
#
# Usage:
#   bash run/infer_bundle.sh MODEL=mobilenetv4_conv_medium \
#        CKPT=experiments/runs_newsplit_ddi/kd_.../fold_4/checkpoints/best_model.pth \
#        OUT=reports/mobile_eval/server_logits.csv
#   bash run/infer_bundle.sh PTE=exports/executorch_v2/m.pte \
#        OUT=reports/mobile_eval/host_executorch_logits.csv
#   bash run/infer_bundle.sh PTE=exports/executorch_v2/m.pte GATE=1 \
#        OUT=reports/mobile_eval/gate_host.csv
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "infer_bundle"
export CUDA_VISIBLE_DEVICES=""          # spec §4: host arm runs on CPU

# Cap the math-library thread pools in the ENVIRONMENT, not just via
# torch.set_num_threads(): OpenMP/MKL size their pools at first use and a
# 64-core host otherwise spawns 64 threads PER PROCESS. With 6 shards that is
# ~384 threads fighting over 64 cores, which measured ~50x slower than one
# 8-thread process. See docs/GOTCHAS.md and docs/MOBILE_EVAL_PIPELINE.md §4.1.
export OMP_NUM_THREADS="${THREADS:-8}"
export MKL_NUM_THREADS="${THREADS:-8}"
export OPENBLAS_NUM_THREADS="${THREADS:-8}"

BUNDLE="${BUNDLE:-data/mobile_eval_bundle}"
: "${OUT:?OUT env var required (output CSV path)}"
GATE="${GATE:-0}"

ARGS=(--bundle "${BUNDLE}" --out "${OUT}" --threads "${THREADS:-8}")
if [ "${GATE}" = "1" ]; then ARGS+=(--from-gate-bins); fi
if [ -n "${START:-}" ]; then ARGS+=(--start "${START}"); fi
if [ -n "${END:-}" ]; then ARGS+=(--end "${END}"); fi

if [ -n "${CKPT:-}" ] && [ -n "${PTE:-}" ]; then
    echo "[run] ERROR: pass CKPT or PTE, not both." >&2; exit 2
elif [ -n "${CKPT:-}" ]; then
    : "${MODEL:?MODEL env var required together with CKPT}"
    ARGS+=(--model-name "${MODEL}" --checkpoint "${CKPT}")
    activate_venv                       # training venv: torch + timm + src/
    echo "[run] arm=pytorch-eager model=${MODEL}"
elif [ -n "${PTE:-}" ]; then
    ARGS+=(--pte "${PTE}")
    EXPORT_VENV="${EXPORT_VENV_DIR:-${PROJECT_DIR}/.venv-export}"
    if [ ! -x "${EXPORT_VENV}/bin/python" ]; then
        echo "[run] ERROR: export venv missing at ${EXPORT_VENV}." >&2
        echo "[run] Run: bash run/setup_export_env.sh" >&2
        exit 2
    fi
    # shellcheck disable=SC1091
    source "${EXPORT_VENV}/bin/activate"
    echo "[run] arm=executorch pte=${PTE}"
else
    echo "[run] ERROR: pass CKPT (+MODEL) or PTE." >&2; exit 2
fi

python scripts/infer_bundle.py "${ARGS[@]}"
