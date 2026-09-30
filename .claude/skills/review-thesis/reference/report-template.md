# Khuôn báo cáo một lượt soát

In ra chat theo đúng khuôn này. Mục tiêu: tác giả đọc xong biết ngay **sửa gì, sửa ở
dòng nào, sửa thành gì** — không phải đọc lại một bài bình luận.

---

## Soát: §4.3 — Bằng chứng thống kê về hiệu quả chưng cất
`thesis/LUAN_VAN.md` dòng 1712–1825 · 114 dòng · soát ngày 12/09/2026

**Kết luận: CẦN SỬA** — 1 CHẶN · 3 NÊN SỬA · 2 GỢI Ý
*(hoặc: **ĐẠT** — không có phát hiện nào ở mức CHẶN hay NÊN SỬA)*

| # | Tiêu chí | Mức | Dòng | Vấn đề |
|---|---|---|---|---|
| 1 | 6 — bịa đặt | CHẶN | 1693 | Con số `0,1851` không khớp `aggregated.json` |
| 2 | 4 — danh mục | NÊN SỬA | 1652 | Caption Bảng 4.6 lệch danh mục |
| 3 | 4 — tham chiếu | CHẶN | 791 | "Mục 4.12" không tồn tại (chương 4 dừng ở 4.10) |
| … | | | | |

### Chi tiết

#### [1] CHẶN · Tiêu chí 6 · dòng 1693

**Trích:**
> …câu nguyên văn trong luận văn…

**Vấn đề:** nói rõ sai ở đâu, một đến hai câu.

**Đối chiếu:** `experiments/runs/<run>/aggregated.json` → `pauc_at_tpr80.mean = …`
(hoặc `KHÔNG VERIFY ĐƯỢC — không tìm thấy artifact tương ứng`).

**Bản vá đề xuất:**
```
…câu viết lại, đúng nguyên văn để dán đè…
```

#### [2] NÊN SỬA · Tiêu chí 4 · dòng 1652
…lặp lại cùng khuôn…

### Đã kiểm và ĐẠT

Nêu ngắn những gì đã kiểm mà không có vấn đề — để tác giả biết phạm vi đã được phủ,
không phải đoán:

- Tiêu chí 1: 23 đoạn văn xuôi, không có tính từ cảm thán, mức độ chắc chắn khớp CI.
- Tiêu chí 2: 20 thuật ngữ đã có trong bảng; 3 ứng viên còn lại là tên riêng → không cần.
- Tiêu chí 3: 0 khối gạch đầu dòng; 6 bảng đều có câu dẫn và câu chốt.
- Tiêu chí 5: 14 con số, đối chiếu chéo toàn văn không thấy mâu thuẫn.
- Tham chiếu & đánh số: 14 tham chiếu (`Mục`/`Bảng`/`Hình`/ảnh nhúng) đều phân giải
  được và **đọc kiểm thấy trỏ đúng nội dung**; số hiệu mục và bảng/hình liên tục;
  MỤC LỤC và hai danh mục khớp. 10 nơi khác đang trỏ vào phần này — giữ nguyên số hiệu.

### Chưa verify được

Liệt kê thẳng, không giấu:

- Dòng 1707: tỉ lệ nén `11,2×` — chưa mở được `reports/benchmark/…`.

### Kiểm chéo

Bắt buộc có khối này — tác giả phải thấy cổng đã chạy và bắt được gì. Không có khối này
thì coi như lượt soát chưa xong:

- **Đã kiểm:** `REMIT=FACTS` 18/18 khẳng định · `REMIT=PATCH` 6/6 bản vá.
- **Phán quyết:** FACTS `SỬA LẠI` (1 lỗi) · PATCH `ĐẠT`.
- **Verifier bắt được:** bản nháp gán `0,1826` cho `aggregated.json` của run A, nhưng số
  đó nằm ở run B → đã sửa phát hiện [1] trước khi gửi.
- **Bất đồng:** verifier báo `BỊA` cho `11,2×`; đã kiểm lại và số này có thật ở
  `reports/benchmark/<file>:<dòng>` — verifier chưa mở file đó. Giữ nguyên, ghi lại ở đây.
- **Sửa SAU kiểm chéo (chưa được agent nào kiểm):** phát hiện [1] và câu vá của nó.

---

## Quy tắc khi viết báo cáo

- **Tham chiếu: nói rõ đã kiểm tới đâu.** "Phân giải được" (script) và "trỏ đúng nội
  dung" (đọc) là hai mức khác nhau — báo cáo phải ghi rõ mức nào đã kiểm, đừng để tác
  giả hiểu nhầm là đã đọc đối chiếu trong khi mới chỉ chạy script.
- **Trích nguyên văn** câu có vấn đề. Không diễn giải rồi bắt lỗi bản diễn giải của mình.
- **Mỗi phát hiện một bản vá dán được ngay.** "Nên viết rõ hơn" không phải bản vá.
- **Không gộp nhiều lỗi vào một mục.** Tác giả duyệt từng mục một.
- **Phần viết tốt thì nói là tốt** — không bịa lỗi cho đủ số lượng (tiêu chí 6).
- Sau khi in báo cáo, thêm **một dòng** vào `thesis/REVIEW_LOG.md`. Không chép nội dung
  báo cáo vào đó.
- **Khối `### Kiểm chéo` là bắt buộc**, kể cả khi cả hai verifier đều `ĐẠT` — "không tìm
  ra lỗi" cũng là thông tin tác giả cần. Và phải ghi rõ **dòng nào sửa sau kiểm chéo**:
  cổng chỉ chạy một lượt nên những dòng đó chưa qua agent nào
  ([cross-check.md](cross-check.md) bước C).
