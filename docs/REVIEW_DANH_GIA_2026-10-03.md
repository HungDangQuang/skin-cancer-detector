# Review độc lập: hướng đi và phần đánh giá (03/10/2026)

> **Nguồn duy nhất của review này** là `PROJECT_BRIEF_FOR_REVIEW.md` (03/10/2026). Reviewer **không** đọc code, không
> chạy lại số nào. Mọi con số dưới đây hoặc lấy từ brief, hoặc là phép tính xấp xỉ của reviewer (ghi rõ "ước tính").
> Mỗi mục có phần **"Đối chiếu trong code"** để tác giả kiểm xem nhận xét có đúng với thực tế hay không.
>
> Ký hiệu: ✅ ổn · ⚠️ cần xem lại · ❌ nên sửa · 🔍 cần kiểm trong code trước khi kết luận

---

## 0. Tóm tắt

| # | Nhận xét chính | Mức |
|---|---|---|
| 1 | Mốc B2 (0,81) lấy từ bác sĩ đọc **dermoscopy, chỉ melanoma**, áp cho ảnh **điện thoại** có cả BCC/SCC. Mâu thuẫn với B3 (mốc nhìn bằng mắt) và với lý do gỡ B4 | ❌ |
| 2 | Quy tắc "cận dưới CI ≥ mốc" là **superiority test**. Với sens thật ≈ mốc thì không cỡ mẫu khả thi nào đạt | ❌ |
| 3 | B1 pAUC và B3 trượt mốc ở chữ số thứ 4 (0,0002 và 0,0001), nhỏ hơn cả nhiễu bootstrap và nhiễu train | ❌ |
| 4 | 8 cổng phải đạt cả 8 thì power chung rất thấp | ⚠️ |
| 5 | C2 đòi student **vượt** teacher, không liên quan đến câu hỏi trung tâm | ❌ |
| 6 | KD không giúp trên PAD (miền mục tiêu), nhưng C1 chỉ để báo cáo | ⚠️ |
| 7 | C4a đặt mốc tuyệt đối cho từng tông da trên nhóm nhỏ và nhãn nhiễu | ⚠️ |
| 8 | B1 so với một test khác (test cuộc thi) trong khi ISIC test chỉ có 76 ca dương | ⚠️ |
| 9 | Endpoint (sens@spec80) không phải thứ người dùng app nhận được (quyết định tại một ngưỡng cố định) | ⚠️ |
| 10 | Mốc chốt post-hoc, test dùng lại, ngưỡng app chọn sau khi xem test, chưa có tập xác nhận | ⚠️ |
| 11 | Parity pipeline camera của app (L3) chưa đo. Đây là nguồn lỗi thực tế phổ biến nhất | ⚠️ |
| 12 | Có thể có source-confounding trong việc chọn checkpoint (val AUPRC gộp) | 🔍 |

**Nhận định chung:** vấn đề chính nằm ở **thiết kế đánh giá**, không nằm ở model. Quy trình kỹ thuật (paired bootstrap,
tách theo nguồn, phát hiện leak, khai báo post-hoc) làm tốt.

---

## 1. Các vấn đề trong phần đánh giá: chi tiết và cách đối chiếu

### 1.1 ❌ Mốc B2 so sánh sai loại ảnh

**Nhận xét.**
- B2 (PAD, ảnh điện thoại) dùng mốc 0,81 = bác sĩ đọc **dermoscopy**, nhãn **chỉ melanoma**.
- B3 (Fitzpatrick, ảnh lâm sàng) dùng mốc 0,47 = **nhìn bằng mắt**.
- B4 bị gỡ với lý do "app nhận ảnh camera, không phải dermoscopy".

Logic dùng để gỡ B4 cũng chính là logic bác bỏ mốc của B2. Ảnh PAD là ảnh lâm sàng nên phải so với mốc cùng loại ảnh.
Ngoài ra nhãn dương PAD gồm MEL + BCC + SCC, còn nhãn âm có ACK (tiền ung thư) và SEK, nên càng không so được với nghiên
cứu chỉ có melanoma.

**Đối chiếu trong code / tài liệu.**
- [ ] `.claude/skills/eval-results/reference/acceptance-gates.md`: dòng B2 và B3 trích nguồn Cochrane nào (bảng nào,
      setting nào: in-person hay image-based, dermoscopy hay visual)?
- [ ] Mở chính bài Cochrane 2018 và kiểm: 0,81 và 0,47 có cùng một nghiên cứu, cùng điểm spec 80% không, và mỗi số ứng
      với setting nào. **Reviewer chưa kiểm được hai con số này.**
- [ ] Code ánh xạ nhãn PAD: chỉ `MEL`, `BCC`, `SCC` → 1; `ACK`, `SEK`, `NEV` → 0? (tìm nơi đọc `diagnostic` của PAD)

### 1.2 ❌ "Cận dưới CI ≥ mốc" là superiority test, không đủ power

**Nhận xét.** Quy tắc này yêu cầu **chứng minh vượt** mốc. Nếu sens thật ≈ 0,82 (gần mốc 0,81) thì cần cỡ mẫu không thể
có. Thêm nữa, mốc Cochrane cũng có CI riêng nhưng đang được coi là hằng số.

**Phân tích độ rộng CI (ước tính).**
- Brief: điểm 0,818, cận dưới 0,7406, khoảng cách ≈ 0,077.
- Sai số binomial thuần: 1,96·√(0,818·0,182/189) ≈ 0,055.
- ⇒ CI thực tế rộng hơn **≈ 1,4 lần**. Lý do: ngưỡng spec80 được **ước lượng lại trên chính tập test** từ chỉ 208 ảnh
  lành.

**Số ca ác tính cần để cận dưới *kỳ vọng* chạm 0,81** (hệ số nới 1,4; power ≈ 50%; giả định số ảnh lành tăng cùng
tỉ lệ; ước tính thô):

| Sens thật | Số ca ác tính cần | So với hiện có (189) |
|---|---|---|
| 0,82 | ~11.000 | ❌ |
| 0,83 | ~2.700 | ❌ (nhiều hơn toàn bộ PAD) |
| 0,85 | ~600 | ⚠️ |
| 0,87 | ~240 | ⚠️ |
| 0,89 | ~115 | ✅ |

Muốn power 80% thì các số trên tăng thêm khoảng 2 lần.

**Đối chiếu trong code.**
- [ ] Hàm tính sens@spec80: ngưỡng có được **tính lại trong mỗi bootstrap resample** không? Nếu có thì đó là nguồn của
      hệ số 1,4 (đúng về mặt phương pháp). Nếu không thì CI hiện tại đang **hẹp hơn** thực tế.
- [ ] Cách nội suy khi không có điểm đúng spec = 0,80: lấy điểm ROC gần nhất, nội suy tuyến tính, hay lấy ngưỡng có
      spec ≥ 0,80? Mỗi cách cho số khác nhau ở chữ số thứ 3.
- [ ] Bootstrap có **stratified theo lớp** không? Không stratified thì số ca dương thay đổi giữa các resample, khiến CI
      rộng hơn một chút.

### 1.3 ❌ Phán quyết nằm sát mép, phụ thuộc nhiễu

| Cổng | Cận dưới | Mốc | Chênh |
|---|---|---|---|
| B1 AUC | 0,9227 | 0,922 | +0,0007 (đạt) |
| B1 pAUC | 0,1418 | 0,142 | −0,0002 (trượt) |
| B3 | 0,4699 | 0,47 | −0,0001 (trượt) |

So với hai nguồn nhiễu:
- Monte Carlo error của bootstrap, phụ thuộc số resample.
- Nhiễu train: brief ghi chạy lại cùng seed lệch ≈ 0,005 AUPRC/fold.

⇒ Đổi bootstrap seed hoặc số resample **có thể lật phán quyết**.

**Đối chiếu trong code.**
- [ ] Số resample bootstrap (`n_boot`) và seed của bootstrap là bao nhiêu?
- [ ] **Thí nghiệm rẻ nên làm:** chạy lại CI của B1 và B3 với 5 bootstrap seed khác nhau và ghi lại cận dưới. Nếu phán
      quyết lật qua lại giữa các seed thì có bằng chứng trực tiếp rằng quy tắc hiện tại không ổn định.
- [ ] Percentile CI hay BCa? Hai cách khác nhau rõ nhất ở chỗ metric gần biên (pAUC, sens).

### 1.4 ⚠️ 8 cổng, phải đạt cả 8

Về α thì không sai (intersection-union test). Nhưng power chung xấp xỉ bằng **tích** power từng cổng. Nếu mỗi cổng có
power 0,6–0,8 thì power chung ≈ 2–17%, kể cả với một model thật sự tốt.

**Đối chiếu.**
- [ ] `acceptance-gates.md`: logic tổng hợp phán quyết là AND tất cả, hay có tầng chính/phụ?

### 1.5 ❌ C2 yêu cầu student vượt teacher

Câu hỏi trung tâm là có model tốt trên điện thoại, không phải student thắng teacher. Mục tiêu hợp lý: student
**không kém** teacher quá δ (non-inferiority) và tốt hơn baseline.

**Điểm đáng ngờ:** student vượt teacher **+0,062 AUPRC trên PAD** (CI [+0,040, +0,085]). Đây là chênh lệch lớn, gợi ý
teacher có thể **không được train cùng công thức** với student.

**Đối chiếu trong code.**
- [ ] Config của run teacher trong `experiments/runs_newsplit_ddi/`: có dùng **sampler phân tầng theo nguồn** không? Có
      DDI không? Augmentation `light`? Checkpoint chọn theo metric nào?
- [ ] Nếu teacher thiếu sampler theo nguồn: (a) C2 là so sánh không công bằng; (b) một teacher train đúng công thức
      có thể làm KD có tác dụng trên PAD.
- [ ] Logit của teacher dùng trong KD được tính trên **cùng view augmentation** với student hay trên ảnh gốc? Teacher ở
      `eval()` mode (dropout tắt)?

### 1.6 ⚠️ KD không giúp trên miền mục tiêu

- C1 PAD: ΔAUPRC −0,0008 [−0,0199, +0,0187], không phân định.
- C1 Fitz: +0,0395 [+0,0310, +0,0478].

Đây là phát hiện trung thực và cần nêu rõ trong luận văn, nhất là khi tên đề tài xoay quanh KD. Vì RQ3 hỏi trực tiếp về
KD nên C1 không nên chỉ để báo cáo phụ.

**Đối chiếu trong code (loss KD).** Brief ghi: `L = 0,3·Focal + 0,7·T²·BCE(σ(s/T), σ(t/T))`, T = 4.
- [ ] Hệ số `T²` có thật sự được nhân không?
- [ ] BCE với soft target có dùng `binary_cross_entropy_with_logits(s/T, sigmoid(t/T))` không (ổn định số học hơn so với
      BCE trên xác suất)?
- [ ] Teacher có `requires_grad=False` hoặc `torch.no_grad()` không?
- [ ] Baseline có **cùng** sampler, augmentation, số epoch, cách chọn checkpoint với bản KD không (để C1 là so sánh công
      bằng)?

### 1.7 ⚠️ C4a: mốc tuyệt đối cho từng tông da

- Nhóm tối n = 411 ảnh, số ca ác tính còn ít hơn; CI rộng ≈ 0,16.
- Nhãn tông da và nhãn ác tính của Fitzpatrick17k có nhiễu (gán bởi người gán nhãn, nhiều ca không có xác nhận bệnh học).
- Chênh sáng − trung bình xuất hiện **ở cả teacher** ⇒ do dữ liệu, không phải do nén.

Đề xuất: báo cáo disparity (C4b) kèm CI, không dùng mốc tuyệt đối làm cổng pass/fail.

**Đối chiếu.**
- [ ] Số ca **ác tính** trong từng nhóm tông da của biến thể headline là bao nhiêu? (CI của sens phụ thuộc số này, không
      phải 411)
- [ ] Nhóm tông da được gộp từ Fitzpatrick I–VI thế nào (I–II / III–IV / V–VI)? Ảnh có nhãn tông da "không rõ" được xử
      lý ra sao?

### 1.8 ⚠️ B1 so với test khác

Kurtansky 2025 đo trên **test của cuộc thi**, còn dự án đo trên phần ISIC của splits v2 với **76 ca ác tính**. Nên để B1
ở dạng tham chiếu, không làm cổng.

**Đối chiếu.**
- [ ] pAUC@TPR≥80% có được cài đặt **giống hệt** công thức chính thức của ISIC 2024 (thang [0; 0,2]) không? Kiểm bằng cách
      chạy hàm của dự án và hàm chính thức trên cùng một mảng dự đoán.

### 1.9 ⚠️ Endpoint không trùng với thứ người dùng nhận được

App trả quyết định nhị phân tại **một ngưỡng cố định**, còn sens@spec80 là một điểm ROC được tính lại trên test. Đề xuất
endpoint chính: **sens và spec tại ngưỡng app đã đóng băng** (xem mục 3). Với ngưỡng cố định, CI chỉ còn sai số
binomial nên hẹp hơn.

Minh hoạ bằng số hiện có (ngưỡng `pad_sens90`, fold 4; Wald CI thô do reviewer tính; **không dùng làm kết luận** vì
ngưỡng được chọn sau khi xem test):

| | Điểm | CI 95% thô |
|---|---|---|
| Sens (189 ác tính) | 0,873 | ≈ [0,83, 0,92] |
| Spec (208 lành) | 0,731 | ≈ [0,67, 0,79] |

So với sens@spec80: cận dưới 0,74 → khoảng 0,83 khi dùng ngưỡng cố định.

**Đối chiếu.**
- [ ] `reports/2026-10-02_threshold_options/README.md`: ngưỡng 0,5705 được tính trên **ảnh PAD của val fold 4**; tập
      val này tách bệnh nhân với test PAD?
- [ ] Ngưỡng trong app Kotlin có **đúng** bằng 0,5705 không, áp lên `sigmoid(logit)` hay lên logit? (0,5705 là xác suất
      thì logit tương ứng ≈ 0,284)

### 1.10 ⚠️ Post-hoc và dùng lại tập test

Brief đã khai báo đầy đủ: mọi mốc ghi nhận ngày 01/10 sau khi thấy kết quả, B4 chuyển sang chỉ báo cáo sau khi thấy nó
trượt, ngưỡng app chọn sau khi xem 3 điểm vận hành trên test PAD, vòng 2 tham khảo số v1.
⇒ **Hiện chưa có kết luận confirmatory nào.** Mọi số là exploratory.

**Đối chiếu.**
- [ ] Liệt kê mọi lần test PAD / HAM / Fitz đã được mở (theo ngày, theo ứng viên) để khai báo trong luận văn.

### 1.11 ⚠️ Parity pipeline camera (L3) chưa đo

A3 so sánh model trên **cùng một tensor đầu vào**, nên không phát hiện được sai khác ở bước tiền xử lý của app. Đây là
nguồn lỗi thực tế phổ biến nhất khi đưa model lên mobile.

**Đối chiếu trong code (Python vs Kotlin).**
- [ ] **Resize + crop:** transform eval của `timm` thường là resize cạnh ngắn theo `crop_pct` rồi center crop. App
      Kotlin có làm **giống hệt** không, hay resize thẳng về 224×224 (làm méo tỉ lệ)?
- [ ] **Interpolation:** Python (bicubic/bilinear, PIL hay torchvision) và Android (`Bitmap.createScaledBitmap` với
      `filter=true` là bilinear) có khớp không?
- [ ] **Normalize:** mean/std (ImageNet hay theo cấu hình riêng của từng backbone `timm`), thứ tự kênh RGB, chia 255
      trước hay sau.
- [ ] **EXIF orientation:** ảnh camera Android thường có cờ xoay; app có xoay ảnh theo EXIF trước khi xử lý không?
- [ ] **Định dạng màu:** decode JPEG có cùng color space không (sRGB), có premultiplied alpha không.
- [ ] **Thí nghiệm đề xuất:** chọn khoảng 200 ảnh PAD, chạy qua pipeline Kotlin thật và pipeline Python, so
      \|Δlogit\| và **tỉ lệ đổi quyết định** tại ngưỡng app.

### 1.12 🔍 Chọn checkpoint có thể bị source-confounding

Brief: "checkpoint chọn theo val AUPRC" (công thức hiện hành), nhưng luật chọn ứng viên vòng 2 dùng "AUPRC trên ảnh PAD
của val". Nếu checkpoint được chọn theo **AUPRC val gộp** thì metric đó bị lẫn khả năng phân biệt nguồn ảnh (PAD ≈ 48%
dương, ISIC ≈ 0,4% dương), giống vấn đề AUC gộp 0,872 brief đã nêu.

Dấu hiệu liên quan: ngưỡng Youden trên toàn val (0,2272) gắn cờ **207/208** ảnh lành PAD ⇒ thang điểm của model khác
nhau rất nhiều giữa các nguồn.

**Đối chiếu.**
- [ ] `best_model_auprc.pth` được chọn theo AUPRC val **gộp** hay **theo nguồn / chỉ PAD**?
- [ ] Nếu gộp: thử chọn lại theo AUPRC val PAD (hoặc trung bình theo nguồn) và xem số PAD có đổi không.

---

## 2. Hướng đi và tiến trình

| Mục | Đánh giá | Ghi chú |
|---|---|---|
| Phát hiện leak bệnh nhân (v1 → v2) | ✅ | Nên đưa vào luận văn như một bài học phương pháp |
| Tách số theo nguồn, AUPRC làm metric xếp hạng | ✅ | Phát hiện AUC gộp 0,872 nhờ đoán nguồn rất có giá trị |
| Paired bootstrap trên hàng test | ✅ | Đúng cách |
| Sampler phân tầng theo nguồn | ✅ | Đòn bẩy duy nhất đã chứng minh trên PAD (+0,056) |
| Gỡ domain augmentation | ✅ | Quyết định dựa trên bằng chứng |
| Thêm DDI | ⚠️ | Có ích ở nhiều tập, nhưng trên PAD thì không phân định; chỉ thử một cặp |
| Vòng chọn 2 (P1/P2) | ⚠️ | Không đụng tới nút thắt B2 (prereg tự ghi nhận). Chênh lệch giữa ứng viên có thể nhỏ hơn nhiễu train ~0,005. Nên chạy cho xong vì đã đăng ký trước, nhưng giới hạn thời gian |
| Khung RQ1–RQ5 | ⚠️ | Thiếu bước đầu tiên: **định nghĩa "tốt"** (endpoint + mốc). RQ4 phần dermoscopy ít liên quan đến app camera. RQ5 có giá trị thực tiễn cao |

---

## 3. Khung đánh giá đề xuất cho luận văn ứng dụng

"Hoạt động tốt trên mobile" = **3 trụ**, đo riêng, quyết định riêng.

### Trụ I: Chạy được (đo kỹ thuật, pass/fail trực tiếp)

| Chỉ số | Cách đo đúng | Mốc đề xuất |
|---|---|---|
| Latency p50/**p95** model | `.pte` **ship**, warm-up, sau 5 phút chạy liên tục | p95 ≤ 80 ms |
| Latency **end-to-end** | decode + xoay EXIF + resize + normalize + inference | p95 ≤ ~300 ms (lựa chọn thiết kế UX, cần ghi rõ) |
| Cold start | Mở app → kết quả đầu tiên | Báo cáo |
| Peak memory | Trên app thật, không đo theo kiến trúc | Báo cáo + ngưỡng cho máy 3–4 GB RAM |
| Thiết bị | **≥ 2 máy**, trong đó có 1 máy cấp thấp | Mốc phải đạt trên máy yếu nhất |

### Trụ II: Giữ nguyên chất lượng

| Chỉ số | Mốc | Trạng thái |
|---|---|---|
| A3 parity model | max\|Δlogit\| < 1e-3 | ✅ đã có (5,2e-06) |
| A4 tất định, không lỗi | lỗi < 0,1%, trùng bit | ✅ đã có |
| **L3 parity pipeline app** | tỉ lệ đổi quyết định < 0,5% | ❌ chưa đo (xem 1.11) |

### Trụ III: Đúng với người dùng (thống kê)

**Endpoint chính (co-primary):** sens **và** spec **tại ngưỡng app đã đóng băng**, trên ảnh điện thoại có nhãn bệnh học.

**Quy tắc:** cận dưới CI 95% của sens ≥ S_min **và** cận dưới CI 95% của spec ≥ Sp_min. Hai mốc **chốt và ghi lại trước**
khi chạy tập xác nhận.

**Nguồn mốc:**

| Nguồn | Vai trò đề xuất | Ghi chú |
|---|---|---|
| (b) Yêu cầu use case sàng lọc (ví dụ "không bỏ sót quá 1/5" ⇒ sens ≥ 0,80; "báo nhầm chấp nhận được" ⇒ spec ≥ 0,50) | **Mốc chính** | Cần lập luận rõ hoặc có ý kiến GVHD / bác sĩ da liễu. Các số ví dụ là minh hoạ, **chưa phải đề xuất cuối** |
| (a) Hiệu năng bác sĩ trên **cùng loại ảnh** (lâm sàng/điện thoại) | Tham chiếu | Reviewer **chưa có nguồn đã kiểm**, cần tra cứu |
| (c) Student không kém teacher quá δ | Cổng phụ | Trả lời "nén có làm hỏng không" |

**Báo cáo kèm (không pass/fail):**
- PPV/NPV ở prevalence giả định 1–5%. PAD có ≈ 48% dương nên PPV đo trực tiếp sẽ ảo.
- Sens/spec theo loại ung thư (BCC / SCC / MEL; MEL rất ít nên CI rộng).
- Theo tông da (disparity + CI).
- Độ bền chất lượng ảnh: mờ, thiếu sáng, khoảng cách.
- Tham chiếu: B1, B3, B4, C1, C2 (dạng non-inferiority).

### Tập xác nhận

Test PAD đã bị nhìn nhiều lần và ngưỡng app được chọn sau khi xem nó ⇒ cần **tập chưa từng bị chạm** cho kết luận
confirmatory.

| Phương án | Khả thi | Ghi chú |
|---|---|---|
| Tập ngoài có ảnh lâm sàng/điện thoại + nhãn bệnh học (ví dụ Derm7pt phần clinical, MIDAS) | ⚠️ | Kiểm license, định nghĩa nhãn, tỉ lệ ảnh chụp bằng điện thoại, trùng lặp với train. Reviewer chưa kiểm các tập này |
| Tự thu ảnh qua app tại phòng khám | ⚠️ | Sát ứng dụng nhất, tốn thời gian, cần thủ tục đạo đức |
| Out-of-fold trên toàn bộ PAD | ⚠️ | Thu hẹp CI (PAD có khoảng ~1.000 ảnh ác tính theo hiểu biết của reviewer, **cần kiểm**), nhưng ước lượng hiệu năng của *quy trình train*, không phải của một checkpoint ship; có optimism nhẹ do val PAD dùng để chọn checkpoint |
| Không có tập mới | ❌ cho confirmatory | Báo cáo được, nhưng ghi rõ "exploratory, có optimism" |

**Cỡ mẫu tập xác nhận cho sens tại ngưỡng cố định** (binomial Wald, ước tính thô):

| Sens thật kỳ vọng | S_min | Số ca ác tính, power ≈ 50% | Số ca ác tính, power ≈ 80% |
|---|---|---|---|
| 0,87 | 0,80 | ~90 | ~180 |
| 0,87 | 0,82 | ~175 | ~355 |
| 0,85 | 0,80 | ~200 | ~400 |

Lưu ý: bảng trong câu trả lời chat trước đó tương ứng power ≈ 50%. Nên chạy simulation để có số chính xác. Spec tính
tương tự theo số ca lành.

---

## 4. Thứ tự việc đề xuất

1. **Quyết định** S_min, Sp_min kèm lập luận use case (có GVHD). Ghi vào `acceptance-gates.md` với ngày.
2. Kiểm các mục 🔍 / checklist ở phần 1, ưu tiên: 1.12 (chọn checkpoint), 1.5 (công thức teacher), 1.11 (pipeline app),
   1.3 (độ nhạy của phán quyết với bootstrap seed).
3. Đóng băng model (P0 hoặc ứng viên vòng 2) và ngưỡng, **chọn lại ngưỡng trên val**, không dùng test.
4. Đo trụ I trên `.pte` ship, 2 máy, end-to-end.
5. Đo L3.
6. Tìm hoặc thu tập xác nhận; tính cỡ mẫu **trước** khi dùng.
7. Chạy xác nhận **một lần duy nhất**, báo cáo theo khung ở mục 3.

---

## 5. Những gì reviewer chưa kiểm được

- Con số Cochrane 2018 (0,81 / 0,47) và Kurtansky 2025 (0,922 / 0,142): chỉ dựa trên mô tả của brief. Nếu mô tả sai
  setting thì mục 1.1 cần xem lại.
- Toàn bộ các bảng cỡ mẫu: xấp xỉ binomial, hệ số nới 1,4 suy từ một điểm dữ liệu.
- Số ảnh ác tính của PAD-UFES-20 và các tập ngoài đề xuất: theo hiểu biết của reviewer, cần kiểm từ nguồn gốc.
- Mọi nhận xét về code (mục "Đối chiếu"): là **giả thuyết cần kiểm**, không phải khẳng định rằng code đang sai.
