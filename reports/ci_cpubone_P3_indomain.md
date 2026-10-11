# Bootstrap 95% confidence intervals — `.tmp/ci_cpubone/P3/indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9713, 0.9863] | 0.6161 [0.5582, 0.6731] | 0.1804 [0.1726, 0.1872] | 0.9517 [0.9304, 0.9711] | 0.9758 [0.9600, 0.9893] |
| `x_baseline` | 5 | 0.9734 [0.9648, 0.9813] | 0.5547 [0.4983, 0.6071] | 0.1758 [0.1678, 0.1832] | 0.9321 [0.9072, 0.9557] | 0.9660 [0.9474, 0.9813] |
| `x_student` | 5 | 0.9838 [0.9773, 0.9897] | 0.6581 [0.6029, 0.7145] | 0.1847 [0.1783, 0.1904] | 0.9615 [0.9405, 0.9802] | 0.9804 [0.9658, 0.9934] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `teacher/efficientnetv2_m` | +0.0045 [+0.0020, +0.0075] * | +0.0420 [+0.0233, +0.0603] * | +0.0043 [+0.0017, +0.0072] * | +0.0098 [+0.0000, +0.0193] | +0.0045 [-0.0022, +0.0132] |
| `x_student` | `x_baseline` | +0.0104 [+0.0062, +0.0155] * | +0.1034 [+0.0756, +0.1333] * | +0.0088 [+0.0047, +0.0136] * | +0.0294 [+0.0136, +0.0447] * | +0.0143 [+0.0029, +0.0280] * |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/efficientnetv2_m`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9330 [0.9073, 0.9528] | 0.0533 [0.0310, 0.0954] | 0.1506 [0.1314, 0.1668] | 0.8368 [0.7735, 0.8950] | 0.9158 [0.8635, 0.9595] |
| pad_ufes_20 | 0.8189 [0.7832, 0.8543] | 0.7966 [0.7453, 0.8444] | 0.0988 [0.0831, 0.1152] | 0.4529 [0.3696, 0.5598] | 0.6751 [0.5822, 0.7542] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0708, +0.1542] * | -0.7433 [-0.7953, -0.6745] * | +0.0518 [+0.0254, +0.0744] * | +0.3839 [+0.2574, +0.4842] * | +0.2407 [+0.1446, +0.3462] * |

### `x_baseline`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9300 [0.9028, 0.9516] | 0.0540 [0.0320, 0.0970] | 0.1464 [0.1262, 0.1647] | 0.8184 [0.7443, 0.8828] | 0.8974 [0.8412, 0.9459] |
| pad_ufes_20 | 0.8784 [0.8480, 0.9069] | 0.8582 [0.8110, 0.8997] | 0.1240 [0.1090, 0.1395] | 0.6328 [0.5362, 0.7187] | 0.7905 [0.7243, 0.8642] |
| **isic2024_minus_pad_ufes_20** | +0.0515 [+0.0114, +0.0888] * | -0.8042 [-0.8505, -0.7410] * | +0.0224 [-0.0034, +0.0460] | +0.1856 [+0.0727, +0.3025] * | +0.1069 [+0.0121, +0.1878] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9483 [0.9267, 0.9659] | 0.0872 [0.0483, 0.1502] | 0.1607 [0.1442, 0.1757] | 0.8658 [0.7976, 0.9260] | 0.9316 [0.8783, 0.9746] |
| pad_ufes_20 | 0.8733 [0.8397, 0.9052] | 0.8439 [0.7917, 0.8910] | 0.1247 [0.1068, 0.1417] | 0.5630 [0.4629, 0.7317] | 0.8275 [0.7505, 0.8882] |
| **isic2024_minus_pad_ufes_20** | +0.0750 [+0.0350, +0.1127] * | -0.7567 [-0.8184, -0.6768] * | +0.0360 [+0.0117, +0.0584] * | +0.3028 [+0.1119, +0.4203] * | +0.1041 [+0.0263, +0.1905] * |


## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|---|
| `x_student` | `teacher/efficientnetv2_m` | isic2024 | +0.0153 [+0.0063, +0.0252] * | +0.0339 [+0.0099, +0.0654] * | +0.0102 [+0.0021, +0.0187] * | +0.0289 [-0.0050, +0.0583] | +0.0158 [-0.0104, +0.0410] |
| `x_student` | `teacher/efficientnetv2_m` | pad_ufes_20 | +0.0544 [+0.0385, +0.0711] * | +0.0473 [+0.0247, +0.0714] * | +0.0259 [+0.0170, +0.0346] * | +0.1101 [+0.0430, +0.2206] * | +0.1524 [+0.1030, +0.2088] * |
| `x_student` | `x_baseline` | isic2024 | +0.0184 [+0.0047, +0.0334] * | +0.0332 [+0.0083, +0.0662] * | +0.0143 [+0.0020, +0.0278] * | +0.0474 [-0.0022, +0.0989] | +0.0342 [-0.0027, +0.0740] |
| `x_student` | `x_baseline` | pad_ufes_20 | -0.0051 [-0.0201, +0.0101] | -0.0143 [-0.0370, +0.0083] | +0.0007 [-0.0076, +0.0096] | -0.0698 [-0.1258, +0.0526] | +0.0370 [-0.0190, +0.0706] |
