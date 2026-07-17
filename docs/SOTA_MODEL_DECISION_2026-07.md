# QUYẾT ĐỊNH BỘ MODEL SOTA — Teacher/Student & nhánh KD (2026-07)

> **Ngày:** 2026-07-16 · **Trạng thái:** đã chốt, đang triển khai.
> Doc này là **bản quyết định** chốt lại từ khảo sát [SOTA_MODEL_SURVEY_2026-07_1.md](SOTA_MODEL_SURVEY_2026-07_1.md)
> sau khi đối chiếu công tâm với code + docs thực tế của repo. Nó thay khảo sát làm nguồn sự thật cho
> "dùng model nào". Khi số liệu 5-fold về, cập nhật cột trạng thái ma trận + memory.

---

## 1. Vì sao có doc này

Bộ model được review lại ở một session khác → khảo sát đề xuất nhiều thay đổi giữ/bỏ/thêm. Doc này chốt
**thay đổi nào đáng làm**, kèm ma trận số lượng và mức ảnh hưởng pipeline, để tránh (a) sprawl vô ích và
(b) đầu tư vào hạng mục trùng lặp với kế hoạch metadata.

---

## 2. Đánh giá khảo sát (fair — đã fact-check với repo)

| Luận điểm khảo sát | Verdict | Căn cứ trong repo |
|---|---|---|
| DKD / logit-standardization / OFA-KD **suy biến ở K≤2** | ✅ **Đúng** (đại số) | Head là single raw logit ([CLAUDE.md](../CLAUDE.md)); NCKD≡0 khi chỉ 1 lớp non-target. Dùng cho Chương 2. |
| Pixel 6a / Tensor G1 → **chỉ XNNPACK CPU**, không QNN NPU | ✅ **Đúng** | Khớp scope deploy đã chốt ([project_benchmark_tasks](../.claude) memory). |
| Feature-based / relational KD là hướng cải tiến hợp lệ duy nhất | ✅ **Đúng nhưng đã có** | **RKD đã code sẵn** — [src/training/feature_distillation.py](../src/training/feature_distillation.py) + [configs/training/distillation_rkd.yaml](../configs/training/distillation_rkd.yaml). Chỉ cần **chạy**, không phải "thêm". |
| Bỏ `maxvit_base` vì **"phá mandate seed=42"** | ❌ **SAI (straw-man)** | [docs/ARCHITECTURE.md:114](ARCHITECTURE.md) + [docs/GOTCHAS.md](GOTCHAS.md): `cudnn_deterministic=false` KHÔNG vi phạm seed (seed vẫn kiểm soát data/init/aug; teacher freeze; số liệu mean±std 5 fold). **Lý do bỏ đúng = accuracy 84,9% top-1 thấp hơn cả 2 teacher kia dù nặng ~2×.** |
| Thêm PanDerm / DINOv3 làm teacher foundation | ⚠️ **Hợp lệ nhưng nặng** | Không có trong `timm` → cần port (§5). Trùng slot "đóng góp mới" với metadata LUPI (§7). |

**Kết luận chung:** khảo sát **vững về khoa học KD**, nhưng **lạc quan quá mức về "cần thêm model"**: phần
lớn khuyến nghị "giữ" đã là hiện trạng, và nhánh feature-KD đã tồn tại trong code.

---

## 3. Quyết định giữ / bỏ / thêm

| Vai trò | Trước | Sau | Ghi chú |
|---|---|---|---|
| Teacher chính | `efficientnetv2_m` | **giữ** | gap thấp nhất (~5×), CNN thuần. Default trong [configs/config.yaml](../configs/config.yaml). |
| Teacher phụ | `convnextv2_base` | **giữ** | ma trận KD của teacher này **đã đủ 5-fold** cho cả 3 student. Trục capacity-gap ~9×. |
| Teacher nặng | `maxvit_base` | **giữ trong registry, LOẠI khỏi run-plan** | Teacher đã train 5 fold nhưng KD bỏ dở (1–2 fold). KHÔNG xóa registry/config (giữ khả năng load checkpoint + tránh phá test). Trích như bằng chứng capacity-gap: *teacher nặng nhất KHÔNG cho student tốt nhất*. |
| **Teacher foundation** | — | **THÊM `panderm`** (ViT-B/16) | Teacher domain da liễu; §5. Fallback `efficientnetv2_s` nếu port bất khả thi. |
| Student | 3 (MNV4/FVit/EFv2) | **+ `repvit_m1_0`** ✅ đã thêm | CNN-thuần reparam, quantize-friendly thứ 2 để củng cố kết luận mobile. |
| KD | logit-KD (BCE) | **+ chạy nhánh RKD** | `training=distillation_rkd` cho teacher chính + PanDerm. Code có sẵn. |

**KHÔNG thêm** (khảo sát nêu nhưng không đáng cho scope này): DINOv3 (khảo sát tự xếp sau PanDerm, không có
benchmark da liễu, ViT→CNN khó nhất), SHViT/StarNet/EdgeNeXt, SimKD (cần projector — RKD tránh được).

---

## 4. Ma trận teacher × student × điều kiện KD (số lượng)

Ký hiệu ô = `folds_done/5`. Student: **MNV4**=mobilenetv4_conv_medium · **FVit**=fastvit_sa12 ·
**EFv2**=efficientformerv2_s2 · **RepViT**=repvit_m1_0 (mới).

### 4.1. logit-KD (`training=distillation`)
| Teacher \ Student | MNV4 | FVit | EFv2 | RepViT |
|---|---|---|---|---|
| `efficientnetv2_m` (chính) | ✅ 5/5 | ✅ 5/5 | ⚠️ 3/5 → **+2** | 🆕 → **+5** |
| `convnextv2_base` (phụ) | ✅ 5/5 | ✅ 5/5 | ✅ 5/5 | 🆕 → **+5** |
| ~~`maxvit_base`~~ | retired (2/5) | retired (2/5) | retired (1/5) | — |

### 4.2. logit+RKD (`training=distillation_rkd`, đều mới)
| Teacher \ Student | MNV4 | FVit | EFv2 | RepViT |
|---|---|---|---|---|
| `efficientnetv2_m` (chính) | 🆕 +5 | 🆕 +5 | 🆕 +5 | 🆕 +5 |
| **`panderm`** (RKD *bắt buộc* — foundation, logit-only vô nghĩa ở K≤2) | 🆕 +5 | 🆕 +5 | 🆕 +5 | 🆕 +5 |
| `convnextv2_base` | *(tùy chọn +20)* | | | |

### 4.3. Run khác
- **Teacher training:** `efficientnetv2_m` ✅, `convnextv2_base` ✅, **`panderm` 🆕 +5** (sau port §5).
- **Baseline no-KD** (teacher-independent, mốc KD-delta): MNV4/FVit/EFv2 *cần verify đã có*; **RepViT 🆕 +5**.

### 4.4. Tổng fold-run MỚI (core)
| Hạng mục | Run |
|---|---|
| eff_v2_m→EFv2 logit (fold 3,4) | 2 |
| {eff_v2_m, convnextv2_base}→RepViT logit | 10 |
| eff_v2_m RKD (4 student × 5) | 20 |
| PanDerm teacher train | 5 |
| PanDerm RKD (4 student × 5) | 20 |
| RepViT baseline no-KD | 5 |
| **CORE TỔNG** | **62** |
| *(tùy chọn) convnextv2_base RKD* | +20 |
| *(tùy chọn) PanDerm logit-only contrast* | +20 |

> "Minimum viable ~47" nếu cắt: bỏ RepViT dưới convnextv2_base (−5) + PanDerm RKD chỉ MNV4/RepViT (−10).

---

## 5. Tích hợp PanDerm (đã verify công khai — không bịa)

**Nguồn:** [Nature Medicine 2025](https://www.nature.com/articles/s41591-025-03747-y) ·
[github.com/SiyuanYan1/PanDerm](https://github.com/SiyuanYan1/PanDerm)

**Dữ kiện xác minh:**
- **Weights công khai:** `PanDerm_Base` ViT-B/16 (Google Drive, `panderm_bb_data6_checkpoint-499.pth`, release 04/2025);
  bản ViT-L/16 (paper, ~300M); `DermLIP_PanDerm` trên HuggingFace `redlessone/DermLIP_PanDerm-base-w-PubMed-256`.
  → Dùng **ViT-B/16 (~86M)** để giữ capacity-gap hợp lý (student ~10M → ~8–9×).
- **Kiến trúc:** ViT patch-16, codebase kiểu BEiT (`classification/furnace/engine_for_finetuning.py`) →
  **KHÔNG phải tên `timm`** → `TimmBackboneModel` (gọi `timm.create_model`) không load trực tiếp.
- **License:** **CC-BY-NC-4.0** — phi thương mại/học thuật, **hợp khoá luận**, phải attribute.
- **Chưa xác nhận (verify trên server):** input size/normalize + feature dim CLS (ViT-B kỳ vọng **768** — kiểm
  từ notebook `feature_extraction_and_umap.ipynb`).

**Cách port (Approach B1(b)) — ĐÃ CODE (2026-07-17):**
1. ✅ Không vendor builder riêng: [src/models/panderm.py](../src/models/panderm.py) dựng **timm ViT-B/16** (mặc
   định `vit_base_patch16_224`, cấu hình qua `cfg.model.backbone`) rồi **nạp weight PanDerm đè lên backbone**.
2. ✅ Class `PanDermModel(TimmBackboneModel)` (không phải `BaseModel` trực tiếp — subclass để tái dùng
   backbone+head+`forward`+`forward_features` sẵn có; `forward_features` inherit chuẩn cho RKD projector-free).
   Loader `_load_panderm_weights` bóc container key (`model/module/state_dict/model_ema`), strip prefix
   (`backbone./encoder./module./model.`), chỉ nạp tensor **khớp tên+shape**, log tỉ lệ match và **raise nếu <
   `min_weight_match`** (chống train nhầm net gần-random khi chọn sai arch).
3. ✅ Đăng ký `"panderm": PanDermModel` trong [src/models/registry.py](../src/models/registry.py).
4. ✅ Config [configs/teacher/panderm.yaml](../configs/teacher/panderm.yaml): `backbone`, `pretrained:false`,
   `weights_path:null` (đặt trên server), `min_weight_match:0.5`, `head.dropout:0.3`.
5. ✅ Test [tests/test_models.py](../tests/test_models.py) (forward-shape + round-trip loader + guard-raise) + docs.
   **CÒN LẠI (trên server):** tải weight GDrive → set `teacher.weights_path` → xác nhận arch (`vit_*` vs
   `beit_*`, dùng tỉ lệ match làm tín hiệu) + feature dim 768 + input size/normalize → poc-smoke-test.

**Fallback (Task B0):** nếu BEiT-loader/weight bất khả thi trong ngân sách công sức → dùng `efficientnetv2_s`
(timm thuần, teacher gap thấp ~2–3×) làm trục "teacher nhẹ" thay cho trục foundation. Ghi rõ quyết định.

---

## 6. Ảnh hưởng pipeline/architecture

| Thay đổi | Đụng architecture? | Việc cần |
|---|---|---|
| `repvit_m1_0` (student) | ❌ Không | ✅ **ĐÃ LÀM**: 1 dòng registry + config + test + docs. Slurm/run 0 đổi (env-var). |
| Loại `maxvit_base` khỏi run-plan | ❌ Không | Chỉ ngừng submit; ghi doc. |
| Chạy RKD | ❌ Không | Đã wired opt-in; đổi `training=distillation_rkd`. |
| `panderm` (teacher) | ⚠️ **CÓ** | Class registry mới + loader BEiT-ViT + weight GDrive (§5). Hạng mục duy nhất đụng thật. |

Slurm/run ([slurm/11_train_teacher.slurm](../slurm/11_train_teacher.slurm),
[slurm/12_train_student.slurm](../slurm/12_train_student.slurm), [run/](../run/)) truyền
`TEACHER`/`STUDENT`/`TRAINING` qua env var → **0 thay đổi** cho mọi model timm mới.

---

## 7. Định vị PanDerm vs kế hoạch metadata LUPI (tránh trùng đóng góp)

[docs/metadata_training_plan.md](metadata_training_plan.md) Approach A đề xuất **privileged teacher (LUPI)**
dùng `tbp_lv_*` — cũng chiếm slot "teacher mới lạ". **Định vị làm 2 trục riêng, trả lời 2 câu khác nhau:**
- **PanDerm** = *"teacher domain-foundation (pretrain 2,1M ảnh da liễu) distill có hơn teacher supervised-CNN
  (`efficientnetv2_m`) xuống student mobile không?"* — trục **kiến trúc/pretrain teacher**.
- **LUPI** = *"metadata privileged Ở TEACHER (image+`tbp_lv_*`) có giúp student image-only không?"* — trục **thông
  tin đầu vào teacher**.

→ Bổ trợ nhau NẾU tách bạch; **thừa** nếu bán cả hai như "một đóng góp duy nhất". Chốt positioning này **trước**
khi đầu tư train PanDerm.

---

## 8. Trạng thái triển khai

- ✅ **Task A (RepViT)** — xong: [configs/student/repvit_m1_0.yaml](../configs/student/repvit_m1_0.yaml),
  registry, [tests/test_models.py](../tests/test_models.py), docs. Static-check thuần shell pass; import +
  Hydra-compose **defer sang server** (no-local-python). Verify timm tag `repvit_m1_0.dist_in1k` trên server.
- 🟡 **Task B (PanDerm)** — **loader + class + config + test ĐÃ CODE** (2026-07-17, §5). Chờ trên server: tải
  weight GDrive → set `teacher.weights_path` → xác nhận arch/feature-dim/normalize → smoke test; hoặc fallback
  `efficientnetv2_s` nếu weight/arch bất khả thi.
- ⏳ **Task C (chạy)** — §9.
- ⏳ **Task D (doc)** — doc này + cập nhật [ARCHITECTURE.md](ARCHITECTURE.md) §1 (số run thực) + memory.

---

## 9. Lệnh chạy (Task C — chạy trên server/cluster, KHÔNG trên Mac)

> Quy ước run-dir tự đặt tên `kd_<teacher>_to_<student>[__suffix]/fold_*`. Dùng `run_suffix=rkd` để tách RKD
> khỏi logit-KD. Trên cluster đổi `bash run/…` → `bash slurm/submit.sh slurm/12_train_student.slurm …`.

```bash
# --- Hoàn tất logit-KD còn thiếu ---
bash run/train_student.sh STUDENT=efficientformerv2_s2 TEACHER=efficientnetv2_m FOLDS="3 4"
bash run/train_student.sh STUDENT=repvit_m1_0 TEACHER=efficientnetv2_m
bash run/train_student.sh STUDENT=repvit_m1_0 TEACHER=convnextv2_base

# --- Baseline no-KD cho RepViT (mốc KD-delta) ---
bash run/train_student.sh STUDENT=repvit_m1_0 TRAINING=baseline

# --- RKD cho teacher chính (4 student) ---
for S in mobilenetv4_conv_medium fastvit_sa12 efficientformerv2_s2 repvit_m1_0; do
  bash run/train_student.sh STUDENT=$S TEACHER=efficientnetv2_m TRAINING=distillation_rkd run_suffix=rkd
done

# --- PanDerm (SAU khi tải weight GDrive + smoke test) ---
# weights_path đi qua EXTRA (Hydra override), KHÔNG phải positional (dấu chấm phá KEY=VALUE parser).
bash run/train_teacher.sh TEACHER=panderm \
  EXTRA="teacher.weights_path=/abs/path/panderm_bb_data6_checkpoint-499.pth"
for S in mobilenetv4_conv_medium fastvit_sa12 efficientformerv2_s2 repvit_m1_0; do
  bash run/train_student.sh STUDENT=$S TEACHER=panderm TRAINING=distillation_rkd run_suffix=rkd
done

# --- Aggregate + so sánh sau khi có kết quả ---
python scripts/aggregate_folds.py --run-dir experiments/runs/kd_efficientnetv2_m_to_repvit_m1_0
python scripts/compare_kd_results.py   # RKD vs logit-KD vs baseline
```

**Verify trước full run:** skill `poc-smoke-test` (hoặc POC 2-epoch) cho `repvit_m1_0` (và `panderm` nếu port
xong); trên server `python -c "import timm; print(timm.list_models('repvit*'))"` xác nhận tag.
