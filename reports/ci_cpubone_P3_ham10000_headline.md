# Bootstrap 95% confidence intervals — `.tmp/ci_cpubone/P3/ham10000_headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_baseline` | 5 | 0.7672 [0.7526, 0.7812] | 0.4424 [0.4153, 0.4697] | 0.0576 [0.0515, 0.0642] | 0.4816 [0.4528, 0.5111] | 0.6407 [0.6164, 0.6647] |
| `x_student` | 5 | 0.8436 [0.8334, 0.8536] | 0.5317 [0.5032, 0.5594] | 0.1045 [0.0994, 0.1098] | 0.5581 [0.5277, 0.5830] | 0.7388 [0.7163, 0.7605] |
| `x_teacher` | 5 | 0.8328 [0.8219, 0.8433] | 0.4938 [0.4676, 0.5219] | 0.0999 [0.0942, 0.1057] | 0.5273 [0.5021, 0.5549] | 0.7167 [0.6930, 0.7391] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `x_baseline` | +0.0764 [+0.0688, +0.0843] * | +0.0892 [+0.0778, +0.1013] * | +0.0469 [+0.0424, +0.0514] * | +0.0765 [+0.0591, +0.0899] * | +0.0980 [+0.0839, +0.1121] * |
| `x_student` | `x_teacher` | +0.0108 [+0.0052, +0.0165] * | +0.0379 [+0.0246, +0.0517] * | +0.0046 [+0.0013, +0.0079] * | +0.0308 [+0.0110, +0.0468] * | +0.0221 [+0.0076, +0.0382] * |
