# Bootstrap 95% confidence intervals — `.tmp/ci_cand2/P2/indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `teacher/efficientnetv2_m` | 5 | 0.9793 [0.9713, 0.9863] | 0.6161 [0.5582, 0.6731] | 0.1804 [0.1726, 0.1872] | 0.9517 [0.9304, 0.9711] | 0.9758 [0.9600, 0.9893] |
| `x_baseline` | 5 | 0.9586 [0.9468, 0.9696] | 0.4169 [0.3572, 0.4756] | 0.1626 [0.1520, 0.1729] | 0.8928 [0.8592, 0.9231] | 0.9404 [0.9176, 0.9617] |
| `x_student` | 5 | 0.9815 [0.9742, 0.9881] | 0.6095 [0.5478, 0.6685] | 0.1826 [0.1758, 0.1890] | 0.9509 [0.9281, 0.9720] | 0.9736 [0.9560, 0.9893] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `teacher/efficientnetv2_m` | +0.0022 [-0.0019, +0.0063] | -0.0065 [-0.0314, +0.0189] | +0.0023 [-0.0019, +0.0064] | -0.0008 [-0.0169, +0.0154] | -0.0023 [-0.0120, +0.0080] |
| `x_student` | `x_baseline` | +0.0229 [+0.0156, +0.0306] * | +0.1926 [+0.1568, +0.2286] * | +0.0200 [+0.0131, +0.0270] * | +0.0581 [+0.0375, +0.0810] * | +0.0332 [+0.0183, +0.0495] * |

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
| isic2024 | 0.8824 [0.8484, 0.9141] | 0.0409 [0.0218, 0.0787] | 0.1202 [0.1023, 0.1395] | 0.6816 [0.5951, 0.7684] | 0.8079 [0.7357, 0.8706] |
| pad_ufes_20 | 0.7937 [0.7558, 0.8303] | 0.7700 [0.7149, 0.8236] | 0.0836 [0.0672, 0.1008] | 0.4540 [0.3432, 0.5709] | 0.6296 [0.5611, 0.7063] |
| **isic2024_minus_pad_ufes_20** | +0.0887 [+0.0362, +0.1385] * | -0.7292 [-0.7844, -0.6600] * | +0.0366 [+0.0099, +0.0615] * | +0.2276 [+0.0796, +0.3650] * | +0.1783 [+0.0714, +0.2729] * |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9412 [0.9181, 0.9603] | 0.0611 [0.0332, 0.1084] | 0.1553 [0.1388, 0.1710] | 0.8316 [0.7585, 0.9000] | 0.9079 [0.8464, 0.9590] |
| pad_ufes_20 | 0.8314 [0.7938, 0.8683] | 0.8049 [0.7491, 0.8583] | 0.1000 [0.0814, 0.1188] | 0.5196 [0.4218, 0.6227] | 0.7111 [0.6129, 0.7905] |
| **isic2024_minus_pad_ufes_20** | +0.1098 [+0.0654, +0.1507] * | -0.7438 [-0.8032, -0.6665] * | +0.0553 [+0.0297, +0.0791] * | +0.3120 [+0.1848, +0.4290] * | +0.1968 [+0.0969, +0.3058] * |


## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|---|
| `x_student` | `teacher/efficientnetv2_m` | isic2024 | +0.0081 [-0.0056, +0.0222] | +0.0078 [-0.0118, +0.0307] | +0.0047 [-0.0066, +0.0165] | -0.0053 [-0.0608, +0.0432] | -0.0079 [-0.0412, +0.0250] |
| `x_student` | `teacher/efficientnetv2_m` | pad_ufes_20 | +0.0125 [-0.0074, +0.0320] | +0.0084 [-0.0207, +0.0390] | +0.0012 [-0.0103, +0.0119] | +0.0667 [-0.0124, +0.1412] | +0.0360 [-0.0240, +0.0977] |
| `x_student` | `x_baseline` | isic2024 | +0.0588 [+0.0376, +0.0810] * | +0.0203 [-0.0142, +0.0574] | +0.0350 [+0.0199, +0.0489] * | +0.1500 [+0.0933, +0.2053] * | +0.1000 [+0.0548, +0.1508] * |
| `x_student` | `x_baseline` | pad_ufes_20 | +0.0377 [+0.0150, +0.0602] * | +0.0349 [+0.0051, +0.0650] * | +0.0164 [+0.0025, +0.0299] * | +0.0656 [-0.0132, +0.1382] | +0.0815 [+0.0146, +0.1308] * |
