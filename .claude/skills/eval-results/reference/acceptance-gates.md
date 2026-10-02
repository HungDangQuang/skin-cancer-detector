---
name: acceptance-gates
description: Hợp đồng DUY NHẤT để phán "model đã ĐẠT YÊU CẦU chưa" (đủ tốt để chạy trên điện thoại) — các cổng A/B/C có mốc số, quy tắc đạt theo cận dưới CI 95%, bộ từ vựng phán quyết bắt buộc, và danh sách suy luận bị cấm đã từng gây kết luận sai trong dự án này. Mọi skill/agent đánh giá phải đi qua file này trước khi viết "đạt", "đủ tốt", "dùng được", "sẵn sàng triển khai/ship".
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

## 1. Trạng thái các mốc

**⚠️ Trạng thái (cập nhật 01/10/2026, tối): B2, B4 (mục tiêu 0,81) và metric C2 (ΔAUPRC) ĐÃ CHỐT — post-hoc;
mọi mốc khác vẫn ĐỀ XUẤT.** Cổng mang mốc đề xuất được báo cáo "so với mốc đề xuất" kèm cờ
`CHƯA CÓ TIÊU CHÍ CHỐT` (§3 bước 3). Phán quyết tổng theo §3 bước 4: một cổng bắt buộc `KHÔNG ĐẠT` với mốc
đã chốt ⇒ `KHÔNG ĐẠT YÊU CẦU` dù các mốc khác còn đề xuất; nếu không có cổng như vậy ⇒ `CHƯA CÓ TIÊU CHÍ CHỐT`.
Không bao giờ viết "model đạt yêu cầu" khi còn mốc đề xuất.

**02/10/2026 (tác giả): B4 chuyển từ "bắt buộc" sang "BÁO CÁO" — post-hoc** (quyết định sau khi đã thấy B4
`KHÔNG ĐẠT` của ứng viên ship; lý do: app nhận ảnh camera, HAM10000 là dermoscopy, train không có ảnh
dermoscopy nào). B4 vẫn được đo, ghi nhãn và báo cáo như cũ, chỉ không còn quyết định chọn model. Các mốc
đề xuất còn lại giữ nguyên (tác giả: "giữ các mốc đề xuất thử xem"), kể cả tập miền PAD · Fitz · HAM của C2.
Phán quyết hiện hành: `reports/2026-10-02_acceptance_verdict_srcsamp.md` — **CHƯA CÓ TIÊU CHÍ CHỐT**
(trước 02/10: KHÔNG ĐẠT YÊU CẦU vì B4).

Khi tác giả chốt: sửa cột "Mốc", ghi ngày chốt vào bảng dưới, đổi trạng thái thành `ĐÃ CHỐT`.
Mốc chốt sau khi đã nhìn thấy kết quả của chính model đang chấm phải được khai là *post-hoc*.

| Hạng mục | Trạng thái | Ngày chốt | Người chốt |
|---|---|---|---|
| **Sáu tiêu chí chọn model** (§2.0) | **ĐÃ CHỐT** — đây là danh sách *cái gì* phải đạt | 01/10/2026 | tác giả |
| Mốc số của từng cổng (§2 A/B/C) | ĐỀ XUẤT — tác giả **đã ghi nhận** 01/10/2026, **post-hoc** (sau khi đã thấy mọi kết quả B/C của ứng viên ship, `reports/ci_gates_srcsamp_*.md`); các dòng CHỜ QUYẾT bên dưới vẫn mở; B2, B4, metric C2 đã chốt ở các dòng kế tiếp | 01/10/2026 (ghi nhận) | tác giả |
| B2: mốc quyết định = **mục tiêu ≥ 0,81** (sàn 0,47 chỉ báo cáo) | **ĐÃ CHỐT — post-hoc** | 01/10/2026 (tối) | tác giả |
| B4 (HAM10000): mốc quyết định = **mục tiêu ≥ 0,81** | **ĐÃ CHỐT — post-hoc** | 01/10/2026 (tối) | tác giả |
| B4: **vai = BÁO CÁO** (không còn bắt buộc; mốc 0,81 giữ để ghi nhãn) | **ĐÃ CHỐT — post-hoc** | 02/10/2026 | tác giả |
| C2 "vượt teacher": cách hiểu (đề xuất: vượt trội có ý nghĩa, `lo > 0`), metric (đề xuất ΔAUPRC), tập miền (đề xuất PAD · Fitz · HAM; ISIC bỏ vì đề xuất xoay quanh ảnh kiểu điện thoại và xuyên miền) | **metric = ΔAUPRC: ĐÃ CHỐT — post-hoc** (01/10/2026 tối, tác giả); cách hiểu `lo > 0` và tập miền PAD·Fitz·HAM: vẫn là đề xuất, đang được dùng | 01/10/2026 tối (metric) | tác giả |
| C4a "tốt trên mọi tông da": mỗi nhóm đạt sàn 0,47 hay mức cao hơn | CHỜ QUYẾT | — | — |
| δ của C4b (đề xuất 0,02 AUC — không có nguồn) | CHỜ QUYẾT | — | — |

## 2. Các cổng

### 2.0 Sáu tiêu chí chọn model (tác giả chốt 01/10/2026) → cổng tương ứng

Một model chỉ được chọn (ship / gọi là "đạt yêu cầu") khi đạt **cả sáu**:

| # | Tiêu chí của tác giả (nguyên ý) | Cổng | Bắt buộc |
|---|---|---|---|
| 1 | Vượt qua phần evaluation — các chỉ số đề xuất | B1 · B2 · B3 | ✅ |
| 2 | Vượt qua teacher | **C2** (student **tốt hơn** teacher có ý nghĩa — không phải "không kém") | ✅ |
| 3 | Tốc độ chấp nhận được trên mobile | A1 | ✅ |
| 4 | Khả năng hoạt động trên mobile được đảm bảo | A3 · **A4** (+ A2 báo cáo) | ✅ |
| 5 | Hoạt động tốt trên các tông da khác nhau | **C4a** (mỗi nhóm tông đạt sàn) · C4b (chênh lệch — báo cáo) | ✅ C4a |
| 6 | Chỉ số evaluation chấp nhận được trên HAM10000 | **B4** | **báo cáo** (từ 02/10/2026, post-hoc — §1) |

C1 (KD > baseline) **không** nằm trong sáu tiêu chí chọn model: nó là bằng chứng *giải pháp KD có hiệu
quả* cho luận văn (câu hỏi (2) ở §0), vẫn phải báo cáo nhưng không quyết định chọn model.

**Chọn ≠ phát triển — cách dùng sáu tiêu chí cho hợp lệ.** Mọi cổng B và C (kể cả C2, C4a) chấm trên
**tập kiểm**: test in-domain (B1, B2, phần PAD của C2), HAM10000 (B4, C2) và Fitzpatrick17k (B3, C2, C4).
Tác giả cấm đưa HAM vào train; brief item 2/3 cấm dùng HAM/Fitz để chọn fold/checkpoint/cấu hình
(`:33`) và cấm dùng test để chọn lại (`:73-75`) — brief đó là đăng ký trước cho câu hỏi *so sánh* của
arm item 2/3, nên ghi HAM/Fitz là "chỉ báo cáo"; ở đây chúng làm cổng **chấp nhận**, không phải công
cụ chọn. Quy trình hợp lệ:

1. Mọi lựa chọn (arm, checkpoint, fold) làm bằng **val** hoặc endpoint đã đăng ký trước → ra **một**
   ứng viên.
2. Sáu tiêu chí **chấp nhận hoặc loại** ứng viên đó, một lần.
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
| B4 | **HAM10000 headline** (dermoscopy, xuyên miền) — tiêu chí 6 | độ nhạy @ độ đặc hiệu 80% | **mục tiêu ≥ 0,81 — ĐÃ CHỐT, post-hoc** (bác sĩ đọc **ảnh dermoscopy** — đúng loại ảnh của HAM); sàn: không dùng — mục tiêu đã chốt là mốc quyết định | Cochrane Dinnes 2018, như B2; chỉ melanoma, trong khi nhãn ác tính của HAM gồm nhiều loại |

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
| C2 | **Student vượt teacher** (tiêu chí 2) — student − teacher, **cùng splits, cùng arm** | CI ghép cặp **ΔAUPRC > 0** (cận dưới > 0) trên **từng** miền PAD · Fitzpatrick · HAM10000 (metric ΔAUPRC: **ĐÃ CHỐT, post-hoc**; cách hiểu `lo > 0` và tập miền: đề xuất) |
| C3 | Nén được bao nhiêu? | chỉ báo cáo tỉ lệ tham số / dung lượng / FLOPs (`reports/benchmark/*.json`) |
| C4a | **Mỗi nhóm tông da** (sáng · trung bình · tối, Fitzpatrick17k) tự đạt sàn (tiêu chí 5) | độ nhạy @ đặc hiệu 80% của **từng** nhóm ≥ sàn B3 (0,47) |
| C4b | Chênh lệch giữa các nhóm tông | **báo cáo** CI của mọi cặp chênh AUC; nhãn tương đương (±δ) chỉ để tham khảo — xem dưới |

- C2 là phép kiểm **vượt trội**, chặt hơn hẳn "không kém": chỉ một miền có CI chứa 0 là `CHƯA CHỨNG MINH`.
  Teacher phải là **chính teacher đã dạy student đó, trên cùng splits** (vd `x_kd__ddi` − `x_teacher__ddi`),
  không phải teacher của ma trận splits v1. Luật "cùng họ checkpoint với bản ship" chỉ áp cho **phía
  student** (`predictions_auprc.csv` nếu ship checkpoint AUPRC); phía teacher dùng `predictions.csv` của
  chính teacher — teacher không có bản `_auprc` và brief cấm train lại teacher.
  "Vượt" = vượt trội có ý nghĩa (`lo > 0`) là **diễn giải** của bản này cho chữ "vượt qua teacher";
  tác giả có thể chốt cách hiểu khác (§1). Lần đo đầu (01/10/2026, ứng viên ship `__srcsamp` checkpoint AUPRC vs
  `runs_newsplit_ddi/teacher/efficientnetv2_m`): `reports/ci_gates_srcsamp_*.md` (driver `.tmp/archived_root_drivers_20261002/.tmp_ci_gates.sh` (local, untracked)).
- C4a là cổng một phía trên từng nhóm — đạt được nếu model đủ tốt ở cả ba nhóm, kể cả khi nhóm tối
  chỉ có n = 411 (CI rộng hơn, nên cần điểm ước lượng cao hơn sàn một khoảng).
- C4b là phép kiểm **tương đương** (hai phía). Với cỡ mẫu Fitzpatrick hiện tại nó **không thể
  `ĐẠT`** dù model công bằng tuyệt đối: CI của chênh AUC rộng ~0,064 (sáng − trung bình) tới
  ~0,10 (các cặp có nhóm tối, n = 411) — đều > 2δ = 0,04 (`reports/ci_ddi_fitzpatrick17k_headline.md`
  mục 4). Ngoài ra chênh sáng − trung bình có ý nghĩa (khác 0) ở **cả 6 arm splits v2, kể cả teacher**.
  Vì vậy tiêu chí 5 được chấm bằng C4a; C4b báo cáo kèm nhãn tham khảo, và nếu C4b `KHÔNG ĐẠT`
  (cả CI nằm ngoài ±δ) thì phải nêu rõ là hạn chế. Đừng nới luật cho vừa.
- **Luật gộp (theo sáu tiêu chí §2.0):** A1 + A3 + A4 + B1 + B2 + B3 + C2 + C4a đều phải `ĐẠT`.
  C1, C3, C4b, A2 và (từ 02/10/2026) **B4** bắt buộc **báo cáo** nhưng không quyết định chọn.

### Báo cáo bắt buộc (không phải cổng, nhưng KHÔNG được bỏ)

Hành vi thật của app tại ngưỡng quyết định lấy từ **val** (không chỉnh trên test): độ nhạy / độ đặc
hiệu / số ảnh lành bị gắn cờ, **tách theo miền**. Ví dụ đã gặp: một checkpoint gắn cờ 205/208 ảnh PAD
lành. Các cổng B/C không phụ thuộc ngưỡng, nên con số này không được biến mất khỏi báo cáo.

**Ngưỡng phải theo miền ảnh app nhận** (đo 01/10/2026, `reports/2026-10-01_pad_threshold/`,
`docs/ANDROID_APP_SPEC.md` §3.5a): ngưỡng Youden trên toàn bộ val bị ảnh ISIC áp đảo và gắn cờ ~mọi ảnh
điện thoại lành (175/175 trên val PAD của fold 4). Điểm vận hành mặc định cho ảnh camera = chọn trên
**hàng PAD của val** (hiện dùng độ nhạy 90% — **post-hoc**: chọn SAU khi đã xem 3 điểm vận hành trên test
PAD của fold 4, mà mọi fold dùng chung các hàng test đó; chỉ Fitzpatrick là phép kiểm chưa bị đụng, ở đó độ nhạy
0,692). Cùng tập val đã dùng để chọn checkpoint và fold; không có CI. Báo cáo hành vi app tại **điểm đó**, kèm
điểm toàn cục để đối chiếu.

## 3. Bộ từ vựng phán quyết — chỉ dùng các nhãn này

Gán nhãn theo **bốn bước, đúng thứ tự** — một cổng chỉ có đúng một nhãn:

**Bước 1 — mỗi ô đo (một metric × một miền/nhóm), chỉ dựa vào khoảng CI 95% `[lo, hi]`:**

| Dạng ô | `ĐẠT` | `KHÔNG ĐẠT` | `CHƯA CHỨNG MINH` |
|---|---|---|---|
| Một phía "≥ m" (B1–B4, C4a) | `lo ≥ m` | `hi < m` | còn lại (CI cắt qua m) — kể cả khi điểm ước lượng đã ở phía sai của m |
| Vượt trội "> 0" (C1, C2) | `lo > 0` | `hi ≤ 0` | còn lại |
| Hai phía "trong ±δ" (C4b, tham khảo) | `−δ ≤ lo` **và** `hi ≤ δ` | `lo > δ` **hoặc** `hi < −δ` | còn lại |
| Không có CI (A1, A3, A4) | số đo thoả mốc | số đo trượt mốc | — |

Ô chưa tính được metric/CI ⇒ `CHƯA ĐO` (ghi lệnh còn thiếu). Riêng **cổng B/C**: ô chỉ có số 1 fold,
hoặc CI tính trên họ checkpoint khác bản ship (phía student) ⇒ hạ xuống `CHƯA CHỨNG MINH`. Quy tắc
"1 fold" **không** áp cho cổng A — cổng A vốn được chấm trên đúng một fold ship.

**Bước 2 — gộp các ô thành nhãn của cổng** (B1 có 2 metric; C2 có 3 miền; C4a có 3 nhóm), ưu tiên
từ trên xuống: có ô `KHÔNG ĐẠT` ⇒ cổng `KHÔNG ĐẠT` · có ô `CHƯA ĐO` ⇒ `CHƯA ĐO` · có ô
`CHƯA CHỨNG MINH` ⇒ `CHƯA CHỨNG MINH` · mọi ô `ĐẠT` ⇒ `ĐẠT`.

**Bước 3 — mốc chưa chốt:** nếu mốc của cổng còn `ĐỀ XUẤT` (§1), nhãn ở bước 2 được ghi là
"<nhãn> *so với mốc đề xuất*" và cổng mang thêm cờ `CHƯA CÓ TIÊU CHÍ CHỐT`.

**Bước 4 — phán quyết tổng**, trên các cổng bắt buộc (luật gộp §2), ưu tiên từ trên xuống:

1. `KHÔNG ĐẠT YÊU CẦU` — có ít nhất một cổng bắt buộc `KHÔNG ĐẠT` **với mốc ĐÃ CHỐT**.
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
| 16 | "Student không kém teacher / ngang teacher ⇒ vượt teacher" | tiêu chí 2 đòi **vượt** (cận dưới Δ > 0), không phải "không kém" | C2 theo luật một phía m = 0 |
| 17 | "Tổng thể công bằng / AUC Fitzpatrick đạt ⇒ hoạt động tốt trên mọi tông da" | số gộp che nhóm yếu | C4a trên **từng** nhóm tông |
| 18 | So nhiều ứng viên trên HAM/Fitz, giữ cái đạt, rồi báo "đạt trên HAM/Fitz" | HAM/Fitz đã thành tập phát triển | chỉ chấm một ứng viên định trước; nếu không ⇒ khai post-hoc (§2.0) |

## 5. Khối bắt buộc trong mọi báo cáo có phán quyết "đạt / chưa đạt"

```
### Cổng chấp nhận (theo .claude/skills/eval-results/reference/acceptance-gates.md)
Model được chấm: <run-dir · fold · checkpoint · splits v1/v2>
Trạng thái mốc: <ĐỀ XUẤT | ĐÃ CHỐT ngày …>
| Cổng | Metric | Mốc | Giá trị [CI 95%] | Nguồn (file:line) | Nhãn |
|---|---|---|---|---|---|
| A1 … C4 | … | … | … | … | ĐẠT / KHÔNG ĐẠT / CHƯA CHỨNG MINH / CHƯA ĐO / CHƯA CÓ TIÊU CHÍ CHỐT |
Hành vi tại ngưỡng val (theo miền): <sens / spec / số ảnh lành bị gắn cờ>
Sáu tiêu chí (§2.0): <tiêu chí 1–6 → nhãn của cổng tương ứng>
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
  **đã được tác giả chốt** 01/10/2026 tối (post-hoc); "vượt qua teacher" → vượt trội có ý nghĩa `lo > 0` (C2,
  metric ΔAUPRC đã chốt, cách hiểu còn đề xuất) và "hoạt động tốt trên các tông da" → mỗi nhóm đạt sàn 0,47
  (C4a) vẫn chờ tác giả chốt (§1).
- Con số "~0,85" (sàn đoán nguồn ảnh trên test v2): tính tay trong lượt kiểm chéo, chưa có artifact.
- "205/208 ảnh PAD lành bị gắn cờ": nguồn là brief item 2/3 (`:12`) và memory, số của **một** checkpoint.
