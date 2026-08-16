---
name: review-runner
description: Review the execution layer (run/*.sh, run/common.sh) AND its documentation (run/README.md) for the project's server rules and known failure modes. Use when the user adds/edits a run/*.sh script or its docs and asks "review my runner script", "is this safe to launch", "check the training job/docs". Enforces the project-scoped (no sudo / no system python) rule and the run-dir isolation rule. NOT for Python-side bugs (use review-training).
---

# review-runner

Reviews `run/` scripts **and** the docs that describe them. These scripts are the
only way jobs get launched, so a bug here either wastes GPU-hours or — worse —
silently overwrites a finished run-dir. This checklist catches both the
destructive mistakes and the strict-mode/logging bugs that make a job "run" with
no output.

Scope: `run/*.sh`, `run/common.sh`, and `run/README.md`.

## How to run

1. Diff in scope: `git diff HEAD -- run/`.
2. Run the **§3 lint from `validate-pipeline`** first (the grep-based runner
   checks) — it mechanically catches most of section A/B below. Then walk this
   checklist for what grep can't see (logic, docs drift).
3. Report most-severe first. **Any** finding in section A is a blocker.
4. Finish by cross-checking the docs (section E): `run/README.md` must match what
   the scripts actually do.

## A. Destructive / environment blockers

- [ ] **Run-dir isolation.** An ablation or variant must never write into an
  existing run-dir. Students isolate with `run_suffix=`; **teachers must use
  `output_dir=`** — `scripts/train_teacher.py:39` hard-wires
  `<output_dir>/teacher/<name>/fold_N` and does **not** read `run_suffix`, so a
  teacher variant without an `output_dir` override silently overwrites the main
  teacher run.
- [ ] **Project-scoped only.** No `sudo`, no `apt`, no system python, no
  `~/.bashrc` / shell-rc edits, no writes outside the repo. Dependencies go in
  `./.venv-linux` (export tooling in `./.venv-export`); env vars are per-session.
  The server is shared with other people — the user audits this.
- [ ] **No `rm -rf` of data/experiment paths**, no killing other processes
  (`pkill`, `killall`, `nvidia-smi --reset-gpu`). If the GPU is busy, wait or pin
  a different `GPU=` id.
- [ ] **`TMPDIR` stays inside the project** when the script writes large temp
  files — the server's `/` has been 100% full before, which is why the convention
  is a per-session `TMPDIR="$(pwd)/.tmp"`.
- [ ] **Never `pip install` inside a training script** — environment setup belongs
  in `run/setup_env.sh` / `run/setup_export_env.sh` only.

## B. Strict-mode & logging (the "ran with no output" class)

Every script sources `run/common.sh`, which sets `set -euo pipefail`.

- [ ] Script `source`s `run/common.sh` (else it loses strict mode, repo-root
  resolution, `activate_venv`/`select_gpu`, AND the `tee` log under `logs/`).
- [ ] `start_log <name>` is called, so the run survives an SSH drop with a
  `logs/<name>_<timestamp>.log` transcript.
- [ ] Every variable uses a `:-default` (`${FOLDS:-0 1 2 3 4}`, `${GPU:-auto}`).
  Under `set -u` a bare `${VAR}` aborts the job before it starts.
- [ ] Tools not present on every box (`nvidia-smi`, `tmux`) are gated with
  `command -v … || true`.
- [ ] Required args fail loudly and early: `: "${MODEL:?MODEL env var required}"`,
  and checkpoint paths are checked with `[ -s "${CKPT}" ]` before the long run.
- [ ] `KEY=VALUE` positional args are accepted the standard way
  (`for arg in "$@"; do export "${arg?}"; done`) so the CLI is uniform.

## C. Hydra override hygiene
- [ ] Multi-token override bundles (`SAMP_OVERRIDES`, `PRIV_ARGS`, `BATCH_SIZES`)
  are left **unquoted** at the call site so they word-split into separate args —
  and are wrapped in `set -f` / `set +f` when they contain a bracket token like
  `data.metadata_cols=[a,b,c]`, so the shell can't pathname-expand it.
- [ ] `EXTRA="…"` is forwarded verbatim and last, so it can override anything.
- [ ] `GPU=cpu` also passes `device=cpu` to Hydra — `CUDA_VISIBLE_DEVICES=""`
  alone doesn't tell the config to use CPU.
- [ ] CPU-only jobs (export, benchmark-mobile, validate, benchmark-set) set
  `export CUDA_VISIBLE_DEVICES=""` so they stay runnable while a training process
  owns the GPU.

## D. Fold loop & dependency logic
- [ ] **5-fold CV is ONE process that loops folds internally**
  (`for FOLD in ${FOLDS:-0 1 2 3 4}`), so one model = one job. A heavy model is
  split across two launches with `FOLDS="0 1 2"` + `FOLDS="3 4"`.
- [ ] A KD student job doesn't assume the teacher checkpoint exists without
  checking (`test -s …/best_model.pth`) — order dependency, not a silent
  random-weight run.
- [ ] Aggregation/eval scripts read the fold-scoped run-dir convention
  (`experiments/runs/<run>/fold_{0..4}/`).

## E. Documentation consistency (the half that's easy to forget)
Drift here sends the next person down the wrong path.
- [ ] `run/README.md` describes the script as it now behaves — launch command,
  env-var overrides (`STUDENT=`, `RUN_DIR=`, `GPU=`, `FOLDS=`), and produced
  output paths all match.
- [ ] Any new `run/*.sh` is added to the README's **Script index** table and to
  the relevant numbered workflow section.
- [ ] The one-time-setup vs per-run distinction stays accurate if the change
  touches `setup_env.sh` / `setup_export_env.sh` / `setup_new_server.sh`.
- [ ] If the change alters run-dir naming or GPU-selection behavior, the matching
  note in `CLAUDE.md`'s "Recurring gotchas" is still correct (flag if it now
  contradicts the script).

## Don't
- Don't approve a script that can overwrite an existing run-dir, even "just for
  this ablation" — fork it with `run_suffix=` / `output_dir=` instead.
- Don't review the script and skip the docs (or vice-versa) — doc drift is a real
  defect here.
