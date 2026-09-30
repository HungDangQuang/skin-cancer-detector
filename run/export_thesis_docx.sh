#!/usr/bin/env bash
# ============================================================================
# Export thesis/LUAN_VAN.md -> thesis/LUAN_VAN.docx (Word) with pandoc.
#
# Runs on the MAC (editing box), not the GPU server: it needs `pandoc` and
# nothing from .venv-linux. Install once with `brew install pandoc`.
#
# Usage:
#   bash run/export_thesis_docx.sh
#   bash run/export_thesis_docx.sh SRC=thesis/LUAN_VAN.md OUT=thesis/LUAN_VAN.docx
#   bash run/export_thesis_docx.sh REBUILD_REF=1      # regenerate the style template
#
# What it does, and WHY each step exists (all three were observed to matter):
#   1. Inserts a blank line before any ATX heading that lacks one. Pandoc's
#      markdown requires it (`blank_before_header`); GitHub's CommonMark does
#      not — so a heading can render fine on GitHub and be silently swallowed
#      into the previous paragraph here. Hit once at "# Chuong 5".
#   2. Rewrites `\tag{3.2}` -> `\qquad (3.2)` inside display math. Pandoc's
#      texmath does not implement \tag and DROPS the equation number with no
#      warning. All 24 display formulas in the thesis carry one, and
#      docs/QUY_DINH_TRINH_BAY_LUAN_VAN.md:68 requires formulas to be numbered
#      by chapter — so losing them would break a submission rule. (The body
#      does NOT cross-reference formula numbers; it refers to sections.)
#   3. Builds a reference.docx for the UIT hard numbers (Times New Roman 13,
#      line spacing 1.5, A4, margins 3.5/2/2.5/2.5 cm, headings 15/14/14pt in
#      TNR) by patching pandoc's own default template — no Word needed.
#
# It then asserts the output still contains every figure, table, heading and
# equation the source had, so a silent drop fails the run instead of shipping.
#
# Two deliberate deviations from reference/review-runner.md, declared here so
# they don't read as oversights:
#   - **No `start_log`.** Like progress.sh / pull_results.sh this is a Mac-side
#     helper that finishes in seconds and never runs over SSH, so a logs/
#     transcript per invocation is noise — the same rationale validate-pipeline
#     §3a gives when exempting the other Mac-side helpers.
#   - **Args parsed with a `case` block, not `for arg; do export "${arg?}"`.**
#     The CLI shape is still KEY=VALUE, but a typo (`OUTPUT=…`) fails loudly
#     instead of being exported and silently ignored.
#
# macOS-only: the template patching uses BSD `sed -i ''`, which GNU sed reads
# as a filename. Port that to `sed -i` if this ever needs to run on Linux.
# ============================================================================
source "$(dirname "$0")/common.sh"

# ---------------------------------------------------------------------------
# Args
for arg in "$@"; do
    case "${arg}" in
        SRC=*)         SRC="${arg#SRC=}" ;;
        OUT=*)         OUT="${arg#OUT=}" ;;
        REBUILD_REF=*) REBUILD_REF="${arg#REBUILD_REF=}" ;;
        *) echo "ERROR: unknown arg '${arg}' (expected KEY=VALUE)"; exit 2 ;;
    esac
done

SRC="${SRC:-thesis/LUAN_VAN.md}"
OUT="${OUT:-thesis/LUAN_VAN.docx}"
REBUILD_REF="${REBUILD_REF:-0}"

BUILD_DIR="${PROJECT_DIR}/thesis/_build"
REF_DOCX="${BUILD_DIR}/reference.docx"
PREP_MD="${BUILD_DIR}/$(basename "${SRC%.md}").prep.md"

if ! command -v pandoc >/dev/null 2>&1; then
    echo "ERROR: pandoc not found. Install it with:  brew install pandoc"
    exit 2
fi
if [ ! -f "${SRC}" ]; then
    echo "ERROR: source not found: ${SRC}"
    exit 2
fi

mkdir -p "${BUILD_DIR}"
echo "[export] pandoc:  $(pandoc --version | head -1)"
echo "[export] source:  ${SRC}"
echo "[export] output:  ${OUT}"

# ---------------------------------------------------------------------------
# Step 3 (first, so the template exists before the conversion): style template.
#
# Twips: 1 cm = 566.93 twips. Left 3.5cm=1984, right 2cm=1134, top/bottom
# 2.5cm=1417. Font size is in half-points, so 13pt = 26. Line spacing 1.5 is
# w:line=360 (240 twips = one single-spaced line) with lineRule="auto".
build_reference_docx() {
    local tmp
    tmp="$(mktemp -d "${BUILD_DIR}/ref.XXXXXX")"
    # shellcheck disable=SC2064
    trap "rm -rf '${tmp}'" RETURN

    pandoc -o "${tmp}/ref.docx" --print-default-data-file reference.docx
    ( cd "${tmp}" && unzip -q ref.docx -d unpacked )

    # pandoc pretty-prints styles.xml and wraps long attribute lists across
    # lines, so a line-oriented sed cannot see a whole <w:rFonts …> element.
    # Flatten to one line first — whitespace between XML tags is insignificant.
    local styles="${tmp}/unpacked/word/styles.xml"
    tr '\n' ' ' < "${styles}" | tr -s ' ' > "${styles}.flat"
    mv "${styles}.flat" "${styles}"

    # Body font + size (docDefaults applies to every style that doesn't override
    # it), then the heading styles, which DO override it: pandoc's default gives
    # them the theme's major font in accent blue at 20/16/14pt. §3 wants chapter
    # and section titles in the body typeface at 14-15pt, so force TNR, drop the
    # accent colour (inherit black) and bring 20pt -> 15pt, 16pt -> 14pt. The
    # rFonts/colour substitutions are global on purpose: every heading level and
    # the Title style carry the same three elements, and all of them should end
    # up in Times New Roman.
    sed -i '' \
        -e 's|<w:rFonts w:asciiTheme="minorHAnsi" w:eastAsiaTheme="minorEastAsia" w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi" />|<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman" />|g' \
        -e 's|<w:rFonts w:asciiTheme="majorHAnsi" w:eastAsiaTheme="majorEastAsia" w:hAnsiTheme="majorHAnsi" w:cstheme="majorBidi" />|<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman" />|g' \
        -e 's|<w:rFonts w:eastAsiaTheme="majorEastAsia" w:cstheme="majorBidi" />|<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman" />|g' \
        -e 's|<w:color w:val="0F4761" w:themeColor="accent1" w:themeShade="BF" />||g' \
        -e 's|<w:sz w:val="24" />|<w:sz w:val="26" />|g' \
        -e 's|<w:szCs w:val="24" />|<w:szCs w:val="26" />|g' \
        -e 's|<w:sz w:val="40" />|<w:sz w:val="30" />|g' \
        -e 's|<w:szCs w:val="40" />|<w:szCs w:val="30" />|g' \
        -e 's|<w:sz w:val="32" />|<w:sz w:val="28" />|g' \
        -e 's|<w:szCs w:val="32" />|<w:szCs w:val="28" />|g' \
        -e 's|<w:spacing w:after="200" />|<w:spacing w:after="120" w:line="360" w:lineRule="auto" />|g' \
        "${styles}"

    # A4 + UIT margins. The default template's sectPr carries no pgSz/pgMar,
    # so Word would fall back to its own locale default (Letter on a US build).
    sed -i '' \
        -e 's|<w:sectPr>|<w:sectPr><w:pgSz w:w="11906" w:h="16838" /><w:pgMar w:top="1417" w:right="1134" w:bottom="1417" w:left="1984" w:header="708" w:footer="708" w:gutter="0" />|' \
        "${tmp}/unpacked/word/document.xml"

    ( cd "${tmp}/unpacked" && zip -q -r -X "${REF_DOCX}" . )
    echo "[export] built style template: ${REF_DOCX}"
}

if [ "${REBUILD_REF}" = "1" ] || [ ! -f "${REF_DOCX}" ]; then
    rm -f "${REF_DOCX}"
    build_reference_docx
else
    echo "[export] reusing style template: ${REF_DOCX}  (REBUILD_REF=1 to regenerate)"
fi

# ---------------------------------------------------------------------------
# Steps 1 + 2: preprocess the markdown.
awk '
    NR > 1 && prev != "" && /^#{1,6} / { print "" }
    { print; prev = $0 }
' "${SRC}" \
| sed -E 's/[[:space:]]*\\tag\{([0-9]+\.[0-9]+)\}\$\$$/ \\qquad (\1)$$/' \
> "${PREP_MD}"

n_blank_fix="$(( $(grep -c '' "${PREP_MD}") - $(grep -c '' "${SRC}") ))"
n_tag_left="$(grep -c 'tag{' "${PREP_MD}" || true)"
echo "[export] preprocessed -> ${PREP_MD}  (blank-line fixes applied: ${n_blank_fix}, \\tag left: ${n_tag_left})"
if [ "${n_tag_left}" != "0" ]; then
    echo "ERROR: ${n_tag_left} \\tag{...} survived preprocessing — their numbers would be dropped."
    exit 1
fi

# ---------------------------------------------------------------------------
# Convert. --resource-path is relative to the SOURCE dir, because the figure
# links in LUAN_VAN.md are written relative to thesis/ (../report_phase_1/...).
src_dir="$(cd "$(dirname "${SRC}")" && pwd)"
pandoc "${PREP_MD}" \
    -o "${OUT}" \
    --reference-doc="${REF_DOCX}" \
    --resource-path="${src_dir}:${PROJECT_DIR}" \
    -f markdown+tex_math_dollars+pipe_tables

# ---------------------------------------------------------------------------
# Verify nothing was silently dropped. Pandoc exits 0 on every drop seen so far,
# so these counts are the only real gate.
#
# The `|| true` on every count is load-bearing, not defensive noise: common.sh
# sets `pipefail`, so a grep that matches nothing exits 1, the whole pipeline
# inherits it, and `set -e` would kill the script at the assignment — before it
# could print the FAIL line naming what went missing. A lost category has to
# report itself, not vanish into a silent non-zero exit.
count_in_docx() { unzip -p "${OUT}" word/document.xml | grep -o "$1" | wc -l | tr -d ' ' || true; }

md_figs="$(grep -c '^!\[' "${PREP_MD}" || true)"
md_tables="$(grep -c '^|---' "${PREP_MD}" || true)"
md_h1="$(grep -cE '^# ' "${PREP_MD}" || true)"
md_h2="$(grep -cE '^## ' "${PREP_MD}" || true)"
md_h3="$(grep -cE '^### ' "${PREP_MD}" || true)"
# Equations: one <m:oMath> per formula, display ones additionally wrapped in
# <m:oMathPara>. Display = lines opening with `$$`; inline = the remaining
# `$…$` pairs. This is the half of the gate that covers trap 2 (\tag): the
# preprocessing check only proves no \tag SURVIVED, not that the numbers landed.
md_eq_block="$(grep -c '^\$\$' "${PREP_MD}" || true)"
md_eq_inline="$(grep -v '^\$\$' "${PREP_MD}" | grep -o '\$[^$]\+\$' | wc -l | tr -d ' ' || true)"
md_eq=$(( md_eq_block + md_eq_inline ))

docx_figs="$(unzip -l "${OUT}" | grep -c 'word/media/' || true)"
docx_tables="$(count_in_docx '<w:tbl>')"
docx_h1="$(count_in_docx 'Heading1')"
docx_h2="$(count_in_docx 'Heading2')"
docx_h3="$(count_in_docx 'Heading3')"
docx_eq="$(count_in_docx '<m:oMath>')"
docx_eq_block="$(count_in_docx '<m:oMathPara>')"

fail=0
check() {  # name  expected  actual
    if [ "$2" = "$3" ]; then
        printf '[export]   OK   %-22s %s\n' "$1" "$3"
    else
        printf '[export]   FAIL %-22s expected %s, got %s\n' "$1" "$2" "$3"
        fail=1
    fi
}
echo "[export] fidelity check (markdown -> docx):"
check "figures"          "${md_figs}"   "${docx_figs}"
check "tables"           "${md_tables}" "${docx_tables}"
check "headings level 1" "${md_h1}"     "${docx_h1}"
check "headings level 2" "${md_h2}"     "${docx_h2}"
check "headings level 3" "${md_h3}"     "${docx_h3}"
check "equations"        "${md_eq}"     "${docx_eq}"
check "display equations" "${md_eq_block}" "${docx_eq_block}"

if [ "${fail}" != "0" ]; then
    echo "ERROR: the .docx lost content — do NOT ship it. Inspect ${PREP_MD}."
    exit 1
fi

# `du -h` reports blocks allocated, not bytes — it read 3.0M for a 2.3M file.
echo "[export] done: ${OUT}  ($(ls -lh "${OUT}" | awk '{print $5}'))"
echo "[export] still to do by hand in Word (pandoc cannot do these from markdown):"
echo "[export]   - replace the hand-written MUC LUC with a real TOC field (References > Table of Contents)"
echo "[export]   - insert page numbers, bottom-centre"
echo "[export]   - header: chapter name, TNR 11, left-aligned"
