# Bootstrap 95% confidence intervals — `.tmp/ci_cand2/P1/indomain`

B = 2000 replicates, seed 42, 59093 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `teacher/convnextv2_base` | 5 | 0.9807 [0.9732, 0.9877] | 0.6654 [0.6089, 0.7195] | 0.1815 [0.1743, 0.1884] | 0.9517 [0.9287, 0.9728] | 0.9751 [0.9592, 0.9888] |
| `x_baseline` | 5 | 0.9654 [0.9556, 0.9744] | 0.5243 [0.4696, 0.5768] | 0.1685 [0.1597, 0.1770] | 0.9170 [0.8908, 0.9425] | 0.9562 [0.9367, 0.9741] |
| `x_student` | 5 | 0.9815 [0.9739, 0.9881] | 0.6689 [0.6143, 0.7235] | 0.1823 [0.1751, 0.1887] | 0.9592 [0.9386, 0.9774] | 0.9743 [0.9585, 0.9880] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `teacher/convnextv2_base` | +0.0008 [-0.0021, +0.0035] | +0.0036 [-0.0121, +0.0214] | +0.0008 [-0.0021, +0.0035] | +0.0075 [+0.0007, +0.0152] * | -0.0008 [-0.0056, +0.0043] |
| `x_student` | `x_baseline` | +0.0161 [+0.0111, +0.0217] * | +0.1447 [+0.1187, +0.1750] * | +0.0139 [+0.0092, +0.0188] * | +0.0423 [+0.0272, +0.0593] * | +0.0181 [+0.0083, +0.0285] * |

## 4. Fairness gaps — paired bootstrap over `source`

### `teacher/convnextv2_base`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9374 [0.9134, 0.9582] | 0.0826 [0.0448, 0.1417] | 0.1507 [0.1324, 0.1687] | 0.8368 [0.7627, 0.9000] | 0.9132 [0.8588, 0.9576] |
| pad_ufes_20 | 0.8725 [0.8405, 0.9012] | 0.8514 [0.8069, 0.8921] | 0.1203 [0.1031, 0.1371] | 0.6063 [0.5140, 0.7185] | 0.8042 [0.7274, 0.8638] |
| **isic2024_minus_pad_ufes_20** | +0.0649 [+0.0261, +0.1017] * | -0.7688 [-0.8232, -0.6956] * | +0.0304 [+0.0054, +0.0542] * | +0.2305 [+0.0922, +0.3389] * | +0.1089 [+0.0283, +0.1980] * |

### `x_baseline`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9107 [0.8801, 0.9357] | 0.0391 [0.0248, 0.0715] | 0.1346 [0.1128, 0.1544] | 0.7711 [0.6974, 0.8445] | 0.8711 [0.8074, 0.9238] |
| pad_ufes_20 | 0.8781 [0.8486, 0.9054] | 0.8592 [0.8147, 0.8985] | 0.1244 [0.1088, 0.1395] | 0.6317 [0.5528, 0.7155] | 0.8042 [0.7244, 0.8694] |
| **isic2024_minus_pad_ufes_20** | +0.0325 [-0.0090, +0.0707] | -0.8202 [-0.8605, -0.7656] * | +0.0102 [-0.0162, +0.0359] | +0.1393 [+0.0233, +0.2414] * | +0.0668 [-0.0258, +0.1622] |

### `x_student`

Group sizes (per fold): isic2024 n=58696, pad_ufes_20 n=397

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| isic2024 | 0.9404 [0.9161, 0.9599] | 0.0885 [0.0485, 0.1523] | 0.1542 [0.1346, 0.1707] | 0.8605 [0.7949, 0.9171] | 0.9105 [0.8571, 0.9539] |
| pad_ufes_20 | 0.8891 [0.8579, 0.9193] | 0.8619 [0.8157, 0.9065] | 0.1298 [0.1107, 0.1474] | 0.6772 [0.5380, 0.7829] | 0.8571 [0.7811, 0.9101] |
| **isic2024_minus_pad_ufes_20** | +0.0514 [+0.0136, +0.0879] * | -0.7734 [-0.8343, -0.6948] * | +0.0244 [-0.0015, +0.0492] | +0.1833 [+0.0536, +0.3275] * | +0.0534 [-0.0208, +0.1422] |


## 6. Named A-vs-B pairs **within each `source`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|---|
| `x_student` | `teacher/convnextv2_base` | isic2024 | +0.0031 [-0.0070, +0.0132] | +0.0058 [-0.0133, +0.0269] | +0.0035 [-0.0053, +0.0122] | +0.0237 [+0.0024, +0.0493] * | -0.0026 [-0.0200, +0.0143] |
| `x_student` | `teacher/convnextv2_base` | pad_ufes_20 | +0.0166 [+0.0036, +0.0298] * | +0.0105 [-0.0090, +0.0320] | +0.0095 [+0.0020, +0.0164] * | +0.0709 [-0.0232, +0.1309] | +0.0529 [+0.0126, +0.0938] * |
| `x_student` | `x_baseline` | isic2024 | +0.0298 [+0.0162, +0.0443] * | +0.0494 [+0.0145, +0.0930] * | +0.0196 [+0.0082, +0.0304] * | +0.0895 [+0.0457, +0.1324] * | +0.0395 [+0.0087, +0.0725] * |
| `x_student` | `x_baseline` | pad_ufes_20 | +0.0110 [-0.0018, +0.0236] | +0.0026 [-0.0169, +0.0231] | +0.0054 [-0.0039, +0.0140] | +0.0455 [-0.0460, +0.1061] | +0.0529 [+0.0124, +0.0949] * |
