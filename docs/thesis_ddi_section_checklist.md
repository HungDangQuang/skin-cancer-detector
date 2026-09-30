# Checklist: đưa arm DDI vào luận văn

> Soạn 2026-09-26, sau khi arm DDI kết thúc và cho kết quả dương (xem
> [domain_aug_plan.md §6a](domain_aug_plan.md)). **Chưa thực hiện** — đây là danh sách việc, không
> phải bản vá.
>
> Mọi `file:line` dưới đây đã đối chiếu với `thesis/LUAN_VAN.md` bản 2.534 dòng hiện tại.

---

## 0. ⛔ Vấn đề chặn — phải quyết trước khi viết một chữ nào về DDI

**Luận văn hiện tại đứng trên `data/splits/` đã rò rỉ bệnh nhân, và không nói điều đó ở đâu cả.**

Bằng chứng, ba mảnh khớp nhau:

| # | Nội dung | Vị trí |
|---|---|---|
| 1 | Toàn chương 4 báo cáo trên **62.040 ảnh / 241 ca dương** | [LUAN_VAN.md:1328](../thesis/LUAN_VAN.md), `:1233`, `:1649`, `:1651`, `:1587`, `:1589`, `:1800`, `:1804`, và cả phần tóm tắt `:61` |
| 2 | Mục 3.3 tên là *"Chiến lược chia dữ liệu chống rò rỉ"* và `:666` khẳng định patient-disjoint là **"điều kiện bắt buộc, không phải tinh chỉnh"** | `:153`, `:666` |
| 3 | Nhưng splits sinh ra các con số đó **không gom theo bệnh nhân** — dấu vân tay kích thước fold: gom theo bệnh nhân buộc các fold val lệch **24.270** dòng, splits cũ lệch **1** dòng | `CLAUDE.md` mục "Data integrity"; `docs/domain_aug_plan.md:35-40` |
| 4 | `grep` toàn văn: **không có** chuỗi `59.093`, `24.270`, `rebuild_splits`, `2026-09-22` | kiểm 26/09 |

⇒ Luận văn đang **mô tả một thiết kế chống rò rỉ mà các con số của nó không tuân theo**. Đây là
vấn đề nghiêm trọng hơn việc thiếu mục DDI, và nó chặn mục DDI vì một lý do cơ học: arm DDI đo trên
splits **mới** (59.093 ảnh / 265 ca dương), nên nếu chèn thẳng vào chương 4 thì cùng một chương sẽ
có hai tập test khác nhau mà người đọc không được cảnh báo.

**Ba lựa chọn, phải chọn một:**

| | Phương án | Cái giá |
|---|---|---|
| **A** (khuyến nghị) | **Công khai vụ rò rỉ**: thêm một mục ở §3.3 kể đúng trình tự phát hiện, giữ nguyên chương 4 như *"kết quả trên splits v1, có rò rỉ bệnh nhân, do đó lạm phát"*, rồi thêm **một mục mới tự chứa** trình bày cả arm `domain` (âm) và arm DDI (dương) trên splits v2 sạch, kèm câu nói rõ hai bộ số không so sánh trực tiếp được | Phải viết lại phần đọc kết quả in-domain ở §4.2 và §5.2; thành thật nhưng làm luận văn mạnh hơn, vì nó cho thấy tác giả tự phát hiện và tự sửa |
| **B** | Train lại toàn bộ ma trận trên splits v2 | 140 fold-run. Không khả thi trong thời gian còn lại |
| **C** | Không nhắc gì, chèn DDI như một mục thường | **Không nên.** Hội đồng chỉ cần hỏi "tập test của mục này bao nhiêu ảnh" là lộ; và nó biến một sai sót kỹ thuật thành một vấn đề liêm chính |

Phần còn lại của checklist viết theo **phương án A**.

---

## 1. Nội dung DDI đặt vào đâu

### 1.1 Chương 2 — văn liệu

| ☐ | Việc | Vị trí |
|:--:|---|---|
| ☐ | Mục **2.4.4 "Bổ sung dữ liệu giàu ca dương"** đã tồn tại sẵn — đây đúng là chỗ neo. Thêm DDI vào đó: bộ duy nhất có ca ác tính **đã xác nhận bệnh học trên da tối**, FST cân bằng có chủ đích | [LUAN_VAN.md:923](../thesis/LUAN_VAN.md) |
| ☐ | Thêm trích dẫn bài báo gốc DDI. ⚠️ **Phải tự kiểm thư mục trước khi chèn** — dự án đã từng có **một mục TLTK bịa** bị xoá (Dhar 2024, xem memory `project_thesis_citation_audit`). Bài cần tìm: Daneshjou và cộng sự, về chênh lệch hiệu năng AI da liễu trên bộ ảnh lâm sàng đa dạng, Science Advances 2022 — **xác minh số tập/số bài/DOI từ nguồn thật**, đừng lấy từ tài liệu này | §TÀI LIỆU THAM KHẢO |

### 1.2 Chương 3 — phương pháp

| ☐ | Việc | Vị trí | Ghi chú |
|:--:|---|---|---|
| ☐ | **"Bốn bộ dữ liệu" → "năm"** — `grep -ic "bốn bộ"` = **14 chỗ**, không phải vài chỗ: `:143` + `:148` (MỤC LỤC), **`:501` (DANH MỤC BẢNG, hàng 3.1)**, `:701`, `:709`, `:711`, `:727`, `:810`, `:1008` (**tên mục 3.2.1**), `:1010`, `:1018`, **`:1020` (tiêu đề Bảng 3.1)**, `:1119` (**tên mục 3.2.6**), `:1121` | 14 dòng trên | Ripple lớn nhất về mặt cơ học — và 3 chỗ dễ quên nhất là `:143`, `:501`, `:1020` (mục lục của 3.2.1, danh mục bảng, và tiêu đề bảng). ⚠️ `:709`/`:711` là **Quyết định thứ ba — phạm vi đánh giá**: DDI là nguồn *huấn luyện*, **không** mở rộng phạm vi *đánh giá*, nên câu đó vẫn ĐÚNG và **không được** đổi thành năm |
| ☐ | **Mục mới cho DDI.** Khuyến nghị đặt **ngay sau §3.2.3 (PAD-UFES-20)** vì DDI cùng vai *nguồn huấn luyện*, không phải nguồn đánh giá như HAM/Fitz ⇒ đánh số lại §3.2.4→3.2.11 | chèn sau `:1077` (hết §3.2.3; §3.2.4 bắt đầu `:1078`) — **không** phải "sau `:1053`", đó là dòng tiêu đề | Nếu muốn tránh đánh số lại thì đặt cuối §3.2 làm §3.2.11, nhưng khi đó thứ tự đọc bị lệch khỏi logic "nguồn train rồi nguồn eval" |
| ☐ | **§3.3 — mục con mới về splits v2**: `scripts/rebuild_splits.py`, đã verify tách biệt bệnh nhân 5/5 fold, 372.242 ảnh / 2.410 bệnh nhân / 1.448 ca dương (0,389%), test 59.093 dòng / 265 dương / 399 bệnh nhân | sau `:1328` | Đây cũng là nơi thực hiện công khai của phương án A |
| ☐ | **§3.3 — cơ chế nạp DDI**: APPEND 656 dòng vào mỗi `fold_*/train_split.csv`; `test_split.csv` và cả 5 `val_split.csv` **giữ nguyên byte-for-byte** ⇒ `runs_newsplit_light` là đối chứng ghép cặp hợp lệ, chi phí 15 chứ không phải 30 fold-run | cùng chỗ | Phải nói rõ **DDI không bao giờ được chấm điểm** |
| ☐ | **§3.11 — cập nhật phần triển khai**: nêu rằng 16 `.pte` hiện có export từ checkpoint splits v1 | `:1597`–`:1628` | Xem [MOBILE_EVAL_PLAN.md §0](MOBILE_EVAL_PLAN.md) — cùng một vấn đề |

### 1.3 Chương 4 — kết quả

| ☐ | Việc | Ghi chú |
|:--:|---|---|
| ☐ | **Mục mới, khuyến nghị §4.11 "Hai cách thu hẹp khoảng cách xuyên miền: tăng cường ảnh và bổ sung dữ liệu"** — trình bày **cả hai** arm trong một mục | Vì sao một mục chứ không hai: hai arm dùng **cùng** đối chứng `runs_newsplit_light`, **cùng** cặp model, **cùng** splits v2, và trả lời **cùng** một câu hỏi bằng hai đường ⇒ đặt cạnh nhau thì `domain` âm 5/5 ô và DDI dương 5/5 ô trở thành **một cặp đối chứng sạch**, mạnh hơn hai kết quả rời |
| ☐ | Cân nhắc phương án thay thế: nhập vào **§4.6 "Kiểm chứng hai lựa chọn dữ liệu" → "ba lựa chọn"** ([:1890](../thesis/LUAN_VAN.md)) | Hợp logic vì DDI đúng là một ablation dữ liệu như §4.6.1 (PAD). Nhưng §4.6 đang đo trên splits v1 ⇒ trộn hai tập test vào một mục. **Không khuyến nghị** |
| ☐ | Câu mở đầu mục mới phải nói **ngay** rằng mọi số trong mục này đo trên splits v2 và **không** so sánh trực tiếp được với §4.2–§4.8 | Đây là điều kiện để phương án A đứng được |
| ☐ | **Dán nhãn "splits v1" cho mọi artifact dẫn xuất của chương 4** — phương án A bắt buộc: **PHỤ LỤC A** (`:2289`, và câu dẫn `:2291` "toàn bộ 19 lượt chạy trong miền" + Bảng A.1–A.8), **§4.9.2 + Hình 4.5** (`:2055`, AUPRC in-domain), **§4.10** (`:2063`, paired CI in-domain) | Đây là ripple dễ bỏ sót nhất: nếu chỉ dán nhãn ở §4.2 mà bỏ Phụ lục A thì bảng đầy đủ vẫn trình bày số v1 như số sạch |
| ☐ | **§3.11 + §4.9/§4.10** — nếu làm on-device evaluation (xem `MOBILE_EVAL_PLAN.md`) thì **phương pháp** vào §3.11 (`:1597`–`:1628`), **số liệu** vào §4.9/§4.10 | ⚠️ Đính chính: §4.9 tên thật là "**Benchmark trên thiết bị biên**" (`:2026`) và **không** chỉ có latency — nó đã có bộ nhớ (peak 208–257 MiB) và **§4.9.2 "Đánh đổi giữa độ chính xác và độ trễ"** (`:2055`) với AUPRC in-domain + **Hình 4.5** Pareto. Điều còn thiếu là số **chất lượng đo TRÊN MÁY**, không phải "số chất lượng" nói chung |

### 1.4 Chương 5 + phần đầu/cuối

| ☐ | Việc | Vị trí |
|:--:|---|---|
| ☐ | **Tóm tắt**: "Bốn kết quả chính" → năm; và con số "241 ca dương" trong tóm tắt phải sửa hoặc gắn nhãn splits v1 | `:61` |
| ☐ | **§5.1** — nếu arm DDI gắn vào một câu hỏi nghiên cứu thì phải trả lời nó ở đây | `:2117` |
| ☐ | **§5.2 Hạn chế** (`:2135`) — thêm ba hạn chế: (a) vụ rò rỉ splits v1 và phạm vi ảnh hưởng; (b) DDI **không bao giờ vào val/test** nên đóng góp chỉ đo gián tiếp; (c) `patient_id` của DDI là **một nhóm mỗi ảnh** (release không có cột bệnh nhân) — chấp nhận được **chỉ vì** DDI không vào val/test | §5.2 |
| ☐ | **§5.3 Hướng phát triển** — đưa DDI vào tập *đánh giá* (cần sinh lại splits + train lại đối chứng); mở rộng arm DDI sang cặp ship | `:2147` |
| ☐ | **Danh mục viết tắt** (A→Z): thêm **DDI** và **FST** (Fitzpatrick Skin Type). `grep "\bDDI\b\|\bFST\b"` = **0 hit toàn văn** ⇒ cả hai đều chưa có. Bảng đã có HAM10000/ISIC/PAD-UFES-20/SLICE-3D nên thêm là hợp lệ | **`:215`–`:262`** (mục "DANH MỤC CÁC KÝ HIỆU VÀ CHỮ VIẾT TẮT", bảng chữ viết tắt kết thúc ở `:262`, sau đó `:264` sang bảng ký hiệu toán học). ⚠️ **Không** phải `:300`–`:335` — vùng đó là "DANH MỤC THUẬT NGỮ CHUYÊN NGÀNH", một bảng khác |
| ☐ | **DANH MỤC BẢNG** và **DANH MỤC HÌNH**: mọi bảng/hình mới phải có mục ở đây | `:491`, `:551` |
| ☐ | **MỤC LỤC**: thêm mục mới, kiểm đánh số dày và không trùng | MỤC LỤC chạy **`:85`–`:212`**. Các dòng phải sửa: `:143`–`:148` (3.2.x), **`:191`–`:196`** (chèn §4.11 sau 4.10.2), `:198`–`:200` (5.x), `:203` (Phụ lục A nếu đổi tên) |

---

## 2. Số liệu được phép dùng — và nguồn của từng con số

Tất cả lấy từ mục **3b** của `reports/ci_ddi_*.md`; quy ước Δ = `x_*__ddi − x_*`, đối chứng là nhánh
`light`; `*` = CI 95% loại trừ 0.

| Ô | ΔAUPRC student KD | teacher | baseline |
|---|---|---|---|
| HAM10000 headline | **+0,0863 [+0,0737, +0,0979]** \* | +0,0391 \* | +0,0154 \* |
| Fitz headline | **+0,0400 [+0,0332, +0,0467]** \* | +0,0233 \* | +0,0241 \* |
| Fitz crop70 | +0,0317 \* | +0,0206 \* | +0,0106 \* |
| Fitz crop50 | +0,0179 \* | +0,0098 \* | +0,0070 |
| Fitz with_non_neoplastic | +0,0434 \* | +0,0175 \* | +0,0253 \* |
| In-domain | +0,0246 [+0,0060, +0,0425] \* | +0,0024 | +0,0041 |

Thêm: HAM10000 Sens@90%Spec của KD **+0,1038 [+0,0875, +0,1190]** \* (mục 3b); nhóm **da tối** Fitz
headline KD ΔAUPRC **+0,0473 [+0,0276, +0,0672]** \* — con số này ở **mục 6** (per-`tone_group`),
không phải mục 3b.

Số liệu nạp: 656 ảnh · 171 ác tính / 485 lành · FST 12/34/56 = 208/241/207 · 0 ảnh bị loại ·
positives mỗi fold +17,3%…+18,9%.

⚠️ **Chưa verify được từ Mac** (phải kiểm trên box trước khi in vào luận văn): các số liệu nạp ở
trên và khẳng định "test/val giữ nguyên byte-for-byte" — `data/splits/fold_*` và
`data/processed/ddi/` chỉ tồn tại trên server.

---

## 3. Sáu tiêu chí soát + quy định trình bày

| ☐ | Yêu cầu | Nguồn |
|:--:|---|---|
| ☐ | **Văn phong khoa học**, không liệt kê gạch đầu dòng thay cho đoạn văn; mục mới phải là **văn xuôi có liên kết** | `feedback_thesis_review_criteria` |
| ☐ | Thuật ngữ mới (DDI, FST) **vào bảng thuật ngữ**, không chỉ giải thích trong ngoặc | nt |
| ☐ | **Tiêu đề bảng ở TRÊN, tiêu đề hình ở DƯỚI**; font 13, lề trái 3,5 cm, giãn 1,5 | `docs/QUY_DINH_TRINH_BAY_LUAN_VAN.md` |
| ☐ | Công thức (nếu thêm) phải có **số hiệu**; xuất Word nuốt im lặng `\tag{}` | memory `project_thesis_docx_export` |
| ☐ | TLTK chia **nhóm ngôn ngữ** rồi alphabet (không phải APA) | `docs/QUY_DINH_TRINH_BAY_LUAN_VAN.md` |
| ☐ | Chạy skill **`review-thesis`** trên mục mới **và** trên §3.3 đã sửa, kèm `--numbering` cho toàn văn | `feedback_thesis_review_criteria` |
| ☐ | Xuất Word bằng `bash run/export_thesis_docx.sh` và **kiểm cổng đối chiếu số lượng** md↔docx | memory `project_thesis_docx_export` |

---

## 4. Những câu KHÔNG được viết

Đã có bằng chứng phản lại, hoặc vượt quá dữ liệu:

1. ❌ *"DDI làm mô hình công bằng hơn"* → chỉ đo được **một** nhóm tông da trên **một** bộ đánh giá;
   nhóm dark của baseline ở crop50 còn **âm** ở Sens@90%Spec (−0,0519 \*).
2. ❌ *"mọi mô hình đều tốt lên"* → **pAUC của teacher âm có ý nghĩa** ở crop70 (−0,0027), crop50
   (−0,0032), with_non_neoplastic (−0,0087) và in-domain (−0,0029). Kết luận dương thuộc **student KD**.
3. ❌ *"DDI thu hẹp khoảng cách sáng–tối"* như một khẳng định của luận văn này → đó là điều **bài
   báo gốc** báo cáo; luận văn này đo được rằng nhóm dark hưởng lợi ở `headline`, và phải nói kèm
   tên biến thể (bài học từ arm `domain`: phát hiện theo tông da **không vững qua các biến thể**).
4. ❌ Đọc in-domain qua AUC (−0,0000) → **AUPRC là headline** ở prevalence 0,39%.
5. ❌ Gọi 656 ảnh là "tăng 656 mẫu" → với `DynamicUndersampledSampler` 1:5 thì **171 ca dương** mới
   là đại lượng có nghĩa (+17,3%…+18,9% positives mỗi fold).

---

## 5. Thứ tự làm

1. Quyết phương án ở **§0** (A/B/C). Mọi việc khác phụ thuộc bước này.
2. Kiểm lại trên box các số "chưa verify được" ở §2.
3. Viết mục công khai rò rỉ ở §3.3 + mục splits v2.
4. Viết mục DDI ở §3.2 (nguồn dữ liệu).
5. Viết mục kết quả §4.11 (cả hai arm).
6. Cập nhật tóm tắt, §5.2, §5.3, danh mục viết tắt, MỤC LỤC, hai danh mục bảng/hình.
7. Xác minh thư mục TLTK cho bài DDI **từ nguồn thật**.
8. Chạy `review-thesis` + `--numbering`, rồi xuất Word và kiểm cổng đối chiếu số lượng.
