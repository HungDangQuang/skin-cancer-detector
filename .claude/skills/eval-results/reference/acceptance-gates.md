---
name: acceptance-gates
description: Hợp đồng DUY NHẤT để phán "model đã ĐẠT YÊU CẦU chưa" (đủ tốt để chạy trên điện thoại) — khung 3 trụ (I chạy được · II giữ chất lượng · III đúng với người dùng tại ngưỡng app) + C2, mốc hiện hành, quy tắc gán nhãn theo cả khoảng CI 95%, bộ từ vựng phán quyết bắt buộc, và danh sách suy luận bị cấm đã từng gây kết luận sai trong dự án này. Mọi skill/agent đánh giá phải đi qua file này trước khi viết "đạt", "đủ tốt", "dùng được", "sẵn sàng triển khai/ship". Lý do + ngày + nhãn post-hoc của từng mốc nằm ở acceptance-gates-history.md.
---

# Cổng chấp nhận — khi nào được nói "model đạt yêu cầu"

> Soạn 01/10/2026 theo yêu cầu tác giả: *"kết quả của các metric cũng phải ra các con số chứng minh
> là model đủ mạnh và hiệu quả thì mới có thể coi là tốt được"*. Câu hỏi trọng tâm của luận văn là
> **"làm thế nào để tạo ra mô hình hoạt động tốt trên điện thoại"** — nên "tốt" phải là một phép
> đo, không phải một cảm nhận.

## 0. Ba câu hỏi KHÁC NHAU — đừng trả lời câu này bằng bằng chứng của câu kia

| Câu hỏi | Bằng chứng hợp lệ | Ví dụ từ vựng được phép |
|---|---|---|
| **(1) Huấn luyện có lành không?** (hội tụ, không NaN, không overfit) | log, `val_metrics.json`, val − test gap | "run khoẻ / có vấn đề" — **không** phải "đạt yêu cầu" |
| **(2) A có tốt hơn B không?** (KD vs baseline, arm mới vs đối chứng, student vs teacher) | **CI bootstrap ghép cặp** (`run/bootstrap_ci.sh PAIR=…`) | "tốt hơn có ý nghĩa / không phân biệt được / kém hơn có ý nghĩa" |
| **(3) Model có ĐẠT YÊU CẦU không?** | **Toàn bộ cổng ở §2**, đo trên đúng model sẽ ship | chỉ các nhãn ở §3 |

"KD tốt hơn baseline" (câu 2) **không bao giờ** suy ra "model đạt" (câu 3). Một student tốt hơn hẳn
baseline của nó vẫn có thể gần đoán mò trên ảnh điện thoại.

**Trùng chữ cần tránh:** các báo cáo arm (vd `reports/2026-10-01_srcsamp_item2_3.md`, brief
`docs/TASK_ITEM2_3_source_sampler_ship_ckpt.md`) viết "item 2 đạt tiêu chí" / "Nếu item 2 KHÔNG đạt" cho **endpoint so sánh đã đăng ký
trước** — đó là câu (2). Khi trích sang câu (3), viết "endpoint item 2 đạt", không viết "model đạt".

## 1. Trạng thái các mốc (hiện hành — cập nhật 04/10/2026)

Bảng này là **trạng thái**, không phải lịch sử: mỗi hạng mục một dòng, giá trị đang áp dụng. Lý do, lời tác giả,
văn liệu và chi tiết post-hoc của từng lần chốt/đổi: [`acceptance-gates-history.md`](acceptance-gates-history.md).
Tài liệu viết trước 05/10/2026 trích "`acceptance-gates.md` §1" để lấy **lý do / văn liệu** (vd đổi C2 ngày 03/10:
Hinton, Furlanello, Mirzadeh, Cho & Hariharan) — phần đó nay ở history §A, nguyên văn.

- Phán quyết tổng theo §3 bước 4: một cổng bắt buộc `KHÔNG ĐẠT` với mốc đã chốt ⇒ `KHÔNG ĐẠT YÊU CẦU` dù các mốc
  khác còn đề xuất; nếu không có cổng như vậy mà còn mốc đề xuất ⇒ `CHƯA CÓ TIÊU CHÍ CHỐT`. Không bao giờ viết
  "model đạt yêu cầu" khi còn mốc đề xuất.
- Mốc **CHỐT TẠM** được dùng **như ĐÃ CHỐT** để gán nhãn (§3), kèm chữ "(tạm)" trong mọi báo cáo; nếu tác giả đổi,
  ghi ngày đổi và khai post-hoc.
- Mốc chốt sau khi đã nhìn thấy kết quả của chính model đang chấm phải được khai là *post-hoc*. Khi tác giả
  chốt/đổi: sửa dòng tương ứng dưới đây **và** thêm một mục có ngày vào `acceptance-gates-history.md` §A.

| Hạng mục | Mốc / giá trị hiện hành | Trạng thái | Ngày | Post-hoc? |
|---|---|---|---|---|
| Luật gộp | **Khung 3 trụ §2.1** (thay luật gộp sáu tiêu chí cũ — lịch sử) | ĐÃ CHỐT | 03/10/2026 | có |
| I-1 độ trễ p95 (§2.1) | ≤ 80 ms | ĐỀ XUẤT | — | — |
| II-1 (= A3) · II-2 (= A4) | như A3 · A4 (§2 A) | ĐỀ XUẤT | — | — |
| II-3 đổi quyết định qua pipeline app | < 0,5% (chốt kèm cỡ mẫu) | ĐỀ XUẤT | — | — |
| III-a: S_min · Sp_min | 0,80 · 0,60 | **CHỐT TẠM** | 04/10/2026 | có với P0; tiên nghiệm với vòng 2 **trừ** một dòng metric test P1 fold 4 đã bị thấy trước (`docs/PREREG_CANDIDATE2_2026-10-02.md` §10) |
| III-b: S_min · Sp_min **mỗi nhóm tông** | 0,80 · 0,60 (giữ 0,80; mốc bác sĩ 0,47 chỉ thêm vào báo cáo) | **CHỐT TẠM** | 04/10/2026 | như III-a |
| III-b: tập chấm | **Fitzpatrick17k-C** (3.086 / 4.320 ảnh headline; `reports/2026-10-04_review_v2_checks/fitz17kC_headline_image_ids.txt`) — chỉ III-b; C2, B3, C4b vẫn trên headline | ĐÃ CHỐT | 04/10/2026 | có |
| C2: metric · tập miền · vai | ΔAUPRC (student − teacher) · PAD · Fitz · HAM · **bắt buộc** | ĐÃ CHỐT | 01/10 (metric) · 03/10 (miền, vai) | có |
| C2: cách hiểu | **không kém** teacher quá δ (`lo > −δ`) | ĐÃ CHỐT | 03/10/2026 | có |
| C2: δ | **CHỐT TẠM:** δ = 0,05 × AUPRC của **chính teacher trong arm**, từng miền — PAD = **các hàng PAD của test in-domain** (không phải AUPRC gộp), Fitz và HAM = **biến thể headline**; điểm ước lượng = trung bình 5 fold, checkpoint chính `predictions.csv`; **không làm tròn** khi so (vd PAD 0,7966 × 0,05 = 0,03983); đổi định nghĩa từ δ tuyệt đối sang tương đối. Teacher `efficientnetv2_m`: PAD 0,040 · Fitz 0,035 · HAM 0,025. Không có nguồn văn liệu (quy ước); tính trên phần AUPRC vượt mức đoán bừa thì 5% này tương đương lớn hơn. Post-hoc với P0 (mọi δ > 0,0068 làm P0 qua) | **CHỐT TẠM** | 04/10/2026 | có với P0 |
| B2 (PAD sens@spec80) | mục tiêu 0,81 · sàn 0,47 — **tham chiếu/báo cáo**, không còn là cổng | ĐÃ CHỐT | 01/10 (mốc) · 03/10 (vai) | có |
| B4 (HAM10000) | mục tiêu 0,81 — vai **BÁO CÁO** | ĐÃ CHỐT | 01/10 (mốc) · 02/10 (vai) | có |
| B1, B3 → báo cáo · C4a → gộp vào III-b | — | ĐÃ CHỐT | 03/10/2026 | có |
| δ của C4b | 0,02 AUC (không có nguồn) | CHỜ QUYẾT (C4b chỉ báo cáo) | — | — |
| Điểm vận hành app | hàng **PAD** của val, độ nhạy 90% (`pad_sens90`) | tác giả xác nhận giữ | 03/10/2026 | có (xem "Báo cáo bắt buộc") |

**Phán quyết hiện hành** của ứng viên ship P0 (khám phá, post-hoc): **`KHÔNG ĐẠT YÊU CẦU (tạm)`** — III-b trượt —
`reports/2026-10-04_acceptance_verdict_P0_3pillar.md`. Các phán quyết cũ (khung cũ) và vì sao đổi: history §A.

## 2. Các cổng

### 2.0 Quy tắc chọn ứng viên và quy tắc đạt (vẫn áp dụng)

Sáu tiêu chí chọn model của tác giả (chốt 01/10/2026) và luật gộp theo chúng là **lịch sử** từ 03/10/2026 —
bảng ánh xạ tiêu chí → cổng ở `acceptance-gates-history.md` §C. C1 (KD > baseline) chưa bao giờ là tiêu chí
chọn model: nó là bằng chứng *giải pháp KD có hiệu quả* cho luận văn (câu hỏi (2) ở §0), vẫn phải báo cáo.
Hai quy tắc dưới đây vẫn áp dụng nguyên văn cho khung 3 trụ (chỉ đổi "tiêu chí bắt buộc" thành "cổng bắt buộc
theo luật gộp §2.1").

**Chọn ≠ phát triển — cách dùng sáu tiêu chí cho hợp lệ.** Mọi cổng B và C (kể cả C2, C4a) chấm trên
**tập kiểm**: test in-domain (B1, B2, phần PAD của C2), HAM10000 (B4, C2) và Fitzpatrick17k (B3, C2, C4).
Tác giả cấm đưa HAM vào train; brief item 2/3 cấm dùng HAM/Fitz để chọn fold/checkpoint/cấu hình
(`:33`) và cấm dùng test để chọn lại (`:73-75`) — brief đó là đăng ký trước cho câu hỏi *so sánh* của
arm item 2/3, nên ghi HAM/Fitz là "chỉ báo cáo"; ở đây chúng làm cổng **chấp nhận**, không phải công
cụ chọn. Quy trình hợp lệ:

1. Mọi lựa chọn (arm, checkpoint, fold) làm bằng **val** hoặc endpoint đã đăng ký trước → ra **một**
   ứng viên.
2. Các cổng bắt buộc (luật gộp §2.1) **chấp nhận hoặc loại** ứng viên đó, một lần.
3. Nếu bị loại: kết luận của luận văn là "ứng viên định trước KHÔNG ĐẠT YÊU CẦU ở cổng X". Muốn thử
   ứng viên kế tiếp thì phải khai *post-hoc* — các tập kiểm đã được nhìn hai lần, và cần một tập kiểm
   khác để xác nhận (§4 #18). Có thể định trước một **danh sách ứng viên theo thứ tự** để giảm vấn đề
   này, nhưng vẫn phải khai số lần đã thử.

**Quy tắc đạt (mọi cổng có CI):** so **cả khoảng** CI 95% (paired bootstrap, `scripts/bootstrap_ci.py`,
không gộp fold) với mốc — luật gán nhãn đầy đủ ở §3, **không bao giờ** dùng điểm ước lượng để gán
`ĐẠT` hay `KHÔNG ĐẠT`.
Cổng B/C chấm trên **CI 5 fold** của arm, **cùng họ checkpoint với bản ship** (ship = `best_model_auprc.pth`
⇒ dùng `predictions_auprc.csv`; kết quả trên checkpoint pAUC không tự áp sang — brief item 2/3 §3);
cổng A chấm trên **đúng fold/checkpoint sẽ ship**. Mọi metric ở B/C là metric **không phụ thuộc ngưỡng**.

### 2.1 Khung 3 trụ — luật hiện hành từ 03/10/2026

| Cổng | Đo gì | Mốc | Chấm trên | Nguồn mốc |
|---|---|---|---|---|
| **I-1** (= A1, thêm p95) | Độ trễ **p95** sau 5 phút chạy liên tục, Pixel 6a, trên `.pte` ship | ≤ 80 ms (ĐỀ XUẤT) | fold ship | ngân sách nội bộ (`docs/ANDROID_APP_SPEC.md:237`); review §3 trụ I |
| **II-1** (= A3) | Điện thoại ↔ máy chủ | như A3 | fold ship | như A3 |
| **II-2** (= A4) | Không lỗi, tất định trên máy | như A4 | fold ship | như A4 |
| **II-3** (L3) | Tỉ lệ đổi quyết định tại ngưỡng app khi ảnh đi qua pipeline thật của app (decode → resize → normalize) so với pipeline Python | < 0,5% (ĐỀ XUẤT) | fold ship | review §3 trụ II |
| **III-a** | Ảnh điện thoại cùng nguồn (PAD, test in-domain): **độ nhạy và độ đặc hiệu tại ngưỡng app đóng băng** (quy tắc `pad_sens90` trên val của fold ship) | cận dưới độ nhạy ≥ **0,80** **và** cận dưới độ đặc hiệu ≥ **0,60** (chốt tạm 04/10) | fold ship | use case sàng lọc (lập luận: `acceptance-gates-history.md` §B dòng S_min, chốt tạm 04/10) |
| **III-b** | Ảnh lâm sàng **khác nguồn** (Fitzpatrick17k headline, **tập con Fitzpatrick17k-C** từ 04/10), **từng** nhóm tông da (sáng · trung bình · tối), cùng ngưỡng app | cận dưới độ nhạy **mỗi nhóm** ≥ **0,80** và cận dưới độ đặc hiệu mỗi nhóm ≥ **0,60** (chốt tạm 04/10) | fold ship | như III-a — "ổn định trên ảnh camera thực tế" |
| **C2** | Student không kém teacher quá δ | §2 C | CI 5 fold (như cũ) | §1 |

- **CI cho III-a/III-b:** ngưỡng cố định ⇒ chỉ còn sai số nhị thức; dùng **Wilson 95%** trên fold ship, **giả định
  các ảnh độc lập**. Giả định này mới được kiểm gần đúng cho PAD trên hai metric không phụ thuộc ngưỡng (gom theo bệnh
  nhân gần như không đổi CI, `reports/2026-10-03_thesis_review_checks/` §1). Với Fitzpatrick không có mã bệnh nhân;
  phần vi phạm đã biết là **ảnh gần trùng** (bản gốc có ~2.297 cụm trùng theo Abhishek et al. 2025, repo chỉ bắt trùng
  tuyệt đối — 3 ảnh) ⇒ từ 04/10 III-b chấm trên tập con Fitzpatrick17k-C để giảm vi phạm này; trùng chưa phát hiện thì
  vẫn có thể còn, và trường hợp nhiều ảnh cùng một người nhưng không gần trùng thì **chưa kiểm được**.
- **Mốc chưa có giá trị** (trước 04/10: S_min, Sp_min, δ): báo số đo + CI, nhãn ô = `CHƯA CHỨNG MINH` kèm cờ
  `CHƯA CÓ TIÊU CHÍ CHỐT`. Từ 04/10 ba mốc này đã CHỐT TẠM nên luật này không còn áp cho chúng.
- **I-1, II-1, II-2, II-3 chấm theo số đo, không CI** (như A1/A3/A4 ở §3). II-3 phải chốt kèm cỡ mẫu: với ~200 ảnh,
  < 0,5% nghĩa là **không ảnh nào** đổi quyết định (1/200 = 0,5%).
- **Tính III cho một run:** `reports/2026-10-03_thesis_review_checks/tone_at_app_threshold.py` (III-b) và
  `reports/2026-10-02_threshold_options/threshold_options.sh` (III-a) — **đã tham số hoá 04/10/2026** (R13): script
  shell nhận `RUN=`/`FITZ=`/`OUT=`, script Python nhận `FITZ_DIR SUMMARY_CSV SHIP_FOLD [KEEP_IDS]`; mặc định là P0 (chạy
  lại ra y hệt kết quả cũ). **III-b từ 04/10:** truyền `KEEP_IDS = reports/2026-10-04_review_v2_checks/fitz17kC_headline_image_ids.txt`.
  Luật nhãn: một phía "≥ m" của §3 bước 1. Bước "ô chỉ có 1 fold ⇒ hạ xuống CHƯA CHỨNG MINH" **không** áp cho
  III (như cổng A — chấm trên đúng model sẽ ship).
- **Luật gộp (từ 03/10/2026):** I-1 + II-1 + II-2 + II-3 + III-a + III-b + C2 đều phải `ĐẠT`.
- **Báo cáo bắt buộc (không quyết định):** B1 (ISIC, so Kurtansky — tham chiếu), sens@spec80 trên PAD so với
  Cochrane (0,81 / 0,76 / 0,47 — tham chiếu), B3, B4 (HAM — ngoài phạm vi ảnh camera, nhưng HAM vẫn trong tập
  miền của C2), C1 (KD − baseline), C3, C4b (chênh lệch giữa các tông, CI ghép cặp), A2, hành vi tại ngưỡng app. **Từ 04/10
  (review v2 D2, D4):** sens@spec80 **theo từng tông** trên Fitzpatrick (headline và Fitzpatrick17k-C, trung bình 5 fold, CI) so với mốc bác sĩ trên ảnh
  lâm sàng 0,47 — chỉ để định vị, không phải cổng; và độ nhạy tốt nhất tại độ đặc hiệu ≥ 0,60 theo tông, fold ship, ngưỡng chọn trên chính test (lạc quan)
  (khoảng cách tới điểm (0,80; 0,60) của III-b) — `reports/2026-10-04_review_v2_checks/`.
- **Post-hoc:** khung, S_min/Sp_min, δ và tập chấm III-b (Fitzpatrick17k-C, 04/10) đều được chốt sau khi đã thấy kết quả của ứng viên hiện tại trên test PAD
  và Fitzpatrick ⇒ với ứng viên đó, mọi nhãn chỉ là **khám phá**; nhãn đứng được cần tập xác nhận chưa ai mở
  (`docs/PROGRESS.md` U8). Phán quyết hiện hành: dòng cuối §1 (trỏ báo cáo phán quyết, nơi có số đo); số khám phá của P0 lúc chốt khung: history §D.

Các mục **A, B, C** dưới đây giữ định nghĩa metric và nguồn mốc; vai trò cổng/báo cáo theo §2.1.

### A. Chạy được trên điện thoại

| # | Metric | Mốc đề xuất | Nguồn mốc |
|---|---|---|---|
| A1 | Độ trễ sau 5 phút chạy liên tục (Pixel 6a, 4 luồng) | ≤ 80 ms/ảnh | ngân sách nội bộ `docs/ANDROID_APP_SPEC.md:237` (spec ghi "20–80 ms … single-threaded"; số đo là 4 luồng) |
| A2 | Bộ nhớ đỉnh lúc suy luận | **chỉ báo cáo, chưa có mốc** — spec không có mốc cho model (`:958` là tiêu chí của bước crop/tiền xử lý 12 MP, không phải model) | đã đo 208–257 MiB cho 16 model (`thesis/LUAN_VAN.md:2053`) |
| A3 | Tương đương điện thoại ↔ máy chủ, trên checkpoint ship | max\|Δlogit\| < 1e-3 **và** \|ΔAUPRC\| < 0,005; các metric khác chỉ báo cáo Δ | 1e-3 = `TOL` mặc định `run/check_pte_parity.sh`; 0,005 = sàn nhiễu chạy lại **của AUPRC** (`experiments/_reproducibility/README.md`) |
| A4 | Chạy ổn định trên điện thoại thật, trên checkpoint ship: export `.pte` + parity PASS (`run/check_pte_parity.sh`), lượt chấm trên máy không lỗi, tất định | lỗi < 0,1% số ảnh **và** chạy lại cho kết quả trùng bit | tiêu chí nghiệm thu của harness Android (`docs/MOBILE_EVAL_TASK.md` §7, đã áp ở `mobile/testing_result/README.md` mục *Acceptance criteria*) |

A3 **chỉ** chứng minh "điện thoại không làm hỏng kết quả" — không chứng minh kết quả đó tốt.
A3 + A4 phải đo **trên điện thoại**, trên **đúng checkpoint ship** — lượt Pixel 29/09 là checkpoint
`__mobile` fold 0 train lại, không phải bản ship. Export thành công **không** phải bằng chứng
(XNNPACK từng lower sai `efficientformerv2_s2` mà không báo lỗi — `CLAUDE.md`). "Đảm bảo" ở đây vẫn
chưa phủ bước đổi kích thước ảnh camera (L3, `docs/MOBILE_EVAL_PLAN.md:66`) và app thật (memory `project_ondevice_eval_gap`) — phải khai.

### B. Mạnh — so với mốc bên ngoài, TÁCH theo miền ảnh (không dùng số gộp)

| # | Miền | Metric | Mốc đề xuất | Nguồn mốc |
|---|---|---|---|---|
| B1 | ISIC (crop 3D-TBP) | AUC-ROC · pAUC@TPR80 | ≥ 0,922 · ≥ 0,142 | Kurtansky 2025 (npj Digit Med, PMC12639164), **Bảng 3**: biến thể chỉ dùng ảnh (tiles) AUC 0,922 · pAUC 0,142 (model thắng giải, ảnh + metadata: 0,9668 · 0,1726). Assistant đối chiếu toàn văn qua Europe PMC ngày 01/10/2026; verifier không kiểm được (không có web). Đo trên tập test của cuộc thi, không phải phần ISIC của splits v2 |
| B2 | **Ảnh điện thoại (PAD)** — cổng quan trọng nhất | độ nhạy @ độ đặc hiệu 80% | **mục tiêu ≥ 0,81 (ĐÃ CHỐT, post-hoc)** · sàn ≥ 0,47 (chỉ báo cáo) | Cochrane Dinnes 2018 (CD011902.pub2): đánh giá **trên ảnh**, độ nhạy ở độ đặc hiệu cố định 80%: dermoscopy **81%**, nhìn bằng mắt (ảnh thường) **47%**. Đích chẩn đoán: melanoma xâm lấn + biến thể hắc tố trong biểu bì không điển hình (**chỉ melanoma**; nhãn dương của dự án gồm cả BCC/SCC). Mục tiêu 0,81 là mức đọc **dermoscopy**, đang áp cho ảnh điện thoại. Assistant đối chiếu tóm tắt qua Europe PMC 01/10/2026; verifier không kiểm được |
| B3 | Ảnh lâm sàng đa dạng (Fitzpatrick17k headline) | độ nhạy @ độ đặc hiệu 80% | sàn ≥ 0,47 (không có mục tiêu) | như B2 (chưa có mốc riêng cho bộ này) |
| B4 | **HAM10000 headline** (dermoscopy, xuyên miền) — tiêu chí 6 — **chỉ báo cáo từ 02/10/2026** (§1) | độ nhạy @ độ đặc hiệu 80% | **mục tiêu ≥ 0,81 — ĐÃ CHỐT, post-hoc** (bác sĩ đọc **ảnh dermoscopy** — đúng loại ảnh của HAM); sàn: không dùng — mục tiêu đã chốt là mốc quyết định | Cochrane Dinnes 2018, như B2; chỉ melanoma, trong khi nhãn ác tính của HAM gồm nhiều loại |

- AUPRC **không** làm cổng B: không có mốc ngoài và không so được giữa các bộ (nền = prevalence).
- **Độ nhạy @ đặc hiệu 80% đã có** từ 01/10/2026 (commit `9535b23`): `compute_metrics` ghi
  `sens_at_80spec`; `bootstrap_ci.sh METRICS=auc_roc,auprc,pauc_at_tpr80,sens_at_90spec,sens_at_80spec`
  (mặc định của runner không đổi). Lần đo đầu cho ứng viên ship: `reports/ci_gates_srcsamp_*.md`.
  Vẫn không được thay sens@80spec bằng sens@90spec — sens@90spec chỉ là **cận dưới** của sens@80spec.
- PAD trong tập test v2 chỉ có 397 ảnh (189 ác tính), CI AUC rộng ~0,07 — cổng B2 với quy tắc
  cận dưới là **chặt có chủ đích**; phải nói điều đó khi báo cáo.

### C. Hiệu quả — chứng minh bằng so sánh GHÉP CẶP

| # | Câu hỏi | Mốc đề xuất |
|---|---|---|
| C1 | KD có giúp không? (`kd` − `baseline`, cùng student/splits/seed) — **bằng chứng luận văn, không phải tiêu chí chọn** | CI ghép cặp ΔAUPRC > 0 trên PAD **và** Fitzpatrick |
| C2 | **Student không kém teacher quá δ** (tiêu chí 2) — student − teacher, **cùng splits, cùng arm** | CI ghép cặp ΔAUPRC có **cận dưới > −δ** trên **từng** miền PAD · Fitzpatrick · HAM10000 (metric ΔAUPRC, cách hiểu, tập miền PAD·Fitz·HAM và vai bắt buộc: **ĐÃ CHỐT, post-hoc**; δ = 5% AUPRC teacher: **chốt tạm 04/10**) |
| C3 | Nén được bao nhiêu? | chỉ báo cáo tỉ lệ tham số / dung lượng / FLOPs (`reports/benchmark/*.json`) |
| C4a | **Mỗi nhóm tông da** (sáng · trung bình · tối, Fitzpatrick17k) tự đạt sàn (tiêu chí 5) | độ nhạy @ đặc hiệu 80% của **từng** nhóm ≥ sàn B3 (0,47) |
| C4b | Chênh lệch giữa các nhóm tông | **báo cáo** CI của mọi cặp chênh AUC; nhãn tương đương (±δ) chỉ để tham khảo — xem dưới |

- C2 là phép kiểm **không kém** (từ 03/10/2026; trước đó là vượt trội `lo > 0`): mỗi miền `ĐẠT` khi cận dưới
  của Δ(student − teacher) > −δ. C2 `ĐẠT` chỉ nói nén không làm mất quá δ — **không** nói KD có tác dụng (đó là C1).
  (Trước 04/10, khi chưa có δ: nhãn ô = `CHƯA CHỨNG MINH` + cờ. Từ 04/10 δ đã chốt tạm — §1.)
  Lưu ý chiều lệch: teacher hiện tại train **không** có sampler theo nguồn (student có) ⇒ teacher yếu hơn trên PAD
  ⇒ phép kiểm không kém **dễ đạt hơn** thực tế; xem `reports/2026-10-04_r6r7/README.md` (R7: cùng công thức thì KD không phân biệt được với teacher trên PAD) và `docs/PROGRESS.md` S16. Tập miền có HAM (dermoscopy) dù B4
  đã thành báo cáo vì cùng lý do — tác giả **giữ HAM** (03/10/2026). Ô HAM (cận dưới −0,0068) là ô quyết định δ
  ở ứng viên hiện tại.
  Teacher phải là **chính teacher đã dạy student đó, trên cùng splits** (vd `x_kd__ddi` − `x_teacher__ddi`),
  không phải teacher của ma trận splits v1. Luật "cùng họ checkpoint với bản ship" chỉ áp cho **phía
  student** (`predictions_auprc.csv` nếu ship checkpoint AUPRC); phía teacher dùng `predictions.csv` của
  chính teacher — teacher không có bản `_auprc` và brief cấm train lại teacher.
  Lần đo đầu (01/10/2026, ứng viên ship `__srcsamp` checkpoint AUPRC vs
  `runs_newsplit_ddi/teacher/efficientnetv2_m`): `reports/ci_gates_srcsamp_*.md` (driver `.tmp/archived_root_drivers_20261002/.tmp_ci_gates.sh` (local, untracked)).
- C4a là cổng một phía trên từng nhóm — đạt được nếu model đủ tốt ở cả ba nhóm, kể cả khi nhóm tối
  chỉ có n = 411 (CI rộng hơn, nên cần điểm ước lượng cao hơn sàn một khoảng).
- C4b là phép kiểm **tương đương** (hai phía). Với cỡ mẫu Fitzpatrick hiện tại nó **không thể
  `ĐẠT`** dù model công bằng tuyệt đối: CI của chênh AUC rộng ~0,064 (sáng − trung bình) tới
  ~0,10 (các cặp có nhóm tối, n = 411) — đều > 2δ = 0,04 (`reports/ci_ddi_fitzpatrick17k_headline.md`
  mục 4). Ngoài ra chênh sáng − trung bình có ý nghĩa (khác 0) ở **cả 6 arm splits v2, kể cả teacher**.
  Vì vậy tiêu chí 5 được chấm bằng C4a; C4b báo cáo kèm nhãn tham khảo, và nếu C4b `KHÔNG ĐẠT`
  (cả CI nằm ngoài ±δ) thì phải nêu rõ là hạn chế. Đừng nới luật cho vừa.
- **Luật gộp hiện hành: §2.1.** (Luật gộp cũ theo sáu tiêu chí, áp đến 02/10/2026: history §C.)
  C1, C3, C4b, A2 và **B4** bắt buộc **báo cáo** nhưng không quyết định chọn.

### Báo cáo bắt buộc (không phải cổng, nhưng KHÔNG được bỏ)

Hành vi thật của app tại ngưỡng quyết định lấy từ **val** (không chỉnh trên test): độ nhạy / độ đặc
hiệu / số ảnh lành bị gắn cờ, **tách theo miền**. Ví dụ đã gặp: một checkpoint gắn cờ 205/208 ảnh PAD
lành. Các cổng B/C không phụ thuộc ngưỡng, nên con số này không được biến mất khỏi báo cáo.

**Ngưỡng phải theo miền ảnh app nhận** (đo 01/10/2026, `reports/2026-10-01_pad_threshold/`,
`docs/ANDROID_APP_SPEC.md` §3.5a): ngưỡng Youden trên toàn bộ val bị ảnh ISIC áp đảo và gắn cờ ~mọi ảnh
điện thoại lành (175/175 trên val PAD của fold 4). Điểm vận hành mặc định cho ảnh camera = chọn trên
**hàng PAD của val** (độ nhạy 90% — tác giả **xác nhận giữ** 03/10/2026; vẫn **post-hoc**: chọn SAU khi đã xem 3 điểm vận hành trên test
PAD của fold 4, mà mọi fold dùng chung các hàng test đó; lúc chọn (01/10) Fitzpatrick là phép kiểm chưa bị đụng, ở
đó độ nhạy cộng 5 fold 0,692 — từ đó số Fitzpatrick tại ngưỡng app đã được xem, nên với ứng viên hiện tại III-b là
post-hoc). Cùng tập val đã dùng để chọn checkpoint và fold; không có CI. Báo cáo hành vi app tại **điểm đó**, kèm
điểm toàn cục để đối chiếu.

## 3. Bộ từ vựng phán quyết — chỉ dùng các nhãn này

Gán nhãn theo **bốn bước, đúng thứ tự** — một cổng chỉ có đúng một nhãn:

**Bước 1 — mỗi ô đo (một metric × một miền/nhóm), chỉ dựa vào khoảng CI 95% `[lo, hi]`:**

| Dạng ô | `ĐẠT` | `KHÔNG ĐẠT` | `CHƯA CHỨNG MINH` |
|---|---|---|---|
| Một phía "≥ m" (III-a, III-b; B1–B4, C4a khi báo cáo) | `lo ≥ m` | `hi < m` | còn lại (CI cắt qua m) — kể cả khi điểm ước lượng đã ở phía sai của m |
| Vượt trội "> 0" (C1) | `lo > 0` | `hi ≤ 0` | còn lại |
| Không kém "> −δ" (C2) | `lo > −δ` | `hi < −δ` | còn lại |
| Hai phía "trong ±δ" (C4b, tham khảo) | `−δ ≤ lo` **và** `hi ≤ δ` | `lo > δ` **hoặc** `hi < −δ` | còn lại |
| Không có CI (A1, A3, A4) | số đo thoả mốc | số đo trượt mốc | — |

Ô chưa tính được metric/CI ⇒ `CHƯA ĐO` (ghi lệnh còn thiếu). Riêng **cổng B/C**: ô chỉ có số 1 fold,
hoặc CI tính trên họ checkpoint khác bản ship (phía student) ⇒ hạ xuống `CHƯA CHỨNG MINH`. Quy tắc
"1 fold" **không** áp cho cổng A — cổng A vốn được chấm trên đúng một fold ship.

**Bước 2 — gộp các ô thành nhãn của cổng** (III-a có 2 ô: độ nhạy, độ đặc hiệu; III-b có 3 nhóm tông; C2 có 3 miền;
B1 có 2 metric khi báo cáo), ưu tiên
từ trên xuống: có ô `KHÔNG ĐẠT` ⇒ cổng `KHÔNG ĐẠT` · có ô `CHƯA ĐO` ⇒ `CHƯA ĐO` · có ô
`CHƯA CHỨNG MINH` ⇒ `CHƯA CHỨNG MINH` · mọi ô `ĐẠT` ⇒ `ĐẠT`.

**Bước 3 — mốc chưa chốt:** nếu mốc của cổng còn `ĐỀ XUẤT` (§1), nhãn ở bước 2 được ghi là
"<nhãn> *so với mốc đề xuất*" và cổng mang thêm cờ `CHƯA CÓ TIÊU CHÍ CHỐT`.

**Bước 4 — phán quyết tổng**, trên các cổng bắt buộc (luật gộp §2), ưu tiên từ trên xuống:

1. `KHÔNG ĐẠT YÊU CẦU` — có ít nhất một cổng bắt buộc `KHÔNG ĐẠT` **với mốc ĐÃ CHỐT** (mốc CHỐT TẠM tính như ĐÃ CHỐT, nhãn ghi kèm "(tạm)").
2. `CHƯA CÓ TIÊU CHÍ CHỐT` — còn cổng bắt buộc mang cờ ở bước 3.
3. `CHƯA KẾT LUẬN ĐƯỢC` — còn cổng bắt buộc `CHƯA ĐO` / `CHƯA CHỨNG MINH`.
4. `ĐẠT YÊU CẦU` — mọi cổng bắt buộc `ĐẠT` với mốc `ĐÃ CHỐT`.

Ví dụ áp luật C4b (giá trị arm DDI, `reports/ci_ddi_fitzpatrick17k_headline.md:80`): chênh AUC
sáng − trung bình +0,0452 [+0,0152; +0,0762], δ = 0,02 ⇒ `lo = 0,0152 < δ` ⇒ **`CHƯA CHỨNG MINH`**,
không phải `KHÔNG ĐẠT` (dù khác 0 có ý nghĩa).

Báo cáo luôn liệt kê từng cổng với nhãn của nó. Không dùng "Good/Moderate/Poor", "khá tốt", "gần đạt",
"promising", "ready" để thay cho phán quyết tổng.

## 4. Suy luận BỊ CẤM — phần lớn đã từng gây kết luận sai trong dự án này (xem §7)

| # | Suy luận sai | Vì sao sai | Thay bằng |
|---|---|---|---|
| 1 | "KD thắng baseline ⇒ model tốt" | câu (2) ≠ câu (3) | chấm đủ cổng B |
| 2 | "AUC in-domain 0,98 ⇒ mạnh" | số gộp ISIC+PAD; sàn "chỉ đoán nguồn ảnh" đã 0,872 trên test v1 (~0,85 trên test v2 theo tính tay của lượt kiểm chéo 01/10, chưa có artifact) | tách theo `source` (`SUBGROUP=source`) |
| 3 | "Điện thoại = máy chủ ⇒ chạy tốt trên mobile" | parity chỉ bảo toàn chất lượng, không tạo ra nó | A3 + B |
| 4 | "Số 1 fold / checkpoint train lại ⇒ kết luận về arm" | 1 checkpoint ≠ phân phối 5 fold; `__mobile` fold 0 yếu bất thường | CI 5 fold; số 1 fold chỉ là `CHƯA CHỨNG MINH` |
| 5 | "Điểm ước lượng vượt mốc ⇒ đạt" | bỏ qua sai số lấy mẫu | cận dưới CI |
| 6 | So AUPRC giữa hai bộ dữ liệu | nền AUPRC = prevalence (0,45% vs 15,6% vs 50%) | AUC / pAUC / sens@spec khi so giữa bộ |
| 7 | Dùng số in-domain splits v1 (`experiments/runs/`, `experiments/runs_isic_only/`) cho phán quyết | splits v1 rò rỉ bệnh nhân ⇒ in-domain bị thổi phồng (`CLAUDE.md` Data integrity) | chỉ splits v2; số xuyên miền v1 dùng được cho AUC/AUPRC/pAUC, **không** cho sens/spec tại ngưỡng |
| 8 | Giấu hành vi tại ngưỡng vì "cổng không phụ thuộc ngưỡng" | người dùng app gặp ngưỡng, không gặp AUC | mục "Báo cáo bắt buộc" |
| 9 | Chọn arm/checkpoint/fold theo HAM/Fitz rồi báo thành công trên chính HAM/Fitz | dùng tập kiểm làm tập phát triển | chọn theo val/endpoint đăng ký trước; nếu đã lỡ → khai post-hoc |
| 10 | "KD thắng 12/12" như bằng chứng | đếm trận thắng không có sai số | CI ghép cặp của Δ |
| 11 | "Hai CI chồng nhau ⇒ không khác nhau" | CI không ghép cặp chồng nhau vẫn có thể có Δ ghép cặp loại trừ 0 | chạy `PAIR=` |
| 12 | "Hiệu chuẩn xong ⇒ model tốt hơn" | AUC/AUPRC/pAUC bất biến với biến đổi đơn điệu | hiệu chuẩn chỉ sửa % hiển thị |
| 13 | Đặt/đổi mốc sau khi xem kết quả rồi tuyên bố đạt | mốc hậu nghiệm | §1: khai post-hoc |
| 14 | Thay sens@80spec bằng sens@90spec để kết luận "không đạt" | sens@90spec ≤ sens@80spec | ghi `CHƯA ĐO` |
| 15 | "Teacher cũng sụt ⇒ nén không gây hại" mà không kiểm student − teacher | đúng hướng nhưng chưa phải C2 | chạy C2 |
| 16 | "Student không kém teacher (C2 đạt) ⇒ KD có tác dụng" | C2 chỉ nói nén không mất quá δ; teacher và baseline có thể cùng tốt | tác dụng KD = C1 (KD − baseline, ghép cặp) |
| 17 | "Tổng thể công bằng / AUC Fitzpatrick đạt ⇒ hoạt động tốt trên mọi tông da" | số gộp che nhóm yếu | III-b (trước 03/10: C4a) trên **từng** nhóm tông |
| 18 | So nhiều ứng viên trên HAM/Fitz, giữ cái đạt, rồi báo "đạt trên HAM/Fitz" | HAM/Fitz đã thành tập phát triển | chỉ chấm một ứng viên định trước; nếu không ⇒ khai post-hoc (§2.0, §2.1) |

## 5. Khối bắt buộc trong mọi báo cáo có phán quyết "đạt / chưa đạt"

```
### Cổng chấp nhận (theo .claude/skills/eval-results/reference/acceptance-gates.md)
Model được chấm: <run-dir · fold · checkpoint · splits v1/v2>
Trạng thái mốc: <theo bảng §1 — từng cổng: ĐỀ XUẤT | CHỐT TẠM ngày … (nhãn kèm "(tạm)") | ĐÃ CHỐT ngày …>
| Cổng | Metric | Mốc | Giá trị [CI 95%] | Nguồn (file:line) | Nhãn |
|---|---|---|---|---|---|
| I-1 · II-1 · II-2 · II-3 · III-a · III-b · C2 (§2.1) | … | … | … | … | ĐẠT / KHÔNG ĐẠT / CHƯA CHỨNG MINH / CHƯA ĐO / CHƯA CÓ TIÊU CHÍ CHỐT |
Báo cáo (không quyết định): B1 · sens@spec80 PAD so Cochrane · B3 · B4 · C1 · C3 · C4b · A2
Hành vi tại ngưỡng app (theo miền): <sens / spec / số ảnh lành bị gắn cờ>
Ứng viên định trước? <có — checkpoint/fold chọn theo val | không — đã so nhiều ứng viên trên HAM/Fitz ⇒ post-hoc>
Phán quyết tổng: <ĐẠT YÊU CẦU | KHÔNG ĐẠT YÊU CẦU | CHƯA KẾT LUẬN ĐƯỢC | CHƯA CÓ TIÊU CHÍ CHỐT>
Lệnh còn thiếu để đo đủ: <…>
```

## 6. Cách đo đủ (lệnh — chạy trên server)

- C1/C2 in-domain theo miền: `bash run/bootstrap_ci.sh RESULTS_DIR=<cây> PAIR="<A>:<B>" SUBGROUP=source`
  (ước tính ~12 phút cho lượt 6 run, suy từ giờ bắt đầu + mtime của `logs/bootstrap_ci_20260926_075720.log`;
  brief item 2/3 ghi "~1,5 phút/lượt" — đó là các lượt Fitzpatrick 4.320 dòng; thời gian theo cỡ tập test, không theo việc tách nhóm).
- C1/C2/C4 trên Fitzpatrick: một lượt riêng trên cây Fitz với `SUBGROUP=tone_group`.
- Tiền tố `x_` làm auto-pairing không chạy — luôn dùng `PAIR=` tường minh
  (`scripts/bootstrap_ci.py` §3 đòi khớp "kind"; memory `project_domain_aug_arm`).
- B2/B3/B4/C4a: thêm `sens_at_80spec` vào `METRICS=` (có từ commit `9535b23`); C4a dùng `SUBGROUP=tone_group`
  trên cây Fitzpatrick (mục 4 của báo cáo cho từng nhóm). Mẫu đầy đủ, kể cả C2 với checkpoint AUPRC của student:
  `.tmp/archived_root_drivers_20261002/.tmp_ci_gates.sh` (local, untracked) → `reports/ci_gates_srcsamp_*.md`.

## 7. Chưa verify được (khi soạn file này)

- ~~Mốc Kurtansky 0,922/0,142 là của biến thể chỉ ảnh~~ — **đã đối chiếu 01/10/2026** (toàn văn, Bảng 3)
  bởi assistant; verifier không kiểm được (không có web).
- ~~Mốc Cochrane 0,81/0,47~~ — **đã đối chiếu 01/10/2026** (tóm tắt CD011902.pub2) bởi assistant; verifier
  không kiểm được. Còn hở: chỉ melanoma, và 0,81 là mức đọc dermoscopy.
- δ = 0,02: đề xuất, không có nguồn.
- §4 #12, #13, #14, #16, #17, #18 là **phòng ngừa** — chưa có tiền lệ được kiểm trong memory/repo;
  các dòng còn lại có tiền lệ (memory/transcript).
- Ánh xạ tiêu chí → cổng là **diễn giải của bản này**: "chấp nhận được trên HAM" → mục tiêu 0,81 (B4)
  **đã được tác giả chốt** 01/10/2026 tối (post-hoc); "giữ được hiệu năng teacher" → không kém quá δ (C2,
  metric ΔAUPRC và cách hiểu đã chốt; δ chốt tạm 04/10 — đổi từ "vượt trội" ngày 03/10/2026, post-hoc) và "hoạt động tốt trên các tông da" → mỗi nhóm đạt sàn 0,47
  (C4a) — **đã gộp vào III-b** từ 03/10/2026 (mốc S_min, §1).
- Con số "~0,85" (sàn đoán nguồn ảnh trên test v2): tính tay trong lượt kiểm chéo, chưa có artifact.
- "205/208 ảnh PAD lành bị gắn cờ": nguồn là brief item 2/3 (`:12`) và memory, số của **một** checkpoint.
