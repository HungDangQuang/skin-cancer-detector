"""
Aggregate per-fold test_metrics.json files into mean ± std.

Usage:
    python scripts/aggregate_folds.py --run-dir experiments/runs/teacher/efficientnetv2_m
    python scripts/aggregate_folds.py --run-dir experiments/runs/kd_efficientnetv2_m_to_efficientformerv2_s2

Expects layout:
    <run-dir>/fold_0/test_metrics.json
    <run-dir>/fold_1/test_metrics.json
    ...
    <run-dir>/fold_4/test_metrics.json

Writes:
    <run-dir>/aggregated.json   — mean, std, min, max, per-fold values for each metric
    <run-dir>/aggregated.md     — short markdown summary table for thesis/report use
"""
import argparse
import json
import sys
from pathlib import Path
from statistics import mean, stdev


def load_fold_metrics(run_dir: Path) -> dict[int, dict]:
    """Return {fold_idx: metrics_dict} for every fold_*/test_metrics.json found."""
    found = {}
    for fold_dir in sorted(run_dir.glob("fold_*")):
        if not fold_dir.is_dir():
            continue
        try:
            idx = int(fold_dir.name.removeprefix("fold_"))
        except ValueError:
            continue
        metrics_path = fold_dir / "test_metrics.json"
        if not metrics_path.exists():
            print(f"WARN: missing {metrics_path}", file=sys.stderr)
            continue
        with open(metrics_path) as f:
            found[idx] = json.load(f)
    return found


def aggregate(per_fold: dict[int, dict]) -> dict:
    """Compute mean/std/min/max across folds for every numeric metric."""
    if not per_fold:
        return {"n_folds": 0, "metrics": {}}

    # Union of metric keys present in any fold; only aggregate numeric ones.
    all_keys = set()
    for m in per_fold.values():
        all_keys.update(m.keys())

    agg = {}
    for key in sorted(all_keys):
        values = [m[key] for m in per_fold.values() if isinstance(m.get(key), (int, float))]
        if len(values) < 1:
            continue
        agg[key] = {
            "mean": mean(values),
            "std": stdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
            "n": len(values),
            "per_fold": {idx: per_fold[idx][key] for idx in sorted(per_fold) if key in per_fold[idx]},
        }
    return {"n_folds": len(per_fold), "fold_ids": sorted(per_fold.keys()), "metrics": agg}


def write_markdown_summary(agg: dict, run_dir: Path, out_path: Path) -> None:
    """Thesis-grade markdown report. Lists EVERY metric from every fold —
    headline rates first, then confusion counts, then anything else, then a
    per-fold matrix so the reader can recompute mean/std and verify."""
    headline_metrics = [
        "pauc_at_tpr80", "auc_roc", "auprc", "accuracy",
        "precision", "recall",
        "sensitivity", "specificity", "f1_score",
        "sens_at_90spec", "sens_at_95spec",
    ]
    count_metrics = ["tp", "fp", "tn", "fn", "threshold"]

    lines = []
    lines.append(f"# 5-fold CV aggregate — `{run_dir.name}`")
    lines.append("")
    lines.append(f"Folds aggregated: {agg['n_folds']} ({agg.get('fold_ids', [])})")
    lines.append("")

    lines.append("## Headline metrics (rates)")
    lines.append("")
    lines.append("| Metric | Mean | Std | Min | Max |")
    lines.append("|---|---|---|---|---|")
    for k in headline_metrics:
        if k not in agg["metrics"]:
            continue
        m = agg["metrics"][k]
        lines.append(f"| {k} | {m['mean']:.4f} | {m['std']:.4f} | {m['min']:.4f} | {m['max']:.4f} |")

    listed = set(headline_metrics)

    present_count_metrics = [k for k in count_metrics if k in agg["metrics"]]
    if present_count_metrics:
        lines.append("")
        lines.append("## Confusion counts & threshold")
        lines.append("")
        lines.append("| Metric | Mean | Std | Min | Max |")
        lines.append("|---|---|---|---|---|")
        for k in present_count_metrics:
            m = agg["metrics"][k]
            lines.append(f"| {k} | {m['mean']:.4f} | {m['std']:.4f} | {m['min']:.4f} | {m['max']:.4f} |")
        listed.update(present_count_metrics)

    other_keys = sorted(k for k in agg["metrics"] if k not in listed and not k.startswith("_"))
    if other_keys:
        lines.append("")
        lines.append("## Other recorded metrics")
        lines.append("")
        lines.append("| Metric | Mean | Std | Min | Max |")
        lines.append("|---|---|---|---|---|")
        for k in other_keys:
            m = agg["metrics"][k]
            lines.append(f"| {k} | {m['mean']:.4f} | {m['std']:.4f} | {m['min']:.4f} | {m['max']:.4f} |")

    # Per-fold matrix — every metric × every fold. Source-of-truth for the means above.
    all_metric_keys = sorted(k for k in agg["metrics"] if not k.startswith("_"))
    fold_ids = agg.get("fold_ids", [])
    if all_metric_keys and fold_ids:
        lines.append("")
        lines.append("## Per-fold matrix (raw values)")
        lines.append("")
        header = "| metric | " + " | ".join(f"fold_{i}" for i in fold_ids) + " |"
        sep = "|---|" + "|".join("---" for _ in fold_ids) + "|"
        lines.append(header)
        lines.append(sep)
        for k in all_metric_keys:
            per_fold = agg["metrics"][k]["per_fold"]
            row = [f"| {k}"]
            for i in fold_ids:
                v = per_fold.get(i)
                row.append(f"{v:.4f}" if isinstance(v, float) else str(v) if v is not None else "—")
            lines.append(" | ".join(row) + " |")

    out_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path,
                        help="Directory containing fold_0/, fold_1/, ... subdirs")
    args = parser.parse_args()

    if not args.run_dir.is_dir():
        print(f"ERROR: not a directory: {args.run_dir}", file=sys.stderr)
        sys.exit(1)

    per_fold = load_fold_metrics(args.run_dir)
    if not per_fold:
        print(f"ERROR: no fold_*/test_metrics.json found under {args.run_dir}", file=sys.stderr)
        sys.exit(1)

    agg = aggregate(per_fold)
    json_out = args.run_dir / "aggregated.json"
    md_out = args.run_dir / "aggregated.md"
    json_out.write_text(json.dumps(agg, indent=2))
    write_markdown_summary(agg, args.run_dir, md_out)
    print(f"Wrote {json_out} ({agg['n_folds']} folds)")
    print(f"Wrote {md_out}")


if __name__ == "__main__":
    main()
