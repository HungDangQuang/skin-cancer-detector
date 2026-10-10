# Đối chiếu review v2 phần đánh giá (`review/REVIEW_DANH_GIA_V2_2026-10-04.md`) — 04/10/2026

Reviewer chỉ đọc brief bản 2, không đọc repo. File này kiểm từng mục 🔍 trong repo/nguồn gốc, chạy các phép tính reviewer
đề xuất (D4, D5, D6), và ghi lại quyết định của tác giả. Phép tính: `checks.py` (chỉ thư viện chuẩn), kết quả
`output.md`:

```
python3 reports/2026-10-04_review_v2_checks/checks.py reports/2026-10-04_review_v2_checks/fitz17kC_headline_image_ids.txt
```

Chạy từ danh sách id trong repo là đủ để tái lập `output.md`. Danh sách id được sinh bằng cách giao cột `md5hash` của CSV
Fitzpatrick17k-C với `image_id` (`fitz_<md5>`) của `predictions.csv` headline (`checks.py <csv> --write-ids`). III-b của
P0 trên tập con: `tone_at_app_threshold_P0_fitz17kC.txt`.

CSV Fitzpatrick17k-C (11.394 dòng, có `md5hash`): `Fitzpatrick17k/Fitzpatrick17k_Analysis/DatasetSplits/SimThresh_T_A2_T_0.99_0.70_FC_T_KeepOne_Out_T_OutThresh_None_0FST_F.csv`
trong repo [kakumarabhishek/Corrected-Skin-Image-Datasets](https://github.com/kakumarabhishek/Corrected-Skin-Image-Datasets),
tải 04/10/2026 từ nhánh `main`, **chưa ghim commit** — chỉ có sha256 của file: `bfc28411147693a910b2b409bf449f4f6e61002f29926626eab3589c442fd219`. File gốc không chép vào
repo; danh sách 3.086 `image_id` của headline còn lại trong Fitzpatrick17k-C (ghép theo md5, `image_id = fitz_<md5>`) ở
`fitz17kC_headline_image_ids.txt`.

## Quyết định của tác giả (04/10/2026, sau review v2)

1. **III-b giữ mốc 0,80 theo từng tông** (không áp D2/D3). So với mốc bác sĩ 0,47 (D2) và điểm độ đặc hiệu 0,60 (D4)
   chỉ thêm vào **báo cáo**.
2. **III-b chấm trên Fitzpatrick17k-C** thay cho toàn bộ headline. Post-hoc: quyết sau khi đã thấy III-b của P0/P1/P2 trên headline **và** kết quả của P0 trên chính Fitzpatrick17k-C (vẫn trượt); số của P1/P2 trên Fitzpatrick17k-C cũng đã được tính trước lúc quyết (`reports/2026-10-04_review_v2_checks/output.md` (1)).
   Nhãn III-b và phán quyết tổng của P0 **không đổi** (KHÔNG ĐẠT YÊU CẦU (tạm)). Chỉ áp cho III-b; C2, B3, C4b vẫn trên
   headline.

Ghi vào `.claude/skills/eval-results/reference/acceptance-gates.md` §1, §2.1; phán quyết
`reports/2026-10-04_acceptance_verdict_P0_3pillar.md`; báo cáo vòng 2 `reports/2026-10-04_round2_report_only.md` §3.

## Từng mục

| Mục review | Kiểm / làm gì | Kết quả |
|---|---|---|
| §1 bảng — I-1 "39,5 ms nên khả năng cao đạt" | — | Đồng ý về hướng, nhưng 39,5 ms là `sustained_ms` theo kiến trúc trên `.pte` khác, không phải p95 trên `.pte` ship ⇒ vẫn `CHƯA ĐO` (U6) |
| 1.1 Mốc III-a "may đo" (0,80 ngay dưới cận dưới 0,818) | Đối chiếu thời điểm | **Đúng**: S_min/Sp_min chốt 04/10 sau khi đã thấy 0,818 / 0,667 (`acceptance-gates.md` §1, hàng S_min). Lập luận use case độc lập với số của P0 cần tác giả + GVHD viết ⇒ thêm vào U7; khai trong luận văn ⇒ `thesis/CAN_SUA_SAU.md` #27 |
| 1.2 C2 dễ vì teacher chưa đúng công thức | Đã có R7 | Đồng ý; đã khai trong phán quyết P0 (lưu ý C2) và `CAN_SUA_SAU.md` #24 |
| 1.2 🔍 δ tuyệt đối từng miền | Tính 0,05 × AUPRC teacher (TB 5 fold, checkpoint chính) | P0 (teacher `efficientnetv2_m`): PAD 0,0398 · Fitz 0,0348 · HAM 0,0247. P1 (teacher `convnextv2_base`): 0,0426 · 0,0354 · 0,0225. Miền HAM có δ nhỏ nhất (AUPRC teacher ~0,45–0,49) nhưng không "rất nhỏ"; cận dưới C2 của P0 trên HAM là −0,0068 ⇒ C2 đạt với mọi δ > 0,0068 (`reports/ci_gates_srcsamp_*`, `reports/ci_cand2_P1_*`) |
| 2.1 Mốc 0,80 cao hơn mọi tham chiếu | D2 làm thành báo cáo | sens@spec80 theo tông (TB 5 fold) trên Fitzpatrick17k-C: sáng 0,5143 [0,4764; 0,5529] — trên 0,47; trung bình 0,4723 [0,4228; 0,5264], tối 0,5092 [0,3985; 0,5928] — cắt qua 0,47 (`output.md` (4)). Tác giả giữ 0,80 làm cổng |
| 2.2 Giữ III-b là lý do dựa vào kết quả | — | **Đúng** (post-hoc theo chiều ngược). Phải khai ⇒ `CAN_SUA_SAU.md` #27 |
| 2.3 III-b gộp tổng quát hoá + công bằng, thực chất 6 điều kiện | Đếm | Đúng: 3 tông × (độ nhạy, độ đặc hiệu) = 6 ô. Chênh lệch giữa tông đã báo cáo riêng (R12, C4b). Tác giả giữ cấu trúc |
| 2.4 🔍 Abhishek et al. 2024 — Fitzpatrick17k có ảnh trùng, nhãn sai | Tìm nguồn; đối chiếu với repo | **Nguồn có thật**: Abhishek, Jain, Hamarneh, *Investigating the Quality of DermaMNIST and Fitzpatrick17k Dermatological Image Datasets*, Scientific Data 12:196 (2025; arXiv 2401.14497) — ~2.297 cụm ảnh gần trùng; bản sạch Fitzpatrick17k-C 11.394 / 16.577 ảnh. Repo chỉ bắt trùng tuyệt đối: 3 ảnh `duplicate_of` + 2 `uninformative` trong 4.320 ảnh headline (`data/splits/fitzpatrick17k/test_split.csv` trên server, cột `quality_flags`). 1.234 / 4.320 ảnh headline **không** có trong Fitzpatrick17k-C. Trên 3.086 ảnh còn lại: nhãn ác/lành và tông khớp 100% với Fitzpatrick17k-C; III-b của P0 vẫn KHÔNG ĐẠT (cận trên 0,634 / 0,544 / 0,592). ⇒ tác giả đổi tập chấm III-b sang Fitzpatrick17k-C. "Fitzpatrick17k là ảnh atlas, không phải ảnh camera người dùng" là hạn chế phải nêu (#27) |
| 2.5 🔍 Gộp tông: III–IV rơi vào nhóm nào | Đọc config | `configs/data/fitzpatrick17k.yaml:41-44`: sáng = I–II, **trung bình = III–IV**, tối = V–VI ⇒ khớp giả định của reviewer. Trên Fitzpatrick17k-C tông trung bình có độ nhạy thấp nhất (0,503), ngang tông tối (0,508). Câu "người Việt phần lớn thuộc III–IV" là giả định của reviewer, **chưa kiểm** nguồn |
| D1 Cổng "triển khai được" = III-a trên dữ liệu bệnh viện (U8) | — | Ghi vào U8 (tập xác nhận); quyết khi có dữ liệu |
| D2 Fitz thành cổng non-inferiority so với 0,47 | — | **Không áp làm cổng** (quyết định 1); chỉ báo cáo (ở trên) |
| D3 Gọi 0,80 là "mục tiêu" | — | **Không áp** (quyết định 1) |
| D4 Điểm ROC tại độ đặc hiệu 0,60 theo tông | `output.md` (2), P0 fold 4, bootstrap B = 1000 | Ngưỡng tốt nhất chọn riêng từng tông **trên chính test** (lạc quan): headline 0,742 / 0,696 / 0,726; Fitzpatrick17k-C 0,743 [0,705; 0,774] / 0,691 [0,648; 0,739] / 0,731 [0,644; 0,820]. Khoảng hụt tới 0,80 ở điểm ước lượng là **0,06–0,11**: tông sáng và tông tối hụt dưới 0,1 (0,057 / 0,069 trên Fitzpatrick17k-C), tông trung bình hụt 0,109 — đúng cỡ "≥ 0,1" reviewer ước tính. Không ngưỡng nào đưa được cả ba tông lên 0,80 ⇒ cần cải thiện model/dữ liệu |
| D5 Số ca ác theo tông | Đếm | Headline: sáng 1.195 · trung bình 757 · tối 208 ca ác (lành 1.115 · 842 · 203). Fitzpatrick17k-C: 934 · 559 · 130 ca ác (lành 824 · 514 · 125) |
| D6 Cỡ mẫu U8 theo độ nhạy thật thấp hơn 0,873 | Power **chính xác** (tổng nhị thức) cho luật thật "cận dưới Wilson 95% ≥ mốc" (`output.md` (3)) | Cần ≥ **218** ca ác nếu độ nhạy thật 0,87 (reviewer ~180: ở n = 180 power chỉ 0,69); **454** nếu 0,85; **1.312** nếu 0,83. Độ đặc hiệu (mốc 0,60, thật 0,73): **99** ca lành. 218 là n **nhỏ nhất** đạt power 0,80; power theo n có dạng răng cưa — từ n = 241 thì 60 giá trị n liền sau đều ≥ 0,80 (với độ đặc hiệu: 111). **Power chung của III-a** (cần cả hai ô; hai mẫu rời nhau): 218 ca ác + 99 ca lành chỉ cho 0,80 × 0,80 ≈ **0,64**; muốn power chung 0,80 cần **287 ca ác + 130 ca lành** (`output.md` (3)) |
| §0 Trả lời câu hỏi chính | — | Đồng ý với nhận định: khó khăn giờ nằm ở hiệu năng trên ảnh lâm sàng khác nguồn, không ở cách đo. Không có việc phát sinh |
| 1.1 gạch 2 "0,873 là số lạc quan" | — | Đồng ý: quy tắc ngưỡng 90% chọn sau khi xem test PAD (`acceptance-gates.md` "Báo cáo bắt buộc"). Đã phản ánh vào D6 (cỡ mẫu tính với độ nhạy thật thấp hơn) |
| §3 Ghi chú "cải thiện III-b là bài toán model/dữ liệu" | — | Đồng ý; D4 ủng hộ cho tông trung bình (cả CI 0,648–0,739 < 0,80 ở fold 4); với tông tối CI tới 0,820 nên chưa khẳng định được cho tông này. Bằng chứng DDI/domain-aug: `reports/2026-10-03_ddi_arm.md`, `docs/domain_aug_plan.md` |
| §4 bảng đánh giá cách xử lý | — | Ghi nhận. Chỗ reviewer vẫn chưa đồng ý: 1.4 (AND 7 cổng, III-b = 6 ô) và 1.7 (lý do giữ mốc theo tông). Hàng 1.6: điều kiện "luận văn nêu KD chưa có tác dụng trên PAD" đã ghi ở `thesis/CAN_SUA_SAU.md` #7, #13. Hàng 1.12: S9 trong `docs/PROGRESS.md`. Hàng "bước 3": xác nhận trên U8 |
| §6 Những gì reviewer chưa kiểm | — | Cochrane: xem "Chưa kiểm được" dưới đây; Abhishek et al.: đã tìm thấy (🔍 2.4); gộp tông: đã kiểm (🔍 2.5); cỡ mẫu: đã tính chính xác (D6); khoảng cách III-b: đã tính (D4) |
| §5 Đính chính R-ngoài §1.11 và §1.9 | Tìm trong docs | Đồng ý. §1.11 đã được brief ghi đúng (`docs/PROJECT_BRIEF_FOR_REVIEW.md` hàng 1.11). Không tài liệu nào trong repo dùng phép so 0,74 vs 0,83 của R-ngoài §1.9 làm bằng chứng |

## Chưa kiểm được

- Chi tiết thuật toán phát hiện trùng của Fitzpatrick17k-C (ngưỡng tương đồng, cách giữ một ảnh mỗi cụm) chỉ đọc qua bản
  HTML arXiv; số 2.297 cụm và 11.394 ảnh lấy từ đó. Bản sạch có thể vẫn còn ảnh trùng chưa phát hiện.
- Câu "người Việt phần lớn thuộc Fitzpatrick III–IV" (reviewer §2.5).
- Nội dung bài Abhishek et al. (Sci Data 12:196, arXiv 2401.14497; ~2.297 cụm trùng; "ảnh lỗi"/"nhãn sai" — theo bản tóm tắt
  và HTML arXiv, chỉ assistant đọc qua web) và việc file `SimThresh_…_0FST_F.csv` chính là bản bài báo gọi là
  Fitzpatrick17k-C (theo mô tả của README repo GitHub, chưa đối chiếu với bài báo). Sub-agent kiểm chéo không có web.
- Số "3 `duplicate_of` + 2 `uninformative`" trong 4.320 ảnh headline: chỉ có trên server (`data/splits/fitzpatrick17k/`
  không có trên Mac).
- Khoảng bootstrap của D2 (tập con) và D4: sub-agent không chạy lại được (chỉ kiểm điểm ước lượng).
- Con số Cochrane 0,47 (đọc qua web 01/10, xem `acceptance-gates.md` §2 B).
