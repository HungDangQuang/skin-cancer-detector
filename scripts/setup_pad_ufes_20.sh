#!/usr/bin/env bash
# ============================================================================
# Stage PAD-UFES-20 raw data into the exact layout scripts/prepare_data.py wants.
#
# WHY: process_pad_ufes_20() (src/data/preprocessing.py) reads
#        data/raw/pad_ufes_20/metadata.csv     (needs cols: img_id, diagnostic)
#        data/raw/pad_ufes_20/images/<img_id>.png
#      The Mendeley "Download all" bundle (zr7vgbcyr2 v1) ships the images as
#      nested imgs_part_*.zip archives plus metadata.csv, and the exact nesting
#      varies between the Mendeley bundle and Kaggle mirrors. This script
#      extracts and CONSOLIDATES whatever it finds into the layout above, so it
#      is robust to those layout differences instead of assuming one.
#
# SPACE-LEAN: the bundle is ~3-4 GB and the cluster volume is tight. The work
# dir is created INSIDE the destination (same filesystem), so files are MOVED
# into place (instant, no extra space) instead of copied via /tmp; and each
# nested archive is deleted right after it is extracted. The only lingering 2x
# is the source zip itself + its extracted contents during `unzip`. Pass
# --rm-zip to delete the source zip once staging succeeds (reclaims ~3 GB
# before the prepare job runs); never deletes it on failure.
#
# RUN ON THE CLUSTER LOGIN NODE, FROM THE REPO ROOT — compute nodes have no
# internet, and this is plain unzip/move work, not a GPU job.
#
#   bash scripts/setup_pad_ufes_20.sh data/raw/archive.zip
#   bash scripts/setup_pad_ufes_20.sh data/raw/archive.zip --rm-zip   # tight on space
#   bash scripts/setup_pad_ufes_20.sh path/to/extracted_dir           # already unzipped
#
# When it prints OK, run the preprocessing job:
#   bash slurm/submit.sh slurm/10_prepare_data.slurm
# ============================================================================
set -euo pipefail

SRC="${1:-}"
RM_ZIP="${2:-}"
DEST_DIR="data/raw/pad_ufes_20"
IMG_DIR="${DEST_DIR}/images"

if [ -z "${SRC}" ] || [ ! -e "${SRC}" ]; then
    echo "ERROR: pass the bundle zip or an already-extracted dir."
    echo "Usage: bash scripts/setup_pad_ufes_20.sh <archive.zip | extracted_dir> [--rm-zip]"
    exit 1
fi

mkdir -p "${IMG_DIR}"

# Work dir INSIDE the destination → same filesystem as IMG_DIR, so `mv` below is
# a rename (instant, zero extra bytes). mktemp's default /tmp is often a
# different fs, which silently turns every move back into a full copy.
WORK="$(mktemp -d "${DEST_DIR}/.staging.XXXXXX")"
trap 'rm -rf "${WORK}"' EXIT

# 1. Get everything into the scratch tree (accept either a zip or a dir).
if [ -d "${SRC}" ]; then
    # Dir input: copy so we never mutate the user's own extracted folder.
    cp -r "${SRC}/." "${WORK}/"
else
    echo "[stage] unzipping outer bundle ..."
    unzip -q -o "${SRC}" -d "${WORK}"
fi

# 2. Extract nested image archives, deleting each one right after to free space.
while IFS= read -r -d '' z; do
    echo "[stage] extracting $(basename "${z}") ..."
    unzip -q -o "${z}" -d "${WORK}"
    rm -f "${z}"
done < <(find "${WORK}" -type f -name '*.zip' -print0)

# 3. Consolidate into the layout prepare_data.py expects (MOVE, same fs).
META_SRC="$(find "${WORK}" -type f -iname 'metadata.csv' | head -n1)"
if [ -z "${META_SRC}" ]; then
    echo "ERROR: metadata.csv not found anywhere in the bundle."
    exit 1
fi
mv -f "${META_SRC}" "${DEST_DIR}/metadata.csv"
echo "[stage] metadata.csv -> ${DEST_DIR}/metadata.csv"

echo "[stage] moving images -> ${IMG_DIR}/ ..."
find "${WORK}" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) \
    -exec mv -f -t "${IMG_DIR}/" {} +

# 4. Verify against what process_pad_ufes_20() actually requires.
HEADER="$(head -n1 "${DEST_DIR}/metadata.csv")"
case "${HEADER}" in *img_id*) ;; *)
    echo "WARN: 'img_id' column not found in metadata.csv header:"; echo "      ${HEADER}";;
esac
case "${HEADER}" in *diagnostic*) ;; *)
    echo "WARN: 'diagnostic' column not found in metadata.csv header:"; echo "      ${HEADER}";;
esac

N_IMG="$(find "${IMG_DIR}" -type f | wc -l | tr -d ' ')"
N_META="$(( $(wc -l < "${DEST_DIR}/metadata.csv") - 1 ))"
echo "[stage] images: ${N_IMG}   metadata rows: ${N_META}   (PAD-UFES-20 ships 2298 images)"

if [ "${N_IMG}" -eq 0 ]; then
    echo "ERROR: no images were staged — inspect the bundle contents."
    exit 1
fi

# 5. Optionally drop the source zip to reclaim space before the prepare job.
#    Only on success, only for a zip input, only when explicitly requested.
if [ "${RM_ZIP}" = "--rm-zip" ] && [ -f "${SRC}" ]; then
    rm -f "${SRC}"
    echo "[stage] removed source zip ${SRC}"
fi

echo "[stage] OK. Next: bash slurm/submit.sh slurm/10_prepare_data.slurm"
