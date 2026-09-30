"""
Pareto figure: in-domain AUPRC vs measured on-device latency (Pixel 6a).

WHY THIS SHAPE. The x axis carries ONE value per architecture, not per run-dir.
The four KD variants of an architecture share a graph and a parameter count and
differ only in weights, and BENCHMARK_RESULTS.md 5.4 shows the 24-149% latency
spread between variants tracks TEMPERATURE (~14% per degree C), not the weights.
Plotting a separate x per variant would be plotting thermal noise. So each
architecture is a vertical cluster: moving UP means picking a better teacher (free
on the speed axis), moving RIGHT means picking a heavier architecture (not free).

x uses the SUSTAINED figure (last minute of a 300 s run), not the best case.
Throttling costs 45-49% on this handset and a screening app doing repeated
inference sees the sustained number. `--latency-col best_ms` switches it back for
comparison.

y error bars are the PAIRED BOOTSTRAP CI, not the fold std. The fold std is the
spread between five models scored on the same rows; the CI is the test set's
sampling error, which is what "is this gap real?" needs.

Inputs (both are artifacts, nothing hard-coded):
    reports/bootstrap_ci_ablation.json   -> per_run.<run>.auprc {point, lo, hi}
    reports/ondevice_latency.csv         -> one row per architecture

Runs on the SERVER (needs matplotlib), not the Mac.

Usage:
    python scripts/plot_pareto.py
    python scripts/plot_pareto.py --latency-col best_ms --out reports/pareto_best.png
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

# Student architectures in the deployed set, longest name first is irrelevant here;
# order fixes the colour assignment so redraws stay visually stable.
ARCHES = [
    "mobilenetv4_conv_medium",
    "repvit_m1_0",
    "fastvit_sa12",
    "efficientformerv2_s2",
]
# Teacher order = the legend order; "baseline" is the no-KD control.
TEACHERS = ["baseline", "efficientnetv2_m", "convnextv2_base", "maxvit_base"]

ARCH_COLOR = {
    "mobilenetv4_conv_medium": "#1b7f5f",
    "repvit_m1_0": "#b07a1e",
    "fastvit_sa12": "#2a5d9e",
    "efficientformerv2_s2": "#9e3b5d",
}
TEACHER_MARKER = {
    "baseline": "o",
    "efficientnetv2_m": "^",
    "convnextv2_base": "s",
    "maxvit_base": "D",
}
ARCH_LABEL = {
    "mobilenetv4_conv_medium": "MobileNetV4-Conv-M",
    "repvit_m1_0": "RepViT-M1.0",
    "fastvit_sa12": "FastViT-SA12",
    "efficientformerv2_s2": "EfficientFormerV2-S2",
}
TEACHER_LABEL = {
    "baseline": "no KD (baseline)",
    "efficientnetv2_m": "KD ← EfficientNetV2-M",
    "convnextv2_base": "KD ← ConvNeXtV2-B",
    "maxvit_base": "KD ← MaxViT-B",
}


def run_name(arch: str, teacher: str) -> str:
    return f"baseline_{arch}" if teacher == "baseline" else f"kd_{teacher}_to_{arch}"


def load_latency(path: Path) -> dict[str, dict]:
    """One row per architecture. '#' comments carry the provenance; skip them."""
    rows = {}
    with path.open() as fh:
        lines = [ln for ln in fh if not ln.lstrip().startswith("#")]
    for r in csv.DictReader(lines):
        rows[r["architecture"]] = r
    missing = [a for a in ARCHES if a not in rows]
    if missing:
        raise SystemExit(f"ERROR: {path} has no row for {missing}")
    return rows


def load_auprc(path: Path) -> dict[str, tuple[float, float, float]]:
    """-> {run_name: (point, lo, hi)} from the bootstrap report's per_run block."""
    per_run = json.loads(path.read_text()).get("per_run", {})
    if not per_run:
        raise SystemExit(f"ERROR: {path} has no per_run block")
    out = {}
    for rel, row in per_run.items():
        m = row.get("auprc")
        if m and "point" in m:
            out[rel] = (m["point"], m["lo"], m["hi"])
    return out


def pareto_front(points: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    """Non-dominated set for (minimise x, maximise y).

    A point is dominated when another is at least as fast AND at least as accurate,
    and strictly better on one of the two. Ties on both axes keep the first seen.
    """
    front = []
    for x, y, tag in sorted(points):
        if any((ox <= x and oy >= y) and (ox < x or oy > y) for ox, oy, _ in points):
            continue
        front.append((x, y, tag))
    return front


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ci-json", type=Path, default=Path("reports/bootstrap_ci_ablation.json"))
    ap.add_argument("--latency-csv", type=Path, default=Path("reports/ondevice_latency.csv"))
    ap.add_argument("--latency-col", default="sustained_ms",
                    choices=["sustained_ms", "best_ms", "cold_ms"],
                    help="sustained_ms (default) is what a screening app actually sees")
    ap.add_argument("--out", type=Path, default=Path("reports/pareto_auprc_vs_latency.png"))
    ap.add_argument("--dpi", type=int, default=200)
    args = ap.parse_args()

    for p in (args.ci_json, args.latency_csv):
        if not p.is_file():
            raise SystemExit(f"ERROR: not found: {p}")

    lat = load_latency(args.latency_csv)
    auprc = load_auprc(args.ci_json)

    fig, ax = plt.subplots(figsize=(11, 7))

    best_per_arch: list[tuple[float, float, str]] = []
    # Top of the tallest error bar per architecture — annotations anchor above THIS,
    # not above the marker, otherwise the text lands inside the whiskers.
    top_per_arch: dict[str, float] = {}
    n_plotted = 0
    for arch in ARCHES:
        x = float(lat[arch][args.latency_col])
        color = ARCH_COLOR[arch]
        ys = []
        for teacher in TEACHERS:
            rel = run_name(arch, teacher)
            if rel not in auprc:
                print(f"[pareto] SKIP (not in CI json): {rel}", file=sys.stderr)
                continue
            point, lo, hi = auprc[rel]
            ys.append(point)
            top_per_arch[arch] = max(top_per_arch.get(arch, hi), hi)
            n_plotted += 1
            ax.errorbar(
                x, point, yerr=[[point - lo], [hi - point]],
                fmt=TEACHER_MARKER[teacher], color=color, markersize=9,
                markeredgecolor="white", markeredgewidth=1.1,
                elinewidth=1.1, capsize=3, ecolor=color, alpha=0.92, zorder=3,
            )
        if ys:
            best_per_arch.append((x, max(ys), arch))

    if n_plotted == 0:
        raise SystemExit("ERROR: nothing plotted — check run names in the CI json")

    front = pareto_front(best_per_arch)
    front_tags = {t for _, _, t in front}
    if len(front) >= 2:
        fx = [p[0] for p in front]
        fy = [p[1] for p in front]
        ax.plot(fx, fy, "--", color="#444444", linewidth=1.6, zorder=2,
                label="Pareto frontier")

    ax.set_xscale("log")
    # Pad in LOG space before annotating: the leftmost and rightmost labels are wide
    # and clip against the axes otherwise. Padding must precede the annotate calls so
    # the alignment decisions below see the final limits.
    xs = [p[0] for p in best_per_arch]
    ax.set_xlim(min(xs) / 2.1, max(xs) * 2.1)

    # Annotate each architecture cluster ABOVE its tallest whisker. Outer clusters are
    # aligned inward so their text cannot run off the canvas.
    xlo, xhi = min(xs), max(xs)
    for x, y, arch in best_per_arch:
        dominated = arch not in front_tags
        lines = [ARCH_LABEL[arch]]
        if lat[arch]["backend"] == "portable":
            lines.append("portable ops — XNNPACK lowering failed")
        if dominated:
            lines.append("DOMINATED")
        if x == xlo:
            ha, dx = "left", -14
        elif x == xhi:
            ha, dx = "right", 14
        else:
            ha, dx = "center", 0
        ax.annotate(
            "\n".join(lines),
            xy=(x, top_per_arch.get(arch, y)), xytext=(dx, 12),
            textcoords="offset points", ha=ha, va="bottom", fontsize=9,
            color="#333333" if not dominated else "#8a8a8a",
            fontweight="bold" if not dominated else "normal", linespacing=1.35,
        )
    # Headroom so the annotations sit inside the axes.
    ylo, yhi = ax.get_ylim()
    ax.set_ylim(ylo, yhi + (yhi - ylo) * 0.13)
    col_label = {"sustained_ms": "sustained (last minute of 300 s)",
                 "best_ms": "best case (coolest measurement)",
                 "cold_ms": "cold start"}[args.latency_col]
    ax.set_xlabel(f"Pixel 6a latency @ 4 threads, {col_label} — ms, log scale", fontsize=11)
    ax.set_ylabel("In-domain AUPRC  (point estimate, 95% paired-bootstrap CI)", fontsize=11)
    ax.set_title("Accuracy vs on-device speed — 16 deployed models, 4 architectures",
                 fontsize=13, fontweight="bold", pad=14)
    ax.grid(True, which="both", axis="both", alpha=0.22, linewidth=0.7)
    ax.set_axisbelow(True)

    # Two legends: architecture = colour (and x position), teacher = marker.
    arch_handles = [
        plt.Line2D([], [], color=ARCH_COLOR[a], marker="o", linestyle="",
                   markersize=9, label=ARCH_LABEL[a])
        for a in ARCHES
    ]
    teacher_handles = [
        plt.Line2D([], [], color="#555555", marker=TEACHER_MARKER[t], linestyle="",
                   markersize=8, label=TEACHER_LABEL[t])
        for t in TEACHERS
    ]
    # Both legends sit in the empty lower band. The teacher legend goes CENTRE, not
    # lower-left: the leftmost clusters have long downward whiskers and a lower-left
    # box lands on top of them.
    leg1 = ax.legend(handles=arch_handles, title="Architecture (sets x)",
                     loc="lower right", fontsize=9, title_fontsize=9, framealpha=0.95)
    ax.add_artist(leg1)
    ax.legend(handles=teacher_handles, title="Teacher (moves y only)",
              loc="lower center", fontsize=9, title_fontsize=9, framealpha=0.95)

    fig.text(
        0.5, 0.012,
        "One x per architecture: the four variants share a graph and differ only in weights, so a "
        "per-variant x would plot thermal noise (BENCHMARK_RESULTS.md §5.4).\n"
        "Choosing a teacher moves a point vertically at no speed cost; choosing an architecture "
        "moves it horizontally. Error bars are test-set sampling error, not fold spread.",
        ha="center", va="bottom", fontsize=8.5, color="#555555",
    )
    fig.tight_layout(rect=(0, 0.058, 1, 1))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=args.dpi, bbox_inches="tight")
    svg = args.out.with_suffix(".svg")
    fig.savefig(svg, bbox_inches="tight")
    plt.close(fig)

    print(f"[pareto] {n_plotted} models plotted, x = {args.latency_col}")
    print(f"[pareto] frontier: {', '.join(t for _, _, t in front)}")
    for x, y, arch in sorted(best_per_arch):
        mark = "ON FRONTIER" if arch in front_tags else "dominated"
        print(f"[pareto]   {arch:26s} {x:9.1f} ms  AUPRC {y:.4f}  {mark}")
    print(f"[pareto] wrote {args.out}")
    print(f"[pareto] wrote {svg}")


if __name__ == "__main__":
    main()
