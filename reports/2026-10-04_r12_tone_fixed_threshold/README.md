# R12 — Công bằng theo tông da tại ngưỡng app cố định, có CI (chỉ báo cáo)

Việc R12 trong `docs/PROGRESS.md` (review luận văn ThesisForge Issue 6, Fix 1–2). P0
(`kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`, `best_model_auprc.pth`), **fold 4** (fold ship),
Fitzpatrick17k headline, ngưỡng app `pad_sens90` = 0,5705. Tính lại:
`python3 reports/2026-10-04_r12_tone_fixed_threshold/tone_ci.py` (chỉ thư viện chuẩn; tham số tuỳ chọn
`FITZ_DIR SUMMARY_CSV SHIP_FOLD [B] [SEED]` cho ứng viên khác). Kết quả đầy đủ: `output.md`.

**Cách tính:** bootstrap theo dòng, B = 2000, seed 42. Mỗi replicate lấy lại toàn bộ 4.320 ảnh một lần và chấm cả ba
tông trên cùng replicate ⇒ chênh giữa hai tông tính trên cùng mẫu. Khoảng phân vị 95%. sens@95spec theo đúng quy tắc
của `src/evaluation/metrics.py::sensitivity_at_specificity`; đối chiếu trên server với hàm đó, điểm ước lượng khớp tới
6 chữ số (sáng 0,248536 · trung bình 0,208719 · tối 0,288462).

| Tông | n ác / n lành | Độ nhạy tại ngưỡng | Độ đặc hiệu tại ngưỡng | sens@95spec |
|---|---|---|---|---|
| sáng | 1195 / 1115 | 0,604 [0,576; 0,631] | 0,755 [0,730; 0,778] | 0,249 [0,204; 0,295] |
| trung bình | 757 / 842 | 0,520 [0,484; 0,556] | 0,779 [0,751; 0,806] | 0,209 [0,156; 0,262] |
| tối | 208 / 203 | 0,524 [0,455; 0,593] | 0,808 [0,750; 0,860] | 0,288 [0,208; 0,380] |

| Chênh (A − B) | Độ nhạy tại ngưỡng | Độ đặc hiệu tại ngưỡng | sens@95spec |
|---|---|---|---|
| sáng − trung bình | **+0,084 [+0,039; +0,127]** | −0,024 [−0,062; +0,010] | +0,040 [−0,027; +0,116] |
| sáng − tối | **+0,080 [+0,004; +0,154]** | −0,053 [−0,110; +0,009] | −0,040 [−0,138; +0,059] |
| trung bình − tối | −0,004 [−0,082; +0,073] | −0,029 [−0,089; +0,030] | −0,080 [−0,191; +0,015] |

In đậm = khoảng loại trừ 0.

**Đọc kết quả:**
- Tại ngưỡng app, tỉ lệ bỏ sót ca ác ở tông **trung bình** và **tối** cao hơn tông sáng khoảng 8 điểm phần trăm, khác 0
  có ý nghĩa (cận dưới của chênh sáng − tối chỉ +0,004, sát 0). Trung bình và tối không phân biệt được.
- Độ đặc hiệu theo chiều ngược lại (tông sáng gắn cờ nhầm nhiều hơn một chút), nhưng mọi khoảng đều chứa 0.
- Ở sens@95spec (không phụ thuộc ngưỡng app), không cặp nào loại trừ 0, nhưng các khoảng rộng (sáng − tối −0,040
  [−0,138; +0,059]) nên **không** suy ra các tông được xếp hạng như nhau. Bảng này không tách được phần chênh do vị trí
  ngưỡng với phần do khả năng xếp hạng. Đối chiếu: trung bình 5 fold, sáng − trung bình khác 0 có ý nghĩa ở cả AUC
  (+0,0409 [+0,0119; +0,0708]) lẫn sens@80spec (+0,0734 [+0,0247; +0,1258]), còn tối − sáng chứa 0
  (`reports/ci_gates_srcsamp_fitzpatrick17k_headline.md` §4).
- Chỉ là fold 4: cộng số đếm 5 fold (mỗi fold dùng ngưỡng `pad_sens90` của nó) thì độ nhạy tông tối 0,699 ≈ tông sáng
  0,712, chỉ tông trung bình thấp (0,657) — `reports/2026-10-03_thesis_review_checks/README.md:46`. Không kết luận
  "da tối kém hơn".
- Cả ba tông vẫn trượt III-b (cận trên độ nhạy < 0,80; headline — trên Fitzpatrick17k-C, tập chấm III-b từ 04/10, cũng vậy:
  `reports/2026-10-04_review_v2_checks/output.md` (1)) — bảng này không đổi phán quyết
  (`reports/2026-10-04_acceptance_verdict_P0_3pillar.md`).

**Giới hạn:** một fold (fold ship); ngưỡng `pad_sens90` chọn post-hoc; Fitzpatrick đã được nhìn nhiều lần
(`reports/2026-10-04_test_set_openings.md`) ⇒ chỉ báo cáo. Không có mã bệnh nhân nên coi các ảnh độc lập. Khoảng
phân vị không hiệu chỉnh cho ba phép so sánh.
