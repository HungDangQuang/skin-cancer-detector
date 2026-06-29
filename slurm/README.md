# Slurm runbook — UIT cluster (`slurm.uit.edu.vn`)

Step-by-step to run the project on the UIT cluster. For deeper background see [`../docs/SLURM.md`](../docs/SLURM.md); for failure-mode diagnosis see the `diagnose-training` skill.

## File map

| File | Role | Where it runs |
|---|---|---|
| `setup_env.sh` | **First-time only** — create venv at `/datastore/keg/hungdang/venv` and install deps | login node |
| `preflight.sh` | Verify env + tiny CPU smoke test before submitting | login node |
| `submit.sh` | sbatch wrapper — does `mkdir -p logs` first, forwards `VAR=value` | login node |
| `_lib.sh` | Shared bash library sourced by every `*.slurm` (strict mode, tee log, helpers) | inside jobs |
| `_template.slurm` | Copy-and-customize starting point | reference |
| `01_prepare_poc.slurm` | Synthetic POC fixtures (CPU only) | sbatch |
| `02_poc_teacher.slurm` | POC teacher, 2 epochs | sbatch |
| `03_poc_student.slurm` | POC KD student, 2 epochs | sbatch |
| `10_prepare_data.slurm` | Real ISIC 2024 preprocessing + 5-fold splits | sbatch |
| `11_train_teacher.slurm` | Full teacher (50 epochs), `TEACHER=` selects backbone | sbatch |
| `12_train_student.slurm` | Full KD student, `STUDENT=`/`TEACHER=` | sbatch |
| `13_ablation_sampler.slurm` | Data-strategy ablation A — sampler `SAMP=off\|3\|5\|10` (KD, reuses teacher) | sbatch |
| `14_ablation_pad.slurm` | Data-strategy ablation B — `ARM=isic_only\|isic_pad` (baseline, identical test) | sbatch |
| `20_evaluate.slurm` | Evaluate any checkpoint | sbatch |
| `21_benchmark_mobile.slurm` | Mobile deployability: params + FP32 size + CPU latency (CPU only) | sbatch |
| `24_benchmark.slurm` | Full compute profile: params + FLOPs + size + CPU/GPU latency + throughput | sbatch |
| `26_make_benchmark_set.slurm` | Build the FIXED benchmark input set (images + preprocessed tensors + ref logits) from the test split | sbatch |
| `23_export_model.slurm` | Export a checkpoint to ONNX / TorchScript for deployment (CPU only) | sbatch |
| `25_export_executorch.slurm` | Export a checkpoint to ExecuTorch `.pte` for Android on-device (CPU only, **isolated venv**) | sbatch |

**Working dir on cluster:** `/datastore/keg/hungdang/skin-cancer-detector`. Override with `DATASTORE_USER_DIR=...` if your account is elsewhere.

---

## What to re-run when

| Situation | Re-run |
|---|---|
| **Reconnecting after a previous session** (most common) | Nothing in `slurm/`. Just SSH, `cd`, `git pull`, `bash slurm/submit.sh …`. |
| **First time ever on this cluster account** | §1 `setup_env.sh` (creates venv) → §2 `preflight.sh` (smoke test). |
| **After `git pull` brings new code** | Optional: `bash slurm/preflight.sh` to confirm Python imports still resolve (30 s). |
| **After `requirements.txt` changes** | `bash slurm/setup_env.sh` (re-runs `pip install -r requirements.txt` on the existing venv). |
| **`venv` got corrupted** (e.g. `ModuleNotFoundError` returns) | `rm -rf /datastore/keg/hungdang/venv && bash slurm/setup_env.sh`. |

The venv at `/datastore/keg/hungdang/venv` and the cloned repo live on persistent storage — they survive SSH disconnects, reboots, and weeks of you not logging in.

---

## 0. Connect

```bash
ssh keg@slurm.uit.edu.vn              # VPN first if off-campus
cd /datastore/keg/hungdang/skin-cancer-detector
git pull
```

If cloning fresh (first time):
```bash
mkdir -p /datastore/keg/hungdang && cd /datastore/keg/hungdang
git clone https://github.com/HungDangQuang/skin-cancer-detector.git
cd skin-cancer-detector && git checkout feature/poc
```

---

## Returning user — just submit

If §1 was done previously and the venv at `/datastore/keg/hungdang/venv` exists, skip to §3 (POC) or §4 (full pipeline). A typical reconnect session:

```bash
ssh keg@slurm.uit.edu.vn
cd /datastore/keg/hungdang/skin-cancer-detector
git pull
bash slurm/submit.sh slurm/<script>.slurm [VAR=value ...]
tail -f logs/<jobname>_<jobid>_runtime.log
```

That's it. No setup, no preflight, no venv-activation needed — the slurm scripts source `_lib.sh` which activates the venv inside each job automatically.

---

## 1. First-time environment setup (login node) — ONE TIME

Only on a fresh account, or after `rm -rf /datastore/keg/hungdang/venv`. Skip this section on reconnects.

```bash
bash slurm/setup_env.sh
```

Creates `/datastore/keg/hungdang/venv`, installs `requirements.txt`, and verifies CUDA. Expected last line:

```
torch: 2.x.x | cuda available: True
Setup complete.
```

If `cuda available: False`, install a torch wheel that matches the cluster's CUDA driver (currently 12.8):
```bash
source /datastore/keg/hungdang/venv/bin/activate
pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

## 2. Preflight (login node) — optional but recommended after pulls

```bash
bash slurm/preflight.sh
```

Verifies working dir, venv, modules, Python imports, and runs a 5+2 synthetic-image smoke test (~30 seconds total). Expected last line:

```
=== All checks passed. Ready to submit jobs. ===
```

Fix any `[FAIL]` line before continuing. `[WARN]` lines are informational (e.g. `gpu_check.sh` is correctly absent on the login node).

---

## 3. POC pipeline (synthetic data — ~30 min total)

Run in order. Each step depends on the previous one's output.

### 3.1 Generate synthetic data (~1 min, CPU)

```bash
bash slurm/submit.sh slurm/01_prepare_poc.slurm
```

Wait for completion, then verify:
```bash
ls data/processed/poc/{benign,malignant} | head
ls data/splits/poc/fold_0/
```

### 3.2 POC teacher (~5–15 min, GPU)

```bash
bash slurm/submit.sh slurm/02_poc_teacher.slurm
# Different teacher arch (smoke-test a SOTA teacher before a full run):
bash slurm/submit.sh slurm/02_poc_teacher.slurm TEACHER=convnextv2_base
# note the "Submitted batch job <jobid>" line, then:
tail -f logs/poc_teacher_<jobid>_runtime.log
```

Done when the log ends with:
```
[INFO] Teacher training complete. Checkpoint: experiments/poc/teacher/efficientnet_b4/checkpoints/best_model.pth
[job] DONE
```

Verify before moving on:
```bash
ls -lh experiments/poc/teacher/efficientnet_b4/checkpoints/best_model.pth
```

### 3.3 POC KD student (~5–10 min, GPU)

```bash
bash slurm/submit.sh slurm/03_poc_student.slurm
# Different student arch:
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv3_large
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilevit_s
# SOTA pair (TEACHER must match the one POC-trained in 3.2 first):
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=mobilenetv4_conv_medium TEACHER=convnextv2_base
```

Verify:
```bash
ls -lh experiments/poc/kd_efficientnet_b4_to_efficientnet_b0/checkpoints/best_model.pth
```

---

## 4. Full pipeline (real ISIC 2024)

### 4.1 Get raw data onto the server

**Option A — Kaggle CLI on the server** (recommended; no local download/upload):
```bash
# One-time: drop your kaggle.json at ~/.kaggle/kaggle.json (chmod 600)
# Then accept the competition rules in the browser, and:
source /datastore/keg/hungdang/venv/bin/activate
pip install kaggle
cd /datastore/keg/hungdang/skin-cancer-detector/data/raw/isic2024
kaggle competitions download -c isic-2024-challenge
unzip -q isic-2024-challenge.zip
rm isic-2024-challenge.zip
rm -rf train-image/ test-image/ test-image.hdf5  # keep only the HDF5 + CSV
```

**Option B — rsync from laptop**:
```bash
ssh keg@slurm.uit.edu.vn "mkdir -p /datastore/keg/hungdang/skin-cancer-detector/data/raw/isic2024"
rsync -avh --progress --partial \
    ~/Downloads/isic-2024-challenge.zip \
    keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/data/raw/isic2024/
# Then SSH in, unzip as in Option A.
```

Required structure under `data/raw/isic2024/`: `train-image.hdf5`, `train-metadata.csv`.

### 4.2 Preprocess + 5-fold splits (~45 min cold — idempotent)
```bash
bash slurm/submit.sh slurm/10_prepare_data.slurm
```
The script skips re-**writing** images whose JPG already exists on disk. Note: it still re-**reads** every image on a warm re-run, because the quality filter (corrupt / too-small / blank / exact-duplicate) and dedup re-run on the on-disk copies too — so a re-run after the filter changed will clean a previously-unfiltered dataset, but warm runs are **not** trivially fast. Dropped images are logged per dataset to `data/processed/<dataset>/excluded_images.csv`, and PAD `patient_id`s are namespaced (`pad_…`) so they can't collide with ISIC across folds. Full cleaning + augmentation spec: [`docs/PREPROCESSING.md`](../docs/PREPROCESSING.md).

### 4.3 Teacher (~24 h, GPU)
`TEACHER=` selects the backbone (default `efficientnet_b4`). SOTA set needs `timm>=1.0`.
```bash
bash slurm/submit.sh slurm/11_train_teacher.slurm                            # baseline B4
bash slurm/submit.sh slurm/11_train_teacher.slurm TEACHER=efficientnetv2_m   # SOTA: also convnextv2_base, maxvit_base
```

### 4.4 Students × {KD, baseline} (~18 h each)
`STUDENT=` picks the student; for KD, `TEACHER=` picks which trained teacher to distill from
(default B4). Run-dir: `kd_<TEACHER>_to_<STUDENT>/`.
```bash
# KD — baseline backbones (default teacher B4)
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv3_large
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilevit_s
# KD — SOTA students (mobile-latency-optimized) from a SOTA teacher
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv4_conv_medium TEACHER=efficientnetv2_m
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=fastvit_sa12            TEACHER=efficientnetv2_m
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientformerv2_s2    TEACHER=efficientnetv2_m
# Baseline (no KD)
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=efficientnet_b0    TRAINING=baseline
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilenetv3_large  TRAINING=baseline
bash slurm/submit.sh slurm/12_train_student.slurm STUDENT=mobilevit_s        TRAINING=baseline
```

### 4.5 Data-strategy ablations (prove PAD mixing + sampler help)

Controlled single-variable ablations that turn the data strategy from an
*assumption* into a *measured* result. Each kicks off a 5-fold array; aggregate
each run-dir with `22_aggregate_folds.slurm`, then compare with
`analyze-evaluation`. Prereq for the sampler ablation: a trained teacher (§4.3).

```bash
# A) SAMPLER — best student (KD MobileNetV3), vary ONLY the undersampler.
#    Reuses the existing teacher; ratio-5 == the main run (already trained).
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=off    # no resampling (natural ~1018:1)
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=3      # 1:3
bash slurm/submit.sh slurm/13_ablation_sampler.slurm SAMP=10     # 1:10
# -> experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large__{samp_off,ratio3,ratio10}/

# B) PAD mixing — baseline (no KD, so the teacher can't leak PAD via soft labels),
#    train ISIC-only vs ISIC+PAD, judged on the IDENTICAL combined held-out test.
bash slurm/submit.sh slurm/14_ablation_pad.slurm ARM=isic_only
bash slurm/submit.sh slurm/14_ablation_pad.slurm ARM=isic_pad
# -> experiments/runs/baseline_mobilenetv3_large__train_{isic_only,isic_pad}/
#    Per-domain (ISIC vs PAD) split comes from predictions.csv's `source` column.
```

Both write `test_metrics.json` (now incl. `auprc`, `sens_at_90spec`,
`sens_at_95spec`), `val_metrics.json` (best-epoch val metrics — for the
val−test overfitting gap), and `predictions.csv` (`y_true,y_prob,y_pred,source`)
per fold.

**Anti-overfitting knobs** (`AUG`, `DROP_PATH` env vars — single-token, forwarded
by `submit.sh`):

```bash
# Stronger augmentation + stochastic depth on a student run:
bash slurm/submit.sh slurm/12_train_student.slurm \
    STUDENT=mobilenetv3_large AUG=heavy DROP_PATH=0.1
# Teacher with stochastic depth:
bash slurm/submit.sh slurm/11_train_teacher.slurm \
    TEACHER=convnextv2_base AUG=heavy DROP_PATH=0.2
```

**`EXTRA=` passthrough** (`11/12/02/03`) — space-separated Hydra overrides
forwarded verbatim (word-split at the call site; pass as **one quoted** arg). Use
it for `maxvit_base`'s cuDNN backward error (see CLAUDE.md gotcha):

```bash
bash slurm/submit.sh slurm/11_train_teacher.slurm \
    TEACHER=maxvit_base EXTRA="cudnn_deterministic=false training.batch_size=16"
```

Both default to `AUG=light` + `DROP_PATH=0.0` (original behavior), so existing
runs are unchanged unless you pass these. `DROP_PATH` maps to the student's
(script 12) or teacher's (script 11) `drop_path_rate`; verify the backbone
accepts it on the cluster before a full run.

---

## 5. Evaluate a checkpoint

```bash
bash slurm/submit.sh slurm/20_evaluate.slurm \
    MODEL=efficientnet_b0 \
    CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/checkpoints/best_model.pth \
    OUT=reports/results/kd_b0.json
```

Metrics JSON contains `pauc_at_tpr80`, `auc_roc`, `sensitivity`, `specificity`, `f1_score`, threshold, TP/FP/TN/FN.

> **Full PC + Android on-device workflow:** see [docs/MOBILE.md](../docs/MOBILE.md) — the end-to-end guide (build benchmark set → PC benchmark → ExecuTorch export → Android latency + parity), written to run after training completes.

### Mobile deployability benchmark

Architecture-level deployability numbers (params, FP32 size, single-core CPU latency). These are weight-independent, so benchmark **one checkpoint per architecture** (any fold) — CPU-only, no GPU requested:

```bash
bash slurm/submit.sh slurm/21_benchmark_mobile.slurm \
    MODEL=efficientnet_b0 \
    CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/fold_0/checkpoints/best_model.pth
# OUT defaults to reports/mobile_benchmark/<MODEL>.json
```

Output JSON contains `params_millions`, `fp32_size_mb`, `cpu_latency_ms_median`, `cpu_latency_ms_p90`, `image_size`. (INT8/TFLite quantization is intentionally de-scoped — backbones run FP32 as-is.)

### Build the fixed benchmark input set

One small, reproducible set of test samples reused for **all** of: PC latency, mobile latency, and the PC↔mobile parity check (the proposal doesn't pin a benchmark dataset — this uses the internal test split = the smartphone-like deployment domain). Preprocessing is identical to evaluation (`build_transforms(cfg,"val")`). CPU-only:

```bash
bash slurm/submit.sh slurm/26_make_benchmark_set.slurm N=100
# Also dump per-model reference logits for parity (optional):
bash slurm/submit.sh slurm/26_make_benchmark_set.slurm N=100 \
    MODEL=efficientnet_b0 \
    CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/fold_0/checkpoints/best_model.pth
```

Output `data/benchmark_set/` (rsync to Mac/phone, **don't commit**): `images/` (originals → parity layer 2), `inputs/<id>.bin` (fully-preprocessed float32 CHW → parity layer 1 + identical input both sides), `inputs.npy` (stacked, PC), `manifest.csv`, `meta.json` (image_size/mean/std/layout), and `ref_<model>.csv` (reference logits) when `MODEL`/`CKPT` given. Selection is seeded + label-stratified (oversamples the rare malignant class so inputs span the model's logit range).

### Full compute profile (PC + device-independent)

Superset of the mobile benchmark for the thesis "deployment story": also FLOPs/MACs, GPU latency, a batch-throughput sweep, and percentile latencies (p90/p95/p99). The CPU @ batch=1 latency (single-thread, phone-comparable) is **always** measured; GPU numbers are added when a GPU is allocated. Like the mobile benchmark these are weight-independent, so run **one checkpoint per architecture** (any fold):

```bash
# With GPU (CPU + GPU numbers):
bash slurm/submit.sh slurm/24_benchmark.slurm \
    MODEL=efficientnet_b0 \
    CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/fold_0/checkpoints/best_model.pth

# CPU-only (skip GPU, queues immediately):
bash slurm/submit.sh slurm/24_benchmark.slurm MODEL=... CKPT=... DEVICE=cpu

# Custom throughput batch sizes:
bash slurm/submit.sh slurm/24_benchmark.slurm MODEL=... CKPT=... BATCH_SIZES="1 16 64"
# OUT defaults to reports/benchmark/<MODEL>.json
```

Output JSON adds `gflops`, `gmacs`, `trainable_params_millions`, `latency_batch1.{cpu,cuda}` (mean/std/median/p90/p95/p99), `throughput.{cpu,cuda}` (images/sec + peak GPU mem per batch size), and `device_info` (always cite the hardware). All FP32 — quantization de-scoped.

### Export a model for deployment

Export a trained checkpoint to **ONNX** (default) or **TorchScript**. CPU-only — no GPU/MPS requested, so it schedules immediately:

```bash
bash slurm/submit.sh slurm/23_export_model.slurm \
    MODEL=mobilenetv3_large \
    CKPT=experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_0/checkpoints/best_model.pth
# Optional: FORMAT=torchscript  OUT=exports/skin_mnv3  CONFIG=<path>
# Default OUT=exports/<MODEL>; CONFIG defaults to the run's saved config.yaml
# (next to the checkpoint) so the ONNX dummy uses the trained image_size.
```

Produces `exports/<name>.onnx` (or `.pt`). Download it and run with `onnxruntime` anywhere — **no torch needed at inference for ONNX**. The model emits a single raw logit: apply `sigmoid()` then compare against the **Youden threshold from that fold's `test_metrics.json`** (not 0.5). Export the **student** (deployment target), not the teacher. This is a research/thesis model — not a validated medical device.

### Export to ExecuTorch (.pte) for Android on-device

Runs the student **as-is** on Android via the PyTorch-native ExecuTorch runtime — no TFLite/TF conversion. ExecuTorch pins its own torch build, so it lives in an **isolated venv** (`${DATASTORE_USER_DIR}/venv-export`) that cannot perturb the training `torch>=2.2`. One-time setup on the **login node**:

```bash
bash slurm/setup_export_env.sh        # creates venv-export (separate from venv)
```

Then export per student (CPU-only job):

```bash
bash slurm/submit.sh slurm/25_export_executorch.slurm \
    MODEL=efficientnet_b0 \
    CKPT=experiments/runs/kd_efficientnet_b4_to_efficientnet_b0/fold_0/checkpoints/best_model.pth
# BACKEND=none for a portable-ops fallback if XNNPACK can't partition an arch
# OUT defaults to exports/executorch/<MODEL>.pte
```

Uses `torch.export` (not TorchScript), so it handles the transformer students (mobilevit_s / fastvit / efficientformerv2) that `torch.jit.script` chokes on. Default backend lowers to the **XNNPACK delegate** (fast Android CPU). **Mandatory parity check on device:** feed the same preprocessed input through PC PyTorch and the `.pte`; require `max|Δlogit|` small (e.g. <1e-3) before trusting any on-device number.

---

## 6. Tracking a job

```bash
# squeue -u keg shows EVERYONE on the shared account; filter by name:
squeue -u keg --name=poc_teacher

# Live logs
tail -f logs/poc_teacher_<jobid>_runtime.log     # always-written tee log (preferred)
tail -f logs/poc_teacher_<jobid>.out             # SBATCH-redirected stdout
tail -f logs/poc_teacher_<jobid>.err             # SBATCH-redirected stderr

# Postmortem after a job ends
sacct -j <jobid> --format=JobID,JobName,State,Elapsed,MaxRSS,ExitCode,WorkDir

# Kill your own job (never anyone else's)
scancel <jobid>
```

### Pulling logs back to your laptop

Logs are written to `/datastore/keg/hungdang/skin-cancer-detector/logs/` on the cluster. To read them in your editor / share with Claude on the Mac, rsync them back after the job finishes:

```bash
# From your laptop. Pull only the new log files for this jobid:
rsync -avh --progress \
    "keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/logs/*_<jobid>*" \
    logs/

# Or sync the whole logs/ dir (cheap — they're small text files):
rsync -avh --progress --delete-excluded --include='*.out' --include='*.err' --include='*.log' \
    keg@slurm.uit.edu.vn:/datastore/keg/hungdang/skin-cancer-detector/logs/ \
    logs/
```

Pull *after* you see `[job] DONE` (or the job failed) — tailing a remote log in real-time is faster done with `ssh keg@slurm.uit.edu.vn "tail -f /datastore/keg/hungdang/skin-cancer-detector/logs/<jobname>_<jobid>_runtime.log"`. The Mac copy is for post-hoc analysis only.

---

## 7. GPU dispatch — current state

`_lib.sh::acquire_gpu` **bypasses `/usr/local/bin/gpu_check.sh` by default** and picks a GPU itself via `nvidia-smi --query-gpu=index,memory.free`. The cluster helper currently has a typo on line 31 (`nvidia-smi-i` instead of `nvidia-smi -i`) that makes it false-negative *and* it issues `scontrol requeue` internally — so once it runs against us, Slurm requeues no matter what our fallback says.

Until UIT admin fixes that typo, every job's log starts with:
```
[lib] Step A: nvidia-smi at /usr/bin/nvidia-smi
[lib] Step B: querying GPU free memory (30s timeout)...
[lib] Step C: nvidia-smi exit=0, ~X bytes returned:
    0, 45921
    1, 45262
    ...
[lib] Step D: selecting GPU with free vRAM >= 14336 MB...
[lib] Step E: picked='N'
[lib] CUDA_VISIBLE_DEVICES=N (selected via nvidia-smi)
```

**Do not** pass `USE_CLUSTER_GPU_CHECK=1` to `submit.sh` — that re-enables the broken helper. The env var is only for after the cluster admin patches the typo.

---

## 8. Common failures

| Symptom | Fix |
|---|---|
| `Submitted batch job <id>` but `logs/<job>_<id>.out` is empty | Submit via `bash slurm/submit.sh ...` not raw `sbatch`. Also check `logs/<job>_<id>_runtime.log` (fallback tee log written by `_lib.sh`). |
| Log shows endless `gpu_check.sh exited 10 — falling through to nvidia-smi` followed by requeue | You passed `USE_CLUSTER_GPU_CHECK=1`. Remove it and re-submit — see §7. |
| `ERROR: venv missing at /datastore/keg/hungdang/venv` | Run `bash slurm/setup_env.sh` on the login node (§1). |
| `ERROR: venv ... is missing core dependencies` | The venv was created but `pip install` didn't finish. `rm -rf /datastore/keg/hungdang/venv && bash slurm/setup_env.sh`. |
| `ImportError` / `ConfigKeyError` in the runtime log | `git pull` for the latest fixes. If you changed code yourself, run the `validate-pipeline` skill locally before re-submitting. |
| `Teacher checkpoint not found: ...` from student job | Re-run `02_poc_teacher.slurm` (or `11_train_teacher.slurm`) and wait for `[job] DONE` before submitting the student. |
| `UserWarning: ... NVIDIA driver ... too old` + training falls back to CPU | Reinstall torch with the matching CUDA build (see §1 — `cu121` works for driver 12.8). |
| `squeue -u keg` doesn't show my job | `keg` is a shared lab account. Use `squeue -u keg --name=<jobname>` or `sacct -u keg --starttime=$(date -d "1 hour ago" '+%H:%M:%S')`. |
| `CUDA_OUT_OF_MEMORY` early in training | The Slurm `gres/mps`-pinned GPU was full (MPS schedules by compute-%, ignores VRAM). `acquire_gpu` now re-checks the pinned GPU's free VRAM and **hops to a freer GPU within the same job**, so this should self-heal; if it still OOMs, every GPU is genuinely full — wait for the cluster to drain (do **not** switch to `--gres=gpu`: QOS `uit` caps `gres/gpu=0`, the job would sit `PD` with `QOSMaxGRESPerUser` forever). |
| `No space left on device` during preprocessing | `df -h /datastore/keg/hungdang/`. Remove the raw zip (`isic-2024-challenge.zip`) and the redundant `train-image/` JPG folder (HDF5 is what we read). |

---

## 9. Resource budget per script

| Script | mps | mem | vRAM | time | Notes |
|---|---|---|---|---|---|
| `01_prepare_poc` | none | 4 G | — | 15 m | CPU only |
| `02_poc_teacher` | 2 | 8 G | 12 G | 1 h | 2 epochs; `TEACHER=` (covers SOTA teachers) |
| `03_poc_student` | 2 | 8 G | 14 G | 1 h | Teacher + student in memory; `STUDENT=`/`TEACHER=` |
| `10_prepare_data` | none | 16 G | — | 4 h | HDF5 decode (idempotent across re-runs) |
| `11_train_teacher` | 4 | 16 G | 20 G | 24 h | teacher (B4 / SOTA), batch 32 |
| `12_train_student` | 4 | 16 G | 22 G | 18 h | KD, frozen teacher + student, batch 64 |
| `20_evaluate` | 1 | 8 G | 6 G | 1 h | Inference |
| `21_benchmark_mobile` | 1 | 4 G | — | 15 m | CPU only, single-thread latency |
| `24_benchmark` | 2 | 8 G | 4 G | 30 m | CPU always; GPU latency/throughput when `DEVICE≠cpu` |
| `26_make_benchmark_set` | none | 8 G | — | 20 m | CPU only, fixed benchmark input set from test split |
| `23_export_model` | none | 8 G | — | 20 m | CPU only, ONNX/TorchScript export |
| `25_export_executorch` | none | 8 G | — | 30 m | CPU only, ExecuTorch `.pte`, isolated venv-export |

Cluster ceilings: 20 MPS, 5 concurrent jobs, 32 vCPU, 72 h max per job. vRAM ≤44 G on L40, ≤80 G on A100.

---

## 10. Before submitting after any code change

Run the `validate-pipeline` skill (`.claude/skills/validate-pipeline/`):

```bash
# Python imports — catches __init__ re-export mismatches
python -c "from src.training import Trainer, KDTrainer, BinaryDistillationLoss; print('ok')"

# Hydra dry-load — catches struct-mode merge errors before training starts
python -c "
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf
import os
with initialize_config_dir(version_base=None, config_dir=os.path.abspath('configs')):
    cfg = compose(config_name='config_poc')
    OmegaConf.set_struct(cfg, False)
    OmegaConf.merge(cfg, {'model': OmegaConf.to_container(cfg.teacher, resolve=True)})
print('ok')
"
```

Both should print `ok`. Anything else means the cluster job will fail at the same point — fix locally.
