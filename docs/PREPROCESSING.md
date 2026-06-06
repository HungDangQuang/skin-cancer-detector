# Preprocessing & Augmentation Spec

Single source of truth reconciling the proposal (§2.2 data strategy, §3.5
augmentation) with the implemented pipeline. Where the proposal and a sound ML
choice disagree, this doc records the **corrected decision and why**, so the
proposal text and the code can be aligned to one spec instead of drifting.

Legend: ✅ implemented & kept · ⬜ proposed, not yet implemented · ⚠️ revise vs proposal · ❌ drop

Dataset facts this spec is designed around (from proposal): ISIC 2024 ≈ 401,059
images, **native ~128×128**, non-dermoscopic; **malignant ≈ 0.9%** (~3,600
positives); deployment domain = plain smartphone photos. PAD-UFES-20 ≈ 2,298
smartphone clinical images, added for extra malignant samples.

---

## 1. Cleaning & unification (offline, `process_isic2024` / `process_pad_ufes_20`)

| Step | Status | Decision |
|---|---|---|
| Decode HDF5 → RGB | ✅ | Keep. |
| Drop corrupt (decode fails) | ✅ | Keep — wrap decode in try/except; widen to catch PIL `DecompressionBombError` (not an `OSError`). |
| Drop blank / near-uniform (pixel variance) | ✅ | Keep — `is_uninformative()`: grayscale `std < 8.0` or `>97%` near-black/white. |
| Drop abnormally small crops (min-size) | ⬜ | **Add.** Proposal §2.2 calls for it; native sizes vary, and a tiny crop upscaled to 224 is pure blur. Suggest dropping images whose native min side `< 32 px` (tune on cluster). |
| Deduplicate (hash / patient_id) | ⬜ | **Add.** Proposal §2.2 calls for it. Use perceptual or exact hash; log duplicates. Prevents the same lesion in train+val. |
| Label unification (PAD 6→binary, HAM 7→binary) | ✅ | Keep. BCC/SCC/MEL→1; AK/NEV/SEK→0. |
| Resize 224×224 (LANCZOS) + ImageNet normalize | ✅ | Keep. **Note:** 128→224 is interpolation, not added detail — don't describe it as high-resolution. |

**Rare-class safety rule:** the quality filter (variance + min-size) must **log
every excluded id with its label** and must not be trusted to auto-drop
`malignant` samples without a human glance at the drop list. Each lost positive
is ~0.03% of all positives.

**ID namespacing:** when ISIC + PAD are concatenated, `patient_id` must be
namespaced (e.g. `pad_…`) so a PAD id cannot collide with an ISIC id and leak
across folds.

---

## 2. Splitting

✅ **Keep as-is.** Patient-level `StratifiedGroupKFold(K=5)`, grouped by
`patient_id`, stratified by `label`. 4 folds train / 1 fold val, rotated 5×.

**FIXED 2026-06-06.** `test_split.csv` is now an **independent held-out test set**:
`generate_group_kfold_splits` first carves a patient-disjoint, label-stratified
holdout (`1/test_holdout_splits` ≈ 17% with the default 6) and runs the 5-fold CV
on the *remaining* dev pool only. So every fold's model is evaluated on the same
data it never trained on → per-fold test metrics are unbiased and paired-comparable.
(Previously `test_split.csv` was fold 0's val set, which folds 1–4 trained on —
their test metrics were optimistically inflated, visible in teacher job 28060
where the clean fold 0 scored well below folds 1–4.)

---

## 3. Class-imbalance strategy — treat as ONE tunable system, not 3 stacked layers

Proposal stacks three corrections: 1:5 dynamic undersampling + Focal Loss
(γ=2, α=0.25) + stronger-augmentation-on-malignant. These are **not
orthogonal**, and as specified they risk over-correcting.

| Component | Status | Decision |
|---|---|---|
| Dynamic undersampling 1:5 (reshuffled per epoch) | ✅ | Keep the mechanism. Treat the **ratio as a hyperparameter**, not a constant. |
| Focal Loss γ=2 | ✅ | Keep. |
| Focal Loss **α=0.25** | ⚠️ | **Revisit.** α=0.25 was tuned (Lin et al. 2017) for a raw ~1000:1 stream *without* undersampling. After undersampling to 1:5 the stream is already ~16.7% positive; α=0.25 then down-weights positives further and can suppress the signal. Treat α **jointly with the ratio**; a cleaner default is α≈0.5 (or γ-only). |
| Stronger augmentation on malignant | ❌ | **Drop** (see §4). Asymmetric aug skews the positive class away from its test-time distribution — exactly the class whose recall matters. Get positive diversity from *more sampling*, not *harsher transforms*. |

**Required experiment (proposal methodology upgrade):** ablate
`undersampling_ratio × focal_α` (e.g. ratios {1:3, 1:5, raw} × α {0.25, 0.5})
on a fixed fold and report a small table. This both fixes the over-correction
risk and turns an assumption into a result.

---

## 4. Augmentation — corrected pipeline

Apply the **same** augmentation distribution to both classes. Train only;
val/test get Resize + Normalize + ToTensorV2 (✅ already correct).

### Keep (safe, domain-appropriate)
| Transform | Status | Note |
|---|---|---|
| HorizontalFlip / VerticalFlip | ✅ | p=0.5. |
| Rotation | ⚠️ | Code uses `RandomRotate90` + `ShiftScaleRotate(rotate_limit=45)`. Proposal wants 0–360°; lesions have no canonical orientation, so widen to **continuous full rotation** (`A.Rotate(limit=180)` or `rotate_limit=180`). |
| Scale ±20% / small shift | ✅ | `ShiftScaleRotate(scale_limit=0.2, shift_limit=0.1)`. |
| ColorJitter (bright/contrast/sat ±20%, hue ±10%) | ✅ | Matches proposal photometric group. |
| GaussianBlur | ✅ | Low p; simulates focus variance. |
| CLAHE | ⬜ | **Add, low p (~0.2).** Safe, simulates lighting variance on smartphones. |

### Drop or de-risk (proposed but problematic)
| Transform | Status | Reason → action |
|---|---|---|
| Microscope-style circular crop | ❌ | Simulates a **dermatoscope-lens vignette** absent from the smartphone deployment domain; the only vignetted data is **HAM10000, the cross-domain *test* set** — training for it conflates generalization with leakage. **Drop**, unless the Android app ships a clip-on lens (then low-p only, and disclose HAM is partly in-distribution). |
| CutOut / CoarseDropout | ❌→⚠️ | Can mask a small lesion entirely → a `malignant` label on a lesion-free image (label noise on the rare class). **Default off.** If added: bound size ≤ ¼ image and disable for malignant. |
| MixUp | ❌→⚠️ | (a) Same-label MixUp (as proposal phrases it) removes MixUp's between-class smoothing benefit. (b) In the **KD branch** the teacher soft-label target must be mixed identically to the input, or supervision is inconsistent. **Default off.** If added: cross-class, and mix teacher logits the same way. |
| Stronger aug on malignant | ❌ | Train/test skew on positives (see §3). |

---

## 5. Proposal text changes implied by this spec

To align the proposal §2.2/§3.5 with the corrected spec, the proposal should:
1. Add the **min-size filter** and **deduplication** to the cleaning steps (currently mentioned only briefly / partially).
2. Reframe imbalance handling as a **tuned system with an ablation** (ratio × α), not three fixed additive layers; change α=0.25 to "tuned jointly with the undersampling ratio."
3. **Remove** the microscope circular-crop, and either remove MixUp/CutOut or specify the safe constrained variants above.
4. State augmentation is **class-symmetric** (drop "stronger on malignant").
5. Specify rotation as **continuous 0–360°**.

## 6. Implementation checklist

- [x] `transforms.py`: widen rotation to full 0–360° (`rotate_limit=180`); add low-p CLAHE (`p=0.2`, before Normalize); aug kept class-symmetric. *(done 2026-06-04)*
- [x] `preprocessing.py`: min-size filter (`min_size=32`, fresh-decode only); exact-duplicate dedup (md5 of resized pixels, first kept); widened `except` to include `Image.DecompressionBombError`; PAD `patient_id` namespaced (`pad_…`) against cross-dataset GroupKFold collision. *(done 2026-06-04)*
- [x] Loss/config: `focal_alpha` (`training.loss.alpha`) and `undersample_ratio` (`data.undersample_ratio`) were **already** config-driven — sweepable via Hydra overrides, no change needed.
- [ ] Add the `ratio × α` ablation to the experiment plan.
- [x] fix the `test_split.csv` independence issue — independent patient-disjoint holdout carved before CV (`test_holdout_splits`, default 6). *(done 2026-06-06)*

### Known limitations of the implemented filters (verify on cluster)
- Dedup is **per-dataset** (`seen_hashes` resets between ISIC and PAD) and **exact-pixel only** — an ISIC↔PAD exact dup or a near-duplicate won't be caught. Intra-dataset exact dups (the main risk) are covered.
- `min_size` only applies on the **fresh decode**; an image already resized to 224 on a prior run can't be re-checked for native size.
- Thresholds (`min_size=32`, `std<8`, `0.97`) are untuned — confirm the `excluded_images.csv` per-label breakdown on the cluster before trusting them; never auto-drop malignant without a look.

> The α/ratio interaction (§3) remains an empirical claim to confirm via the
> cluster ablation, not an asserted fact.
