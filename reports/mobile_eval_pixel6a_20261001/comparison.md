# Server vs mobile — same bundle, same checkpoint, same threshold

`mobile`: executorch-android-1.4.0(threads=4) · batch 1 · device Pixel 6a (Tensor G1)
`mobile`: executorch-android-1.4.0(threads=4) · batch 1 · device Pixel 6a (Tensor G1)

Δ = `mobile` − `mobile`. † = threshold-free.

| dataset | metric | mobile | mobile | Δ |
|---|---|---|---|---|
| `indomain` | n | 59093 | 59093 | 0 |
| `indomain` | prevalence | 0.0045 | 0.0045 | +0.0000 |
| `indomain` | auprc† | 0.6182 | 0.6588 | +0.0406 |
| `indomain` | pauc_at_tpr80† | 0.1843 | 0.1837 | -0.0006 |
| `indomain` | auc_roc† | 0.9834 | 0.9828 | -0.0005 |
| `indomain` | sens_at_90spec† | 0.9585 | 0.9585 | +0.0000 |
| `indomain` | sens_at_95spec† | 0.9283 | 0.9208 | -0.0075 |
| `indomain` | sensitivity | 0.9509 | 0.9283 | -0.0226 |
| `indomain` | specificity | 0.9366 | 0.9451 | +0.0085 |
| `indomain` | f1_score | 0.1186 | 0.1315 | +0.0129 |
| `indomain` | brier | 0.0095 | 0.0127 | +0.0032 |
| `indomain` | ece | 0.0436 | 0.0721 | +0.0285 |
| `ham10000_headline` | n | 7470 | 7470 | 0 |
| `ham10000_headline` | prevalence | 0.1565 | 0.1565 | +0.0000 |
| `ham10000_headline` | auprc† | 0.4044 | 0.5793 | +0.1749 |
| `ham10000_headline` | pauc_at_tpr80† | 0.0956 | 0.1276 | +0.0319 |
| `ham10000_headline` | auc_roc† | 0.8049 | 0.8807 | +0.0757 |
| `ham10000_headline` | sens_at_90spec† | 0.4192 | 0.6133 | +0.1942 |
| `ham10000_headline` | sens_at_95spec† | 0.2335 | 0.4251 | +0.1916 |
| `ham10000_headline` | sensitivity | 0.9957 | 1.0000 | +0.0043 |
| `ham10000_headline` | specificity | 0.0621 | 0.0927 | +0.0306 |
| `ham10000_headline` | f1_score | 0.2824 | 0.2903 | +0.0078 |
| `ham10000_headline` | brier | 0.3270 | 0.2264 | -0.1005 |
| `ham10000_headline` | ece | 0.4470 | 0.3550 | -0.0920 |
| `fitzpatrick17k_headline` | n | 4320 | 4320 | 0 |
| `fitzpatrick17k_headline` | prevalence | 0.5000 | 0.5000 | +0.0000 |
| `fitzpatrick17k_headline` | auprc† | 0.5963 | 0.7246 | +0.1284 |
| `fitzpatrick17k_headline` | pauc_at_tpr80† | 0.0407 | 0.0617 | +0.0210 |
| `fitzpatrick17k_headline` | auc_roc† | 0.6176 | 0.7315 | +0.1138 |
| `fitzpatrick17k_headline` | sens_at_90spec† | 0.1778 | 0.3634 | +0.1856 |
| `fitzpatrick17k_headline` | sens_at_95spec† | 0.1042 | 0.2384 | +0.1343 |
| `fitzpatrick17k_headline` | sensitivity | 1.0000 | 1.0000 | +0.0000 |
| `fitzpatrick17k_headline` | specificity | 0.0009 | 0.0014 | +0.0005 |
| `fitzpatrick17k_headline` | f1_score | 0.6669 | 0.6670 | +0.0001 |
| `fitzpatrick17k_headline` | brier | 0.3214 | 0.2207 | -0.1007 |
| `fitzpatrick17k_headline` | ece | 0.2862 | 0.0841 | -0.2021 |

Reading it: a non-zero Δ on a † row comes from the runtime (graph lowering, or the JPEG decoder). On a non-† row it can additionally come from a logit crossing the frozen threshold. The project's single-fold rerun noise floor is 0.0053 AUPRC, but inference on a fixed checkpoint is deterministic, so a genuine runtime Δ should be far smaller than that.
