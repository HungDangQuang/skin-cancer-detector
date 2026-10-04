# Phán quyết cổng chấp nhận — P0 theo khung 3 trụ, mốc chốt tạm 04/10/2026

> Việc N7 trong `docs/PROGRESS.md`. Hợp đồng: `.claude/skills/eval-results/reference/acceptance-gates.md` §2.1 (khung
> 3 trụ, 03/10/2026) và §3 (từ vựng nhãn). Thay cho `reports/2026-10-02_acceptance_verdict_srcsamp.md` (luật gộp cũ,
> giữ nguyên làm lịch sử).
>
> **Vì sao chấm P0:** vòng chọn thứ hai (P1 = `convnextv2_base → mobilenetv4`, P2 = `efficientnetv2_m → repvit_m1_0`)
> chọn lại **P0, fold 4** theo luật chỉ dùng val đã đăng ký trước — `reports/2026-10-04_candidate2_selection/`
> (val PAD AUPRC: P0 0,8831 · P1 0,8840 · P2 0,8536; P1 hơn P0 0,0009 < biên hoà 0,005 ⇒ giữ cặp đứng trước,
> `docs/PREREG_CANDIDATE2_2026-10-02.md` §4, §7.1). Theo prereg §5 chỉ ứng viên được chọn nhận phán quyết; P1/P2
> chỉ được chấm để báo cáo.
>
> **Mốc:** S_min = 0,80, Sp_min = 0,60 (III-a và III-b), δ của C2 = 0,05 × AUPRC của chính teacher, từng miền — tác
> giả **chốt tạm** 04/10/2026 (`acceptance-gates.md` §1; prereg §10). Chốt tạm được dùng **như đã chốt** để gán nhãn,
> kèm chữ "(tạm)". Với P0 mọi mốc này là **post-hoc** (đã thấy số test PAD, Fitzpatrick, HAM của P0 trước khi chốt)
> ⇒ mọi nhãn bên dưới là **khám phá**, không phải xác nhận.

### Cổng chấp nhận (theo .claude/skills/eval-results/reference/acceptance-gates.md)
Model được chấm: `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp` · fold 4 (I, II, III) / CI 5 fold (C2) · `best_model_auprc.pth` · splits v2
Trạng thái mốc: S_min, Sp_min, δ **chốt tạm 04/10/2026, post-hoc với P0**; I-1, II-1, II-2, II-3 còn **ĐỀ XUẤT** (⚑)

| Cổng | Metric | Mốc | Giá trị [CI 95%] | Nguồn | Nhãn |
|---|---|---|---|---|---|
| I-1 | độ trễ p95 sau 5 phút, Pixel 6a, trên `.pte` ship | ≤ 80 ms ⚑ | chưa đo trên `.pte` ship, chưa có p95 (số tham khảo theo kiến trúc, `.pte` khác: 39,5 ms = cột `sustained_ms`, phút cuối của lượt 300 s) | `reports/ondevice_latency.csv:22` | **CHƯA ĐO** ⚑ |
| II-1 (= A3) | điện thoại ↔ máy chủ | max\|Δlogit\| < 1e-3 · \|ΔAUPRC\| < 0,005 ⚑ | 5,245e-06 · 0,0000 | `reports/2026-10-01_pixel6a_srcsamp_vs_mobile.md` §1 | ĐẠT so với mốc đề xuất ⚑ |
| II-2 (= A4) | parity + không lỗi + tất định | lỗi < 0,1% · trùng bit ⚑ | parity PASS 6,311e-06 · 0/70.883 lỗi · 500/500 trùng bit | như trên; `reports/mobile_benchmark/parity_mobilenetv4_conv_medium__srcsamp_auprc_fold4.json` | ĐẠT so với mốc đề xuất ⚑ |
| II-3 | tỉ lệ đổi quyết định qua pipeline thật của app | < 0,5% ⚑ | chưa đo (L3, cần U5) | — | **CHƯA ĐO** ⚑ |
| III-a | PAD test, tại ngưỡng app `pad_sens90` 0,5705: độ nhạy · độ đặc hiệu | cận dưới ≥ 0,80 · ≥ 0,60 (tạm) | 165/189 = 0,873 [0,818, 0,913] · 152/208 = 0,731 [0,667, 0,786] | `reports/2026-10-02_threshold_options/summary.csv` dòng `4,pad_sens90`; Wilson: `reports/2026-10-04_ppv_npv_app_threshold/` | **ĐẠT (tạm)** |
| III-b | Fitzpatrick17k headline, cùng ngưỡng, từng tông: độ nhạy | cận dưới ≥ 0,80 (tạm) | sáng 722/1195 = 0,604 [0,576, 0,632] · trung bình 394/757 = 0,520 [0,485, 0,556] · tối 109/208 = 0,524 [0,456, 0,591] | `reports/2026-10-03_thesis_review_checks/README.md:38-40` | **KHÔNG ĐẠT (tạm)** — cận **trên** của cả ba tông < 0,80 |
| III-b | … độ đặc hiệu | cận dưới ≥ 0,60 (tạm) | sáng 0,755 [0,729, 0,779] · trung bình 0,779 [0,750, 0,806] · tối 0,808 [0,748, 0,856] | như trên | ĐẠT (tạm) — không đổi nhãn cổng |
| C2 | student − teacher `efficientnetv2_m`, ΔAUPRC, cận dưới > −δ | δ (tạm, không làm tròn khi so): PAD 0,7966 × 0,05 = 0,03983 · Fitz ≈ 0,035 · HAM ≈ 0,025 (`acceptance-gates.md` §1) — mọi cận dưới của P0 ≥ −0,0068 nên làm tròn không đổi nhãn | PAD +0,0619 [+0,0396, +0,0852] · Fitz +0,0068 [−0,0008, +0,0146] · HAM +0,0059 [−0,0068, +0,0189] | `reports/ci_gates_srcsamp_indomain.json` (`explicit_pairs_by_subgroup` → `pad_ufes_20`); `…_fitzpatrick17k_headline.json`, `…_ham10000_headline.json` (`explicit_pairs`) | **ĐẠT (tạm)** — xem lưu ý lệch công thức bên dưới |

**Lưu ý C2 — so sánh không cùng công thức** (`acceptance-gates.md` §2 C; review 03/10 §1.5): teacher `efficientnetv2_m`
train **không** có sampler theo nguồn và chỉ có checkpoint pAUC; student có cả hai. Teacher vì thế yếu hơn trên PAD, nên
phép kiểm không kém **dễ đạt hơn** thực tế. Δ PAD +0,0619 **không** được đọc là "student vượt teacher"; phần nào đến từ
sampler/checkpoint thì đang đo ở R7 (KD không sampler theo nguồn vs cùng teacher, ghép cặp trên PAD). C2 `ĐẠT` cũng không
nói KD có tác dụng (đó là C1, ô PAD chưa chứng minh).

Báo cáo (không quyết định) — giữ nguyên từ `reports/2026-10-02_acceptance_verdict_srcsamp.md:29-37`:
- B1 ISIC: AUC 0,9437 [0,9227, 0,9616] · pAUC 0,1580 [0,1418, 0,1730] — tham chiếu Kurtansky 0,922 / 0,142 (cận dưới AUC
  **trên** mốc 0,0007, cận dưới pAUC **dưới** mốc 0,0002 ⇒ nhãn có thể lật theo seed bootstrap, R6). Bootstrap theo bệnh nhân: cận dưới AUC ISIC 0,9204 < 0,922 (`reports/2026-10-03_thesis_review_checks/README.md:26`).
- sens@spec80 PAD: 0,8180 [0,7406, 0,8786] — tham chiếu Cochrane 0,81 / 0,76 / 0,47 (`acceptance-gates.md` §2.1; 0,81 = đọc dermoscopy, 0,47 = nhìn ảnh thường).
- B3 Fitzpatrick sens@spec80: 0,4946 [0,4699, 0,5178]. B4 HAM sens@spec80: 0,7259 [0,7018, 0,7508].
- C1 (KD − baseline, ΔAUPRC): PAD −0,0008 [−0,0199, +0,0187] (chưa chứng minh) · Fitz +0,0395 [+0,0310, +0,0478].
- C4b (chênh AUC giữa tông): sáng − trung bình +0,0409 [+0,0119, +0,0708] khác 0 có ý nghĩa (hạn chế); hai cặp còn lại chứa 0.
- A2 / C3: 208–257 MiB (theo kiến trúc, 16 model) · 1,653 GFLOPs.
- PPV/NPV tại ngưỡng app ở prevalence giả định 1% / 5%: PPV 0,032 / 0,146 — `reports/2026-10-04_ppv_npv_app_threshold/`.

Hành vi tại ngưỡng app (theo miền), fold 4, `pad_sens90` 0,5705: PAD độ nhạy 0,873 / độ đặc hiệu 0,731 (56/208 ảnh
lành bị gắn cờ); Fitzpatrick độ nhạy 0,567 / độ đặc hiệu 0,769; ISIC bắt 5/76 ca ác (ảnh ISIC không phải đầu vào của
app). Điểm toàn cục 0,2272 để đối chiếu: PAD lành bị gắn cờ 207/208.

Ứng viên định trước? **Có** ở vòng 2: P0 chọn lại bằng val theo luật đăng ký trước. **Nhưng** mọi mốc (khung 3 trụ,
S_min, Sp_min, δ) và quy tắc ngưỡng `pad_sens90` được chốt sau khi đã xem test PAD/Fitzpatrick/HAM của P0 ⇒ post-hoc.
Khai thêm cho vòng 2: đây là vòng chọn **thứ hai** — mọi tập kiểm đã được nhìn qua ứng viên thứ nhất (prereg §1;
`acceptance-gates.md` §4 #18); lượt chạy thử `select_candidate.py` ngày 03/10 đã cho thấy P0 xếp trên P2 ở val PAD (chỉ val); hai cặp P1/P2 được chọn có tham khảo số HAM/Fitz của **splits v1** (prereg §7.4); và lúc ~00:25 UTC
04/10, trước N1, assistant đã thấy một dòng metric test tổng in-domain của P1 fold 4 qua `tail` log (prereg §10). Luật
chọn chỉ đọc val nên dòng đó không vào phép chọn. Danh sách mọi lần mở test: `reports/2026-10-04_test_set_openings.md`.

**Phán quyết tổng: KHÔNG ĐẠT YÊU CẦU (tạm, khám phá).** Lý do: III-b là cổng bắt buộc, mốc S_min đã chốt (tạm), và
cả khoảng CI của độ nhạy ở **cả ba** nhóm tông nằm dưới 0,80 (`acceptance-gates.md` §3 bước 4, mục 1). I-1 và II-3
`CHƯA ĐO`, nhưng không đổi được kết luận: dù hai cổng đó đạt, III-b vẫn trượt.

Đọc kết quả:
- Trên ảnh điện thoại cùng nguồn (PAD) model đạt cả hai mốc; trên ảnh lâm sàng khác nguồn thì bỏ sót 40–48% ca ác ở
  fold 4. Khoảng hụt lớn: cận trên tốt nhất (0,632, tông sáng) còn cách 0,80 khoảng 0,17.
- Mốc sẽ được review lại. Muốn III-b đổi nhãn thì phải hạ S_min xuống ≤ 0,5559 (cận trên tông trung bình) mới thôi
  `KHÔNG ĐẠT`, và ≤ 0,4563 (cận dưới tông tối) mới `ĐẠT` — đổi mốc sau khi đã thấy bảng này là post-hoc (§4 #13).
- Cộng 5 fold (mỗi fold ngưỡng `pad_sens90` của nó) độ nhạy Fitzpatrick theo tông cao hơn fold 4: 0,712 / 0,657 /
  0,699 — vẫn dưới 0,80; độ đặc hiệu thì 0,593 / 0,584 / 0,597, cũng dưới Sp_min 0,60. Tức là các fold khác không đạt
  III-b theo hướng khác: bắt nhiều ca ác hơn nhưng gắn cờ nhiều ảnh lành hơn (điểm ước lượng, không CI;
  `reports/2026-10-03_thesis_review_checks/README.md:38-46`).

Lệnh còn thiếu để đo đủ:
- I-1 (p95) và A2 trên chính `.pte` ship — U6.
- II-3 — U5 rồi S2/S3/S11 (`docs/L3_CAMERA_EVAL_GUIDE.md`).

Chưa verify được trên Mac: các số của II-1/II-2 chỉ đọc lại từ báo cáo 01/10–02/10 (đo trên Pixel 6a); Wilson CI
coi các ảnh là độc lập (Fitzpatrick không có mã bệnh nhân để kiểm).
