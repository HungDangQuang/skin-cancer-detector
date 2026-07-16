# Agents index & usage guide

Custom sub-agents for this project live in `.claude/agents/<name>.md`. This file
explains what each does and — more importantly — **when to reach for an agent vs.
a skill vs. just doing it inline**.

## How activation actually works (read this first)

- Sub-agents do **not** auto-trigger. The main assistant spawns one (via the Agent
  tool) only when **you explicitly ask** — e.g. "use the result-analyst", "use a
  subagent", "analyze these in parallel". A plain "analyze run X" is handled
  **inline** (or with a skill), not by spawning.
- Each `description:` field is for *routing/discoverability*, not an automatic cue.
- When an agent does run: it works in its **own isolated context** with only the
  tools its frontmatter allows, returns **one final message** to the main
  assistant, and the assistant relays a summary to you. You don't talk to it
  directly. For fan-out, the assistant merges the verdicts.
- **Cost:** every spawn is a cold start (re-derives context) and costs tokens.
  Spawn only when you gain **parallelism** or **context isolation** — not for a
  single small task.

## When to use what

| Situation | Use |
|---|---|
| One result / one file / one sequential step | **Inline** or the matching **skill** (`analyze-evaluation`, `compare-kd`, `diagnose-training`) |
| Many independent results to triage at once | **Sub-agent, fanned out** (one per run/model/dataset) |
| Heavy read-only sweep of the whole repo | Built-in **Explore** agent |
| Designing a large refactor before coding | Built-in **Plan** agent |
| Anything that must run training/eval | **Neither** — agents are Mac-only; submit via the `submit-slurm` skill |

Rule of thumb: a **skill** = one specialized task, runs inline in the main
context. A **sub-agent** = the same kind of work *replicated in parallel* or kept
*out of* the main context. Don't replace a skill with an agent for a lone task.

## Project agents

### result-analyst
Analyzes ONE finished experiment and returns a concise, grounded verdict
(best metric, val−test overfitting gap, KD delta), citing the file paths it read.
Read-only (`Read, Grep, Glob, Bash`); never trains, edits, or submits; says
"missing" instead of guessing. Built to be spawned **in parallel** for triaging
many runs.

- **Single run:** "use result-analyst on `experiments/runs/teacher/efficientnetv2_m`"
- **Fan-out:** "use result-analyst in parallel on every student in `experiments/runs/`"
- **KD vs baseline:** "result-analyst: did KD help `mobilenetv4_conv_medium`?"
- **Eval JSON / log:** "result-analyst on `reports/results/poc_kd_mnv4.json`"

Returns: verdict (good/moderate/poor/inconclusive) + headline AUPRC (vs prevalence
baseline) + pAUC@TPR80 + sens/spec + aggregated mean±std (if present) + overfitting
gap + KD delta + flags. It follows the project metric rules (quote `test_metrics.json`
not val; AUPRC over AUC-ROC at ~0.4% prevalence; cite mean±std across folds).

## Built-in agents you can also ask for

- **Explore** — read-only fan-out search across many files; returns conclusions,
  not file dumps. Good for "where is X used / audit all configs for Y".
- **Plan** — architecture/implementation planning for a larger change.
- **general-purpose** — multi-step research/search when you're not sure where the
  answer is.

## Adding or tuning an agent

- Create `.claude/agents/<name>.md` with frontmatter `name`, `description`
  (when-to-use, third person), optional `tools` (comma-separated allowlist — omit
  to inherit all; restrict for safety), optional `model` (`sonnet`/`opus`/`haiku`).
  The markdown body is the agent's system prompt.
- New/edited agents are picked up at **session start** — restart (or reload) before
  the agent is spawnable, same as hooks.
- Keep result/analysis agents **read-only** (no Edit/Write) so a parallel swarm
  can't step on the working tree. The `local-python-guard` / `slurm-*-guard` hooks
  still apply to anything an agent runs via Bash.
