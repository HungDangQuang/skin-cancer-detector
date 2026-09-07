#!/usr/bin/env bash
# ============================================================================
# run/export_all_students.sh — export EVERY mobile student to ExecuTorch (.pte)
# in one launch, with the parity gate applied to each one. CPU-only.
#
# This is a thin driver over three existing scripts; it adds no new logic beyond
# the loop, the run-tagged output name and the pass/fail summary. Per student it
# runs, in the order the parity check requires:
#
#   1. run/make_benchmark_set.sh MODEL=<m> CKPT=<c>   -> data/benchmark_set/ref_<m>.csv
#   2. run/export_executorch.sh  MODEL=<m> CKPT=<c>   -> exports/executorch/<m>__<tag>.pte
#   3. run/check_pte_parity.sh   MODEL=<m> PTE=<pte>  -> reports/mobile_benchmark/parity_<m>__<tag>.json
#
# The SAME checkpoint goes into steps 1 and 2 by construction — that pairing is
# the trap `docs/GOTCHAS.md` warns about (a mismatched CKPT fails parity for a
# reason that has nothing to do with the lowering), and driving all three from
# one PAIRS entry is the point of this script.
#
# Output names carry a run tag (`<model>__<teacher>_fold<N>.pte`) so exporting a
# second checkpoint of the same architecture never clobbers an earlier .pte.
# Set TAGGED=0 for the bare `exports/executorch/<model>.pte` convention instead.
#
# Uses the ISOLATED export venv (./.venv-export) for steps 2-3 and the training
# venv (./.venv-linux) for step 1 — each child script activates its own, so this
# driver deliberately activates neither.
# One-time setup first:  bash run/setup_env.sh && bash run/setup_export_env.sh
#
# Args are KEY=VALUE OR env vars:
#   PAIRS      whitespace-separated "MODEL:RUN_DIR:FOLD" triples. RUN_DIR is
#              relative to experiments/runs/. Default = the four mobile students
#              at their best-AUPRC KD run and median-behaving fold (see below).
#   N          benchmark-set size                    (default 100)
#   BENCH_DIR  benchmark set / ref logits dir        (default data/benchmark_set)
#   PTE_DIR    .pte output dir                       (default exports/executorch)
#   PARITY_DIR parity JSON dir                       (default reports/mobile_benchmark)
#   BACKEND    xnnpack | none                        (default xnnpack)
#   FALLBACK   1 = retry a failed xnnpack export with BACKEND=none (default 1)
#   TAGGED     1 = <model>__<teacher>_fold<N>.pte, 0 = <model>.pte   (default 1)
#   SKIP_EXISTING 1 = don't re-export a .pte that already exists     (default 1)
#   TOL        parity tolerance, max |dlogit|        (default 1e-3)
#   DRY        1 = print the plan and exit, run nothing              (default 0)
#
# Usage:
#   bash run/export_all_students.sh DRY=1                  # show the plan
#   bash run/export_all_students.sh                        # export all four
#   bash run/export_all_students.sh PAIRS="fastvit_sa12:kd_maxvit_base_to_fastvit_sa12:4"
#   bash run/export_all_students.sh BACKEND=none FALLBACK=0
#
# Exit codes: 0 = every student exported AND passed parity, 1 = at least one
# student failed (the summary table says which), 2 = setup problem.
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "export_all_students"
# CPU-only, like every other export/benchmark job: stays runnable while a
# training process owns the GPU. No activate_venv — the children pick their own.
export CUDA_VISIBLE_DEVICES=""
# The server's / has hit 100% before; keep scratch inside the project.
export TMPDIR="${TMPDIR:-${PROJECT_DIR}/.tmp}"
mkdir -p "${TMPDIR}"

# Default selection, decided 2026-08-24: per student, the KD run with the best
# 5-fold mean AUPRC (the clinical headline metric at ~0.39% prevalence), at the
# fold closest to that run's own 5-fold mean on AUPRC + pAUC — the
# "median-behaving fold, never the best one" rule from docs/ANDROID_APP_SPEC.md §2.
PAIRS_DEFAULT="
mobilenetv4_conv_medium:kd_convnextv2_base_to_mobilenetv4_conv_medium:0
fastvit_sa12:kd_maxvit_base_to_fastvit_sa12:4
efficientformerv2_s2:kd_convnextv2_base_to_efficientformerv2_s2:0
repvit_m1_0:kd_maxvit_base_to_repvit_m1_0:1
"
PAIRS="${PAIRS:-${PAIRS_DEFAULT}}"
N="${N:-100}"
# Defaulted with ${VAR-…} (unset-only), then guarded with ${VAR:?…}: an empty
# `BENCH_DIR=` typed as a KEY=VALUE arg would otherwise build absolute paths like
# /ref_<model>.csv — i.e. writes OUTSIDE the project folder on a shared box.
BENCH_DIR="${BENCH_DIR-data/benchmark_set}"
PTE_DIR="${PTE_DIR-exports/executorch}"
PARITY_DIR="${PARITY_DIR-reports/mobile_benchmark}"
: "${BENCH_DIR:?BENCH_DIR must not be empty}"
: "${PTE_DIR:?PTE_DIR must not be empty}"
: "${PARITY_DIR:?PARITY_DIR must not be empty}"
BACKEND="${BACKEND:-xnnpack}"
FALLBACK="${FALLBACK:-1}"
TAGGED="${TAGGED:-1}"
SKIP_EXISTING="${SKIP_EXISTING:-1}"
TOL="${TOL:-1e-3}"
DRY="${DRY:-0}"

# ---------------------------------------------------------------------------
# Derive the run tag: kd_<teacher>_to_<student> -> "<teacher>_fold<N>",
# baseline_<student> -> "nokd_fold<N>". Used only for output file names.
run_tag() {
    local run="$1" fold="$2" teacher
    case "${run}" in
        kd_*_to_*) teacher="${run#kd_}"; teacher="${teacher%%_to_*}" ;;
        baseline_*) teacher="nokd" ;;
        *) teacher="${run}" ;;
    esac
    echo "${teacher}_fold${fold}"
}

# ---------------------------------------------------------------------------
# Plan: resolve every pair up front so a typo or a missing checkpoint is caught
# before the first (slow) export instead of halfway through.
declare -a P_MODEL P_CKPT P_PTE P_PARITY P_TAG
n_pairs=0
setup_error=0
echo ""
echo "=== plan ==="
printf "%-24s %-46s %-6s %s\n" "MODEL" "RUN_DIR" "FOLD" "-> .pte"
for pair in ${PAIRS}; do
    model="${pair%%:*}"
    rest="${pair#*:}"
    run="${rest%%:*}"
    fold="${rest##*:}"
    if [ "${model}" = "${pair}" ] || [ -z "${run}" ] || [ -z "${fold}" ]; then
        echo "[run] ERROR: malformed PAIRS entry '${pair}' (want MODEL:RUN_DIR:FOLD)" >&2
        setup_error=1
        continue
    fi
    ckpt="experiments/runs/${run}/fold_${fold}/checkpoints/best_model.pth"
    tag="$(run_tag "${run}" "${fold}")"
    if [ "${TAGGED}" = "1" ]; then
        pte="${PTE_DIR}/${model}__${tag}.pte"
        parity="${PARITY_DIR}/parity_${model}__${tag}.json"
    else
        pte="${PTE_DIR}/${model}.pte"
        parity="${PARITY_DIR}/parity_${model}.json"
    fi
    if [ ! -s "${ckpt}" ]; then
        echo "[run] ERROR: checkpoint not found or empty: ${ckpt}" >&2
        setup_error=1
        continue
    fi
    P_MODEL+=("${model}"); P_CKPT+=("${ckpt}"); P_PTE+=("${pte}")
    P_PARITY+=("${parity}"); P_TAG+=("${tag}")
    n_pairs=$((n_pairs + 1))
    printf "%-24s %-46s %-6s %s\n" "${model}" "${run}" "${fold}" "${pte}"
done

if [ "${setup_error}" != "0" ]; then
    echo "[run] ABORT: fix the entries above before launching (nothing was written)." >&2
    exit 2
fi
if [ "${n_pairs}" = "0" ]; then
    echo "[run] ERROR: PAIRS resolved to nothing." >&2
    exit 2
fi
echo "backend=${BACKEND} fallback=${FALLBACK} bench_set=${BENCH_DIR} (N=${N}) tol=${TOL}"
if [ "${DRY}" = "1" ]; then
    echo "[run] DRY=1 — plan only, nothing executed."
    exit 0
fi

mkdir -p "${PTE_DIR}" "${PARITY_DIR}"

# ---------------------------------------------------------------------------
declare -a S_EXPORT S_PARITY S_BACKEND
rc=0
for i in $(seq 0 $((n_pairs - 1))); do
    model="${P_MODEL[$i]}"; ckpt="${P_CKPT[$i]}"
    pte="${P_PTE[$i]}"; parity="${P_PARITY[$i]}"
    # Statuses are accumulated in scalars and pushed to the summary arrays ONCE
    # at the end of the iteration, so the three arrays can never drift out of
    # alignment no matter which branch a student takes.
    st_export="?"; st_backend="-"; st_parity="-"
    echo ""
    echo "############################################################"
    echo "# [$((i + 1))/${n_pairs}] ${model}  (${P_TAG[$i]})"
    echo "############################################################"

    # --- 1. reference logits from THIS checkpoint (also rebuilds the fixed
    #        benchmark set; the sampling is seeded from cfg.seed, so repeated
    #        runs select the same images and stay comparable across models).
    #        Any existing ref_<model>.csv belongs to a different checkpoint —
    #        keep it instead of silently dropping it.
    if [ -s "${BENCH_DIR}/ref_${model}.csv" ]; then
        keep_dir="${BENCH_DIR}/_replaced/$(date '+%Y%m%d_%H%M%S')"
        mkdir -p "${keep_dir}"
        cp -p "${BENCH_DIR}/ref_${model}.csv" "${keep_dir}/ref_${model}.csv"
        echo "[run] kept previous reference logits -> ${keep_dir}/ref_${model}.csv"
    fi
    if bash run/make_benchmark_set.sh N="${N}" OUTDIR="${BENCH_DIR}" \
            MODEL="${model}" CKPT="${ckpt}"; then

        # --- 2. export
        if [ -s "${pte}" ] && [ "${SKIP_EXISTING}" = "1" ]; then
            echo "[run] .pte already exists, skipping export (SKIP_EXISTING=1): ${pte}"
            st_export="SKIPPED"; st_backend="?"
        elif bash run/export_executorch.sh MODEL="${model}" CKPT="${ckpt}" \
                BACKEND="${BACKEND}" OUT="${pte}"; then
            st_export="OK"; st_backend="${BACKEND}"
        elif [ "${FALLBACK}" = "1" ] && [ "${BACKEND}" = "xnnpack" ] \
                && bash run/export_executorch.sh MODEL="${model}" CKPT="${ckpt}" \
                       BACKEND=none OUT="${pte}"; then
            echo "[run] xnnpack export failed for ${model} — fell back to BACKEND=none"
            st_export="OK(fb)"; st_backend="none"
        else
            echo "[run] FAILED: export ${model}" >&2
            st_export="FAIL"
        fi

        # --- 3. parity gate (PC PyTorch vs .pte, same 100 inputs)
        if [ "${st_export}" != "FAIL" ]; then
            if bash run/check_pte_parity.sh MODEL="${model}" PTE="${pte}" \
                    BENCH_DIR="${BENCH_DIR}" TOL="${TOL}" OUT="${parity}"; then
                st_parity="PASS"
            elif [ "${FALLBACK}" = "1" ] && [ "${st_backend}" = "xnnpack" ]; then
                # A .pte can lower "successfully" and still compute garbage:
                # measured 2026-08-24, XNNPACK mis-lowered efficientformerv2_s2
                # to logits of ~-2.2e10 against a PyTorch -3.15. Parity is the
                # only thing that catches that, so it must drive the fallback
                # too — not just an export that errors out.
                echo "[run] PARITY FAILED on xnnpack for ${model} — re-exporting with BACKEND=none"
                if bash run/export_executorch.sh MODEL="${model}" CKPT="${ckpt}" \
                            BACKEND=none OUT="${pte}" \
                        && bash run/check_pte_parity.sh MODEL="${model}" PTE="${pte}" \
                            BENCH_DIR="${BENCH_DIR}" TOL="${TOL}" OUT="${parity}"; then
                    st_export="OK(fb)"; st_backend="none"; st_parity="PASS"
                else
                    echo "[run] PARITY FAILED for ${model} on BOTH backends — do NOT report on-device numbers" >&2
                    st_backend="none"; st_parity="FAIL"
                fi
            else
                echo "[run] PARITY FAILED for ${model} — do NOT report on-device numbers" >&2
                st_parity="FAIL"
            fi
        fi
    else
        echo "[run] FAILED: reference logits for ${model}" >&2
        st_export="REF-FAIL"
    fi

    if [ "${st_export}" = "FAIL" ] || [ "${st_export}" = "REF-FAIL" ] \
            || [ "${st_parity}" = "FAIL" ]; then
        rc=1
    fi
    S_EXPORT+=("${st_export}"); S_BACKEND+=("${st_backend}"); S_PARITY+=("${st_parity}")
done

# ---------------------------------------------------------------------------
echo ""
echo "=== summary ==="
printf "%-24s %-10s %-9s %-8s %s\n" "MODEL" "EXPORT" "BACKEND" "PARITY" ".pte"
for i in $(seq 0 $((n_pairs - 1))); do
    size="-"
    # NB: `[ -s x ] && size=…` would abort the whole script under `set -e` on
    # the very first missing .pte — the failing list is the last command here.
    if [ -s "${P_PTE[$i]}" ]; then
        size="$(du -h "${P_PTE[$i]}" | cut -f1)"
    fi
    printf "%-24s %-10s %-9s %-8s %s (%s)\n" \
        "${P_MODEL[$i]}" "${S_EXPORT[$i]:-?}" "${S_BACKEND[$i]:-?}" \
        "${S_PARITY[$i]:-?}" "${P_PTE[$i]}" "${size}"
done
echo ""
if [ "${rc}" = "0" ]; then
    echo "[run] DONE — all ${n_pairs} students exported and parity-checked."
else
    echo "[run] DONE WITH FAILURES — see the summary above." >&2
fi
exit "${rc}"
