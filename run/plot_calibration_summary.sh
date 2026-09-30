#!/usr/bin/env bash
# ============================================================================
# Probability-calibration summary figure — three panels, one post-hoc pass. CPU-only.
#
# Joins existing calibration artifacts; it never re-runs inference and never trains:
#   experiments/runs/**/calibration_metrics.json              -> panels (a),(b),(c)
#   experiments/runs/**/calibration_anatom_site_general.json  -> panel (b) subgroup
#   reports/external/<ds>/<variant>/**/calibration_metrics.json -> panel (a)
#
# WHY THREE PANELS: Muc 4.9 of the thesis reports ONE post-hoc analysis (19 runs
# re-scored on 3 domains) but had grown four subsections and three tables.
#   (a) ECE raw -> after prior-shift, per domain, with the log-odds constant
#       -> the constant's SIZE explains all three outcomes at once
#   (b) all rows vs the PAD clinical subgroup -> a global constant breaks a subgroup
#   (c) teacher ECE vs its students' ECE -> KD transfers the calibration profile
#
# PANEL (a) IS THE POINT. Prior-shift adds logit(pi_target)-logit(pi_train) to every
# log-odds. In-domain that constant is -3.94 and ECE drops ~32x; on HAM10000 it is
# -0.08 (pi 15.6% ~ the sampler's 16.67%) and nothing moves; on Fitzpatrick17k it is
# +1.61, the wrong direction, and ECE doubles. Reading "calibration does not help out
# of domain" off the middle row is a misreading of arithmetic as failure.
#
# Both prevalences, and hence the constant, are DERIVED from the artifacts
# (`pi_train` + per-fold `pi_target`), never passed in, so the figure cannot drift
# away from the splits. The script exits non-zero if the three domains do not cover
# the same number of runs.
#
# NOTE: teacher runs nest one level deeper (`experiments/runs/teacher/<name>/`), so
# the script globs recursively. A non-recursive glob finds 16 of the 19 runs.
#
# Args are KEY=VALUE OR env vars:
#   INDOMAIN_DIR  in-domain run root      (default experiments/runs)
#   HAM_DIR       HAM10000 variant dir    (default reports/external/ham10000/headline)
#   FITZ_DIR      Fitzpatrick variant dir
#                            (default reports/external/fitzpatrick17k/headline)
#   OUT           output png; an .svg is written alongside
#                                         (default reports/calibration_summary.png)
#   DPI           raster resolution       (default 200)
#
# Usage:
#   bash run/plot_calibration_summary.sh
#   bash run/plot_calibration_summary.sh OUT=reports/calib.png DPI=300
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "plot_calibration_summary"
activate_venv
# Pure matplotlib over existing JSON — stays runnable while a job owns the GPU.
export CUDA_VISIBLE_DEVICES=""
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
export MPLCONFIGDIR="${TMPDIR}/mpl"
mkdir -p "${TMPDIR}" "${MPLCONFIGDIR}"

INDOMAIN_DIR="${INDOMAIN_DIR:-experiments/runs}"
HAM_DIR="${HAM_DIR:-reports/external/ham10000/headline}"
FITZ_DIR="${FITZ_DIR:-reports/external/fitzpatrick17k/headline}"
OUT="${OUT:-reports/calibration_summary.png}"
DPI="${DPI:-200}"

for d in "${INDOMAIN_DIR}" "${HAM_DIR}" "${FITZ_DIR}"; do
    if [ ! -d "${d}" ]; then
        echo "[run] ERROR: missing input directory: ${d}" >&2
        echo "[run]   calibration files come from scripts/compute_calibration.py" >&2
        exit 2
    fi
done

echo "[run] calibration summary | in-domain=${INDOMAIN_DIR} ham=${HAM_DIR} fitz=${FITZ_DIR} -> ${OUT}"
python scripts/plot_calibration_summary.py \
    --indomain-dir "${INDOMAIN_DIR}" \
    --ham-dir "${HAM_DIR}" \
    --fitz-dir "${FITZ_DIR}" \
    --out "${OUT}" \
    --dpi "${DPI}"

echo "[run] DONE"
