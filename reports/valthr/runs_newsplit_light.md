# Val-frozen vs test-Youden threshold metrics — `/workspace/skin-cancer-detector/experiments/runs_newsplit_light`

Predictions: `fold_*/predictions.csv`; threshold source: `fold_*/val_predictions.csv` (Youden's J on that fold's own val set).

`testthr_*` reproduces what `test_metrics*.json` reports (threshold fitted on the test set — optimistic). `valthr_*` is the honest counterpart (threshold frozen before seeing the test labels). Mean ± std over the folds of each run; the std is the spread between the fold models, not a confidence interval. Ranking metrics do not depend on a threshold and are not repeated here.

## Group `all`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2376 ± 0.0182 → 0.2434 ± 0.0443 | 0.9238 ± 0.0258 → 0.9117 ± 0.0172 | 0.9324 ± 0.0279 → 0.9360 ± 0.0153 | 0.1182 ± 0.0317 → 0.1166 ± 0.0209 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.1871 ± 0.0399 → 0.1840 ± 0.0637 | 0.9404 ± 0.0098 → 0.9374 ± 0.0143 | 0.9277 ± 0.0037 → 0.9239 ± 0.0212 | 0.1047 ± 0.0047 → 0.1039 ± 0.0223 |
| `teacher/efficientnetv2_m` | 5 | 0.2733 ± 0.0978 → 0.2182 ± 0.0617 | 0.9208 ± 0.0173 → 0.9291 ± 0.0195 | 0.9499 ± 0.0153 → 0.9296 ± 0.0222 | 0.1515 ± 0.0497 → 0.1137 ± 0.0356 |

## Group `isic2024`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2376 ± 0.0182 → 0.2434 ± 0.0443 | 0.7342 ± 0.0899 → 0.6921 ± 0.0600 | 0.9356 ± 0.0280 → 0.9392 ± 0.0153 | 0.0309 ± 0.0072 → 0.0293 ± 0.0045 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.1871 ± 0.0399 → 0.1840 ± 0.0637 | 0.7921 ± 0.0341 → 0.7816 ± 0.0498 | 0.9309 ± 0.0037 → 0.9271 ± 0.0213 | 0.0288 ± 0.0018 → 0.0282 ± 0.0060 |
| `teacher/efficientnetv2_m` | 5 | 0.2733 ± 0.0978 → 0.2182 ± 0.0617 | 0.7237 ± 0.0603 → 0.7553 ± 0.0628 | 0.9531 ± 0.0153 → 0.9328 ± 0.0222 | 0.0417 ± 0.0142 → 0.0305 ± 0.0091 |

## Group `pad_ufes_20`

| Run | folds | thr test → val | sens test → val | spec test → val | f1 test → val |
|---|---|---|---|---|---|
| `baseline_mobilenetv4_conv_medium` | 5 | 0.2376 ± 0.0182 → 0.2434 ± 0.0443 | 1.0000 ± 0.0000 → 1.0000 ± 0.0000 | 0.0298 ± 0.0133 → 0.0317 ± 0.0206 | 0.6520 ± 0.0031 → 0.6524 ± 0.0048 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.1871 ± 0.0399 → 0.1840 ± 0.0637 | 1.0000 ± 0.0000 → 1.0000 ± 0.0000 | 0.0260 ± 0.0043 → 0.0269 ± 0.0087 | 0.6511 ± 0.0010 → 0.6513 ± 0.0020 |
| `teacher/efficientnetv2_m` | 5 | 0.2733 ± 0.0978 → 0.2182 ± 0.0617 | 1.0000 ± 0.0000 → 0.9989 ± 0.0024 | 0.0577 ± 0.0233 → 0.0385 ± 0.0247 | 0.6586 ± 0.0056 → 0.6536 ± 0.0049 |

## Coverage

Scored folds: 15. Skipped (no `val_predictions.csv`): 0.

