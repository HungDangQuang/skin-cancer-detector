# Kiểm tra theo review luận văn ThesisForge (bản gửi GVHD 20/09) — 03/10/2026

Review: `docs/review_luan_van_grad_thesisforge.pdf`. Ứng viên được kiểm: P0 =
`experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`, checkpoint AUPRC.
Đã có từ trước: sens@90spec theo tông (`reports/ci_gates_srcsamp_fitzpatrick17k_headline.md` §4) và số theo tông tại ngưỡng Youden toàn cục 0,2272 (suy biến: độ nhạy ≈ 1, độ đặc hiệu ≈ 0). Hai script trong thư mục này chỉ dùng thư viện chuẩn Python, không gọi hàm metric của repo; chạy từ gốc repo.

## 1. Bootstrap theo bệnh nhân có cần không? (review Issue 1)

Tập test in-domain v2 có nhiều ảnh cho mỗi bệnh nhân:
- ISIC: 58.696 ảnh từ 161 bệnh nhân (một người có tới 2.803 ảnh).
- PAD: 397 ảnh từ 238 bệnh nhân.

`scripts/bootstrap_ci.py` resample theo **ảnh**. Script `cluster_bootstrap.py` so cách đó với resample theo **bệnh nhân**. Thống kê là trung bình 5 fold, theo đúng quy ước của repo. Đường cong ROC được tính lại trong mỗi lần resample. Trước khi chạy, script kiểm tra `predictions_auprc.csv` khớp từng dòng với `data/splits/isic2024/test_split.csv` (nhãn và nguồn, cả 5 fold).

| Nguồn (B) | Metric | Điểm | CI theo ảnh | CI theo bệnh nhân | Độ rộng CI thay đổi |
|---|---|---|---|---|---|
| PAD (1000) | AUC | 0,8779 | [0,8431, 0,9093] | [0,8397, 0,9093] | +5% |
| PAD (1000) | độ nhạy @ đặc hiệu 80% | 0,8180 | [0,7259, 0,8794] | [0,7264, 0,8817] | +1% |
| ISIC (1000) | AUC | 0,9437 | [0,9234, 0,9610] | [0,9204, 0,9642] | +17% |
| ISIC (1000) | độ nhạy @ đặc hiệu 80% | 0,9289 | [0,8784, 0,9676] | [0,8822, 0,9697] | −2% |

Điểm ước lượng trùng với `reports/ci_gates_srcsamp_indomain.md`. Cận dưới CI tính theo ảnh lệch so với báo cáo đó tới ~0,015, vì khác bộ sinh số ngẫu nhiên và B = 1000 thay vì 2000.

**Đọc kết quả:**
- **PAD (ảnh điện thoại):** trên hai metric đã đo, gom theo bệnh nhân gần như không đổi CI (chênh +1–5% nằm cỡ nhiễu Monte Carlo ở B = 1000), phù hợp với ~1,7 ảnh mỗi người. Với cổng B2 thì không cần làm lại. Các hiệu ghép cặp trên PAD (student − teacher, KD − baseline) **chưa đo** theo cách này; dự đoán là cũng ít đổi, nhưng đó là suy luận.
- **ISIC:** CI của AUC rộng thêm ~17%. Cận dưới (0,9204) xuống dưới mốc 0,922 ⇒ **ô AUC của B1 lật** từ ĐẠT sang CHƯA CHỨNG MINH. Cả cổng B1 vốn đã CHƯA CHỨNG MINH vì ô pAUC, nên phán quyết không đổi. 76 ca dương ISIC chỉ đến từ 45 bệnh nhân ⇒ AUPRC/pAUC trên ISIC có thể rộng thêm nhiều hơn AUC (chưa đo).
- Kết luận: với ảnh điện thoại (PAD) thì không cần sửa `bootstrap_ci.py`. Mọi khẳng định về ISIC nên kèm câu hạn chế này; nếu luận văn dựa vào CI trên ISIC thì nên thêm tuỳ chọn resample theo bệnh nhân.
- HAM10000 headline có một ảnh mỗi tổn thương. Fitzpatrick17k không có mã bệnh nhân.

**Giới hạn:** một run, hai metric. AUPRC, pAUC và các hiệu ghép cặp chưa được tính theo cách này.

## 2. Độ nhạy / độ đặc hiệu theo tông da tại ngưỡng app (review Issue 6)

Script: `tone_at_app_threshold.py`. Ngưỡng `pad_sens90` của từng fold lấy từ `reports/2026-10-02_threshold_options/summary.csv`. Tập: Fitzpatrick17k headline.

| Tông | Fold 4 (model ship): độ nhạy [Wilson 95%] | Fold 4: độ đặc hiệu | Cộng 5 fold: độ nhạy / độ đặc hiệu |
|---|---|---|---|
| sáng | 722/1195 = 0,604 [0,576, 0,632] | 842/1115 = 0,755 [0,729, 0,779] | 0,712 / 0,593 |
| trung bình | 394/757 = 0,520 [0,485, 0,556] | 656/842 = 0,779 [0,750, 0,806] | 0,657 / 0,584 |
| tối | 109/208 = 0,524 [0,456, 0,591] | 164/203 = 0,808 [0,748, 0,856] | 0,699 / 0,597 |

Tổng cả ba tông ở fold 4 là 1.225/2.160 = 0,567 (độ nhạy) và 0,769 (độ đặc hiệu), khớp `threshold_options`.

**Đọc kết quả:**
- Ở fold 4 (model ship), tại ngưỡng app, model bỏ sót 40–48% ca ác tính trên ảnh lâm sàng khác nguồn, ở cả ba tông. Cộng 5 fold thì bỏ sót 29–34% nhưng độ đặc hiệu chỉ ~0,59 (ngưỡng các fold khác cho đánh đổi khác).
- Ở fold 4, tông trung bình và tông tối thấp hơn tông sáng ~0,08 độ nhạy; CI tông sáng không chồng CI tông trung bình. Cộng 5 fold thì chỉ tông trung bình còn thấp (0,657); tông tối (0,699) ≈ tông sáng (0,712). ⇒ không kết luận "da tối kém hơn" từ bảng này.
- **Giới hạn:**
  - Đây là số của một fold.
  - Wilson CI coi các ảnh là độc lập.
  - Ngưỡng chọn post-hoc.
  - Fitzpatrick đã được nhìn nhiều lần, nên chỉ dùng để báo cáo, không dùng làm cổng (viết trước khung 3 trụ; từ 03/10 Fitzpatrick tại ngưỡng app là cổng III-b, và với ứng viên này là post-hoc).

## 3. Label smoothing đã từng chạy chưa? (review Issue 4)

**Chưa từng chạy thành thí nghiệm:**
- Template khởi tạo (commit `1dc99f5`, 13/04) có `label_smoothing: 0.1` cho cross-entropy 7 lớp. Tham số này bị bỏ khi chuyển sang bài toán nhị phân (commit `de596e3`, 21/04).
- Ngày 21/06, khi bàn các đòn bẩy chống overfit, tác giả từ chối label smoothing (memory `project_overfitting_levers`).
- Luận văn viết "KD = làm mượt nhãn thích ứng theo từng mẫu" (`thesis/LUAN_VAN.md:888-896`). Đó là lập luận cơ chế, không phải kết quả đo.
- Hiện không có dòng code, config hay run-dir nào về label smoothing.
