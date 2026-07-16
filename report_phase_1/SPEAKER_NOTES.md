# KỊCH BẢN THUYẾT TRÌNH — BẢO VỆ ĐỀ CƯƠNG LUẬN VĂN

> **Cách dùng:** Mỗi mục tương ứng 1 slide trong [SLIDE_CONTENT.md](SLIDE_CONTENT.md) (bố cục **24 slide** + phụ lục tài liệu tham khảo, cập nhật 2026-07-04). Phần **[LỜI NÓI]** là kịch bản để nói theo (văn nói tự nhiên, KHÔNG đọc nguyên văn bullet trên slide). **[CHUYỂN TIẾP]** là câu nối sang slide sau. **⏱** là thời lượng gợi ý.
>
> **Tổng thời lượng mục tiêu: ~18 phút** (còn ~2–7 phút cho Q&A tùy quy định hội đồng). Nếu chỉ cho 15 phút: lướt nhanh slide 12 (dữ liệu bổ trợ), 14 (related work), 19B (bỏ hẳn — là slide tùy chọn).
>
> **Mẹo trình bày:**
> - Đừng đọc bullet — bullet để hội đồng đọc, bạn *kể* nội dung.
> - Xương sống để hội đồng nhớ: **3 vấn đề → 1 nút thắt → KD → 3 câu hỏi (RQ1/2/3) → kết quả bước đầu chứng minh khả thi.**
> - **Điểm nhấn lớn nhất của buổi này là PHẦN 6 (slide 20–22): đã có KẾT QUẢ THẬT.** Đây là thứ khác biệt so với một đề cương thuần lý thuyết — hãy dành năng lượng và sự tự tin cho phần này.
> - **Nguyên tắc vàng khi đọc số: TRUNG THỰC.** Chỗ nào mới đủ 4 fold, chỗ nào KD chỉ "có sắc thái" (AUPRC phụ thuộc teacher) — nói thẳng. Hội đồng đánh giá cao sự trung thực hơn là tô hồng.

---

## Slide 1 — Trang bìa ⏱ 30s

**[LỜI NÓI]**
Kính thưa quý thầy cô trong hội đồng. Em xin tự giới thiệu, em là Đặng Quang Hưng, học viên cao học khóa 18. Hôm nay em xin trình bày đề cương luận văn với đề tài *"Phát hiện ung thư da trên thiết bị biên sử dụng mô hình học sâu kết hợp chưng cất tri thức"*, dưới sự hướng dẫn của thầy TS. Nguyễn Thanh Bình.

**[CHUYỂN TIẾP]** Sau đây em xin đi vào nội dung trình bày.

---

## Slide 2 — Nội dung trình bày (Agenda) ⏱ 25s

**[LỜI NÓI]**
Bài trình bày của em gồm bảy phần. Đầu tiên là vấn đề và động lực nghiên cứu. Tiếp đến là kỹ thuật chưng cất tri thức và câu hỏi nghiên cứu. Phần ba là dữ liệu — trong đó em phân tích sâu bộ ISIC 2024 — và ba thách thức đặc trưng. Phần bốn là các nghiên cứu liên quan và giải pháp đề xuất. Phần năm là phương pháp thực hiện đầu–cuối. Phần sáu — em xin nhấn mạnh — là độ đo đánh giá và **kết quả bước đầu đã chạy được**. Cuối cùng là kế hoạch và kết luận.

**[CHUYỂN TIẾP]** Trước hết, em xin bắt đầu với vấn đề gốc của bài toán.

---

# PHẦN 1 — VẤN ĐỀ & ĐỘNG LỰC

## Slide 3 — Vấn đề 1: Nghịch lý melanoma ⏱ 55s

**[LỜI NÓI]**
Vấn đề gốc của đề tài xuất phát từ một nghịch lý. Theo GLOBOCAN 2022, mỗi năm có khoảng 331 nghìn ca mắc mới ung thư hắc tố — melanoma — và gần 59 nghìn ca tử vong.

Điều đáng chú ý là: melanoma chỉ chiếm khoảng 10% tổng số ca ung thư da, nhưng lại gây ra tới 80% số ca tử vong. Tức đây là loại nguy hiểm nhất.

Nhưng có một tin tốt: nếu phát hiện ở giai đoạn khu trú, tỷ lệ sống sau 5 năm lên tới 99%. Nói cách khác, khoảng cách giữa con số 99% khi bắt sớm và số ca tử vong khi bắt muộn — chính là dư địa mà công nghệ có thể lấp. Cơ hội sống gần như phụ thuộc hoàn toàn vào việc phát hiện có kịp thời hay không.

**[CHUYỂN TIẾP]** Vậy hiện nay việc phát hiện sớm đang gặp trở ngại gì?

---

## Slide 4 — Vấn đề 2: Thiếu bác sĩ, mà AI mạnh lại kẹt trên cloud ⏱ 70s

**[LỜI NÓI]**
Vấn đề thứ hai là khoảng trống tiếp cận. Chẩn đoán truyền thống dựa vào kinh nghiệm bác sĩ da liễu qua soi da và quy tắc ABCD, nhưng ở nhiều khu vực thiếu chuyên gia và chi phí thăm khám cao, nên người dân khó tiếp cận.

Học sâu, đặc biệt là CNN, đã chứng minh đạt độ chính xác ngang bác sĩ da liễu — công trình kinh điển của Esteva năm 2017 trên Nature. Các kiến trúc như EfficientNet, Vision Transformer liên tục cải thiện.

Tuy nhiên có một rào cản: những mô hình mạnh nhất thường rất lớn nên phải chạy trên đám mây. Điều này kéo theo ba vấn đề: độ trễ, phụ thuộc kết nối internet, và đặc biệt là rủi ro riêng tư — vì ảnh y tế của bệnh nhân phải gửi lên server.

Vì vậy xu hướng hiện nay là đưa AI xuống thẳng thiết bị — gọi là Edge AI: sàng lọc ngay tại chỗ, chạy offline, và bảo vệ quyền riêng tư vì dữ liệu không rời khỏi máy.

**[CHUYỂN TIẾP]** Nhưng đưa AI xuống thiết bị lại chạm ngay vào một nút thắt.

---

## Slide 5 — Vấn đề 3: Nút thắt cốt lõi — nhỏ thì kém chính xác ⏱ 60s

**[LỜI NÓI]**
Nút thắt cốt lõi là sự đánh đổi giữa độ chính xác và kích thước, tốc độ. Các mô hình gọn như EfficientNet-B0, MobileNetV3 hay MobileViT chạy được trên điện thoại, nhưng thường phải chấp nhận suy giảm độ chính xác.

Trong y tế đây là điều rất nhạy cảm. Nếu mô hình bỏ sót một ca ác tính — một ca ung thư bị chẩn đoán nhầm là lành tính — hậu quả có thể rất nghiêm trọng. Do đó yêu cầu về độ nhạy rất khắt khe. Đây cũng là lý do cuộc thi ISIC 2024 chọn chỉ số pAUC ở mức độ nhạy từ 80% trở lên làm thước đo chính thức — chỉ thưởng cho vùng độ nhạy cao.

Vậy câu hỏi nút thắt đặt ra là: làm sao để một mô hình vừa đủ nhỏ để chạy trên điện thoại, mà vẫn không bỏ sót ca ác tính? Chính đánh đổi này là lý do tồn tại của đề tài.

**[CHUYỂN TIẾP]** Và kỹ thuật hứa hẹn nhất để gỡ nút thắt này chính là chưng cất tri thức.

---

# PHẦN 2 — GIẢI PHÁP & CÂU HỎI NGHIÊN CỨU

## Slide 6 — Vì sao chọn Chưng cất tri thức (KD)? ⏱ 80s

*(Slide dùng hình sẵn `figures/kd_flow_slide.png` — chỉ vào hình khi nói)*

**[LỜI NÓI]**
Chưng cất tri thức — Knowledge Distillation — được Hinton đề xuất năm 2015. Ý tưởng là dùng một mô hình teacher lớn, chính xác cao, để dạy một mô hình student nhỏ gọn. Điểm mấu chốt là student không chỉ học từ nhãn cứng 0/1, mà học từ *nhãn mềm* — tức phân phối xác suất của teacher. Phân phối mềm này mang theo thông tin về mức độ tương đồng giữa các lớp mà nhãn cứng bỏ qua — người ta gọi đó là "dark knowledge".

Vì sao KD đặc biệt phù hợp bài toán của em? Ba lý do. Thứ nhất, student vẫn nhỏ và nhanh như cũ, chi phí suy luận không đổi, nhưng học được "kinh nghiệm" của teacher — nhắm thẳng vào nút thắt "nhỏ mà vẫn chính xác". Thứ hai, tín hiệu mềm của teacher làm mượt biên quyết định, đặc biệt có lợi ở lớp ác tính hiếm, nơi nhãn cứng quá thưa. Thứ ba, không cần đổi kiến trúc suy luận, không cần thêm dữ liệu gán nhãn — nên rẻ và triển khai được ngay trên điện thoại.

Nói ngắn gọn: KD là cách "nén tri thức" chứ không "nén thô", nên giữ được độ chính xác trong ngân sách của thiết bị biên. Trên hình quý thầy cô có thể thấy: teacher đóng băng sinh nhãn mềm, còn gradient chỉ cập nhật student.

**[CHUYỂN TIẾP]** KD hứa hẹn như vậy, nhưng khi nhìn vào các nghiên cứu hiện có, em thấy vẫn còn khoảng trống.

---

## Slide 7 — Khoảng trống: KD trong da liễu vẫn bỏ ngỏ ⏱ 55s

**[LỜI NÓI]**
KD đã được dùng trong da liễu, nhưng chưa ai trả lời trọn vẹn. Thứ nhất, đa số nghiên cứu mới chỉ khảo sát một cặp teacher–student duy nhất. Thứ hai, chưa có nghiên cứu nào đánh giá KD một cách hệ thống trên nhiều paradigm kiến trúc student khác nhau — CNN, hybrid, transformer. Thứ ba, chưa ai kiểm chứng liệu một teacher mạnh hơn có thực sự tạo ra student tốt hơn không. Thứ tư, sau khi distill, mô hình có thực sự chạy được trên điện thoại với độ trễ chấp nhận được không. Và cuối cùng, bộ ISIC 2024 — vốn có ảnh gần với ảnh smartphone nhất — gần như chưa được khai thác trong bối cảnh KD.

**[CHUYỂN TIẾP]** Từ những khoảng trống này, em hình thành câu hỏi nghiên cứu trung tâm.

---

## Slide 8 — Câu hỏi nghiên cứu trung tâm ⏱ 70s

**[LỜI NÓI]**
Câu hỏi nghiên cứu trung tâm là: *liệu chưng cất tri thức có mang lại cải thiện đáng kể và nhất quán cho các mô hình nhẹ thuộc nhiều paradigm thiết kế khác nhau, và chất lượng của teacher ảnh hưởng thế nào đến hiệu quả KD trên student?*

Em phân rã thành ba câu hỏi con. RQ1: KD có cải thiện nhất quán không, và paradigm kiến trúc nào hưởng lợi nhiều nhất? RQ2: teacher mạnh hơn thì có tạo student tốt hơn không — tức tương quan giữa chất lượng teacher và mức cải thiện. RQ3: student sau distill có thực sự chạy được trên điện thoại không?

Để trả lời khách quan, em không chỉ báo cáo độ chính xác đơn thuần, mà thiết kế một thực nghiệm so sánh đối chứng có kiểm soát: mỗi student được huấn luyện song song theo hai nhánh — một có KD, một không — với mọi thứ khác giữ nguyên. Nhờ vậy phần chênh lệch, em ký hiệu Delta pAUC và Delta AUPRC, chính là tác động thuần túy của KD. Đây cũng là đóng góp khoa học cốt lõi của đề tài.

**[CHUYỂN TIẾP]** Từ ba câu hỏi này, em cụ thể hóa thành các mục tiêu.

---

## Slide 9 — Mục tiêu đề tài ⏱ 65s

**[LỜI NÓI]**
Mục tiêu tổng quát là đánh giá có hệ thống hiệu quả của KD cho các mô hình nhỏ, đồng thời kiểm chứng khả năng triển khai thực tế trên Android. Mục tiêu này chia thành ba nhóm tuần tự.

Nhóm thứ nhất — nền tảng dữ liệu: pipeline từ ISIC 2024 kết hợp PAD-UFES-20, với 5-fold cross-validation theo nguyên tắc patient-disjoint để tránh rò rỉ. Việc bổ sung PAD giúp nâng tỷ lệ mẫu ác tính từ khoảng 0,1% lên 0,39%.

Nhóm thứ hai — trọng tâm: huấn luyện và so sánh đối chứng KD với baseline trên nhiều kiến trúc teacher và student, đồng thời phân tích tương quan giữa chất lượng teacher và mức cải thiện AUPRC của student.

Nhóm thứ ba — tổng quát hóa và triển khai: kiểm chứng chéo miền trên HAM10000, phân tích công bằng trên Fitzpatrick17k, và export mô hình sang ExecuTorch để đo hiệu năng thật trên điện thoại Pixel 6a.

**[CHUYỂN TIẾP]** Để thực hiện, trước hết em xin nói rõ về bài toán và dữ liệu.

---

# PHẦN 3 — DỮ LIỆU & THÁCH THỨC

## Slide 10 — Bài toán & bốn bộ dữ liệu ⏱ 70s

**[LỜI NÓI]**
Bài toán được đặt trong khung phân loại nhị phân: đầu vào là ảnh tổn thương da 224×224, đầu ra là một logit duy nhất, áp sigmoid để ra xác suất ác tính. Về ánh xạ nhãn, em tuân theo quy ước lâm sàng: melanoma, ung thư biểu mô tế bào đáy và tế bào vảy được gán ác tính; còn nốt ruồi lành, dày sừng và các tổn thương lành khác gán lành tính.

Đề tài dùng bốn bộ dữ liệu với vai trò tách bạch. ISIC 2024 với hơn 400 nghìn ảnh non-dermoscopic là dữ liệu huấn luyện chính và test nội bộ. PAD-UFES-20 gồm ảnh chụp smartphone, dùng để bổ sung mẫu ác tính. HAM10000 là ảnh dermoscopic, chỉ dùng kiểm chứng chéo miền. Và Fitzpatrick17k, có thông tin thang sắc tố da từ một đến sáu, dùng để phân tích công bằng.

Em xin nhấn mạnh: hai bộ HAM10000 và Fitzpatrick17k tuyệt đối không dùng để train, chỉ dùng đánh giá hậu kỳ.

**[CHUYỂN TIẾP]** Trong bốn bộ này, ISIC 2024 là bộ trung tâm — em xin phân tích kỹ vì sao nó "đúng" cho đề tài.

---

## Slide 11 — Phân tích sâu ISIC 2024 ⏱ 75s

**[LỜI NÓI]**
Đây là slide chứng minh em chọn đúng bộ dữ liệu. ISIC 2024 SLICE-3D có hơn 401 nghìn ảnh tổn thương da, cắt ra từ ảnh chụp toàn thân 3D của hàng nghìn bệnh nhân.

Bộ này hội đủ ba điều kiện mà đề tài cần. Thứ nhất, loại ảnh là non-dermoscopic — gần với ảnh chụp smartphone trong điều kiện thực, không cần máy soi da chuyên dụng — đúng đối tượng triển khai của đề tài. Các bộ dermoscopic như HAM10000 tuy đẹp nhưng xa thực tế người dùng cộng đồng.

Thứ hai, quy mô lớn và có sẵn mã bệnh nhân patient_id, cho phép chia fold patient-disjoint để chống rò rỉ dữ liệu.

Thứ ba, phân phối lớp cực kỳ mất cân bằng — chỉ khoảng 0,1% ác tính, tức khoảng một ca ác tính trên một nghìn ảnh — phản ánh đúng bối cảnh sàng lọc bệnh hiếm ngoài thực tế. Và cuộc thi đã định nghĩa sẵn metric pAUC ở TPR từ 80%, khớp trực tiếp với yêu cầu "không bỏ sót ca ác tính".

Tóm lại, ISIC 2024 là bộ thực tế nhất hiện có cho kịch bản Edge AI cộng đồng, nên em chọn làm bộ huấn luyện chính.

**[CHUYỂN TIẾP]** Bên cạnh ISIC, ba bộ còn lại đóng vai trò bổ trợ.

---

## Slide 12 — Các bộ dữ liệu bổ trợ ⏱ 50s

**[LỜI NÓI]**
PAD-UFES-20 gồm khoảng 2.300 ảnh chụp smartphone lâm sàng. Vai trò của nó là bổ sung mẫu ác tính, giúp nâng tỷ lệ ác tính tổng từ khoảng 0,1% lên 0,39%, để mô hình học lớp hiếm ổn định hơn. Khi ghép PAD vào, em gán thêm tiền tố "pad_" cho mã bệnh nhân để không trùng mã với ISIC — đây là bước chống rò rỉ.

Hai bộ còn lại chỉ dùng đánh giá hậu kỳ: HAM10000 là ảnh dermoscopic, dùng kiểm chứng chéo miền vì khác loại ảnh so với train; Fitzpatrick17k có thang sắc tố da, dùng phân tích công bằng theo nhóm màu da.

**[CHUYỂN TIẾP]** Bốn bộ dữ liệu này đặt ra ba thách thức đặc trưng mà em phải xử lý.

---

## Slide 13 — Ba thách thức & cách xử lý ⏱ 70s

**[LỜI NÓI]**
Thách thức thứ nhất là mất cân bằng lớp cực đoan — chỉ khoảng 0,39% mẫu ác tính. Ở mức này, AUC-ROC có xu hướng lạc quan giả. Vì vậy em chọn AUPRC làm chỉ số chính, còn pAUC ở TPR từ 80% là ưu tiên thứ hai. Về mặt huấn luyện, em kết hợp dynamic undersampling theo tỷ lệ 1:5 mỗi epoch, cùng Focal Loss để mô hình tập trung vào các mẫu khó.

Thách thức thứ hai là rò rỉ dữ liệu. Toàn bộ tổn thương của một bệnh nhân phải nằm trong cùng một fold. Em dùng StratifiedGroupKFold, tách một tập test độc lập khoảng 17% ra trước khi chia fold, và gán tiền tố "pad_" cho mã bệnh nhân khi ghép PAD.

Thách thức thứ ba là ràng buộc triển khai biên: mô hình cuối phải đủ nhỏ và nhanh, nên có giới hạn cứng về tham số, FLOPs và độ trễ — và bắt buộc phải đo trên máy thật.

**[CHUYỂN TIẾP]** Trước khi trình bày giải pháp, em xin điểm qua các nghiên cứu liên quan để thấy đề tài đứng ở đâu.

---

# PHẦN 4 — NGHIÊN CỨU LIÊN QUAN & GIẢI PHÁP

## Slide 14 — Các nghiên cứu liên quan (dòng thời gian 10 năm) ⏱ 80s

**[LỜI NÓI]**
Em xin tóm tắt lĩnh vực theo dòng thời gian mười năm.

Giai đoạn 2015 đến 2019 là giai đoạn đặt nền móng. Esteva 2017 lần đầu chứng minh CNN phân loại ung thư da ngang bác sĩ. Cùng thời kỳ, Hinton đề xuất KD, và hai kiến trúc gọn nhẹ quan trọng ra đời là EfficientNet và MobileNetV3.

Giai đoạn 2020 đến 2021, các mô hình lớn thống trị bảng xếp hạng — ensemble EfficientNet, rồi Vision Transformer. Chính xác cao, nhưng nặng, không chạy được trên điện thoại.

Giai đoạn 2022 đến 2023, cộng đồng tìm kiến trúc cân bằng, tiêu biểu là MobileViT và biến thể HI-MViT.

Và giai đoạn 2024 đến 2025 là lúc hai chuyển biến xảy ra đồng thời: bộ ISIC 2024 gần ảnh smartphone ra đời, và KD bắt đầu được áp dụng nghiêm túc vào da liễu — như Islam 2024 nén student còn hơn 2 megabyte, hay Saha 2025 nén student nhỏ hơn teacher tới 160 lần.

Điểm chốt: hai hướng "mô hình lớn chính xác" và "mô hình nhỏ triển khai được" phát triển song song nhưng chưa thực sự hội tụ — đó là chỗ đứng của đề tài.

**[CHUYỂN TIẾP]** Từ đó, em đề xuất giải pháp: một khung teacher–student đa kiến trúc.

---

## Slide 15 — Giải pháp: nhiều teacher & student trên nhiều paradigm ⏱ 85s

**[LỜI NÓI]**
Ý tưởng cốt lõi là: thay vì chỉ một cặp teacher–student, em huấn luyện cả một dải teacher với chất lượng khác nhau, ghép với cả một dải student trải nhiều paradigm khác nhau. Chỉ khi làm vậy mới trả lời được RQ1 — paradigm nào hưởng lợi nhất, và RQ2 — teacher mạnh có tạo student tốt hơn không.

Về teacher, em có bốn kiến trúc sắp theo chất lượng tăng dần: EfficientNet-B4 khoảng 17,6 triệu tham số làm mốc, rồi EfficientNetV2-M, ConvNeXtV2-Base, và mạnh nhất là MaxViT-Base — một kiến trúc lai CNN với Transformer.

Về student, em có sáu kiến trúc trải nhiều paradigm: từ nhóm cổ điển EfficientNet-B0, MobileNetV3-Large, MobileViT-S; đến nhóm thế hệ mới tối ưu cho di động là MobileNetV4, FastViT và EfficientFormerV2.

Em xin lưu ý: đây không phải hai "tầng" tách biệt, mà là một dải teacher từ yếu đến mạnh và một dải student đa paradigm, để quét được cả hai câu hỏi trong cùng một khung đối chứng. Tất cả mô hình dùng chung một classification head, load backbone từ thư viện timm — các kiến trúc mới yêu cầu timm phiên bản 1.0 trở lên — và teacher luôn được đóng băng khi distill.

**[CHUYỂN TIẾP]** Vậy việc chưng cất được thực hiện qua hàm mất mát như thế nào?

---

## Slide 16 — Hàm mất mát chưng cất ⏱ 70s

**[LỜI NÓI]**
Hàm mất mát KD của em gồm hai thành phần, theo nguyên lý Hinton nhưng có điều chỉnh cho bài toán mất cân bằng.

Thành phần thứ nhất là L_hard — tín hiệu từ nhãn cứng. Điểm khác biệt so với Hinton gốc: em không dùng cross-entropy thông thường, mà dùng Focal Loss với gamma bằng 2 và alpha bằng 0,25, để mô hình tập trung vào các mẫu ác tính hiếm và khó.

Thành phần thứ hai là L_soft — phần truyền dark knowledge từ teacher, tính bằng BCE giữa phân phối mềm của student và của teacher, với nhiệt độ T bằng 4.

Hai thành phần cân bằng bởi hệ số alpha bằng 0,3 — tức 30% cho nhãn cứng và 70% cho nhãn mềm, phản ánh việc em muốn student học nhiều từ teacher.

Một điểm quan trọng về thiết kế thí nghiệm: khi chạy nhánh baseline, em đặt alpha bằng 1,0 và không load teacher. Nhờ vậy nhánh baseline hoàn toàn không có bất kỳ ảnh hưởng nào của KD — đây là nền để đo Delta một cách sạch sẽ.

**[CHUYỂN TIẾP]** Và đây chính là điểm cốt lõi trong thiết kế thực nghiệm của em.

---

## Slide 17 — Thiết kế thực nghiệm so sánh đối chứng ⏱ 70s

**[LỜI NÓI]**
Điểm mấu chốt trong thiết kế là nguyên tắc ceteris paribus — "mọi thứ khác giữ nguyên". Mỗi student được huấn luyện song song theo hai nhánh, có KD và không KD, với cùng dữ liệu, cùng seed ngẫu nhiên, cùng siêu tham số và cùng quy trình đánh giá. Khác biệt duy nhất là hàm mất mát. Nhờ đó, mọi chênh lệch quan sát được đều quy về tác động của KD, không lẫn nhiễu.

Về quy mô, toàn bộ ma trận thực nghiệm gồm: 4 teacher nhân 5 fold là 20 lượt huấn luyện; 6 student baseline nhân 5 fold là 30 lượt; và khoảng 12 cặp teacher–student KD nhân 5 fold là khoảng 60 lượt.

Hiệu quả KD được định lượng qua Delta pAUC và Delta AUPRC — lấy KD trừ baseline. Và để khẳng định chênh lệch có ý nghĩa thống kê chứ không ngẫu nhiên, em dùng kiểm định Paired t-test trên 5 fold với mức ý nghĩa p nhỏ hơn 0,05 — không kết luận từ một con số điểm.

**[CHUYỂN TIẾP]** Tiếp theo em xin trình bày phương pháp thực hiện cụ thể.

---

# PHẦN 5 — PHƯƠNG PHÁP THỰC HIỆN

## Slide 18 — Pipeline thực thi đầu–cuối ⏱ 75s

*(Slide dùng hình sẵn `figures/kd_pipeline_slide.png` — 3 bước. Chỉ vào hình khi nói.)*

**[LỜI NÓI]**
Toàn bộ quy trình từ dữ liệu thô đến mô hình trên điện thoại, em tóm tắt thành ba bước trên hình.

Bước một là chuẩn bị dữ liệu và huấn luyện teacher. Về dữ liệu, em chia hai giai đoạn: giai đoạn offline chạy một lần — giải mã ảnh, resize 224×224, lọc ảnh hỏng và trùng, chuẩn hóa nhãn, rồi tách tập test độc lập trước khi chia 5 fold; giai đoạn online trong lúc train dùng Albumentations để tăng cường — lật, xoay, dịch chuyển co giãn, jitter màu, CLAHE, làm mờ Gauss. Em cố ý không dùng MixUp, CutMix hay CutOut vì không phù hợp với vùng tổn thương tập trung. Teacher được train trước bằng Focal Loss thuần.

Bước hai là chưng cất KD: mỗi student train hai nhánh — nhánh KD dùng KDTrainer, nhánh baseline dùng Trainer thường — với sampler undersampling 1:5 mỗi epoch.

Bước ba là đánh giá và triển khai: chạy trên test độc lập, ghi test_metrics.json, tổng hợp 5 fold theo mean cộng trừ std, rồi Paired t-test; cuối cùng export sang ExecuTorch .pte và benchmark trên Pixel 6a.

Toàn bộ cấu hình bằng Hydra, chạy trên cụm UIT Slurm với GPU L40. Optimizer là AdamW với learning rate phân tầng, cosine annealing, tối đa 50 epoch, lưu checkpoint theo val pAUC.

**[CHUYỂN TIẾP]** Sau khi huấn luyện, việc đánh giá được tổ chức thành ba tầng.

---

## Slide 19 — Đánh giá 3 tầng & triển khai ⏱ 70s

**[LỜI NÓI]**
Việc đánh giá được tổ chức thành ba tầng độc lập.

Tầng một là in-domain, trên tập test của ISIC 2024 cộng PAD. Ở đây em tính đầy đủ pAUC, AUPRC, AUC-ROC, độ nhạy, độ đặc hiệu và F1. Ngưỡng quyết định chọn theo thống kê Youden's J.

Tầng hai là cross-domain, trên HAM10000 — ảnh dermoscopic hoàn toàn không tham gia huấn luyện — để kiểm tra khả năng tổng quát hóa sang miền ảnh khác.

Tầng ba là fairness, trên Fitzpatrick17k. Em chia theo nhóm sắc tố da: sáng, trung bình và tối, rồi đo khoảng cách hiệu năng lớn nhất giữa các nhóm, để xem mô hình có thiên vị theo màu da hay không — đây là vấn đề đạo đức quan trọng trong AI y tế.

Cuối cùng là phần triển khai: mô hình tốt nhất export sang .pte, đo trực tiếp trên Pixel 6a — độ trễ trung vị, đuôi p95, throughput và kích thước file — rồi vẽ đường Pareto giữa AUPRC và độ trễ để chỉ ra mô hình cân bằng tốt nhất.

**[CHUYỂN TIẾP]** *(Nếu dùng slide 19B:)* Để hình dung mô hình được dùng thực tế ra sao, em xin minh họa luồng suy luận trên điện thoại. *(Nếu bỏ 19B, chuyển thẳng:)* Vậy em đo bằng những độ đo nào, và bao nhiêu là "tốt"?

---

## Slide 19B (tùy chọn) — Luồng suy luận trên thiết bị ⏱ 55s

*(Slide dùng hình sẵn `figures/app_inference_slide.png`. Bỏ qua nếu cần rút giờ.)*

**[LỜI NÓI]**
Slide này minh họa mô hình được dùng thực tế thế nào. Toàn bộ chạy hoàn toàn offline trên máy: student tốt nhất được export ExecuTorch .pte, không cần cloud, nên bảo vệ riêng tư.

Luồng gồm: ảnh từ camera hoặc thư viện, qua một cổng kiểm tra chất lượng — kiểm mờ, kiểm độ sáng; rồi suy luận trên .pte cho ra xác suất ác tính; áp ngưỡng Youden's J; và đưa ra khuyến nghị. Điểm cần nhấn: ngưỡng quyết định không cố định ở 0,5 mà chọn theo Youden's J đã lưu cùng mỗi model, để cân bằng độ nhạy và độ đặc hiệu đúng như lúc đánh giá. Đầu ra hướng người dùng chỉ gồm hai mức: nguy cơ thấp thì tự theo dõi, nguy cơ cao thì đi khám bác sĩ sớm.

Em xin nói rõ để trung thực: đây là công cụ *sàng lọc*, không thay thế chẩn đoán. Và cổng kiểm tra chất lượng là bước phía ứng dụng dự kiến, còn phần suy luận .pte và ngưỡng Youden's J thì đã có trong pipeline.

**[CHUYỂN TIẾP]** Vậy em đo hiệu năng bằng những độ đo nào?

---

# PHẦN 6 — ĐỘ ĐO & KẾT QUẢ BƯỚC ĐẦU

## Slide 20 — Độ đo đánh giá: chọn gì, vì sao ⏱ 70s

**[LỜI NÓI]**
Trước khi vào kết quả, em xin làm rõ cách đọc các độ đo, vì ở mức mất cân bằng cực đoan này, chọn sai độ đo sẽ hiểu sai kết quả.

Chỉ số chính của em là AUPRC. Lý do: ở prevalence chỉ khoảng 0,4%, một baseline ngẫu nhiên chỉ đạt AUPRC bằng đúng prevalence, tức khoảng 0,004. Nên nếu mô hình đạt AUPRC trên 0,5 thì đã là rất mạnh — gấp hơn một trăm lần baseline. AUPRC nhạy với khả năng tìm đúng lớp hiếm, nên phản ánh đúng năng lực phát hiện ca ác tính.

Chỉ số ưu tiên thứ hai là pAUC ở TPR từ 80% — metric chính thức của ISIC 2024, đã chuẩn hóa về khoảng từ 0,02 ngẫu nhiên đến 0,20 hoàn hảo; trên 0,17 là rất tốt.

Kèm theo là độ nhạy — chỉ số an toàn lâm sàng quan trọng nhất, mong muốn từ 0,90 trở lên — và độ đặc hiệu để kiểm soát báo động giả.

Ngược lại, accuracy gần như vô nghĩa ở đây: đoán "tất cả lành tính" đã đạt accuracy 99,6%. Và AUC-ROC thì lạc quan, chỉ dùng kèm chứ không đứng một mình.

**[CHUYỂN TIẾP]** Với cách đọc đó, em xin trình bày kết quả bước đầu — và đây là phần em tâm đắc nhất.

---

## Slide 21 — Kết quả bước đầu (1): độ chính xác ⏱ 85s

**[LỜI NÓI]**
Đây là kết quả thật đã chạy 5-fold cross-validation trên tập test độc lập, báo cáo mean cộng trừ std.

Em xin bắt đầu bằng phát hiện ấn tượng nhất. Nhìn bảng teacher, chất lượng tăng dần từ EfficientNet-B4 với AUPRC 0,600, lên EfficientNetV2-M 0,649, ConvNeXtV2-Base 0,683, và MaxViT-Base 0,688. Xu hướng rõ: teacher càng hiện đại, AUPRC càng cao.

Bây giờ nhìn sang bảng student sau KD. Điểm đáng chú ý là: các student chỉ khoảng 4 đến 12 triệu tham số lại *vượt* teacher EfficientNet-B4 vốn 17,6 triệu tham số — ở cả AUPRC lẫn pAUC. Ví dụ EfficientFormerV2 đạt AUPRC 0,684, FastViT đạt pAUC 0,1908, MobileNetV4 đạt độ nhạy 0,962. Nghĩa là sự kết hợp giữa KD, kiến trúc mobile hiện đại và cách xử lý mất cân bằng đang hoạt động rất tốt.

Em xin lưu ý để trung thực: dòng EfficientFormerV2 hiện mới đủ 4 fold, em đã đánh dấu cảnh báo — con số sẽ được cập nhật khi đủ 5 fold. Và một điểm chung: pAUC của mọi student đều quanh 0,19, tức đã rất gần trần lý thuyết 0,20.

**[CHUYỂN TIẾP]** Nhưng độ chính xác cao chưa đủ. Câu hỏi thật sự là: KD đóng góp bao nhiêu, và chạy trên điện thoại thật ra sao?

---

## Slide 22 — Kết quả bước đầu (2): KD giúp gì & benchmark Pixel 6a ⏱ 90s

**[LỜI NÓI]**
Slide này trả lời hai câu hỏi cốt lõi, và em xin trình bày một cách trung thực nhất.

Thứ nhất, KD giúp gì? Có hai mức độ chắc chắn. KD cải thiện *nhất quán* pAUC và độ nhạy trên mọi cặp student với teacher — Delta luôn dương. Đây đúng là mục tiêu y tế "không bỏ sót". Nhưng với AUPRC thì có một sắc thái tinh tế: KD chỉ nâng AUPRC khi teacher đủ mạnh. Cụ thể, với teacher mạnh ConvNeXtV2, KD nâng AUPRC của MobileNetV4 thêm 0,052 — từ 0,609 lên 0,661. Còn với teacher yếu EfficientNet-B4, Delta AUPRC nằm trong khoảng nhiễu. Đây chính là bằng chứng bước đầu cho RQ2: teacher mạnh hơn *có* tạo student tốt hơn, ít nhất về AUPRC.

Thứ hai, chạy trên điện thoại thật ra sao? Em đã benchmark thật trên Pixel 6a. MobileNetV3 nhẹ nhất — 8,4 mili giây, 16 megabyte. MobileNetV4 22,6 mili giây. EfficientFormerV2 42,8 mili giây. Và FastViT chậm nhất — 65,5 mili giây.

Xin quý thầy cô chú ý một điều bất ngờ: FastViT chậm nhất *dù* có ít tham số hơn EfficientFormerV2. Tức thứ hạng độ trễ bị *đảo* trên mobile so với suy đoán từ số tham số hay FLOPs. Đây chính là lý do đề tài *bắt buộc* phải benchmark trên máy thật, không thể suy từ lý thuyết.

Từ đó, khuyến nghị triển khai của em là MobileNetV4 chưng cất từ ConvNeXtV2 — cân bằng tốt nhất: đủ 5 fold, độ nhạy 0,962, 22 mili giây, 32 megabyte, và cũng chính là case chứng minh KD mạnh nhất. Nếu ưu tiên nhẹ và nhanh tối đa thì chọn MobileNetV3.

**[CHUYỂN TIẾP]** Những kết quả này là output của các giai đoạn đầu trong kế hoạch. Em xin trình bày toàn bộ kế hoạch.

---

# PHẦN 7 — KẾ HOẠCH & KẾT LUẬN

## Slide 23 — Kế hoạch thực hiện ⏱ 55s

**[LỜI NÓI]**
Kế hoạch kéo dài từ tháng 6 đến tháng 11 năm 2026, gồm 8 giai đoạn, và em xin cập nhật trạng thái thật.

Giai đoạn 1 — pipeline và tiền xử lý — đã xong. Giai đoạn 2 — huấn luyện teacher — đã hoàn thành phần lớn. Giai đoạn 3 — huấn luyện student cả KD lẫn baseline — đang chạy để hoàn thiện ma trận. Giai đoạn 4 — export và benchmark Pixel 6a — đã xong 4 model, chính là các số quý thầy cô vừa thấy. Các giai đoạn còn lại: đánh giá chéo miền và fairness, tổng hợp 5-fold cùng Paired t-test, rồi viết và bảo vệ luận văn.

Em xin lưu ý các giai đoạn 2 và 3 phụ thuộc hàng đợi GPU của cụm dùng chung nên chạy gối nhau khi tài nguyên cho phép; phần viết luận văn cũng có thể bắt đầu song song với các chương không phụ thuộc kết quả.

**[CHUYỂN TIẾP]** Em xin tóm lại toàn bộ.

---

## Slide 24 — Kết luận & Cảm ơn ⏱ 55s

**[LỜI NÓI]**
Tóm lại, đề tài hướng tới lấp đồng thời ba khoảng trống: đánh giá KD một cách hệ thống trên nhiều paradigm kiến trúc; làm rõ vai trò của chất lượng teacher; và chứng minh khả năng chạy thực tế trên điện thoại.

Và khác với một đề cương thuần lý thuyết, kết quả bước đầu của em đã chứng minh được tính khả thi: student nhỏ sau KD đã vượt teacher yếu; KD cải thiện nhất quán pAUC và độ nhạy; và mô hình đã chạy thật trên Pixel 6a với độ trễ từ 8 đến 65 mili giây.

Về đóng góp, em kỳ vọng mang lại một bằng chứng thực nghiệm có hệ thống về tác động của KD, cùng một pipeline và báo cáo triển khai Android tái sử dụng được cho các bài toán ảnh y tế tương tự. Xa hơn, hướng này có thể hỗ trợ sàng lọc ung thư da thời gian thực, bảo vệ riêng tư, và đặc biệt phù hợp với những vùng thiếu nguồn lực y tế.

Phần trình bày của em đến đây là hết. Em xin chân thành cảm ơn quý thầy cô đã lắng nghe, và rất mong nhận được góp ý từ hội đồng ạ.

---

## Slide 25 — Tài liệu tham khảo (phụ lục, dự phòng)

**[LỜI NÓI]** *(Chỉ dùng khi hội đồng hỏi nguồn)*
Dạ, danh sách đầy đủ 22 tài liệu tham khảo có trong slide phụ lục ạ. Ở đây em trích những công trình nền tảng nhất — Esteva 2017, Hinton 2015 về KD, ISIC 2024, Focal Loss của Lin 2017, và các nghiên cứu KD da liễu gần đây như Islam 2024, Saha 2025.

---

## 📌 CHUẨN BỊ CHO PHẦN HỎI — ĐÁP (Q&A)

> Các câu hội đồng có khả năng hỏi cao. Vì bộ slide mới có KẾT QUẢ THẬT, hội đồng sẽ xoáy vào tính vững của số liệu — chuẩn bị kỹ Q7–Q11.

**Q1: Vì sao chọn AUPRC làm chỉ số chính thay vì Accuracy hay AUC-ROC?**
→ Vì prevalence chỉ ~0,39%. Ở mức mất cân bằng cực đoan này, một mô hình dự đoán "tất cả lành tính" đã đạt accuracy 99,6%, và AUC-ROC cũng bị lạc quan giả vì có quá nhiều mẫu âm. AUPRC tập trung vào lớp dương hiếm, so với baseline = prevalence (≈0,004), nên phản ánh đúng năng lực phát hiện ca ác tính. AUPRC ~0,66 tức gấp hơn 150 lần baseline.

**Q2: Vì sao không dùng lượng tử hóa (quantization) mà chỉ FP32?**
→ Đề tài giới hạn phạm vi ở FP32 để cô lập tác động của KD, tránh trộn thêm biến quantization vào so sánh. Quantization là hướng mở rộng tương lai. Đây là lựa chọn scope có chủ đích, không phải thiếu sót.

**Q3: Làm sao đảm bảo không rò rỉ dữ liệu giữa train và test?**
→ Ba lớp bảo vệ: (1) StratifiedGroupKFold nhóm theo patient_id; (2) tách held-out test ~17% patient-disjoint TRƯỚC khi chia fold; (3) gán tiền tố "pad_" khi ghép PAD để không trùng patient_id với ISIC.

**Q4: Vì sao chọn T=4 và α=0,3? Có tuning không?**
→ Đây là giá trị theo thông lệ trong các nghiên cứu KD (Hinton dùng T=2–4; α thiên về soft label khi teacher đáng tin). Vì trọng tâm đề tài là so sánh CÓ/KHÔNG KD trên nhiều kiến trúc chứ không phải tối ưu siêu tham số KD, em cố định để đảm bảo công bằng giữa các cặp.

**Q5: Nếu KD KHÔNG cải thiện thì sao — đề tài còn giá trị không?**
→ Vẫn có giá trị. Một kết quả "KD không giúp một cách nhất quán trên mọi paradigm" cũng là phát hiện khoa học có ý nghĩa, vì nó đính chính giả định phổ biến rằng KD luôn hiệu quả. Thiết kế đối chứng cho phép kết luận theo cả hai chiều. Thực tế kết quả bước đầu cho thấy KD cải thiện chắc chắn ở pAUC/Sens, còn AUPRC thì "có điều kiện" (cần teacher đủ mạnh) — bản thân sắc thái đó đã là một đóng góp.

**Q6: Vì sao dùng Pixel 6a mà không phải thiết bị khác?**
→ Pixel 6a là thiết bị Android tầm trung phổ biến, đại diện tốt cho chip ARM phổ thông (Cortex-A55/A76) — đúng đối tượng người dùng cộng đồng mà đề tài nhắm tới.

**Q7: ΔpAUC/ΔAUPRC bao nhiêu thì coi là "đáng kể"?**
→ Em dùng Paired t-test trên 5 fold với p<0,05 để khẳng định ý nghĩa thống kê, kết hợp báo cáo mean ± std để thể hiện cả độ lớn lẫn độ ổn định — không chỉ dựa vào một con số điểm.

**Q8 (MỚI — quan trọng): Kết quả EfficientFormerV2 mới 4 fold, có đáng tin không?**
→ Em đã đánh dấu rõ dòng đó bằng cảnh báo và nói rõ khi trình bày. Đây là kết quả *bước đầu* để chứng minh khả thi; con số sẽ được cập nhật khi đủ 5 fold. Các kết luận chính của em (student vượt teacher yếu, KD nâng pAUC/Sens nhất quán, latency đảo trên mobile) đều dựa trên các cặp đã đủ 5 fold, nên không phụ thuộc vào dòng 4 fold này.

**Q9 (MỚI): Vì sao student lại vượt được teacher? Nghe có vẻ vô lý.**
→ Student chỉ vượt teacher *yếu* (EfficientNet-B4), không vượt teacher mạnh nhất. Có ba lý do: (1) các student thế hệ mới (MobileNetV4/FastViT/EfficientFormerV2) tuy ít tham số nhưng kiến trúc hiện đại hơn B4; (2) chúng được distill từ teacher *mạnh hơn* chính B4 (ConvNeXtV2); (3) cách xử lý mất cân bằng (undersampling + Focal Loss) tối ưu trực tiếp cho AUPRC/pAUC. Đây không phải nghịch lý — mà đúng là điều KD hướng tới: nén tri thức của teacher tốt vào student nhỏ.

**Q10 (MỚI): Latency đảo trên mobile nghĩa là gì, vì sao quan trọng?**
→ Trên máy chủ/GPU, mô hình ít FLOPs thường nhanh hơn. Nhưng trên CPU ARM của điện thoại, FastViT (ít param hơn) lại chậm hơn EfficientFormerV2 vì các phép toán reparam/attention của nó không được tối ưu tốt trên phần cứng đó. Bài học: không thể suy độ trễ mobile từ số param/FLOPs — *phải đo on-device*. Đây chính là một đóng góp thực nghiệm của đề tài, và là lý do RQ3 (đo thật trên phone) là cần thiết chứ không thừa.

**Q11 (MỚI): Cross-domain (HAM10000) và fairness (Fitzpatrick17k) chưa có kết quả — điểm yếu?**
→ Đúng, hai phần này thuộc giai đoạn 5, hiện chưa chạy — em đã ghi rõ trạng thái "chưa" trong bảng kế hoạch. Pipeline đánh giá cho cả hai đã sẵn sàng (chỉ chạy inference hậu kỳ, không cần train lại). Đây là công việc còn lại của luận văn, và em ưu tiên hoàn thiện ma trận KD/baseline trước vì đó là đóng góp cốt lõi.
