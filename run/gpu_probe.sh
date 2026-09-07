#!/usr/bin/env bash
# ============================================================================
# run/gpu_probe.sh — sample GPU utilization / VRAM into a CSV while a job runs,
# then print p50/p90/p95/max so you can decide how many jobs fit at once.
#
# READ-ONLY observer. It never pins CUDA_VISIBLE_DEVICES, never launches or
# signals a training job, and never touches another user's processes: the only
# thing it does to a PID is `kill -0` (an existence test) and only for a PID
# owned by the current user. Launch the training job yourself, then point this
# at it.
#
# Why this exists: run/progress.sh shows a single nvidia-smi SNAPSHOT for a
# status display. Deciding MAX_JOBS for run/train_kd_parallel.sh needs the
# distribution over a whole fold — a job can average 45% and still spike to
# 100%, and it is the PEAK VRAM, not the mean, that decides whether a second
# job OOMs.
#
# Usage:
#   # 1) start the training job (tmux window 1), then:
#   bash run/gpu_probe.sh PID=auto
#
#   # explicit PID, sample every 2s, stop when the job exits:
#   bash run/gpu_probe.sh PID=48210 INTERVAL=2
#
#   # fixed 30-minute window, tag it for the summary file:
#   bash run/gpu_probe.sh DURATION=1800 TAG=kd_fastvit_fold0
#
#   # no PID / no DURATION -> samples until Ctrl-C (summary still printed)
#
# Args (KEY=VALUE, or env vars):
#   PID        watch this PID and stop when it exits; "auto" = the newest
#              scripts/train_{teacher,student}.py owned by THIS user (default: none)
#   DURATION   stop after N seconds; 0 = no time limit                (default 0)
#   INTERVAL   seconds between samples                                (default 5)
#   GPU        index to record, or "all"                              (default all)
#              NOTE: this only filters what is RECORDED. It does not pin
#              CUDA_VISIBLE_DEVICES — use GPU= on the training script for that.
#   OUT        CSV path        (default reports/gpu_probe_<TAG>_<timestamp>.csv)
#   TAG        label for the output filename + summary header         (default "")
#
# Output:
#   <OUT>                     ts,elapsed_s,index,util_pct,mem_used_mb,mem_total_mb,temp_c,power_w
#   <OUT without .csv>_summary.txt   per-GPU p50/p90/p95/max + VRAM-fit estimate
#   logs/gpu_probe_<timestamp>.log   full transcript (survives an SSH drop)
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "gpu_probe"

PID="${PID:-}"
DURATION="${DURATION:-0}"
INTERVAL="${INTERVAL:-5}"
GPU="${GPU:-all}"
TAG="${TAG:-}"

if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "ERROR: nvidia-smi not found — nothing to sample. This script is server-only."
    exit 2
fi

# Numeric knobs are validated up front: under `set -u`/`set -e` a stray value
# would otherwise surface as a confusing `[: integer expression expected` in the
# middle of the sampling loop.
case "${INTERVAL}" in ''|*[!0-9]*) echo "ERROR: INTERVAL must be a whole number of seconds (got '${INTERVAL}')"; exit 2 ;; esac
case "${DURATION}" in ''|*[!0-9]*) echo "ERROR: DURATION must be a whole number of seconds, 0 = unlimited (got '${DURATION}')"; exit 2 ;; esac
[ "${INTERVAL}" -ge 1 ] || { echo "ERROR: INTERVAL must be >= 1"; exit 2; }

TS="$(date '+%Y%m%d_%H%M%S')"
_slug="${TAG:+${TAG}_}"
OUT="${OUT:-reports/gpu_probe_${_slug}${TS}.csv}"
SUMMARY="${OUT%.csv}_summary.txt"
mkdir -p "$(dirname "${OUT}")"

# --- resolve PID=auto to our OWN newest training process (never someone else's)
WATCH_PID=""
if [ "${PID}" = "auto" ]; then
    # DataLoader workers are forks of the trainer with a BYTE-IDENTICAL cmdline,
    # so a plain `pgrep -n` picks a WORKER, not the trainer — and PyTorch
    # recycles workers between epochs (persistent_workers=False), which would
    # make the probe stop early thinking the job had finished. Keep only
    # processes whose parent is not itself a match; take the newest of those.
    # `tr` is load-bearing: pgrep emits ONE PID PER LINE, and the `case` test
    # below matches on " <ppid> " — with newlines the space-delimited pattern
    # never matches and every worker slips through.
    _cands="$(pgrep -u "$(id -u)" -f 'scripts/train_(teacher|student)\.py' 2>/dev/null | tr '\n' ' ' || true)"
    for _p in ${_cands}; do
        _pp="$(ps -o ppid= -p "${_p}" 2>/dev/null | tr -d ' ')"
        case " ${_cands} " in *" ${_pp} "*) continue ;; esac
        WATCH_PID="${_p}"
    done
    if [ -z "${WATCH_PID}" ]; then
        echo "ERROR: PID=auto found no scripts/train_{teacher,student}.py owned by $(id -un)."
        echo "       Start the training job first, or pass an explicit PID=<n>."
        exit 2
    fi
    echo "[run] PID=auto resolved to ${WATCH_PID}: $(ps -o args= -p "${WATCH_PID}" 2>/dev/null | cut -c1-110)"
elif [ -n "${PID}" ]; then
    if ! kill -0 "${PID}" 2>/dev/null; then
        echo "ERROR: PID ${PID} is not running (or not visible to $(id -un))."
        exit 2
    fi
    # The server is shared: refuse to watch someone else's process even though
    # `kill -0` only tests existence. Keeps the audit trail unambiguous.
    _owner="$(ps -o user= -p "${PID}" 2>/dev/null | tr -d ' ')"
    if [ -n "${_owner}" ] && [ "${_owner}" != "$(id -un)" ]; then
        echo "ERROR: PID ${PID} belongs to '${_owner}', not $(id -un). Refusing to watch another user's job."
        exit 2
    fi
    WATCH_PID="${PID}"
fi

echo "[run] gpu_probe | tag='${TAG}' | interval=${INTERVAL}s | duration=${DURATION}s | gpu=${GPU} | watch_pid=${WATCH_PID:-none}"
echo "[run] CSV     -> ${OUT}"
echo "[run] summary -> ${SUMMARY}"
# NOT `a && b && echo` — common.sh sets `set -e`, and a bare AND-list whose
# first test is false makes the whole list exit non-zero, killing the script
# exactly in the normal case (a PID WAS given).
if [ -z "${WATCH_PID}" ] && [ "${DURATION}" = "0" ]; then
    echo "[run] no PID and no DURATION — sampling until Ctrl-C"
fi

echo "ts,elapsed_s,index,util_pct,mem_used_mb,mem_total_mb,temp_c,power_w" > "${OUT}"

STOP=0
trap 'STOP=1' INT TERM
T0="$(date +%s)"

should_continue() {
    [ "${STOP}" = "0" ] || return 1
    if [ -n "${WATCH_PID}" ]; then
        kill -0 "${WATCH_PID}" 2>/dev/null || return 1
    fi
    if [ "${DURATION}" -gt 0 ]; then
        [ $(( $(date +%s) - T0 )) -lt "${DURATION}" ] || return 1
    fi
    return 0
}

# p50/p90/p95/max for one column of one GPU index. Sorting with sort(1) keeps
# this linear-ish; an in-awk sort would crawl on a multi-hour sample.
pctl() {  # $1=col  $2=percentile  $3=gpu index
    awk -F, -v c="$1" -v g="$3" 'NR>1 && $3==g && $c!="" {print $c+0}' "${OUT}" \
      | sort -n \
      | awk -v p="$2" '{v[n++]=$1} END{ if(n==0){printf "n/a"; exit} printf "%.0f", v[int((p/100)*(n-1)+0.5)] }'
}

summarize() {
    local n_all
    n_all="$(( $(wc -l < "${OUT}") - 1 ))"
    {
        echo "================================================================"
        echo "gpu_probe summary${TAG:+  [${TAG}]}"
        echo "samples: ${n_all}   interval: ${INTERVAL}s   span: $(( $(date +%s) - T0 ))s"
        echo "csv:     ${OUT}"
        echo "================================================================"
        # `{ ...; } | tee` runs the block in a SUBSHELL, so a `return` here would
        # only leave the subshell, not the function — guard with a plain `if`
        # around the body instead of an early return.
        if [ "${n_all}" -lt 2 ]; then
            echo "Not enough samples to summarize (need at least 2)."
        else
        for idx in $(awk -F, 'NR>1 {print $3}' "${OUT}" | sort -u); do
            local total u50 u90 u95 umax m50 m95 mmax fit
            total="$(awk -F, -v g="${idx}" 'NR>1 && $3==g {print $6+0; exit}' "${OUT}")"
            u50="$(pctl 4 50 "${idx}")";  u90="$(pctl 4 90 "${idx}")"
            u95="$(pctl 4 95 "${idx}")";  umax="$(pctl 4 100 "${idx}")"
            m50="$(pctl 5 50 "${idx}")";  m95="$(pctl 5 95 "${idx}")"
            mmax="$(pctl 5 100 "${idx}")"
            echo ""
            echo "GPU ${idx}   (${total} MiB total)"
            echo "  utilization %   p50=${u50}  p90=${u90}  p95=${u95}  max=${umax}"
            echo "  VRAM used MiB   p50=${m50}  p95=${m95}  max=${mmax}"
            # VRAM headroom only. 90% of total is the usable ceiling (allocator
            # fragmentation + cuDNN workspace live in the rest).
            if [ "${mmax}" != "n/a" ] && [ "${mmax}" -gt 0 ] 2>/dev/null; then
                fit="$(awk -v t="${total}" -v m="${mmax}" 'BEGIN{ printf "%d", int(t*0.9/m) }')"
                echo "  fits by VRAM    ~${fit} job(s) of this size (0.9 x ${total} / ${mmax})"
            fi
            # An idle card yields a huge, meaningless "fits" number. Say so
            # rather than let it be quoted out of context.
            if [ "${umax}" != "n/a" ] && [ "${umax}" -lt 5 ] 2>/dev/null; then
                echo "  !! max utilization ${umax}% — no real workload was sampled on this GPU."
                echo "     The numbers above are an IDLE baseline, not a job profile."
            fi
            echo "  read as: VRAM decides IF a 2nd job fits; utilization decides if it"
            echo "           HELPS. p50 near 100 means the card is already saturated —"
            echo "           a 2nd job then buys no throughput, only OOM risk."
        done
        echo ""
        echo "Next: set MAX_JOBS in run/train_kd_parallel.sh from the smaller of the"
        echo "      two — the VRAM fit, and how far p50 utilization is below 100."
        fi
    } | tee "${SUMMARY}"
}

# Kept on ONE line so the validate-pipeline §3c lint can see the 2>/dev/null
# guard next to the call (it greps line-by-line).
QCOLS="index,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw"

while should_continue; do
    now="$(date +%s)"
    nvidia-smi --query-gpu="${QCOLS}" --format=csv,noheader,nounits 2>/dev/null \
      | tr -d ' ' \
      | awk -F, -v ts="$(date '+%F %T')" -v el="$(( now - T0 ))" -v want="${GPU}" \
            'want=="all" || $1==want { print ts "," el "," $1 "," $2 "," $3 "," $4 "," $5 "," $6 }' \
      >> "${OUT}" || true
    sleep "${INTERVAL}" || true
done

echo ""
echo "[run] sampling stopped ($( [ "${STOP}" = "1" ] && echo "interrupted" || echo "watched job exited / duration reached" ))"
summarize
echo "[run] DONE"
