#!/usr/bin/env bash
# ============================================================================
# Fitzpatrick17k fairness summary figure — three panels, one experiment. CPU-only.
#
# Joins existing artifacts; it never re-runs inference and never trains:
#   reports/external/fitzpatrick17k/headline/bootstrap_ci.json
#       -> per-run AUC-ROC + per-run tone-group gaps (needs SUBGROUP=tone_group)
#   reports/external/fitzpatrick17k/<variant>/bootstrap_ci.json + one predictions.csv
#       -> per-group AUPRC and each group's prevalence, for the prevalence-trap panel
#
# WHY THREE PANELS: Muc 4.8 of the thesis reports ONE experiment but had grown
# three subsections and four tables.
#   (a) gap strips, one dot per run  -> the disadvantaged group is the MIDDLE one
#   (b) AUPRC vs its own baseline    -> raw AUPRC is not comparable across groups
#   (c) per-run AUC-ROC with CIs     -> out of domain the teachers pull ahead
#
# PANEL (b) IS THE POINT OF THE VARIANT. AUPRC's random baseline IS the subgroup's
# prevalence, and in `with_non_neoplastic` prevalence differs by tone group
# (dark ~9.6% vs light ~15.4%). Reading raw AUPRC there suggests a large gap that
# normalising by the baseline removes. Prevalence is READ from a predictions.csv,
# never passed in, so the figure cannot drift from the split.
#
# Args are KEY=VALUE OR env vars:
#   HEADLINE_CI  main-variant bootstrap report
#                (default reports/external/fitzpatrick17k/headline/bootstrap_ci.json)
#   VARIANT_DIR  variant used for panel (b)
#                (default reports/external/fitzpatrick17k/with_non_neoplastic)
#   GAP_METRIC   metric for panel (a)          (default auc_roc)
#   OUT          output png; an .svg is written alongside
#                                              (default reports/fitzpatrick_summary.png)
#   DPI          raster resolution             (default 200)
#
# Usage:
#   bash run/plot_fitzpatrick_summary.sh
#   bash run/plot_fitzpatrick_summary.sh GAP_METRIC=auprc OUT=reports/fitz_auprc.png
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "plot_fitzpatrick_summary"
activate_venv
# Pure matplotlib over existing JSON/CSV — stays runnable while a job owns the GPU.
export CUDA_VISIBLE_DEVICES=""
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
export MPLCONFIGDIR="${TMPDIR}/mpl"
mkdir -p "${TMPDIR}" "${MPLCONFIGDIR}"

HEADLINE_CI="${HEADLINE_CI:-reports/external/fitzpatrick17k/headline/bootstrap_ci.json}"
VARIANT_DIR="${VARIANT_DIR:-reports/external/fitzpatrick17k/with_non_neoplastic}"
GAP_METRIC="${GAP_METRIC:-auc_roc}"
OUT="${OUT:-reports/fitzpatrick_summary.png}"
DPI="${DPI:-200}"

if [ ! -s "${HEADLINE_CI}" ]; then
    echo "[run] ERROR: missing or empty input: ${HEADLINE_CI}" >&2
    echo "[run]   it comes from run/bootstrap_ci.sh SUBGROUP=tone_group" >&2
    exit 2
fi
if [ ! -s "${VARIANT_DIR}/bootstrap_ci.json" ]; then
    echo "[run] ERROR: missing or empty input: ${VARIANT_DIR}/bootstrap_ci.json" >&2
    exit 2
fi

echo "[run] Fitzpatrick summary | headline=${HEADLINE_CI} variant=${VARIANT_DIR} gap=${GAP_METRIC} -> ${OUT}"
python scripts/plot_fitzpatrick_summary.py \
    --headline-ci "${HEADLINE_CI}" \
    --variant-dir "${VARIANT_DIR}" \
    --gap-metric "${GAP_METRIC}" \
    --out "${OUT}" \
    --dpi "${DPI}"

echo "[run] DONE"
