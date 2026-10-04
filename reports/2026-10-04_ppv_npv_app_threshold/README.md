# R11 — PPV / NPV tại ngưỡng app, ở prevalence giả định (chỉ báo cáo)

Việc R11 trong `docs/PROGRESS.md`. Ứng viên P0 (`kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`,
`best_model_auprc.pth`, fold 4), ngưỡng app `pad_sens90` = 0,5705, hàng PAD của test in-domain.
Nguồn số: dòng `4,pad_sens90` của `reports/2026-10-02_threshold_options/summary.csv`. Tính lại:
`python3 reports/2026-10-04_ppv_npv_app_threshold/ppv_npv.py` (chỉ thư viện chuẩn).

**Vì sao không đo PPV thẳng trên test:** ảnh PAD trong test có 189/397 ca ác (~48%), xa mọi tỉ lệ ác tính thực tế
của một app sàng lọc. PPV phụ thuộc prevalence nên đo trực tiếp ở đây là số ảo; ta giữ độ nhạy/độ đặc hiệu đã đo
và đổi prevalence bằng công thức Bayes.

| | |
|---|---|
| Độ nhạy (PAD test) | 165/189 = 0,873 — Wilson 95% [0,818; 0,913] |
| Độ đặc hiệu (PAD test) | 152/208 = 0,731 — Wilson 95% [0,667; 0,786] |

| Prevalence (giả định) | PPV | khoảng PPV | NPV | khoảng NPV | số ca bị app báo "nên đi khám" / 1000 ảnh | trong đó thật sự ác |
|---|---|---|---|---|---|---|
| 1% | 0,032 | [0,024; 0,041] | 0,9982 | [0,9973; 0,9989] | 275 | 8,7 |
| 5% | 0,146 | [0,114; 0,184] | 0,9909 | [0,9858; 0,9942] | 299 | 43,7 |

Đọc: ở prevalence 1%, cứ ~31 ảnh bị báo "nên đi khám" thì 1 ảnh là ác (PPV 3,2%); ở 5%, ~1/7. Trong số các kết quả
"không đáng lo", tỉ lệ thật ra là ác (1 − NPV) là ~1,8‰ (1%) đến ~9,1‰ (5%); tính trên 1.000 ảnh bất kỳ thì là ~1,3
(1%) đến ~6,3 (5%) ca ác bị bỏ sót.

**Giới hạn — đọc trước khi trích:**
- Prevalence 1% và 5% là **giả định minh hoạ**, không đo; chưa có nguồn cho tỉ lệ ác tính của người dùng app.
- "Khoảng" ghép hai đầu Wilson của độ nhạy và độ đặc hiệu (PPV/NPV đơn điệu theo cả hai) ⇒ **bảo thủ, không phải
  CI 95% đồng thời**, và bỏ qua sai số của chính prevalence.
- Độ nhạy/độ đặc hiệu lấy từ **một** fold (fold ship), trên ảnh PAD. Test PAD fold 4 đã được xem nhiều lần và
  quy tắc `pad_sens90` chọn sau khi xem (post-hoc — `reports/2026-10-02_threshold_options/README.md` mục giới hạn).
- Chỉ áp cho ảnh kiểu PAD. Trên ảnh lâm sàng khác nguồn (Fitzpatrick) độ nhạy tại cùng ngưỡng thấp hơn nhiều
  (0,567 fold 4), nên PPV/NPV ở đó sẽ kém hơn bảng này.
- App chỉ hiển thị nhị phân (`displayMode: "binary"`) ⇒ các số này **không** hiển thị cho người dùng; chúng dành
  cho phần thảo luận an toàn trong luận văn.
