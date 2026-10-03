# Bootstrap 95% confidence intervals — `.tmp/ci_item3/fitzpatrick17k_headline`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `p0_ckpt_auprc` | 5 | 0.7077 [0.6941, 0.7220] | 0.7022 [0.6843, 0.7213] | 0.0538 [0.0499, 0.0580] | 0.3415 [0.3162, 0.3661] | 0.4946 [0.4699, 0.5178] |
| `p0_ckpt_pauc` | 5 | 0.6999 [0.6861, 0.7145] | 0.6951 [0.6767, 0.7148] | 0.0515 [0.0475, 0.0558] | 0.3265 [0.3009, 0.3513] | 0.4769 [0.4535, 0.5025] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `p0_ckpt_auprc` | `p0_ckpt_pauc` | +0.0078 [+0.0050, +0.0104] * | +0.0071 [+0.0034, +0.0111] * | +0.0023 [+0.0011, +0.0036] * | +0.0150 [+0.0051, +0.0238] * | +0.0178 [+0.0081, +0.0249] * |
