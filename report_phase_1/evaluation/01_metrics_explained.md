# Giải thích các độ đo (vì sao dùng & mức quan trọng)

Bài toán: phân loại nhị phân tổn thương da (benign=0, malignant=1), **prevalence rất
thấp ~0.4%**. Chính vì lớp dương hiếm nên việc chọn metric phải cẩn thận — nhiều metric
quen thuộc (accuracy, AUC-ROC) trở nên gây hiểu nhầm ở prevalence này.

Ký hiệu mức quan trọng: 🔴 Cốt lõi · 🟡 Hỗ trợ · ⚪ Bổ sung.

---

## A. Độ chính xác (chất lượng model — không phụ thuộc thiết bị)

### 🔴 pAUC@TPR≥80% — *metric chính*
- **Là gì:** Partial AUC, chỉ tính phần đường ROC có **TPR ≥ 0.80**, chuẩn hoá về ~[0.02, 0.20]
  (random ≈ 0.02, hoàn hảo = 0.20).
- **Vì sao dùng:** đây là **metric chính thức của thử thách ISIC 2024**. Nó chỉ thưởng cho
  model hoạt động tốt ở **vùng độ nhạy cao** — đúng với yêu cầu sàng lọc ung thư (phải bắt
  được hầu hết ca ác tính). Một model có AUC tổng thể cao nhưng yếu ở vùng TPR cao sẽ bị phạt.
- **Quan trọng:** dùng làm **thước đo xếp hạng chính** giữa các model.

### 🔴 AUPRC (Area Under Precision-Recall Curve) — *headline ở prevalence thấp*
- **Là gì:** diện tích dưới đường Precision–Recall. Baseline ngẫu nhiên = prevalence (~0.004).
- **Vì sao dùng:** ở 0.4% dương, **AUC-ROC lạc quan quá mức** (dễ đạt >0.98 dù model tầm thường
  vì lớp âm áp đảo). AUPRC nhạy với khả năng thực sự **tìm đúng lớp hiếm** → phản ánh trung thực hơn.
- **Quan trọng:** là **con số headline** nên trích dẫn trong proposal, KHÔNG dùng AUC-ROC một mình.

### 🟡 AUC-ROC
- **Là gì:** diện tích dưới đường ROC.
- **Vì sao dùng:** chuẩn so sánh phổ biến, dễ đối chiếu với văn liệu. **Nhưng lạc quan ở lớp
  hiếm** → chỉ dùng kèm, không đứng một mình.

### 🔴 Sensitivity (Recall / TPR) = TP/(TP+FN)
- **Vì sao dùng:** tỉ lệ **bắt đúng ca ác tính**. Trong y tế, bỏ sót (FN) nguy hiểm hơn báo
  động giả → đây là **chỉ số an toàn quan trọng nhất**.

### 🔴 Specificity = TN/(TN+FP)
- **Vì sao dùng:** tỉ lệ loại đúng ca lành; liên quan trực tiếp tới **số báo động giả** người
  dùng phải chịu. Đi cặp với Sensitivity để mô tả điểm vận hành.

### 🟡 Sens@95%Spec (và Sens@90%Spec)
- **Là gì:** độ nhạy đạt được khi **cố định** độ đặc hiệu ở 95% (hoặc 90%).
- **Vì sao dùng:** cho biết model bắt được bao nhiêu ca ác tính **ở một mức báo động giả cố
  định** — dễ diễn giải cho bối cảnh triển khai thực (thay vì để Youden tự chọn ngưỡng).

### ⚪ F1 / Precision / Accuracy
- Ở prevalence 0.4%, **precision luôn rất thấp** (nhiều FP so với ít TP thật) và **accuracy vô
  nghĩa** (dự đoán "toàn lành" đã đạt ~99.6%). Chỉ để tham khảo, KHÔNG dùng đánh giá chính.

### 🔴 Decision threshold (Youden's J)
- **Là gì:** ngưỡng cắt xác suất, chọn để tối đa **J = Sens + Spec − 1**. **KHÔNG phải 0.5.**
- **Vì sao dùng:** model xuất 1 logit thô; ngưỡng quyết định benign/malignant phải tối ưu trên
  dữ liệu, và **khác nhau theo model** → phải lưu và triển khai đúng ngưỡng này.
- ⚠️ Ngưỡng còn **khác nhau giữa các fold của cùng một model** → khi deploy phải lấy lại ngưỡng
  từ `val_predictions.csv` của đúng fold được ship, không hardcode một con số.

### 🟡 Brier score & ECE — *hiệu chuẩn (calibration), khác với xếp hạng*
- **Là gì:** `brier` = sai số bình phương trung bình giữa xác suất dự đoán và nhãn; `ECE` =
  expected calibration error (15 bin). Cả hai nằm sẵn trong `test_metrics.json`.
- **Vì sao cần:** sampler undersampling dạy model theo prior ~16,7% ác tính, trong khi prevalence
  thật là **0,39%** → `sigmoid(logit)` **lệch cao có hệ thống**. Con số "% nguy cơ" hiển thị cho
  người dùng vì thế không trung thực nếu không hiệu chỉnh.
- **Quan trọng:** đây là chỉ số **chẩn đoán**, không phải chỉ số xếp hạng. Hiệu chỉnh offline bằng
  `scripts/compute_calibration.py --run-dir <run>` (prior-shift / Platt / isotonic, fit trên
  `val_predictions.csv`) **không đổi bất kỳ số nào** ở pAUC/AUPRC/AUC — các metric xếp hạng bất
  biến với mọi biến đổi đơn điệu. Nó chỉ làm xác suất hiển thị trở nên đúng.

---

## B. Hiệu năng tĩnh (kiến trúc — so chéo thiết bị được)

| Độ đo | Vì sao dùng | Mức |
|---|---|---|
| **Params (M)** | Độ nặng model, chuẩn học thuật. **Không dự đoán được tốc độ** | 🔴 |
| **FLOPs / MACs (G)** | Chi phí tính toán độc lập phần cứng. **Không tỉ lệ latency thật** trên ARM → luôn kèm latency đo | 🔴 |
| **Kích thước `.pte`/model (MB)** | Quyết định APK size + RAM nạp — rất thực tế cho mobile | 🔴 |

---

## C. Độ trễ & bộ nhớ (device-specific — chỉ so trong cùng thiết bị + cùng cấu hình)

| Độ đo | Vì sao dùng | Mức |
|---|---|---|
| **Median / p50 (ms)** | Độ trễ điển hình, bền outlier → **headline latency** | 🔴 |
| **Mean ± Std (ms)** | Std = độ ổn định; thấp = UX mượt, đoán trước được | 🔴 |
| **p90 / p95 / p99 (ms)** | Tail latency — trường hợp xấu; cam kết "99% dưới X ms" | 🔴 |
| **Min / Max (ms)** | Min = trần phần cứng; Max = lần tệ (dễ nhiễu) | 🟡 |
| **Cold-start (ms)** | Độ trễ lần đầu — ấn tượng đầu của người dùng | 🟡 |
| **Load time (ms)** | Thời gian nạp model (1 lần) — ảnh hưởng khởi động app | 🟡 |
| **FPS** | 1000/latency; chỉ quan trọng nếu xử lý **camera real-time** | ⚪ |
| **Peak RAM (MB)** | RAM đỉnh; cao → Android kill app | 🔴 (chưa đo) |
| **Throughput sweep (img/s)** | Kịch bản **server batch**, KHÔNG áp dụng app batch=1 | ⚪ |

---

## D. Cấu hình đo — bắt buộc khai báo

**Warmup iters** (làm nóng cache/JIT/XNNPACK), **Measured iters** (cỡ mẫu), **Threads**
(latency phụ thuộc mạnh — báo cáo rõ cấu hình quote), **Batch size** (=1 cho mobile),
**Thiết bị/SoC/ABI/SDK** (latency chỉ có nghĩa khi gắn phần cứng cụ thể).

### 3 nguyên tắc vàng
1. **Params/FLOPs/size** so chéo thiết bị được; **latency chỉ so trong cùng máy + cùng threads**.
2. Latency báo cáo **median + tail (p95/p99)**, không chỉ mean.
3. Luôn khai báo **warmup + iters + threads + thiết bị**; nếu thiếu, phép đo mất giá trị.
