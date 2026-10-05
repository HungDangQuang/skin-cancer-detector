---
name: dev-cycle
description: Run the project's end-to-end change→server→thesis cycle as one process. (1) Review the edits against this project's rules, (2) commit + push them to the current feature branch WITHOUT asking approval, (3) emit the run/ launch command and record the job in docs/PROGRESS.md (the single tracker), (4) when results return, report objective metrics compared against SOTA/papers via eval-results, (5) update the proposal (report_phase_1/DE_CUONG.md + docs/DE_CUONG.md) through update-report. Use when the user says "run the full cycle", "do the whole process end to end", "ship this change", or after a code change they want carried through to submission, evaluation, and the proposal. NOT a substitute for the area review skills — it CALLS them.
---

# dev-cycle

The master workflow that takes a change from code → reviewed → pushed → submitted →
evaluated-against-SOTA → written into the proposal. Run the phases in order. Do not
skip a phase; if a phase can't complete (e.g. results aren't back yet), stop cleanly
at that phase and tell the user exactly what you're waiting for.

**Standing authorizations for this workflow (already decided by the user):**
- **Commit + push without asking approval**, to the **current feature branch, no PR**
  (settings.json allows `git add/commit/push`; `push --force` stays denied).
- SOTA comparison uses **`docs/SOTA_BENCHMARKS.md` + WebSearch** to fill gaps.

**Always-on guardrails (never violated, even here):**
- Mac-only: never run training/eval/pip locally — that's the GPU server's job (the
  `local-python-guard` hook blocks it anyway).
- No hallucination: cite file paths / source URLs for every number; say "unknown" or
  "not yet computed" instead of guessing.
- Project-scoped server rules are absolute (no sudo/system-python, deps only in ./.venv-linux).

---

## Phase 1 — Review the change against the rules

1. `git diff --stat` + `git diff` to see exactly what changed.
2. Run the **area review checklist(s)** routed by path (same map the PostToolUse hook uses;
   files live next to this one in `reference/`):
   - `src/data/**`, `scripts/prepare_data.py` → `review-preprocessing.md`
   - `src/training/**`, `src/models/**`, `scripts/train_*.py` → `review-training.md`
   - `run/**`, `run/README.md` → `review-runner.md`
3. Run **`validate-pipeline.md`** (static checks: imports, Hydra compose, runner lint §3a–§3h).
4. Cross-check the principles the user cares about: the CLAUDE.md server rules,
   `docs/GOTCHAS.md`, and the feedback rules (no local python, project-scoped only,
   run-dir isolation, struct mode, augmentation-is-config-driven, …).
5. **Gate:** if anything violates a rule or a review finds a blocker → STOP, fix it,
   re-review. Do **not** proceed to Phase 2 until review + validate-pipeline are clean.
   Report the review outcome plainly (what passed, what was fixed).

## Phase 2 — Commit + push (no approval)

1. If on `main`, create a feature branch first (never commit straight to main).
2. `git add` the relevant files (only this task's — leave unrelated untracked/modified files
   alone), commit with a clear message + the `Co-Authored-By:` trailer the session's
   system reminder specifies (don't hard-code a model name here; it goes stale).
3. `git push` to `origin/<current-branch>`. No PR (user's choice). Never `--force`.
4. Report the commit hash + branch + that it's pushed.

## Phase 3 — Launch command + job tracking

There is no scheduler and no job id — a job is a process on the box. You normally can't launch
it from the Mac, so emit the command and track it.

1. Give the exact `bash run/<script>.sh VAR=value ...` command(s) for this change (pick the
   right script via the `run/README.md` script index). Quote `EXTRA="..."` as one arg when
   passing Hydra overrides. Remind the server rules that bite at launch: `TMPDIR="$(pwd)/.tmp"`,
   pin `GPU=<id>` when two jobs share the box, launch under `tmux`/`nohup`, and a new arm forks its
   run-dir (`run_suffix=` for students, `output_dir=` for teachers).
2. **Record it in `docs/PROGRESS.md`** — the only tracker (follow its header: one row per task,
   code **A** while running, status symbol + date). Put in the row: the command, purpose,
   expected output (`experiments/runs_newsplit_<arm>/<run>/fold_*/test_metrics.json`), the tmux
   session / log file (`logs/<name>_<timestamp>.log`) and what result you are waiting for.
   Never open a second tracker.
3. Stop here until results come back. Tell the user what you're waiting for; they (or
   `/progress`) can check it with `bash run/progress_all.sh`.

## Phase 4 — Objective results vs SOTA

When the user says the job is done, first `bash run/pull_results.sh` (check, then `pull`) so the
artifacts are on the Mac. Then use the **eval-results** skill — this phase is its job:

1. Quote `test_metrics.json` / `aggregated.json` (mean ± std), never `val_pauc`; cite the path.
   A difference between arms is a **paired bootstrap CI** (`run/bootstrap_ci.sh PAIR=…`), not a
   win count. State splits v1 vs v2.
2. **Headline = AUPRC vs its `prevalence` baseline**, plus **pAUC@TPR80** (ISIC 2024 official,
   ~0.02–0.20); lead the mobile story with the **PAD** (phone-photo) subset.
3. **Compare against SOTA/papers before judging** — `docs/SOTA_BENCHMARKS.md`; WebSearch to fill a
   missing reference number and record it there with source URL + date.
4. "Is it good enough / đạt yêu cầu" is answered **only** through
   `eval-results/reference/acceptance-gates.md`. Everything else is a comparison.
5. Before the verdict reaches the user it goes through the **cross-check gate** (`CLAUDE.md`). Then
   set the `docs/PROGRESS.md` row to ✅ with a one-line result and move it to §7.

## Phase 5 — Update the proposal

Once results are validated, use **update-report**: it owns `report_phase_1/DE_CUONG.md` (full
proposal), `docs/DE_CUONG.md` (short form), `reports/*.md` and its own cross-check step. The thesis
`thesis/LUAN_VAN.md` is not edited here — propose changes through **review-thesis** (report
first, edit on approval).

---

## Resuming mid-cycle

If invoked when jobs are already pending, read `docs/PROGRESS.md` §0–§2 (rows with 🏃 / ⏳) — those
are the results you're waiting on. Run `/progress` to see whether they are still alive and
`/pull-results` to see whether they have finished; pick up at Phase 4 if they have.
