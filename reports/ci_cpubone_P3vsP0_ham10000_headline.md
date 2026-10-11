# Bootstrap 95% confidence intervals — `.tmp/ci_p3p0/ham10000_headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_p0` | 5 | 0.8416 [0.8306, 0.8518] | 0.4997 [0.4728, 0.5267] | 0.1073 [0.1020, 0.1126] | 0.5321 [0.5035, 0.5604] | 0.7259 [0.7018, 0.7508] |
| `x_p3` | 5 | 0.8436 [0.8334, 0.8536] | 0.5317 [0.5032, 0.5594] | 0.1045 [0.0994, 0.1098] | 0.5581 [0.5277, 0.5830] | 0.7388 [0.7163, 0.7605] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_p3` | `x_p0` | +0.0021 [-0.0021, +0.0063] | +0.0320 [+0.0214, +0.0422] * | -0.0027 [-0.0052, -0.0000] * | +0.0260 [+0.0108, +0.0400] * | +0.0128 [-0.0005, +0.0264] |
