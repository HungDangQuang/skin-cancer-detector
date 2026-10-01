# Bootstrap 95% confidence intervals — `.tmp/pixel_cmp/ham10000_headline`

B = 2000 replicates, seed 42, 7470 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_mobilenetv4_ddi_fold0` | 1 ⚠ | 0.8049 [0.7913, 0.8181] | 0.4044 [0.3765, 0.4337] | 0.0956 [0.0887, 0.1025] | 0.4192 [0.3843, 0.4497] |
| `x_mobilenetv4_srcsamp_auprc_fold4` | 1 ⚠ | 0.8807 [0.8702, 0.8901] | 0.5793 [0.5482, 0.6090] | 0.1276 [0.1213, 0.1336] | 0.6133 [0.5778, 0.6457] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_mobilenetv4_srcsamp_auprc_fold4` | `x_mobilenetv4_ddi_fold0` | +0.0757 [+0.0643, +0.0871] * | +0.1749 [+0.1493, +0.2013] * | +0.0319 [+0.0240, +0.0398] * | +0.1942 [+0.1599, +0.2324] * |
