"""
Apply the pre-registered, VALIDATION-ONLY selection rule of a candidate round and write the result
(docs/PREREG_CANDIDATE2_2026-10-02.md §4 + §7.1). Commit the output BEFORE any test file of the
candidates is opened or any external evaluation is run (§7.2).

Rule:
  1. Pair score = mean over the 5 folds of AUPRC on the PAD-UFES-20 rows of val, from
     fold_N/val_predictions<tag>.csv joined row for row with <splits_dir>/fold_N/val_split.csv
     (row count and labels checked — `val_with_source` from scripts/make_app_config.py).
  2. Tie (§7.1): take the top score; if a candidate listed EARLIER (order of --candidate) scores
     less than --tie below it, the earliest such candidate wins. 0.005 is a convention borrowed from
     the single-fold rerun noise floor, not a measured noise of AUPRC on ~350-400 PAD val rows.
  3. Ship fold = the fold whose val AUPRC over ALL val rows (val_metrics<tag>.json "auprc") is the
     median of the 5 folds of the chosen pair.

This script opens ONLY val_predictions<tag>.csv, val_metrics<tag>.json and val_split.csv. Each of
those paths is checked by `_val_only` (refuses any other file name) before it is read;
`val_with_source` rebuilds the same two CSV paths itself, so keep the two in step if either changes.

Usage (on the server, in .venv-linux — CPU only):
    python scripts/select_candidate.py \
        --candidate P0=experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp \
        --candidate P1=experiments/runs_newsplit_ddi/kd_convnextv2_base_to_mobilenetv4_conv_medium__srcsamp \
        --candidate P2=experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_repvit_m1_0__srcsamp \
        --out-dir reports/2026-10-04_candidate2_selection
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score

sys.path.insert(0, str(Path(__file__).parent))
from make_app_config import PHONE_SOURCE, val_with_source  # noqa: E402

N_FOLDS = 5
_ALLOWED_PREFIXES = ("val_predictions", "val_metrics", "val_split")


def _val_only(path: Path) -> Path:
    """Refuse to touch anything that is not a validation file (prereg §7.2)."""
    if not path.name.startswith(_ALLOWED_PREFIXES):
        sys.exit(f"ERROR: refusing to read {path} — this script may only read validation files")
    if not path.is_file():
        sys.exit(f"ERROR: missing {path}")
    return path


def pad_val_auprc(run_dir: Path, splits_dir: Path, fold: int, tag: str) -> dict:
    fold_dir = run_dir / f"fold_{fold}"
    _val_only(fold_dir / f"val_predictions{tag}.csv")
    _val_only(splits_dir / f"fold_{fold}" / "val_split.csv")
    val = val_with_source(fold_dir, splits_dir, fold, tag)
    pad = val[val["source"] == PHONE_SOURCE]
    n_pos = int(pad["y_true"].sum())
    if len(pad) == 0 or n_pos == 0 or n_pos == len(pad):
        sys.exit(f"ERROR: {fold_dir}: PAD val rows need both classes (rows={len(pad)}, pos={n_pos})")
    return {
        "fold": fold,
        "pad_rows": int(len(pad)),
        "pad_pos": n_pos,
        "val_rows": int(len(val)),
        "pad_auprc": float(average_precision_score(pad["y_true"], pad["y_prob"])),
    }


def all_val_auprc(run_dir: Path, fold: int, tag: str) -> float:
    path = _val_only(run_dir / f"fold_{fold}" / f"val_metrics{tag}.json")
    with open(path) as fh:
        metrics = json.load(fh)
    if "auprc" not in metrics:
        sys.exit(f"ERROR: {path} has no 'auprc'")
    return float(metrics["auprc"])


def apply_tie_rule(order: list[str], scores: dict[str, float], tie: float) -> tuple[str, str]:
    top = max(order, key=lambda name: scores[name])
    for name in order:  # earliest listed first
        if scores[top] - scores[name] < tie:
            if name == top:
                return name, f"highest score ({scores[top]:.4f})"
            return name, (f"tie rule §7.1: {name} ({scores[name]:.4f}) is listed before {top} "
                          f"({scores[top]:.4f}) and trails it by {scores[top] - scores[name]:.4f} < {tie}")
    raise AssertionError("unreachable: the top candidate always satisfies the tie condition")


def median_fold(fold_auprc: dict[int, float]) -> int:
    ranked = sorted(fold_auprc, key=lambda k: (fold_auprc[k], k))
    return ranked[len(ranked) // 2]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidate", action="append", required=True, metavar="NAME=RUN_DIR",
                    help="in pre-registered order (prereg §2); repeat for each candidate")
    ap.add_argument("--splits-dir", default="data/splits/isic2024")
    ap.add_argument("--ckpt-tag", default="_auprc", help='"" or _auprc (prereg §4.2: _auprc)')
    ap.add_argument("--tie", type=float, default=0.005)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--force", action="store_true", help="overwrite an existing selection.json")
    args = ap.parse_args()
    if args.tie <= 0:
        sys.exit(f"ERROR: --tie must be > 0, got {args.tie}")

    order, runs = [], {}
    for spec in args.candidate:
        name, sep, path = spec.partition("=")
        if not sep or not name or not path:
            sys.exit(f"ERROR: --candidate wants NAME=RUN_DIR, got {spec!r}")
        if name in runs:
            sys.exit(f"ERROR: candidate {name} given twice")
        if Path(path).resolve() in {p.resolve() for p in runs.values()}:
            sys.exit(f"ERROR: run-dir {path} given for two candidates")
        order.append(name)
        runs[name] = Path(path)
    splits_dir = Path(args.splits_dir)
    out_dir = Path(args.out_dir)
    if (out_dir / "selection.json").exists() and not args.force:
        sys.exit(f"ERROR: {out_dir}/selection.json exists — pass --force to overwrite")

    per_fold, scores = {}, {}
    for name in order:
        rows = [pad_val_auprc(runs[name], splits_dir, k, args.ckpt_tag) for k in range(N_FOLDS)]
        per_fold[name] = rows
        scores[name] = float(np.mean([r["pad_auprc"] for r in rows]))

    winner, reason = apply_tie_rule(order, scores, args.tie)
    fold_auprc = {k: all_val_auprc(runs[winner], k, args.ckpt_tag) for k in range(N_FOLDS)}
    ship_fold = median_fold(fold_auprc)

    result = {
        "rule": "docs/PREREG_CANDIDATE2_2026-10-02.md §4 + §7.1 (validation only)",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ckpt_tag": args.ckpt_tag,
        "tie": args.tie,
        "order": order,
        "run_dirs": {n: str(runs[n]) for n in order},
        "pad_val_auprc_mean": scores,
        "pad_val_per_fold": per_fold,
        "winner": winner,
        "winner_reason": reason,
        "winner_all_val_auprc_per_fold": {str(k): v for k, v in fold_auprc.items()},
        "ship_fold": ship_fold,
        "files_read": "val_predictions{tag}.csv, val_split.csv, val_metrics{tag}.json only",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "selection.json", "w") as fh:
        json.dump(result, fh, indent=2)

    lines = [
        "# Kết quả chọn ứng viên — chỉ dùng val",
        "",
        f"Luật: {result['rule']}. Checkpoint tag `{args.ckpt_tag}`. Sinh lúc {result['created_utc']}.",
        "Script chỉ đọc `val_predictions*.csv`, `val_split.csv`, `val_metrics*.json`.",
        "",
        "| Ứng viên | Run-dir | AUPRC val PAD (TB 5 fold) | " + " | ".join(f"fold_{k}" for k in range(N_FOLDS)) + " |",
        "|---|---|---|" + "---|" * N_FOLDS,
    ]
    for name in order:
        cells = " | ".join(f"{r['pad_auprc']:.4f} ({r['pad_pos']}/{r['pad_rows']})" for r in per_fold[name])
        lines.append(f"| {name} | `{runs[name]}` | {scores[name]:.4f} | {cells} |")
    lines += [
        "",
        "Ô fold: AUPRC (số ca ác / số hàng PAD của val).",
        "",
        f"**Chọn: {winner}** — {reason}.",
        "",
        f"**Fold ship: fold_{ship_fold}** — trung vị AUPRC toàn bộ val (`val_metrics{args.ckpt_tag}.json`) "
        f"của {winner}: " + " · ".join(f"fold_{k} {fold_auprc[k]:.4f}"
                                        for k in sorted(fold_auprc, key=lambda k: (fold_auprc[k], k))) + ".",
    ]
    (out_dir / "selection.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n[select] wrote {out_dir}/selection.json + selection.md — commit them before opening any test file")


if __name__ == "__main__":
    main()
