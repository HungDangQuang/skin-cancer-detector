# Data-Strategy Ablation Plan — 2026-06-21

Goal: turn the two data-strategy pillars from **assumptions** into **measured,
defensible results** for the thesis:

1. **PAD-UFES-20 mixing** improves performance (esp. on the smartphone/PAD domain).
2. **DynamicUndersampledSampler (1:5)** beats its alternatives (no resampling / other ratios).

Why this was needed: the 30-run experiment ablates only **KD vs baseline**. PAD
and the sampler were fixed in every run, so nothing currently attributes any of
the AUC 0.987 to them. See [docs/PREPROCESSING.md §7](../docs/PREPROCESSING.md).

---

## 1. What was built (foundation — no retraining needed to benefit)

- `compute_metrics` now emits **AUPRC** (+ `prevalence` baseline) and
  fixed-specificity operating points **`sens_at_90spec` / `sens_at_95spec`**.
- `Evaluator.save_predictions` writes **`predictions.csv`** (`y_true,y_prob,y_pred,source`)
  next to every `test_metrics.json` → PR-curve, AUPRC, per-domain (ISIC vs PAD),
  bootstrap CIs all recomputable offline.
- `aggregate_folds.py` lists the new metrics in the headline table.

## 2. Ablation A — Sampler  (`slurm/13_ablation_sampler.slurm`)

Best student (KD `efficientnet_b4 → mobilenetv3_large`); **teacher reused**;
seed/folds/hparams/loss fixed; vary ONLY the undersampler.

```bash
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=off    # natural ~1018:1
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=3      # 1:3
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=10     # 1:10
# SAMP=5 == the existing main run kd_…_to_mobilenetv3_large (reuse it)
bash slurm/submit.sh slurm/22_aggregate_folds.slurm RUN_DIR=experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large__samp_off
```

| Arm | pAUC | AUC-ROC | AUPRC | Sens | Spec | Sens@95spec | verdict |
|---|---|---|---|---|---|---|---|
| no sampler (off) | _tbd_ | | | | | | |
| 1:3 | _tbd_ | | | | | | |
| **1:5 (main)** | 0.1881 | 0.9873 | _re-eval_ | 0.9552 | 0.9364 | _tbd_ | reference |
| 1:10 | _tbd_ | | | | | | |

> Existing 1:5 AUPRC/operating-points are blank until the main run is re-evaluated
> with the new evaluator (cheap inference on the existing checkpoint).

## 3. Ablation B — PAD mixing  (`slurm/14_ablation_pad.slurm`)

**Baseline (no KD)** so the teacher can't leak PAD via soft labels. Train ISIC-only
vs ISIC+PAD; **identical combined held-out test**; `train_sources` filters
train+val only.

```bash
bash slurm/submit.sh slurm/14_ablation_pad.slurm ARM=isic_only
bash slurm/submit.sh slurm/14_ablation_pad.slurm ARM=isic_pad
bash slurm/submit.sh slurm/22_aggregate_folds.slurm RUN_DIR=experiments/runs/baseline_mobilenetv3_large__train_isic_only
```

Per-domain breakdown (the key table) — split `predictions.csv` by `source`:

| Train data | Test subset | AUPRC | Sens | Sens@95spec | verdict |
|---|---|---|---|---|---|
| ISIC-only | ISIC-source | _tbd_ | | | |
| ISIC-only | **PAD-source** | _tbd_ | | | ← does PAD help here? |
| ISIC+PAD | ISIC-source | _tbd_ | | | |
| ISIC+PAD | **PAD-source** | _tbd_ | | | |

## 4. Decision rules (reuse the KD verdict convention)

- Report 5-fold **mean ± std**; significance via pooled-std (n=5), as in
  [2026-06-09_student_arm_analysis.md §3](2026-06-09_student_arm_analysis.md).
- **Win iff ΔAUPRC > 0 AND ΔSens > 0** (domain priority: a missed malignant
  outweighs a false alarm). For PAD, the decisive cell is the **PAD-source test
  subset** — that's the smartphone-domain generalization claim.

## 5. Status

- [x] Foundation code (metrics + predictions) — merged, validated (static).
- [x] Ablation slurm scripts 13 + 14 — authored, reviewed, lint-clean.
- [ ] Re-eval main 1:5 run for AUPRC/operating-points.
- [ ] Submit sampler arms (off/3/10) on cluster.
- [ ] Submit PAD arms (isic_only/isic_pad) on cluster.
- [ ] Aggregate + fill tables above + write verdict.
