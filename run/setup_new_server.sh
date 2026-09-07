#!/usr/bin/env bash
# ============================================================================
# Bootstrap a NEWLY-RENTED GPU server to train the REMAINING KD students, in
# parallel with (and NOT duplicating) the current server.
#
# Run from the repo root AFTER cloning it, e.g.:
#     git clone https://github.com/HungDangQuang/skin-cancer-detector.git
#     cd skin-cancer-detector && git checkout apply-metadata-for-training
#     bash run/setup_new_server.sh                      # venv + deps only
#     SRC="root@<CUR_IP>:/workspace/skin-cancer-detector" PORT=<p> bash run/setup_new_server.sh
#
# What it does:
#   [1] builds the venv + installs deps (delegates to run/setup_env.sh)
#   [2] if SRC is given, rsyncs from the CURRENT server the two things a KD
#       student run needs that are NOT in git:
#         - data/processed/  + data/splits/   (the resized images + fold CSVs)
#         - experiments/runs/teacher/<T>/      (teacher checkpoints for KD)
#
# WHY copy (not regenerate) data/splits: the held-out test set + fold assignment
# must be BYTE-IDENTICAL to the other runs, or Q2 cross-teacher numbers are not
# comparable. Always copy splits from the source; never re-run prepare_data here.
#
# Env:
#   SRC       rsync source "user@host:/abs/repo/path" of the CURRENT server.
#             If unset -> only the venv is built and the fetch commands are printed.
#   PORT      ssh port of SRC (default 22)
#   TEACHERS  teacher checkpoints to pull (default "convnextv2_base maxvit_base"
#             — the teachers the NEW server will distill from; efficientnetv2_m is
#             already fully trained so it is not needed here)
# ============================================================================
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> [1/2] venv + deps (run/setup_env.sh)"
bash run/setup_env.sh

PORT="${PORT:-22}"
TEACHERS="${TEACHERS:-convnextv2_base maxvit_base}"

if [ -z "${SRC:-}" ]; then
    cat <<EOF

==> venv ready. SRC not set — fetch data + teachers from the CURRENT server with:

    SRC="root@<CUR_SERVER_IP>:/workspace/skin-cancer-detector" PORT=<ssh_port> \\
        bash run/setup_new_server.sh

(That re-runs this script; step [1] is a fast no-op since the venv already exists.)
EOF
    exit 0
fi

RSH="ssh -p ${PORT} -o StrictHostKeyChecking=accept-new"
echo "==> [2/2] fetching data + teacher checkpoints from ${SRC} (port ${PORT})"
mkdir -p data/processed data/splits experiments/runs/teacher

echo "  -> data/processed"
rsync -avz --info=progress2 -e "${RSH}" "${SRC}/data/processed/" data/processed/
echo "  -> data/splits (must match the other runs exactly)"
rsync -avz --info=progress2 -e "${RSH}" "${SRC}/data/splits/"    data/splits/
for T in ${TEACHERS}; do
    echo "  -> teacher ${T}"
    rsync -avz --info=progress2 -e "${RSH}" \
        "${SRC}/experiments/runs/teacher/${T}/" "experiments/runs/teacher/${T}/"
done

echo
echo "==> Verify before training:"
echo "    ls data/splits/                                            # fold_*/{train,val}_split.csv + test_split.csv"
echo "    find experiments/runs/teacher -name best_model.pth | wc -l # expect 5 per pulled teacher"
echo "    head -1 data/splits/fold_0/train_split.csv                 # confirm image_path points to data/processed (relative)"
echo
echo "Then start the NON-overlapping Phase-2 training (see the launch command your assistant gave)."
