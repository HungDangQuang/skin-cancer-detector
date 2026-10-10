# Bootstrap 95% confidence intervals — `.tmp/ci_gates/fitzpatrick17k_headline`

B = 2000 replicates, seed 3, 4320 test rows.

**Fold convention:** each replicate draws one set of row indices, scores **every fold** on those same rows, and averages. Folds are five models on the *same* test set, so their predictions are never pooled (that would replicate each row 5× and shrink the interval into fiction). The interval therefore describes the same fold-mean the other tables quote, with the test set's sampling error instead of the between-model spread.

## 1. Per-run

| Run | folds | sens_at_80spec |
|---|---|---|
| `x_student` | 5 | 0.4946 [0.4700, 0.5191] |
| `x_teacher` | 5 | 0.4690 [0.4463, 0.4953] |
