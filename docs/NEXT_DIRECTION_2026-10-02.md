# Hướng tiếp theo sau phán quyết "KHÔNG ĐẠT YÊU CẦU" (02/10/2026)

> 📋 **Theo dõi việc: `docs/PROGRESS.md`** — phân tích các hướng để tác giả chọn; hướng H3 đang hoãn (S1 trong PROGRESS). Không cập nhật trạng thái ở đây.

> **Cập nhật 02/10/2026 (tối):** tác giả chọn **H2** — B4 chuyển sang báo cáo (post-hoc), vẫn đo. Phán quyết ứng viên
> hiện tại giờ là CHƯA CÓ TIÊU CHÍ CHỐT. H3 (dermoscopy) tạm không làm. Bước tiếp theo: vòng chọn thứ hai với
> hai cặp teacher–student mới — `docs/PREREG_CANDIDATE2_2026-10-02.md`.

> Đầu vào: `reports/2026-10-02_acceptance_verdict_srcsamp.md`. Các lựa chọn đánh số H1–H4 (không liên quan tới
> mục "B" mà tác giả đã duyệt — mục đó là app config + hướng dẫn L3). Văn bản này **đề xuất**; mọi lựa chọn là
> của tác giả. Chưa train hay chạy gì theo văn bản này.

## 1. Tình trạng

| Cổng | Nhãn | Khoảng cách tới mốc |
|---|---|---|
| **B4 HAM10000** sens@spec80 | **KHÔNG ĐẠT** (mốc đã chốt 0,81) | 0,7259 [0,7018, 0,7508]: cận trên thiếu ~0,06 |
| B2 PAD sens@spec80 | CHƯA CHỨNG MINH (mốc đã chốt 0,81) | 0,8180 [0,7406, 0,8786]: điểm ước lượng đã vượt, CI rộng vì PAD test chỉ 397 ảnh |
| B1 ISIC pAUC | CHƯA CHỨNG MINH so với mốc đề xuất | cận dưới 0,1418, thiếu 0,0002 |
| B3 Fitzpatrick | CHƯA CHỨNG MINH so với mốc đề xuất | cận dưới 0,4699, thiếu 0,0001 |
| C2 student − teacher ΔAUPRC | CHƯA CHỨNG MINH | PAD vượt; Fitz, HAM chứa 0 |
| C4a | CHƯA CHỨNG MINH so với mốc đề xuất | nhóm trung bình 0,4473 [0,4077, 0,4861] |

**Chỉ B4 làm hỏng phán quyết.** Các cổng còn lại chưa chứng minh được, nhưng cũng chưa trượt.

## 2. Ràng buộc phải giữ

1. **Cấm đưa HAM10000 vào train**, kể cả gián tiếp (tác giả, 29/09). Một hướng được chọn **từ phân tích lỗi
   trên HAM** đã dùng HAM làm tập phát triển, nên phải khai **post-hoc** và xác nhận trên một tập dermoscopy
   **khác, chưa đụng**.
2. Mọi tập kiểm hiện có (test in-domain, HAM, Fitzpatrick) **đã được nhìn**. Ứng viên kế tiếp là ứng viên
   thứ hai và phải khai số lần đã thử (`acceptance-gates.md` §2.0 bước 3).
3. Dữ liệu cũ: không chạy `prepare`; `data/splits` phải được sao lưu ngay khi thay đổi (`CLAUDE.md`).

## 3. Vì sao HAM trượt — bằng chứng đang có

- Tập train **không có ảnh dermoscopy nào**: ISIC 2024 là crop 3D-TBP, PAD là ảnh điện thoại, DDI là ảnh lâm
  sàng. HAM10000 là dermoscopy, nên đây là chênh miền thật, không phải lỗi pipeline.
- Lỗi tập trung ở hai loại lành `bkl` và `df`. AUC "mọi ca ác vs một loại lành", arm light → DDI:
  bkl 0,561 → 0,607 · df 0,515 → 0,521 (gần đoán mò); nv 0,820 → 0,861. **Số tính ad-hoc ngày 29/09, chưa
  có CI, chưa lưu thành artifact** (memory `project_ham_bkl_df_bottleneck`). Bản cũ trên splits v1
  (`reports/2026-08-23_external_evaluation.md:250-251`) cũng cho specificity rất thấp ở hai loại này.

## 4. Các lựa chọn

| | Lựa chọn | Làm gì | Ưu | Nhược / rủi ro |
|---|---|---|---|---|
| **H1** | **Ghi nhận và kết thúc** | Luận văn báo ứng viên KHÔNG ĐẠT ở B4, phân tích nguyên nhân (§3), nêu hướng mở | Trung thực, không tốn máy, không phát sinh post-hoc mới | Không có model "đạt" |
| **H2** | **Xét lại phạm vi tiêu chí 6** | Nếu app chỉ nhận ảnh camera (không kính dermoscopy), HAM là miền nằm ngoài sản phẩm. Tác giả có thể đổi vai của B4 từ "bắt buộc" sang "báo cáo" | Khớp phạm vi sản phẩm | Đổi tiêu chí **sau khi** thấy kết quả: phải khai rõ, và người chấm có thể coi là nới luật. `acceptance-gates.md` §2 mục C ghi "Đừng nới luật cho vừa" |
| **H3** | **Thêm dữ liệu dermoscopy không phải HAM vào train** | Một arm mới: thêm một nguồn dermoscopy có **cả hai lớp** (ác và lành, gồm SK/DF), kiểm chống trùng với HAM, train lại teacher + student 5 fold, chấm lại toàn bộ cổng, rồi xác nhận trên một tập dermoscopy thứ hai chưa đụng | Đánh trúng nguyên nhân §3 | Post-hoc (chọn từ lỗi trên HAM); cần tập xác nhận mới; tốn máy cỡ arm DDI (teacher + student 5 fold) cộng chuẩn bị dữ liệu |
| **H4** | **Chỉ tinh chỉnh ngưỡng / hiệu chuẩn** | — | — | **Không cứu được B4**: sens@spec80 không phụ thuộc ngưỡng. Loại |

Chi tiết cần kiểm nếu chọn H3 (chưa verify, phải làm trước khi train):
- **Nguồn ứng viên:** các bộ dermoscopy công khai không thuộc HAM. Bộ lưu trữ ISIC 2018/2019 **có chứa HAM**,
  nên phải lọc theo nguồn và kiểm trùng bằng md5 điểm ảnh, như `prepare_external_data.py` đang làm cho tập ngoài.
- **Bẫy shortcut:** thêm dermoscopy chỉ ở một lớp sẽ làm "là ảnh dermoscopy" tương quan với nhãn, giống sàn
  "đoán nguồn ảnh" ISIC-vs-PAD đã gặp. Phải có cả hai lớp, với tỉ lệ gần với các nguồn khác.
- **Tập xác nhận:** cần một tập dermoscopy có nhãn, không trùng nguồn train lẫn HAM, chưa từng được nhìn.
  Không có nó thì kết quả của H3 chỉ là post-hoc trên HAM.
- **Đăng ký trước:** chốt endpoint (B4 trên tập xác nhận, và không làm xấu B2/B3) **trước** khi train.

## 5. Đề xuất

1. **Làm H1 ngay**, độc lập với lựa chọn sau: kết quả hiện tại đủ để viết thành một phát hiện trung thực.
2. **Quyết định phạm vi sản phẩm trước khi chọn H2 hay H3.** Nếu app chỉ nhận ảnh camera, H2 hợp lý hơn nhưng
   phải khai là đổi tiêu chí sau khi thấy kết quả. Nếu app cần nhận ảnh dermoscopy, đi H3, và tìm tập xác nhận
   trước khi tốn máy train.
3. Không chọn H4.

Việc cần tác giả quyết: (a) phạm vi ảnh đầu vào của app; (b) H2 hay H3; (c) nếu H3, chấp nhận chi phí và tìm
nguồn dữ liệu + tập xác nhận.
