#!/usr/bin/env bash
# ============================================================================
# run/progress_all.sh — run run/progress.sh on EVERY training box and print one
# combined report. Meant to be run from the Mac.
#
# It pipes run/progress.sh into each host over stdin
# (`ssh host 'bash -s' < run/progress.sh`), so the servers never need a
# `git pull` to get the newest monitor, and nothing is written on them.
#
# Usage:
#   bash run/progress_all.sh                       # both vast.ai boxes
#   bash run/progress_all.sh WATCH=30              # refresh every 30s
#   bash run/progress_all.sh HOSTS="vast"          # just one
#   bash run/progress_all.sh HOSTS="vast vastnew islab"   # add a box
#   bash run/progress_all.sh RUNS=0                # skip the run-dir summary
#
# Args (KEY=VALUE, or env vars):
#   HOSTS       space-separated ssh targets, each optionally "host:/repo/path"
#               (default "vast vastnew" — the aliases in ~/.ssh/config)
#   REMOTE_DIR  repo path used for hosts that don't carry their own ":path"
#               (default /workspace/skin-cancer-detector — the vast.ai layout)
#   WATCH       seconds between refreshes (default 0 = one-shot)
#   RUNS        1|0, forwarded to progress.sh (run-dir fold summary)
#   SSH_OPTS    extra ssh options (default "-o BatchMode=yes -o ConnectTimeout=10")
#
# Adding a third box = add its alias to ~/.ssh/config and to HOSTS. Nothing in
# this script is vast-specific except the default HOSTS/REMOTE_DIR values.
#
# Like run/progress.sh this is a READ-ONLY reporter and deliberately does NOT
# source run/common.sh: it runs on the Mac, where there is no ./.venv-linux and
# no GPU, and it must not create a logs/ entry per refresh. See run/README.md.
# ============================================================================
set -uo pipefail

for arg in "$@"; do
    case "${arg}" in
        *=*)       export "${arg?}" ;;
        -h|--help) sed -n '2,28p' "$0"; exit 0 ;;
        *)         echo "[progress-all] ignoring unknown arg: ${arg}" >&2 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_SCRIPT="${SCRIPT_DIR}/progress.sh"
[ -f "${LOCAL_SCRIPT}" ] || { echo "ERROR: ${LOCAL_SCRIPT} not found" >&2; exit 2; }

HOSTS="${HOSTS:-vast vastnew}"
REMOTE_DIR="${REMOTE_DIR:-/workspace/skin-cancer-detector}"
WATCH="${WATCH:-0}"
RUNS="${RUNS:-1}"
SSH_OPTS="${SSH_OPTS:--o BatchMode=yes -o ConnectTimeout=10}"

if [ -t 1 ]; then COLOR="${COLOR:-1}"; else COLOR="${COLOR:-0}"; fi

report_once() {
    local entry host dir err rc
    for entry in ${HOSTS}; do
        case "${entry}" in
            *:*) host="${entry%%:*}"; dir="${entry#*:}" ;;
            *)   host="${entry}";     dir="${REMOTE_DIR}" ;;
        esac

        err="$(mktemp -t progress_all.XXXXXX)"
        # shellcheck disable=SC2086  # SSH_OPTS must word-split into separate flags
        ssh -T ${SSH_OPTS} "${host}" \
            "PROJECT_DIR='${dir}' LABEL='${host}' COLOR='${COLOR}' RUNS='${RUNS}' WATCH=0 bash -s" \
            < "${LOCAL_SCRIPT}" 2>"${err}"
        rc=$?
        if [ "${rc}" -ne 0 ]; then
            echo "=== ${host}: UNREACHABLE or script failed (ssh exit ${rc})"
            # The vast.ai login banner also lands on stderr; only shown on failure.
            sed 's/^/    /' "${err}"
        fi
        rm -f "${err}"
        echo
    done
}

if [ "${WATCH}" != "0" ]; then
    while :; do
        clear 2>/dev/null || printf '\033[H\033[2J'
        report_once
        printf 'refresh every %ss — Ctrl-C to stop\n' "${WATCH}"
        sleep "${WATCH}"
    done
else
    report_once
fi
