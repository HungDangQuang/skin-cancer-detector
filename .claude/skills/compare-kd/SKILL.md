---
name: compare-kd
description: Compare ALL teacher/student training results across experiments/runs/ to judge whether Knowledge Distillation helps and find the best teacher-student pair. Runs scripts/compare_kd_results.py (pairs each KD student against its baseline, aggregates folds, ranks by performance AND by KD delta) and renders a verdict. Use when the user says "compare all results", "which teacher-student pair is best", "did KD help across the board", "rank my students", or after training the full KD + baseline matrix. NOT for a single checkpoint (use analyze-evaluation) and NOT for one student's controlled KD-vs-baseline setup (use kd-experiment).
---

# compare-kd

Answers two questions in one sweep: **"does KD help?"** and **"which teacher → student pair is best?"** — across every run under `experiments/runs/`, with all metrics shown but the important ones first.

This is the cross-run roll-up. It complements, not replaces:
- `analyze-evaluation` — verdict on one or a few `reports/results/*.json` eval files.
- `kd-experiment` — *sets up / runs* one student's KD-vs-baseline pair.
- `assess-training` / `diagnose-training` — judge a single run's log.

## Inputs it reads

The fold-scoped `test_metrics.json` the trainers auto-write (unbiased, held-out test set — **not** `val_metrics.json`):

```
experiments/runs/
  teacher/<name>/fold_{0..4}/test_metrics.json          (teacher reference)
  baseline_<student>/fold_{0..4}/test_metrics.json       (student, NO KD)
  kd_<teacher>_to_<student>/fold_{0..4}/test_metrics.json (student, WITH KD)
```

These live on the cluster. If they're not on the laptop, the user must rsync first
(`rsync -avz slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/experiments/runs/ ./experiments/runs/`).
If `experiments/runs/` is empty/missing, say so and stop — don't invent numbers.

## How to run

1. Run the engine (pure stdlib — works on the laptop or the cluster):

   ```bash
   python scripts/compare_kd_results.py
   # writes reports/comparison/kd_comparison.{md,json} and prints the md
   # --include-ablations to also include __suffix ablation runs (default: main runs only)
   # --students fastvit_sa12,mobilenetv4_conv_medium  to restrict
   ```

2. Read `reports/comparison/kd_comparison.json` for exact numbers (don't eyeball the
   wide markdown table — quote the JSON). Each pair has `kd`, `baseline`, and `deltas`.

3. Render the verdict (below). **Never assert a number you didn't read from the JSON.**

## Reading the result — priorities

Quote metrics in this order (the script already orders them this way):

1. **AUPRC** — the headline at ~0.4% prevalence; AUC-ROC is optimistic here. Compare against `prevalence` (its random baseline).
2. **pAUC@TPR80** — the official ISIC 2024 metric, range ≈ [0.02, 0.20].
3. **AUC-ROC**, then **sensitivity** and the fixed-specificity operating points `sens_at_95spec` / `sens_at_90spec` (catching malignant matters most), then specificity / F1.

Always cite **mean ± std across folds**, never a single fold. A delta smaller than the
baseline's fold-to-fold std is within noise — say so rather than calling it a win.

## The verdict to produce

- **Does KD help?** Use the script's per-headline tally (how many students KD improved on AUPRC and on pAUC, with mean Δ). State HELPS / MIXED / DOES NOT HELP per metric, and call out any student where KD *hurt* AUPRC — that's the interesting case, don't bury it.
- **Best pair — performance:** highest AUPRC then pAUC (Ranking A).
- **Best pair — KD effect:** biggest ΔAUPRC then ΔpAUC vs the same student's baseline (Ranking B).
- If A and B disagree (a strong student that KD barely moved vs a weak student KD lifted a lot), present **both** and explain the trade-off — the user asked for both criteria.
- **Teacher vs student gap:** note where the distilled student approaches/exceeds its teacher (Section 4 reference) — a student beating its teacher is a headline result worth flagging.

## Caveats to always surface

- Pairing is by exact student name + `run_suffix`. A KD run with no matching `baseline_<student>` can't yield a delta — the script lists it under Ranking A but not B; mention if a baseline is missing so the user trains it.
- Ablation runs (`__samp_off`, `__ratio3`, `__train_isic_only`, …) are excluded by default; only include them when the question is specifically about that ablation.
- This judges the merged-dataset held-out test. Cross-domain (HAM10000) and fairness (Fitzpatrick17k) are separate, post-hoc evaluations — don't conflate.

## Don't

- Don't run training or eval here — this reads existing `test_metrics.json` only.
- Don't quote `val_metrics.json` for verdicts (it's early-stopping-biased); `val − test` is the overfitting gap, a different question.
- Don't call a sub-std delta a real KD effect.
