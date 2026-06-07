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
# RUN ON THE CLUSTER LOGIN NODE — compute nodes have no internet, and this is
# plain unzip/copy work, not a GPU job. Download the bundle in a browser from
#   https://data.mendeley.com/datasets/zr7vgbcyr2/1
# rsync it up, then:
#
#   bash scripts/setup_pad_ufes_20.sh ~/zr7vgbcyr2-1.zip
#   # or, if you already unzipped it somewhere:
#   bash scripts/setup_pad_ufes_20.sh path/to/extracted_dir
#
# When it prints OK, run the preprocessing job:
#   bash slurm/submit.sh slurm/10_prepare_data.slurm
# ============================================================================
set -euo pipefail

SRC="${1:-}"
DEST_DIR="data/raw/pad_ufes_20"
IMG_DIR="${DEST_DIR}/images"

if [ -z "${SRC}" ] || [ ! -e "${SRC}" ]; then
    echo "ERROR: pass the Mendeley bundle zip or an already-extracted dir."
    echo "Usage: bash scripts/setup_pad_ufes_20.sh <zr7vgbcyr2-1.zip | extracted_dir>"
    exit 1
fi

WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

# 1. Get everything into a scratch tree (accept either a zip or a dir).
if [ -d "${SRC}" ]; then
    cp -r "${SRC}/." "${WORK}/"
else
    echo "[stage] unzipping outer bundle ..."
    unzip -q -o "${SRC}" -d "${WORK}"
fi

# 2. Extract any nested image archives (imgs_part_*.zip, images.zip, ...).
while IFS= read -r -d '' z; do
    echo "[stage] extracting $(basename "${z}") ..."
    unzip -q -o "${z}" -d "${WORK}"
done < <(find "${WORK}" -type f -name '*.zip' -print0)

# 3. Consolidate into the layout prepare_data.py expects.
mkdir -p "${IMG_DIR}"

META_SRC="$(find "${WORK}" -type f -iname 'metadata.csv' | head -n1)"
if [ -z "${META_SRC}" ]; then
    echo "ERROR: metadata.csv not found anywhere in the bundle."
    exit 1
fi
cp "${META_SRC}" "${DEST_DIR}/metadata.csv"
echo "[stage] metadata.csv -> ${DEST_DIR}/metadata.csv"

echo "[stage] collecting images -> ${IMG_DIR}/ ..."
find "${WORK}" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) \
    -exec cp -n {} "${IMG_DIR}/" \;

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

echo "[stage] OK. Next: bash slurm/submit.sh slurm/10_prepare_data.slurm"
