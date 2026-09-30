# Nhật ký soát luận văn

Bảng theo dõi tiến độ soát [LUAN_VAN.md](LUAN_VAN.md) theo sáu tiêu chí của tác giả.
Quy trình và rubric: [.claude/skills/review-thesis/](../.claude/skills/review-thesis/SKILL.md).

Trạng thái: `—` chưa soát · `ĐẠT` không còn phát hiện · `CẦN SỬA` đã báo cáo, chờ duyệt bản vá ·
`ĐÃ SỬA` bản vá đã áp vào LUAN_VAN.md.

Nội dung báo cáo **không** nằm ở đây — file này chỉ là bảng theo dõi.

Cột "Kiểm chéo" = kết quả cổng kiểm chéo bắt buộc (chốt 14/09/2026): hai sub-agent
`review-verifier` chạy song song trên bản nháp báo cáo trước khi nó tới tác giả, ghi dạng
`FACTS <phán quyết> · PATCH <phán quyết>` (ví dụ `FACTS ĐẠT · PATCH SỬA LẠI(2)`). Dấu `—`
nghĩa là mục đó được soát **trước** khi có cổng, không phải cổng đã chạy và sạch. Quy trình:
[cross-check.md](../.claude/skills/review-thesis/reference/cross-check.md).

Cột "Dòng" là mốc lúc dựng lại bảng (13/09/2026, sau đợt sửa bố cục theo Phụ lục 2) và sẽ trôi
sau mỗi lần sửa; lấy số dòng hiện tại bằng
`python3 .claude/skills/review-thesis/scripts/section_audit.py --list`.

| Phần | Dòng | Trạng thái | Ngày soát | CHẶN / NÊN SỬA / GỢI Ý | Kiểm chéo | Ghi chú |
|---|---|---|---|---|---|---|
| LỜI CAM ĐOAN | 33 | — | | | | |
| TÓM TẮT | 53 | — | | | | |
| ABSTRACT | 69 | — | | | | |
| MỤC LỤC | 85 | — | | | | |
| DANH MỤC CÁC KÝ HIỆU VÀ CHỮ VIẾT TẮT | 215 | — | | | | |
| DANH MỤC THUẬT NGỮ CHUYÊN NGÀNH | 280 | — | | | | |
| DANH MỤC BẢNG | 486 | — | | | | |
| DANH MỤC HÌNH | 546 | — | | | | |
| MỞ ĐẦU | 565 | — | | | | |
| **Chương 1. TỔNG QUAN** | 575 | — | | | | |
| 1.1 Bối cảnh y tế và động lực nghiên cứu | 578 | ĐÃ SỬA | 13/09/2026 | 0 / 3 / 1 | — | Áp đủ 4/4 bản vá. Còn treo: 12 trích dẫn chưa đối chiếu được toàn văn — [TRICH_DAN_CAN_KIEM_CHUNG.md](TRICH_DAN_CAN_KIEM_CHUNG.md) |
| 1.2 Động lực kỹ thuật: nghịch lý chính xác – triển khai | 586 | ĐÃ SỬA | 13/09/2026 | 0 / 5 / 1 | — | Áp đủ 5/5 bản vá — phát hiện [7] (trùng lặp với 1.3.2) đã xử lý ở lượt soát §1.3. Thêm: mô tả lại ensemble ISIC 2020 cho khớp [16] (18 mô hình, 16 thuộc họ EfficientNet) |
| 1.3 Các nghiên cứu liên quan theo trục thời gian | 599 | ĐÃ SỬA | 13/09 + 14/09 + 15/09 + 16/09 | 6 / 4 / 0 | FACTS `SỬA LẠI` ×3 · PATCH `SỬA LẠI`/`CHẶN` ×3 | Bốn lượt. 16/09 tái cấu trúc §1.3.4: Bảng 1.1 thêm cột **"Nhánh đối chứng không chưng cất"** (3 Không / 1 Có) và đổi cột cuối thành "Accuracy tuyệt đối đã báo cáo" → **xoá hẳn đoạn chú thích 755 ký tự**; dòng 633 bỏ 5 số không so được + mệnh đề sai về [29] MobileNetV3. **Phát hiện lật kết luận cũ**: [37] Pavel CÓ nhánh đối chứng (HSB) — sổ trích dẫn lượt 2 ghi "kiểm được cho cả bốn" là sai. §1.3.4: 2.520 → 1.632 ký tự |
| 1.4 Khoảng trống nghiên cứu | 637 | ĐÃ SỬA | 13/09 + 15/09 | 1 / 6 / 2 | FACTS `SỬA LẠI` ×2 · PATCH `SỬA LẠI` ×5 | Áp đủ **8/8** bản vá, gồm cả ô Bảng 1.5 (dòng 792) `Mục 4.12`→`Mục 4.9` — mục CHẶN đó **đã hết**, lượt soát §1.8 không phải tìm lại. Kiểm chéo bắt 2 lỗi của người soát: dải dòng `distillation.py:78-82` phải là `70-86`, và đếm mức "0 CHẶN" che mất hàng CHẶN ngoài phạm vi. **Treo 1 phát hiện MỚI chờ duyệt**: dòng 881 (§2.3.2) trỏ `(Mục 1.4)` cho mệnh đề *teacher mạnh hơn có dạy tốt hơn không* — Bảng 1.2 hàng 3 không còn phát biểu mệnh đề đó. **16/09 — tác giả viết lại Bảng 1.2 (5 hàng → 4)**: bỏ hàng "paradigm nào hưởng lợi nhiều nhất" (Mục 4.3 bác bỏ cách đọc theo paradigm — thủ phạm là chất lượng baseline, r = −0,963), gộp hai vế teacher vào một hàng (khép luôn phát hiện treo về dòng 881), đổi hệ quả hàng ISIC 2024 và đổi câu hỏi hàng cuối sang "student có hoạt động tốt hơn trên điện thoại không". Kéo theo: câu dẫn + câu chốt §1.4, §1.8 dòng 745, con trỏ Q2 ở §1.6. Rà 6/6 câu hỏi Q1–Q6: đều có đáp án ở §5.1. **16/09 (lượt 2)** — đổi khung lý do chọn mô hình: tiêu chí là **hiệu năng tốt nhất hiện có theo từng vai trò**, còn việc trải paradigm là đặc điểm giữ có chủ đích, không phải tiêu chí chọn. Sửa §2.2 mở đầu, đoạn teacher, §2.2.3 mở đầu + đoạn chốt, TÓM TẮT, ABSTRACT, §1.8, mục `Paradigm` trong bảng thuật ngữ; thêm mục `State-of-the-art` (nhóm C). **16/09 (lượt 3)** — bỏ hẳn đoạn định vị "đóng góp là thực nghiệm chứ không phải thuật toán" (§1.8 đã nói đủ), và viết lại câu chốt thành **thiết lập quy trình thực nghiệm bốn thành phần để kiểm chứng** thay vì "lấp khoảng trống". Hệ quả hàng 2 đổi từ "chọn teacher dựa trên trực giác" sang "chưa có căn cứ đã kiểm chứng". §1.4 nay 15 dòng |
| 1.5 Phát biểu bài toán | 656 | ĐÃ SỬA | 13/09/2026 | 1 / 1 / 2 | — | Áp đủ 4/4 bản vá. CHẶN đã gỡ: khẳng định "thứ hạng tốc độ đảo chiều x86→ARM" trái số đo (hai nền cùng thứ tự; Chương 4 không đo x86) → thay bằng backend 181× + điều tiết nhiệt 45–49%, cả hai có sẵn trong §4.9.1. Cổng `--numbering` toàn văn: 0 phát hiện |
| 1.6 Câu hỏi nghiên cứu | 671 | ĐÃ SỬA | 16/09/2026 (2 lượt) | 0 / 7 / 0 | FACTS `ĐẠT`/`SỬA LẠI` · PATCH `ĐẠT`/`SỬA LẠI` | Lượt 1: 6 bản vá (thuật ngữ, quy ước trích, chú dẫn `[4, 31]`, Q3 khớp §5.1, câu chốt). Lượt 2 (tác giả yêu cầu đối chiếu câu hỏi trung tâm ↔ 6 câu con): phát hiện câu hỏi trung tâm chỉ có **2 vế** trong khi văn bản khẳng định **3 câu** đi thẳng vào nó — Q4 không bám vế nào. Áp Cách A (sửa câu mô tả, 1 dòng, không đụng câu hỏi trung tâm). **Còn để ngỏ**: chữ "đáng kể" không câu con nào nhận; MỞ ĐẦU dòng ~569 phát biểu câu hỏi trung tâm bằng cặp vế KHÁC (trục "cứu lại bao nhiêu phần hiệu năng đã mất" = Q4) — chênh có sẵn, mức GỢI Ý; Q4 nay được mô tả nhưng không gán nhãn cốt-lõi hay phụ-trợ |
| 1.7 Phạm vi và giới hạn của luận văn | 692 | ĐÃ SỬA | 16/09/2026 | 1 / 3 / 2 | FACTS `SỬA LẠI`(4) + `SỬA LẠI`(3) · PATCH `SỬA LẠI`(4) + `SỬA LẠI`(2) | Áp đủ **6/6** bản vá. CHẶN đã gỡ: dòng 710 từng hứa "Mục 5.3 đề xuất chúng như hướng phát triển" nhưng §5.3 chỉ có 5 hướng, không hướng nào về chưng cất đặc trưng/quan hệ → nay trỏ Bảng 2.1 (Mục 2.3.2). **Phát hiện đối chiếu repo**: dòng 726 "chứ không phải vì đã thử và thất bại" sai với hàng RKD của Bảng 1.4 — hai nhánh `*__rkd` ĐÃ chạy đủ 5 fold; paired CI (`bootstrap_ci_dirA_decomp.md:76`) cho thấy thêm RKD làm **mobilenetv4** mất 0,0069 pAUC [0,0031; 0,0109], còn **fastvit 4/4 khoảng đều chứa 0** → mệnh đề đã bị cắt bỏ. Cùng cụm từ ở dòng **1563** thì ĐÚNG (nhánh `SAMP=off` thật sự chưa chạy) → cấm tìm-thay toàn văn. Kiểm chéo chạy 2 lượt (bản nháp + bản đã áp), bắt 6 lỗi của người soát, không lỗi nào trong luận văn: `distillation_rkd.yaml:41`→`:42`; dòng 696→694; "dòng 179 khối thuật ngữ"→459; registry 16–19 có **4** teacher không-privileged (kèm `panderm`); "đã thử và thất bại" ở **1563** không phải 1561; back-ref §1.7 ở **2150** không phải 2152. **Treo 2 GỢI Ý chưa xử lý**: (a) Bảng 1.4 hàng 2 cột cuối "mở lại được nếu tinh chỉnh trọng số" nay chỉ đúng cho nhánh *quan hệ*, không đúng cho nhánh *đặc trưng* (bị loại vì cần lớp chiếu); (b) [TRICH_DAN_CAN_KIEM_CHUNG.md](TRICH_DAN_CAN_KIEM_CHUNG.md) neo theo SỐ DÒNG tuyệt đối nên nay lệch thêm +2 (đã lệch sẵn từ trước) |
| 1.8 Đóng góp của luận văn | 732 | ĐÃ SỬA | 17–18/09/2026 | 3 / 6 / 1 | FACTS `SỬA LẠI`(5) + `CHẶN`(2) · PATCH `CHẶN`(4) + `SỬA LẠI`(3) | Áp đủ 10/10 bản vá + 6 chỗ ripple (61, 77, 668, 2123, 2133, 2153). Kiểm chéo lượt áp bắt thêm 2 lỗi do CHÍNH bản vá tạo ra ("ra ngoài miền" — Fitzpatrick không đảo thứ hạng; "2/4 student" là số của AUC) → đã sửa vòng 2. Còn dòng 1888 §4.5 chờ tác giả quyết |
| **Chương 2. CƠ SỞ LÝ THUYẾT** | 795 | — | | | | |
| 2.1 Bài toán phân loại tổn thương da bằng học sâu | 797 | ĐÃ SỬA | 18/09/2026 | 0 / 3 / 1 | FACTS `SỬA LẠI`(4) + `SỬA LẠI`(2) · PATCH `SỬA LẠI`(4) + `SỬA LẠI`(2) | Áp **1/4** bản vá: [2] dòng 803 "Chương 4 **sẽ** định lượng" → "Chương 4 định lượng". **[3] (dòng 801, cụm "bộ dữ liệu thực tế nhất từ trước tới nay") — tác giả TỪ CHỐI**, chốt: 801 và 624 giữ nguyên, ripple 624 vô hiệu. **[1] (dòng 803, phạm vi) và [4] (dòng 811, dấu câu) — chưa có quyết định.** ⚠️ [1] và [2] loại trừ nhau nên vấn đề của [1] CÒN NGUYÊN trong chính câu vừa sửa, và nay phát biểu **chắc chắn hơn** (hết thì tương lai): câu vẫn hứa "mức suy giảm đó" cho **cả hai** chiều trong khi Chương 4 chỉ đo chiều "ngược lại" (dòng 1988). Kiểm chéo lượt SOÁT bắt 4 lỗi của người soát (đếm "2 chỗ sẽ" → ≥5; "2 chỗ so sánh nhất" → 1; Bảng 3.6 ở 1135–1136 không phải 1131; 293=Clinical image / 296=Dermoscopy). Kiểm chéo lượt ÁP bắt thêm 2: log còn `CẦN SỬA`, và **chặn một lỗi bịa** — định báo "sửa 1/5 tạo chỗ không đồng nhất mới", số đo nói ngược (nay 21 thì hiện tại ↔ 4 "sẽ" ở 1098/1202/1266/1691; bản vá ĐƯA 803 về nhóm đa số). `--numbering` toàn văn: 0 phát hiện, exit 0. "114 lớp bệnh" (dòng 810) = KHÔNG VERIFY ĐƯỢC (không có `data/raw/fitzpatrick17k/` trên Mac); dòng 799 "phần lớn các cuộc thi ISIC trước 2024" chưa xếp hạng phát hiện |
| 2.2 Các họ kiến trúc thị giác máy tính liên quan | 819 | — | | | | |
| 2.3 Chưng cất tri thức | 850 | — | | | | |
| 2.4 Mất cân bằng lớp cực đoan | 901 | — | | | | |
| 2.5 Đánh giá mô hình ở prevalence rất thấp | 933 | — | | | | |
| **Chương 3. PHƯƠNG PHÁP ĐỀ XUẤT** | 971 | — | | | | |
| 3.1 Tổng quan kiến trúc hệ thống | 973 | — | | | | |
| 3.2 Dữ liệu và tiền xử lý | 1010 | — | | | | |
| 3.3 Chiến lược chia dữ liệu chống rò rỉ | 1294 | — | | | | |
| 3.4 Kiến trúc mô hình | 1346 | — | | | | |
| 3.5 Hàm mất mát và cơ chế chưng cất | 1440 | — | | | | |
| 3.6 Chiến lược xử lý mất cân bằng lớp | 1480 | — | | | | |
| 3.7 Quy trình huấn luyện và nhánh đối chứng | 1524 | — | | | | |
| 3.8 Kiểm chứng hai lựa chọn dữ liệu | 1546 | — | | | | |
| 3.9 Các độ đo đánh giá | 1564 | — | | | | |
| 3.10 Đánh giá độ tin cậy của chênh lệch | 1587 | — | | | | |
| 3.11 Đưa mô hình lên thiết bị | 1601 | — | | | | |
| **Chương 4. KẾT QUẢ THỰC NGHIỆM** | 1633 | — | | | | |
| 4.1 Quy mô thực nghiệm đã hoàn tất | 1635 | — | | | | |
| 4.2 Hiệu năng trong miền của student và teacher | 1651 | — | | | | |
| 4.3 Bằng chứng thống kê về hiệu quả chưng cất | 1711 | — | | | | |
| 4.4 Hai miền ảnh ẩn sau con số AUPRC tổng | 1825 | — | | | | |
| 4.5 Đánh giá hiệu quả chưng cất theo từng teacher | 1872 | — | | | | |
| 4.6 Kiểm chứng hai lựa chọn dữ liệu | 1894 | — | | | | |
| 4.7 Tổng quát hoá xuyên miền — HAM10000 | 1968 | — | | | | |
| 4.8 Công bằng theo tông da — Fitzpatrick17k | 1994 | — | | | | |
| 4.9 Benchmark trên thiết bị biên | 2030 | — | | | | |
| 4.10 Lựa chọn mô hình triển khai | 2067 | — | | | | |
| **Chương 5. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN** | 2117 | — | | | | |
| 5.1 Trả lời câu hỏi nghiên cứu trung tâm | 2121 | — | | | | |
| 5.2 Hạn chế của nghiên cứu | 2139 | — | | | | |
| 5.3 Hướng phát triển | 2151 | — | | | | |
| **DANH MỤC CÔNG BỐ KHOA HỌC CỦA TÁC GIẢ** | 2167 | — | | | | |
| **TÀI LIỆU THAM KHẢO** | 2179 | — | | | | |
| **PHỤ LỤC A — Bảng đầy đủ 19 run in-domain** | 2293 | — | | | | |
| **PHỤ LỤC B — Cấu hình siêu tham số đầy đủ** | 2431 | — | | | | |
| B.1 Dữ liệu và chia dữ liệu | 2435 | — | | | | |
| B.2 Kiến trúc | 2451 | — | | | | |
| B.3 Tối ưu hoá | 2463 | — | | | | |
| B.4 Hàm mất mát | 2482 | — | | | | |
| B.5 Callback | 2495 | — | | | | |
| B.6 Đánh giá và thống kê | 2506 | — | | | | |
| B.7 Triển khai | 2519 | — | | | | |
