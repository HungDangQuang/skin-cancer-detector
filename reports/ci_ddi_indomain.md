# Bootstrap 95% confidence intervals — `.tmp/ci_ddi_indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline` | 5 | 0.9769 [0.9682, 0.9846] | 0.5988 [0.5395, 0.6584] | 0.1781 [0.1698, 0.1854] | 0.9411 [0.9162, 0.9636] |
| `x_baseline__ddi` | 5 | 0.9744 [0.9653, 0.9825] | 0.6029 [0.5471, 0.6582] | 0.1755 [0.1669, 0.1833] | 0.9434 [0.9192, 0.9638] |
| `x_kd` | 5 | 0.9816 [0.9743, 0.9881] | 0.6000 [0.5445, 0.6561] | 0.1827 [0.1758, 0.1889] | 0.9540 [0.9318, 0.9744] |
| `x_kd__ddi` | 5 | 0.9816 [0.9746, 0.9879] | 0.6246 [0.5646, 0.6825] | 0.1826 [0.1760, 0.1886] | 0.9525 [0.9307, 0.9720] |
| `x_teacher` | 5 | 0.9823 [0.9760, 0.9881] | 0.6137 [0.5540, 0.6718] | 0.1833 [0.1773, 0.1889] | 0.9517 [0.9307, 0.9721] |
| `x_teacher__ddi` | 5 | 0.9793 [0.9713, 0.9863] | 0.6161 [0.5582, 0.6731] | 0.1804 [0.1726, 0.1872] | 0.9517 [0.9304, 0.9711] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `x_baseline__ddi` | `x_baseline` | -0.0025 [-0.0068, +0.0018] | +0.0041 [-0.0165, +0.0227] | -0.0026 [-0.0068, +0.0018] | +0.0023 [-0.0085, +0.0127] |
| `x_kd__ddi` | `x_kd` | -0.0000 [-0.0025, +0.0024] | +0.0246 [+0.0060, +0.0425] * | -0.0001 [-0.0026, +0.0023] | -0.0015 [-0.0123, +0.0095] |
| `x_teacher__ddi` | `x_teacher` | -0.0030 [-0.0061, -0.0002] * | +0.0024 [-0.0169, +0.0199] | -0.0029 [-0.0060, -0.0001] * | +0.0000 [-0.0109, +0.0110] |

## 4. Fairness gaps — paired bootstrap over `source`

### `x_baseline`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9254 [0.8979, 0.9472] | 0.0770 [0.0419, 0.1321] | 0.1450 [0.1236, 0.1619] | 0.8000 [0.7264, 0.8628] |
| pad_ufes_20 | 0.8039 [0.7654, 0.8414] | 0.7737 [0.7203, 0.8277] | 0.0866 [0.0676, 0.1055] | 0.4529 [0.3672, 0.5722] |
| **isic2024_minus_pad_ufes_20** | +0.1215 [+0.0744, +0.1651] * | -0.6966 [-0.7620, -0.6161] * | +0.0584 [+0.0310, +0.0833] * | +0.3471 [+0.2086, +0.4476] * |

### `x_baseline__ddi`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9161 [0.8870, 0.9385] | 0.0652 [0.0359, 0.1140] | 0.1367 [0.1165, 0.1548] | 0.8053 [0.7375, 0.8656] |
| pad_ufes_20 | 0.7945 [0.7583, 0.8283] | 0.7800 [0.7305, 0.8274] | 0.0834 [0.0672, 0.1002] | 0.4614 [0.3938, 0.5513] |
| **isic2024_minus_pad_ufes_20** | +0.1216 [+0.0782, +0.1641] * | -0.7147 [-0.7672, -0.6486] * | +0.0533 [+0.0274, +0.0771] * | +0.3439 [+0.2315, +0.4272] * |

### `x_kd`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9414 [0.9177, 0.9597] | 0.0769 [0.0425, 0.1308] | 0.1581 [0.1392, 0.1731] | 0.8421 [0.7704, 0.9039] |
| pad_ufes_20 | 0.8043 [0.7702, 0.8379] | 0.7743 [0.7222, 0.8241] | 0.0912 [0.0757, 0.1074] | 0.4582 [0.3766, 0.5584] |
| **isic2024_minus_pad_ufes_20** | +0.1371 [+0.0958, +0.1761] * | -0.6974 [-0.7557, -0.6196] * | +0.0669 [+0.0431, +0.0888] * | +0.3839 [+0.2615, +0.4819] * |

### `x_kd__ddi`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9418 [0.9200, 0.9593] | 0.0716 [0.0375, 0.1264] | 0.1570 [0.1405, 0.1713] | 0.8447 [0.7769, 0.9029] |
| pad_ufes_20 | 0.8245 [0.7875, 0.8596] | 0.7997 [0.7458, 0.8499] | 0.0993 [0.0816, 0.1166] | 0.4963 [0.4022, 0.5818] |
| **isic2024_minus_pad_ufes_20** | +0.1173 [+0.0751, +0.1577] * | -0.7281 [-0.7906, -0.6529] * | +0.0577 [+0.0332, +0.0805] * | +0.3484 [+0.2397, +0.4590] * |

### `x_teacher`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9435 [0.9244, 0.9598] | 0.0665 [0.0393, 0.1190] | 0.1586 [0.1451, 0.1716] | 0.8316 [0.7636, 0.8935] |
| pad_ufes_20 | 0.8198 [0.7866, 0.8535] | 0.7878 [0.7337, 0.8390] | 0.1014 [0.0876, 0.1165] | 0.4772 [0.3938, 0.5805] |
| **isic2024_minus_pad_ufes_20** | +0.1237 [+0.0843, +0.1613] * | -0.7213 [-0.7786, -0.6504] * | +0.0571 [+0.0368, +0.0756] * | +0.3543 [+0.2279, +0.4573] * |

### `x_teacher__ddi`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|
| isic2024 | 0.9330 [0.9073, 0.9528] | 0.0533 [0.0310, 0.0954] | 0.1506 [0.1314, 0.1668] | 0.8368 [0.7735, 0.8950] |
| pad_ufes_20 | 0.8189 [0.7832, 0.8543] | 0.7966 [0.7453, 0.8444] | 0.0988 [0.0831, 0.1152] | 0.4529 [0.3696, 0.5598] |
| **isic2024_minus_pad_ufes_20** | +0.1141 [+0.0708, +0.1542] * | -0.7433 [-0.7953, -0.6745] * | +0.0518 [+0.0254, +0.0744] * | +0.3839 [+0.2574, +0.4842] * |


## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|---|
| `x_baseline__ddi` | `x_baseline` | isic2024 | -0.0093 [-0.0249, +0.0056] | -0.0118 [-0.0322, +0.0071] | -0.0083 [-0.0215, +0.0050] | +0.0053 [-0.0310, +0.0444] |
| `x_baseline__ddi` | `x_baseline` | pad_ufes_20 | -0.0094 [-0.0263, +0.0078] | +0.0063 [-0.0197, +0.0305] | -0.0031 [-0.0106, +0.0051] | +0.0085 [-0.0646, +0.0754] |
| `x_kd__ddi` | `x_kd` | isic2024 | +0.0004 [-0.0079, +0.0081] | -0.0053 [-0.0239, +0.0099] | -0.0011 [-0.0079, +0.0059] | +0.0026 [-0.0334, +0.0395] |
| `x_kd__ddi` | `x_kd` | pad_ufes_20 | +0.0202 [+0.0026, +0.0369] * | +0.0254 [-0.0010, +0.0495] | +0.0081 [-0.0008, +0.0167] | +0.0381 [-0.0449, +0.0891] |
| `x_teacher__ddi` | `x_teacher` | isic2024 | -0.0105 [-0.0211, -0.0008] * | -0.0132 [-0.0369, +0.0026] | -0.0080 [-0.0176, +0.0006] | +0.0053 [-0.0308, +0.0487] |
| `x_teacher__ddi` | `x_teacher` | pad_ufes_20 | -0.0009 [-0.0181, +0.0154] | +0.0087 [-0.0170, +0.0325] | -0.0026 [-0.0106, +0.0054] | -0.0243 [-0.0874, +0.0371] |
