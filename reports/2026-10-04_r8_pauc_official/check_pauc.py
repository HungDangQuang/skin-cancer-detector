"""R8 (docs/PROGRESS.md): project pauc_at_tpr vs the official ISIC 2024 scoring function, on the same arrays.

Official function: ISIC-Research/Challenge-2024-Metrics, PrimaryMetric-pAUC.py (Nicholas R Kurtansky, MSKCC),
copied below verbatim except the module alias. Run on the server from the repo root:
    PYTHONPATH=$(pwd) .venv-linux/bin/python reports/2026-10-04_r8_pauc_official/check_pauc.py <predictions.csv> ...
Each CSV needs y_true,y_prob (and optionally source); scored on all rows and per source.
"""
import sys

import numpy as np
import pandas as pd
import sklearn.metrics as sklean

from src.evaluation.metrics import pauc_at_tpr


def p_auc_tpr(v_gt, v_pred, min_tpr=None, sample_weight=None):  # official, verbatim
    if len(np.unique(v_gt)) != 2:
        raise ValueError(
            "Only one class present in y_true. ROC AUC score "
            "is not defined in that case."
        )
    v_gt = abs(np.asarray(v_gt)-1)
    v_pred = abs(np.asarray(v_pred)-1)
    max_fpr = abs(1-min_tpr)
    fpr, tpr, _ = sklean.roc_curve(v_gt, v_pred, sample_weight=sample_weight)
    if max_fpr is None or max_fpr == 1:
        return sklean.auc(fpr, tpr)
    if max_fpr <= 0 or max_fpr > 1:
        raise ValueError("Expected min_tpr in range [0, 1), got: %r" % min_tpr)
    stop = np.searchsorted(fpr, max_fpr, "right")
    x_interp = [fpr[stop - 1], fpr[stop]]
    y_interp = [tpr[stop - 1], tpr[stop]]
    tpr = np.append(tpr[:stop], np.interp(max_fpr, x_interp, y_interp))
    fpr = np.append(fpr[:stop], max_fpr)
    partial_auc = sklean.auc(fpr, tpr)
    return(partial_auc)


worst = 0.0
print("file,subset,n,n_pos,ours,official,abs_diff")
for path in sys.argv[1:]:
    df = pd.read_csv(path)
    subsets = [("all", df)]
    if "source" in df.columns:
        subsets += [(s, g) for s, g in df.groupby("source")]
    for name, g in subsets:
        y, p = g["y_true"].to_numpy().astype(int), g["y_prob"].to_numpy()
        ours, off = pauc_at_tpr(y, p, 0.80), p_auc_tpr(y, p, 0.80)
        d = abs(ours - off)
        worst = max(worst, d)
        print(f"{path},{name},{len(g)},{int(y.sum())},{ours:.10f},{off:.10f},{d:.3e}")
print(f"MAX_ABS_DIFF {worst:.3e}")
