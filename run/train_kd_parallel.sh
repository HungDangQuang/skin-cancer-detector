#!/usr/bin/env bash
# ============================================================================
# Train several KD student runs CONCURRENTLY on ONE GPU, packing as many as the
# VRAM allows WITHOUT OOM. For a single dedicated box (e.g. 24GB 3090).
#
# One unit of work = one `run/train_student.sh STUDENT=<s> TEACHER=<t>` call,
# which trains all 5 folds sequentially in one process (~6-7 GB with a
# convnextv2_base teacher at the FIXED batch=64 — batch is NEVER lowered here).
#
# The launcher is VRAM-gated: it starts a new job only when
#     (running jobs < MAX_JOBS)  AND  (free VRAM >= MIN_FREE_MB)
# then sleeps WARMUP so the new job grabs its memory before the next decision.
# Backfills as jobs finish, never over-committing. Runs already at 5/5 folds are
# skipped, and PARTIAL runs resume — only folds missing test_metrics.json are trained.
#
# NOTE on concurrency (measured 2026-08-13 on the 3090): a single KD training job
# already drives GPU util to ~100% (compute-bound), so extra concurrent jobs do NOT
# finish sooner — they time-slice the same saturated GPU (total wall-clock ~= running
# them one after another) and only add OOM risk. Default MAX_JOBS=2 is a safe cap
# (2x~6.7GB fits 24GB); use MAX_JOBS=1 for strictly-sequential, lowest-risk runs.
#
# Usage (from repo root; run under tmux/nohup for a detach-safe long run):
#   tmux new -s kd
#   bash run/train_kd_parallel.sh                                  # convnextv2_base x 4 students
#   bash run/train_kd_parallel.sh TEACHERS="convnextv2_base maxvit_base"
#   bash run/train_kd_parallel.sh MAX_JOBS=1                       # strictly sequential
#   bash run/train_kd_parallel.sh MAX_JOBS=2 STUDENTS="repvit_m1_0"  # just re-run repvit
#
# Args/env (KEY=VALUE):
#   TEACHERS     space list of teachers to distill from   (default "convnextv2_base")
#   STUDENTS     space list of students                   (default all 4 SOTA)
#   TRAINING     distillation | distillation_rkd          (default distillation)
#   MAX_JOBS     hard cap on concurrent jobs              (default 2; see NOTE above.
#                MAX_JOBS=1 = strictly sequential)
#   MIN_FREE_MB  min free VRAM (MB) required to launch     (default 8000)
#   WARMUP       s to wait after a launch before next      (default 90)
#   POLL         s between VRAM/slot polls                 (default 30)
#   GPU          physical GPU id                           (default 0)
#   AGGREGATE    1 = aggregate + compare after all finish  (default 1)
#
# TIP: check `nvidia-smi --query-gpu=utilization.gpu --format=csv` with ONE job
# running. If it already reads ~100%, more concurrency won't speed things up (only
# raise MAX_JOBS if a single job leaves the GPU clearly under-utilized).
# ============================================================================
set -uo pipefail   # NOT -e: one failed student must not abort the whole batch

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for arg in "$@"; do export "${arg?}"; done

TEACHERS="${TEACHERS:-convnextv2_base}"
STUDENTS="${STUDENTS:-mobilenetv4_conv_medium fastvit_sa12 efficientformerv2_s2 repvit_m1_0}"
TRAINING="${TRAINING:-distillation}"
MAX_JOBS="${MAX_JOBS:-2}"          # hard cap 2 concurrent. Measured 2026-08-13: 3 jobs
                                   # -> GPU util 100% (compute-bound, ~zero speedup) AND
                                   # a 4th got launched on a transient free-VRAM dip then
                                   # OOM'd. 2 jobs (~13GB/24GB) always fit; 3 does not.
MIN_FREE_MB="${MIN_FREE_MB:-8000}"
WARMUP="${WARMUP:-90}"
POLL="${POLL:-30}"
GPU="${GPU:-0}"
AGGREGATE="${AGGREGATE:-1}"
# Reduce allocator fragmentation (helps avoid the "reserved but unallocated" OOM).
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

mkdir -p logs reports/comparison
PIDS=()

free_vram() {   # MB free on our GPU (empty -> 0 so we wait, never over-launch)
    nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i "${GPU}" 2>/dev/null \
        | head -n1 | tr -d ' '
}
running_jobs() {
    local c=0 p
    for p in "${PIDS[@]:-}"; do
        [ -n "${p}" ] && kill -0 "${p}" 2>/dev/null && c=$((c + 1))
    done
    echo "${c}"
}

echo "[kd-par] teachers=[${TEACHERS}] students=[${STUDENTS}]"
echo "[kd-par] MAX_JOBS=${MAX_JOBS} MIN_FREE_MB=${MIN_FREE_MB} WARMUP=${WARMUP}s GPU=${GPU} TRAINING=${TRAINING}"

for T in ${TEACHERS}; do
    for S in ${STUDENTS}; do
        run_dir="experiments/runs/kd_${T}_to_${S}"
        # Per-fold resume: only train folds whose test_metrics.json is missing, so a
        # killed/restarted batch never redoes a completed fold.
        miss=""
        for k in 0 1 2 3 4; do
            [ -f "${run_dir}/fold_${k}/test_metrics.json" ] || miss="${miss} ${k}"
        done
        miss="$(echo ${miss})"   # trim leading/trailing space
        if [ -z "${miss}" ]; then
            echo "[kd-par] SKIP ${T}->${S} (already 5/5)"
            continue
        fi

        # Block until a slot frees AND there is enough headroom to fit one more.
        while :; do
            r=$(running_jobs)
            f=$(free_vram); f=${f:-0}
            if [ "${r}" -lt "${MAX_JOBS}" ] && [ "${f}" -ge "${MIN_FREE_MB}" ]; then
                break
            fi
            echo "[kd-par] wait: running=${r}/${MAX_JOBS} free=${f}MB (need >=${MIN_FREE_MB}) ..."
            sleep "${POLL}"
        done

        log="logs/kd_${T}_to_${S}_$(date +%Y%m%d_%H%M%S).out"
        echo "[kd-par] LAUNCH ${T}->${S} folds=[${miss}]  (running=$(running_jobs), free=$(free_vram)MB)  log=${log}"
        GPU="${GPU}" bash run/train_student.sh \
            STUDENT="${S}" TEACHER="${T}" TRAINING="${TRAINING}" FOLDS="${miss}" >"${log}" 2>&1 &
        PIDS+=("$!")
        sleep "${WARMUP}"   # let the new job allocate before deciding on the next
    done
done

echo "[kd-par] all jobs launched (${#PIDS[@]}); waiting for completion ..."
wait
echo "[kd-par] all training finished."

if [ "${AGGREGATE}" = "1" ]; then
    for T in ${TEACHERS}; do for S in ${STUDENTS}; do
        d="experiments/runs/kd_${T}_to_${S}"
        [ -d "${d}" ] && python scripts/aggregate_folds.py --run-dir "${d}" || true
    done; done
    python scripts/compare_kd_results.py \
        --out-md reports/comparison/kd_comparison.md \
        --out-json reports/comparison/kd_comparison.json || true
    echo "[kd-par] aggregated + compared -> reports/comparison/. rsync experiments/runs + reports back to Mac."
fi
