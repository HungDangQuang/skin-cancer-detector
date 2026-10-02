"""
Emit the Android app's per-model ``config.json`` (docs/ANDROID_APP_SPEC.md §3.2) from a
trained run — thresholds chosen on VALIDATION only, performance reported on TEST.

Operating points (docs/ANDROID_APP_SPEC.md §3.5, §3.5a):
  phone_sens<NN>  threshold = the val PAD-UFES-20 (phone photo) rows' malignant score
                  that keeps sensitivity >= --phone-sens-target; reported on test PAD rows.
  global_youden   threshold = Youden J on all val rows; reported on all test rows.
val_predictions*.csv has no source column; its rows follow
<splits_dir>/fold_N/val_split.csv one for one (row count and labels are checked).

Two modes (docs/ANDROID_APP_SPEC.md §3.4a):
  binary      no --phone-prevalence / --global-prevalence / --pi-target. The app shows the
              decision only: no calibration block, no risk bands, no PPV/NPV. Sensitivity,
              specificity and falseAlarmsPer1000 (prevalence-free) are still written.
  calibrated  all three given. Prevalences and the calibration target are DECISIONS, not
              constants, so they have no default. Giving only some of them is an error.
See docs/APP_CONFIG_GUIDE.md.

Usage (on the server, in .venv-linux — importing src.evaluation pulls in torch; CPU only):
    python scripts/make_app_config.py \
        --run-dir experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp \
        --fold 4 --ckpt-tag _auprc --pte exports/executorch_srcsamp/<model>.pte \
        --executorch-version 1.5.1 --model-id <id> --model-version v1.0.0 \
        --display-name "..." --phone-prevalence <p> --global-prevalence <p> --pi-target <p> \
        --benchmark-json reports/benchmark/mobilenetv4_conv_medium.json --out <dir>/config.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from omegaconf import OmegaConf

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.evaluation.metrics import youden_threshold  # noqa: E402

PHONE_SOURCE = "pad_ufes_20"


def _logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        sys.exit(f"ERROR: missing {path}")
    return pd.read_csv(path)


def val_with_source(fold_dir: Path, splits_dir: Path, fold: int, tag: str) -> pd.DataFrame:
    """val_predictions<tag>.csv joined row-by-row with val_split.csv (label + source)."""
    vp = _read_csv(fold_dir / f"val_predictions{tag}.csv")
    vs = _read_csv(splits_dir / f"fold_{fold}" / "val_split.csv")
    if len(vp) != len(vs):
        sys.exit(f"ERROR: val_predictions{tag}.csv has {len(vp)} rows, val_split.csv {len(vs)} — "
                 "they must be the same split in the same order")
    if not np.array_equal(vp["y_true"].to_numpy(), vs["label"].to_numpy()):
        sys.exit("ERROR: val_predictions labels do not match val_split.csv row for row")
    out = vp[["y_true", "y_prob"]].copy()
    out["source"] = vs["source"].astype(str).to_numpy()
    return out


def threshold_for_sensitivity(y_true: np.ndarray, y_prob: np.ndarray, target: float) -> float:
    """Largest threshold t with mean(prob[malignant] >= t) >= target (flag rule: prob >= t)."""
    pos = np.sort(y_prob[y_true == 1])
    if pos.size == 0:
        sys.exit("ERROR: no malignant rows to set a sensitivity threshold on")
    # round() first: pos.size * (1 - 0.90) is 0.0999.. * n in floating point, which would floor one
    # step low whenever n * 0.1 is an integer.
    k = int(math.floor(round(pos.size * (1.0 - target), 9)))  # positives allowed below t
    return float(pos[min(k, pos.size - 1)])


def threshold_for_specificity(y_true: np.ndarray, y_prob: np.ndarray, target: float) -> float:
    """Smallest threshold t with mean(prob[benign] < t) >= target."""
    neg = np.sort(y_prob[y_true == 0])
    if neg.size == 0:
        sys.exit("ERROR: no benign rows to set a specificity threshold on")
    k = int(math.ceil(round(neg.size * target, 9)))  # benign rows that must fall below t
    if k <= 0:
        return float(neg[0])
    # Just above the k-th smallest benign score, so ties at that score stay below t.
    return float(np.nextafter(neg[k - 1], np.inf))


def rates(y_true: np.ndarray, y_prob: np.ndarray, thr: float) -> tuple[float, float, int, int]:
    flag = y_prob >= thr
    pos, neg = y_true == 1, y_true == 0
    sens = float(flag[pos].mean()) if pos.any() else float("nan")
    spec = float((~flag[neg]).mean()) if neg.any() else float("nan")
    return sens, spec, int(pos.sum()), int(neg.sum())


def ppv_npv(sens: float, spec: float, prev: float) -> tuple[float, float]:
    tp, fp = sens * prev, (1 - spec) * (1 - prev)
    tn, fn = spec * (1 - prev), (1 - sens) * prev
    ppv = tp / (tp + fp) if tp + fp > 0 else float("nan")
    npv = tn / (tn + fn) if tn + fn > 0 else float("nan")
    return ppv, npv


def operating_point(op_id, label, thr, test, prevalence, shift, source_desc, eval_desc):
    """prevalence/shift None = binary mode: only the prevalence-free fields are written."""
    sens, spec, n_pos, n_neg = rates(test["y_true"].to_numpy(), test["y_prob"].to_numpy(), thr)
    thr_w = round(thr, 6)  # the value written to the file; I3 is defined on what the app reads
    op = {"id": op_id, "label": label, "threshold": thr_w}
    if shift is not None:
        op["calibratedThreshold"] = round(_sigmoid(_logit(thr_w) + shift), 8)
    op["sensitivity"] = round(sens, 4)
    op["specificity"] = round(spec, 4)
    if prevalence is not None:
        ppv, npv = ppv_npv(sens, spec, prevalence)
        op["prevalenceForPpv"] = prevalence
        op["ppvAtPrevalence"] = round(ppv, 4)
        op["npvAtPrevalence"] = round(npv, 5)
    op["falseAlarmsPer1000"] = int(round((1 - spec) * 1000))  # per 1000 benign: prevalence-free
    op["thresholdSource"] = source_desc
    op["evaluatedOn"] = f"{eval_desc} (n_malignant={n_pos}, n_benign={n_neg})"
    return op


def agg_metric(agg: dict, key: str) -> dict | None:
    m = agg.get("metrics", {}).get(key)
    return {"mean": round(m["mean"], 4), "std": round(m["std"], 4)} if m else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--fold", type=int, required=True)
    ap.add_argument("--ckpt-tag", default="", help='"" = best_model.pth files, "_auprc" = the AUPRC twin')
    ap.add_argument("--pte", type=Path, required=True, help="the exported .pte this config describes")
    ap.add_argument("--executorch-version", required=True, help="version of the export venv that wrote the .pte")
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--model-version", required=True)
    ap.add_argument("--display-name", required=True)
    ap.add_argument("--phone-sens-target", type=float, default=0.90)
    ap.add_argument("--phone-prevalence", type=float, default=None,
                    help="malignant prevalence assumed for camera photos in deployment (PPV/NPV of the phone point)")
    ap.add_argument("--global-prevalence", type=float, default=None,
                    help="prevalence for PPV/NPV of the global point and for metrics.prevalence")
    ap.add_argument("--pi-target", type=float, default=None,
                    help="calibration target prior for the displayed risk (prior shift)")
    ap.add_argument("--default-op", default=None, help="default operating point id (default: the phone point)")
    ap.add_argument("--skip-global-op", action="store_true",
                    help="leave out global_youden: on camera photos it flags almost every benign image "
                         "(reports/2026-10-02_threshold_options/), so it should not be user-selectable")
    ap.add_argument("--benchmark-json", type=Path, default=None)
    ap.add_argument("--pi-train", type=float, default=None,
                    help="training prior for the prior shift (default 1/(1+data.undersample_ratio)); see the guide for phone photos")
    ap.add_argument("--backend", default="xnnpack", help="backend the .pte was lowered to (xnnpack | portable)")
    ap.add_argument("--threshold-note", default="",
                    help="extra provenance appended to the phone point's thresholdSource (e.g. a report path)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--force", action="store_true", help="overwrite an existing --out")
    args = ap.parse_args()

    prev_args = ("phone_prevalence", "global_prevalence", "pi_target")
    given = [n for n in prev_args if getattr(args, n) is not None]
    if given and len(given) != len(prev_args):
        sys.exit("ERROR: give all of --phone-prevalence, --global-prevalence, --pi-target "
                 "(calibrated mode) or none of them (binary mode); got only "
                 + ", ".join("--" + n.replace("_", "-") for n in given))
    binary = not given
    for name in given:
        v = getattr(args, name)
        if not 0.0 < v < 1.0:
            sys.exit(f"ERROR: --{name.replace('_', '-')} must be in (0, 1), got {v}")
    if binary and args.pi_train is not None:
        sys.exit("ERROR: --pi-train only applies in calibrated mode")
    if args.out.exists() and not args.force:
        sys.exit(f"ERROR: {args.out} exists — pass --force to overwrite")
    if not args.pte.is_file():
        sys.exit(f"ERROR: missing {args.pte}")

    fold_dir = args.run_dir / f"fold_{args.fold}"
    cfg = OmegaConf.load(fold_dir / "config.yaml")
    tag = args.ckpt_tag
    splits_dir = Path(cfg.data.splits_dir)

    val = val_with_source(fold_dir, splits_dir, args.fold, tag)
    test = _read_csv(fold_dir / f"predictions{tag}.csv")
    if "source" not in test.columns:
        sys.exit(f"ERROR: predictions{tag}.csv has no source column")
    agg_path = args.run_dir / f"aggregated{tag}.json"
    if not agg_path.is_file():
        sys.exit(f"ERROR: missing {agg_path} — run run/aggregate.sh (METRICS_NAME=test_metrics{tag}.json) first")
    agg = json.loads(agg_path.read_text())

    pi_train, shift = None, None  # binary mode: no prior shift, nothing calibrated is displayed
    if not binary:
        ratio = float(cfg.data.get("undersample_ratio", 5))
        pi_train = args.pi_train if args.pi_train is not None else 1.0 / (1.0 + ratio)
        if not 0.0 < pi_train < 1.0:
            sys.exit(f"ERROR: piTrain must be in (0, 1), got {pi_train}")
        shift = _logit(args.pi_target) - _logit(pi_train)

    vp = val[val["source"] == PHONE_SOURCE]
    tp = test[test["source"] == PHONE_SOURCE]
    if vp.empty or tp.empty:
        sys.exit(f"ERROR: no {PHONE_SOURCE} rows in val ({len(vp)}) or test ({len(tp)})")
    t_phone = threshold_for_sensitivity(vp["y_true"].to_numpy(), vp["y_prob"].to_numpy(), args.phone_sens_target)
    t_global = float(youden_threshold(val["y_true"].to_numpy(), val["y_prob"].to_numpy()))

    pct = int(round(args.phone_sens_target * 100))
    phone_id = f"phone_sens{pct}"
    ops = [
        operating_point(
            phone_id, "Camera photos", t_phone, tp, args.phone_prevalence, shift,
            f"sensitivity {pct}% on the {PHONE_SOURCE} rows of fold_{args.fold} val_predictions{tag}.csv "
            f"(n={len(vp)})" + (f"; {args.threshold_note}" if args.threshold_note else ""),
            f"test {PHONE_SOURCE} rows of fold_{args.fold} predictions{tag}.csv"),
    ]
    if not args.skip_global_op:
        ops.append(operating_point(
            "global_youden", "Reference (all images)", t_global, test, args.global_prevalence, shift,
            f"Youden J on all rows of fold_{args.fold} val_predictions{tag}.csv (n={len(val)})",
            f"all test rows of fold_{args.fold} predictions{tag}.csv"))
    default_op = args.default_op or phone_id
    if default_op not in {o["id"] for o in ops}:
        sys.exit(f"ERROR: --default-op {default_op} is not one of {[o['id'] for o in ops]}")

    # Risk bands on the CALIBRATED scale (calibrated mode only), cut at points chosen on the
    # default point's val rows:
    # low < sens-99% point <= moderate < default threshold <= elevated < spec-95% point <= high.
    risk_bands = None
    if not binary:
        dom = vp if default_op == phone_id else val
        y, p = dom["y_true"].to_numpy(), dom["y_prob"].to_numpy()
        cuts_raw = [threshold_for_sensitivity(y, p, 0.99),
                    t_phone if default_op == phone_id else t_global,
                    threshold_for_specificity(y, p, 0.95)]
        cuts = [round(_sigmoid(_logit(c) + shift), 8) for c in cuts_raw]
        # Spec §3.2: "moderate" ends exactly at the default point's calibratedThreshold.
        cuts[1] = next(o["calibratedThreshold"] for o in ops if o["id"] == default_op)
        if not (cuts[0] < cuts[1] < cuts[2] < 1.0):
            sys.exit(f"ERROR: risk-band cut points are not increasing ({cuts}); set them by hand")
        risk_bands = [
            {"id": "low", "maxCalibratedProb": cuts[0], "label": "Low"},
            {"id": "moderate", "maxCalibratedProb": cuts[1], "label": "Moderate"},
            {"id": "elevated", "maxCalibratedProb": cuts[2], "label": "Elevated"},
            {"id": "high", "maxCalibratedProb": 1.0, "label": "High"},
        ]

        # Invariant I3 (spec §3.4): calibratedThreshold == sigmoid(logit(threshold) + logitShift).
        for o in ops:
            if abs(o["calibratedThreshold"] - _sigmoid(_logit(o["threshold"]) + shift)) > 1e-6:
                sys.exit(f"ERROR: invariant I3 broken for {o['id']}")

    val_norm = next((t for t in cfg.augmentation.val if t.name == "Normalize"), None)
    if val_norm is None:
        sys.exit("ERROR: no Normalize step in augmentation.val of the run config")
    bench_path = args.benchmark_json
    if bench_path is None and "student" in cfg:
        guess = Path("reports/benchmark") / f"{cfg.student.name}.json"  # same architecture as the run
        bench_path = guess if guess.is_file() else None
    if bench_path is None:
        print("WARN: no benchmark JSON for this architecture — params/GFLOPs/size left out")
    bench = json.loads(bench_path.read_text()) if bench_path else {}
    metrics = {"nFolds": agg.get("n_folds")}
    if not binary:
        metrics = {"prevalence": args.global_prevalence, **metrics}
    for out_key, key in [("paucAtTpr80", "pauc_at_tpr80"), ("aucRoc", "auc_roc"), ("auprc", "auprc"),
                         ("sensAt80Spec", "sens_at_80spec"), ("sensitivity", "sensitivity"),
                         ("specificity", "specificity"), ("precision", "precision"),
                         ("brier", "brier"), ("ece", "ece")]:
        v = agg_metric(agg, key)
        if v:
            metrics[out_key] = v
    metrics["note"] = ("5-fold test means of the threshold-free metrics, whole in-domain test set "
                       "(ISIC + PAD pooled). sensitivity/specificity/precision are at the TEST-set Youden threshold "
                       "(optimistic); the operating points above are the deployment numbers.")
    for out_key, key in [("paramsMillions", "params_millions"), ("gflops", "gflops"),
                         ("fp32SizeMb", "fp32_size_mb")]:
        if key in bench:
            metrics[out_key] = bench[key]

    config = {
        "schemaVersion": 1,
        "modelId": args.model_id,
        "modelVersion": args.model_version,
        "displayName": args.display_name,
        "sourceRun": str(args.run_dir),
        "fold": args.fold,
        "checkpoint": f"best_model{tag}.pth",
        "exportedAt": datetime.fromtimestamp(args.pte.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "executorchVersion": args.executorch_version,
        "pteSha256": hashlib.sha256(args.pte.read_bytes()).hexdigest(),
        "backend": args.backend,
        "asset": "model.pte",
        "input": {
            "size": int(cfg.data.image_size), "channels": 3, "channelOrder": "RGB", "layout": "CHW",
            "batch": 1, "dtype": "float32", "scale": 1.0 / 255.0,
            "mean": [float(x) for x in val_norm.mean], "std": [float(x) for x in val_norm.std],
            "resize": "squash",
            "note": "x/255 then (x-mean)/std, per channel; no aspect-ratio preservation",
        },
        "output": {"count": 1, "names": ["logit"], "activation": "sigmoid", "positiveClass": "malignant"},
        "displayMode": "binary" if binary else "calibrated",
        "defaultOperatingPoint": default_op,
        "thresholdSource": "; ".join(f"{o['id']}: {o['thresholdSource']}" for o in ops),
        "operatingPoints": ops,
        "metrics": metrics,
        "ood": {"enabled": False, "outputIndex": 1, "threshold": None, "idKeep": 0.95,
                "note": "Requires a 2-output GatedModel .pte — see docs/ood_gate_plan.md §5."},
    }
    if not binary:  # calibrated mode only (spec §3.4a): the displayed-risk machinery
        config["calibration"] = {
            "method": "prior_shift", "piTrain": round(pi_train, 8), "piTarget": args.pi_target,
            "logitShift": shift,  # full precision: the app checks I3 against this value
            "note": "logit_cal = logit + logit(piTarget) - logit(piTrain); monotone, does not change decisions",
        }
        config["riskBands"] = risk_bands
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(config, indent=2, allow_nan=False) + "\n")
    print(f"Wrote {args.out} (displayMode={config['displayMode']})")
    for o in ops:
        ppv = (f" PPV@{o['prevalenceForPpv']}={o['ppvAtPrevalence']:.3f}" if "ppvAtPrevalence" in o else "")
        print(f"  {o['id']:<14} thr={o['threshold']:.4f} sens={o['sensitivity']:.3f} "
              f"spec={o['specificity']:.3f}{ppv}  [{o['evaluatedOn']}]")


if __name__ == "__main__":
    main()
