# Server vs mobile — same bundle, same checkpoint, same threshold

`server`: pytorch-eager · batch 1 · device cpu
`host-executorch`: executorch-1.5.1 · batch 1 · device cpu

Δ = `host-executorch` − `server`. † = threshold-free.

| dataset | metric | server | host-executorch | Δ |
|---|---|---|---|---|
| `indomain` | n | 59093 | 59093 | 0 |
| `indomain` | prevalence | 0.0045 | 0.0045 | +0.0000 |
| `indomain` | auprc† | 0.6588 | 0.6588 | +0.0000 |
| `indomain` | pauc_at_tpr80† | 0.1837 | 0.1837 | -0.0000 |
| `indomain` | auc_roc† | 0.9828 | 0.9828 | -0.0000 |
| `indomain` | sens_at_90spec† | 0.9585 | 0.9585 | +0.0000 |
| `indomain` | sens_at_95spec† | 0.9208 | 0.9208 | +0.0000 |
| `indomain` | sensitivity | 0.9283 | 0.9283 | +0.0000 |
| `indomain` | specificity | 0.9451 | 0.9451 | +0.0000 |
| `indomain` | f1_score | 0.1315 | 0.1315 | +0.0000 |
| `indomain` | brier | 0.0127 | 0.0127 | -0.0000 |
| `indomain` | ece | 0.0721 | 0.0721 | +0.0000 |
| `ham10000_headline` | n | 7470 | 7470 | 0 |
| `ham10000_headline` | prevalence | 0.1565 | 0.1565 | +0.0000 |
| `ham10000_headline` | auprc† | 0.5793 | 0.5793 | -0.0000 |
| `ham10000_headline` | pauc_at_tpr80† | 0.1276 | 0.1276 | -0.0000 |
| `ham10000_headline` | auc_roc† | 0.8807 | 0.8807 | +0.0000 |
| `ham10000_headline` | sens_at_90spec† | 0.6133 | 0.6133 | +0.0000 |
| `ham10000_headline` | sens_at_95spec† | 0.4251 | 0.4251 | +0.0000 |
| `ham10000_headline` | sensitivity | 1.0000 | 1.0000 | +0.0000 |
| `ham10000_headline` | specificity | 0.0927 | 0.0927 | +0.0000 |
| `ham10000_headline` | f1_score | 0.2903 | 0.2903 | +0.0000 |
| `ham10000_headline` | brier | 0.2264 | 0.2264 | -0.0000 |
| `ham10000_headline` | ece | 0.3550 | 0.3550 | -0.0000 |
| `fitzpatrick17k_headline` | n | 4320 | 4320 | 0 |
| `fitzpatrick17k_headline` | prevalence | 0.5000 | 0.5000 | +0.0000 |
| `fitzpatrick17k_headline` | auprc† | 0.7246 | 0.7246 | +0.0000 |
| `fitzpatrick17k_headline` | pauc_at_tpr80† | 0.0617 | 0.0617 | +0.0000 |
| `fitzpatrick17k_headline` | auc_roc† | 0.7315 | 0.7315 | +0.0000 |
| `fitzpatrick17k_headline` | sens_at_90spec† | 0.3634 | 0.3634 | +0.0000 |
| `fitzpatrick17k_headline` | sens_at_95spec† | 0.2384 | 0.2384 | +0.0000 |
| `fitzpatrick17k_headline` | sensitivity | 1.0000 | 1.0000 | +0.0000 |
| `fitzpatrick17k_headline` | specificity | 0.0014 | 0.0014 | +0.0000 |
| `fitzpatrick17k_headline` | f1_score | 0.6670 | 0.6670 | +0.0000 |
| `fitzpatrick17k_headline` | brier | 0.2207 | 0.2207 | -0.0000 |
| `fitzpatrick17k_headline` | ece | 0.0841 | 0.0841 | -0.0000 |

Reading it: a non-zero Δ on a † row comes from the runtime (graph lowering, or the JPEG decoder). On a non-† row it can additionally come from a logit crossing the frozen threshold. The project's single-fold rerun noise floor is 0.0053 AUPRC, but inference on a fixed checkpoint is deterministic, so a genuine runtime Δ should be far smaller than that.
