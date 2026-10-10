# Review vòng 2: phần đánh giá sau khi sửa (04/10/2026)

> **Nguồn duy nhất** là `PROJECT_BRIEF_FOR_REVIEW.md` bản 2 (04/10/2026). Reviewer **không** đọc code hay repo, không chạy
> lại số nào. Số hoặc lấy từ brief, hoặc là phép tính/ước tính của reviewer (ghi rõ).
> Bản này nối tiếp `docs/REVIEW_DANH_GIA_2026-10-03.md` (R-ngoài).
>
> Ký hiệu: ✅ ổn · ⚠️ cần xem lại · ❌ nên sửa · 🔍 cần kiểm trong repo

---

## 0. Trả lời câu hỏi chính

> *Phần evaluation hiện tại còn khó như lo lắng không?*

**Không còn khó kiểu "đo sai", nhưng giờ khó vì model thật sự chưa đủ tốt ở một chỗ.**

| | Bản 1 (03/10) | Bản 2 (04/10) |
|---|---|---|
| Nguồn của độ khó | Cách đo: superiority test, mốc sai loại ảnh, phán quyết sát mép, 8 cổng AND | Hiệu năng thật: III-b trượt với **cận trên** < 0,80 |
| III-a / B2 (ảnh PAD) | Chưa chứng minh (cận dưới 0,74 so với mốc 0,81) | **Đạt (tạm)** |
| Fitzpatrick | Sát mép (cận dưới 0,4699 so với 0,47) | **Trượt rõ** (điểm 0,52–0,60) |
| C2 | Đòi student vượt teacher | Non-inferiority, **đạt (tạm)** |

Bài toán đã chuyển từ "khung đánh giá quá khó" sang "model chưa tổng quát hoá được sang ảnh lâm sàng khác nguồn". Đây là
chuyển biến đúng hướng. Tuy vậy, **mốc của III-b vẫn đáng bàn** (mục 2), còn III-a và C2 **có thể bị cho là dễ** (mục 1).

---

## 1. Độ khó của từng cổng hiện tại

| Cổng | Kết quả P0 (fold 4) | Độ khó | Nhận xét |
|---|---|---|---|
| I-1, II-1/2/3 | II-1/2 đạt; I-1, II-3 chưa đo | ✅ hợp lý | Đo kỹ thuật. Latency theo kiến trúc 39,5 ms so với mốc 80 ms nên khả năng cao sẽ đạt |
| III-a | sens 0,873 [0,818; 0,913] · spec 0,731 [0,667; 0,786] | ⚠️ có vẻ dễ vì post-hoc | Xem 1.1 |
| **III-b** | sens sáng 0,604 · trung bình 0,520 · tối 0,524, cận trên < 0,80 | ❌ khó thật, mốc có thể chặt hơn mọi tham chiếu | Xem mục 2 |
| C2 | cận dưới ΔAUPRC: PAD +0,0396 · Fitz −0,0008 · HAM −0,0068 | ⚠️ dễ vì teacher yếu | Xem 1.2 |

### 1.1 ⚠️ III-a: mốc trông như được "may đo"

- S_min = 0,80, Sp_min = 0,60 được chốt **sau** khi đã thấy cận dưới của P0 là 0,818 / 0,667. S_min nằm ngay dưới 0,818.
  Hội đồng có thể hỏi mốc có được chọn theo kết quả không.
- Quy tắc ngưỡng 90% được chọn sau khi xem test PAD ⇒ 0,873 là **số lạc quan**.
- ⇒ Nhãn "ĐẠT (tạm)" của III-a **chưa có giá trị xác nhận**. Chỉ dữ liệu mới (U8, bệnh viện) mới trả lời được.

**Cần làm:**
- [ ] Viết lập luận use case cho 0,80 / 0,60 **độc lập với số của P0** (chi phí bỏ sót và chi phí báo nhầm), có GVHD xác nhận.
- [ ] Khai trong luận văn: mốc chốt sau khi thấy cận dưới 0,818 / 0,667.

### 1.2 ⚠️ C2 đạt chủ yếu vì teacher chưa được train đúng công thức

- Teacher thiếu sampler theo nguồn và chỉ có checkpoint pAUC (crosscheck §1.5).
- R7: KD không sampler − teacher, cùng công thức, trên PAD: +0,0032 [−0,0169; +0,0251] ⇒ ngang nhau.
- ⇒ Mức P0 hơn teacher +0,0619 trên PAD phần lớn đến từ sampler/checkpoint, không phải chất lượng KD.
- Khi train lại teacher đúng công thức (S16), C2 **có thể khó hơn**.

**Cần làm:**
- [ ] Luận văn ghi rõ: C2 hiện so với teacher chưa tối ưu.
- [ ] 🔍 δ = 5% AUPRC của teacher là δ **tương đối**: trên miền có AUPRC teacher thấp (HAM?), δ tuyệt đối rất nhỏ. Kiểm
      giá trị δ tuyệt đối của từng miền PAD / Fitz / HAM.

---

## 2. ❌ III-b: điểm nghẽn thật

### 2.1 Mốc 0,80 cao hơn mọi tham chiếu bên ngoài

| Tham chiếu | Độ nhạy | Điểm vận hành | Nguồn |
|---|---|---|---|
| Bác sĩ nhìn **ảnh lâm sàng** | 0,47 | spec 80% | Cochrane Dinnes 2018 (theo brief bản 2, đã kiểm qua web) |
| P0 trên Fitzpatrick | ≈ 0,49 | spec 80% | brief bản 1, B3 |
| P0 trên Fitzpatrick tại ngưỡng app | ≈ 0,57 (gộp) | spec ≈ 0,77 | brief bản 1, bảng hành vi tại ngưỡng |
| **Mốc III-b** | **≥ 0,80, từng tông** | spec ≥ 0,60 | tác giả, chốt tạm 04/10 |

- Model **ngang mức bác sĩ** trên loại ảnh này, nhưng III-b đòi khoảng **1,7 lần** mức đó.
- Lưu ý: điểm vận hành khác nhau (spec 80% so với ≥ 60%), và Cochrane chỉ tính melanoma ⇒ so sánh **định hướng**, không
  chặt. Nhưng hướng thì rõ.

### 2.2 Lý do giữ III-b là lý do dựa vào kết quả

Hợp đồng §1: không giữ III-b thì "khung chỉ chấm ảnh PAD và P0 gần như đạt". Đây là post-hoc **theo chiều ngược**: đặt
cổng để tránh đạt quá dễ. Động cơ trung thực, nhưng về phương pháp thì cũng là chọn mốc sau khi xem số. Câu hỏi hội đồng
dễ đặt ra: *"Vì sao 0,80, mà không phải mức có tham chiếu?"*

### 2.3 III-b gộp hai câu hỏi khác nhau

1. **Tổng quát hoá khác nguồn:** model có giữ hiệu năng trên ảnh lâm sàng khác PAD không?
2. **Công bằng theo tông da:** chênh lệch giữa các tông có chấp nhận được không?

Đặt mốc tuyệt đối cho **từng** tông với AND cả độ nhạy lẫn độ đặc hiệu thực chất là **6 điều kiện** phải đạt cùng lúc
trên các nhóm nhỏ. Tách ra thì chẩn đoán vấn đề rõ hơn.

### 2.4 Fitzpatrick17k có phải proxy tốt cho "camera thực tế"?

- Câu hỏi trung tâm số 2 nói về **ảnh camera thực tế**. Fitzpatrick17k là ảnh atlas da liễu trên web, cách chụp và chất
  lượng khác ảnh người dùng tự chụp.
- Theo hiểu biết của reviewer, đã có nghiên cứu (Abhishek và cộng sự, 2024) báo cáo Fitzpatrick17k có **ảnh trùng lặp và
  nhãn sai**. 🔍 **Cần kiểm lại nguồn này.** Nếu đúng thì giả định độc lập của Wilson CI bị vi phạm (brief §7 đã tự nêu
  rủi ro này).

### 2.5 Lý do tốt hơn để giữ một cổng theo tông da

Người dùng Việt Nam phần lớn thuộc nhóm tông **trung bình** (thường xếp Fitzpatrick III–IV, tuỳ cách gộp nhóm). Đây lại
là nhóm **yếu nhất** của P0 (0,520 tại ngưỡng app). ⇒ Yêu cầu theo tông da **gắn trực tiếp với người dùng mục tiêu**.
Đây là lập luận mạnh hơn lý do "để khung không quá dễ".

🔍 Kiểm cách gộp Fitzpatrick I–VI thành ba nhóm sáng / trung bình / tối để biết III–IV rơi vào nhóm nào.

---

## 3. Đề xuất

| # | Đề xuất | Lý do |
|---|---|---|
| D1 | **Cổng chính "triển khai được" = III-a chấm lại trên dữ liệu bệnh viện (U8)**, tách theo tông nếu cỡ mẫu đủ | Đúng miền (camera thật, người Việt), không dính post-hoc, trả lời thẳng câu hỏi trung tâm 2 |
| D2 | **Fitzpatrick (III-b) thành cổng tổng quát hoá có tham chiếu**: sens@spec80 so với mốc bác sĩ trên ảnh lâm sàng (0,47) theo kiểu non-inferiority; công bằng báo cáo bằng chênh lệch (R12) | Mốc có nguồn độc lập thay vì 0,80 tự đặt. **Phải khai là thay đổi post-hoc** |
| D3 | Nếu giữ 0,80 trên Fitz: gọi là **mục tiêu**, không phải điều kiện "đạt" | Trung thực về việc chưa có tham chiếu nào ở mức đó |
| D4 | **Tính điểm ROC trên Fitz tại spec 0,60**, từng tông | Biết khoảng cách thật đến (0,80; 0,60). Hiện chỉ biết sens ≈ 0,49 @ spec 0,80 và ≈ 0,57 @ spec ≈ 0,77, nên gap có vẻ ≥ 0,1 (ước tính) |
| D5 | Ghi **số ca ác tính** theo từng tông trong Fitz headline | Wilson CI phụ thuộc số ca dương, không phải 411 / 1.599 / 2.310 |
| D6 | **Cỡ mẫu U8 tính theo độ nhạy thật thấp hơn 0,873** | 0,873 là số lạc quan, và miền bệnh viện có thể khác PAD |

**Cỡ mẫu U8 cho độ nhạy, mốc S_min = 0,80** (binomial Wald; cận dưới CI 95% hai phía, tương đương α = 0,025 một phía; power 80%; ước tính thô):

| Sens thật | Số ca ác tính cần |
|---|---|
| 0,87 | ~180 |
| 0,85 | ~400 |
| 0,83 | ~1.200 |

Nên chạy simulation để có số chính xác. Với độ đặc hiệu (Sp_min = 0,60), nếu spec thật ≈ 0,73 thì cần khoảng 90 ca lành
(ước tính); ca lành thường dễ thu hơn.

**Ghi chú:** dù chọn hướng nào, cải thiện III-b là **bài toán model/dữ liệu** (RQ5: thêm ảnh lâm sàng thật, đa tông
da), không còn là bài toán khung đánh giá. Bằng chứng hiện có: DDI giúp trên Fitz; domain augmentation thì hại.

---

## 4. Nhận xét về cách xử lý các nhận xét của R-ngoài

| Mục | Đánh giá | Ghi chú |
|---|---|---|
| Minh bạch quy trình (timeline UTC, khai hai commit message sai, dòng test P1 bị lộ) | ✅ | Rất tốt. Ảnh hưởng thực tế nhỏ vì bước chọn chỉ dùng val và kết quả giữ P0 |
| 1.1 Mốc B2 | ✅ | Đã kiểm Cochrane, B2 thôi làm cổng |
| 1.2 Superiority test | ✅ một phần | Hợp lý khi giữ quy tắc cận dưới, vì endpoint mới đã có CI hẹp hơn |
| 1.3 Sát mép | ✅ | R6 là kiểm tra tốt; báo "cận dưới ≈ mốc" là cách trình bày đúng |
| 1.4 AND nhiều cổng | ⚠️ | Vẫn là AND 7 cổng; III-b thực chất là 6 điều kiện (xem 2.3) |
| 1.5 C2 / teacher | ✅ | R7 trả lời đúng câu hỏi; suy luận ghép đã được khai là suy luận |
| 1.6 C1 chỉ báo cáo | ✅ chấp nhận được | Lý do (KD là bằng chứng, không phải tiêu chí chọn) hợp lý, **miễn là** luận văn nêu rõ KD chưa có tác dụng trên PAD |
| 1.7 Mốc theo tông | ⚠️ | **Lý do yếu nhất** trong các mục tác giả quyết khác đề xuất (xem 2.2, 2.5) |
| 1.8 pAUC | ✅ | R8 khớp tới 2,8e-17 |
| 1.10 Post-hoc | ✅ | Danh sách các lần mở test là thực hành tốt |
| 1.12 Checkpoint lẫn nguồn | ✅ một phần | Fold ship vẫn là fold 4; chọn checkpoint trong fold theo val PAD (S9) nên làm khi train lại |
| §4 bước 3 (giữ ngưỡng 90%) | ⚠️ chấp nhận được | Quy tắc vẫn tính trên val; chỉ việc chọn mục tiêu 90% là post-hoc. Chấp nhận được **nếu** xác nhận trên U8 |

---

## 5. Đính chính hai điểm sai của R-ngoài (03/10)

- **§1.11:** giả định "timm `crop_pct` + center crop" **không đúng** với repo. Train dùng LANCZOS resize thẳng về
  224×224 (crosscheck §1.11). Checklist đối chiếu pipeline app vẫn còn giá trị, nhưng phải đối chiếu với phép resize này.
- **§1.9:** so cận dưới 0,74 (sens@spec80) với ≈ 0,83 (ngưỡng app) như thể CI hẹp lại nhờ đổi endpoint là **phóng đại**.
  Hai số ở **hai điểm vận hành khác nhau** (spec 0,80 so với 0,73), nên một phần chênh lệch đến từ việc hạ độ đặc hiệu.
  Nguyên lý "ngưỡng cố định thì CI không bị nới bởi việc ước lượng ngưỡng" vẫn đúng, nhưng mức chênh nêu trong R-ngoài
  không dùng được làm bằng chứng.

---

## 6. Những gì reviewer chưa kiểm được

- Con số Cochrane (47% / 81% / 76%): dựa trên brief bản 2 ghi là đã kiểm qua web; reviewer không tự đối chiếu.
- Nghiên cứu về trùng lặp / nhãn sai trong Fitzpatrick17k (Abhishek và cộng sự, 2024): theo hiểu biết của reviewer, cần kiểm.
- Cách gộp tông da Việt Nam vào nhóm "trung bình": giả định, cần đối chiếu với cách gộp trong repo.
- Mọi bảng cỡ mẫu: xấp xỉ binomial, chưa simulation.
- Khoảng cách III-b ≥ 0,1 (D4): suy từ hai điểm vận hành đã biết, chưa có điểm ROC tại spec 0,60.
