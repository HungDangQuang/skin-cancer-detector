# Bootstrap 95% confidence intervals — `.tmp/ci_ddi/ham10000/headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline` | 5 | 0.7708 [0.7578, 0.7831] | 0.3625 [0.3402, 0.3860] | 0.0825 [0.0768, 0.0884] | 0.3589 [0.3314, 0.3851] |
| `x_baseline__ddi` | 5 | 0.7738 [0.7613, 0.7857] | 0.3779 [0.3551, 0.4016] | 0.0815 [0.0762, 0.0870] | 0.3759 [0.3494, 0.4020] |
| `x_kd` | 5 | 0.7855 [0.7726, 0.7972] | 0.3967 [0.3737, 0.4208] | 0.0869 [0.0813, 0.0927] | 0.3966 [0.3702, 0.4217] |
| `x_kd__ddi` | 5 | 0.8267 [0.8153, 0.8375] | 0.4829 [0.4556, 0.5100] | 0.1002 [0.0949, 0.1057] | 0.5004 [0.4720, 0.5254] |
| `x_teacher` | 5 | 0.8078 [0.7960, 0.8196] | 0.4547 [0.4286, 0.4812] | 0.0893 [0.0837, 0.0949] | 0.4826 [0.4540, 0.5092] |
| `x_teacher__ddi` | 5 | 0.8328 [0.8219, 0.8433] | 0.4938 [0.4676, 0.5219] | 0.0999 [0.0942, 0.1057] | 0.5273 [0.5021, 0.5549] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline__ddi` | `x_baseline` | +0.0030 [-0.0014, +0.0078] | +0.0154 [+0.0064, +0.0244] * | -0.0010 [-0.0035, +0.0017] | +0.0169 [+0.0017, +0.0329] * |
| `x_kd__ddi` | `x_kd` | +0.0412 [+0.0367, +0.0459] * | +0.0863 [+0.0737, +0.0979] * | +0.0133 [+0.0107, +0.0162] * | +0.1038 [+0.0875, +0.1190] * |
| `x_teacher__ddi` | `x_teacher` | +0.0250 [+0.0203, +0.0295] * | +0.0391 [+0.0274, +0.0504] * | +0.0107 [+0.0079, +0.0134] * | +0.0447 [+0.0310, +0.0616] * |
