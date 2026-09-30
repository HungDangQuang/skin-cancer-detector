# testing_result — on-device evaluation, Pixel 6a, 2026-09-29

Arm A (`processed224`) of `MOBILE_EVAL_PIPELINE.md`: every image of `dataset_for_mobile_test.zip`
scored on a real phone with the `.pte` from `models_for_mobile_test.zip`, then scored off-device by
the ML repo's `scripts/eval_from_logits.py` — the same program and the same frozen threshold as the
`results_server/` tables.

## Setup

| | |
|---|---|
| Model | `mobilenetv4_ddi_fold0` (`mobilenetv4_conv_medium`, XNNPACK, 33.67 MB) |
| Device | Google Pixel 6a (Tensor G1), arm64-v8a |
| Runtime | `org.pytorch:executorch-android:1.4.0`, 4 threads, batch 1, `LOAD_MODE_FILE` |
| Bundle | `mobile_eval_bundle`, 70,883 rows, manifest SHA-256 `2128e9acc05788b9…` |
| Preprocessing | `BitmapFactory` ARGB_8888 decode, **no resize**, `/255` then `(x − mean) / std`, CHW |
| Threshold | 0.158256247639656 (frozen, from the fold's `val_predictions.csv`; same value as the server tables) |
| Harness | branch `implement-mobile-eval`, `tools/run_eval.sh` |
| Run | 2026-09-29 20:09 → 21:10 (≈ 61 min incl. gate, determinism recheck, summary), ≈ 37.5 ms/image |

## Acceptance criteria (MOBILE_EVAL_TASK.md §7)

| # | Criterion | Result |
|---|---|---|
| 1 | SHA256SUMS | ✅ dataset 70,985/70,985 on the Mac **and** on the phone; models pack 4/4 |
| 2 | `.bin` gate max\|Δ\| < 1e-3 | ✅ **3.338e-06** (100 samples, worst id 000082) |
| 3 | Determinism | ✅ first 500 rows re-scored: **500/500 bit-identical**; 4 threads vs 1 thread: 100/100 bit-identical |
| 4 | Errors < 0.1 % | ✅ **0 / 70,883** |
| 5 | ≥ 7 significant digits | ✅ written with `%.9g` |

Parity of the whole run against the reference logits (`ref_mobilenetv4_ddi_fold0_full.csv`, PyTorch
eager): **max\|Δlogit\| 6.676e-06, 0 rows ≥ 1e-3**.

JPEG decoder (the one divergence never measured before): on the 100 gate images, the logit from the
phone's own JPEG decode + normalisation is **bit-identical** to the logit from the pre-normalised
`.bin` tensor (100/100) — Android's decoder produced exactly the input PIL produced on the host.

## Test metrics on the phone

| Dataset | n | Prevalence | AUPRC | pAUC@TPR80 | AUC-ROC | Sens@90%Spec | Sens@95%Spec | Sensitivity | Specificity | F1 | Brier | ECE |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| `indomain` (ISIC + PAD) | 59,093 | 0.0045 | 0.6182 | 0.1843 | 0.9834 | 0.9585 | 0.9283 | 0.9509 | 0.9366 | 0.1186 | 0.0095 | 0.0436 |
| `ham10000_headline` | 7,470 | 0.1565 | 0.4044 | 0.0956 | 0.8049 | 0.4192 | 0.2335 | 0.9957 | 0.0621 | 0.2824 | 0.3270 | 0.4470 |
| `fitzpatrick17k_headline` | 4,320 | 0.5000 | 0.5963 | 0.0407 | 0.6176 | 0.1778 | 0.1042 | 1.0000 | 0.0009 | 0.6669 | 0.3214 | 0.2862 |

## Phone vs server

- All 36 metric rows: **Δ = 0.0000** at 4 decimals (`scored/vs_server/comparison.md`).
- At full precision (the two `metrics.json`): largest \|Δ\| ≈ **1.4e-07** (HAM10000 pAUC@TPR80 and
  AUC-ROC) — about 40,000× below the project's single-fold noise floor of 0.0053 AUPRC.
- Sensitivity, specificity, F1, Sens@90%Spec, Sens@95%Spec: **exactly equal** on all three datasets.

**Conclusion:** running the model on the phone — ExecuTorch runtime plus Android's JPEG decoding —
does not change the reported quality.

## Caveats (from the models pack README)

1. **Single fold** (fold 0, retrained checkpoint) — not a 5-fold mean ± std; do not place beside the
   Chapter 4 table.
2. **Do not compare AUPRC across datasets** — its baseline is the prevalence (0.45 % … 50 %). Across
   datasets use AUC-ROC / pAUC.
3. HAM10000 specificity 0.06 and Fitzpatrick 0.0009 are properties of the model + threshold on
   out-of-domain data; the server shows the identical values.

## Files

```
testing_result/
  README.md                                    this file
  device_output/                               pulled from the phone (eval_results/)
    mobilenetv4_ddi_fold0.csv                  THE DELIVERABLE: sample_id,logit,error — 70,883 rows
    mobilenetv4_ddi_fold0.json                 run summary: gate, determinism, vs_reference, device, runtime
    gate_mobilenetv4_ddi_fold0.csv             per-image gate: ref, .bin @4t, .bin @1t, JPEG path, deltas
    mobilenetv4_ddi_fold0.csv.fingerprint      manifest + .pte SHA-256 guarding resume
    run_log.txt                                harness log of every session
  scored/                                      produced on the Mac by eval_from_logits.py
    mobile/table.md, mobile/metrics.json       the phone's metric table
    vs_server/comparison.md                    phone − server (PyTorch eager)
    vs_host_executorch/comparison.md           phone − host ExecuTorch
```

## Reproduce the scoring

```bash
cd ~/Documents/skin-cancer-detector
.venv-export/bin/python scripts/eval_from_logits.py \
  --manifest <unzipped>/mobile_eval_bundle/manifest.csv \
  --logits   testing_result/device_output/mobilenetv4_ddi_fold0.csv \
  --threshold 0.158256247639656 --label mobile \
  --runtime "executorch-android-1.4.0(threads=4)" --device "Pixel 6a (Tensor G1)" \
  --out-dir  testing_result/scored/mobile
.venv-export/bin/python scripts/eval_from_logits.py \
  --compare results_server/server/metrics.json testing_result/scored/mobile/metrics.json \
  --out-dir testing_result/scored/vs_server
```

The same command on `reports/mobile_eval/server_logits.csv` reproduces `results_server/server/table.md`
exactly (checked 2026-09-29).
