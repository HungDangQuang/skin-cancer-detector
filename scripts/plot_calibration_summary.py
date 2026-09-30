"""
One figure for the whole probability-calibration analysis (thesis Muc 4.9).

WHY ONE FIGURE. Like the two out-of-domain tiers, this is a SINGLE post-hoc pass:
no run is retrained and no image is re-inferred, only the probabilities already
stored per image are re-mapped and ECE recomputed. It covers all 19 runs on all
3 domains. Three panels carry the evidence:

  (a) PRIOR-SHIFT IS ONE CONSTANT, AND ITS SIZE DECIDES EVERYTHING.
      Prior-shift adds logit(pi_target) - logit(pi_train) to every log-odds. That
      one number is fixed by the evaluated set's prevalence, and it explains all
      three outcomes at once: in-domain (pi 0.39%) the constant is large and ECE
      drops ~32x; on HAM10000 (pi 15.6% ~ the sampler's 16.67%) it is ~0 and
      nothing moves; on Fitzpatrick17k (pi 50%) it FLIPS SIGN and ECE doubles.
      Reading "calibration does not help out of domain" off the middle row is the
      classic misreading: the correction did its job, and its job was ~nothing.

  (b) A GLOBAL CONSTANT BREAKS A SUBGROUP.
      Same in-domain runs, cut into all-rows vs the clinical PAD-UFES-20 photos
      (prevalence 34.1%, ~88x the pooled 0.39%). One target prevalence for the
      whole set overshoots on that subgroup: it improves overall in 19/19 and
      degrades the subgroup in 17/19. This is the ranking-axis finding of Muc 4.4
      reappearing on the calibration axis.

  (c) DISTILLATION TRANSFERS THE TEACHER'S CALIBRATION PROFILE, NEAR 1:1.
      Raw in-domain ECE, teacher on x and its four students on y. Four students
      per teacher share architecture set, data, hyperparameters and seed; only the
      teacher differs. They sit on the diagonal. The four no-teacher baselines,
      the same four architectures, scatter over a band 5-20x wider. This is the
      thesis's contribution 2c and the empirical evidence for Muc 2.3.3.

NOTHING IS HARD-CODED. Both prevalences and therefore the log-odds constant are
derived from the calibration artifacts themselves (`pi_train` + per-fold
`pi_target`), so the figure cannot drift away from the splits it describes. The
script refuses to draw when a domain is missing runs rather than plotting a
partial matrix.

TEACHER RUNS NEST ONE LEVEL DEEPER (`experiments/runs/teacher/<name>/` and
`reports/external/<ds>/<var>/teacher/<name>/`), so every lookup globs recursively.
A non-recursive glob silently finds 16 of the 19 runs.

Inputs (all existing artifacts, no GPU, no re-inference):
    experiments/runs/**/calibration_metrics.json              -> panels (a), (b), (c)
    experiments/runs/**/calibration_anatom_site_general.json  -> panel (b) subgroup
    reports/external/<ds>/<variant>/**/calibration_metrics.json -> panel (a)

Runs on the SERVER (needs matplotlib), not the Mac.

Usage:
    bash run/plot_calibration_summary.sh
    python scripts/plot_calibration_summary.py --out reports/calibration_summary.png
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless server: no display, and this must precede pyplot
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

TEACHERS = ["efficientnetv2_m", "maxvit_base", "convnextv2_base"]
STUDENTS = ["mobilenetv4_conv_medium", "fastvit_sa12",
            "efficientformerv2_s2", "repvit_m1_0"]

PRETTY = {
    "efficientnetv2_m": "EfficientNetV2-M", "convnextv2_base": "ConvNeXtV2-Base",
    "maxvit_base": "MaxViT-Base", "mobilenetv4_conv_medium": "MobileNetV4",
    "repvit_m1_0": "RepViT", "fastvit_sa12": "FastViT",
    "efficientformerv2_s2": "EfficientFormerV2",
}

BETTER_ECE = "↓ lower is better"

GOOD = "#2e7d4f"   # correction improved ECE
BAD = "#c0392b"    # correction made ECE worse
GRID = "#dcdcdc"
TEACHER_COLOR = {"efficientnetv2_m": "#2a5d9e", "maxvit_base": "#b07a1e",
                 "convnextv2_base": "#7d4a9e"}
BASE_COLOR = "#9aa0a6"


def _legend(ax, handles, ncol: int = 1, title: str | None = None):
    """House convention: legends sit OUTSIDE the axes, flush to the top-right."""
    return ax.legend(
        handles=handles, ncol=ncol, title=title, title_fontsize=8,
        loc="lower right", bbox_to_anchor=(1.0, 1.005),
        fontsize=8, frameon=False, borderaxespad=0.0, handletextpad=0.5,
        columnspacing=1.4,
    )


def _load(path: Path) -> dict:
    if not path.is_file():
        sys.exit(f"ERROR: missing input {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _run_tag(path: Path, root: Path) -> str:
    """Run identity relative to its root, keeping the `teacher/<name>` prefix."""
    return str(path.parent.relative_to(root))


def _collect(root: Path, name: str = "calibration_metrics.json") -> dict[str, dict]:
    """Every run under `root` that has `name`. Recursive: teachers nest deeper."""
    out: dict[str, dict] = {}
    for path in sorted(root.glob(f"**/{name}")):
        out[_run_tag(path, root)] = _load(path)
    return out


def _logit(p: float) -> float:
    return math.log(p / (1.0 - p))


def _shift_constant(runs: dict[str, dict]) -> float:
    """logit(pi_target) - logit(pi_train), read off the artifacts themselves.

    Every run in a domain scores the same rows under the same sampler, so the
    constant is a property of the domain. Disagreement means two evaluation
    rounds got mixed, which is worth failing on rather than averaging away.
    """
    seen = set()
    for tag, d in runs.items():
        pi_t = {f["pi_target"] for f in d["per_fold"].values()}
        if len(pi_t) != 1:
            sys.exit(f"ERROR: {tag} has {len(pi_t)} different pi_target across folds")
        seen.add((round(pi_t.pop(), 9), round(d["pi_train"], 9)))
    if len(seen) != 1:
        sys.exit(f"ERROR: runs disagree on (pi_target, pi_train): {sorted(seen)}")
    pi_target, pi_train = seen.pop()
    return _logit(pi_target) - _logit(pi_train), pi_target


def _arrow_row(ax, y: float, runs: dict[str, dict], raw_key="ece_raw", cal_key="ece_cal"):
    """One horizontal segment per run, raw -> calibrated, coloured by direction.

    Returns (n_worse, values) — the caller needs the values because `annotate`
    draws outside the data limits, so nothing here autoscales the x axis.
    """
    worse = 0
    seen: list[float] = []
    for i, d in enumerate(runs.values()):
        raw, cal = d[raw_key], d[cal_key]
        worse += cal > raw
        seen += [raw, cal]
        yy = y + (i - (len(runs) - 1) / 2) * 0.030
        ax.annotate(
            "", xy=(cal, yy), xytext=(raw, yy),
            arrowprops=dict(arrowstyle="-|>", color=BAD if cal > raw else GOOD,
                            lw=1.0, alpha=0.75, shrinkA=0, shrinkB=0),
        )
    return worse, seen


def panel_one_constant(ax, domains: list[tuple[str, dict, float, float]]) -> None:
    """(a) The size of the prior-shift constant decides each domain's outcome."""
    labels, seen = [], []
    for y, (name, runs, const, pi) in enumerate(domains):
        worse, vals = _arrow_row(ax, y, runs)
        seen += vals
        n = len(runs)
        verdict = (f"{n - worse}/{n} improved" if worse < n - worse
                   else f"{worse}/{n} made worse")
        ax.text(max(vals) * 1.22, y, verdict, ha="left", va="center", fontsize=8.5,
                color=BAD if worse > n - worse else GOOD)
        labels.append(f"{name}\nprevalence {pi * 100:.2f}%\nconstant {const:+.2f}")

    ax.set_xscale("log")
    ax.set_xlim(min(seen) * 0.55, max(seen) * 3.0)
    ax.set_yticks(range(len(domains)))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_ylim(-0.55, len(domains) - 0.35)
    ax.invert_yaxis()
    ax.set_xlabel(f"ECE, raw → after prior-shift   ·   one arrow = one run\n{BETTER_ECE}",
                  fontsize=9)
    ax.set_title("(a) One constant, and its size decides the outcome",
                 fontsize=10.5, weight="bold", loc="left", pad=28)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    _legend(ax, [
        Line2D([], [], color=GOOD, lw=1.6, label="ECE improved"),
        Line2D([], [], color=BAD, lw=1.6, label="ECE got worse"),
    ], ncol=2)


def panel_subgroup(ax, overall: dict[str, dict], subgroup: dict[str, dict],
                   sub_n: int, sub_prev: float, all_prev: float) -> None:
    """(b) The same global correction that fixes the whole set breaks a subgroup."""
    rows = [
        (f"all test rows\nprevalence {all_prev * 100:.2f}%", overall),
        (f"PAD-UFES-20 clinical photos\n{sub_n:,} images · prevalence {sub_prev * 100:.1f}%",
         subgroup),
    ]
    labels, seen = [], []
    for y, (label, runs) in enumerate(rows):
        worse, vals = _arrow_row(ax, y, runs)
        seen += vals
        n = len(runs)
        ax.text(max(vals) * 1.22, y,
                f"{worse}/{n} made worse" if worse else f"{n}/{n} improved",
                ha="left", va="center", fontsize=8.5, color=BAD if worse else GOOD)
        labels.append(label)

    ax.set_xscale("log")
    ax.set_xlim(min(seen) * 0.55, max(seen) * 2.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_ylim(-0.5, len(rows) - 0.4)
    ax.invert_yaxis()
    ax.set_xlabel(f"In-domain ECE, raw → after prior-shift   ·   one arrow = one run\n"
                  f"{BETTER_ECE}", fontsize=9)
    ax.set_title("(b) The same correction breaks the clinical subgroup",
                 fontsize=10.5, weight="bold", loc="left", pad=28)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    _legend(ax, [
        Line2D([], [], color=GOOD, lw=1.6, label="ECE improved"),
        Line2D([], [], color=BAD, lw=1.6, label="ECE got worse"),
    ], ncol=2)


def panel_inheritance(ax, teacher_ece: dict[str, float],
                      student_ece: dict[str, dict[str, float]],
                      baseline_ece: dict[str, float]) -> None:
    """(c) Students track their own teacher's ECE; baselines have nothing to track."""
    xs = [teacher_ece[t] for t in TEACHERS]
    span = max(xs + list(baseline_ece.values()))
    base_x = span * 1.22  # the no-teacher control gets its own slot on the right

    lo, hi = min(xs) * 0.80, span * 1.05
    ax.plot([lo, hi], [lo, hi], color="#777777", lw=1.0, ls="--", zorder=1)
    # Top-left is the one empty corner: everything sits on or right of the diagonal.
    ax.annotate("dashed line:\nstudent ECE = teacher ECE", (lo, hi),
                textcoords="offset points", xytext=(4, -2), ha="left", va="top",
                fontsize=7.5, color="#555555")

    for t in TEACHERS:
        x = teacher_ece[t]
        ys = [student_ece[t][s] for s in STUDENTS]
        ax.plot([x] * len(ys), ys, "o", ms=7, color=TEACHER_COLOR[t], alpha=0.8,
                markeredgecolor="white", markeredgewidth=0.6, zorder=3)
        ax.plot([x], [x], "*", ms=13, color=TEACHER_COLOR[t],
                markeredgecolor="white", markeredgewidth=0.6, zorder=4)
        ax.annotate(f"{PRETTY[t]}\nspread {max(ys) - min(ys):.4f}", (x, min(ys)),
                    textcoords="offset points", xytext=(0, -13), ha="center",
                    va="top", fontsize=7.5, color=TEACHER_COLOR[t])

    ys = list(baseline_ece.values())
    ax.plot([base_x] * len(ys), ys, "o", ms=7, color=BASE_COLOR, alpha=0.85,
            markeredgecolor="white", markeredgewidth=0.6, zorder=3)
    ax.annotate(f"no teacher\nspread {max(ys) - min(ys):.4f}", (base_x, min(ys)),
                textcoords="offset points", xytext=(0, -13), ha="center", va="top",
                fontsize=7.5, color="#555555")
    ax.axvspan(base_x * 0.955, base_x * 1.045, color="#f0f0f0", zorder=0)

    all_y = [v for t_ in TEACHERS for v in student_ece[t_].values()] + list(baseline_ece.values()) + xs
    ax.set_ylim(min(all_y) - (max(all_y) - min(all_y)) * 0.22,
                max(all_y) + (max(all_y) - min(all_y)) * 0.10)
    ax.set_xlim(lo * 0.92, base_x * 1.10)
    ax.set_xticks(xs + [base_x])
    ax.set_xticklabels([f"{v:.4f}" for v in xs] + ["none"], fontsize=8)
    ax.set_xlabel(f"ECE of the teacher this student learned from\n"
                  f"★ = the teacher itself   ·   {BETTER_ECE}", fontsize=9)
    ax.set_ylabel(f"Raw ECE of the student   ·   {BETTER_ECE}", fontsize=9)
    ax.set_title("(c) KD inherits the teacher's calibration",
                 fontsize=10.5, weight="bold", loc="left", pad=28)
    ax.grid(color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    _legend(ax, [
        Line2D([], [], color=TEACHER_COLOR[t], lw=0, marker="o", ms=6,
               label=PRETTY[t]) for t in TEACHERS
    ] + [Line2D([], [], color=BASE_COLOR, lw=0, marker="o", ms=6,
                label="baseline, no KD")], ncol=4)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--indomain-dir", type=Path, default=Path("experiments/runs"))
    ap.add_argument("--ham-dir", type=Path,
                    default=Path("reports/external/ham10000/headline"))
    ap.add_argument("--fitz-dir", type=Path,
                    default=Path("reports/external/fitzpatrick17k/headline"))
    ap.add_argument("--subgroup-file", default="calibration_anatom_site_general.json")
    ap.add_argument("--subgroup-key", default="nan",
                    help="the anatomical-site bucket that IS the PAD clinical photos")
    ap.add_argument("--out", type=Path, default=Path("reports/calibration_summary.png"))
    ap.add_argument("--dpi", type=int, default=200)
    args = ap.parse_args()

    ind = _collect(args.indomain_dir)
    ham = _collect(args.ham_dir)
    fitz = _collect(args.fitz_dir)
    for name, runs in (("in-domain", ind), ("HAM10000", ham), ("Fitzpatrick17k", fitz)):
        if not runs:
            sys.exit(f"ERROR: no calibration_metrics.json found for {name}")
    # A domain missing runs would silently redraw a different experiment.
    if not (len(ind) == len(ham) == len(fitz)):
        sys.exit(f"ERROR: run counts differ (in-domain {len(ind)}, HAM {len(ham)}, "
                 f"Fitzpatrick {len(fitz)}); re-run scripts/compute_calibration.py "
                 f"so all three domains cover the same runs")

    domains = []
    for name, runs in (("in-domain", ind), ("HAM10000", ham), ("Fitzpatrick17k", fitz)):
        const, pi = _shift_constant(runs)
        domains.append((name, {k: v["mean"] for k, v in runs.items()}, const, pi))

    # Panel (b): the subgroup cut lives in a sibling file, same runs.
    sub_raw = _collect(args.indomain_dir, args.subgroup_file)
    missing = sorted(set(ind) - set(sub_raw))
    if missing:
        sys.exit(f"ERROR: {len(missing)} run(s) have no {args.subgroup_file}: {missing[:3]}")
    subgroup, sub_n, sub_prev = {}, None, None
    for tag, d in sub_raw.items():
        g = (d.get("subgroups") or {}).get(args.subgroup_key)
        if g is None:
            sys.exit(f"ERROR: subgroup '{args.subgroup_key}' absent from {tag}")
        subgroup[tag] = g
        sub_n, sub_prev = g["n"], g["prevalence"]

    teacher_ece = {t: ind[f"teacher/{t}"]["mean"]["ece_raw"] for t in TEACHERS}
    student_ece = {t: {s: ind[f"kd_{t}_to_{s}"]["mean"]["ece_raw"] for s in STUDENTS}
                   for t in TEACHERS}
    baseline_ece = {s: ind[f"baseline_{s}"]["mean"]["ece_raw"] for s in STUDENTS}

    fig = plt.figure(figsize=(18.6, 6.6), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.12, 0.96, 1.18])
    panel_one_constant(fig.add_subplot(gs[0, 0]), domains)
    panel_subgroup(fig.add_subplot(gs[0, 1]), {k: v["mean"] for k, v in ind.items()},
                   subgroup, sub_n, sub_prev, domains[0][3])
    panel_inheritance(fig.add_subplot(gs[0, 2]), teacher_ece, student_ece, baseline_ece)

    n_fold = next(iter(ind.values()))["n_folds"]
    fig.suptitle(
        f"Probability calibration is a property of the domain — {len(ind)} runs × "
        f"3 domains × {n_fold} folds, post-hoc only: no retraining, no re-inference, "
        f"and every ranking metric unchanged",
        fontsize=12, weight="bold", x=0.006, ha="left",
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=args.dpi)
    svg = args.out.with_suffix(".svg")
    fig.savefig(svg)
    print(f"[plot] wrote {args.out} and {svg}")


if __name__ == "__main__":
    main()
