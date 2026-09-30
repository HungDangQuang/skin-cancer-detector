# Bootstrap 95% confidence intervals — `.tmp/framing_ci`

B = 2000 replicates, seed 42, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `shipA_crop50` | 5 | 0.6754 [0.6610, 0.6905] | 0.6664 [0.6472, 0.6870] | 0.0489 [0.0448, 0.0531] | 0.2711 [0.2465, 0.2960] |
| `shipA_crop70` | 5 | 0.6797 [0.6650, 0.6948] | 0.6695 [0.6501, 0.6908] | 0.0519 [0.0478, 0.0564] | 0.2681 [0.2475, 0.2897] |
| `shipA_headline` | 5 | 0.6726 [0.6575, 0.6873] | 0.6623 [0.6436, 0.6840] | 0.0502 [0.0462, 0.0545] | 0.2598 [0.2367, 0.2806] |
| `shipB_crop50` | 5 | 0.6497 [0.6358, 0.6635] | 0.6332 [0.6159, 0.6531] | 0.0455 [0.0418, 0.0493] | 0.2340 [0.2152, 0.2544] |
| `shipB_crop70` | 5 | 0.6543 [0.6406, 0.6685] | 0.6302 [0.6123, 0.6500] | 0.0485 [0.0447, 0.0527] | 0.2190 [0.1994, 0.2378] |
| `shipB_headline` | 5 | 0.6427 [0.6283, 0.6568] | 0.6172 [0.5991, 0.6367] | 0.0459 [0.0422, 0.0498] | 0.2044 [0.1858, 0.2235] |
| `teach_crop50` | 5 | 0.7022 [0.6886, 0.7164] | 0.6874 [0.6700, 0.7067] | 0.0589 [0.0547, 0.0634] | 0.2936 [0.2713, 0.3204] |
| `teach_crop70` | 5 | 0.7082 [0.6947, 0.7221] | 0.6925 [0.6747, 0.7114] | 0.0601 [0.0560, 0.0646] | 0.3033 [0.2800, 0.3247] |
| `teach_headline` | 5 | 0.7039 [0.6904, 0.7179] | 0.6920 [0.6742, 0.7111] | 0.0573 [0.0533, 0.0616] | 0.3137 [0.2891, 0.3346] |

## 3b. Named A-vs-B pairs — paired bootstrap (A − B)

Requested with `--pair A:B`. Sections 2 and 3 only pair kd-vs-baseline and suffix-vs-main, so two KD runs compared to each other land here. **This is the table to read when two per-run intervals in section 1 overlap** — overlapping unpaired intervals do not mean the models are equivalent; the paired delta can still exclude 0. `*` marks an interval excluding 0.

| A | B | auc_roc | auprc | pauc_at_tpr80 | sens_at_90spec |
|---|---|---|---|---|---|
| `shipA_crop50` | `shipA_headline` | +0.0028 [-0.0057, +0.0114] | +0.0041 [-0.0068, +0.0148] | -0.0013 [-0.0043, +0.0017] | +0.0113 [-0.0076, +0.0319] |
| `shipA_crop70` | `shipA_headline` | +0.0071 [+0.0021, +0.0122] * | +0.0071 [+0.0001, +0.0141] * | +0.0017 [-0.0002, +0.0037] | +0.0083 [-0.0033, +0.0228] |
| `shipB_crop50` | `shipB_headline` | +0.0070 [-0.0018, +0.0156] | +0.0160 [+0.0057, +0.0263] * | -0.0004 [-0.0033, +0.0024] | +0.0296 [+0.0127, +0.0478] * |
| `shipB_crop70` | `shipB_headline` | +0.0115 [+0.0061, +0.0168] * | +0.0130 [+0.0065, +0.0195] * | +0.0026 [+0.0008, +0.0044] * | +0.0146 [+0.0022, +0.0269] * |
| `teach_crop50` | `teach_headline` | -0.0017 [-0.0096, +0.0062] | -0.0045 [-0.0143, +0.0056] | +0.0016 [-0.0014, +0.0046] | -0.0201 [-0.0373, +0.0023] |
| `teach_crop70` | `teach_headline` | +0.0042 [-0.0003, +0.0090] | +0.0005 [-0.0051, +0.0059] | +0.0028 [+0.0009, +0.0047] * | -0.0104 [-0.0218, +0.0034] |
