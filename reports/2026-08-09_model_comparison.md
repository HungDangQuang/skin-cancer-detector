# So sánh thực nghiệm — model tốt nhất (cập nhật 2026-08-10, **chỉ dữ liệu train từ 15/7**)

Bản soạn lại của `report_phase_1/evaluation/02_model_comparison.md` + `03_kd_effectiveness.md`, **chỉ giữ
các run train từ 15/7/2026 trở đi** (đợt huấn luyện hợp lệ) và **chỉ bộ SOTA**.

> ⚠️ **Phạm vi (quan trọng):** đã **LOẠI** các run KD `convnextv2_base→*` và `maxvit_base→*` vì chúng là bản
> **tháng 6 (trước 15/7)**. Hệ quả: **teacher duy nhất có ma trận KD hợp lệ là `efficientnetv2_m`.** File
> `reports/comparison/kd_comparison.md` (dump thô) vẫn còn dòng tháng 6 → không dùng; báo cáo này mới đúng phạm vi.

- **Nguồn số:** `experiments/runs/<run>/aggregated.json` (mean ± std qua 5 fold). Không lấy từ trí nhớ.
- **Quy ước:** headline **AUPRC** (prevalence ~0.39%, AUC-ROC lạc quan quá mức); **pAUC@80** = metric chuẩn
  ISIC 2024. Cột **n** = số fold. Tất cả run in-scope đều **5/5**.
- **Bộ in-scope:** teacher `{efficientnetv2_m, convnextv2_base, maxvit_base}` (standalone) + student SOTA
  `{mobilenetv4, fastvit_sa12, efficientformerv2_s2, repvit_m1_0}` với KD chỉ từ `efficientnetv2_m`.

---

## 1. Bảng xếp hạng (sắp theo AUPRC giảm dần)

| # | Model | Vai trò | n | AUPRC | pAUC@80 | AUC | Sens | Sens@95Spec |
|---|---|---|---|---|---|---|---|---|
| — | **maxvit_base** | *teacher* | 5 | **0.6566 ± 0.0211** | 0.1830 ± 0.0025 | 0.9824 ± 0.0024 | 0.925 | 0.917 |
| — | **convnextv2_base** | *teacher* | 5 | 0.6506 ± 0.0306 | 0.1822 ± 0.0021 | 0.9816 ± 0.0021 | 0.920 | 0.915 |
| — | efficientnetv2_m | *teacher* | 5 | 0.6298 ± 0.0488 | 0.1826 ± 0.0025 | 0.9820 ± 0.0025 | 0.927 | 0.912 |
| — | efficientformerv2_s2 | *baseline* | 5 | 0.6283 ± 0.0147 | 0.1812 ± 0.0016 | 0.9804 ± 0.0016 | 0.918 | 0.918 |
| 1 | efficientformerv2_s2 ← efficientnetv2_m | KD | 5 | **0.6220 ± 0.0531** | 0.1849 ± 0.0017 | 0.9841 ± 0.0017 | 0.929 | 0.931 |
| 2 | fastvit_sa12 ← efficientnetv2_m | KD | 5 | 0.6209 ± 0.0225 | 0.1853 ± 0.0023 | 0.9846 ± 0.0023 | 0.929 | 0.934 |
| — | mobilenetv4_conv_medium | *baseline* | 5 | 0.6101 ± 0.0476 | 0.1798 ± 0.0052 | 0.9790 ± 0.0053 | 0.920 | 0.916 |
| — | fastvit_sa12 | *baseline* | 5 | 0.6082 ± 0.0417 | 0.1825 ± 0.0032 | 0.9817 ± 0.0033 | 0.923 | 0.923 |
| 3 | mobilenetv4_conv_medium ← efficientnetv2_m | KD | 5 | 0.6056 ± 0.0341 | **0.1859 ± 0.0016** | **0.9852 ± 0.0017** | **0.933** | 0.930 |
| 4 | repvit_m1_0 ← efficientnetv2_m | KD | 5 | 0.5537 ± 0.0292 | 0.1832 ± 0.0008 | 0.9823 ± 0.0009 | 0.924 | 0.923 |
| — | repvit_m1_0 | *baseline* | 5 | 0.5365 ± 0.0362 | 0.1718 ± 0.0024 | 0.9709 ± 0.0025 | 0.912 | 0.890 |

*(Sens / Sens@95Spec làm tròn 3 chữ số; std đầy đủ trong `aggregated.json`. Chỉ student KD được đánh số hạng.)*

**Đọc bảng:** theo **AUPRC**, teacher (nặng) đứng đầu, còn giữa các student thì thứ hạng AUPRC lẫn lộn giữa KD
và baseline. Nhưng theo **pAUC@80 / AUC / Sensitivity**, **4 student KD chiếm trọn nhóm đầu** (pAUC ~0.185–0.186)
so với baseline (~0.180–0.183) — đó là nơi KD thể hiện (xem §3).

---

## 2. Kết luận — model nào tốt nhất

### 2.1 Model student tốt nhất (đủ 5 fold, in-scope)
**`mobilenetv4_conv_medium ← efficientnetv2_m` (KD).** Dẫn đầu **pAUC@80 (0.1859)** + **AUC (0.9852)** +
**Sensitivity (0.933)** trong toàn bộ student, và là model **nhẹ/nhanh nhất** (~22 ms, ~32 MB `.pte` theo
benchmark trước) → ứng viên triển khai on-device tốt nhất.
- **AUPRC cao nhất trong nhóm KD student:** `efficientformerv2_s2 ← efficientnetv2_m` (0.6220).
- Lưu ý: giữa các student, **AUPRC của KD không phải lúc nào cũng > baseline** (efv2: base 0.6283 > KD 0.6220;
  mnv4: base 0.6101 > KD 0.6056) — nhưng đều **trong nhiễu** (< 1 std). KD thắng chắc ở pAUC/Sens (§3).

### 2.2 Teacher — chỉ so được STANDALONE
- Standalone: **`maxvit_base` (0.6566) ≈ `convnextv2_base` (0.6506)** là hai teacher mạnh nhất, hơn
  `efficientnetv2_m` (0.6298) nhưng **trong 1 std**.
- ⚠️ **Không kết luận được "teacher nào tạo student tốt nhất"** — chỉ `efficientnetv2_m` có ma trận KD hợp lệ
  trong phạm vi July-15+. Muốn khép, phải train lại KD của convnextv2/maxvit (xem §4).

### 2.3 Student vs teacher
Teacher (AUPRC 0.63–0.66) cao hơn student (0.55–0.62) về AUPRC, nhưng student KD **đạt/vượt teacher ở pAUC@80
và Sensitivity** dù nhẹ hơn nhiều lần — đúng mục tiêu KD (nén về mobile mà giữ vùng độ nhạy cao).

---

## 3. Hiệu quả Knowledge Distillation (KD − Baseline) — teacher `efficientnetv2_m`

Δ = `kd_efficientnetv2_m_to_<student>` − `baseline_<student>` (cùng kiến trúc/data/seed, 5 fold). Dương = KD giúp.
Baseline dùng để trừ: efficientformerv2_s2 0.6283 / fastvit 0.6082 / mobilenetv4 0.6101 / repvit 0.5365.

| Student | n(KD) | Δ pAUC@80 | Δ AUPRC | Δ Sens | Δ Sens@95Spec |
|---|---|---|---|---|---|
| repvit_m1_0 | 5 | +0.0115 | **+0.0172** | +0.0124 | +0.0323 |
| fastvit_sa12 | 5 | +0.0028 | +0.0127 | +0.0066 | +0.0108 |
| mobilenetv4_conv_medium | 5 | +0.0061 | −0.0045 | +0.0124 | +0.0141 |
| efficientformerv2_s2 | 5 | +0.0037 | −0.0062 | +0.0108 | +0.0133 |

### 3.1 KD cải thiện NHẤT QUÁN pAUC@80 và Sensitivity
Trên **cả 4/4 student**, **Δ pAUC@80 luôn dương** (+0.003 → +0.012), **Δ Sensitivity luôn dương**, và
**Δ Sens@95Spec luôn dương** (+0.011 → +0.032). KD kéo model về **vùng độ nhạy cao** — đúng thứ cần cho sàng
lọc ung thư. **Đây là bằng chứng chắc chắn nhất cho luận điểm KD.**

### 3.2 AUPRC — hỗn hợp, trong nhiễu
- repvit +0.0172 và fastvit +0.0127 dương; mnv4 −0.0045, efv2 −0.0062 âm nhẹ — **đều < 1 std → trong nhiễu**.
- Với teacher `efficientnetv2_m`, **KD không nâng AUPRC một cách đáng tin**; giá trị KD nằm ở pAUC + Sensitivity.
- ⚠️ Luận điểm "hiệu quả AUPRC phụ thuộc chất lượng teacher" (bản trước) **đã rút** — nó dựa trên KD convnextv2
  tháng 6 (ngoài phạm vi). Muốn khẳng định lại → cần train KD convnextv2/maxvit trong đợt mới.

### 3.3 Thông điệp một câu (cho slide)
> "Với teacher EfficientNetV2-M, Knowledge Distillation cải thiện **nhất quán** pAUC@TPR≥80% và độ nhạy (kể cả
> Sens@95Spec) trên **cả 4** kiến trúc student; thay đổi AUPRC ở mức nhiễu."

---

## 4. Công việc còn lại (chạy trên server)

1. **Khép Q2 — train KD `convnextv2_base` (và tùy chọn `maxvit_base`) × 4 student** trong đợt mới, đồng bộ với
   teacher hiện tại, để so "teacher nào tạo student tốt nhất":
   ```bash
   for S in mobilenetv4_conv_medium fastvit_sa12 efficientformerv2_s2 repvit_m1_0; do
     bash run/train_student.sh STUDENT=$S TEACHER=convnextv2_base TRAINING=distillation
   done
   ```
2. **Post-hoc cho model chốt** (`mobilenetv4 ← efficientnetv2_m`): calibration + benchmark latency/size + Pareto.
3. Sau mỗi đợt: `python3 scripts/aggregate_folds.py --run-dir <run>` → `compare_kd_results.py` → cập nhật báo
   cáo này + `2026-08-10_research_questions.md`.

---

## 5. Cảnh báo độ tin
- **Phạm vi:** chỉ July-15+. KD convnextv2/maxvit (tháng 6) đã loại → Q2 chưa khép, KD chỉ kiểm chứng 1 teacher.
- **Δ AUPRC std lớn** (0.03–0.05). Δ nhỏ hơn ~1 std nên mô tả là "trong nhiễu"; ở phạm vi này **không có Δ AUPRC
  nào vượt ngưỡng khẳng định mạnh** — dùng pAUC/Sens làm bằng chứng KD.
- Teacher standalone hơn kém nhau **trong 1 std** → không tuyên bố teacher "tốt nhất" tuyệt đối từ standalone.

---

## 6. ⏳ Bức tranh TẠM THỜI cho Q2 (dữ liệu tháng 6 — PLACEHOLDER, chờ train lại)

> ⚠️ **KHÔNG phải kết quả chính thức.** Điền tạm bằng KD `convnextv2_base`/`maxvit_base` **bản tháng 6** (distill
> từ teacher **cũ**; config train giống hệt bản July nhưng teacher đã train lại 19–21/7). Chỉ để hình dung Q2 trong
> lúc `run/train_kd_parallel.sh` chạy lại trên server. **Số sẽ thay** khi có bản July-15+.

Mỗi ô = **AUPRC / pAUC@80** (n fold):

| Student (KD) | efficientnetv2_m (Jul ✅) | convnextv2_base (Jun ⏳) | maxvit_base (Jun ⏳) |
|---|---|---|---|
| mobilenetv4_conv_medium | 0.6056 / 0.1859 (n5) | **0.6614 / 0.1898** (n5) | 0.6510 / 0.1905 (n1) |
| fastvit_sa12 | 0.6209 / 0.1853 (n5) | **0.6756 / 0.1908** (n5) | 0.6124 / 0.1888 (n1) |
| efficientformerv2_s2 | 0.6220 / 0.1849 (n5) | **0.6839 / 0.1897** (n4) | — (0 fold) |
| repvit_m1_0 | 0.5537 / 0.1832 (n5) | — | — |

**Xu hướng tạm:** `convnextv2_base` tạo student tốt hơn `efficientnetv2_m` ở mọi student có dữ liệu (AUPRC
+0.05…+0.06, pAUC +0.003…+0.005) → nếu giữ xu hướng, **convnextv2_base sẽ là teacher-KD tốt nhất**. maxvit n=1 chưa đọc được.

**Models PLACEHOLDER cần update sau khi server train xong** (thay số tháng 6 → July-15+):
- `kd_convnextv2_base_to_{mobilenetv4_conv_medium (n5), fastvit_sa12 (n5), efficientformerv2_s2 (n4)}`
- `kd_maxvit_base_to_{mobilenetv4_conv_medium (n1), fastvit_sa12 (n1)}`
- **Chưa có dữ liệu nào** (train mới hoàn toàn): `kd_convnextv2_base_to_repvit_m1_0`, `kd_maxvit_base_to_{efficientformerv2_s2, repvit_m1_0}`

Khi có bản mới: `run/train_kd_parallel.sh` → `aggregate_folds.py` → `compare_kd_results.py` → thay §6 này bằng bảng chính thức và cập nhật §2.2 (Q2).
