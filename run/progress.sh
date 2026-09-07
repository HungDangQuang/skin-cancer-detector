#!/usr/bin/env bash
# ============================================================================
# run/progress.sh — READ-ONLY progress report for the training jobs on THIS box.
#
# Answers, for every running `scripts/train_{student,teacher}.py` process:
#   - which teacher / student / training mode (KD | KD+RKD | baseline) it is
#   - which fold it is on, and where that sits in the job's FOLDS list
#   - % done for the current fold (epoch N/M + time inside the epoch) and for
#     the whole job, plus an ETA
#   - RAM (main proc + dataloader workers) and GPU VRAM held by that PID
#   - last epoch's val_loss / val_pauc so you can see it is still learning
# then a per-run-dir summary of how many folds already have test_metrics.json.
#
# Usage (on the server):
#   bash run/progress.sh                 # one-shot report
#   bash run/progress.sh WATCH=15        # refresh every 15s (Ctrl-C to stop)
#   bash run/progress.sh RUNS=0          # skip the run-dir summary
#
# From the Mac, for BOTH vast.ai boxes at once:  bash run/progress_all.sh
#
# --- deliberate deviations from the run/*.sh house style --------------------
# This script does NOT source run/common.sh and does NOT call start_log,
# unlike every other run/*.sh. Reasons (both intentional, see run/README.md):
#   1. run/progress_all.sh pipes this file into the servers over stdin
#      (`ssh host 'bash -s' < run/progress.sh`), so ${BASH_SOURCE[0]} does not
#      resolve to a path and `source "$(dirname "$0")/common.sh"` would break.
#      Piping means the servers never need a `git pull` to get a newer monitor.
#   2. It is a read-only status reporter: it must not activate the venv, must
#      not touch CUDA_VISIBLE_DEVICES, and must not litter logs/ with a log
#      file per invocation (WATCH=15 would write thousands).
# It therefore sets its own strict mode below. It reads `ps`, `nvidia-smi`,
# logs/ and experiments/runs/ — it never writes, never kills, never installs.
# ============================================================================
# NOT -e: a missing nvidia-smi, an unreadable log or a vanished PID must degrade
# the report, never abort it half-printed.
set -uo pipefail

for arg in "$@"; do
    case "${arg}" in
        *=*)       export "${arg?}" ;;
        -h|--help) sed -n '2,30p' "$0" 2>/dev/null || echo "see run/README.md"; exit 0 ;;
        *)         echo "[progress] ignoring unknown arg: ${arg}" >&2 ;;
    esac
done

# --- repo root -------------------------------------------------------------
# Piped over ssh there is no script path to derive from, so probe the known
# locations (a repo root is identified by run/common.sh) or take PROJECT_DIR=.
PROJECT_DIR="${PROJECT_DIR:-}"
if [ -z "${PROJECT_DIR}" ]; then
    for _cand in "${PWD}" \
                 "/workspace/skin-cancer-detector" \
                 "${HOME}/skin-cancer-detector" \
                 "/mnt/sharednas/binhnt/hungdang/skin-cancer-detector"; do
        if [ -f "${_cand}/run/common.sh" ]; then PROJECT_DIR="${_cand}"; break; fi
    done
fi
if [ -z "${PROJECT_DIR}" ] || [ ! -d "${PROJECT_DIR}" ]; then
    echo "ERROR: repo root not found. Pass it explicitly: PROJECT_DIR=/path/to/skin-cancer-detector" >&2
    exit 2
fi
cd "${PROJECT_DIR}" || exit 2

LABEL="${LABEL:-$(hostname)}"
WATCH="${WATCH:-0}"          # >0 = refresh loop, seconds
RUNS="${RUNS:-1}"            # 1 = print the run-dir fold summary
STALE_MIN="${STALE_MIN:-10}" # log untouched for this many minutes => STALLED
OUTPUT_DIR_DEFAULT="${OUTPUT_DIR_DEFAULT:-experiments/runs}"
BAR_W="${BAR_W:-22}"
TAIL_BYTES="${TAIL_BYTES:-32768}"   # how far back to look for the live tqdm bar

# Filled in per pass (declared here so `set -u` never trips over them).
LOG_MAP=""        # "pid<TAB>logfile" for every trainer process
CLAIMED_LOGS=""   # logs already attributed to a job in this pass
VRAM_NS_OK=1      # 0 = nvidia-smi PIDs live in another namespace than ours

# --- colors ----------------------------------------------------------------
COLOR="${COLOR:-auto}"
if [ "${COLOR}" = "auto" ]; then
    if [ -t 1 ]; then COLOR=1; else COLOR=0; fi
fi
if [ "${COLOR}" = "1" ]; then
    B=$'\033[1m'; DIM=$'\033[2m'; R=$'\033[0m'
    RED=$'\033[31m'; GRN=$'\033[32m'; YLW=$'\033[33m'; BLU=$'\033[36m'
else
    B=""; DIM=""; R=""; RED=""; GRN=""; YLW=""; BLU=""
fi

# --- small helpers ---------------------------------------------------------
hr() { printf '%s\n' "------------------------------------------------------------------------------"; }

# seconds -> "2d 03h 14m"
hms() {
    awk -v s="${1:-}" 'BEGIN{
        if (s == "" || s < 0) { print "?"; exit }
        d=int(s/86400); s-=d*86400; h=int(s/3600); s-=h*3600; m=int(s/60);
        if (d>0)      printf "%dd %02dh %02dm", d, h, m;
        else if (h>0) printf "%dh %02dm", h, m;
        else          printf "%dm", m;
    }'
}

# MB -> "6.7 GB"
gb() {
    awk -v m="${1:-}" 'BEGIN{
        if (m == "" || m+0 <= 0) { print "-"; exit }
        if (m+0 >= 1024) printf "%.1f GB", m/1024; else printf "%d MB", m;
    }'
}

# percent -> "[####......]  42.1%"
bar() {
    awk -v p="${1:-0}" -v w="${2:-22}" 'BEGIN{
        if (p == "" || p < 0) p = 0; if (p > 100) p = 100;
        n = int(p*w/100 + 0.5); s = "[";
        for (i = 0; i < n; i++) s = s "#";
        for (; i < w; i++)      s = s ".";
        printf "%s] %5.1f%%", s, p;
    }'
}

# "2026-08-16 11:06:55" -> epoch seconds (GNU date; BSD/mac fallback). "" if unparseable.
to_epoch() {
    [ -n "${1:-}" ] || { echo ""; return; }
    date -d "$1" +%s 2>/dev/null \
        || date -j -f "%Y-%m-%d %H:%M:%S" "$1" +%s 2>/dev/null \
        || echo ""
}

file_mtime() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo ""; }

# ============================================================================
# Host-level: GPU, RAM, disk
# ============================================================================
print_host() {
    local now; now="$(date '+%F %T')"
    printf '%s\n' "${B}=== ${LABEL} ${R}${DIM}(${now})${R}"

    if command -v nvidia-smi >/dev/null 2>&1; then
        nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits 2>/dev/null \
            | awk -F', *' '{printf "  GPU %s  %-22s  VRAM %6.1f/%.0f GB (%2.0f%%)  util %3s%%  %s C\n", \
                            $1, $2, $3/1024, $4/1024, 100*$3/$4, $5, $6}'
    else
        echo "  GPU: not available on this box"
    fi

    if command -v free >/dev/null 2>&1; then
        free -m 2>/dev/null | awk '/^Mem:/{printf "  RAM   %.1f/%.1f GB used, %.1f GB available\n", $3/1024, $2/1024, $7/1024}'
    fi

    # Project filesystem, plus "/" separately when the repo lives elsewhere —
    # a full "/" has bitten this project before (Errno 28 mid-run).
    local proj_fs
    proj_fs="$(df -h . 2>/dev/null | awk 'NR==2{print $NF}')"
    df -h . 2>/dev/null | awk 'NR==2{printf "  DISK  %-14s %s used of %s (%s)\n", $NF, $3, $2, $5}'
    if [ "${proj_fs}" != "/" ]; then
        df -h / 2>/dev/null | awk 'NR==2{printf "  DISK  %-14s %s used of %s (%s)\n", "/", $3, $2, $5}'
    fi
}

# ============================================================================
# Log parsing — everything about the CURRENT fold, in one pass.
#
# Two log line formats carry the epoch summary (both are emitted; dedup by epoch
# number): "2026-08-16 11:06:55 | INFO | ... | Epoch 8/50 | ..." and Hydra's
# "[2026-08-16 11:06:55,053][...][INFO] - Epoch 8/50 | ...".
# tqdm writes with \r and no newline, so a whole epoch can be ONE "line" —
# hence the `tr '\r' '\n'`.
# Emits: fold|fold_start|epoch|total_epochs|last_epoch_ts|val_loss|val_pauc|train_loss|early_stop|folds_list
# ============================================================================
parse_log() {
    local log="$1"
    tr '\r' '\n' < "${log}" 2>/dev/null | awk '
        function ts(line,   m) {
            if (match(line, /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]/))
                return substr(line, RSTART, RLENGTH);
            return "";
        }
        function val(line, key,   m, s) {
            if (match(line, key "=[-0-9.naeNA]+")) {
                s = substr(line, RSTART, RLENGTH); sub(key "=", "", s); return s;
            }
            return "";
        }
        # run/train_{student,teacher}.sh header — the FOLDS list this job owns.
        /^\[run\] (Student|Teacher) / {
            if (match($0, /folds [0-9 ]+/)) {
                fl = substr($0, RSTART+6, RLENGTH-6); sub(/ +$/, "", fl);
            }
        }
        # per-fold banner: "[run] === distillation: T -> S | fold 3 (start 2026-08-16 04:39:35) ==="
        /^\[run\] === / {
            if (match($0, /fold [0-9]+/)) fold = substr($0, RSTART+5, RLENGTH-5);
            if (match($0, /\(start [0-9-]+ [0-9:]+\)/))
                fstart = substr($0, RSTART+7, RLENGTH-8);
            ep = 0; tot = 0; lastts = ""; vl = ""; vp = ""; tl = ""; es = 0;
        }
        /Epoch [0-9]+\/[0-9]+ \|/ {
            if (match($0, /Epoch [0-9]+\/[0-9]+/)) {
                split(substr($0, RSTART+6, RLENGTH-6), a, "/");
                if (a[1]+0 != ep) {            # same epoch is logged twice
                    ep = a[1]+0; tot = a[2]+0;
                    lastts = ts($0);
                    tl = val($0, "train_loss"); vl = val($0, "val_loss"); vp = val($0, "val_pauc");
                }
            }
        }
        /Early stopping triggered/ { es = 1 }
        END {
            printf "%s|%s|%d|%d|%s|%s|%s|%s|%d|%s\n",
                   fold, fstart, ep, tot, lastts, vl, vp, tl, es, fl;
        }
    '
}

# ----------------------------------------------------------------------------
# pid -> log file, via the `tee` that start_log spawned.
#
# start_log does `exec > >(tee -a logs/<name>_<ts>.log)`, so the tee is a child
# of the run/train_*.sh shell. It is NOT always the trainer's direct parent:
# depending on the bash build, the script shell forks an extra copy of itself
# (seen on one vast box: python's parent = 2274, tee's parent = 2282, both
# `run/train_student.sh`). So both the tee and the trainer are walked UP to the
# outermost `run/train_{student,teacher}.sh` ancestor — that root is the job,
# and it is what pairs them. PGID is useless here: every job launched by
# run/train_kd_parallel.sh shares the launcher's process group.
# Emits "pid<TAB>logpath" lines for the trainer processes.
# ----------------------------------------------------------------------------
log_map() {
    printf '%s\n' "$1" | awk '
        function root(p,   r) {
            r = p;
            while ((r in par) && (par[r] in cmd) && (cmd[par[r]] ~ /run\/train_(student|teacher)\.sh/))
                r = par[r];
            return r;
        }
        {
            pid = $1; par[pid] = $2;
            a = ""; for (i = 6; i <= NF; i++) a = a $i " ";
            cmd[pid] = a;
            if (a ~ /^tee -a /)                              { tees[++nt] = pid; teelog[pid] = $NF }
            if (a ~ /scripts\/train_(student|teacher)\.py/)  { pys[++np]  = pid }
        }
        END {
            for (i = 1; i <= nt; i++) rootlog[root(tees[i])] = teelog[tees[i]];
            for (i = 1; i <= np; i++) {
                r = root(pys[i]);
                if (r in rootlog) printf "%s\t%s\n", pys[i], rootlog[r];
            }
        }
    '
}

# Last tqdm bar (current phase inside the epoch), unicode blocks stripped.
parse_bar() {
    tail -c "${TAIL_BYTES:-32768}" "$1" 2>/dev/null | tr '\r' '\n' \
        | grep -aE '[0-9]+/[0-9]+ \[[0-9]' | tail -1 \
        | sed -e 's/|[^|]*|/ /' -e 's/  */ /g' -e 's/^ //'
}

# ============================================================================
# Jobs
# ============================================================================
print_jobs() {
    local ps_all train_lines all_pids mains now
    now="$(date +%s)"
    ps_all="$(ps -eo pid=,ppid=,etimes=,rss=,pcpu=,args= 2>/dev/null)"

    train_lines="$(printf '%s\n' "${ps_all}" | grep -E 'scripts/train_(student|teacher)\.py' | grep -v ' grep ')"
    if [ -z "${train_lines}" ]; then
        echo "  ${YLW}no training process running${R}"
        return 0
    fi

    # A dataloader worker is a fork of the trainer and has the SAME cmdline, so
    # "main" = a train_*.py process whose parent is not itself a train_*.py.
    all_pids="$(printf '%s\n' "${train_lines}" | awk '{print $1}')"
    mains="$(printf '%s\n' "${train_lines}" \
             | awk -v pids="${all_pids}" 'BEGIN{n=split(pids,a," "); for(i=1;i<=n;i++) s[a[i]]=1} !($2 in s)')"

    # pid -> VRAM (MiB). Some containers (one of the two vast boxes) run in their
    # own PID namespace while nvidia-smi reports the HOST pids — then nothing
    # matches and per-process VRAM is simply unavailable; say so instead of "-".
    local gpu_map
    gpu_map="$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')"
    VRAM_NS_OK=1
    if [ -n "${gpu_map}" ]; then
        if ! printf '%s\n' "${gpu_map}" | awk -F, -v all="$(printf '%s\n' "${ps_all}" | awk '{print $1}' | tr '\n' ' ')" \
             'BEGIN{n=split(all,a," "); for(i=1;i<=n;i++) s[a[i]]=1} ($1 in s){found=1} END{exit !found}'; then
            VRAM_NS_OK=0
        fi
    fi

    LOG_MAP="$(log_map "${ps_all}")"

    local n=0
    while IFS= read -r line; do
        [ -n "${line}" ] || continue
        n=$((n + 1))
        print_one_job "${line}" "${ps_all}" "${gpu_map}" "${now}"
    done <<EOF
${mains}
EOF
    if [ "${VRAM_NS_OK}" = "0" ]; then
        hr
        printf '  %s\n' "${DIM}note: per-process VRAM is unavailable on this box (nvidia-smi reports host PIDs, the container sees its own) — use the GPU total above.${R}"
    fi
    [ "${n}" -gt 0 ] || echo "  ${YLW}no training process running${R}"
}

print_one_job() {
    local line="$1" ps_all="$2" gpu_map="$3" now="$4"

    local pid ppid etimes rss pcpu args
    pid="$(echo "${line}"  | awk '{print $1}')"
    ppid="$(echo "${line}" | awk '{print $2}')"
    etimes="$(echo "${line}" | awk '{print $3}')"
    rss="$(echo "${line}"  | awk '{print $4}')"
    pcpu="$(echo "${line}" | awk '{print $5}')"
    args="$(echo "${line}" | awk '{for(i=6;i<=NF;i++) printf "%s ", $i}')"

    # --- what is it training? (Hydra overrides on the command line) ---------
    local kind="student" stu="" tea="" trn="" fold="" aug="" suffix="" outdir="${OUTPUT_DIR_DEFAULT}" priv=0
    local tok
    for tok in ${args}; do
        case "${tok}" in
            *scripts/train_teacher.py) kind="teacher" ;;
            *scripts/train_student.py) kind="student" ;;
            student=*)                 stu="${tok#*=}" ;;
            teacher=*)                 tea="${tok#*=}" ;;
            training=*)                trn="${tok#*=}" ;;
            data.fold=*)               fold="${tok#*=}" ;;
            augmentation=*)            aug="${tok#*=}" ;;
            run_suffix=*)              suffix="${tok#*=}" ;;
            output_dir=*)              outdir="${tok#*=}" ;;
            data.metadata_as_input=*)  priv=1 ;;
        esac
    done

    # --- run-dir (must mirror scripts/train_{teacher,student}.py) -----------
    local run_name
    case "${kind}" in
        teacher) run_name="teacher/${tea}" ;;                       # train_teacher.py:39 (path is hard-wired, no suffix)
        *)       case "${trn}" in
                     baseline*) run_name="baseline_${stu}${suffix}" ;;   # train_student.py:93
                     *)         run_name="kd_${tea}_to_${stu}${suffix}" ;;  # train_student.py:71
                 esac ;;
    esac
    local run_dir="${outdir}/${run_name}"

    # --- the log this process is tee'ing into -------------------------------
    local log cand hdr
    log="$(printf '%s\n' "${LOG_MAP}" | awk -F'\t' -v p="${pid}" '$1==p{print $2}' | head -1)"
    if [ -z "${log}" ] || [ ! -f "${log}" ]; then
        # Fallback (job not launched through start_log, or tee already gone):
        # newest logs/train_<kind>_*.log whose [run] header names this model and
        # that no earlier job in this pass already claimed — never blindly the
        # newest one, or two concurrent jobs would report each other's numbers.
        log=""
        for cand in $(ls -t "logs/train_${kind}"_*.log 2>/dev/null); do
            case " ${CLAIMED_LOGS} " in *" ${cand} "*) continue ;; esac
            hdr="$(head -c 4096 "${cand}" 2>/dev/null | tr '\r' '\n' | grep -a -m1 '^\[run\] \(Student\|Teacher\) ')"
            case "${hdr}" in
                *"${stu:-__none__}"*) [ -n "${stu}" ] && { log="${cand}"; break; } ;;
            esac
            if [ "${kind}" = "teacher" ]; then
                case "${hdr}" in *"Teacher ${tea} "*) log="${cand}"; break ;; esac
            fi
        done
    fi
    [ -n "${log}" ] && CLAIMED_LOGS="${CLAIMED_LOGS} ${log}"

    # --- parse it ------------------------------------------------------------
    local pfold fstart epoch total lastts vloss vpauc tloss estop folds_list
    if [ -n "${log}" ] && [ -f "${log}" ]; then
        IFS='|' read -r pfold fstart epoch total lastts vloss vpauc tloss estop folds_list <<EOF
$(parse_log "${log}")
EOF
    else
        pfold=""; fstart=""; epoch=0; total=0; lastts=""; vloss=""; vpauc=""; tloss=""; estop=0; folds_list=""
    fi
    [ -n "${folds_list}" ] || folds_list="0 1 2 3 4"
    [ -n "${fold}" ] || fold="${pfold}"

    # --- progress math -------------------------------------------------------
    # fold %  = (completed epochs + fraction of the epoch in flight) / total epochs
    # job  %  = (folds finished in THIS job's FOLDS list + fold %) / folds in list
    local fstart_s lastts_s
    fstart_s="$(to_epoch "${fstart}")"
    lastts_s="$(to_epoch "${lastts}")"

    local idx=0 nfolds=0 f
    for f in ${folds_list}; do
        [ "${f}" = "${fold}" ] && idx="${nfolds}"
        nfolds=$((nfolds + 1))
    done
    [ "${nfolds}" -gt 0 ] || nfolds=1

    local calc fold_pct job_pct eta_fold eta_job avg_epoch
    calc="$(awk -v ep="${epoch:-0}" -v tot="${total:-0}" -v fs="${fstart_s:-}" -v lt="${lastts_s:-}" \
                -v now="${now}" -v idx="${idx}" -v nf="${nfolds}" 'BEGIN{
        fold_pct = 0; job_pct = 0; eta_fold = ""; eta_job = ""; avg = "";
        if (tot > 0 && ep > 0 && fs != "" && lt != "") {
            avg = (lt - fs) / ep;                       # mean seconds per epoch, this fold
            intra = (avg > 0) ? (now - lt) / avg : 0;   # time-based, since train and val
            if (intra < 0) intra = 0;                   # phases differ wildly in length
            if (intra > 0.99) intra = 0.99;
            fold_pct = 100 * (ep + intra) / tot;
            eta_fold = (tot - ep - intra) * avg;
            eta_job  = eta_fold + (nf - idx - 1) * tot * avg;
        } else if (tot > 0 && ep > 0) {
            fold_pct = 100 * ep / tot;
        }
        if (fold_pct > 100) fold_pct = 100;
        job_pct = 100 * (idx + fold_pct/100) / nf;
        printf "%.4f|%.4f|%s|%s|%s", fold_pct, job_pct, eta_fold, eta_job, avg;
    }')"
    IFS='|' read -r fold_pct job_pct eta_fold eta_job avg_epoch <<EOF
${calc}
EOF

    # --- resources -----------------------------------------------------------
    local wcount wrss
    read -r wcount wrss <<EOF
$(printf '%s\n' "${ps_all}" | awk -v p="${pid}" '$2==p {c++; r+=$4} END{print c+0, r+0}')
EOF
    local main_mb=$(( ${rss:-0} / 1024 ))
    local work_mb=$(( ${wrss:-0} / 1024 ))
    local vram vram_txt
    vram="$(printf '%s\n' "${gpu_map}" | awk -F, -v p="${pid}" '$1==p{print $2}' | head -1)"
    if [ -n "${vram}" ]; then
        vram_txt="$(gb "${vram}")"
    elif [ "${VRAM_NS_OK}" = "0" ]; then
        vram_txt="n/a*"
    else
        vram_txt="-"
    fi

    # --- freshness -----------------------------------------------------------
    local state="${GRN}RUNNING${R}" mt age=0
    if [ -n "${log}" ] && [ -f "${log}" ]; then
        mt="$(file_mtime "${log}")"
        [ -n "${mt}" ] && age=$(( now - mt ))
        if [ "${age}" -gt $(( STALE_MIN * 60 )) ]; then
            state="${RED}STALLED (log quiet $(hms ${age}))${R}"
        fi
    fi
    [ "${estop:-0}" = "1" ] && state="${state} ${YLW}[early-stopped this fold]${R}"

    # --- render --------------------------------------------------------------
    local title mode
    case "${trn}" in
        baseline*)          mode="baseline (no KD)" ;;
        distillation_rkd)   mode="KD + RKD feature-KD" ;;
        distillation*)      mode="KD (logit)" ;;
        "")                 mode="standalone" ;;
        *)                  mode="${trn}" ;;
    esac
    [ "${priv}" = "1" ] && mode="${mode} + privileged/LUPI"

    if [ "${kind}" = "teacher" ]; then
        title="teacher ${B}${tea}${R}"
    else
        title="student ${B}${stu}${R} ${DIM}<-${R} teacher ${B}${tea}${R}"
    fi

    hr
    printf '%s  %s\n' "${BLU}▶${R} ${title}" "${DIM}[${mode}]${R}"
    printf '   %-9s pid=%s  up %s  cpu %s%%  aug=%s\n' "state:" "${pid}" "$(hms "${etimes}")" "${pcpu}" "${aug:-light}"
    printf '   %-9s %s\n' "" "${state}"
    printf '   %-9s %s\n' "run-dir:" "${run_dir}"

    # fold line
    local done_folds
    done_folds="$(ls -d "${run_dir}"/fold_*/test_metrics.json 2>/dev/null | wc -l | tr -d ' ')"
    printf "   %-9s fold ${B}%s${R} of [%s]  (job fold %d/%d)   run-dir: %s/5 folds finished\n" \
           "fold:" "${fold:-?}" "${folds_list}" "$((idx + 1))" "${nfolds}" "${done_folds:-0}"

    # epoch + progress
    if [ "${total:-0}" -gt 0 ]; then
        printf '   %-9s epoch %s/%s   %s\n' "fold %:" "${epoch}" "${total}" "$(bar "${fold_pct}" "${BAR_W}")"
    else
        printf '   %-9s %s\n' "fold %:" "${DIM}warming up (no epoch logged yet)${R}"
    fi
    printf '   %-9s %s   %s\n' "job %:" "$(bar "${job_pct}" "${BAR_W}")" \
           "${DIM}(this launch = folds ${folds_list})${R}"

    if [ -n "${eta_fold}" ]; then
        printf '   %-9s ~%s/epoch  ->  fold ends in ~%s, job in ~%s %s\n' \
               "eta:" "$(hms "${avg_epoch}")" "$(hms "${eta_fold}")" "$(hms "${eta_job}")" \
               "${DIM}(if it runs all ${total} epochs; early stopping can cut it)${R}"
    fi

    # resources
    printf '   %-9s main %s + %s workers %s = %s   |   VRAM %s\n' \
           "ram:" "$(gb "${main_mb}")" "${wcount:-0}" "$(gb "${work_mb}")" \
           "$(gb "$(( main_mb + work_mb ))")" "${vram_txt}"

    # last metrics + live bar
    if [ -n "${vpauc}" ]; then
        printf '   %-9s train_loss=%s  val_loss=%s  val_pauc=%s  %s\n' \
               "last ep:" "${tloss:-?}" "${vloss:-?}" "${vpauc}" "${DIM}(@ ${lastts})${R}"
    fi
    local livebar
    livebar="$(parse_bar "${log}")"
    [ -n "${livebar}" ] && printf '   %-9s %s\n' "now:" "${DIM}${livebar}${R}"
    [ -n "${log}" ] && printf '   %-9s %s\n' "log:" "${DIM}${log}${R}"
}

# ============================================================================
# Run-dir summary: how many folds already produced test_metrics.json
# ============================================================================
print_runs() {
    local base="${OUTPUT_DIR_DEFAULT}"
    [ -d "${base}" ] || return 0
    hr
    printf '%s\n' "${B}run-dirs (folds with test_metrics.json)${R}"
    find "${base}" -maxdepth 4 -name test_metrics.json 2>/dev/null \
        | sed 's#/fold_[0-9]*/test_metrics.json##' \
        | sort | uniq -c \
        | awk -v base="${base}" -v w="${BAR_W}" '{
            n = $1; d = $2; sub("^" base "/", "", d);
            p = (n > 5 ? 5 : n) * 100 / 5;
            k = int(p*w/100 + 0.5); s = "[";
            for (i = 0; i < k; i++) s = s "#";
            for (; i < w; i++)      s = s ".";
            printf "  %-52s %d/5 %s]\n", d, n, s;
        }' | sort
}

# ============================================================================
main_once() {
    print_host
    hr
    printf '%s\n' "${B}training jobs${R}"
    print_jobs
    [ "${RUNS}" = "1" ] && print_runs
    hr
}

if [ "${WATCH}" != "0" ]; then
    while :; do
        clear 2>/dev/null || printf '\033[H\033[2J'
        main_once
        printf '%s\n' "${DIM}refresh every ${WATCH}s — Ctrl-C to stop${R}"
        sleep "${WATCH}"
    done
else
    main_once
fi
