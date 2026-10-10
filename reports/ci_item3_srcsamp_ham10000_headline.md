# Bootstrap 95% confidence intervals — `.tmp/ci_item3/ham10000_headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `p0_ckpt_auprc` | 5 | 0.8416 [0.8306, 0.8518] | 0.4997 [0.4728, 0.5267] | 0.1073 [0.1020, 0.1126] | 0.5321 [0.5035, 0.5604] | 0.7259 [0.7018, 0.7508] |
| `p0_ckpt_pauc` | 5 | 0.8337 [0.8223, 0.8446] | 0.4969 [0.4687, 0.5255] | 0.1022 [0.0965, 0.1078] | 0.5334 [0.5050, 0.5618] | 0.7199 [0.6979, 0.7438] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `p0_ckpt_auprc` | `p0_ckpt_pauc` | +0.0079 [+0.0055, +0.0104] * | +0.0028 [-0.0032, +0.0091] | +0.0051 [+0.0035, +0.0067] * | -0.0014 [-0.0121, +0.0087] | +0.0060 [-0.0036, +0.0133] |
