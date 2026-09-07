#!/usr/bin/env bash
# ============================================================================
# run/pull_results.sh — compare the run-dirs on every training box against the
# ones on this Mac, then pull down the ones that are missing (or newer).
#
# Meant to be run FROM THE MAC. It is a *check* by default: nothing is written
# until you add `pull`.
#
# Usage:
#   bash run/pull_results.sh                      # check only: what's on the servers but not here
#   bash run/pull_results.sh pull                 # + rsync the NEW folds down
#   bash run/pull_results.sh pull stale           # + also re-pull folds whose remote copy is NEWER
#   bash run/pull_results.sh pull ckpt            # + also best_model.pth (heavy; never last_model.pth)
#   bash run/pull_results.sh pull dry             # rsync --dry-run (show, don't write)
#   bash run/pull_results.sh vastnew              # only one host
#   bash run/pull_results.sh 'kd_convnextv2*'     # only run-dirs matching a glob
#
# Bare words are parsed as: check|pull -> MODE, stale|force -> STALE=1,
# ckpt -> CKPT=1, dry -> DRY=1, anything with / * kd_ baseline_ teacher ->
# appended to ONLY, everything else -> treated as an ssh host alias.
# KEY=VALUE args always win over bare words.
#
# Args (KEY=VALUE, or env vars):
#   HOSTS       space-separated ssh targets, each optionally "host:/repo/path"
#               (default "vastnew" — the alias in ~/.ssh/config)
#   REMOTE_DIR  repo path for hosts without their own ":path"
#               (default /workspace/skin-cancer-detector — the vast.ai layout)
#   ROOTS       run roots to compare, relative to the repo root
#               (default "experiments/runs experiments/runs_isic_only")
#   MODE        check | pull        (default check)
#   ONLY        space-separated globs filtering the run-dir path (default: all)
#   STALE       1 = also pull folds whose remote test_metrics.json is newer
#               than the local one; the local fold is MOVED to
#               experiments/_replaced/<timestamp>/ first, never deleted
#   CKPT        1 = also pull checkpoints/best_model.pth (last_model.pth never)
#   DRY         1 = rsync --dry-run
#   ARGS        extra bare/KEY=VALUE args as one string (used by /pull-results)
#   SSH_OPTS    extra ssh options (default "-o BatchMode=yes -o ConnectTimeout=10")
#
# What gets pulled (per fold): test_metrics.json, val_metrics.json,
# predictions.csv, val_predictions.csv, config.yaml, training_curves.png,
# calibration_metrics.json, reliability_curve.png — i.e. everything the
# eval-results / update-report skills read (~4 MB/fold). Plus aggregated.json /
# aggregated.md at the run-dir level. Checkpoints only with CKPT=1.
#
# Like run/progress*.sh this runs on the Mac, so it deliberately does NOT source
# run/common.sh: there is no ./.venv-linux and no GPU here, and a status check
# must not create a logs/ entry. It never writes anything on the servers.
# See run/README.md §8.
# ============================================================================
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}" || exit 2

HOSTS_DEFAULT="vastnew"
HOSTS_ARG=""
ONLY="${ONLY:-}"
MODE="${MODE:-check}"
STALE="${STALE:-0}"
CKPT="${CKPT:-0}"
DRY="${DRY:-0}"

parse_arg() {
    case "$1" in
        *=*)                export "${1?}" ;;
        check|pull)         MODE="$1" ;;
        stale|force)        STALE=1 ;;
        ckpt|checkpoint*)   CKPT=1 ;;
        dry|dry-run)        DRY=1 ;;
        -h|--help)          sed -n '2,45p' "$0"; exit 0 ;;
        "")                 : ;;
        */*|*\**|kd_*|baseline_*|teacher*|runs*)
                            ONLY="${ONLY} $1" ;;
        *)                  HOSTS_ARG="${HOSTS_ARG} $1" ;;
    esac
}

for arg in "$@"; do parse_arg "${arg}"; done
# ARGS="..." (one string, e.g. from the /pull-results slash command). Globs must
# survive word-splitting untouched, hence the set -f fence.
if [ -n "${ARGS:-}" ]; then
    set -f
    # shellcheck disable=SC2086  # deliberate word-split of the ARGS string
    set -- ${ARGS}
    set +f
    for arg in "$@"; do parse_arg "${arg}"; done
fi

HOSTS="${HOSTS:-${HOSTS_ARG:-${HOSTS_DEFAULT}}}"
REMOTE_DIR="${REMOTE_DIR:-/workspace/skin-cancer-detector}"
ROOTS="${ROOTS:-experiments/runs experiments/runs_isic_only}"
SSH_OPTS="${SSH_OPTS:--o BatchMode=yes -o ConnectTimeout=10}"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_ROOT="experiments/_replaced/${STAMP}"

if [ -t 1 ]; then COLOR="${COLOR:-1}"; else COLOR="${COLOR:-0}"; fi
if [ "${COLOR}" = "1" ]; then
    B=$'\033[1m'; R=$'\033[0m'; DIM=$'\033[2m'
    GRN=$'\033[32m'; YEL=$'\033[33m'; CYA=$'\033[36m'
else
    B=""; R=""; DIM=""; GRN=""; YEL=""; CYA=""
fi

TMP="$(mktemp -d -t pull_results.XXXXXX)" || exit 2
trap 'rm -rf "${TMP}"' EXIT

# ---------------------------------------------------------------------------
# Inventory snippet — ONE source of truth, run both locally (bash) and remotely
# (ssh 'bash -s'), so the two sides can never drift. Emits one line per fold dir:
#     <relpath>|DONE|<mtime of test_metrics.json>|<bytes of light artifacts>|<bytes of best_model.pth>
#     <relpath>|RUNNING|0|0|0
# `ls -l` column 5 is the size on both GNU and BSD userland; `stat` differs, so
# both flavours are tried.
# ---------------------------------------------------------------------------
INVENTORY='
cd "$PROJECT_DIR" 2>/dev/null || { echo "__ERR__ no such dir: $PROJECT_DIR" >&2; exit 9; }
_mtime() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo 0; }
_size()  { ls -l "$1" 2>/dev/null | awk "{print \$5+0}" || echo 0; }
for r in $ROOTS; do
    [ -d "$r" ] || continue
    find "$r" -maxdepth 3 -type d -name "fold_*" 2>/dev/null | sort | while IFS= read -r f; do
        if [ -f "$f/test_metrics.json" ]; then
            sz=$(ls -l "$f"/*.json "$f"/*.csv "$f"/*.png "$f"/*.yaml 2>/dev/null | awk "{t+=\$5} END{print t+0}")
            ck=0
            [ -f "$f/checkpoints/best_model.pth" ] && ck=$(_size "$f/checkpoints/best_model.pth")
            printf "%s|DONE|%s|%s|%s\n" "$f" "$(_mtime "$f/test_metrics.json")" "${sz:-0}" "${ck:-0}"
        else
            printf "%s|RUNNING|0|0|0\n" "$f"
        fi
    done
done
'

human() { awk -v b="${1:-0}" 'BEGIN{ if (b<1024) printf "%d B", b;
    else if (b<1048576) printf "%.0f KB", b/1024;
    else if (b<1073741824) printf "%.1f MB", b/1048576;
    else printf "%.2f GB", b/1073741824 }'; }

# ONLY is a list of globs matched against the fold path; empty = match everything.
match_only() {
    [ -z "${ONLY// /}" ] && return 0
    local p
    for p in ${ONLY}; do
        case "$1" in *${p}*|${p}) return 0 ;; esac
    done
    return 1
}

# ---------------------------------------------------------------------------
# 1. Inventories
# ---------------------------------------------------------------------------
PROJECT_DIR="${REPO_ROOT}" ROOTS="${ROOTS}" bash -c "${INVENTORY}" > "${TMP}/local" 2>/dev/null

UNREACHABLE=""
HOST_LIST=""
for entry in ${HOSTS}; do
    case "${entry}" in
        *:*) host="${entry%%:*}"; dir="${entry#*:}" ;;
        *)   host="${entry}";     dir="${REMOTE_DIR}" ;;
    esac
    # shellcheck disable=SC2086  # SSH_OPTS must word-split into separate flags
    ssh -T ${SSH_OPTS} "${host}" "PROJECT_DIR='${dir}' ROOTS='${ROOTS}' bash -s" \
        <<< "${INVENTORY}" > "${TMP}/remote.${host}" 2>"${TMP}/err.${host}"
    if [ $? -ne 0 ] || [ ! -s "${TMP}/remote.${host}" ]; then
        UNREACHABLE="${UNREACHABLE} ${host}"
        rm -f "${TMP}/remote.${host}"
        continue
    fi
    HOST_LIST="${HOST_LIST} ${host}:${dir}"
done

# ---------------------------------------------------------------------------
# 2. Classify every remote fold against the local copy
#    NEW     = no finished local copy            -> pulled by `pull`
#    STALE   = local exists but remote is newer  -> pulled only with `stale`
#    SAME    = already here
#    RUNNING = still training on the box, no test_metrics.json yet
# ---------------------------------------------------------------------------
: > "${TMP}/classified"
for entry in ${HOST_LIST}; do
    host="${entry%%:*}"
    awk -F'|' -v host="${host}" '
        NR==FNR { lst[$1]=$2; lmt[$1]=$3; next }
        {
            path=$1; st=$2; rmt=$3; sz=$4; ck=$5; cls="SAME";
            if (st == "RUNNING")                          cls="RUNNING";
            else if (!(path in lst) || lst[path]!="DONE") cls="NEW";
            else if (rmt > lmt[path] + 2)                 cls="STALE";
            print cls "|" host "|" path "|" sz "|" ck;
        }' "${TMP}/local" "${TMP}/remote.${host}" >> "${TMP}/classified"
done

# apply the ONLY filter
: > "${TMP}/sel"
while IFS='|' read -r cls host path sz ck; do
    [ -z "${path}" ] && continue
    match_only "${path}" && printf '%s|%s|%s|%s|%s\n' "${cls}" "${host}" "${path}" "${sz}" "${ck}" >> "${TMP}/sel"
done < "${TMP}/classified"

# ---------------------------------------------------------------------------
# 3. Report
# ---------------------------------------------------------------------------
printf '%s\n' "${B}=== run-dirs: servers vs. this Mac ===${R}"
printf '%s\n' "${DIM}hosts:${HOSTS}   roots: ${ROOTS}   mode: ${MODE}${DIM}${R}"
[ -n "${ONLY// /}" ] && printf '%s\n' "${DIM}filter:${ONLY}${R}"
[ -n "${UNREACHABLE}" ] && printf '%s\n' "${YEL}UNREACHABLE:${UNREACHABLE}${R}"
echo

for entry in ${HOST_LIST}; do
    host="${entry%%:*}"; dir="${entry#*:}"
    printf '%s\n' "${B}${CYA}${host}${R}  ${DIM}${dir}${R}"
    awk -F'|' -v host="${host}" -v grn="${GRN}" -v yel="${YEL}" -v dim="${DIM}" -v rst="${R}" '
        # pass 1: the local inventory — how many finished folds this Mac has per run
        NR==FNR { if ($2=="DONE") { lr=$1; sub("/fold_[0-9]+$", "", lr); lcnt[lr]++ } next }
        $2 != host { next }
        {
            run=$3; sub("/fold_[0-9]+$", "", run);
            n[run]++; c[run "|" $1]++; sz[run] += ($1=="NEW" || $1=="STALE" ? $4 : 0);
            ck[run] += ($1=="NEW" || $1=="STALE" ? $5 : 0);
            if (!(run in seen)) { seen[run]=1; order[++k]=run }
        }
        END {
            if (k == 0) { print "  (no run-dirs)"; exit }
            printf "  %-58s %5s %5s %5s %8s   %s\n", "run-dir", "new", "old", "here", "run", "to pull";
            for (i = 1; i <= k; i++) {
                r = order[i]; lbl = r; sub("^experiments/", "", lbl);
                nw = c[r "|NEW"] + 0; st = c[r "|STALE"] + 0;
                sm = c[r "|SAME"] + 0; rn = c[r "|RUNNING"] + 0;
                mb = sz[r] / 1048576;
                # folds this Mac has that the server does NOT have at all: if some
                # folds are being replaced by a re-train, these leftovers belong to
                # the OLD experiment and would silently mix into one run-dir.
                left = lcnt[r] - (sm + st); if (left < 0) left = 0;
                warn = (st > 0 && left > 0) ? sprintf("  MIXED: %d fold cu con lai", left) : "";
                col = (nw > 0 ? grn : (st > 0 ? yel : dim));
                printf "  %s%-58s %5d %5d %5d %8d   %6.1f MB%s%s\n", col, lbl, nw, st, sm, rn, mb, warn, rst;
            }
        }' "${TMP}/local" "${TMP}/sel"
    echo
done

# totals (pre-bound: `read` below is the only writer, and a short read under
# `set -u` must not leave any of them unset)
TOT_NEW=0; TOT_STALE=0; TOT_SAME=0; TOT_RUN=0; TOT_NEW_B=0; TOT_STALE_B=0; TOT_CK=0
read -r TOT_NEW TOT_STALE TOT_SAME TOT_RUN TOT_NEW_B TOT_STALE_B TOT_CK <<EOF
$(awk -F'|' '{ if ($1=="NEW") {n++; b+=$4; c+=$5} else if ($1=="STALE") {s++; b2+=$4; c2+=$5}
    else if ($1=="SAME") m++; else if ($1=="RUNNING") r++ }
    END { printf "%d %d %d %d %d %d %d", n+0, s+0, m+0, r+0, b+0, b2+0, c+c2+0 }' "${TMP}/sel")
EOF

printf '%s\n' "${B}tổng kết${R}"
printf '  %-28s %s\n' "NEW (chưa có ở Mac):"     "${GRN}${TOT_NEW} fold${R}  ${DIM}~$(human "${TOT_NEW_B}")${R}"
printf '  %-28s %s\n' "STALE (server mới hơn):"  "${YEL}${TOT_STALE} fold${R}  ${DIM}~$(human "${TOT_STALE_B}") — chỉ pull khi thêm 'stale'${R}"
printf '  %-28s %s\n' "SAME (đã có):"            "${TOT_SAME} fold"
printf '  %-28s %s\n' "RUNNING (đang train):"    "${TOT_RUN} fold ${DIM}(chưa có test_metrics.json)${R}"
[ "${CKPT}" = "1" ] && printf '  %-28s %s\n' "best_model.pth:" "~$(human "${TOT_CK}")"
if [ "${TOT_STALE}" -gt 0 ]; then
    printf '  %s\n' "${DIM}STALE = cùng đường dẫn nhưng bản trên server mới hơn (thường là run cũ bị train lại)."
    printf '  %s\n' " 'stale' sẽ chuyển bản Mac cũ sang experiments/_replaced/<ts>/ rồi mới ghi — không xoá.${R}"
fi

# local-only run-dirs (no fold of this run exists on ANY server) — usually old runs
cat "${TMP}"/remote.* 2>/dev/null | awk -F'|' '{r=$1; sub("/fold_[0-9]+$","",r); print r}' \
    | sort -u > "${TMP}/remote_runs"
LOCAL_ONLY=""
while IFS= read -r r; do
    [ -z "${r}" ] && continue
    match_only "${r}" && LOCAL_ONLY="${LOCAL_ONLY}${r}"$'\n'
done <<< "$(awk -F'|' '$2=="DONE"{r=$1; sub("/fold_[0-9]+$","",r); print r}' "${TMP}/local" \
    | sort -u | comm -23 - "${TMP}/remote_runs")"
LOCAL_ONLY="${LOCAL_ONLY%$'\n'}"
if [ -n "${LOCAL_ONLY}" ]; then
    echo
    printf '%s\n' "${DIM}chỉ có ở Mac (không server nào có — thường là run cũ):${R}"
    printf '%s\n' "${LOCAL_ONLY}" | head -12 | sed "s/^/  ${DIM}/;s/$/${R}/"
    [ "$(printf '%s\n' "${LOCAL_ONLY}" | wc -l | tr -d ' ')" -gt 12 ] && printf '  %s\n' "${DIM}...${R}"
fi

if [ "${MODE}" != "pull" ]; then
    echo
    if [ "${TOT_NEW}" -gt 0 ] || [ "${TOT_STALE}" -gt 0 ]; then
        printf '%s\n' "${B}để tải về:${R}  bash run/pull_results.sh pull$([ "${TOT_STALE}" -gt 0 ] && echo ' stale')"
    else
        printf '%s\n' "${GRN}Mac đã có đủ mọi fold đã train xong trên server.${R}"
    fi
    exit 0
fi

# ---------------------------------------------------------------------------
# 4. Pull
# ---------------------------------------------------------------------------
echo
printf '%s\n' "${B}=== pull ===${R}"
[ "${DRY}" = "1" ] && printf '%s\n' "${YEL}DRY RUN — rsync sẽ chỉ liệt kê, không ghi${R}"

RSYNC_FLAGS="-az"
[ "${DRY}" = "1" ] && RSYNC_FLAGS="${RSYNC_FLAGS}n"
RSYNC_FLAGS="${RSYNC_FLAGS} -v"

# Filter order matters (first match wins): last_model.pth is banned outright
# (it is what filled the disk in the 2026-07-01 incident), checkpoints/ only
# rides along with CKPT=1, then the light artefacts, then everything else out.
build_filters() {
    FILTERS=(--exclude='last_model.pth')
    if [ "${CKPT}" = "1" ]; then
        FILTERS+=(--include='checkpoints/' --include='checkpoints/best_model.pth')
    else
        FILTERS+=(--exclude='checkpoints/')
    fi
    FILTERS+=(--include='*/' --include='*.json' --include='*.csv' --include='*.png'
              --include='*.yaml' --exclude='*')
}
build_filters

PULLED=0
FAILED=0
SELECT="NEW"
[ "${STALE}" = "1" ] && SELECT="NEW STALE"

while IFS='|' read -r cls host path sz ck; do
    case " ${SELECT} " in *" ${cls} "*) ;; *) continue ;; esac
    dir=""
    for entry in ${HOST_LIST}; do
        [ "${entry%%:*}" = "${host}" ] && dir="${entry#*:}"
    done
    [ -z "${dir}" ] && continue

    if [ "${cls}" = "STALE" ] && [ "${DRY}" != "1" ]; then
        mkdir -p "${BACKUP_ROOT}/$(dirname "${path}")"
        mv "${path}" "${BACKUP_ROOT}/${path}" 2>/dev/null \
            && printf '  %s\n' "${YEL}backup${R} ${path} -> ${BACKUP_ROOT}/${path}"
    fi

    [ "${DRY}" = "1" ] || mkdir -p "${path}"
    printf '  %s %s:%s\n' "${GRN}pull${R}" "${host}" "${path}"
    # shellcheck disable=SC2086  # RSYNC_FLAGS / SSH_OPTS must word-split
    # stderr is kept apart: the vast.ai login banner lands there and would
    # otherwise be printed as if it were transferred files. `< /dev/null` stops
    # rsync's ssh from swallowing the while-read loop's stdin (it would then
    # pull only the first fold).
    if rsync ${RSYNC_FLAGS} -e "ssh ${SSH_OPTS}" "${FILTERS[@]}" \
            "${host}:${dir}/${path}/" "${path}/" \
            < /dev/null > "${TMP}/rsync.out" 2>"${TMP}/rsync.err"; then
        PULLED=$((PULLED + 1))
        grep -vE '^[[:space:]]*$|^(sending|receiving|Transfer)|sent .*bytes|total size|speedup|^\./?$' \
            "${TMP}/rsync.out" | sed 's/^/      /' | head -12
    else
        FAILED=$((FAILED + 1))
        printf '  %s %s\n' "${YEL}FAIL${R}" "${host}:${path}"
        tail -5 "${TMP}/rsync.err" | sed 's/^/      /'
    fi
done < "${TMP}/sel"

# run-dir level files (aggregated.json / aggregated.md) for every touched run
awk -F'|' -v sel="${SELECT}" '
    { if (index(" " sel " ", " " $1 " ") == 0) next;
      run=$3; sub("/fold_[0-9]+$", "", run); key=$2 "|" run;
      if (!(key in seen)) { seen[key]=1; print key } }' "${TMP}/sel" \
| while IFS='|' read -r host run; do
    dir=""
    for entry in ${HOST_LIST}; do
        [ "${entry%%:*}" = "${host}" ] && dir="${entry#*:}"
    done
    [ -z "${dir}" ] && continue
    # shellcheck disable=SC2086
    rsync ${RSYNC_FLAGS} -e "ssh ${SSH_OPTS}" \
        --include='aggregated.json' --include='aggregated.md' --exclude='*' \
        "${host}:${dir}/${run}/" "${run}/" < /dev/null >/dev/null 2>&1
done

echo
printf '%s\n' "${B}xong${R}: ${GRN}${PULLED}${R} fold pulled, ${FAILED} lỗi${DRY:+}"
[ "${DRY}" = "1" ] && printf '%s\n' "${DIM}(dry run — chưa ghi gì)${R}"
[ -d "${BACKUP_ROOT}" ] && printf '%s\n' "${DIM}bản local cũ đã được chuyển vào ${BACKUP_ROOT}/ (không xoá)${R}"
[ "${FAILED}" -gt 0 ] && exit 1
exit 0
