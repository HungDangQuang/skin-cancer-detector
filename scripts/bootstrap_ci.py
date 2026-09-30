"""
Bootstrap confidence intervals over an evaluation-results tree.

WHY: every number in the reports is currently `mean ± std over 5 folds`. That
std measures how much the five *models* disagree, not the sampling error of the
test set — so it cannot answer "is this gap real?". The Fitzpatrick dark-tone
group is 137 images per fold; at that size a fold std is not evidence either way.
This script resamples the *test rows* instead, which is the uncertainty a reader
actually cares about.

Four outputs (the things a fold std cannot give you):
  1. CI per run per metric        -> "AUPRC 0.480 [0.44-0.52]"
  2. PAIRED CI on the KD delta    -> "dAUPRC +0.030 [+0.011, +0.048]" instead of
                                     the much weaker "KD won 12/12"
  3. PAIRED CI on an ABLATION     -> every `__<suffix>` fork vs the same run
     delta (main - ablated)          without the suffix, e.g.
                                     baseline_<s>__train_isic_only (PAD mixing)
                                     or kd_..._to_...__samp_off (the sampler).
                                     Section 2 cannot pair these: both sides are
                                     kind="baseline"/"kd", so the kd-vs-baseline
                                     lookup never fires.
  4. PAIRED CI on a fairness gap  -> bootstraps (light AUC - dark AUC) directly,
                                     not two CIs compared by eye
  5. PAIRED CI on the ablation    -> needs --subgroup-col. For the PAD arms the
     delta WITHIN a subgroup         whole-test delta of (3) is the WRONG cell:
                                     the ISIC-only arm collapses on the 377 PAD
                                     rows and those carry ~75% of all positives,
                                     so it is inflated. Use --subgroup-col source
                                     and quote the per-source delta instead.

FOLD HANDLING (one convention, stated and applied everywhere):
    **Shared row indices across folds; the statistic is the mean over folds.**
The 5 folds are 5 *models* scored on the SAME test rows, so pooling the fold
predictions would replicate every test row 5x and shrink the interval into
fiction. Instead each bootstrap replicate draws ONE set of row indices, scores
every fold on those same rows, and averages -> a replicate of exactly the
"mean ± std over 5 folds" quantity the reports already cite. The script asserts
the folds really do share identical labels/order before doing this.

PAIRING: the same seeded index arrays are reused for every run, so a paired
delta is just `boot[kd] - boot[baseline]` element-wise. Pairing matters — the
two models are scored on identical rows, and an unpaired interval throws away
that correlation and overstates the uncertainty.

Metrics reuse src.evaluation.metrics, so the point estimates reproduce
test_metrics.json exactly rather than a lookalike reimplementation.

Runs on the SERVER (needs numpy + scikit-learn), not the Mac.

Usage:
    python scripts/bootstrap_ci.py --results-dir reports/external/ham10000/headline
    python scripts/bootstrap_ci.py --results-dir reports/external/fitzpatrick17k/headline \\
        --subgroup-col tone_group
    python scripts/bootstrap_ci.py --results-dir experiments/runs --n-boot 2000 --seed 42
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

from src.evaluation.metrics import pauc_at_tpr, sensitivity_at_specificity

# Reuse the run-name grammar of the comparison script so both tools agree on
# what "kd_<teacher>_to_<student>" pairs with, and on teacher/<name> nesting.
sys.path.insert(0, str(Path(__file__).parent))
from compare_kd_results import find_run_dirs, parse_run_name  # noqa: E402

METRICS = ("auc_roc", "auprc", "pauc_at_tpr80", "sens_at_90spec")
_MIN_TPR = 0.80
_SPEC_LEVEL = 0.90


# --------------------------------------------------------------------------- #
# Metric evaluation
# --------------------------------------------------------------------------- #
def _metric(name: str, y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Reference implementation: one metric on one array pair, via the repo's own
    functions. Used for the POINT estimates and for verifying the fast path.

    NaN when undefined (single-class). The library functions return 0.0 there,
    which is a sentinel, not a measurement — averaging it in would drag the
    interval down.
    """
    if len(np.unique(y_true)) < 2:
        return float("nan")
    if name == "auc_roc":
        return float(roc_auc_score(y_true, y_prob))
    if name == "auprc":
        return float(average_precision_score(y_true, y_prob))
    if name == "pauc_at_tpr80":
        return float(pauc_at_tpr(y_true, y_prob, min_tpr=_MIN_TPR))
    if name == "sens_at_90spec":
        return float(sensitivity_at_specificity(y_true, y_prob, (_SPEC_LEVEL,))["sens_at_90spec"])
    raise ValueError(f"unknown metric {name!r}")


# --------------------------------------------------------------------------- #
# Fast path: a bootstrap resample is just integer WEIGHTS over the original rows,
# so the ROC/PR curves come from one pre-sort per fold plus an O(n) cumsum per
# replicate. This is exact (not an approximation) and ~50x faster than calling
# sklearn four times per replicate — which at B=2000 x 19 runs x 5 trees was the
# difference between ~10 hours and ~15 minutes. `_verify_fast_path` asserts the
# two agree before any of it is trusted.
# --------------------------------------------------------------------------- #
class _SortedCurve:
    """One fold pre-sorted by score descending, with tie-group boundaries.

    Ties matter: sklearn's curves only expose one point per distinct score, and
    emitting a point mid-tie would change the trapezoid area.
    """

    def __init__(self, y_true: np.ndarray, y_score: np.ndarray):
        order = np.argsort(-y_score, kind="mergesort")
        self.order = order
        self.y = y_true[order].astype(np.float64)
        s = y_score[order]
        self.distinct = np.r_[np.flatnonzero(np.diff(s)), s.size - 1]

    def tps_fps(self, w_sorted: np.ndarray):
        tp = np.cumsum(w_sorted * self.y)[self.distinct]
        fp = np.cumsum(w_sorted * (1.0 - self.y))[self.distinct]
        return tp, fp


def _partial_auc(fpr: np.ndarray, tpr: np.ndarray, max_fpr: float) -> float:
    """Raw partial area under the ROC up to max_fpr, interpolating the last point
    — i.e. sklearn's roc_auc_score(max_fpr=...) BEFORE its McClish correction,
    which is exactly the quantity src.evaluation.metrics.pauc_at_tpr returns."""
    stop = int(np.searchsorted(fpr, max_fpr, "right"))
    if stop >= fpr.size:
        return float(np.trapezoid(tpr, fpr))
    y_end = np.interp(max_fpr, fpr[stop - 1:stop + 1], tpr[stop - 1:stop + 1])
    return float(np.trapezoid(np.r_[tpr[:stop], y_end], np.r_[fpr[:stop], max_fpr]))


def _fast_metrics(curve: _SortedCurve, flipped: _SortedCurve,
                  w: np.ndarray, metrics) -> dict:
    """All requested metrics for one weighted resample. `w` is per-ORIGINAL-row."""
    tp, fp = curve.tps_fps(w[curve.order])
    P, N = tp[-1], fp[-1]
    if P <= 0 or N <= 0:          # single-class resample -> undefined, not zero
        return {m: float("nan") for m in metrics}

    out = {}
    recall = tp / P
    if "auc_roc" in metrics or "sens_at_90spec" in metrics:
        fpr = np.r_[0.0, fp / N]
        tpr = np.r_[0.0, recall]
        if "auc_roc" in metrics:
            out["auc_roc"] = float(np.trapezoid(tpr, fpr))
        if "sens_at_90spec" in metrics:
            ok = (1.0 - fpr) >= _SPEC_LEVEL
            out["sens_at_90spec"] = float(np.max(np.where(ok, tpr, -1.0))) if ok.any() else 0.0
    if "auprc" in metrics:
        ps = tp + fp
        precision = np.divide(tp, ps, out=np.zeros_like(tp), where=ps != 0)
        out["auprc"] = float(np.sum(np.diff(np.r_[0.0, recall]) * precision))
    if "pauc_at_tpr80" in metrics:
        # The ISIC metric is the partial area under the FLIPPED ROC (labels and
        # scores negated), which maps "TPR >= 0.80" onto "FPR <= 0.20".
        tp_f, fp_f = flipped.tps_fps(w[flipped.order])
        out["pauc_at_tpr80"] = _partial_auc(np.r_[0.0, fp_f / fp_f[-1]],
                                            np.r_[0.0, tp_f / tp_f[-1]],
                                            1.0 - _MIN_TPR)
    return out


def _verify_fast_path(y_true, probs, metrics, tol=1e-9) -> None:
    """Refuse to produce intervals from a fast path that disagrees with the repo's
    own metric functions. Runs once per run-dir on unit weights — cheap, and it
    is the only thing standing between a subtle curve bug and a plausible-looking
    confidence interval."""
    w = np.ones(len(y_true), dtype=np.float64)
    for p in probs:
        curve = _SortedCurve(y_true, p)
        flipped = _SortedCurve(1 - y_true, -p)
        fast = _fast_metrics(curve, flipped, w, metrics)
        for m in metrics:
            ref = _metric(m, y_true, p)
            if not np.isfinite(ref) and not np.isfinite(fast[m]):
                continue
            if abs(fast[m] - ref) > tol:
                raise SystemExit(
                    f"Fast-path metric '{m}' disagrees with src.evaluation.metrics "
                    f"({fast[m]!r} vs {ref!r}, tol {tol:g}). Refusing to report "
                    "confidence intervals from it."
                )


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def load_run_predictions(run_dir: Path, subgroup_col: str | None):
    """Read fold_*/predictions.csv -> (y_true, [y_prob per fold], subgroup or None).

    Returns None if the run has no usable predictions. Enforces the shared-rows
    assumption: every fold must expose the same labels in the same order, which
    is what makes one index draw valid across all folds.
    """
    y_true_ref = None
    subgroup = None
    probs, folds = [], []

    for fold_dir in sorted(run_dir.glob("fold_*")):
        csv_path = fold_dir / "predictions.csv"
        if not csv_path.is_file():
            continue
        yt, yp, sg = [], [], []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            has_sg = subgroup_col is not None and subgroup_col in (reader.fieldnames or [])
            for row in reader:
                yt.append(int(float(row["y_true"])))
                yp.append(float(row["y_prob"]))
                if has_sg:
                    sg.append((row[subgroup_col] or "nan").strip())
        yt = np.asarray(yt, dtype=np.int8)
        if y_true_ref is None:
            y_true_ref = yt
            if sg:
                subgroup = np.asarray(sg, dtype=object)
        elif yt.shape != y_true_ref.shape or not np.array_equal(yt, y_true_ref):
            raise SystemExit(
                f"{run_dir}: {fold_dir.name}/predictions.csv does not have the same "
                "rows (or row order) as the first fold. The shared-index bootstrap "
                "assumes all folds score the identical test set — refusing to guess."
            )
        probs.append(np.asarray(yp, dtype=np.float64))
        folds.append(fold_dir.name)

    if y_true_ref is None or not probs:
        return None
    return y_true_ref, probs, subgroup, folds


# --------------------------------------------------------------------------- #
# Bootstrap
# --------------------------------------------------------------------------- #
def _make_indices(n: int, n_boot: int, seed: int) -> np.ndarray:
    """(n_boot, n) resample indices, drawn ONCE and reused for every run — that
    shared draw is exactly what makes the paired deltas below valid."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n, size=(n_boot, n), dtype=np.int64)


def _make_stratified_indices(mask: np.ndarray, n_boot: int, seed: int) -> np.ndarray:
    """Resample WITHIN one subgroup, preserving that group's size."""
    pos = np.flatnonzero(mask)
    rng = np.random.default_rng(seed)
    return pos[rng.integers(0, len(pos), size=(n_boot, len(pos)), dtype=np.int64)]


def bootstrap_run(y_true, probs, indices, metrics=METRICS, point_idx=None):
    """-> {metric: (point_estimate, replicate_vector)} using the fold-mean statistic.

    `point_idx` restricts the POINT estimate to a row subset, and must be passed
    whenever `indices` is subgroup-stratified — otherwise the point estimate is
    silently the whole test set while the interval describes the subgroup.
    """
    if point_idx is None:
        point_idx = slice(None)
    yt_point = y_true[point_idx]

    # Point estimates come from the repo's own functions, so they reproduce
    # test_metrics.json exactly rather than a lookalike.
    out = {m: (float(np.mean([_metric(m, yt_point, p[point_idx]) for p in probs])),
               np.empty(len(indices), dtype=np.float64))
           for m in metrics}

    n = len(y_true)
    curves = [(_SortedCurve(y_true, p), _SortedCurve(1 - y_true, -p)) for p in probs]
    per_fold = np.empty(len(probs), dtype=np.float64)
    for b, idx in enumerate(indices):
        # A resample = integer multiplicities over the original rows.
        w = np.bincount(idx, minlength=n).astype(np.float64)
        vals = [_fast_metrics(c, f, w, metrics) for c, f in curves]
        for m in metrics:
            for k, v in enumerate(vals):
                per_fold[k] = v[m]
            out[m][1][b] = np.mean(per_fold)
    return out


def ci(reps: np.ndarray, alpha: float = 0.05) -> dict:
    """Percentile interval, NaN replicates excluded and counted."""
    good = reps[~np.isnan(reps)]
    if good.size == 0:
        return {"lo": None, "hi": None, "n_valid": 0, "n_dropped": int(reps.size)}
    lo, hi = np.percentile(good, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {
        "lo": float(lo),
        "hi": float(hi),
        "n_valid": int(good.size),
        "n_dropped": int(reps.size - good.size),
    }


def _fmt(point, c) -> str:
    if c["lo"] is None:
        return f"{point:.4f} [undefined]"
    return f"{point:.4f} [{c['lo']:.4f}, {c['hi']:.4f}]"


def _fmt_delta(point, c) -> str:
    if c["lo"] is None:
        return f"{point:+.4f} [undefined]"
    sig = "" if (c["lo"] <= 0.0 <= c["hi"]) else " *"
    return f"{point:+.4f} [{c['lo']:+.4f}, {c['hi']:+.4f}]{sig}"


# --------------------------------------------------------------------------- #
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results-dir", type=Path, required=True,
                    help="Tree of run-dirs holding fold_*/predictions.csv "
                         "(reports/external/<ds>/<variant> or experiments/runs)")
    ap.add_argument("--n-boot", type=int, default=2000, help="Bootstrap replicates (default 2000)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--alpha", type=float, default=0.05, help="1-alpha CI (default 0.05 -> 95%%)")
    ap.add_argument("--subgroup-col", default=None,
                    help="Column in predictions.csv to bootstrap fairness gaps over "
                         "(e.g. tone_group). Skipped if absent.")
    ap.add_argument("--min-subgroup-n", type=int, default=20)
    ap.add_argument("--pair", action="append", default=[], metavar="RUN_A:RUN_B",
                    help="Paired delta between TWO named run-dirs, signed A - B. Repeatable. "
                         "Sections 2 and 2b only pair kd-vs-baseline and suffix-vs-main, so "
                         "comparing two KD runs to each other needs this. Names are the "
                         "run-dir names relative to --results-dir, e.g. "
                         "kd_maxvit_base_to_fastvit_sa12:kd_convnextv2_base_to_mobilenetv4_conv_medium")
    ap.add_argument("--metrics", default=",".join(METRICS),
                    help=f"Comma-separated subset of {','.join(METRICS)}")
    ap.add_argument("--out-json", type=Path, default=None,
                    help="Default: <results-dir>/bootstrap_ci.json")
    ap.add_argument("--out-md", type=Path, default=None,
                    help="Default: <results-dir>/bootstrap_ci.md")
    args = ap.parse_args()

    metrics = tuple(m.strip() for m in args.metrics.split(",") if m.strip())
    unknown = [m for m in metrics if m not in METRICS]
    if unknown:
        ap.error(f"unknown metric(s) {unknown}; choose from {list(METRICS)}")

    runs = find_run_dirs(args.results_dir)
    if not runs:
        raise SystemExit(
            f"No run-dirs with fold_*/ found under {args.results_dir}.\n"
            "Note teacher runs must stay nested as teacher/<name> — flattening them "
            "makes the discovery skip them."
        )

    # ---- 1. per-run CIs -------------------------------------------------- #
    loaded, boots, indices = {}, {}, None
    for rel, path in sorted(runs):
        data = load_run_predictions(path, args.subgroup_col)
        if data is None:
            print(f"skip (no predictions.csv): {rel}", file=sys.stderr)
            continue
        y_true, probs, subgroup, folds = data
        if indices is None:
            indices = _make_indices(len(y_true), args.n_boot, args.seed)
            n_rows = len(y_true)
        elif len(y_true) != indices.shape[1]:
            print(f"skip (different test-set size, cannot pair): {rel}", file=sys.stderr)
            continue
        loaded[rel] = (y_true, probs, subgroup, folds)
        # Gate the fast path against the repo's own metric functions before any
        # interval is computed from it.
        _verify_fast_path(y_true, probs, metrics)
        boots[rel] = bootstrap_run(y_true, probs, indices, metrics)
        print(f"[bootstrap] {rel}: {len(folds)} folds x {args.n_boot} replicates", file=sys.stderr)

    if not boots:
        raise SystemExit("No run produced predictions — nothing to bootstrap.")

    report = {
        "results_dir": str(args.results_dir),
        "n_boot": args.n_boot,
        "seed": args.seed,
        "alpha": args.alpha,
        "n_test_rows": int(n_rows),
        "fold_convention": ("shared row indices across folds; statistic = mean over folds "
                            "(folds are models on the SAME test rows, so predictions are "
                            "never pooled)"),
        "metrics": list(metrics),
        "per_run": {},
        "kd_deltas": {},
        "ablation_deltas": {},
        "ablation_deltas_by_subgroup": {},
        "explicit_pairs": {},
        "explicit_pairs_by_subgroup": {},
        "fairness_gaps": {},
    }
    for rel, res in boots.items():
        report["per_run"][rel] = {
            # Surfaced because not every run has all 5 folds — a 3-fold interval
            # must not be quoted as if it were a 5-fold one.
            "n_folds": len(loaded[rel][3]),
            **{m: {"point": res[m][0], **ci(res[m][1], args.alpha)} for m in metrics},
        }

    # ---- 2. paired KD deltas --------------------------------------------- #
    # kd_<teacher>_to_<student>  vs  baseline_<student> (same suffix).
    by_key = {}
    for rel in boots:
        info = parse_run_name(rel)
        if info:
            by_key[rel] = info
    for rel, info in by_key.items():
        if info["kind"] != "kd":
            continue
        base_rel = next(
            (r for r, i in by_key.items()
             if i["kind"] == "baseline" and i["student"] == info["student"]
             and i["suffix"] == info["suffix"]),
            None,
        )
        if base_rel is None:
            continue
        entry = {"kd_run": rel, "baseline_run": base_rel}
        for m in metrics:
            kd_pt, kd_reps = boots[rel][m]
            bl_pt, bl_reps = boots[base_rel][m]
            # Same seeded indices on both -> element-wise difference IS the
            # paired bootstrap of the delta.
            entry[m] = {"point": kd_pt - bl_pt, **ci(kd_reps - bl_reps, args.alpha)}
        report["kd_deltas"][rel] = entry

    # ---- 2b. paired ablation deltas --------------------------------------- #
    # <run>__<suffix>  vs  the SAME run with no suffix — the `run_suffix` fork
    # convention (train_student.py:44). Covers the PAD arms
    # (baseline_<s>__train_isic_only) and the sampler arms (__samp_off/__ratio3),
    # neither of which section 2 can pair: both sides are kind="baseline" there,
    # so the kd-vs-baseline lookup never fires.
    #
    # SIGN: point = main − ablated, so a POSITIVE delta means the main
    # configuration (PAD mixed in / sampler at 1:5) wins. Read it the same way as
    # the KD delta above, not as "suffix minus baseline".
    for rel, info in by_key.items():
        if not info["suffix"]:
            continue
        main_rel = next(
            (r for r, i in by_key.items()
             if not i["suffix"] and i["kind"] == info["kind"]
             and i["student"] == info["student"] and i["teacher"] == info["teacher"]),
            None,
        )
        if main_rel is None:
            continue
        entry = {"ablated_run": rel, "main_run": main_rel, "suffix": info["suffix"]}
        for m in metrics:
            ab_pt, ab_reps = boots[rel][m]
            mn_pt, mn_reps = boots[main_rel][m]
            # Same seeded indices on both -> element-wise difference IS the
            # paired bootstrap of the delta (identical argument to section 2).
            entry[m] = {"point": mn_pt - ab_pt, **ci(mn_reps - ab_reps, args.alpha)}
        report["ablation_deltas"][rel] = entry

    # ---- 2c. explicit A-vs-B pairs ---------------------------------------- #
    # Sections 2 and 2b only reach kd-vs-baseline and suffix-vs-main. Comparing two
    # KD runs to EACH OTHER (e.g. the two ship candidates on the Pareto frontier)
    # has no automatic rule, so it is named on the command line. Same shared index
    # arrays, so this is a genuine paired delta — which matters: two overlapping
    # UNPAIRED per-run intervals can still hide a paired difference that excludes 0.
    for spec in args.pair:
        if spec.count(":") != 1:
            raise SystemExit(f"ERROR: --pair wants exactly one ':' -> got {spec!r}")
        a_rel, b_rel = (x.strip() for x in spec.split(":"))
        missing = [r for r in (a_rel, b_rel) if r not in boots]
        if missing:
            raise SystemExit(
                f"ERROR: --pair {spec}: not bootstrapped: {missing}\n"
                f"Available: {', '.join(sorted(boots))}"
            )
        entry = {"run_a": a_rel, "run_b": b_rel, "sign": "a_minus_b"}
        for m in metrics:
            a_pt, a_reps = boots[a_rel][m]
            b_pt, b_reps = boots[b_rel][m]
            entry[m] = {"point": a_pt - b_pt, **ci(a_reps - b_reps, args.alpha)}
        report["explicit_pairs"][f"{a_rel} vs {b_rel}"] = entry

    # ---- 3. paired fairness gaps ----------------------------------------- #
    # Keeps each run's per-group replicate vectors so section 5 can difference
    # them across runs. Valid because _make_stratified_indices is seeded from the
    # GROUP index only (seed + 1000 + gi), never from the run — every run
    # therefore draws the SAME rows for the same group, which is exactly the
    # pairing requirement.
    sub_boots: dict[str, dict] = {}
    if args.subgroup_col:
        for rel, (y_true, probs, subgroup, _folds) in loaded.items():
            if subgroup is None:
                continue
            groups = [g for g in sorted(set(subgroup.tolist()))
                      if g not in ("nan", "") and int((subgroup == g).sum()) >= args.min_subgroup_n]
            if len(groups) < 2:
                continue
            # Stratified draws: each group is resampled at its own size, so a
            # 137-row group stays a 137-row group and its width shows honestly.
            g_boot = {}
            for gi, g in enumerate(groups):
                mask = subgroup == g
                gidx = _make_stratified_indices(mask, args.n_boot, args.seed + 1000 + gi)
                # point_idx is REQUIRED here: without it the point estimate would
                # be the whole test set while the interval describes the group.
                g_boot[g] = bootstrap_run(y_true, probs, gidx, metrics,
                                          point_idx=np.flatnonzero(mask))
            entry = {"n_per_group": {g: int((subgroup == g).sum()) for g in groups},
                     "per_group": {}, "gaps": {}}
            for g in groups:
                entry["per_group"][g] = {
                    m: {"point": g_boot[g][m][0], **ci(g_boot[g][m][1], args.alpha)}
                    for m in metrics
                }
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    a, b = groups[i], groups[j]
                    pair = {}
                    for m in metrics:
                        # The gap is bootstrapped DIRECTLY, not read off two
                        # separate intervals by eye. Tone groups are DISJOINT row
                        # sets, so there is nothing to pair across them and the
                        # independent within-group draws are the correct pairing
                        # here — differencing the replicate vectors gives the
                        # sampling distribution of the gap itself.
                        pt = g_boot[a][m][0] - g_boot[b][m][0]
                        pair[m] = {"point": pt,
                                   **ci(g_boot[a][m][1] - g_boot[b][m][1], args.alpha)}
                    entry["gaps"][f"{a}_minus_{b}"] = pair
            report["fairness_gaps"][rel] = entry
            sub_boots[rel] = g_boot

    # ---- 5. paired ablation deltas WITHIN each subgroup ------------------- #
    # Section 3 answers the ablation on the WHOLE test set. For the PAD-mixing
    # arms that is the wrong cell: the ISIC-only arm collapses on the 377 PAD
    # rows, and those rows carry ~75% of all positives, so the whole-test delta
    # is inflated. The decisive cell is the delta restricted to one source
    # subset — which is what this section reports, still paired.
    for rel, info in by_key.items():
        if not info["suffix"] or rel not in sub_boots:
            continue
        main_rel = next(
            (r for r, i in by_key.items()
             if not i["suffix"] and i["kind"] == info["kind"]
             and i["student"] == info["student"] and i["teacher"] == info["teacher"]
             and r in sub_boots),
            None,
        )
        if main_rel is None:
            continue
        entry = {"ablated_run": rel, "main_run": main_rel, "suffix": info["suffix"],
                 "by_group": {}}
        for g in sub_boots[rel]:
            if g not in sub_boots[main_rel]:
                continue
            entry["by_group"][g] = {}
            for m in metrics:
                ab_pt, ab_reps = sub_boots[rel][g][m]
                mn_pt, mn_reps = sub_boots[main_rel][g][m]
                entry["by_group"][g][m] = {"point": mn_pt - ab_pt,
                                           **ci(mn_reps - ab_reps, args.alpha)}
        if entry["by_group"]:
            report["ablation_deltas_by_subgroup"][rel] = entry

    # ---- 6. explicit A-vs-B pairs WITHIN each subgroup -------------------- #
    for spec in args.pair:
        a_rel, b_rel = (x.strip() for x in spec.split(":"))
        if a_rel not in sub_boots or b_rel not in sub_boots:
            continue
        entry = {"run_a": a_rel, "run_b": b_rel, "sign": "a_minus_b", "by_group": {}}
        for g in sub_boots[a_rel]:
            if g not in sub_boots[b_rel]:
                continue
            entry["by_group"][g] = {}
            for m in metrics:
                a_pt, a_reps = sub_boots[a_rel][g][m]
                b_pt, b_reps = sub_boots[b_rel][g][m]
                entry["by_group"][g][m] = {"point": a_pt - b_pt,
                                           **ci(a_reps - b_reps, args.alpha)}
        if entry["by_group"]:
            report["explicit_pairs_by_subgroup"][f"{a_rel} vs {b_rel}"] = entry

    # ---- write ------------------------------------------------------------ #
    out_json = args.out_json or args.results_dir / "bootstrap_ci.json"
    out_md = args.out_md or args.results_dir / "bootstrap_ci.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2))

    pct = int(round((1 - args.alpha) * 100))
    lines = [
        f"# Bootstrap {pct}% confidence intervals — `{args.results_dir}`",
        "",
        f"B = {args.n_boot} replicates, seed {args.seed}, {n_rows} test rows.",
        "",
        "**Fold convention:** each replicate draws one set of row indices, scores "
        "**every fold** on those same rows, and averages. Folds are five models on "
        "the *same* test set, so their predictions are never pooled (that would "
        "replicate each row 5× and shrink the interval into fiction). The interval "
        "therefore describes the same fold-mean the other tables quote, with the "
        "test set's sampling error instead of the between-model spread.",
        "",
        "## 1. Per-run",
        "",
        "| Run | folds | " + " | ".join(metrics) + " |",
        "|---|---|" + "---|" * len(metrics),
    ]
    for rel in sorted(report["per_run"]):
        row = report["per_run"][rel]
        nf = row["n_folds"]
        flag = "" if nf == 5 else " ⚠"
        lines.append(f"| `{rel}` | {nf}{flag} | "
                     + " | ".join(_fmt(row[m]["point"], row[m]) for m in metrics) + " |")

    if report["kd_deltas"]:
        lines += [
            "",
            "## 2. KD effect — paired bootstrap (KD − baseline)",
            "",
            "Both models are resampled on the **identical** rows, so the correlation "
            "between them is kept; an unpaired interval would overstate the "
            "uncertainty. `*` marks an interval excluding 0.",
            "",
            "| KD run | vs baseline | " + " | ".join(metrics) + " |",
            "|---|---|" + "---|" * len(metrics),
        ]
        for rel in sorted(report["kd_deltas"]):
            e = report["kd_deltas"][rel]
            lines.append(
                f"| `{rel}` | `{e['baseline_run']}` | "
                + " | ".join(_fmt_delta(e[m]["point"], e[m]) for m in metrics) + " |"
            )

    if report["ablation_deltas"]:
        lines += [
            "",
            "## 3. Ablation effect — paired bootstrap (main − ablated)",
            "",
            "Pairs each `__<suffix>` fork against the same run without the suffix. "
            "The sign is **main − ablated**, so a positive delta means the main "
            "configuration wins (e.g. `__train_isic_only` → positive = mixing "
            "PAD-UFES-20 into TRAIN+VAL helps). Same identical-rows pairing as "
            "section 2. `*` marks an interval excluding 0.",
            "",
            "| Ablated run | vs main | " + " | ".join(metrics) + " |",
            "|---|---|" + "---|" * len(metrics),
        ]
        for rel in sorted(report["ablation_deltas"]):
            e = report["ablation_deltas"][rel]
            lines.append(
                f"| `{rel}` | `{e['main_run']}` | "
                + " | ".join(_fmt_delta(e[m]["point"], e[m]) for m in metrics) + " |"
            )

    if report["explicit_pairs"]:
        lines += [
            "",
            "## 3b. Named A-vs-B pairs — paired bootstrap (A − B)",
            "",
            "Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and "
            "suffix-vs-main, so two KD runs compared to each other land here. **This is the "
            "table to read when two per-run intervals in section 1 overlap** — overlapping "
            "unpaired intervals do not mean the models are equivalent; the paired delta can "
            "still exclude 0. `*` marks an interval excluding 0.",
            "",
            "| A | B | " + " | ".join(metrics) + " |",
            "|---|---|" + "---|" * len(metrics),
        ]
        for key in sorted(report["explicit_pairs"]):
            e = report["explicit_pairs"][key]
            lines.append(
                f"| `{e['run_a']}` | `{e['run_b']}` | "
                + " | ".join(_fmt_delta(e[m]["point"], e[m]) for m in metrics) + " |"
            )

    if report["fairness_gaps"]:
        lines += ["", f"## 4. Fairness gaps — paired bootstrap over `{args.subgroup_col}`", ""]
        for rel in sorted(report["fairness_gaps"]):
            e = report["fairness_gaps"][rel]
            sizes = ", ".join(f"{g} n={n}" for g, n in e["n_per_group"].items())
            lines += [f"### `{rel}`", "", f"Group sizes (per fold): {sizes}", "",
                      "| Group / gap | " + " | ".join(metrics) + " |",
                      "|---|" + "---|" * len(metrics)]
            for g, row in e["per_group"].items():
                lines.append(f"| {g} | " + " | ".join(_fmt(row[m]["point"], row[m]) for m in metrics) + " |")
            for gap, row in e["gaps"].items():
                lines.append(f"| **{gap}** | " + " | ".join(_fmt_delta(row[m]["point"], row[m]) for m in metrics) + " |")
            lines.append("")

    if report["ablation_deltas_by_subgroup"]:
        lines += [
            "",
            f"## 5. Ablation effect **within each `{args.subgroup_col}`** — paired (main − ablated)",
            "",
            "Section 3 gives the ablation delta on the whole test set. For the "
            "PAD-mixing arms that is the wrong cell — the ISIC-only arm collapses "
            "on the PAD rows, and those rows carry ~75% of all positives, so the "
            "whole-test delta is inflated. **Quote this table instead.** Still "
            "paired: every run draws the same rows for a given group, so the "
            "replicate vectors difference directly. `*` marks an interval "
            "excluding 0.",
            "",
            "| Ablated run | vs main | group | " + " | ".join(metrics) + " |",
            "|---|---|---|" + "---|" * len(metrics),
        ]
        for rel in sorted(report["ablation_deltas_by_subgroup"]):
            e = report["ablation_deltas_by_subgroup"][rel]
            for g, row in e["by_group"].items():
                lines.append(
                    f"| `{rel}` | `{e['main_run']}` | {g} | "
                    + " | ".join(_fmt_delta(row[m]["point"], row[m]) for m in metrics) + " |"
                )

    if report["explicit_pairs_by_subgroup"]:
        lines += [
            "",
            f"## 6. Named A-vs-B pairs **within each `{args.subgroup_col}`** — paired (A − B)",
            "",
            "The per-subgroup version of section 3b. On the in-domain tree this splits the "
            "delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test "
            "row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. "
            "`*` marks an interval excluding 0.",
            "",
            "| A | B | group | " + " | ".join(metrics) + " |",
            "|---|---|---|" + "---|" * len(metrics),
        ]
        for key in sorted(report["explicit_pairs_by_subgroup"]):
            e = report["explicit_pairs_by_subgroup"][key]
            for g, row in e["by_group"].items():
                lines.append(
                    f"| `{e['run_a']}` | `{e['run_b']}` | {g} | "
                    + " | ".join(_fmt_delta(row[m]["point"], row[m]) for m in metrics) + " |"
                )

    out_md.write_text("\n".join(lines) + "\n")
    print(f"[bootstrap] wrote {out_json}")
    print(f"[bootstrap] wrote {out_md}")


if __name__ == "__main__":
    main()
