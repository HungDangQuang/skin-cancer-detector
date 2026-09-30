"""
One figure for the whole HAM10000 cross-domain evaluation (thesis Muc 4.7).

WHY ONE FIGURE. Muc 4.7 reports a SINGLE experiment — every trained run scored,
unchanged, on one out-of-domain test set — but it had grown four tables that each
showed a slice of it. Three panels carry the same evidence and let the reader see
the shape instead of parsing 12x6 cells:

  (a) FOREST PLOT of the paired KD delta on AUPRC, one row per KD pair.
      The vertical line at 0 does the work: a bar clear of it is a run where
      distillation helped by more than the test set's sampling error. This is the
      "did KD survive the domain change?" panel.

  (b) SCATTER of achieved AUPRC (x) against that same delta (y).
      Two DIFFERENT questions get two different answers and the table hid it: the
      pair that GAINS most from KD is not the pair that SCORES best. The downward
      trend is the inverse law of Muc 4.3 (r = -0.963 in-domain) reappearing on an
      independent evaluation tier.

  (c) DUMBBELL of Sens@90%Spec in-domain vs on HAM10000, one row per run-dir.
      Specificity is FIXED at 90% on both ends, so the threshold has already been
      re-picked per domain; sensitivity still collapses. That is why Muc 4.7 can
      say the loss is ranking capability, not a mis-set threshold.

Bars/segments are PAIRED BOOTSTRAP intervals, not fold std. The fold std is the
spread between five models scored on the same rows; the CI is the test set's
sampling error, which is what "is this gap real?" needs.

Panel (c) uses sens_at_90spec on BOTH ends on purpose — it is the operating point
both bootstrap reports carry, so the two halves of the comparison come from the
same estimator rather than from a fold-mean on one side and a CI on the other.

Inputs (both are artifacts, nothing hard-coded):
    reports/external/ham10000/<variant>/bootstrap_ci.json
        -> per_run.<run>.<metric>{point,lo,hi}, kd_deltas.<run>.<metric>{...}
    experiments/runs/bootstrap_ci.json
        -> per_run.<run>.sens_at_90spec{point,lo,hi}   (the in-domain end of (c))

Runs on the SERVER (needs matplotlib), not the Mac.

Usage:
    bash run/plot_ham_summary.sh
    python scripts/plot_ham_summary.py --out reports/ham_summary.png
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless server: no display, and this must precede pyplot
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

# Teacher order fixes the colour assignment so redraws stay visually stable.
TEACHERS = ["efficientnetv2_m", "convnextv2_base", "maxvit_base"]
TEACHER_COLOR = {
    "efficientnetv2_m": "#2a5d9e",
    "convnextv2_base": "#1b7f5f",
    "maxvit_base": "#b07a1e",
}
TEACHER_LABEL = {
    "efficientnetv2_m": "EfficientNetV2-M",
    "convnextv2_base": "ConvNeXtV2-Base",
    "maxvit_base": "MaxViT-Base",
}
STUDENT_LABEL = {
    "mobilenetv4_conv_medium": "MobileNetV4",
    "repvit_m1_0": "RepViT",
    "fastvit_sa12": "FastViT",
    "efficientformerv2_s2": "EfficientFormerV2",
}

SIG_COLOR = "#c0392b"  # interval clear of 0
NULL_COLOR = "#9aa0a6"  # interval touching 0
GRID = "#dcdcdc"

# Figure text is ENGLISH even though the thesis body is Vietnamese: the figure is
# the part that travels (slides, a paper draft, an external reader), and mixing
# the two inside one axis label reads worse than committing to one language.
# Every quantitative axis carries its own direction-of-good marker — a reader
# should never have to guess whether up is better.
BETTER = "↑ higher is better"


def _legend(ax, handles, ncol: int = 1, title: str | None = None):
    """House convention: legends sit OUTSIDE the axes, flush to the top-right.

    An overlaid legend has to be nudged panel by panel to dodge the data, and it
    still covers whatever moves when the numbers are redrawn. Anchoring it above
    the frame costs a little height and never collides.
    """
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


def _split_kd_run(run: str) -> tuple[str, str]:
    """`kd_<teacher>_to_<student>` -> (teacher, student). Raises on anything else."""
    if not run.startswith("kd_") or "_to_" not in run:
        raise ValueError(f"not a KD run tag: {run}")
    teacher, student = run[len("kd_"):].split("_to_", 1)
    return teacher, student


def _pair_label(run: str) -> str:
    teacher, student = _split_kd_run(run)
    return f"{TEACHER_LABEL.get(teacher, teacher)} → {STUDENT_LABEL.get(student, student)}"


def _run_label(run: str) -> str:
    if run.startswith("teacher/"):
        name = run.split("/", 1)[1]
        return f"teacher {TEACHER_LABEL.get(name, name)}"
    if run.startswith("baseline_"):
        student = run[len("baseline_"):]
        return f"baseline {STUDENT_LABEL.get(student, student)}"
    return _pair_label(run)


def _is_significant(ci: dict) -> bool:
    return ci["lo"] > 0.0 or ci["hi"] < 0.0


def panel_forest(ax, deltas: dict, metric: str) -> list[str]:
    """One row per KD pair, sorted by effect. Returns the row order for reuse."""
    order = sorted(deltas, key=lambda r: deltas[r][metric]["point"])
    for y, run in enumerate(order):
        ci = deltas[run][metric]
        colour = SIG_COLOR if _is_significant(ci) else NULL_COLOR
        ax.plot([ci["lo"], ci["hi"]], [y, y], color=colour, lw=2.0, solid_capstyle="butt", zorder=2)
        ax.plot([ci["lo"], ci["lo"]], [y - 0.16, y + 0.16], color=colour, lw=1.4, zorder=2)
        ax.plot([ci["hi"], ci["hi"]], [y - 0.16, y + 0.16], color=colour, lw=1.4, zorder=2)
        ax.plot([ci["point"]], [y], "o", ms=5.5, color=colour, zorder=3)

    ax.axvline(0.0, color="#333333", lw=1.2, ls="-", zorder=1)
    ax.annotate(
        "0 = distillation\nchanged nothing", (0.0, len(order) - 0.55),
        textcoords="offset points", xytext=(6, 0), ha="left", va="center",
        fontsize=7.5, color="#555555",
    )
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([_pair_label(r) for r in order], fontsize=8.5)
    ax.set_ylim(-0.7, len(order) - 0.1)
    ax.set_xlabel(f"Δ AUPRC from distillation (KD − baseline)   ·   {BETTER}", fontsize=9)
    # pad clears the two-row legend that _legend() parks above the frame
    ax.set_title("(a) Distillation still helps out of domain",
                 fontsize=10.5, weight="bold", loc="left", pad=28)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)

    n_sig = sum(_is_significant(deltas[r][metric]) for r in order)
    _legend(ax, [
        Line2D([], [], color=SIG_COLOR, lw=2, marker="o", ms=5,
               label=f"95% CI excludes 0 — real effect ({n_sig}/{len(order)})"),
        Line2D([], [], color=NULL_COLOR, lw=2, marker="o", ms=5,
               label=f"95% CI includes 0 — undecided ({len(order) - n_sig}/{len(order)})"),
    ])
    return order


def panel_scatter(ax, per_run: dict, deltas: dict, metric: str) -> None:
    """Achieved score vs KD gain — the two questions the forest plot cannot separate."""
    best_score = max(deltas, key=lambda r: per_run[r][metric]["point"])
    best_gain = max(deltas, key=lambda r: deltas[r][metric]["point"])

    handles = []
    for teacher in TEACHERS:
        runs = [r for r in deltas if _split_kd_run(r)[0] == teacher]
        ax.scatter(
            [per_run[r][metric]["point"] for r in runs],
            [deltas[r][metric]["point"] for r in runs],
            s=58, color=TEACHER_COLOR[teacher], edgecolor="white", lw=0.9, zorder=3,
        )
        handles.append(Line2D([], [], color=TEACHER_COLOR[teacher], lw=0, marker="o",
                              ms=6, label=TEACHER_LABEL[teacher]))

    ax.axhline(0.0, color="#333333", lw=1.0, zorder=1)
    # Both callouts are pushed LEFT into the empty upper-left corner; annotating
    # in place would collide with the legend and with each other.
    for run, note, xy_text, va in (
        (best_gain, "largest gain from KD", (-14, 6), "bottom"),
        (best_score, "highest score achieved", (-14, -6), "top"),
    ):
        ax.annotate(
            f"{_pair_label(run)}\n({note})",
            (per_run[run][metric]["point"], deltas[run][metric]["point"]),
            textcoords="offset points", xytext=xy_text, ha="right", va=va, fontsize=7.2,
            color="#333333",
            arrowprops={"arrowstyle": "-", "color": "#9aa0a6", "lw": 0.8,
                        "shrinkA": 0, "shrinkB": 4},
        )

    ax.set_xlabel(f"AUPRC achieved on HAM10000   ·   {BETTER}", fontsize=9)
    ax.set_ylabel(f"Δ AUPRC from distillation   ·   {BETTER}", fontsize=9)
    ax.set_title("(b) Largest gain ≠ highest score",
                 fontsize=10.5, weight="bold", loc="left", pad=26)
    ax.grid(color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.margins(x=0.16, y=0.16)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    _legend(ax, handles, ncol=3, title="Teacher")


def panel_dumbbell(ax, indomain: dict, ham: dict, metric: str) -> None:
    """One row per run-dir: the same fixed-specificity operating point, two domains."""
    runs = sorted(ham, key=lambda r: ham[r][metric]["point"])
    drops = []
    for y, run in enumerate(runs):
        x_in = indomain[run][metric]["point"]
        x_out = ham[run][metric]["point"]
        drops.append(x_in - x_out)
        ax.plot([x_out, x_in], [y, y], color="#c9ccd1", lw=1.6, zorder=1)
        ax.plot([x_out], [y], "o", ms=5.5, color=SIG_COLOR, zorder=3)
        ax.plot([x_in], [y], "o", ms=5.5, color="#2a5d9e", zorder=3)

    ax.annotate(
        f"every run loses {min(drops):.2f}–{max(drops):.2f}\nsensitivity at the SAME specificity",
        (0.5, len(runs) - 0.55), ha="center", va="center", fontsize=7.5, color="#555555",
    )
    ax.set_yticks(range(len(runs)))
    ax.set_yticklabels([_run_label(r) for r in runs], fontsize=7.5)
    ax.set_ylim(-0.7, len(runs) - 0.1)
    ax.set_xlim(0.0, 1.0)
    ax.set_xlabel(f"Sensitivity at a fixed 90% specificity   ·   {BETTER}", fontsize=9)
    ax.set_title("(c) The operating point does not transfer",
                 fontsize=10.5, weight="bold", loc="left", pad=28)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    _legend(ax, [
        Line2D([], [], color="#2a5d9e", lw=0, marker="o", ms=6,
               label="In-domain test set"),
        Line2D([], [], color=SIG_COLOR, lw=0, marker="o", ms=6,
               label="HAM10000 (out of domain)"),
    ], ncol=2)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ham-ci", type=Path, default=Path("reports/external/ham10000/headline/bootstrap_ci.json"))
    ap.add_argument("--indomain-ci", type=Path, default=Path("experiments/runs/bootstrap_ci.json"))
    ap.add_argument("--metric", default="auprc", help="ranking metric for panels (a) and (b)")
    ap.add_argument("--op-metric", default="sens_at_90spec", help="operating point for panel (c)")
    ap.add_argument("--out", type=Path, default=Path("reports/ham_summary.png"))
    ap.add_argument("--dpi", type=int, default=200)
    args = ap.parse_args()

    ham = _load(args.ham_ci)
    indomain = _load(args.indomain_ci)

    deltas = ham.get("kd_deltas") or {}
    if not deltas:
        sys.exit(f"ERROR: no kd_deltas in {args.ham_ci} — re-run run/bootstrap_ci.sh on that dir")
    for name, blob, metric in (("HAM", ham, args.metric), ("in-domain", indomain, args.op_metric)):
        if metric not in blob.get("metrics", []):
            sys.exit(f"ERROR: {name} report has no metric '{metric}' (has {blob.get('metrics')})")

    # Panel (c) joins two reports; a run present in one but not the other would
    # silently drop a row, so refuse instead of drawing a partial picture.
    missing = sorted(set(ham["per_run"]) - set(indomain["per_run"]))
    if missing:
        sys.exit(f"ERROR: {len(missing)} run(s) missing from {args.indomain_ci}: {missing}")

    # constrained_layout, not tight_layout: panels (a) and (c) carry long run-name
    # tick labels, which is exactly the case tight_layout mis-measures (it warned
    # and clipped the left panel).
    fig = plt.figure(figsize=(17.5, 7.0), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.15])
    panel_forest(fig.add_subplot(gs[0, 0]), deltas, args.metric)
    panel_scatter(fig.add_subplot(gs[0, 1]), ham["per_run"], deltas, args.metric)
    panel_dumbbell(fig.add_subplot(gs[0, 2]), indomain["per_run"], ham["per_run"], args.op_metric)

    fig.suptitle(
        f"Cross-domain evaluation on HAM10000 — {len(ham['per_run'])} runs, "
        f"{ham['n_test_rows']:,} images, frozen thresholds, "
        f"paired bootstrap B = {ham['n_boot']:,}",
        fontsize=12, weight="bold", x=0.006, ha="left",
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=args.dpi)
    svg = args.out.with_suffix(".svg")
    fig.savefig(svg)
    print(f"[plot] wrote {args.out} and {svg}")


if __name__ == "__main__":
    main()
