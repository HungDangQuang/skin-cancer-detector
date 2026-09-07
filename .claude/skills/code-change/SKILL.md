---
name: code-change
description: >
  Implement any code/config/runner change and carry it through the project's mandatory
  modification workflow — edit → area-specific review → propagate to run/ + docs → static
  validate → run on the GPU server. Use when the user asks to "change/add/remove code", "fix
  the trainer / loss / sampler / split", "add a new model architecture", "run POC / smoke
  test", "launch a training job", "validate the pipeline", or "run the full cycle / ship this
  end to end". It routes to the right detailed checklist in reference/ based on WHICH files
  you touched. NOT for judging a finished run's results (use eval-results) and NOT for
  teaching project concepts (use tutor-knowledge).
---

# code-change

The single entry-point for **making a code/config/runner change and getting it safely onto the
GPU server**. This project forbids running Python/pytest/training on the Mac (local ≠ runtime),
so the loop here is: edit → review against the area contract → propagate to the `run/*.sh`
wrapper + docs → static-validate → launch. Real correctness (pytest, training) is a **server**
step.

The detailed, battle-tested checklists live **verbatim** in `reference/`. This file is just the
router — open the matching reference file and follow it.

## The mandatory workflow (CLAUDE.md §"Modification workflow")

1. **Code** the change.
2. **Review** — route by the path you edited to the matching `reference/` checklist:

   | You touched… | Open |
   |---|---|
   | `src/data/**`, `scripts/prepare_data.py` | `reference/review-preprocessing.md` |
   | `src/training/**`, `src/models/**`, `scripts/train_{teacher,student}.py` | `reference/review-training.md` |
   | `run/**`, `run/README.md` | `reference/review-runner.md` |
   | adding a brand-new architecture | `reference/add-model.md` (then `review-training.md`) |

   The PostToolUse `modification-workflow` hook injects a `[modification-workflow]` reminder
   naming the area right after you edit — treat it as a required step, not a suggestion.

3. **Propagate to the runner (if any).** If the change alters how a job is invoked, what it
   consumes, or what it produces, update the matching `run/*.sh` **and** `run/README.md` in the
   *same* task. A code change that silently desyncs from its runner script is a defect.

4. **Verify (static, Mac-only).** Follow `reference/validate-pipeline.md` — Python import
   sanity, Hydra config compose, runner-script lint. This is the only verification possible
   locally; state explicitly that pytest / smoke-test is deferred to the server rather than
   claiming it passed. The runtime half is `bash run/validate.sh` **on the server**.

5. **Run.**
   - Training / evaluation / export → the matching `run/*.sh` (see `run/README.md` index).
   - Quick end-to-end check on synthetic data → `reference/poc-smoke-test.md` (`bash run/poc.sh`).
   - Controlled KD-vs-baseline for one student → `reference/kd-experiment.md`.
   - Full change→commit→launch→proposal cycle → `reference/dev-cycle.md`.

6. **Document.** End state = up-to-date docs, not a TODO to update them later: `CLAUDE.md`
   gotchas, relevant `docs/*.md`, and memory (`MEMORY.md` + the matching file). To write up
   the *results* of the run afterwards, use the **update-report** skill.

## Hard rules (never violate)

- **Keep everything inside the project folder.** No `sudo`/`apt`/system-python, no `~/.bashrc`
  edits; dependencies only in `./.venv-linux` (export tooling in `./.venv-export`); env vars
  per-session only. The server is shared — the user audits this.
- **Never install or run Python on the Mac** (hook-enforced). `ModuleNotFoundError` locally is
  expected, not a bug to fix with `pip install`.
- **Every `run/*.sh` uses `set -euo pipefail`** (via `run/common.sh`) — so give every variable a
  `${VAR:-default}` and gate non-universal CLIs (`nvidia-smi`) behind `command -v`.
- **Never overwrite an existing run-dir.** Ablations isolate with `run_suffix=` (students) or
  `output_dir=` (teachers — `scripts/train_teacher.py` does *not* read `run_suffix`).

See `reference/review-runner.md` and `docs/GOTCHAS.md` for the full rationale.

## reference/ index

| File | Use for |
|---|---|
| `reference/review-preprocessing.md` | splits / augmentation / sampler / dataset processing contract |
| `reference/review-training.md` | Trainer/KDTrainer contract, loss, optimizer/scheduler, KD loss |
| `reference/review-runner.md` | `run/*.sh` execution-layer contract + known server failure modes |
| `reference/add-model.md` | register in `MODEL_REGISTRY` + matching config |
| `reference/validate-pipeline.md` | static checks (imports, Hydra compose, runner lint) |
| `reference/poc-smoke-test.md` | synthetic-data POC end-to-end smoke test |
| `reference/kd-experiment.md` | controlled KD-vs-baseline for one student |
| `reference/dev-cycle.md` | end-to-end change→commit→launch→proposal orchestration |
