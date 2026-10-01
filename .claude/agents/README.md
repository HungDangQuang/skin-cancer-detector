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
- **One standing exception (2026-09-14):** `review-verifier` **is** spawned without being
  asked each time — the author pre-authorized it as a mandatory **cross-check gate** on any
  answer carrying numbers, `file:line`, or a patch (`CLAUDE.md` → "Cross-check gate").
  Two instances in parallel, one pass, every time. That standing authorization applies to
  this agent only.
- **Cost:** every spawn is a cold start (re-derives context) and costs tokens.
  Spawn only when you gain **parallelism** or **context isolation** — not for a
  single small task.

## When to use what

| Situation | Use |
|---|---|
| One result / one file / one sequential step | **Inline** or the matching **skill** (`eval-results`, or `code-change` for edits) |
| Bản nháp báo cáo / câu trả lời có số liệu hoặc bản vá, **trước khi** gửi tác giả | **Sub-agent** `review-verifier` ×2 song song — cổng kiểm chéo **bắt buộc** |
| Learning / reviewing / quizzing project **concepts** (not results) | **Sub-agent** `knowledge-tutor` |
| Many independent results to triage at once | **Sub-agent, fanned out** (one per run/model/dataset) |
| Heavy read-only sweep of the whole repo | Built-in **Explore** agent |
| Designing a large refactor before coding | Built-in **Plan** agent |
| Anything that must run training/eval | **Neither** — agents are Mac-only; submit via the `code-change` skill (`run/README.md`) |

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

Returns: verdict (good/moderate/poor/inconclusive — **run health only**) + `ACCEPTANCE` (labels
from `.claude/skills/eval-results/reference/acceptance-gates.md`, or "not assessed"; it never
writes "đạt / ready to ship" on its own) + `SPLITS` (v1 leaked / v2) + headline AUPRC (vs prevalence
baseline) + pAUC@TPR80 + sens/spec + aggregated mean±std (if present) + overfitting
gap + KD delta + flags. It follows the project metric rules (quote `test_metrics.json`
not val; AUPRC over AUC-ROC at ~0.4% prevalence; cite mean±std across folds).

### review-verifier
Kiểm chéo một **bản nháp** báo cáo/câu trả lời trước khi nó tới tác giả: mọi con số, câu
trích, `file:line` và khẳng định phủ định có đúng không (`REMIT=FACTS`), và bản vá có đủ
thông tin + minh bạch không (`REMIT=PATCH`). Read-only (`Read, Grep, Glob, Bash`), `model: opus`,
đối kháng: nó **không tin** citation của bản nháp mà tự mở lại nguồn, và phân biệt rõ bốn mức
`ĐÚNG` / `SAI` / `KHÔNG VERIFY ĐƯỢC` / `BỊA`.

- **Cách dùng (luôn là cặp, một message, song song):**
  "REMIT=FACTS, bản nháp `<scratchpad>/review_draft_4.3.md`, §4.3 dòng 1711–1824"
  + "REMIT=PATCH, cùng bản nháp".
- **Một lượt, không ping-pong.** Sửa xong không spawn lại — phải khai với tác giả rằng
  những dòng sửa sau kiểm chéo chưa qua agent nào.
- **`ĐẠT` là kết quả hợp lệ** — agent bị cấm bịa phát hiện cho báo cáo dày lên.

Hợp đồng đầy đủ (khi nào bắt buộc, khuôn prompt, cách xử lý bất đồng, chi phí):
[`.claude/skills/review-thesis/reference/cross-check.md`](../skills/review-thesis/reference/cross-check.md).
`model: opus` là cố ý — cổng chống bịa đặt thì bản thân nó không được bịa; hạ xuống
`sonnet` bằng tham số `model` khi spawn nếu mục cần soát nhẹ.

### knowledge-tutor
A Computer-Vision **professor** that teaches, reviews, and quizzes the project's
*concepts* (not results), grounded in the repo's actual code + `docs/review-knowledge-checklist.md`
+ `report_phase_1/`. Read-only (`Read, Grep, Glob`); replies in Vietnamese (bilingual),
cites `file:line`, says "chưa xác minh được" instead of guessing. Companion to the
10-day self-study plan `docs/review-10-day-plan-vi.md`.

- **Explain:** "use knowledge-tutor to explain Tier 6 (KD)"
- **Quiz / examiner:** "knowledge-tutor: play examiner and grill me on evaluation (Day 8)"
- **Where's the code:** "knowledge-tutor: where does pAUC get computed, walk me through it"

NOT for a result verdict (that's `result-analyst`) and NOT for reviewing code you just
changed (use the area review skills).

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
  can't step on the working tree. The `local-python-guard` hook still applies to
  anything an agent runs via Bash.
