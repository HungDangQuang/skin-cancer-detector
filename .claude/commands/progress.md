---
description: Tiến độ training trên các server (fold, % , ETA, RAM/VRAM) — mặc định tất cả server
argument-hint: "[host ...]   ví dụ: vast  |  vast vastnew  |  (bỏ trống = tất cả)"
allowed-tools: Bash(bash run/progress_all.sh:*)
---

## Trạng thái hiện tại của các job training

!`bash run/progress_all.sh COLOR=0 HOSTS="$ARGUMENTS"`

---

Dựa trên output ở trên (đã là dữ liệu thật, **không chạy lại script**), trả lời bằng tiếng Việt:

1. **Bảng tóm tắt 1 dòng/job**: server · teacher → student · fold hiện tại/tổng · epoch · % job · ETA.
2. **Cảnh báo nếu có** — chỉ nêu khi thật sự xuất hiện trong output:
   - job `STALLED` (log không đổi > 10 phút) hoặc không có job nào chạy trên một server;
   - VRAM gần hết (còn < 2 GB trống) hoặc disk > 90%;
   - `val_pauc` epoch cuối tụt rõ so với các job khác, hoặc loss = `nan`.
3. **Còn thiếu gì để xong**: từ bảng run-dir cuối output, nêu run nào chưa đủ 5/5 fold và ước tính khi nào xong.

Ngắn gọn — không lặp lại nguyên văn output, không phân tích chất lượng model (việc đó dùng skill `eval-results` sau khi có `test_metrics.json`).

Ràng buộc:
- Đây là lệnh **chỉ đọc**. Không được launch job, không `kill`, không sửa file, không ssh làm gì khác.
- Nếu một server báo `UNREACHABLE`, chỉ report — không tự động thử lại hay đổi host.
- ETA trong output giả định chạy đủ số epoch; early stopping (patience 10) thường kết thúc sớm hơn → nói rõ đó là cận trên.
