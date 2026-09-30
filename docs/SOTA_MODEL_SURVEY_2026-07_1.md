# THỐNG KÊ MÔ HÌNH SOTA — Teacher & Student cho KD phát hiện ung thư da trên edge

> **Ngày:** 2026-07 · **Phạm vi:** khảo sát teacher/student SOTA, verdict giữ/bỏ/thay, đề xuất thay thế.
> **Hai câu hỏi định hướng toàn bộ file này:**
> 1. **KD có áp dụng tốt cho bài toán này không?** (§3)
> 2. **Student cuối có chạy tốt trên mobile (Pixel 6a / ExecuTorch / XNNPACK) không?** (§4)
> **Trạng thái:** tài liệu khảo sát để ra quyết định — chưa áp dụng vào code.

---

## 0. Ràng buộc đã chốt (neo mọi đánh giá bên dưới)

| Ràng buộc | Giá trị | Hệ quả cho lựa chọn model |
|---|---|---|
| Framework | PyTorch + `timm>=1.0`, checkpoint `.pth` | Chỉ xét model có trong `timm` hoặc port PyTorch sạch |
| Export | **ExecuTorch `.pte`**, KHÔNG TFLite | Lượng tử hoá theo **PT2E flow** |
| Thiết bị | **Pixel 6a — Tensor G1** | **KHÔNG có QNN NPU** → chỉ **XNNPACK (CPU)** |
| Head | **Single raw logit + sigmoid** (nhị phân) | Loại bỏ nhiều logit-based KD (xem §3.2) |
| KD loss | `0.3·Focal + 0.7·T²·BCE(σ(s/T),σ(t/T))`, T=4 | Distill ở logit-level nhị phân — nghèo dark knowledge |
| Metric | pAUC@TPR≥80 (đối chiếu ISIC), **AUPRC** (headline) | Trần image-only thực tế ~0,142–0,16 pAUC |
| Prevalence | ~0,39% sau tiền xử lý | Ưu tiên feature-based KD để thu hẹp capacity gap |
| Mandate | `seed=42` mọi nơi | Loại model cần `cudnn_deterministic=false` |

---

## 1. Teacher — bảng thống kê & verdict

### 1.1. Ba teacher đang chọn

| Teacher (`timm`) | Params (M) | GMACs | ImageNet top-1 | Pretrain | Capacity gap vs student¹ | Verdict |
|---|---|---|---|---|---|---|
| **`efficientnetv2_m`** | ~54 | ~24 @480 | 85,1% | IN1k/IN21k | **~5×** (thấp nhất) | ✅ **GIỮ — teacher chính** |
| **`convnextv2_base`** | 88,7 | 15,4 @224 / 45,2 @384 | 86,7 / 87,6% | FCMAE→IN22k→1k | ~7–9× | ✅ Giữ được² |
| **`maxvit_base`** | ~119 | ~43,7 | 84,9% | IN1k | **~10–12×** (cao nhất) | ❌ **BỎ** |

¹ Gap tính theo params so với student ~9,7–12,6M.
² Teacher **không cần export** ra `.pte` → độ nặng chỉ tốn training-time, không ảnh hưởng deployment.

**Vì sao bỏ `maxvit_base`:**
- Nặng nhất (~119M, ~43,7 GMACs) nhưng top-1 (84,9%) **thấp hơn cả hai teacher kia** → tệ nhất về hiệu suất/chi phí.
- Cần `cudnn_deterministic=false` → **phá vỡ mandate `seed=42`** → không reproducible. Đây là lý do quyết định.
- Block-attention + grid-attention là kiến trúc teacher tạo capacity gap lớn nhất với student nhỏ.

### 1.2. Teacher thay thế / bổ sung đáng cân nhắc

| Teacher | Params | Điểm mạnh | `timm`/PyTorch | Đề xuất |
|---|---|---|---|---|
| **PanDerm** (ViT-base, Nat. Med. 2025) | ~86 (base) | ⭐ Foundation model **da liễu**, pretrain 2,1M ảnh gồm **TBP** (đúng modality SLICE-3D); vượt clinician ở melanoma sớm | PyTorch (dễ hơn sau khi chuyển thuần torch) | ⭐ **Đáng thử nhất** — teacher domain-specific |
| **ConvNeXt V2-Tiny** | ~28 | Thu hẹp gap về **~2–3×**, quantizable hơn Base | ✅ `timm` | ✅ Thay `maxvit_base` như teacher thứ 2 |
| **EfficientNetV2-S** | ~24 | CNN thuần, gap ~2×, rất ổn định | ✅ `timm` | ✅ Ứng viên teacher tầm trung |
| **DINOv3** (Meta, 8/2025) | ViT 21M→840M; ConvNeXt 29M→200M | Generic-SSL foundation, dense features mạnh nhất hiện tại; transfer y tế tốt (thắng MIDOG 2025 histopathology) | ✅ HF (PyTorch) | 🔵 **Teacher variant nghiên cứu** — xem phân tích §1.3 |
| ~~Google Derm Foundation~~ | — | Da liễu, nhưng **hệ TF/embedding-API** | ❌ Lệch stack | ❌ **Loại** sau khi chuyển thuần PyTorch |

> **Khuyến nghị teacher:** giữ **`efficientnetv2_m` làm teacher chính** (gap thấp nhất, CNN thuần); thay `maxvit_base` bằng **`convnextv2_tiny`** hoặc **`efficientnetv2_s`** để thu hẹp capacity gap; nếu còn thời gian, thử **PanDerm** như một teacher variant — đây là đóng góp học thuật giá trị nhất (distill từ foundation model da liễu → student mobile).

### 1.3. Phân tích riêng: DINOv3 — teacher hay student?

**Kết luận nhanh:** ❌ KHÔNG dùng làm student; 🔵 hợp lệ làm **teacher variant nghiên cứu**, nhưng **xếp sau PanDerm** cho task da liễu.

**Thông số họ DINOv3** (Meta, arXiv:2508.10104, 8/2025): distill từ ViT-7B thành suite ViT (21M→840M) + ConvNeXt (T 29M, S, B, L 200M). Biến thể nhỏ nhất ViT-S = 21,6M params, 82,4 MB @FP32 / 41,2 MB @FP16. Là **SSL frozen-feature model**, thế mạnh công bố là dùng backbone đông cứng không cần fine-tune; thế mạnh lớn nhất là **dense features** (segmentation/depth/correspondence).

**❌ Vì sao KHÔNG làm student:**
- Biến thể nhỏ nhất (ViT-S 21,6M) đã **~2× ngân sách param** của student slot (~9,7M), và là **ViT thuần** (patch-16, RoPE, register tokens, SwiGLU) → đúng nhóm op **XNNPACK INT8 xử lý kém trên CPU** Tensor G1. Rủi ro còn cao hơn `efficientformerv2_s2`.
- Biến thể ConvNeXt-T (29M) mobile-friendly hơn nhưng vẫn **~3× param budget**, không thiết kế cho Pareto frontier điện thoại như MobileNetV4/RepViT.
- **Không có biến thể "DINOv3-mobile"** — "nhỏ" của DINOv3 vẫn là cỡ edge-server, không phải phone.

**🔵 Vì sao làm teacher thì hợp lệ nhưng không phải #1:**

| Tiêu chí | DINOv3 | Đối thủ tốt hơn |
|---|---|---|
| Domain relevance | Generic (ảnh web) | **PanDerm** pretrain 2,1M ảnh da liễu gồm TBP — dark knowledge sát task |
| Capacity gap | ViT-B 86M / ViT-L 300M → student ~10M = gap **9–30×** | `efficientnetv2_m` (~5×), `convnextv2_tiny` (~3×) |
| Cơ chế transfer ở K≤2 | Logit-level suy biến → **bắt buộc feature-based cross-arch** (ViT patch-token → CNN feature-map, cần projector + căn chỉnh spatial — khó nhất) | CNN→CNN căn chỉnh feature dễ hơn nhiều |

- Teacher **không cần export** → chuyện ViT khó quantize **không** thành vấn đề ở vai trò teacher. ✅
- Bằng chứng transfer y tế mạnh: DINOv3-H+ + LoRA (~1,3M params train) **thắng MIDOG 2025 Task 2** (histopathology, low-prevalence). Nhưng đây là histopathology, **không phải dermatoscopy/clinical**.
- Vì logit-level KD gần như không truyền gì ở nhị phân single-logit, **toàn bộ giá trị DINOv3 phải đi qua feature** — mà feature ViT → student CNN là cặp cross-architecture khó căn chỉnh nhất. Nếu dùng ViT nhỏ (S+/B) để giữ gap hợp lý thì lại mất phần lớn ưu thế "foundation khổng lồ".
- Là SSL frozen-feature → để xuất binary logit vẫn phải fine-tune như mọi backbone; ưu thế dense-feature phần lớn **bị lãng phí** khi phân loại nhị phân trên crop TBP độ phân giải thấp.

**Nếu vẫn thử DINOv3 làm teacher:**
- Dùng **ViT-S+ (29M)** hoặc **ConvNeXt-B distilled** để giữ capacity gap hợp lý.
- **Bắt buộc feature-based KD**, KHÔNG logit-based.
- Đặt cạnh 2 teacher khác thành trục ablation đẹp: *"generic-SSL (DINOv3) vs domain-foundation (PanDerm) vs supervised-CNN (`efficientnetv2_m`) — cái nào distill tốt nhất xuống student mobile?"* Nhưng nếu chỉ đầu tư **một** hướng foundation-model → **PanDerm > DINOv3** cho da liễu.

> ⚠️ **Caveat (ngoại suy):** không tìm thấy benchmark DINOv3 fine-tune **riêng cho da liễu/ISIC** đã công bố — bằng chứng transfer y tế mạnh nhất hiện là histopathology. Lợi ích cụ thể cho đúng bài toán này **chưa có số bảo chứng**.

---

## 2. Student — bảng thống kê & verdict (trọng tâm: **chạy tốt trên mobile**)

### 2.1. Ba student đang chọn

| Student (`timm`) | Params (M) | GFLOPs | ImageNet top-1 | Họ kiến trúc | INT8 trên XNNPACK³ | Verdict |
|---|---|---|---|---|---|---|
| **`mobilenetv4_conv_medium`** | ~9,7 | ~1,0 | ~79,9% | **CNN thuần** (UIB) | ✅ **Tốt nhất** — speedup 2–3× | ✅ **GIỮ — student tốt nhất cho mobile** |
| **`fastvit_sa12`** | ~10,9 | ~1,9 | ~80,6% | Hybrid (RepMixer + attn cuối) | ⚠️ TB — reparam giúp, attn cuối cản | ✅ Giữ |
| **`efficientformerv2_s2`** | ~12,6 | ~1,3 | ~82,0% | Mobile-ViT (attn downsampling) | ⚠️⚠️ **Cao rủi ro — có thể INT8 ≈ FP32** | ✅ Giữ **như đối tượng nghiên cứu** |

³ Đánh giá định tính dựa trên coverage của XNNPACK INT8 (conv/linear tốt; softmax/LayerNorm/attention thường không quantize/không delegate → phân mảnh graph). **Chưa phải số đo — xem §4 & Caveats.**

**Nhận định trọng tâm mobile:**
- `mobilenetv4_conv_medium` là **student an toàn nhất và nhanh nhất** trên đường CPU/XNNPACK — CNN thuần, không có op cản delegate. Đây nên là **student đại diện** cho kết luận "chạy tốt trên mobile".
- `efficientformerv2_s2` **top-1 cao nhất trên giấy** nhưng nhiều attention downsampling → nguy cơ **mất lợi thế sau INT8 trên CPU thật**. Giá trị của nó là **phơi bày khoảng cách giữa "SOTA trên FLOPs" và "SOTA trên thiết bị"**.
- `fastvit_sa12` nằm giữa — structural reparameterization là lợi thế **thật** khi export.

### 2.2. Student thay thế / bổ sung

| Student | Params | top-1 | Latency công bố (thiết bị)⁴ | INT8-friendly | Đề xuất |
|---|---|---|---|---|---|
| **RepViT-M1.0 / M1.1** (CVPR 2024) | ~6,8 / ~8,2 | ~80 / 80,7% | ~1,0 ms (iPhone 12, CoreML) | ✅ **CNN thuần** — rất tốt | ⭐ **Ứng viên thay thế mạnh nhất** — student CNN thứ 2, quantize dễ |
| **SHViT** (CVPR 2024) | nhỏ | — | nhanh (iPhone 12/CPU) | TB (single-head attn) | 🔵 Tùy chọn |
| **StarNet-S** (CVPR 2024) | nhỏ | 77,4% (S3) | ~0,98 ms (iPhone 12) | ✅ Element-wise mul | 🔵 Tùy chọn nhẹ |
| **EdgeNeXt-S** | ~5,6 | ~79% | — | TB | 🔵 (được dùng trong solution ISIC 2024) |

⁴ **Số latency KHÔNG so trực tiếp được** — đo trên iPhone/CoreML, không phải Pixel 6a/ExecuTorch/XNNPACK.

> **Khuyến nghị student:** giữ nguyên bộ ba (đủ đa dạng CNN / hybrid / mobile-ViT — đúng thiết kế để trả lời "kiến trúc nào sống sót sau INT8"). Cân nhắc **thêm RepViT-M1.0** làm student CNN-thuần thứ hai nếu muốn củng cố kết luận mobile bằng một điểm dữ liệu quantize-friendly nữa. Nếu buộc phải chọn **một** student "chạy tốt trên mobile" để làm sản phẩm cuối → **`mobilenetv4_conv_medium`**.

---

## 3. KD có áp dụng tốt cho bài toán này không?

Đây là câu hỏi khoa học trung tâm của luận văn. Câu trả lời ngắn: **có, nhưng chỉ với đúng loại KD** — và điều đó tự nó là một đóng góp.

### 3.1. Capacity gap — rủi ro làm KD kém hiệu quả

Gap teacher→student ~5–12× nằm trong vùng cảnh báo của **Cho & Hariharan (2019)** và **TAKD (Mirzadeh 2020)**: teacher quá mạnh có thể làm student **học kém hơn**. Hệ quả thiết kế:
- Ưu tiên teacher gap thấp (`efficientnetv2_m` ~5×) làm teacher chính.
- Ablation teacher mạnh↔yếu chính là **bằng chứng trực tiếp về capacity-gap problem** trên domain y tế — đáng đưa vào luận văn.

### 3.2. ⛔ Nhiều SOTA KD **suy biến** vì head nhị phân single-logit

Đây là điểm phải nêu rõ khi biện luận "KD nào áp dụng được":

| Phương pháp KD | Áp dụng cho single-logit nhị phân? | Lý do |
|---|---|---|
| Vanilla KL / **BCE-KD (đang dùng)** | ✅ Có | Hợp lệ; T² đúng cả cho sigmoid/BCE |
| **DKD** | ❌ Không | NCKD ≡ 0 khi chỉ 1 lớp non-target → suy biến về TCKD |
| **Logit standardization** | ❌ Không | Z-score trên 1 logit không xác định (K=1); hằng số khi K=2 |
| **OFA-KD** | ❌ Không | Chiếu qua logit-space đa lớp vô nghĩa khi K≤2 |
| **DIST** (inter-class) | ❌ Không | Cần quan hệ liên-lớp |
| **DIST** (intra-batch) | ✅ Có | Pearson trên chiều batch, không phải chiều lớp |
| **Feature-based** (FitNet, SimKD, RKD, CRD, SP) | ✅ **Có — hướng đúng** | Hoạt động trên backbone features, độc lập K |

**Kết luận §3:** KD **áp dụng tốt** cho bài toán này, nhưng không gian cải tiến nằm ở **feature-based / relational KD**, KHÔNG ở logit-based KD hiện đại. Đây là luận điểm Chương 2 nên nêu: *"các SOTA logit KD suy biến ở K≤2, do đó nghiên cứu chọn hướng feature-based để thu hẹp capacity gap."*

---

## 4. Student cuối có chạy tốt trên mobile không?

### 4.1. Ràng buộc phần cứng — phải phát biểu đúng

- Pixel 6a = **Tensor G1**, không phải Snapdragon → **QNN NPU không dùng được** trong ExecuTorch.
- Đường thực tế: **XNNPACK (CPU big-core)**. EdgeTPU của Tensor không có ExecuTorch backend; Vulkan (Mali-G78) còn non.
- → Trong luận văn phải ghi: *"latency đo trên CPU qua XNNPACK delegate; NPU không khả dụng cho Tensor G1."* Không phải điểm yếu — chỉ cần nói đúng.

### 4.2. Vì sao student CNN thắng trên đường CPU

XNNPACK INT8 phủ tốt conv/linear nhưng **softmax/LayerNorm/attention thường không quantize & không delegate** → graph phân mảnh → fallback FP32 → overhead quantize/dequantize ở mỗi ranh giới. Hệ quả **INT8 có thể không nhanh hơn FP32** với student nhiều attention.

| Student | Dự đoán trên XNNPACK INT8 | Vai trò trong kết luận mobile |
|---|---|---|
| `mobilenetv4_conv_medium` | ✅ Speedup 2–3× | **Sản phẩm cuối chạy tốt nhất** |
| `fastvit_sa12` | ⚠️ Speedup giảm | Trung gian |
| `efficientformerv2_s2` | ⚠️⚠️ Có thể INT8 ≈ FP32 | Minh chứng "SOTA-FLOPs ≠ SOTA-thiết bị" |

### 4.3. 🎯 Đây là đóng góp, không phải rủi ro

Nếu `efficientformerv2_s2` thắng FP32 nhưng thua `mobilenetv4_conv_medium` ở INT8 on-device → đó là **finding**: ranking lật khi xuống thiết bị thật. Rất ít paper đo điều này. Đề xuất báo cáo **cả ba mức** (L1 FP32 `.pth` → L2 FP32 `.pte` → L3 INT8 `.pte`) kèm `conversion_drop`, `quantization_drop`, và latency/RAM/FPS đo thực trên Pixel 6a.

---

## 5. Đề xuất tổng hợp (ranked)

**Về teacher:**
1. Giữ **`efficientnetv2_m`** làm teacher chính.
2. **Bỏ `maxvit_base`**; thay bằng **`convnextv2_tiny`** hoặc **`efficientnetv2_s`** (gap ~2–3×).
3. (Nếu còn thời gian) thử **PanDerm** — teacher da liễu, đóng góp mới nổi bật. Ưu tiên hơn DINOv3 cho task này.
4. (Tùy chọn, chỉ nếu làm ablation foundation-model) **DINOv3** (ViT-S+/ConvNeXt-B) làm teacher generic-SSL để so với PanDerm — **bắt buộc feature-based KD**, xem §1.3.

**Về student (mục tiêu mobile):**
4. Giữ bộ ba hiện tại (đa dạng CNN/hybrid/mobile-ViT — đúng để trả lời câu hỏi INT8).
5. Sản phẩm cuối "chạy tốt trên mobile" → chốt **`mobilenetv4_conv_medium`**.
6. (Tùy chọn) thêm **RepViT-M1.0** làm điểm dữ liệu CNN quantize-friendly thứ hai.

**Về KD (mục tiêu chứng minh KD phù hợp):**
7. Giữ BCE-KD hiện tại làm baseline hợp lệ.
8. **Thêm một feature-based KD branch** (SimKD hoặc RKD) — hướng cải tiến *hợp lệ toán học* duy nhất cho binary, và thu hẹp capacity gap.
9. **KHÔNG** dùng DKD / logit standardization / OFA-KD (suy biến ở K≤2).

**Ngưỡng đổi quyết định:**
- Nếu feature-based KD không cho **ΔpAUC ≥ ~+0,01 nhất quán ≥4/5 fold** → kết luận KD lợi ích giới hạn cho binary image-only, tập trung vào deployment/calibration.
- Nếu INT8 khiến student transformer mất **>2% (quantization_drop)** → ưu tiên student CNN cho sản phẩm cuối.

---

## 6. Caveats

- **Không có bộ latency đồng nhất trên Pixel 6a/ExecuTorch** cho 6 model. Số iPhone/CoreML & Pixel EdgeTPU **không so trực tiếp được**. Cột INT8/mobile trong các bảng là **dự đoán định tính** — **bắt buộc tự đo** để có số hợp lệ.
- **Params/FLOPs/top-1** tổng hợp từ paper gốc + `timm`; có biến thể weight (`in1k` vs `distilled`) chênh ~0,5–1% → verify lại theo phiên bản `timm` đang dùng.
- Degeneracy của DKD/logit-standardization/OFA-KD ở K≤2: **chắc chắn** (chứng minh đại số). Lợi ích cụ thể của feature-based KD cho binary + prevalence 0,39%: **chưa được chứng minh mạnh** trong y văn — kỳ vọng khiêm tốn.
- Trần image-only ~0,142–0,16 pAUC là **giới hạn dữ liệu** (crop TBP, signal phần lớn ở metadata), không phải giới hạn model → không kỳ vọng student image-only vượt trần này.

---

> **Bảo trì:** khi chốt quyết định ở §5, cập nhật registry (`src/models/registry.py`), config (`configs/teacher/`, `configs/student/`) và `ARCHITECTURE.md` §3–§4 tương ứng.
