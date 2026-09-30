# Bootstrap 95% confidence intervals — `.tmp/ci_newsplit/ham10000/headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4` | 5 | 0.7708 [0.7578, 0.7831] | 0.3625 [0.3402, 0.3860] | 0.0825 [0.0768, 0.0884] | 0.3589 [0.3314, 0.3851] |
| `x_baseline_mobilenetv4__domain` | 5 | 0.7334 [0.7187, 0.7472] | 0.3311 [0.3078, 0.3554] | 0.0642 [0.0584, 0.0698] | 0.3126 [0.2851, 0.3413] |
| `x_kd_mobilenetv4` | 5 | 0.7855 [0.7726, 0.7972] | 0.3967 [0.3737, 0.4208] | 0.0869 [0.0813, 0.0927] | 0.3966 [0.3702, 0.4217] |
| `x_kd_mobilenetv4__domain` | 5 | 0.7880 [0.7752, 0.7997] | 0.3772 [0.3547, 0.4009] | 0.0890 [0.0824, 0.0956] | 0.3673 [0.3402, 0.3960] |
| `x_teacher_efficientnetv2_m` | 5 | 0.8078 [0.7960, 0.8196] | 0.4547 [0.4286, 0.4812] | 0.0893 [0.0837, 0.0949] | 0.4826 [0.4540, 0.5092] |
| `x_teacher_efficientnetv2_m__domain` | 5 | 0.8168 [0.8046, 0.8278] | 0.4612 [0.4322, 0.4887] | 0.0970 [0.0916, 0.1022] | 0.4820 [0.4509, 0.5104] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline_mobilenetv4__domain` | `x_baseline_mobilenetv4` | -0.0374 [-0.0445, -0.0305] * | -0.0314 [-0.0416, -0.0211] * | -0.0184 [-0.0223, -0.0149] * | -0.0464 [-0.0634, -0.0278] * |
| `x_kd_mobilenetv4__domain` | `x_kd_mobilenetv4` | +0.0025 [-0.0052, +0.0097] | -0.0195 [-0.0307, -0.0092] * | +0.0021 [-0.0027, +0.0066] | -0.0293 [-0.0478, -0.0094] * |
| `x_teacher_efficientnetv2_m__domain` | `x_teacher_efficientnetv2_m` | +0.0089 [+0.0020, +0.0158] * | +0.0065 [-0.0062, +0.0189] | +0.0077 [+0.0033, +0.0121] * | -0.0007 [-0.0206, +0.0185] |
