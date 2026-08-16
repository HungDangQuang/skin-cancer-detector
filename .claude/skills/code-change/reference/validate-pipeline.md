---
name: validate-pipeline
description: Static-check the pipeline (Python imports, Hydra config composition, run/*.sh runner scripts) before launching any job on the GPU server. Use after touching src/, configs/, or run/ — or whenever a remote job died with an import or config error and you want to catch the next one locally.
---

# validate-pipeline

Catches the bugs that have actually bitten this project, **without** spending GPU time. Runs in seconds on the Mac. Designed around real failures we've paid for:

- `ImportError: cannot import name 'DistillationLoss' from 'src.training.distillation'` — caught by **§1** (import sanity).
- `ConfigKeyError: Key 'model' is not in struct` from `OmegaConf.merge(cfg, {"model": ...})` — caught by **§2** (Hydra dry-load) + **§4** (anti-pattern grep).
- `FOLDS: unbound variable` under `set -euo pipefail` — caught by **§3** (runner script lint).
- `nvidia-smi: command not found` spam — caught by **§3**.
- A teacher ablation silently overwriting the main teacher run-dir — caught by **§3**.

## When to use

- Right after any change in `src/`, `configs/`, `scripts/`, or `run/` and **before** `bash run/<script>.sh ...`.
- When a remote job failed with `ImportError`, `ConfigKeyError`, or an unbound-var bash trace — run this locally to catch the next one before re-launching.
- Before merging any branch that touches the training pipeline.

## DO NOT

- Treat this as a substitute for `poc-smoke-test`. Static checks confirm "the wiring is plausible"; the smoke test confirms "training actually runs end-to-end". Use both.
- Skip the runner script lint just because the Python parts pass. Several incidents on this project came from shell-side issues that the Python side never sees.
- Claim §1/§2 "passed" if you only ran them on the Mac — the Mac has no torch/timm. On the Mac use `python3 -m py_compile` + the grep checks; the real §1/§2 run happens on the server via `bash run/validate.sh`.

## 1. Python import sanity

Catches mismatches between `__init__.py` re-exports and the actual class/function names in submodules — these only fail at import time on the server, halfway through a job.

```bash
# SERVER ONLY (needs torch/timm) — this is exactly what run/validate.sh §1 does.
python -c "
import src.data
import src.models
import src.training
import src.evaluation
import src.utils
from src.models.registry import MODEL_REGISTRY
from src.training import Trainer, KDTrainer, BinaryDistillationLoss
print('imports ok |', len(MODEL_REGISTRY), 'models registered')
"
```

If anything fails, fix the real symbol name in the failing `__init__.py` before doing anything else.

On the Mac, the closest local equivalent is a compile-only pass:

```bash
python3 -m compileall -q src scripts && echo "syntax ok"
```

## 2. Hydra config dry-load

Catches struct-mode merge errors (the `OmegaConf.merge(cfg, {"model": ...})` bug we hit), missing default groups, and unresolved interpolations — without launching training.

```bash
# SERVER ONLY — run/validate.sh §2 does this for EVERY registered model.
python -c "
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf
import os
cfg_dir = os.path.abspath('configs')

for root in ['config', 'config_poc']:
    with initialize_config_dir(version_base=None, config_dir=cfg_dir):
        cfg = compose(config_name=root)
        # Reproduce what train_teacher / train_student do:
        OmegaConf.set_struct(cfg, False)
        merged = OmegaConf.merge(cfg, {'model': OmegaConf.to_container(cfg.teacher, resolve=True)})
        assert merged.model.name, f'{root}: merged model has no name'
        print(f'{root:12s} ok | teacher={cfg.teacher.name} student={cfg.student.name}')
"
```

## 3. Runner script lint

Greps every `run/*.sh` for known fragile patterns. Each finding is a real failure mode we've already paid for. **This section runs fine on the Mac** — it's pure grep.

```bash
echo "--- a) run/*.sh that don't source common.sh (lose strict mode + logging) ---"
# Exempt: common.sh itself, the standalone setup scripts (they must run BEFORE a
# venv exists), and train_kd_parallel.sh (deliberately `set -uo pipefail` without
# -e, so one failed student can't abort the whole batch).
for f in run/*.sh; do
    case "$f" in
        run/common.sh|run/setup_env.sh|run/setup_export_env.sh|run/setup_new_server.sh|run/train_kd_parallel.sh) continue ;;
    esac
    grep -q 'common\.sh' "$f" || echo "  $f does not source run/common.sh"
done
echo "  (done)"

echo "--- b) Variables referenced but never defaulted (set -u will kill the job) ---"
# Every KEY=VALUE knob must be read as ${KEY:-default} or ${KEY:?message} at least
# once. Plain assignments and `for VAR in` loop variables count as bound.
for f in run/*.sh; do
    miss=""
    for v in $(grep -oE '\$\{[A-Z][A-Z0-9_]*[:}]' "$f" | tr -d '${:}' | sort -u); do
        case "$v" in PROJECT_DIR|BASH_SOURCE|PATH|HOME|USER|PWD|CUDA_VISIBLE_DEVICES|IFS) continue ;; esac
        grep -qE "(^|[^A-Za-z_])${v}=|\\\$\{${v}:|for ${v} in" "$f" || miss="${miss} ${v}"
    done
    [ -n "$miss" ] && echo "  $f: possibly unbound ->${miss}"
done
echo "  (done)"

echo "--- c) nvidia-smi without a guard or fallback ---"
# Must be either gated by `command -v` or made non-fatal (2>/dev/null + a default).
# run/common.sh is excluded: it IS the guard (select_gpu wraps its call in command -v).
grep -nE 'nvidia-smi' run/*.sh \
    | grep -v '^run/common.sh:' \
    | grep -vE 'command -v|2>/dev/null|echo |^[^:]+:[0-9]+:[[:space:]]*#' \
    || echo "  (clean — all calls gated or non-fatal)"

echo "--- d) Teacher variant using run_suffix (train_teacher.py IGNORES it!) ---"
# scripts/train_teacher.py:39 hard-wires <output_dir>/teacher/<name>/fold_N and
# never reads run_suffix — a teacher ablation must isolate with output_dir=,
# otherwise it silently OVERWRITES the main teacher run.
BAD=$(grep -nE 'train_teacher\.py' -A6 run/*.sh 2>/dev/null | grep -E 'run_suffix')
if [ -n "${BAD}" ]; then
    echo "  FAIL: run_suffix passed to train_teacher.py (use output_dir= instead):"
    echo "${BAD}"
else
    echo "  (clean — teacher variants isolate via output_dir)"
fi

echo "--- e) Destructive / out-of-project commands ---"
# Hard rule: the server is shared and everything must stay inside the project
# folder. No sudo/apt/system-python, no killing other people's processes.
FOUND=$(grep -nE '\bsudo\b|\bapt(-get)?[[:space:]]+install|\bpkill\b|\bkillall\b|rm[[:space:]]+-rf[[:space:]]+/|nvidia-smi[[:space:]]+(--reset-gpu|-r\b|--gpu-reset)|fuser[[:space:]]+-k|>>[[:space:]]*~/\.(bashrc|zshrc|profile)' run/*.sh 2>/dev/null \
        | grep -vE ':[0-9]+:[[:space:]]*#')
if [ -n "${FOUND}" ]; then
    echo "  FAIL: forbidden patterns detected:"
    echo "${FOUND}"
else
    echo "  (clean — no sudo/kill/rm -rf //rc-file edits)"
fi

echo "--- f) pip install outside the setup scripts ---"
FOUND=$(grep -nE '\bpip[0-9]*[[:space:]]+install' run/*.sh 2>/dev/null \
        | grep -vE '^run/(setup_env|setup_export_env|setup_new_server)\.sh' \
        | grep -vE ':[0-9]+:[[:space:]]*#')
if [ -n "${FOUND}" ]; then
    echo "  FAIL: pip install in a non-setup script:"; echo "${FOUND}"
else
    echo "  (clean — deps only installed by the setup scripts)"
fi

echo "--- g) Bracket Hydra tokens not protected by set -f ---"
# 'data.metadata_cols=[a,b,c]' / 'data.train_sources=[isic2024]' get built into a
# shell var that is then passed UNQUOTED (so it word-splits into separate Hydra
# args) — without noglob the shell may pathname-expand the bracket. Only override
# BUNDLES matter here; a bracket inside a quoted `python -c "..."` block is safe.
for f in $(grep -lE '^[[:space:]]*[A-Z_]+="[^"]*=\[' run/*.sh 2>/dev/null); do
    grep -q 'set -f' "$f" || echo "  $f has a bracket override bundle but never sets noglob (set -f)"
done
echo "  (done)"

echo "--- h) Required args not validated before a long run ---"
# MODEL/CKPT/RUN_DIR style args must use ${VAR:?...} so the job dies in 1s, not 1h.
for f in run/evaluate.sh run/benchmark.sh run/export_model.sh run/export_executorch.sh run/aggregate.sh; do
    [ -f "$f" ] || continue
    grep -qE '\$\{[A-Z_]+:\?' "$f" || echo "  $f never uses \${VAR:?...} for its required args"
done
echo "  (done)"
```

A clean run is silent except for the `(clean)` / `(done)` markers. Anything else is a finding to fix.

Also worth a syntax pass on anything you edited:

```bash
for f in run/*.sh; do bash -n "$f" || echo "SYNTAX FAIL: $f"; done
```

## 4. Code anti-patterns to look for (manual + grep, in diffs)

```bash
echo "--- i) np.trapz removed in NumPy 2.0 — use np.trapezoid ---"
# Skip comment lines so the explanatory comment in metrics.py doesn't false-positive.
FOUND=$(grep -nE '\bnp\.trapz\b|\bnumpy\.trapz\b' src/ scripts/ -r 2>/dev/null \
        | grep -vE ':[0-9]+:[[:space:]]*#')
if [ -n "${FOUND}" ]; then
    echo "  FAIL:"; echo "${FOUND}"
else
    echo "  (clean — no np.trapz in code)"
fi

echo "--- j) timm .num_features used directly instead of infer_backbone_out_dim ---"
# MobileNetV3 reports num_features=960 but forward() emits 1280. Always prefer
# infer_backbone_out_dim(backbone) in src/models/heads.py.
FOUND=$(grep -nE 'self\.backbone\.num_features|backbone\.num_features' src/models/ -r 2>/dev/null \
        | grep -vE 'heads\.py')
if [ -n "${FOUND}" ]; then
    echo "  FAIL:"; echo "${FOUND}"
else
    echo "  (clean — using infer_backbone_out_dim)"
fi

echo "--- k) Trainer history keys declared but never appended in fit() ---"
# Trainer historically declared val_pauc but never appended → matplotlib crash
# in plot_training_curves. Each key in `self.history = {...}` must show up
# with `.append(` in the same file. Use `while read` for portable word-splitting
# (bash 3.x on macOS doesn't always split unquoted $var by newlines).
any_missing=0
for f in src/training/trainer.py src/training/kd_trainer.py; do
    [ -f "$f" ] || continue
    grep -oE 'self\.history\s*=\s*\{[^}]*\}' "$f" \
        | grep -oE '"[a-z_]+"' | tr -d '"' | sort -u \
        | while IFS= read -r k; do
            grep -q "history\[\"${k}\"\]\.append" "$f" \
                || echo "  $f declares history key '${k}' but never .append()s it"
        done
done
```

These are easy to spot in `git diff` even without the grep:

- `OmegaConf.merge(cfg, {"new_top_level_key": ...})` **without** a preceding `OmegaConf.set_struct(cfg, False)` — Hydra emits cfg in struct mode, struct-merge rejects new keys.
- `from .X import Y` in any `__init__.py` where `Y` doesn't appear as `class Y` or `def Y` in `X.py`. Easiest check: `grep -n "^class \|^def " src/<module>/X.py` and compare.
- `forward(x)` returning `(B, 1)` shape — `BinaryFocalLoss` and `BinaryDistillationLoss` expect `(B,)`. Always `.squeeze(1)`.
- A new `run/*.sh` that doesn't `source run/common.sh` — loses strict mode and the `logs/` transcript.
- A standalone script that does `OmegaConf.load("configs/config.yaml")` directly. Use `src/utils/config.py::load_config` which composes the Hydra `defaults:` list, otherwise `cfg.data` will be missing.
- `cfg.data.label_col` passed to `generate_group_kfold_splits()`. That's the *raw* CSV column name — the processed dataframe uses `"label"`. Pass the literal `"label"`.

## 5. Pipeline prerequisite check

Catches "launched student before teacher finished" — the student script will refuse to run, but you'd rather not find out an hour in.

```bash
# Run this on the server before `bash run/poc.sh STAGE=student`:
test -s experiments/poc/teacher/efficientnetv2_m/checkpoints/best_model.pth \
    && echo "teacher checkpoint OK" \
    || echo "MISSING — run 'bash run/poc.sh STAGE=teacher' first and wait for [run] DONE"
```

## What "clean" looks like

```
imports ok | 8 models registered
config       ok | teacher=efficientnetv2_m student=mobilenetv4_conv_medium
config_poc   ok | teacher=efficientnetv2_m student=mobilenetv4_conv_medium
--- a) run/*.sh that don't source common.sh ---
  (done)
--- b) Script knobs without :- default ---
  (clean)
--- c) nvidia-smi without 'command -v' guard ---
  (clean — all calls gated)
--- d) Teacher variant using run_suffix ---
  (clean — teacher variants isolate via output_dir)
--- e) Destructive / out-of-project commands ---
  (clean — no sudo/kill/rm -rf //rc-file edits)
--- f) pip install outside the setup scripts ---
  (clean — deps only installed by the setup scripts)
--- g) Bracket Hydra tokens not protected by set -f ---
  (done)
--- h) Required args not validated before a long run ---
  (done)
```

If every section passes, launch with confidence. If any fail, fix locally and re-run — don't rely on a 6-hour job to surface the bug. Sections **(d)** and **(e)** are the most important: (d) prevents destroying a finished run-dir, (e) enforces the project-scoped rule on the shared server.
