# KD DESIGN REVIEW — Rà soát thiết kế KD & lựa chọn model

> **Ngày:** 2026-07-13
> **Phạm vi:** Rà soát `ARCHITECTURE.md` (bản 2026-07-13) đối chiếu với literature KD/edge-deployment tính đến 7/2026.
> **Mục đích:** Ghi lại các phát hiện cần **quyết định** trước khi khoá thiết kế thực nghiệm, và các đoạn lập luận dùng được cho Chương 2 / Chương 4.
> **Trạng thái:** Draft để review — chưa áp dụng thay đổi nào vào code.

> ### ★ CẬP NHẬT 2026-07-14 — đối chiếu code + chốt phạm vi (đọc TRƯỚC khi dùng file này)
> Đã kiểm chứng **từng claim với code thực tế** (3 agent + đọc trực tiếp `losses.py`/`distillation.py`): **không claim nào bịa** — mọi cơ chế đều có thật trong code. Nhưng mức "nguy hiểm" đã được hiệu chỉnh:
> - **§0 (mức L3) & §4.2 — NGOÀI PHẠM VI.** INT8 quantization **de-scoped** (chỉ FP32 ExecuTorch). Bỏ toàn bộ phân tích rủi ro INT8/transformer; chỉ giữ §4.1 (latency = CPU/XNNPACK, không NPU) cho FP32.
> - **§4.3/§4.4 (`cudnn_deterministic`) — ĐÍNH CHÍNH.** KHÔNG phải "vi phạm mandate seed=42". Mặc định `true` (`configs/config.yaml:24`); chỉ override tuỳ chọn cho maxvit như workaround cuDNN-backward; seed=42 vẫn kiểm soát data/init/aug; teacher freeze + báo cáo mean±std/5-fold. Lý do (nếu có) để bỏ maxvit là **accuracy thấp hơn dù nặng ~2×**, không phải reproducibility.
> - **§6.1 (calibration) — HẠ MỨC.** Đúng là **0 code calibration**, nhưng mọi metric báo cáo (pAUC/AUPRC/sens@spec ở ngưỡng Youden) **miễn nhiễm** miscalibration → đây là **điểm-cộng tuỳ chọn**, không phải "rủi ro nghiêm trọng nhất". Chỉ thành nguy hiểm lâm sàng nếu app hiển thị "% nguy cơ" cho người dùng (hiện chưa chốt).
> - **§7 (prevalence) — ĐÃ CHỐT = 0,39%** đo thực tế (ISIC 2024 + PAD-UFES-20, tập test độc lập, job 28250). Con số "0,9%" trong `PREPROCESSING.md` là **sai ~9×** — đã sửa.
> - **Nguy hiểm THẬT còn lại (đã/đang xử lý):** (A) số prevalence trong docs — **đã sửa**; (B) docstring focal-α mô tả sai — **đã sửa**, còn cần ablation α=0.25-vs-0.75 để bảo vệ; (C) câu chữ ma trận "30 run" lệch thực tế 3-teacher — **đã sửa** trong `CLAUDE.md`/`ARCHITECTURE.md`.
> - **Điểm mạnh xác nhận đúng (viết vào luận văn):** §2 (logit-KD suy biến K≤2 — kiểm chứng đại số), §3.4 (hệ số T² đúng cho sigmoid/BCE), §5 (7 quyết định).

---

## 0. Bối cảnh đã chốt (không cần bàn lại)

Hai thay đổi sau là **chủ đích thiết kế**, đã xác nhận, được coi là ràng buộc cố định của mọi phân tích bên dưới:

| # | Quyết định | Hệ quả kỹ thuật |
|---|---|---|
| 1 | **Stack thuần PyTorch / `timm`** (`.pth`, `TimmBackboneModel`) | Mọi teacher/student lấy từ `timm>=1.0`. Mở đường cho teacher PyTorch-native (vd. PanDerm); đóng đường với teacher hệ TF (vd. Google Derm Foundation). |
| 2 | **Export bằng ExecuTorch (`.pte`)**, không dùng TFLite | Pipeline lượng tử hoá chuyển sang **PT2E flow**. Ràng buộc backend (xem §4). |

**Ba mức precision — đổi tên tương ứng:**

```
L1: FP32 native (.pth)
      │  torch.export.export_for_training → prepare_pt2e → calibrate → convert_pt2e
L2: FP32 ExecuTorch (.pte, XNNPACK delegate)
      │
L3: INT8 ExecuTorch (.pte, PT2E static quantization)
```

Hai chỉ số chẩn đoán giữ nguyên ý nghĩa, chỉ đổi tên artifact:
- `conversion_drop = L1 − L2` (mục tiêu < 1%) — đo mất mát do **export/lowering**
- `quantization_drop = L2 − L3` (mục tiêu < 2%) — đo mất mát do **INT8 PTQ**
- Nếu `quantization_drop > 2%` → cân nhắc QAT.

---

## 1. Các delta còn lại cần bạn quyết định

Ngoài hai item đã chốt ở §0, `ARCHITECTURE.md` còn chứa 5 thay đổi so với proposal cũ. Chúng **chưa được xác nhận là chủ đích** — cần chốt để tránh lệch giữa code và luận văn.

| # | Nội dung | Cũ (proposal) | Mới (ARCHITECTURE.md) | Cần làm gì |
|---|---|---|---|---|
| 3 | **Công thức KD loss** | `α·Focal + (1−α)·T²·KLDiv` (softmax, multi-class) | `0.3·Focal + 0.7·T²·BCE(σ(s/T), σ(t/T))` | ⚠️ **Xem §2, §3** — thay đổi này có hệ quả lý thuyết lớn |
| 4 | **Headline metric** | AUC-ROC | **AUPRC** (pAUC vẫn primary) | ✅ Đúng — chỉ cần làm rõ vai trò kép (§6.3) |
| 5 | **Prevalence** | 0,9% | **~0,4%** | ⚠️ Chốt con số & ghi rõ nguồn gốc (§7) |
| 6 | **MixUp/CutMix/CutOut** | Không đề cập | **Bị cấm** (`_FORBIDDEN_OPS`) | ✅ Đúng — cần viết rõ lý do vào luận văn (§5.3) |
| 7 | **`cudnn_deterministic`** | seed=42 bắt buộc mọi nơi | **`false` cho `maxvit_base`** | 🔴 **Mâu thuẫn với mandate reproducibility** (§4.3) |

---

## 2. ⛔ PHÁT HIỆN CỐT LÕI: Logit-based KD hiện đại **suy biến** trong bài toán binary

Đây là phát hiện quan trọng nhất của đợt rà soát này, và nó **đảo ngược khuyến nghị trước đó** (vốn đề xuất DKD, logit standardization, OFA-KD).

### 2.1. Vấn đề

Model của dự án xuất **1 raw logit + sigmoid** (`build_head()` = `Dropout → Linear(in, 1)`). Trong khi đó, gần như toàn bộ nhánh "SOTA logit-based KD" 2022–2026 được xây dựng trên **vector logit K chiều + softmax**, và khai thác **quan hệ liên-lớp** (inter-class relations / "dark knowledge").

**Binary classification không có quan hệ liên-lớp.** Teacher chỉ truyền được **một con số duy nhất**: mức độ tự tin.

### 2.2. Kiểm chứng toán học

| Phương pháp | Với K=1 (sigmoid — thiết kế hiện tại) | Với K=2 (softmax — nếu đổi head) | Kết luận |
|---|---|---|---|
| **Logit Standardization** [4] | Z-score cần std trên chiều class → std = 0 → **không xác định** | μ=(z₀+z₁)/2, σ=\|z₁−z₀\|/2 → logit chuẩn hoá **luôn bằng [−1,+1]** bất kể input | ❌ **Suy biến ở cả hai** |
| **DKD** (Decoupled KD) [5] | Không tồn tại non-target class | Chỉ 1 non-target → sau chuẩn hoá p̂ ≡ 1 → **NCKD ≡ 0** → DKD thoái hoá thành TCKD | ❌ **Vô dụng cho binary** |
| **OFA-KD** [6] | Chiếu feature vào logit-space 1 chiều | Logit-space 2 chiều suy biến | ❌ Không dùng được như paper |
| **DIST** — *inter-class* relation [7] | Suy biến | Suy biến | ❌ |
| **DIST** — *intra-batch* relation [7] | Pearson correlation trên **chiều batch** → **vẫn hợp lệ** | Hợp lệ | ✅ **Dùng được** |

> **Điểm mấu chốt:** đổi sang 2-logit softmax head **KHÔNG** cứu được vấn đề. DKD và logit standardization suy biến ở **cả K=1 lẫn K=2**. Đây là giới hạn nội tại của binary task, không phải lỗi thiết kế.

### 2.3. Hệ quả — đường nâng cấp KD **đúng**

Không gian cải tiến KD nằm ở **feature-based** và **relational** KD, **không** nằm ở logit loss.

| Hướng | Phương pháp | Vì sao hợp lệ ở K=1 | Chi phí | Ưu tiên |
|---|---|---|---|---|
| **Feature-based** | **SimKD** [10], ReviewKD [9], FitNet [8], Attention Transfer | Hoạt động trên **backbone features** — hoàn toàn độc lập với K | TB (cần projector, nhất là cross-architecture) | ⭐⭐⭐ |
| **Relational** | **RKD** [11] (distance/angle giữa các sample), CRD [12], DIST intra-batch [7] | Quan hệ **giữa các mẫu trong batch**, không phải giữa các lớp | Thấp–TB | ⭐⭐⭐ |
| **Logit** | **MSE trên raw logit** [13] | Hợp lệ ở K=1. Lý thuyết [13]: KL ở T lớn ≈ logit matching | **Rất thấp** | ⭐⭐ (thử ngay) |

**Vì sao feature-based đặc biệt quan trọng ở đây:** capacity gap giữa teacher (54–119M params) và student (9,7–12,6M) là **~5–12×**, nằm trong vùng cảnh báo của Cho & Hariharan [1] và TAKD [2]. Feature-based KD giải quyết **đúng** vấn đề đó — student học *biểu diễn trung gian*, không chỉ học *đầu ra cuối*. Với binary task, đầu ra cuối chứa quá ít thông tin để thu hẹp gap.

### 2.4. Đoạn lập luận đề xuất cho **Chương 2**

> *"Trong bài toán phân loại nhị phân với single-logit head, các phương pháp logit-based knowledge distillation tiên tiến — DKD [5], logit standardization [4], OFA-KD [6] — đều suy biến về mặt toán học, vì chúng khai thác quan hệ liên-lớp (inter-class relations) vốn không tồn tại khi K ≤ 2. Cụ thể, phép chuẩn hoá Z-score của [4] không xác định khi K=1 và cho kết quả hằng số khi K=2; thành phần NCKD của [5] triệt tiêu đồng nhất khi chỉ có một lớp non-target. Do đó, không gian cải tiến KD cho bài toán này nằm ở **feature-based distillation** và **relational distillation**, chứ không nằm ở việc tinh chỉnh logit loss. Đây cũng là lý do nghiên cứu này lựa chọn [phương pháp X] thay vì áp dụng máy móc các SOTA KD method vốn được thiết kế cho multi-class benchmark như CIFAR-100/ImageNet."*

Đây là một luận điểm lý thuyết **có giá trị học thuật thật** — nó cho thấy tác giả hiểu *vì sao* không dùng SOTA method, thay vì chỉ không biết đến chúng.

---

## 3. ⚠️ Cảnh báo: `hard loss + logit-level BCE` — cần một ablation

### 3.1. Bối cảnh

Loss hiện tại có cấu trúc:

```
L_total = 0.3 · Focal(σ(s), y)            ← probability-level (hard)
        + 0.7 · T² · BCE(σ(s/T), σ(t/T))  ← logit-level (soft)
```

DHKD (KDD 2025) [14] phát hiện một hiện tượng đáng chú ý: kết hợp **BinaryKL loss (logit-level)** với **CE loss (probability-level)** làm student **suy giảm hiệu năng — thậm chí tệ hơn dùng riêng từng loss**. Nguyên nhân được chứng minh qua lý thuyết *neural collapse*: gradient của hai loss **mâu thuẫn nhau tại linear classifier head**, nhưng **không mâu thuẫn tại backbone**. Kết quả: classifier head không hội tụ được về simplex ETF → collapse.

Giải pháp của [14]: **dual-head** — head chính học hard loss, head phụ học logit-level loss, cả hai chia sẻ backbone. Nhờ đó giữ được tác dụng tốt của BinaryKL lên backbone mà không phá classifier.

### 3.2. Mức độ áp dụng — phải trung thực

Lập luận của [14] dựa trên hình học **simplex ETF**, vốn **suy biến khi K=1** (không có "khung đẳng giác" nào để collapse khi chỉ có một vector trọng số duy nhất trong classifier). Do đó:

> **KHÔNG thể khẳng định** loss hiện tại chắc chắn bị collapse. Nhưng cơ chế nền — *"logit-level loss và probability-level loss có thể xung đột gradient tại classifier head"* — vẫn là một rủi ro hợp lý cần loại trừ bằng thực nghiệm.

### 3.3. Ablation đề xuất (chi phí: 3 run, 1 fold)

| Nhánh | Loss | Kỳ vọng |
|---|---|---|
| A | Chỉ `Focal` (no KD) | Baseline |
| B | Chỉ `T²·BCE` (KD only, bỏ hard loss) | — |
| C | `0.3·Focal + 0.7·T²·BCE` (hiện tại) | Nên **tốt hơn cả A và B** |

**Đọc kết quả:**
- Nếu **C > max(A, B)** → không có xung đột. Giữ nguyên thiết kế. ✅
- Nếu **C < max(A, B)** → **đã tái hiện hiện tượng DHKD trong binary setting**. Đây là một **finding có thể công bố**, và fix bằng dual-head [14].

### 3.4. ✅ Xác nhận tích cực: hệ số T² là ĐÚNG

Hệ số `T²` thường bị coi là "chỉ đúng cho softmax-KL". **Không phải.** Nó cũng đúng cho sigmoid/BCE:

```
∂/∂s  BCE(σ(s/T), σ(t/T))  =  (1/T) · (σ(s/T) − σ(t/T))

Với T lớn:  σ(s/T) − σ(t/T)  ≈  (s − t) / (4T)        [vì σ'(0) = 1/4]

⟹ gradient ≈ (s − t) / (4T²)

⟹ nhân T² khôi phục đúng thang gradient — chính là lập luận gốc của Hinton.
```

Thiết kế `T=4.0` + hệ số `T²` là **hợp lý và bảo vệ được**. Không cần đổi.

---

## 4. ExecuTorch / XNNPACK / Pixel 6a — đánh giá lại lượng tử hoá

### 4.1. 🔴 Ràng buộc phần cứng cần ghi rõ trong luận văn

ExecuTorch cung cấp delegate: **CoreML** (iOS), **XNNPACK** (CPU), **Qualcomm QNN** (NPU Snapdragon).

**Pixel 6a dùng Tensor G1 — KHÔNG phải Snapdragon.**

| Backend | Khả dụng trên Pixel 6a? | Ghi chú |
|---|---|---|
| XNNPACK (CPU) | ✅ **Có** | Đường chính thực tế |
| Qualcomm QNN (NPU) | ❌ **Không** | Chỉ cho Snapdragon |
| EdgeTPU (Tensor) | ❌ Không | Không có ExecuTorch backend; thuộc địa hạt TFLite/NNAPI (NNAPI đã deprecated từ Android 15) |
| Vulkan (Mali-G78) | ⚠️ Có nhưng non | Không nên phụ thuộc |

> ### ⚠️ Phải phát biểu chính xác trong Chương 4
> *"Latency được đo trên **CPU big-core thông qua XNNPACK delegate** của ExecuTorch. Tăng tốc NPU không khả dụng cho SoC Tensor G1 trong ExecuTorch tại thời điểm nghiên cứu, do backend Qualcomm QNN chỉ hỗ trợ nền tảng Snapdragon."*

Đây **không phải điểm yếu** — chỉ cần phát biểu đúng. Nếu không, hội đồng/reviewer sẽ hỏi và câu trả lời sẽ trở nên lúng túng.

### 4.2. Hệ quả: rủi ro INT8 với student transformer

XNNPACK INT8 phủ tốt **conv / linear**, nhưng **softmax, LayerNorm, attention** thường **không được quantize và không được delegate** → graph bị phân mảnh → fallback về portable kernel FP32 → overhead quantize/dequantize ở mỗi ranh giới partition.

> **Hệ quả nghiêm trọng:** INT8 có thể **không nhanh hơn FP32 đáng kể — thậm chí chậm hơn** — với các student có nhiều attention.

| Student | Rủi ro INT8 trên XNNPACK | Dự đoán |
|---|---|---|
| `mobilenetv4_conv_medium` | **Thấp** — CNN thuần (UIB blocks) | ✅ Speedup 2–3× như kỳ vọng |
| `fastvit_sa12` | **Trung bình** — RepMixer reparameterization giúp fold branch, nhưng vẫn có self-attention ở stage cuối | ⚠️ Speedup giảm |
| `efficientformerv2_s2` | **Cao** — attention downsampling xuyên nhiều stage | ⚠️⚠️ **Có thể INT8 ≈ FP32** |

### 4.3. 🎯 Đây là cơ hội, không phải rủi ro

`ARCHITECTURE.md` §6 đã tự cảnh báo đúng: *"ranking có thể lật trên mobile, nhất là student transformer"*. **Hãy biến điều này thành đóng góp chính của Chương 4.**

Rất ít paper đo được điều này. Câu hỏi nghiên cứu:

> *"Mobile-ViT nào thực sự giữ được lợi thế accuracy sau khi qua INT8 + ExecuTorch trên CPU thật — thay vì chỉ tốt trên bảng FLOPs?"*

Nếu `efficientformerv2_s2` **thắng ở FP32 nhưng thua `mobilenetv4_conv_medium` ở INT8 on-device** → đó là **finding**, không phải thất bại. Đó chính là sự khác biệt giữa "SOTA trên leaderboard" và "SOTA trên Pareto frontier deployment".

### 4.4. Verdict cập nhật cho 6 model

| Model | Vai trò | Verdict | Lý do |
|---|---|---|---|
| `efficientnetv2_m` | Teacher | ✅ **GIỮ — teacher chính** | CNN thuần, capacity gap ~5× (thấp nhất trong 3), INT8-friendly nếu cần |
| `convnextv2_base` | Teacher | ✅ **Giữ được** | Teacher **không cần export** → độ nặng chỉ tốn training time, không ảnh hưởng deployment |
| `maxvit_base` | Teacher | ❌ **BỎ** | ~119M params / ~43,7 GMACs nhưng top-1 (84,9%) **thấp hơn cả hai teacher kia**. **Và:** `cudnn_deterministic=false` **phá vỡ mandate seed=42** → không reproducible |
| `mobilenetv4_conv_medium` | Student | ✅ **Tốt nhất** | Càng đúng hơn trên XNNPACK. Pareto-optimal đa nền tảng |
| `fastvit_sa12` | Student | ✅ Giữ | Structural reparameterization là lợi thế **thật** trên ExecuTorch |
| `efficientformerv2_s2` | Student | ✅ Giữ **như đối tượng nghiên cứu** | Giá trị nằm ở việc phơi bày giới hạn INT8 của mobile-ViT |

---

## 5. ✅ Những gì đang làm ĐÚNG (giữ nguyên, tự tin bảo vệ)

| # | Quyết định | Vì sao đúng |
|---|---|---|
| 5.1 | **AUPRC làm headline** ở prevalence ~0,4% | AUC-ROC bị **thổi phồng** ở imbalance cực đoan (specificity cao dễ đạt khi negative áp đảo). AUPRC phản ánh trải nghiệm thực: *bao nhiêu false positive trên mỗi true positive* |
| 5.2 | **`sens_at_{90,95}spec`** | Đúng chuẩn báo cáo lâm sàng, dễ diễn giải cho hội đồng y khoa |
| 5.3 | **Cấm MixUp/CutMix/CutOut** | Đúng về y khoa: trộn lesion tạo ảnh **phi sinh lý**; ở 0,4% malignant, CutMix dễ **làm hỏng nhãn** (dán mảnh malignant vào ảnh benign nhưng nhãn không đổi tương ứng). ⚠️ **Phải ghi rõ lý do trong luận văn** — đây là quyết định đi ngược mặc định của CV, reviewer sẽ hỏi |
| 5.4 | **`test_split.csv` độc lập + patient-disjoint** | Chặn data leakage ở mức bệnh nhân |
| 5.5 | **`val − test` làm tín hiệu overfit** | Thiết kế chẩn đoán tốt, ít người làm |
| 5.6 | **Latency cluster CPU = proxy, không phải số điện thoại** | Tự cảnh báo đúng, tránh một sai lầm phổ biến |
| 5.7 | **Aggregate mean ± std trên 5 fold** | Đúng — 1 fold đơn lẻ có variance rất rộng ở prevalence thấp |

---

## 6. 🔴 Ba rủi ro MỚI phát hiện

### 6.1. Calibration — nghiêm trọng nhất, chưa thấy xử lý

**Vấn đề:** dự án đang chống imbalance bằng **ba lớp chồng nhau**:

```
DynamicUndersampledSampler (1:5)  +  focal γ=2.0  +  focal α=0.25
```

- pAUC và AUPRC là **ranking metrics** → **miễn nhiễm** với miscalibration. Không ảnh hưởng số liệu Chương 4. ✅
- **NHƯNG** sản phẩm hiển thị **"risk probability"** cho người dùng cuối.

Sau undersampling 1:5, model học trên prior **16,7%**, không phải **0,4%** thật:

```
σ(logit) phản ánh P(malignant | đã undersample) ≈ 16,7% prior
Thực tế                                          ≈  0,4% prior
⟹ xác suất hiển thị bị thổi phồng ~40×
```

> ### ⚠️ Rủi ro lâm sàng thật
> Một screening app hiển thị **"nguy cơ 15%"** cho một nốt ruồi lành tính sẽ gây **lo lắng không cần thiết** và **quá tải phòng khám da liễu** — đúng thứ mà công cụ này lẽ ra phải giảm.

**Fix đề xuất:**
1. Thêm bước **post-hoc calibration**: prior correction (điều chỉnh log-odds theo tỉ lệ prior), hoặc Platt scaling / isotonic regression.
2. Fit calibrator trên một **held-out set giữ nguyên prevalence gốc** (KHÔNG undersample).
3. Báo cáo **calibration curve + Brier score / ECE** — đây là một mục Chương 4 rất đáng viết và hầu như không tốn compute.

**Ghi chú phụ:** `focal α=0.25` đang **down-weight lớp positive** (malignant, lớp hiếm). Trong RetinaNet gốc điều này là có chủ đích (γ đã đủ mạnh), nhưng ở đây nó **chồng lên** undersampling 1:5 → cần kiểm tra lại xem có đúng ý đồ không, hay nên đảo thành α=0.75.

### 6.2. Ma trận thực nghiệm không khớp với 3 teacher

`ARCHITECTURE.md` §1: *"Baseline set: 30 run (3 arch × 2 điều kiện × 5 fold)"*.

Con số này **chỉ tính student**, ngầm **cố định 1 teacher**. Nhưng registry khai báo **3 teacher**. Nếu muốn so sánh đủ:

```
3 teacher × 3 student × 5 fold  = 45 KD run
+ 3 student × 5 fold (no-KD)    = 15 run
+ 3 teacher × 5 fold (train)    = 15 run
                                 ─────────
                                   75 run
```

**Đề xuất (giữ ngân sách 30 run):**
- Chọn **`efficientnetv2_m` làm teacher chính** → chạy đủ 5 fold × 3 student × 2 điều kiện = **30 run** (giữ nguyên baseline set).
- Hai teacher còn lại → **ablation 1 fold** (≈ 6 run) để trả lời câu hỏi phụ: *"teacher mạnh hơn có cho student tốt hơn không?"*
- **Bonus:** chính ablation này cho **bằng chứng trực tiếp về capacity-gap problem** [1][2] — nếu `convnextv2_base` (88,7M) cho student **kém hơn** `efficientnetv2_m` (54M), bạn đã tái hiện được kết quả của Cho & Hariharan trên domain y tế. Đó là một đóng góp.

### 6.3. pAUC vs AUPRC — "primary" là cái nào?

`ARCHITECTURE.md` §0 nói pAUC là *"metric chính"* nhưng AUPRC là *"headline"*. Hai từ này mâu thuẫn bề mặt. **Hội đồng sẽ hỏi.**

**Phát biểu đề xuất — hai vai trò khác nhau, không mâu thuẫn:**

| Metric | Vai trò | Vì sao cần |
|---|---|---|
| **pAUC@TPR≥80%** | **Metric đối chiếu** với ISIC 2024 | Cho phép so sánh trực tiếp với literature và leaderboard. Bắt buộc phải có |
| **AUPRC** | **Metric đánh giá lâm sàng chính** | Phản ánh đúng hiệu năng ở prevalence thực ~0,4% |

---

## 7. Ghi chú về prevalence — cần chốt con số

Có ba con số đang lưu hành, cần thống nhất và **ghi rõ nguồn gốc**:

| Nguồn | Prevalence | Ghi chú |
|---|---|---|
| Proposal cũ | 0,9% | Đã lỗi thời |
| `ARCHITECTURE.md` | **~0,4%** | Con số đang dùng — nhưng **của tập nào?** |
| ISIC 2024 private test set (paper gốc) | **~0,09%** (342 / 370.704) | Prevalence "thật" của SLICE-3D |

Chênh lệch 0,4% vs 0,09% nhiều khả năng do **quality filter + resize + merge PAD-UFES-20** trong `prepare_data.py`. **Cần ghi rõ:** *"prevalence sau tiền xử lý = X% trên tập Y"*, để reviewer không hiểu nhầm là sai số.

---

## 8. Kế hoạch hành động (theo ưu tiên)

### 🟢 Làm ngay — chi phí ~0

- [ ] **Ghi rõ trong Chương 4:** latency = **CPU / XNNPACK trên Pixel 6a**, không phải NPU (§4.1)
- [ ] **Phát biểu rõ vai trò kép** pAUC (đối chiếu ISIC) vs AUPRC (lâm sàng) (§6.3)
- [ ] **Bỏ `maxvit_base`** — `cudnn_deterministic=false` mâu thuẫn mandate seed=42, và accuracy thấp hơn 2 teacher kia dù nặng gấp đôi (§4.4)
- [ ] **Chốt con số prevalence** và ghi rõ nó là của tập nào, sau bước tiền xử lý nào (§7)
- [ ] **Viết lý do cấm MixUp/CutMix** vào luận văn (§5.3)

### 🟡 Ưu tiên cao — chi phí thấp, giá trị lớn

- [ ] **Thêm post-hoc calibration** + báo cáo calibration curve/ECE — rủi ro lâm sàng thật, fix rẻ (§6.1)
- [ ] **Kiểm tra lại `focal α=0.25`** — có đang down-weight nhầm lớp malignant không? (§6.1)
- [ ] **Ablation 3 nhánh** focal-only / BCE-KD-only / cả hai (3 run, 1 fold) → kiểm tra hiện tượng DHKD (§3.3)
- [ ] **Chốt 1 teacher chính** (`efficientnetv2_m`), 2 teacher còn lại → ablation 1-fold (§6.2)

### 🔵 Ưu tiên trung bình — nếu còn thời gian

- [ ] **Thêm một feature-based KD branch** (SimKD hoặc RKD) — đây mới là hướng nâng cấp KD **hợp lệ về mặt toán học** cho binary (§2.3). Thay thế cho khuyến nghị DKD/logit-standardization **đã bị bác bỏ**
- [ ] **Thử MSE trên raw logit** [13] như một baseline KD thứ hai — chi phí gần bằng 0
- [ ] **Cân nhắc PanDerm làm teacher** — giờ **dễ hơn nhiều** vì stack đã thuần PyTorch. Foundation model da liễu, pretrain trên 2,1M ảnh gồm cả **TBP** (đúng modality của SLICE-3D)
- [ ] ~~Google Derm Foundation~~ — **loại bỏ khỏi cân nhắc**: hệ TF/embedding-API, lệch stack sau khi chuyển thuần PyTorch

---

## 9. Caveats & mức độ chắc chắn

Ghi rõ để không tự tin quá mức:

| Nhận định | Độ chắc chắn | Ghi chú |
|---|---|---|
| DKD / logit standardization suy biến ở K≤2 | 🟢 **Cao** — chứng minh được bằng đại số | Kiểm chứng trực tiếp từ công thức gốc |
| Hệ số T² đúng cho sigmoid/BCE | 🟢 **Cao** — dẫn xuất được | |
| QNN không khả dụng trên Tensor G1 | 🟢 **Cao** | QNN là backend Qualcomm-only |
| Hiện tượng DHKD collapse xảy ra ở K=1 | 🟡 **Thấp–TB** | Lý thuyết ETF của [14] **suy biến ở K=1**. Cần ablation, **không được khẳng định trước** |
| INT8 làm chậm `efficientformerv2_s2` | 🟡 **Trung bình** | Suy luận từ đặc điểm kiến trúc + coverage của XNNPACK, **chưa đo** |
| Prevalence 0,4% vs 0,09% | 🟡 Cần xác minh | Phụ thuộc pipeline tiền xử lý của dự án |
| Số params/FLOPs của 6 model | 🟡 Nên verify | Có nhiều biến thể weight (`in1k` vs `distilled`), chênh 0,5–1% |

---

## 10. Tài liệu tham khảo

[1] Cho, J.H. & Hariharan, B. (2019). "On the Efficacy of Knowledge Distillation." *ICCV 2019*, pp. 4794–4802.
[2] Mirzadeh, S.I. et al. (2020). "Improved Knowledge Distillation via Teacher Assistant." *AAAI 2020*. arXiv:1902.03393
[3] Hinton, G. et al. (2015). "Distilling the Knowledge in a Neural Network." arXiv:1503.02531
[4] Sun, S. et al. (2024). "Logit Standardization in Knowledge Distillation." *CVPR 2024 (Highlight)*. arXiv:2403.01427
[5] Zhao, B. et al. (2022). "Decoupled Knowledge Distillation." *CVPR 2022*. arXiv:2203.08679
[6] Hao, Z. et al. (2023). "One-for-All: Bridge the Gap Between Heterogeneous Architectures in Knowledge Distillation." *NeurIPS 2023*.
[7] Huang, T. et al. (2022). "Knowledge Distillation from A Stronger Teacher (DIST)." *NeurIPS 2022*. arXiv:2205.10536
[8] Romero, A. et al. (2015). "FitNets: Hints for Thin Deep Nets." *ICLR 2015*. arXiv:1412.6550
[9] Chen, P. et al. (2021). "Distilling Knowledge via Knowledge Review (ReviewKD)." *CVPR 2021*. arXiv:2104.09044
[10] Chen, D. et al. (2022). "Knowledge Distillation with the Reused Teacher Classifier (SimKD)." *CVPR 2022*. arXiv:2203.14001
[11] Park, W. et al. (2019). "Relational Knowledge Distillation." *CVPR 2019*. arXiv:1904.05068
[12] Tian, Y. et al. (2020). "Contrastive Representation Distillation (CRD)." *ICLR 2020*. arXiv:1910.10699
[13] Kim, T. et al. (2021). "Comparing Kullback-Leibler Divergence and Mean Squared Error Loss in Knowledge Distillation." *IJCAI 2021*. arXiv:2105.08919
[14] Yang, P. et al. (2025). "Dual-Head Knowledge Distillation: Enhancing Logits Utilization with an Auxiliary Head." *KDD 2025*. arXiv:2411.08937
[15] Lin, T.-Y. et al. (2017). "Focal Loss for Dense Object Detection." *ICCV 2017*. arXiv:1708.02002
[16] Kurtansky, N.R. et al. (2025). "Automated triage of cancer-suspicious skin lesions with 3D total-body photography." *npj Digital Medicine*. PMC12639164
[17] Yan, S. et al. (2025). "A multimodal vision foundation model for clinical dermatology (PanDerm)." *Nature Medicine* 31(8):2691–2702. arXiv:2410.15038

---

> **Bảo trì file này:** đây là **snapshot review tại 2026-07-13**, không phải doc sống. Khi các quyết định ở §8 được chốt, chuyển chúng vào `CLAUDE.md` (§Architecture) hoặc `ARCHITECTURE.md`, và đánh dấu file này là *superseded*.
