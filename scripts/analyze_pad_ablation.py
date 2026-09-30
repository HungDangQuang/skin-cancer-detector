#!/usr/bin/env python
"""
Analyze the PAD-mixing ablation: compare an ISIC+PAD ("with-PAD") training arm
against an ISIC-only ("no-PAD") arm on an IDENTICAL held-out combined test set,
broken down BY SOURCE domain (isic2024 vs pad_ufes_20).

Both arms must have been trained on the same fixed test split, so the only
difference is whether PAD rows were in TRAIN+VAL. Each arm is a run root holding
fold_*/predictions.csv (y_true,y_prob,y_pred,source) — written by
Evaluator.save_predictions during training.

The decisive cell for the "PAD helps smartphone-domain generalization" claim is
the **pad_ufes_20** test subset (plan: reports/2026-06-21_data_strategy_ablation_plan.md §3).
Ranking metrics (AUPRC / pAUC / AUC) are threshold-invariant; sensitivity here is
reported at each subset's own Youden threshold, matching compute_metrics' default.

Usage:
    python scripts/analyze_pad_ablation.py \
        --with-pad-dir experiments/runs/teacher/efficientnetv2_m \
        --no-pad-dir   experiments/runs_noPAD/teacher/efficientnetv2_m \
        --out reports/pad_ablation_efficientnetv2_m.md

Win rule (per subset): with-PAD wins iff ΔAUPRC > 0 AND ΔSens > 0.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.evaluation.metrics import compute_metrics  # noqa: E402

# Metrics reported in the comparison tables (headline first).
REPORTED = ["auprc", "pauc_at_tpr80", "auc_roc", "sensitivity", "specificity",
            "sens_at_95spec", "prevalence"]
SUBSETS = ["all", "isic2024", "pad_ufes_20"]


def _load_predictions(fold_dir: Path) -> list[dict]:
    """Read one fold's predictions.csv into a list of {y_true,y_prob,source}."""
    csv_path = fold_dir / "predictions.csv"
    if not csv_path.is_file():
        return []
    rows = []
    with csv_path.open() as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "y_true": int(r["y_true"]),
                "y_prob": float(r["y_prob"]),
                "source": r.get("source", "unknown"),
            })
    return rows


def _metrics_for_subset(rows: list[dict], subset: str) -> dict | None:
    """compute_metrics over one source subset ('all' = whole test)."""
    if subset != "all":
        rows = [r for r in rows if r["source"] == subset]
    if not rows:
        return None
    y_true = [r["y_true"] for r in rows]
    y_prob = np.array([r["y_prob"] for r in rows])
    # A subset with only one class can't yield AUC/AUPRC — skip it loudly.
    if len(set(y_true)) < 2:
        return None
    return compute_metrics(y_true, y_prob)


def _arm_summary(run_dir: Path) -> dict[str, dict[str, dict]]:
    """Per-subset mean±std across all folds for one training arm."""
    fold_dirs = sorted(run_dir.glob("fold_*"))
    if not fold_dirs:
        raise SystemExit(f"ERROR: no fold_*/ under {run_dir}")

    # subset -> metric -> list of per-fold values
    acc: dict[str, dict[str, list[float]]] = {s: {} for s in SUBSETS}
    n_folds_used = 0
    for fd in fold_dirs:
        rows = _load_predictions(fd)
        if not rows:
            continue
        n_folds_used += 1
        for subset in SUBSETS:
            m = _metrics_for_subset(rows, subset)
            if m is None:
                continue
            for k in REPORTED:
                if k in m:
                    acc[subset].setdefault(k, []).append(float(m[k]))

    if n_folds_used == 0:
        raise SystemExit(f"ERROR: no fold_*/predictions.csv found under {run_dir}")

    summary: dict[str, dict[str, dict]] = {}
    for subset in SUBSETS:
        summary[subset] = {
            k: {"mean": float(np.mean(v)), "std": float(np.std(v)), "n": len(v)}
            for k, v in acc[subset].items()
        }
    summary["_n_folds"] = n_folds_used  # type: ignore[assignment]
    return summary


def _fmt(d: dict | None) -> str:
    if not d:
        return "—"
    return f"{d['mean']:.4f} ± {d['std']:.4f}"


def build_report(with_pad: dict, no_pad: dict, name: str) -> str:
    lines: list[str] = []
    lines.append(f"# PAD-mixing ablation — {name}\n")
    lines.append("Identical combined held-out test; only TRAIN+VAL differ "
                 "(with-PAD = ISIC+PAD, no-PAD = ISIC-only).\n")
    lines.append(f"- with-PAD folds: {with_pad.get('_n_folds')}  |  "
                 f"no-PAD folds: {no_pad.get('_n_folds')}\n")

    for subset in SUBSETS:
        title = {"all": "Whole test (ISIC+PAD)",
                 "isic2024": "ISIC-source subset",
                 "pad_ufes_20": "PAD-source subset  ← decisive cell"}[subset]
        lines.append(f"\n## {title}\n")
        lines.append("| Metric | no-PAD (ISIC-only) | with-PAD (ISIC+PAD) | Δ (with − no) |")
        lines.append("|---|---|---|---|")
        wp, np_ = with_pad.get(subset, {}), no_pad.get(subset, {})
        for k in REPORTED:
            a, b = np_.get(k), wp.get(k)
            delta = f"{b['mean'] - a['mean']:+.4f}" if (a and b) else "—"
            lines.append(f"| {k} | {_fmt(a)} | {_fmt(b)} | {delta} |")

        # Verdict for this subset (win iff ΔAUPRC>0 AND ΔSens>0).
        a_ap, b_ap = np_.get("auprc"), wp.get("auprc")
        a_se, b_se = np_.get("sensitivity"), wp.get("sensitivity")
        if a_ap and b_ap and a_se and b_se:
            d_ap = b_ap["mean"] - a_ap["mean"]
            d_se = b_se["mean"] - a_se["mean"]
            win = d_ap > 0 and d_se > 0
            verdict = "✅ PAD HELPS" if win else "❌ no clear win"
            lines.append(f"\n**Verdict:** {verdict} "
                         f"(ΔAUPRC={d_ap:+.4f}, ΔSens={d_se:+.4f}; "
                         f"win iff both > 0)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--with-pad-dir", required=True, type=Path,
                   help="Run root of the ISIC+PAD arm (holds fold_*/predictions.csv)")
    p.add_argument("--no-pad-dir", required=True, type=Path,
                   help="Run root of the ISIC-only arm (holds fold_*/predictions.csv)")
    p.add_argument("--out", type=Path, default=None,
                   help="Write the Markdown report here (also printed to stdout)")
    args = p.parse_args()

    name = args.with_pad_dir.name
    with_pad = _arm_summary(args.with_pad_dir)
    no_pad = _arm_summary(args.no_pad_dir)
    report = build_report(with_pad, no_pad, name)

    print(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report)
        json_out = args.out.with_suffix(".json")
        json_out.write_text(json.dumps(
            {"name": name, "with_pad": with_pad, "no_pad": no_pad}, indent=2))
        print(f"\nWrote {args.out}\nWrote {json_out}", file=sys.stderr)


if __name__ == "__main__":
    main()
