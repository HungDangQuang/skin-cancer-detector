# Android on-device **evaluation** harness — task brief

**For an independent Android/Kotlin project.** You do not need, and will not be given, the
machine-learning repository these models came from. Everything required arrives as a handover bundle
described in §2. No Python, no training data, no server access is involved on your side.

Written 2026-09-26.

> **If you did the August 2026 latency benchmark: this is a different job.** That one measured *how
> fast* and *how heavy*, and explicitly told you not to compute accuracy. This one measures *whether
> the model still computes the right thing when the app does its own image handling*. Timing is
> irrelevant here — you may leave the phone plugged in.

---

## 1. What this is

We have image classifiers exported to **ExecuTorch `.pte`**: one image in, one number out
(skin-lesion screening). We have scored them on a server over a fixed, labelled test set. We now
need **the same images scored on a real phone**, so we can prove the model we deploy is the model we
evaluated.

The whole deliverable is: **one raw logit per image, per model, written to a CSV.** That is it. We
compute every quality metric ourselves, off-device.

### What you are NOT doing

- **Not computing accuracy, AUC, AUPRC, sensitivity, or any metric.** Dump logits; we do the maths.
  Our metric definitions are non-standard (a partial AUC above a fixed sensitivity floor) and must
  come from one implementation only.
- **Not applying `sigmoid`, a threshold, or calibration.** The threshold is not 0.5 and lives
  outside the model.
- **Not measuring latency or memory.** Already done. (We do want one wall-clock total per run — §6 —
  purely as a sanity figure.)
- **Not building the product app.** No camera, no UI polish, no risk display. A single screen or an
  instrumented test is fine.
- **Not quantising, converting, or re-exporting the `.pte`.** If a model misbehaves, report it.

---

## 2. The handover bundle

```
mobile_eval_handover/
├── README.md
├── catalog.json                  ← the models; drive your harness from this, never hardcode names
├── SHA256SUMS                    ← run `shasum -c SHA256SUMS` after extracting, before anything else
├── models/
│   └── <model_id>.pte            ← 1–4 files, 24–48 MB each
├── eval_set/
│   ├── images/<id>__<source>__y<label>.jpg   ← ~59,000 JPEGs, 224×224, ~6 KB each (~350 MB total)
│   ├── manifest.csv              ← id,image_file,input_bin,label,source,src_path
│   └── meta.json                 ← preprocessing constants — read these, don't hardcode
├── l1_gate/
│   ├── inputs/<id>.bin           ← 100 pre-normalised tensors
│   └── refs/ref_<model_id>.csv   ← id,label,source,logit,prob  (per model)
└── (no schema/ file — the JSON shape is printed inline in §6)
```

Notes that will save you time:

- **The `<id>` in `l1_gate/` and in `eval_set/` refer to the same images.** The gate set is a subset
  of the evaluation set, cut from the same manifest. You can join them by `id`.
- The image filename encodes the label (`y0`/`y1`). **Ignore it** — read labels from
  `manifest.csv` if you need them at all (you do not, for this job).
- `manifest.csv` has an `input_bin` column that is only meaningful for the 100 gate ids; it may be
  empty for the rest.
- **The CSVs use CRLF (`\r\n`) line endings.** They are written by Python's `csv` module. Trim
  `\r` when parsing, or you will spend an afternoon on a "data problem" that is a parsing bug.
- In `refs/ref_<model_id>.csv`, **compare the `logit` column (index 3)**. Ignore `label`, `source`
  and `prob`.

### Getting ~350 MB and ~59,000 small files onto the device

Do **not** ship the images inside the APK (`assets/`) — the build will be unusable. Push them to the
app's external files dir and read from there:

```
adb push mobile_eval_handover /sdcard/Android/data/<your.package>/files/
```

`adb push` of ~59,000 tiny files is slow (many round trips). Pushing a single archive and unpacking
it on-device is usually much faster — either is fine, just verify `SHA256SUMS` afterwards.

---

## 3. What to build

### 3.1 Runtime dependency — read this before you pick a version

`org.pytorch:executorch-android`.

⚠️ **`catalog.json` may declare `executorch_version: "1.4.1"`, and 1.4.1 does not exist for Android
on Maven.** This tripped up the August run. Use **1.4.0** (or 1.3.1). Our earlier parity work
verified that **1.3.1 and 1.4.0 produce identical logits**, so the choice is not numerically
critical — but **record the exact dependency coordinate you used** in the output.

### 3.2 Device and threads

- **A real arm64 device.** No emulator: emulated CPU paths are not what we are measuring.
- Record the thread count. Our earlier parity work found logits **identical across 1 and 4 threads**,
  so pick whatever is convenient (4 is faster). If you observe logits changing with thread count,
  that is a finding — report it.

### 3.3 Two arms, and the second one is the point

| Arm | Input | What it isolates |
|---|---|---|
| **A — `processed224`** | `eval_set/images/*.jpg`, already 224×224 | Your JPEG decode + normalisation only |
| **B — `resample`** | full-resolution originals (a **second, smaller bundle** we send later) | Your **resampling filter** — the images arrive at native size and you must scale them to 224 |

**Build arm A first and report it before starting arm B.** Arm B has an extra requirement: run it
once per resampling filter we ask for (bilinear, nearest, and a Lanczos implementation if you have
one) and report each separately — we are measuring the filter, not your app.

---

## 4. The model contract

### 4.1 Input

| Property | Value |
|---|---|
| Shape | `(1, 3, 224, 224)` — NCHW |
| Type | `float32`, little-endian |
| Channel order | **RGB** (not BGR, not ARGB) |
| Value range | normalised: `/255`, then `(x − mean) / std` |
| mean | `[0.485, 0.456, 0.406]` |
| std | `[0.229, 0.224, 0.225]` |

The images in `eval_set/images/` are **already 224×224**, so **arm A must not resize at all**. If
your code scales anyway (even 224→224 through a scaler), you introduce error we cannot attribute.
Decode, normalise, feed.

**Decode carefully — this is where this job goes wrong.**

```kotlin
val opts = BitmapFactory.Options().apply {
    inPreferredConfig = Bitmap.Config.ARGB_8888
    inScaled = false        // do NOT let screen density rescale the bitmap
    inSampleSize = 1        // no subsampling
    inPremultiplied = false // alpha must not touch the colour channels
}
// decodeFile returns null on a corrupt/unreadable file — handle it, do NOT let it throw:
val bmp = BitmapFactory.decodeFile(path, opts)
    ?: return Row(id, logit = null, error = "decode_returned_null")
if (bmp.width != 224 || bmp.height != 224) {
    return Row(id, logit = null, error = "unexpected_size_${bmp.width}x${bmp.height}")
}
```

Then, in **CHW** order — all of channel R, then all of G, then all of B:

```kotlin
val mean = floatArrayOf(0.485f, 0.456f, 0.406f)
val std  = floatArrayOf(0.229f, 0.224f, 0.225f)
val px = IntArray(224 * 224)
bmp.getPixels(px, 0, 224, 0, 0, 224, 224)
val out = FloatArray(3 * 224 * 224)
for (c in 0 until 3) {
    val shift = 16 - 8 * c                       // R=16, G=8, B=0
    for (i in px.indices) {
        val v = ((px[i] shr shift) and 0xFF) / 255f
        out[c * 224 * 224 + i] = (v - mean[c]) / std[c]
    }
}
```

Two traps that have bitten this exact pipeline: writing **HWC** instead of CHW (the model runs and
produces plausible-looking nonsense), and dividing by `std` **before** subtracting `mean`. Verify
against §5.1 before trusting anything.

### 4.2 Output

One `float`: a **raw logit**. Unbounded and frequently negative. Measured across the references we
have shipped before: **−7.41 to +6.22**, plus one known model that reaches **+77.45** on a single
input. Do not clamp, do not transform, do not assume a range.

Write it with **at least 7 significant digits** (`"%.7g"`). We compare against a server value at
1e-5 resolution; rounding to 3 decimals destroys the measurement.

---

## 5. Procedure

### 5.1 Gate — do this before the ~59,000-image run

**Step 1, `.bin` path.** Run all 100 `l1_gate/inputs/*.bin` through each model and compare to
`refs/ref_<model_id>.csv`:

```
required:  max over the 100 samples of |device_logit − reference_logit|  <  1e-3
```

These inputs are **already normalised** — feed them straight in, do not decode, do not normalise.
This separates "your preprocessing is wrong" from "the export is wrong". **If it fails, stop and
report.**

**Step 2, image path.** Take the same 100 ids from `eval_set/images/`, run them through **your arm-A
path**, and compare to the same refs. Report `max|Δ|` — we do not yet know what value to expect here
and measuring it is part of the point. But calibrate your debugging: a Δ of order **1** means a
layout or channel bug, not a finding. A Δ of order 1e-2 or below is plausibly real.

### 5.2 The evaluation run

For each model in `catalog.json`, for every image: decode → normalise → infer → append a row.

Budget (measured on a Pixel 6a, thermally throttled, 4 threads): **~40 min** for the smallest
architecture, up to **~2 h** for the largest XNNPACK one. If the catalog contains a model marked
`backend: "portable"`, it runs ~99× slower (≈64 h) — **skip it** unless the catalog marks it
`required: true`.

**Conditions — deliberately relaxed compared with the August benchmark:**

- **Plugged in is fine. Any clock speed is fine. Thermal throttling is fine.** Logits are
  deterministic; throttling changes only how long this takes.
- Do not run other heavy apps, simply so it finishes.

**Engineering requirements — a multi-hour loop needs these:**

1. **Flush to disk every ≤ 500 rows.** Do not hold 59,000 results in memory and write at the end.
2. **Resumable.** On restart, skip ids already present in the output file.
3. **Never silently skip an image.** A decode or inference failure gets a row with an empty `logit`
   and a non-empty `error`. A missing row is indistinguishable from a bug; an error row is data.
4. **Determinism check.** Re-run the first 500 images a second time; every logit must be
   **bit-identical**. Report whether it was. If it is not, stop — nothing else is reliable.
5. Keep the order given by `manifest.csv`, so our join is trivial.

---

## 6. Output

One CSV per model per arm:

```csv
id,logit,error
0000,-0.5613037,
0001,2.1068820,
0002,,decode_returned_null
```

Plus one JSON summary per model per arm. There is no schema file; this is the shape:

```json
{
  "model_id": "mobilenetv4_conv_medium__...",
  "arm": "processed224",
  "resample_filter": null,
  "n_attempted": 59093, "n_succeeded": 59093, "n_errored": 0,
  "gate": {
    "bin_path_max_abs_logit_delta": 4.1e-06,
    "image_path_max_abs_logit_delta": 0.0031,
    "tolerance": 0.001,
    "bin_path_passed": true,
    "n_samples": 100
  },
  "determinism": { "n_rechecked": 500, "bit_identical": true },
  "runtime": {
    "executorch_dependency": "org.pytorch:executorch-android:1.4.0",
    "threads": 4
  },
  "device": {
    "model": "Pixel 6a", "soc": "Tensor G1", "abi": "arm64-v8a",
    "android_version": "14", "sdk_int": 34
  },
  "wall_clock_seconds": 2418
}
```

---

## 7. Acceptance criteria

A run is deliverable when **all** of these hold:

1. `shasum -c SHA256SUMS` passed on the bundle.
2. §5.1 Step 1 passed for every model (`max|Δ| < 1e-3`).
3. The determinism recheck was bit-identical.
4. `n_errored / n_attempted < 0.001` (fewer than ~59 bad rows), **and** every error row carries a
   reason string.
5. Every row has 7+ significant digits.

If any of 1–3 fails, that is a **stop-and-report**, not something to work around.

## 8. When to stop and ask us

- The `.bin` gate fails on any model.
- Logits change between runs, or between thread counts.
- More than ~0.1% of images fail to decode.
- `catalog.json` disagrees with what you find in the bundle (missing model, missing ref file,
  a declared runtime version that does not exist).
- Anything makes you want to modify a `.pte`, re-export, or "correct" a number.

## 9. What to send back

1. The per-model CSVs — that is the deliverable.
2. The JSON summaries.
3. A short note on anything surprising, especially any image that failed to decode and whether the
   determinism check held.

Do not send interpretations of model quality; we have the labels and will compute that. If a number
looks wrong to you, say so and show it — do not adjust anything to make it look right.
