# Cổng kiểm chéo — một lượt, hai sub-agent, trước khi báo cáo tới tác giả

Do tác giả chốt **14/09/2026**: bản nháp báo cáo **không được gửi thẳng**. Trước khi in
ra chat, nó phải đi qua **đúng một lượt** kiểm chéo bằng sub-agent
[`review-verifier`](../../../agents/review-verifier.md).

Lý do: tiêu chí 6 ("kiên quyết nói không với việc bịa đặt") ràng buộc **cả người soát**.
Người soát cũng trích sai một chữ, cũng gán một con số cho artifact không chứa nó, cũng
viết một bản vá "đẹp" mà kèm theo một khẳng định mới chưa verify. Một lượt đọc lại của
chính mình không bắt được những lỗi đó — chúng nằm đúng ở chỗ mình đã tin là đúng.

## Khi nào cổng này bắt buộc

| Trường hợp | Cổng |
|---|---|
| Lượt soát một mục luận văn (skill này) | **Bắt buộc**, luôn luôn |
| Câu trả lời có số liệu kết quả, hoặc trích `file:line`, hoặc kèm bản vá/đoạn dán được | **Bắt buộc** |
| Một QA mới hoặc QA cập nhật (`answer-qa`, loại B) | **Bắt buộc** — chạy trên bản nháp trong scratchpad, **trước** khi ghi vào `QA/` |
| Đã áp bản vá vào `LUAN_VAN.md` rồi, báo lại "đã sửa xong" | **Bắt buộc** — kiểm bản đã áp, không kiểm bản nháp |
| Câu hỏi thuần thao tác ("file này ở đâu", "chạy lệnh nào") | Không — nói rõ là không, đừng ngầm bỏ |

Trong mọi trường hợp: **không bịa đặt**, dù có cổng hay không. Cổng là lưới an toàn
thứ hai, không phải giấy phép cho lượt đầu cẩu thả.

## Bốn bước

### A. Ghi bản nháp ra file (không ghi vào project)

Bản nháp đi vào **scratchpad của phiên** (đường dẫn nằm trong system prompt, dạng
`/private/tmp/claude-501/.../scratchpad/`), **không** vào `thesis/` hay `reports/` —
nó là file tạm, không phải sản phẩm:

```
<scratchpad>/review_draft_<mục>.md
```

Bản nháp phải đầy đủ đúng như sẽ gửi tác giả (theo `report-template.md`), kể cả mục
"Chưa verify được". Gửi cho verifier một bản rút gọn là tự vô hiệu hoá cổng.

### B. Spawn HAI instance song song — trong **một** message

Hai remit, hai instance, chạy cùng lúc (`run_in_background: false` — câu trả lời phụ
thuộc trực tiếp vào kết quả, và không có việc gì hữu ích để làm trong lúc chờ):

| Instance | Remit | Trả lời câu hỏi |
|---|---|---|
| 1 | `REMIT=FACTS` | Mọi số/câu trích/`file:line`/khẳng định phủ định có đúng không, có bịa không |
| 2 | `REMIT=PATCH` | Bản vá có đủ thông tin, có sửa đúng lỗi, có kéo theo đủ chỗ phải sửa, và báo cáo có minh bạch về chỗ chưa kiểm |

Prompt cho mỗi instance phải có đủ. **Loại A — lượt soát một mục luận văn:**

```
REMIT=FACTS   (hoặc REMIT=PATCH)
Loại bản nháp: A — lượt soát mục luận văn
Bản nháp: <đường dẫn TUYỆT ĐỐI trong scratchpad>
Phần được soát: §<N.M> — <tiêu đề> · thesis/LUAN_VAN.md dòng <a>–<b>
Artifact bản nháp tự nhận đã đối chiếu: <liệt kê đường dẫn>
Rubric: .claude/skills/review-thesis/reference/criteria.md
Khuôn báo cáo mà bản nháp phải tuân theo: .claude/skills/review-thesis/reference/report-template.md
```

**Loại B — bản vá code/docs/workflow, hoặc câu trả lời có số liệu** (không có §N.M, không có
`criteria.md` nào áp được — nếu bỏ trống hai trường này mà không nói, verifier sẽ bắt lỗi
"thiếu sáu tiêu chí" cho một bản vá không phải luận văn, tức bịa lỗi):

```
REMIT=FACTS   (hoặc REMIT=PATCH)
Loại bản nháp: B — bản vá <n> file / câu trả lời
Bản nháp: <đường dẫn TUYỆT ĐỐI trong scratchpad>
Yêu cầu gốc của user (TRÍCH NGUYÊN VĂN): "<…>"
File đã tạo/sửa: <liệt kê>
Thước đo "đủ": từng mệnh đề trong yêu cầu gốc + quy tắc cứng ở CLAUDE.md
Được phép dùng git chỉ-đọc (git status --porcelain / git diff / git show) để tách
thay đổi của lượt này khỏi thay đổi còn tồn từ phiên trước.
```


**Agent mới chỉ được nạp khi khởi động phiên.** `.claude/agents/review-verifier.md` vừa tạo
hay vừa sửa thì phiên đang chạy **chưa spawn được** bằng `subagent_type: review-verifier`
(xem `.claude/agents/README.md` mục "Adding or tuning an agent"). Trong phiên đó, spawn
`general-purpose` và mở đầu prompt bằng: *"Đọc `.claude/agents/review-verifier.md` và làm
đúng theo đó, REMIT=…"* — cùng hợp đồng, chỉ khác đường vào. Phải nói rõ với tác giả là
đã dùng lối tạm này, vì agent tạm không bị giới hạn `tools:` read-only của file agent.

**Hai instance không thấy nhau.** Đó là chủ đích: hai góc độc lập trên cùng một bản
nháp, rồi assistant chính đối chiếu. Đừng chuyển kết quả của instance này sang instance
kia rồi spawn thêm lượt nữa.

### C. Đối chiếu (việc của assistant chính, không uỷ quyền)

1. **`BỊA` hoặc `SAI` đã được chứng minh → sửa bản nháp trước khi gửi.** Không có ngoại lệ.
2. **`KHÔNG VERIFY ĐƯỢC` → xuống mục "Chưa verify được" của báo cáo**, không âm thầm bỏ.
3. **Verifier nói bỏ sót → thêm phát hiện đó vào báo cáo**, kèm nguồn, sau khi tự mở
   nguồn kiểm lại (verifier cũng có thể sai).
4. **Verifier sai thì nói là sai** — nhưng phải nói kèm `file:line` chứng minh, và phải
   nói ra cho tác giả biết là đã có bất đồng, không im lặng ghi đè. Hai bất đồng hay gặp:
   verifier báo `BỊA` cho một con số nằm ở artifact khác nó chưa mở, và verifier đội mức
   một `GỢI Ý` lên `CHẶN`.
5. **Đúng một lượt.** Không spawn lượt hai để "kiểm lại bản đã sửa". Hệ quả phải nói
   thẳng trong báo cáo: **những dòng sửa SAU kiểm chéo chưa được agent nào kiểm** — ghi
   rõ là đã sửa sau kiểm chéo (xem mục D). Đây là chỗ minh bạch quan trọng nhất của
   cả cổng này; ỉm nó đi là biến cổng thành trang trí.

### D. Báo cáo phải hiện cổng ra cho tác giả thấy

Thêm khối `### Kiểm chéo` vào cuối báo cáo (khuôn ở `report-template.md`). Tối thiểu:
bao nhiêu khẳng định đã kiểm / tổng, hai phán quyết, verifier bắt được gì, mình đã sửa
gì sau đó, và **dòng nào chưa được kiểm chéo vì sửa sau**.

Ghi thêm vào cột `Kiểm chéo` của `thesis/REVIEW_LOG.md`: `FACTS <phán quyết> · PATCH
<phán quyết>` (ví dụ `FACTS ĐẠT · PATCH SỬA LẠI(2)`).

## Chi phí và giới hạn

- **Hai spawn cho mỗi lượt soát.** Mỗi spawn là một cold start, phải tự đọc lại mục
  luận văn và các artifact. Đó là giá của cổng — đừng bù bằng cách rút ngắn bản nháp.
- Verifier là **read-only** và **chỉ chạy trên Mac**: nó không train, không eval, không
  sửa file. Một con số chỉ tồn tại trên server thì cả hai bên đều chỉ có thể kết luận
  `KHÔNG VERIFY ĐƯỢC` — và báo cáo phải nói vậy.
- Verifier **không** thay `section_audit.py`. Lượt cơ học (bước 2 của skill) vẫn phải
  chạy trước; verifier kiểm **kết luận**, không phải chạy lại lượt quét.
- Đừng dùng cổng này để soát một mục luận văn mới — đó là việc của skill `review-thesis`
  ở lượt chính. Verifier chỉ soát **bản nháp**.
