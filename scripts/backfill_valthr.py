#!/usr/bin/env python
"""
Back-fill the val-frozen threshold metrics (valthr_*) for runs trained before
the trainers started writing them (2026-10-02).

test_metrics*.json's sensitivity/specificity/f1_score/threshold use Youden's J
fitted on the TEST set itself (the trainers never passed a threshold), so they
are optimistic. This recomputes, per fold, the same rates at the threshold
chosen by Youden's J on that fold's own val_predictions*.csv, from the files
already on disk — no inference, and nothing is written inside the run-dirs.

A fold is scored only when BOTH files exist; every skipped fold is listed in
the report (and the script exits 1 if nothing was scored), so a short coverage
cannot pass silently.

Usage:
    python scripts/backfill_valthr.py --results-dir experiments/runs_newsplit_ddi \
        --out-csv reports/valthr/runs_newsplit_ddi.csv
    # the best-by-val-AUPRC checkpoint (extra_monitors=[auprc]):
    python scripts/backfill_valthr.py --results-dir experiments/runs_newsplit_ddi \
        --pred-name predictions_auprc.csv \
        --out-csv reports/valthr/runs_newsplit_ddi_auprc.csv

Output:
    <out-csv>   one row per run x fold x group (group = "all", then each value
                of the test file's `source` column when present)
    <out-md>    (default: <out-csv> with .md) mean ± std over folds per run,
                test-Youden vs val-Youden side by side, plus the coverage list
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from src.evaluation.metrics import metrics_at_frozen_threshold, youden_threshold

_RATES = ["sensitivity", "specificity", "precision", "f1_score", "accuracy"]
_COUNTS = ["tp", "fp", "tn", "fn"]


def _fold_index(fold_dir: Path) -> int:
    try:
        return int(fold_dir.name.split("_", 1)[1])
    except (IndexError, ValueError):
        return -1


def discover(results_dir: Path, pred_name: str, val_pred_name: str):
    """Every fold_* dir under results_dir holding pred_name -> (run, fold, dir, has_val)."""
    # os.walk(followlinks=True): Path.rglob on Python 3.10 does not descend into
    # symlinked dirs, and the CI / comparison trees are built from symlinks.
    found = []
    for root, dirs, files in os.walk(results_dir, followlinks=True):
        dirs.sort()
        fold_dir = Path(root)
        if not (fold_dir.name.startswith("fold_") and pred_name in files):
            continue
        run = fold_dir.parent.relative_to(results_dir).as_posix()
        found.append((run, _fold_index(fold_dir), fold_dir, (fold_dir / val_pred_name).is_file()))
    return found


def score_fold(fold_dir: Path, pred_name: str, val_pred_name: str) -> list[dict]:
    test = pd.read_csv(fold_dir / pred_name)
    val = pd.read_csv(fold_dir / val_pred_name)
    thr_test = youden_threshold(test["y_true"].values, test["y_prob"].values)
    thr_val = youden_threshold(val["y_true"].values, val["y_prob"].values)

    groups = [("all", test)]
    if "source" in test.columns:
        groups += [(str(g), sub) for g, sub in test.groupby("source", sort=True)]

    rows = []
    for group, sub in groups:
        y, p = sub["y_true"].values, sub["y_prob"].values
        at_test = metrics_at_frozen_threshold(y, p, thr_test, prefix="testthr_")
        at_val = metrics_at_frozen_threshold(y, p, thr_val, prefix="valthr_")
        rows.append({"group": group, "n": len(sub), "n_pos": int(y.sum()), **at_test, **at_val})
    return rows


def _fmt(values: pd.Series) -> str:
    v = values.dropna()
    if len(v) == 0:
        return "—"
    std = v.std(ddof=1) if len(v) > 1 else 0.0
    return f"{v.mean():.4f} ± {std:.4f}"


def write_md(df: pd.DataFrame, skipped: list, out_md: Path, args) -> None:
    lines = [
        f"# Val-frozen vs test-Youden threshold metrics — `{args.results_dir}`",
        "",
        f"Predictions: `fold_*/{args.pred_name}`; threshold source: `fold_*/{args.val_pred_name}` "
        "(Youden's J on that fold's own val set).",
        "",
        "`testthr_*` reproduces what `test_metrics*.json` reports (threshold fitted on the test set — "
        "optimistic). `valthr_*` is the honest counterpart (threshold frozen before seeing the test "
        "labels). Mean ± std over the folds of each run; the std is the spread between the fold "
        "models, not a confidence interval. Ranking metrics do not depend on a threshold and are not "
        "repeated here.",
        "",
    ]
    for group in ["all"] + sorted(g for g in df["group"].unique() if g != "all"):
        sub = df[df["group"] == group]
        if sub.empty:
            continue
        lines += [f"## Group `{group}`", "",
                  "| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |",
                  "|---|---|---|---|---|---|"]
        for run, r in sub.groupby("run", sort=True):
            cells = [f"`{run}`", str(len(r))]
            for k in ["threshold", "sensitivity", "specificity", "f1_score"]:
                cells.append(f"{_fmt(r['testthr_' + k])} → {_fmt(r['valthr_' + k])}")
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    lines += ["## Coverage", "",
              f"Scored folds: {df[df['group'] == 'all'].shape[0]}. "
              f"Skipped (no `{args.val_pred_name}`): {len(skipped)}.", ""]
    for run, fold in skipped:
        lines.append(f"- `{run}` fold {fold}")
    out_md.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--results-dir", type=Path, required=True)
    ap.add_argument("--pred-name", default="predictions.csv")
    ap.add_argument("--val-pred-name", default=None,
                    help="default: val_<pred-name> (val_predictions.csv / val_predictions_auprc.csv)")
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, default=None)
    args = ap.parse_args()
    args.val_pred_name = args.val_pred_name or f"val_{args.pred_name}"
    args.out_md = args.out_md or args.out_csv.with_suffix(".md")

    for out in (args.out_csv, args.out_md):
        if out.resolve().is_relative_to(args.results_dir.resolve()):
            print(f"[valthr] ERROR: {out} must be outside --results-dir ({args.results_dir})",
                  file=sys.stderr)
            return 2

    found = discover(args.results_dir, args.pred_name, args.val_pred_name)
    rows, skipped = [], []
    for run, fold, fold_dir, has_val in found:
        if not has_val:
            skipped.append((run, fold))
            continue
        for row in score_fold(fold_dir, args.pred_name, args.val_pred_name):
            rows.append({"run": run, "fold": fold, **row})

    print(f"[valthr] {len(found)} fold dirs with {args.pred_name}; scored {len(found) - len(skipped)}, "
          f"skipped {len(skipped)} (no {args.val_pred_name})")
    if not rows:
        print("[valthr] ERROR: nothing scored", file=sys.stderr)
        return 1

    df = pd.DataFrame(rows)
    cols = ["run", "fold", "group", "n", "n_pos"] + [
        f"{p}{k}" for p in ("testthr_", "valthr_") for k in ["threshold"] + _RATES + _COUNTS]
    df = df[cols].sort_values(["run", "fold", "group"]).reset_index(drop=True)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_csv, index=False, float_format="%.6g")
    write_md(df, skipped, args.out_md, args)
    print(f"[valthr] wrote {args.out_csv} ({len(df)} rows) and {args.out_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
