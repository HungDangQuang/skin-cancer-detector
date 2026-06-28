"""
Cross-run comparison of teacher / student training results to judge whether
Knowledge Distillation (KD) helps and to find the best teacher-student pair.

Scans the fold-scoped run-dir tree written by train_teacher.py / train_student.py:

    experiments/runs/
      teacher/<name>/fold_{0..4}/test_metrics.json          (teacher reference)
      baseline_<student>/fold_{0..4}/test_metrics.json       (student, NO KD)
      kd_<teacher>_to_<student>/fold_{0..4}/test_metrics.json (student, WITH KD)

For every (teacher -> student) KD run it pairs against the matching
baseline_<student> run, aggregates each across folds (mean +/- std), and reports
the KD delta. Two rankings are produced (the user asked for both):
  A) by absolute student performance  (AUPRC, then pAUC@TPR80)
  B) by KD improvement                (delta AUPRC, then delta pAUC@TPR80)

Pure stdlib — runs on the Mac (after rsync of the JSONs) or on the cluster.
No torch / numpy / sklearn import, so it never needs the cluster venv.

Usage:
    python scripts/compare_kd_results.py
    python scripts/compare_kd_results.py --runs-dir experiments/runs \
        --out-md reports/comparison/kd_comparison.md \
        --out-json reports/comparison/kd_comparison.json
    python scripts/compare_kd_results.py --include-ablations   # keep __suffix runs
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean, stdev

# Metrics shown first (headline) — order matters for ranking and table layout.
# All are higher-is-better. AUPRC is the headline at ~0.4% prevalence (AUC-ROC is
# optimistic); pauc_at_tpr80 is the official ISIC 2024 metric.
PRIORITY_METRICS = [
    "auprc",
    "pauc_at_tpr80",
    "auc_roc",
    "sensitivity",
    "sens_at_95spec",
    "sens_at_90spec",
    "specificity",
    "f1_score",
]
# Ranking keys (in tie-break order) for the two views.
PERF_KEYS = ["auprc", "pauc_at_tpr80"]
DELTA_KEYS = ["auprc", "pauc_at_tpr80"]


# --------------------------------------------------------------------------- #
# Discovery + aggregation
# --------------------------------------------------------------------------- #
def split_suffix(name: str) -> tuple[str, str]:
    """`kd_a_to_b__ratio3` -> ('kd_a_to_b', '__ratio3'); no suffix -> (name, '')."""
    idx = name.find("__")
    return (name[:idx], name[idx:]) if idx != -1 else (name, "")


def parse_run_name(rel: str) -> dict | None:
    """Classify a run directory (relative to runs_dir) into kind/teacher/student/suffix.

    Returns None for directories that aren't a recognized run.
    """
    parts = Path(rel).parts
    if parts and parts[0] == "teacher" and len(parts) >= 2:
        base, suffix = split_suffix(parts[1])
        return {"kind": "teacher", "teacher": base, "student": None, "suffix": suffix}
    name = parts[0]
    base, suffix = split_suffix(name)
    if base.startswith("kd_") and "_to_" in base:
        teacher, student = base[len("kd_"):].split("_to_", 1)
        return {"kind": "kd", "teacher": teacher, "student": student, "suffix": suffix}
    if base.startswith("baseline_"):
        return {"kind": "baseline", "teacher": None,
                "student": base[len("baseline_"):], "suffix": suffix}
    return None


def find_run_dirs(runs_dir: Path) -> list[tuple[str, Path]]:
    """Return (relative-name, abs-path) for every dir holding fold_*/test_metrics.json
    (or a bare test_metrics.json). teacher/<name> is matched one level deeper."""
    found = []
    if not runs_dir.is_dir():
        return found
    candidates = [p for p in runs_dir.iterdir() if p.is_dir()]
    # teacher/* lives one level down
    tdir = runs_dir / "teacher"
    if tdir.is_dir():
        candidates += [p for p in tdir.iterdir() if p.is_dir()]
    for p in candidates:
        if p.name == "teacher" and p.parent == runs_dir:
            continue  # the container, not a run
        has_folds = any((fd / "test_metrics.json").is_file()
                        for fd in p.glob("fold_*"))
        if has_folds or (p / "test_metrics.json").is_file():
            found.append((str(p.relative_to(runs_dir)), p))
    return found


def load_fold_metrics(run_dir: Path) -> dict[int, dict]:
    """{fold_idx: metrics} for each fold_*/test_metrics.json; falls back to a bare
    test_metrics.json as fold -1 when no fold_* dirs exist."""
    per_fold: dict[int, dict] = {}
    for fold_dir in sorted(run_dir.glob("fold_*")):
        mp = fold_dir / "test_metrics.json"
        if mp.is_file():
            try:
                per_fold[int(fold_dir.name.split("_")[1])] = json.loads(mp.read_text())
            except (ValueError, json.JSONDecodeError) as e:
                print(f"WARN: bad {mp}: {e}", file=sys.stderr)
    if not per_fold and (run_dir / "test_metrics.json").is_file():
        try:
            per_fold[-1] = json.loads((run_dir / "test_metrics.json").read_text())
        except json.JSONDecodeError as e:
            print(f"WARN: bad {run_dir/'test_metrics.json'}: {e}", file=sys.stderr)
    return per_fold


def aggregate(per_fold: dict[int, dict]) -> dict:
    """{metric: {mean,std,min,max,n}} over folds for every numeric metric."""
    keys: set[str] = set()
    for m in per_fold.values():
        keys |= {k for k, v in m.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    agg = {}
    for k in keys:
        vals = [m[k] for m in per_fold.values() if isinstance(m.get(k), (int, float))]
        if not vals:
            continue
        agg[k] = {
            "mean": mean(vals),
            "std": stdev(vals) if len(vals) > 1 else 0.0,
            "min": min(vals), "max": max(vals), "n": len(vals),
        }
    return {"metrics": agg, "n_folds": len(per_fold), "fold_ids": sorted(per_fold)}


# --------------------------------------------------------------------------- #
# Formatting helpers
# --------------------------------------------------------------------------- #
def m_mean(agg: dict, key: str):
    return agg["metrics"].get(key, {}).get("mean")


def fmt(agg: dict, key: str) -> str:
    e = agg["metrics"].get(key)
    return f"{e['mean']:.4f} ± {e['std']:.4f}" if e else "—"


def fmt_delta(d) -> str:
    if d is None:
        return "—"
    arrow = "▲" if d > 1e-9 else ("▼" if d < -1e-9 else "≈")
    return f"{d:+.4f} {arrow}"


# --------------------------------------------------------------------------- #
# Build comparison
# --------------------------------------------------------------------------- #
def build(runs_dir: Path, include_ablations: bool, students_filter: set[str] | None):
    runs = find_run_dirs(runs_dir)
    teachers: dict[tuple, dict] = {}     # (name, suffix) -> agg
    baselines: dict[tuple, dict] = {}    # (student, suffix) -> agg
    kds: list[dict] = []                 # each: teacher/student/suffix/agg

    for rel, path in runs:
        info = parse_run_name(rel)
        if info is None:
            continue
        if info["suffix"] and not include_ablations:
            continue
        agg = aggregate(load_fold_metrics(path))
        if agg["n_folds"] == 0:
            continue
        agg["run"] = rel
        if info["kind"] == "teacher":
            teachers[(info["teacher"], info["suffix"])] = agg
        elif info["kind"] == "baseline":
            baselines[(info["student"], info["suffix"])] = agg
        elif info["kind"] == "kd":
            kds.append({**info, "agg": agg})

    pairs = []
    for kd in kds:
        student, suffix = kd["student"], kd["suffix"]
        if students_filter and student not in students_filter:
            continue
        base = baselines.get((student, suffix))
        teacher = teachers.get((kd["teacher"], suffix))
        deltas = {}
        if base:
            for k in PRIORITY_METRICS:
                a, b = m_mean(kd["agg"], k), m_mean(base, k)
                deltas[k] = (a - b) if (a is not None and b is not None) else None
        pairs.append({
            "teacher": kd["teacher"], "student": student, "suffix": suffix,
            "kd": kd["agg"], "baseline": base, "teacher_agg": teacher,
            "deltas": deltas,
        })
    return pairs, teachers, baselines


def rank_perf(pairs):
    def key(p):
        return tuple(-(m_mean(p["kd"], k) or -1) for k in PERF_KEYS)
    return sorted(pairs, key=key)


def rank_delta(pairs):
    def key(p):
        return tuple(-(p["deltas"].get(k) if p["deltas"].get(k) is not None else -9)
                     for k in DELTA_KEYS)
    return sorted([p for p in pairs if p["baseline"]], key=key)


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def render_md(pairs, teachers, runs_dir: Path) -> str:
    L = ["# KD vs Baseline — teacher/student comparison", "",
         f"Source: `{runs_dir}`  |  metric = mean ± std across folds  |  "
         "Δ = KD − baseline (▲ better, ▼ worse).", "",
         "Headline metric is **AUPRC** (prevalence ~0.4% makes AUC-ROC optimistic); "
         "**pAUC@TPR80** is the official ISIC 2024 metric.", ""]

    if not pairs:
        L.append("**No KD runs found.** Train students first "
                 "(`12_train_student.slurm`) and rsync `experiments/runs/`.")
        return "\n".join(L)

    # 1. Core KD-effect table (priority metrics, KD vs baseline + delta)
    L += ["## 1. Does KD help? (per teacher → student)", ""]
    head = ["teacher → student"]
    for k in PRIORITY_METRICS:
        head += [f"{k} (KD)", f"{k} (base)", f"Δ{k}"]
    L.append("| " + " | ".join(head) + " |")
    L.append("|" + "---|" * len(head))
    for p in rank_perf(pairs):
        tag = f"`{p['teacher']}` → `{p['student']}`" + (f" `{p['suffix']}`" if p["suffix"] else "")
        row = [tag]
        for k in PRIORITY_METRICS:
            row += [fmt(p["kd"], k),
                    fmt(p["baseline"], k) if p["baseline"] else "—",
                    fmt_delta(p["deltas"].get(k))]
        L.append("| " + " | ".join(row) + " |")
    L.append("")

    # 2. Ranking A — by student performance
    L += ["## 2. Ranking A — best student performance (KD runs, by AUPRC then pAUC)", "",
          "| rank | teacher → student | AUPRC | pAUC@TPR80 | AUC-ROC | Sensitivity |",
          "|---|---|---|---|---|---|"]
    for i, p in enumerate(rank_perf(pairs), 1):
        L.append(f"| {i} | `{p['teacher']}`→`{p['student']}`{p['suffix']} | "
                 f"{fmt(p['kd'],'auprc')} | {fmt(p['kd'],'pauc_at_tpr80')} | "
                 f"{fmt(p['kd'],'auc_roc')} | {fmt(p['kd'],'sensitivity')} |")
    L.append("")

    # 3. Ranking B — by KD improvement
    rd = rank_delta(pairs)
    L += ["## 3. Ranking B — biggest KD improvement (Δ vs same student's baseline)", "",
          "| rank | teacher → student | ΔAUPRC | ΔpAUC@TPR80 | ΔAUC-ROC | ΔSensitivity |",
          "|---|---|---|---|---|---|"]
    for i, p in enumerate(rd, 1):
        L.append(f"| {i} | `{p['teacher']}`→`{p['student']}`{p['suffix']} | "
                 f"{fmt_delta(p['deltas'].get('auprc'))} | {fmt_delta(p['deltas'].get('pauc_at_tpr80'))} | "
                 f"{fmt_delta(p['deltas'].get('auc_roc'))} | {fmt_delta(p['deltas'].get('sensitivity'))} |")
    if not rd:
        L.append("| — | (no matching baseline_<student> runs to compare) | — | — | — | — |")
    L.append("")

    # 4. Teacher reference
    if teachers:
        L += ["## 4. Teacher reference (standalone, for teacher vs student gap)", "",
              "| teacher | AUPRC | pAUC@TPR80 | AUC-ROC | Sensitivity |",
              "|---|---|---|---|---|"]
        for (name, suffix), agg in sorted(teachers.items()):
            L.append(f"| `{name}`{suffix} | {fmt(agg,'auprc')} | {fmt(agg,'pauc_at_tpr80')} | "
                     f"{fmt(agg,'auc_roc')} | {fmt(agg,'sensitivity')} |")
        L.append("")

    # 5. Verdict
    L += ["## 5. Verdict — did KD help?", ""]
    comparable = [p for p in pairs if p["baseline"]]
    if not comparable:
        L.append("No (KD, baseline) pairs share a student — cannot judge KD effect yet. "
                 "Run each student both with KD (`distillation`) and without (`baseline`).")
    else:
        for headline in ("auprc", "pauc_at_tpr80"):
            pos = sum(1 for p in comparable if (p["deltas"].get(headline) or 0) > 0)
            tot = sum(1 for p in comparable if p["deltas"].get(headline) is not None)
            mean_d = mean([p["deltas"][headline] for p in comparable
                           if p["deltas"].get(headline) is not None]) if tot else 0.0
            verdict = "HELPS" if mean_d > 0 and pos * 2 >= tot else (
                "MIXED" if pos else "DOES NOT HELP")
            L.append(f"- **{headline}**: KD improved {pos}/{tot} students "
                     f"(mean Δ = {mean_d:+.4f}) → **{verdict}**")
        best = rank_perf(comparable)[0]
        L.append("")
        L.append(f"**Best pair (performance):** `{best['teacher']}` → `{best['student']}`"
                 f"{best['suffix']} — AUPRC {fmt(best['kd'],'auprc')}, "
                 f"pAUC {fmt(best['kd'],'pauc_at_tpr80')}.")
        rd = rank_delta(comparable)
        if rd:
            top = rd[0]
            L.append(f"**Best pair (KD effect):** `{top['teacher']}` → `{top['student']}`"
                     f"{top['suffix']} — ΔAUPRC {fmt_delta(top['deltas'].get('auprc'))}, "
                     f"ΔpAUC {fmt_delta(top['deltas'].get('pauc_at_tpr80'))}.")
    return "\n".join(L)


def to_json(pairs, teachers) -> dict:
    return {
        "pairs": [{
            "teacher": p["teacher"], "student": p["student"], "suffix": p["suffix"],
            "kd": p["kd"]["metrics"], "kd_n_folds": p["kd"]["n_folds"],
            "baseline": p["baseline"]["metrics"] if p["baseline"] else None,
            "deltas": p["deltas"],
        } for p in pairs],
        "teachers": {f"{n}{s}": a["metrics"] for (n, s), a in teachers.items()},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", type=Path, default=Path("experiments/runs"))
    ap.add_argument("--out-md", type=Path, default=Path("reports/comparison/kd_comparison.md"))
    ap.add_argument("--out-json", type=Path, default=Path("reports/comparison/kd_comparison.json"))
    ap.add_argument("--include-ablations", action="store_true",
                    help="include __suffix ablation runs (default: main runs only)")
    ap.add_argument("--students", default=None,
                    help="comma-separated student names to restrict to")
    args = ap.parse_args()

    sfilter = set(args.students.split(",")) if args.students else None
    pairs, teachers, _ = build(args.runs_dir, args.include_ablations, sfilter)
    md = render_md(pairs, teachers, args.runs_dir)

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(md)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(to_json(pairs, teachers), indent=2))

    print(md)
    print(f"\n[compare] wrote {args.out_md} and {args.out_json}")
    if not pairs:
        sys.exit(0)


if __name__ == "__main__":
    main()
