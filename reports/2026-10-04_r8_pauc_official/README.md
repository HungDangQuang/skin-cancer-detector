# R8 — `pauc_at_tpr` của dự án so với hàm chấm chính thức ISIC 2024

Việc R8 trong `docs/PROGRESS.md` (review 03/10 §1.8). Câu hỏi: số pAUC@TPR80 của dự án có cùng **định nghĩa metric**
với số của cuộc thi (Kurtansky 2025) không.

**Hàm chính thức:** `PrimaryMetric-pAUC.py` trong repo [ISIC-Research/Challenge-2024-Metrics](https://github.com/ISIC-Research/Challenge-2024-Metrics)
(Nicholas R Kurtansky, MSKCC), tải 04/10/2026 qua `raw.githubusercontent.com/.../main/PrimaryMetric-pAUC.py`. Chép
nguyên văn vào `check_pauc.py`, chỉ đổi tên module.

**Khác nhau về cách viết, không khác về toán:** hàm chính thức đảo nhãn (`1 − y`), đảo điểm (`1 − p`), lấy
`roc_curve`, nội suy tại `max_fpr = 0,2` rồi tính `auc`. Hàm của dự án (`src/evaluation/metrics.py:11-45`) đảo nhãn,
đảo điểm (`−p`, cùng thứ tự với `1 − p`), gọi `roc_auc_score(max_fpr=0,2)` của sklearn (cũng nội suy y như vậy rồi
nhân hệ số McClish), rồi đảo ngược hệ số McClish.

**Kiểm bằng số** (server, 04/10/2026, `src/evaluation/metrics.py` md5 trùng bản Mac): P0, checkpoint `_auprc`, 5 fold
test in-domain (toàn bộ, ISIC, PAD) + HAM headline và Fitzpatrick headline fold 4 — 19 dòng trong `output.csv`, tức 17 tập khác nhau (với HAM và Fitz, dòng "all" trùng dòng theo nguồn), từ 397 đến 59.093 ảnh.
**Chênh tuyệt đối lớn nhất: 2,8e-17** (sai số dấu phẩy động). Chi tiết: `output.csv`.

**Kết luận:** cùng metric. B1 so được với Kurtansky **về định nghĩa**; vẫn **không** cùng dữ liệu (tập test của cuộc thi
khác phần ISIC của splits v2 — `acceptance-gates.md` §2 B1), nên so sánh B1 chỉ là tham chiếu.

**Một khác biệt hành vi (không ảnh hưởng số đã báo cáo):** khi chỉ có một lớp, hàm chính thức `raise ValueError`, hàm
của dự án trả `0,0`. `bootstrap_ci.py` đã xử lý mẫu một lớp thành `NaN` (`CLAUDE.md`, mục bootstrap); mọi tập con ở
trên đều có đủ hai lớp.
