# Tóm tắt dự án để review — bản 2 (04/10/2026): các nhận xét đã được xử lý thế nào

> **Dành cho:** người hoặc AI review **ngoài dự án**, cần kiểm xem các nhận xét của ba bản review đã được xử lý hết
> chưa.
> - Bản 1 (03/10, commit `3815e7c`) là bản gửi đi để lấy review; bản này thay nó.
> - Đây không phải nơi theo dõi việc. Trạng thái **mới nhất** của từng việc nằm ở `docs/PROGRESS.md`; trạng thái ghi ở
>   đây là ảnh chụp lúc viết (04/10/2026, ~07:50 giờ VN = 00:50 UTC).

## 0. Cách dùng tài liệu này

**Repo:** `https://github.com/HungDangQuang/skin-cancer-detector`, nhánh `docs/tracker-cleanup-and-ddi`. Mọi đường dẫn
tính từ gốc repo.

**Ba bản review cần đối chiếu:**

| Bản review | File | Nội dung |
|---|---|---|
| R-ngoài (03/10) | `docs/REVIEW_DANH_GIA_2026-10-03.md` | review dự án (đọc bản 1 của brief này): 12 nhận xét §1.1–1.12, nhận xét hướng đi §2, đề xuất khung đánh giá §3, thứ tự việc §4 |
| ThesisForge | `docs/review_luan_van_grad_thesisforge.pdf` | review kỹ thuật/phương pháp của bản luận văn gửi GVHD (~20/09): Issue 1–10 |
| ThesisPolisher | `docs/danh_gia_luan_van_thesispolisher.pdf` | chỉ ngôn ngữ/định dạng của bản luận văn đó: L1–L5, F1–F8, A1–A3 |

**Mốc thời gian quan trọng (UTC):**

| Thời điểm | Sự kiện | Bằng chứng |
|---|---|---|
| 03/10 | đổi khung đánh giá; đối chiếu review với code; ghi chú sửa luận văn | commit `efc1a9c` |
| 03/10 16:52 | vòng chọn 2 train xong | `docs/PROGRESS.md` mục 7 (log chỉ có trên server) |
| 04/10 ~00:25 | một phiên assistant thấy **một dòng số test của P1 fold 4** khi `tail` log | `docs/PREREG_CANDIDATE2_2026-10-02.md` §10 |
| 04/10 00:28:21 | **chạy** bước chọn ứng viên (chỉ đọc val) | `reports/2026-10-04_candidate2_selection/selection.md` dòng 3 |
| 04/10 00:32:12 | commit **chốt tạm các mốc số** | commit `518e80d` |
| 04/10 00:32:51 | commit **kết quả chọn** | commit `c61bab2` |
| 04/10 00:33:02 | bắt đầu chấm test vòng 2 (chỉ báo cáo) | lời báo của phiên làm N2–N4 |

Ghi chú về trình tự: các mốc được chốt **sau** khi bước chọn đã chạy, nhưng **trước** commit kết quả chọn và trước khi
đọc số test vòng 2 (ngoài dòng đã lộ ở 00:25). Bước chọn chỉ dùng val và không phụ thuộc các mốc này.
**Hai commit message không chính xác** (không sửa lịch sử git; bảng trên mới là căn cứ): `518e80d` ghi "before the
round-2 selection" — thực ra bước chọn đã chạy lúc 00:28:21; `c61bab2` ghi "before any round-2 test number" — thực ra
một dòng test của P1 fold 4 đã lộ lúc ~00:25.

Các commit sau đó (phán quyết P0, PPV/NPV, danh sách các lần mở test, script tham số hoá, bản brief này): xem
`git log`.

**Các file để kiểm:**
- Hợp đồng chấm (luật "đạt" duy nhất): `.claude/skills/eval-results/reference/acceptance-gates.md` — **§1** là lịch sử quyết định có ngày; **§2.1** là luật hiện hành; mục A/B/C định nghĩa các cổng cũ.
- Đối chiếu từng ý của R-ngoài với code (dưới đây gọi tắt là *crosscheck*): `reports/2026-10-03_review_crosscheck.md`.
- Kiểm tra theo ThesisForge: `reports/2026-10-03_thesis_review_checks/README.md`.
- Ghi chú sửa luận văn: `thesis/CAN_SUA_SAU.md` (#1–#23).
- Danh sách các lần mở tập test: `reports/2026-10-04_test_set_openings.md`.
- Phán quyết hiện hành: `reports/2026-10-04_acceptance_verdict_P0_3pillar.md`.

**Ký hiệu trạng thái ở §6:**

| Ký hiệu | Nghĩa |
|---|---|
| ✅ | đã xử lý trong repo |
| 📝 | đã ghi thành chỗ cần sửa trong luận văn — **luận văn chưa sửa** (quyết định của tác giả: chỉ sửa khi có kết quả ổn) |
| 👤 | chờ tác giả quyết, **hoặc tác giả đã quyết khác đề xuất** (có ghi lý do) |
| 🔜 | đã lên lịch hoặc đang chạy, chưa có kết quả trong repo |
| ⏸ | hoãn |
| ❌ | không làm, vì nhận xét không áp dụng hoặc sai (có bằng chứng) |

**Thuật ngữ:**

| Từ | Nghĩa |
|---|---|
| P0 / P1 / P2 | ứng viên `efficientnetv2_m → mobilenetv4_conv_medium` / `convnextv2_base → mobilenetv4` / `efficientnetv2_m → repvit_m1_0` |
| I-1, II-1/2/3, III-a, III-b, C2 | các cổng của khung 3 trụ (§4) |
| B1–B4, C1, C4a, C4b | các cổng cũ, nay chỉ báo cáo: ISIC, ảnh PAD, Fitzpatrick, HAM (độ nhạy ở độ đặc hiệu 80%); KD − baseline; mốc theo từng tông da; chênh lệch giữa các tông |
| S_min / Sp_min | độ nhạy / độ đặc hiệu tối thiểu (0,80 / 0,60, chốt tạm) |
| Wilson CI | khoảng tin cậy nhị thức, dùng cho độ nhạy/độ đặc hiệu tại một ngưỡng cố định |
| headline | biến thể chấm chính của HAM/Fitzpatrick |
| biên hoà | hai ứng viên chênh dưới 0,005 trên val thì coi là hoà, giữ ứng viên đứng trước (PREREG §7.1) |
| mã U / R / S / N | việc trong `docs/PROGRESS.md`: chờ tác giả / làm được ngay / để sau / sau khi train |

## 1. Bối cảnh (đã đổi so với bản 1)

**Bài toán:** phân loại nhị phân tổn thương da từ một ảnh.
- Model chạy offline trên Android (ExecuTorch).
- App chỉ hiện quyết định ("nên đi khám" / "không thấy dấu hiệu đáng ngờ").
- Nhãn ác tính: PAD = melanoma, BCC, SCC; HAM10000 tính cả `akiec`.

**Hai câu hỏi trung tâm** (tác giả chốt 03/10, thay câu của bản 1):
1. Làm thế nào để thu gọn và triển khai mô hình học sâu phân loại tổn thương da lên thiết bị di động?
2. Làm cách nào duy trì hiệu năng chẩn đoán ổn định trên miền ảnh chụp từ camera thực tế?

Bộ câu hỏi con là **đề xuất, chưa được duyệt**. KD là một giải pháp trong câu 1.

## 2. Dữ liệu

| Dataset | Loại ảnh | Vai trò | Quy mô |
|---|---|---|---|
| ISIC 2024 | crop từ chụp toàn thân 3D | train / val / test in-domain | cùng PAD: 372.242 ảnh, 2.410 bệnh nhân |
| PAD-UFES-20 | ảnh **điện thoại** | train / val / test — gần app nhất | test: 397 ảnh (189 ác) |
| DDI | ảnh lâm sàng, tông da cân bằng | chỉ train | 656 ảnh (171 ác) |
| HAM10000 | dermoscopy | chỉ đánh giá. B4 chỉ báo cáo, **nhưng HAM vẫn nằm trong cổng C2** | 7.470 ảnh (headline) |
| Fitzpatrick17k | ảnh lâm sàng khác nguồn, có tông da | chỉ đánh giá — **cổng III-b** | 4.320 ảnh (tối 411 · sáng 2.310 · trung bình 1.599) |

**Splits v2** (22/09): test 59.093 ảnh, tách theo bệnh nhân trước khi chia 5 fold.

**Splits v1 bị rò rỉ bệnh nhân.** Luận văn bản ~20/09 dùng v1 và ghi nhầm là "patient-disjoint". Tác giả chọn
**phương án A**: công khai rò rỉ, giữ Chương 4 v1 kèm nhãn "lạm phát", thêm một mục v2 tự chứa (`thesis/CAN_SUA_SAU.md`
#8, `docs/thesis_ddi_section_checklist.md`).

## 3. Model và vòng chọn 2

- **Huấn luyện:** KD logit, sampler phân tầng theo nguồn ảnh, checkpoint chọn theo val AUPRC.
- **Vòng 2 chọn lại P0** (`efficientnetv2_m → mobilenetv4_conv_medium`, fold 4), chỉ bằng val (`reports/2026-10-04_candidate2_selection/`):
  - AUPRC trên ảnh PAD của val: P0 0,8831 · P1 0,8840 · P2 0,8536.
  - P1 hơn 0,0009, dưới biên hoà, nên giữ P0.

## 4. Đánh giá — luật hiện hành (khung 3 trụ, từ 03/10)

Luật đầy đủ ở hợp đồng §2.1. Model "đạt" chỉ khi **mọi** cổng dưới đây đạt.

| Cổng | Đo gì | Mốc | Trạng thái mốc |
|---|---|---|---|
| I-1 | độ trễ p95 trên `.pte` sẽ ship (Pixel 6a, sau 5 phút) | ≤ 80 ms | đề xuất |
| II-1 / II-2 | điện thoại = máy chủ; không lỗi, tất định | như A3 / A4 cũ | đề xuất |
| II-3 | tỉ lệ đổi quyết định khi ảnh đi qua pipeline thật của app | < 0,5% | đề xuất |
| III-a | ảnh PAD, tại **ngưỡng app đóng băng**: độ nhạy và độ đặc hiệu | cận dưới Wilson ≥ 0,80 · ≥ 0,60 | **chốt tạm 04/10** |
| III-b | Fitzpatrick17k, cùng ngưỡng, **từng tông da** | cùng hai mốc trên | **chốt tạm 04/10** |
| C2 | student không kém teacher quá δ (ΔAUPRC; PAD · Fitz · HAM) | δ = 5% AUPRC của chính teacher | **chốt tạm 04/10** |

**Chỉ báo cáo:** B1 (ISIC, so Kurtansky 2025), độ nhạy@đặc hiệu 80% trên PAD so với mốc Cochrane, B3, B4, C1, C4b,
bộ nhớ, tỉ lệ nén, hành vi tại ngưỡng app.

**Ngưỡng app:** quy tắc "độ nhạy 90% trên ảnh PAD của val" (fold 4 = 0,5705). Tác giả giữ quy tắc này ngày 03/10; nó
**post-hoc** vì được chọn sau khi xem test PAD.

**Phán quyết hiện hành của P0: `KHÔNG ĐẠT YÊU CẦU (tạm, khám phá)`** (`reports/2026-10-04_acceptance_verdict_P0_3pillar.md`):

| Cổng | Kết quả (fold 4) | Nhãn |
|---|---|---|
| II-1 / II-2 | max\|Δlogit\| 5,2e-06; 0/70.883 lỗi, trùng bit | đạt so với mốc đề xuất |
| III-a | độ nhạy 165/189 = 0,873 [0,818; 0,913]; độ đặc hiệu 152/208 = 0,731 [0,667; 0,786] | ĐẠT (tạm) |
| **III-b** | độ nhạy theo tông: sáng 0,604 [0,576; 0,632] · trung bình 0,520 [0,485; 0,556] · tối 0,524 [0,456; 0,591] | **KHÔNG ĐẠT** — cận trên cả ba tông < 0,80 |
| C2 | cận dưới ΔAUPRC: PAD +0,0396 · Fitz −0,0008 · HAM −0,0068 | ĐẠT (tạm) |
| I-1, II-3 | — | chưa đo; sẽ đo phía mobile sau |

**Phải đọc kèm:**
- **Khung, các mốc và quy tắc ngưỡng đều được chốt sau khi đã thấy kết quả của P0** ⇒ với P0, mọi nhãn chỉ là khám phá. "Chốt tạm" nghĩa là tác giả sẽ review lại; đổi mốc sau khi xem số là post-hoc và phải khai.
- **Khung mới nới hơn khung cũ ở ba chỗ, một chỗ đã bù** (hợp đồng §1):
  - Trụ III chấm trên **một** fold ship bằng Wilson CI, thay vì CI 5 fold.
  - Mốc 0,81 (B2) thôi làm cổng.
  - III-b ban đầu thiếu sàn độ đặc hiệu — **đã bù 04/10** bằng Sp_min.

## 5. Kết quả mới kể từ lúc có review

| Kiểm tra | Kết quả | Nguồn |
|---|---|---|
| Bootstrap theo bệnh nhân thay vì theo ảnh | PAD: CI gần như không đổi (+1–5%); ISIC: CI của AUC rộng thêm ~17%. Một run, hai metric, script tự viết | thesis_review_checks §1 |
| Độ nhạy/độ đặc hiệu theo tông tại ngưỡng app | như bảng III-b; cộng 5 fold: độ nhạy 0,712 / 0,657 / 0,699 | thesis_review_checks §2 |
| Label smoothing đã từng chạy chưa | **chưa** (chỉ có trong template 7 lớp tháng 4). Việc tác giả từ chối ngày 21/06 lấy từ ghi chép riêng, xem §7 | thesis_review_checks §3 |
| PPV/NPV tại ngưỡng app | ở tỉ lệ ác tính giả định 1% / 5%: PPV 0,032 / 0,146 | `reports/2026-10-04_ppv_npv_app_threshold/` |
| Code KD | T², BCE trên logit, baseline cùng công thức (crosscheck §1.6); teacher `.eval()` + `no_grad` (crosscheck §1.5) | crosscheck |
| Teacher có train cùng công thức với student không | **không**: teacher thiếu sampler theo nguồn và chỉ có checkpoint pAUC | crosscheck §1.5 |
| Fold ship nếu chọn theo AUPRC val PAD | vẫn là fold 4 | `selection.md` |

## 6. Bảng đối chiếu: từng nhận xét đã được xử lý thế nào

### 6.1 R-ngoài (`docs/REVIEW_DANH_GIA_2026-10-03.md`)

| # | Nhận xét (rút gọn) | Trạng thái | Đã làm / chỗ kiểm |
|---|---|---|---|
| 1.1 | Mốc B2 0,81 là mức đọc dermoscopy, chỉ melanoma, áp sai cho ảnh điện thoại | ✅ | Nguồn Cochrane đã được kiểm lại (qua web, xem §7): trên ảnh, ở độ đặc hiệu 80% — dermoscopy 81%, ảnh lâm sàng 47%; khám trực tiếp 76%. B2 **thôi làm cổng** (hợp đồng §1, §2.1); ghi chú #20 |
| 1.2 | "Cận dưới ≥ mốc" là phép kiểm vượt trội, thiếu power | ✅ một phần | Endpoint đổi sang độ nhạy/độ đặc hiệu tại ngưỡng cố định, Wilson CI. Vẫn giữ quy tắc cận dưới (có chủ đích). Cỡ mẫu cho tập xác nhận: ~180 ca ác cho power 80% (U8) |
| 1.3 | B1 pAUC / B3 trượt mốc ở chữ số thứ 4 | ✅ một phần · 🔜 | B1, B3 chỉ báo cáo. Kiểm theo seed bootstrap (R6): đã khởi chạy trên server 04/10 (theo danh sách lần mở test, dòng 15), chưa có kết quả trong repo |
| 1.4 | AND 8 cổng làm power chung thấp | ✅ một phần | Thay bằng AND 7 cổng của khung 3 trụ (vẫn là AND) |
| 1.5 | C2 "vượt teacher" không hợp lý; nghi teacher khác công thức | ✅ · 🔜 · ⏸ | C2 = không kém teacher quá δ (theo văn liệu KD, hợp đồng §1). Lệch công thức teacher đã xác nhận và khai. CI ghép cặp tách hiệu ứng (R7): đang chạy, chưa có kết quả trong repo. Train lại teacher đúng công thức: S16 |
| 1.6 | Kiểm loss KD; C1 không nên chỉ để báo cáo | ✅ (code) · 👤 (C1) | Code đúng. **Tác giả giữ C1 chỉ báo cáo**: tác dụng của KD là bằng chứng cho luận văn, không phải tiêu chí chọn model (hợp đồng §2.0). Luận văn phải nêu KD chưa chứng minh được tác dụng trên PAD (#7, #13) |
| 1.7 | Bỏ mốc tuyệt đối theo tông da, chỉ báo cáo chênh lệch | 👤 (quyết khác đề xuất) | **Tác giả giữ mốc theo từng tông** và nâng lên 0,80 (cổng III-b). Lý do: không giữ thì khung chỉ chấm ảnh PAD và P0 gần như đạt (hợp đồng §1). Mối lo nhãn Fitzpatrick nhiễu **chưa được trả lời**. Chênh lệch có CI ghép cặp: R12 |
| 1.8 | B1 so với test khác; pAUC có đúng công thức chính thức | ✅ · 🔜 | B1 chỉ báo cáo. So với hàm chấm chính thức: R8 |
| 1.9 | Endpoint nên là độ nhạy/độ đặc hiệu tại ngưỡng app | ✅ | Trụ III. Config app thật: ngưỡng 0,570523, so trên `sigmoid(logit)`; bằng chứng ở repo app riêng, xem §7. Phép so số trong review bị lệch điểm vận hành (crosscheck §1.9) |
| 1.10 | Post-hoc, tập test dùng lại, chưa có tập xác nhận | ✅ · 👤 | Khai post-hoc ở hợp đồng §1 và PREREG §8–§10. Danh sách các lần mở test: `reports/2026-10-04_test_set_openings.md`. Tác giả chọn **thu dữ liệu mới qua bệnh viện** (U8). Việc **không dùng ảnh crawl từ web làm tập xác nhận** là đánh giá của assistant, chưa phải quyết định của tác giả |
| 1.11 | Pipeline camera (L3) chưa đo | ⏸ | Đã thành cổng II-3; đo phía mobile, làm sau (U5, S11). Giả định "timm crop_pct" của reviewer không đúng: train dùng LANCZOS kéo về 224×224 (crosscheck §1.11) |
| 1.12 | Checkpoint chọn theo AUPRC val gộp (lẫn nguồn) | ✅ một phần · ⏸ | Fold ship chọn theo val PAD cũng ra fold 4 (0,8326 / 0,8593 / **0,8946** / 0,9144 / 0,9146). Checkpoint trong một fold vẫn chọn theo val gộp; chọn lại theo PAD cần sửa code và train lại (S9) |
| §2 | Thêm DDI: có ích nhưng chỉ thử một cặp | ⏸ | Chưa thử cặp khác; giới hạn đã ghi ở bản 1 của brief (§5) |
| §2 | Khung RQ thiếu bước "định nghĩa tốt"; RQ4 phần dermoscopy ít liên quan | ✅ | Định nghĩa "tốt" = khung 3 trụ (hợp đồng §2.1); câu hỏi trung tâm đổi (§1); dermoscopy (HAM) không làm cổng riêng, chỉ báo cáo qua B4 |
| §2 | Phát hiện rò rỉ là bài học phương pháp, nên đưa vào luận văn | 📝 | Phương án A (#8) |
| §2 | Vòng 2 nên giới hạn thời gian | ✅ | Đã chạy xong; chọn lại P0 |
| §3 trụ I | Độ trễ p95, đầu-cuối, cold start, bộ nhớ trên app thật, ≥ 2 máy | ✅ một phần · ⏸ | p95 là cổng I-1 (chưa đo). Độ trễ đầu-cuối, cold start, bộ nhớ trên app: U6, đo phía mobile, làm sau. ≥ 2 máy: S10 |
| §3 báo cáo kèm | PPV/NPV; theo loại ung thư; độ bền chất lượng ảnh | ✅ · ⏸ | PPV/NPV đã tính (§5). Theo loại ung thư: S15. Độ bền ảnh: S14 |
| §4 bước 3 | Chọn lại ngưỡng trên val, không dùng test | 👤 (quyết khác đề xuất) | Tác giả **giữ** quy tắc ngưỡng 90% đã chọn post-hoc; phải xác nhận trên dữ liệu mới (U8) |

### 6.2 ThesisForge (`docs/review_luan_van_grad_thesisforge.pdf`)

| Issue | Nhận xét (rút gọn) | Trạng thái | Đã làm / chỗ kiểm |
|---|---|---|---|
| 1 | In-domain bị PAD chi phối; nên bootstrap theo bệnh nhân | ✅ · 📝 | Mọi số tách ISIC/PAD; đã đo bootstrap theo bệnh nhân (§5). Ghi chú #12, #18 |
| 2 | Thiếu hiệu chuẩn và giao thức ngưỡng | ✅ (repo) · 📝 · 👤 | Repo: ngưỡng chọn trên val rồi đóng băng. Luận văn: phân biệt ba loại ngưỡng (#14). ECE/Brier: U9 (app chỉ hiện quyết định nhị phân). Chưa xét temperature/Platt |
| 3 | r = −0,963 bị diễn giải quá mạnh | 📝 | Số tính trên in-domain v1 (lạm phát): bỏ hoặc gắn nhãn (#9) |
| 4 | Thiếu baseline nén khác (label smoothing, class-balanced, INT8, pruning…) | 👤 · 📝 | Label smoothing chưa từng chạy; INT8 bị gác 14/07 → U11. Câu hạn chế: #15. "KD = làm mượt nhãn" phải ghi là giả thuyết (#13) |
| 5 | Thiếu phân tích lỗi, Grad-CAM | ⏸ | S12 |
| 6 | Công bằng chỉ ở metric gộp | ✅ · 🔜 | Đã tính theo tông tại ngưỡng app; nay là cổng III-b. CI ghép cặp của chênh lệch: R12. Ghi chú #11 |
| 7 | Gói tái lập | ⏸ | S13 |
| 8 | Quy trình an toàn cho người dùng | ✅ (app) · 📝 · ⏸ | App (repo riêng, xem §7) có kiểm tra chất lượng ảnh, kết quả "ảnh không hợp lệ", thông điệp nhị phân. Mô tả trong luận văn: #16. Cổng OOD: S7 |
| 9 | Phát biểu "tốt nhất / duy nhất" | 📝 | #17. Chưa xét bảng tiêu chí chọn backbone |
| 10 | Placeholder, bảng vỡ | 📝 | #19 |
| — | Lời khen "patient-disjoint" | 📝 | Dựa trên mô tả sai; phương án A (#8) |
| Checklist #2 | Viết lại tóm tắt/kết luận | 📝 | #17, #21 |

### 6.3 ThesisPolisher (`docs/danh_gia_luan_van_thesispolisher.pdf`)

| Mục | Trạng thái | Chỗ kiểm |
|---|---|---|
| L1–L5, A1–A3 (văn phong, thuật ngữ) | 📝 | #19, #21 |
| F1–F6 (placeholder, mục lục, số trang, cột "Nguồn tệp", nhãn hình lặp, bảng rộng) | 📝 | #19. Mục lục và số trang phải làm tay khi xuất Word (`run/export_thesis_docx.sh` chỉ in lời nhắc) |
| F7 (TLTK phải theo thứ tự xuất hiện) | ❌ không áp dụng | Quy định UIT xếp TLTK theo nhóm ngôn ngữ, trong nhóm theo bảng chữ cái (`docs/QUY_DINH_TRINH_BAY_LUAN_VAN.md` §11). Reviewer cũng ghi "cần xác nhận với mẫu của trường" |
| F8 ([14], [26] không được trích) | ❌ | Trong bản hiện tại có trích ở `thesis/LUAN_VAN.md:1532` ("[14, 26]"). Bản ~20/09 reviewer đọc không có trong git |

### 6.4 Đề xuất: không trình bày bảng cổng cũ trong luận văn

Đã ghi (#23): thân luận văn chỉ trình bày bộ tiêu chí cuối, kèm 3–4 câu khai báo việc đổi tiêu chí sau khi đã thấy kết
quả.

## 7. Chưa kiểm được độc lập (người review ngoài cần biết)

- **Nguồn web, chỉ assistant đọc** (các lượt kiểm chéo không có web):
  - Cochrane Dinnes 2018 (81 / 47 / 76 / 92%).
  - Kurtansky 2025.
  - Văn liệu KD: Hinton 2015; Mirzadeh 2020; Cho & Hariharan 2019; Furlanello 2018.
  - SCIN (bộ ảnh da của Google), giấy phép DermNet, các văn bản luật VN.
- **Bằng chứng ở repo app riêng `SkinDetector` của tác giả** (config ngưỡng, `Decision.kt`, các tính năng an toàn): không nằm trong repo này. Crosscheck tự ghi mục 1.9–1.10 là "viết sau lượt kiểm, chưa ai kiểm lại".
- **Ghi chép riêng ngoài repo:** việc tác giả từ chối label smoothing ngày 21/06.
- **Chỉ có trên server:** các run vòng 2, log driver, dòng test P1 fold 4 đã lộ, trạng thái R6/R7.
- **Bootstrap theo bệnh nhân** dùng script thư viện chuẩn tự viết, không dùng hàm metric của repo.
- **Wilson CI** giả định các ảnh độc lập; chưa kiểm được trên Fitzpatrick (không có mã bệnh nhân).
- **Bản luận văn ~20/09** mà hai review đọc không có trong git (chỉ có bản 05/09 và 30/09).
- **Luận văn chưa được sửa:** mọi mục 📝 mới là ghi chú.

## 8. Câu hỏi gợi ý cho reviewer

1. Mỗi nhận xét ở §6 đã được xử lý đúng chưa? Có mục ✅ nào thật ra chỉ xử lý một phần?
2. Ở các chỗ tác giả quyết khác đề xuất (1.6, 1.7, §4 bước 3), lý do có đủ không?
3. Khung 3 trụ với III-b bắt buộc trên Fitzpatrick có cân bằng không: có quá dễ (Wilson một fold) hay quá khó (mốc 0,80 cho ảnh khác nguồn)?
4. Các mốc chốt tạm (0,80 / 0,60 / δ = 5% AUPRC teacher) có lý lẽ đủ không, khi biết chúng post-hoc với P0?
5. Kết luận "đạt trên ảnh điện thoại cùng nguồn, chưa ổn định trên ảnh lâm sàng khác nguồn (tạm, khám phá, post-hoc)" có đứng được với bằng chứng hiện có không, và cần gì để xác nhận?
6. Các mục 👤 / ⏸ nào nên làm trước khi viết lại luận văn?
