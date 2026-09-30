# KỊCH BẢN THUYẾT TRÌNH — BẢO VỆ LUẬN VĂN THẠC SĨ

> **Cách dùng:** Mỗi mục tương ứng 1 slide trong [SLIDE_CONTENT.md](SLIDE_CONTENT.md) (bố cục **33 slide**, cập nhật **2026-09-19**, phản ánh luận văn đã **hoàn tất** — 140/140 fold-run). Phần **[LỜI NÓI]** là kịch bản để nói theo (văn nói tự nhiên, KHÔNG đọc nguyên văn bullet trên slide). **[CHUYỂN TIẾP]** là câu nối sang slide sau. **⏱** là thời lượng gợi ý.
>
> **Tổng thời lượng của kịch bản đầy đủ (cộng dồn mọi ⏱): ~32 phút.** Đây là kịch bản nói hết mọi chi tiết; hội đồng luận văn thường cho 20–30 phút trình bày, nên hãy tự lượng: nếu chỉ có 20–22 phút, cắt slide 12/14 (dữ liệu bổ trợ/văn liệu) xuống còn 1–2 câu, gộp slide 24–25 (hai ablation) thành một câu tóm tắt, và rút slide 30–32 xuống mức nêu kết luận không đọc lại số. Nếu có 25–28 phút, giữ nguyên như đã viết và chỉ nói nhanh hơn ở PHẦN 1, 3, 4. **Không cắt PHẦN 5 (slide 19–29)** — đây là chương kết quả, trọng tâm của buổi bảo vệ.
>
> **Mẹo trình bày:**
> - Đừng đọc bullet — bullet để hội đồng đọc, bạn *kể* nội dung.
> - Xương sống để hội đồng nhớ: **3 vấn đề → nút thắt → KD (không phải "dark knowledge") → 6 câu hỏi nghiên cứu → 140/140 lượt huấn luyện → kết quả 3 tầng → triển khai thật → trả lời đủ 6 câu hỏi.**
> - **Điểm nhấn lớn nhất của buổi này là PHẦN 5 (slide 19–29): toàn bộ ma trận đã XONG**, không còn phần nào "đang chạy" hay "chưa trả lời được" như bản đề cương cũ.
> - **Nguyên tắc vàng khi đọc số: TRUNG THỰC — nói trước khi bị hỏi.** Bốn chỗ phải chủ động nói ra: (1) ở **AUPRC** teacher vẫn hơn student, KD chỉ vượt ở **pAUC**; (2) bằng chứng thống kê **chắc nhất nằm ở HAM10000** (11/12 CI loại trừ 0), còn in-domain chỉ 5/12 — vì cỡ mẫu 241 ca dương chứ không phải KD yếu; (3) **không có "teacher tốt nhất" độc lập với miền** — teacher tốt nhất trên HAM10000 lại tệ nhất trên Fitzpatrick17k; (4) mô hình **suy giảm nặng ngoài miền huấn luyện** — đây là hạn chế lớn nhất, không phải điểm yếu để giấu.

---

## Slide 1 — Trang bìa ⏱ 30s

**[LỜI NÓI]**
Kính thưa quý thầy cô trong hội đồng. Em xin tự giới thiệu, em là Đặng Quang Hưng, học viên cao học khóa 18. Hôm nay em xin trình bày luận văn với đề tài *"Phát hiện ung thư da trên thiết bị biên sử dụng mô hình học sâu kết hợp chưng cất tri thức"*, dưới sự hướng dẫn của thầy TS. Nguyễn Thanh Bình.

**[CHUYỂN TIẾP]** Sau đây em xin đi vào nội dung trình bày.

---

## Slide 2 — Nội dung trình bày (Agenda) ⏱ 25s

**[LỜI NÓI]**
Bài trình bày của em gồm bảy phần. Đầu tiên là vấn đề và động lực nghiên cứu. Tiếp đến là chưng cất tri thức, khoảng trống nghiên cứu và câu hỏi nghiên cứu. Phần ba là dữ liệu — bốn bộ dữ liệu và ba thách thức. Phần bốn là nghiên cứu liên quan và phương pháp đề xuất. Phần năm — em xin nhấn mạnh — là **kết quả thực nghiệm**, với toàn bộ 140 lượt huấn luyện đã hoàn tất. Phần sáu là triển khai trên thiết bị thật và lựa chọn mô hình. Cuối cùng là trả lời câu hỏi nghiên cứu, hạn chế và hướng phát triển.

**[CHUYỂN TIẾP]** Trước hết, em xin bắt đầu với vấn đề gốc của bài toán.

---

# PHẦN 1 — VẤN ĐỀ & ĐỘNG LỰC

## Slide 3 — Vấn đề 1: Nghịch lý melanoma ⏱ 50s

**[LỜI NÓI]**
Vấn đề gốc của đề tài xuất phát từ một nghịch lý. Theo GLOBOCAN 2022, mỗi năm có khoảng 331 nghìn ca mắc mới ung thư hắc tố — melanoma — và gần 59 nghìn ca tử vong.

Điều đáng chú ý là: melanoma chỉ chiếm khoảng 10% tổng số ca ung thư da, nhưng lại gây ra tới 80% số ca tử vong. Tức đây là loại nguy hiểm nhất.

Nhưng có một tin tốt: nếu phát hiện ở giai đoạn khu trú, tỷ lệ sống sau 5 năm lên tới 99%. Nói cách khác, phần lớn tử vong do melanoma không đến từ thiếu phương pháp điều trị, mà đến từ phát hiện muộn. Cơ hội sống gần như phụ thuộc hoàn toàn vào việc phát hiện có kịp thời hay không.

**[CHUYỂN TIẾP]** Vậy hiện nay việc phát hiện sớm đang gặp trở ngại gì?

---

## Slide 4 — Vấn đề 2: Thiếu bác sĩ, mà AI mạnh lại kẹt trên cloud ⏱ 65s

**[LỜI NÓI]**
Vấn đề thứ hai là khoảng trống tiếp cận. Chẩn đoán truyền thống dựa vào kinh nghiệm bác sĩ da liễu qua soi da và quy tắc ABCD, nhưng ở nhiều khu vực thiếu chuyên gia và chi phí thăm khám cao, nên người dân khó tiếp cận.

Học sâu, đặc biệt là CNN, đã chứng minh đạt độ chính xác ngang 21 bác sĩ da liễu có chứng chỉ — công trình kinh điển của Esteva năm 2017 trên Nature. Các kiến trúc như EfficientNet, Vision Transformer liên tục cải thiện.

Tuy nhiên có một rào cản: mô hình thắng cuộc ISIC 2020 là một ensemble tới 18 mô hình — quá lớn để chạy trên điện thoại, nên phải chạy trên đám mây. Điều này kéo theo ba vấn đề: độ trễ và phụ thuộc kết nối, rủi ro riêng tư dữ liệu y tế, và chi phí vận hành theo lượt dùng.

Vì vậy hướng đi là đưa AI xuống thẳng thiết bị — Edge AI — với một điều kiện em tự đặt ra ngay từ đầu: phải đo trên chính thiết bị đích, không chỉ đạt điểm cao trên máy chủ.

**[CHUYỂN TIẾP]** Nhưng đưa AI xuống thiết bị lại chạm ngay vào một nút thắt.

---

## Slide 5 — Vấn đề 3: Nút thắt cốt lõi — nhỏ thì kém chính xác ⏱ 55s

**[LỜI NÓI]**
Nút thắt cốt lõi là sự đánh đổi giữa độ chính xác và kích thước, tốc độ. Các mô hình gọn như EfficientNet-B0, MobileNetV3 hay MobileViT chạy được trên điện thoại, nhưng thường phải chấp nhận suy giảm độ chính xác.

Trong y tế đây là điều rất nhạy cảm: bỏ sót một ca ác tính có thể dẫn tới tử vong, trong khi một dương tính giả chỉ dẫn tới một lần khám xác nhận — hậu quả hoàn toàn bất đối xứng. Đây cũng là lý do ISIC 2024 chọn pAUC ở độ nhạy từ 80% trở lên làm thước đo chính thức — chỉ thưởng cho vùng độ nhạy cao.

Câu hỏi nút thắt: làm sao mô hình vừa đủ nhỏ để chạy trên điện thoại, vừa không bỏ sót ca ác tính? Hướng luận văn chọn để trả lời là chưng cất tri thức.

**[CHUYỂN TIẾP]** Vậy chưng cất tri thức thực sự hoạt động thế nào, và vì sao nó phù hợp bài toán này?

---

# PHẦN 2 — CHƯNG CẤT TRI THỨC & CÂU HỎI NGHIÊN CỨU

## Slide 6 — Chưng cất tri thức là gì, và nó thực sự làm gì ⏱ 65s

*(Slide dùng hình sẵn `figures/kd_flow_slide.png` — chỉ vào hình khi nói)*

**[LỜI NÓI]**
Chưng cất tri thức — Knowledge Distillation — do Hinton đề xuất năm 2015: dùng một mô hình teacher lớn, chính xác cao, để dạy một mô hình student nhỏ gọn qua nhãn mềm thay vì chỉ nhãn cứng 0 hoặc 1.

Ở đây em xin nêu một điểm luận văn làm rõ lại. Văn liệu thường quy tác dụng của nhãn mềm cho "dark knowledge" — thông tin ở phân phối tương đối giữa các lớp sai. Nhưng ở bài toán nhị phân một logit của em, khái niệm đó **không tồn tại theo đúng nghĩa** — nhãn mềm chỉ là một số vô hướng, không có "lớp sai" nào để xếp hạng.

Cơ chế thật sự, theo phân tích của em, là **làm mượt nhãn thích ứng theo từng mẫu**: teacher thay nhãn cứng bằng mục tiêu mềm phản ánh đúng độ khó của mẫu đó — và dự đoán rút ra từ cơ chế này đã được kiểm chứng bằng số liệu ở Chương 4, em sẽ trình bày ở slide 21.

**[CHUYỂN TIẾP]** Nhưng dù cơ chế hứa hẹn, khi nhìn vào văn liệu hiện có, em thấy vẫn còn bốn khoảng trống.

---

## Slide 7 — Khoảng trống nghiên cứu ⏱ 55s

**[LỜI NÓI]**
Thứ nhất, hầu như không có nghiên cứu nào so sánh chính student ở hai trạng thái có và không chưng cất — phần lớn chỉ báo accuracy tuyệt đối sau KD, nên không tách được phần nào do KD mang lại.

Thứ hai, khi có nhiều teacher, các công trình hoặc gộp lại thành một nguồn tri thức duy nhất, hoặc chỉ xếp hạng theo điểm tuyệt đối cùng một miền — nên cả hai câu hỏi "teacher mạnh hơn có dạy tốt hơn không" và "thứ tự teacher có đổi khi đổi miền không" đều bỏ ngỏ.

Thứ ba, bộ ISIC 2024 — gần với ảnh smartphone nhất — chưa được khai thác trong bối cảnh KD.

Thứ tư, rất ít công trình hỏi: sau chưng cất, student có thực sự chạy tốt hơn trên điện thoại thật không, và số đo có thuộc đúng mô hình đã đánh giá không.

**[CHUYỂN TIẾP]** Từ bốn khoảng trống này, em hình thành câu hỏi nghiên cứu trung tâm.

---

## Slide 8 — Câu hỏi nghiên cứu trung tâm ⏱ 60s

**[LỜI NÓI]**
Câu hỏi trung tâm: liệu chưng cất tri thức có thực sự mang lại cải thiện đáng kể và nhất quán cho các mô hình gọn nhẹ thuộc nhiều paradigm khác nhau, và chất lượng teacher ảnh hưởng thế nào đến hiệu quả KD?

Em phân rã thành sáu câu hỏi kiểm chứng được: Q1 trộn PAD có tốt hơn không, Q2 teacher mạnh hơn có tạo student tốt hơn không, Q3 KD có nhất quán qua các paradigm không, Q4 student có vượt teacher không, Q5 nên triển khai mô hình nào, và Q6 tỉ lệ undersampling 1:5 có đúng không.

Để trả lời khách quan, em thiết kế thực nghiệm đối chứng ceteris paribus: mỗi student chạy hai nhánh — có KD và không — mọi thứ khác giữ nguyên. Cả sáu câu hỏi này đều đã được trả lời đầy đủ ở Chương 4 và 5 — em sẽ tổng hợp lại ở slide 30.

**[CHUYỂN TIẾP]** Trước khi vào kết quả, em xin nói rõ phạm vi và những đóng góp cụ thể của luận văn.

---

## Slide 9 — Phạm vi & đóng góp của luận văn ⏱ 60s

**[LỜI NÓI]**
Về phạm vi, luận văn có bốn quyết định có chủ đích: chỉ phân loại nhị phân một logit — vì bốn bộ dữ liệu chỉ có hệ nhãn chung ở mức đó; chỉ chưng cất theo logit, không theo đặc trưng hay quan hệ — để không cần lớp chiếu số chiều và không đụng đồ thị student khi export; đánh giá hồi cứu, không thẩm định lâm sàng tiến cứu; và export FP32, không lượng tử hóa INT8.

Về đóng góp, có bốn, quan hệ nhân quả với nhau. Đóng góp công cụ là ma trận 12 cặp trên 3 tầng đánh giá độc lập, kết luận bằng khoảng tin cậy bootstrap ghép cặp. Từ đó là hai đóng góp khoa học: cơ chế KD ở bài toán một logit đã kiểm chứng định lượng; và hai câu trả lời tưởng hiển nhiên hóa ra sai — không có "teacher tốt nhất" độc lập với miền, và bất bình đẳng tông da nằm ở nhóm trung bình chứ không phải nhóm tối. Đóng góp thứ tư thuộc kỹ thuật: pipeline tái lập được, cổng kiểm tra tương đương đã chứng minh cần thiết, và phép đo trên thiết bị có kiểm soát nhiệt.

Em xin nói rõ: luận văn không đề xuất toán tử, kiến trúc hay hàm mất mát mới — giá trị nằm ở quy mô có kiểm soát và độ nghiêm ngặt của đánh giá.

**[CHUYỂN TIẾP]** Để hiện thực hóa các đóng góp đó, trước hết em xin trình bày về dữ liệu.

---

# PHẦN 3 — DỮ LIỆU & THÁCH THỨC

## Slide 10 — Bài toán & bốn bộ dữ liệu ⏱ 55s

**[LỜI NÓI]**
Bài toán đặt trong khung phân loại nhị phân: ảnh tổn thương da 224×224 vào, một logit ra, áp sigmoid thành xác suất ác tính. Nhãn theo quy ước lâm sàng: melanoma, ung thư biểu mô tế bào đáy và tế bào vảy là ác tính; nốt ruồi, dày sừng lành tính, u xơ da và tổn thương mạch máu là lành tính.

Luận văn dùng bốn bộ dữ liệu vai trò tách bạch: ISIC 2024 hơn 401 nghìn ảnh non-dermoscopic là huấn luyện chính; PAD-UFES-20 bổ sung ca ác tính và miền lâm sàng; HAM10000 và Fitzpatrick17k chỉ dùng đánh giá — kiểm chứng chéo miền và phân tích công bằng.

Em xin nhấn mạnh: hai bộ HAM10000 và Fitzpatrick17k tuyệt đối không dùng để train, validate, hay chọn ngưỡng — thực thi bằng mã, dừng chương trình nếu phát hiện trùng lặp.

**[CHUYỂN TIẾP]** Trong bốn bộ này, ISIC 2024 là bộ trung tâm — em xin phân tích kỹ vì sao nó "đúng" cho đề tài.

---

## Slide 11 — ISIC 2024: vì sao là dữ liệu huấn luyện chính ⏱ 60s

**[LỜI NÓI]**
ISIC 2024 SLICE-3D có hơn 401 nghìn ảnh, cắt tự động từ ảnh chụp toàn thân 3D — không nguồn sáng phân cực, không tiếp xúc da — nên gần với ảnh chụp smartphone hơn hẳn các bộ dermoscopic.

Mỗi ảnh có 53 cột metadata, em cố ý chỉ giữ 3 cột — định danh ảnh, nhãn, mã bệnh nhân. 39 cột mô tả hình học do thiết bị 3D tính ra bị loại vì không lấy được trên điện thoại; 8 cột chẩn đoán sau sinh thiết bị cấm tuyệt đối vì rò rỉ nhãn — riêng việc một ô có giá trị hay rỗng đã gần như lộ nhãn.

Bộ này hội đủ ba điều kiện: ảnh gần smartphone, đủ lớn để 5-fold cross-validation còn ý nghĩa, và mất cân bằng thực tế đi kèm metric an toàn lâm sàng pAUC ở TPR từ 80%.

**[CHUYỂN TIẾP]** Bên cạnh ISIC, ba bộ còn lại đóng vai trò bổ trợ.

---

## Slide 12 — Ba bộ dữ liệu bổ trợ ⏱ 50s

**[LỜI NÓI]**
PAD-UFES-20 gồm 2.298 ảnh chụp smartphone lâm sàng thật. Vai trò của nó là nâng prevalence từ khoảng 0,1% lên 0,3885%, và mang vào đúng loại biến thiên ứng dụng sẽ gặp — ánh sáng phòng khám, góc chụp tùy tay.

HAM10000 là ảnh soi da, miền ngược hẳn dữ liệu huấn luyện — biến thể chính giữ một ảnh mỗi tổn thương, 7.470 ảnh, 1.169 ca ác tính.

Fitzpatrick17k là bộ da liễu công khai lớn duy nhất có chú thích tông da, ảnh lâm sàng trường rộng — 4.320 ảnh, 2.160 ca ác tính, chia ba nhóm sáng, trung bình, tối. Em xin nói thêm: bộ gốc chỉ cung cấp URL, 76% đã chết — em khôi phục qua một mirror xác minh bằng mã băm nội dung, đạt độ phủ 99,98%.

**[CHUYỂN TIẾP]** Bốn bộ dữ liệu này đặt ra ba thách thức đặc trưng mà luận văn phải xử lý.

---

## Slide 13 — Ba thách thức & cách xử lý ⏱ 60s

**[LỜI NÓI]**
Thách thức thứ nhất là mất cân bằng lớp cực đoan — prevalence chỉ 0,3885%, khiến accuracy vô nghĩa và AUC-ROC lạc quan giả. Em chọn AUPRC làm chỉ số chính, pAUC ở TPR từ 80% là chỉ số ISIC 2024, kết hợp undersampling 1:5 mỗi epoch cùng Focal Loss.

Thách thức thứ hai là rò rỉ dữ liệu. Em tách held-out test khoảng 17% patient-disjoint trước, rồi mới chia 5 fold. Đây không phải lý thuyết suông — chính dự án từng mắc lỗi lấy validation của fold 0 làm test, khiến bốn fold còn lại train trên chính dữ liệu test của chúng. Lỗi này em đã phát hiện và sửa.

Thách thức thứ ba là ràng buộc triển khai biên: phải đo trên thiết bị thật, vì nền tảng thực thi có thể nới khoảng cách hai kiến trúc tới 181 lần, và điều tiết nhiệt làm chậm thêm 45 đến 49% sau 5 phút — cả hai hiệu ứng đều không nằm trong FLOPs.

**[CHUYỂN TIẾP]** Trước khi trình bày giải pháp, em xin điểm qua các nghiên cứu liên quan để thấy đề tài đứng ở đâu.

---

# PHẦN 4 — NGHIÊN CỨU LIÊN QUAN & PHƯƠNG PHÁP ĐỀ XUẤT

## Slide 14 — Bối cảnh văn liệu: 10 năm chưa hội tụ ⏱ 65s

**[LỜI NÓI]**
Em xin tóm tắt lĩnh vực theo dòng thời gian mười năm. 2015–2019 đặt nền móng: Esteva 2017 chứng minh CNN ngang bác sĩ; Hinton đề xuất KD; EfficientNet và MobileNetV3 ra đời. 2020–2021, mô hình lớn thống trị — ensemble 18 mô hình thắng ISIC 2020, rồi Vision Transformer — chính xác hơn nhưng nặng hơn. 2022–2023, cộng đồng tìm kiến trúc cân bằng — MobileViT, HI-MViT đạt F1 0,931, AUC 0,977 trên ISIC 2018.

2024–2025, ISIC 2024 SLICE-3D ra đời và KD bắt đầu ứng dụng vào da liễu — nhưng em xin nhấn một điểm quan trọng: hầu như tất cả các công trình đó đều **không có nhánh đối chứng**, chỉ báo accuracy tuyệt đối sau chưng cất — Islam 2024 báo 98,75% trên HAM10000, Saha 2025 báo 88,6 đến 88,9%, Winata 2025 báo 87,53% trên ISIC 2019 nhưng so với framework khác chứ không so với chính student của họ. Chỉ duy nhất Pavel 2025 có một baseline để so sánh.

Điểm chốt: hai hướng "mô hình lớn chính xác" và "mô hình nhỏ triển khai được" chưa bao giờ thực sự hội tụ — đó là chỗ đứng của đề tài.

**[CHUYỂN TIẾP]** Từ đó, luận văn xây dựng một khung teacher–student đa kiến trúc.

---

## Slide 15 — Khung thực nghiệm: 3 teacher × 4 student, 4 paradigm ⏱ 65s

**[LỜI NÓI]**
Ý tưởng cốt lõi: thay vì chỉ một cặp teacher–student, em huấn luyện một dải ba teacher chất lượng khác nhau, ghép với một dải bốn student trải bốn paradigm — ghép đầy đủ, không chọn lọc cặp "hứa hẹn", để tỉ lệ thắng đo đúng phương pháp chứ không đo lựa chọn của người làm thí nghiệm.

Ba teacher: MaxViT-Base gần 119 triệu tham số — lai CNN với Transformer; ConvNeXtV2-Base gần 88 triệu; EfficientNetV2-M gần 53 triệu. Bốn student: EfficientFormerV2-S2 là hybrid attention–CNN; FastViT-SA12 dùng tái tham số hóa; MobileNetV4-Conv-Medium là CNN depthwise-separable; RepViT-M1.0 mang thiết kế Vision Transformer, nhẹ nhất, hơn 6 triệu tham số.

Bảy mô hình dùng chung một chuẩn đầu ra — pooling, dropout, một tầng tuyến tính ra đúng một logit — và teacher luôn đóng băng hoàn toàn khi distill. Ba nhân bốn cho ra 12 cặp chưng cất.

**[CHUYỂN TIẾP]** Vậy việc chưng cất được thực hiện qua hàm mất mát như thế nào?

---

## Slide 16 — Hàm mất mát chưng cất ⏱ 55s

**[LỜI NÓI]**
Hàm mất mát gồm hai thành phần, theo nguyên lý Hinton nhưng điều chỉnh cho mất cân bằng. L_hard là tín hiệu nhãn cứng — em dùng Focal Loss, gamma 2 và alpha 0,25, thay vì cross-entropy thường. L_soft truyền mục tiêu mềm từ teacher, tính bằng BCE với nhiệt độ T bằng 4. Hai thành phần cân bằng bởi hệ số alpha 0,3 — 30% nhãn cứng, 70% nhãn mềm.

Một điểm quan trọng: nhánh baseline loại bỏ hẳn teacher khỏi quy trình, không chỉ đặt trọng số soft về 0 — vì teacher hiện diện vẫn chiếm tài nguyên, phá vỡ nguyên tắc ceteris paribus. Và em chọn chưng cất theo logit, không theo đặc trưng hay quan hệ, vì không cần lớp chiếu số chiều khi ghép các teacher/student khác chiều đặc trưng, và không đụng đồ thị tính toán của student khi export.

**[CHUYỂN TIẾP]** Và đây chính là nền tảng cho thiết kế đối chứng của toàn bộ thực nghiệm.

---

## Slide 17 — Thiết kế đối chứng & quy mô thực nghiệm đã hoàn tất ⏱ 65s

**[LỜI NÓI]**
Đơn vị so sánh là một cặp: lượt KD ghép theo từng fold với lượt đối chứng của đúng student đó — không ghép hai giá trị trung bình — để chênh lệch quy được về đúng một nguyên nhân.

Về quy mô: tập test giữ lại 62.040 ảnh dùng chung mọi fold mọi run; pool huấn luyện mỗi fold 248.161 ảnh; thực dùng mỗi epoch chỉ 5.790 ảnh sau lấy mẫu.

Em xin báo cáo: **140 trên 140 lượt huấn luyện fold-run đã hoàn tất** — 15 teacher, 15 teacher ablation loại PAD, 20 student baseline, 60 KD, và 30 cho hai ablation dữ liệu.

Về kiểm định thống kê, em xin nói rõ một thay đổi so với đề cương: em dùng khoảng tin cậy bootstrap ghép cặp, hai nghìn lần lặp, thay cho paired t-test dự kiến trước đây — vì 5 fold không phải 5 mẫu độc lập, mà là 5 mô hình khác nhau chấm trên cùng một tập, nên độ lệch chuẩn giữa các fold đo mức bất đồng giữa các mô hình chứ không đo sai số lấy mẫu mà kiểm định t giả định; với n bằng 5, lực thống kê cũng gần như không còn.

**[CHUYỂN TIẾP]** Tiếp theo em xin trình bày cách đánh giá được tổ chức thành ba tầng độc lập.

---

## Slide 18 — Ba tầng đánh giá độc lập & các độ đo ⏱ 55s

**[LỜI NÓI]**
Tầng một là in-domain, ISIC 2024 cộng PAD, 62.040 ảnh, prevalence 0,3885% — thuận lợi nhất nhưng cùng nguồn ảnh với train. Tầng hai là cross-domain trên HAM10000, 7.470 ảnh, prevalence 15,6% — miền ảnh ngược hẳn. Tầng ba là fairness trên Fitzpatrick17k, 4.320 ảnh, prevalence 50% — ở đây em hỏi "mô hình tốt không đều ở đâu" theo nhóm tông da, chứ không hỏi "tốt đến đâu".

Lưu ý quan trọng: ba tỉ lệ ca ác tính chênh nhau hơn hai bậc độ lớn, nên AUPRC không so được giữa ba tầng — đường cơ sở ngẫu nhiên của nó chính bằng prevalence. Bộ độ đo mỗi lượt chạy gồm AUPRC chính, pAUC ISIC 2024, AUC-ROC tham khảo, độ nhạy/đặc hiệu/F1 theo Youden's J, và độ nhạy tại đặc hiệu cố định 90–95% cho vận hành thực tế.

**[CHUYỂN TIẾP]** Với thiết kế đó, em xin trình bày kết quả thực nghiệm — phần trọng tâm của luận văn.

---

# PHẦN 5 — KẾT QUẢ THỰC NGHIỆM

## Slide 19 — Hiệu năng in-domain: teacher vs. student ⏱ 70s

**[LỜI NÓI]**
Nhìn bảng teacher: MaxViT-Base đạt AUPRC 0,6566, ConvNeXtV2-Base 0,6506, EfficientNetV2-M 0,6298 — hai teacher đầu chênh nhau trong phạm vi một độ lệch chuẩn, nên em không tuyên bố teacher nào mạnh nhất tuyệt đối.

Sang student sau chưng cất trên cả 12 tổ hợp: 11 trên 12 ô KD đạt pAUC vượt cả teacher mạnh nhất, ở mức 0,1830; cặp cao nhất đạt 0,1859 — dù nhẹ hơn teacher nhiều lần. Nói cách khác, ở vùng vận hành lâm sàng, student đạt hiệu năng ngang hoặc vượt teacher.

Nhưng em xin chủ động nói phần chưa đạt, để trung thực: xét toàn dải xếp hạng — tức AUPRC — thì teacher vẫn nhỉnh hơn, 0,63 đến 0,66, so với dải 0,55 đến 0,65 của mười hai ô student — cặp KD cao nhất chỉ đạt 0,6510, vẫn dưới teacher mạnh nhất. Vì vậy đây là hai kết luận khác nhau tùy chỉ số, không được gộp làm một. Và thứ tự ba teacher cũng đảo chiều giữa hai chỉ số: EfficientNetV2-M thấp nhất AUPRC nhưng lại cao nhất pAUC ở cả bốn hàng student — điều này sẽ trở lại ở slide 23.

**[CHUYỂN TIẾP]** Những con số trên là điểm ước lượng. Câu hỏi tiếp theo: chênh lệch đó có đáng tin hay không?

---

## Slide 20 — Bằng chứng thống kê: không đếm thắng, đo khoảng tin cậy ⏱ 65s

**[LỜI NÓI]**
Nếu chỉ đếm dấu thô trên 12 cặp, kết quả rất đẹp: pAUC, AUC, độ nhạy đều thắng 12 trên 12; AUPRC thắng 10 trên 12. Nhưng đếm dấu không cho biết liệu chênh lệch có giữ nguyên nếu tập test đổi đi đôi chút hay không.

Vì vậy em dùng khoảng tin cậy bootstrap ghép cặp, hai nghìn lần lặp. Kết quả khắt khe hơn hẳn: số cặp có khoảng tin cậy loại trừ 0 ở phía dương là 9 trên 12 cho AUC-ROC, 8 trên 12 cho pAUC, nhưng chỉ 5 trên 12 cho AUPRC — chỉ số chính của luận văn.

Điều em muốn nhấn mạnh nhất: cột "âm có ý nghĩa" toàn số 0, ở mọi chỉ số — không một cặp nào bị chưng cất làm tệ đi có ý nghĩa thống kê. Bảy cặp còn lại trên AUPRC rơi vào "không kết luận được" — chưa đủ bằng chứng, không phải đã chứng minh là không có. Nguyên nhân của khoảng cách 12/12 xuống 5/12 không phải KD yếu, mà là cỡ mẫu — tập test in-domain chỉ có 241 ca dương; ở slide 26, bằng chứng trên HAM10000 với 1.169 ca dương sẽ mạnh hơn hẳn.

**[CHUYỂN TIẾP]** Vậy KD tác động mạnh nhất ở đâu, theo quy luật nào?

---

## Slide 21 — Quy luật: KD giúp nhiều nhất đúng ở student yếu nhất ⏱ 60s

**[LỜI NÓI]**
Em tính tương quan Pearson trên 12 cặp giữa pAUC baseline và mức cải thiện do KD mang lại: hệ số tương quan âm 0,963 — gần như tuyến tính hoàn hảo. Dấu âm nói rằng student càng mạnh sẵn thì chưng cất càng ít thay đổi được.

Minh chứng: RepViT-M1.0, baseline yếu nhất, chiếm cả hai vị trí đầu trong năm cặp cải thiện AUPRC lớn nhất — dẫn đầu là MaxViT dạy RepViT, cộng 0,0708. Ngược lại, FastViT-SA12, student mạnh nhất, là nơi KD tác động yếu nhất — trung bình chỉ cộng 0,0024 pAUC.

Quy luật này khớp cơ chế "làm mượt nhãn thích ứng" ở slide 6: student đủ mạnh thì vốn đã xử lý tốt mẫu mơ hồ, nên KD không còn gì để bù. Vì pAUC gần chạm trần 0,20, cách trình bày đúng là phần trăm khoảng cách còn lại được xóa — trung bình 12 cặp xóa được 22,7%.

**[CHUYỂN TIẾP]** Có hai cặp mang dấu âm ở bảng AUPRC tổng. Vì sao, và điều đó có nghĩa gì?

---

## Slide 22 — Hai miền ẩn sau một con số AUPRC tổng ⏱ 65s

**[LỜI NÓI]**
Tập test 62.040 ảnh nhưng 241 ca dương không nằm đều: 61.663 ảnh ISIC chỉ có 61 ca ác tính, trong khi 377 ảnh PAD chứa tới 180 ca — 0,6% số ảnh nắm ba phần tư số ca bệnh.

Hai cặp có Delta AUPRC âm ở bảng tổng — đều liên quan teacher EfficientNetV2-M — khi tách riêng theo miền lại dương rõ trên miền ISIC: cộng 19,4% và 33,1% tương đối. Phần âm hoàn toàn đến từ tập con PAD, vốn quyết định phần lớn con số tổng. Phát biểu đúng cho hai cặp này là "KD không giúp", chứ không phải "KD làm hại".

Quy luật thứ hai lộ ra ở đây: trên miền ISIC, mười trên mười hai cặp cải thiện từ 7% đến 43,8%; cùng những cặp ấy trên miền PAD chỉ dao động từ âm 4,2% đến dương 11,8% — KD giúp nhiều nhất đúng ở miền mà baseline còn yếu nhất, lặp lại quy luật ở slide trước nhưng theo trục miền ảnh.

**[CHUYỂN TIẾP]** Với ba teacher, câu hỏi tự nhiên là: teacher mạnh hơn có dạy tốt hơn không?

---

## Slide 23 — Đánh giá theo từng teacher: teacher mạnh hơn có dạy tốt hơn? ⏱ 60s

**[LỜI NÓI]**
Trong miền, trên AUPRC, thứ tự trùng khớp: MaxViT-Base mạnh nhất cũng cho mức cải thiện student cao nhất, cộng 0,0360, thắng cả bốn student; rồi ConvNeXtV2-Base; EfficientNetV2-M thấp nhất, chỉ thắng hai trên bốn. Nhưng với chỉ ba teacher, đây chỉ là "trùng thứ tự", chưa đủ để nói "tương quan" theo nghĩa thống kê.

Điều thú vị xảy ra khi đổi miền: trên HAM10000, chính EfficientNetV2-M — teacher yếu nhất trong miền — lại vươn lên tốt nhất. Nhưng trên Fitzpatrick17k thì đúng teacher đó rơi xuống cuối bảng, không student nào đạt khoảng tin cậy dương, hai trên bốn còn tụt AUC có ý nghĩa.

Kết luận: **không tồn tại một "teacher tốt nhất" độc lập với miền và với chỉ số đo**. Bước chọn teacher trong thực tế phải kèm một phép đánh giá trên miền gần miền triển khai, chứ không thể chỉ dựa vào điểm in-domain.

**[CHUYỂN TIẾP]** Trước khi sang hai tầng ngoài miền, em xin trình bày hai thí nghiệm kiểm chứng lựa chọn dữ liệu.

---

## Slide 24 — Kiểm chứng lựa chọn dữ liệu (1): trộn PAD-UFES-20 ⏱ 55s

**[LỜI NÓI]**
Đây là câu trả lời cho Q1. Em dựng một nhánh đối chứng chỉ huấn luyện trên ISIC, đủ 5 fold, rồi chấm trên đúng tập test đã dùng cho nhánh có PAD — đọc trên tập con 377 ảnh PAD, vì đọc trên toàn tập sẽ phóng đại do nhánh ISIC-only chưa từng thấy ảnh điện thoại.

Kết quả: cả ba teacher cải thiện, AUPRC cộng 0,092 đến 0,131. Ở tầng student — có ý nghĩa triển khai vì đây là mô hình đem lên thiết bị — ba trên bốn kiến trúc đạt khoảng tin cậy dương, cộng 0,105 đến 0,120; riêng RepViT không đạt ý nghĩa trên AUPRC nhưng đạt trên AUC và pAUC. Trên miền ISIC gốc, thêm PAD không hề gây hại — teacher trung tính, student ba trên bốn còn cải thiện.

Kết luận này rất chắc vì dựa trên khoảng tin cậy ghép cặp chứ không phải điểm ước lượng, và đúng cho cả mô hình đem đi triển khai, không chỉ teacher.

**[CHUYỂN TIẾP]** Thí nghiệm thứ hai kiểm chứng tỉ lệ lấy mẫu giảm.

---

## Slide 25 — Kiểm chứng lựa chọn dữ liệu (2): tỉ lệ undersampling 1:5 ⏱ 60s

**[LỜI NÓI]**
Đây là câu trả lời cho Q6. Em giữ cố định một cặp chưng cất, chỉ đổi tỉ lệ lấy mẫu thành 1:3, 1:5 và 1:10.

So với 1:10, tỉ lệ 1:5 thắng có ý nghĩa ở cả ba miền, AUPRC toàn tập cộng 0,057. Nguyên nhân thú vị: không phải vì 1:10 ít ca dương hơn — số ca ác tính không đổi ở cả ba nhánh, luôn 965 ảnh — mà vì nhánh 1:10 có nhiều ảnh lành tính hơn mỗi epoch, khiến mất mát validation chạm đáy sớm và kích hoạt dừng sớm ở cả 5 fold. Đây là tương tác giữa tỉ lệ lấy mẫu và tiêu chí dừng sớm, không phải mô hình học kém hơn.

So với 1:3 thì khác hẳn: khoảng tin cậy chứa 0, không phân biệt được — dù điểm ước lượng 1:3 trông nhỉnh hơn. Nếu chỉ nhìn điểm ước lượng sẽ kết luận sai là nên đổi sang 1:3. Kết luận đúng: 1:5 dẫn đầu ở pAUC — chỉ số chuẩn ISIC 2024 — không thua ở đâu, tránh mức 1:10 làm giảm hiệu năng rõ rệt.

**[CHUYỂN TIẾP]** Toàn bộ kết quả vừa rồi đều là in-domain. Câu hỏi quyết định là: KD có còn tác dụng khi mô hình rời khỏi miền huấn luyện không?

---

## Slide 26 — Tổng quát hoá xuyên miền: HAM10000 ⏱ 70s

**[LỜI NÓI]**
Đây là phần em cho là có tính quyết định nhất về bằng chứng của toàn luận văn. Em chấm nguyên trạng 19 lượt chạy trên HAM10000 — không huấn luyện thêm, không chỉnh ngưỡng — trên 7.470 ảnh, 1.169 ca ác tính.

Kết quả: 12 trên 12 cặp dương trên AUPRC, 11 trên 12 có khoảng tin cậy loại trừ 0 — chắc hơn hẳn 5 trên 12 trong miền, vì cỡ mẫu ca dương lớn hơn, 1.169 so với 241. Biên độ trải rộng 0,006 đến 0,0713, trung vị 0,0304. Bốn cặp dẫn đầu đều đổ vào MobileNetV4 và RepViT — hai student yếu nhất; ngoại lệ có ý nghĩa duy nhất là cặp dạy EfficientFormerV2-S2 — kém hơn baseline, vì đây là student mạnh nhất trên bộ này.

Hạn chế quan trọng: ngưỡng quyết định chọn từ trong miền **không chuyển miền được**. Trong miền, độ nhạy tại đặc hiệu cố định 90% đạt 92,7 đến 95,8%; sang HAM10000, dưới đúng ràng buộc ấy, không lượt nào vượt 51%, kể cả ba teacher — vì khả năng xếp hạng bị hỏng khi đổi nguồn sáng và kỹ thuật chụp, không phải do chọn ngưỡng sai.

**[CHUYỂN TIẾP]** Tầng đánh giá thứ ba đặt một câu hỏi khác hẳn: mô hình có phục vụ đồng đều mọi tông da không?

---

## Slide 27 — Công bằng theo tông da: Fitzpatrick17k ⏱ 70s

**[LỜI NÓI]**
Em chấm 19 lượt chạy trên 4.320 ảnh Fitzpatrick17k, chia ba nhóm tông da: sáng, trung bình, tối. Ở ngưỡng đóng băng từ trong miền, mô hình gắn cờ 93 đến 99% ảnh lành tính là báo động nhầm, nên mọi kết luận công bằng chỉ dựa vào AUC và AUPRC toàn dải ngưỡng, không dùng điểm vận hành.

Thứ tự AUC ba nhóm: sáng 0,6755, tối 0,6474, trung bình 0,6286. Đây là phát hiện bất ngờ nhất luận văn: giả thuyết "càng tối da càng kém" **không đứng được** — nhóm tối xếp hạng tốt hơn nhóm trung bình. Khoảng cách duy nhất dồn hẳn về một phía là giữa nhóm sáng và trung bình — cả 19 trên 19 lượt chạy có khoảng tin cậy loại trừ 0, cả AUC lẫn AUPRC.

Hai điều cho thấy mức độ nghiêm ngặt: bằng chứng chỉ dứt khoát sau khi em khôi phục độ phủ Fitzpatrick17k lên 99,98% — bản cũ chỉ tải 23,4%, chỉ 1/19 phân định được, còn dựng lên tín hiệu giả; và có một cạm bẫy phương pháp — so AUPRC thô giữa các nhóm tỉ lệ ca bệnh khác nhau dẫn tới kết luận ngược hẳn.

**[CHUYỂN TIẾP]** Sau khi đánh giá đủ ba tầng, em xin trình bày kết quả đo trên chính thiết bị thật.

---

## Slide 28 — Benchmark trên thiết bị biên: Pixel 6a ⏱ 70s

**[LỜI NÓI]**
Em đo 16 mô hình — bốn kiến trúc student, mỗi kiến trúc bốn biến thể gồm ba bản chưng cất và một bản đối chứng. Trước khi đo tốc độ, cả 16 mô hình phải vượt một cổng kiểm tra tương đương số học, và cả 16 đạt — ở cả máy chủ lẫn chính Pixel 6a.

Cổng này không phải thủ tục hình thức — nó bắt được một lỗi thật: EfficientFormerV2-S2 export "thành công" không cảnh báo, nhưng logit lệch tới 13 bậc độ lớn so với bản gốc, buộc phải chạy bằng bộ toán tử tham chiếu, chậm hơn nhiều.

Kết quả đo sau 5 phút chạy liên tục: MobileNetV4 nhanh nhất, 39,5 mili giây; RepViT 57,2; FastViT 113,9; còn EfficientFormerV2-S2 mất tới 3,9 giây — chậm hơn MobileNetV4 tới 181 lần lúc máy còn nguội. Điều tiết nhiệt làm ba kiến trúc trên backend tăng tốc chậm thêm 45 đến 49% sau 5 phút, đo khi nhiệt máy tăng từ 31,5 lên 40,1 độ C. Bộ nhớ không phải vấn đề. Và điểm quan trọng cho việc chọn teacher: bốn biến thể một kiến trúc chạy nhanh như nhau, nên chọn teacher nào là hoàn toàn miễn phí trên trục tốc độ.

**[CHUYỂN TIẾP]** Với dữ liệu tốc độ và độ chính xác đầy đủ, em xin đưa ra lựa chọn mô hình cuối cùng.

---

## Slide 29 — Lựa chọn mô hình triển khai ⏱ 65s

**[LỜI NÓI]**
Sau benchmark, đường biên Pareto chỉ còn hai ứng viên: cặp MaxViT dạy FastViT-SA12, và cặp ConvNeXtV2 dạy MobileNetV4. Cặp đầu cao hơn ở cả năm chỉ số chất lượng; cặp sau thắng tốc độ, dung lượng, và ổn định giữa các fold.

Để phân xử, em dùng khoảng tin cậy ghép cặp thay vì so hai khoảng riêng lẻ, vốn dễ đánh lừa do chồng lấn. Kết quả: trong miền, khác biệt không lớn — mọi khoảng tin cậy chứa 0. Ngoài miền thì rất rõ — 8 trên 8 chỉ số trên cả hai bộ ngoài miền đều loại trừ 0, mạnh nhất ở nhóm da tối, cộng 0,0646 AUPRC.

Khuyến nghị của em là cặp MaxViT dạy FastViT-SA12 cho kịch bản sàng lọc cộng đồng thực tế, đổi lại mỗi ảnh mất 113,9 mili giây thay vì 39,5. Khuyến nghị đảo lại trong hai trường hợp: nếu ràng buộc thiết bị cứng hoặc cần thời gian thực, chọn cặp MobileNetV4; và nếu chắc chắn ảnh đầu vào luôn cùng miền huấn luyện, hai cặp tương đương về chất lượng nên chọn MobileNetV4 vì nhanh hơn 2,9 lần.

**[CHUYỂN TIẾP]** Đến đây em xin tổng hợp lại câu trả lời cho toàn bộ sáu câu hỏi nghiên cứu.

---

# PHẦN 6 — KẾT LUẬN

## Slide 30 — Trả lời sáu câu hỏi nghiên cứu ⏱ 75s

**[LỜI NÓI]**
Q1, trộn PAD có giúp không: có, rất chắc, cả hai tầng, không hại miền ISIC.

Q2, teacher mạnh hơn có tạo student tốt hơn không: có khi đo trong miền, nhưng không có đáp án độc lập với miền triển khai — đảo hoàn toàn giữa HAM10000 và Fitzpatrick17k.

Q3, KD có nhất quán qua các paradigm không: có về hướng, xóa trung bình 22,7% khoảng cách còn lại tới trần pAUC, cả bốn paradigm hưởng lợi; nhưng bằng chứng ý nghĩa thống kê mạnh nhất nằm ở xuyên miền, do cỡ mẫu.

Q4, student có vượt teacher không: vượt trên pAUC và độ nhạy, chưa vượt trên AUPRC, thua rõ ngoài miền. Cặp triển khai: pAUC 0,1851 so với 0,1830 của teacher — cao hơn; AUPRC 0,6510 so với 0,6566 — chênh nhỏ hơn cả độ lệch chuẩn giữa các fold. Đổi lại nhẹ hơn 11,2 lần tham số/dung lượng, 16,2 lần FLOPs.

Q5, chọn gì để triển khai: cặp MaxViT dạy FastViT-SA12 cho kịch bản cộng đồng; cặp MobileNetV4 nếu ràng buộc thiết bị cứng — kết luận chắc chắn nhất trong sáu câu.

Q6, tỉ lệ 1:5 có đúng không: có, đã chứng minh — thắng 1:10 có ý nghĩa, không phân biệt được với 1:3.

**[CHUYỂN TIẾP]** Em xin nêu thẳng những hạn chế của nghiên cứu, chủ động, không đợi hội đồng hỏi.

---

## Slide 31 — Hạn chế của nghiên cứu ⏱ 60s

**[LỜI NÓI]**
Thứ nhất: dữ liệu ca ác tính trong miền quá ít — chỉ 241 ca dương, 74,7% đến từ 377 ảnh PAD. Vì vậy chỉ 5/12 cặp đạt khoảng tin cậy dương trong miền, và fold tốt nhất vượt trung bình tới 0,0263 AUPRC — lớn hơn cả hiệu quả KD trong miền là 0,0235. Đây là lý do em đặt luận điểm chính lên tầng xuyên miền, không phải in-domain.

Thứ hai: năng lực ngoài miền còn hạn chế — độ nhạy tại đặc hiệu 90% rơi còn 0,324 đến 0,510 trên HAM10000, còn Fitzpatrick17k thì gần như gắn cờ mọi ảnh; không cách chọn ngưỡng nào nâng được trần đó, vì giới hạn nằm ở khả năng xếp hạng.

Thứ ba: dịch chuyển miền gây khó cho cả teacher lẫn student như nhau — trên HAM10000, cả ba teacher cũng tụt về 0,481 đến 0,498, nằm gọn trong dải của 16 student — nghĩa là khoảng cách còn lại không phải cái giá của nén mô hình, mà là giới hạn của dữ liệu huấn luyện.

Về phạm vi kết luận: kỹ thuật thì dứt khoát — mô hình chạy thật, 113,9 mili giây, 16/16 vượt cổng kiểm tra tương đương. Lâm sàng thì chỉ trong phạm vi bốn bộ dữ liệu đã dùng — thẩm định tiến cứu trên bệnh nhân thật là thiết kế nghiên cứu khác, ngoài phạm vi luận văn này.

**[CHUYỂN TIẾP]** Từ những hạn chế đó, em đề xuất năm hướng phát triển tiếp theo.

---

## Slide 32 — Hướng phát triển & Kết luận ⏱ 70s

**[LỜI NÓI]**
Một, mở rộng nguồn dữ liệu — thêm ảnh lâm sàng smartphone, vì chỉ 377 ảnh PAD đã giúp AUPRC tăng 0,092 đến 0,131. Hai, tối ưu năng lực xử lý trên thiết bị — không phải nhỏ thêm, mà khai thác nhiều hơn từ tính toán sẵn có, kể cả đưa kiến trúc bị kẹt ở bộ toán tử tham chiếu trở lại backend tăng tốc. Ba, một cổng phát hiện ảnh ngoài phân phối — bắt buộc trước khi dùng thật, vì HAM10000 và Fitzpatrick17k vẫn là ảnh da nên chưa đại diện input thực sự bất thường. Bốn, một tầng đề xuất và hướng dẫn người dùng — diễn giải, theo dõi theo thời gian, khuyến nghị đi khám chứ không phải chẩn đoán — chỉ có nghĩa sau cổng OOD. Năm, mở rộng sang iOS — cổng kiểm tra tương đương và benchmark phải làm lại trên chính thiết bị đích.

Tóm lại, chưng cất tri thức áp dụng được cho bài toán này: cải thiện nhất quán về hướng trên cả bốn paradigm, không cặp nào bị làm hại có ý nghĩa trong miền, và bằng chứng quyết định nhất đến từ tầng xuyên miền. Mức cải thiện không đồng đều — phụ thuộc student, miền, teacher — và luận văn định lượng được từng phụ thuộc đó, thay vì chỉ khẳng định chung chung "KD có tác dụng".

Phần trình bày của em đến đây là hết. Em xin chân thành cảm ơn quý thầy cô đã lắng nghe, và rất mong nhận được góp ý từ hội đồng ạ.

---

## Slide 33 — Tài liệu tham khảo (phụ lục, dự phòng)

**[LỜI NÓI]** *(Chỉ dùng khi hội đồng hỏi nguồn)*
Dạ, danh sách tài liệu tham khảo chọn lọc có trong slide phụ lục ạ, đánh số riêng cho slide và có ghi số gốc trong luận văn. Ở đây em trích những công trình nền tảng nhất — Esteva 2017, Hinton 2015 về KD, Focal Loss của Lin 2017, ISIC 2024, các kiến trúc teacher/student, và các nghiên cứu KD da liễu gần đây như Islam 2024, Saha 2025, Winata 2025. Danh mục đầy đủ 55 tài liệu tham khảo nằm trong bản luận văn đầy đủ ạ.

---

## 📌 CHUẨN BỊ CHO PHẦN HỎI — ĐÁP (Q&A)

> Bộ slide này trình bày kết quả CUỐI CÙNG, đã hoàn tất. Hội đồng sẽ xoáy sâu vào tính vững của phương pháp thống kê, các hạn chế đã nêu, và các phát hiện bất ngờ (Q8, Q9, Q11 dưới đây) — chuẩn bị kỹ nhất cho nhóm này.

**Q1: Vì sao chọn AUPRC làm chỉ số chính thay vì Accuracy hay AUC-ROC?**
→ Vì prevalence chỉ 0,3885%. Ở mức mất cân bằng cực đoan này, một mô hình dự đoán "tất cả lành tính" đã đạt accuracy 99,61%, và AUC-ROC cũng bị lạc quan giả vì có quá nhiều mẫu âm dễ phân loại. AUPRC lấy chính prevalence làm đường cơ sở ngẫu nhiên, nên phản ánh đúng năng lực phát hiện ca ác tính.

**Q2: Vì sao không dùng lượng tử hóa (quantization) mà chỉ FP32?**
→ Bốn student đã được chọn theo tiêu chí tối ưu độ trễ trên thiết bị di động, nên bước lượng tử hóa không cần thiết trong phạm vi này; đây là lựa chọn scope có chủ đích, không phải thiếu sót, và INT8 để ngỏ cho hướng phát triển tiếp theo.

**Q3: Làm sao đảm bảo không rò rỉ dữ liệu giữa train và test?**
→ Bốn lớp bảo vệ: (1) tách held-out test khoảng 17% patient-disjoint TRƯỚC khi chia fold; (2) StratifiedGroupKFold nhóm theo patient_id cho 5 fold; (3) tiền tố riêng cho mã bệnh nhân/mã tổn thương khi ghép các bộ dữ liệu; (4) một phép đối chiếu tự động giữa hai bộ đánh giá ngoài với toàn bộ dữ liệu nội bộ, dừng chương trình với mã thoát khác 0 nếu phát hiện trùng lặp.

**Q4: Vì sao chọn T=4 và α=0,3? Có tuning không?**
→ Đây là cấu hình cố định theo thông lệ trong văn liệu KD. Vì trọng tâm luận văn là so sánh có/không KD trên nhiều kiến trúc và nhiều teacher — không phải tối ưu siêu tham số KD — em cố định T và α ở cùng một giá trị cho tất cả 12 cặp, để các hiệu số Δ so được với nhau. Đây là một giới hạn đã nêu rõ: kết luận đo tác động của KD dưới đúng cấu hình này, không phải tác động của KD nói chung.

**Q5: Vì sao dùng bootstrap CI ghép cặp thay vì paired t-test như đề cương ban đầu?**
→ 5 fold không phải 5 mẫu độc lập rút từ phân phối của tập test, mà là 5 mô hình khác nhau chấm trên cùng một tập 62.040 hàng — độ lệch chuẩn giữa các fold đo mức bất đồng giữa các mô hình, không đo sai số lấy mẫu mà kiểm định t giả định. Với n=5, lực thống kê cũng gần như không còn. Bootstrap ghép cặp resample trực tiếp trên hàng của tập test, không giả định dạng phân phối, và ghép cặp giữ được tương quan giữa hai nhánh so sánh.

**Q6: Vì sao dùng Pixel 6a mà không phải thiết bị khác?**
→ Luận văn đo trên một Google Pixel 6a, chip Tensor G1 với ba cụm lõi ARM khác nhau về hiệu năng — một thiết bị Android tầm trung. Về mặt thực tế, đây là lựa chọn hợp lý cho đối tượng người dùng cộng đồng mà đề tài nhắm tới, dù luận văn không dành riêng một đoạn để biện minh cho việc chọn máy này.

**Q7: Kết luận "KD cải thiện" của luận văn mạnh tới đâu — có phải "KD thắng 12/12" không?**
→ Không, và luận văn cố tình tránh câu đó. Đếm dấu thô thì 12/12 thắng ở pAUC/AUC/độ nhạy, nhưng khoảng tin cậy ghép cặp — phép kiểm khắt khe hơn — chỉ cho 5/12 cặp có ý nghĩa trên AUPRC trong miền. Phát biểu đúng và mạnh nhất mà dữ liệu cho phép là: không một cặp nào bị KD làm tệ đi có ý nghĩa thống kê; còn "cải thiện có ý nghĩa" thì tùy chỉ số và tùy tầng đánh giá, mạnh nhất ở xuyên miền.

**Q8: Vì sao bằng chứng ở in-domain (5/12) lại yếu hơn hẳn ở HAM10000 (11/12)? Có phải KD chỉ thật sự tác dụng ngoài miền?**
→ Không phải KD yếu hơn trong miền — nguyên nhân đã xác định được là cỡ mẫu. Tập test in-domain chỉ có 241 ca dương, còn HAM10000 có 1.169, nên cùng một hiệu ứng cho khoảng tin cậy hẹp hơn hẳn ở HAM10000. Cách đọc đúng: bằng chứng in-domain "chưa đủ để khẳng định", không phải "đã chứng minh không có" — và đây là lý do luận văn đặt luận điểm chính lên tầng xuyên miền.

**Q9: "Không có teacher tốt nhất độc lập với miền" — phát hiện này có ý nghĩa gì cho người thiết kế hệ thống?**
→ Nghĩa là bước chọn teacher không thể chỉ dựa vào điểm số in-domain. Teacher tốt nhất trên ảnh dermoscopic (HAM10000) lại là teacher tệ nhất trên ảnh lâm sàng trường rộng (Fitzpatrick17k). Quy trình đúng phải bao gồm một lần đánh giá trên miền gần với miền triển khai thực tế trước khi chốt teacher, chứ không lấy backbone có điểm cao nhất rồi mặc định nó cũng dạy tốt nhất.

**Q10: Student có vượt được teacher không?**
→ Tùy chỉ số. Ở pAUC@TPR≥80% và độ nhạy thì có — 11/12 cặp KD vượt pAUC teacher mạnh nhất. Ở AUPRC so với chính teacher mạnh nhất thì chưa — cặp chưng cất tốt nhất chỉ đạt 0,6510, vẫn dưới 0,6566 của teacher mạnh nhất. Ngoài miền huấn luyện thì student thua rõ. Với cặp đem triển khai cụ thể, chênh lệch AUPRC chỉ 0,0056 — nhỏ hơn cả độ lệch chuẩn giữa 5 fold của chính mỗi bên — trong khi đổi lại nhẹ hơn 11,2 lần tham số và dung lượng — đây đúng là vai trò được kỳ vọng ở chưng cất tri thức.

**Q11: Fitzpatrick17k cho thấy nhóm tối tốt hơn nhóm trung bình — kết quả này có tin được không, hay chỉ là do cỡ mẫu nhóm tối nhỏ?**
→ Câu hỏi rất đúng chỗ, và em đã kiểm tra riêng. Khoảng cách nhóm tối trừ nhóm trung bình có dấu nhất quán — nhóm tối cao hơn — nhưng bằng chứng mỏng, không lượt nào phân định được trên AUC. Khoảng cách duy nhất dứt khoát, có ý nghĩa ở cả 19/19 lượt chạy, là giữa nhóm sáng và nhóm trung bình. Vì vậy phát biểu đúng là: giả thuyết "càng tối da càng kém" không đứng được trên bằng chứng này, nhưng em cũng không tuyên bố nhóm tối được phục vụ tốt — vì nhóm tối chỉ có 411 ảnh mỗi fold, ít hơn nhóm sáng gần sáu lần, nên khoảng tin cậy liên quan tới nó đều rộng hơn hẳn.

**Q12: Sao biết trộn PAD-UFES-20 là có lợi, mà không phải chỉ làm nhiễu dữ liệu?**
→ Em không giả định mà chạy một thí nghiệm đối chứng có kiểm soát: mỗi teacher hai nhánh, cấu hình y hệt, chỉ khác tập huấn luyện, đánh giá trên cùng một tập test — 30 lượt huấn luyện ở tầng teacher, 40 lượt ở tầng student. Kết quả: cả ba teacher và ba trên bốn student cải thiện có ý nghĩa trên miền PAD, còn trên miền ISIC gốc thì không hại — thậm chí ba trên bốn student còn cải thiện thêm. Vì nhất quán trên nhiều kiến trúc nên đây không phải may mắn của một mô hình.

**Q13: Latency đảo trên mobile nghĩa là gì, vì sao quan trọng?**
→ Trên CPU ARM của điện thoại, chọn backend thực thi quyết định tốc độ nhiều hơn cả số tham số. Kiến trúc EfficientFormerV2-S2 có 12,1 triệu tham số nhưng bị hạ đồ thị sai trên backend tăng tốc nên phải chạy trên bộ toán tử tham chiếu đơn luồng, chậm hơn MobileNetV4 — chỉ 8,4 triệu tham số — tới 181 lần. Bài học: không thể suy độ trễ mobile từ số tham số hay FLOPs, phải đo trên chính thiết bị thật, và phải có một cổng kiểm tra tương đương để phát hiện những trường hợp hạ đồ thị sai như thế này.

**Q14: Xác suất mô hình đưa ra có tin được không, khi huấn luyện có undersampling?**
→ Bộ lấy mẫu dạy mô hình theo tỉ lệ ác tính khoảng 16,7% mỗi epoch, trong khi thực tế chỉ 0,3885%, nên có cơ sở để nghi ngờ xác suất sigmoid thô bị lệch. Điều quan trọng: dù có lệch hay không, điều đó **không ảnh hưởng tới bất kỳ kết luận xếp hạng nào** em vừa trình bày, vì AUPRC, pAUC và AUC — cả sáu câu hỏi nghiên cứu của luận văn — đều tính từ thứ hạng chứ không từ giá trị xác suất, nên bất biến với mọi phép biến đổi đơn điệu của điểm số. Việc hiệu chuẩn lại con số phần trăm hiển thị cho người dùng cuối là một bước độc lập, có thể làm hoàn toàn về sau mà không đụng tới bất kỳ số liệu nào ở Chương 4 — nhưng nằm ngoài phạm vi sáu câu hỏi nghiên cứu mà luận văn này trả lời, nên em không đưa vào báo cáo.

**Q15: Vì sao cả ba teacher đều suy giảm mạnh trên HAM10000 và Fitzpatrick17k — điều đó có phủ nhận giá trị của việc dùng mô hình lớn không?**
→ Không phủ nhận, nhưng nó đổi cách hiểu về khoảng cách còn lại. Khi ra ngoài miền huấn luyện, mức suy giảm không phân biệt mô hình lớn với mô hình nhỏ — cả ba teacher cũng tụt độ nhạy xuống dải tương đương 16 student. Điều đó cho thấy khoảng cách ngoài miền là giới hạn của chính dữ liệu huấn luyện, không phải cái giá phải trả khi nén mô hình bằng chưng cất — nên hướng khắc phục đúng là mở rộng miền dữ liệu huấn luyện hoặc thêm cơ chế thích nghi miền, chứ không phải bỏ KD hay chọn teacher khác.
