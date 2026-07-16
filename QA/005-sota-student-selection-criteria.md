# QA 005 — On what criteria were the SOTA students selected in this project?

**Status:** verified 2026-06-29 · experiment-design

## Question
Các student SOTA được chọn trong project này dựa theo tiêu chí nào?

## Answer
The three SOTA students — **`mobilenetv4_conv_medium`, `fastvit_sa12`, `efficientformerv2_s2`** ([CLAUDE.md](../CLAUDE.md) "Architecture") — were chosen by **two binding criteria plus one architectural-diversity criterion**, and the first two are what separate the *student* selection from the *teacher* selection:

**1. Must be on-device / mobile-latency deployable (the defining student constraint).** Unlike the teacher — which is frozen and used only during training, so it can be the heaviest available backbone — the student is the model that actually ships to the phone. "Runs on mobile" therefore binds *only* the student. The three picks are explicitly the **mobile-/on-device-latency-optimized** SOTA family ([CLAUDE.md](../CLAUDE.md) "Architecture": "the SOTA mobile-/on-device-latency-optimized set"; [project_sota_model_set.md](../../.claude/projects/-Users-hungdang-Documents-skin-cancer-detector/memory/project_sota_model_set.md) line 14, 23), and the proposal labels them "Bộ student (nhẹ, tối ưu cho di động)" ([docs/DE_CUONG.md:58-60](../docs/DE_CUONG.md#L58-L60)).

**2. Must be current SOTA (reviewer-defense).** The baseline students kept for comparison — EfficientNet-B0, MobileNetV3-Large (both 2019), MobileViT-S (2021) — are no longer the newest mobile architectures. The SOTA set is the contemporary mobile-latency state of the art: **MobileNetV4 (2024), FastViT (2023, Apple, deployed on iPhone), EfficientFormerV2 (2022, Snap)**. A further selection reason for EfficientFormerV2 specifically is that it is the backbone **recent ISIC-2024 SOTA papers use** ([project_sota_model_set.md](../../.claude/projects/-Users-hungdang-Documents-skin-cancer-detector/memory/project_sota_model_set.md) line 23). The old set is retained as baseline so the thesis can quantify the SOTA-vs-baseline gain rather than just asserting it.

**3. Architectural-paradigm diversity (mirroring the baseline trio).** The three picks deliberately span the major efficient-design paradigms, exactly as the baselines did:
- `mobilenetv4_conv_medium` — `paradigm: nas_optimized` (NAS-designed pure CNN) ([configs/student/mobilenetv4_conv_medium.yaml:3](../configs/student/mobilenetv4_conv_medium.yaml#L3))
- `fastvit_sa12` — `paradigm: hybrid_cnn_transformer` ([configs/student/fastvit_sa12.yaml:3](../configs/student/fastvit_sa12.yaml#L3))
- `efficientformerv2_s2` — `paradigm: hybrid_cnn_transformer` ([configs/student/efficientformerv2_s2.yaml:3](../configs/student/efficientformerv2_s2.yaml#L3))

This lets KD effectiveness be tested across both a NAS-CNN and the CNN-transformer hybrid family, not on a single architecture style.

**Practical constraints that all three also satisfy:** they run at the project's `image_size = 224` like every other model, and they are implementable through the single generic `TimmBackboneModel` wrapper with no per-arch code ([CLAUDE.md](../CLAUDE.md) "Model registry") — at the cost of requiring **`timm >= 1.0`** (they are absent from timm 0.9.x; [project_sota_model_set.md](../../.claude/projects/-Users-hungdang-Documents-skin-cancer-detector/memory/project_sota_model_set.md) line 21).

**Caveat on "mobile-latency".** The selection rationale rests on these being mobile-optimized, but the project's own benchmark measures **CPU latency on the cluster server as a proxy, not a phone number** — only params/FLOPs/size transfer cleanly across devices, and the latency *ranking* can flip on real mobile silicon, especially for the transformer-hybrid students ([project_benchmark_tasks.md](../../.claude/projects/-Users-hungdang-Documents-skin-cancer-detector/memory/project_benchmark_tasks.md)). So "mobile-optimized" is a published-design property of the architectures, not yet an on-device measurement in this repo.

## Evidence
- [CLAUDE.md](../CLAUDE.md) "Architecture" — student set splits into baseline `{efficientnet_b0, mobilenetv3_large, mobilevit_s}` and SOTA "mobile-/on-device-latency-optimized" `{mobilenetv4_conv_medium, fastvit_sa12, efficientformerv2_s2}`; requires `timm>=1.0`.
- [docs/DE_CUONG.md:58-60](../docs/DE_CUONG.md#L58-L60) — proposal: "Bộ student (nhẹ, tối ưu cho di động)" listing exactly these three SOTA students.
- [configs/student/mobilenetv4_conv_medium.yaml:3](../configs/student/mobilenetv4_conv_medium.yaml#L3) — `paradigm: nas_optimized`.
- [configs/student/fastvit_sa12.yaml:3](../configs/student/fastvit_sa12.yaml#L3) — `paradigm: hybrid_cnn_transformer`, backbone `.apple_in1k`.
- [configs/student/efficientformerv2_s2.yaml:3](../configs/student/efficientformerv2_s2.yaml#L3) — `paradigm: hybrid_cnn_transformer`, backbone `.snap_dist_in1k`.
- `project_sota_model_set.md` (memory, 2026-06-21) — rationale: reviewer-defense vs 2019–2021 baselines; MobileNetV4/FastViT/EfficientFormerV2 are mobile-latency SOTA; EfficientFormerV2 used by recent ISIC-2024 SOTA papers; "run on mobile" binds only the student (teacher stays heaviest SOTA); `timm>=1.0` required.
- `project_benchmark_tasks.md` (memory) — caveat: CPU latency is a proxy, not a phone number; latency ranking can flip on mobile for transformer students.

## For the thesis
The SOTA student backbones (MobileNetV4-Conv-Medium, FastViT-SA12, EfficientFormerV2-S2) were selected on two governing criteria — on-device mobile deployability (the constraint that, unlike the frozen teacher, binds the student because it is the model actually deployed) and contemporary state-of-the-art status (replacing the 2019–2021 baseline mobile networks, with EfficientFormerV2 chosen partly because recent ISIC-2024 work adopts it) — together with deliberate coverage of distinct efficient-design paradigms (a NAS-optimized CNN and the CNN–transformer hybrid family). The earlier mobile networks are retained as baselines so the gain from the SOTA set is measured rather than assumed.
