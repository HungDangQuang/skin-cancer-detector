# SOTA benchmarks — reference for judging our results

The `dev-cycle` Phase 4 compares our numbers against published SOTA **before** calling
the pipeline effective. This file is that reference. **Every number here must be cited**
(paper / leaderboard URL + the date you verified it). If a cell is unknown, leave it
`TBD — verify via WebSearch`; do NOT invent a value. Update a row when WebSearch finds a
better source, and stamp the `Verified` column.

## Metric context (facts — safe to rely on)

- **ISIC 2024 official metric = pAUC above 80% TPR**, normalized to **[0, 0.2]**
  (random ≈ 0.02, perfect = 0.20). Quote ours on the same scale.
- At this prevalence (~0.4% malignant) **AUPRC is the honest headline**, not AUC-ROC.
  Always compare AUPRC against its random baseline = prevalence.
- Cross-domain (HAM10000) and fairness-by-skin-tone (Fitzpatrick17k) are reported
  separately and are never used for training.

## A. ISIC 2024 challenge (primary external yardstick)

| Method / entry | Metric | Reported value | Source (URL) | Verified |
|---|---|---|---|---|
| ISIC 2024 top public-LB | pAUC@TPR80 ([0,0.2]) | TBD — verify via WebSearch | TBD | — |
| ISIC 2024 top private-LB | pAUC@TPR80 ([0,0.2]) | TBD — verify via WebSearch | TBD | — |
| Common Kaggle baseline (EfficientNet) | pAUC@TPR80 | TBD — verify via WebSearch | TBD | — |

## B. Knowledge-distillation / mobile skin-lesion papers

| Paper (year) | Dataset | Teacher → Student | Headline metric + value | Source (URL) | Verified |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD — verify via WebSearch | TBD | — |

## C. Cross-domain & fairness references

| Reference | Dataset | Metric | Value | Source | Verified |
|---|---|---|---|---|---|
| TBD (HAM10000 generalization) | HAM10000 | AUPRC / AUC | TBD | TBD | — |
| TBD (Fitzpatrick17k fairness) | Fitzpatrick17k | gap across tones | TBD | TBD | — |

## D. Our results (filled by dev-cycle Phase 4 — cite run dirs)

| Run | Metric | Our value (mean±std) | vs SOTA above | Run dir |
|---|---|---|---|---|
| teacher convnextv2_base | pAUC@TPR80 / AUPRC | TBD | TBD | experiments/runs/teacher/convnextv2_base |
| best KD student | pAUC@TPR80 / AUPRC | TBD | TBD | experiments/runs/kd_*/ |

> Verdict rule: state plainly where we beat / match / lag each reference, and name the
> limitation (single fold, missing cross-domain, stale-scale pre-2026-06-04 logs).
> "Effective" requires being in range of the cited SOTA on the official metric **and**
> AUPRC clearly above the prevalence baseline — not just a high AUC-ROC.
