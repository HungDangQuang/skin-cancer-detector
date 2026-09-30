---
name: update-report
description: >
  Write or refresh the project's Markdown deliverables once results exist — the report files
  under reports/, the proposal docs/DE_CUONG.md, narrative summaries of aggregated fold
  results, and the tasks/daily job log. Use when the user says "update the report", "write up
  these results", "refresh the ablation report", "update the proposal / đề cương", "log this
  job", or "turn aggregated.json into a report". It documents; it does not judge (use
  eval-results for the verdict) or change code (use code-change). Answering + storing a thesis
  Q&A is a separate skill (answer-qa).
---

# update-report

The entry-point for keeping the project's **Markdown deliverables** current after a run
finishes. This is the "Document" step of the modification workflow, made callable on its own.

## What this skill maintains

| Target | When to touch |
|---|---|
| `reports/*.md` (e.g. `pad_ablation_*.md`, `2026-*_kd_runs.md`, ablation plans) | new results for an experiment already tracked here — update the number tables + conclusion |
| `docs/DE_CUONG.md` (the proposal / đề cương) | a headline result changed and the proposal must reflect it |
| a new `reports/<date>_<topic>.md` | a result/analysis with no existing home |
| `tasks/daily/<date>.md` | logging a submitted job so results are tracked back to it |
| `CLAUDE.md` gotchas / `docs/*.md` / `MEMORY.md` | anything non-obvious the run revealed |

## Rules

- **Numbers come from the artifacts, never from memory.** Read `test_metrics.json`,
  `val_metrics.json`, `aggregated.json/md`, or `predictions.csv` and cite the source path.
  Quote the **aggregated mean ± std** over folds, and lead with **AUPRC** at the ~0.39%
  prevalence (pAUC@TPR≥80 for ISIC-benchmark comparison). If you need the *verdict* first,
  run **eval-results**; this skill writes up a verdict you already have.
- **Match the existing report's structure** — reuse its heading layout, table columns, and
  tone rather than inventing a new format. Look at a sibling `reports/*.md` first.
- **Don't overwrite a report whose framing contradicts the new data** without flagging it —
  surface the discrepancy instead of silently editing.
- Keep edits scoped to `.md`; code/config changes go through **code-change**.

## Google Drive — deferred

Pushing reports to Google Drive is **out of scope for now**. The connected MCP exposes
`create_file` but **no update/overwrite** tool, and there is no agreed target Drive folder, so
"update on Drive" can't be done cleanly yet. Revisit when an update/overwrite tool or a target
folder exists; until then this skill only maintains repo-local `.md`.
