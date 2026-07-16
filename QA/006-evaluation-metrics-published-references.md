# QA 006 — Các metric đánh giá có được bài báo chính thống nào sử dụng không?

**Status:** verified 2026-07-01 · evaluation

## Question
Các metric đang sử dụng có bài báo nào đang sử dụng để đánh giá không? Nếu có thì tôi chỉ công nhận các bài báo đã đăng chính thống và uy tín.

## Answer
**Có — mọi metric mà project báo cáo đều là metric chuẩn, có nguồn gốc từ bài báo peer-reviewed hoặc từ metric chính thức của một challenge y khoa uy tín. Không có metric nào tự chế.** Dưới đây là ánh xạ từng metric (đúng như code tính trong [src/evaluation/metrics.py](../src/evaluation/metrics.py)) tới nguồn công bố chính thống.

**1. pAUC@TPR≥80% — metric chính (primary).**
Đây **chính là metric chính thức của ISIC 2024 Challenge** ("Skin Cancer Detection with 3D-TBP"): partial AUC của đường ROC trong vùng TPR ≥ 80%, chọn vì lâm sàng đòi hỏi model độ nhạy cao (bỏ sót ác tính là lỗi nghiêm trọng). Bộ dữ liệu và metric được mô tả trong bài **dataset descriptor đăng trên *Scientific Data* (Nature Portfolio), 2024 — "SLICE-3D dataset: 400,000 skin lesion image crops extracted from 3D TBP"** (doi: [10.1038/s41597-024-03743-w](https://www.nature.com/articles/s41597-024-03743-w)). Một bài **peer-reviewed trên *npj Digital Medicine* (2025), "Automated triage of cancer-suspicious skin lesions with 3D total-body photography"** ([s41746-025-02070-7](https://www.nature.com/articles/s41746-025-02070-7)) báo cáo trực tiếp con số này (pAUC@80%TPR = 0.1757, AUC = 0.9704) → chứng minh metric được dùng để đánh giá trong tài liệu chính thống, và cho một mốc so sánh.
Về mặt thống kê, chuẩn hóa partial-AUC mà code dùng (McClish correction, xem [metrics.py:11-46](../src/evaluation/metrics.py#L11-L46)) là của bài kinh điển **McClish, D.K. (1989), "Analyzing a Portion of the ROC Curve", *Medical Decision Making* 9(3):190-195** (PMID 2668680, doi: 10.1177/0272989X8900900307).

**2. AUC-ROC.** Metric nền tảng nhất trong y khoa chẩn đoán, giới thiệu bởi **Hanley, J.A. & McNeil, B.J. (1982), "The meaning and use of the area under a receiver operating characteristic (ROC) curve", *Radiology* 143(1):29-36.** Trong lĩnh vực da liễu AI, được dùng làm metric chính ở bài landmark **Esteva et al. (2017), "Dermatologist-level classification of skin cancer with deep neural networks", *Nature* 542:115-118** (doi: 10.1038/nature21056). *Lưu ý phương pháp:* ở prevalence ~0.4%, AUC-ROC lạc quan giả — project vẫn báo cáo nhưng không dùng làm headline.

**3. AUPRC (Average Precision).** Được khuyến nghị làm headline ở dữ liệu mất cân bằng bởi **Saito, T. & Rehmsmeier, M. (2015), "The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets", *PLOS ONE* 10(3):e0118432** (PMID 25738806) — đúng lý do code lưu `auprc` kèm `prevalence` làm baseline ([metrics.py:162-163](../src/evaluation/metrics.py#L162-L163)). Cơ sở lý thuyết PR-vs-ROC: **Davis, J. & Goadrich, M. (2006), "The Relationship Between Precision-Recall and ROC Curves", *ICML*.**

**4. Sensitivity / Specificity và điểm vận hành sens@fixed-spec.** Cặp độ nhạy/độ đặc hiệu là chuẩn vàng của đánh giá test chẩn đoán y khoa, dùng trong cả Esteva et al. (2017) lẫn **Tschandl et al. (2020), "Human–computer collaboration for skin cancer recognition", *Nature Medicine* 26:1229-1234.** Cách đọc độ nhạy tại một sàn độ đặc hiệu cố định (`sens_at_90spec`/`sens_at_95spec`, [metrics.py:61-101](../src/evaluation/metrics.py#L61-L101)) là quy ước sàng lọc chuẩn.

**5. Ngưỡng quyết định — Youden's J.** Cách chọn threshold (`youden_threshold`, [metrics.py:48-59](../src/evaluation/metrics.py#L48-L59)) theo **Youden, W.J. (1950), "Index for rating diagnostic tests", *Cancer* 3(1):32-35.**

**6. F1 / Precision / Accuracy.** Metric ML tổng quát, liệt kê cho đầy đủ; ở imbalance chúng bị trần bởi prevalence nên **không** dùng làm phán quyết (xem QA 002).

Tóm lại: metric *chính* (pAUC@TPR80) đến từ challenge y khoa uy tín + dataset paper Nature; các metric hỗ trợ (AUC-ROC, AUPRC, sens/spec, Youden) đều truy về bài kinh điển peer-reviewed. Đủ điều kiện "chỉ công nhận bài đã đăng chính thống".

## Evidence
- [src/evaluation/metrics.py:11-46](../src/evaluation/metrics.py#L11-L46) — `pauc_at_tpr()` triển khai pAUC@TPR≥80% với McClish correction (ISIC 2024 metric).
- [src/evaluation/metrics.py:158-167](../src/evaluation/metrics.py#L158-L167) — `auc_roc`, `auprc`+`prevalence`, `sens_at_*spec` được tính và lưu.
- [src/evaluation/metrics.py:48-59](../src/evaluation/metrics.py#L48-L59) — `youden_threshold()` chọn ngưỡng theo J = TPR − FPR.
- ISIC 2024 Challenge trang chính thức: https://challenge2024.isic-archive.com/ ; dataset paper *Scientific Data* doi:10.1038/s41597-024-03743-w ; benchmark peer-reviewed *npj Digital Medicine* s41746-025-02070-7 (pAUC@80TPR=0.1757). Web-verified 2026-07-01.
- McClish 1989 *Medical Decision Making* 9:190-195 (PMID 2668680) — web-verified 2026-07-01.
- Saito & Rehmsmeier 2015 *PLOS ONE* e0118432 (PMID 25738806) — web-verified 2026-07-01.
- Hanley & McNeil 1982 *Radiology* 143:29-36 ; Esteva et al. 2017 *Nature* 542:115-118 ; Tschandl et al. 2020 *Nature Medicine* 26:1229-1234 ; Youden 1950 *Cancer* 3:32-35 ; Davis & Goadrich 2006 *ICML* — reference kinh điển; đối chiếu DOI lần cuối trước khi in luận văn.

## For the thesis
Bộ metric đánh giá của đề tài không tự chế: chỉ số chính pAUC@TPR≥80% là metric chính thức của ISIC 2024 Challenge (dataset công bố trên *Scientific Data*, được dùng làm thước đo trong bài *npj Digital Medicine* 2025), còn các chỉ số hỗ trợ (AUC-ROC, AUPRC, độ nhạy/độ đặc hiệu, ngưỡng Youden) đều truy nguồn về các công trình peer-reviewed kinh điển (McClish 1989, Hanley & McNeil 1982, Saito & Rehmsmeier 2015, Youden 1950, Esteva et al. 2017), bảo đảm tính đối sánh với y văn.
