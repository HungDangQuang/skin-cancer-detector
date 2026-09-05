> ⛔ **SUPERSEDED — 2026-08-26. KHÔNG trích số từ file này.**
>
> Bản thay thế duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](BAO_CAO_TONG_HOP.md).
>
> Lý do: viết khi `kd_convnextv2_base_to_efficientformerv2_s2` mới 4/5 fold và CHƯA có bootstrap CI in-domain. Cả hai điều kiện nay đã đổi.

---

# Thống kê toàn bộ kết quả training (cập nhật 2026-08-24)

Tổng hợp **toàn bộ** run in-domain hiện có trên máy Mac, sau khi đã đồng bộ nốt các fold còn thiếu từ
`vast`/`vastnew`. Mỗi số trong file này trích thẳng từ artifact (`test_metrics.json` / `aggregated.json`),
không lấy từ trí nhớ hay từ report cũ.

**Nguồn số:**
- `experiments/runs/<run>/fold_*/test_metrics.json` — số **test** (không thiên lệch), không phải `val_metrics.json`.
- Bảng roll-up: `reports/comparison/kd_comparison_sota.{md,json}` (sinh bởi `scripts/compare_kd_results.py`,
  lọc `--students mobilenetv4_conv_medium,fastvit_sa12,efficientformerv2_s2,repvit_m1_0`).
- Bản đầy đủ (kèm cả họ model đã retire): `reports/comparison/kd_comparison.{md,json}`.

**Quy ước:** headline là **AUPRC** (prevalence đo được **0.39%** → AUC-ROC lạc quan quá mức);
**pAUC@TPR80** là metric chuẩn ISIC 2024. Luôn trích **mean ± std qua 5 fold**.
Δ nhỏ hơn ~1 std của baseline = "trong nhiễu", không tính là thắng.

---

## 0. 🔴 Hai điểm dữ liệu phải biết trước khi đọc

**(a) Câu hỏi Q2 "teacher nào tốt nhất cho KD" — GIỜ ĐÃ TRẢ LỜI ĐƯỢC.**
Report `2026-08-10_research_questions.md` loại KD `convnextv2_base→*` và `maxvit_base→*` vì đó là bản
tháng 6. Các run đó **đã được train lại toàn bộ từ 12/8 đến 23/8** và nay đầy đủ. Ma trận KD hợp lệ hiện là
**3 teacher × 4 student**, không còn chỉ 1 teacher. Xem §4.

**(b) Đã sửa một lỗi trộn thí nghiệm.**
`kd_convnextv2_base_to_efficientformerv2_s2/fold_3` trên Mac là bản **30/6** còn sót lại giữa các fold mới.
Bằng chứng cứng: fold đó có **62.072 dòng test**, trong khi *mọi* fold khác của toàn bộ ma trận SOTA có
**62.040 dòng** → khác thế hệ data-prep, không được gộp. Nó cũng là fold "đẹp" nhất (AUPRC 0.6886) nên đã
đẩy cặp này lên hạng 1 một cách giả tạo. Đã pull bản train lại từ `vast` (AUPRC 0.6792, 62.040 dòng);
bản cũ lưu ở `experiments/_replaced/20260824_081414/` (không xoá).
Ngoài fold này, **không còn fold nào lệch thế hệ** trong toàn bộ ma trận SOTA (đã quét lại toàn bộ).

Ngoài ra: **mọi `aggregated.json` của các run convnextv2/maxvit đều đang là bản 10/8** — cũ hơn chính các
fold của nó (12/8–23/8). Đã regenerate lại toàn bộ. Report nào trích `aggregated.md` trước hôm nay đều sai số.

---

## 1. Tình trạng dữ liệu — cái gì đã có, cái gì còn thiếu

### 1.1 Ma trận chính (in-scope, SOTA)

| Nhóm | Run | Fold | Ghi chú |
|---|---|---|---|
| Teacher | `teacher/efficientnetv2_m` | **5/5** ✅ | |
| Teacher | `teacher/convnextv2_base` | **5/5** ✅ | |
| Teacher | `teacher/maxvit_base` | **5/5** ✅ | |
| Baseline (no KD) | `baseline_mobilenetv4_conv_medium` | **5/5** ✅ | |
| Baseline | `baseline_fastvit_sa12` | **5/5** ✅ | |
| Baseline | `baseline_efficientformerv2_s2` | **5/5** ✅ | |
| Baseline | `baseline_repvit_m1_0` | **5/5** ✅ | |
| KD | `efficientnetv2_m` → 4 student | **5/5 × 4** ✅ | |
| KD | `convnextv2_base` → mobilenetv4 / fastvit / repvit | **5/5 × 3** ✅ | repvit vừa pull fold 3,4 hôm nay |
| KD | `convnextv2_base` → efficientformerv2_s2 | **4/5** ⚠️ | **fold_4 đang train** |
| KD | `maxvit_base` → 4 student | **5/5 × 4** ✅ | |
| PAD ablation | `runs_isic_only/teacher/*` (3 teacher) | **5/5 × 3** ✅ | chỉ có nhánh teacher |

→ **19/20 run-dir đủ 5 fold. Tổng 99/100 fold.**

### 1.2 ⚠️ Còn thiếu (remark)

1. **`kd_convnextv2_base_to_efficientformerv2_s2` fold_4 — đang train.** Cả `vast` và `vastnew` đều đang
   chạy 1 fold cho run này. Đây là **run duy nhất chưa đủ 5 fold**. Mọi số của nó trong report này là
   **mean qua 4 fold**, không so sánh trực tiếp được với 11 cặp còn lại (5 fold) — xem cảnh báo ở §3.
2. **Bootstrap CI in-domain — CHƯA CHẠY.** `scripts/bootstrap_ci.py` cần `numpy`+`sklearn` nên **không chạy
   được trên Mac** (đúng theo CLAUDE.md: Mac chỉ để sửa code). Đây là thứ **quan trọng nhất còn thiếu**:
   nhiều Δ ở §3 nhỏ hơn std giữa các fold, chỉ có **paired CI** mới kết luận được. Chạy trên server:
   `bash run/bootstrap_ci.sh RESULTS_DIR=experiments/runs`.
   *(CI cho HAM10000 và Fitzpatrick17k thì đã có sẵn: `reports/external/*/headline/bootstrap_ci.md`.)*
3. **External eval của `kd_convnextv2_base_to_efficientformerv2_s2` mới có 3/5 fold**
   (`reports/external/ham10000/headline/.../` đánh dấu `3 ⚠`) — chạy lại `run/evaluate_external.sh` cho
   run này sau khi fold_4 xong.
4. **Teacher `panderm` — chưa train fold nào.** Loader đã code xong (`src/models/panderm.py`) nhưng chưa có
   run-dir nào. Nhánh foundation-model vẫn đang là kế hoạch.
5. **Chưa có ablation nào được train.** Không tồn tại run-dir `__suffix` nào: không có `__mselogit`
   (MSE-logit KD), `__rkd` (RKD feature-KD), `__samp_off`, `__ratio3`, `__focal_a075`. Code đã có, run thì chưa.
6. **PAD ablation chỉ có nhánh teacher**, chưa có nhánh student baseline (`runs_isic_only/baseline_*`).
7. **Benchmark thiếu `repvit_m1_0`** — `reports/benchmark/` chỉ có 3/4 student SOTA.
   `reports/mobile_benchmark/` toàn model thuộc họ đã retire (efficientnet_b0/b4, mobilenetv3, mobilevit).
8. **`exports/` không tồn tại trên Mac** — chưa có `.pte` nào ở local (bản export + parity nằm trên server).

### 1.3 Đã loại khỏi mọi bảng (historical)

Họ baseline cũ — `teacher/efficientnet_b4`, `baseline_{efficientnet_b0, mobilenetv3_large, mobilevit_s}`,
`kd_efficientnet_b4_to_*` (đều 4/7/2026) — đã bị **xoá khỏi model registry ngày 15/7**, không rebuild được.
Chúng vẫn nằm trong `reports/comparison/kd_comparison.md` (dump thô, 15 cặp) — **đừng dùng file đó**;
bản đúng phạm vi là `kd_comparison_sota.md` (12 cặp).

---

## 2. Bảng chính — AUPRC (headline)

Hàng = student, cột = teacher. Cột cuối = baseline không KD.

| Student | ← efficientnetv2_m | ← convnextv2_base | ← maxvit_base | Baseline (no KD) |
|---|---|---|---|---|
| `mobilenetv4_conv_medium` | 0.6056 ± 0.0341 | **0.6351 ± 0.0189** | 0.6254 ± 0.0127 | 0.6101 ± 0.0476 |
| `fastvit_sa12` | 0.6209 ± 0.0225 | 0.6427 ± 0.0304 | **0.6510 ± 0.0129** | 0.6082 ± 0.0417 |
| `efficientformerv2_s2` | 0.6220 ± 0.0531 | **0.6521 ± 0.0255** ⚠️4f | 0.6435 ± 0.0330 | 0.6283 ± 0.0147 |
| `repvit_m1_0` | 0.5537 ± 0.0292 | 0.5814 ± 0.0385 | **0.6073 ± 0.0267** | 0.5365 ± 0.0362 |

### pAUC@TPR80 (metric chuẩn ISIC 2024)

| Student | ← efficientnetv2_m | ← convnextv2_base | ← maxvit_base | Baseline (no KD) |
|---|---|---|---|---|
| `mobilenetv4_conv_medium` | **0.1859 ± 0.0016** | 0.1835 ± 0.0028 | 0.1837 ± 0.0028 | 0.1798 ± 0.0052 |
| `fastvit_sa12` | **0.1853 ± 0.0023** | 0.1842 ± 0.0028 | 0.1851 ± 0.0010 | 0.1825 ± 0.0032 |
| `efficientformerv2_s2` | **0.1849 ± 0.0017** | 0.1838 ± 0.0029 ⚠️4f | 0.1843 ± 0.0007 | 0.1812 ± 0.0016 |
| `repvit_m1_0` | **0.1832 ± 0.0008** | 0.1806 ± 0.0032 | 0.1832 ± 0.0013 | 0.1718 ± 0.0024 |

### Teacher (standalone, để đối chiếu)

| Teacher | AUPRC | pAUC@TPR80 | AUC-ROC | Sensitivity |
|---|---|---|---|---|
| `maxvit_base` | **0.6566 ± 0.0211** | 0.1830 ± 0.0025 | 0.9824 ± 0.0024 | 0.9245 ± 0.0074 |
| `convnextv2_base` | 0.6506 ± 0.0306 | 0.1822 ± 0.0021 | 0.9816 ± 0.0021 | 0.9203 ± 0.0119 |
| `efficientnetv2_m` | 0.6298 ± 0.0488 | 0.1826 ± 0.0025 | 0.9820 ± 0.0025 | 0.9270 ± 0.0196 |

---

## 3. KD có giúp không? → ✅ **CÓ**, nhưng mức độ phụ thuộc metric

| Metric | Số cặp KD thắng | Δ trung bình |
|---|---|---|
| **AUPRC** (headline) | **10/12** | **+0.0243** |
| **pAUC@TPR80** (ISIC) | **12/12** | +0.0052 |
| AUC-ROC | 12/12 | +0.0053 |
| Sensitivity | 12/12 | +0.0100 |
| Sens@90%Spec | 12/12 | +0.0091 |
| Sens@95%Spec | 12/12 | +0.0126 |

**Điểm đáng chú ý — 2 cặp KD làm AUPRC *tệ đi*, cả hai đều là teacher `efficientnetv2_m`:**
- `efficientnetv2_m → efficientformerv2_s2`: ΔAUPRC **−0.0062**
- `efficientnetv2_m → mobilenetv4_conv_medium`: ΔAUPRC **−0.0045**

Cả hai Δ này đều nhỏ hơn nhiều so với std của baseline (0.0147 và 0.0476) → **trong nhiễu**, không phải
"KD làm hại", mà là "KD không giúp gì cho AUPRC ở hai cặp này". Đáng chú ý là cùng lúc đó pAUC và cả
4 chỉ số về sensitivity vẫn tăng → KD cải thiện **ranking ở vùng TPR cao** (vùng lâm sàng quan tâm) kể cả
khi AUPRC toàn cục không đổi.

### Top 5 cặp có Δ KD lớn nhất (Ranking B)

| # | Cặp | ΔAUPRC | ΔpAUC | ΔSens@95Spec |
|---|---|---|---|---|
| 1 | `maxvit_base → repvit_m1_0` | **+0.0708** | +0.0114 | +0.0232 |
| 2 | `convnextv2_base → repvit_m1_0` | +0.0449 | +0.0088 | +0.0191 |
| 3 | `maxvit_base → fastvit_sa12` | +0.0428 | +0.0026 | +0.0066 |
| 4 | `convnextv2_base → fastvit_sa12` | +0.0345 | +0.0017 | +0.0050 |
| 5 | `convnextv2_base → mobilenetv4_conv_medium` | +0.0250 | +0.0037 | +0.0025 |

**Quy luật rõ ràng: student càng yếu, KD càng có lãi.** `repvit_m1_0` là student yếu nhất
(baseline AUPRC 0.5365 — kém cặp thứ hai 0.07) và chiếm cả 2 hạng đầu về Δ. Với `repvit`, KD nâng pAUC
từ 0.1718 lên 0.1806–0.1832, tức **vượt xa 1 std** (0.0024) — đây là hiệu ứng KD chắc chắn nhất trong cả bảng.

### ⚠️ Cặp tốt nhất về hiệu năng tuyệt đối (Ranking A) — đọc kỹ

| # | Cặp | AUPRC | pAUC | Fold |
|---|---|---|---|---|
| 1 | `convnextv2_base → efficientformerv2_s2` | 0.6521 ± 0.0255 | 0.1838 ± 0.0029 | **4** ⚠️ |
| 2 | `maxvit_base → fastvit_sa12` | 0.6510 ± 0.0129 | 0.1851 ± 0.0010 | 5 |
| 3 | `maxvit_base → efficientformerv2_s2` | 0.6435 ± 0.0330 | 0.1843 ± 0.0007 | 5 |

Hạng 1 và hạng 2 **cách nhau 0.0011 AUPRC**, trong khi std của chúng là 0.0255 và 0.0129 → **hoàn toàn
trong nhiễu, không phân định được**. Hơn nữa hạng 1 mới có 4 fold nên chưa so sánh công bằng.

→ **Cặp nên chọn để triển khai lúc này: `maxvit_base → fastvit_sa12`** — AUPRC 0.6510 ± **0.0129**
(std nhỏ nhất trong top 3, tức ổn định nhất giữa các fold), pAUC 0.1851 ± 0.0010, AUC 0.9845,
Sens 0.9336, và có đủ 5 fold. Chốt cuối cùng nên đợi fold_4 + paired bootstrap CI.

> **Lưu ý so với kết luận cũ:** report 10/8 chọn `mobilenetv4 ← efficientnetv2_m` là "best deployable"
> vì nó có **pAUC cao nhất (0.1859)** — điều này *vẫn đúng*. Nhưng xếp theo **AUPRC (headline ở prevalence
> 0.39%)** thì cặp đó chỉ đứng hạng 10/12 (0.6056) và ΔAUPRC âm. Hai metric cho hai đáp án khác nhau;
> AUPRC mới là headline theo quy ước của dự án.

---

## 4. Q2 — Teacher nào là teacher KD tốt nhất? → **maxvit_base**, nhưng có điều kiện

| Teacher | AUPRC của chính nó | AUPRC student TB | **ΔAUPRC TB** | Thắng | ΔpAUC TB | pAUC student TB |
|---|---|---|---|---|---|---|
| `maxvit_base` | 0.6566 | **0.6318** | **+0.0360** | **4/4** | +0.0053 | 0.1841 |
| `convnextv2_base` | 0.6506 | 0.6278 | +0.0320 | **4/4** | +0.0042 | 0.1830 |
| `efficientnetv2_m` | 0.6298 | 0.6005 | +0.0048 | 2/4 | **+0.0060** | **0.1848** |

**Trên AUPRC — kết luận rõ:** `maxvit_base` và `convnextv2_base` là teacher tốt hơn hẳn `efficientnetv2_m`
(+0.036 / +0.032 và thắng 4/4, so với +0.005 và chỉ thắng 2/4). Khoảng cách này **lớn hơn std giữa các fold**
của phần lớn student → đây là tín hiệu thật, không phải nhiễu.

**Và thứ tự này khớp đúng với chất lượng standalone của teacher:**
maxvit (0.6566) > convnextv2 (0.6506) > efficientnetv2_m (0.6298) — **cùng thứ tự với ΔAUPRC**.
Tức là ở dự án này, *teacher mạnh hơn thì distil ra student tốt hơn* — không gặp nghịch lý
"teacher quá mạnh dạy kém" mà tài liệu KD hay nhắc.

**Nhưng trên pAUC thì đảo chiều:** `efficientnetv2_m` cho pAUC cao nhất cho **cả 4/4 student**.
Chênh lệch chỉ 0.0007–0.0018, cùng cỡ với std (0.0008–0.0031) → **trong nhiễu**, nhưng hướng nhất quán
4/4 nên không nên bỏ qua. Cần paired bootstrap CI (§1.2 mục 2) để chốt.

> Đối chiếu cross-domain: theo `reports/2026-08-23_external_evaluation.md`, `efficientnetv2_m` là teacher
> **tốt nhất trên HAM10000** nhưng **tệ nhất trên Fitzpatrick17k**. Cộng với kết quả in-domain ở đây,
> câu "teacher nào tốt nhất" **không có đáp án độc lập với domain và metric** — phải nói rõ đo trên đâu.

---

## 5. Student có vượt teacher không?

| Teacher | AUPRC teacher | Student vượt được |
|---|---|---|
| `convnextv2_base` | 0.6506 | `efficientformerv2_s2` (0.6521) — nhưng chỉ 4 fold và chênh 0.0015 → **trong nhiễu** |
| `maxvit_base` | 0.6566 | không |
| `efficientnetv2_m` | 0.6298 | không |

Nhưng trên **pAUC@TPR80 thì student thắng gần như tuyệt đối**: teacher tốt nhất đạt 0.1830, trong khi
**11/12 cặp KD đều ≥ 0.1832**. Nghĩa là ở vùng vận hành lâm sàng (TPR ≥ 80%), student nhẹ đã bắt kịp và
vượt teacher — đây là luận điểm mạnh nhất cho hướng đề tài (nén model cho on-device mà không mất hiệu năng).

---

## 6. Kiểm tra overfitting (val − test)

Gap AUPRC trung bình qua các fold, cho cả 19 run:

- Teacher: +0.020 … +0.036
- Baseline student: +0.017 … +0.033
- KD student: +0.012 … +0.042

Gap **pAUC** thì gần như bằng 0 với mọi run (−0.0013 … +0.0017).

→ **Không có dấu hiệu overfitting bất thường.** Gap AUPRC dương nhẹ và đồng đều là bình thường (val được
early-stopping tối ưu vào). Không run nào lệch hẳn khỏi nhóm — không cần can thiệp `drop_path_rate` hay
augmentation `heavy`.

---

## 7. Chi phí triển khai (để cân nhắc cùng độ chính xác)

| Student | Params | FP32 size | GFLOPs | CPU lat. | AUPRC tốt nhất |
|---|---|---|---|---|---|
| `mobilenetv4_conv_medium` | 8.44 M | 32.4 MB | 1.653 | 27.4 ms | 0.6351 |
| `fastvit_sa12` | 10.56 M | 40.4 MB | 2.962 | 41.2 ms | **0.6510** |
| `efficientformerv2_s2` | 12.13 M | 46.7 MB | 2.493 | 42.4 ms | 0.6521 ⚠️4f |
| `repvit_m1_0` | — | — | — | — | 0.6073 |

Nguồn: `reports/benchmark/*.json` (đo trên server Linux + L40, batch 1, 1 thread CPU).
⚠️ **Latency CPU server chỉ là proxy, KHÔNG phải số trên điện thoại** — thứ hạng có thể đảo với student
kiểu transformer. Chỉ params/FLOPs/size là chuyển được sang thiết bị khác.
`repvit_m1_0` **chưa được benchmark** (xem §1.2 mục 7).

`mobilenetv4` rẻ hơn `fastvit` **33% về latency, 20% về size, 44% về FLOPs**, đổi lại kém **0.0159 AUPRC**
(0.6351 vs 0.6510 — cỡ 1.2 std của fastvit, tức có thể là chênh lệch thật, chờ CI để chốt).
Nếu ràng buộc tài nguyên là chính, `convnextv2_base → mobilenetv4_conv_medium` là lựa chọn hợp lý hơn.

---

## 8. Tóm tắt

**Đã chốt được:**
1. **KD có tác dụng** — thắng 12/12 trên pAUC, sensitivity và cả 2 điểm vận hành cố định; 10/12 trên AUPRC.
2. **Q2 đã trả lời được** (lần đầu): `maxvit_base` là teacher KD tốt nhất trên AUPRC (+0.036, 4/4),
   `efficientnetv2_m` yếu nhất (+0.005, 2/4). Thứ tự khớp với chất lượng standalone của teacher.
3. **Student vượt teacher trên pAUC** — 11/12 cặp KD ≥ teacher tốt nhất.
4. **Không có overfitting.**
5. Cặp triển khai đề xuất: **`maxvit_base → fastvit_sa12`** (chính xác) hoặc
   **`convnextv2_base → mobilenetv4_conv_medium`** (cân bằng chi phí).

**Chưa chốt được / còn thiếu:**
1. `kd_convnextv2_base_to_efficientformerv2_s2` fold_4 — **đang train**, run duy nhất chưa đủ.
2. **Paired bootstrap CI in-domain chưa chạy** — nhiều Δ ở §3–§4 nằm trong nhiễu, chưa có CI thì chưa
   phát biểu được "khác biệt có ý nghĩa". Đây là việc ưu tiên cao nhất, phải chạy trên server.
3. Hạng 1 vs hạng 2 của Ranking A không phân định được (chênh 0.0011, std 0.013–0.026).
4. Trên pAUC, `efficientnetv2_m` thắng 4/4 nhưng trong nhiễu — mâu thuẫn với kết luận theo AUPRC, chờ CI.
5. Chưa train: teacher `panderm`, toàn bộ ablation KD-variant, nhánh student của PAD ablation.
6. Chưa benchmark `repvit_m1_0`; external eval của 1 run mới có 3/5 fold.

### Việc nên làm tiếp, theo thứ tự

```bash
# 1. (server) CI in-domain — thứ quan trọng nhất còn thiếu
bash run/bootstrap_ci.sh RESULTS_DIR=experiments/runs

# 2. (Mac) khi fold_4 xong thì kéo về + tổng hợp lại
bash run/pull_results.sh pull
python3 scripts/aggregate_folds.py --run-dir experiments/runs/kd_convnextv2_base_to_efficientformerv2_s2
python3 scripts/compare_kd_results.py --students mobilenetv4_conv_medium,fastvit_sa12,efficientformerv2_s2,repvit_m1_0 \
    --out-md reports/comparison/kd_comparison_sota.md --out-json reports/comparison/kd_comparison_sota.json

# 3. (server) benchmark student còn thiếu (benchmark.sh cần CẢ MODEL lẫn CKPT)
bash run/benchmark.sh MODEL=repvit_m1_0 \
    CKPT=experiments/runs/kd_maxvit_base_to_repvit_m1_0/fold_0/checkpoints/best_model.pth

# 4. (server) external eval lại cho run đã đủ fold
bash run/evaluate_external.sh   # sau khi fold_4 xong
```

---
---

# PHẦN II — SCOPE CỦA LUẬN VĂN

Phần này thống kê lại **phạm vi thực tế** của luận văn, đối chiếu giữa cái đề cương
([report_phase_1/DE_CUONG.md](../report_phase_1/DE_CUONG.md)) cam kết và cái đã thực sự tồn tại trên đĩa.
Mọi trạng thái dưới đây được kiểm bằng cách đếm artifact, không lấy từ bảng tiến độ trong đề cương
(bảng đó đang lạc hậu ở 3 dòng — xem §S.5).

## S.1 Câu hỏi nghiên cứu

**Câu hỏi trung tâm** ([DE_CUONG.md:27](../report_phase_1/DE_CUONG.md#L27)):

> *"Liệu KD có thực sự mang lại cải thiện đáng kể và nhất quán cho các mô hình lightweight thuộc nhiều
> paradigm thiết kế khác nhau, và chất lượng của teacher ảnh hưởng thế nào đến hiệu quả KD?"*

Tách thành 3 câu hỏi kiểm chứng được:

| | Câu hỏi | Trạng thái |
|---|---|---|
| **Q1** | Trộn PAD-UFES-20 vào train có làm teacher tốt hơn không? | ✅ đã trả lời — có, cả 3 teacher |
| **Q2** | Teacher mạnh hơn có tạo ra student tốt hơn không? | ✅ **đã trả lời (24/8)** — có, trên AUPRC |
| **Q3** | KD có cải thiện student nhất quán qua các paradigm không? | ✅ đã trả lời — có, 12/12 pAUC, 10/12 AUPRC |

Đóng góp khoa học được tuyên bố là **ΔpAUC và ΔAUPRC trên ma trận đa kiến trúc** — tức bản thân
*hiệu số*, không phải điểm số tuyệt đối. Đây là điểm cần nhớ khi so với văn liệu (xem QA-A1).

## S.2 Phạm vi bài toán

| Chiều | Phạm vi |
|---|---|
| Bài toán | Phân loại **nhị phân** benign(0)/malignant(1), ảnh 224×224 → **một logit duy nhất** |
| Ánh xạ nhãn | melanoma, BCC, SCC → 1; nevus, keratosis, lành tính khác → 0 |
| Dữ liệu train | ISIC 2024 SLICE-3D + PAD-UFES-20 (prevalence ~0,1% → **0,388%**) |
| Test in-domain | **62.040 ảnh, 241 ca ác tính**, patient-disjoint, tách TRƯỚC khi chia fold |
| CV | `StratifiedGroupKFold` K=5, group = `patient_id` |
| Metric headline | **AUPRC**; thứ hai **pAUC@TPR≥80%** (chuẩn ISIC 2024); AUC-ROC chỉ tham khảo |
| Ngưỡng quyết định | Youden's J, **khác nhau giữa các fold** |

## S.3 Ma trận thực nghiệm — 110 lượt huấn luyện, đã xong 109

| Nhóm | Công thức | Số fold-run | Đã xong |
|---|---|---|---|
| Teacher (with-PAD) | 3 × 5 fold | 15 | **15** ✅ |
| Teacher ISIC-only (ablation PAD) | 3 × 5 fold | 15 | **15** ✅ |
| Student baseline (không KD) | 4 × 5 fold | 20 | **20** ✅ |
| **Ma trận KD** | 3 teacher × 4 student × 5 fold | 60 | **59** 🔄 |
| **TỔNG** | | **110** | **109 (99,1%)** |

**3 teacher:** EfficientNetV2-M (CNN fused-MBConv) · ConvNeXtV2-Base (modern ConvNet) · MaxViT-Base (CNN–Transformer hybrid)
**4 student** (cố ý trải 4 paradigm khác nhau — đây là điểm mới so với văn liệu vốn chỉ dùng 1 cặp):
MobileNetV4-Conv-Medium (depthwise-separable CNN, 8,44M) · FastViT-SA12 (CNN + reparameterization, 10,56M) ·
EfficientFormerV2-S2 (attention–CNN hybrid, 12,13M) · RepViT-M1.0 (CNN mang thiết kế ViT, *chưa benchmark*)

> ⚠️ **Con số "30 run" trong các tài liệu cũ đã sai.** "30" = 3 student × 2 điều kiện × 5 fold cho **một**
> teacher. Scope thực tế là **4 student × 3 teacher** → 110 fold-run.

## S.4 Ba tầng đánh giá

| Tầng | Bộ dữ liệu | Vai trò | Trạng thái |
|---|---|---|---|
| **(i) In-domain** | ISIC 2024 + PAD test split (62.040 ảnh, prev 0,388%) | Kết quả chính | ✅ 109/110 fold |
| **(ii) Cross-domain** | HAM10000 (ảnh dermoscopic, prev 15,7%) | Tổng quát hoá | ✅ **xong**, 3 biến thể |
| **(iii) Fairness** | Fitzpatrick17k (sắc tố da I–VI) | Công bằng | ✅ **xong**, 2 biến thể, coverage 99,98% |

Cả hai bộ ngoài **không bao giờ dùng để train**, ngưỡng quyết định bị **đóng băng** từ
`val_predictions.csv` nội bộ của chính run đó, và bước chuẩn bị kết thúc bằng kiểm tra rò rỉ (exit 2 nếu trùng).

## S.5 ⚠️ Bảng tiến độ trong đề cương đang sai 3 dòng

Đối chiếu [DE_CUONG.md:206–219](../report_phase_1/DE_CUONG.md#L206) với thực tế trên đĩa:

| GĐ | Đề cương ghi | **Thực tế (24/8)** |
|---|---|---|
| 3 | ✅ xong (15/15) | ⚠️ **một nửa** — PAD ablation xong 15/15, nhưng **ablation bộ lấy mẫu chưa chạy fold nào** |
| 5 | 🔄 20/60 | ✅ **59/60** — chỉ còn 1 fold |
| 6 | 🔄 đã đo 3 kiến trúc | 🔄 đúng, nhưng thiếu repvit + 3 teacher; `.pte` + parity đã PASS trên server, **chưa đo Pixel 6a** |
| 7 | ⏳ chưa chạy eval | ✅ **ĐÃ XONG CẢ HAI BỘ** |
| 8 | ⏳ | ⏳ **Paired t-test không tồn tại trong code**; bootstrap CI có nhưng mới chạy cho external; calibration chạy **6 run external, 0 run in-domain** |

→ Luận văn đang **đi trước** kế hoạch ở GĐ5 và GĐ7, **chậm hơn** ở GĐ3 (ablation sampler) và GĐ8.

## S.6 Nằm NGOÀI scope thực nghiệm (đã code, cố ý không chạy)

Đây là các nhánh đã có mã nguồn chạy được nhưng **mặc định tắt** và **chưa có fold-run nào**. Đề cương
gọi chúng là "hướng mở rộng để ngỏ" — cần nói rõ trong luận văn để không bị hiểu là đã thử mà thất bại:

| Hạng mục | Mã nguồn | Vì sao ngoài scope |
|---|---|---|
| Teacher nền tảng **PanDerm** | `src/models/panderm.py` | Trọng số ngoài `timm`, giấy phép CC-BY-NC-4.0 |
| **Teacher đặc quyền (LUPI)** | `PrivilegedTimmBackboneModel` | Trục nghiên cứu riêng; student vẫn image-only |
| **MSE-logit KD** (Kim 2021) | `distillation.py`, `soft_loss_type=mse` | Biến thể; mặc định `bce` |
| **RKD feature-KD** (Park 2019) | `feature_distillation.py` | Biến thể; cần bật `training=distillation_rkd` |
| **Ablation bộ lấy mẫu** | `run/ablation_sampler.sh` | Đề cương hứa ở GĐ3, **chưa chạy** |
| **Cổng OOD Mahalanobis** | chưa code, chỉ có design doc | Phạm vi = an toàn ứng dụng, không thuộc Chương 4 |
| **Lượng tử hoá INT8** | — | **Đã de-scope** từ 2026-07 |

Mọi nhánh trên đều **mặc định tắt** → kết quả chính không bị ảnh hưởng dù một byte.

---

# PHẦN III — Q&A

## Nhóm A — Làm rõ scope

### QA-S1. Chính xác thì luận văn này chứng minh điều gì?

Ba mệnh đề, tất cả đều đã có bằng chứng định lượng:

1. **Trộn PAD-UFES-20 làm teacher tốt hơn** — đo trên subset ảnh PAD trong test set (miền mà nhánh
   ISIC-only chưa từng thấy), đúng cho cả 3 teacher. Nguồn: `reports/pad_ablation_*.md`.
2. **KD cải thiện student nhất quán qua 4 paradigm** — 12/12 trên pAUC, sensitivity và cả hai điểm vận
   hành cố định; 10/12 trên AUPRC.
3. **Teacher mạnh hơn tạo student tốt hơn** — thứ tự ΔAUPRC (maxvit +0,0360 > convnextv2 +0,0320 >
   efficientnetv2_m +0,0048) **trùng khớp** thứ tự AUPRC standalone của teacher (0,6566 > 0,6506 > 0,6298).

Điều luận văn **không** chứng minh: rằng model này dùng được trên lâm sàng. Đó là nghiên cứu hồi cứu trên
tập test giữ lại, không phải thử nghiệm tiền cứu.

### QA-S2. "Ma trận" là bao nhiêu run? Con số 30 có còn đúng không?

**Không.** 30 = 3 student × 2 điều kiện × 5 fold cho **một** teacher — con số của thiết kế cũ hồi tháng 6.
Scope hiện tại là **110 fold-run** (§S.3), đã xong 109. Bất kỳ chỗ nào trong luận văn còn ghi "30 run"
đều phải sửa.

### QA-S3. Vì sao chọn 4 student này mà không phải 4 model nhẹ bất kỳ?

Vì câu hỏi nghiên cứu là *"KD có nhất quán qua các **paradigm thiết kế** không"*, nên 4 student được chọn
để **trải 4 họ kiến trúc khác nhau**, không phải để chọn 4 model tốt nhất:

| Student | Paradigm | Vai trò trong thiết kế |
|---|---|---|
| MobileNetV4-Conv-Medium | Depthwise-separable CNN | CNN nhẹ kinh điển |
| FastViT-SA12 | CNN + reparameterization | Kỹ thuật hợp nhất nhánh khi inference |
| EfficientFormerV2-S2 | Attention–CNN hybrid | Có attention thật |
| RepViT-M1.0 | CNN mang thiết kế ViT | ViT-hoá một CNN thuần |

Nếu cả 4 paradigm đều hưởng lợi thì kết luận "KD giúp model nhẹ" mới có sức nặng — và đúng là cả 4 đều
hưởng lợi trên pAUC. Đây chính là chỗ luận văn khác văn liệu, vốn thường chỉ khảo sát **một** cặp
teacher–student ([DE_CUONG.md:25](../report_phase_1/DE_CUONG.md#L25)).

### QA-S4. Những gì đã code nhưng không chạy thì tính vào scope thế nào?

Tính là **"đã cài đặt, để ngỏ"**, không tính là kết quả và cũng không được kể như thất bại. Danh sách đầy
đủ ở §S.6. Điểm quan trọng: mọi nhánh đó **mặc định tắt**, đã kiểm tra bằng static-validate, nên các run
chính **giống hệt từng byte** so với khi các nhánh đó chưa tồn tại. Trong luận văn nên đặt chúng ở mục
"Hướng phát triển" kèm câu "mã nguồn đã sẵn sàng, chưa huấn luyện".

Riêng **ablation bộ lấy mẫu** thì khác: đề cương **đã hứa** ở GĐ3 và đánh dấu ✅, nhưng thực tế chưa chạy
fold nào. Đây là món nợ, không phải hướng mở rộng — hoặc chạy, hoặc sửa đề cương.

### QA-S5. Đề cương hứa gì mà hiện chưa có?

| Đã hứa | Trạng thái thật | Mức nghiêm trọng |
|---|---|---|
| **Paired t-test 5 fold (p<0,05)**, nhắc 6 lần | **Không tồn tại trong mã nguồn** | 🔴 Cao — xem QA-B4 |
| Ablation bộ lấy mẫu | Chưa chạy | 🟡 Trung bình |
| Benchmark on-device **Pixel 6a** | Chưa đo; mới có latency CPU server (proxy) | 🟡 Trung bình |
| Phân tích **Pareto** AUPRC vs latency | Chưa có hình nào | 🟡 Trung bình |
| Params 3 teacher + RepViT | Vẫn để "*chưa đo*" trong bảng | 🟢 Thấp |
| Hiệu chuẩn xác suất cho model chốt | Mới chạy 6 run external, **0 run in-domain** | 🟢 Thấp (không đổi metric xếp hạng) |

### QA-S6. Vì sao AUPRC là headline mà không phải accuracy?

Vì prevalence là **0,388%** (241 ca ác tính / 62.040 ảnh). Ở mức đó:

- **Accuracy vô dụng** — model đoán "tất cả lành tính" đạt 99,6% accuracy mà không bắt được ca nào.
- **AUC-ROC lạc quan** — specificity được tính trên 61.799 ảnh lành tính nên phần lớn dương tính giả bị
  pha loãng; baseline đã 0,971–0,980 nên không còn phân biệt được các model.
- **AUPRC là loại duy nhất phạt đúng dương tính giả** ở prevalence thấp. Đường cơ sở ngẫu nhiên của nó
  **chính là prevalence = 0,0039**, nên AUPRC 0,65 tương đương gấp ~167 lần đoán mò.
- **pAUC@TPR≥80%** giữ vai trò riêng: đây là metric chính thức ISIC 2024, dùng để so với bảng xếp hạng
  quốc tế. Nó chỉ tính phần đường ROC ở TPR ≥ 80% — đúng vùng vận hành sàng lọc.

Hai metric, hai vai trò: **AUPRC = kết luận lâm sàng, pAUC = so sánh benchmark.** Không mâu thuẫn.

---

## Nhóm B — Phân tích kết quả

### QA-B1. Vì sao Δ KD nhỏ hơn nhiều so với các con số ở phần "nghiên cứu liên quan"?

Đây là câu hỏi quan trọng nhất của luận văn, và câu trả lời là **đang so sai hai đại lượng**.

**(a) Các con số trong đề cương không phải là Δ KD.**
[DE_CUONG.md:72](../report_phase_1/DE_CUONG.md#L72) trích: Islam et al. 2024 đạt **98,75% accuracy**,
Saha et al. 2025 đạt **91,7% accuracy**. Đó là **độ chính xác tuyệt đối** trên bộ đa lớp tương đối cân
bằng — không phải phần KD đóng góp thêm. Bài **duy nhất** trong danh mục báo cáo một Δ KD thực sự là
Suryakanth et al. (MTAKD): **+0,75–1,1%**. Kết quả của luận văn (+22,3% giảm lỗi tương đối, ~+2–4% trên
các thang tuyệt đối) **cùng bậc độ lớn hoặc cao hơn**. Nói cách khác: kết quả *khớp* văn liệu, không hề dưới.

**(b) Metric đã gần bão hoà nên Δ tuyệt đối buộc phải nhỏ.**
Baseline đã ở AUC 0,971–0,980. Chỉ còn 2% lỗi để cải thiện. Đổi sang thang **tỉ lệ lỗi giảm được**:

| Cặp | Giảm lỗi AUC | % headroom pAUC (trần 0,20) |
|---|---|---|
| maxvit → repvit | **+39,7%** | **+40,5%** |
| efficientnetv2_m → repvit | +39,2% | +40,6% |
| efficientnetv2_m → mobilenetv4 | +29,3% | +30,4% |
| convnextv2 → fastvit (thấp nhất) | +10,7% | +9,9% |
| **Trung bình 12 cặp** | **+22,3%** | **+22,7%** |

**KD xoá được trung bình 22% lượng lỗi còn lại.** Đây mới là cách trình bày đúng; "+0,005 pAUC" là cách
tự làm hại mình.

**(c) Nhưng quy ra ca bệnh thì đúng là ít.** Trên 241 ca ác tính, KD bắt thêm trung bình **+2,4 ca**
(cao nhất +5,2 ca ở `convnextv2→repvit`) và giảm trung bình **121 dương tính giả** — nhưng riêng số dương
tính giả dao động rất mạnh giữa các cặp (−994 … +311), nên **không được dùng nó như một kết luận chung**.
Con số +2,4 ca nên nêu thẳng trong luận văn: nó trung thực, và nó nói lên rằng **ở in-domain đã bão hoà,
giá trị thật của KD nằm ở chỗ khác** (xem QA-B3).

### QA-B2. Bài toán nhị phân một logit có thực sự truyền được "dark knowledge" không?

**Gần như không** — và đây là lý do cơ chế nhất cho QA-B1.

Đề cương ([DE_CUONG.md:104](../report_phase_1/DE_CUONG.md#L104)) viết soft loss "truyền *dark knowledge*
từ phân phối mềm của teacher". Nhưng mã nguồn thực tế
([distillation.py:81](../src/training/distillation.py#L81)):

```python
soft_targets = torch.sigmoid(teacher_logits / T)   # (B,) — MỘT số vô hướng mỗi ảnh
```

Dark knowledge theo Hinton là **cấu trúc tương đồng giữa các lớp SAI** — chữ số "2" mà teacher chấm hơi
giống "7" hơn là "9". Đó là thông tin nhãn cứng không có. Với **một logit nhị phân, không tồn tại lớp sai
nào để xếp hạng**: teacher chỉ truyền được đúng một đại lượng — mức độ tự tin.

Nên KD ở đây thoái hoá thành **label smoothing thích ứng theo mẫu** + **trọng số độ khó** (ảnh nào teacher
lưỡng lự thì student học nhẹ tay). Cơ chế đó có thật và có ích, nhưng yếu hơn hẳn dark knowledge 1000 lớp
trên ImageNet. **Gain 2–4% tuyệt đối là đúng bằng những gì cơ chế này có thể cho.**

Bằng chứng khớp với giải thích này: cặp lãi nhiều nhất luôn là `repvit_m1_0` — student **yếu nhất**
(baseline AUPRC 0,5365, kém cặp thứ hai 0,07). KD giúp nhiều nhất ở chỗ student *chưa* học đủ từ nhãn
cứng — đúng vai trò của một bộ điều chuẩn, không phải "truyền tri thức mới".

**Khuyến nghị:** bỏ chữ "dark knowledge" khỏi mô tả, hoặc nói rõ nó bị thoái hoá trong setup nhị phân.
Đây là hạn chế thật và nêu thẳng thì mạnh hơn là để hội đồng phát hiện.

### QA-B3. Vậy KD thể hiện rõ nhất ở đâu?

**Ở dữ liệu lạ, không phải in-domain.** So sánh cùng 12 cặp:

| | In-domain (prev 0,388%) | HAM10000 (prev 15,7%) |
|---|---|---|
| ΔAUPRC trung bình | +0,0243 (thắng 10/12) | **+0,0297 (thắng 12/12)** |
| ΔpAUC trung bình | +0,0052 | **+0,0071** |
| AUC của baseline | 0,971–0,980 (**gần bão hoà**) | 0,76–0,82 (**còn dư địa**) |

Và ở HAM10000 **đã có paired bootstrap CI**: `efficientnetv2_m→mobilenetv4` cho
**ΔAUPRC +0,0713 [+0,0598, +0,0819]** — khoảng tin cậy không chứa 0, tức khác biệt chắc chắn thật.

→ Luận điểm mạnh nhất nên là: **"KD không chỉ cải thiện điểm số, nó cải thiện khả năng chống dịch chuyển
miền"** — đúng nhu cầu của một app chạy trên điện thoại người dùng, nơi ảnh không bao giờ giống tập train.

### QA-B4. Vì sao không có Paired t-test như đề cương hứa, và nên thay bằng gì?

Đề cương nhắc Paired t-test 6 lần nhưng **mã nguồn không có** (`compare_kd_results.py` là stdlib thuần,
chỉ tính mean ± std + Δ). Có hai lựa chọn, và lựa chọn thứ hai tốt hơn:

**Vì sao t-test trên 5 fold là công cụ yếu ở đây:**
- **n = 5** → gần như không có lực thống kê.
- **5 fold không phải 5 mẫu độc lập của phân phối test.** Chúng là **5 model khác nhau chấm trên CÙNG
  62.040 hàng test**. Độ lệch chuẩn giữa các fold đo *sự dao động giữa các model*, không đo *sai số lấy
  mẫu của tập test* — mà cái sau mới là thứ trả lời "kết quả này có lặp lại trên bệnh nhân mới không".

**Công cụ đúng — paired bootstrap trên hàng test** (`scripts/bootstrap_ci.py`, đã có sẵn): mỗi lần lặp bốc
một bộ chỉ số hàng, chấm **mọi fold** trên cùng bộ đó rồi lấy trung bình. Ghép cặp (cùng hàng cho cả nhánh
KD lẫn baseline) là mấu chốt — **CI của hai run có thể chồng nhau trong khi CI của hiệu số vẫn tách hẳn khỏi 0**.

Đây chính là lý do "bootstrap CI in-domain" là món còn thiếu quan trọng nhất (§1.2 mục 2): nhiều Δ ở
Phần I nhỏ hơn std giữa các fold, chưa có CI thì với từng cặp riêng lẻ vẫn chưa khẳng định được gì.
Trên external thì CI đã có và đã cho kết luận dứt khoát.

```bash
bash run/bootstrap_ci.sh RESULTS_DIR=experiments/runs   # chạy trên server
```

Trong luận văn: hoặc chạy bootstrap rồi sửa đề cương thành "paired bootstrap CI", hoặc chạy cả hai và
trình bày t-test như kiểm chứng phụ. **Đừng để nguyên lời hứa t-test mà không có kết quả.**

### QA-B5. Student có "vượt teacher" không?

**Phải trả lời tách theo metric, nếu không sẽ thành tuyên bố sai.**

| Metric | Kết luận |
|---|---|
| **AUPRC** | ❌ **Không.** Teacher 0,6298–0,6566; student KD tốt nhất 0,6521. Cặp duy nhất vượt (convnextv2→efficientformerv2, 0,6521 vs 0,6506) chênh 0,0015 và mới có 4 fold → **trong nhiễu** |
| **pAUC@TPR80** | ✅ **Có, gần như tuyệt đối.** Teacher cao nhất 0,1830; **11/12 cặp KD đạt ≥ 0,1832** |
| **Sensitivity** | ✅ Phần lớn student KD ≥ teacher |

→ Phát biểu an toàn: **"Ở vùng vận hành lâm sàng (TPR ≥ 80%), student gọn nhẹ đạt hiệu năng ngang hoặc
vượt teacher; xét trên toàn dải xếp hạng (AUPRC) thì teacher vẫn nhỉnh hơn."**
*(Chưa nêu được tỉ lệ nén cụ thể vì params của 3 teacher vẫn "chưa đo" — xem QA-S5.)*
Đây đúng là luận điểm cần cho hướng on-device, và nó vẫn đủ mạnh mà không cần nói quá.

### QA-B6. Nếu chỉ được chọn một model để ship thì chọn gì?

| Ưu tiên | Chọn | Lý do |
|---|---|---|
| **Chính xác tối đa** | `maxvit_base → fastvit_sa12` | AUPRC 0,6510 ± **0,0129** (std nhỏ nhất → ổn định nhất giữa các fold), pAUC 0,1851, đủ 5 fold |
| **Cân bằng chi phí** | `convnextv2_base → mobilenetv4_conv_medium` | AUPRC 0,6351, nhưng **rẻ hơn 33% latency / 20% size / 44% FLOPs** |
| ~~Theo pAUC~~ | ~~`efficientnetv2_m → mobilenetv4`~~ | pAUC cao nhất (0,1859) nhưng AUPRC hạng 10/12 — **hai metric mâu thuẫn, ưu tiên AUPRC** |

Ba lưu ý bắt buộc khi ship: (1) latency CPU server **chỉ là proxy**, chưa đo Pixel 6a; (2) ngưỡng Youden
**khác nhau giữa các fold** nên phải lấy đúng ngưỡng của fold được ship; (3) chốt cuối cùng nên đợi
paired bootstrap CI — hiện hạng 1 và hạng 2 chênh 0,0011, không phân định được.

