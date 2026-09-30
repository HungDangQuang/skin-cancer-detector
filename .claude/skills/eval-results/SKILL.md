---
name: eval-results
description: >
  Read the artifacts a run produced, judge them, and conclude whether the solution is
  effective. Use when the user asks "is this checkpoint good", "did KD help", "compare the
  students / teacher vs student", "rank my runs", "is this training run any good / how do I
  improve it", "why did it fail / NaN / not learn", or shares a reports/results/*.json, a
  training log, or an experiments/runs/ dir. It routes to the right detailed rubric in
  reference/ based on WHICH artifact you have. NOT for making a code change (use code-change)
  and NOT for writing the result up into a report (use update-report).
---

# eval-results

The single entry-point for the **"is this good / did it work?"** question. Pick the rubric by
**what artifact you have** — the detailed, project-specific criteria live **verbatim** in
`reference/` (moved here from the old eval skills). Open the matching file and follow it.

## Route by artifact

| You have… | Question | Open |
|---|---|---|
| one/few `reports/results/*.json` (eval JSON) | "is this checkpoint good?", one KD-vs-baseline, cross-student compare | `reference/analyze-evaluation.md` |
| **all** of `experiments/runs/` | "did KD help across the board?", rank every teacher-student pair | `reference/compare-kd.md` |
| a **successful** training log | score the run (good/moderate/poor) + how to improve the next one | `reference/assess-training.md` |
| a **failed / misbehaving** run (crash, NaN, never learned) | triage the failure + recommend a fix | `reference/diagnose-training.md` |

## Grounding rules (this project)

- **Quote `test_metrics.json`, not val metrics**, for any verdict — val is biased by
  early-stopping. Cite the **aggregated mean ± std** (`aggregated.json/md`) over folds, not a
  single fold.
- Headline metric at the measured **~0.39% prevalence** is **AUPRC** (clinical); **pAUC@TPR≥80**
  is the ISIC-benchmark comparison metric; AUC-ROC is optimistic — don't lead with it.
- A large **val − test** gap (esp. AUPRC/pAUC) is the overfitting signal.
- Never invent numbers — read them from the JSON and cite `file:line`; say "missing" if an
  artifact isn't there rather than guessing.

## reference/ index

| File | Was skill | Use for |
|---|---|---|
| `reference/analyze-evaluation.md` | analyze-evaluation | verdict on one/few eval JSONs (single or comparison mode) |
| `reference/compare-kd.md` | compare-kd | whole-matrix KD-vs-baseline via `scripts/compare_kd_results.py` |
| `reference/assess-training.md` | assess-training | score a finished, successful training log |
| `reference/diagnose-training.md` | diagnose-training | triage a crashed / NaN / non-learning run |

For a single finished run you can also spawn the **result-analyst** agent (parallel triage of
many runs); this skill is the interactive, single-thread path.
