# NỘI DUNG SLIDE — BẢO VỆ LUẬN VĂN THẠC SĨ

> **Hướng dẫn dùng file này:** Mỗi mục `## Slide N` là một slide. Phần **Tiêu đề** là title, **Nội dung** là các bullet đưa lên slide (giữ ngắn gọn), **Ghi chú thuyết trình** là lời nói của người trình bày (không đưa lên slide). Đưa toàn bộ file này cho AI dựng slide (Gamma / Beautiful.ai / PowerPoint Copilot) và yêu cầu: "tạo slide theo từng mục, phong cách học thuật, tối giản, có biểu đồ/bảng khi được gợi ý".
>
> **Tổng: 32 slide** (+ 1 slide phụ lục tài liệu tham khảo) · Thời lượng đề xuất: 22–28 phút · Đối tượng: Hội đồng chấm luận văn thạc sĩ.
>
> **Trạng thái nguồn số liệu (cập nhật 2026-09-19):** File này thay thế toàn bộ bản cũ (từng đánh dấu SUPERSEDED khi luận văn còn ở giai đoạn đề cương, chỉ có 1 teacher và ma trận KD dở dang 20/60). Luận văn (`thesis/LUAN_VAN.md`) nay đã **hoàn tất**: **140/140 lượt huấn luyện fold-run**, ma trận đầy đủ 3 teacher × 4 student × 5 fold ở cả hai nhánh KD/baseline, cả ba tầng đánh giá (in-domain, HAM10000, Fitzpatrick17k) và benchmark Pixel 6a đã có kết quả cuối. Mọi con số trong file này trích trực tiếp từ các Bảng/Hình của `thesis/LUAN_VAN.md` (Chương 1, 3, 4, 5) và đã qua một lượt kiểm chéo độc lập đối chiếu từng số với nguồn; một vài slide ghi rõ số Bảng nguồn trong ngoặc khi cần đối chiếu nhanh, các slide còn lại có thể tra theo tên bảng/mục tương ứng ở Chương 4–5 của luận văn. Đây không còn là slide "bảo vệ đề cương" mà là slide **bảo vệ luận văn** — đổi khung trình bày từ "kế hoạch sẽ làm" sang "đã làm và kết luận được gì".
>
> **⚠️ HÌNH ĐÃ VẼ SẴN — BẮT BUỘC DÙNG, KHÔNG VẼ LẠI:** Thư mục `report_phase_1/figures/` chứa các hình SVG/PNG tự vẽ (style "soft-card") và các hình ma trận kết quả (matplotlib, 3 panel). Khi một slide ghi *"DÙNG HÌNH SẴN: `figures/<tên>`"* thì chèn đúng file đó, không tự sinh lại. Ưu tiên bản `_slide.png` (16:9) khi có; một số hình kết quả (ham_summary, fitzpatrick_summary, benchmark_session, export_parity, paired_bootstrap) chỉ có bản gốc — vẫn dùng được ở slide vì đã là bố cục nhiều panel theo chiều ngang, chỉ cần chỉnh cỡ khi dựng.

---

## Slide 1 — Trang bìa

**Tiêu đề:** PHÁT HIỆN UNG THƯ DA TRÊN THIẾT BỊ BIÊN SỬ DỤNG MÔ HÌNH HỌC SÂU KẾT HỢP CHƯNG CẤT TRI THỨC

**Phụ đề (tiếng Anh):** Knowledge-Distilled Deep Learning Models for Skin Cancer Detection on Edge Devices

**Nội dung:**
- Học viên: Đặng Quang Hưng · MSHV: 230101006 · Khóa 18 · Đợt 1
- Người hướng dẫn khoa học: TS. Nguyễn Thanh Bình
- Trường Đại học Công nghệ Thông tin — ĐHQG TP.HCM
- Luận văn thạc sĩ ngành Khoa học Máy tính · Mã số 8480101

**Gợi ý hình:** Ảnh nền tổn thương da mờ / icon smartphone + AI. Logo trường.

---

## Slide 2 — Nội dung trình bày (Agenda)

**Tiêu đề:** Nội dung trình bày

**Nội dung:**
1. Vấn đề & động lực nghiên cứu
2. Chưng cất tri thức, khoảng trống nghiên cứu & câu hỏi nghiên cứu
3. Dữ liệu — bốn bộ dữ liệu và ba thách thức
4. Nghiên cứu liên quan & phương pháp đề xuất — ma trận 12 cặp teacher–student, thiết kế đối chứng
5. Kết quả thực nghiệm — 140 lượt huấn luyện, ba tầng đánh giá độc lập
6. Triển khai trên thiết bị thật (Pixel 6a) & lựa chọn mô hình
7. Trả lời câu hỏi nghiên cứu, hạn chế & hướng phát triển

**Gợi ý hình:** Danh sách đánh số dạng timeline dọc, tô sáng mục 5–6 (kết quả + triển khai — trọng tâm của luận văn đã hoàn tất).

---

# PHẦN 1 — VẤN ĐỀ & ĐỘNG LỰC

---

## Slide 3 — Vấn đề 1: Ung thư da nguy hiểm nhưng phát hiện sớm thì cứu được

**Tiêu đề:** Vấn đề 1 — Nghịch lý melanoma: ít ca, nhiều tử vong, nhưng chữa được nếu bắt sớm

**Nội dung:**
- **~331.722** ca melanoma mắc mới mỗi năm · **~58.667** ca tử vong (GLOBOCAN 2022)
- Melanoma chỉ **~10%** số ca ung thư da nhưng gây **~80%** số ca tử vong liên quan
- Phát hiện ở giai đoạn khu trú → tỷ lệ sống 5 năm đạt **99%**
- 🎯 **Chốt vấn đề:** phần lớn tử vong do melanoma không đến từ thiếu phương pháp điều trị mà từ **phát hiện muộn**

**Gợi ý hình:** Infographic 3 khối số khổng lồ: `10% ca — 80% tử vong — 99% sống nếu sớm`. Màu đỏ cho tử vong, xanh cho 99%.

---

## Slide 4 — Vấn đề 2: Chẩn đoán truyền thống không phủ được, AI mạnh lại kẹt trên cloud

**Tiêu đề:** Vấn đề 2 — Khoảng trống tiếp cận: thiếu bác sĩ, mà AI mạnh lại phụ thuộc cloud

**Nội dung:**
- Chẩn đoán truyền thống dựa vào bác sĩ da liễu (soi da, quy tắc ABCD) → thiếu chuyên gia ở vùng khó khăn, chi phí tiếp cận cao
- CNN đạt hiệu năng **ngang 21 bác sĩ da liễu có chứng chỉ** (Esteva 2017); EfficientNet, ViT liên tục nâng trần hiệu năng
- **Nhưng** mô hình thắng cuộc ISIC 2020 là **ensemble 18 mô hình** — quá lớn để chạy trên điện thoại → buộc phải triển khai cloud:
  - ⏱ độ trễ & phụ thuộc kết nối · 🔒 rủi ro riêng tư dữ liệu y tế · 💰 chi phí vận hành theo lượt dùng
- 🎯 **Chốt vấn đề:** cần đưa AI **xuống thẳng thiết bị** (Edge AI), và điều kiện tự đặt ra: phải **đo trên chính thiết bị đích**, không chỉ đạt điểm cao trên máy chủ

**Gợi ý hình:** Sơ đồ 2 cột Cloud AI vs Edge AI; cột Cloud gắn 3 icon cảnh báo (trễ/riêng tư/chi phí), cột Edge gắn dấu tick.

---

## Slide 5 — Vấn đề 3: Nút thắt cốt lõi — nhỏ để chạy được thì lại kém chính xác

**Tiêu đề:** Vấn đề 3 — Đánh đổi Độ chính xác ↔ Kích thước/Tốc độ trên thiết bị biên

**Nội dung:**
- Mô hình gọn (EfficientNet-B0, MobileNetV3, MobileViT) chạy được trên điện thoại **nhưng suy giảm độ chính xác**
- Y tế: **bỏ sót một ca ác tính (âm tính giả)** có thể dẫn tới tử vong; một **dương tính giả** chỉ dẫn tới một lần khám xác nhận → hậu quả bất đối xứng
- ISIC 2024 dùng thước đo chính thức **pAUC@TPR≥80%** — chỉ tính vùng độ nhạy ≥80%, đúng chế độ vận hành mà một công cụ sàng lọc được phép hoạt động
- 🎯 **Câu hỏi nút thắt:** làm sao mô hình **vừa nhỏ** (chạy trên phone) **vừa không bỏ sót** ca ác tính? → **Chưng cất tri thức (Knowledge Distillation)** là hướng luận văn chọn

**Gợi ý hình:** Cái cân thăng bằng: đĩa trái "Độ chính xác / Độ nhạy", đĩa phải "Nhỏ gọn / Tốc độ"; mũi tên nối sang slide 6.

---

# PHẦN 2 — CHƯNG CẤT TRI THỨC & CÂU HỎI NGHIÊN CỨU

---

## Slide 6 — Chưng cất tri thức là gì, và nó thực sự làm gì ở bài toán một logit

**Tiêu đề:** Chưng cất tri thức — cơ chế thật, không phải "dark knowledge"

**Nội dung:**
- **KD** (Hinton 2015): mô hình *teacher* lớn hướng dẫn mô hình *student* nhỏ qua **nhãn mềm** (soft labels) thay vì chỉ nhãn cứng 0/1
- Văn liệu thường quy tác dụng của nhãn mềm cho **"dark knowledge"** — thông tin phân phối tương đối giữa các lớp *sai*
- ⚠️ **Luận văn chỉ ra: ở bài toán nhị phân MỘT logit, "dark knowledge" theo nghĩa đó KHÔNG TỒN TẠI** — nhãn mềm của teacher chỉ là một số vô hướng cho mỗi ảnh, không có "lớp sai" nào để xếp hạng
- Cơ chế thật sự: **làm mượt nhãn thích ứng theo từng mẫu** — teacher thay nhãn cứng bằng một mục tiêu mềm phản ánh độ khó của chính mẫu đó
- Dự đoán rút ra từ cơ chế này **đã được kiểm chứng định lượng** ở Chương 4 (r = −0,963, Slide 21)

**Ghi chú thuyết trình:** Đây là một trong bốn đóng góp khoa học của luận văn (Đóng góp 2a–2b), không phải kiến thức nền lấy từ sách giáo khoa. Nhấn: học viên không chỉ *dùng* KD mà còn *giải thích lại* nó đúng cho dạng bài toán này.

**Gợi ý hình:** DÙNG HÌNH SẴN: `figures/kd_flow_slide.png` — sơ đồ cơ chế KD (teacher đóng băng → nhãn mềm; student → dự đoán; nhãn cứng + nhãn mềm → hàm mất mát kết hợp → backprop chỉ student). Chú thích thêm dòng "không có 'dark knowledge' kiểu đa lớp ở đây — chỉ có một số vô hướng mỗi ảnh".

---

## Slide 7 — Khoảng trống nghiên cứu

**Tiêu đề:** Bốn khoảng trống mà văn liệu KD trong da liễu để lại

**Nội dung:**
1. Hầu như không **so sánh chính student ở hai trạng thái có/không chưng cất** — chỉ báo accuracy tuyệt đối sau KD → không tách được phần do KD mang lại
2. Khi có nhiều teacher, hoặc **gộp lại** thành một nguồn tri thức, hoặc chỉ xếp hạng theo điểm tuyệt đối cùng một miền → *"teacher mạnh hơn có dạy tốt hơn không"* và *"thứ tự teacher có đổi khi đổi miền không"* đều bỏ ngỏ
3. **ISIC 2024** — bộ benchmark lớn gần ảnh smartphone nhất — chưa được khai thác trong bối cảnh KD
4. Rất ít công trình hỏi: sau chưng cất, student có **chạy tốt hơn trên điện thoại thật** không, và số đo có thuộc đúng mô hình đã đánh giá không

**Ghi chú thuyết trình:** Bốn khoảng trống này ánh xạ trực tiếp sang bốn thành phần thiết kế của luận văn (nhánh đối chứng · ma trận 3 teacher × 4 student trên 3 tầng đánh giá · ISIC 2024 làm dữ liệu chính · export–kiểm tra tương đương–benchmark thật).

**Gợi ý hình:** 4 ô đánh số với dấu ❓, viền đứt, mỗi ô nối mũi tên sang thành phần thiết kế tương ứng.

---

## Slide 8 — Câu hỏi nghiên cứu trung tâm

**Tiêu đề:** Câu hỏi nghiên cứu — sáu câu hỏi kiểm chứng được

**Nội dung:**
> *"Liệu chưng cất tri thức có thực sự mang lại cải thiện đáng kể và nhất quán cho các mô hình gọn nhẹ thuộc nhiều paradigm thiết kế khác nhau, và chất lượng của teacher ảnh hưởng thế nào đến hiệu quả KD trên student?"*

| Mã | Câu hỏi |
|---|---|
| **Q1** | Trộn PAD-UFES-20 vào tập huấn luyện có làm mô hình tốt hơn không? |
| **Q2** | Teacher mạnh hơn có tạo ra student tốt hơn không? |
| **Q3** | Chưng cất có cải thiện student nhất quán qua các paradigm kiến trúc khác nhau không? |
| **Q4** | Student sau chưng cất có vượt được teacher không? |
| **Q5** | Nếu chỉ được triển khai một mô hình duy nhất thì chọn gì? |
| **Q6** | Tỉ lệ undersampling 1:5 có phải lựa chọn đúng không? |

- Cách trả lời khách quan: thực nghiệm đối chứng **ceteris paribus** — mỗi student chạy 2 nhánh (KD / không KD), mọi thứ khác giữ nguyên
- Toàn bộ sáu câu đã được trả lời ở Chương 4–5 (Slide 30)

**Gợi ý hình:** Highlight box cho câu hỏi lớn; bảng 6 câu hỏi bên dưới dạng 6 chip màu khác nhau.

---

## Slide 9 — Phạm vi & đóng góp của luận văn

**Tiêu đề:** Bốn quyết định phạm vi & bốn đóng góp

**Nội dung:**
- **Phạm vi (4 quyết định có chủ đích):** (1) phân loại nhị phân một logit, không đa lớp bệnh danh; (2) chỉ chưng cất theo logit (Hinton + Focal Loss), không theo đặc trưng/quan hệ; (3) đánh giá hồi cứu trên 4 bộ dữ liệu công khai, không thẩm định lâm sàng tiến cứu; (4) export FP32, không lượng tử hoá INT8
- **Bốn đóng góp:**
  1. **Công cụ** — ma trận 12 cặp (3 teacher × 4 student, 4 paradigm), 3 tầng đánh giá độc lập, kết luận bằng khoảng tin cậy bootstrap ghép cặp
  2. **Khoa học** — cơ chế KD ở bài toán một logit = làm mượt nhãn thích ứng, và dự đoán từ đó (r = −0,963) đã kiểm chứng
  3. **Khoa học** — hai câu trả lời "hiển nhiên" hoá ra sai: không có "teacher tốt nhất" độc lập miền; bất bình đẳng tông da nằm ở nhóm **trung bình**, không phải nhóm tối
  4. **Kỹ thuật** — pipeline tái lập được, cổng kiểm tra tương đương số học **cần thiết chứ không hình thức** (đã bắt một lỗi thật), đo trên thiết bị có kiểm soát nhiệt

**Ghi chú thuyết trình:** Nhấn rằng luận văn không đề xuất toán tử, kiến trúc hay hàm mất mát mới — giá trị nằm ở quy mô có kiểm soát và độ nghiêm ngặt của đánh giá.

**Gợi ý hình:** 2 cột — trái "Phạm vi" (4 khối), phải "Đóng góp" (4 khối màu khác, đánh số 1→4 theo quan hệ nhân quả).

---

# PHẦN 3 — DỮ LIỆU & THÁCH THỨC

---

## Slide 10 — Bài toán & bốn bộ dữ liệu

**Tiêu đề:** Định nghĩa bài toán & 4 bộ dữ liệu (vai trò tách bạch)

**Nội dung:**
- **Bài toán:** phân loại nhị phân — ảnh 224×224 → 1 logit → `sigmoid` → xác suất ác tính
- Ánh xạ nhãn lâm sàng: melanoma/BCC/SCC = 1 (ác tính); nevus/keratosis lành tính/dermatofibroma/vascular = 0

| Bộ dữ liệu | Số ảnh công bố | Loại ảnh | Vai trò |
|---|---|---|---|
| **ISIC 2024 SLICE-3D** | **401.059** | Non-dermoscopic (cắt từ TBP 3D) | **Huấn luyện chính** + test nội bộ |
| PAD-UFES-20 | 2.298 | Lâm sàng, chụp bằng điện thoại | Bổ sung ca ác tính + miền lâm sàng |
| HAM10000 | 10.015 | Soi da (dermoscopic) | **Chỉ** kiểm chứng chéo miền |
| Fitzpatrick17k | 16.577 | Lâm sàng (atlas, có tông da I–VI) | **Chỉ** phân tích công bằng |

- ⚠️ HAM10000 & Fitzpatrick17k **không bao giờ** dùng để train, validate hay chọn ngưỡng — thực thi bằng mã, dừng chương trình nếu phát hiện trùng lặp

**Gợi ý hình:** Bảng trên + 1 ảnh mẫu đại diện mỗi dataset.

---

## Slide 11 — ISIC 2024: vì sao là dữ liệu huấn luyện chính

**Tiêu đề:** ISIC 2024 SLICE-3D — bộ dữ liệu phù hợp nhất cho kịch bản Edge AI cộng đồng

**Nội dung:**
- **401.059** ảnh tổn thương da, cắt tự động từ ảnh **3D Total-Body Photography (TBP)** — không nguồn sáng phân cực, không tiếp xúc da → gần với ảnh chụp smartphone
- Tỉ lệ ca ác tính chỉ **~0,1%** — phản ánh đúng thực tế sàng lọc, là "điểm khó chứ không phải khuyết điểm"
- Mỗi ảnh có **53 cột metadata**, luận văn cố ý chỉ giữ 3 cột (`isic_id`, `target`, `patient_id`); **39 cột `tbp_lv_*`** bị loại vì chỉ đo được bằng thiết bị TBP 3D, không lấy được trên điện thoại; **8 cột chẩn đoán/mô bệnh học sau sinh thiết bị cấm tuyệt đối** vì rò rỉ nhãn
- 🎯 Hội đủ 3 điều kiện: ảnh gần smartphone · đủ lớn để 5-fold CV còn ý nghĩa · mất cân bằng thực tế đi kèm metric an toàn lâm sàng (pAUC@80)

**Gợi ý hình:** Donut chart phân phối lớp (benign ~99,9% / malignant ~0,1%) bên trái; bảng phân loại 53→3 cột metadata bên phải, tô đỏ nhóm 8 cột rò rỉ.

---

## Slide 12 — Ba bộ dữ liệu bổ trợ

**Tiêu đề:** PAD-UFES-20 & hai bộ đánh giá ngoài miền

**Nội dung:**
- **PAD-UFES-20** — 2.298 ảnh chụp smartphone lâm sàng thật (không thiết bị chuyên dụng): nâng prevalence từ ~0,1% lên **0,3885%**, và mang vào đúng loại biến thiên ứng dụng sẽ gặp (ánh sáng phòng khám, góc chụp tuỳ tay)
- **HAM10000** — ảnh soi da (dermoscopic), **miền ngược hẳn** dữ liệu huấn luyện → dùng để kiểm tra KD có mất tác dụng khi đổi miền không; biến thể chính giữ 1 ảnh/tổn thương → **7.470 ảnh**, 1.169 ca ác tính (15,6%)
- **Fitzpatrick17k** — bộ da liễu công khai lớn duy nhất có chú thích tông da; ảnh lâm sàng trường rộng (khác hướng HAM10000); biến thể chính **4.320 ảnh**, 2.160 ác tính (50,0%), ba nhóm: sáng 2.310 · trung bình 1.599 · tối 411
  - ⚠️ Bộ gốc chỉ cung cấp URL, **76% đã chết** → khôi phục qua mirror xác minh bằng md5-hash, đạt **99,98% độ phủ** (16.574/16.577)

**Gợi ý hình:** 3 thẻ (PAD / HAM / Fitzpatrick), mỗi thẻ 1 dòng vai trò + 1 con số nổi bật (0,3885% / 7.470 ảnh / 99,98%).

---

## Slide 13 — Ba thách thức đặc trưng & cách xử lý

**Tiêu đề:** Ba thách thức & giải pháp tương ứng

**Nội dung:**
- **1. Mất cân bằng lớp cực đoan** (prevalence 0,3885%) → accuracy vô nghĩa (đoán "toàn lành" vẫn đạt 99,61%), AUC-ROC lạc quan giả
  - → **AUPRC là chỉ số chính** (đường cơ sở ngẫu nhiên = chính prevalence), pAUC@TPR≥80% là chỉ số ISIC 2024
  - → **Undersampling động 1:5/epoch + Focal Loss** (γ=2, α=0,25)
- **2. Rò rỉ dữ liệu** → tách held-out test (~17%) **patient-disjoint trước**, rồi `StratifiedGroupKFold(K=5)`; tiền tố `pad_`/`ham_` cho `patient_id`/`lesion_id`
  - ⚠️ Đây không phải lý thuyết suông: chính dự án từng lấy val của fold 0 làm test, khiến 4 fold còn lại train trên chính dữ liệu test — lỗi đã phát hiện và sửa
- **3. Ràng buộc triển khai biên** → phải **đo trên thiết bị thật**: nền tảng thực thi có thể nới khoảng cách hai kiến trúc tới **181 lần**; điều tiết nhiệt làm chậm thêm **45–49%** sau 5 phút (Slide 28) — cả hai hiệu ứng đều không nằm trong FLOPs

**Gợi ý hình:** 3 hàng, mỗi hàng: icon (cân lệch / khóa chống rò rỉ / điện thoại) → mũi tên → giải pháp.

---

# PHẦN 4 — NGHIÊN CỨU LIÊN QUAN & PHƯƠNG PHÁP ĐỀ XUẤT

---

## Slide 14 — Bối cảnh văn liệu: 10 năm chưa hội tụ

**Tiêu đề:** Các nghiên cứu liên quan — hành trình 10 năm và các công trình KD 2024–2025

**Nội dung:**
- **2015–2019 · Đặt nền móng:** Esteva 2017 (CNN ngang bác sĩ); Hinton 2015 (KD); EfficientNet & MobileNetV3
- **2020–2021 · Mô hình lớn thống trị:** ensemble 18 mô hình thắng ISIC 2020; ViT — chính xác hơn nhưng nặng hơn
- **2022–2023 · Tìm kiến trúc cân bằng:** MobileViT; HI-MViT (F1=0,931, AUC=0,977 trên ISIC 2018)
- **2024–2025 · KD vào da liễu:** ISIC 2024 SLICE-3D công bố; các công trình KD da liễu hầu như **không có nhánh đối chứng** — báo accuracy tuyệt đối (Islam 2024: 98,75% trên HAM10000; Saha 2025: 88,6–88,9%; Winata 2025 MTAKD: 87,53% trên ISIC 2019, không so với chính student của họ; chỉ Pavel 2025 có "hybrid student baseline")
- 🎯 Các hướng "mô hình lớn chính xác" và "mô hình nhỏ triển khai được" **chưa bao giờ thực sự hội tụ** — đó là chỗ đứng của luận văn

**Gợi ý hình:** Timeline ngang 4 mốc; bảng nhỏ 4 công trình KD 2024–2025 kèm cột "có nhánh đối chứng không" (❌❌❌✅).

---

## Slide 15 — Khung thực nghiệm: 3 teacher × 4 student, 4 paradigm

**Tiêu đề:** Ma trận 12 cặp teacher–student, trải bốn paradigm kiến trúc

**Nội dung:**

| Vai trò | Model | Paradigm | Params | GFLOPs | Size FP32 |
|---|---|---|---:|---:|---:|
| Teacher | MaxViT-Base | CNN–Transformer hybrid | 118,699 M | 47,843 | 453,37 MB |
| Teacher | ConvNeXtV2-Base | Modern ConvNet + GRN | 87,694 M | 30,707 | 334,53 MB |
| Teacher | EfficientNetV2-M | CNN fused-MBConv | 52,860 M | 10,722 | 202,76 MB |
| Student | EfficientFormerV2-S2 | Hybrid attention–CNN | 12,132 M | 2,493 | 46,75 MB |
| Student | FastViT-SA12 | CNN + tái tham số hoá | 10,557 M | 2,962 | 40,41 MB |
| Student | MobileNetV4-Conv-M | CNN depthwise-separable | 8,436 M | 1,653 | 32,44 MB |
| Student | RepViT-M1.0 | CNN mang thiết kế ViT | 6,403 M | 2,214 | 24,64 MB |

- Một chuẩn đầu ra chung cho cả 7 backbone: GAP → Dropout → Dense(1) → **một logit duy nhất**; teacher **luôn đóng băng** khi distill (khoá gradient + `no_grad` + không cập nhật)
- Ghép đầy đủ 3×4 = **12 cặp**, không chọn lọc cặp "hứa hẹn" — để tỉ lệ thắng đo đúng phương pháp chứ không đo lựa chọn của người làm thí nghiệm

**Ghi chú thuyết trình:** Bảy mô hình dùng chung một cách dựng (chỉ khác tên kiến trúc + tỉ lệ dropout) nên kiến trúc là biến độc lập duy nhất — điều kiện để 140 lượt huấn luyện chỉ là 140 dòng cấu hình chứ không phải 140 lần viết code riêng.

**Gợi ý hình:** Bảng trên; bên cạnh ma trận lưới 3×4 tô đủ 12 ô.

---

## Slide 16 — Hàm mất mát chưng cất

**Tiêu đề:** Hàm mất mát KD (điều chỉnh cho mất cân bằng)

**Nội dung:**
```
L_total = α · L_hard + (1 − α) · T² · L_soft
```
- `L_hard = FocalLoss(z_student, y_true)` — γ=2,0, α=0,25 → xử lý mất cân bằng
- `L_soft = BCE(σ(z_student/T), σ(z_teacher/T))` — mục tiêu mềm, **T = 4,0**
- Hệ số **α = 0,3** → 30% nhãn cứng + 70% nhãn mềm
- Nhánh **baseline**: cùng script, chỉ đổi một cờ để **loại bỏ hẳn** teacher (không phải chỉ đặt trọng số về 0) — vì teacher hiện diện vẫn chiếm tài nguyên và tham gia huấn luyện, phá vỡ *ceteris paribus*
- Chưng cất theo **logit** (không theo đặc trưng/quan hệ) — có chủ đích: không cần lớp chiếu số chiều (điều kiện của ma trận 3×4 dị chiều) và không đụng đồ thị student (điều kiện export thiết bị)

**Ghi chú thuyết trình:** Cái giá của lựa chọn này: mỗi mẫu chỉ còn một con số, nên những gì teacher truyền được cho student bị chặn ở một đại lượng vô hướng — đây chính là lý do định lượng cho mức cải thiện "khiêm tốn" thấy ở Chương 4.

**Gợi ý hình:** Công thức lớn làm trọng tâm; tái dùng `figures/kd_flow_slide.png` bên cạnh.

---

## Slide 17 — Thiết kế đối chứng & quy mô thực nghiệm đã hoàn tất

**Tiêu đề:** Ceteris paribus, 5-fold CV, và 140 lượt huấn luyện đã XONG

**Nội dung:**
- Đơn vị so sánh: **một cặp** = lượt KD ghép **theo từng fold** với lượt đối chứng của đúng student đó (không ghép hai giá trị trung bình) — điều kiện để Δ quy về đúng một nguyên nhân
- Quy mô dữ liệu mỗi fold: test giữ lại **62.040 ảnh** (dùng chung mọi fold, mọi run) · pool huấn luyện **248.161 ảnh** · thực dùng mỗi epoch sau lấy mẫu **5.790 ảnh**
- ✅ **140/140 lượt huấn luyện fold-run hoàn tất**: 15 teacher + 15 teacher ISIC-only (ablation) + 20 student baseline + 60 KD (3×4×5) + 30 ablation (PAD-UFES-20 loại trừ + tỉ lệ lấy mẫu)
- **Kiểm định thống kê: khoảng tin cậy bootstrap ghép cặp** (B=2.000, resample trên hàng test), **thay cho paired t-test** dự kiến ban đầu — lý do: 5 fold không phải 5 mẫu độc lập, và n=5 gần như không còn lực thống kê

**Ghi chú thuyết trình:** Đây là một thay đổi phương pháp so với đề cương, và luận văn nêu rõ lý do — điểm này hội đồng hay hỏi nên cần trả lời chủ động thay vì đợi được hỏi.

**Gợi ý hình:** DÙNG HÌNH SẴN: `figures/kd_pipeline_slide.png` cho quy trình 3 bước; có thể ghép nhỏ bảng "140/140 ✅" bên cạnh.

---

## Slide 18 — Ba tầng đánh giá độc lập & các độ đo

**Tiêu đề:** Đánh giá 3 tầng độc lập — hỏi ba câu khác nhau trên ba bộ dữ liệu khác nhau

**Nội dung:**
- **(i) In-domain** — test ISIC 2024 + PAD-UFES-20 (62.040 ảnh, prevalence 0,3885%): điều kiện thuận lợi nhất, nhưng cùng nguồn ảnh với train
- **(ii) Cross-domain — HAM10000** (7.470 ảnh, prevalence 15,6%): miền ảnh **ngược hẳn** (soi da) — kiểm tra KD có mất tác dụng khi đổi miền
- **(iii) Fairness — Fitzpatrick17k** (4.320 ảnh, prevalence 50,0%): không hỏi "tốt đến đâu" mà hỏi "tốt **không đều** ở đâu" theo nhóm tông da
- ⚠️ Ba tỉ lệ ca ác tính chênh nhau hơn 2 bậc độ lớn → **AUPRC không so được giữa 3 tầng** (đường cơ sở ngẫu nhiên = chính prevalence của tầng đó)
- Bộ độ đo mỗi lượt chạy: **AUPRC** (chính) · **pAUC@TPR≥80%** (ISIC 2024) · AUC-ROC (tham khảo) · Sensitivity/Specificity/F1 (ngưỡng Youden's J) · Sens@90/95%Spec (vận hành) · TP/FP/TN/FN (quy ra số ca)

**Gợi ý hình:** DÙNG HÌNH SẴN: `figures/eval_tiers_slide.png` (Hình 4.1 của luận văn) — ba tầng, ba prevalence, cùng một bộ trọng số.

---

# PHẦN 5 — KẾT QUẢ THỰC NGHIỆM

---

## Slide 19 — Hiệu năng in-domain: teacher vs. student

**Tiêu đề:** Kết quả in-domain — student nhỏ đạt vùng độ nhạy của teacher, nhưng chưa vượt AUPRC

**Nội dung:**

**Ba teacher standalone:**
| Teacher | AUPRC | pAUC@80 | Sensitivity |
|---|---|---|---|
| MaxViT-Base | **0,6566 ± 0,0211** | 0,1830 ± 0,0025 | 0,9245 |
| ConvNeXtV2-Base | 0,6506 ± 0,0306 | 0,1822 ± 0,0021 | 0,9203 |
| EfficientNetV2-M | 0,6298 ± 0,0488 | 0,1826 ± 0,0025 | **0,9270** |

- Student KD tốt nhất mỗi hàng (Bảng 4.1–4.2, 12 tổ hợp): AUPRC cao nhất **0,6510** (FastViT-SA12 ← MaxViT), pAUC cao nhất **0,1859** (MobileNetV4 ← EfficientNetV2-M) — **11/12 ô KD vượt pAUC teacher mạnh nhất (0,1830)**
- 🎯 **Trên pAUC (vùng vận hành lâm sàng) và trong miền huấn luyện, student vượt hoặc ngang teacher. Trên AUPRC (toàn dải xếp hạng), teacher vẫn nhỉnh hơn** — hai kết luận khác nhau tuỳ chỉ số, không được gộp làm một
- Thứ tự teacher **đảo chiều** giữa hai chỉ số: EfficientNetV2-M thấp nhất AUPRC nhưng cao nhất pAUC ở cả 4 hàng student

**Ghi chú thuyết trình:** Đây là phát biểu an toàn nhất rút ra được: "ở vùng vận hành lâm sàng và trong miền huấn luyện, student đạt hiệu năng ngang/vượt teacher; xét toàn dải xếp hạng thì teacher vẫn nhỉnh hơn; khoảng cách này sẽ **mở lại** khi gặp dịch chuyển miền" (Slide 26–27).

**Gợi ý hình:** 2 bảng cạnh nhau; vạch ngang ở mức pAUC teacher cao nhất (0,1830).

---

## Slide 20 — Bằng chứng thống kê: không đếm thắng, đo khoảng tin cậy

**Tiêu đề:** Từ "đếm thắng" tới "khoảng tin cậy" — bức tranh khắt khe hơn nhiều

**Nội dung:**
- Đếm dấu thô (12 cặp, mean 5-fold): pAUC/AUC/Sensitivity/Sens@90/95%Spec **12/12 cặp thắng**; AUPRC **10/12**, Δ trung bình +0,0235
- Nhưng đếm dấu **không cho biết** liệu chênh lệch có giữ nguyên nếu tập test đổi đi đôi chút → cần **paired bootstrap CI 95%** (B=2.000, ghép cặp theo hàng test)
- **Khoảng tin cậy loại trừ 0 (dương):** AUC-ROC 9/12 · pAUC 8/12 · **AUPRC chỉ 5/12** · Sens@90%Spec 3/12
- ✅ **Cột "âm có ý nghĩa" toàn số 0 ở mọi chỉ số** — không một cặp nào bị KD làm tệ đi có ý nghĩa thống kê, đây là phát biểu mạnh nhất không cần điều kiện kèm theo
- 7/12 cặp còn lại trên AUPRC rơi vào "không kết luận được" — đọc đúng là *chưa đủ bằng chứng*, không phải *đã chứng minh không có*

**Ghi chú thuyết trình:** Nguyên nhân của khoảng cách 12/12 → 5/12 không phải KD yếu mà là **cỡ mẫu**: tập test in-domain chỉ có 241 ca dương. Bằng chứng ở HAM10000 (1.169 ca dương) mạnh hơn hẳn — xem Slide 26.

**Gợi ý hình:** DÙNG HÌNH SẴN: `figures/paired_bootstrap.png` (Hình 4.2) minh hoạ cách dựng khoảng tin cậy ghép cặp; kèm bảng đếm 12 cặp bên dưới.

---

## Slide 21 — Quy luật: KD giúp nhiều nhất đúng ở student yếu nhất

**Tiêu đề:** Khả năng tận dụng KD tỉ lệ nghịch với chất lượng sẵn có của student (r = −0,963)

**Nội dung:**
- Tương quan Pearson trên 12 cặp: **pAUC baseline ↔ ΔpAUC: r = −0,963**; AUPRC baseline ↔ ΔpAUC: r = −0,913
- RepViT-M1.0 (student baseline yếu nhất, pAUC 0,1718) chiếm **cả hai vị trí đầu** trong 5 cặp có ΔAUPRC lớn nhất — dẫn đầu: `MaxViT-Base → RepViT-M1.0` **+0,0708 [+0,0429; +0,0917]** (loại trừ 0 ở cả AUPRC và pAUC), kế đến `ConvNeXtV2-Base → RepViT-M1.0` +0,0449; ba vị trí còn lại thuộc về FastViT-SA12 và MobileNetV4
- FastViT-SA12 (baseline mạnh nhất, pAUC 0,1825) là nơi KD tác động **yếu nhất**, trung bình chỉ +0,0024 pAUC qua 3 teacher
- Quy luật này khớp với cơ chế "làm mượt nhãn thích ứng" (Slide 6): student đã đủ mạnh thì vốn đã xử lý tốt các mẫu mơ hồ, nên KD không còn gì để bù
- **Trình bày đúng cho một metric gần bão hoà (pAUC trần 0,20):** phần trăm headroom được xoá — trung bình **12 cặp xoá được 22,7%** khoảng cách còn lại tới trần pAUC (22,4% AUC)

**Ghi chú thuyết trình:** Đây là phát biểu định lượng, không phải mô tả định tính — và chính vì n=12 chứ không phải 1 cặp nên tương quan này mới đo được. Hệ quả cho thiết kế hệ thống: KD phát huy đúng ở chỗ ta muốn nén mạnh nhất.

**Gợi ý hình:** Scatter r=−0,963: trục x = pAUC baseline, trục y = ΔpAUC, 12 điểm, đường hồi quy; bảng % headroom bên cạnh.

---

## Slide 22 — Hai miền ẩn sau một con số AUPRC tổng

**Tiêu đề:** Vì sao hai cặp có Δ âm — và vì sao phải luôn đọc kèm phân rã theo miền

**Nội dung:**
- Tập test 62.040 ảnh nhưng 241 ca dương **không nằm đều**: ISIC 61.663 ảnh chỉ 61 ca ác tính (0,099%); PAD **377 ảnh chứa 180 ca (47,75%)** — 0,6% số ảnh nắm 3/4 số ca bệnh
- Hai cặp có ΔAUPRC âm ở bảng tổng (`EfficientNetV2-M → MobileNetV4`: −0,0045; `→ EfficientFormerV2-S2`: −0,0062) **đều dương rõ trên miền ISIC** khi tách riêng: **+19,4%** và **+33,1%** tương đối
- Phần âm hoàn toàn đến từ tập con PAD (377 ảnh, quyết định phần lớn con số tổng) — phát biểu đúng là *"KD không giúp"*, không phải *"KD làm hại"*
- Quy luật thứ hai: trên miền ISIC 10/12 cặp cải thiện +7,0% đến +43,8%; cùng cặp ấy trên miền PAD chỉ dao động −4,2% đến +11,8% — **KD giúp nhiều nhất đúng ở miền mà baseline còn yếu nhất**, lặp lại quy luật ở Slide 21 nhưng theo trục miền ảnh

**Ghi chú thuyết trình:** Đây là hạn chế Chương 5 nêu thẳng: mọi chỉ số AUPRC toàn tập trong luận văn là **thống kê hỗn hợp**, không phải hiệu năng thuần trên ISIC — muốn con số đại diện ISIC phải dùng riêng dải 0,045–0,069.

**Gợi ý hình:** Bảng 2 cột (ISIC / PAD) cho 12 cặp, tô đỏ 2 dòng có Δ tổng âm để thấy chúng dương khi tách miền.

---

## Slide 23 — Đánh giá theo từng teacher: teacher mạnh hơn có dạy tốt hơn?

**Tiêu đề:** Q2 — Có, trong miền; nhưng không có teacher tốt nhất độc lập với miền triển khai

**Nội dung:**

| Teacher | AUPRC của chính nó | ΔAUPRC student TB | Số student thắng | ΔpAUC student TB |
|---|---|---|---|---|
| MaxViT-Base | **0,6566** | **+0,0360** | **4/4** | +0,0053 |
| ConvNeXtV2-Base | 0,6506 | +0,0299 | **4/4** | +0,0043 |
| EfficientNetV2-M | 0,6298 | +0,0048 | 2/4 | **+0,0060** |

- Trong miền trên AUPRC: **thứ tự trùng khớp** — teacher mạnh hơn dạy tốt hơn (nhưng n=3 nên chỉ nói "trùng thứ tự", chưa phải "tương quan")
- Đổi sang HAM10000: **EfficientNetV2-M vươn lên tốt nhất** (ΔAUPRC TB +0,0386, so với +0,0337 và +0,0221)
- Đổi sang Fitzpatrick17k: **chính teacher đó rơi xuống cuối bảng**, không student nào đạt CI dương, 2/4 student còn tụt AUC có ý nghĩa
- 🎯 **Không tồn tại "teacher tốt nhất" độc lập với miền và độ đo** — bước chọn teacher phải kèm đánh giá trên miền gần miền triển khai

**Ghi chú thuyết trình:** Đây là một trong hai phát hiện "phổ biến hoá ra sai" của luận văn (Đóng góp 3a) — chỉ lộ ra được vì thiết kế có ≥3 teacher × ≥2 bộ ngoài miền, điều một thiết kế 1-teacher không thể phát hiện.

**Gợi ý hình:** 3 cột nhỏ (In-domain / HAM10000 / Fitzpatrick17k), mỗi cột xếp hạng 3 teacher — tô rõ EfficientNetV2-M nhảy từ hạng 3 → hạng 1 → hạng 3.

---

## Slide 24 — Kiểm chứng lựa chọn dữ liệu (1): trộn PAD-UFES-20

**Tiêu đề:** Q1 — Trộn PAD-UFES-20 giúp cả hai tầng, không hại miền ISIC gốc

**Nội dung:**
- Nhánh đối chứng ISIC-only (3 teacher + 4 student, đủ 5-fold) so với nhánh có PAD, đọc trên **tập con 377 ảnh PAD** của test (đọc trên toàn tập sẽ phóng đại vì nhánh ISIC-only chưa từng thấy ảnh điện thoại)

| Tầng | Kết quả |
|---|---|
| **Teacher** (3/3) | ΔAUPRC +0,092 đến **+0,131**; MaxViT AUC PAD 0,755 → 0,855 |
| **Student** (3/4 CI dương) | ΔAUPRC **+0,105 đến +0,120**; RepViT không đạt ý nghĩa trên AUPRC nhưng đạt trên AUC (+0,0644) và pAUC (+0,0277) |
| **Miền ISIC** | Không hại — teacher trung tính (+0,0035, trong nhiễu); **student còn cải thiện có ý nghĩa 3/4** (+46% đến +118% tương đối) |

- 🎯 Kết luận **rất chắc** vì dựa trên khoảng tin cậy ghép cặp, và đúng cho cả mô hình đem triển khai (student), không chỉ teacher

**Gợi ý hình:** Biểu đồ cột nhóm: teacher/student × ISIC-only vs +PAD, trên AUPRC miền PAD.

---

## Slide 25 — Kiểm chứng lựa chọn dữ liệu (2): tỉ lệ undersampling 1:5

**Tiêu đề:** Q6 — Tỉ lệ 1:5 đã chứng minh, không còn là tham số kế thừa từ đề cương

**Nội dung:**

| Nhánh | Ảnh/epoch | AUPRC (mean±std) | pAUC@80 | Fold dừng sớm |
|---|--:|---|---|---|
| 1:3 | 3.860 | 0,6152 ± 0,0438 | 0,1852 | 1/5 |
| **1:5** *(đang dùng)* | 5.790 | 0,6056 ± 0,0341 | **0,1859** | — |
| 1:10 | 10.615 | 0,5486 ± 0,0484 | 0,1826 | **5/5** |

- **1:5 vs 1:10**: thắng có ý nghĩa ở cả 3 miền, CI toàn tập **+0,0570 [+0,0343; +0,0781]** — nguyên nhân **không phải** ít ca dương hơn (số ca ác tính mỗi epoch **không đổi** ở cả ba nhánh, luôn 965 ảnh): nhánh 1:10 có **nhiều ảnh lành tính hơn** mỗi epoch, khiến mất mát validation chạm đáy rồi đi ngang sớm hơn, đủ kích hoạt điều kiện dừng sớm ở cả 5/5 fold — tương tác giữa tỉ lệ lấy mẫu và tiêu chí dừng sớm, không phải mô hình học kém hơn mỗi epoch
- **1:5 vs 1:3**: **không phân biệt được** (CI toàn tập −0,0097 [−0,0222; +0,0044], chứa 0) — mặc dù điểm ước lượng 1:3 trông nhỉnh hơn trên AUPRC, chỉ khoảng tin cậy mới cho biết không có cơ sở để đổi
- 🎯 1:5 **dẫn đầu ở pAUC** (chỉ số chuẩn ISIC 2024), không thua ở đâu, và tránh mức 1:10 làm giảm hiệu năng rõ rệt

**Ghi chú thuyết trình:** Chi tiết đáng nhớ nhất của slide này: nếu chỉ nhìn điểm ước lượng (không có CI) sẽ kết luận sai rằng nên đổi sang 1:3.

**Gợi ý hình:** Bảng trên + biểu đồ CI ngang (forest plot) 2 hàng: "1:5 vs 1:10" và "1:5 vs 1:3".

---

## Slide 26 — Tổng quát hoá xuyên miền: HAM10000

**Tiêu đề:** Bằng chứng KD quyết định nhất nằm ở đây, không phải in-domain

**Nội dung:**
- Một thí nghiệm duy nhất: 19 lượt chạy chấm nguyên trạng (không huấn luyện thêm, không chỉnh ngưỡng) trên **7.470 ảnh** (biến thể 1 ảnh/tổn thương), **1.169 ca ác tính**
- **12/12 cặp dương trên AUPRC, 11/12 có CI loại trừ 0** — chắc hơn hẳn in-domain (5/12) vì cỡ mẫu ca dương lớn hơn (1.169 vs 241)
- Biên độ trải rộng **+0,0060 đến +0,0713**, trung vị **+0,0304**; đỉnh là `EfficientNetV2-M → MobileNetV4-Conv-Medium` +0,0713 [+0,0598; +0,0819]
- Cùng quy luật Slide 21: 4 cặp dẫn đầu đổ vào MobileNetV4/RepViT (student yếu); ngoại lệ có ý nghĩa duy nhất là `EfficientNetV2-M → EfficientFormerV2-S2` — **kém hơn** baseline trên AUC/pAUC (student mạnh nhất trên bộ này)
- ⚠️ **Ngưỡng quyết định KHÔNG chuyển miền được**: in-domain Sens@90%Spec đạt 92,7–95,8%; sang HAM10000 dưới cùng ràng buộc chỉ còn **32,4–51,0%**, kể cả 3 teacher

**Ghi chú thuyết trình:** Đây là kết quả có tính quyết định về mặt bằng chứng nhất của toàn luận văn — nói rõ với hội đồng rằng bằng chứng KD "chắc" nằm ở tầng xuyên miền, không phải in-domain, vì lý do cỡ mẫu chứ không phải hiệu ứng yếu đi.

**Gợi ý hình:** DÙNG HÌNH SẴN: `figures/ham_summary.png` (Hình 4.3, 3 panel: (a) Δ ghép cặp kèm CI, (b) điểm đạt được vs mức cải thiện, (c) độ nhạy tại đặc hiệu cố định trong/ngoài miền).

---

## Slide 27 — Công bằng theo tông da: Fitzpatrick17k

**Tiêu đề:** Nhóm chịu thiệt là nhóm TRUNG BÌNH, không phải nhóm tối

**Nội dung:**
- 19 lượt chạy chấm trên **4.320 ảnh** (biến thể chính), 2.160 ca ác tính (50,0%); ba nhóm: sáng 2.310 · trung bình 1.599 · tối 411
- Ở ngưỡng đóng băng, mô hình gắn cờ **93–99% ảnh lành tính** là báo động nhầm → mọi kết luận chỉ dựa vào **AUC/AUPRC** (toàn dải ngưỡng), không dùng điểm vận hành
- Thứ tự AUC ba nhóm: **sáng 0,6755 → tối 0,6474 → trung bình 0,6286**
- Giả thuyết trực giác *"càng tối da càng kém"* **không đứng được**: `dark − medium` nằm **bên phải** vạch 0 (tối xếp hạng tốt hơn trung bình); chỉ hàng **`light − medium`** dồn hẳn về một phía — **19/19 lượt chạy có CI loại trừ 0**, cả AUC lẫn AUPRC
- Bằng chứng chỉ dứt khoát **sau khi khôi phục độ phủ Fitzpatrick17k lên 99,98%** — trên bản 23,4% cũ chỉ 1/19 phân định được, và còn dựng lên tín hiệu giả (9/19 → tụt về 1/19)
- ⚠️ **Cạm bẫy phương pháp:** so AUPRC thô giữa các nhóm có tỉ lệ ca bệnh khác nhau (biến thể phụ) dẫn tới kết luận **ngược hẳn** — phải quy về bội số so với đường cơ sở riêng của mỗi nhóm

**Ghi chú thuyết trình:** Đây là phát hiện thứ hai trong nhóm "phổ biến hoá ra sai" (Đóng góp 3b) — không nằm trong mục tiêu ban đầu, xuất hiện trong quá trình phân tích. Trên Fitzpatrick17k, 3 teacher chiếm trọn 3 vị trí đầu bảng — student không bám kịp trên ảnh lâm sàng trường rộng.

**Gợi ý hình:** DÙNG HÌNH SẴN: `figures/fitzpatrick_summary.png` (Hình 4.4, 3 panel: (a) khoảng cách AUC từng cặp nhóm, (b) AUPRC thô so với đường cơ sở riêng từng nhóm, (c) teacher vs student ngoài miền).

---

## Slide 28 — Benchmark trên thiết bị biên: Pixel 6a

**Tiêu đề:** 16/16 mô hình vượt cổng kiểm tra tương đương — rồi mới đo tốc độ thật

**Nội dung:**
- **16 mô hình** đo (4 kiến trúc × 4 biến thể — 3 KD + 1 baseline); export ExecuTorch `.pte` FP32, **cổng kiểm tra tương đương số học 16/16 PASS ở cả máy chủ lẫn chính Pixel 6a**
- ⚠️ Cổng này bắt được lỗi thật: EfficientFormerV2-S2 export "thành công" không cảnh báo, nhưng logit lệch tới **13 bậc độ lớn** (−2,2×10¹⁰ so với −3,15) → buộc chạy bằng bộ toán tử tham chiếu (portable), chậm hơn nhiều

| Kiến trúc | Backend | Size `.pte` | Sau 5 phút chạy liên tục | Chậm đi do nhiệt |
|---|---|--:|--:|--:|
| MobileNetV4-Conv-M | xnnpack | 32,11 MiB | **39,5 ms** | +47,5% |
| RepViT-M1.0 | xnnpack | 24,46 MiB | 57,2 ms | +49,4% |
| FastViT-SA12 | xnnpack | 40,35 MiB | 113,9 ms | +44,8% |
| EfficientFormerV2-S2 | **portable** | 47,98 MiB | **3.908,2 ms** | 0% |

- **Điều tiết nhiệt** làm 3 kiến trúc backend tăng tốc chậm thêm **45–49%** sau 5 phút — đo trên cùng một phiên, nhiệt máy tăng 31,5°C→40,1°C
- MobileNetV4 nhanh nhất mọi điều kiện, bỏ xa EfficientFormerV2-S2 tới **181 lần** lúc máy còn nguội; bộ nhớ **không phải vấn đề** (208–257 MiB cả 16 mô hình)
- 🎯 Bốn biến thể của một kiến trúc chạy nhanh như nhau → **chọn teacher nào là MIỄN PHÍ trên trục tốc độ**

**Gợi ý hình:** DÙNG HÌNH SẴN: `../reports/pareto_auprc_vs_latency.png` (Hình 4.5 — đường dẫn tính từ `report_phase_1/`, vì file gốc nằm ở `reports/`) — AUPRC vs latency (log), đường biên Pareto chỉ còn MobileNetV4-Conv-M và FastViT-SA12.

---

## Slide 29 — Lựa chọn mô hình triển khai

**Tiêu đề:** Q5 — Hai ứng viên trên đường biên Pareto, khoảng tin cậy ghép cặp phân xử

**Nội dung:**

| Chiều | MaxViT → FastViT-SA12 | ConvNeXtV2 → MobileNetV4 |
|---|--:|--:|
| AUPRC in-domain | **0,6510** | 0,6351 |
| AUPRC HAM10000 | **0,4572** | 0,4198 |
| AUPRC Fitzpatrick17k | **0,6623** | 0,6172 |
| Độ trễ (5 phút liên tục) | 113,9 ms | **39,5 ms** |
| Size `.pte` | 40,35 MiB | **32,11 MiB** |

- **Khoảng tin cậy ghép cặp** (không phải hai khoảng riêng lẻ — dễ đánh lừa vì chồng lấn): in-domain **không lớn** (mọi CI chứa 0); ngoài miền **khác biệt rõ, 8/8 độ đo trên HAM10000 + Fitzpatrick17k loại trừ 0**, mạnh nhất ở nhóm da tối (+0,0646 AUPRC)
- 🎯 **Khuyến nghị: `MaxViT-Base → FastViT-SA12`** cho kịch bản sàng lọc cộng đồng thực tế — đổi lại mỗi ảnh mất 113,9 ms thay vì 39,5 ms
- **Đảo khuyến nghị** trong hai trường hợp: (a) ràng buộc thiết bị cứng/cần thời gian thực → chọn `ConvNeXtV2-Base → MobileNetV4` (suy giảm rõ khi dịch chuyển miền, chấp nhận đổi lấy tốc độ); (b) nếu ảnh đầu vào **chắc chắn cùng miền** với dữ liệu huấn luyện thì hai cặp **tương đương về chất lượng** trong miền — khi đó chọn `ConvNeXtV2-Base → MobileNetV4` vì nó nhanh hơn 2,9× và ổn định hơn giữa các fold, không còn lý do chọn cặp kia

**Ghi chú thuyết trình:** Đây là minh hoạ trực tiếp cho lý do phải dùng CI ghép cặp (Slide 20/25): ước lượng riêng rẽ cho hai mô hình trên HAM10000 thì hai khoảng **chồng lấn nhau** — sẽ kết luận sai là "ngang nhau" — còn CI ghép cặp cho +0,0374 [+0,0245; +0,0495], loại trừ 0 dứt khoát.

**Gợi ý hình:** Bảng 9 trục (Bảng 4.18 rút gọn) + forest plot CI ghép cặp cho 4 chỉ số × 3 miền.

---

# PHẦN 6 — KẾT LUẬN

---

## Slide 30 — Trả lời sáu câu hỏi nghiên cứu

**Tiêu đề:** Q1–Q6: câu trả lời kèm mức chắc chắn

**Nội dung:**
- **Q1 (trộn PAD?)** — **Có**, rất chắc: cả 2 tầng, khoảng tin cậy ghép cặp, không hại miền ISIC
- **Q2 (teacher mạnh → student tốt hơn?)** — Có khi đo trong miền, nhưng **không có đáp án độc lập với miền triển khai** (đảo hoàn toàn trên HAM10000 vs Fitzpatrick17k)
- **Q3 (nhất quán qua paradigm?)** — Có về hướng (xoá TB 22,7% headroom pAUC, cả 4 paradigm hưởng lợi); bằng chứng ý nghĩa thống kê mạnh nhất nằm ở xuyên miền (11/12), không phải in-domain (5/12) — do cỡ mẫu 241 ca dương
- **Q4 (student vượt teacher?)** — Vượt trên pAUC (11/12 cặp) và độ nhạy; **chưa vượt** trên AUPRC; thua rõ ngoài miền. Cặp triển khai: pAUC 0,1851 > 0,1830 của teacher, AUPRC 0,6510 vs 0,6566 (chênh nhỏ hơn cả std 5-fold) — đổi lại nhẹ hơn **11,2×** tham số/dung lượng, **16,2×** FLOPs
- **Q5 (chọn gì để triển khai?)** — `MaxViT-Base → FastViT-SA12` cho kịch bản cộng đồng; `ConvNeXtV2 → MobileNetV4` nếu ràng buộc thiết bị cứng — kết luận chắc chắn nhất trong 6 câu (CI ghép cặp trực tiếp giữa 2 ứng viên)
- **Q6 (tỉ lệ 1:5 đúng?)** — Có, đã chứng minh: thắng 1:10 có ý nghĩa, không phân biệt được với 1:3

**Gợi ý hình:** 6 khối, mỗi khối 1 câu hỏi + 1 icon mức chắc chắn (✅ rất chắc / ⚠️ có điều kiện).

---

## Slide 31 — Hạn chế của nghiên cứu

**Tiêu đề:** Ba hạn chế lớn nhất — nêu chủ động, không đợi hội đồng hỏi

**Nội dung:**
1. **Dữ liệu ca ác tính quá ít trong miền** — chỉ 241 ca dương, 74,7% đến từ 377 ảnh PAD → chỉ 5/12 cặp đạt CI dương in-domain; fold tốt nhất vượt trung bình tới **+0,0263 AUPRC**, lớn hơn cả hiệu quả KD (+0,0235) → luận văn đặt luận điểm chính lên tầng xuyên miền, không phải in-domain
2. **Năng lực ngoài miền còn hạn chế** — Sens@90%Spec rơi còn 0,324–0,510 trên HAM10000; Fitzpatrick17k gần như gắn cờ mọi ảnh ở ngưỡng đóng băng; **không cách chọn ngưỡng nào nâng được trần đó** — giới hạn nằm ở khả năng xếp hạng
3. **Dịch chuyển miền gây khó cho cả teacher lẫn student như nhau** — trên HAM10000 cả 3 teacher cũng tụt về 0,481–0,498, nằm trong dải 0,324–0,510 của 16 student → khoảng cách còn lại **không phải cái giá của nén mô hình** mà là giới hạn của dữ liệu huấn luyện
- **Phạm vi kết luận:** kỹ thuật thì kết luận dứt khoát (chạy thật, 113,9 ms, 16/16 parity); lâm sàng thì chỉ trong phạm vi 4 bộ dữ liệu đã dùng — thẩm định tiến cứu là nghiên cứu khác, ngoài phạm vi

**Gợi ý hình:** 3 khối "Hạn chế" + 1 khối "Phạm vi kết luận" riêng biệt, tông màu trung tính (không đỏ báo lỗi — đây là giới hạn thiết kế, không phải sai sót).

---

## Slide 32 — Hướng phát triển & Kết luận

**Tiêu đề:** Năm hướng phát triển tiếp theo, và kết luận

**Nội dung:**
1. **Mở rộng & làm phong phú nguồn dữ liệu** — thêm ảnh lâm sàng smartphone (bằng chứng đã có: PAD giúp +0,092 đến +0,131 chỉ với 377 ảnh)
2. **Tối ưu năng lực xử lý trên thiết bị** — không phải nhỏ thêm, mà khai thác nhiều hơn từ tính toán sẵn có; đưa các kiến trúc bị kẹt ở bộ toán tử tham chiếu (EfficientFormerV2-S2) trở lại backend tăng tốc
3. **Cổng phát hiện ảnh ngoài phân phối (OOD)** — điều kiện **bắt buộc** trước khi dùng thật, vì HAM10000/Fitzpatrick17k vẫn là ảnh da nên chưa đại diện input thực sự bất thường
4. **Tầng đề xuất & hướng dẫn người dùng** — diễn giải, theo dõi theo thời gian, khuyến nghị đi khám (không phải chẩn đoán) — chỉ có nghĩa **sau** cổng OOD
5. **Mở rộng sang iOS** — định dạng không bó buộc hệ điều hành, nhưng cổng kiểm tra tương đương và benchmark phải làm lại trên chính thiết bị đích

**Kết luận:** Chưng cất tri thức **áp dụng được** cho bài toán này — cải thiện nhất quán về hướng trên cả 4 paradigm, không cặp nào bị hại có ý nghĩa trong miền, và bằng chứng quyết định nhất đến từ tầng xuyên miền. Mức cải thiện không đồng đều — phụ thuộc student, phụ thuộc miền, phụ thuộc teacher — và luận văn định lượng được từng phụ thuộc đó thay vì chỉ khẳng định "KD có tác dụng".

**Trân trọng cảm ơn Hội đồng!**

**Gợi ý hình:** 5 khối hướng phát triển dạng roadmap; slide cảm ơn tối giản kèm thông tin liên hệ học viên.

---

## (Phụ lục) Slide 33 — Tài liệu tham khảo

**Tiêu đề:** Tài liệu tham khảo chọn lọc (đánh số theo slide, đối chiếu số gốc trong luận văn ở ngoặc vuông)

**Nội dung:**
- [1] Esteva A., et al. (2017), "Dermatologist-level classification of skin cancer with deep neural networks", *Nature* [ref luận văn 11]
- [2] Hinton G., Vinyals O., Dean J. (2015), "Distilling the Knowledge in a Neural Network", *arXiv:1503.02531* [17]
- [3] Lin T. Y., et al. (2017), "Focal Loss for Dense Object Detection", *ICCV 2017* [25]
- [4] Tan M., Le Q. V. (2019), "EfficientNet: Rethinking Model Scaling for CNNs", *ICML 2019* [45]
- [5] Dosovitskiy A., et al. (2021), "An Image is Worth 16×16 Words" (ViT), *ICLR 2021* [8]
- [6] Tu Z., et al. (2022), "MaxViT: Multi-Axis Vision Transformer", *ECCV 2022* [47]
- [7] Woo S., et al. (2023), "ConvNeXt V2", *CVPR 2023* [54]
- [8] Qin D., et al. (2024), "MobileNetV4: Universal Models for the Mobile Ecosystem", *ECCV 2024* [41]
- [9] Vasu P. K. A., et al. (2023), "FastViT", *ICCV 2023* [48]
- [10] Li Y., et al. (2023), "Rethinking Vision Transformers for MobileNet Size and Speed" (EfficientFormerV2), *ICCV 2023* [24]
- [11] Wang A., et al. (2024), "RepViT: Revisiting Mobile CNN From ViT Perspective", *CVPR 2024* [50]
- [12] International Skin Imaging Collaboration (2024), *ISIC 2024 — Skin Cancer Detection with 3D-TBP*, Kaggle [20]
- [13] Pacheco A. G. C., et al. (2020), "PAD-UFES-20", *Data in Brief* [33]
- [14] Tschandl P., Rosendahl C., Kittler H. (2018), "The HAM10000 dataset", *Scientific Data* [46]
- [15] Groh M., et al. (2021), "Evaluating DNNs... with the Fitzpatrick 17k Dataset", *CVPR 2021 Workshops* [15]
- [16] Islam N., et al. (2024), "Leveraging Knowledge Distillation for Lightweight Skin Cancer Classification", *arXiv:2406.17051* [21]
- [17] Saha S., et al. (2025), "Knowledge distillation approach for skin cancer classification on lightweight deep learning model", *Healthcare Technology Letters* [42]
- [18] Winata A., et al. (2025), "MTAKD: multi-teacher agreement knowledge distillation", *Scientific Reports* [53]
- [19] Efron B., Tibshirani R. J. (1993), *An Introduction to the Bootstrap*, Chapman & Hall/CRC [10]
- [20] Ha Q., Liu B., Liu F. (2020), "Identifying Melanoma Images using EfficientNet Ensemble", *arXiv:2010.05351* [16]
- [21] PyTorch Team (2024), *ExecuTorch: On-device AI inference runtime* [40]
- [22] Wang M., Gao X., Zhang L. (2025), "Recent global patterns in skin cancer incidence, mortality, and prevalence", *Chinese Medical Journal* [51]
- [23] Youden W. J. (1950), "Index for rating diagnostic tests", *Cancer* [55]

**Gợi ý hình:** Danh sách 2 cột gọn; giữ để dự phòng khi Hội đồng hỏi nguồn. Danh mục đầy đủ 55 mục nằm ở `thesis/LUAN_VAN.md` (mục TÀI LIỆU THAM KHẢO).
