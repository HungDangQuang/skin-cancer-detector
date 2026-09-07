#!/usr/bin/env bash
# ============================================================================
# Bootstrap confidence intervals over an evaluation-results tree. CPU-only.
#
# Answers what "mean ± std over 5 folds" cannot: the sampling error of the TEST
# SET. Produces (1) a CI per run per metric, (2) a PAIRED CI on the KD delta —
# a far stronger claim than "KD won 12/12" — (3) a PAIRED CI on each ABLATION
# delta (every `__<suffix>` fork vs the same run without the suffix, signed
# main − ablated), (4) a PAIRED CI on a fairness gap (light AUC − dark AUC
# bootstrapped directly, not two CIs eyeballed), and (5) with SUBGROUP set, the
# ABLATION delta restricted to each subgroup — the cell to quote for PAD.
#
# Section 3 is what covers the data-strategy ablations: the PAD arms
# (baseline_<student>__train_isic_only) and the sampler arms (__samp_off,
# __ratio3, __ratio10). Section 2 cannot pair those — both sides parse to the
# same kind, so the kd-vs-baseline lookup never fires.
#
# Reads only fold_*/predictions.csv, so it never re-runs inference and never
# writes inside experiments/runs/ when pointed at reports/external/.
#
# Args are KEY=VALUE OR env vars:
#   RESULTS_DIR  tree of run-dirs with fold_*/predictions.csv     [required]
#                e.g. reports/external/ham10000/headline | experiments/runs
#   N_BOOT       bootstrap replicates                (default 2000)
#   SEED         RNG seed                            (default 42)
#   ALPHA        1-ALPHA interval                    (default 0.05 -> 95%)
#   SUBGROUP     predictions.csv column for fairness gaps (default: none)
#                e.g. tone_group on Fitzpatrick17k
#   METRICS      comma-separated subset              (default all four)
#   PAIR         "RUN_A:RUN_B" — paired delta between TWO named run-dirs, signed
#                A - B. Semicolon-separate several. Sections 2/3 only pair
#                kd-vs-baseline and suffix-vs-main, so comparing two KD runs to
#                EACH OTHER (e.g. the two Pareto ship candidates) needs this.
#   OUT_JSON     (default ${RESULTS_DIR}/bootstrap_ci.json)
#   OUT_MD       (default ${RESULTS_DIR}/bootstrap_ci.md)
#
# Usage:
#   bash run/bootstrap_ci.sh RESULTS_DIR=reports/external/ham10000/headline
#   bash run/bootstrap_ci.sh RESULTS_DIR=reports/external/fitzpatrick17k/headline \
#        SUBGROUP=tone_group
#   # data-strategy ablations — send output OUTSIDE experiments/runs/ so the cited
#   # experiments/runs/bootstrap_ci.{json,md} from 2026-08-24 is not overwritten.
#   # SUBGROUP=source is REQUIRED for the PAD arms: without it you only get the
#   # whole-test delta, which is inflated (the ISIC-only arm collapses on the 377
#   # PAD rows and those carry ~75% of all positives). Section 5 is the cell to
#   # quote; section 3 is not.
#   bash run/bootstrap_ci.sh RESULTS_DIR=experiments/runs SUBGROUP=source \
#        OUT_JSON=reports/bootstrap_ci_ablation.json \
#        OUT_MD=reports/bootstrap_ci_ablation.md
#   # compare the two ship candidates directly (overlapping per-run intervals do
#   # NOT mean equivalent — only the paired delta settles it):
#   bash run/bootstrap_ci.sh RESULTS_DIR=reports/external/ham10000/headline \
#        PAIR="kd_maxvit_base_to_fastvit_sa12:kd_convnextv2_base_to_mobilenetv4_conv_medium"
#
# NOTE teacher runs must stay nested as teacher/<name> in the tree — flattening
# them makes run discovery skip them silently (same rule as compare_kd_results).
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "bootstrap_ci"
activate_venv
# Pure numpy/sklearn over existing CSVs — stays runnable while a training or
# eval process owns the GPU.
export CUDA_VISIBLE_DEVICES=""
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
mkdir -p "${TMPDIR}"

: "${RESULTS_DIR:?RESULTS_DIR env var required (e.g. reports/external/ham10000/headline)}"
N_BOOT="${N_BOOT:-2000}"
SEED="${SEED:-42}"
ALPHA="${ALPHA:-0.05}"
METRICS="${METRICS:-auc_roc,auprc,pauc_at_tpr80,sens_at_90spec}"
OUT_JSON="${OUT_JSON:-${RESULTS_DIR}/bootstrap_ci.json}"
OUT_MD="${OUT_MD:-${RESULTS_DIR}/bootstrap_ci.md}"

if [ ! -d "${RESULTS_DIR}" ]; then
    echo "[run] ERROR: RESULTS_DIR not found: ${RESULTS_DIR}" >&2
    exit 2
fi

ARGS=(--results-dir "${RESULTS_DIR}" --n-boot "${N_BOOT}" --seed "${SEED}"
      --alpha "${ALPHA}" --metrics "${METRICS}"
      --out-json "${OUT_JSON}" --out-md "${OUT_MD}")
# PAIR holds one or more "A:B" specs separated by ";". Split on ";" only, so a
# run-dir name may contain anything except a semicolon.
if [ -n "${PAIR:-}" ]; then
    _old_ifs="${IFS}"
    IFS=";"
    for _spec in ${PAIR}; do
        [ -n "${_spec}" ] && ARGS+=(--pair "${_spec}")
    done
    IFS="${_old_ifs}"
fi
if [ -n "${SUBGROUP:-}" ]; then
    ARGS+=(--subgroup-col "${SUBGROUP}")
fi

echo "[run] Bootstrap CI | dir=${RESULTS_DIR} B=${N_BOOT} seed=${SEED} subgroup=${SUBGROUP:-none} pair=${PAIR:-none}"
python scripts/bootstrap_ci.py "${ARGS[@]}"

echo "[run] DONE"
