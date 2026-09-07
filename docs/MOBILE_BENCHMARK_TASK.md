# Android on-device benchmark — task brief

**For an independent Android/Kotlin project.** You do not need, and will not be
given, the machine-learning repository these models came from. Everything
required arrives as a single handover bundle described in §2. No Python, no
training data, no server access is involved on your side.

Written 2026-08-24.

---

## 1. What this is

We have 16 trained image classifiers exported to **ExecuTorch `.pte`** format.
They are skin-lesion screening models: one image in, one number out. We need to
know **how fast and how heavy they are on a real Android phone**, and we need
proof that they compute the same numbers on the phone as they do on a PC.

You are building a **throwaway benchmark harness**, not a product app. No camera,
no UI polish, no user-facing risk display. A single screen (or even a
instrumented test) that loads models, runs them over a fixed set of inputs, and
writes JSON results is the whole deliverable.

### What you are NOT doing

- Not measuring accuracy. The 100 inputs in the bundle are far too few to say
  anything about model quality, and accuracy is already established elsewhere.
  Do not compute or report accuracy, AUC, or any quality metric.
- Not interpreting the model's output medically. The output is a raw number; the
  mapping from that number to a decision involves a threshold and a calibration
  step that are deliberately **not** part of this task (see §4.3).
- Not building the product app.
- Not quantising, converting, re-exporting, or otherwise modifying the `.pte`
  files. If a model does not work, report it — do not fix it.

---

## 2. The handover bundle

You receive one directory, roughly **700 MB**:

```
mobile_benchmark_handover/
├── README.md                     ← this document
├── catalog.json                  ← machine-readable list of all 16 models
├── SHA256SUMS                    ← verify after extracting: shasum -c SHA256SUMS
├── models/
│   ├── mobilenetv4_conv_medium__convnextv2_base_fold0.pte
│   ├── … (16 files total, 24–48 MB each, 580 MB total)
├── benchmark_set/
│   ├── inputs/0000.bin … 0099.bin      ← 100 preprocessed input tensors
│   ├── images/0000__isic2024__y1.jpg…  ← the 100 original images (optional, §6.6)
│   ├── refs/ref_<model_name>.csv       ← 16 files: expected output per model
│   ├── manifest.csv                    ← id ↔ image file ↔ input file ↔ label
│   └── meta.json                       ← input format constants
└── schema/
    └── result.schema.json        ← the JSON you must produce
```

`catalog.json` is the file to drive your harness from — it lists every model with
its `.pte` filename, its matching reference CSV, its backend, and its expected
parity magnitude. Do not hardcode model names in Kotlin; iterate the catalog.

---

## 3. What to build

### 3.1 Runtime dependency — version must match exactly

The `.pte` files were produced with **ExecuTorch 1.4.1**. The Android runtime AAR
must be **the same version**. The `.pte` container is versioned; a mismatched
runtime either refuses to load or, worse, loads and behaves incorrectly.

**If you cannot obtain exactly 1.4.1 for Android, stop and tell us before doing
anything else.** We can re-export the models against whatever version you can
actually depend on — that is a cheap operation on our side and far better than
you working around a version gap. When you do resolve it, report back the exact
dependency coordinate and version you used; it goes in the results JSON.

The runtime must include the **XNNPACK** backend: 12 of the 16 models are lowered
to XNNPACK and will not run without it.

### 3.2 Device requirements

- A **physical Android phone**, `arm64-v8a`. Emulator numbers are worthless for
  latency and will be rejected.
- Report the exact device model, SoC/chipset, Android version and SDK level.
- If you have more than one device available, benchmarking on two is a bonus, not
  a requirement — but never mix results from two devices in one table.

### 3.3 Getting 580 MB of models onto the device

Do **not** put the `.pte` files in `assets/` or `res/`. That would produce an
absurd APK and hit packaging limits.

Push them to the app's external files directory and load from a plain filesystem
path:

```
adb push models/       /sdcard/Android/data/<your.package>/files/models/
adb push benchmark_set/ /sdcard/Android/data/<your.package>/files/benchmark_set/
```

which the app reads via `context.getExternalFilesDir(null)`. The app therefore
ships empty and the data is staged by `adb`, which also makes re-runs cheap.

### 3.4 Core inference call

The API shape (from the PyTorch ExecuTorch Android bindings, `org.pytorch.executorch`):

```kotlin
val module = Module.load(pteFile.absolutePath)

fun loadBin(file: File, numEl: Int = 3 * 224 * 224): FloatArray {
    val buf = ByteBuffer.wrap(file.readBytes())
        .order(ByteOrder.LITTLE_ENDIAN).asFloatBuffer()
    return FloatArray(numEl).also { buf.get(it) }
}

val tensor = Tensor.fromBlob(loadBin(binFile), longArrayOf(1, 3, 224, 224))
val logit  = module.forward(EValue.from(tensor))[0].toTensor().dataAsFloatArray[0]
```

Verify these signatures against the 1.4.1 AAR you actually depend on — the above
is the shape our PC-side documentation assumes, not something we have executed on
Android. If the API differs, adapt and note it in your report.

**Read the `.bin` file once, outside the timing loop.** File I/O is not what we
are measuring.

### 3.5 Thread control

Latency depends heavily on thread count, so it must be controlled and reported.
Determine how the 1.4.1 Android runtime sets the number of threads, and measure at
**1 thread and 4 threads** for every model.

If thread count turns out not to be controllable in that version, measure at the
default, and state clearly in your report that the setting was not controllable
and what the default was. Do not guess a number.

---

## 4. The model contract

### 4.1 Input

Every one of the 16 models takes exactly the same input shape:

| Property | Value |
|---|---|
| Shape | `(1, 3, 224, 224)` — NCHW |
| Type | `float32`, little-endian |
| Channel order | RGB |
| Layout in the `.bin` file | CHW, no batch dimension — add the leading `1` at inference |
| Value range | **already normalised** — `/255` then `(x − mean) / std` applied |
| mean | `[0.485, 0.456, 0.406]` |
| std | `[0.229, 0.224, 0.225]` |

The `inputs/*.bin` files are **fully preprocessed**. Feed them straight to the
model. Your harness does not need to implement any image preprocessing for the
main benchmark. (`meta.json` in the bundle carries these same constants
machine-readably; prefer reading it over hardcoding.)

### 4.2 Output

One float: a **raw logit**. Unbounded and frequently negative. Measured across the
reference files in this bundle, values sit between roughly **−6.1 and +2.6** — but
one model (`efficientformerv2_s2__nokd_fold2`) produces an outlier as large as
**+77.4** on one input. Do not assume a bounded range, and do not clamp.

It is not a probability and not a class index.

For parity checking you compare this raw logit directly against the reference —
no transformation at all.

### 4.3 What the `.pte` deliberately does NOT contain

Worth knowing so you don't go looking for it: the file contains no preprocessing,
no `sigmoid`, no decision threshold, and no probability calibration. Converting a
logit into an actual screening decision requires a threshold that is **not 0.5**
and a calibration step, both of which live outside the model.

**None of that is in scope for this task** — it matters only if this work later
grows into a real app, at which point ask us for the model configuration contract.
For benchmarking, the logit is the endpoint.

---

## 5. The 16 models

Four architectures × four training variants each. The variants differ only in how
the model was trained; they are architecturally identical within a row.

| # | `.pte` file | Architecture | Backend | Size (MB) | Expected `max|Δlogit|` (PC) |
|---|---|---|---|---|---|
| 1 | `mobilenetv4_conv_medium__convnextv2_base_fold0.pte` | MobileNetV4-Conv-Medium | xnnpack | 32.11 | 4.13e-06 |
| 2 | `mobilenetv4_conv_medium__efficientnetv2_m_fold4.pte` | MobileNetV4-Conv-Medium | xnnpack | 32.11 | 5.53e-06 |
| 3 | `mobilenetv4_conv_medium__maxvit_base_fold4.pte` | MobileNetV4-Conv-Medium | xnnpack | 32.11 | 3.54e-06 |
| 4 | `mobilenetv4_conv_medium__nokd_fold4.pte` | MobileNetV4-Conv-Medium | xnnpack | 32.11 | 3.92e-06 |
| 5 | `fastvit_sa12__convnextv2_base_fold4.pte` | FastViT-SA12 | xnnpack | 40.35 | 1.70e-05 |
| 6 | `fastvit_sa12__efficientnetv2_m_fold4.pte` | FastViT-SA12 | xnnpack | 40.35 | 2.52e-05 |
| 7 | `fastvit_sa12__maxvit_base_fold4.pte` | FastViT-SA12 | xnnpack | 40.35 | 2.28e-05 |
| 8 | `fastvit_sa12__nokd_fold3.pte` | FastViT-SA12 | xnnpack | 40.35 | 6.30e-05 |
| 9 | `repvit_m1_0__convnextv2_base_fold4.pte` | RepViT-M1.0 | xnnpack | 24.46 | 6.67e-06 |
| 10 | `repvit_m1_0__efficientnetv2_m_fold0.pte` | RepViT-M1.0 | xnnpack | 24.46 | 8.75e-06 |
| 11 | `repvit_m1_0__maxvit_base_fold1.pte` | RepViT-M1.0 | xnnpack | 24.46 | 1.16e-05 |
| 12 | `repvit_m1_0__nokd_fold1.pte` | RepViT-M1.0 | xnnpack | 24.46 | 5.84e-06 |
| 13 | `efficientformerv2_s2__convnextv2_base_fold0.pte` | EfficientFormerV2-S2 | **portable** | 47.98 | 3.41e-05 |
| 14 | `efficientformerv2_s2__efficientnetv2_m_fold4.pte` | EfficientFormerV2-S2 | **portable** | 47.98 | 6.53e-05 |
| 15 | `efficientformerv2_s2__maxvit_base_fold1.pte` | EfficientFormerV2-S2 | **portable** | 47.98 | 1.56e-05 |
| 16 | `efficientformerv2_s2__nokd_fold2.pte` | EfficientFormerV2-S2 | **portable** | 47.98 | 5.57e-04 |

**Benchmark all 16.** Note what to expect from that: because the four models in
each row share an architecture and a backend, their latencies should come out
nearly identical — differing weights do not change the computation graph. That is
not wasted work; it is a **built-in consistency check**. If two models in the same
row differ by more than ~5 % in median latency, something is wrong with the
measurement setup (thermal drift, background load, an ordering effect), and that
is exactly the kind of error a single run per architecture would hide.

Report all 16 individually; do not average within a row.

### 5.1 Why the EfficientFormerV2 rows say "portable"

Those four models could not be lowered to the XNNPACK backend correctly, so they
use ExecuTorch's portable (reference) operator implementations instead. Portable
ops are **substantially slower** — on our server CPU the difference was roughly
70×. Expect these four to be dramatically slower than the other twelve.

**This is expected, not a bug. Do not report it as a failure and do not attempt to
re-export them to XNNPACK.** Just measure them honestly; the slowness is a real
deployment cost that we need quantified.

---

## 6. Procedure

### 6.1 Device conditions — fix before measuring

Airplane mode on · screen on at fixed brightness · no other apps foreground or
background · battery above 50 % and **not charging** (charging changes thermal
behaviour) · device at room temperature, idle for a few minutes before the first
run.

Run all 16 models in one session so they share thermal conditions, and
**randomise or rotate the model order** between repeat runs so that any thermal
drift does not systematically favour whichever model happens to go first.

### 6.2 Record this configuration — a latency number without it is not a measurement

warmup iterations · measured iterations · thread count · batch size (always 1) ·
device model · SoC · ABI · Android version and SDK level · ExecuTorch AAR version
and dependency coordinate · backend per model.

### 6.3 Step A — parity gate (before any timing)

For each model, run all 100 `inputs/*.bin` through it and compare each output
logit against the matching row in `benchmark_set/refs/ref_<model_name>.csv`.

```
required:  max over all 100 samples of |device_logit − reference_logit|  <  1e-3
```

The reference CSV has columns `id,label,source,logit,prob`, 100 data rows plus a
header. Match on `id`, which corresponds to the `.bin` filename (`0042.bin` ↔ id
`0042`, zero-padded to 4 digits). **Compare the `logit` column** (index 3);
ignore `label`, `source`, and `prob`.

⚠️ **The CSV files use CRLF (`\r\n`) line endings**, as does `manifest.csv` — they
were written by Python's `csv` module. A Kotlin parser that splits on `\n` will
leave a trailing `\r` on the last field of every row, and `"0.632290\r".toFloat()`
throws `NumberFormatException`. Use `readLines()` (which handles both), or split
on `\\r?\\n`, or `.trim()` every field. This is a five-minute bug that looks like
a data problem, so it is called out here rather than left to be discovered.

Every model has its **own** reference file, named to match the `.pte` exactly.
Never compare a model against another model's reference — they are different
models and it will fail for reasons that have nothing to do with Android.

**If a model fails the gate, do not time it.** Report the failure with the worst
sample id, the device logit, and the reference logit. A model computing different
numbers is a different model and its speed is meaningless.

The "Expected `max|Δlogit|`" column in §5 is what we measured on PC. Your
on-device values will not match exactly — different CPU, different math library —
but should be the same order of magnitude, i.e. somewhere around 1e-6 to 1e-4. A
value near 1e-2 or larger, or something wild like 1e+10, means something is
broken; stop and report rather than proceeding to timing.

One model is a deliberate exception: **model 16
(`efficientformerv2_s2__nokd_fold2`) clears the gate by only 1.8×** on PC
(5.57e-04 against 1e-3), where every other model clears it by 15× or more. The
cause is benign — that model emits one outlier logit of ≈ +77.4, and absolute
float error grows with magnitude. If this one model lands slightly over 1e-3 on
your device, report the number and flag it rather than treating it as a hard
failure; for the other fifteen, over-tolerance genuinely means something is wrong.

### 6.4 Step B — latency

For each model, at **1 thread and 4 threads**:

- **Cold start** — `Module.load` plus the first `forward`, measured once in a
  fresh process. Report separately; never fold it into the steady-state numbers.
- **Steady state** — at least 30 warmup iterations (discarded), then 100–200
  measured iterations cycling through the 100 inputs. Report **median, p90, p95,
  p99, and mean**. Median and the tail are what matter; a mean alone will not be
  accepted.
- **Sustained / thermal** — run continuously for about 5 minutes and report the
  median of the first minute against the median of the last minute, as a ratio.
  This shows whether the phone throttles. Doing this for **one representative
  model per architecture** (4 runs) is sufficient; it does not need to be done
  for all 16.

### 6.5 Step C — memory

Report **peak PSS** during the steady-state loop — sample
`Debug.MemoryInfo.totalPss` periodically during the run, or read
`adb shell dumpsys meminfo <package>` at peak — plus the `.pte` file size on disk.

Peak memory is the number that decides whether a model is viable on a low-RAM
device, so it matters as much as latency here.

### 6.6 Step D — preprocessing check (optional, only if asked)

Skip this unless we explicitly request it. It exists for the eventual product app,
not for the benchmark: decode `images/<file>`, resize to 224×224, apply `/255` and
the mean/std from `meta.json`, and compare the resulting tensor against the
matching `inputs/<id>.bin`.

If you do run it: **use a loose tolerance.** Android's
`Bitmap.createScaledBitmap` (bilinear) does not produce identical pixels to the
resize used when the `.bin` files were generated. The arrays will differ and that
is expected. The pass criterion is that the final logit moves only slightly and no
prediction flips — not element-wise equality.

---

## 7. Deliverables

### 7.1 One JSON per model per thread setting

32 files total (16 models × 2 thread settings), or 16 files each containing an
array of thread settings — either is fine as long as every number is
unambiguously attributed to a thread count. Conform to
`schema/result.schema.json`:

```json
{
  "pte_file": "repvit_m1_0__maxvit_base_fold1.pte",
  "architecture": "repvit_m1_0",
  "backend": "xnnpack",
  "executorch_version": "1.4.1",
  "executorch_dependency": "<the exact Gradle coordinate you used>",
  "device": "<manufacturer model>",
  "soc": "<chipset>",
  "abi": "arm64-v8a",
  "android_release": "14",
  "android_sdk": 34,
  "threads": 1,
  "warmup_iters": 30,
  "measured_iters": 200,
  "batch_size": 1,
  "parity": {
    "tolerance": 1e-3,
    "max_abs_logit_delta": 0.0,
    "n_over_tolerance": 0,
    "n_samples": 100,
    "worst_sample": { "id": "0000", "device_logit": 0.0, "reference_logit": 0.0 },
    "passed": true
  },
  "latency_ms": { "mean": 0.0, "median": 0.0, "p90": 0.0, "p95": 0.0, "p99": 0.0 },
  "cold_start_ms": 0.0,
  "sustained": {
    "measured": true,
    "duration_s": 300,
    "median_first_min_ms": 0.0,
    "median_last_min_ms": 0.0,
    "throttle_ratio": 1.0
  },
  "peak_pss_mb": 0.0,
  "model_size_mb": 24.46
}
```

Use `"sustained": {"measured": false}` for the 12 models where you skipped it.

### 7.2 A summary table

One Markdown or CSV file: one row per model, columns for architecture, backend,
size, parity result, median@1t, median@4t, p95@4t, cold start, peak PSS.

### 7.3 A short written note

Half a page covering: the device and conditions used, anything that did not work,
whether thread count was controllable, whether the within-row latency consistency
check (§5) held, and any judgement calls you made. If something in this brief
turned out to be wrong or impossible, say so plainly — that is more useful to us
than a workaround we don't know about.

### 7.4 Do not send back

The `.pte` files, the images, or the input tensors — we already have them. Just
results and notes.

---

## 8. Acceptance criteria

1. All 16 models load and pass the parity gate at `< 1e-3`, or every failure is
   reported with concrete numbers.
2. Every latency figure carries device, SoC, thread count, warmup and iteration
   counts.
3. Median **and** tail percentiles reported — not mean alone.
4. Cold start reported separately from steady state.
5. Peak PSS reported for all 16.
6. Within each architecture row, the four variants agree on median latency to
   within about 5 % — or the discrepancy is investigated and explained.
7. No number from an emulator.

---

## 9. Traps

| Trap | Why it bites |
|---|---|
| Using one model's `ref_*.csv` for another | Fails parity for a reason unrelated to Android. Each `.pte` has its own reference file with a matching name. |
| Splitting the reference CSVs on `\n` | They are CRLF. The trailing `\r` breaks `toFloat()` on the last field (§6.3). |
| Assuming logits are small | Most sit in −6.1…+2.6, but one model emits ≈ +77.4 on one input (§4.2). Do not clamp or assume a range. |
| Putting the `.pte` files in `assets/` | 580 MB APK; packaging limits. Use `adb push` to external files dir (§3.3). |
| Timing the `.bin` file read | We are measuring inference, not I/O. Load inputs before the timing loop. |
| Reporting mean latency only | Tail latency is what users feel. Median + p95/p99 required. |
| Folding cold start into the average | Cold start is 1.5–2× steady state and belongs in its own field. |
| Reporting the four EfficientFormerV2 models as broken because they are slow | They use portable ops by design (§5.1). Slow is the expected result. |
| Running an ExecuTorch version other than 1.4.1 | `.pte` is a versioned container. Tell us instead of working around it. |
| Benchmarking on an emulator | Latency numbers are meaningless. Physical arm64-v8a device only. |
| Interpreting a logit as a probability or applying a 0.5 threshold | Out of scope here, and would be wrong — see §4.3. |

---

## 10. When to stop and ask

Contact us rather than improvising if: ExecuTorch 1.4.1 is not obtainable for
Android; any model fails to load; any model fails the parity gate; thread count
cannot be controlled; or the within-row latency consistency check fails and you
cannot find a measurement cause. Every one of these is cheaper for us to resolve
at the source than for you to work around.
