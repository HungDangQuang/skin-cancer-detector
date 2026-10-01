# Bootstrap 95% confidence intervals — `.tmp/ci_gates/ham10000_headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | 5 | 0.8416 [0.8306, 0.8518] | 0.4997 [0.4728, 0.5267] | 0.1073 [0.1020, 0.1126] | 0.5321 [0.5035, 0.5604] | 0.7259 [0.7018, 0.7508] |
| `x_teacher` | 5 | 0.8328 [0.8219, 0.8433] | 0.4938 [0.4676, 0.5219] | 0.0999 [0.0942, 0.1057] | 0.5273 [0.5021, 0.5549] | 0.7167 [0.6930, 0.7391] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `x_teacher` | +0.0087 [+0.0027, +0.0147] * | +0.0059 [-0.0068, +0.0189] | +0.0073 [+0.0037, +0.0107] * | +0.0048 [-0.0148, +0.0210] | +0.0092 [-0.0055, +0.0251] |
