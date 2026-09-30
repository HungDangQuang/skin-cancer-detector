#!/usr/bin/env python3
"""Mechanical pre-pass for a thesis section review (stdlib only, runs on the Mac).

Usage:
    python3 .claude/skills/review-thesis/scripts/section_audit.py 4.3
    python3 ... "3.2.8" --file thesis/LUAN_VAN.md
    python3 ... "MỞ ĐẦU"
    python3 ... 4.3 --numbers-context   # also grep the rest of the doc for each number
    python3 ... --numbering             # whole-document cross-reference + numbering sweep

It does NOT judge the writing. It gathers the evidence the six review criteria
need — paragraph/bullet structure, English terms vs the glossary, table/figure
ids vs the two indexes, every numeric literal that must be verified against a
real artifact, and (criteria 4 + 5) whether every "Mục/Chương/Phụ lục/Bảng/Hình"
reference resolves to something that exists and whether the numbering is dense,
unique and correctly nested. The verdict is written by the reviewer, from this
evidence: a reference that RESOLVES may still point at the wrong content.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

GLOSSARY_HEADING = "DANH MỤC THUẬT NGỮ"
TABLE_INDEX_HEADING = "DANH MỤC BẢNG"
FIGURE_INDEX_HEADING = "DANH MỤC HÌNH"

# Pure-ASCII Vietnamese words (no diacritics) that must not be mistaken for
# English technical terms. Most Vietnamese words carry diacritics and are
# filtered out by the ASCII test itself; these are the ones that slip through.
VI_ASCII_STOPWORDS = {
    "cho", "con", "khi", "hay", "trong", "ra", "sau", "do", "theo", "da", "hai",
    "ba", "ta", "nhau", "ngay", "tay", "so", "cao", "sai", "mang", "may", "mau",
    "sang", "mo", "van", "thu", "sinh", "an", "am", "em", "no", "vi", "ai",
    "ho", "tren", "ban", "canh", "hang", "cham", "tang", "giam", "bao", "dang",
    "phai", "trai", "toan", "dan", "ong", "cac", "cung", "xanh", "danh",
    "song", "suy", "thay", "che", "soi", "sao", "ghi", "qua", "dung", "thang",
    "thao", "tham", "chi", "tin", "duy", "coi", "tra", "quan", "quy", "trung",
    "hao", "tao", "cai", "goi", "loi", "noi", "moi", "nang", "vang", "sam",
    "ranh", "manh", "mach", "hoan", "toi", "boi", "day", "nay", "gay", "may",
    "tay", "hay", "cay", "xay", "chay", "chan", "than", "gian", "khoang",
}

# Tokens that are neither Vietnamese nor thesis terminology worth indexing.
NOISE_TOKENS = {
    "http", "https", "www", "com", "org", "net", "html", "md", "png", "svg",
    "csv", "json", "yaml", "sh", "py", "pth", "pte", "et", "al", "vs", "eg",
    "ie", "ok", "min", "max", "std", "mean", "id", "ids", "fold", "folds",
}

WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_+][A-Za-z0-9]+)*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
# Vietnamese decimal comma (0,385) and thousands dot are both used in this thesis.
NUMBER_RE = re.compile(r"(?<![\w.,])[-+±]?\d+(?:[.,]\d+)*\s*(?:%|×|x|GFLOPs|MB|ms|M\b)?")
# A reference always carries the chapter prefix ("Bảng 4.5", "Hình A.2"), so the
# id must contain a dot. Without that, "một mô hình 453 MB" reads as "Hình 453".
# "Hình" stays capital-only for the same reason ("mô hình", "cấu hình").
TABLE_REF_RE = re.compile(r"[Bb]ảng\s+([A-Z]?\d+(?:\.\d+)+)")
FIGURE_REF_RE = re.compile(r"Hình\s+([A-Z]?\d+(?:\.\d+)+)")
# Caption delimiters differ by kind in this thesis: tables are bold
# (**Bảng 3.1 — …**), figures italic (*Hình 3.1 — …*) under the embedded image.
# Định dạng chú thích theo Phụ lục 2 §4: bảng là `**Bảng 3.2**. Tiêu đề` (dấu chấm NGOÀI
# chữ đậm), hình là `**Hình 4.5.** Tiêu đề` (dấu chấm TRONG chữ đậm). Nhóm bắt: 1 = dấu
# phân cách, 2 = số hiệu, 3 = phần tiêu đề — thứ tự này được dùng ở cuối tệp.
CAPTION_TABLE_RE = re.compile(r"^(\*{2})Bảng\s+([A-Z]?\d+(?:\.\d+)*)\1\.\s+(.+)$")
CAPTION_FIGURE_RE = re.compile(r"^(\*{2})Hình\s+([A-Z]?\d+(?:\.\d+)*)\.\1\s+(.+)$")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
MATH_SPAN_RE = re.compile(r"\$[^$]*\$")

# Connectives that bind one paragraph to the previous one. Used only as a signal
# for criterion 3 (flow vs. bullet dump), never as a rule.
CONNECTIVES = (
    "tuy nhiên", "nhưng", "do đó", "vì vậy", "vì thế", "bởi vậy", "ngược lại",
    "mặt khác", "hơn nữa", "ngoài ra", "cụ thể", "chi tiết hơn", "nói cách khác",
    "điều này", "kết quả là", "từ đó", "trước hết", "tiếp theo", "cuối cùng",
    "đầu tiên", "thứ hai", "thứ ba", "chính vì", "khác biệt", "đáng chú ý",
    "bảng trên", "bảng dưới", "hình trên", "hình dưới", "như đã", "trở lại",
    "phần trên", "mục trên", "để trả lời", "câu hỏi", "lý do",
)


def caption_key(text: str) -> str:
    """Comparable form of a caption: no punctuation, no trailing source note."""
    t = re.split(r"T[ệe]p ngu[ồo]n", text)[0]
    t = norm(t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return t.strip()


def caption_drift(caption: str, index_text: str) -> tuple[float, list[str]]:
    """How far a caption has drifted from its index line.

    -> (coverage of the shorter wording by the longer, words only the index has).
    A caption may legitimately say MORE than the index line; the failure that
    matters is the index promising a word the caption never uses.
    """
    a = [w for w in caption_key(caption).split() if len(w) > 1]
    b = [w for w in caption_key(index_text).split() if len(w) > 1]
    if not a or not b:
        return 0.0, b
    sa, sb = set(a), set(b)
    missing = [w for w in b if w not in sa]
    return len(sb & sa) / len(sb), missing


def norm(s: str) -> str:
    """Casefold + strip accents, for tolerant matching."""
    s = unicodedata.normalize("NFD", s.casefold())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# --------------------------------------------------------------------------- #
# Document parsing
# --------------------------------------------------------------------------- #
def parse_headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """-> [(line_index, level, text)] skipping fenced code blocks."""
    out, in_fence = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            out.append((i, len(m.group(1)), m.group(2)))
    return out


def find_section(headings, lines, key: str) -> tuple[int, int, str]:
    """Resolve '4.3' / 'MỞ ĐẦU' / a heading substring to (start, end, title)."""
    nkey = norm(key.strip())
    is_numeric = re.fullmatch(r"\d+(\.\d+)*", key.strip()) is not None
    hits = []
    for idx, (ln, level, text) in enumerate(headings):
        ntext = norm(text)
        if is_numeric:
            m = re.match(r"(\d+(?:\.\d+)*)", text.strip())
            if m and m.group(1) == key.strip():
                hits.append(idx)
        elif nkey in ntext:
            hits.append(idx)
    if not hits:
        sys.exit(f"Không tìm thấy phần khớp với {key!r}. Dùng --list để xem các mục.")
    if len(hits) > 1:
        titles = "\n".join(f"  - dòng {headings[h][0]+1}: {headings[h][2]}" for h in hits)
        sys.exit(f"{key!r} khớp nhiều mục:\n{titles}\nHãy nêu cụ thể hơn.")
    idx = hits[0]
    start, level, title = headings[idx]
    end = len(lines)
    for ln, lvl, _ in headings[idx + 1:]:
        if lvl <= level:
            end = ln
            break
    return start, end, title


def slice_index_section(lines, headings, heading_key: str) -> list[str]:
    for idx, (ln, level, text) in enumerate(headings):
        if heading_key in text:
            end = len(lines)
            for ln2, lvl2, _ in headings[idx + 1:]:
                if lvl2 <= level:
                    end = ln2
                    break
            return lines[ln:end]
    return []


def table_rows(block: list[str]) -> list[list[str]]:
    rows = []
    for line in block:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):  # separator row
            continue
        rows.append(cells)
    return rows


def build_glossary(lines, headings) -> dict[str, str]:
    """-> {normalised term or alias: Vietnamese rendering}."""
    block = slice_index_section(lines, headings, GLOSSARY_HEADING)
    terms: dict[str, str] = {}
    for cells in table_rows(block):
        if len(cells) < 2 or norm(cells[0]).startswith("thuat ngu"):
            continue
        vi = cells[1]
        raw = cells[0]
        variants = [raw]
        # "Basal Cell Carcinoma (BCC)" -> also "BCC"
        for abbr in re.findall(r"\(([^)]+)\)", raw):
            variants.append(abbr)
        variants.append(re.sub(r"\([^)]*\)", "", raw))
        # "Dermoscopy / dermoscopic image" -> both halves
        for v in list(variants):
            if "/" in v:
                variants.extend(v.split("/"))
        for v in variants:
            v = v.strip().strip("*")
            if v:
                terms[norm(v)] = vi
    return terms


def build_index(lines, headings, heading_key: str) -> dict[str, str]:
    block = slice_index_section(lines, headings, heading_key)
    out = {}
    for cells in table_rows(block):
        if len(cells) < 2:
            continue
        key = cells[0].strip()
        if re.fullmatch(r"[A-Z]?\d+(\.\d+)*", key):
            out[key] = cells[1].strip()
    return out


# --------------------------------------------------------------------------- #
# Per-criterion evidence
# --------------------------------------------------------------------------- #
def classify_blocks(body: list[str], start_line: int):
    """Split the section into typed blocks: prose / bullets / table / code / caption."""
    blocks, cur, cur_kind, in_fence = [], [], None, False

    def flush():
        nonlocal cur, cur_kind
        if cur:
            blocks.append((cur_kind, cur[0][0], [t for _, t in cur]))
        cur, cur_kind = [], None

    for offset, line in enumerate(body):
        ln = start_line + offset + 1
        s = line.strip()
        if s.startswith("```"):
            if not in_fence:
                flush()
            in_fence = not in_fence
            cur_kind = "code"
            cur.append((ln, line))
            if not in_fence:
                flush()
            continue
        if in_fence:
            cur.append((ln, line))
            continue
        if not s:
            flush()
            continue
        if HEADING_RE.match(line):
            flush()
            blocks.append(("heading", ln, [line]))
            continue
        if s.startswith("|"):
            kind = "table"
        elif re.match(r"^([-*+]|\d+[.)])\s", s):
            kind = "bullet"
        elif CAPTION_TABLE_RE.match(s) or CAPTION_FIGURE_RE.match(s):
            kind = "caption"
        elif set(s) <= set("-*_ ") and len(s) >= 3:
            kind = "rule"
        else:
            kind = "prose"
        if kind != cur_kind:
            flush()
            cur_kind = kind
        cur.append((ln, line))
    flush()
    return blocks


def _valid_tokens(text: str):
    """WORD_RE matches whose neighbours are not letters.

    Without this, a Vietnamese word with diacritics ("phí", "Phần") donates an
    ASCII prefix ("ph", "Ph") that looks like an English token.
    """
    out = []
    for m in WORD_RE.finditer(text):
        before = text[m.start() - 1] if m.start() else ""
        after = text[m.end()] if m.end() < len(text) else ""
        if before.isalpha() or after.isalpha():
            continue
        out.append((m.start(), m.end(), m.group(0)))
    return out


def extract_terms(body: list[str], glossary: dict[str, str]):
    """-> (known, unknown) lists of [term, count, line_offset, vi_or_None]."""
    known: dict[str, list] = {}
    unknown: dict[str, list] = {}
    in_fence = False
    for offset, line in enumerate(body):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Code spans are identifiers and $…$ is math — neither is terminology.
        text = MATH_SPAN_RE.sub(" ", CODE_SPAN_RE.sub(" ", line))
        toks = _valid_tokens(text)

        # An English phrase = consecutive valid tokens joined by one space/-//.
        # A lone lowercase ASCII word is usually a diacritic-free Vietnamese one
        # ("trung", "quan", "chi") and is not flagged on its own.
        adjacent = [False] * len(toks)
        for i in range(len(toks) - 1):
            if re.fullmatch(r"[ \-/]", text[toks[i][1]:toks[i + 1][0]]):
                adjacent[i] = adjacent[i + 1] = True

        # Longest-first n-gram match against the glossary.
        consumed = [False] * len(toks)
        for n in (4, 3, 2):
            for i in range(len(toks) - n + 1):
                if any(consumed[i:i + n]) or not all(adjacent[i:i + n - 1]):
                    continue
                phrase = text[toks[i][0]:toks[i + n - 1][1]]
                key = norm(phrase)
                hit = glossary.get(key) or glossary.get(key.rstrip("s"))
                if hit is not None:
                    for k in range(i, i + n):
                        consumed[k] = True
                    e = known.setdefault(phrase, [phrase, 0, offset, hit])
                    e[1] += 1

        for i, (a, b, tok) in enumerate(toks):
            if consumed[i]:
                continue
            low = tok.lower()
            if low in VI_ASCII_STOPWORDS or low in NOISE_TOKENS:
                continue
            hit = glossary.get(norm(tok)) or glossary.get(norm(tok).rstrip("s"))
            if hit is not None:
                e = known.setdefault(tok, [tok, 0, offset, hit])
                e[1] += 1
                continue
            technical = (
                (tok.isupper() and len(tok) >= 2)
                or any(c.isdigit() for c in tok)
                or ("-" in tok or "_" in tok)
                # A capitalized word only counts if it is too long to be a
                # Vietnamese word ("Quy", "Tham").
                or (tok[0].isupper() and not tok.isupper() and len(tok) >= 4)
                or (len(tok) >= 3 and tok.islower() and adjacent[i])
            )
            if not technical:
                continue
            e = unknown.setdefault(tok, [tok, 0, offset, None])
            e[1] += 1
    return (
        sorted(known.values(), key=lambda e: -e[1]),
        sorted(unknown.values(), key=lambda e: -e[1]),
    )


# --------------------------------------------------------------------------- #
# Cross-references and numbering (criteria 4 + 5)
# --------------------------------------------------------------------------- #
SEC_CHAPTER_RE = re.compile(r"^[Cc]hương\s+(\d+)\b")   # `Chương 4. …` theo Phụ lục 2 §1
SEC_APPENDIX_RE = re.compile(r"^PHỤ\s+LỤC\s+([A-Z])\b")
SEC_APP_SUB_RE = re.compile(r"^([A-Z]\.\d+(?:\.\d+)*)\s")
SEC_NUM_RE = re.compile(r"^(\d+(?:\.\d+)*)\s")

REF_SECTION_RE = re.compile(r"\b[Mm]ục\s+([A-Z]?\d+(?:\.\d+)*)")
REF_CHAPTER_RE = re.compile(r"\b[Cc]hương\s+(\d+)")
REF_APPENDIX_RE = re.compile(r"\b[Pp]hụ\s+lục\s+([A-Z](?:\.\d+)*)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
TOC_ENTRY_RE = re.compile(r"^\s*-\s*\[(.+?)\]\(#([^)]+)\)\s*$")


def section_id(title: str) -> str | None:
    """'Chương 4. …'->'4'; '4.3 …'->'4.3'; 'PHỤ LỤC B — …'->'B'; 'B.2 …'->'B.2'."""
    t = title.strip()
    for rx in (SEC_CHAPTER_RE, SEC_APPENDIX_RE, SEC_APP_SUB_RE, SEC_NUM_RE):
        m = rx.match(t)
        if m:
            return m.group(1)
    return None


def id_parts(sid: str) -> list[str]:
    return sid.split(".")


def id_key(sid: str):
    """Natural order: 3.2 before 3.10, letters after digits."""
    return [(0, int(p), "") if p.isdigit() else (1, 0, p) for p in id_parts(sid)]


def is_ancestor(anc: str, sid: str) -> bool:
    return sid == anc or sid.startswith(anc + ".")


def slugify(title: str) -> str:
    """GitHub heading anchor: lowercase, drop punctuation, spaces -> hyphens."""
    s = unicodedata.normalize("NFC", title).casefold()
    s = "".join(c for c in s if c.isalnum() or c in " -_")
    return s.strip().replace(" ", "-")


def build_sections(headings):
    """-> (by_id {id: [(line, level, title)]}, ordered [(line, level, title, id)])."""
    by_id: dict[str, list] = {}
    ordered = []
    for ln, level, text in headings:
        sid = section_id(text)
        ordered.append((ln, level, text, sid))
        if sid:
            by_id.setdefault(sid, []).append((ln, level, text))
    return by_id, ordered


def owner_section(ordered, line_no: int) -> str | None:
    """Deepest numbered heading that contains the 1-based line_no."""
    owner = None
    for ln, _level, _text, sid in ordered:
        if ln + 1 > line_no:
            break
        if sid:
            owner = sid
    return owner


def scan_captions(lines):
    """-> {'Bảng'|'Hình': {id: (line, caption_text)}} plus duplicates list."""
    caps = {"Bảng": {}, "Hình": {}}
    dups = []
    in_fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        s = line.strip()
        for kind, rx in (("Bảng", CAPTION_TABLE_RE), ("Hình", CAPTION_FIGURE_RE)):
            m = rx.match(s)
            if m:
                cid, text = m.group(2), m.group(3).strip()
                if cid in caps[kind]:
                    dups.append((kind, cid, caps[kind][cid][0], i + 1))
                else:
                    caps[kind][cid] = (i + 1, text)
    return caps, dups


def scan_refs(lines, lo: int, hi: int, caps):
    """Every cross-reference on lines [lo, hi) (0-based). -> [(line, kind, target)]."""
    out = []
    in_fence = False
    for i in range(lo, hi):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        ln = i + 1
        is_caption = bool(CAPTION_TABLE_RE.match(line.strip())
                          or CAPTION_FIGURE_RE.match(line.strip()))
        for rx, kind in ((REF_SECTION_RE, "Mục"), (REF_CHAPTER_RE, "Chương"),
                         (REF_APPENDIX_RE, "Phụ lục")):
            for m in rx.finditer(line):
                out.append((ln, kind, m.group(1)))
        if not is_caption:
            for rx, kind in ((TABLE_REF_RE, "Bảng"), (FIGURE_REF_RE, "Hình")):
                for m in rx.finditer(line):
                    out.append((ln, kind, m.group(1)))
        for m in IMG_RE.finditer(line):
            out.append((ln, "ảnh", m.group(1)))
    return out


def resolve_ref(kind: str, target: str, by_id, caps, doc_dir: Path):
    """-> (ok: bool, note: str). note describes WHERE it lands, for the human."""
    if kind in ("Mục", "Chương", "Phụ lục"):
        hits = by_id.get(target)
        if hits:
            ln, _lvl, title = hits[0]
            return True, f"→ “{title[:62]}” (dòng {ln + 1})"
        parent = target.rsplit(".", 1)[0] if "." in target else target
        near = sorted((k for k in by_id if k != target and is_ancestor(parent, k)),
                      key=id_key)
        tip = f" — mục có thật gần nhất: {', '.join(near[-3:])}" if near else ""
        return False, f"KHÔNG TỒN TẠI mục {target}{tip}"
    if kind in ("Bảng", "Hình"):
        hit = caps[kind].get(target)
        if hit:
            return True, f"→ caption ở dòng {hit[0]}: “{hit[1][:52]}”"
        return False, f"KHÔNG CÓ caption **{kind} {target} — …** ở bất kỳ đâu"
    # kind == "ảnh": path is relative to the markdown file. A remote or in-page
    # target is not a file this script can check.
    if re.match(r"^(https?:|data:|#)", target):
        return True, "(đường dẫn ngoài — không kiểm được bằng script)"
    p = (doc_dir / target).resolve()
    if p.exists():
        return True, "tệp có thật"
    return False, f"KHÔNG THẤY TỆP {target}"


def check_numbering(by_id, ordered):
    """Heading-number defects: level mismatch, duplicate, missing parent, gap."""
    issues = []
    for sid, hits in sorted(by_id.items()):
        if len(hits) > 1:
            where = ", ".join(str(h[0] + 1) for h in hits)
            issues.append(("CHẶN", f"số hiệu {sid} bị dùng cho {len(hits)} tiêu đề (dòng {where})"))
        ln, level, title = hits[0]
        depth = len(id_parts(sid))
        if level != depth:
            issues.append(("NÊN SỬA", f"{sid} (dòng {ln + 1}) là cấp {depth} theo số hiệu "
                                      f"nhưng dùng tiêu đề markdown cấp {level}"))
        if depth > 1:
            parent = sid.rsplit(".", 1)[0]
            if parent not in by_id:
                issues.append(("CHẶN", f"{sid} (dòng {ln + 1}) không có mục cha {parent}"))
    # contiguity among siblings
    children: dict[str, list] = {}
    for sid, hits in by_id.items():
        parts = id_parts(sid)
        if len(parts) < 2 or not parts[-1].isdigit():
            continue
        children.setdefault(".".join(parts[:-1]), []).append((int(parts[-1]), sid, hits[0][0]))
    for parent, kids in sorted(children.items()):
        nums = sorted(k[0] for k in kids)
        missing = [n for n in range(1, max(nums) + 1) if n not in nums]
        if missing:
            issues.append(("CHẶN", f"mục con của {parent} nhảy cóc: thiếu "
                                   + ", ".join(f"{parent}.{n}" for n in missing)))
        in_doc = [k[0] for k in sorted(kids, key=lambda k: k[2])]
        if in_doc != sorted(in_doc):
            issues.append(("NÊN SỬA", f"mục con của {parent} không theo thứ tự tăng dần "
                                      f"trong văn bản: {in_doc}"))
    return issues


def check_caption_numbering(caps, dups, scope: str | None = None):
    """Bảng/Hình numbering: duplicates, chapter gaps, out-of-order appearance."""
    issues = []
    for kind, cid, first, second in dups:
        issues.append(("CHẶN", f"{kind} {cid} có hai caption (dòng {first} và {second})"))
    for kind in ("Bảng", "Hình"):
        groups: dict[str, list] = {}
        for cid, (ln, _t) in caps[kind].items():
            head, _, tail = cid.rpartition(".")
            if not head or not tail.isdigit():
                continue
            groups.setdefault(head, []).append((int(tail), ln))
        for chap, items in sorted(groups.items()):
            if scope and chap != scope:
                continue
            nums = sorted(n for n, _ in items)
            missing = [n for n in range(1, max(nums) + 1) if n not in nums]
            if missing:
                issues.append(("CHẶN", f"{kind} chương {chap} nhảy cóc: thiếu "
                                       + ", ".join(f"{chap}.{n}" for n in missing)))
            in_doc = [n for n, _ in sorted(items, key=lambda t: t[1])]
            if in_doc != sorted(in_doc):
                issues.append(("NÊN SỬA", f"{kind} chương {chap} xuất hiện không theo thứ tự "
                                          f"số hiệu: {in_doc}"))
    return issues


def check_index_pointers(lines, headings, by_id, ordered, caps, doc_path: Path,
                         only: set | None = None):
    """DANH MỤC BẢNG 'Mục' column and DANH MỤC HÌNH 'Nguồn tệp' column."""
    issues = []
    root = Path.cwd()
    for kind, heading_key, col in (("Bảng", TABLE_INDEX_HEADING, "Mục"),
                                   ("Hình", FIGURE_INDEX_HEADING, "Nguồn tệp")):
        block = slice_index_section(lines, headings, heading_key)
        for cells in table_rows(block):
            if len(cells) < 3:
                continue
            cid = cells[0].strip()
            if not re.fullmatch(r"[A-Z]?\d+(\.\d+)*", cid):
                continue
            if only is not None and cid not in only:
                continue
            cap = caps[kind].get(cid)
            if cap is None:
                issues.append(("CHẶN", f"{kind} {cid} có trong danh mục nhưng thân bài "
                                       f"không có caption nào"))
                continue
            val = cells[2].strip().strip("`")
            if col == "Mục":
                want = re.sub(r"^Phụ\s+lục\s+", "", val).strip()
                owner = owner_section(ordered, cap[0])
                if want not in by_id:
                    issues.append(("NÊN SỬA", f"danh mục ghi {kind} {cid} ở Mục {val}, "
                                              f"nhưng mục đó không tồn tại"))
                elif owner is None or not is_ancestor(want, owner):
                    issues.append(("NÊN SỬA", f"danh mục ghi {kind} {cid} ở Mục {val}, "
                                              f"caption thực nằm trong Mục {owner} (dòng {cap[0]})"))
            else:
                cand = [root / val, doc_path.parent / val]
                if not any(p.exists() for p in cand):
                    issues.append(("CHẶN", f"tệp nguồn của {kind} {cid} không tồn tại: {val}"))
    return issues


def check_toc(lines, headings, by_id, only_ids: set | None = None):
    """MỤC LỤC entries vs real headings: missing, orphan, title/anchor drift."""
    issues = []
    block = slice_index_section(lines, headings, "MỤC LỤC")
    entries = {}
    for line in block:
        m = TOC_ENTRY_RE.match(line)
        if m:
            entries[m.group(1).strip()] = m.group(2).strip()
    if not entries:
        return [("NÊN SỬA", "không đọc được MỤC LỤC (không có mục nào dạng '- [tiêu đề](#anchor)')")]
    titles = {text.strip(): (ln, level) for ln, level, text in headings}
    for text, (ln, _lvl) in titles.items():
        sid = section_id(text)
        if only_ids is not None and sid not in only_ids:
            continue
        if text not in entries:
            issues.append(("NÊN SỬA", f"tiêu đề “{text[:58]}” (dòng {ln + 1}) không có trong MỤC LỤC"))
            continue
        want = slugify(text)
        if entries[text] != want:
            issues.append(("NÊN SỬA", f"anchor trong MỤC LỤC của “{text[:44]}” là "
                                      f"#{entries[text]}, đúng phải là #{want}"))
    if only_ids is None:
        for text in entries:
            if text not in titles and norm(text) not in {norm(t) for t in titles}:
                issues.append(("NÊN SỬA", f"MỤC LỤC có mục “{text[:58]}” nhưng không có "
                                          f"tiêu đề nào như vậy trong luận văn"))
    return issues


def print_issues(issues, empty_msg: str) -> int:
    """Print, and return how many defects were printed (for the exit code)."""
    if not issues:
        print(f"  ✓ {empty_msg}")
        return 0
    for level, msg in issues:
        print(f"  ✗ [{level}] {msg}")
    return len(issues)


def report_crossrefs(lines, headings, by_id, ordered, caps, doc_path, start, end, cur_id):
    print("\n[7] THAM CHIẾU CHÉO — phần này trỏ đi đâu, và ai trỏ vào nó")
    refs = scan_refs(lines, start, end, caps)
    if not refs:
        print("  (phần này không có tham chiếu chéo nào)")
    seen = set()
    bad = 0
    for ln, kind, target in refs:
        key = (kind, target)
        if key in seen:
            continue
        seen.add(key)
        ok, note = resolve_ref(kind, target, by_id, caps, doc_path.parent)
        if kind in ("Mục", "Chương", "Phụ lục") and ok and cur_id and target == cur_id:
            note += "  ⚠ tự trỏ vào chính phần đang soát"
        print(f"  dòng {ln}: {kind} {target}  {'✓' if ok else '✗'} {note}")
        bad += not ok
    if refs:
        print(f"  → {len(seen)} tham chiếu khác nhau, {bad} không phân giải được.")
        print("    Phân giải được ≠ trỏ đúng chỗ: đọc câu chứa tham chiếu và tiêu đề đích,")
        print("    hỏi xem mục đích có thật sự trả lời điều câu đó hứa không (tiêu chí 5).")
    if cur_id:
        # Renumbering this section breaks references to it AND to its children.
        inbound: dict[str, list] = {}
        for i, line in enumerate(lines):
            if start <= i < end:
                continue
            for rx, _kind in ((REF_SECTION_RE, "Mục"), (REF_CHAPTER_RE, "Chương"),
                              (REF_APPENDIX_RE, "Phụ lục")):
                for m in rx.finditer(line):
                    if is_ancestor(cur_id, m.group(1)):
                        inbound.setdefault(m.group(1), []).append(i + 1)
        if inbound:
            total = sum(len(v) for v in inbound.values())
            print(f"  trỏ VÀO phần này: {total} nơi")
            for tid in sorted(inbound, key=id_key):
                where = inbound[tid]
                shown = ", ".join(map(str, where[:10])) + ("…" if len(where) > 10 else "")
                print(f"    - {tid}: {len(where)} nơi (dòng {shown})")
            print(f"    → đổi số hiệu trong phần {cur_id} là phải sửa từng nơi đó.")
        else:
            print(f"  trỏ VÀO phần này: không nơi nào nhắc “Mục {cur_id}” "
                  f"hay mục con của nó.")


def report_numbering(lines, headings, by_id, ordered, caps, dups, doc_path,
                     start, end, cur_id):
    print("\n[8] ĐÁNH SỐ (tiêu đề · bảng/hình · danh mục · MỤC LỤC)")
    sub = {sid for sid in by_id if cur_id and is_ancestor(cur_id, sid)}
    if cur_id:
        print(f"  tiêu đề trong phần: "
              f"{', '.join(sorted(sub, key=id_key)) or '(không có mục con)'}")
    scoped_by_id = {k: v for k, v in by_id.items() if k in sub} if cur_id else by_id
    issues = [i for i in check_numbering(by_id, ordered)
              if not cur_id or any(s in i[1] for s in sub)]
    print_issues(issues, "số hiệu tiêu đề liên tục, đúng cấp, có mục cha")
    in_sec = {kind: {cid for cid, (ln, _t) in caps[kind].items() if start < ln <= end}
              for kind in ("Bảng", "Hình")}
    chap = (cur_id or "").split(".")[0] or None
    cap_issues = check_caption_numbering(caps, dups, scope=chap)
    if cur_id:
        for kind in ("Bảng", "Hình"):
            if in_sec[kind]:
                print(f"  {kind} có caption trong phần: "
                      + ", ".join(sorted(in_sec[kind], key=lambda c: caps[kind][c][0])))
    print_issues(cap_issues, f"số hiệu bảng/hình{' chương ' + chap if chap else ''} "
                             "liên tục, không trùng, xuất hiện đúng thứ tự")
    only = (in_sec["Bảng"] | in_sec["Hình"]) if cur_id else None
    print_issues(check_index_pointers(lines, headings, by_id, ordered, caps, doc_path, only),
                 "cột “Mục” và “Nguồn tệp” của danh mục trỏ đúng")
    print_issues(check_toc(lines, headings, by_id, sub | {cur_id} if cur_id else None),
                 "MỤC LỤC khớp tiêu đề và anchor")
    refs_all = {(k, t) for _ln, k, t in scan_refs(lines, 0, len(lines), caps)}
    orphan = [f"{kind} {cid}" for kind in ("Bảng", "Hình")
              for cid in sorted(in_sec[kind], key=id_key) if (kind, cid) not in refs_all]
    print_issues([("NÊN SỬA", "có caption nhưng KHÔNG chỗ nào trong luận văn nhắc tên: "
                              + ", ".join(orphan) + " → thiếu câu dẫn, hoặc bảng thừa")]
                 if orphan else [],
                 "mọi bảng/hình của phần đều được nhắc tên trong văn")


def report_global(lines, headings, by_id, ordered, caps, dups, doc_path) -> int:
    print("=" * 78)
    print("SOÁT TOÀN VĂN: THAM CHIẾU CHÉO & ĐÁNH SỐ")
    print(f"Tệp : {doc_path}  ({len(lines)} dòng, {len(by_id)} mục có số hiệu, "
          f"{len(caps['Bảng'])} bảng, {len(caps['Hình'])} hình)")
    print("=" * 78)
    bad_n = 0
    print("\n[A] SỐ HIỆU TIÊU ĐỀ")
    bad_n += print_issues(check_numbering(by_id, ordered),
                          "mọi mục liên tục, đúng cấp, có mục cha")
    print("\n[B] SỐ HIỆU BẢNG & HÌNH")
    bad_n += print_issues(check_caption_numbering(caps, dups),
                          "mọi bảng/hình liên tục trong chương, không trùng, đúng thứ tự")
    print("\n[C] DANH MỤC BẢNG / HÌNH TRỎ ĐÚNG CHƯA")
    bad_n += print_issues(check_index_pointers(lines, headings, by_id, ordered, caps, doc_path),
                          "mọi dòng danh mục trỏ đúng mục và đúng tệp có thật")
    print("\n[D] MỤC LỤC")
    bad_n += print_issues(check_toc(lines, headings, by_id), "MỤC LỤC khớp toàn bộ tiêu đề")
    print("\n[E] THAM CHIẾU CHÉO KHÔNG PHÂN GIẢI ĐƯỢC")
    bad = []
    for ln, kind, target in scan_refs(lines, 0, len(lines), caps):
        ok, note = resolve_ref(kind, target, by_id, caps, doc_path.parent)
        if not ok:
            bad.append((ln, kind, target, note))
    if not bad:
        print("  ✓ mọi tham chiếu Mục/Chương/Phụ lục/Bảng/Hình/ảnh đều phân giải được")
    for ln, kind, target, note in bad:
        print(f"  ✗ dòng {ln}: {kind} {target} — {note}")
    bad_n += len(bad)
    print("\n[F] BẢNG/HÌNH CÓ CAPTION NHƯNG KHÔNG AI NHẮC")
    refs_all = {(k, t) for _ln, k, t in scan_refs(lines, 0, len(lines), caps)}
    orphan = [f"{kind} {cid}" for kind in ("Bảng", "Hình")
              for cid in sorted(caps[kind], key=id_key) if (kind, cid) not in refs_all]
    if orphan:
        print("  ✗ [NÊN SỬA] không được nhắc trong văn (thiếu câu dẫn, hoặc thừa): "
              + ", ".join(orphan))
        bad_n += len(orphan)
    else:
        print("  ✓ mọi bảng/hình đều được nhắc ít nhất một lần trong văn")
    print(f"\nTỔNG: {bad_n} phát hiện cơ học (exit 1 nếu > 0).")
    print("Đây là lượt CƠ HỌC. “Trỏ đúng chỗ” về mặt NỘI DUNG vẫn phải đọc: xem")
    print("reference/criteria.md, tiêu chí 4 và 5.")
    return bad_n


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("section", nargs="?", help="số mục (4.3), hoặc một phần tiêu đề")
    ap.add_argument("--file", default="thesis/LUAN_VAN.md")
    ap.add_argument("--list", action="store_true", help="liệt kê mọi mục rồi thoát")
    ap.add_argument("--numbers-context", action="store_true",
                    help="với mỗi số, tìm những nơi khác trong luận văn cũng nhắc tới nó")
    ap.add_argument("--numbering", action="store_true",
                    help="soát THAM CHIẾU CHÉO + ĐÁNH SỐ trên TOÀN VĂN rồi thoát "
                         "(không cần chỉ định mục)")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        sys.exit(f"Không thấy {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    headings = parse_headings(lines)

    if args.list:
        for ln, level, text in headings:
            print(f"{ln+1:>5}  {'  ' * (level - 1)}{text}")
        return

    by_id, ordered = build_sections(headings)
    caps, cap_dups = scan_captions(lines)

    if args.numbering:
        sys.exit(1 if report_global(lines, headings, by_id, ordered, caps, cap_dups, path)
                 else 0)

    if not args.section:
        for ln, level, text in headings:
            print(f"{ln+1:>5}  {'  ' * (level - 1)}{text}")
        return

    start, end, title = find_section(headings, lines, args.section)
    body = lines[start:end]
    glossary = build_glossary(lines, headings)
    tbl_index = build_index(lines, headings, TABLE_INDEX_HEADING)
    fig_index = build_index(lines, headings, FIGURE_INDEX_HEADING)

    print("=" * 78)
    print(f"PHẦN: {title}")
    print(f"Tệp : {path}  dòng {start+1}–{end}  ({end - start} dòng)")
    print(f"Tham chiếu: bảng thuật ngữ {len(glossary)} khoá · "
          f"danh mục bảng {len(tbl_index)} · danh mục hình {len(fig_index)}")
    print("=" * 78)

    # --- [3] cấu trúc đoạn -------------------------------------------------- #
    blocks = classify_blocks(body, start)
    counts: dict[str, int] = {}
    for kind, _, blines in blocks:
        counts[kind] = counts.get(kind, 0) + 1
    prose_lines = sum(len(b) for k, _, b in blocks if k == "prose")
    bullet_lines = sum(len(b) for k, _, b in blocks if k == "bullet")
    print("\n[3] CẤU TRÚC ĐOẠN (liên kết vs. liệt kê)")
    print(f"  khối: " + " · ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"  dòng văn xuôi = {prose_lines} · dòng gạch đầu dòng = {bullet_lines}"
          + (f"  (tỉ lệ gạch đầu dòng {bullet_lines/(prose_lines+bullet_lines):.0%})"
             if prose_lines + bullet_lines else ""))
    for i, (kind, ln, blines) in enumerate(blocks):
        if kind != "bullet":
            continue
        prev = blocks[i - 1] if i else None
        nxt = blocks[i + 1] if i + 1 < len(blocks) else None
        lead = prev is not None and prev[0] == "prose"
        after = nxt is not None and nxt[0] == "prose"
        flag = "OK" if (lead and after) else ("thiếu câu dẫn" if not lead else "thiếu câu chốt")
        print(f"    - dòng {ln}: {len(blines)} gạch đầu dòng — {flag}")
    weak = []
    for kind, ln, blines in blocks:
        if kind != "prose":
            continue
        first = norm(blines[0].strip())
        if not any(norm(c) in first[:60] for c in CONNECTIVES):
            weak.append(ln)
    print(f"  đoạn văn xuôi mở đầu KHÔNG có từ nối rõ ràng: {len(weak)}"
          + (f" (dòng {', '.join(map(str, weak[:12]))}{'…' if len(weak) > 12 else ''})" if weak else ""))
    print("  → chỉ là tín hiệu; đọc thật để kết luận, đoạn không có từ nối vẫn có thể liền mạch.")

    # --- [4] bảng & hình ---------------------------------------------------- #
    print("\n[4] BẢNG & HÌNH vs. DANH MỤC")
    body_text = "\n".join(body)
    refs_t = sorted(set(TABLE_REF_RE.findall(body_text)))
    refs_f = sorted(set(FIGURE_REF_RE.findall(body_text)))
    captions_t = [(CAPTION_TABLE_RE.match(l.strip()), start + i + 1)
                  for i, l in enumerate(body) if CAPTION_TABLE_RE.match(l.strip())]
    captions_f = [(CAPTION_FIGURE_RE.match(l.strip()), start + i + 1)
                  for i, l in enumerate(body) if CAPTION_FIGURE_RE.match(l.strip())]
    # match groups: 1 = delimiter, 2 = id, 3 = caption text
    if not (refs_t or refs_f):
        print("  (phần này không nhắc tới bảng/hình nào)")
    for kind, refs, sec_caps, index in (
        ("Bảng", refs_t, captions_t, tbl_index),
        ("Hình", refs_f, captions_f, fig_index),
    ):
        for rid in refs:
            in_index = rid in index
            cap = next((m.group(3).strip() for m, _ in sec_caps if m.group(2) == rid), None)
            mark = "✓ có trong danh mục" if in_index else "✗ THIẾU trong danh mục"
            print(f"  {kind} {rid}: {mark}")
            if in_index and cap:
                cover, missing = caption_drift(cap, index[rid])
                if cover < 0.85:
                    print(f"      ⚠ caption ≠ danh mục (trùng {cover:.0%} số từ"
                          + (f"; danh mục có mà caption không: {', '.join(missing[:6])}"
                             if missing else "") + ")")
                    print(f"        caption : {cap[:110]}")
                    print(f"        danh mục: {index[rid]}")
    raw_tables = [(ln, blines) for k, ln, blines in blocks if k == "table"]
    captioned_lines = {ln for _, ln in captions_t}
    for ln, blines in raw_tables:
        has_caption = any(abs(ln - c) <= 3 for c in captioned_lines)
        if not has_caption:
            print(f"  ⚠ bảng markdown ở dòng {ln} ({len(blines)} dòng) không có caption '**Bảng N.M — …**'"
                  " → không đánh số thì không vào được danh mục")

    # --- [2] thuật ngữ ------------------------------------------------------ #
    known, unknown = extract_terms(body, glossary)
    print("\n[2] THUẬT NGỮ")
    print(f"  đã có trong bảng thuật ngữ ({len(known)}):")
    for term, cnt, off, vi in known[:40]:
        print(f"    ✓ {term}  ×{cnt}  → “{vi}”")
    print(f"  CHƯA có trong bảng thuật ngữ — ứng viên cần cân nhắc ({len(unknown)}):")
    for term, cnt, off, _ in unknown[:40]:
        print(f"    ? {term}  ×{cnt}  (dòng {start + off + 1})")
    if len(unknown) > 40:
        print(f"    … và {len(unknown) - 40} ứng viên nữa")
    print("  → danh sách này có nhiễu (tên tệp, tên riêng, viết tắt đơn vị). Lọc bằng mắt:")
    print("    chỉ thuật ngữ CHUYÊN NGÀNH lần đầu xuất hiện mới cần vào bảng.")

    # --- [6] số liệu cần verify --------------------------------------------- #
    print("\n[6] SỐ LIỆU CẦN ĐỐI CHIẾU VỚI ARTIFACT (chống bịa số)")
    doc_text = "\n".join(lines)
    seen = set()
    n_lines = 0
    for offset, line in enumerate(body):
        if HEADING_RE.match(line):
            continue
        nums = [m.group(0).strip() for m in NUMBER_RE.finditer(line)]
        nums = [n for n in nums if re.search(r"\d", n) and len(n.rstrip("%×xM")) > 1]
        if not nums:
            continue
        n_lines += 1
        ln = start + offset + 1
        shown = line.strip()
        print(f"  dòng {ln}: {shown[:150]}{'…' if len(shown) > 150 else ''}")
        if args.numbers_context:
            for n in nums:
                if n in seen:
                    continue
                seen.add(n)
                others = [i + 1 for i, l in enumerate(lines)
                          if n in l and not (start < i + 1 <= end)]
                if others:
                    print(f"      ↳ “{n}” cũng xuất hiện ở dòng {others[:8]}"
                          f"{'…' if len(others) > 8 else ''} — kiểm tính nhất quán")
    print(f"  tổng: {n_lines} dòng có số. MỖI con số phải truy được về một artifact"
          " (aggregated.json / test_metrics.json / reports/*.md / file cấu hình).")

    # --- [7]+[8] tham chiếu chéo & đánh số ---------------------------------- #
    cur_id = section_id(title)
    report_crossrefs(lines, headings, by_id, ordered, caps, path, start, end, cur_id)
    report_numbering(lines, headings, by_id, ordered, caps, cap_dups, path,
                     start, end, cur_id)

    print("\nHết phần cơ học. Sáu tiêu chí còn lại (văn phong, tính đồng nhất, không bịa)")
    print("do người/mô hình đọc và kết luận — xem reference/criteria.md.")


if __name__ == "__main__":
    main()
