#!/usr/bin/env bash
# ============================================================================
# Evaluate trained checkpoints on an EXTERNAL, EVALUATION-ONLY dataset —
# HAM10000 (cross-domain) or Fitzpatrick17k (fairness).
#
# The decision threshold is FROZEN from each run's own internal validation fold;
# nothing is fitted on the external set (see scripts/evaluate_external.py).
# Results land under reports/external/ — training run-dirs are never written to.
#
# Prereqs:
#   bash run/download_external.sh DATASET=<ds>     # raw bytes
#   bash run/prepare_external.sh  DATASET=<ds>     # splits + leakage guard
#   trained runs with fold_*/checkpoints/best_model.pth AND val_predictions.csv
#
# Usage:
#   bash run/evaluate_external.sh DATASET=ham10000
#   bash run/evaluate_external.sh DATASET=fitzpatrick17k VARIANTS=all GPU=0
#   bash run/evaluate_external.sh DATASET=ham10000 \
#        RUNS="experiments/runs/kd_efficientnetv2_m_to_fastvit_sa12 experiments/runs/baseline_fastvit_sa12"
#
# Args (KEY=VALUE):
#   DATASET   ham10000 | fitzpatrick17k              [required]
#   RUNS      space-separated run-dirs (default: every run-dir under
#             experiments/runs/ that has fold_*/checkpoints/best_model.pth)
#   FOLDS     comma-separated fold ids               (default 0,1,2,3,4)
#   VARIANTS  split variants, or 'all'               (default headline)
#   BATCH     eval batch size                        (default 64)
#   WORKERS   dataloader workers                     (default 8)
#   GPU       physical GPU id / auto / cpu           (default auto)
#
# Output per run × variant:
#   reports/external/<ds>/<variant>/<run_tag>/fold_N/{test_metrics.json,predictions.csv,
#                                                     subgroup_metrics.json}
#   reports/external/<ds>/<variant>/<run_tag>/aggregated.{json,md}
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done
start_log "evaluate_external"
activate_venv
select_gpu

: "${DATASET:?DATASET env var required (ham10000 | fitzpatrick17k)}"
FOLDS="${FOLDS:-0,1,2,3,4}"
VARIANTS="${VARIANTS:-headline}"
BATCH="${BATCH:-64}"
WORKERS="${WORKERS:-8}"
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
mkdir -p "${TMPDIR}"

case "${DATASET}" in
    ham10000|fitzpatrick17k) ;;
    *) echo "ERROR: DATASET must be ham10000 | fitzpatrick17k (got '${DATASET}')"; exit 1 ;;
esac

if [ ! -f "data/splits/${DATASET}/test_split.csv" ]; then
    echo "ERROR: data/splits/${DATASET}/test_split.csv not found."
    echo "       Run first: bash run/download_external.sh DATASET=${DATASET}"
    echo "              and bash run/prepare_external.sh  DATASET=${DATASET}"
    exit 1
fi

# The leakage guard is what makes these numbers meaningful; refuse to report a
# cross-domain result whose overlap check never ran or came back dirty.
OVERLAP_REPORT="reports/external_overlap_check_${DATASET}.md"
if [ ! -f "${OVERLAP_REPORT}" ]; then
    echo "ERROR: ${OVERLAP_REPORT} missing — the external-vs-internal overlap check has"
    echo "       not run. Re-run: bash run/prepare_external.sh DATASET=${DATASET}"
    exit 1
fi
if grep -q "overlapping image(s) found — STOP" "${OVERLAP_REPORT}"; then
    echo "ERROR: ${OVERLAP_REPORT} reports overlap with the internal splits."
    echo "       Resolve it before evaluating — the numbers would be inflated."
    exit 1
fi

# Default run set: everything trained, discovered by the presence of a fold-0
# checkpoint (teachers live one level deeper than students).
if [ -z "${RUNS:-}" ]; then
    RUNS="$(find experiments/runs -mindepth 2 -maxdepth 3 -type d -name 'fold_*' \
              -exec test -f '{}/checkpoints/best_model.pth' ';' -print \
            | sed 's|/fold_[0-9]*$||' | sort -u | tr '\n' ' ')"
fi
if [ -z "${RUNS// /}" ]; then
    echo "ERROR: no run-dir with fold_*/checkpoints/best_model.pth found under experiments/runs/."
    echo "       Pass RUNS=\"<dir> <dir>\" explicitly, or rsync the checkpoints in."
    exit 1
fi

RUN_FLAGS=""
N_RUNS=0
for r in ${RUNS}; do
    # Fail before the sweep starts, not 40 minutes in: an explicitly passed
    # run-dir with no checkpoint is a typo, not a run to skip quietly.
    if ! ls "${r}"/fold_*/checkpoints/best_model.pth >/dev/null 2>&1; then
        echo "ERROR: no fold_*/checkpoints/best_model.pth under '${r}'."
        echo "       Checkpoints are not pulled to the Mac by default — rsync them to this box."
        exit 1
    fi
    RUN_FLAGS="${RUN_FLAGS} --run-dir ${r}"
    N_RUNS=$((N_RUNS + 1))
done

# GPU=cpu must reach the Python side too — CUDA_VISIBLE_DEVICES="" alone only
# hides the device, it doesn't tell the script which device to ask for.
DEVICE_FLAG=""
if [ "${GPU:-auto}" = "cpu" ]; then
    DEVICE_FLAG="--device cpu"
fi

echo "[run] External eval | dataset=${DATASET} variants=${VARIANTS} folds=${FOLDS} runs=${N_RUNS}"
for r in ${RUNS}; do echo "        ${r}"; done

# shellcheck disable=SC2086
python scripts/evaluate_external.py \
    --dataset "${DATASET}" \
    --folds "${FOLDS}" \
    --variants "${VARIANTS}" \
    --batch-size "${BATCH}" \
    --num-workers "${WORKERS}" \
    ${DEVICE_FLAG} ${RUN_FLAGS}

echo "[run] DONE — results under reports/external/${DATASET}/"
