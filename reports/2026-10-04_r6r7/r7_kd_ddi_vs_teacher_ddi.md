# Bootstrap 95% confidence intervals — `.tmp/ci_r7`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_80spec |
|---|---|---|---|---|---|
| `x_kd__ddi` | 5 | 0.9816 [0.9746, 0.9879] | 0.6246 [0.5646, 0.6825] | 0.1826 [0.1760, 0.1886] | 0.9781 [0.9646, 0.9897] |
| `x_teacher__ddi` | 5 | 0.9793 [0.9713, 0.9863] | 0.6161 [0.5582, 0.6731] | 0.1804 [0.1726, 0.1872] | 0.9758 [0.9600, 0.9893] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_80spec |
|---|---|---|---|---|---|
| `x_kd__ddi` | `x_teacher__ddi` | +0.0023 [-0.0006, +0.0053] | +0.0085 [-0.0085, +0.0252] | +0.0022 [-0.0007, +0.0052] | +0.0023 [-0.0051, +0.0106] |

## 4. Fairness gaps — paired bootstrap over `source`

### `x_kd__ddi`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_80spec |
|---|---|---|---|---|
| isic2024 | 0.9418 [0.9200, 0.9593] | 0.0716 [0.0375, 0.1264] | 0.1570 [0.1405, 0.1713] | 0.9289 [0.8811, 0.9672] |
| pad_ufes_20 | 0.8245 [0.7875, 0.8596] | 0.7997 [0.7458, 0.8499] | 0.0993 [0.0816, 0.1166] | 0.6878 [0.6022, 0.7850] |
| **isic2024_minus_pad_ufes_20** | +0.1173 [+0.0751, +0.1577] * | -0.7281 [-0.7906, -0.6529] * | +0.0577 [+0.0332, +0.0805] * | +0.2411 [+0.1321, +0.3341] * |

### `x_teacher__ddi`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_80spec |
|---|---|---|---|---|
| isic2024 | 0.9330 [0.9073, 0.9528] | 0.0533 [0.0310, 0.0954] | 0.1506 [0.1314, 0.1668] | 0.9158 [0.8635, 0.9595] |
| pad_ufes_20 | 0.8189 [0.7832, 0.8543] | 0.7966 [0.7453, 0.8444] | 0.0988 [0.0831, 0.1152] | 0.6751 [0.5822, 0.7542] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0708, +0.1542] * | -0.7433 [-0.7953, -0.6745] * | +0.0518 [+0.0254, +0.0744] * | +0.2407 [+0.1446, +0.3462] * |


## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_kd__ddi` | `x_teacher__ddi` | isic2024 | +0.0087 [-0.0011, +0.0183] | +0.0184 [-0.0027, +0.0432] | +0.0064 [-0.0018, +0.0149] | +0.0132 [-0.0136, +0.0353] |
| `x_kd__ddi` | `x_teacher__ddi` | pad_ufes_20 | +0.0056 [-0.0110, +0.0222] | +0.0032 [-0.0169, +0.0251] | +0.0005 [-0.0103, +0.0105] | +0.0127 [-0.0345, +0.0774] |
