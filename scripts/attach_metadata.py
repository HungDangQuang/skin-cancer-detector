"""
Attach ISIC 2024 metadata columns to EXISTING split CSVs and prediction CSVs,
without re-running ``prepare_data.py`` and without any GPU inference.

WHY THIS EXISTS
---------------
Direction D (subgroup calibration, docs/metadata_training_plan.md §D) needs
``anatom_site_general`` / ``sex`` next to each prediction. The designed path is
"re-run prepare with data.metadata_cols=[...] then re-evaluate", but that needs
``train-image.hdf5`` (opened unconditionally by ``process_isic2024``) *and*
``data/raw/pad_ufes_20/`` — without the PAD raw dir ``prepare_data.py`` silently
drops every PAD row (``prepare_data.py`` "PAD-UFES-20 not found" branch), which
would produce DIFFERENT splits from the ones all finished runs were trained and
tested on. This script sidesteps both: it only ADDS columns, so split membership
and fold assignment are provably untouched, and it costs no GPU time.

WHY POSITIONAL BACK-FILL IS SOUND
---------------------------------
``predictions.csv`` is written row-aligned to ``test_dataloader()``, which is
built with ``shuffle=False`` over the test split CSV read in file order
(``src/data/datamodule.py``), and ``train_sources`` filters train+val ONLY — the
test set is deliberately left whole. So prediction row *i* is split row *i*.
Rather than trusting that, every file is verified before it is touched:
  1. row counts must match exactly, and
  2. the ``source`` column (isic2024 / pad_ufes_20), when present in both, must
     match row-for-row — any reordering or mixed-experiment run-dir breaks this.
A file failing either guard is SKIPPED (never partially written) and the script
exits non-zero.

Writes are additive, atomic (tmp + os.replace) and idempotent (re-running
replaces the columns in place). Every file touched is copied to --backup-dir
first, so nothing that cost GPU hours can be lost.

Pure stdlib csv on purpose: values are copied verbatim as text, so y_prob keeps
its exact printed precision.

Runs on the SERVER (that is where the run-dirs and the raw metadata CSV live).

Usage:
    # both stages, the direction-D columns
    python scripts/attach_metadata.py --cols anatom_site_general,sex

    # splits only (unblocks a future re-eval / direction-A training run)
    python scripts/attach_metadata.py --stage splits --cols anatom_site_general,sex

    # preview without writing
    python scripts/attach_metadata.py --dry-run
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.data.preprocessing import _validate_metadata_cols  # noqa: E402

DEFAULT_COLS = "anatom_site_general,sex"
# csv's default field-size limit chokes on nothing here, but the ISIC metadata is
# 246 MB / ~401k rows — read it streaming, keeping only the requested columns.
ID_COL = "isic_id"


def load_metadata(meta_csv: Path, cols: list[str]) -> dict[str, list[str]]:
    """Map isic_id -> [value per requested column], read verbatim as text."""
    with open(meta_csv, newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        if ID_COL not in header:
            raise SystemExit(f"ERROR: {meta_csv} has no '{ID_COL}' column")
        missing = [c for c in cols if c not in header]
        if missing:
            raise SystemExit(
                f"ERROR: columns {missing} not in {meta_csv}. Available: {sorted(header)}"
            )
        table: dict[str, list[str]] = {}
        for row in reader:
            table[row[ID_COL]] = [(row.get(c) or "").strip() for c in cols]
    return table


def _read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        return header, [r for r in reader]


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    """Atomic write: full file to <path>.tmp in the same dir, then os.replace."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    os.replace(tmp, path)


def _backup(path: Path, project_dir: Path, backup_dir: Path) -> None:
    try:
        rel = path.resolve().relative_to(project_dir)
    except ValueError:
        rel = Path(path.name)
    dst = backup_dir / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)


def _strip_cols(header: list[str], rows: list[list[str]], cols: list[str]) -> tuple[list[str], list[list[str]]]:
    """Drop already-present metadata columns so a re-run replaces (not duplicates) them."""
    drop = {i for i, h in enumerate(header) if h in cols}
    if not drop:
        return header, rows
    keep = [i for i in range(len(header)) if i not in drop]
    return [header[i] for i in keep], [[r[i] for i in keep if i < len(r)] for r in rows]


def attach_to_csv(
    path: Path,
    id_source: tuple[list[str], list[list[str]]] | None,
    table: dict[str, list[str]],
    cols: list[str],
    project_dir: Path,
    backup_dir: Path,
    dry_run: bool,
) -> tuple[bool, str]:
    """Append `cols` to one CSV.

    ``id_source`` is None for a split CSV (it carries its own ``image_id``), or
    the (header, rows) of the split CSV a predictions CSV must be aligned to.
    Returns (ok, message).
    """
    header, rows = _read_csv(path)

    if id_source is None:
        if "image_id" not in header:
            return False, "no image_id column"
        ids = [r[header.index("image_id")] for r in rows]
        src_ref = None
    else:
        ref_header, ref_rows = id_source
        if len(rows) != len(ref_rows):
            return False, f"ROW COUNT MISMATCH: {len(rows)} vs split {len(ref_rows)} — skipped"
        ids = [r[ref_header.index("image_id")] for r in ref_rows]
        src_ref = (
            [r[ref_header.index("source")] for r in ref_rows]
            if "source" in ref_header
            else None
        )
        # Alignment guard 1 — the label sequence. 62k rows at ~0.39% positives:
        # any reordering or a run-dir holding a different experiment's fold
        # breaks this. Applies to val_predictions.csv too (it has no `source`).
        if "label" in ref_header and "y_true" in header:
            want = [int(float(r[ref_header.index("label")])) for r in ref_rows]
            got = [int(float(r[header.index("y_true")])) for r in rows]
            if got != want:
                n_bad = sum(1 for a, b in zip(got, want) if a != b)
                return False, f"LABEL ORDER MISMATCH on {n_bad} rows — skipped"
        # Alignment guard 2 — the per-row origin tag (test predictions only).
        if src_ref is not None and "source" in header:
            got_src = [r[header.index("source")] for r in rows]
            if got_src != src_ref:
                n_bad = sum(1 for a, b in zip(got_src, src_ref) if a != b)
                return False, f"SOURCE ORDER MISMATCH on {n_bad} rows — skipped"

    header, rows = _strip_cols(header, rows, cols)
    blank = [""] * len(cols)
    matched = 0
    for r, img_id in zip(rows, ids):
        vals = table.get(img_id)
        if vals is None:
            r.extend(blank)
        else:
            r.extend(vals)
            matched += 1
    header = header + cols

    pct = 100.0 * matched / len(rows) if rows else 0.0
    msg = f"{len(rows)} rows, {matched} matched ({pct:.1f}%)"
    if dry_run:
        return True, msg + " [dry-run]"
    _backup(path, project_dir, backup_dir)
    _write_csv(path, header, rows)
    return True, msg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cols", default=DEFAULT_COLS,
                    help=f"comma-separated ISIC metadata columns (default: {DEFAULT_COLS})")
    ap.add_argument("--stage", choices=["splits", "predictions", "both"], default="both",
                    help="which artifacts to attach to (default: both)")
    ap.add_argument("--meta-csv", type=Path, default=Path("data/raw/isic2024/train-metadata.csv"),
                    help="raw ISIC metadata CSV (the source of the columns)")
    ap.add_argument("--splits-dir", type=Path, default=Path("data/splits/isic2024"),
                    help="dir holding test_split.csv + fold_*/{train,val}_split.csv")
    ap.add_argument("--runs-dir", type=Path, default=Path("experiments/runs"),
                    help="tree of run-dirs with fold_*/predictions.csv")
    ap.add_argument("--backup-dir", type=Path, default=None,
                    help="default: reports/_metadata_backup/<timestamp>/")
    ap.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    cols = [c.strip() for c in args.cols.split(",") if c.strip()]
    if not cols:
        raise SystemExit("ERROR: --cols is empty")
    # Same leakage/reserved-name contract as prepare_data.py — iddx_*/mel_* are
    # post-biopsy fields and would leak the label; base schema names would be
    # overwritten with NaN for PAD rows.
    _validate_metadata_cols(cols)

    if not args.meta_csv.exists():
        raise SystemExit(
            f"ERROR: {args.meta_csv} not found. Copy the ISIC train-metadata.csv "
            f"onto this machine first (it is the only source of these columns)."
        )

    project_dir = Path(__file__).resolve().parent.parent
    backup_dir = args.backup_dir or (
        project_dir / "reports" / "_metadata_backup"
        / datetime.now().strftime("%Y%m%d_%H%M%S")
    )

    print(f"[attach] cols={cols} stage={args.stage} dry_run={args.dry_run}")
    print(f"[attach] reading {args.meta_csv} ...")
    table = load_metadata(args.meta_csv, cols)
    print(f"[attach] {len(table)} ISIC ids in metadata")
    if not args.dry_run:
        print(f"[attach] backups -> {backup_dir}")

    failures: list[str] = []
    test_split = args.splits_dir / "test_split.csv"

    if args.stage in ("splits", "both"):
        targets = [test_split]
        for fold_dir in sorted(args.splits_dir.glob("fold_*")):
            targets += [fold_dir / "train_split.csv", fold_dir / "val_split.csv"]
        print(f"\n[attach] --- splits ({len(targets)} files) ---")
        for path in targets:
            if not path.exists():
                print(f"  MISS {path}")
                continue
            ok, msg = attach_to_csv(path, None, table, cols, project_dir, backup_dir, args.dry_run)
            print(f"  {'OK  ' if ok else 'FAIL'} {path}: {msg}")
            if not ok:
                failures.append(f"{path}: {msg}")

    if args.stage in ("predictions", "both"):
        if not test_split.exists():
            raise SystemExit(f"ERROR: {test_split} not found (needed to align predictions)")
        # Read the split CSVs ONCE; predictions are aligned against them.
        test_ref = _read_csv(test_split)
        val_refs: dict[str, tuple[list[str], list[list[str]]]] = {}
        pred_files = sorted(args.runs_dir.rglob("fold_*/predictions.csv"))
        val_files = sorted(args.runs_dir.rglob("fold_*/val_predictions.csv"))
        print(f"\n[attach] --- predictions ({len(pred_files)} test + {len(val_files)} val) ---")
        for path in pred_files:
            ok, msg = attach_to_csv(path, test_ref, table, cols, project_dir, backup_dir, args.dry_run)
            print(f"  {'OK  ' if ok else 'FAIL'} {path}: {msg}")
            if not ok:
                failures.append(f"{path}: {msg}")
        for path in val_files:
            fold = path.parent.name  # fold_N
            if fold not in val_refs:
                ref_path = args.splits_dir / fold / "val_split.csv"
                if not ref_path.exists():
                    print(f"  MISS {ref_path} (needed for {path})")
                    failures.append(f"{path}: missing {ref_path}")
                    continue
                val_refs[fold] = _read_csv(ref_path)
            ok, msg = attach_to_csv(path, val_refs[fold], table, cols, project_dir, backup_dir, args.dry_run)
            print(f"  {'OK  ' if ok else 'FAIL'} {path}: {msg}")
            if not ok:
                failures.append(f"{path}: {msg}")

    print(f"\n[attach] done | {len(failures)} failure(s)")
    if failures:
        for f in failures:
            print(f"  FAILED {f}")
        # Non-zero so the runner surfaces it instead of the caller assuming
        # every run-dir now carries the metadata columns.
        sys.exit(1)


if __name__ == "__main__":
    main()
