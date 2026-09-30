#!/usr/bin/env bash
# ============================================================================
# Post-training evaluation of the source-stratified sampler arm (item 2) and its
# best-by-val-AUPRC checkpoint (item 3) — steps S3 + S4 of
# docs/TASK_ITEM2_3_source_sampler_ship_ckpt.md.
#
#   aggregate  fold means for both checkpoints    -> <run>/aggregated{,_auprc}.{json,md}
#   external   HAM10000 (headline) + Fitzpatrick17k (all variants), both checkpoints,
#              each into its OWN out-root         -> ${OUT_PAUC}/, ${OUT_AUPRC}/   (GPU)
#   ci         paired bootstrap CIs, pre-registered sign NEW - CONTROL
#              (pAUC checkpoint on both sides)    -> reports/ci_srcsamp_*.{json,md}
#              + per-run CIs of the AUPRC checkpoint -> reports/ci_srcsamp_auprc_*.{json,md}
#
# The control arm is the same tree without the suffix (trained 2026-09-25, pAUC
# checkpoint only). The CI trees are symlinks under .tmp/ci_srcsamp/ holding just
# the new arm + its control, so no other run of the tree enters a report. The
# explicit PAIR carries the pre-registered sign; bootstrap_ci.py's automatic
# suffix pairing (section 2b) is also printed, with the OPPOSITE sign
# (control - new) — quote the explicit-pair section.
#
# Usage (after the arm has trained; GPU work, so one job at a time):
#   bash run/srcsamp_eval.sh GPU=0
#   bash run/srcsamp_eval.sh STAGES="ci"                 # re-run one stage
#
# Args (KEY=VALUE):
#   TREE       training tree                (default experiments/runs_newsplit_ddi)
#   SUFFIX     new-arm run_suffix           (default __srcsamp)
#   OUT_PAUC   external out-root, pAUC ckpt (default reports/external_newsplit_srcsamp)
#   OUT_AUPRC  external out-root, AUPRC ckpt(default reports/external_newsplit_srcsamp_auprc)
#   CONTROL_EXT external out-root holding the control arm's results
#                                           (default reports/external_newsplit_ddi)
#   STAGES     subset of "aggregate external ci" (default all three)
#   GPU        passed to evaluate_external.sh (default auto)
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done
start_log "srcsamp_eval"
activate_venv
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
mkdir -p "${TMPDIR}"

TREE="${TREE:-experiments/runs_newsplit_ddi}"
SUFFIX="${SUFFIX:-__srcsamp}"
OUT_PAUC="${OUT_PAUC:-reports/external_newsplit_srcsamp}"
OUT_AUPRC="${OUT_AUPRC:-reports/external_newsplit_srcsamp_auprc}"
CONTROL_EXT="${CONTROL_EXT:-reports/external_newsplit_ddi}"
STAGES="${STAGES:-aggregate external ci}"
GPU="${GPU:-auto}"
FITZ_VARIANTS="headline crop70 crop50 with_non_neoplastic"
BASES="kd_efficientnetv2_m_to_mobilenetv4_conv_medium baseline_mobilenetv4_conv_medium"

has_stage() { case " ${STAGES} " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

# New-arm runs with all five folds scored; the KD arm is required, the baseline
# arm (S2, optional in the brief) is used only if it finished.
NEW_RUNS=""
for b in ${BASES}; do
    r="${TREE}/${b}${SUFFIX}"
    # `|| true`: with no match ls fails, and under pipefail that would kill the script.
    n=$( (ls "${r}"/fold_*/test_metrics.json 2>/dev/null || true) | wc -l)
    if [ "${n}" -eq 5 ]; then
        NEW_RUNS="${NEW_RUNS} ${b}"
    elif [ "${b#kd_}" != "${b}" ]; then
        echo "[run] ERROR: ${r} has ${n}/5 folds with test_metrics.json" >&2
        exit 1
    else
        echo "[run] WARN: ${r} has ${n}/5 folds — left out"
    fi
done
echo "[run] srcsamp eval | tree=${TREE} suffix=${SUFFIX} runs:${NEW_RUNS} | stages: ${STAGES}"

if has_stage aggregate; then
    for b in ${NEW_RUNS}; do
        bash run/aggregate.sh RUN_DIR="${TREE}/${b}${SUFFIX}"
        bash run/aggregate.sh RUN_DIR="${TREE}/${b}${SUFFIX}" METRICS_NAME=test_metrics_auprc.json
    done
fi

if has_stage external; then
    RUNS=""
    for b in ${NEW_RUNS}; do RUNS="${RUNS} ${TREE}/${b}${SUFFIX}"; done
    for ds_var in "ham10000 headline" "fitzpatrick17k all"; do
        set -- ${ds_var}
        bash run/evaluate_external.sh DATASET="$1" VARIANTS="$2" RUNS="${RUNS}" GPU="${GPU}" \
            OUT_ROOT="${OUT_PAUC}"
        bash run/evaluate_external.sh DATASET="$1" VARIANTS="$2" RUNS="${RUNS}" GPU="${GPU}" \
            OUT_ROOT="${OUT_AUPRC}" CKPT_NAME=best_model_auprc.pth \
            VAL_PRED_NAME=val_predictions_auprc.csv
    done
fi

if has_stage ci; then
    CI_ROOT="${PROJECT_DIR}/.tmp/ci_srcsamp"
    PAIRS=""
    for b in ${NEW_RUNS}; do PAIRS="${PAIRS:+${PAIRS};}${b}${SUFFIX}:${b}"; done

    # $1 = tree name, $2 = source dir of the NEW arm's runs, $3 = source dir of the control
    link_tree() {
        local tree="${CI_ROOT}/$1"
        rm -rf "${tree}"
        mkdir -p "${tree}"
        for b in ${NEW_RUNS}; do
            for pair in "$2/${b}${SUFFIX}:${b}${SUFFIX}" "$3/${b}:${b}"; do
                local src="${pair%%:*}"
                case "${src}" in /*) ;; *) src="${PROJECT_DIR}/${src}" ;; esac
                if [ ! -d "${src}" ]; then
                    echo "[run] ERROR: missing ${src}" >&2
                    return 1
                fi
                ln -sfn "${src}" "${tree}/${pair##*:}"
            done
        done
        echo "${tree}"
    }

    # ---- pAUC checkpoint: new vs control, paired, pre-registered sign -------- #
    t=$(link_tree indomain "${TREE}" "${TREE}")
    bash run/bootstrap_ci.sh RESULTS_DIR="${t}" PAIR="${PAIRS}" SUBGROUP=source \
        OUT_JSON=reports/ci_srcsamp_indomain.json OUT_MD=reports/ci_srcsamp_indomain.md
    t=$(link_tree ham10000_headline "${OUT_PAUC}/ham10000/headline" "${CONTROL_EXT}/ham10000/headline")
    bash run/bootstrap_ci.sh RESULTS_DIR="${t}" PAIR="${PAIRS}" \
        OUT_JSON=reports/ci_srcsamp_ham10000_headline.json OUT_MD=reports/ci_srcsamp_ham10000_headline.md
    for v in ${FITZ_VARIANTS}; do
        t=$(link_tree "fitzpatrick17k_${v}" "${OUT_PAUC}/fitzpatrick17k/${v}" "${CONTROL_EXT}/fitzpatrick17k/${v}")
        bash run/bootstrap_ci.sh RESULTS_DIR="${t}" PAIR="${PAIRS}" SUBGROUP=tone_group \
            OUT_JSON="reports/ci_srcsamp_fitzpatrick17k_${v}.json" \
            OUT_MD="reports/ci_srcsamp_fitzpatrick17k_${v}.md"
    done

    # ---- AUPRC checkpoint: per-run CIs only (the control has no such file) --- #
    t=$(link_tree auprc_indomain "${TREE}" "${TREE}")
    bash run/bootstrap_ci.sh RESULTS_DIR="${t}" PRED_NAME=predictions_auprc.csv SUBGROUP=source \
        OUT_JSON=reports/ci_srcsamp_auprc_indomain.json OUT_MD=reports/ci_srcsamp_auprc_indomain.md
    bash run/bootstrap_ci.sh RESULTS_DIR="${OUT_AUPRC}/ham10000/headline" \
        OUT_JSON=reports/ci_srcsamp_auprc_ham10000_headline.json \
        OUT_MD=reports/ci_srcsamp_auprc_ham10000_headline.md
    for v in ${FITZ_VARIANTS}; do
        bash run/bootstrap_ci.sh RESULTS_DIR="${OUT_AUPRC}/fitzpatrick17k/${v}" SUBGROUP=tone_group \
            OUT_JSON="reports/ci_srcsamp_auprc_fitzpatrick17k_${v}.json" \
            OUT_MD="reports/ci_srcsamp_auprc_fitzpatrick17k_${v}.md"
    done
fi

echo "[run] DONE"
