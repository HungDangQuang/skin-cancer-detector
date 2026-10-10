# Bootstrap 95% confidence intervals — `.tmp/ci_cand2/P2/ham10000_headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_baseline` | 5 | 0.7390 [0.7260, 0.7515] | 0.3365 [0.3145, 0.3586] | 0.0702 [0.0652, 0.0756] | 0.3211 [0.2972, 0.3452] | 0.5196 [0.4953, 0.5434] |
| `x_student` | 5 | 0.8159 [0.8030, 0.8283] | 0.4661 [0.4379, 0.4952] | 0.0939 [0.0876, 0.1004] | 0.4885 [0.4555, 0.5204] | 0.6758 [0.6480, 0.7007] |
| `x_teacher` | 5 | 0.8328 [0.8219, 0.8433] | 0.4938 [0.4676, 0.5219] | 0.0999 [0.0942, 0.1057] | 0.5273 [0.5021, 0.5549] | 0.7167 [0.6930, 0.7391] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `x_baseline` | +0.0769 [+0.0675, +0.0855] * | +0.1296 [+0.1112, +0.1468] * | +0.0237 [+0.0190, +0.0281] * | +0.1673 [+0.1410, +0.1912] * | +0.1562 [+0.1334, +0.1766] * |
| `x_student` | `x_teacher` | -0.0170 [-0.0251, -0.0094] * | -0.0277 [-0.0434, -0.0109] * | -0.0061 [-0.0109, -0.0016] * | -0.0388 [-0.0641, -0.0178] * | -0.0409 [-0.0607, -0.0227] * |
