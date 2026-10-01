# Skills index

Quick reference for the project's Claude Code skills — what each one does and when
to reach for it. Each skill lives in `.claude/skills/<name>/SKILL.md`; this file is
just the map. Invoke with `/<name>` or let Claude auto-route from the description.

The directory was consolidated from 15 fragmented skills into **6 clear entry-points**
(2026-08-02); `review-thesis` was added later (2026-09-12), making 7. The detailed, area-specific checklists were **not** thrown away — they live
verbatim under each skill's `reference/` and the SKILL.md routes to the right one.

## The 7 skills

| Skill | Use it when you want to… | Routes to (`reference/`) |
|---|---|---|
| [code-change](code-change/SKILL.md) | **add / remove / edit code** and carry it through review → validate → run on the GPU server | review-preprocessing · review-training · review-runner · add-model · validate-pipeline · poc-smoke-test · kd-experiment · dev-cycle |
| [eval-results](eval-results/SKILL.md) | **read & judge results**, conclude whether the solution is effective — and, only via `acceptance-gates`, whether the model **meets the requirement** | **acceptance-gates** · analyze-evaluation · compare-kd · assess-training · diagnose-training |
| [update-report](update-report/SKILL.md) | **write / refresh the report `.md`** (reports/, proposal, daily log) once results exist | — (Google Drive deferred) |
| [draw-diagram](draw-diagram/SKILL.md) | **draw a pipeline / architecture figure** in the house soft-card SVG style | — (was `diagram-style`) |
| [answer-qa](answer-qa/SKILL.md) | **answer a thesis question AND store it** as `QA/NNN-*.md`, qua **cổng kiểm chéo** trước khi ghi file | — (dùng `review-thesis/reference/cross-check.md`) |
| [tutor-knowledge](tutor-knowledge/SKILL.md) | **learn / review / get quizzed** on project concepts (`/tutor`) | delegates to the `knowledge-tutor` agent |
| [review-thesis](review-thesis/SKILL.md) | **soát một phần của `thesis/LUAN_VAN.md`** theo sáu tiêu chí của tác giả, kèm **cổng kiểm chéo** bằng sub-agent trước khi báo cáo | criteria · report-template · cross-check · `scripts/section_audit.py` |

## Routing cheatsheet (pick by intent)

- **"I need to change code / run it"** → `code-change`. It reads the path you edited and opens
  the matching `reference/` checklist (preprocessing / training / runner), runs the
  validate-pipeline static checks, then launches via `bash run/<script>.sh`. The PostToolUse hook
  reminds you automatically after each edit.
- **"Review phần 4.3 của luận văn"** → `review-thesis`. Chạy `scripts/section_audit.py <mục>`
  để lấy bằng chứng cơ học (thuật ngữ vs. bảng thuật ngữ, bảng/hình vs. danh mục, mọi con số),
  đọc toàn văn, chấm theo `reference/criteria.md`, báo cáo + ghi `thesis/REVIEW_LOG.md`.
  **Không** tự sửa `LUAN_VAN.md` cho tới khi tác giả duyệt.
  Trước khi báo cáo ra chat: **cổng kiểm chéo bắt buộc** — hai sub-agent `review-verifier`
  chạy song song (`REMIT=FACTS` + `REMIT=PATCH`), đúng một lượt, rồi báo cáo phải có khối
  `### Kiểm chéo` (`reference/cross-check.md`).
- **"Is this good? Did KD help? Why did it fail?"** → `eval-results`. Pick the rubric by the
  artifact you have: eval JSON → analyze-evaluation; all runs → compare-kd; good log →
  assess-training; broken run → diagnose-training.
- **"Model đạt yêu cầu chưa / đủ tốt chưa / dùng được trên điện thoại chưa?"** → `eval-results`
  → **`reference/acceptance-gates.md`** — the only route to that verdict.
- **"Write this up."** → `update-report` for the `.md` deliverables; `answer-qa` if it's a
  thesis question you want stored under `QA/`.
- **"Draw the pipeline / a figure."** → `draw-diagram` (SVG, not a matplotlib number-plot).
- **"Explain / quiz me on concept X."** → `tutor-knowledge` (spawns the `knowledge-tutor` agent).

## Notes

- **"Đạt yêu cầu" có đúng một định nghĩa:** `eval-results/reference/acceptance-gates.md`
  (2026-10-01). Good/Moderate/Poor trong `analyze-evaluation` / `assess-training` chỉ là sức khoẻ
  của run; "KD tốt hơn baseline" chỉ là so sánh. Không skill/agent nào được tự viết "đạt / đủ tốt /
  sẵn sàng ship" ngoài đường đó — `review-verifier` chấm vi phạm là `SAI`.

- **Cổng kiểm chéo:** mọi câu trả lời có số liệu / `file:line` / bản vá đều phải qua hai
  sub-agent `review-verifier` một lượt trước khi gửi — không riêng lượt soát luận văn
  (`CLAUDE.md` → "Cross-check gate").
- **Agents vs skills:** `eval-results` overlaps the `result-analyst` agent (parallel triage of
  many runs) and `tutor-knowledge` fronts the `knowledge-tutor` agent — use the agent when you
  need a read-only sweep fanned out; use the skill for the interactive, single-thread path.
- **Google Drive** sync for reports is intentionally deferred — the connected MCP has
  `create_file` but no update/overwrite, and no target folder is agreed yet.
