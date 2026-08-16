# Preprocessing & Augmentation Spec

Single source of truth reconciling the proposal (§2.2 data strategy, §3.5
augmentation) with the implemented pipeline. Where the proposal and a sound ML
choice disagree, this doc records the **corrected decision and why**, so the
proposal text and the code can be aligned to one spec instead of drifting.

Legend: ✅ implemented & kept · ⬜ proposed, not yet implemented · ⚠️ revise vs proposal · ❌ drop

Dataset facts this spec is designed around: ISIC 2024 ≈ 401,059 images, **native
~128×128**, non-dermoscopic; deployment domain = plain smartphone photos.
PAD-UFES-20 ≈ 2,298 smartphone clinical images, added for extra malignant samples.

**Prevalence — quote the measured figure, not the proposal's.** The proposal's
"malignant ≈ 0.9% (~3,600 positives)" is an ~9× overcount and must not be cited.
Measured in this project: processed **ISIC-only ≈ 0.098%** positive; after merging
PAD-UFES-20 the independent, patient-disjoint held-out **test set ≈ 0.39%**
(241 malignant / 61,831 benign — job 28250 logs, confirmed). **Report 0.39% as the
working prevalence, on the combined ISIC 2024 + PAD-UFES-20 test set** — this is the
number all headline-metric choices (AUPRC over AUC-ROC) are justified against.

**Obtaining the raw data.** ISIC 2024 → Kaggle (`train-image.hdf5` +
`train-metadata.csv`). PAD-UFES-20 → Mendeley `zr7vgbcyr2` v1; stage it with
`bash scripts/setup_pad_ufes_20.sh <bundle.zip>`, which extracts the nested
`imgs_part_*.zip` and writes `data/raw/pad_ufes_20/{metadata.csv, images/}`.
PAD is **optional**: `prepare_data.py` concatenates it only if that dir exists,
else it runs ISIC-only. See [run/README.md](../run/README.md) for the cluster steps.

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

### 1.1 External test sets (HAM10000 / Fitzpatrick17k) — two-tier filter policy

`process_ham10000` / `process_fitzpatrick17k` (same file) prepare the two
**evaluation-only** datasets. They are never trained on, which inverts the logic
above: for a training set, dropping a bad image improves the signal; for a test
set, **every dropped image silently changes the benchmark**. So filtering runs in
two tiers:

| Tier | What | Action | Log |
|---|---|---|---|
| 1 — integrity | unreadable / corrupt / decode bomb / native side `< 32 px` / missing file / dead-link payload | **DROP** (not a valid model input at all) | `data/processed/<ds>/excluded_images.csv` |
| 2 — quality | `is_uninformative`, exact-pixel duplicate | **KEEP + flag** | `data/processed/<ds>/quality_flags.csv` + a `quality_flags` column in the split CSV |

Reporting both the full and the flag-filtered subset is what shows the verdict
does not depend on the filter.

**Why tier 2 never drops:** `is_uninformative`'s thresholds were calibrated on
ISIC dermoscopy tiles. A flat clinical photograph of uniform skin can trip
`std < 8.0` — and how flat a photo reads is not independent of skin tone, so
auto-dropping would bias the *fairness* numbers by the very variable being
measured.

**Geometry stays squashed.** External images are resized to `224×224` without
preserving aspect ratio, exactly like `process_isic2024` / `process_pad_ufes_20`.
HAM10000 is 4:3, so a center-crop would be tempting — but it would stack a
*preprocessing* difference on top of the *domain* difference being measured, and
the two could not be told apart afterwards.

**Per-dataset specifics:**

- **HAM10000** — several photographs share one `lesion_id`, and md5 dedup cannot
  catch them (different shots = different pixels). `is_lesion_representative`
  marks the first image per lesion by sorted `image_id` (deterministic), and the
  headline split uses only those; treating all shots as independent would shrink
  confidence intervals artificially. `dx` is carried through so the
  `akiec → malignant` convention can be re-tested without reprocessing.
- **Fitzpatrick17k** — the release ships **URLs, not images**
  (`scripts/download_fitzpatrick17k.py` fetches them). Validation is
  `HTTP 200 → Content-Type: image/* → PIL decode → md5 matches the metadata
  column`; the md5 layer is what reliably catches a dead link whose HTML error
  page was saved as a `.jpg`. Rows with `fitzpatrick_scale = -1` (unknown tone)
  are dropped at prepare time. **The download success rate is a coverage
  limitation that belongs in the thesis**, and it may not be uniform across tone
  groups.
- **Framing confound** — many Fitzpatrick17k photographs frame a whole limb or
  face rather than a lesion close-up, unlike everything the models trained on.
  There is no lesion detector here and a hand-rolled "wide-field" heuristic could
  filter unevenly across tones, so this is quantified by hand instead:
  `scripts/sample_spotcheck.py` draws a seeded, tone-stratified sample of 100 for
  manual labelling and reports the rate per tone group.

**Leakage guard.** `scripts/prepare_external_data.py` ends with an overlap check
against the internal splits — an `image_id` intersection (decisive for HAM10000,
which keeps `ISIC_*` ids from the ISIC Archive) plus a decoded-pixel md5 check
against the internal held-out test split. It writes
`reports/external_overlap_check_<ds>.md` and **exits 2 on any hit**; an
overlapping image is data the model may have trained on, which would inflate the
"generalization" number.

**Split variants written** (all in the internal `test_split.csv` schema, so
`SkinLesionDataset` reads them unchanged):

| Dataset | File | Role |
|---|---|---|
| ham10000 | `test_split.csv` | headline — one image per lesion |
| ham10000 | `test_split_full.csv` | every image (appendix / literature comparison) |
| ham10000 | `test_split_no_akiec.csv` | akiec dropped (label-convention sensitivity) |
| fitzpatrick17k | `test_split.csv` | headline — benign vs malignant only |
| fitzpatrick17k | `test_split_with_nonneo.csv` | `non-neoplastic` merged into benign |

Prepared with (CPU-only, no GPU):

```bash
bash run/prepare_external.sh DATASET=ham10000
bash run/prepare_external.sh DATASET=fitzpatrick17k DOWNLOAD_LIMIT=50   # trial first
```

> ⚠️ **Not yet wired to evaluation.** `SkinLesionDataModule.setup()` always builds
> train/val from `fold_dir`, so it cannot read a test-only split yet, and
> `Evaluator` defaults to picking a Youden threshold **on the set being measured**
> — which would violate the `do_not_use_for: threshold_selection` rule these
> configs declare. Both are the next phase's work.

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
risk and turns an assumption into a result. **Now wired** as
`run/ablation_sampler.sh` (`SAMP=off|3|5|10`, toggles
`data.use_weighted_sampler`/`data.undersample_ratio`) — see §7.

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

### 4.1 Augmentation is config-driven (since 2026-06-21)

`build_transforms` ([src/data/transforms.py](../src/data/transforms.py)) builds the
pipeline **from `configs/augmentation/{light,heavy}.yaml`**, not from a hard-coded
list (it previously ignored those YAMLs entirely — switching presets did nothing).
`Resize` is always prepended and `ToTensorV2` always appended; `Normalize`
defaults to ImageNet stats if omitted.

- **`light` (default)** reproduces the exact pipeline that was hard-coded before,
  so the original 30-run results are reproducible with `augmentation=light`.
- **`heavy`** is a *strictly stronger* anti-overfit variant (higher p, wider
  ColorJitter, + `GaussNoise`) for the rare-class manifold. Enable per-run with
  `augmentation=heavy` (requires retraining).
- **MixUp / CutMix / CoarseDropout(CutOut) stay excluded and are now ENFORCED in
  code**: `build_transforms` raises `ValueError` if any appears in the config
  (`_FORBIDDEN_OPS`), so the design decision above can't be silently undone via
  YAML. To revisit, update this doc first, then add a builder + remove from the
  forbidden set.
- Supported ops: `HorizontalFlip, VerticalFlip, RandomRotate90, ShiftScaleRotate,
  RandomScale, Rotate, ColorJitter, CLAHE, GaussianBlur, GaussNoise, Normalize`.
  Any other name raises (typo-safe).

### 4.2 Stochastic depth (`drop_path_rate`) — model-side anti-overfit knob

Each model config (`configs/{teacher,student}/*.yaml`) has `drop_path_rate: 0.0`
(off by default → no behavior change). `create_timm_backbone`
([src/models/heads.py](../src/models/heads.py)) passes it to `timm.create_model`
only when `> 0`. Enable per-run: `student.drop_path_rate=0.1` /
`teacher.drop_path_rate=0.2` (strongest on the ViT/ConvNeXt SOTA set). Verify the
backbone accepts the kwarg on the cluster before a full run.

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
- [x] Add the `ratio × α` ablation to the experiment plan — `run/ablation_sampler.sh` (§7). *(wired 2026-06-21)*
- [x] `transforms.py`: make augmentation **config-driven** (read `configs/augmentation/{light,heavy}.yaml`); `light` == prior hard-coded behavior, `heavy` == stronger safe variant; MixUp/CutMix/CutOut enforced-forbidden via `raise`. *(done 2026-06-21, §4.1)*
- [x] Models: add `drop_path_rate` (stochastic depth) knob, default 0.0/off, via `create_timm_backbone`. *(done 2026-06-21, §4.2)*
- [x] fix the `test_split.csv` independence issue — independent patient-disjoint holdout carved before CV (`test_holdout_splits`, default 6). *(done 2026-06-06)*
- [x] `preprocessing.py`: external eval-only processors `process_ham10000` / `process_fitzpatrick17k` on a shared `_clean_external_image`, with the **two-tier** filter policy (§1.1); `scripts/download_fitzpatrick17k.py` (URL fetch + 4-step validation), `scripts/prepare_external_data.py` (split variants + leakage guard), `scripts/sample_spotcheck.py` (framing confound), `run/prepare_external.sh`. The existing ISIC/PAD processors were **not touched**. *(done 2026-08-10; images not yet downloaded — nothing run on the server)*

### Known limitations of the implemented filters (verify on cluster)
- Dedup is **per-dataset** (`seen_hashes` resets between ISIC and PAD) and **exact-pixel only** — an ISIC↔PAD exact dup or a near-duplicate won't be caught. Intra-dataset exact dups (the main risk) are covered.
- `min_size` only applies on the **fresh decode**; an image already resized to 224 on a prior run can't be re-checked for native size.
- Thresholds (`min_size=32`, `std<8`, `0.97`) are untuned — confirm the `excluded_images.csv` per-label breakdown on the cluster before trusting them; never auto-drop malignant without a look.
- On the external sets (§1.1) the same thresholds only **flag** (tier 2), so an untuned `std<8` cannot silently shrink the benchmark — but the flag counts still need a look before the filtered-subset numbers are quoted.
- The Fitzpatrick17k `md5hash` column is *assumed* to be the md5 of the image bytes. The downloader probes the first 25 fetches and aborts if under half match, rather than rejecting the whole dataset after hours — if that fires, re-run with `--md5-check warn` and record the choice.

> The α/ratio interaction (§3) remains an empirical claim to confirm via the
> cluster ablation, not an asserted fact.

---

## 7. Data-strategy ablation harness (prove PAD + sampler help)

The two pillars of the data strategy — **PAD mixing** and the **undersampler** —
were design assumptions with no counterfactual in the 30-run experiment (which
ablates only KD vs baseline). These make them *measurable*. Both are
single-variable, 5-fold, and land in isolated run-dirs via `run_suffix`.

| Ablation | Script | Varies | Held fixed | Read the verdict from |
|---|---|---|---|---|
| **Sampler** | `run/ablation_sampler.sh` | `data.use_weighted_sampler` / `data.undersample_ratio` (`SAMP=off\|3\|5\|10`) | KD, **teacher reused**, seed, folds, loss | pAUC / sens / AUPRC vs the main ratio-5 run |
| **PAD mixing** | `run/ablation_pad.sh` | `data.train_sources` (`ARM=isic_only\|isic_pad`) — filters **TRAIN+VAL only** | **baseline (no KD)**, identical combined test | per-domain rows (PAD-source) of the combined test |

Two design rules that make the comparisons honest:
- **PAD ablation runs baseline, not KD.** A KD teacher trained on ISIC+PAD would
  leak PAD knowledge into the ISIC-only arm via soft labels. Baseline (no teacher)
  isolates the single variable = whether PAD is in the student's training data.
- **The test set is never filtered.** `train_sources` only touches train+val, so
  both arms are judged on the *same* held-out combined test; its PAD portion is
  trained on by neither arm. `SkinLesionDataModule._filter_to_sources` enforces
  this (and raises if a filter empties a split).

**Enabling metrics (foundation):** `Evaluator.save_predictions` now writes
`predictions.csv` (`y_true,y_prob,y_pred,source`) next to every `test_metrics.json`,
and `compute_metrics` adds `auprc` (+ `prevalence` baseline) and
`sens_at_90spec`/`sens_at_95spec`. AUPRC is the honest summary at ~0.4% prevalence
(AUC-ROC is optimistic); the `source` column drives the ISIC-vs-PAD breakdown; and
PR-curve / bootstrap CIs are recomputable offline from the saved predictions.
`source_from_path()` derives the origin tag from the processed path
(`data/processed/<dataset>/…`).
