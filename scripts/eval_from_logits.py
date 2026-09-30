#!/usr/bin/env python
"""
Score a logits CSV against the mobile-eval bundle manifest, and emit one table.

This is the SHARED scorer for both arms (contract: docs/MOBILE_EVAL_PIPELINE.md
sections 3 and 6). The server arm and the phone arm each produce a
`sample_id,logit,error` CSV; running THIS program on both is what makes the two
tables structurally identical. Do not compute metrics on the device, and do not
write a second scorer for the server: the project's pAUC@TPR>=80 definition must
come from one implementation only (src/evaluation/metrics.py).

Steps 9-11 of the spec happen here: sigmoid, the FROZEN threshold, metrics.
The threshold is taken from the run's own internal val_predictions.csv (Youden's
J) and is never refit on the evaluation set.

Usage:
    # one arm -> metrics.json + table.md
    python scripts/eval_from_logits.py \
        --manifest data/mobile_eval_bundle/manifest.csv \
        --logits reports/mobile_eval/server_logits.csv \
        --threshold-from experiments/runs_newsplit_ddi/kd_.../fold_4/val_predictions.csv \
        --label server --out-dir reports/mobile_eval/server

    # side-by-side
    python scripts/eval_from_logits.py --compare \
        reports/mobile_eval/server/metrics.json \
        reports/mobile_eval/mobile/metrics.json \
        --out-dir reports/mobile_eval

Output:
    <out-dir>/metrics.json   {dataset: {metric: value}}, plus "_meta"
    <out-dir>/table.md       rows = dataset, fixed metric columns
    <out-dir>/comparison.md  (--compare) server | mobile | delta per dataset x metric
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd

from src.evaluation.metrics import compute_metrics, youden_threshold
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Fixed column set and order. Both arms emit exactly these, so the two tables can
# be laid side by side. Rank-based metrics first (threshold-free, so any delta is
# purely a runtime effect), then threshold-dependent ones, then calibration.
_METRICS = [
    "n",
    "prevalence",
    "auprc",
    "pauc_at_tpr80",
    "auc_roc",
    "sens_at_90spec",
    "sens_at_95spec",
    "sensitivity",
    "specificity",
    "f1_score",
    "brier",
    "ece",
]
_RANK_FREE = {"auprc", "pauc_at_tpr80", "auc_roc", "sens_at_90spec", "sens_at_95spec"}


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def load_logits(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"sample_id": str})
    for col in ("sample_id", "logit"):
        if col not in df.columns:
            raise SystemExit(f"ERROR: {path} has no '{col}' column (got {list(df.columns)})")
    if "error" not in df.columns:
        df["error"] = ""
    return df


def frozen_threshold(val_predictions: Path) -> float:
    """Youden's J on the run's own internal validation fold — never on the eval set."""
    df = pd.read_csv(val_predictions)
    for col in ("y_true", "y_prob"):
        if col not in df.columns:
            raise SystemExit(f"ERROR: {val_predictions} has no '{col}' column")
    thr = youden_threshold(df["y_true"].to_numpy(), df["y_prob"].to_numpy())
    logger.info(f"Frozen threshold {thr:.6f} from {val_predictions} (n={len(df)})")
    return thr


def score(manifest: pd.DataFrame, logits: pd.DataFrame, threshold: float) -> dict:
    merged = manifest.merge(logits, on="sample_id", how="left", validate="one_to_one")

    n_absent = int(merged["logit"].isna().sum())
    n_errored = int((merged["error"].fillna("") != "").sum())
    if n_absent:
        logger.warning(
            f"{n_absent} manifest row(s) have no usable logit "
            f"({n_errored} carry an explicit error string). They are EXCLUDED from the "
            "metrics; both arms must exclude the same rows for the tables to compare."
        )

    out: dict = {}
    for key, grp in merged.groupby("dataset", sort=False):
        ok = grp[grp["logit"].notna()]
        if ok.empty:
            logger.warning(f"{key}: no scored rows, skipped")
            continue
        y_true = ok["label"].astype(int).to_numpy()
        if len(np.unique(y_true)) < 2:
            logger.warning(f"{key}: single-class subset, metrics undefined — skipped")
            continue
        y_prob = _sigmoid(ok["logit"].astype(float).to_numpy())
        m = compute_metrics(y_true, y_prob, threshold=threshold)
        row = {k: m[k] for k in _METRICS if k in m}
        row["n"] = int(len(ok))
        row["prevalence"] = float(y_true.mean())
        row["n_unscored"] = int(len(grp) - len(ok))
        out[str(key)] = row
    return out


def write_table(results: dict, meta: dict, out_dir: Path, label: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(
        json.dumps({"_meta": meta, **results}, indent=2, default=float)
    )

    lines = [
        f"# Evaluation table — arm `{label}`",
        "",
        f"Runtime: **{meta.get('runtime', label)}** · batch **{meta.get('batch_size', 1)}** · "
        f"device **{meta.get('device', 'unspecified')}**",
        f"Frozen threshold: **{meta['threshold']:.6f}** (source: `{meta['threshold_source']}`)",
        "",
        "Structure is fixed by `docs/MOBILE_EVAL_PIPELINE.md` §6 so this table can be laid "
        "beside the other arm's. Rank-free metrics are marked †: a delta there can only come "
        "from the runtime, never from a threshold crossing.",
        "",
        "| dataset | " + " | ".join(m + ("†" if m in _RANK_FREE else "") for m in _METRICS) + " |",
        "|---" * (len(_METRICS) + 1) + "|",
    ]
    for key, row in results.items():
        cells = []
        for m in _METRICS:
            v = row.get(m)
            if v is None:
                cells.append("—")
            elif m == "n":
                cells.append(f"{int(v)}")
            else:
                cells.append(f"{v:.4f}")
        lines.append(f"| `{key}` | " + " | ".join(cells) + " |")

    unscored = {k: r["n_unscored"] for k, r in results.items() if r.get("n_unscored")}
    if unscored:
        lines += ["", f"**Rows excluded for missing/errored logits:** {unscored}"]
    lines += [
        "",
        "AUPRC is **not** comparable across datasets — its random baseline is the prevalence "
        "column, which differs by orders of magnitude here. Across datasets use `auc_roc` / "
        "`pauc_at_tpr80`; across arms within one dataset every column is fair.",
    ]
    (out_dir / "table.md").write_text("\n".join(lines) + "\n")
    logger.info(f"Wrote {out_dir/'metrics.json'} and {out_dir/'table.md'}")


def write_comparison(a_path: Path, b_path: Path, out_dir: Path) -> None:
    a_all = json.loads(a_path.read_text())
    b_all = json.loads(b_path.read_text())
    a_meta, b_meta = a_all.pop("_meta", {}), b_all.pop("_meta", {})
    a_label = a_meta.get("label", a_path.parent.name)
    b_label = b_meta.get("label", b_path.parent.name)

    if a_meta.get("manifest_sha") and a_meta.get("manifest_sha") != b_meta.get("manifest_sha"):
        logger.warning(
            "The two arms were scored against DIFFERENT manifests — the deltas below "
            "mix a data difference into a runtime difference."
        )
    if a_meta.get("threshold") != b_meta.get("threshold"):
        logger.warning(
            f"Different frozen thresholds ({a_meta.get('threshold')} vs "
            f"{b_meta.get('threshold')}): threshold-dependent rows are not comparable."
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Server vs mobile — same bundle, same checkpoint, same threshold",
        "",
        f"`{a_label}`: {a_meta.get('runtime', '?')} · batch {a_meta.get('batch_size', '?')} · "
        f"device {a_meta.get('device', '?')}",
        f"`{b_label}`: {b_meta.get('runtime', '?')} · batch {b_meta.get('batch_size', '?')} · "
        f"device {b_meta.get('device', '?')}",
        "",
        "Δ = " + f"`{b_label}` − `{a_label}`. † = threshold-free.",
        "",
        f"| dataset | metric | {a_label} | {b_label} | Δ |",
        "|---|---|---|---|---|",
    ]
    for key in a_all:
        if key not in b_all:
            logger.warning(f"{key} missing from {b_path}, skipped")
            continue
        for m in _METRICS:
            av, bv = a_all[key].get(m), b_all[key].get(m)
            if av is None or bv is None:
                continue
            tag = m + ("†" if m in _RANK_FREE else "")
            if m == "n":
                lines.append(f"| `{key}` | {tag} | {int(av)} | {int(bv)} | {int(bv) - int(av)} |")
            else:
                lines.append(f"| `{key}` | {tag} | {av:.4f} | {bv:.4f} | {bv - av:+.4f} |")
    lines += [
        "",
        "Reading it: a non-zero Δ on a † row comes from the runtime (graph lowering, or the "
        "JPEG decoder). On a non-† row it can additionally come from a logit crossing the "
        "frozen threshold. The project's single-fold rerun noise floor is 0.0053 AUPRC, but "
        "inference on a fixed checkpoint is deterministic, so a genuine runtime Δ should be "
        "far smaller than that.",
    ]
    (out_dir / "comparison.md").write_text("\n".join(lines) + "\n")
    logger.info(f"Wrote {out_dir/'comparison.md'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--logits", type=Path)
    ap.add_argument("--threshold-from", type=Path, help="val_predictions.csv of the same run/fold")
    ap.add_argument("--threshold", type=float, help="explicit threshold (skips --threshold-from)")
    ap.add_argument("--label", default="arm", help="server | mobile | any tag")
    ap.add_argument("--runtime", default=None, help="e.g. 'pytorch-eager' or 'executorch-1.4.0'")
    ap.add_argument("--device", default=None, help="e.g. 'cpu' or 'Pixel 6a (Tensor G1)'")
    ap.add_argument("--batch-size", type=int, default=1)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument(
        "--compare",
        nargs=2,
        metavar=("A_METRICS_JSON", "B_METRICS_JSON"),
        help="emit comparison.md from two metrics.json files instead of scoring",
    )
    args = ap.parse_args()

    if args.compare:
        write_comparison(Path(args.compare[0]), Path(args.compare[1]), args.out_dir)
        return

    for req in ("manifest", "logits"):
        if getattr(args, req) is None:
            ap.error(f"--{req} is required unless --compare is used")
    if args.threshold is None and args.threshold_from is None:
        ap.error("pass --threshold-from (preferred) or --threshold")

    manifest = pd.read_csv(args.manifest, dtype={"sample_id": str})
    logits = load_logits(args.logits)
    if len(logits) != len(manifest):
        logger.warning(
            f"logits has {len(logits)} rows, manifest has {len(manifest)} — the spec requires "
            "one row per manifest row, including failures."
        )

    thr = args.threshold if args.threshold is not None else frozen_threshold(args.threshold_from)
    results = score(manifest, logits, thr)

    import hashlib

    meta = {
        "label": args.label,
        "runtime": args.runtime or args.label,
        "device": args.device,
        "batch_size": args.batch_size,
        "threshold": float(thr),
        "threshold_source": str(args.threshold_from) if args.threshold_from else "explicit",
        "manifest": str(args.manifest),
        "manifest_sha": hashlib.sha256(args.manifest.read_bytes()).hexdigest()[:16],
        "logits": str(args.logits),
        "spec": "docs/MOBILE_EVAL_PIPELINE.md",
    }
    write_table(results, meta, args.out_dir, args.label)


if __name__ == "__main__":
    main()
