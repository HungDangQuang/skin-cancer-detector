#!/usr/bin/env bash
# ============================================================================
# Pareto figure — in-domain AUPRC vs measured Pixel 6a latency. CPU-only.
#
# Joins two existing artifacts; it never re-runs inference and never trains:
#   reports/bootstrap_ci_ablation.json  -> AUPRC point + 95% paired-bootstrap CI
#   reports/ondevice_latency.csv        -> one row per ARCHITECTURE (not per variant)
#
# WHY ONE x PER ARCHITECTURE: the four KD variants of an architecture share a graph
# and a parameter count and differ only in weights. BENCHMARK_RESULTS.md §5.4 shows
# the 24-149% latency spread between variants tracks TEMPERATURE (~14% per °C), not
# the weights — so a per-variant x would plot thermal noise. Each architecture is a
# vertical cluster: a better teacher moves a point UP for free, a heavier
# architecture moves it RIGHT.
#
# DEFAULT x IS `sustained_ms`, NOT the best case. Thermal throttling costs 45-49% on
# this handset (§5.3) and a screening app doing repeated inference sees the sustained
# figure. Use LATENCY_COL=best_ms only for an explicit best-case comparison.
#
# Args are KEY=VALUE OR env vars:
#   CI_JSON      bootstrap report   (default reports/bootstrap_ci_ablation.json)
#   LATENCY_CSV  per-arch latency   (default reports/ondevice_latency.csv)
#   LATENCY_COL  sustained_ms | best_ms | cold_ms   (default sustained_ms)
#   OUT          output png; an .svg is written alongside
#                                   (default reports/pareto_auprc_vs_latency.png)
#   DPI          raster resolution  (default 200)
#
# Usage:
#   bash run/plot_pareto.sh
#   bash run/plot_pareto.sh LATENCY_COL=best_ms OUT=reports/pareto_best.png
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "plot_pareto"
activate_venv
# Pure matplotlib over existing JSON/CSV — stays runnable while a job owns the GPU.
export CUDA_VISIBLE_DEVICES=""
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
export MPLCONFIGDIR="${TMPDIR}/mpl"
mkdir -p "${TMPDIR}" "${MPLCONFIGDIR}"

CI_JSON="${CI_JSON:-reports/bootstrap_ci_ablation.json}"
LATENCY_CSV="${LATENCY_CSV:-reports/ondevice_latency.csv}"
LATENCY_COL="${LATENCY_COL:-sustained_ms}"
OUT="${OUT:-reports/pareto_auprc_vs_latency.png}"
DPI="${DPI:-200}"

for f in "${CI_JSON}" "${LATENCY_CSV}"; do
    if [ ! -s "${f}" ]; then
        echo "[run] ERROR: missing or empty input: ${f}" >&2
        echo "[run]   ${CI_JSON} comes from run/bootstrap_ci.sh" >&2
        echo "[run]   ${LATENCY_CSV} is transcribed from reports/BENCHMARK_RESULTS.md" >&2
        exit 2
    fi
done

echo "[run] Pareto | ci=${CI_JSON} latency=${LATENCY_CSV} col=${LATENCY_COL} -> ${OUT}"
python scripts/plot_pareto.py \
    --ci-json "${CI_JSON}" \
    --latency-csv "${LATENCY_CSV}" \
    --latency-col "${LATENCY_COL}" \
    --out "${OUT}" \
    --dpi "${DPI}"

echo "[run] DONE"
