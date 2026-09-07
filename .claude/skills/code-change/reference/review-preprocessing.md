---
name: review-preprocessing
description: Review data-preprocessing code (src/data/, scripts/prepare_data.py) against this project's known-correct preprocessing contract. Use when the user changes preprocessing/splits/augmentation/sampler, asks "review my preprocessing", "did I break the data pipeline", "check the splits/aug", or after editing process_isic2024 / process_pad_ufes_20 / generate_group_kfold_splits / build_transforms / the sampler. NOT for judging training results (use assess-training) and NOT a substitute for validate-pipeline's static checks.
---

# review-preprocessing

Reviews the **data layer** — offline image processing, split generation, online
augmentation, and class-imbalance sampling — against the contract the rest of
this repo assumes. Catches data bugs that silently poison training (leakage,
label corruption, dropped-class imbalance, wrong normalization) and never throw
an exception, so neither `validate-pipeline` nor a crash will surface them.

Scope: `src/data/preprocessing.py`, `src/data/dataset.py`,
`src/data/datamodule.py`, `src/data/transforms.py`, `src/data/sampler.py`,
`scripts/prepare_data.py`.

## How to run

1. Get the diff in scope: `git diff HEAD -- src/data/ scripts/prepare_data.py`
   (also `git diff main...HEAD` if reviewing a branch).
2. Walk the checklist below **in order** — it follows the data flow. For each
   item, read the relevant hunk + the enclosing function and confirm the
   invariant holds. Cite `file:line`.
3. Report findings most-severe first. A leakage or label bug outranks any
   style/efficiency note. End with what you could NOT verify locally (the Mac
   can't import `h5py`/`numpy`/`pandas` — real correctness is a cluster
   `prepare` run), and recommend the static `validate-pipeline` pass.

## The preprocessing contract (the requirement to review against)

The intended pipeline — any change must preserve every step:

1. **ISIC 2024 extraction** (`process_isic2024`): read JPEG bytes from
   `train-image.hdf5` + `train-metadata.csv`; raw label column is `target`,
   written into the processed df under the column **`label`**; decode → RGB →
   resize **224×224 LANCZOS** → save `data/processed/isic2024/{benign,malignant}/{isic_id}.jpg`.
2. **Quality filter** (`is_uninformative`): drop corrupt (decode raises) and
   uninformative images (grayscale `std < 8.0`, or `>97%` pixels near-black ≤10 /
   near-white ≥245); excluded ids+reason logged to `excluded_images.csv`;
   excluded rows must NOT appear in the returned df.
3. **PAD-UFES-20** (optional, `process_pad_ufes_20`): 6 dx → binary
   (BCC/SCC/MEL=1, ACK/NEV/SEK=0); same resize + same quality filter; concat
   with ISIC.
4. **Splits** (`generate_group_kfold_splits`): `StratifiedGroupKFold(n=5)`
   grouped by **`patient_id`** (no patient leakage), stratified by `label` →
   `fold_{0..4}/{train,val}_split.csv`; fold 0's val also written as held-out
   `test_split.csv`.
5. **Online aug** (`build_transforms`, Albumentations): train = Resize, H/V
   flip, RandomRotate90, ShiftScaleRotate, ColorJitter, GaussianBlur, **ImageNet
   Normalize** (mean `[0.485,0.456,0.406]` std `[0.229,0.224,0.225]`),
   ToTensorV2; val/test = Resize → Normalize → ToTensorV2 only.
6. **Imbalance** (`DynamicUndersampledSampler`): ~**1:5 malignant:benign** per
   epoch, reshuffled via `datamodule.set_epoch(epoch)`.

## Review checklist

### A. Labels & schema (silent-corruption class)
- [ ] **`label_col` trap**: `generate_group_kfold_splits` is called with
  `label_col="label"`, NOT `cfg.data.label_col` (which is the raw `"target"`).
  Passing `cfg.data.label_col` on the processed df → `KeyError: 'target'`.
- [ ] `SkinLesionDataset` still reads columns `image_path` + `label`; any rename
  upstream must match `dataset.py` and the CSV writer.
- [ ] Label is `int(0/1)`; benign=0/malignant=1 mapping unchanged (PAD map intact).
- [ ] Every row written to a split CSV has a real on-disk `image_path` (excluded/
  unlinked images must be dropped from `records`, else dataset `Image.open` crashes mid-training).

### B. Leakage & splits (the bug that inflates every metric)
- [ ] Grouping is still by `patient_id` — losing the group arg silently leaks a
  patient's lesions across train/val and inflates val/test scores.
- [ ] Stratification label is `label`; folds preserve benign:malignant ratio.
- [ ] `test_split.csv` is fold 0's val. Note it's NOT independent of folds 1–4's
  train sets — flag if a change quotes it as a fully held-out set.
- [ ] `seed` is threaded through (`shuffle=True, random_state=seed`) so splits
  are reproducible across teacher/student/baseline runs.

### C. Quality filter (the new code — over/under-dropping)
- [ ] Excluded images are removed from `records` AND a stale bad image already on
  disk is `unlink()`ed (on-disk dataset must match the CSVs).
- [ ] Exception coverage is wide enough — PIL `DecompressionBombError` is NOT an
  `OSError`; an uncaught type re-crashes the prepare job it was meant to protect.
- [ ] Filter does not silently gut the **malignant** (rare) class — recommend the
  user check `excluded_images.csv`'s per-label breakdown on the cluster, not just the count.
- [ ] Re-run determinism: filtering a re-encoded on-disk JPEG vs a fresh resized
  array can classify borderline `std≈8.0` images differently between runs.
- [ ] `excluded_images.csv` write isn't left stale by an `if excluded:` guard
  when a later lenient run finds nothing.

### D. Augmentation & normalization (train/eval skew)
- [ ] Val/test pipeline has **no** random aug — only Resize + Normalize +
  ToTensorV2. A flip/jitter leaking into eval makes metrics noisy/non-reproducible.
- [ ] Normalize stats match between train and val/test (both ImageNet) — a
  mismatch is train/serve skew that no test catches.
- [ ] `image_size` is read from config, consistent with the 224×224 offline resize.
- [ ] PIL→numpy conversion happens before Albumentations (it operates on `np.ndarray`).

### E. Sampler & datamodule
- [ ] Undersampler still targets ~1:5 and is reshuffled each epoch via
  `set_epoch(epoch)` — a sampler built once and never re-seeded repeats the same
  benign subset every epoch (hidden underfit).
- [ ] Sampler is applied to **train only**, never val/test.

### F. Idempotency & cost
- [ ] Fast-path (`dst.exists()`) behavior is intentional — re-decoding every
  already-processed image on resume defeats the skip optimization (ISIC ≈ 400k images).

## Don't
- Don't try to import the modules on the Mac to "confirm" — it won't (no deps).
  Reason from the code + the contract above, then defer real verification to a
  cluster `bash run/prepare_data.sh` run.
- Don't approve a split change without re-checking the `patient_id` grouping —
  it's the highest-cost, lowest-visibility bug in this layer.
