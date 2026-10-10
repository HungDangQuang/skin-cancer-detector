# R6 + R7 — bootstrap lại trên file dự đoán đã có (04/10/2026)

Driver `.tmp/r6r7.sh` trên server (CPU, chỉ đọc file dự đoán sẵn có, ghi vào thư mục này). Việc R6, R7 trong
`docs/PROGRESS.md`.

## R7 — tách hiệu ứng sampler/checkpoint khỏi C2

Câu hỏi (review 03/10 §1.5): P0 hơn teacher trên PAD (C2: ΔAUPRC +0,0619 [+0,0396; +0,0852],
`reports/ci_gates_srcsamp_indomain.json`) là nhờ KD hay nhờ công thức train khác (sampler theo nguồn + checkpoint
AUPRC, teacher không có)?

So sánh ghép cặp **cùng công thức với teacher**: `x_kd__ddi` = KD `efficientnetv2_m → mobilenetv4_conv_medium` trên
`runs_newsplit_ddi`, **không** sampler theo nguồn, checkpoint chính; `x_teacher__ddi` = `teacher/efficientnetv2_m`,
checkpoint chính. Test in-domain, `SUBGROUP=source`, B = 2000, seed 42 (`r7_kd_ddi_vs_teacher_ddi.md:52`).

| Ô PAD (A − B) | AUC | AUPRC | pAUC@TPR80 | sens@80spec |
|---|---|---|---|---|
| KD (không sampler) − teacher | +0,0056 [−0,0110; +0,0222] | +0,0032 [−0,0169; +0,0251] | +0,0005 [−0,0103; +0,0105] | +0,0127 [−0,0345; +0,0774] |

AUPRC PAD từng run: KD 0,7997 · teacher 0,7966 (`r7_kd_ddi_vs_teacher_ddi.md:31,41`).

Đặt cạnh hiệu ứng của sampler theo nguồn đã đo 30/09 (log server `bootstrap_ci_20260930_210419`, lưu vào git ở commit `2a732be` ngày 01/10) (cùng student, checkpoint chính, ghép cặp):
KD `__srcsamp` − KD = **+0,0563 [+0,0391; +0,0748]** AUPRC trên PAD (`reports/ci_srcsamp_indomain.json`,
`explicit_pairs_by_subgroup`).

**Đọc:** cùng công thức thì student KD **không phân biệt được** với teacher trên PAD (mọi khoảng chứa 0). Phần lớn khoảng
"P0 hơn teacher" +0,0619 trùng cỡ với hiệu ứng sampler +0,0563 ⇒ nhiều khả năng đến từ sampler theo nguồn (và checkpoint),
không phải từ KD. Đây là ghép hai phép đo khác nhau (không có một phép thử ghép cặp duy nhất tách ba thành phần), nên là
suy luận. Kết quả này **không** đổi nhãn C2 của P0 (C2 chấm trên P0, không phải trên `x_kd__ddi`), nhưng đổi cách đọc:
**không** được viết "student vượt teacher nhờ KD". Muốn có C2 cùng công thức thì phải train lại teacher cùng công thức
(S16).

## R6 — độ nhạy của nhãn B1/B3 với seed bootstrap

Câu hỏi (review 03/10 §1.3): cận dưới của B1 (ISIC: AUC, pAUC) và B3 (Fitzpatrick sens@80spec) của P0 nằm sát mốc
(0,922 / 0,142 / 0,47). Nhãn có đổi khi chỉ đổi seed bootstrap không?

Chạy lại `bootstrap_ci` trên đúng các cây symlink của `reports/ci_gates_srcsamp_*` (`.tmp/ci_gates/` trên server),
B = 2000, seed 42 và 1–5. **Seed 42 tái lập đúng số đã công bố** (0,9227 / 0,1418 / 0,4699). Cận dưới chưa làm tròn
(`r6_b1_indomain_seed*.json` → `fairness_gaps.x_student.per_group.isic2024`; `r6_b3_fitz_seed*.json` →
`per_run.x_student`):

| Seed | B1 AUC lo (mốc 0,922) | B1 pAUC lo (mốc 0,142) | Nhãn cổng B1 | B3 lo (mốc 0,47) | Nhãn B3 |
|---|---|---|---|---|---|
| 42 | 0,922679 | 0,141796 | CCM | 0,469931 | CCM |
| 1 | 0,922521 | 0,141567 | CCM | 0,469167 | CCM |
| 2 | 0,922965 | **0,142375** | **ĐẠT** | 0,468964 | CCM |
| 3 | 0,922143 | 0,141606 | CCM | 0,469999 | CCM |
| 4 | **0,921359** | 0,141234 | CCM | 0,469334 | CCM |
| 5 | 0,922333 | 0,141947 | CCM | 0,468103 | CCM |

Biên độ dao động của cận dưới giữa 6 seed: AUC 0,0016 · pAUC 0,0011 · B3 0,0019 — lớn hơn khoảng cách tới mốc.

**Đọc:** nhãn B1 **lật theo seed** (ĐẠT ở 1/6 seed; ô AUC đạt ở 5/6, ô pAUC ở 1/6). B3 là `CHƯA CHỨNG MINH` ở cả 6 seed,
nhưng thiếu dưới 0,002. Cả hai **sát mốc tới mức không phân định được** với B = 2000; báo cáo đúng là "cận dưới ≈ mốc".
B1 và B3 chỉ còn là báo cáo trong khung 3 trụ ⇒ không đổi phán quyết.
