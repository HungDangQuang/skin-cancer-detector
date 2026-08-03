# Skills index

Quick reference for the project's Claude Code skills — what each one does and when
to reach for it. Each skill lives in `.claude/skills/<name>/SKILL.md`; this file is
just the map. Invoke with `/<name>` or let Claude auto-route from the description.

The directory was consolidated from 15 fragmented skills into **6 clear entry-points**
(2026-08-02). The detailed, area-specific checklists were **not** thrown away — they live
verbatim under each skill's `reference/` and the SKILL.md routes to the right one.

## The 6 skills

| Skill | Use it when you want to… | Routes to (`reference/`) |
|---|---|---|
| [code-change](code-change/SKILL.md) | **add / remove / edit code** and carry it through review → validate → run on the cluster | review-preprocessing · review-training · review-slurm · add-model · validate-pipeline · submit-slurm · poc-smoke-test · kd-experiment · dev-cycle |
| [eval-results](eval-results/SKILL.md) | **read & judge results**, conclude whether the solution is effective | analyze-evaluation · compare-kd · assess-training · diagnose-training |
| [update-report](update-report/SKILL.md) | **write / refresh the report `.md`** (reports/, proposal, daily log) once results exist | — (Google Drive deferred) |
| [draw-diagram](draw-diagram/SKILL.md) | **draw a pipeline / architecture figure** in the house soft-card SVG style | — (was `diagram-style`) |
| [answer-qa](answer-qa/SKILL.md) | **answer a thesis question AND store it** as `QA/NNN-*.md` | — |
| [tutor-knowledge](tutor-knowledge/SKILL.md) | **learn / review / get quizzed** on project concepts (`/tutor`) | delegates to the `knowledge-tutor` agent |

## Routing cheatsheet (pick by intent)

- **"I need to change code / run it"** → `code-change`. It reads the path you edited and opens
  the matching `reference/` checklist (preprocessing / training / slurm), runs the
  validate-pipeline static checks, then submits via `slurm/submit.sh`. The PostToolUse hook
  reminds you automatically after each edit.
- **"Is this good? Did KD help? Why did it fail?"** → `eval-results`. Pick the rubric by the
  artifact you have: eval JSON → analyze-evaluation; all runs → compare-kd; good log →
  assess-training; broken run → diagnose-training.
- **"Write this up."** → `update-report` for the `.md` deliverables; `answer-qa` if it's a
  thesis question you want stored under `QA/`.
- **"Draw the pipeline / a figure."** → `draw-diagram` (SVG, not a matplotlib number-plot).
- **"Explain / quiz me on concept X."** → `tutor-knowledge` (spawns the `knowledge-tutor` agent).

## Notes

- **Agents vs skills:** `eval-results` overlaps the `result-analyst` agent (parallel triage of
  many runs) and `tutor-knowledge` fronts the `knowledge-tutor` agent — use the agent when you
  need a read-only sweep fanned out; use the skill for the interactive, single-thread path.
- **Google Drive** sync for reports is intentionally deferred — the connected MCP has
  `create_file` but no update/overwrite, and no target folder is agreed yet.
