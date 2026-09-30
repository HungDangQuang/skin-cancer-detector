# Server vs mobile — same bundle, same checkpoint, same threshold

`server`: pytorch-eager(threads=8) · batch 1 · device cpu
`mobile`: executorch-android-1.4.0(threads=4) · batch 1 · device Pixel 6a (Tensor G1)

Δ = `mobile` − `server`. † = threshold-free.

| dataset | metric | server | mobile | Δ |
|---|---|---|---|---|
| `indomain` | n | 59093 | 59093 | 0 |
| `indomain` | prevalence | 0.0045 | 0.0045 | +0.0000 |
| `indomain` | auprc† | 0.6182 | 0.6182 | +0.0000 |
| `indomain` | pauc_at_tpr80† | 0.1843 | 0.1843 | +0.0000 |
| `indomain` | auc_roc† | 0.9834 | 0.9834 | +0.0000 |
| `indomain` | sens_at_90spec† | 0.9585 | 0.9585 | +0.0000 |
| `indomain` | sens_at_95spec† | 0.9283 | 0.9283 | +0.0000 |
| `indomain` | sensitivity | 0.9509 | 0.9509 | +0.0000 |
| `indomain` | specificity | 0.9366 | 0.9366 | +0.0000 |
| `indomain` | f1_score | 0.1186 | 0.1186 | +0.0000 |
| `indomain` | brier | 0.0095 | 0.0095 | -0.0000 |
| `indomain` | ece | 0.0436 | 0.0436 | -0.0000 |
| `ham10000_headline` | n | 7470 | 7470 | 0 |
| `ham10000_headline` | prevalence | 0.1565 | 0.1565 | +0.0000 |
| `ham10000_headline` | auprc† | 0.4044 | 0.4044 | +0.0000 |
| `ham10000_headline` | pauc_at_tpr80† | 0.0956 | 0.0956 | +0.0000 |
| `ham10000_headline` | auc_roc† | 0.8049 | 0.8049 | +0.0000 |
| `ham10000_headline` | sens_at_90spec† | 0.4192 | 0.4192 | +0.0000 |
| `ham10000_headline` | sens_at_95spec† | 0.2335 | 0.2335 | +0.0000 |
| `ham10000_headline` | sensitivity | 0.9957 | 0.9957 | +0.0000 |
| `ham10000_headline` | specificity | 0.0621 | 0.0621 | +0.0000 |
| `ham10000_headline` | f1_score | 0.2824 | 0.2824 | +0.0000 |
| `ham10000_headline` | brier | 0.3270 | 0.3270 | -0.0000 |
| `ham10000_headline` | ece | 0.4470 | 0.4470 | -0.0000 |
| `fitzpatrick17k_headline` | n | 4320 | 4320 | 0 |
| `fitzpatrick17k_headline` | prevalence | 0.5000 | 0.5000 | +0.0000 |
| `fitzpatrick17k_headline` | auprc† | 0.5963 | 0.5963 | +0.0000 |
| `fitzpatrick17k_headline` | pauc_at_tpr80† | 0.0407 | 0.0407 | +0.0000 |
| `fitzpatrick17k_headline` | auc_roc† | 0.6176 | 0.6176 | +0.0000 |
| `fitzpatrick17k_headline` | sens_at_90spec† | 0.1778 | 0.1778 | +0.0000 |
| `fitzpatrick17k_headline` | sens_at_95spec† | 0.1042 | 0.1042 | +0.0000 |
| `fitzpatrick17k_headline` | sensitivity | 1.0000 | 1.0000 | +0.0000 |
| `fitzpatrick17k_headline` | specificity | 0.0009 | 0.0009 | +0.0000 |
| `fitzpatrick17k_headline` | f1_score | 0.6669 | 0.6669 | +0.0000 |
| `fitzpatrick17k_headline` | brier | 0.3214 | 0.3214 | -0.0000 |
| `fitzpatrick17k_headline` | ece | 0.2862 | 0.2862 | -0.0000 |

Reading it: a non-zero Δ on a † row comes from the runtime (graph lowering, or the JPEG decoder). On a non-† row it can additionally come from a logit crossing the frozen threshold. The project's single-fold rerun noise floor is 0.0053 AUPRC, but inference on a fixed checkpoint is deterministic, so a genuine runtime Δ should be far smaller than that.
