# Skills index

Quick reference for the project's Claude Code skills — what each one does and when
to reach for it. Each skill lives in `.claude/skills/<name>/SKILL.md`; this file is
just the map. Invoke with `/<name>` or let Claude auto-route from the description.

Skills are grouped by the moment in the workflow you'd use them.

## 0. End-to-end (the master workflow)

| Skill | Use it when… | Focus |
|---|---|---|
| [dev-cycle](dev-cycle/SKILL.md) | "run the full cycle / do the whole process / ship this" | Orchestrates the 5 phases below: review → commit+push (no approval, feature branch) → emit slurm cmd + log job to `tasks/daily/` → results vs SOTA → update `docs/DE_CUONG.md`. It **calls** the area skills; it doesn't replace them. |

## 1. Edit → review (the mandatory modification workflow)

Run the matching review skill **right after** editing source, then `validate-pipeline`.
See `CLAUDE.md` "Modification workflow".

| Skill | Use it when you touched… | Focus |
|---|---|---|
| [review-preprocessing](review-preprocessing/SKILL.md) | `src/data/**`, `scripts/prepare_data.py` | Splits, augmentation, sampler, dataset processing vs the known-correct contract |
| [review-training](review-training/SKILL.md) | `src/training/**`, `src/models/**`, `scripts/train_{teacher,student}.py` | Trainer/KDTrainer contract, loss, optimizer/scheduler, KD loss |
| [review-slurm](review-slurm/SKILL.md) | `slurm/*.slurm`, `_lib.sh`, `submit.sh`, slurm docs | Shared-cluster no-kill rule + known cluster failure modes |
| [validate-pipeline](validate-pipeline/SKILL.md) | any of `src/`, `configs/`, `slurm/` | Static checks (Python imports, Hydra compose, slurm lint) — **always last, before submitting** |

## 2. Run on the cluster

| Skill | Use it when… | Focus |
|---|---|---|
| [submit-slurm](submit-slurm/SKILL.md) | submitting a job, or authoring a new `*.slurm` script | Wraps `slurm/submit.sh`; enforces queue-don't-evict |
| [poc-smoke-test](poc-smoke-test/SKILL.md) | quick end-to-end check before long training | Synthetic data POC pipeline (no ISIC download) |

## 3. Judge results & run experiments

The "is this good?" family — pick by **what artifact you have** and **how many runs**.

| Skill | Input | Use it when… |
|---|---|---|
| [analyze-evaluation](analyze-evaluation/SKILL.md) | one (or few) `reports/results/*.json` | Verdict on a checkpoint / one KD-vs-baseline / cross-student comparison |
| [compare-kd](compare-kd/SKILL.md) | **all** of `experiments/runs/` | "Did KD help across the board?", rank every teacher-student pair |
| [kd-experiment](kd-experiment/SKILL.md) | one student arch (to run) | Set up & run a controlled KD-vs-baseline pair for that student |
| [assess-training](assess-training/SKILL.md) | a **successful** training log | Score a finished run (good/moderate/poor) + how to improve next |
| [diagnose-training](diagnose-training/SKILL.md) | a **failed / misbehaving** run | Triage a crash, NaN, or a run that never started learning |

## 4. Extend the project

| Skill | Use it when… | Focus |
|---|---|---|
| [add-model](add-model/SKILL.md) | adding a new architecture | Register in `MODEL_REGISTRY` + matching config |

## 5. Thesis documentation

| Skill | Use it when… | Focus |
|---|---|---|
| [answer-qa](answer-qa/SKILL.md) | a methodology/results question you want **saved** | Answer grounded in code/results, store as `QA/NNN-*.md` |
| [diagram-style](diagram-style/SKILL.md) | drawing a pipeline/architecture **figure** for the report or slides | House "soft-card" SVG style — pastel containers, white cards, gray arrows; canonical example in `report_phase_1/figures/` |

---

### Routing cheatsheet (avoid the common mix-ups)

- **"Is this good?"** → eval JSON: `analyze-evaluation` · successful log: `assess-training` · crashed/weird run: `diagnose-training`.
- **KD effect** → one student you still need to run: `kd-experiment` · all existing runs: `compare-kd`.
- **After editing code** → area review skill, then `validate-pipeline`. The cluster is the only place real correctness (pytest, training) is verified.
