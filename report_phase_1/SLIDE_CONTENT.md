> ⛔ **SUPERSEDED — 2026-08-26. KHÔNG trích số từ file này.**
>
> Bản thay thế duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](../reports/BAO_CAO_TONG_HOP.md).
>
> Lý do: cùng phạm vi "chỉ 1 teacher" (22/08).

---

# NỘI DUNG SLIDE — BẢO VỆ ĐỀ CƯƠNG LUẬN VĂN THẠC SĨ

> **Hướng dẫn dùng file này:** Mỗi mục `## Slide N` là một slide. Phần **Tiêu đề** là title, **Nội dung** là các bullet đưa lên slide (giữ ngắn gọn), **Ghi chú thuyết trình** là lời nói của người trình bày (không đưa lên slide). Đưa toàn bộ file này cho AI dựng slide (Gamma / Beautiful.ai / PowerPoint Copilot) và yêu cầu: "tạo slide theo từng mục, phong cách học thuật, tối giản, có biểu đồ/bảng khi được gợi ý".
>
> **Tổng: 24 slide** (+ 2 slide bổ sung **19B** tùy chọn và **21B** ablation dữ liệu + phụ lục tài liệu tham khảo) · Thời lượng đề xuất: 16–20 phút · Đối tượng: Hội đồng đánh giá đề cương.
>
> **⚠️ HÌNH ĐÃ VẼ SẴN — BẮT BUỘC DÙNG, KHÔNG VẼ LẠI:** Thư mục `report_phase_1/figures/` chứa các hình dạng SVG/PNG do học viên tự vẽ (phong cách "soft-card" đồng bộ). Khi một slide ghi *"DÙNG HÌNH SẴN: `figures/<tên>.png`"* thì **chèn đúng file PNG đó làm hình chính của slide, không tự sinh lại hình mới**. Dùng bản `_slide.png` (tỉ lệ 16:9) cho slide. Các hình có sẵn cho bộ slide này:
> - `figures/kd_pipeline_slide.png` — pipeline tổng thể 3 bước (Teacher → Chưng cất KD → Đánh giá + triển khai) → **Slide 18**
> - `figures/kd_flow_slide.png` — cơ chế chưng cất tri thức (teacher đóng băng, nhãn mềm, hàm mất mát kết hợp, backprop chỉ student) → **Slide 6** (và tái dùng ở **Slide 16**)
> - `figures/app_inference_slide.png` — luồng suy luận trên thiết bị của ứng dụng (camera → cổng chất lượng → suy luận .pte → ngưỡng → khuyến nghị) → **Slide 19B**
>
> **Ghi chú số liệu (cập nhật 2026-08-22):** Các slide phần "Kết quả bước đầu" dùng số THẬT đã chạy **đủ 5-fold CV** trên test độc lập, trích từ `experiments/runs/*/aggregated.json`. **Phạm vi: chỉ các run huấn luyện từ 15/7/2026** — đợt hợp lệ, đồng bộ với bộ mô hình hiện tại. Hệ quả phải nói rõ khi trình bày: **ma trận KD mới hoàn tất cho một teacher (EfficientNetV2-M)**, nên câu hỏi "teacher nào chưng cất tốt nhất" chưa trả lời được; phần cross-domain/fairness cũng chưa chạy. Tài liệu tham khảo trong slide được **đánh số lại từ [1]** (không theo số của đề cương).

---

## Slide 1 — Trang bìa

**Tiêu đề:** PHÁT HIỆN UNG THƯ DA TRÊN THIẾT BỊ BIÊN SỬ DỤNG MÔ HÌNH HỌC SÂU KẾT HỢP CHƯNG CẤT TRI THỨCV

**Phụ đề (tiếng Anh):** Knowledge-Distilled Deep Learning Models for Skin Cancer Detection on Edge Devices

**Nội dung:**
- Học viên: Đặng Quang Hưng · MSHV: 230101006 · Khóa 18 · Đợt 1
- Người hướng dẫn khoa học: TS. Nguyễn Thanh Bình
- Trường Đại học Công nghệ Thông tin — ĐHQG TP.HCM

**Gợi ý hình:** Ảnh nền tổn thương da mờ / icon smartphone + AI. Logo trường.

---

## Slide 2 — Nội dung trình bày (Agenda)

**Tiêu đề:** Nội dung trình bày

**Nội dung:**
1. Vấn đề & động lực — vì sao có đề tài này
2. Chưng cất tri thức & câu hỏi nghiên cứu
3. Mục tiêu đề tài
4. Dữ liệu (phân tích sâu ISIC 2024) & ba thách thức
5. Các nghiên cứu liên quan & khoảng trống
6. Giải pháp đề xuất & thiết kế thực nghiệm đối chứng
7. Phương pháp thực hiện (pipeline đầu–cuối)
8. Độ đo đánh giá & **kết quả bước đầu**
9. Kế hoạch thực hiện & kết luận

**Gợi ý hình:** Danh sách đánh số dạng timeline dọc, tô sáng mục 8 (kết quả).

---

# PHẦN 1 — VẤN ĐỀ & ĐỘNG LỰC

> *Ba vấn đề nối tiếp nhau sinh ra đề tài. Trình bày trực quan: mỗi vấn đề một slide, một hình ảnh trung tâm, một câu chốt.*

---

## Slide 3 — Vấn đề 1: Ung thư da nguy hiểm nhưng phát hiện sớm thì cứu được

**Tiêu đề:** Vấn đề 1 — Nghịch lý melanoma: ít ca, nhiều tử vong, nhưng chữa được nếu bắt sớm

**Nội dung:**
- **~331.722** ca melanoma mắc mới mỗi năm · **~58.667** ca tử vong (GLOBOCAN 2022) [1]
- Melanoma chỉ **~10%** số ca ung thư da nhưng gây **~80%** số ca tử vong [2]
- Nhưng phát hiện ở giai đoạn khu trú → tỷ lệ sống 5 năm đạt **99%** [3]
- 🎯 **Chốt vấn đề:** cơ hội sống phụ thuộc gần như hoàn toàn vào **phát hiện sớm**

**Ghi chú thuyết trình:** Đây là "vấn đề gốc". Nhấn nghịch lý bằng 3 con số lớn — melanoma ít nhưng chết nhiều, và khoảng cách giữa 99% (bắt sớm) với con số tử vong (bắt muộn) chính là dư địa mà công nghệ có thể lấp.

**Gợi ý hình:** Infographic 3 khối số khổng lồ: `10% ca — 80% tử vong — 99% sống nếu sớm`. Dùng màu đỏ cho tử vong, xanh cho 99%.

---

## Slide 4 — Vấn đề 2: Chẩn đoán truyền thống không phủ được, AI mạnh lại kẹt trên cloud

**Tiêu đề:** Vấn đề 2 — Khoảng trống tiếp cận: thiếu bác sĩ, mà AI mạnh lại phụ thuộc cloud

**Nội dung:**
- Chẩn đoán truyền thống dựa vào bác sĩ da liễu (soi da, quy tắc ABCD) [4] → **thiếu chuyên gia ở vùng khó khăn, chi phí cao**
- Học sâu (CNN) đạt độ chính xác **ngang bác sĩ** [5]; EfficientNet [6], ViT [7] liên tục cải thiện
- **Nhưng** mô hình mạnh thường rất lớn → phải chạy trên **cloud**:
  - ⏱ độ trễ · 📶 phụ thuộc internet · 🔒 **rủi ro riêng tư dữ liệu y tế** [8]
- 🎯 **Chốt vấn đề:** cần đưa AI **xuống thẳng thiết bị** (Edge AI) — sàng lọc tại chỗ, offline, bảo mật [9]

**Gợi ý hình:** Sơ đồ 2 cột Cloud AI vs Edge AI; cột Cloud gắn 3 icon cảnh báo (trễ/mạng/khóa), cột Edge gắn dấu tick.

---

## Slide 5 — Vấn đề 3: Nút thắt cốt lõi — nhỏ để chạy được thì lại kém chính xác

**Tiêu đề:** Vấn đề 3 — Đánh đổi Độ chính xác ↔ Kích thước/Tốc độ trên thiết bị biên

**Nội dung:**
- Mô hình gọn (EfficientNet-B0 [6], MobileNetV3 [10], MobileViT [11]) → chạy được trên điện thoại **nhưng suy giảm độ chính xác**
- Y tế: **bỏ sót 1 ca ác tính (false negative) = hậu quả nghiêm trọng** → yêu cầu **độ nhạy cao**
- ISIC 2024 chọn thước đo chính thức **pAUC@TPR≥80%** — chỉ thưởng vùng độ nhạy cao [12]
- 🎯 **Câu hỏi nút thắt:** làm sao mô hình **vừa nhỏ** (chạy trên phone) **vừa không bỏ sót** ca ác tính?

**Ghi chú thuyết trình:** Đây là "nút thắt" hội tụ cả 3 vấn đề, và là cầu nối trực tiếp sang giải pháp KD ở slide sau. Dừng lại nhấn: chính đánh đổi này là lý do tồn tại của đề tài.

**Gợi ý hình:** Cái cân thăng bằng: đĩa trái "Độ chính xác / Độ nhạy", đĩa phải "Nhỏ gọn / Tốc độ"; dấu hỏi lớn ở giữa.

---

# PHẦN 2 — GIẢI PHÁP HƯỚNG TỚI & CÂU HỎI NGHIÊN CỨU

---

## Slide 6 — Vì sao chọn Chưng cất tri thức (KD)?

**Tiêu đề:** Chưng cất tri thức — con đường hứa hẹn nhất để "gỡ" nút thắt

**Nội dung:**
- **KD** [13]: teacher lớn (chính xác) dạy student nhỏ qua **nhãn mềm** (soft labels) thay vì chỉ nhãn cứng 0/1
- Nhãn mềm mang **"dark knowledge"** — mức độ tương đồng giữa các lớp mà nhãn cứng bỏ qua
- **Vì sao KD phù hợp bài toán này (đánh mạnh):**
  - Student vẫn **nhỏ/nhanh như cũ** (không tăng chi phí suy luận) nhưng học được "kinh nghiệm" của teacher → nhắm thẳng vào nút thắt "nhỏ mà vẫn chính xác"
  - Tín hiệu mềm của teacher **làm mượt biên quyết định** → đặc biệt có lợi ở **lớp ác tính hiếm**, nơi nhãn cứng quá thưa
  - Không cần đổi kiến trúc suy luận, không cần thêm dữ liệu gán nhãn → **rẻ và triển khai được ngay trên phone**
- 🎯 KD = cách "nén tri thức" chứ không "nén thô" → giữ độ chính xác trong ngân sách thiết bị biên

**Gợi ý hình:** **DÙNG HÌNH SẴN: `figures/kd_flow_slide.png`** — sơ đồ cơ chế KD (teacher đóng băng → nhãn mềm; student → dự đoán; nhãn cứng + nhãn mềm → hàm mất mát kết hợp → backprop chỉ cập nhật student). Chèn full-width; không vẽ lại. Khi thuyết trình chỉ cần nhấn nhánh "soft labels / dark knowledge" và ghi chú "suy luận vẫn nhỏ & nhanh".

---

## Slide 7 — Khoảng trống: KD trong da liễu vẫn còn bỏ ngỏ

**Tiêu đề:** KD đã được dùng — nhưng chưa ai trả lời trọn vẹn

**Nội dung:**
- Đa số nghiên cứu KD da liễu mới chỉ khảo sát **một cặp teacher–student duy nhất**
- Chưa đánh giá **hệ thống** KD trên **nhiều paradigm kiến trúc student** (CNN, hybrid, transformer…)
- Chưa trả lời: **teacher mạnh hơn có thực sự tạo student tốt hơn?**
- Sau khi distill, mô hình có **thực sự chạy được trên điện thoại** với độ trễ chấp nhận được không?
- **ISIC 2024** (ảnh gần smartphone nhất) **gần như chưa được khai thác** trong bối cảnh KD

**Ghi chú thuyết trình:** Đây là bản lề: từ "KD hứa hẹn" (slide 6) sang "nhưng còn thiếu bằng chứng có hệ thống" → dẫn thẳng tới câu hỏi nghiên cứu.

**Gợi ý hình:** 4 ô "chưa trả lời" với dấu ❓, viền đứt.

---

## Slide 8 — Câu hỏi nghiên cứu trung tâm

**Tiêu đề:** Câu hỏi nghiên cứu — và vì sao phải chứng minh KD một cách có kiểm soát

**Nội dung:**
> *"Liệu chưng cất tri thức có mang lại cải thiện **đáng kể và nhất quán** cho các mô hình lightweight thuộc **nhiều paradigm** thiết kế khác nhau, và **chất lượng của teacher** ảnh hưởng thế nào đến hiệu quả KD trên student?"*

- **Phân rã thành 3 câu hỏi con:**
  - RQ1 — KD có cải thiện nhất quán không, và **paradigm nào hưởng lợi nhất**?
  - RQ2 — **Teacher mạnh hơn → student tốt hơn?** (tương quan chất lượng teacher ↔ mức cải thiện)
  - RQ3 — Student sau distill có **chạy thực tế trên điện thoại** không?
- Cách trả lời khách quan: **thực nghiệm so sánh đối chứng có kiểm soát** — mỗi student chạy **2 nhánh: có KD / không KD**, mọi thứ khác giữ nguyên
- Đóng góp khoa học cốt lõi = **ΔpAUC** và **ΔAUPRC** (KD − baseline) — tác động *thuần túy* của KD

**Gợi ý hình:** Highlight box cho câu hỏi lớn; bên dưới 3 chip RQ1/RQ2/RQ3; nhánh Student → {KD, Baseline} → Δ.

---

## Slide 9 — Mục tiêu đề tài

**Tiêu đề:** Mục tiêu — 3 nhóm tuần tự

**Nội dung:**
- **Mục tiêu tổng quát:** đánh giá có hệ thống hiệu quả KD cho mô hình nhỏ + kiểm chứng khả thi triển khai Android
- **Nhóm 1 — Nền tảng dữ liệu:** pipeline ISIC 2024 + PAD-UFES-20; 5-fold CV patient-disjoint (nâng prevalence ~0,1% → ~0,39%)
- **Nhóm 2 — Trọng tâm:** huấn luyện & so sánh đối chứng KD/baseline trên **nhiều kiến trúc teacher & student**; phân tích tương quan chất lượng teacher ↔ ΔAUPRC
- **Nhóm 3 — Tổng quát hóa & triển khai:** cross-domain (HAM10000), fairness (Fitzpatrick17k), export ExecuTorch + benchmark thật trên **Pixel 6a**

**Gợi ý hình:** 3 khối xếp chồng nối bằng mũi tên tuần tự.

---

# PHẦN 3 — DỮ LIỆU & THÁCH THỨC

---

## Slide 10 — Bài toán & bốn bộ dữ liệu

**Tiêu đề:** Định nghĩa bài toán & 4 bộ dữ liệu (vai trò tách bạch)

**Nội dung:**
- **Bài toán:** phân loại nhị phân — ảnh 224×224 → 1 logit → `sigmoid` → xác suất ác tính
- Ánh xạ nhãn lâm sàng: melanoma/BCC/SCC = 1 (ác tính); nevus/keratosis/lành = 0

| Bộ dữ liệu | Số ảnh | Loại ảnh | Vai trò |
|---|---|---|---|
| **ISIC 2024 SLICE-3D** [12] | **401.059** | Non-dermoscopic (TBP crop) | **Huấn luyện chính + test nội bộ** |
| PAD-UFES-20 [14] | 2.298 | Lâm sàng, smartphone | Bổ sung mẫu ác tính |
| HAM10000 [15] | 10.015 | Dermoscopic | Kiểm chứng chéo miền |
| Fitzpatrick17k [16] | 16.577 | Lâm sàng (da I–VI) | Phân tích công bằng |

- ⚠️ HAM10000 & Fitzpatrick17k **không bao giờ dùng để train** — chỉ đánh giá hậu kỳ

**Gợi ý hình:** Bảng trên + 1 ảnh mẫu đại diện mỗi dataset.

---

## Slide 11 — Phân tích sâu ISIC 2024: vì sao là bộ dữ liệu "đúng" cho đề tài

**Tiêu đề:** ISIC 2024 SLICE-3D — bộ dữ liệu phù hợp nhất cho kịch bản Edge AI cộng đồng

**Nội dung:**
- **Quy mô:** **401.059** ảnh tổn thương da, cắt từ ảnh **3D Total-Body Photography (TBP)** của hàng nghìn bệnh nhân
- **Loại ảnh = non-dermoscopic** → gần với **ảnh chụp smartphone** trong điều kiện thực (không cần máy soi da chuyên dụng) → **đúng đối tượng triển khai của đề tài**
- **Phân phối lớp cực kỳ mất cân bằng:** chỉ **~0,1% ác tính** (≈ **1 ác tính / 1.000 ảnh**) — phản ánh **đúng bối cảnh sàng lọc thực tế** (bệnh hiếm)
- **Nhãn nhị phân sẵn** (`target` 0/1) + **metadata giàu**: `isic_id`, `patient_id` (⇒ chia fold patient-disjoint chống rò rỉ), thông tin giải phẫu/kích thước tổn thương
- **Metric chuẩn hóa sẵn:** cuộc thi định nghĩa **pAUC@TPR≥80%** — khớp trực tiếp với yêu cầu "không bỏ sót ca ác tính"
- 🎯 **Kết luận:** ISIC 2024 hội đủ 3 điều kiện đề tài cần — *(i)* ảnh gần smartphone, *(ii)* quy mô lớn + patient_id để chống rò rỉ, *(iii)* mất cân bằng thực tế + metric an toàn lâm sàng

**Ghi chú thuyết trình:** Đây là slide "chứng minh chọn dataset đúng". Nhấn: các bộ dermoscopic (HAM) đẹp nhưng xa thực tế người dùng; ISIC 2024 là bộ *thực tế nhất* hiện có cho kịch bản cộng đồng, nên là bộ huấn luyện chính.

**Gợi ý hình:** Bên trái — donut chart phân phối lớp (benign ~99,9% / malignant ~0,1%, phóng to lát malignant). Bên phải — icon quy trình: TBP → crop tổn thương → metadata(patient_id) → nhãn 0/1.

---

## Slide 12 — Các bộ dữ liệu bổ trợ

**Tiêu đề:** PAD-UFES-20 & hai bộ đánh giá hậu kỳ

**Nội dung:**
- **PAD-UFES-20** [14] — **2.298** ảnh **chụp smartphone lâm sàng** (6 lớp → nhị phân): ác tính = BCC/SCC/MEL, lành = ACK/NEV/SEK
  - Vai trò: **bổ sung mẫu ác tính** → nâng prevalence tổng ~0,1% → **~0,39%**, giúp mô hình học lớp hiếm ổn định hơn
  - Gán tiền tố `pad_` cho `patient_id` khi ghép để **không trùng mã** với ISIC (tránh rò rỉ)
- **HAM10000** [15] (dermoscopic) — chỉ dùng **kiểm chứng chéo miền** (khác loại ảnh so với train)
- **Fitzpatrick17k** [16] (có thang sắc tố da I–VI) — chỉ dùng **phân tích công bằng** theo nhóm màu da

**Gợi ý hình:** 3 thẻ nhỏ (PAD / HAM / Fitzpatrick) với 1 dòng vai trò mỗi thẻ; PAD tô đậm.

---

## Slide 13 — Ba thách thức đặc trưng & cách xử lý

**Tiêu đề:** Ba thách thức & giải pháp tương ứng

**Nội dung:**
- **1. Mất cân bằng lớp cực đoan** (~0,39% ác tính) → AUC-ROC lạc quan giả
  - → **AUPRC là chỉ số chính**, pAUC@TPR≥80% ưu tiên 2
  - → **Dynamic undersampling (1:5/epoch) + Focal Loss** (γ=2, α=0,25) [17]
- **2. Rò rỉ dữ liệu** → tách held-out test (~17%) patient-disjoint **trước**, rồi `StratifiedGroupKFold(K=5)`; tiền tố `pad_` cho patient_id
- **3. Ràng buộc triển khai biên** → giới hạn cứng về tham số, FLOPs, latency; bắt buộc **đo on-device thật**

**Gợi ý hình:** 3 hàng, mỗi hàng: icon (cân lệch / khóa chống rò rỉ / điện thoại) → mũi tên → giải pháp.

---

# PHẦN 4 — NGHIÊN CỨU LIÊN QUAN & GIẢI PHÁP

---

## Slide 14 — Các nghiên cứu liên quan (dòng thời gian 10 năm)

**Tiêu đề:** Các nghiên cứu liên quan — hành trình 10 năm

**Nội dung:**
- **2015–2019 · Đặt nền móng:** Esteva 2017 (CNN ngang bác sĩ) [5]; Hinton 2015 (KD) [13]; EfficientNet [6] & MobileNetV3 [10]
- **2020–2021 · Mô hình lớn thống trị:** ensemble EfficientNet ISIC 2020 [18]; ViT [7] — chính xác hơn nhưng nặng hơn
- **2022–2023 · Tìm kiến trúc cân bằng:** MobileViT [11]; HI-MViT (F1=0,931) [19]
- **2024–2025 · KD vào da liễu + dữ liệu smartphone:** ISIC 2024 SLICE-3D [12]; Islam 2024 (student 2,03MB, 98,75%) [20]; Saha 2025 (student nhỏ hơn teacher 160×) [21]; MTAKD đa-teacher [22]

**Ghi chú thuyết trình:** Chốt: các hướng "mô hình lớn chính xác" và "mô hình nhỏ triển khai được" phát triển song song nhưng **chưa hội tụ** — đó là chỗ đứng của đề tài.

**Gợi ý hình:** Timeline ngang 4 mốc, mỗi mốc 2–3 điểm nhấn.

---

## Slide 15 — Giải pháp đề xuất: nhiều teacher & student trên nhiều paradigm

**Tiêu đề:** Khung teacher–student đa kiến trúc (không giới hạn một cặp)

**Nội dung:**
- **Ý tưởng:** thay vì 1 cặp, huấn luyện **một tập teacher** (chất lượng khác nhau) × **một tập student** (paradigm khác nhau) → mới trả lời được RQ1 (paradigm nào lợi nhất) & RQ2 (teacher mạnh → student tốt hơn?)

| Vai trò | Model | Paradigm |
|---|---|---|
| **Teacher** | EfficientNetV2-M | CNN cải tiến (fused-MBConv) |
| Teacher | ConvNeXtV2-Base | Modern ConvNet |
| Teacher | MaxViT-Base | CNN–Transformer hybrid |
| **Student** | MobileNetV4-Conv-M (8,44M) | Depthwise-separable CNN |
| Student | FastViT-SA12 (10,56M) | CNN + Reparameterization |
| Student | EfficientFormerV2-S2 (12,13M) | Attention–CNN hybrid |
| Student | RepViT-M1.0 | CNN mang thiết kế ViT |

- Chung head: GAP → Dropout → Dense(1); `sigmoid` tại inference; backbone từ `timm` (`timm≥1.0`); teacher **luôn đóng băng** khi distill
- Ma trận đầy đủ = **3 teacher × 4 student × 2 nhánh (KD / baseline) × 5 fold**

**Ghi chú thuyết trình:** Nói rõ ý đồ thiết kế: *một dải teacher có chất lượng khác nhau* × *một dải student trải nhiều paradigm*, để quét được cả hai câu hỏi (paradigm nào hưởng lợi nhất, teacher mạnh có tạo student tốt hơn không) trong cùng một khung đối chứng. Params của student là số **thực đo**; 3 teacher và RepViT chưa chạy job benchmark nên không trích số.

**Gợi ý hình:** Bảng trên, cột trái tô màu theo Teacher/Student; sắp teacher theo chất lượng tăng dần.

---

## Slide 16 — Hàm mất mát chưng cất

**Tiêu đề:** Hàm mất mát KD (điều chỉnh cho mất cân bằng)

**Nội dung:**
```
L_total = α · L_hard + (1 − α) · T² · L_soft
```
- `L_hard = FocalLoss(z_student, y_true)` — γ=2, α=0,25 [17] → xử lý mất cân bằng
- `L_soft = BCE(σ(z_student/T), σ(z_teacher/T))` — truyền "dark knowledge", **T = 4,0**
- Hệ số cân bằng **α = 0,3** → 30% nhãn cứng + 70% nhãn mềm (thiên về học từ teacher)
- Nhánh **baseline**: một cờ cấu hình `use_kd=false` chuyển sang `Trainer` + Focal Loss thuần, **không nạp teacher** (tương đương α = 1,0) → **kiểm soát tuyệt đối** thí nghiệm

**Ghi chú thuyết trình:** Điểm mới so với Hinton gốc: thay CE hard-label bằng **Focal Loss** vì mất cân bằng cực đoan. Nhấn cơ chế baseline — cùng một script, cùng data/seed/siêu tham số, chỉ đổi một cờ để bỏ teacher — đây là nền để đo Δ sạch. (Nếu hội đồng hỏi thêm: repo còn cài sẵn 2 biến thể tắt-mặc-định — MSE trên logit thô, và chưng cất quan hệ ở mức đặc trưng RKD — để ngỏ cho giai đoạn sau.)

**Gợi ý hình:** Đặt **công thức lớn** làm trọng tâm slide; bên cạnh **tái dùng `figures/kd_flow_slide.png`** (đã có khối "Combined KD loss" ghi rõ `0.3·focal + 0.7·T²·BCE(soft), T=4` và teacher đóng băng) để minh họa 2 dòng gradient hard/soft đổ vào student. Không vẽ sơ đồ mới — hình này đã thể hiện đúng cơ chế.

---

## Slide 17 — Thiết kế thực nghiệm so sánh đối chứng

**Tiêu đề:** Thiết kế *ceteris paribus* & ma trận thực nghiệm

**Nội dung:**
- Nguyên tắc: mỗi student chạy **2 nhánh (KD / không KD)** với **cùng** dữ liệu, seed, siêu tham số, quy trình — **chỉ khác hàm mất mát** → mọi Δ đều quy về KD
- Ma trận thực nghiệm (5-fold CV) — **tổng 110 lượt huấn luyện**:

| Nhóm | Lượt | Trạng thái |
|---|---|---|
| 3 teacher × 5 fold | 15 | ✅ |
| 3 teacher ISIC-only (ablation PAD) × 5 fold | 15 | ✅ |
| 4 student baseline × 5 fold | 20 | ✅ |
| KD: 3 teacher × 4 student × 5 fold | 60 | 🔄 20/60 |

- Định lượng: **ΔpAUC**, **ΔAUPRC** (KD − baseline); Δ nhỏ hơn 1 std được mô tả là "trong nhiễu"
- Kiểm định ý nghĩa: **Paired t-test (p < 0,05)** trên 5 fold — *bước còn lại*, hiện đang báo cáo mean ± std và so Δ với std

**Gợi ý hình:** Sơ đồ nhánh Student → {KD, Baseline} → so sánh Δ; ma trận teacher×student dạng lưới, tô ô đã xong.

---

# PHẦN 5 — PHƯƠNG PHÁP THỰC HIỆN

---

## Slide 18 — Pipeline thực thi đầu–cuối

**Tiêu đề:** Quy trình thực thi từ dữ liệu thô đến mô hình trên điện thoại

> **⚠️ Dựng slide:** **DÙNG HÌNH SẴN: `figures/kd_pipeline_slide.png`** làm hình chính (bản 16:9). Hình này tóm tắt pipeline thành **3 bước** — *Bước 1: Huấn luyện teacher · Bước 2: Chưng cất KD (×3 student) · Bước 3: Đánh giá + triển khai on-device* — và đã ghi đúng công thức loss, checkpoint `.pth`, export ExecuTorch `.pte`. **Không vẽ lại.** Danh sách 7 khối chi tiết bên dưới là **phần chú thích / lời thuyết trình** ánh xạ vào 3 bước của hình (Bước 1 ⊇ khối 1–3, Bước 2 ⊇ khối 4–5, Bước 3 ⊇ khối 6–7) — dùng để nói, không cần vẽ thành 7 ô riêng.

**7 khối chi tiết (ánh xạ vào 3 bước của hình, dùng khi thuyết trình):**
1. **Dữ liệu thô:** ISIC 2024 (HDF5 + metadata) + PAD-UFES-20
2. **Tiền xử lý offline:** giải mã → resize 224×224 → lọc ảnh hỏng/trùng → chuẩn hóa nhãn nhị phân
3. **Chia dữ liệu:** tách held-out test (~17%) patient-disjoint → `StratifiedGroupKFold(K=5)`
4. **Tăng cường online (Albumentations):** flip, rotate 90°, ShiftScaleRotate, color jitter, CLAHE, Gaussian blur — **không** MixUp/CutMix/CutOut
5. **Huấn luyện:** Teacher (Focal Loss) → Student {KD `KDTrainer` / Baseline `Trainer`}; sampler undersampling 1:5/epoch
6. **Đánh giá & tổng hợp:** test độc lập → `test_metrics.json` → aggregate 5-fold (mean±std) → Paired t-test
7. **Triển khai:** export **ExecuTorch .pte (FP32)** → benchmark **Pixel 6a** → phân tích Pareto

**Nội dung (bullet phụ nếu còn chỗ):**
- Cấu hình bằng **Hydra**; khởi chạy qua lớp script `run/*.sh` (`bash run/train_teacher.sh TEACHER=…`) — **1 lệnh = 1 tiến trình = cả 5 fold**, log tee ra file nên mất SSH không mất kết quả
- Môi trường: **máy chủ GPU thuê ngoài (2 máy × 1 RTX 3090)**, không có hệ quản lý hàng đợi — chạy dưới `tmux`
- Huấn luyện: **AdamW** (LR 1e-4 backbone / 1e-3 head), cosine + 3 epoch warmup, ≤50 epoch, early stopping theo `val_loss`, **checkpoint theo `val pAUC@80`**

**Gợi ý hình:** `figures/kd_pipeline_slide.png` (3 bước băng ngang). Nếu muốn tô sáng, nhấn **Bước 2 (Chưng cất KD)** và **Bước 3 (Đánh giá + triển khai)** — hai bước cốt lõi của đóng góp.

---

## Slide 19 — Đánh giá 3 tầng & triển khai

**Tiêu đề:** Đánh giá 3 tầng độc lập + đo trên máy thật

**Nội dung:**
- **(i) In-domain** — test split ISIC 2024 + PAD-UFES-20: pAUC@TPR≥80%, AUPRC, AUC-ROC, sensitivity, specificity, F1 (ngưỡng theo Youden's J)
- **(ii) Cross-domain** — HAM10000 [15] (dermoscopic, **không** train) → đo tổng quát hóa sang miền ảnh khác
- **(iii) Fairness** — Fitzpatrick17k [16], nhóm da I–II / III–IV / V–VI; đo **khoảng cách hiệu năng max–min** giữa các nhóm
- **Triển khai:** export **.pte (FP32)** → benchmark **Pixel 6a** (latency trung vị, tail p95, FPS, kích thước) → **Pareto AUPRC vs latency**

**Gợi ý hình:** 3 tầng đánh giá xếp chồng + icon điện thoại cho benchmark.

---

## Slide 19B (tùy chọn) — Luồng suy luận trên thiết bị (ứng dụng minh họa)

> **Slide chèn thêm — tùy chọn.** Nếu dùng, đánh số lại các slide sau thành 20→21… hoặc giữ nhãn "19B" để không phải đánh số lại toàn bộ. Bỏ qua slide này nếu cần rút thời lượng — nó minh họa *cách mô hình được dùng thực tế*, bổ trợ cho phần triển khai (Slide 19) và ứng dụng (Slide 24).

**Tiêu đề:** Từ mô hình đến ứng dụng — luồng suy luận trên điện thoại

**Nội dung:**
- **Chạy hoàn toàn offline, trên máy** — mô hình student tốt nhất được export **ExecuTorch `.pte` (FP32)**, không cần cloud, bảo vệ riêng tư
- Luồng: **Ảnh (camera/thư viện) → Cổng kiểm tra chất lượng (mờ/độ sáng) → Suy luận `.pte` → xác suất ác tính `P(malignant)` → Ngưỡng (Youden's J) → Khuyến nghị**
- Ngưỡng quyết định **không cố định 0,5** mà chọn theo **Youden's J** đã lưu cùng mỗi model → cân bằng độ nhạy/độ đặc hiệu đúng như lúc đánh giá
- Đầu ra hướng người dùng: **Nguy cơ thấp** (tự theo dõi, tái khám ~3 tháng) / **Nguy cơ cao** (đi khám bác sĩ da liễu sớm) — **công cụ sàng lọc, không thay chẩn đoán**

**Ghi chú thuyết trình:** Slide này trả lời câu "sau khi distill thì dùng thế nào" (RQ3 ở góc độ trải nghiệm). Nhấn 2 ý: (1) tất cả chạy on-device/offline nên riêng tư + không phụ thuộc mạng; (2) cổng chất lượng + ngưỡng lâm sàng cho thấy đây là công cụ *sàng lọc có trách nhiệm*, không phải hộp đen. Nếu Hội đồng hỏi về an toàn lâm sàng, đây là slide để giải thích.

**Gợi ý hình:** **DÙNG HÌNH SẴN: `figures/app_inference_slide.png`** — chèn full-width làm hình chính, không vẽ lại. (Lưu ý trung thực khi trình bày: cổng kiểm tra chất lượng là bước *phía ứng dụng* dự kiến, phần suy luận `.pte` + ngưỡng Youden's J là đã có trong pipeline.)

---

# PHẦN 6 — ĐỘ ĐO & KẾT QUẢ BƯỚC ĐẦU

---

## Slide 20 — Độ đo đánh giá: chọn gì, vì sao, ngưỡng dùng được

**Tiêu đề:** Các độ đo — vì sao chọn & khoảng giá trị "dùng được"

**Nội dung:**

| Độ đo | Vì sao chọn (ở prevalence ~0,4%) | Khoảng & ngưỡng "dùng được" |
|---|---|---|
| **AUPRC** 🔴 | Headline metric: nhạy với khả năng tìm đúng **lớp hiếm**; AUC-ROC bị lạc quan giả | Baseline ngẫu nhiên ≈ **prevalence 0,004**; cần **vượt xa** — ở bài này **>0,5** là rất mạnh (≈125–170× baseline) |
| **pAUC@TPR≥80%** 🔴 | Metric **chính thức ISIC 2024**; chỉ thưởng vùng độ nhạy cao (sàng lọc) | Chuẩn hóa **[0,02 ngẫu nhiên – 0,20 hoàn hảo]**; **>0,17** = rất tốt |
| **Sensitivity** 🔴 | "Không bỏ sót ca ác tính" — chỉ số an toàn lâm sàng quan trọng nhất | Sàng lọc mong muốn **≥0,90** |
| **Specificity** 🔴 | Kiểm soát số **báo động giả** người dùng phải chịu | Mong muốn **≥0,90** |
| AUC-ROC 🟡 | Dễ đối chiếu văn liệu, **nhưng lạc quan** → chỉ dùng kèm | >0,97 nhưng **không đứng một mình** |
| F1 / Accuracy ⚪ | Ở 0,4% dương: accuracy ~99,6% dù đoán "toàn lành" → **vô nghĩa** | Chỉ tham khảo |

- Ngưỡng quyết định chọn theo **Youden's J** (không phải 0,5), lưu & triển khai đúng ngưỡng mỗi model

**Ghi chú thuyết trình:** Nếu hội đồng hỏi "bao nhiêu là tốt": AUPRC phải so với baseline = prevalence (0,004), nên 0,6+ là *rất mạnh*; pAUC gần trần 0,20 là gần tối ưu. Đây là lý do em báo cáo AUPRC + pAUC, không dùng accuracy.

**Gợi ý hình:** Bảng trên; cột phải dùng thanh gradient "ngưỡng dùng được".

---

## Slide 21 — Kết quả bước đầu (1): độ chính xác — student nhỏ đạt vùng độ nhạy của teacher

**Tiêu đề:** Kết quả bước đầu — độ chính xác (5-fold CV, test độc lập, mean ± std)

**Nội dung:**

**Teacher (standalone, đủ 5 fold):**
| Teacher | AUPRC | pAUC@80 | Sensitivity |
|---|---|---|---|
| **MaxViT-Base** | **0,6566 ± 0,0211** | 0,1830 | 0,924 |
| ConvNeXtV2-Base | 0,6506 ± 0,0306 | 0,1822 | 0,920 |
| EfficientNetV2-M | 0,6298 ± 0,0488 | 0,1826 | **0,927** |

**Student sau KD (teacher = EfficientNetV2-M, đủ 5 fold cả 4 student):**
| Student | AUPRC | pAUC@80 | Sens | Sens@95Spec |
|---|---|---|---|---|
| EfficientFormerV2-S2 | **0,6220** | 0,1849 | 0,929 | 0,931 |
| FastViT-SA12 | 0,6209 | 0,1853 | 0,929 | **0,934** |
| **MobileNetV4-Conv-M** | 0,6056 | **0,1859** | **0,933** | 0,930 |
| RepViT-M1.0 | 0,5537 | 0,1832 | 0,924 | 0,923 |

- 🎯 **Phát hiện chính:** **cả 4 student sau KD đều đạt pAUC@80 (0,183–0,186) ngang hoặc CAO HƠN cả 3 teacher (0,182–0,183)** và độ nhạy tương đương — dù nhẹ hơn nhiều lần. Đúng mục tiêu của KD: nén về mobile mà giữ vùng độ nhạy cao.
- ⚠️ **Trung thực:** ở **AUPRC** thì teacher vẫn cao hơn (0,63–0,66 vs 0,55–0,62). Không nói "student vượt teacher".

**Ghi chú thuyết trình:** Mở bằng phát hiện chắc chắn nhất: student nhỏ đạt vùng độ nhạy của teacher. Ngay sau đó chủ động nói phần chưa đạt (AUPRC) — hội đồng đánh giá cao sự trung thực hơn tô hồng. Nếu bị hỏi teacher nào mạnh nhất: MaxViT ≈ ConvNeXtV2 nhưng **chênh trong 1 std**, không tuyên bố tuyệt đối.

**Gợi ý hình:** 2 bảng cạnh nhau; vẽ một đường ngang ở mức pAUC teacher (~0,183) để thấy 4 student KD đều nằm trên/ngang đường đó.

---

## Slide 21B — Kết quả bước đầu (2): ablation dữ liệu — PAD-UFES-20 có thực sự giúp không?

**Tiêu đề:** Ablation dữ liệu — chứng minh (không giả định) rằng trộn PAD-UFES-20 là đúng

**Nội dung:**
- **Thiết kế đối chứng:** cùng cấu hình, cùng **một tập test**, chỉ khác TRAIN+VAL — *ISIC+PAD* vs *ISIC-only*. Chạy cho **cả 3 teacher**, mỗi nhánh 5 fold (30 lượt huấn luyện).
- **Ô quyết định = subset ảnh PAD trong test** (miền lâm sàng mà nhánh ISIC-only chưa từng thấy):

| Teacher | ΔAUPRC | ΔpAUC@80 | ΔSens | ΔSens@95Spec |
|---|---|---|---|---|
| EfficientNetV2-M | **+0,1241** | +0,0349 | +0,0756 | +0,1844 |
| ConvNeXtV2-Base | **+0,0920** | +0,0356 | +0,1256 | +0,1089 |
| MaxViT-Base | **+0,1311** | +0,0352 | +0,1256 | **+0,2322** |

- **Miền ISIC gốc: Δ nằm trong nhiễu** → thêm PAD **không hại** miền dermoscopy
- 🎯 **Kết luận:** trộn ảnh smartphone lâm sàng giúp mô hình tổng quát hóa **rõ rệt** sang đúng loại ảnh mà ứng dụng thực tế sẽ gặp — đúng với **cả 3/3** teacher

**Ghi chú thuyết trình:** Đây là slide cho thấy đề tài *kiểm chứng* các lựa chọn thiết kế chứ không chỉ khẳng định. Nhấn: kết quả nhất quán trên cả 3 teacher nên không phải may mắn của một kiến trúc. Nếu hội đồng hỏi "sao không đo trên toàn bộ test": vì nhánh ISIC-only chưa từng thấy ảnh PAD nên số whole-test bị thổi phồng — subset PAD mới là ô so sánh công bằng.

**Gợi ý hình:** Biểu đồ cột nhóm: 3 teacher × 2 nhánh (ISIC-only vs +PAD) trên AUPRC của subset PAD.

---

## Slide 22 — Kết quả bước đầu (3): KD giúp gì & chạy trên Pixel 6a ra sao

**Tiêu đề:** Hiệu quả KD (trung thực) + benchmark thật trên Pixel 6a

**Nội dung:**

**Δ = KD − Baseline** (teacher EfficientNetV2-M, cùng data/seed/siêu tham số, **4/4 student × 5 fold**):

| Student | ΔpAUC@80 | ΔAUPRC | ΔSens | ΔSens@95Spec |
|---|---|---|---|---|
| RepViT-M1.0 | **+0,0115** | **+0,0172** | +0,0124 | **+0,0324** |
| FastViT-SA12 | +0,0028 | +0,0127 | +0,0066 | +0,0108 |
| MobileNetV4-Conv-M | +0,0061 | −0,0045 | +0,0124 | +0,0141 |
| EfficientFormerV2-S2 | +0,0037 | −0,0062 | +0,0108 | +0,0133 |

- ✅ **Chắc chắn: KD cải thiện 4/4 student** ở **pAUC@80, AUC, Sensitivity và Sens@95Spec** → đúng mục tiêu y tế "không bỏ sót ca ác tính"
- ⚠️ **Trung thực: ΔAUPRC hỗn hợp** (2 dương / 2 âm nhẹ) — **cả 4 đều nhỏ hơn 1 std → nằm trong nhiễu**, không phải "KD làm hại". Bằng chứng KD của đề tài nằm ở **pAUC + độ nhạy**, không phải AUPRC

**Benchmark on-device Pixel 6a (`.pte` FP32, 4 threads, median):**
| Model (KD ← EfficientNetV2-M) | AUPRC | pAUC | Latency | Size .pte | FPS |
|---|---|---|---|---|---|
| **MobileNetV4-Conv-M** | 0,6056 | **0,1859** | **22,6 ms** | **32 MB** | 44 |
| EfficientFormerV2-S2 | **0,6220** | 0,1849 | 42,8 ms | 47 MB | 23 |
| FastViT-SA12 | 0,6209 | 0,1853 | 65,5 ms | 40 MB | 15 |

- ⚠️ **Thứ hạng latency KHÔNG theo params:** FastViT chậm nhất (65 ms) dù **ít param hơn** EfficientFormerV2 (10,6M vs 12,1M) → **phải đo on-device thật, không suy từ FLOPs**. FastViT bị lấn át: chậm hơn 1,5× mà độ chính xác ngang
- 🎯 **Khuyến nghị deploy:** **MobileNetV4-Conv-M ← EfficientNetV2-M** — thắng ở *cả hai* trục: nhanh nhất/nhẹ nhất **và** dẫn đầu pAUC@80 (0,1859), AUC (0,9852), Sens (0,933) trong toàn bộ student

**Ghi chú thuyết trình:** Trung thực là điểm cộng: KD chắc chắn ở pAUC/Sens (4/4), còn AUPRC nằm trong nhiễu — nói thẳng, và giải thích vì sao std lớn hơn Δ ở prevalence 0,39%. Nếu bị hỏi "sao chỉ có một teacher": ma trận KD của 2 teacher còn lại đang chạy, đó là công việc còn lại trong kế hoạch. Nhấn latency đảo — chính là lý do đề tài *phải* benchmark trên máy thật.

**Gợi ý hình:** Trái — bảng benchmark; phải — scatter Pareto AUPRC (trục y) vs latency (trục x), khoanh MobileNetV4 là "điểm cân bằng".

---

# PHẦN 7 — KẾ HOẠCH & KẾT LUẬN

---

## Slide 23 — Kế hoạch thực hiện

**Tiêu đề:** Kế hoạch thực hiện (06/2026 – 11/2026)

**Nội dung:**

| GĐ | Nội dung | Thời gian | Trạng thái |
|---|---|---|---|
| 1 | Pipeline + tiền xử lý + 5-fold CV + test holdout độc lập | 06/2026 | ✅ Xong |
| 2 | Huấn luyện 3 teacher (15 lượt) | 07/2026 | ✅ Xong |
| 3 | **Ablation dữ liệu** (teacher ISIC-only, 15 lượt) | 07/2026 | ✅ Xong |
| 4 | 4 student nhánh baseline (20 lượt) | 07–08/2026 | ✅ Xong |
| 5 | Ma trận KD: 3 teacher × 4 student × 5 fold (60 lượt) | 08–09/2026 | 🔄 20/60 |
| 6 | Export `.pte` + parity check + benchmark Pixel 6a + Pareto | 09/2026 | 🔄 đã đo 3 kiến trúc |
| 7 | Cross-domain (HAM10000) + fairness (Fitzpatrick17k) | 09–10/2026 | ⏳ Chưa |
| 8 | Tổng hợp 5-fold + Paired t-test + tương quan teacher↔Δ + hiệu chuẩn | 10/2026 | ⏳ Chưa |
| 9 | Viết luận văn | 09–11/2026 | ⏳ |
| 10 | Hoàn thiện, nộp & bảo vệ | 11/2026 | ⏳ |

**Ghi chú thuyết trình:** Đã hoàn thành **70/110 lượt huấn luyện**. Kết quả ở slide 21–22 chính là output của GĐ 1–6. Đường găng là GĐ 5 — thiếu nó thì chưa trả lời được câu "teacher nào chưng cất tốt nhất"; em đã ghi rõ điều đó thay vì trích số của đợt huấn luyện cũ.

**Gợi ý hình:** Gantt chart ngang, tô màu trạng thái (xong/đang/chưa).

---

## Slide 24 — Kết luận & Cảm ơn

**Tiêu đề:** Kết luận

**Nội dung:**
- Đề tài **lấp đồng thời 3 khoảng trống**: KD trên nhiều paradigm · vai trò chất lượng teacher · khả thi triển khai điện thoại thực tế
- **Kết quả bước đầu đã chứng minh khả thi:**
  - KD cải thiện **nhất quán 4/4 student** ở pAUC@TPR≥80%, AUC và độ nhạy — student nhỏ đạt vùng độ nhạy của teacher
  - **Ablation chứng minh** trộn PAD-UFES-20 giúp **cả 3/3 teacher** trên ảnh lâm sàng mà không hại miền gốc
  - Đã **chạy thật** trên Pixel 6a: 22–65 ms, `.pte` 32–47 MB
- **Còn lại (nói rõ):** hoàn tất ma trận KD cho 2 teacher còn lại để trả lời "teacher nào chưng cất tốt nhất"; cross-domain + fairness; kiểm định thống kê
- Đóng góp: **bằng chứng thực nghiệm có hệ thống** + **pipeline & báo cáo triển khai Android tái sử dụng được**
- Ứng dụng: sàng lọc ung thư da thời gian thực, bảo vệ riêng tư, phù hợp vùng thiếu nguồn lực y tế

**Trân trọng cảm ơn Hội đồng!**

**Gợi ý hình:** Slide cảm ơn tối giản + thông tin liên hệ học viên.

---

## (Phụ lục) Slide 25 — Tài liệu tham khảo

**Tiêu đề:** Tài liệu tham khảo (đánh số theo slide)

**Nội dung:**
- [1] Wang, M., et al. (2025). Recent global patterns in skin cancer incidence, mortality, and prevalence. *Clinics in Dermatology*.
- [2] De Pinto, G., et al. (2024). Global trends in cutaneous malignant melanoma incidence and mortality. *Melanoma Research*.
- [3] Siegel, R. L., et al. (2020). Cancer statistics, 2020. *CA: A Cancer Journal for Clinicians*.
- [4] Kittler, H., et al. (2002). Diagnostic accuracy of dermoscopy. *The Lancet Oncology*.
- [5] Esteva, A., et al. (2017). Dermatologist-level classification of skin cancer with deep neural networks. *Nature*.
- [6] Tan, M., & Le, Q. V. (2019). EfficientNet: Rethinking Model Scaling for CNNs. *ICML*.
- [7] Dosovitskiy, A., et al. (2021). An Image is Worth 16×16 Words (ViT). *ICLR*.
- [8] Price, W. N., & Cohen, I. G. (2019). Privacy in the age of medical big data. *Nature Medicine*.
- [9] Dhar, T., et al. (2024). Challenges and opportunities in edge AI for skin disease diagnosis. *Scientific Reports*.
- [10] Howard, A., et al. (2019). Searching for MobileNetV3. *ICCV*.
- [11] Mehta, S., & Rastegari, M. (2022). MobileViT. *ICLR*.
- [12] Kurtansky, N. R., et al. (2024). ISIC 2024 Challenge: Skin Cancer Detection with 3D-TBP. *ISIC Archive*.
- [13] Hinton, G., et al. (2015). Distilling the Knowledge in a Neural Network. *arXiv:1503.02531*.
- [14] Pacheco, A. G., & Krohling, R. A. (2020). PAD-UFES-20 / impact of patient clinical information. *Computers in Biology and Medicine*.
- [15] Tschandl, P., et al. (2018). The HAM10000 dataset. *Scientific Data*.
- [16] Groh, M., et al. (2021). Evaluating DNNs with the Fitzpatrick 17k Dataset. *CVPR Workshop*.
- [17] Lin, T. Y., et al. (2017). Focal Loss for Dense Object Detection. *ICCV*.
- [18] Ha, Q., et al. (2020). Identifying Melanoma Images using EfficientNet Ensemble. *arXiv:2010.05351*.
- [19] Ding, Y., et al. (2023). HI-MViT: a lightweight model for explainable skin disease classification. *Digital Health*.
- [20] Islam, N., et al. (2024). Leveraging Knowledge Distillation for Lightweight Skin Cancer Classification. *arXiv:2406.17051*.
- [21] Saha, S., et al. (2025). Knowledge distillation for skin cancer classification on lightweight models. *Healthcare Technology Letters*.
- [22] Suryakanth, P., et al. (2025). MTAKD: multi-teacher agreement knowledge distillation. *Scientific Reports*.

**Gợi ý hình:** Danh sách 2 cột gọn; để dự phòng khi Hội đồng hỏi nguồn.
