---
name: review-thesis
description: Review one section of thesis/LUAN_VAN.md against the author's six fixed criteria — scientific register, glossary coverage, connected prose vs. bullet dumps, table/figure index coverage, internal consistency, and zero fabrication — plus a mechanical sweep that every cross-reference (Mục/Chương/Phụ lục/Bảng/Hình, embedded images) resolves and that the numbering (headings, tables, figures, MỤC LỤC, the two indexes) is dense, unique and correctly nested. Use when the user says "review phần 4.3", "soát mục 3.2.8 luận văn", "/review-thesis <mục>", or pastes a section of the thesis asking for feedback. Reports findings + proposed patches; it never edits LUAN_VAN.md until the user approves. Every draft report first goes through ONE mandatory cross-check pass — two `review-verifier` sub-agents in parallel (facts/fabrication, and patch completeness + transparency) — before it reaches the author. NOT for writing new report content (use update-report) and NOT for judging experiment results (use eval-results).
---

# review-thesis

Soát **một phần** của [thesis/LUAN_VAN.md](../../../thesis/LUAN_VAN.md) theo đúng sáu
tiêu chí do chính tác giả đặt ra. Mỗi lần gọi = một phần được soát, một mục được
ghi vào [thesis/REVIEW_LOG.md](../../../thesis/REVIEW_LOG.md).

Luận văn đã hoàn tất về nội dung (2.539 dòng, 5 chương + 2 phụ lục A–B; phụ lục C đã bỏ
13/09/2026). Việc ở đây là **soát**, không phải viết lại: giữ giọng văn của tác giả, chỉ
bản vá tối thiểu.

## Sáu tiêu chí (nguyên văn của tác giả — không diễn giải lại, không thêm bớt)

1. Văn phong viết có hợp lý theo văn phong của một bài báo cáo khoa học không?
2. Các thuật ngữ chuyên ngành trong phần đó có được thêm vào bảng thuật ngữ chưa?
3. Các đoạn văn trong phần đó có viết để có sự liên kết với nhau và không như những
   gạch đầu dòng mang tính liệt kê không?
4. Các bảng, diagram trong hình có được liệt kê trong mục lục bảng hay diagram không?
5. Nội dung trong phần đó có đồng nhất không?
6. Kiên quyết nói không với việc bịa đặt.

Cách chấm từng tiêu chí — dấu hiệu ĐẠT, dấu hiệu LỖI, mức độ nghiêm trọng — nằm ở
[reference/criteria.md](reference/criteria.md). Đọc file đó trước khi chấm.

## Quy trình (6 bước, không bỏ bước nào)

### 1. Chốt phạm vi

Người dùng nói "review phần 4.3" → phần đó là từ tiêu đề `## 4.3` tới tiêu đề cùng
cấp hoặc cao hơn kế tiếp. Nếu chỉ nói "chương 4" thì hỏi lại muốn soát cả chương
(hơn 500 dòng, nên tách) hay một mục. Nếu mơ hồ, chạy:

```bash
python3 .claude/skills/review-thesis/scripts/section_audit.py --list
```

### 2. Chạy lượt soát cơ học (kèm kiểm tham chiếu + đánh số)

```bash
python3 .claude/skills/review-thesis/scripts/section_audit.py 4.3
python3 .claude/skills/review-thesis/scripts/section_audit.py 4.3 --numbers-context
python3 .claude/skills/review-thesis/scripts/section_audit.py --numbering   # toàn văn
```

Script chỉ dùng thư viện chuẩn — **chạy được trên Mac**, không đụng tới `.venv-linux`
(xem `CLAUDE.md` mục "Local environment ≠ runtime environment"). Nó không phán xét;
nó gom bằng chứng:

| Mục in ra | Phục vụ tiêu chí |
|---|---|
| `[3] CẤU TRÚC ĐOẠN` — số khối văn xuôi / gạch đầu dòng, khối gạch đầu dòng thiếu câu dẫn hoặc câu chốt, đoạn mở đầu không có từ nối | 3 |
| `[4] BẢNG & HÌNH` — mọi `Bảng N.M` / `Hình N.M` được nhắc, có trong danh mục chưa, caption có khớp danh mục không, bảng markdown nào chưa đánh số | 4 |
| `[2] THUẬT NGỮ` — thuật ngữ tiếng Anh đã có trong bảng thuật ngữ (kèm bản dịch đang dùng) và ứng viên **chưa** có | 2, 5 |
| `[6] SỐ LIỆU` — mọi dòng có số; `--numbers-context` chỉ ra chỗ khác trong luận văn cũng nhắc con số đó | 5, 6 |
| `[7] THAM CHIẾU CHÉO` — mọi `Mục/Chương/Phụ lục/Bảng/Hình` và mọi ảnh nhúng mà phần này trỏ tới, kèm **tiêu đề đích**; và mọi nơi khác trỏ NGƯỢC vào phần này | 4, 5 |
| `[8] ĐÁNH SỐ` — số hiệu tiêu đề (liên tục, đúng cấp, có mục cha), số hiệu bảng/hình trong chương, cột "Mục"/"Nguồn tệp" của danh mục, và MỤC LỤC (tiêu đề + anchor) | 4, 5 |

`--numbering` chạy đúng các phép kiểm `[7]`/`[8]` nhưng trên **toàn văn** và không cần
chỉ định mục — dùng nó sau mỗi lần chèn/xoá/đổi số một mục hay một bảng, vì một thao tác
như vậy làm hỏng tham chiếu ở những phần không ai đang soát. Nó **thoát với mã 1** khi
còn phát hiện (0 khi sạch), nên dùng được làm cổng kiểm tra trước khi giao bản luận văn.

**Phân giải được ≠ trỏ đúng chỗ.** Script chỉ khẳng định mục đích *tồn tại*; nó in kèm
tiêu đề đích để người soát đọc và tự trả lời câu hỏi thật: *nội dung ở đó có đúng là thứ
câu này hứa không*. Một tham chiếu trỏ nhầm sang mục có thật là lỗi mà script không bắt
được — xem `reference/criteria.md` tiêu chí 4.

Danh sách "chưa có trong bảng thuật ngữ" **có nhiễu** (tên riêng, tên tệp, đơn vị đo,
mảnh LaTeX). Lọc bằng mắt trước khi đưa vào báo cáo — đề xuất một thuật ngữ đã có sẵn
là lỗi của người soát, không phải của tác giả.

### 3. Đọc toàn văn phần đó

Bắt buộc. Script không đọc hộ được tiêu chí 1, 5, 6.

```bash
sed -n '1712,1825p' thesis/LUAN_VAN.md   # §4.3, mốc 14/09/2026 — số dòng trôi sau mỗi lần sửa
```

### 4. Verify từng con số — không có ngoại lệ

Tiêu chí 6 là tiêu chí duy nhất mà **người soát cũng có thể vi phạm**. Mọi con số
trong phần được soát phải truy được về một artifact có thật:

| Loại số liệu | Nguồn phải mở ra để đối chiếu |
|---|---|
| Kết quả một run (AUPRC, pAUC, Sens@…) | `experiments/runs/<run>/aggregated.json` hoặc `fold_*/test_metrics.json` |
| Khoảng tin cậy, Δ ghép cặp | `reports/bootstrap_ci*.md` / `.json` |
| Kết quả xuyên miền, công bằng tông da | `reports/external/<ds>/<variant>/aggregated.{json,md}` |
| Latency, kích thước `.pte`, tỉ lệ nén | `reports/benchmark/*` |
| Siêu tham số, tỉ lệ lấy mẫu, kích thước ảnh | `configs/**`, `src/**` (trích `file:line`) |
| Số ảnh, prevalence, số fold | `reports/BAO_CAO_TONG_HOP.md`, `CLAUDE.md`, memory |

Ba quy tắc cứng:

- **Không verify được ≠ đúng.** Ghi thẳng `KHÔNG VERIFY ĐƯỢC — chưa tìm ra artifact`
  thay vì lặng lẽ cho qua.
- **Không tự bịa số thay thế.** Nếu phát hiện một số sai mà chưa biết số đúng, nói rõ
  là chưa biết.
- **Chênh lệch dưới sàn nhiễu không phải lỗi.** Sàn nhiễu run-to-run là ~0,005 AUPRC
  cho một fold (`experiments/_reproducibility/README.md`); đừng bắt lỗi làm tròn.

Đây chính là `feedback_no_hallucination` áp dụng cho luận văn: trích `file:line`, thà
nói "không rõ" còn hơn đoán.

### 5. Kiểm chéo bắt buộc — một lượt, hai sub-agent

Bản nháp **không** được gửi thẳng ra chat. Ghi nó vào scratchpad của phiên, rồi spawn
**hai** instance của sub-agent
[`review-verifier`](../../agents/review-verifier.md) **song song trong một message**:

| Instance | Remit | Kiểm gì |
|---|---|---|
| 1 | `REMIT=FACTS` | mọi con số, mọi câu trích nguyên văn, mọi `file:line`, mọi khẳng định phủ định — đúng / sai / không verify được / **bịa** |
| 2 | `REMIT=PATCH` | bản vá có dán được ngay, có sửa đúng lỗi đã nêu, có kéo theo đủ chỗ phải sửa, có mang vào khẳng định mới chưa verify; và báo cáo có **minh bạch** về chỗ chưa kiểm |

Verifier là read-only, chạy trên Mac, tự mở lại nguồn — nó **không tin** citation của
bản nháp. Sau khi hai kết quả về, assistant chính đối chiếu: `BỊA`/`SAI` đã chứng minh
thì sửa bản nháp trước khi gửi; `KHÔNG VERIFY ĐƯỢC` thì xuống mục "Chưa verify được";
verifier sai thì nói rõ là sai **kèm `file:line`**, không im lặng ghi đè.

**Đúng một lượt** — không spawn lượt hai để kiểm lại bản đã sửa. Vì vậy những dòng
sửa **sau** kiểm chéo chưa được agent nào kiểm, và báo cáo **phải nói ra điều đó**.

Toàn bộ quy tắc — khi nào cổng bắt buộc, khuôn prompt spawn, cách đối chiếu bất đồng,
chi phí — ở [reference/cross-check.md](reference/cross-check.md). Đọc file đó trước
lần spawn đầu tiên.

### 6. Ra báo cáo + ghi log

In báo cáo ra chat theo khuôn ở [reference/report-template.md](reference/report-template.md),
kèm khối `### Kiểm chéo` (kết quả bước 5 — bắt buộc, kể cả khi cả hai verifier đều ĐẠT),
rồi thêm **một dòng** vào bảng trong `thesis/REVIEW_LOG.md` (trạng thái + ngày + số
phát hiện + cột `Kiểm chéo`). Không viết nội dung báo cáo vào REVIEW_LOG — file đó
là bảng theo dõi.

## Chính sách sửa: báo cáo trước, sửa sau khi duyệt

Do tác giả chốt (12/09/2026, bổ sung cổng kiểm chéo 14/09/2026):

- **Không** tự ý sửa `thesis/LUAN_VAN.md` trong lượt soát.
- Mỗi phát hiện phải kèm **bản vá cụ thể** — câu viết lại, dòng cần thêm vào bảng
  thuật ngữ, dòng cần thêm vào danh mục bảng/hình — để tác giả duyệt là áp được ngay.
- Chỉ sửa khi tác giả nói "sửa mục này" / "sửa hết". Sau khi sửa, cập nhật trạng thái
  của phần đó trong `REVIEW_LOG.md`.
- Sửa bảng thuật ngữ thì phải giữ **thứ tự bảng chữ cái trong đúng nhóm A–H**; sửa
  danh mục bảng/hình thì giữ đúng thứ tự số hiệu.
- **Đổi số hiệu là việc dây chuyền.** Trước khi đề xuất chèn, xoá hay đánh số lại một
  mục/bảng/hình, đọc danh sách "trỏ VÀO phần này" của `[7]`: bản vá phải liệt kê đủ
  mọi dòng phải sửa theo (thân bài, MỤC LỤC, danh mục bảng/hình), không chỉ chỗ đổi số.
  Chạy lại `--numbering` sau khi áp để xác nhận không còn tham chiếu gãy.
- **Báo cáo "đã sửa xong" cũng phải qua cổng kiểm chéo.** Sau khi áp bản vá vào
  `LUAN_VAN.md`, lượt kiểm chéo ở bước 5 chạy trên **bản đã áp** (không phải bản nháp):
  verifier đọc lại chính những dòng vừa sửa để xác nhận con số/câu trích trong đó đúng.
- **Không bao giờ tự bịa để lấp chỗ trống**, ở cả hai phía: không bịa số trong bản vá,
  không bịa lỗi cho báo cáo dày lên. Cổng kiểm chéo tồn tại vì lỗi này không tự thấy được.

## Ranh giới

- Một lượt = một phần. Soát cả chương trong một lượt sẽ ra báo cáo hời hợt — tách ra.
- Không đánh giá lại **kết quả thí nghiệm** (dùng `eval-results`), không viết nội dung
  mới cho báo cáo (dùng `update-report`), không đổi code (dùng `code-change`).
- Không đề xuất chạy lại thí nghiệm để "làm đẹp" một con số. Nếu số liệu yếu thì
  tiêu chí 6 đòi nói đúng cái yếu đó, không đòi che nó.
- Không đổi giọng văn của tác giả vì sở thích cá nhân. Chỉ nêu chỗ **vi phạm văn phong
  khoa học** theo `reference/criteria.md` tiêu chí 1.
