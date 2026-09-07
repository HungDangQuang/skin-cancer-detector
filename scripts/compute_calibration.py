"""
Offline probability-calibration analysis for a fold-scoped run directory.

WHY: the models train on an undersampled prior (~16.7% malignant, the 1:5
DynamicUndersampledSampler ratio) rather than the true ~0.39% prevalence, so the
raw ``sigmoid(logit)`` is systematically over-confident when shown as a "% risk".
The RANKING metrics (pAUC@TPR80 / AUPRC / AUC-ROC) are invariant to a monotone
re-scaling of probabilities and are therefore UNCHANGED — this script does not
touch the Chapter-4 numbers. It only produces honest displayed probabilities plus
a reliability curve + ECE/Brier before-vs-after, from prediction CSVs that already
exist (no re-training / re-inference needed).

Three correction modes (``--method``):
  none      prior-shift closed form (default). Corrects ONLY the prior mismatch
            introduced by undersampling — needs no fit set:
                logit_cal = logit(p) + (logit(pi_target) - logit(pi_train))
            with pi_train = 1/(1+ratio) and pi_target = target prevalence.
  isotonic  non-parametric monotone map fit on the VAL predictions (which keep the
            true prevalence — val loader has no sampler), applied to TEST.
  platt     logistic (Platt) scaling on the val log-odds, applied to TEST.

CAVEAT: focal loss with loss.alpha=0.25 also distorts calibration BEYOND the prior;
prior-shift only fixes the prior term. If ECE stays high after --method none, use
--method isotonic or platt (they need val_predictions.csv, written by the training
scripts alongside predictions.csv).

Reuses brier_score / expected_calibration_error from src.evaluation.metrics so the
raw numbers match test_metrics.json exactly.

Runs on the SERVER (needs numpy + scikit-learn + matplotlib), not the Mac.

Optional --subgroup <col> (direction D fairness diagnostic): break the raw-vs-
calibrated ECE/Brier down per subgroup (e.g. anatom_site_general / sex). Needs
data.metadata_cols set at prepare-time so the column exists in predictions.csv.
The GLOBAL correction is unchanged — no per-group calibrator is fit (too few
positives per group at 0.39% prevalence); it only REPORTS per-group calibration.

Usage:
    python scripts/compute_calibration.py --run-dir experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium
    python scripts/compute_calibration.py --run-dir <run> --target-prevalence 0.0039
    python scripts/compute_calibration.py --run-dir <run> --method isotonic
    python scripts/compute_calibration.py --run-dir <run> --subgroup anatom_site_general
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from statistics import mean, stdev

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.evaluation.metrics import brier_score, expected_calibration_error  # noqa: E402

_EPS = 1e-6


def _logit(p: np.ndarray | float) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), _EPS, 1.0 - _EPS)
    return np.log(p / (1.0 - p))


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=float)))


def load_predictions(csv_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read (y_true, y_prob) from a predictions CSV (cols y_true,y_prob,y_pred[,source])."""
    y_true, y_prob = [], []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            y_true.append(int(float(row["y_true"])))
            y_prob.append(float(row["y_prob"]))
    return np.asarray(y_true, dtype=float), np.asarray(y_prob, dtype=float)


def load_column(csv_path: Path, col: str) -> np.ndarray | None:
    """Read one column (as strings) from a predictions CSV; None if absent.

    Used by --subgroup: an empty/blank cell becomes "nan" so PAD rows (which
    have no ISIC metadata) group into a single explicit bucket instead of "".
    """
    vals: list[str] = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        if col not in (reader.fieldnames or []):
            return None
        for row in reader:
            v = str(row.get(col, "")).strip()
            vals.append(v if v else "nan")
    return np.asarray(vals, dtype=object)


def prior_correct(p: np.ndarray, pi_train: float, pi_target: float) -> np.ndarray:
    """Closed-form prior-shift: move log-odds by logit(pi_target) - logit(pi_train)."""
    shift = float(_logit(pi_target)) - float(_logit(pi_train))
    return _sigmoid(_logit(p) + shift)


def fit_apply(method: str, val_true, val_prob, test_prob) -> np.ndarray:
    """Fit a val-based calibrator and apply it to the test probabilities."""
    if method == "isotonic":
        from sklearn.isotonic import IsotonicRegression

        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        iso.fit(val_prob, val_true)
        return np.clip(iso.predict(test_prob), 0.0, 1.0)
    if method == "platt":
        from sklearn.linear_model import LogisticRegression

        lr = LogisticRegression(C=1e6, solver="lbfgs")  # ~unregularized Platt on log-odds
        lr.fit(_logit(val_prob).reshape(-1, 1), val_true.astype(int))
        return lr.predict_proba(_logit(test_prob).reshape(-1, 1))[:, 1]
    raise ValueError(f"Unknown fit method: {method}")


def _fold_index(fold_dir: Path) -> int:
    try:
        return int(fold_dir.name.split("_", 1)[1])
    except (IndexError, ValueError):
        return -1


def discover_folds(run_dir: Path) -> list[tuple[int, Path]]:
    """(fold_idx, fold_dir) for each fold_*/predictions.csv; bare predictions.csv -> fold -1."""
    folds = []
    for fold_dir in sorted(run_dir.glob("fold_*")):
        if (fold_dir / "predictions.csv").is_file():
            folds.append((_fold_index(fold_dir), fold_dir))
    if not folds and (run_dir / "predictions.csv").is_file():
        folds.append((-1, run_dir))
    return folds


def _reliability_curve(y_true, raw, cal, out_path: Path, method: str) -> None:
    """Pooled raw-vs-calibrated reliability curve (quantile bins for heavy imbalance)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.calibration import calibration_curve

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="perfectly calibrated")
    for probs, name, color in ((raw, "raw sigmoid", "tab:red"),
                               (cal, f"calibrated ({method})", "tab:green")):
        try:
            frac_pos, mean_pred = calibration_curve(y_true, probs, n_bins=10, strategy="quantile")
            ax.plot(mean_pred, frac_pos, "o-", color=color, label=name)
        except ValueError:
            continue
    ax.set_xlabel("mean predicted probability")
    ax.set_ylabel("observed positive rate")
    ax.set_title("Reliability curve (pooled folds)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-dir", type=Path, required=True,
                    help="run dir holding fold_*/predictions.csv (KD/baseline/teacher run)")
    ap.add_argument("--ratio", type=float, default=5.0,
                    help="undersampler malignant:benign ratio (pi_train = 1/(1+ratio)); default 5")
    ap.add_argument("--target-prevalence", default="auto",
                    help="displayed prevalence for prior-shift: 'auto' (mean y_true of test) or a float")
    ap.add_argument("--method", choices=["none", "isotonic", "platt"], default="none",
                    help="none = prior-shift closed form (default); isotonic/platt fit on val_predictions.csv")
    ap.add_argument("--subgroup", default=None,
                    help="predictions.csv column (e.g. anatom_site_general / sex) to break "
                         "calibration ECE/Brier down by. Needs data.metadata_cols set at "
                         "prepare-time so the column exists in predictions.csv (direction D).")
    ap.add_argument("--min-subgroup-n", type=int, default=20,
                    help="skip subgroups with fewer than this many pooled samples (default 20)")
    # Output paths are overridable so one run-dir can hold several --subgroup
    # breakdowns side by side (the fixed default name would overwrite the
    # previous subgroup's JSON).
    ap.add_argument("--out-json", type=Path, default=None,
                    help="default: <run-dir>/calibration_metrics.json")
    ap.add_argument("--out-png", type=Path, default=None,
                    help="default: <run-dir>/reliability_curve.png")
    args = ap.parse_args()

    run_dir: Path = args.run_dir
    if not run_dir.is_dir():
        print(f"ERROR: not a directory: {run_dir}", file=sys.stderr)
        sys.exit(1)

    folds = discover_folds(run_dir)
    if not folds:
        print(f"ERROR: no fold_*/predictions.csv (or predictions.csv) under {run_dir}", file=sys.stderr)
        sys.exit(1)

    pi_train = 1.0 / (1.0 + args.ratio)
    per_fold: dict[str, dict] = {}
    pooled_true, pooled_raw, pooled_cal = [], [], []
    pooled_sub: list = []
    subgroup_missing = False  # True if --subgroup col absent from any used fold

    for idx, fold_dir in folds:
        y_true, y_prob = load_predictions(fold_dir / "predictions.csv")
        sub_vals = None
        if args.subgroup:
            sub_vals = load_column(fold_dir / "predictions.csv", args.subgroup)
            if sub_vals is None:
                subgroup_missing = True
            elif len(sub_vals) != len(y_true):
                print(f"WARN fold {idx}: --subgroup column length mismatch; skipping subgroup.",
                      file=sys.stderr)
                subgroup_missing = True

        if args.method == "none":
            if args.target_prevalence == "auto":
                pi_target = float(y_true.mean())
            else:
                pi_target = float(args.target_prevalence)
            if not (0.0 < pi_target < 1.0):
                print(f"WARN fold {idx}: target prevalence {pi_target} out of (0,1); skipping.",
                      file=sys.stderr)
                continue
            p_cal = prior_correct(y_prob, pi_train, pi_target)
        else:
            val_csv = fold_dir / "val_predictions.csv"
            if not val_csv.is_file():
                print(f"WARN fold {idx}: --method {args.method} needs {val_csv} (missing); skipping.",
                      file=sys.stderr)
                continue
            val_true, val_prob = load_predictions(val_csv)
            pi_target = float(y_true.mean())  # for reporting only
            p_cal = fit_apply(args.method, val_true, val_prob, y_prob)

        per_fold[str(idx)] = {
            "pi_target": pi_target,
            "n": int(len(y_true)),
            "brier_raw": brier_score(y_true, y_prob),
            "ece_raw": expected_calibration_error(y_true, y_prob),
            "brier_cal": brier_score(y_true, p_cal),
            "ece_cal": expected_calibration_error(y_true, p_cal),
        }
        pooled_true.append(y_true)
        pooled_raw.append(y_prob)
        pooled_cal.append(p_cal)
        if args.subgroup and sub_vals is not None and len(sub_vals) == len(y_true):
            pooled_sub.append(sub_vals)

    if not per_fold:
        print("ERROR: no fold produced calibration numbers (see warnings above).", file=sys.stderr)
        sys.exit(1)

    metric_keys = ["brier_raw", "ece_raw", "brier_cal", "ece_cal"]
    agg_mean = {k: mean(f[k] for f in per_fold.values()) for k in metric_keys}
    agg_std = {k: (stdev([f[k] for f in per_fold.values()]) if len(per_fold) > 1 else 0.0)
               for k in metric_keys}

    y_true_all = np.concatenate(pooled_true)
    raw_all = np.concatenate(pooled_raw)
    cal_all = np.concatenate(pooled_cal)

    out = {
        "run_dir": str(run_dir),
        "method": args.method,
        "ratio": args.ratio,
        "pi_train": pi_train,
        "target_prevalence": args.target_prevalence,
        "n_folds": len(per_fold),
        "per_fold": per_fold,
        "mean": agg_mean,
        "std": agg_std,
    }

    # --- Optional per-subgroup breakdown (direction D fairness diagnostic) ---
    # Same GLOBAL correction (no per-group calibrator — too few positives per group
    # at 0.39% prevalence to fit one honestly); we only REPORT raw-vs-calibrated
    # ECE/Brier per subgroup so uneven calibration quality across site/sex is visible.
    if args.subgroup:
        if subgroup_missing or not pooled_sub:
            print(f"WARN: --subgroup '{args.subgroup}' not found in predictions.csv "
                  f"(set data.metadata_cols at prepare-time + re-eval); skipping subgroup.",
                  file=sys.stderr)
        else:
            sub_all = np.concatenate(pooled_sub)
            groups: dict[str, dict] = {}
            for g in sorted(set(sub_all.tolist())):
                mask = sub_all == g
                n_g = int(mask.sum())
                if n_g < args.min_subgroup_n:
                    continue
                yt, rw, cl = y_true_all[mask], raw_all[mask], cal_all[mask]
                groups[str(g)] = {
                    "n": n_g,
                    "prevalence": float(yt.mean()),
                    "brier_raw": brier_score(yt, rw),
                    "ece_raw": expected_calibration_error(yt, rw),
                    "brier_cal": brier_score(yt, cl),
                    "ece_cal": expected_calibration_error(yt, cl),
                }
            out["subgroup_col"] = args.subgroup
            out["min_subgroup_n"] = args.min_subgroup_n
            out["subgroups"] = groups
            print(f"[calibration] subgroup '{args.subgroup}': {len(groups)} groups "
                  f">= {args.min_subgroup_n} samples")
            for g, m in groups.items():
                print(f"[calibration]   {g:>20} n={m['n']:<6} prev={m['prevalence']:.4f} "
                      f"ECE {m['ece_raw']:.4f}->{m['ece_cal']:.4f}")

    json_path = args.out_json or (run_dir / "calibration_metrics.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(out, indent=2))
    print(f"[calibration] wrote {json_path} ({len(per_fold)} folds, method={args.method})")
    print(f"[calibration] ECE  raw {agg_mean['ece_raw']:.4f} -> cal {agg_mean['ece_cal']:.4f} | "
          f"Brier raw {agg_mean['brier_raw']:.4f} -> cal {agg_mean['brier_cal']:.4f}")

    png_path = args.out_png or (run_dir / "reliability_curve.png")
    _reliability_curve(y_true_all, raw_all, cal_all, png_path, args.method)
    print(f"[calibration] wrote {png_path}")


if __name__ == "__main__":
    main()
