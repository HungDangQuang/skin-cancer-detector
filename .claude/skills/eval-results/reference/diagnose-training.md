---
name: diagnose-training
description: Triage a training run that crashed, NaN'd, stalled, or never started learning, and recommend a fix. Use when the user says "diagnose this run", "why did it fail/crash", "training looks broken/weird", "loss is NaN", "why isn't it learning", or shares a log from a job that went wrong. NOT for scoring a *successful* run (use assess-training) and NOT for a verdict on an eval JSON / checkpoint quality (use analyze-evaluation).
---

# diagnose-training

Systematic diagnosis of a training run: check whether the loss is dropping, the metric is improving, gradients are flowing, and whether known failure modes (class collapse, NaN, leakage) are present.

## When to use

- User shares a `logs/<name>_<timestamp>.log` or `experiments/<run>/training_curves.png` and asks what's wrong.
- A POC or full training run completed but `val_pauc` is stuck at 0 or near random.
- KD soft loss is suspiciously high relative to hard loss (or vice versa).
- A re-run produces different results than expected.

## Where to look (in order)

### 1. The fallback runtime log
```bash
cat logs/<name>_<timestamp>.log
```
This is the only log — every `run/*.sh` tees to it via `start_log` in `run/common.sh`, so it survives a dropped SSH session. The header at the top tells you: script name, hostname, working dir, date, and the GPU that was selected.

### 2. A backgrounded launcher's log
```bash
tail -200 logs/kd_<teacher>_to_<student>_<timestamp>.out   # run/train_kd_parallel.sh
```

### 3. The training curves PNG
`experiments/<run>/training_curves.png` — quick visual check. If `val_loss` is flat or rising while `train_loss` drops → overfitting or leakage.

### 4. The saved config
```bash
cat experiments/<run>/config.yaml
```
Confirm the hyperparams that actually ran (Hydra resolves overrides at runtime).

### 5. Was it killed by the OS?
```bash
dmesg -T 2>/dev/null | tail -40    # look for "Out of memory: Killed process"
nvidia-smi                          # is another process still holding the VRAM?
```

## Common failure modes

### Training-time (Python / model)

| Symptom | Likely cause | Where to confirm |
|---|---|---|
| `val_pauc` stuck at 0 across all epochs | All predictions same class — head bias collapsed | Check `pauc_at_tpr` returns 0 because `mask.sum() < 2` in `src/evaluation/metrics.py:30`; print prob distribution |
| `train_loss` drops, `val_loss` flat/rising | Data leakage OR severe overfitting | Confirm `StratifiedGroupKFold` grouped by `patient_id` in `scripts/prepare_data.py`; check val set has malignant samples |
| `loss=nan` on first iter | LR too high, or label dtype mismatch | Check `cfg.training.optimizer.lr_*` against `configs/training/distillation.yaml` defaults; ensure labels cast to float in the dataset |
| KD `soft_loss` ≈ 0 from epoch 1 | Teacher logits collapsed (always negative or positive) | `python -c "import torch; ckpt = torch.load('teacher.pth'); print(ckpt['model_state_dict'].keys())"` then run inference on val |
| `val_pauc` jumps wildly between epochs | Validation set too small (POC has only 36) | Expected for POC; only meaningful with full data |
| `RuntimeError: mat1 and mat2 shapes cannot be multiplied (BxC1 and C2x1)` | timm `model.num_features` doesn't match `forward(x)` output for some backbones (MobileNetV3: reports 960, emits 1280) | Use `infer_backbone_out_dim()` in `src/models/heads.py` — runs a dummy forward to get the true dim |
| `ValueError: x and y must have same first dimension, but have shapes (N,) and (0,)` (matplotlib) | Trainer's `history["val_pauc"]` (or similar key) never got appended in the fit loop | Confirm every key declared in `self.history = {...}` is `.append()`ed once per epoch in `fit()`; KDTrainer's pattern at `kd_trainer.py:104` is the reference |
| `AttributeError: module 'numpy' has no attribute 'trapz'` | NumPy 2.0 removed `np.trapz` | Use `np.trapezoid` |
| `KeyError: 'target'` in `generate_group_kfold_splits` | `cfg.data.label_col` is the *raw CSV* column name; the processed dataframe uses `"label"` | Pass `label_col="label"` to the splits function (see CLAUDE.md gotcha) |
| `omegaconf.errors.ConfigKeyError: Missing key data` from a standalone script | Plain `OmegaConf.load("configs/config.yaml")` doesn't compose Hydra's `defaults:` list | Use `src/utils/config.py::load_config` (auto-detects Hydra root configs) or switch the script to `@hydra.main` |
| `import` errors at start (e.g. `cannot import name X from src.<pkg>`) | `__init__.py` re-exports a symbol whose name doesn't match `class X` / `def X` in the submodule | `grep -n "^class \|^def " src/<pkg>/<mod>.py` and align the `__init__.py` re-export |

### Server / environment

| Symptom | Likely cause | Where to confirm / fix |
|---|---|---|
| `OSError: [Errno 28] No space left on device` during preprocessing | the project volume is full — typically the unzipped `train-image/` JPG folder duplicates what's already in `train-image.hdf5` | `df -h .` (and `df -h /` — the server root has hit 100% before, hence the per-session `TMPDIR="$(pwd)/.tmp"`); delete the redundant zip and the `train-image/` folder; HDF5 is the only file the preprocessor reads |
| Log file exists but is empty | The process died before `start_log`'s `tee` opened, or the shell aborted on an unbound variable under `set -u` | Re-run the script with `bash -x run/<script>.sh …` to see where it exits; check `dmesg -T | tail` for an OOM kill |
| `import` errors at start | venv outdated or core dep missing | Re-run `bash run/setup_env.sh` (or delete `./.venv-linux` first if the install was interrupted) |
| `UserWarning: The NVIDIA driver on your system is too old (found version 12080)` + falls back to CPU | torch wheel built against a newer CUDA than driver supports | `pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu121` (cu121 works for driver 12.8) |

## Quick checks

### Is the checkpoint actually trained?
```python
import torch
ckpt = torch.load("path/to/best_model.pth", map_location="cpu", weights_only=False)
print(list(ckpt.keys()))                              # expect 'model_state_dict' + meta
print(ckpt.get("epoch"), ckpt.get("metrics"))         # which epoch saved + val metrics
state = ckpt["model_state_dict"]
total_params = sum(v.numel() for v in state.values())
print(f"Params loaded: {total_params:,}")
```

### Loss components for a KD run (read from log)
```bash
grep -E "Epoch [0-9]+/[0-9]+" logs/<run>_runtime.log
```
Expected pattern:
```
Epoch 1/2 | train_loss=X (hard=Y, soft=Z) | val_loss=W val_pauc=V
```
Both `hard` and `soft` should be > 0 and decreasing.

## Don't conclude prematurely

- **POC val_pauc may be low even when working** — synthetic data with 30 malignant samples gives noisy val metrics. The signal: `train_loss` should drop epoch-over-epoch.
- **One bad epoch ≠ broken training** — early stopping uses `patience` for a reason.
- **Always check the config that ran** (`experiments/<run>/config.yaml`), not what's currently in `configs/`. Hydra overrides may have shifted things.
