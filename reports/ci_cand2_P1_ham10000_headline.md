# Bootstrap 95% confidence intervals — `.tmp/ci_cand2/P1/ham10000_headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_baseline` | 5 | 0.7442 [0.7303, 0.7569] | 0.3882 [0.3634, 0.4127] | 0.0630 [0.0581, 0.0681] | 0.3979 [0.3730, 0.4232] | 0.5675 [0.5428, 0.5904] |
| `x_student` | 5 | 0.7929 [0.7800, 0.8055] | 0.4441 [0.4172, 0.4716] | 0.0825 [0.0770, 0.0880] | 0.4614 [0.4310, 0.4892] | 0.6395 [0.6121, 0.6652] |
| `x_teacher` | 5 | 0.7803 [0.7670, 0.7935] | 0.4505 [0.4231, 0.4774] | 0.0712 [0.0658, 0.0771] | 0.4657 [0.4369, 0.4921] | 0.6433 [0.6165, 0.6677] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `x_baseline` | +0.0487 [+0.0422, +0.0554] * | +0.0559 [+0.0445, +0.0678] * | +0.0194 [+0.0157, +0.0230] * | +0.0635 [+0.0456, +0.0803] * | +0.0720 [+0.0557, +0.0867] * |
| `x_student` | `x_teacher` | +0.0126 [+0.0066, +0.0190] * | -0.0064 [-0.0161, +0.0044] | +0.0113 [+0.0080, +0.0147] * | -0.0043 [-0.0211, +0.0114] | -0.0038 [-0.0186, +0.0100] |
