> ⛔ **SUPERSEDED — 2026-08-26. KHÔNG trích số từ file này.**
>
> Bản thay thế duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](../../reports/BAO_CAO_TONG_HOP.md).
>
> Lý do: cùng phạm vi "chỉ 1 teacher" (22/08); §0 của chính file này ghi "chưa trả lời được Q2" — nay đã trả lời.

---

# So sánh model — model nào tốt hơn (Phase 1)

Tất cả số là **mean ± std qua 5 fold** trên **tập test độc lập** (patient-disjoint), trích từ
`experiments/runs/<run>/aggregated.json`. Cập nhật **2026-08-22**.

Cách đọc: xếp hạng theo **AUPRC** (headline ở prevalence 0,39%) và **pAUC@80** (metric ISIC 2024).

---

## 0. ⚠️ Phạm vi — đọc trước

Chỉ tính các run huấn luyện **từ 15/7/2026**. Đã **LOẠI**:

- **KD `convnextv2_base→*` và `maxvit_base→*`** — bản tháng 6, distill từ teacher *cũ*. Các run-dir
  này hiện đang bị train lại và **trộn fold cũ với fold mới** (ví dụ
  `kd_convnextv2_base_to_fastvit_sa12`: fold_0 mtime 2026-08-13 nhưng fold_1..4 vẫn 2026-06-29/30)
  → `aggregated.json` của chúng **không đáng tin**, không được trích.
- **Tier baseline cũ** (`efficientnet_b4`, `efficientnet_b0`, `mobilenetv3_large`, `mobilevit_s`) —
  4 kiến trúc đã bị xoá khỏi `src/models/registry.py`, không còn thuộc đề tài.

**Hệ quả:** teacher duy nhất có ma trận KD hợp lệ là **`efficientnetv2_m`** → xem §2.2.

---

## 1. Bảng xếp hạng (sắp theo AUPRC giảm dần)

| # | Model | Vai trò | n | AUPRC | pAUC@80 | AUC | Sens | Sens@95Spec |
|---|---|---|---|---|---|---|---|---|
| — | **maxvit_base** | *teacher* | 5 | **0.6566 ± 0.0211** | 0.1830 ± 0.0025 | 0.9824 ± 0.0024 | 0.924 | 0.917 |
| — | **convnextv2_base** | *teacher* | 5 | 0.6506 ± 0.0306 | 0.1822 ± 0.0021 | 0.9816 ± 0.0021 | 0.920 | 0.915 |
| — | efficientnetv2_m | *teacher* | 5 | 0.6298 ± 0.0488 | 0.1826 ± 0.0025 | 0.9820 ± 0.0025 | 0.927 | 0.912 |
| — | efficientformerv2_s2 | *baseline* | 5 | 0.6283 ± 0.0147 | 0.1812 ± 0.0016 | 0.9804 ± 0.0016 | 0.918 | 0.918 |
| 1 | efficientformerv2_s2 ← efficientnetv2_m | KD | 5 | **0.6220 ± 0.0531** | 0.1849 ± 0.0017 | 0.9841 ± 0.0017 | 0.929 | 0.931 |
| 2 | fastvit_sa12 ← efficientnetv2_m | KD | 5 | 0.6209 ± 0.0225 | 0.1853 ± 0.0023 | 0.9846 ± 0.0023 | 0.929 | **0.934** |
| — | mobilenetv4_conv_medium | *baseline* | 5 | 0.6101 ± 0.0476 | 0.1798 ± 0.0052 | 0.9790 ± 0.0053 | 0.920 | 0.916 |
| — | fastvit_sa12 | *baseline* | 5 | 0.6082 ± 0.0417 | 0.1825 ± 0.0032 | 0.9817 ± 0.0033 | 0.923 | 0.923 |
| 3 | mobilenetv4_conv_medium ← efficientnetv2_m | KD | 5 | 0.6056 ± 0.0341 | **0.1859 ± 0.0016** | **0.9852 ± 0.0017** | **0.933** | 0.930 |
| 4 | repvit_m1_0 ← efficientnetv2_m | KD | 5 | 0.5537 ± 0.0292 | 0.1832 ± 0.0008 | 0.9823 ± 0.0009 | 0.924 | 0.923 |
| — | repvit_m1_0 | *baseline* | 5 | 0.5365 ± 0.0362 | 0.1718 ± 0.0024 | 0.9709 ± 0.0025 | 0.912 | 0.890 |

*(Sens / Sens@95Spec làm tròn 3 chữ số; std đầy đủ trong `aggregated.json`. Chỉ student KD được đánh số hạng.)*

**Đọc bảng:** theo **AUPRC**, teacher (nặng) đứng đầu và thứ hạng giữa student KD/baseline lẫn lộn.
Nhưng theo **pAUC@80 / AUC / Sensitivity**, **4 student KD chiếm trọn nhóm đầu** (pAUC 0,1832–0,1859)
so với baseline (0,1718–0,1825) và **cao hơn cả 3 teacher** (0,1822–0,1830) — đó là nơi KD thể hiện (§3).

---

## 2. Kết luận rút ra

### 2.1 Model student tốt nhất
**`mobilenetv4_conv_medium ← efficientnetv2_m` (KD).** Dẫn đầu **pAUC@80 (0.1859)** + **AUC (0.9852)**
+ **Sensitivity (0.933)** trong toàn bộ student, đồng thời là model **nhanh nhất/nhẹ nhất** đã đo
(22,6 ms · 32,1 MB `.pte` — §2.4).
- **AUPRC cao nhất trong nhóm KD student:** `efficientformerv2_s2 ← efficientnetv2_m` (0.6220).
- Lưu ý trung thực: **AUPRC của KD không phải lúc nào cũng > baseline** (efv2: base 0.6283 > KD 0.6220;
  mnv4: base 0.6101 > KD 0.6056) — nhưng đều **trong nhiễu** (< 1 std). KD thắng chắc ở pAUC/Sens (§3).

### 2.2 Teacher — chỉ so được STANDALONE
- Standalone: **`maxvit_base` (0.6566) ≈ `convnextv2_base` (0.6506)**, hơn `efficientnetv2_m` (0.6298)
  nhưng **trong 1 std** → không tuyên bố "teacher mạnh nhất" tuyệt đối.
- ⚠️ **Không kết luận được "teacher nào tạo student tốt nhất"** — chỉ `efficientnetv2_m` có ma trận KD
  hợp lệ. Muốn khép phải train lại KD của convnextv2/maxvit (§4).

### 2.3 Student vs teacher
Teacher (AUPRC 0.63–0.66) **cao hơn** student (0.55–0.62) ở AUPRC. Nhưng student KD **đạt/vượt teacher
ở pAUC@80 và Sensitivity** dù nhẹ hơn nhiều lần — đúng mục tiêu KD (nén về mobile mà giữ vùng độ nhạy cao).

> ⚠️ Luận điểm cũ **"student vượt teacher"** đã bị rút: nó so với teacher `efficientnet_b4`
> (AUPRC 0.5998) — model đã bị loại khỏi đề tài.

### 2.4 Ứng viên cho mobile (đo on-device Pixel 6a, `.pte` FP32, 4 threads)

| Model (bản deploy) | AUPRC | pAUC | Sens | Latency@t4 | Size .pte | n |
|---|---|---|---|---|---|---|
| **mobilenetv4 ← efficientnetv2_m (KD)** | 0.6056 | **0.1859** | **0.933** | **22,6 ms** | **32,1 MB** | 5 |
| efficientformerv2_s2 ← efficientnetv2_m (KD) | **0.6220** | 0.1849 | 0.929 | 42,8 ms | 47,0 MB | 5 |
| fastvit_sa12 ← efficientnetv2_m (KD) | 0.6209 | 0.1853 | 0.929 | 65,5 ms | 40,3 MB | 5 |
| repvit_m1_0 ← efficientnetv2_m (KD) | 0.5537 | 0.1832 | 0.924 | *chưa đo* | *chưa đo* | 5 |

Latency là **weight-independent** (`docs/MOBILE.md §0`) nên số đo 2026-07-04 vẫn hợp lệ cho các kiến
trúc này; cột độ chính xác đã thay bằng bản July-15+.

**Khuyến nghị Phase 1:** **`mobilenetv4 ← efficientnetv2_m`** — thắng ở cả hai trục: nhanh/nhẹ nhất
*và* dẫn đầu pAUC/AUC/Sens. Nếu bắt buộc tối đa AUPRC → `efficientformerv2_s2` (0.6220) nhưng chậm
gần 2× và `.pte` lớn hơn 15 MB.

**FastViT bị lấn át:** AUPRC ≈ EfficientFormerV2 (0.6209 vs 0.6220) nhưng chậm hơn **1,5×** (65,5 vs
42,8 ms) — một kết luận chỉ có được nhờ đo on-device thật.

---

## 3. Còn thiếu
- **KD `convnextv2_base`/`maxvit_base` × 4 student** (đợt mới) → khép §2.2.
- **Benchmark `repvit_m1_0`** + params/FLOPs cho 3 teacher.
- **Export `.pte`** cho checkpoint July-15+ (`exports/` đang rỗng) + parity check.

*Chi tiết benchmark: [../benchmark/README.md](../benchmark/README.md). Hiệu quả KD:
[03_kd_effectiveness.md](03_kd_effectiveness.md).*
