# External evaluation — cross-domain (HAM10000) & fairness (Fitzpatrick17k)

**Date:** 2026-08-23 (revised same day — see below) · **Box:** `vastnew`
(`/workspace/skin-cancer-detector`, 1×RTX 3090)
**Scope:** 19 trained run-dirs (3 teachers + 4 baselines + 12 KD students) × 5 folds, evaluated on
two datasets that were **never trained on** — **all five split variants**, plus post-hoc calibration
and bootstrap confidence intervals.

> **Revision note.** The first version of this report ran only HAM10000's `headline` split and a
> 23 %-coverage Fitzpatrick17k. Since then: both remaining HAM variants were evaluated (§3.4), a
> complete md5-verified Fitzpatrick17k was obtained (§2.1) and **§4 was rewritten from scratch on
> it**, calibration was added (§5), and every claim now carries a bootstrap interval (§6). Two
> conclusions changed materially — the fairness finding (§4.2) and the best-teacher claim (§4.1).

Raw artefacts: `reports/external/<dataset>/<variant>/<run>/fold_N/{test_metrics.json,predictions.csv,subgroup_metrics.json}`
plus `aggregated.{json,md}`, `kd_comparison.{md,json}`, `bootstrap_ci.{md,json}` and
`calibration_metrics*.json` per variant.

---

## 1. What was run

```bash
# --- data ---
bash run/download_external.sh DATASET=ham10000 RM_ZIP=1
# Fitzpatrick17k images come from the md5-verified Kaggle mirror, NOT the dead
# per-row URLs — see §2.1 for the verification and the credential handling.
bash run/prepare_external.sh  DATASET=ham10000
bash run/prepare_external.sh  DATASET=fitzpatrick17k SKIP_DOWNLOAD=1

# --- evaluation (all variants of both sets, 19 runs x 5 folds each) ---
bash run/evaluate_external.sh DATASET=ham10000       VARIANTS=all GPU=0
bash run/evaluate_external.sh DATASET=fitzpatrick17k VARIANTS=all GPU=0
python scripts/compare_kd_results.py --runs-dir reports/external/<ds>/<variant>

# --- analysis on the predictions that produced (no re-inference) ---
python scripts/compute_calibration.py --run-dir reports/external/<ds>/<variant>/<run>   # §5
bash run/bootstrap_ci.sh RESULTS_DIR=reports/external/<ds>/<variant> N_BOOT=2000        # §6

# --- mobile (CPU-only, independent of the above) ---
bash run/export_executorch.sh MODEL=mobilenetv4_conv_medium CKPT=<fold_4 ckpt>
bash run/check_pte_parity.sh  MODEL=mobilenetv4_conv_medium   # max|Δlogit| 5.53e-06 ✅
```

**The decision threshold is frozen**, taken from each run's own internal validation fold
(Youden's J over `val_predictions.csv`). Nothing was fitted on the external sets — those configs
declare `do_not_use_for: threshold_selection`. Ranking metrics (pAUC / AUC / AUPRC) are
threshold-free; sensitivity / specificity are what a deployed model would actually have produced.

**Leakage guards passed clean** for both datasets (`reports/external_overlap_check_*.md`): no
`ISIC_*` id intersection and no decoded-pixel md5 match against the internal held-out test split.

---

## 2. The two evaluation sets, as actually obtained

| Dataset | Obtained | Headline split | Malignant | Prevalence |
|---|---|---|---|---|
| HAM10000 (dermoscopy, cross-domain) | **10,015 / 10,015** images, md5-verified | 7,470 (one image per lesion) | 1,169 | 15.7 % |
| Fitzpatrick17k (clinical photos, fairness) | **16,574 / 16,577 (99.98 %)**, md5-verified | 4,320 (benign vs malignant) | 2,160 | 50.0 % |

> ✅ **The Fitzpatrick17k coverage problem is RESOLVED (2026-08-23).** The first pass could only
> fetch 3,887 / 16,577 (23.4 %) because `www.dermaamin.com` (12,631 rows, 76 %) now 404s on every
> image path. A complete mirror was found on Kaggle and verified byte-for-byte (§2.1), so the
> fairness analysis in §4 now runs on essentially the whole release. **All Fitzpatrick numbers in
> this report are the full-coverage ones**; the superseded 23 %-subset results are kept for the
> paper trail under `reports/_archive/fitzpatrick17k_subset23pct_20260823/`.
>
> What changed, and why it matters more than the row count suggests:
>
> | | 23 % subset | Full set |
> |---|---|---|
> | Headline split (benign vs malignant) | 1,043 | **4,320** |
> | Prevalence | 64.6 % | **50.0 %** |
> | Tone: dark / light / medium | 137 / 310 / 596 | **411 / 2,310 / 1,599** |
> | Dark-tone malignant cases | — | **208** (of 411) |
>
> The old subset was one atlas only, so its 64.6 % prevalence was an artefact of *which* atlas
> survived, not a property of Fitzpatrick17k. The dark-tone group tripled (137 → 411), which is the
> difference between "not measurable" and "measurable with a stated interval" for the fairness gap.
>
> Processing (`prepare_external.sh`): 16,574 raw → **16,012** usable after dropping 562 rows with an
> unknown Fitzpatrick scale (`-1`, the release's explicit unknown code — useless for a tone
> breakdown). Tier-1 integrity drops: **0**. Tier-2 quality flags (kept, not dropped, per the
> two-tier rule): 12. The leakage check against the internal splits re-ran and is **clean**.

### 2.1 How the complete set was obtained and verified (2026-08-23)

The HuggingFace mirrors are dead ends — `spycoder/fitzpatrick` is metadata-only and
`ZYXue/Fitzpatrick_17k` is a 5k-row VQA derivative. But the Kaggle dataset
**`mobaswiralfarabi/fitzpatrick17k-original`** (1.46 GB, CC0 as declared by the uploader)
passes every acceptance test that can be applied *without downloading it*:

| Criterion | Result |
|---|---|
| Ships actual image files | ✅ 16,574 `.jpg` under `finalfitz17k/` |
| Filenames map to the release `md5hash` | ✅ every name is `<32-hex>.jpg`; **16,574 / 16,577** official hashes present, **0 files not in the release** |
| Bytes are the original, not re-encoded | ✅ **3,887 / 3,887** — every image we independently downloaded from `atlasdermatologico.com.br` and md5-verified has a **byte-identical file size** in the mirror |
| Coverage of what we are missing | 3 rows absent, all `www.dermaamin.com` |

The byte-size test is nearly free and it is what justified spending the download at all: 3,887
independent re-encodings landing on the exact same byte count is not a thing that happens. Kaggle's
public API answers **unauthenticated for metadata**, so this is reusable for vetting any mirror
before committing to it:

```bash
# paginate on .nextPageTokenNullable (83 pages at pageSize=200)
curl -s "https://www.kaggle.com/api/v1/datasets/list/<owner>/<slug>?pageSize=200&pageToken=$TOK" \
  | jq -r '.datasetFiles[] | [.name, (.totalBytes|tostring)] | @tsv'
# then `join` those sizes against the images already on disk
```

**Then the real verification, on the downloaded bytes.** In this release the filename *is* the
content md5, so the check is exact and self-contained:

| Check | Result |
|---|---|
| Archive downloaded | 1,421,973,831 bytes, `http=200` |
| Files extracted | 16,574 `.jpg` |
| **`md5sum` == filename** | ✅ **16,574 / 16,574**, zero mismatches |
| Hashes present in the official `fitzpatrick17k.csv` | ✅ 16,574 / 16,577, **0 files not in the release** |
| Still missing | 3 rows, all `www.dermaamin.com` |

So the mirror is **byte-identical to the original release**, not a re-encode. Provenance is recorded
in `data/raw/fitzpatrick17k/download_log.csv` (`status=ok, reason=kaggle_mirror_md5_verified`), and
the pre-mirror 23 %-coverage manifests are kept as `*_subset23pct.csv.bak` beside it.

Credential handling, per the project's hard rule: the token lives **inside the repo** at
`.kaggle/kaggle.json` (`chmod 600`, already covered by `.gitignore`), never in `$HOME`. The download
used `curl -K .kaggle/curlrc` so the key never appears in a process argument list.

⚠️ The uploader's CC0 tag is **not** authoritative for the underlying atlas images — cite the
original Fitzpatrick17k release terms, not the Kaggle license field.

---

## 3. HAM10000 — cross-domain results (headline split, 7,470 images)

Ranked by pAUC@TPR≥80 (mean ± std over 5 folds).

| run | folds | pAUC@TPR80 | AUC-ROC | AUPRC | Sens | Spec |
|---|---|---|---|---|---|---|
| `kd_maxvit_base_to_fastvit_sa12` | 5 | **0.1148 ± 0.0141** | 0.8333 ± 0.0516 | 0.4572 ± 0.1036 | 0.9921 | 0.192 |
| `kd_convnextv2_base_to_fastvit_sa12` | 5 | 0.1083 ± 0.0043 | 0.8304 ± 0.0175 | 0.4625 ± 0.0541 | 0.9875 | 0.210 |
| `kd_efficientnetv2_m_to_fastvit_sa12` | 5 | 0.1069 ± 0.0198 | **0.8333 ± 0.0412** | 0.4797 ± 0.0673 | 0.9904 | 0.141 |
| `teacher/maxvit_base` | 5 | 0.1036 ± 0.0140 | 0.8233 ± 0.0470 | **0.4856 ± 0.1025** | 0.9916 | 0.141 |
| `kd_maxvit_base_to_efficientformerv2_s2` | 5 | 0.1028 ± 0.0146 | 0.8298 ± 0.0351 | 0.4841 ± 0.0812 | 0.9894 | 0.103 |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 5 | 0.1028 ± 0.0169 | 0.8211 ± 0.0354 | 0.4467 ± 0.0589 | 0.9784 | 0.222 |
| `baseline_efficientformerv2_s2` | 5 | 0.0996 ± 0.0118 | 0.8227 ± 0.0198 | 0.4533 ± 0.0237 | 0.9879 | 0.145 |
| `kd_convnextv2_base_to_efficientformerv2_s2` | 3 | 0.0985 ± 0.0128 | 0.8218 ± 0.0200 | 0.4619 ± 0.0279 | 0.9929 | 0.129 |
| `teacher/efficientnetv2_m` | 5 | 0.0967 ± 0.0163 | 0.8212 ± 0.0282 | 0.4761 ± 0.0451 | 0.9706 | 0.234 |
| `kd_efficientnetv2_m_to_efficientformerv2_s2` | 5 | 0.0964 ± 0.0199 | 0.8148 ± 0.0465 | 0.4593 ± 0.0822 | 0.9932 | 0.141 |
| `kd_convnextv2_base_to_mobilenetv4_conv_medium` | 5 | 0.0964 ± 0.0051 | 0.8065 ± 0.0092 | 0.4198 ± 0.0341 | 0.9896 | 0.171 |
| `baseline_fastvit_sa12` | 5 | 0.0933 ± 0.0227 | 0.8027 ± 0.0449 | 0.4346 ± 0.0656 | 0.9920 | 0.091 |
| `kd_maxvit_base_to_mobilenetv4_conv_medium` | 5 | 0.0920 ± 0.0181 | 0.7820 ± 0.0765 | 0.3958 ± 0.1257 | 0.9760 | 0.208 |
| `baseline_mobilenetv4_conv_medium` | 5 | 0.0915 ± 0.0147 | 0.7856 ± 0.0358 | 0.3754 ± 0.0408 | 0.9784 | 0.203 |
| `kd_efficientnetv2_m_to_repvit_m1_0` | 5 | 0.0903 ± 0.0181 | 0.7763 ± 0.0576 | 0.3665 ± 0.0819 | 0.9879 | 0.138 |
| `kd_maxvit_base_to_repvit_m1_0` | 5 | 0.0855 ± 0.0058 | 0.7644 ± 0.0313 | 0.3493 ± 0.0521 | 0.9868 | 0.107 |
| `kd_convnextv2_base_to_repvit_m1_0` | 5 | 0.0826 ± 0.0209 | 0.7691 ± 0.0460 | 0.3669 ± 0.0434 | 0.9719 | 0.182 |
| `baseline_repvit_m1_0` | 5 | 0.0798 ± 0.0086 | 0.7565 ± 0.0168 | 0.3347 ± 0.0274 | 0.9897 | 0.085 |
| `teacher/convnextv2_base` | 5 | 0.0772 ± 0.0231 | 0.7900 ± 0.0467 | 0.4547 ± 0.0645 | 0.9701 | 0.193 |

### 3.1 Did KD survive the domain shift? **Yes.**

`scripts/compare_kd_results.py` on `reports/external/ham10000/headline`:

- **AUPRC: KD improved 12/12 student pairs** (mean Δ = **+0.0297**) → HELPS
- **pAUC@TPR80: KD improved 10/12** (mean Δ = +0.0071) → HELPS
- Best KD effect: `efficientnetv2_m → mobilenetv4_conv_medium` (ΔAUPRC **+0.0713**, ΔpAUC +0.0113)
- Best absolute pair: `maxvit_base → efficientformerv2_s2` (AUPRC 0.4841)

This is a stronger claim than the in-domain result: in-domain the KD deltas were partly inside
fold noise, whereas out-of-domain KD improves **every** student on AUPRC. Distillation is buying
generalization, not just fitting the ISIC test split better.

### 3.2 The operating point does NOT transfer — and re-thresholding does not rescue it

| | in-domain (ISIC+PAD test, prevalence 0.39 %) | HAM10000 (prevalence 15.7 %) |
|---|---|---|
| `kd_efficientnetv2_m_to_fastvit_sa12` | pAUC 0.1853 · AUC 0.9846 · Sens 0.930 · **Spec 0.962** | pAUC 0.1069 · AUC 0.8333 · Sens 0.990 · **Spec 0.141** |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | pAUC 0.1859 · AUC 0.9852 · Sens 0.933 · **Spec 0.953** | pAUC 0.1028 · AUC 0.8211 · Sens 0.978 · **Spec 0.222** |

At the frozen threshold the models flag nearly everything (Sens ≈ 0.98–0.99, Spec ≈ 0.10–0.23).
That number alone is ambiguous: it could be pure prior shift (threshold picked at 0.39 %
prevalence, applied at 15.7 %), which a re-calibration would fix.

**It is not.** The threshold-free fixed-specificity operating points — already recorded in every
`test_metrics.json` as `sens_at_90spec` / `sens_at_95spec` — show what the model can do when the
threshold *is* allowed to move to the target domain:

Fitzpatrick figures below are the **full-coverage** ones (§2.1), with bootstrap CIs.

| run | in-domain Sens@95Spec | HAM Sens@**90**Spec | HAM Sens@95Spec | Fitz Sens@90Spec (95 % CI) |
|---|---|---|---|---|
| `kd_efficientnetv2_m_to_fastvit_sa12` | 0.934 ± 0.008 | **0.508 ± 0.081** | 0.335 ± 0.063 | 0.221 [0.200, 0.239] |
| `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 0.930 ± 0.010 | 0.463 ± 0.085 | 0.298 ± 0.072 | 0.194 [0.175, 0.213] |
| `teacher/efficientnetv2_m` | 0.912 ± 0.009 | 0.498 ± 0.053 | 0.330 ± 0.045 | 0.285 [0.263, 0.307] |
| `baseline_fastvit_sa12` | 0.923 ± 0.011 | 0.435 ± 0.074 | 0.291 ± 0.058 | 0.208 [0.188, 0.227] |

Best across all 19 runs: HAM Sens@90Spec 0.508, Sens@95Spec 0.336; Fitzpatrick Sens@90Spec
**0.314 [0.289, 0.335]** (`teacher/convnextv2_base`), best student 0.264 [0.241, 0.288]. Note 90 %
specificity is a **looser** requirement than the 95 % used in-domain, so the real gap is wider than
the columns suggest.

So there are two effects and both are real:

1. **Domain shift (capability loss)** — AUC 0.98 → 0.82, pAUC 0.185 → 0.107, and at a sane
   operating point sensitivity falls from ~0.92 to ~0.46–0.51 (HAM) / ~0.19–0.31 (Fitzpatrick).
   Recalibration cannot recover this; it is a ranking-quality loss.
2. **Prior shift (presentation)** — on top of that, the frozen threshold is mismatched, which is
   what turns "moderate ranking" into "flags everything". `scripts/compute_calibration.py` fixes
   the *displayed probability* and the reliability diagram, **not** the sensitivity ceiling above.

Report `sens_at_90spec` / `sens_at_95spec` as the honest deployment numbers; quote AUC/pAUC/AUPRC
for capability comparison between models.

### 3.2b KD also helps at the fixed operating point

Δ `sens_at_90spec` (KD − matching baseline), 12 teacher→student pairs:

- **HAM10000: KD improves 11/12, mean Δ +0.0318** (best `efficientnetv2_m → mobilenetv4_conv_medium`
  **+0.0932 [+0.0758, +0.1139]**, i.e. 0.370 → 0.463 sensitivity at 90 % specificity). 7/12 pairs
  have a paired CI excluding zero.
- **Fitzpatrick17k (full coverage): KD improves 11/12, mean Δ +0.0243**, with **9/12** paired CIs
  excluding zero — a higher significant count than on HAM despite the smaller mean, because the
  4,320-row set is less noisy per model than the class-imbalanced HAM split.

This is the most decision-relevant KD result in the whole study: the gain survives *both* the
domain shift and the removal of the threshold artifact, on both external sets.

### 3.3 Per-diagnosis breakdown (`subgroup_metrics.json`, frozen threshold)

`kd_maxvit_base_to_fastvit_sa12` — recall on malignant classes / specificity on benign classes:

| dx | n | metric | value |
|---|---|---|---|
| mel (melanoma) | 614 | recall | 0.992 ± 0.007 |
| bcc | 327 | recall | 0.991 ± 0.006 |
| akiec | 228 | recall | 0.995 ± 0.004 |
| nv (nevus) | 5,403 | specificity | 0.216 ± 0.050 |
| bkl (benign keratosis) | 727 | specificity | 0.028 ± 0.015 |
| df (dermatofibroma) | 73 | specificity | 0.003 ± 0.006 |
| vasc | 98 | specificity | 0.216 ± 0.056 |

Melanoma recall > 99 % is reassuring, but at this threshold it is bought with a near-total loss of
specificity — **benign keratosis and dermatofibroma are essentially always flagged**. Those two
classes do not exist as separate labels in the training data, so the model has never been asked to
separate them from malignancy; that, plus the prior shift, is the mechanism.

### 3.4 The KD verdict holds across all three HAM10000 split variants (added 2026-08-23)

All 19 runs × 5 folds were re-evaluated on the two remaining variants, so the headline result can
be checked against the two obvious objections to it.

| Variant | Images | Malignant | Prevalence | KD on AUPRC | KD on pAUC | Best pair (AUPRC) |
|---|---|---|---|---|---|---|
| `headline` (1 image / lesion) | 7,470 | 1,169 | 15.6 % | **12/12**, Δ +0.0297 | 10/12, Δ +0.0071 | maxvit→efficientformerv2_s2, 0.4841 |
| `full` (every photograph) | 10,015 | 1,954 | 19.5 % | **12/12**, Δ +0.0298 | 10/12, Δ +0.0063 | maxvit→efficientformerv2_s2, 0.4971 |
| `no_akiec` (drops actinic keratosis) | 7,242 | 941 | 13.0 % | **12/12**, Δ +0.0267 | 11/12, Δ +0.0074 | efficientnetv2_m→fastvit_sa12, 0.4323 |

**Nothing flips.** KD improves AUPRC on 12/12 student pairs in every variant, with a delta that
barely moves (+0.027 … +0.030), and `efficientnetv2_m → mobilenetv4_conv_medium` is the strongest
KD effect in all three (ΔAUPRC +0.0713 / +0.0654 / +0.0636). Two specific objections are therefore
answered:

- **"The result is an artefact of counting akiec as malignant."** No — dropping akiec removes 228
  positives (1,169 → 941) and the verdict is unchanged; pAUC even improves to 11/12.
- **"It only holds on the de-duplicated split."** No — `full` reproduces it exactly.

⚠️ **Do not read the raw AUPRC column as a ranking across variants.** AUPRC's random baseline *is*
the prevalence, and prevalence differs per variant by construction. Lift over baseline:
`full` 0.4971/0.195 = **2.5×**, `headline` 0.4841/0.156 = **3.1×**, `no_akiec` 0.4323/0.130 = **3.3×**.
So `no_akiec`'s lower absolute AUPRC is the *best* relative performance of the three — the opposite
of what the raw number suggests.

⚠️ **`full` is for literature comparison only.** It contains repeat photographs of the same lesion,
so its rows are **not independent**; any CI computed from it is optimistic and it must not be used
as the headline.

---

## 4. Fitzpatrick17k — fairness analysis (4,320 images, 99.98 % coverage)

Rewritten 2026-08-23 on the **full** image set (§2.1). The previous version of this section used the
23 % atlas subset and is superseded; it survives at
`reports/_archive/fitzpatrick17k_subset23pct_20260823/`.

Headline split: 4,320 clinical photos, 2,160 malignant (**50.0 %**), tone groups
dark 411 / light 2,310 / medium 1,599. Ranked by AUC, with bootstrap CIs (B = 2000):

| run | AUC-ROC | AUPRC |
|---|---|---|
| `teacher/convnextv2_base` | **0.7039 [0.6904, 0.7179]** | **0.6920 [0.6742, 0.7111]** |
| `teacher/efficientnetv2_m` | 0.6777 [0.6645, 0.6913] | 0.6730 [0.6548, 0.6925] |
| `teacher/maxvit_base` | 0.6759 [0.6618, 0.6901] | 0.6735 [0.6552, 0.6948] |
| `kd_maxvit_base_to_fastvit_sa12` | 0.6726 [0.6575, 0.6873] | 0.6623 [0.6436, 0.6840] |
| `kd_convnextv2_base_to_efficientformerv2_s2` | 0.6724 [0.6581, 0.6871] | 0.6598 [0.6410, 0.6796] |
| `kd_maxvit_base_to_efficientformerv2_s2` | 0.6709 [0.6561, 0.6858] | 0.6608 [0.6415, 0.6819] |
| `baseline_efficientformerv2_s2` | 0.6601 [0.6457, 0.6752] | 0.6409 [0.6219, 0.6612] |

**Teachers still lead, and now the CIs prove it**: `teacher/convnextv2_base` [0.6904, 0.7179] does
not overlap the best student [0.6575, 0.6873]. On clinical photographs the mobile student is *not*
"as good as the teacher" — unlike on HAM10000, where students beat the teachers. Worth one sentence
in the discussion: the capacity gap that KD closes in-domain reopens under this domain shift.

### 4.1 The KD effect on clinical photos depends on WHICH teacher

Aggregate verdicts: headline AUPRC 10/12 (Δ +0.0158), pAUC 8/12 (Δ +0.0011); with non-neoplastic
merged, AUPRC 8/12 (Δ +0.0162), pAUC 10/12 (Δ +0.0036). But the paired CIs (§6) show the average
hides a clean split by teacher — AUPRC, headline split:

| Teacher | Students with CI excluding 0 (AUPRC) | Note |
|---|---|---|
| `convnextv2_base` | **4 / 4 positive** | also 3/4 positive on AUC |
| `maxvit_base` | **4 / 4 positive** | also 4/4 positive on AUC |
| `efficientnetv2_m` | **0 / 4** | and **2/4 significantly NEGATIVE on AUC** (mobilenetv4 −0.0067 [−0.0132, −0.0001], repvit −0.0090 [−0.0173, −0.0007]) |

This is the sharpest result of the whole external evaluation, because it reverses the in-domain
ranking: **`efficientnetv2_m` is the best teacher on HAM10000 (ΔAUPRC +0.0713) and the worst on
Fitzpatrick, where it actively hurts two of its four students.** So "which teacher is best" has no
domain-free answer, and a teacher picked on dermoscopy can transfer *negatively* to clinical photos.
`maxvit_base → repvit_m1_0` is the best KD effect here (ΔAUPRC +0.0392 [+0.0304, +0.0481]).

### 4.2 Per-tone performance — the gap is light vs **medium**, not light vs dark

Mean AUC over all 19 runs, with the paired-bootstrap gap CIs (§6, gaps bootstrapped directly):

| Tone group | n (per fold) | Mean AUC over 19 runs |
|---|---|---|
| light (Fitzpatrick I–II) | 2,310 | **0.6755** |
| dark (V–VI) | 411 | 0.6469 |
| medium (III–IV) | 1,599 | **0.6284** |

| Gap | Mean | CI excludes 0 | Verdict |
|---|---|---|---|
| **light − medium** | +0.0471 AUC / +0.0895 AUPRC | **19 / 19 runs** (both metrics) | **Real and universal** |
| dark − light | −0.0286 AUC / −0.0318 AUPRC | 4 / 19 (AUC), 1 / 19 (AUPRC) | Directional, mostly unresolved |
| dark − medium | +0.0185 AUC / +0.0577 AUPRC | 0 / 19 (AUC), 1 / 19 (AUPRC) | Not resolved |

**Three things follow, and the first is the one that would have been missed.**

1. **The disparity is not monotone in skin tone.** Performance is worst on **medium** (III–IV), not
   on the darkest group. Every one of the 19 runs is significantly better on light than on medium;
   no run is significantly worse on dark than on medium. A "model does worse as skin gets darker"
   narrative would be *wrong* on this evidence, and the old subset — where medium and dark were
   596 and 137 images — could not have detected it.
2. **The light−dark gap is directionally present but individually unresolved.** The mean is
   −0.029 AUC (light better) and only 4 of 19 runs have an interval excluding zero. Tripling the
   dark group (137 → 411) sharpened this from "not measurable at all" to "small, consistently
   signed, mostly not significant per run" — state it that way, with the interval, rather than
   claiming either a gap or fairness.
3. **This is a ranking statement only.** See §4.3 — specificity is ~0 at the frozen threshold, so
   AUC/AUPRC are the only columns carrying information.

### 4.3 Why specificity collapses entirely on this set

Fitzpatrick17k photos are wide-field clinical images (whole limb/face) at **50.0 %** malignant
prevalence in the headline split, versus lesion-centered crops at 0.39 % in training. Sens ≈ 0.99
with Spec ≈ 0 is the arithmetic consequence of applying an ISIC-calibrated threshold to that
distribution. It is *not* an additional finding about fairness, and it is not fixed by calibration
(§5).

## 5. Calibration of the displayed probability (added 2026-08-23)

Post-hoc only: no retraining, no re-inference. **Ranking metrics are unchanged** — pAUC / AUPRC /
AUC are invariant to any monotone rescaling, so nothing in §3, §4 or Chapter 4 moves. This section
is about whether a shown "% risk" is honest, and nothing else.

Run with `scripts/compute_calibration.py --run-dir reports/external/<ds>/headline/<run>`
(mean over 5 folds; `--method platt` additionally needs the run's own internal
`val_predictions.csv`, copied in from `experiments/runs/<run>/fold_N/`).

| Dataset | Run | ECE raw | ECE prior-shift | ECE Platt | Brier raw | Brier Platt |
|---|---|---|---|---|---|---|
| HAM10000 | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 0.3019 | 0.2884 | **0.0594** | 0.2180 | 0.1150 |
| HAM10000 | `baseline_mobilenetv4_conv_medium` | 0.3686 | 0.3552 | **0.0823** | 0.2697 | 0.1321 |
| HAM10000 | `teacher/efficientnetv2_m` | 0.2887 | 0.2744 | **0.0588** | 0.2019 | 0.1118 |
| Fitzpatrick17k | `kd_efficientnetv2_m_to_mobilenetv4_conv_medium` | 0.2052 | 0.4079 | **0.1817** | 0.2823 | 0.2778 |
| Fitzpatrick17k | `baseline_mobilenetv4_conv_medium` | 0.2860 | 0.4372 | **0.2031** | 0.3230 | 0.2894 |
| Fitzpatrick17k | `teacher/efficientnetv2_m` | **0.1360** | 0.3694 | 0.2088 | 0.2475 | 0.2768 |

Four things fall out, and the second is the one that is easy to get wrong:

1. **On HAM10000, Platt scaling cuts ECE ~5×** (0.302 → 0.059 for the deployable student). The
   displayed probability becomes usable; the decision quality does not change.
2. **Prior-shift is almost a no-op on HAM10000 — by arithmetic, not by failure.** The correction is
   `logit(π_target) − logit(π_train)`, and here π_target = 0.1565 (HAM's own prevalence) against
   π_train = 1/(1+5) = 0.1667 from the undersampler. Those are nearly equal, so the shift is ≈ 0.
   Prior-shift is the right tool for the *internal* 0.39 %-prevalence test set; it is the wrong tool
   for HAM, and reporting "calibration barely helped" from it would be a misreading.
3. **Prior-shift is actively harmful on Fitzpatrick** (0.205 → 0.408; 0.286 → 0.437; 0.136 → 0.369 —
   it roughly *doubles* ECE on all three runs). At 50 % prevalence the shift
   `logit(0.50) − logit(0.167)` pushes every probability sharply up, on a model that is already
   over-confident. Platt helps the two students (0.205 → 0.182, 0.286 → 0.203) but **hurts the
   teacher** (0.136 → 0.209), because the teacher's raw output happened to sit closest to this set's
   prior. **A calibrator is only valid for the prevalence it was fitted against** — there is no
   dataset-independent "calibrated model", and the right correction differs per model *and* per
   deployment domain.
4. **Which correction wins is not knowable from the training data alone.** The three datasets
   (internal 0.39 %, HAM 15.6 %, Fitzpatrick 50.0 %) each need a different answer: prior-shift,
   Platt, and "it depends on the model" respectively. Any deployment must therefore state the
   prevalence it assumes, and the app should expose that assumption rather than hard-coding one
   logit shift.

Bonus KD finding: the **KD student is better calibrated than its own baseline** before any
correction — ECE 0.302 vs 0.369 on HAM, 0.205 vs 0.286 on Fitzpatrick.

Per-tone ECE on Fitzpatrick (KD student, raw): dark 0.205, light 0.187, medium 0.230 — the same
ordering as the AUC gaps in §4.2 (medium worst), and notably **uniform**: miscalibration is not
concentrated on the dark-tone group.

> **This is a presentation fix, not a performance fix.** §3.2 shows sensitivity at 90 % specificity
> is ~0.46–0.51 on HAM, and §4.3 that specificity is ~0 on Fitzpatrick at the frozen threshold. No
> threshold or calibration change lifts those ceilings. Artefacts:
> `calibration_metrics.json` + `reliability_curve.png` (prior-shift) and
> `calibration_metrics_platt.json` + `reliability_curve_platt.png` per run-dir.

---

## 6. Bootstrap confidence intervals (added 2026-08-23)

Everything above is `mean ± std over 5 folds` — the spread between the five *models*, which says
nothing about the sampling error of the test set and therefore cannot settle "is this gap real?".
`scripts/bootstrap_ci.py` (`run/bootstrap_ci.sh RESULTS_DIR=…`) resamples the test **rows** out of
the existing `predictions.csv` files: B = 2000, seed 42, no re-inference.

**Fold convention (applied everywhere):** one row-index draw per replicate, applied to **all five
folds**, then averaged. The folds are five models scored on the *same* rows, so pooling their
predictions would replicate every row 5× and shrink the interval by ~√5 into fiction.

### 6.1 The KD claim, restated as an effect size

Both arms are resampled on **identical rows**, so the delta is *paired*. This matters concretely:
`kd_convnextv2_base_to_mobilenetv4` AUPRC 0.4198 [0.3959, 0.4440] and its baseline
0.3754 [0.3578, 0.3996] **overlap** — read separately they look inconclusive — yet the paired delta
is **+0.0445 [+0.0350, +0.0547]**, decisively non-zero. An unpaired interval throws away the
correlation and would have understated the evidence.

On HAM10000 headline, of the 12 KD pairs:

| Metric | CI excludes 0, positive | CI excludes 0, **negative** | inconclusive |
|---|---|---|---|
| AUPRC | **10 / 12** | 0 | 2 |
| AUC-ROC | 9 / 12 | **1** | 2 |
| pAUC@TPR80 | 9 / 12 | **1** | 2 |
| Sens@90 %Spec | 7 / 12 | 0 | 5 |

Headline effect, the deployable pair `efficientnetv2_m → mobilenetv4_conv_medium`:

| Metric | Paired Δ (KD − baseline) |
|---|---|
| AUPRC | **+0.0713 [+0.0598, +0.0819]** |
| AUC-ROC | +0.0355 [+0.0303, +0.0403] |
| pAUC@TPR80 | +0.0113 [+0.0083, +0.0142] |
| Sens@90 %Spec | **+0.0932 [+0.0758, +0.1139]** |

**"ΔAUPRC +0.071 [+0.060, +0.082]" is the sentence to put in the thesis** — an effect size with an
interval, not the tally "KD won 12/12".

**Two honest negatives the win-count was hiding.** `kd_efficientnetv2_m_to_efficientformerv2_s2` is
significantly **worse** than its baseline on AUC (−0.0079 [−0.0129, −0.0028]) and on pAUC
(−0.0032 [−0.0062, −0.0002]), with AUPRC inconclusive (+0.0060 [−0.0054, +0.0177]). Both
inconclusive AUPRC rows are `efficientformerv2_s2`, which has the strongest baseline of the four
students (AUPRC 0.4533) — KD has the least headroom exactly where the student is already good.
So the correct claim is **"KD helps most students, and its benefit shrinks toward zero (and can
reverse) as the baseline student gets stronger"**, not "KD always helps".

⚠️ `kd_convnextv2_base_to_efficientformerv2_s2` has only **3 folds**; the output marks it `3 ⚠`.
Do not quote its interval as a 5-fold result.

Artefacts: `<tree>/bootstrap_ci.{json,md}` for all three HAM variants and both Fitzpatrick variants.

---

## 7. What this changes

1. **KD's headline claim is now an effect size, not a tally.** On HAM10000 the deployable pair
   improves AUPRC by **+0.0713 [+0.0598, +0.0819]** (paired bootstrap, §6.1), and the verdict is
   unchanged across all three split variants (§3.4). That is a far stronger thesis sentence than
   "KD won 12/12", and it survives the two obvious objections to the headline split.
2. **But KD is not universally beneficial, and the report now says where it isn't.** Two pairs on
   HAM10000 are inconclusive on AUPRC and one is significantly *worse* on AUC — both involve
   `efficientformerv2_s2`, the strongest baseline student. KD's benefit shrinks toward zero as the
   student gets stronger.
3. **The best teacher is domain-dependent — this is the sharpest new result.** `efficientnetv2_m`
   gives the largest KD gain on HAM10000 (+0.0713 AUPRC) yet on Fitzpatrick it helps **0/4**
   students and significantly *hurts* 2/4 on AUC, while `convnextv2_base` and `maxvit_base` are
   4/4 positive there (§4.1). A teacher selected on dermoscopy can transfer negatively to clinical
   photographs, so teacher choice must be justified against the *deployment* domain.
4. **The fairness finding changed shape once coverage was fixed.** At 99.98 % coverage the
   reproducible disparity is **light vs medium** (19/19 runs, mean +0.047 AUC), not light vs dark
   (4/19, mean +0.029). Performance is worst on Fitzpatrick III–IV, *not* on the darkest group — so
   a "worse as skin gets darker" narrative is not supported. The light−dark gap is consistently
   signed but individually unresolved; quote the interval, claim neither a gap nor a clearance.
5. **Deployment: recalibration is necessary, NOT sufficient, and not transferable.** Each domain
   needs a different correction (prior-shift internally, Platt on HAM, model-dependent on
   Fitzpatrick — §5), so the app must state the prevalence it assumes rather than hard-code one
   logit shift. And no correction lifts the ceiling: sensitivity at 90 % specificity is ~0.46–0.51
   on HAM (§3.2) and specificity ≈ 0 on Fitzpatrick (§4.3). Scope every deployment claim to the
   training domain.
6. **Teachers beat students out of domain on Fitzpatrick** — `teacher/convnextv2_base`
   [0.6904, 0.7179] vs the best student [0.6575, 0.6873], non-overlapping — while students win on
   HAM10000. The capacity gap KD closes in-domain reopens under domain shift.
7. **The mobile path is unblocked.** The first `.pte` exists and PyTorch↔ExecuTorch parity is
   confirmed at `max|Δlogit|` 5.53e-06 (`docs/BENCHMARK_AND_RESULTS.md` GAP-6). On-device latency,
   memory, and preprocessing parity still require a physical handset.

---

## 8. Reproducing / extending

- Everything is recomputable offline from `predictions.csv` (`y_true,y_prob,y_pred,source,image_id,dx|tone_group,…`)
  — PR curves, bootstrap CIs, per-subgroup slices, alternative thresholds. No re-inference needed.
- New code this round: **`scripts/bootstrap_ci.py` + `run/bootstrap_ci.sh`** (per-run CIs, paired KD
  deltas, paired fairness gaps) and **`scripts/check_pte_parity.py` + `run/check_pte_parity.sh`**
  (PyTorch ↔ `.pte` gate). Earlier: `scripts/download_ham10000.py`, `scripts/evaluate_external.py`,
  `run/download_external.sh`, `run/evaluate_external.sh`.
- Superseded artefacts are kept, not deleted: `reports/_archive/fitzpatrick17k_subset23pct_20260823/`
  and `data/raw/fitzpatrick17k/*_subset23pct.csv.bak`.

### Still open

1. **On-device measurement** — latency, peak RAM, and preprocessing parity (layer 2) need a physical
   Android device; the ExecuTorch AAR must pin **1.4.1** to match `./.venv-export`.
2. **3 Fitzpatrick images remain missing** (all `dermaamin.com`, absent from the mirror too) —
   16,574 / 16,577 is the practical ceiling without contacting the authors.
3. **The teacher×domain interaction (§4.1) deserves its own experiment.** It was found post-hoc in
   the CIs; confirming *why* `efficientnetv2_m` transfers badly to clinical photos (backbone prior?
   dermoscopy-specific texture reliance?) would be a genuine thesis contribution rather than an
   observation.
