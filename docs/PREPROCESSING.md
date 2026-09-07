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
  are dropped at prepare time. Coverage was restored to **99.98 %** from an
  md5-verified mirror, so the set is effectively complete — see "How the images
  were obtained" below before quoting any coverage caveat.
- **Framing confound** — many Fitzpatrick17k photographs frame a whole limb or
  face rather than a lesion close-up, unlike everything the models trained on.
  There is no lesion detector here and a hand-rolled "wide-field" heuristic could
  filter unevenly across tones, so this is quantified by hand instead:
  `scripts/sample_spotcheck.py` draws a seeded, tone-stratified sample of 100 for
  manual labelling and reports the rate per tone group. **§1.2 turns the same
  confound into a measurement** instead of only a caveat.

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
| fitzpatrick17k | `test_split_crop70.csv` | headline rows, centre 70 % of each raw image (framing — §1.2) |
| fitzpatrick17k | `test_split_crop50.csv` | headline rows, centre 50 % of each raw image (framing — §1.2) |

Downloaded and prepared with (CPU-only, no GPU):

```bash
bash run/download_external.sh DATASET=ham10000 RM_ZIP=1        # Harvard Dataverse, md5-verified
bash run/download_external.sh DATASET=fitzpatrick17k SAMPLE=60 # trial first (random rows)
bash run/download_external.sh DATASET=fitzpatrick17k           # then all ~16.5k URLs

bash run/prepare_external.sh DATASET=ham10000
bash run/prepare_external.sh DATASET=fitzpatrick17k SKIP_DOWNLOAD=1
```
**What the sets actually contain (HAM10000 measured 2026-08-23; Fitzpatrick17k re-measured 2026-09-05).**

| Dataset | Fetched | Prepared (headline) | Malignant | Prevalence |
|---|---|---|---|---|
| ham10000 | 10,015 / 10,015 images | 7,470 (one per lesion) | 1,169 | 15.7 % |
| fitzpatrick17k | 16,574 / 16,577 images (**99.98 %**) | 4,320 (benign vs malignant) | 2,160 | 50.0 % |

Fitzpatrick17k after processing: 16,012 usable images (562 dropped for unknown skin tone, 0 tier-1
integrity drops, 12 tier-2 flags kept); tone × label in the headline split = light 1,115/1,195,
medium 842/757, dark 203/208 (benign/malignant). Both overlap checks came back clean.

> **How the images were obtained.** The release ships URLs, not images, and one of the
> two linked atlases (`www.dermaamin.com`) has gone dark — fetching the published URLs
> directly recovers only ~24 %. This project does not use that subset. A public mirror
> whose **filenames are the content md5** was verified against the release's own
> `md5hash` column (so the check is exact and self-proving) and brought coverage to
> **99.98 %**; `data/raw/fitzpatrick17k/download_log.csv` records the outcome per row
> (16,574 `kaggle_mirror_md5_verified`, 3 `not_in_mirror_and_url_dead`). Quote 99.98 %.
>
> ⚠️ The mirror uploader's CC0 label carries **no authority** over the source atlas
> images — cite the original Fitzpatrick17k release's terms, not the mirror's licence field.

**Evaluation path.** `scripts/evaluate_external.py` (`run/evaluate_external.sh`)
reads these CSVs directly — not through `SkinLesionDataModule`, which only knows
the internal fold layout — and freezes each run's decision threshold from its own
internal `val_predictions.csv` (Youden's J), honouring the
`do_not_use_for: threshold_selection` rule these configs declare. Results go to
`reports/external/<ds>/<variant>/<run_tag>/`, with a per-subgroup table (`dx` for
HAM10000, `tone_group` for Fitzpatrick17k).

---


### 1.2 Framing variants — does cropping to the lesion help? (Fitzpatrick17k)

**The question.** The Android app hands the model whatever the camera framed.
Every training image, by contrast, is a lesion-centred crop (ISIC 2024 is
`~128×128` cut from 3D total-body photography; PAD-UFES-20 is a clinical
close-up). So a natural deployment idea is *"crop to the lesion on-device, then
classify"*. That is a claim about **field of view**, and it is testable with the
data already on disk — no retraining, no new dataset.

**The design.** Fitzpatrick17k is the only evaluation set that is genuinely
wide-field (whole limbs and faces). `crop_variants:` in
`configs/data/fitzpatrick17k.yaml` re-prepares those same rows keeping only the
central fraction of each **raw** image, then applies the *identical* squash to
`224×224`:

| Variant | Field of view | Everything else |
|---|---|---|
| `headline` | full frame (control) | identical |
| `crop70` | central 70 % of width **and** height | identical |
| `crop50` | central 50 % of width **and** height | identical |

Both sides of the crop are scaled by the same factor, so the **aspect ratio is
unchanged** and the squash that follows is byte-for-byte the same operation as
the headline path. One variable moves: how much skin surrounds the lesion.
Cropping happens on the raw pixels *before* the resize — cropping the already
squashed 224 square would discard the very detail the crop is meant to zoom into.

**Reading the result.** `headline → crop70 → crop50` is a monotone series on the
same rows and the same labels, so it is a **paired** comparison (use
`scripts/bootstrap_ci.py`, not a win count):

- **AUC rises with cropping** → framing mismatch is a real, recoverable part of
  the cross-domain drop, and an on-device crop step is worth building.
- **AUC flat** → the drop is about image content (camera, lighting, tone,
  modality) and no amount of cropping recovers it. This is the outcome the
  HAM10000 evidence predicts: HAM is *already* tightly cropped around the lesion
  and still falls from AUC 0.98 in-domain to 0.83.
- **AUC falls** → the centre crop is cutting the lesion out of frame. Check a
  handful of `crop50` images before concluding anything.

Note this measures the **ceiling** of a perfect crop: a centre crop assumes the
lesion is centred, which a real detector would not guarantee.

**Traps this design already avoids:**

- **Each fraction gets its own `data/processed/fitzpatrick17k_<key>/`.**
  `_clean_external_image`'s `dst.exists()` fast-path cannot tell a cropped file
  from an uncropped one, so a shared directory would silently score the headline
  pixels under a crop variant's name — a green run reporting nothing.
- **Row counts match the headline by construction.** The tier-1 `min_size` guard
  is applied to the RAW frame *before* the crop (`src/data/preprocessing.py`),
  precisely so a crop variant drops exactly the rows the headline drops and the
  delta stays paired. Prepare still prints a loud warning on a count mismatch —
  that would mean a missing or unreadable source file, not that cropping is
  selective.
- **The threshold still comes from the internal val fold**, unchanged — a crop
  variant is a different *input*, not a licence to refit the operating point.
- **`is_uninformative` (tier 2) flags more aggressively after cropping** — a
  centre crop of uniform skin is flatter than the full frame. It still only
  flags, never drops (§1.1), but compare the `quality_flags` counts across
  variants before attributing a change to framing alone. Measured 2026-09-05:
  5 (headline) -> 9 (crop70) -> 13 (crop50) flags, all kept; row counts stayed 4,320.

#### Result (measured 2026-09-05) — cropping helps universally, but recovers only ~6 % of the gap

**Scope: all 19 run-dirs × 5 folds × 3 variants = 285 evaluations, no failed fold.** Sources:
`reports/framing_crop_ci19.{json,md}` (38 paired deltas + `tone_group` subgroups),
`reports/external/fitzpatrick17k/{crop70,crop50}/`. The first 3-run pass is kept at
`reports/framing_crop_ci.{json,md}`.

*Three checks that make the deltas trustworthy:* re-running `headline` reproduced the
existing numbers exactly (fastvit AUPRC 0.6623, mobilenetv4 0.6172, teacher AUC 0.7039);
`y_true` matched across variants on **95/95 folds** (so the pairing is valid); and `y_prob`
differed on **95/95** (so the crop actually reached the model — not the `dst.exists()` trap).

**Paired bootstrap, crop − headline, 2000 replicates:**

| Variant | Metric | Positive | CI excludes 0 | Mean |
|---|---|---|---|---|
| **crop70** | AUC-ROC | **19/19** | **18/19** | **+0.0127** |
| | AUPRC | 19/19 | 16/19 | +0.0112 |
| | pAUC@80 | 19/19 | 16/19 | +0.0035 |
| | Sens@90Spec | 17/19 | 7/19 | +0.0104 |
| **crop50** | AUC-ROC | 18/19 | 11/19 | +0.0122 |
| | AUPRC | 18/19 | 12/19 | +0.0140 |

**1. Real and universal, but small — the "AUC rises" branch at the bottom of its range.**
crop70 is positive on 19/19 runs and significant on 18/19, coverage on par with the §6.1
fairness result. But the mean is only **+0.0127 AUC**. Against a ~0.20 gap (in-domain ISIC
≈ 0.94 vs Fitzpatrick ≈ 0.64) that is roughly **6 % of the distance recovered**. Framing
mismatch is a genuine, addressable — and minor — component of the cross-domain drop. The
bulk is image content plus the missing benign classes, exactly as HAM10000 predicted: HAM
is already tightly cropped and still falls 0.98 → 0.83.

**2. Teachers benefit too — `convnextv2_base` is the sole exception.** `teacher/maxvit_base`
(+0.0166 *) and `teacher/efficientnetv2_m` (+0.0149 *) are both significant; only
`teacher/convnextv2_base` (+0.0042 [−0.0003, +0.0090]) is not — and it is the **only one of
19 runs** that misses on AUC. A "large backbones are less sensitive to field of view" story
does **not** survive the full sweep; this is one backbone's quirk, not a capacity effect.
*(The 3-run pilot suggested the opposite, because `convnextv2_base` was the only teacher in it.)*

**3. crop50 is not worse on score — it is worse on CERTAINTY.** Mean AUC is nearly identical
(+0.0122 vs +0.0127) but significant runs drop from **18/19 to 11/19**, and between-run
variance grows. There is a **teacher-dependent split**: the `efficientnetv2_m` family gains
*more* at 50 % (`→mobilenetv4` +0.0269 vs +0.0194 at 70 %) while the `maxvit_base` family
degrades (`→fastvit` +0.0028, loses significance). Note `efficientnetv2_m` is the *weakest*
teacher on Fitzpatrick — it has the most headroom, the same rule that governs KD gain.
→ **crop70 is the safe default**; crop50 is only worth considering if the teacher is known.

**4. Dark skin benefits most — the strongest result of the experiment.** Mean ΔAUC over 19 runs:

| Tone group | ΔAUC (crop70) | ΔAUC (crop50) |
|---|---|---|
| light (I–II) | +0.0086 | +0.0040 |
| medium (III–IV) | +0.0174 | +0.0215 |
| **dark (V–VI)** | **+0.0207** | **+0.0350** |

Medium gains more than light on **17/19** runs; dark on **18/19**. The light−medium gap — the
one gap §6.1 proves is real and universal — narrows from **+0.0469 to +0.0380** (17/19 runs).

**5. And it narrows for the RIGHT reason.** At crop70 the light group gets worse on **0/19**
runs while medium improves on **19/19**. That is a genuine fairness gain, not levelling down —
and a stronger argument for an on-device crop than the +0.0127 AUC is.

> ⚠️ **At crop50 the levelling-down warning does partly apply.** The gap narrows further
> (+0.0469 → +0.0294, on 19/19 runs) but light degrades on **5/19** runs and the number of
> gaps that stay significant falls to **9/19** — most of the gap became *undecidable*, not
> absent. Gap size alone is never a fairness verdict: read the per-group values and the
> certainty next to it. Same class of error as the prevalence trap in §6.2, different clothing.

**What to conclude for the app.** An on-device "crop to the lesion, then classify" step is
worth building, but it is a refinement, not a fix: a small but universal ranking gain, most of
it for medium and **dark** skin, and it leaves the operating-point problem untouched —
Sens@90Spec reaches significance on only 7/19 runs. A centre crop also assumes the lesion is
centred, which a real detector would not guarantee, so these are the **ceiling** of a perfect
crop, not the expected value of a shipped one.
**Run it** (CPU-only; the crop variants add ~2 processing passes and one
`data/processed/` tree each):

```bash
bash run/prepare_external.sh DATASET=fitzpatrick17k SKIP_DOWNLOAD=1   # writes crop70 + crop50
bash run/evaluate_external.sh DATASET=fitzpatrick17k VARIANTS=headline,crop70,crop50 GPU=0
```

`CROP_FRACS=none` skips them; `CROP_FRACS=0.8,0.6` overrides the config.

**Getting the paired CI takes one extra step.** `scripts/bootstrap_ci.py --pair A:B`
only pairs run-dirs *inside one* `--results-dir`, and the two sides of a framing
comparison live in sibling variant trees. Stage them under one directory first (a
symlink per variant is enough), giving each a name that does NOT start with `kd_` or
`baseline_` so the kd-vs-baseline auto-pairing does not also fire:

```bash
R="$(pwd)/reports/external/fitzpatrick17k"
mkdir -p .tmp/framing_ci
ln -s "$R/headline/kd_maxvit_base_to_fastvit_sa12" .tmp/framing_ci/shipA_headline
ln -s "$R/crop70/kd_maxvit_base_to_fastvit_sa12"   .tmp/framing_ci/shipA_crop70
# ... one link per run x variant ...

python scripts/bootstrap_ci.py --results-dir .tmp/framing_ci --n-boot 2000 --seed 42 \
    --pair shipA_crop70:shipA_headline \
    --out-json reports/framing_crop_ci.json --out-md reports/framing_crop_ci.md

# add --subgroup-col tone_group for the per-tone table
```

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
