# Bootstrap 95% confidence intervals — `.tmp/ci_gates/fitzpatrick17k_headline`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | 5 | 0.7077 [0.6941, 0.7220] | 0.7022 [0.6843, 0.7213] | 0.0538 [0.0499, 0.0580] | 0.3415 [0.3162, 0.3661] | 0.4946 [0.4699, 0.5178] |
| `x_teacher` | 5 | 0.6937 [0.6802, 0.7072] | 0.6954 [0.6771, 0.7143] | 0.0493 [0.0457, 0.0533] | 0.3092 [0.2835, 0.3322] | 0.4690 [0.4453, 0.4955] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|
| `x_student` | `x_teacher` | +0.0140 [+0.0075, +0.0204] * | +0.0068 [-0.0008, +0.0146] | +0.0045 [+0.0021, +0.0068] * | +0.0323 [+0.0172, +0.0481] * | +0.0256 [+0.0082, +0.0394] * |

## 4. Fairness gaps — paired bootstrap over `tone_group`

### `x_student`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| dark | 0.7242 [0.6796, 0.7654] | 0.7355 [0.6804, 0.7894] | 0.0601 [0.0484, 0.0743] | 0.3462 [0.2815, 0.4319] | 0.5000 [0.4248, 0.5837] |
| light | 0.7222 [0.7036, 0.7413] | 0.7319 [0.7071, 0.7564] | 0.0551 [0.0495, 0.0610] | 0.3654 [0.3292, 0.4042] | 0.5207 [0.4886, 0.5554] |
| medium | 0.6813 [0.6582, 0.7037] | 0.6494 [0.6165, 0.6844] | 0.0511 [0.0451, 0.0574] | 0.2951 [0.2554, 0.3376] | 0.4473 [0.4077, 0.4861] |
| **dark_minus_light** | +0.0019 [-0.0450, +0.0464] | +0.0036 [-0.0577, +0.0624] | +0.0050 [-0.0077, +0.0203] | -0.0192 [-0.0974, +0.0775] | -0.0207 [-0.1034, +0.0683] |
| **dark_minus_medium** | +0.0428 [-0.0068, +0.0885] | +0.0861 [+0.0206, +0.1496] * | +0.0090 [-0.0046, +0.0243] | +0.0510 [-0.0269, +0.1480] | +0.0527 [-0.0318, +0.1465] |
| **light_minus_medium** | +0.0409 [+0.0119, +0.0708] * | +0.0825 [+0.0402, +0.1230] * | +0.0041 [-0.0043, +0.0129] | +0.0702 [+0.0170, +0.1269] * | +0.0734 [+0.0247, +0.1258] * |

### `x_teacher`

Group sizes (per fold): dark n=411, light n=2310, medium n=1599

| Group / gap | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|
| dark | 0.6900 [0.6469, 0.7316] | 0.7003 [0.6416, 0.7565] | 0.0488 [0.0378, 0.0618] | 0.3385 [0.2673, 0.4049] | 0.4596 [0.3914, 0.5346] |
| light | 0.7097 [0.6915, 0.7282] | 0.7271 [0.7020, 0.7514] | 0.0504 [0.0451, 0.0564] | 0.3299 [0.3022, 0.3689] | 0.5081 [0.4720, 0.5437] |
| medium | 0.6702 [0.6478, 0.6926] | 0.6426 [0.6086, 0.6773] | 0.0489 [0.0435, 0.0549] | 0.2626 [0.2290, 0.3035] | 0.4069 [0.3741, 0.4523] |
| **dark_minus_light** | -0.0198 [-0.0667, +0.0246] | -0.0268 [-0.0931, +0.0352] | -0.0016 [-0.0138, +0.0120] | +0.0086 [-0.0749, +0.0776] | -0.0485 [-0.1256, +0.0376] |
| **dark_minus_medium** | +0.0198 [-0.0289, +0.0669] | +0.0577 [-0.0119, +0.1245] | -0.0001 [-0.0126, +0.0132] | +0.0758 [-0.0088, +0.1467] | +0.0527 [-0.0318, +0.1345] |
| **light_minus_medium** | +0.0396 [+0.0112, +0.0694] * | +0.0845 [+0.0416, +0.1259] * | +0.0015 [-0.0063, +0.0099] | +0.0673 [+0.0189, +0.1202] * | +0.1012 [+0.0432, +0.1492] * |


## 6. Named A-vs-B pairs **within each `tone_group`** — paired (A − B)

The per-subgroup version of section 3b. On the in-domain tree this splits the delta by acquisition domain (`isic2024` vs `pad_ufes_20`), which the whole-test row cannot: the PAD subset holds ~75% of the positives on ~0.6% of the rows. `*` marks an interval excluding 0.

| A | B | group | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec | sens_at_80spec |
|---|---|---|---|---|---|---|---|
| `x_student` | `x_teacher` | dark | +0.0342 [+0.0116, +0.0572] * | +0.0352 [+0.0084, +0.0626] * | +0.0113 [+0.0033, +0.0193] * | +0.0077 [-0.0386, +0.0723] | +0.0404 [-0.0097, +0.0924] |
| `x_student` | `x_teacher` | light | +0.0125 [+0.0045, +0.0208] * | +0.0049 [-0.0043, +0.0150] | +0.0047 [+0.0015, +0.0079] * | +0.0355 [+0.0104, +0.0553] * | +0.0126 [-0.0070, +0.0369] |
| `x_student` | `x_teacher` | medium | +0.0111 [+0.0004, +0.0217] * | +0.0068 [-0.0059, +0.0202] | +0.0021 [-0.0015, +0.0060] | +0.0325 [+0.0037, +0.0557] * | +0.0404 [+0.0111, +0.0595] * |
