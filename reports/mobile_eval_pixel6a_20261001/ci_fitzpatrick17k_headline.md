# Bootstrap 95% confidence intervals — `.tmp/pixel_cmp/fitzpatrick17k_headline`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_mobilenetv4_ddi_fold0` | 1 ⚠ | 0.6176 [0.6015, 0.6342] | 0.5963 [0.5753, 0.6204] | 0.0407 [0.0366, 0.0448] | 0.1778 [0.1564, 0.1982] |
| `x_mobilenetv4_srcsamp_auprc_fold4` | 1 ⚠ | 0.7315 [0.7174, 0.7465] | 0.7246 [0.7043, 0.7453] | 0.0617 [0.0571, 0.0669] | 0.3634 [0.3287, 0.4018] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_mobilenetv4_srcsamp_auprc_fold4` | `x_mobilenetv4_ddi_fold0` | +0.1138 [+0.1014, +0.1262] * | +0.1284 [+0.1123, +0.1436] * | +0.0210 [+0.0165, +0.0257] * | +0.1856 [+0.1537, +0.2222] * |
