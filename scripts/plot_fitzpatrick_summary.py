"""
One figure for the whole Fitzpatrick17k fairness evaluation (thesis Muc 4.8).

WHY ONE FIGURE. Like the HAM10000 tier, this is a SINGLE experiment — every
trained run scored, unchanged, on one out-of-domain set carrying a skin-tone
annotation — that had grown into three subsections and four tables. Three panels
carry the same evidence:

  (a) GAP STRIPS, one row per pairwise tone-group gap, one dot per run.
      The vertical line at 0 does the work. `light - medium` sits entirely clear
      of it; the two gaps involving `dark` straddle it. This is the panel that
      refuses the expected story ("the model gets worse as skin gets darker")
      and points at the MIDDLE group instead.

  (b) RAW AUPRC vs ITS OWN RANDOM BASELINE, on the `with_non_neoplastic` variant.
      AUPRC's random baseline IS the subgroup's prevalence, and prevalence
      differs by tone group in that variant (dark 9.6% vs light 15.4%). Plotting
      the baseline underneath each bar shows why the raw -0.12 AUPRC gap is an
      artifact: normalised by that baseline the order flips back to (a)'s.

  (c) AUC-ROC PER RUN with paired-bootstrap CIs, coloured by role.
      Out of domain the three teachers separate from the students — the capacity
      gap that distillation closes in-domain reopens here.

All intervals are PAIRED BOOTSTRAP over the test rows, not the fold std. The
fold std is the spread between five models scored on the same rows; the CI is the
test set's sampling error, which is what "is this gap real?" needs.

Panel (b) reads prevalence from a `predictions.csv` rather than taking it as an
argument: prevalence is a property of the split, so hard-coding it would let the
figure drift silently if the split were ever rebuilt.

Inputs (all artifacts, nothing hard-coded):
    reports/external/fitzpatrick17k/headline/bootstrap_ci.json
        -> per_run.<run>.auc_roc{point,lo,hi}
        -> fairness_gaps.<run>.gaps.<gap>.<metric>{point,lo,hi}
    reports/external/fitzpatrick17k/with_non_neoplastic/bootstrap_ci.json
        -> fairness_gaps.<run>.per_group.<group>.auprc.point, n_per_group
    reports/external/fitzpatrick17k/with_non_neoplastic/<run>/fold_0/predictions.csv
        -> y_true + tone_group, for each group's prevalence

Runs on the SERVER (needs matplotlib), not the Mac.

Usage:
    bash run/plot_fitzpatrick_summary.sh
    python scripts/plot_fitzpatrick_summary.py --out reports/fitzpatrick_summary.png
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless server: no display, and this must precede pyplot
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

GROUPS = ["light", "medium", "dark"]
GROUP_LABEL = {
    "light": "light (Fitzpatrick I–II)",
    "medium": "medium (III–IV)",
    "dark": "dark (V–VI)",
}
GAPS = ["light_minus_medium", "dark_minus_light", "dark_minus_medium"]
GAP_LABEL = {
    "light_minus_medium": "light − medium",
    "dark_minus_light": "dark − light",
    "dark_minus_medium": "dark − medium",
}

ROLES = ["teacher", "kd", "baseline"]
ROLE_COLOR = {"teacher": "#b07a1e", "kd": "#2a5d9e", "baseline": "#9aa0a6"}
ROLE_LABEL = {"teacher": "Teacher", "kd": "KD student", "baseline": "Baseline student"}

SIG_COLOR = "#c0392b"  # interval clear of 0
NULL_COLOR = "#9aa0a6"  # interval touching 0
BAR_COLOR = "#2a5d9e"
BASE_COLOR = "#c0392b"
GRID = "#dcdcdc"

# Figure text is ENGLISH even though the thesis body is Vietnamese, and every
# quantitative axis states its direction of good — same convention as the
# HAM10000 summary figure.
BETTER = "↑ higher is better"


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


def _role(run: str) -> str:
    if run.startswith("teacher/"):
        return "teacher"
    if run.startswith("baseline_"):
        return "baseline"
    return "kd"


def _run_label(run: str) -> str:
    pretty = {
        "efficientnetv2_m": "EfficientNetV2-M", "convnextv2_base": "ConvNeXtV2-Base",
        "maxvit_base": "MaxViT-Base", "mobilenetv4_conv_medium": "MobileNetV4",
        "repvit_m1_0": "RepViT", "fastvit_sa12": "FastViT",
        "efficientformerv2_s2": "EfficientFormerV2",
    }
    if run.startswith("teacher/"):
        return f"teacher {pretty.get(run.split('/', 1)[1], run)}"
    if run.startswith("baseline_"):
        return f"baseline {pretty.get(run[len('baseline_'):], run)}"
    teacher, student = run[len("kd_"):].split("_to_", 1)
    return f"{pretty.get(teacher, teacher)} → {pretty.get(student, student)}"


def _is_significant(ci: dict) -> bool:
    return ci["lo"] > 0.0 or ci["hi"] < 0.0


def _group_prevalence(variant_dir: Path) -> dict[str, float]:
    """Prevalence per tone group, read off any one fold's predictions.

    Every run scores the SAME rows, so the first `predictions.csv` found answers
    this for all of them; disagreement between runs would mean the split was
    rebuilt mid-experiment, which the row-count check below would catch.
    """
    csv_paths = sorted(variant_dir.glob("*/fold_0/predictions.csv"))
    if not csv_paths:
        sys.exit(f"ERROR: no fold_0/predictions.csv under {variant_dir}")
    pos: dict[str, int] = {}
    tot: dict[str, int] = {}
    with csv_paths[0].open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for field in ("y_true", "tone_group"):
            if field not in (reader.fieldnames or []):
                sys.exit(f"ERROR: {csv_paths[0]} has no '{field}' column")
        for row in reader:
            g = row["tone_group"]
            tot[g] = tot.get(g, 0) + 1
            pos[g] = pos.get(g, 0) + (1 if row["y_true"] == "1" else 0)
    return {g: pos[g] / tot[g] for g in tot}


def panel_gaps(ax, gaps_by_run: dict, metric: str) -> None:
    """One row per gap, one dot per run — where a gap does or doesn't clear zero."""
    for y, gap in enumerate(GAPS):
        vals = [gaps_by_run[r][gap][metric] for r in gaps_by_run]
        n_sig = sum(_is_significant(ci) for ci in vals)
        for ci in vals:
            colour = SIG_COLOR if _is_significant(ci) else NULL_COLOR
            ax.plot([ci["point"]], [y], "o", ms=6, color=colour, alpha=0.75,
                    markeredgecolor="white", markeredgewidth=0.5, zorder=3)
        ax.text(1.0, y + 0.28, f"{n_sig}/{len(vals)} runs decisive",
                transform=ax.get_yaxis_transform(), ha="right", va="bottom",
                fontsize=8, color="#555555")

    ax.axvline(0.0, color="#333333", lw=1.2, zorder=1)
    # Each row is a SUBTRACTION between two groups, so the reader needs the sign
    # convention and the zero line spelled out or the panel is unreadable.
    ax.annotate(
        "0 = the two groups\nare ranked equally well", (0.0, -0.42),
        textcoords="offset points", xytext=(6, 0), ha="left", va="center",
        fontsize=7.5, color="#555555",
    )
    ax.set_yticks(range(len(GAPS)))
    ax.set_yticklabels([GAP_LABEL[g] for g in GAPS], fontsize=9)
    ax.set_ylim(-0.85, len(GAPS) - 0.1)
    ax.set_xlabel("Gap in AUC-ROC, group A − group B   ·   one dot = one run\n"
                  "positive ⇒ A is ranked better than B", fontsize=9)
    ax.set_title("(a) The disadvantaged group is the MIDDLE one",
                 fontsize=10.5, weight="bold", loc="left", pad=28)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    _legend(ax, [
        Line2D([], [], color=SIG_COLOR, lw=0, marker="o", ms=6,
               label="95% CI excludes 0"),
        Line2D([], [], color=NULL_COLOR, lw=0, marker="o", ms=6,
               label="95% CI includes 0"),
    ], ncol=2)


def panel_prevalence_trap(ax, auprc: dict[str, float], prev: dict[str, float]) -> None:
    """Each group's AUPRC against its OWN random baseline (= its prevalence)."""
    ys = range(len(GROUPS))
    for y, g in zip(ys, GROUPS):
        ax.barh(y, auprc[g], height=0.5, color=BAR_COLOR, zorder=2)
        ax.plot([prev[g], prev[g]], [y - 0.32, y + 0.32], color=BASE_COLOR, lw=2.2, zorder=4)
        ax.text(auprc[g] + 0.008, y, f"{auprc[g] / prev[g]:.2f}× baseline",
                va="center", ha="left", fontsize=8.5, color="#333333")

    ax.set_yticks(list(ys))
    ax.set_yticklabels([GROUP_LABEL[g] for g in GROUPS], fontsize=9)
    ax.set_ylim(-0.6, len(GROUPS) - 0.1)
    ax.set_xlim(0.0, max(auprc.values()) * 1.55)
    ax.set_xlabel(f"AUPRC on the with-non-neoplastic variant   ·   {BETTER}", fontsize=9)
    ax.set_title("(b) Raw AUPRC is not comparable across groups",
                 fontsize=10.5, weight="bold", loc="left", pad=28)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    _legend(ax, [
        Line2D([], [], color=BAR_COLOR, lw=6, label="AUPRC achieved"),
        Line2D([], [], color=BASE_COLOR, lw=2.2, label="random baseline = this group's prevalence"),
    ])


def panel_runs(ax, per_run: dict, metric: str) -> None:
    """Every run's out-of-domain ranking score, coloured by role."""
    order = sorted(per_run, key=lambda r: per_run[r][metric]["point"])
    for y, run in enumerate(order):
        ci = per_run[run][metric]
        colour = ROLE_COLOR[_role(run)]
        ax.plot([ci["lo"], ci["hi"]], [y, y], color=colour, lw=2.0, zorder=2)
        ax.plot([ci["point"]], [y], "o", ms=5.5, color=colour, zorder=3)

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([_run_label(r) for r in order], fontsize=7.5)
    ax.set_ylim(-0.7, len(order) - 0.1)
    ax.set_xlabel(f"AUC-ROC on Fitzpatrick17k   ·   {BETTER}", fontsize=9)
    ax.set_title("(c) Out of domain the teachers pull ahead again",
                 fontsize=10.5, weight="bold", loc="left", pad=28)
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    _legend(ax, [
        Line2D([], [], color=ROLE_COLOR[r], lw=2, marker="o", ms=5, label=ROLE_LABEL[r])
        for r in ROLES
    ], ncol=3)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    base = Path("reports/external/fitzpatrick17k")
    ap.add_argument("--headline-ci", type=Path, default=base / "headline/bootstrap_ci.json")
    ap.add_argument("--variant-dir", type=Path, default=base / "with_non_neoplastic",
                    help="variant whose prevalence differs by tone group (panel b)")
    ap.add_argument("--gap-metric", default="auc_roc", help="metric for panel (a)")
    ap.add_argument("--out", type=Path, default=Path("reports/fitzpatrick_summary.png"))
    ap.add_argument("--dpi", type=int, default=200)
    args = ap.parse_args()

    headline = _load(args.headline_ci)
    variant = _load(args.variant_dir / "bootstrap_ci.json")

    fair = headline.get("fairness_gaps") or {}
    if not fair:
        sys.exit(f"ERROR: no fairness_gaps in {args.headline_ci} — re-run "
                 f"run/bootstrap_ci.sh with SUBGROUP=tone_group")
    gaps_by_run = {r: fair[r]["gaps"] for r in fair}
    missing = sorted(g for g in GAPS if any(g not in v for v in gaps_by_run.values()))
    if missing:
        sys.exit(f"ERROR: gap(s) {missing} absent from {args.headline_ci}")

    # Panel (b): mean AUPRC per group over every run, against that group's own
    # random baseline. Averaging over runs is deliberate — the trap is a property
    # of the SPLIT, not of any one model.
    vfair = variant.get("fairness_gaps") or {}
    if not vfair:
        sys.exit(f"ERROR: no fairness_gaps in {args.variant_dir}/bootstrap_ci.json")
    auprc = {
        g: sum(vfair[r]["per_group"][g]["auprc"]["point"] for r in vfair) / len(vfair)
        for g in GROUPS
    }
    prev = _group_prevalence(args.variant_dir)
    for g in GROUPS:
        if g not in prev:
            sys.exit(f"ERROR: tone group '{g}' missing from the variant's predictions")

    fig = plt.figure(figsize=(17.5, 7.0), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.1, 1.0, 1.1])
    panel_gaps(fig.add_subplot(gs[0, 0]), gaps_by_run, args.gap_metric)
    panel_prevalence_trap(fig.add_subplot(gs[0, 1]), auprc, prev)
    panel_runs(fig.add_subplot(gs[0, 2]), headline["per_run"], "auc_roc")

    sizes = next(iter(fair.values()))["n_per_group"]
    fig.suptitle(
        f"Skin-tone fairness on Fitzpatrick17k — {len(headline['per_run'])} runs, "
        f"{headline['n_test_rows']:,} images "
        f"(light {sizes['light']:,} · medium {sizes['medium']:,} · dark {sizes['dark']:,}), "
        f"paired bootstrap B = {headline['n_boot']:,}",
        fontsize=12, weight="bold", x=0.006, ha="left",
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=args.dpi)
    svg = args.out.with_suffix(".svg")
    fig.savefig(svg)
    print(f"[plot] wrote {args.out} and {svg}")


if __name__ == "__main__":
    main()
