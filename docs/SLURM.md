# Slurm Training Guide — UIT DGX Cluster

Step-by-step instructions to train the KD pipeline on `slurm.uit.edu.vn`.
Cluster rules from `HuongDanSuDungSlurm.pdf`:

- **Working dir**: `/datastore/keg/hungdang` (NOT `/home/${USER}` — 30 GB hard limit). Override with `DATASTORE_USER_DIR=...` if your account/path differs.
- **Limits**: 20 MPS, 5 concurrent jobs, 32 vCPU, 72 h max per job
- **vRAM**: declared via `REQUIRED_VRAM` arg to `acquire_gpu`; < 44000 MB on L40, < 80000 MB on A100
- **GPU dispatch**: `gpu_check.sh` returns the best free GPU; codes 10 (requeue) / 11 (fatal after 5 retries)

---

## File layout under `slurm/`

| File | Purpose | Where to run |
|---|---|---|
| `setup_env.sh` | Build the venv, install deps, create `logs/` | login node |
| `preflight.sh` | Verify env + run a tiny smoke test | login node |
| `submit.sh` | sbatch wrapper — guarantees `logs/` exists, forwards env vars | login node |
| `_lib.sh` | Shared bash library (sourced by every `*.slurm`) | inside jobs |
| `01_prepare_poc.slurm` | Generate synthetic POC fixtures (CPU-only) | sbatch |
| `02_poc_teacher.slurm` | POC teacher (2 epochs) | sbatch |
| `03_poc_student.slurm` | POC KD student (2 epochs) | sbatch |
| `10_prepare_data.slurm` | Real ISIC 2024 preprocessing + 5-fold splits | sbatch |
| `11_train_teacher.slurm` | Full teacher (50 epochs), `TEACHER=` selects backbone | sbatch |
| `12_train_student.slurm` | Full KD student dispatcher, `STUDENT=`/`TEACHER=` | sbatch |
| `13_ablation_sampler.slurm` | Ablation A — undersampler `SAMP=off\|3\|5\|10` (KD, reuses teacher) | sbatch |
| `14_ablation_pad.slurm` | Ablation B — `ARM=isic_only\|isic_pad` (baseline, identical test) | sbatch |
| `20_evaluate.slurm` | Evaluate any checkpoint | sbatch |
| `21_benchmark_mobile.slurm` | Mobile deployability: params + FP32 size + CPU latency (CPU only) | sbatch |
| `24_benchmark.slurm` | Full compute profile: params + FLOPs + size + CPU/GPU latency + throughput | sbatch |
| `26_make_benchmark_set.slurm` | Build the fixed benchmark input set (images + tensors + ref logits) from test split | sbatch |
| `23_export_model.slurm` | Export a checkpoint to ONNX / TorchScript (CPU only) | sbatch |
| `25_export_executorch.slurm` | Export a checkpoint to ExecuTorch `.pte` for Android (CPU only, isolated venv) | sbatch |
| `_template.slurm` | Copy-and-customize starting point | reference |

**Key invariant**: every `*.slurm` script begins with `source "${SLURM_SUBMIT_DIR}/slurm/_lib.sh"`. The library handles `set -euo pipefail`, `mkdir -p logs`, **fallback `tee` log** at `logs/<job>_<jobid>_runtime.log` (so output survives even if SBATCH redirect fails), diagnostic header, and helper functions `load_python_env`, `acquire_gpu`, `setup_mps`.

---

## 0. Connect

```bash
ssh ${USER}@slurm.uit.edu.vn          # VPN first if off-campus

cd /datastore/keg/hungdang
git clone https://github.com/HungDangQuang/skin-cancer-detector.git
cd skin-cancer-detector
git checkout feature/poc
```

Or, if already cloned:
```bash
cd /datastore/keg/hungdang/skin-cancer-detector
git fetch && git checkout feature/poc && git pull
```

---

## 1. One-time setup (login node)

```bash
bash slurm/setup_env.sh        # creates /datastore/keg/hungdang/venv + installs deps
bash slurm/preflight.sh        # verifies the env + runs a 5-image smoke test
```

`preflight.sh` is the most useful debugging tool — it runs the actual data-prep code without Slurm so any environment / dependency / path bug surfaces immediately.

Expected end of `preflight.sh`:
```
=== All checks passed. Ready to submit jobs. ===
Next: bash slurm/submit.sh slurm/01_prepare_poc.slurm
```

---

## 2. POC pipeline (synthetic data, ~30 min total)

```bash
bash slurm/submit.sh slurm/01_prepare_poc.slurm
# → wait for "Submitted batch job <ID>"
# → tail -f logs/prepare_poc_<ID>.out

bash slurm/submit.sh slurm/02_poc_teacher.slurm
# Different teacher arch (e.g. smoke-test a SOTA teacher before a full run):
bash slurm/submit.sh slurm/02_poc_teacher.slurm TEACHER=convnextv2_base

bash slurm/submit.sh slurm/03_poc_student.slurm
# Different student arch:
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv4_conv_medium
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=efficientformerv2_s2
# Smoke-test a SOTA pair (TEACHER must match the one POC-trained above):
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv4_conv_medium TEACHER=convnextv2_base
```

**Always submit via `submit.sh`, not raw `sbatch`** — it ensures `logs/` exists before sbatch parses the `--output` directive (Slurm 23 silently drops output if the parent dir is missing).

---

## 3. Full pipeline (real ISIC 2024)

### 3.1 Upload raw data
```bash
# from your laptop:
rsync -avh --progress isic2024/ ${USER}@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/data/raw/isic2024/
```
Required structure:
```
data/raw/isic2024/
├── train-image.hdf5
└── train-metadata.csv
```

**Optional — add PAD-UFES-20** (extra malignant samples; `prepare_data.py`
auto-detects it and concatenates it into every fold). Download the "Download
all" bundle in a browser from [data.mendeley.com/datasets/zr7vgbcyr2/1](https://data.mendeley.com/datasets/zr7vgbcyr2/1)
(Mendeley gates the bundle behind a browser session — there is no clean curl),
rsync it into the repo's data area on the cluster, then stage it:
```bash
# from your laptop, after the browser download (Kaggle mirror works too):
rsync -avh --progress ~/Downloads/zr7vgbcyr2-1.zip \
  ${USER}@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/data/raw/
# on the cluster LOGIN node, from the repo root (just unzip work, not a GPU job):
bash scripts/setup_pad_ufes_20.sh data/raw/zr7vgbcyr2-1.zip
```
`setup_pad_ufes_20.sh` extracts the nested `imgs_part_*.zip` archives and
consolidates everything into the layout the preprocessing reads:
```
data/raw/pad_ufes_20/
├── metadata.csv      # cols: img_id, diagnostic
└── images/           # <img_id>.png  (≈2298 files)
```
> 💽 The bundle is ~3–4 GB and the shared volume is tight. The helper stages
> in-place (moves, not `/tmp` copies) to halve peak usage; if you're still short
> on space, pass `--rm-zip` to delete the source zip the moment staging
> succeeds: `bash scripts/setup_pad_ufes_20.sh data/raw/zr7vgbcyr2-1.zip --rm-zip`.
> Check headroom first with `df -h .`. A `No space left on device` mid-copy
> leaves a partial `images/` — `rm -rf data/raw/pad_ufes_20/images` and retry.
> ⚠️ Adding PAD-UFES-20 changes the concatenated dataframe, so **all fold CSVs
> and `test_split.csv` are regenerated** in §3.2 — any existing teacher/student
> checkpoints were trained on the old splits and must be retrained.

### 3.2 Preprocess + 5-fold splits
```bash
bash slurm/submit.sh slurm/10_prepare_data.slurm
```
Drops corrupt / too-small / blank / exact-duplicate images (logged to `data/processed/<dataset>/excluded_images.csv`) and writes patient-grouped 5-fold splits + `test_split.csv`. The quality filter re-runs on already-on-disk images, so warm re-runs still decode every image (not instant). Spec: [`PREPROCESSING.md`](PREPROCESSING.md).

### 3.3 Train teacher
Pick the teacher with `TEACHER=` (default `efficientnetv2_m`).
```bash
bash slurm/submit.sh slurm/11_train_teacher.slurm                              # default efficientnetv2_m
bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=convnextv2_base
bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=maxvit_base
```
Output: `experiments/runs/teacher/<TEACHER>/fold_{0..4}/`.

### 3.4 KD-train students
`STUDENT=` picks the student, `TEACHER=` picks which trained teacher to distill from
(must already be trained in §3.3 with the same `TEACHER`). Run-dir is
`experiments/runs/kd_<TEACHER>_to_<STUDENT>/fold_{0..4}/`.

Students (mobile-/on-device-latency-optimized), distilling from a trained teacher:
```bash
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12            TEACHER=efficientnetv2_m
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2    TEACHER=efficientnetv2_m
```
KD variants (opt-in, default behaviour unchanged): add `EXTRA="training.distillation.soft_loss_type=mse run_suffix=__mselogit"`
for MSE-on-logit KD, or `TRAINING=distillation_rkd` for RKD feature-KD.
> Model sets — **teachers** `{efficientnetv2_m, convnextv2_base, maxvit_base}`,
> **students** `{mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2}`.
> All 6 need `timm>=1.0` — re-run `slurm/setup_env.sh` after pulling.

### 3.4b Anti-overfitting knobs (`AUG`, `DROP_PATH`)
`11_train_teacher` and `12_train_student` accept two opt-in env vars (defaults
reproduce the original behavior, so existing runs are unchanged):
- `AUG=light|heavy` (default `light`) → `augmentation=<AUG>`; `heavy` is the
  stronger anti-overfit pipeline (see docs/PREPROCESSING.md §4.1).
- `DROP_PATH=<float>` (default `0.0`) → stochastic depth on the student (script 12)
  or teacher (script 11). Recommended student ~0.1, teacher/ViT ~0.2. Verify the
  backbone accepts the kwarg on the cluster first.
- `EXTRA="<hydra overrides>"` (default empty) → space-separated Hydra overrides
  forwarded verbatim (word-split at the call site — pass as one quoted arg). For
  `maxvit_base`'s cuDNN backward error: `EXTRA="cudnn_deterministic=false training.batch_size=16"`.
  Also on the POC scripts `02`/`03`.
```bash
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium AUG=heavy DROP_PATH=0.1
bash slurm/submit.sh slurm/11_train_teacher.slurm  TEACHER=convnextv2_base   AUG=heavy DROP_PATH=0.2
bash slurm/submit.sh slurm/11_train_teacher.slurm  TEACHER=maxvit_base EXTRA="cudnn_deterministic=false training.batch_size=16"
```
Each fold also writes `val_metrics.json` (best-epoch val metrics) → compute the
**val − test** gap (esp. AUPRC/pAUC) as the overfitting signal.

### 3.4c Metadata knobs (`META_COLS`, `PRIVILEGED`) — direction A/D
Opt-in, default off (image-only runs byte-for-byte unchanged). See
`docs/metadata_training_plan.md`.
- `META_COLS=<c1,c2,...>` (comma-separated, **no spaces**; `iddx_*`/`mel_*`
  rejected as post-biopsy leakage). On `10_prepare_data` it carries those columns
  into the split CSVs. Splits are seed-deterministic, so adding columns doesn't
  change rows/order — existing checkpoints stay valid.
- **Direction D** (subgroup calibration, no retrain): prepare with
  `META_COLS=anatom_site_general,sex`, re-run eval, then
  `python scripts/compute_calibration.py --run-dir <run> --subgroup anatom_site_general`.
- **Direction A** (privileged/LUPI teacher): `PRIVILEGED=1` on `11`/`12` sets
  `data.metadata_as_input=true data.metadata_cols=[$META_COLS]`. The teacher
  (`TEACHER=<name>_privileged`) fuses image ⊕ tabular `tbp_lv_*`; the student
  stays image-only and distills the fused structure via RKD
  (`TRAINING=distillation_privileged`), so `.pte`/benchmark are unchanged. Use the
  SAME `META_COLS` for prepare + both training steps (the dataset raises `KeyError`
  otherwise). Fold loops run under `set -f` so the `[...]` list token reaches Hydra
  verbatim.
```bash
# Direction A end-to-end (privileged-vs-plain ablation on the same student):
bash slurm/submit.sh slurm/10_prepare_data.slurm META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=efficientnetv2_m_privileged PRIVILEGED=1 META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m_privileged TRAINING=distillation_privileged PRIVILEGED=1 META_COLS=tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color
# -> experiments/runs/kd_efficientnetv2_m_privileged_to_mobilenetv4_conv_medium/ (vs the plain kd_..._to_... run)
```

### 3.5 Controlled comparison (no KD)
```bash
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium    TRAINING=baseline
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium  TRAINING=baseline
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2        TRAINING=baseline
```

### 3.6 Data-strategy ablations (prove PAD mixing + the sampler help)
Single-variable ablations so the data strategy is *measured*, not assumed. Each
is a 5-fold array; aggregate with `22_aggregate_folds.slurm` and compare with the
`eval-results` skill (reference/analyze-evaluation.md). The new `test_metrics.json` carries `auprc` +
`sens_at_90/95spec`; `predictions.csv` carries a `source` column for ISIC-vs-PAD
per-domain breakdowns.

```bash
# A) Sampler (KD MobileNetV4 student, teacher reused; ratio-5 == the main run):
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=off   # natural ~1018:1
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=3
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=10

# B) PAD mixing (baseline so the teacher can't leak PAD via soft labels;
#    ISIC-only vs ISIC+PAD on the IDENTICAL combined held-out test):
bash slurm/submit.sh slurm/14_ablation_pad.slurm ARM=isic_only
bash slurm/submit.sh slurm/14_ablation_pad.slurm ARM=isic_pad
```

`13` overrides `data.use_weighted_sampler`/`data.undersample_ratio` + `run_suffix`;
`14` overrides `data.train_sources` (filters TRAIN+VAL only) + `run_suffix`. Both
land in isolated run-dirs (`…__samp_off`, `…__train_isic_only`, …) so the main 30
runs are never overwritten.

---

## 4. Evaluation

```bash
bash slurm/submit.sh slurm/20_evaluate.slurm \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/checkpoints/best_model.pth \
    OUT=reports/results/kd_b0.json
```

Metrics JSON contains: `pauc_at_tpr80` (primary), `auc_roc`, `sensitivity`, `specificity`, `f1_score`, threshold (Youden's J), TP/FP/TN/FN.

### Mobile deployability benchmark

Params + FP32 size + single-core CPU latency are architecture-level (weight-independent), so benchmark one checkpoint per architecture, any fold. CPU-only — no GPU:

```bash
bash slurm/submit.sh slurm/21_benchmark_mobile.slurm \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
```

Output (default `reports/mobile_benchmark/<MODEL>.json`): `params_millions`, `fp32_size_mb`, `cpu_latency_ms_median`, `cpu_latency_ms_p90`, `image_size`. INT8/TFLite quantization is de-scoped — FP32 backbones run as-is.

### Full compute profile (PC + device-independent)

`24_benchmark.slurm` is the superset for the thesis deployment story: adds FLOPs/MACs, GPU latency, a batch-throughput sweep, and percentile latencies (p90/p95/p99). CPU @ batch=1 (single-thread, phone-comparable) is always measured; GPU numbers added when a GPU is allocated. One checkpoint per architecture, any fold:

```bash
# With GPU:
bash slurm/submit.sh slurm/24_benchmark.slurm \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
# CPU-only: add DEVICE=cpu   |   custom sweep: BATCH_SIZES="1 16 64"
```

Output (default `reports/benchmark/<MODEL>.json`) adds `gflops`, `gmacs`, `trainable_params_millions`, `latency_batch1.{cpu,cuda}`, `throughput.{cpu,cuda}` (images/sec + peak GPU mem), `device_info`. All FP32.

### Fixed benchmark input set

`26_make_benchmark_set.slurm` builds one reproducible set of test samples reused for PC latency, mobile latency, and the parity check (proposal pins no benchmark dataset → uses the internal test split = smartphone-like deployment domain). Preprocessing identical to eval (`build_transforms(cfg,"val")`). CPU-only:

```bash
bash slurm/submit.sh slurm/26_make_benchmark_set.slurm N=100
# + reference logits for parity: MODEL=mobilenetv4_conv_medium CKPT=.../best_model.pth
```

Output `data/benchmark_set/` (rsync, don't commit): `images/` (originals → parity layer 2), `inputs/<id>.bin` (preprocessed float32 CHW → parity layer 1), `inputs.npy`, `manifest.csv`, `meta.json`, `ref_<model>.csv`. Seeded + label-stratified (oversamples rare malignant).

### Export for deployment (ONNX / TorchScript)

```bash
bash slurm/submit.sh slurm/23_export_model.slurm \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
# Optional: FORMAT=torchscript (default onnx), OUT=exports/<name>, CONFIG=<path>
```

CPU-only (no `--gres`). Produces `exports/<name>.onnx` (or `.pt`); `CONFIG` defaults to the run's saved `config.yaml` so the ONNX dummy input uses the trained `image_size`. The model emits one raw logit → apply `sigmoid()` then the **Youden threshold from that fold's `test_metrics.json`** (not 0.5). Export the **student**, not the teacher. Research/thesis model, not a validated medical device.

### Export to ExecuTorch (.pte) for Android on-device

Runs the student **as-is** on Android via PyTorch-native ExecuTorch — no TFLite/TF conversion. ExecuTorch pins its own torch build → **isolated venv** `${DATASTORE_USER_DIR}/venv-export`, created once on the login node so it can't perturb the training `torch>=2.2`:

```bash
bash slurm/setup_export_env.sh        # one-time, login node (separate from setup_env.sh)
bash slurm/submit.sh slurm/25_export_executorch.slurm \
    MODEL=mobilenetv4_conv_medium \
    CKPT=experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
# BACKEND=none = portable-ops fallback; OUT defaults to exports/executorch/<MODEL>.pte
```

Uses `torch.export` (handles transformer students that `torch.jit.script` fails on); default lowers to the XNNPACK delegate. The slurm script sources `_lib.sh` for strict-mode/logging but activates `venv-export` directly (NOT `load_python_env`). **Mandatory on-device parity check** (max|Δlogit| <1e-3) before trusting any number.

---

## 5. Resource budget

| Script | mps | mem | vRAM | time | Notes |
|---|---|---|---|---|---|
| `01_prepare_poc` | none | 4 G | — | 15 m | CPU only |
| `02_poc_teacher` | 2 | 8 G | 12 G | 1 h | 2 epochs; `TEACHER=` (covers SOTA teachers) |
| `03_poc_student` | 2 | 8 G | 14 G | 1 h | T+S in memory; `STUDENT=`/`TEACHER=` |
| `10_prepare_data` | none | 16 G | — | 4 h | HDF5 decode |
| `11_train_teacher` | 4 | 16 G | 20 G | 24 h | teacher (B4 / SOTA), batch 32 |
| `12_train_student` | 4 | 16 G | 22 G | 18 h | KD, frozen teacher + student, batch 64 |
| `13_ablation_sampler` | 4 | 16 G | 22 G | 18 h | KD student, teacher reused; per arm × 5 folds |
| `14_ablation_pad` | 4 | 16 G | 12 G | 18 h | baseline student (no teacher); per arm × 5 folds |
| `20_evaluate` | 1 | 8 G | 6 G | 1 h | inference |
| `21_benchmark_mobile` | none | 4 G | — | 15 m | CPU only, single-thread latency |
| `24_benchmark` | 1 | 8 G | 4 G | 30 m | CPU always; GPU latency/throughput when `DEVICE≠cpu` |
| `26_make_benchmark_set` | none | 8 G | — | 20 m | CPU only, fixed benchmark input set from test split |
| `23_export_model` | none | 8 G | — | 20 m | CPU only, ONNX/TorchScript export |
| `25_export_executorch` | none | 8 G | — | 30 m | CPU only, ExecuTorch `.pte`, isolated venv-export |

Peak MPS at 3 students in parallel: 12 of 20 limit.

---

## 6. Tracking jobs

```bash
squeue -u ${USER}                    # your jobs (PD/R/CG)
squeue -j <jobid>                    # specific job
scontrol show job <jobid>            # detailed (only while job is alive)
sacct -j <jobid> --format=JobID,JobName,State,Elapsed,MaxRSS,ExitCode,WorkDir
                                     # postmortem (after job ends)
scancel <jobid>                      # kill a job

# Live logs
tail -f logs/poc_teacher_<jobid>.out   # stdout
tail -f logs/poc_teacher_<jobid>.err   # stderr
tail -f logs/poc_teacher_<jobid>_runtime.log   # fallback (always written)

# Quick interactive GPU check
srun --gres=mps:l40:1 --time=00:05:00 --pty nvidia-smi
```

---

## 7. Troubleshooting

| Symptom | Root cause / Fix |
|---|---|
| `sbatch` printed a job ID, but `logs/<jobname>_<id>.out` is empty/missing and `squeue` shows nothing | `logs/` didn't exist when sbatch parsed the `--output` directive. **Always submit via `bash slurm/submit.sh ...`** — it does `mkdir -p logs` first. Also check `logs/<jobname>_<id>_runtime.log` (fallback tee log written by `_lib.sh`). |
| Job exited with code 10 in log | `gpu_check.sh` couldn't find a free GPU — Slurm requeues. Just wait. |
| Job exited with code 11 in log | 5× requeue exhausted. Lower `REQUIRED_VRAM` (the arg to `acquire_gpu` in the script) or wait for cluster to free up. |
| `module: command not found` in log | You ran the `*.slurm` script directly (`bash slurm/02_poc_teacher.slurm`) instead of `sbatch …`. Modules are only available on Slurm-allocated nodes. |
| `ERROR: venv missing at /datastore/<user>/venv` | Run `bash slurm/setup_env.sh` on the login node. |
| `import` errors in the runtime log | Re-run `slurm/setup_env.sh`, then `slurm/preflight.sh` to confirm. |
| `gpu_check.sh: not found` | Helper isn't installed on this node — confirm you're on a compute node (the `_lib.sh` diagnostic header prints `Hostname:`). Login node has no helper and no GPUs. |
| `Disk quota exceeded` on `/home` | Move data to `/datastore/keg/hungdang` (30 GB cap on `/home`). |

---

## 8. End-to-end checklist

- [ ] Connected to `slurm.uit.edu.vn`
- [ ] Repo at `/datastore/keg/hungdang/skin-cancer-detector`, branch `feature/poc`
- [ ] `bash slurm/setup_env.sh` succeeded
- [ ] `bash slurm/preflight.sh` ended with **All checks passed**
- [ ] POC: `01 → 02 → 03` finished, `experiments/poc/.../best_model.pth` exists
- [ ] Real data uploaded under `data/raw/isic2024/`
- [ ] `10_prepare_data` finished, splits exist
- [ ] `11_train_teacher` finished
- [ ] `12_train_student` finished for 3 students × {KD, baseline}
- [ ] `20_evaluate` produced metric JSONs
