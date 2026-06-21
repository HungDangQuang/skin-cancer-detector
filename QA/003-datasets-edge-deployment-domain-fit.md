# QA 003 — Why do the chosen datasets work for edge deployment, given ISIC 2024 images are not phone photos?

**Status:** verified 2026-06-17 · data

## Question
Tại sao việc sử dụng các dataset đã được nêu ra trong khoá luận này có thể hoạt động tốt trên thiết bị biên? Nhất là với dataset ISIC2024, hình ảnh không hề chụp từ điện thoại.

## Answer
The question conflates two independent properties, and one premise needs correcting. **"Runs on an edge device" is a property of the model, not of the dataset; "matches the phone-camera input domain" is the dataset property — and ISIC 2024 SLICE-3D, despite not being literal phone photos, is non-dermoscopic, consumer-camera-quality lesion crops that the project explicitly treats as a proxy for the smartphone deployment domain.** So the dataset choice is in fact aligned with edge deployment, not in tension with it.

**1. Edge-deployability comes from the model design, not the dataset.** No training dataset makes a model run on-device; that is decided by parameter count, FP32 size, and CPU latency. The project distills the large EfficientNet-B4 teacher into small students — EfficientNet-B0 / MobileNetV3-Large / MobileViT-S ([CLAUDE.md](../CLAUDE.md) "Architecture") — and measures their on-device cost with a dedicated CPU benchmark (`slurm/21_benchmark_mobile.slurm`, reporting `params_millions`, `fp32_size_mb`, `cpu_latency_ms_median/p90` — [docs/SLURM.md:171-181](../docs/SLURM.md#L171-L181)). Whatever the training images look like, it is these mobile-class backbones + KD that make inference feasible at the edge.

**2. The premise is partly mistaken: ISIC 2024 is *not* dermoscopy — it approximates phone-quality imaging.** ISIC 2024 SLICE-3D consists of lesion tiles cropped from 3D total-body photography, **native ~128×128, non-dermoscopic**, with the project's stated **deployment domain = plain smartphone photos** ([docs/PREPROCESSING.md:11-13](../docs/PREPROCESSING.md#L11-L13)). They are not captured on a phone, but their imaging characteristics — low resolution, ordinary (non-dermatoscopic) optics, no contact-lens vignette — are far closer to a casual phone snapshot than to a clinical dermatoscope image. That is precisely why ISIC 2024 is the **primary training set** ([configs/data/isic2024.yaml:2](../configs/data/isic2024.yaml#L2) `role: primary_training`) for a phone-targeted screener.

**3. PAD-UFES-20 closes the remaining gap with real smartphone images.** It is ≈2,298 **smartphone clinical images** added specifically for extra malignant positives ([docs/PREPROCESSING.md:12-13](../docs/PREPROCESSING.md#L12-L13), [configs/data/pad_ufes_20.yaml:2](../configs/data/pad_ufes_20.yaml#L2) `role: augment_malignant`). So the training mix is non-dermoscopic ISIC tiles + genuine phone photos — both in the deployment domain.

**4. The genuinely-dermoscopic data is deliberately kept OUT of training.** HAM10000 is dermoscopic and is used **only for cross-domain evaluation, never for training/validation/threshold selection** ([configs/data/ham10000.yaml:3,16-25](../configs/data/ham10000.yaml#L3)). Reinforcing this, the microscope-style circular-crop augmentation (which simulates a dermatoscope-lens vignette) was **dropped**, because the only vignetted data is the HAM10000 test set, so training for it would conflate generalization with leakage ([docs/PREPROCESSING.md:101](../docs/PREPROCESSING.md#L101)). This shows a conscious effort to keep the *training* domain aligned with the phone deployment domain and to test dermoscopy only as out-of-distribution.

**5. One honest caveat on resolution.** ISIC tiles are upscaled 128→224 before the network; this is interpolation, not added detail, and must not be described as "high-resolution" ([docs/PREPROCESSING.md:38](../docs/PREPROCESSING.md#L38)). It does, however, mean the model is trained at the same modest effective detail a phone crop would provide — another point of domain consistency rather than a defect.

**Bottom line:** the datasets support edge deployment because (a) edge feasibility is delivered by the compact KD students measured on the mobile benchmark, and (b) the *training* domain — non-dermoscopic ISIC 2024 crops plus real PAD-UFES-20 smartphone photos — is intentionally chosen to resemble phone-camera input, while true dermoscopy (HAM10000) is reserved as an out-of-distribution test rather than training data.

## Evidence
- [docs/PREPROCESSING.md:11-13](../docs/PREPROCESSING.md#L11-L13) — ISIC 2024 native ~128×128, **non-dermoscopic**, deployment domain = plain smartphone photos; PAD-UFES-20 ≈ smartphone clinical images.
- [docs/PREPROCESSING.md:38](../docs/PREPROCESSING.md#L38) — 128→224 is interpolation, not added detail (resolution caveat).
- [docs/PREPROCESSING.md:101](../docs/PREPROCESSING.md#L101) — microscope circular-crop aug dropped to avoid leaking dermoscope-vignette features from HAM into training.
- [configs/data/isic2024.yaml:2](../configs/data/isic2024.yaml#L2) — `role: primary_training`.
- [configs/data/pad_ufes_20.yaml:2](../configs/data/pad_ufes_20.yaml#L2) — `role: augment_malignant`, smartphone clinical images.
- [configs/data/ham10000.yaml:3,16-25](../configs/data/ham10000.yaml#L3) — dermoscopic, `role: cross_domain_evaluation`, `do_not_use_for: [training, validation_during_training, threshold_selection]`.
- [docs/SLURM.md:171-181](../docs/SLURM.md#L171-L181) — mobile deployability benchmark (params / FP32 size / CPU latency) — edge cost is a model property, measured separately.
- [CLAUDE.md](../CLAUDE.md) "Architecture" — KD from B4 teacher into mobile-class students (B0 / MobileNetV3-Large / MobileViT-S).

## For the thesis
Edge feasibility in this work is provided by the compact knowledge-distilled student models (measured via the CPU mobile benchmark), while domain suitability is provided by the training data: ISIC 2024 SLICE-3D consists of non-dermoscopic, consumer-camera-quality lesion crops whose appearance approximates the smartphone deployment domain, complemented by genuine smartphone clinical images from PAD-UFES-20. Truly dermoscopic data (HAM10000) is deliberately excluded from training and used only for out-of-distribution evaluation, keeping the training domain consistent with phone-based deployment.
