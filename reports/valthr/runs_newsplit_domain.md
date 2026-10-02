# Val-frozen vs test-Youden threshold metrics — `/workspace/skin-cancer-detector/experiments/runs_newsplit_domain`

Predictions: `fold_*/predictions.csv`; threshold source: `fold_*/val_predictions.csv` (Youden's J on that fold's own val set).

`testthr_*` reproduces what `test_metrics*.json` reports (threshold fitted on the test set — optimistic). `valthr_*` is the honest counterpart (threshold frozen before seeing the test labels). Mean ± std over the folds of each run; the std is the spread between the fold models, not a confidence interval. Ranking metrics do not depend on a threshold and are not repeated here.

## Group `all`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2234 ± 0.0172 → 0.2491 ± 0.0378 | 0.9238 ± 0.0090 → 0.8936 ± 0.0315 | 0.9172 ± 0.0113 → 0.9381 ± 0.0212 | 0.0921 ± 0.0121 → 0.1219 ± 0.0315 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.2246 ± 0.0888 → 0.2263 ± 0.0758 | 0.9208 ± 0.0243 → 0.9109 ± 0.0224 | 0.9310 ± 0.0210 → 0.9329 ± 0.0164 | 0.1132 ± 0.0294 → 0.1119 ± 0.0199 |
| `teacher/efficientnetv2_m` | 5 | 0.2784 ± 0.0427 → 0.2978 ± 0.0488 | 0.9366 ± 0.0191 → 0.9147 ± 0.0310 | 0.9377 ± 0.0123 → 0.9437 ± 0.0236 | 0.1214 ± 0.0187 → 0.1389 ± 0.0438 |

## Group `isic2024`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2234 ± 0.0172 → 0.2491 ± 0.0378 | 0.7342 ± 0.0314 → 0.6289 ± 0.1099 | 0.9203 ± 0.0113 → 0.9413 ± 0.0212 | 0.0236 ± 0.0037 → 0.0282 ± 0.0054 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.2246 ± 0.0888 → 0.2263 ± 0.0758 | 0.7263 ± 0.0875 → 0.6947 ± 0.0723 | 0.9342 ± 0.0211 → 0.9362 ± 0.0164 | 0.0292 ± 0.0060 → 0.0281 ± 0.0040 |
| `teacher/efficientnetv2_m` | 5 | 0.2784 ± 0.0427 → 0.2978 ± 0.0488 | 0.7789 ± 0.0667 → 0.7026 ± 0.1079 | 0.9410 ± 0.0123 → 0.9469 ± 0.0236 | 0.0337 ± 0.0056 → 0.0364 ± 0.0110 |

## Group `pad_ufes_20`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2234 ± 0.0172 → 0.2491 ± 0.0378 | 1.0000 ± 0.0000 → 1.0000 ± 0.0000 | 0.0221 ± 0.0134 → 0.0298 ± 0.0196 | 0.6502 ± 0.0031 → 0.6520 ± 0.0046 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.2246 ± 0.0888 → 0.2263 ± 0.0758 | 0.9989 ± 0.0024 → 0.9979 ± 0.0029 | 0.0202 ± 0.0120 → 0.0221 ± 0.0185 | 0.6493 ± 0.0025 → 0.6492 ± 0.0034 |
| `teacher/efficientnetv2_m` | 5 | 0.2784 ± 0.0427 → 0.2978 ± 0.0488 | 1.0000 ± 0.0000 → 1.0000 ± 0.0000 | 0.0163 ± 0.0111 → 0.0260 ± 0.0208 | 0.6488 ± 0.0026 → 0.6511 ± 0.0049 |

## Coverage

Scored folds: 15. Skipped (no `val_predictions.csv`): 0.

