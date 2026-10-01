# Sáu tiêu chí soát luận văn — cách chấm

Rubric cho skill `review-thesis`. Mỗi tiêu chí có: câu hỏi gốc, cách kiểm, dấu hiệu
ĐẠT, dấu hiệu LỖI, và mức độ. Mức độ dùng thống nhất ba bậc:

| Mức | Nghĩa | Ví dụ |
|---|---|---|
| **CHẶN** | Không sửa thì phần đó không nộp được | Số liệu không truy được về artifact; bảng bị nhắc nhưng không tồn tại |
| **NÊN SỬA** | Sai quy ước, người phản biện sẽ hỏi | Thuật ngữ mới chưa vào bảng; caption lệch danh mục |
| **GỢI Ý** | Cải thiện, không bắt buộc | Câu quá dài; một từ nối làm mạch văn mượt hơn |

Quy ước chung của tài liệu này (đã kiểm trên bản hiện tại, đừng "sửa" ngược lại):

- Chủ ngữ là **"luận văn"**, "nghiên cứu này", hoặc chính đối tượng kỹ thuật. **Không
  có "chúng tôi"** (0 lần trong toàn văn) — giữ nguyên.
- Số thập phân dùng **dấu phẩy** kiểu Việt: `0,6510`, `0,1851`.
- Ký hiệu 🔴 / ⚠️ được dùng **có chủ đích** trong ô bảng để đánh dấu cấm/cảnh báo (43
  dòng, đều nằm trong bảng). Không coi là lỗi văn phong. **Tiêu đề mục thì không còn
  emoji nào** — nếu gặp emoji trong một tiêu đề thì đó là ngoại lệ mới, hỏi ý tác giả
  chứ đừng tự bỏ.
- Bảng thuật ngữ index **khái niệm**, không index **tên riêng**: không có mục nào cho
  `MobileNetV4`, `ISIC 2024`, `HAM10000`. Các tên riêng được giới thiệu ở Bảng 3.1
  (bộ dữ liệu) và Bảng 3.11 (mô hình). Đừng đề xuất thêm tên riêng vào bảng thuật ngữ.

---

## Tiêu chí 1 — Văn phong báo cáo khoa học

> *Văn phong viết có hợp lý theo văn phong của một bài báo cáo khoa học không?*

**Cách kiểm:** đọc toàn văn phần đó. Script không giúp được tiêu chí này.

**Dấu hiệu ĐẠT**

- Mọi phát biểu mạnh đều đi kèm bằng chứng ngay tại chỗ: một con số, một bảng, một mục
  tham chiếu, hoặc một trích dẫn văn liệu.
- Mức độ chắc chắn khớp với bằng chứng: "có ý nghĩa" **chỉ khi** khoảng tin cậy loại
  trừ 0; khi CI chứa 0 thì viết "chưa phân biệt được với 0", không viết "không có tác
  dụng" cũng không viết "có xu hướng tốt hơn".
- Nêu cả giới hạn của chính kết quả mình vừa nêu, ở đúng chỗ nêu nó.
- Giọng khách quan, mô tả cái đã làm và cái đo được.

**Dấu hiệu LỖI**

| Lỗi | Mức |
|---|---|
| Tính từ cảm thán, marketing: "tuyệt vời", "cực kỳ", "vượt trội hoàn toàn", "hoàn hảo" | NÊN SỬA |
| Khẳng định nhân quả từ dữ liệu chỉ cho thấy tương quan | CHẶN |
| "Có ý nghĩa thống kê" mà không có CI / phép kiểm nào đứng sau | CHẶN |
| Dùng "sẽ" cho việc đã hoàn thành; trộn thì tương lai vào phần kết quả | NÊN SỬA |
| Câu dài trên ~60 từ, lồng ba mệnh đề trở lên, đọc phải quay lại đầu câu | GỢI Ý |
| Ngôn ngữ hội thoại, dấu chấm lửng tuỳ hứng, câu hỏi tu từ không được trả lời | NÊN SỬA |
| Xưng "tôi"/"chúng tôi" (lệch quy ước của chính tài liệu) | NÊN SỬA |
| Viết tắt dùng trước khi được định nghĩa lần đầu | NÊN SỬA |

**Lưu ý riêng cho luận văn này:** bốn phát biểu bị cấm nằm ở **Bảng 5.1 (Mục 5.2 Hạn
chế của nghiên cứu)** và trong `CLAUDE.md`. Ví dụ điển hình: **không được viết
"metadata có hại"** — số liệu nói metadata trơ (0/8 phép kiểm có ý nghĩa), thủ phạm là
RKD. Khi soát bất kỳ phần nào chạm tới hướng A, đối chiếu với Bảng 5.1 trước khi kết
luận. (Luận văn đang được biên tập: chương 4 nay dừng ở 4.10, phần thảo luận/hạn chế đã
chuyển sang chương 5 — nếu số hiệu lại đổi, lấy vị trí đúng bằng
`section_audit.py --list` chứ đừng tin số hiệu chép trong tài liệu này.)

---

## Tiêu chí 2 — Thuật ngữ đã vào bảng thuật ngữ chưa

> *Các thuật ngữ chuyên ngành trong phần đó có được thêm vào bảng thuật ngữ chưa?*

**Cách kiểm:** mục `[2] THUẬT NGỮ` của script, rồi lọc bằng mắt.

Bảng thuật ngữ nằm ngay sau MỤC LỤC (số dòng trôi theo mỗi lần biên tập — lấy mốc hiện
tại bằng `section_audit.py --list`), chia tám nhóm:

| Nhóm | Chủ đề |
|---|---|
| A | Y học và da liễu |
| B | Dữ liệu và tiền xử lý |
| C | Kiến trúc mạng và huấn luyện |
| D | Chưng cất tri thức |
| E | Hàm mất mát và mất cân bằng lớp |
| F | Đánh giá và kết luận thống kê |
| G | Triển khai trên thiết bị biên |
| H | Hạ tầng, công cụ và tái lập |

**Cần vào bảng:** thuật ngữ tiếng Anh chuyên ngành (khái niệm, kỹ thuật, độ đo, cấu
phần kiến trúc) mà người đọc ngoài ngành không đoán được nghĩa.

**Không cần vào bảng:** tên riêng mô hình/bộ dữ liệu/thư viện/tệp (`timm`, `.pte`,
`aggregated.json`), đơn vị đo (ms, MB, GFLOPs), mảnh LaTeX, từ tiếng Anh phổ thông.

**Dấu hiệu LỖI**

| Lỗi | Mức |
|---|---|
| Thuật ngữ chuyên ngành xuất hiện lần đầu trong phần mà không có trong bảng | NÊN SỬA |
| Bản dịch tiếng Việt trong thân bài khác bản dịch trong bảng thuật ngữ | NÊN SỬA |
| Viết tắt dùng trong thân bài nhưng bảng chỉ ghi dạng đầy đủ (hoặc ngược lại) | NÊN SỬA |
| Hai thuật ngữ khác nghĩa bị dùng lẫn (ví dụ *Inference* nhóm C vs *Statistical inference* nhóm F) | CHẶN |

**Bản vá phải nêu rõ:** thuộc nhóm nào, chèn vào giữa hai dòng nào (giữ thứ tự bảng
chữ cái), và đủ ba cột: `Thuật ngữ tiếng Anh | Nghĩa tiếng Việt | Giải thích ngắn gọn`.

---

## Tiêu chí 3 — Đoạn văn có liên kết, không phải gạch đầu dòng liệt kê

> *Các đoạn văn có viết để có sự liên kết với nhau và không như những gạch đầu dòng
> mang tính liệt kê không?*

**Cách kiểm:** mục `[3] CẤU TRÚC ĐOẠN` của script + đọc thật.

Bản hiện tại gần như **không dùng gạch đầu dòng trong thân bài** — thông tin dạng danh
sách được đưa vào bảng có đánh số. Đó là chuẩn phải giữ.

**Dấu hiệu ĐẠT**

- Mỗi đoạn có một ý chính, và câu đầu đoạn nối được với đoạn trước (bằng từ nối, bằng
  việc nhắc lại khái niệm vừa nêu, hoặc bằng một câu hỏi mà đoạn trước vừa mở ra).
- Trước mỗi bảng có **câu dẫn** nói bảng trả lời câu hỏi gì; sau bảng có **câu chốt**
  rút ra điều cần nhớ. Bảng không bao giờ đứng trơ giữa hai tiêu đề.
- Nếu buộc phải liệt kê, danh sách nằm trong bảng có số hiệu, hoặc được viết thành câu
  có trật tự ("trước hết… tiếp đó… cuối cùng").

**Dấu hiệu LỖI**

| Lỗi | Mức |
|---|---|
| Khối gạch đầu dòng không có câu dẫn phía trên hoặc câu chốt phía dưới | NÊN SỬA |
| Chuỗi đoạn rời rạc, mỗi đoạn một ý, không đoạn nào nhắc tới đoạn trước | NÊN SỬA |
| Bảng đứng ngay sau tiêu đề, không câu dẫn | NÊN SỬA |
| Đoạn chỉ gồm một câu, lặp lại y nguyên nội dung bảng ngay dưới | GỢI Ý |
| Gạch đầu dòng dùng cho nội dung đáng lẽ là bảng có số hiệu (vì nó có ≥ 2 chiều thông tin) | NÊN SỬA |

Cảnh báo "đoạn mở đầu không có từ nối" của script **chỉ là tín hiệu**. Một đoạn mở đầu
bằng danh từ khái niệm vẫn liền mạch. Đừng biến nó thành lỗi máy móc, và đừng đề xuất
nhét từ nối vào mọi đoạn — văn sẽ thành sáo.

---

## Tiêu chí 4 — Bảng và hình có trong danh mục

> *Các bảng, diagram trong hình có được liệt kê trong mục lục bảng hay diagram không?*

**Cách kiểm:** mục `[4] BẢNG & HÌNH` của script làm gần hết việc; mục `[7] THAM CHIẾU
CHÉO` và `[8] ĐÁNH SỐ` phủ nốt phần trỏ-tới-đâu và đánh-số-có-đúng-không.

Hai danh mục: `DANH MỤC BẢNG` có cột `Bảng | Nội dung | Mục`; `DANH MỤC HÌNH` có cột
`Hình | Nội dung | Nguồn tệp`. Cả hai nằm trước MỞ ĐẦU.

**Dấu hiệu ĐẠT**

- Mọi bảng markdown trong thân bài đều có caption `**Bảng N.M — …**` ngay trên nó.
  Hình thì ngược lại: ảnh nhúng `![Hình N.M — …](…png)` rồi caption **in nghiêng**
  `*Hình N.M — … Tệp nguồn: …*` ngay dưới. Hai kiểu này là quy ước của tài liệu, script
  nhận cả hai — đừng "sửa" hình thành in đậm.
- Mọi `Bảng N.M` / `Hình N.M` được nhắc đều có dòng tương ứng trong danh mục.
- Caption trong thân bài **khớp** nội dung ghi ở danh mục (cho phép caption dài hơn
  phần ghi chú trong ngoặc, nhưng ý chính phải trùng).
- Cột "Mục" của danh mục bảng trỏ đúng mục đang chứa bảng đó.
- Hình: tệp SVG được trỏ tới trong cột "Nguồn tệp" **phải tồn tại trên đĩa** — kiểm
  bằng `ls`, đây là nơi dễ lệch nhất sau khi vẽ lại hình.
- Mọi bảng/hình đều được nhắc ít nhất một lần trong văn ("Bảng 4.6 cho thấy…"). Bảng
  chưa bao giờ được nhắc là bảng thừa hoặc câu dẫn bị thiếu.

**Dấu hiệu LỖI**

| Lỗi | Mức |
|---|---|
| Nhắc `Bảng N.M` mà danh mục không có | CHẶN |
| Bảng markdown không có caption đánh số | CHẶN |
| Caption ≠ nội dung ghi trong danh mục | NÊN SỬA |
| Cột "Mục"/"Nguồn tệp" trỏ sai | NÊN SỬA |
| Tệp hình trong cột "Nguồn tệp" không tồn tại | CHẶN |
| Số hiệu nhảy cóc (4.5 → 4.7) hoặc trùng | CHẶN |
| Bảng/hình có caption nhưng **không chỗ nào trong luận văn nhắc tên nó** | NÊN SỬA |

### 4b. Tham chiếu chéo trỏ đúng chỗ, và đánh số đúng

Đây là phần dễ hỏng nhất sau mỗi lần biên tập: chèn thêm một mục làm lệch số của mọi
mục sau nó, và mọi câu "xem Mục 4.7" trong các chương khác vẫn trỏ vào số cũ. Script
kiểm bằng `[7]` (trỏ đi đâu, ai trỏ vào) và `[8]` (số hiệu, danh mục, MỤC LỤC).

**Hai câu hỏi tách bạch, đừng gộp:**

1. **Tham chiếu có phân giải được không** — mục/bảng/hình/tệp đích có tồn tại không.
   Việc này script làm hết, kết quả `✗` là lỗi chắc chắn.
2. **Tham chiếu có trỏ đúng chỗ không** — mục đích có thật sự chứa thứ mà câu văn hứa
   không. Việc này **script không làm được**: nó chỉ in tiêu đề đích ra để người soát
   đọc. "Chi tiết ở Mục 3.10" mà 3.10 nói về chuyện khác là lỗi CHẶN mà lượt cơ học
   báo `✓`.

| Lỗi | Mức |
|---|---|
| `Mục/Chương/Phụ lục N.M` được nhắc nhưng không có tiêu đề nào mang số hiệu đó | CHẶN |
| Tham chiếu phân giải được nhưng **mục đích không chứa nội dung được hứa** | CHẶN |
| Ảnh nhúng `![…](…)` trỏ tới tệp không tồn tại | CHẶN |
| Số hiệu tiêu đề nhảy cóc, trùng, hoặc không có mục cha | CHẶN |
| Số hiệu tiêu đề không khớp cấp markdown (`4.3.1` đặt ở `##`) | NÊN SỬA |
| Mục con xuất hiện trong văn bản không theo thứ tự số hiệu | NÊN SỬA |
| Tiêu đề thiếu trong MỤC LỤC, hoặc anchor trong MỤC LỤC sai | NÊN SỬA |
| Cột "Mục" của danh mục bảng trỏ sang mục không chứa caption đó | NÊN SỬA |
| Tham chiếu tới chính phần đang đọc ("xem Mục 4.3" viết trong Mục 4.3) | GỢI Ý |

**Khi đề xuất đổi số hiệu:** bản vá phải liệt kê **mọi nơi trỏ vào** (script in sẵn ở
`[7]`, tính cả các mục con), cộng dòng tương ứng trong MỤC LỤC và trong danh mục
bảng/hình. Đổi số ở một chỗ rồi để các chỗ khác trỏ vào số cũ là biến một lỗi thành
nhiều lỗi. Sau khi áp bản vá, chạy `section_audit.py --numbering` để xác nhận toàn văn
không còn tham chiếu gãy.

---

## Tiêu chí 5 — Nội dung trong phần có đồng nhất không

> *Nội dung trong phần đó có đồng nhất không?*

Ba lớp đồng nhất, kiểm cả ba:

**(a) Đồng nhất số liệu.** Một đại lượng chỉ có một giá trị trong toàn luận văn. Chạy
`--numbers-context` để thấy mọi nơi khác cùng nhắc con số đó. Chú ý cặp dễ lệch:
prevalence `0,3885%` vs cách nói tắt `0,39%` (cả hai đều đúng nếu dùng đúng ngữ cảnh —
nhưng phải nhất quán trong cùng một phần), số fold, số run, số ảnh trước/sau lọc.

**(b) Đồng nhất thuật ngữ và ký hiệu.** Một khái niệm — một cách gọi. Không lúc
"chưng cất tri thức" lúc "chưng cất kiến thức"; không lúc `pAUC@TPR≥80%` lúc `pAUC@80`
trừ khi dạng rút gọn đã được khai báo. Ký hiệu toán ($T$, $\alpha$) phải trùng với
định nghĩa ở chỗ giới thiệu nó.

**(c) Đồng nhất phạm vi và kết luận.** Câu kết của phần không được mạnh hơn dữ liệu
phần đó đưa ra, và không được mâu thuẫn với kết luận ở phần khác (đặc biệt
Chương 5 vs Chương 4, và tóm tắt đầu chương vs số liệu trong chương).

| Lỗi | Mức |
|---|---|
| Cùng một đại lượng, hai giá trị khác nhau ở hai chỗ | CHẶN |
| Kết luận của phần mâu thuẫn với Chương 5 (đặc biệt Mục 5.1 và Bảng 5.1) | CHẶN |
| Một khái niệm hai cách gọi | NÊN SỬA |
| Dạng rút gọn của một độ đo dùng mà chưa khai báo | NÊN SỬA |
| Đơn vị/cách làm tròn không thống nhất trong cùng một bảng | NÊN SỬA |

---

## Tiêu chí 6 — Kiên quyết nói không với việc bịa đặt

> *Kiên quyết nói không với việc bịa đặt.*

Tiêu chí này ràng buộc **cả hai phía**: văn bản không được bịa, và người soát cũng
không được bịa ra phát hiện.

**Phía luận văn — mỗi loại phát biểu, một nguồn bắt buộc:**

| Phát biểu | Phải mở file nào ra để xác nhận |
|---|---|
| Số kết quả của một run | `experiments/runs/<run>/aggregated.json`, `fold_*/test_metrics.json` |
| Khoảng tin cậy / Δ ghép cặp | `reports/bootstrap_ci*.md`, `.json` |
| Kết quả HAM10000 / Fitzpatrick17k | `reports/external/<ds>/<variant>/aggregated.{json,md}` |
| Latency, kích thước, tỉ lệ nén | `reports/benchmark/*` |
| Siêu tham số, kiến trúc, tỉ lệ lấy mẫu | `configs/**`, `src/**` — trích `file:line` |
| Quy mô dữ liệu, prevalence, số fold | `reports/BAO_CAO_TONG_HOP.md`, `CLAUDE.md` |
| Con số của công trình khác | Mục TÀI LIỆU THAM KHẢO + đúng bài báo đó |

**Dấu hiệu LỖI**

| Lỗi | Mức |
|---|---|
| Con số không truy được về artifact nào | CHẶN |
| Trích dẫn văn liệu không có trong danh mục tham khảo | CHẶN |
| So sánh số của luận văn với số của bài báo khác mà **không cùng thang** (khác tập test, khác prevalence, khác định nghĩa metric) | CHẶN |
| Khẳng định một thí nghiệm "đã chạy" trong khi run-dir không tồn tại | CHẶN |
| Nội suy một con số chưa đo ("ước tính khoảng…") mà không nói rõ là ước tính | CHẶN |
| Câu "mô hình đạt yêu cầu / đủ tốt / dùng được trên điện thoại / sẵn sàng triển khai" không đi qua `.claude/skills/eval-results/reference/acceptance-gates.md` (mốc đã chốt, cận CI, tách miền), hoặc suy nó từ "KD tốt hơn baseline" / "điện thoại = máy chủ" / số in-domain gộp hay splits v1 | CHẶN |

**Phía người soát — ba điều tuyệt đối không làm:**

1. Không đoán một con số là đúng vì "nhìn hợp lý". Không mở được artifact thì ghi
   `KHÔNG VERIFY ĐƯỢC`.
2. Không bịa số đúng để thay số sai. Phát hiện sai mà chưa biết đúng là gì thì nói vậy.
3. Không bịa ra lỗi để báo cáo trông dày dặn. Phần viết tốt thì kết luận là ĐẠT.

**Không phải lỗi:** chênh lệch nhỏ hơn sàn nhiễu run-to-run ~0,005 AUPRC cho một fold
(`experiments/_reproducibility/README.md`). Đừng bắt lỗi làm tròn ở chữ số thứ tư.
