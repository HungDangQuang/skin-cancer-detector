---
name: acceptance-gates-history
description: Nhật ký quyết định của cổng chấp nhận — lý do, ngày, nhãn post-hoc của từng lần tác giả chốt/đổi mốc. KHÔNG dùng để gán nhãn; luật hiện hành chỉ ở acceptance-gates.md.
---

# Cổng chấp nhận — nhật ký quyết định

> Tách khỏi `acceptance-gates.md` ngày 05/10/2026 (tác giả duyệt): file luật chỉ giữ luật **đang áp dụng**;
> mọi đoạn dưới đây được chuyển **nguyên văn** từ bản 04/10/2026, không sửa chữ. Số mục `§…` bên trong các
> đoạn trích là số mục của `acceptance-gates.md` (vẫn giữ nguyên số mục sau khi tách).
>
> **Đọc file này khi** cần trả lời "mốc X chốt khi nào, vì sao, có post-hoc không", hoặc khi viết phần
> hạn chế/khai post-hoc của luận văn. **Không cần đọc** để gán nhãn một model — dùng `acceptance-gates.md`.
>
> **Khi tác giả chốt/đổi một mốc:** thêm một mục có ngày vào cuối §A (lý do, ai chốt, đã thấy kết quả của
> model nào trước khi chốt ⇒ post-hoc với model đó), rồi sửa bảng §1 của `acceptance-gates.md`.

## A. Các quyết định theo ngày (nguyên văn §1 cũ)

**⚠️ Trạng thái (cập nhật 03/10/2026): B2, B4 (mục tiêu 0,81), metric C2 (ΔAUPRC) cách hiểu C2 (không kém
teacher quá δ), tập miền C2 (PAD·Fitz·HAM) và vai bắt buộc của C2 (03/10) ĐÃ CHỐT — post-hoc; S_min 0,80 · Sp_min 0,60 · δ của C2 = 5% AUPRC teacher: CHỐT TẠM 04/10/2026 (dùng như ĐÃ CHỐT); các mốc còn lại (I-1, II-1/2/3) vẫn ĐỀ XUẤT.**
`CHƯA CÓ TIÊU CHÍ CHỐT` (§3 bước 3). Phán quyết tổng theo §3 bước 4: một cổng bắt buộc `KHÔNG ĐẠT` với mốc
đã chốt ⇒ `KHÔNG ĐẠT YÊU CẦU` dù các mốc khác còn đề xuất; nếu không có cổng như vậy ⇒ `CHƯA CÓ TIÊU CHÍ CHỐT`.
Không bao giờ viết "model đạt yêu cầu" khi còn mốc đề xuất.

**02/10/2026 (tác giả): B4 chuyển từ "bắt buộc" sang "BÁO CÁO" — post-hoc** (quyết định sau khi đã thấy B4
`KHÔNG ĐẠT` của ứng viên ship; lý do: app nhận ảnh camera, HAM10000 là dermoscopy, train không có ảnh
dermoscopy nào). B4 vẫn được đo, ghi nhãn và báo cáo như cũ, chỉ không còn quyết định chọn model. Các mốc
đề xuất còn lại giữ nguyên (tác giả: "giữ các mốc đề xuất thử xem"), kể cả tập miền PAD · Fitz · HAM của C2.
Phán quyết hiện hành: `reports/2026-10-02_acceptance_verdict_srcsamp.md` — **CHƯA CÓ TIÊU CHÍ CHỐT**
(trước 02/10: KHÔNG ĐẠT YÊU CẦU vì B4).

**03/10/2026 (tác giả): tiêu chí 2 đổi từ "student VƯỢT teacher" sang "student KHÔNG KÉM teacher quá δ" — post-hoc**
(quyết định sau khi đã thấy C2 của ứng viên ship). Lý do: mục đích của KD khi nén là giữ hiệu năng của teacher
ở mô hình nhỏ hơn (Hinton et al. 2015, arXiv:1503.02531: "compress the knowledge in an ensemble into a single
model which is much easier to deploy"); student vượt teacher là trường hợp đặc biệt, chủ yếu khi student cùng cỡ
teacher (Furlanello et al. 2018, Born-Again Networks, ICML), còn khi chênh lệch dung lượng lớn thì student thường
kém đi (Mirzadeh et al., AAAI 2020: "the student network performance degrades when the gap between student and
teacher is large"; Cho & Hariharan, ICCV 2019). Ngoài ra phép so student − teacher hiện tại lệch công thức train
(teacher thiếu sampler theo nguồn) nên "vượt" không đo được tác dụng của KD. Metric ΔAUPRC và tập miền giữ
nguyên; **δ: CHỜ QUYẾT**. Tác dụng của KD vẫn đo bằng C1 (KD − baseline). Đây là **đảo lại** quyết định 01/10
(hôm đó tác giả chọn "vượt" khi "không kém quá δ" đang được bàn). Phán quyết hiện hành ghi ở dòng dưới chấm C2
theo luật cũ (`lo > 0`); theo luật mới, C2 chưa có nhãn cho tới khi chốt δ. Với vòng chọn 2 (test P1/P2 chưa
mở) đổi này là tiên nghiệm — chốt δ **trước** khi mở test vòng 2 thì không post-hoc với P1/P2
(`docs/PREREG_CANDIDATE2_2026-10-02.md` §8).

**03/10/2026 (tác giả): đổi sang KHUNG 3 TRỤ — post-hoc** (theo review ngoài `docs/REVIEW_DANH_GIA_2026-10-03.md`
§3, đã sửa sau kiểm chéo). Từ ngày này phán quyết theo **§2.1**, không theo luật gộp cũ của §2.0. Ba trụ: I chạy
được · II giữ chất lượng · III đúng với người dùng tại **ngưỡng app đóng băng**, gồm cả ảnh điện thoại cùng nguồn
(III-a) **và** ảnh lâm sàng khác nguồn theo từng tông da (III-b). B2 (mốc 0,81 — mức đọc dermoscopy) thôi làm cổng;
B1, B3 và C4a cũ chuyển thành báo cáo / gộp vào III-b. Lý do: đo đúng thứ app làm (ngưỡng cố định, ảnh camera) và
đúng hai câu trung tâm (thu gọn + triển khai; ổn định trên ảnh camera thực tế). Ghi rõ: trụ III-b (Fitzpatrick tại
ngưỡng app) được giữ **bắt buộc** để khung mới vẫn đòi ổn định trên ảnh khác nguồn — bản đề xuất chỉ chấm trên PAD
đã bị kiểm chéo chặn vì sẽ làm ứng viên hiện tại gần như đạt. Khung mới **nới** ở ba chỗ, phải khai: III-b ban đầu chưa có
sàn độ đặc hiệu (cổng B3/C4a cũ cố định độ đặc hiệu 0,80) — **đã bù 04/10: Sp_min áp cả III-b**; III chấm trên **một** fold ship bằng Wilson CI (cổng B cũ
dùng CI 5 fold); B2 0,81 thôi làm cổng. S_min, Sp_min, δ của C2: **CHỜ QUYẾT** ⇒ phán quyết vẫn
`CHƯA CÓ TIÊU CHÍ CHỐT`.

**04/10/2026 (tác giả): CHỐT TẠM S_min = 0,80, Sp_min = 0,60 (cả III-a và III-b), δ của C2 = 5% AUPRC của chính
teacher** — tác giả sẽ review lại. Mốc "chốt tạm" được dùng **như ĐÃ CHỐT** để gán nhãn (§3), kèm chữ "(tạm)"
trong mọi báo cáo; nếu tác giả đổi, ghi ngày đổi và khai post-hoc. Với ứng viên hiện tại (P0) mọi mốc này là
post-hoc; với vòng 2 được chốt trước khi xem số test — **trừ một dòng metric test của P1 fold 4** mà một phiên
assistant đã nhìn thấy qua `tail` log lúc ~00:25 UTC 04/10, trước khi chốt (`docs/PREREG_CANDIDATE2_2026-10-02.md`
§10). Hệ quả của việc dùng mốc tạm như đã chốt: phán quyết khám phá của P0 đổi từ `CHƯA CÓ TIÊU CHÍ CHỐT` sang
`KHÔNG ĐẠT YÊU CẦU (tạm)` (III-b trượt).

Khi tác giả chốt: sửa cột "Mốc", ghi ngày chốt vào bảng dưới, đổi trạng thái thành `ĐÃ CHỐT`.
Mốc chốt sau khi đã nhìn thấy kết quả của chính model đang chấm phải được khai là *post-hoc*.

## B. Bảng trạng thái mốc đầy đủ (nguyên văn, 04/10/2026)

| Hạng mục | Trạng thái | Ngày chốt | Người chốt |
|---|---|---|---|
| **Sáu tiêu chí chọn model** (§2.0) | **ĐÃ CHỐT** — đây là danh sách *cái gì* phải đạt (tiêu chí 6 chỉ báo cáo từ 02/10/2026) | 01/10/2026 | tác giả |
| Mốc số của từng cổng (§2 A/B/C) | ĐỀ XUẤT — tác giả **đã ghi nhận** 01/10/2026, **post-hoc** (sau khi đã thấy mọi kết quả B/C của ứng viên ship, `reports/ci_gates_srcsamp_*.md`); các dòng CHỜ QUYẾT bên dưới vẫn mở; B2, B4, metric C2 đã chốt ở các dòng kế tiếp | 01/10/2026 (ghi nhận) | tác giả |
| B2: mốc quyết định = **mục tiêu ≥ 0,81** (sàn 0,47 chỉ báo cáo) | **ĐÃ CHỐT — post-hoc** | 01/10/2026 (tối) | tác giả |
| B4 (HAM10000): mốc quyết định = **mục tiêu ≥ 0,81** | **ĐÃ CHỐT — post-hoc** | 01/10/2026 (tối) | tác giả |
| B4: **vai = BÁO CÁO** (không còn bắt buộc; mốc 0,81 giữ để ghi nhãn) | **ĐÃ CHỐT — post-hoc** | 02/10/2026 | tác giả |
| C2: metric ΔAUPRC (student − teacher), tập miền PAD · Fitz · **HAM** (ISIC bỏ vì đề xuất xoay quanh ảnh kiểu điện thoại và xuyên miền); C2 vẫn **bắt buộc** | **metric = ΔAUPRC: ĐÃ CHỐT — post-hoc** (01/10/2026 tối); **tập miền (giữ HAM) và vai bắt buộc: ĐÃ CHỐT — post-hoc** (03/10/2026, tác giả xác nhận) | 01/10 (metric); 03/10 (tập miền, vai) | tác giả |
| C2: cách hiểu = **không kém teacher quá δ** (`lo > −δ`), thay cho "vượt trội `lo > 0`" | **ĐÃ CHỐT — post-hoc** | 03/10/2026 | tác giả |
| δ của C2 (biên không kém) | **CHỐT TẠM:** δ = 0,05 × AUPRC của **chính teacher trong arm**, từng miền — PAD = **các hàng PAD của test in-domain** (không phải AUPRC gộp), Fitz và HAM = **biến thể headline**; điểm ước lượng = trung bình 5 fold, checkpoint chính `predictions.csv`; **không làm tròn** khi so (vd PAD 0,7966 × 0,05 = 0,03983); đổi định nghĩa từ δ tuyệt đối sang tương đối. Teacher `efficientnetv2_m`: PAD 0,040 · Fitz 0,035 · HAM 0,025. Không có nguồn văn liệu (quy ước); tính trên phần AUPRC vượt mức đoán bừa thì 5% này tương đương lớn hơn. Post-hoc với P0 (mọi δ > 0,0068 làm P0 qua) | 04/10/2026 (tạm) | tác giả |
| C4a "tốt trên mọi tông da" | **gộp vào III-b** từ 03/10/2026 (§2.1) — mốc là S_min | 03/10/2026 | tác giả |
| δ của C4b (đề xuất 0,02 AUC — không có nguồn) | CHỜ QUYẾT (C4b chỉ báo cáo) | — | — |
| **Khung 3 trụ (§2.1) thay luật gộp của §2.0** | **ĐÃ CHỐT — post-hoc** | 03/10/2026 | tác giả |
| B2 (mốc 0,81) thôi làm cổng → tham chiếu; B1, B3 → báo cáo; C4a → gộp vào III-b | **ĐÃ CHỐT — post-hoc** | 03/10/2026 | tác giả |
| S_min (độ nhạy tối thiểu, III-a và III-b) · Sp_min (độ đặc hiệu tối thiểu, III-a **và III-b**) | **CHỐT TẠM: S_min = 0,80; Sp_min = 0,60** (tác giả sẽ review lại, nên có GVHD). Lý do: quy tắc ngưỡng nhắm độ nhạy 90% trên val, cho phép tụt tới 0,80 = không bỏ sót quá 1/5; độ đặc hiệu là phần còn lại của quy tắc đó (val fold 4 ≈ 0,67) và "lành" ở PAD gồm cả tổn thương tiền ung thư (ACK) — 0,60 = gửi đi khám tối đa 4/10 tổn thương lành. Áp Sp_min cho cả III-b để không nới | 04/10/2026 (tạm) | tác giả |
| Mốc II-3 (tỉ lệ đổi quyết định qua pipeline app) | ĐỀ XUẤT < 0,5% (review §3) | — | — |
| III-b: **giữ** mốc 0,80 theo từng tông (review v2 đề xuất D2/D3 thay bằng mốc bác sĩ 0,47 — **không** đổi; so với 0,47 chỉ thêm vào báo cáo) | **CHỐT TẠM** (như S_min) | 04/10/2026 | tác giả |
| III-b: tập chấm = **Fitzpatrick17k-C** (phần headline còn lại sau khi Abhishek, Jain & Hamarneh, Sci Data 12:196, 2025 loại ảnh gần trùng/ảnh lỗi: 3.086 / 4.320 ảnh; danh sách `reports/2026-10-04_review_v2_checks/fitz17kC_headline_image_ids.txt`) thay cho toàn bộ headline. Chỉ áp cho III-b; C2, B3, C4b vẫn trên headline | **ĐÃ CHỐT — post-hoc** (quyết sau khi đã thấy III-b của P0/P1/P2 trên headline **và** kết quả của P0 trên chính Fitzpatrick17k-C (vẫn trượt); số của P1/P2 trên Fitzpatrick17k-C cũng đã được tính trước lúc quyết (`reports/2026-10-04_review_v2_checks/output.md` (1)); nhãn của P0 không đổi). Lý do chỉ dời III-b: III-b dùng Wilson CI giả định ảnh độc lập trên một fold; C2/B3/C4b giữ headline để so được với các báo cáo đã có | 04/10/2026 | tác giả |

## B2. Sửa câu chữ trong file luật sau khi tách (05/10/2026, chờ tác giả xác nhận)

- §5 khuôn khối phán quyết: cột "Nhãn" trước liệt kê `CHƯA CÓ TIÊU CHÍ CHỐT` như nhãn thứ năm; nay ghi là **cờ** theo §3 bước 3.
- §7: "δ = 0,02: đề xuất, không có nguồn." → "δ của C4b = 0,02 …" (0,02 chỉ là δ của C4b; δ của C2 chốt tạm 04/10).
- §2.0 bước 2: xem §C dưới (nguyên văn cũ giữ ở đó).

## C. Sáu tiêu chí chọn model và luật gộp cũ (§2.0 cũ — áp đến 02/10/2026)

Tiêu đề gốc: 2.0 Sáu tiêu chí chọn model (tác giả chốt 01/10/2026; tiêu chí 2 đổi 03/10/2026) → cổng tương ứng — **lịch sử; luật hiện hành ở §2.1 (03/10/2026)**

Một model chỉ được chọn (ship / gọi là "đạt yêu cầu") khi đạt mọi tiêu chí có cột "Bắt buộc" ✅ — **năm tiêu chí 1–5**; tiêu chí 6 (B4) chỉ báo cáo từ 02/10/2026 (§1):

| # | Tiêu chí của tác giả (nguyên ý) | Cổng | Bắt buộc |
|---|---|---|---|
| 1 | Vượt qua phần evaluation — các chỉ số đề xuất | B1 · B2 · B3 | ✅ |
| 2 | Giữ được hiệu năng của teacher (đổi 03/10/2026, post-hoc — trước đó: "vượt qua teacher") | **C2** (student **không kém** teacher quá δ) | ✅ |
| 3 | Tốc độ chấp nhận được trên mobile | A1 | ✅ |
| 4 | Khả năng hoạt động trên mobile được đảm bảo | A3 · **A4** (+ A2 báo cáo) | ✅ |
| 5 | Hoạt động tốt trên các tông da khác nhau | **C4a** (mỗi nhóm tông đạt sàn) · C4b (chênh lệch — báo cáo) | ✅ C4a |
| 6 | Chỉ số evaluation chấp nhận được trên HAM10000 | **B4** | **báo cáo** (từ 02/10/2026, post-hoc — §1) |

C1 (KD > baseline) **không** nằm trong sáu tiêu chí chọn model: nó là bằng chứng *giải pháp KD có hiệu
quả* cho luận văn (câu hỏi (2) ở §0), vẫn phải báo cáo nhưng không quyết định chọn model.

Bước 2 của quy trình "Chọn ≠ phát triển" (nguyên văn §2.0 cũ; ở file luật nay viết lại thành "Các cổng bắt buộc (luật gộp §2.1) …" — diễn giải của lượt tách 05/10, chờ tác giả xác nhận):

2. Các tiêu chí bắt buộc (1–5; tiêu chí 6 chỉ báo cáo từ 02/10/2026) **chấp nhận hoặc loại** ứng viên đó, một lần.
3. Nếu bị loại: kết luận của luận văn là "ứng viên định trước KHÔNG ĐẠT YÊU CẦU ở cổng X". Muốn thử

Luật gộp cũ (nguyên văn từ mục C cũ):

- **Luật gộp cũ (theo sáu tiêu chí §2.0, áp đến 02/10/2026):** A1 + A3 + A4 + B1 + B2 + B3 + C2 + C4a đều phải `ĐẠT`. **Từ 03/10/2026 dùng luật gộp của §2.1.**
  C1, C3, C4b, A2 và (từ 02/10/2026) **B4** bắt buộc **báo cáo** nhưng không quyết định chọn.

## D. Số đo khám phá của P0 lúc chốt khung 3 trụ (nguyên văn §2.1 cũ)

- Kết quả hiện có (khám phá, ngưỡng post-hoc, fold 4): III-a độ nhạy 0,873 / độ đặc
  hiệu 0,731; III-b độ nhạy theo tông 0,604 / 0,520 / 0,524 trên headline, 0,603 / 0,503 / 0,508 trên Fitzpatrick17k-C.

Phán quyết đầy đủ: `reports/2026-10-04_acceptance_verdict_P0_3pillar.md`.
