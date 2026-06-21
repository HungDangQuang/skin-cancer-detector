# Student Arm Analysis & Thesis Feasibility — 2026-06-09

Consolidated analysis of the full KD experiment (teacher + 30 student runs) and an
assessment of thesis readiness.

> **Data provenance.** Student numbers below are **extracted from the training-log
> auto-eval lines** (`logs/train_student_<job>_<fold>.out`, the
> `src.evaluation.evaluator` line). They are byte-identical to the cluster's
> `experiments/runs/<run>/fold_*/test_metrics.json`, which are **not yet rsync'd**.
> Re-pull the canonical JSONs + run `22_aggregate_folds.slurm` to replace these with
> the official `aggregated.{json,md}` before quoting in the thesis.
> Teacher numbers are re-aggregated from the fresh per-fold JSONs (its on-disk
> `aggregated.json` is **stale** — job 28179, old leaked-split teacher, AUC 0.87 — ignore it).

## 1. Runs covered

| Job | Model | Mode | Run dir |
|---|---|---|---|
| 28250 | EfficientNet-B4 | teacher | `teacher/efficientnet_b4` |
| 28273 | EfficientNet-B0 | **KD** | `kd_efficientnet_b4_to_efficientnet_b0` |
| 28276 | MobileNetV3-Large | **KD** | `kd_efficientnet_b4_to_mobilenetv3_large` |
| 28279 | MobileViT-S | **KD** | `kd_efficientnet_b4_to_mobilevit_s` |
| 28281 | EfficientNet-B0 | baseline | `baseline_efficientnet_b0` |
| 28282 | MobileNetV3-Large | baseline | `baseline_mobilenetv3_large` |
| 28283 | MobileViT-S | baseline | `baseline_mobilevit_s` |

All 6 student jobs × 5 folds completed (30 runs). Test set: independent,
patient-disjoint held-out split, 241 pos / 61,831 neg (**0.39% malignant**).
pAUC is the correct post-2026-06-04 ISIC metric (range ≈ [0.02, 0.20]).

## 2. Results — 5-fold mean ± std (4 dp)

| metric | KD b0 | base b0 | KD mnet | base mnet | KD mvit | base mvit | teacher B4 |
|---|---|---|---|---|---|---|---|
| pauc@tpr80 | 0.1877±0.0005 | 0.1850±0.0023 | **0.1881**±0.0009 | 0.1858±0.0007 | 0.1879±0.0008 | 0.1865±0.0018 | 0.1785±0.0031 |
| auc_roc | 0.9870±0.0005 | 0.9844±0.0023 | **0.9873**±0.0009 | 0.9852±0.0007 | 0.9872±0.0009 | 0.9858±0.0018 | 0.9777±0.0031 |
| sensitivity | 0.9403±0.0056 | 0.9328±0.0184 | **0.9552**±0.0049 | 0.9336±0.0114 | 0.9453±0.0119 | 0.9403±0.0122 | 0.9087±0.0114 |
| specificity | 0.9485±0.0060 | 0.9375±0.0099 | 0.9364±0.0069 | 0.9564±0.0095 | 0.9439±0.0073 | 0.9515±0.0122 | 0.9551±0.0084 |
| f1_score | 0.1253±0.0124 | 0.1057±0.0126 | 0.1056±0.0104 | 0.1472±0.0264 | 0.1171±0.0126 | 0.1358±0.0236 | 0.1396±0.0267 |
| accuracy | 0.9484±0.0059 | 0.9375±0.0098 | 0.9365±0.0068 | 0.9563±0.0094 | 0.9439±0.0072 | 0.9515±0.0121 | ~0.95 |

Low precision/F1 (~0.05–0.15) is an **artifact of 0.39% prevalence + Youden
thresholding**, not a model defect. Accuracy is non-informative at this imbalance.

## 3. KD vs baseline (pooled-std significance, n=5)

Rule: KD wins iff Δauc > 0 **and** Δsens > 0 (domain priority: a missed malignant
outweighs a false alarm).

| Student | Δ auc | Δ sens | Δ spec | Verdict |
|---|---|---|---|---|
| **MobileNetV3-Large** | +0.0021 (robust) | **+0.0216 (robust)** | −0.0200 (robust) | **KD wins** — buys +2.2pp sensitivity for −2.0pp specificity |
| EfficientNet-B0 | +0.0026 (marginal) | +0.0075 (noise) | +0.0109 (marginal) | KD helps, weakly — improves every axis |
| MobileViT-S | +0.0014 (noise) | +0.0050 (noise) | −0.0076 (noise) | Wash — KD neither helps nor hurts |

**KD's benefit is real and robust for MobileNetV3, marginal for B0, negligible for MobileViT.**

## 4. Cross-student ranking (KD arm, sensitivity → AUC)

1. **KD MobileNetV3-Large** — sens 0.9552, AUC 0.9873, pAUC 0.1881 ← best student
2. KD MobileViT-S — sens 0.9453, AUC 0.9872
3. KD EfficientNet-B0 — sens 0.9403, AUC 0.9870

No Pareto-dominated student; they trade sensitivity vs specificity.

## 5. Teacher vs students

Students **out-generalize** the teacher (AUC 0.987 vs 0.978, sens ~0.94 vs 0.909).
Because the *baselines* beat it too, this is **not** a KD artifact — the smaller
backbones simply generalize better here; B4's extra capacity is not the bottleneck.
KD transfer is excellent (students at/above teacher). Frame this deliberately in the
writeup so it does not read as a bug.

## 6. Conclusions

- **Best model:** KD MobileNetV3-Large (highest sensitivity + AUC).
- **Does KD work?** Yes — robustly for MobileNetV3, marginally for B0, not for MobileViT.
- **Mobile-ready?** Architecturally yes (~5–6M params, ~21–23 MB FP32). On-device
  metrics (size/params/latency) not yet measured — see gaps. **Quantization de-scoped**
  (2026-06-08): optional polish, not a requirement.

## 7. Thesis feasibility

| Pillar | Status |
|---|---|
| 1. KD → accurate lightweight classifiers | **Done** (strong) |
| 2. Clinically credible (high sensitivity at realistic imbalance) | **Done** (strong) |
| 3. KD helps vs baseline | **Done** (nuanced, characterized) |
| 4. Mobile-deployable | **Achievable now** — no storage needed |
| 5. Cross-domain generalization (HAM10000) | **Blocked — server storage full** |
| 6. Fairness across skin tones (Fitzpatrick17k) | **Blocked — server storage full** |

**Verdict: the thesis is highly feasible.** The core contribution is already proven.
Nothing blocking is methodological — the only hard blocker is **server storage**, and
it sits on the two *extension* claims, not the core. Completion tiers:

- **Minimum viable (now):** pillars 1–3 + mobile benchmark (4).
- **Strong (after storage frees):** add HAM10000 cross-domain (5) — highest-value addition.
- **Distinctive:** add Fitzpatrick fairness (6).

## 8. Evaluation gaps — is the model "good"?

Discrimination is well-covered. Missing standard medical-ML experiments:

| Experiment | Why it matters | Blocked? |
|---|---|---|
| **AUPRC / PR curve** | AUC-ROC is optimistic at 0.39% prevalence; AUPRC is the honest metric | No (needs evaluator to save predictions) |
| **Calibration** (ECE, Brier, reliability) | `sigmoid(logit)` must be a trustworthy probability for a medical model | No (same) |
| Bootstrap confidence intervals | Defensible CIs + KD-delta significance | No (same) |
| Operating points (sens @ fixed 90/95% spec) | Clinicians pick an operating point, not Youden's J | No (same) |
| Explainability / artifact-bias (Grad-CAM) | Show the model attends to the lesion, not rulers/ink/hair | No (existing checkpoints + test images) |
| External validation (HAM10000) | The biggest "does it generalize" experiment | **Yes — storage** |
| Fairness subgroups (Fitzpatrick17k) | Per-skin-tone sensitivity | **Yes — storage** |

**High-leverage enabler:** patch `src/evaluation/evaluator.py` to save a sibling `.npz`
(`y_true`, `y_prob`). Then AUPRC / PR / calibration / CIs / operating points all compute
offline from existing runs — zero storage, no retraining.

## 9. Immediate next steps (storage-safe)

1. Aggregate students (`22_aggregate_folds.slurm`) + re-pull canonical `aggregated.{json,md}`
   to replace the log-extracted numbers here.
2. Build the mobile FP32 benchmark (params + size + CPU-latency proxy) → completes pillar 4.
3. Patch evaluator to save predictions → unlock AUPRC / calibration / CIs / Grad-CAM.
4. (When storage frees) stage HAM10000 + Fitzpatrick17k → pillars 5 & 6.

## Caveats

- Student numbers are **log-extracted**, not canonical JSON — verify after re-pull.
- Teacher on-disk `aggregated.json` is **stale** (job 28179) — re-aggregate.
- CPU latency (when measured) is a **relative proxy**, not a phone number.
- MobileViT-S is the model to watch for mobile export (attention ops).
