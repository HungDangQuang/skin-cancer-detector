# Báo cáo tiến độ luận văn — 09/10/2026

**Đề tài:** Phát hiện ung thư da trên thiết bị biên sử dụng mô hình học sâu kết hợp chưng cất tri thức
**Học viên:** Đặng Quang Hưng · **Người hướng dẫn:** TS. Nguyễn Thanh Bình · **Ngày lập:** 09/10/2026

> Bản chụp ngày 09/10/2026 cho buổi báo cáo tiến độ, không cập nhật tiếp. Trạng thái hiện hành chỉ theo dõi ở
> `docs/PROGRESS.md`.

> **Tóm tắt.** Các lượt huấn luyện và đánh giá đã lên lịch đều đã chạy xong (theo tracker ngày 04/10, không còn job
> trên server). Còn hoãn ba việc: đo độ trễ p95 và pipeline camera trên đúng mô hình phát hành, và huấn luyện lại
> teacher cùng công thức (mục 1). Mô hình đang được chọn để triển khai (student MobileNetV4, chưng cất từ teacher
> EfficientNetV2-M) chạy trên điện thoại cho **kết quả trùng khớp với máy chủ**. Mô hình đạt mốc (tạm, khám phá) trên
> ảnh chụp bằng điện thoại cùng nguồn với dữ liệu huấn luyện (PAD-UFES-20). Tuy nhiên mô hình **chưa đạt** trên ảnh
> lâm sàng khác nguồn (Fitzpatrick17k): ở ngưỡng quyết định của ứng dụng, nó chỉ bắt được 50–60% ca ác tính, trong
> khi mốc là 80%. Phán quyết hiện hành là **KHÔNG ĐẠT YÊU CẦU (tạm, khám phá)**. Luận văn đã có bản toàn văn, nhưng
> viết trên bộ chia dữ liệu cũ (có rò rỉ bệnh nhân) nên phần kết quả cần viết lại. Đề cương rút gọn đã cập nhật đến
> 08/10 và đang được trình bày lại theo khung mẫu.

**Quy ước và thuật ngữ**

- `[a; b]` là khoảng tin cậy 95%: bootstrap theo ảnh test (2.000 lần) cho các chỉ số xếp hạng và các chênh lệch
  (ghép cặp khi so hai mô hình), Wilson cho các tỉ lệ đếm được.
- "TB 5 fold" là trung bình của 5 mô hình kiểm định chéo, chấm trên cùng tập test.
- **Mọi số đo trên bộ chia dữ liệu mới theo bệnh nhân (splits v2, 22/09/2026)**, trừ khi ghi khác.
- **AUPRC** là diện tích dưới đường precision–recall, chỉ số chính khi ca ác rất hiếm (~0,45% trên tập test trong
  miền). Không so được AUPRC giữa hai bộ dữ liệu khác nhau.
- **pAUC@TPR80** là AUC ở vùng độ nhạy ≥ 80%, chỉ số chính thức của ISIC 2024 (thang 0–0,2).
- **sens@spec80** là độ nhạy khi cố định độ đặc hiệu 80%.
- **Fitzpatrick17k "headline"** có 4.320 ảnh, nửa ác nửa lành. **Fitzpatrick17k-C** là tập con 3.086 ảnh, đã loại
  ảnh gần trùng. Tập này dùng chấm trụ III-b từ 04/10; việc đổi sang tập này được quyết sau khi đã thấy kết quả
  (post-hoc).
- **File `.pte`** là mô hình đã chuyển sang định dạng chạy trên điện thoại (ExecuTorch).
- **Logit** là đầu ra thô của mô hình, trước khi đổi thành xác suất.

---

## 1. Tiến độ hiện tại

Ký hiệu: ✅ xong · 🟡 đang làm / xong một phần · ⬜ chưa làm · ⏸ tạm hoãn.

### 1.1 Huấn luyện

| | Hạng mục | Trạng thái |
|---|---|---|
| ✅ | Ma trận cũ gồm 3 teacher × 4 student, có và không có KD, kèm các thí nghiệm loại trừ dữ liệu: 140 lượt fold (07–09/2026) | Xong. Số trong miền bị thổi phồng do rò rỉ bệnh nhân; số ngoài miền (AUC/AUPRC/pAUC) vẫn dùng được |
| ✅ | Phát hiện rò rỉ và dựng lại bộ chia theo bệnh nhân (22/09) | Xong: 372.242 ảnh, 2.410 bệnh nhân; tập test 59.093 ảnh, 265 ca ác |
| ✅ | Ba can thiệp dữ liệu trên bộ chia mới: tăng cường ảnh theo miền, bổ sung ảnh DDI, lấy mẫu phân tầng theo nguồn (23/09–03/10) | Xong. Tăng cường theo miền thất bại và đã gỡ; hai can thiệp còn lại có ích (mục 2.3) |
| ✅ | Vòng chọn ứng viên thứ hai: thử thêm hai cặp teacher → student, ConvNeXtV2-Base → MobileNetV4 (đổi teacher) và EfficientNetV2-M → RepViT-M1.0 (đổi student). Luật chọn được đăng ký trước ngày 02/10 | Train xong 03/10, chọn ngày 04/10: luật chọn trên tập val giữ lại ứng viên cũ |
| ⏸ | Huấn luyện lại teacher cùng công thức với student (lấy mẫu theo nguồn, checkpoint theo AUPRC), để phép so student − teacher được công bằng | Chưa làm |
| ⬜ | So sánh với các kỹ thuật nén và điều chuẩn khác (label smoothing không cần teacher, lượng tử hoá INT8) | Chưa làm; chờ quyết định có đưa vào phạm vi không |

Theo tracker (bản cập nhật 04/10, trên nhánh `docs/tracker-cleanup-and-ddi`), không còn job nào chạy trên server.

### 1.2 Đánh giá

| | Hạng mục | Trạng thái |
|---|---|---|
| ✅ | Đánh giá trong miền (ISIC 2024, PAD-UFES-20) trên tập test mới, có khoảng tin cậy ghép cặp | Xong |
| ✅ | Đánh giá ngoài miền: HAM10000 (dermoscopy) và Fitzpatrick17k (ảnh lâm sàng, 4 biến thể), theo từng nhóm tông da | Xong |
| ✅ | Xây dựng bộ tiêu chí đánh giá ba trụ: chạy được, chạy đúng trên điện thoại, và đúng với người dùng tại ngưỡng của app | Xong 03/10. Mốc chốt tạm 04/10: độ nhạy tối thiểu 0,80, độ đặc hiệu tối thiểu 0,60, và biên "không kém teacher" δ = 5% AUPRC của teacher |
| ✅ | Phán quyết cho mô hình ứng viên | Xong 04/10: **KHÔNG ĐẠT YÊU CẦU (tạm, khám phá)** |
| ✅ | Đánh giá trên điện thoại thật (Pixel 6a) với chính mô hình ứng viên: 70.883 ảnh, so với máy chủ | Xong 01/10, kết quả trùng khớp (mục 2.5) |
| ⏸ | Độ trễ phân vị 95 (p95) trên đúng file `.pte` của mô hình ứng viên | Chưa đo; hiện chỉ có số theo kiến trúc |
| ⏸ | Pipeline camera thật của app (chụp → cắt → thu nhỏ → mô hình), đo tỉ lệ quyết định bị đổi so với máy chủ | Chưa đo |
| ⬜ | Chốt chính thức các mốc (cùng GVHD) | Đang chờ |
| ⬜ | Tập xác nhận mới, chưa từng mở (thu qua bệnh viện) | Chưa có. Ước tính cần ~287 ca ác + 130 ca lành, nếu độ nhạy thật 0,87 và độ đặc hiệu thật 0,73 (bằng điểm ước lượng của mô hình trên ảnh PAD) |

### 1.3 Luận văn

| | Hạng mục | Trạng thái |
|---|---|---|
| ✅ | Bản toàn văn 5 chương + 2 phụ lục (`thesis/LUAN_VAN.md`, ~2.530 dòng, 55 tài liệu tham khảo) | Xong 29/08, đã gửi GVHD 20/09 |
| ✅ | Chọn cách xử lý sự cố rò rỉ (03/10): công khai sự cố ở Mục 3.3, giữ Chương 4 cũ kèm nhãn "lạm phát", thêm một mục kết quả mới tự chứa trên bộ chia mới | Đã quyết |
| 🟡 | Danh sách chỗ cần sửa (27 mục, `thesis/CAN_SUA_SAU.md`) | Đã ghi chú, **chưa sửa**; chờ có kết quả ổn mới sửa |
| ⬜ | Viết lại câu hỏi nghiên cứu theo hai câu hỏi trung tâm (chốt 03/10) | Chưa làm; bộ câu hỏi con vẫn là đề xuất |
| ⬜ | Viết mục kết quả trên bộ chia mới, tiêu chí ba trụ và kết quả trên điện thoại | Chưa làm |

### 1.4 Đề cương (proposal)

| | Hạng mục | Trạng thái |
|---|---|---|
| ✅ | Đề cương đầy đủ (`report_phase_1/DE_CUONG.md`) | Cập nhật đến 19/09; chưa phản ánh các điều chỉnh sau đó |
| ✅ | Đề cương rút gọn (`docs/DE_CUONG.md`) cập nhật 08/10: hai câu hỏi trung tâm, sự cố rò rỉ, khung ba trụ, kế hoạch theo giai đoạn | Xong (bản chụp ở commit `dc3e966`) |
| 🟡 | Trình bày lại theo khung đề cương mẫu: thêm biểu đồ Gantt và bảng giải trình chỉnh sửa | Đang làm 09/10, chưa commit |
| ⬜ | Duyệt bộ câu hỏi con; chốt các mốc đánh giá | Chờ GVHD |

---

## 2. Kết quả tính đến 09/10/2026

### 2.1 Mô hình đang được xét

| | |
|---|---|
| Ứng viên triển khai (P0) | Student **MobileNetV4-Conv-Medium**, chưng cất từ teacher **EfficientNetV2-M**; huấn luyện có ảnh DDI và lấy mẫu phân tầng theo nguồn; checkpoint chọn theo AUPRC; fold 4 |
| Hai ứng viên vòng 2 (chỉ báo cáo) | P1 = ConvNeXtV2-Base → MobileNetV4 · P2 = EfficientNetV2-M → RepViT-M1.0 |
| Cách chọn | Luật đăng ký trước, chỉ dùng tập val (AUPRC trên ảnh PAD): P0 0,8831 · P1 0,8840 · P2 0,8536. P1 hơn P0 0,0009, dưới biên hoà 0,005 ⇒ giữ P0 |
| Ngưỡng quyết định của app | 0,5705, chọn trên ảnh PAD của tập val sao cho độ nhạy ≈ 90%. Quy tắc này được chọn sau khi đã xem kết quả ⇒ post-hoc |
| Kích thước / chi phí | ~32 MiB (file `.pte` cùng kiến trúc); 1,653 GFLOPs |

### 2.2 Bảng kết quả đánh giá

**Bảng 1. Kết quả theo bộ tiêu chí ba trụ — mô hình P0**

| Trụ | Tiêu chí | Mốc | Kết quả [95%] | Nhãn |
|---|---|---|---|---|
| I. Chạy được | Độ trễ p95 trên Pixel 6a | ≤ 80 ms (đề xuất) | chưa đo trên đúng file của P0 | CHƯA ĐO |
| II. Chạy đúng trên điện thoại | Chênh logit tối đa điện thoại ↔ máy chủ · chênh AUPRC | < 1e-3 · < 0,005 (đề xuất) | 5,2e-06 · 0,0000 | ĐẠT (mốc đề xuất) |
| | Ổn định: tỉ lệ lỗi · chạy lại có trùng bit | < 0,1% · trùng (đề xuất) | 0/70.883 · 500/500 | ĐẠT (mốc đề xuất) |
| | Tỉ lệ quyết định bị đổi qua pipeline camera của app | < 0,5% (đề xuất) | chưa đo | CHƯA ĐO |
| III-a. Đúng trên ảnh điện thoại (PAD, tập test) | Độ nhạy · độ đặc hiệu tại ngưỡng app | cận dưới ≥ 0,80 · ≥ 0,60 (tạm) | 165/189 = 0,873 [0,818; 0,913] · 152/208 = 0,731 [0,667; 0,786] | **ĐẠT (tạm)** |
| III-b. Đúng trên ảnh lâm sàng khác nguồn (Fitzpatrick17k-C), từng tông da | Độ nhạy tại ngưỡng app | cận dưới ≥ 0,80 mỗi tông (tạm) | sáng 0,603 [0,571; 0,634] · trung bình 0,503 [0,461; 0,544] · tối 0,508 [0,423; 0,592] | **KHÔNG ĐẠT (tạm)** |
| | Độ đặc hiệu tại ngưỡng app | cận dưới ≥ 0,60 mỗi tông (tạm) | 0,742 · 0,813 · 0,824 (cận dưới 0,711 · 0,777 · 0,748) | ĐẠT (tạm) |
| Student so với teacher | ΔAUPRC student − teacher, từng miền (TB 5 fold) | cận dưới > −δ (tạm) | PAD +0,0619 [+0,0396; +0,0852] · Fitz +0,0068 [−0,0008; +0,0146] · HAM +0,0059 [−0,0068; +0,0189] | ĐẠT (tạm)* |
| **Tổng** | | | | **KHÔNG ĐẠT YÊU CẦU (tạm, khám phá)** |

Trụ I–III đo trên fold 4 (mô hình phát hành); dòng student − teacher là khoảng tin cậy trên trung bình 5 fold.
"(tạm)" là mốc chốt tạm 04/10. Gọi là "khám phá" vì các mốc được chốt sau khi đã thấy số của P0.
\* Teacher chưa được huấn luyện cùng công thức với student, nên phép so này dễ đạt hơn thực tế (mục 2.3, điểm 3).
Khối `Cổng chấp nhận` đầy đủ ở Phụ lục A. Nguồn: `reports/2026-10-04_acceptance_verdict_P0_3pillar.md`; bảng số
tổng hợp ở `docs/EVAL_RESULTS_2026-10-04.md` §2–§5.

**Bảng 2. Khả năng xếp hạng theo từng miền ảnh (TB 5 fold, không phụ thuộc ngưỡng)**

| Ứng viên | ISIC AUC | ISIC pAUC@TPR80 | PAD sens@spec80 | Fitzpatrick sens@spec80 | HAM10000 sens@spec80 |
|---|---|---|---|---|---|
| P0 (được chọn) | 0,9437 [0,9227; 0,9616] | 0,1580 [0,1418; 0,1730] | 0,8180 [0,7406; 0,8786] | 0,4946 [0,4699; 0,5178] | 0,7259 [0,7018; 0,7508] |
| P1 | 0,9404 [0,9161; 0,9599] | 0,1542 [0,1346; 0,1707] | 0,8571 [0,7811; 0,9101] | 0,4792 [0,4546; 0,5068] | 0,6395 [0,6121; 0,6652] |
| P2 | 0,9412 [0,9181; 0,9603] | 0,1553 [0,1388; 0,1710] | 0,7111 [0,6129; 0,7905] | 0,4325 [0,4037; 0,4581] | 0,6758 [0,6480; 0,7007] |
| *Tham chiếu* | *0,922 (ISIC 2024, chỉ dùng ảnh)* | *0,142* | *bác sĩ: 0,81 đọc dermoscopy / 0,47 nhìn ảnh thường* | *0,47* | *0,81* |

Tham chiếu ISIC: Kurtansky et al. 2025, biến thể chỉ dùng ảnh, đo trên tập test của cuộc thi (không phải phần ISIC
của bộ chia v2). Tham chiếu bác sĩ: tổng quan Cochrane (Dinnes et al. 2018), chỉ tính melanoma. HAM10000 là ảnh
dermoscopy, khác loại ảnh app nhận, nên chỉ báo cáo. Nguồn: `docs/EVAL_RESULTS_2026-10-04.md` §7.

**Bảng 3. Tại ngưỡng của app — cả ba ứng viên (fold 4, Wilson 95%)**

| Ứng viên | PAD độ nhạy | PAD độ đặc hiệu | Fitz17k-C độ nhạy: sáng · trung bình · tối | Fitz17k-C độ đặc hiệu: sáng · trung bình · tối |
|---|---|---|---|---|
| P0 | 0,873 [0,818; 0,913] | 0,731 [0,667; 0,786] | 0,603 · 0,503 · 0,508 | 0,742 · 0,813 · 0,824 |
| P1 | 0,894 [0,842; 0,930] | 0,707 [0,642; 0,764] | 0,706 · 0,646 · 0,723 | 0,655 · 0,720 · 0,624 |
| P2 | 0,862 [0,806; 0,904] | 0,673 [0,607; 0,733] | 0,696 · 0,530 · 0,546 | 0,609 · 0,714 · 0,768 |

Cả ba ứng viên đều đạt trên ảnh PAD và đều trượt trên Fitzpatrick: không tông da nào có cận dưới độ nhạy ≥ 0,80.
Bảng này được tính **sau** khi đã chọn P0, nên không được dùng để đổi ứng viên. Nguồn:
`docs/EVAL_RESULTS_2026-10-04.md` §3–§4.

**Bảng 4. Hiệu quả của chưng cất tri thức (KD): có KD − không KD, cùng student, ΔAUPRC, TB 5 fold — chỉ báo cáo**

| Ứng viên | PAD | Fitzpatrick | HAM10000 |
|---|---|---|---|
| P0 | −0,0008 [−0,0199; +0,0187] | **+0,0395 [+0,0310; +0,0478]** | **+0,1115 [+0,0985; +0,1257]** |
| P1 | +0,0026 [−0,0169; +0,0231] | **+0,0397 [+0,0322; +0,0466]** | **+0,0559 [+0,0445; +0,0678]** |
| P2 | **+0,0349 [+0,0051; +0,0650]** | **+0,0403 [+0,0313; +0,0492]** | **+0,1296 [+0,1112; +0,1468]** |

In đậm là khoảng tin cậy không chứa 0. Nguồn: `docs/EVAL_RESULTS_2026-10-04.md` §6;
ô P0 · HAM10000: `reports/ci_srcsamp_auprc_ham10000_headline.md:20`.

### 2.3 Kết quả hiện tại chưa tốt ở điểm nào, nguyên nhân, xu hướng cải thiện

**(1) Bỏ sót nhiều ca ác trên ảnh lâm sàng khác nguồn. Đây là điểm yếu chính và là lý do của phán quyết KHÔNG ĐẠT.**

- *Biểu hiện:* tại ngưỡng app, độ nhạy trên Fitzpatrick17k-C chỉ 0,50–0,60 tuỳ tông da, trong khi mốc là 0,80. Cận
  trên tốt nhất (0,634) vẫn cách mốc khoảng 0,17. Trên ảnh PAD (cùng nguồn với dữ liệu train), mô hình đạt 0,873.
- *Nguyên nhân:*
  - **Không phải do chọn ngưỡng, ít nhất với tông sáng và tông trung bình.** Kể cả khi chọn ngưỡng tốt nhất riêng cho
    từng tông trên chính tập test (cách chọn lạc quan), ở độ đặc hiệu 0,60 độ nhạy cũng chỉ đạt 0,69–0,74
    (Fitzpatrick17k-C, fold 4). Với tông tối, khoảng tin cậy kéo tới 0,820 nên chưa khẳng định được.
  - **Giả thuyết hiện tại là lệch miền ảnh.** Dữ liệu train gồm ảnh ISIC (cắt từ ảnh chụp toàn thân 3D), ảnh điện
    thoại PAD và 656 ảnh DDI. Fitzpatrick17k thì là ảnh atlas trên web. Đây là suy luận, chưa được kiểm bằng một phép
    thử riêng.
  - **Một phần do nhãn và độ phủ chẩn đoán khác nhau giữa các bộ dữ liệu.** Độ nhạy thấp nhất rơi vào ba chẩn đoán:
    mycosis fungoides (0,299), kaposi sarcoma (0,323) và actinic keratosis (0,360).
    - Actinic keratosis được Fitzpatrick17k xếp vào nhóm ác, nhưng PAD-UFES-20 (dữ liệu train) gán nhãn **lành**.
      Đây là lệch nhãn thật.
    - Mycosis fungoides và kaposi sarcoma có nhãn ác trong train, nhưng train chỉ có 38 ảnh của hai chẩn đoán này
      (từ DDI), tức là thiếu dữ liệu.
    - Bỏ riêng actinic keratosis, độ nhạy chỉ tăng lên 0,624 / 0,521 / 0,516. Bỏ cả ba chẩn đoán thì lên 0,660 /
      0,585 / 0,582, vẫn dưới 0,80. Vậy đây chỉ là một phần nguyên nhân.
    - Phân tích này dùng chính tập Fitzpatrick, nên hướng nào chọn dựa trên nó đều phải khai là post-hoc.
  - Đổi teacher hoặc đổi student (vòng 2) không đóng được khoảng hụt: P1 và P2 cũng trượt ở cùng chỗ (Bảng 3).
- *Xu hướng cải thiện:* ngoài KD (Bảng 4), hai can thiệp dữ liệu dưới đây cho cải thiện có ý nghĩa ngoài miền
  (ΔAUPRC của student có KD, TB 5 fold, khoảng tin cậy ghép cặp):

  | Can thiệp | HAM10000 | Fitzpatrick17k | Ảnh PAD |
  |---|---|---|---|
  | Thêm 656 ảnh DDI | **+0,0863 [+0,0737; +0,0979]** | **+0,0400 [+0,0332; +0,0467]** | — |
  | Lấy mẫu phân tầng theo nguồn (trên nền đã có DDI) | **+0,0140 [+0,0049; +0,0233]** | **+0,0328 [+0,0262; +0,0391]** | **+0,0563 [+0,0391; +0,0748]** |
  | Tăng cường ảnh theo miền (một preset) | kém đi có ý nghĩa ở cả 5/5 ô ngoài miền ⇒ đã gỡ | | |

  Riêng việc thêm DDI đã nâng AUPRC của student có KD trên Fitzpatrick từ 0,6223 lên 0,6624, và trên HAM10000 từ
  0,3967 lên 0,4829. Trong các thử nghiệm đã làm, thêm ảnh thật đa dạng (656 ảnh DDI) có ích, còn preset tăng cường
  ảnh theo miền thì không. Đây là kết quả trên một bộ dữ liệu bổ sung và một preset, chưa đủ để khái quát. Các hướng
  ứng viên là bổ sung ảnh lâm sàng/điện thoại thật có nhãn sinh thiết (đề xuất hợp tác với bệnh viện) và huấn luyện
  lại teacher cùng công thức. Hướng cụ thể chưa được chọn.

**(2) Chênh lệch giữa các nhóm tông da.**

- *Biểu hiện:*
  - Tại ngưỡng app (Fitzpatrick headline, fold 4), độ nhạy tông sáng cao hơn tông trung bình +0,084 [+0,039; +0,127]
    và cao hơn tông tối +0,080 [+0,004; +0,154].
  - Độ đặc hiệu không có cặp tông nào chênh có ý nghĩa.
  - Về khả năng xếp hạng (TB 5 fold), AUC tông sáng cao hơn tông trung bình +0,0409 [+0,0119; +0,0708].
- *Nguyên nhân:* chưa xác định được bằng thí nghiệm. Tông tối có ít mẫu (208 ca ác ở bản headline, 130 ở
  Fitzpatrick17k-C) nên khoảng tin cậy rộng. Chưa khẳng định được tông tối kém hơn tông trung bình.
- *Xu hướng:* thêm DDI cải thiện AUPRC của student có KD có ý nghĩa ở **cả ba** nhóm tông: tối +0,0473
  [+0,0276; +0,0672], trung bình +0,0381, sáng +0,0399. Tức là cả ba nhóm cùng được nâng lên; chưa kiểm khoảng
  cách giữa các tông có thu hẹp hay không.

**(3) Lợi ích của KD trên ảnh điện thoại chưa được chứng minh.**

- *Biểu hiện:*
  - Với P0, có KD so với không KD trên ảnh PAD: −0,0008 [−0,0199; +0,0187] (Bảng 4), không phân biệt được.
  - Khoảng "student hơn teacher" +0,0619 trên PAD nhiều khả năng đến từ bộ lấy mẫu theo nguồn (+0,0563) và cách
    chọn checkpoint (+0,0023), không phải từ KD.
  - Khi cùng công thức huấn luyện, KD − teacher trên PAD chỉ +0,0032 [−0,0169; +0,0251].
  - Đây là suy luận ghép hai phép đo: các điểm ước lượng cộng lại đúng +0,0619, còn các khoảng tin cậy thì không
    cộng được.
- *Nguyên nhân:* teacher hiện được train **không** có bộ lấy mẫu theo nguồn nên yếu hơn trên PAD. Phép so student
  − teacher vì thế chưa cùng công thức.
- *Điểm tích cực:* KD giúp có ý nghĩa ở ngoài miền (Fitzpatrick +0,04 ở cả ba cặp; HAM10000 từ +0,06 đến +0,13) và
  ở phần ảnh ISIC. Việc nên làm là huấn luyện lại teacher cùng công thức (giai đoạn 10b của đề cương).

**(4) Phép đo phía điện thoại chưa đủ.** Chưa đo độ trễ p95 trên đúng file của P0, và chưa đo pipeline camera thật
của app (chụp → cắt → thu nhỏ). Rủi ro cụ thể đã biết: theo spec, app thu nhỏ ảnh bằng bilinear, trong khi lúc train
dùng LANCZOS.

**(5) Kết quả hiện mang tính khám phá.**

- Các mốc được chốt sau khi đã thấy kết quả.
- Tập test PAD/HAM/Fitzpatrick đã được mở ít nhất 18 lần. Danh sách ở `reports/2026-10-04_test_set_openings.md`
  chỉ ghi tới trưa 04/10; phân tích theo chẩn đoán chiều 04/10 chưa được thêm vào.
- Ngưỡng app được chọn sau khi đã xem test.
- Muốn có kết luận xác nhận, cần một tập mới chưa từng mở và chỉ chạy một lần.

### 2.4 Các kết quả đã đạt được

1. **Mô hình nhỏ đã chạy trên điện thoại thật và cho kết quả trùng máy chủ.** MobileNetV4 (~32 MiB, 1,653 GFLOPs)
   được xuất sang ExecuTorch và chạy trên Pixel 6a. Metric trùng máy chủ tới 4 chữ số thập phân trên 70.883 ảnh (mục
   2.5).
2. **Đạt mốc (tạm) trên ảnh chụp bằng điện thoại cùng nguồn.** Tại ngưỡng app, trên ảnh PAD, độ nhạy là 0,873 và
   độ đặc hiệu là 0,731; cả hai cận dưới đều vượt mốc tạm 0,80 / 0,60. Kết quả này mang tính khám phá, vì mốc và
   ngưỡng được chọn sau khi đã xem test.
3. **Student không kém teacher quá δ trên cả ba miền** (PAD, Fitzpatrick, HAM10000), dù student là mô hình di động
   nhỏ hơn teacher. Cần lưu ý:
   - Mốc là mốc tạm; δ được chốt sau khi đã thấy số, và mọi δ > 0,0068 đều cho P0 qua.
   - Teacher chưa được huấn luyện cùng công thức, nên phép so này dễ đạt hơn thực tế (mục 2.3, điểm 3).
4. **Trên ISIC 2024, khả năng xếp hạng ở quanh mức tham chiếu** của biến thể chỉ dùng ảnh: AUC 0,9437, pAUC 0,1580,
   so với tham chiếu 0,922 / 0,142.
   - Cận dưới khoảng tin cậy xấp xỉ mốc: nhãn đổi theo seed bootstrap, và bootstrap theo bệnh nhân cho cận dưới
     AUC 0,9204 < 0,922.
   - Tham chiếu đo trên tập test của cuộc thi, không phải phần ISIC của bộ chia v2.
   - Hàm pAUC của dự án đã được đối chiếu khớp với hàm chấm chính thức ISIC 2024 (chênh tối đa 2,8e-17).
5. **Tìm được hai can thiệp dữ liệu có ích, có bằng chứng thống kê:** bổ sung DDI và lấy mẫu phân tầng theo nguồn
   (mục 2.3). Đồng thời loại được một hướng không hiệu quả (preset tăng cường ảnh theo miền).
6. **Nền tảng phương pháp chặt chẽ hơn:**
   - Đã phát hiện và sửa rò rỉ bệnh nhân.
   - Mọi so sánh dùng bootstrap ghép cặp thay vì đếm số lần thắng.
   - Vòng chọn thứ hai có luật chọn được đăng ký trước khi mở kết quả test của vòng đó.
   - Có bộ tiêu chí đánh giá đo tại đúng ngưỡng quyết định của app.
7. **Cấu hình mô hình cho ứng dụng đã có.** App dùng chế độ hiển thị nhị phân: chỉ đưa ra kết luận, không hiển thị
   xác suất. Ngưỡng được sinh tự động bằng script từ tập val thay vì nhập tay. Phần ứng dụng Android vẫn đang phát
   triển.

### 2.5 Khả năng của mô hình trên server và trên điện thoại có khác nhau nhiều không?

**Không. Về chất lượng dự đoán, điện thoại và máy chủ cho kết quả trùng nhau.** Phép so dùng cùng checkpoint P0 và
cùng 70.883 ảnh (59.093 trong miền, 7.470 HAM10000, 4.320 Fitzpatrick17k). Máy chủ chạy bằng PyTorch; Pixel 6a chạy
bằng ExecuTorch (XNNPACK, 4 luồng).

**Bảng 5. Máy chủ so với điện thoại — mô hình P0, fold 4 (các metric không phụ thuộc ngưỡng)**

| Tập | Metric | Máy chủ | Điện thoại | Chênh |
|---|---|---|---|---|
| Trong miền (ISIC + PAD) | AUPRC · AUC · pAUC@TPR80 | 0,6588 · 0,9828 · 0,1837 | 0,6588 · 0,9828 · 0,1837 | 0,0000 |
| HAM10000 | AUPRC · AUC · pAUC@TPR80 | 0,5793 · 0,8807 · 0,1276 | 0,5793 · 0,8807 · 0,1276 | 0,0000 |
| Fitzpatrick17k | AUPRC · AUC · pAUC@TPR80 | 0,7246 · 0,7315 · 0,0617 | 0,7246 · 0,7315 · 0,0617 | 0,0000 |

Hàng "Trong miền" là số gộp ISIC + PAD, chỉ dùng để so điện thoại với máy chủ. Không đọc AUC 0,98 là độ mạnh của
mô hình; số theo từng miền ở Bảng 2. Cũng không so AUPRC giữa các hàng, vì tỉ lệ ca ác của mỗi tập khác nhau.

| Kiểm tra ở mức logit | Kết quả |
|---|---|
| Chênh logit tối đa trên 70.883 ảnh | 5,245e-06 (0 ảnh vượt 1e-3) |
| Ảnh lỗi | 0/70.883 |
| Chạy lại 500 ảnh | trùng bit |
| 4 luồng so với 1 luồng (100 ảnh) | trùng bit |
| Giải mã JPEG trên Android so với đầu vào nhị phân (100 ảnh) | PASS |

| Tốc độ / bộ nhớ trên Pixel 6a, theo kiến trúc MobileNetV4 (đo 27/08 trên file `.pte` cũ cùng kiến trúc) | Giá trị |
|---|---|
| Độ trễ ổn định: phút cuối của 5 phút chạy liên tục, đã tính điều tiết nhiệt | 39,5 ms/ảnh |
| Tốt nhất (máy nguội) · khởi động lạnh | 21,6 ms · 69,3 ms |
| Bộ nhớ đỉnh (khoảng của 16 mô hình đã đo) | 208–257 MiB |

Kết luận cho câu hỏi này:

- **Chuyển sang điện thoại không làm thay đổi chất lượng.** Quá trình chuyển gồm export ExecuTorch, phần cứng ARM và
  bộ giải mã ảnh Android. Sai khác lớn nhất trên logit là 5,2e-06. Độ nhạy và độ đặc hiệu tại ngưỡng đối chiếu trùng
  tới 4 chữ số. Số ảnh bị đổi quyết định tại ngưỡng app chưa được đếm trực tiếp.
- **Tốc độ có vẻ đủ nhưng chưa chốt.** Độ trễ theo kiến trúc (~40 ms/ảnh khi máy đã nóng) nằm dưới mốc đề xuất
  80 ms. Tuy nhiên **p95 trên đúng file của P0 chưa đo**, nên chưa kết luận chính thức cho trụ I.
- **Khoảng cách lớn thật sự nằm giữa các loại ảnh, không nằm giữa máy chủ và điện thoại.** Cùng một mô hình bắt 87%
  ca ác trên ảnh điện thoại PAD, nhưng chỉ 50–60% trên ảnh lâm sàng Fitzpatrick (mục 2.3).
- **Ảnh chụp thật qua camera của app chưa được đo.** Phép đo trên điện thoại ở đây dùng ảnh đã tiền xử lý sẵn
  224×224. Vì vậy vẫn còn một nguồn sai khác có thể xuất hiện ở khâu thu nhỏ ảnh.

Nguồn: `reports/2026-10-01_pixel6a_srcsamp_vs_mobile.md` §1;
`reports/mobile_eval_pixel6a_20261001/mobilenetv4_srcsamp_auprc_fold4/table.md`; repo `SkinDetector-eval`
`eval-results/2026-10-01-pixel6a-srcsamp/scored/vs_server/comparison.md`; độ trễ: `reports/ondevice_latency.csv:22`.

---

## 3. Việc tiếp theo và các điểm cần GVHD cho ý kiến

| # | Việc | Cần |
|---|---|---|
| 1 | Chốt chính thức các mốc: độ nhạy tối thiểu 0,80, độ đặc hiệu tối thiểu 0,60, và δ. Lập luận từ bài toán sàng lọc (chi phí bỏ sót so với báo nhầm), độc lập với số đo hiện có | Ý kiến GVHD |
| 2 | Chọn hướng thu hẹp khoảng hụt trên ảnh lâm sàng khác nguồn: dữ liệu thật mới, teacher cùng công thức | Ý kiến GVHD |
| 3 | Thu tập xác nhận mới qua bệnh viện (nhãn sinh thiết, duyệt đạo đức; ~287 ca ác + 130 ca lành theo giả định ở mục 1.2) | Hỗ trợ kết nối từ GVHD |
| 4 | Có mở rộng phạm vi sang so sánh với INT8 / label smoothing không, hay ghi thành hạn chế | Ý kiến GVHD |
| 5 | Đo p95 trên file `.pte` của P0 và đo pipeline camera thật của app | Học viên tự làm |
| 6 | Viết lại luận văn theo hai câu hỏi trung tâm và kết quả trên bộ chia mới (27 mục đã ghi chú) | Học viên tự làm, sau khi có (1) và (2) |

---

## Phụ lục A — Cổng chấp nhận (chép từ báo cáo phán quyết)

### Cổng chấp nhận (theo .claude/skills/eval-results/reference/acceptance-gates.md, khung 3 trụ — bản trên nhánh `docs/tracker-cleanup-and-ddi`)

- **Model được chấm:** `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`
  · fold 4 (trụ I, II, III) / CI 5 fold (student − teacher) · `best_model_auprc.pth` · splits v2.
- **Trạng thái mốc:**
  - Độ nhạy tối thiểu 0,80, độ đặc hiệu tối thiểu 0,60, δ = 5% AUPRC teacher: chốt tạm 04/10/2026, post-hoc với P0.
  - Độ trễ, tương đương điện thoại–máy chủ, độ ổn định, pipeline camera: còn ở mức đề xuất.
- **Bảng cổng:** Bảng 1 (mục 2.2); nguồn từng dòng ở cột "Nguồn" của
  `reports/2026-10-04_acceptance_verdict_P0_3pillar.md`.
- **Hành vi tại ngưỡng app 0,5705 (fold 4):**
  - PAD: độ nhạy 0,873, độ đặc hiệu 0,731 (56/208 ảnh lành bị gắn cờ).
  - Fitzpatrick: độ nhạy 0,567, độ đặc hiệu 0,769.
  - ISIC: bắt 5/76 ca ác (ảnh ISIC không phải đầu vào của app).
  - Đối chiếu với ngưỡng toàn cục 0,2272: 207/208 ảnh PAD lành bị gắn cờ.
- **Ứng viên định trước?** Có ở vòng 2: P0 được chọn lại bằng val theo luật đăng ký trước. Nhưng mọi mốc và quy tắc
  ngưỡng được chốt sau khi đã xem test của P0, nên là post-hoc. Các khai báo kèm theo:
  - Đây là vòng chọn thứ hai: mọi tập kiểm đã được nhìn qua ứng viên thứ nhất.
  - Hai cặp P1/P2 được chọn có tham khảo số HAM/Fitzpatrick của splits v1.
  - Một dòng metric test trong miền của P1 fold 4 đã bị thấy trước khi chọn. Luật chọn chỉ đọc val, nên dòng đó
    không vào phép chọn.
  - Tập chấm III-b đổi sang Fitzpatrick17k-C sau khi đã thấy kết quả; nhãn của P0 không đổi.
- **Phán quyết tổng: KHÔNG ĐẠT YÊU CẦU (tạm, khám phá)** vì III-b trượt ở cả ba tông. Trụ I và tỉ lệ đổi quyết định
  qua pipeline camera chưa đo, nhưng dù đạt cũng không đổi được kết luận.
- **Còn thiếu để đo đủ:** độ trễ p95 trên đúng file `.pte` của P0; tỉ lệ đổi quyết định qua pipeline camera của app.

## Phụ lục B — Nguồn số liệu và giới hạn

**Nguồn số liệu**

- Phán quyết: `reports/2026-10-04_acceptance_verdict_P0_3pillar.md`. Bảng số tổng hợp ngày 04/10:
  `docs/EVAL_RESULTS_2026-10-04.md` (chưa commit).
- Can thiệp DDI: `reports/ci_ddi_ham10000_headline.md`, `reports/ci_ddi_fitzpatrick17k_headline.md`. Lấy mẫu theo
  nguồn: `reports/2026-10-01_srcsamp_item2_3.md`. Tăng cường theo miền: `docs/domain_aug_plan.md`.
- Kế hoạch theo giai đoạn: `docs/DE_CUONG.md` Bảng 5–6.

**Lưu ý về nhánh git.** Các file `reports/2026-10-04_*`, bản `docs/PROGRESS.md` cập nhật 04/10,
`thesis/CAN_SUA_SAU.md` và khung 3 trụ trong `acceptance-gates.md` hiện chỉ có trên nhánh
`docs/tracker-cleanup-and-ddi`, chưa merge vào `develop`. Trên `develop`, `acceptance-gates.md` và
`docs/PROGRESS.md` vẫn ghi luật cũ, với phán quyết CHƯA CÓ TIÊU CHÍ CHỐT (02/10). Cần merge nhánh đó trước khi gửi
link các file nguồn.

**Chưa verify được trên Mac**

- Mọi số ngày 04/10 được tính trên server: Bảng 1, 3, 4, chênh theo tông, phân tích theo chẩn đoán, KD − teacher
  cùng công thức, ngưỡng tốt nhất theo tông, cỡ mẫu. Bootstrap không chạy lại được trên Mac.
- Số đo trên điện thoại được đọc lại từ kết quả đã kéo về (Pixel 6a, 01/10). Số ảnh đổi quyết định tại ngưỡng app
  chưa được đếm.
- Độ trễ là số chép tay (27/08) của một file `.pte` khác, cùng kiến trúc.
- Mốc Kurtansky và Cochrane, cùng hàm chấm pAUC chính thức của ISIC 2024, chỉ được đối chiếu qua web; lượt kiểm chéo
  không kiểm lại được.
- Khoảng Wilson giả định các ảnh độc lập. Fitzpatrick không có mã bệnh nhân; danh sách ảnh Fitzpatrick17k-C chưa được
  ghim theo commit của nguồn gốc.
- Trạng thái app Android chỉ dựa trên unit test (02/10); test instrumented và giao diện chưa chạy.
- Trạng thái "không còn job trên server" là ảnh chụp ngày 04/10.
