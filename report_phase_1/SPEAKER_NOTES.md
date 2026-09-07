> ⛔ **SUPERSEDED — 2026-08-26. KHÔNG trích số từ file này.**
>
> Bản thay thế duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](../reports/BAO_CAO_TONG_HOP.md).
>
> Lý do: cùng phạm vi "chỉ 1 teacher" (22/08).

---

# KỊCH BẢN THUYẾT TRÌNH — BẢO VỆ ĐỀ CƯƠNG LUẬN VĂN

> **Cách dùng:** Mỗi mục tương ứng 1 slide trong [SLIDE_CONTENT.md](SLIDE_CONTENT.md) (bố cục **24 slide** + 2 slide bổ sung 19B/21B + phụ lục tài liệu tham khảo, cập nhật **2026-08-22**). Phần **[LỜI NÓI]** là kịch bản để nói theo (văn nói tự nhiên, KHÔNG đọc nguyên văn bullet trên slide). **[CHUYỂN TIẾP]** là câu nối sang slide sau. **⏱** là thời lượng gợi ý.
>
> **Tổng thời lượng mục tiêu: ~19 phút** (còn ~2–6 phút cho Q&A tùy quy định hội đồng). Nếu chỉ cho 15 phút: lướt nhanh slide 12 (dữ liệu bổ trợ), 14 (related work), bỏ hẳn 19B (tùy chọn). **Giữ 21B** — đó là kết quả ablation, một trong hai điểm mạnh nhất của buổi này.
>
> **Mẹo trình bày:**
> - Đừng đọc bullet — bullet để hội đồng đọc, bạn *kể* nội dung.
> - Xương sống để hội đồng nhớ: **3 vấn đề → 1 nút thắt → KD → 3 câu hỏi (RQ1/2/3) → kết quả bước đầu chứng minh khả thi.**
> - **Điểm nhấn lớn nhất của buổi này là PHẦN 6 (slide 20–22): đã có KẾT QUẢ THẬT, đủ 5 fold.** Đây là thứ khác biệt so với một đề cương thuần lý thuyết — hãy dành năng lượng và sự tự tin cho phần này.
> - **Nguyên tắc vàng khi đọc số: TRUNG THỰC.** Ba chỗ phải chủ động nói ra, đừng chờ bị hỏi: (1) ở **AUPRC** teacher vẫn hơn student; (2) **ΔAUPRC của KD nằm trong nhiễu**, bằng chứng KD nằm ở pAUC + độ nhạy; (3) **mới có ma trận KD của một teacher** nên chưa trả lời được "teacher nào chưng cất tốt nhất". Hội đồng đánh giá cao sự trung thực hơn là tô hồng — và cả ba điều này đều đã có trong kế hoạch để xử lý.

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

Về teacher, em có ba kiến trúc tiên tiến với chất lượng khác nhau: EfficientNetV2-M, ConvNeXtV2-Base, và MaxViT-Base — một kiến trúc lai CNN với Transformer.

Về student, em có bốn kiến trúc thế hệ mới, được tối ưu cho độ trễ trên thiết bị di động và trải nhiều paradigm thiết kế: MobileNetV4-Conv-Medium là CNN depthwise-separable, FastViT-SA12 dùng kỹ thuật reparameterization, EfficientFormerV2-S2 là lai attention với CNN, và RepViT-M1.0 là CNN nhưng mang thiết kế của Vision Transformer.

Em xin lưu ý ý đồ thiết kế: một dải teacher có chất lượng khác nhau nhân với một dải student đa paradigm, để quét được cả hai câu hỏi trong cùng một khung đối chứng — tổng cộng là ba nhân bốn, tức mười hai cặp chưng cất. Tất cả mô hình dùng chung một classification head, load backbone từ thư viện timm — các kiến trúc này yêu cầu timm phiên bản 1.0 trở lên — và teacher luôn được đóng băng khi distill.

**[CHUYỂN TIẾP]** Vậy việc chưng cất được thực hiện qua hàm mất mát như thế nào?

---

## Slide 16 — Hàm mất mát chưng cất ⏱ 70s

**[LỜI NÓI]**
Hàm mất mát KD của em gồm hai thành phần, theo nguyên lý Hinton nhưng có điều chỉnh cho bài toán mất cân bằng.

Thành phần thứ nhất là L_hard — tín hiệu từ nhãn cứng. Điểm khác biệt so với Hinton gốc: em không dùng cross-entropy thông thường, mà dùng Focal Loss với gamma bằng 2 và alpha bằng 0,25, để mô hình tập trung vào các mẫu ác tính hiếm và khó.

Thành phần thứ hai là L_soft — phần truyền dark knowledge từ teacher, tính bằng BCE giữa phân phối mềm của student và của teacher, với nhiệt độ T bằng 4.

Hai thành phần cân bằng bởi hệ số alpha bằng 0,3 — tức 30% cho nhãn cứng và 70% cho nhãn mềm, phản ánh việc em muốn student học nhiều từ teacher.

Một điểm quan trọng về thiết kế thí nghiệm: nhánh baseline được bật bằng đúng một cờ cấu hình. Khi cờ đó tắt KD, chương trình chuyển sang bộ huấn luyện thường với Focal Loss thuần và hoàn toàn không nạp teacher — tương đương alpha bằng 1,0. Nhờ vậy hai nhánh dùng chung một mã nguồn, cùng dữ liệu, cùng seed, cùng siêu tham số, chỉ khác hàm mất mát — đây là nền để đo Delta một cách sạch sẽ.

**[CHUYỂN TIẾP]** Và đây chính là điểm cốt lõi trong thiết kế thực nghiệm của em.

---

## Slide 17 — Thiết kế thực nghiệm so sánh đối chứng ⏱ 70s

**[LỜI NÓI]**
Điểm mấu chốt trong thiết kế là nguyên tắc ceteris paribus — "mọi thứ khác giữ nguyên". Mỗi student được huấn luyện song song theo hai nhánh, có KD và không KD, với cùng dữ liệu, cùng seed ngẫu nhiên, cùng siêu tham số và cùng quy trình đánh giá. Khác biệt duy nhất là hàm mất mát. Nhờ đó, mọi chênh lệch quan sát được đều quy về tác động của KD, không lẫn nhiễu.

Về quy mô, toàn bộ ma trận thực nghiệm là 110 lượt huấn luyện: 3 teacher nhân 5 fold là 15 lượt; thêm 15 lượt nữa cho nhánh ablation dữ liệu; 4 student baseline nhân 5 fold là 20 lượt; và 12 cặp teacher–student KD nhân 5 fold là 60 lượt. Hiện em đã chạy xong 70 trong số 110 lượt đó.

Hiệu quả KD được định lượng qua Delta pAUC và Delta AUPRC — lấy KD trừ baseline. Vì độ lệch chuẩn giữa các fold ở AUPRC lớn hơn phần lớn các Delta quan sát được, nguyên tắc của em là: Delta nào nhỏ hơn một độ lệch chuẩn thì mô tả là *nằm trong nhiễu*, không kết luận. Bước kiểm định chính thức bằng Paired t-test trên 5 fold với p nhỏ hơn 0,05 nằm trong kế hoạch — hiện em mới báo cáo mean cộng trừ std và so Delta với std.

**[CHUYỂN TIẾP]** Tiếp theo em xin trình bày phương pháp thực hiện cụ thể.

---

# PHẦN 5 — PHƯƠNG PHÁP THỰC HIỆN

## Slide 18 — Pipeline thực thi đầu–cuối ⏱ 75s

*(Slide dùng hình sẵn `figures/kd_pipeline_slide.png` — 3 bước. Chỉ vào hình khi nói.)*

**[LỜI NÓI]**
Toàn bộ quy trình từ dữ liệu thô đến mô hình trên điện thoại, em tóm tắt thành ba bước trên hình.

Bước một là chuẩn bị dữ liệu và huấn luyện teacher. Về dữ liệu, em chia hai giai đoạn: giai đoạn offline chạy một lần — giải mã ảnh, resize 224×224, lọc ảnh hỏng và trùng, chuẩn hóa nhãn, rồi tách tập test độc lập trước khi chia 5 fold; giai đoạn online trong lúc train dùng Albumentations để tăng cường — lật, xoay, dịch chuyển co giãn, jitter màu, CLAHE, làm mờ Gauss. Em cố ý không dùng MixUp, CutMix hay CutOut vì không phù hợp với vùng tổn thương tập trung. Teacher được train trước bằng Focal Loss thuần.

Bước hai là chưng cất KD: mỗi student train hai nhánh — nhánh KD dùng KDTrainer, nhánh baseline dùng Trainer thường — với sampler undersampling 1:5 mỗi epoch.

Bước ba là đánh giá và triển khai: chạy trên test độc lập, ghi lại toàn bộ metrics và cả file dự đoán từng ảnh — nhờ vậy mọi chỉ số đều tính lại được offline mà không cần chạy lại inference — rồi tổng hợp 5 fold theo mean cộng trừ std, và sau đó là kiểm định thống kê. Cuối cùng export sang ExecuTorch .pte và benchmark trên Pixel 6a.

Toàn bộ cấu hình bằng Hydra và khởi chạy qua một lớp script thống nhất — mỗi lệnh là một tiến trình chạy tuần tự cả 5 fold, log được ghi ra file nên mất kết nối SSH cũng không mất kết quả. Em chạy trên máy chủ GPU thuê ngoài, hai máy, mỗi máy một card RTX 3090. Optimizer là AdamW với learning rate phân tầng, cosine annealing có 3 epoch warmup, tối đa 50 epoch, dừng sớm theo val loss, và lưu checkpoint theo val pAUC.

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
Đây là kết quả thật, đã chạy đủ 5-fold cross-validation trên tập test độc lập, báo cáo mean cộng trừ std. Em xin nói trước về phạm vi: em chỉ dùng các run huấn luyện từ giữa tháng 7 trở đi, tức đợt đồng bộ với bộ mô hình hiện tại — các run cũ hơn em loại hết để không trộn hai thí nghiệm khác nhau.

Nhìn bảng teacher: MaxViT-Base đạt AUPRC 0,657, ConvNeXtV2-Base 0,651, EfficientNetV2-M 0,630. Em xin nói ngay cho chính xác: hai teacher đầu chênh nhau **trong một độ lệch chuẩn**, nên em *không* tuyên bố teacher nào mạnh nhất một cách tuyệt đối.

Bây giờ nhìn sang bảng student sau chưng cất. Đây là phát hiện chính: cả bốn student — dù nhẹ hơn teacher nhiều lần — đều đạt pAUC ở mức 0,183 đến 0,186, tức **ngang hoặc cao hơn cả ba teacher** vốn ở mức 0,182 đến 0,183; độ nhạy cũng tương đương. Nói cách khác, KD đã nén được đúng cái mà bài toán sàng lọc cần: năng lực ở vùng độ nhạy cao.

Em xin chủ động nói phần chưa đạt, để trung thực: ở chỉ số AUPRC thì teacher vẫn cao hơn student — 0,63 đến 0,66 so với 0,55 đến 0,62. Vì vậy em **không** phát biểu là "student vượt teacher"; phát biểu đúng là student đạt được vùng độ nhạy của teacher với chi phí tính toán nhỏ hơn nhiều lần.

**[CHUYỂN TIẾP]** Trước khi nói KD đóng góp bao nhiêu, em xin trình bày một thí nghiệm đối chứng về dữ liệu.

---

## Slide 21B — Ablation dữ liệu: PAD-UFES-20 có thực sự giúp không? ⏱ 60s

**[LỜI NÓI]**
Ở phần dữ liệu em có nói là trộn thêm PAD-UFES-20 để mô hình bền vững hơn với ảnh chụp điện thoại. Nhưng nói vậy chỉ là giả định, nên em đã chạy một thí nghiệm đối chứng để kiểm chứng.

Cách làm: em huấn luyện mỗi teacher theo hai nhánh với cấu hình y hệt nhau, chỉ khác tập huấn luyện — một nhánh có PAD, một nhánh chỉ ISIC — rồi đánh giá cả hai trên **cùng một tập test**. Em làm cho cả ba teacher, mỗi nhánh 5 fold, tổng cộng 30 lượt huấn luyện.

Ô so sánh quyết định là phần ảnh PAD trong tập test, tức đúng miền ảnh lâm sàng mà nhánh ISIC-only chưa từng nhìn thấy. Kết quả: cả ba teacher đều tốt lên rõ rệt — AUPRC tăng từ 0,092 đến 0,131, và độ nhạy ở mức đặc hiệu 95% tăng tới 0,23 với MaxViT. Trong khi đó trên miền ISIC gốc thì chênh lệch nằm trong nhiễu, tức việc thêm PAD **không làm hại** miền dermoscopy ban đầu.

Điều em muốn nhấn: kết quả nhất quán trên cả ba kiến trúc teacher, nên đây không phải may mắn của một mô hình. Đây là bằng chứng định lượng cho một lựa chọn thiết kế dữ liệu.

**[CHUYỂN TIẾP]** Còn bản thân kỹ thuật chưng cất thì đóng góp bao nhiêu, và mô hình chạy trên điện thoại thật ra sao?

---

## Slide 22 — Kết quả bước đầu (2): KD giúp gì & benchmark Pixel 6a ⏱ 90s

**[LỜI NÓI]**
Slide này trả lời hai câu hỏi cốt lõi, và em xin trình bày một cách trung thực nhất.

Thứ nhất, KD giúp gì? Kết quả của em có hai mức độ chắc chắn khác nhau, và em xin nói rõ cả hai.

Chỗ chắc chắn: với teacher EfficientNetV2-M, KD cải thiện *nhất quán* trên **cả bốn trên bốn** student ở pAUC, ở AUC, ở độ nhạy, và ở độ nhạy tại mức đặc hiệu 95%. Delta luôn dương, không có ngoại lệ. Đây đúng là mục tiêu y tế "không bỏ sót". Đáng chú ý là student yếu nhất — RepViT — lại hưởng lợi nhiều nhất, pAUC tăng 0,0115 và độ nhạy tại 95% đặc hiệu tăng 0,032.

Chỗ chưa chắc chắn, em xin nói thẳng: với AUPRC thì kết quả hỗn hợp — hai student dương, hai student âm nhẹ. Nhưng cả bốn Delta đều **nhỏ hơn một độ lệch chuẩn**, nên cách đọc đúng là "nằm trong nhiễu", chứ không phải "KD làm hại". Kết luận của em vì thế là: bằng chứng về giá trị của KD nằm ở pAUC và độ nhạy, không phải ở AUPRC — và em nêu đúng như vậy chứ không chọn lọc con số có lợi.

Em cũng xin nói rõ một giới hạn: hiện em mới hoàn tất ma trận chưng cất cho **một** teacher. Hai teacher còn lại đang chạy, nên câu hỏi "teacher nào chưng cất tốt nhất" em chưa trả lời được — đó là công việc còn lại và đã nằm trong kế hoạch.

Thứ hai, chạy trên điện thoại thật ra sao? Em đã benchmark thật trên Pixel 6a. MobileNetV4 22,6 mili giây, file 32 megabyte. EfficientFormerV2 42,8 mili giây, 47 megabyte. Và FastViT chậm nhất — 65,5 mili giây.

Xin quý thầy cô chú ý một điều bất ngờ: FastViT chậm nhất *dù* có ít tham số hơn EfficientFormerV2. Tức thứ hạng độ trễ không đi theo số tham số hay FLOPs. Hệ quả thực tế là FastViT bị lấn át hoàn toàn — chậm hơn một phẩy năm lần mà độ chính xác thì ngang. Đây chính là lý do đề tài *bắt buộc* phải benchmark trên máy thật, không thể suy từ lý thuyết.

Từ đó, khuyến nghị triển khai của em là MobileNetV4-Conv-Medium chưng cất từ EfficientNetV2-M. Nó thắng ở cả hai trục cùng lúc: vừa nhanh nhất và nhẹ nhất trong các model đã đo, vừa dẫn đầu pAUC, AUC và độ nhạy trong toàn bộ nhóm student.

**[CHUYỂN TIẾP]** Những kết quả này là output của các giai đoạn đầu trong kế hoạch. Em xin trình bày toàn bộ kế hoạch.

---

# PHẦN 7 — KẾ HOẠCH & KẾT LUẬN

## Slide 23 — Kế hoạch thực hiện ⏱ 55s

**[LỜI NÓI]**
Kế hoạch kéo dài từ tháng 6 đến tháng 11 năm 2026, gồm 10 giai đoạn, và em xin cập nhật trạng thái thật.

Giai đoạn 1 — pipeline và tiền xử lý — đã xong. Giai đoạn 2 — huấn luyện ba teacher, 15 lượt — đã xong. Giai đoạn 3 — ablation dữ liệu, 15 lượt — đã xong, chính là slide 21B. Giai đoạn 4 — bốn student nhánh baseline, 20 lượt — đã xong. Giai đoạn 5 — ma trận chưng cất — đang chạy, hiện được 20 trên 60 lượt. Giai đoạn 6 — export và benchmark trên Pixel 6a — đã đo được ba kiến trúc, chính là các số quý thầy cô vừa thấy. Tổng cộng em đã chạy xong 70 trên 110 lượt huấn luyện.

Các giai đoạn còn lại: đánh giá chéo miền và fairness, tổng hợp 5-fold cùng kiểm định thống kê và hiệu chuẩn xác suất, rồi viết và bảo vệ luận văn.

Em xin lưu ý các giai đoạn huấn luyện phụ thuộc tài nguyên GPU thuê ngoài nên chạy gối nhau khi tài nguyên cho phép; phần viết luận văn cũng có thể bắt đầu song song với các chương không phụ thuộc kết quả. Đường găng hiện tại là giai đoạn 5.

**[CHUYỂN TIẾP]** Em xin tóm lại toàn bộ.

---

## Slide 24 — Kết luận & Cảm ơn ⏱ 55s

**[LỜI NÓI]**
Tóm lại, đề tài hướng tới lấp đồng thời ba khoảng trống: đánh giá KD một cách hệ thống trên nhiều paradigm kiến trúc; làm rõ vai trò của chất lượng teacher; và chứng minh khả năng chạy thực tế trên điện thoại.

Và khác với một đề cương thuần lý thuyết, kết quả bước đầu của em đã chứng minh được tính khả thi trên ba mặt: thứ nhất, chưng cất tri thức cải thiện nhất quán cả bốn trên bốn student ở pAUC và độ nhạy, giúp student nhỏ đạt được vùng độ nhạy của teacher; thứ hai, thí nghiệm ablation chứng minh việc trộn dữ liệu ảnh smartphone lâm sàng giúp cả ba trên ba teacher mà không hại miền gốc; thứ ba, mô hình đã chạy thật trên Pixel 6a với độ trễ từ 22 đến 65 mili giây.

Phần còn lại em xin nói rõ: hoàn tất ma trận chưng cất cho hai teacher còn lại, đánh giá chéo miền và công bằng, cùng kiểm định thống kê — tất cả đều đã có trong kế hoạch.

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
→ Vì prevalence chỉ ~0,39%. Ở mức mất cân bằng cực đoan này, một mô hình dự đoán "tất cả lành tính" đã đạt accuracy 99,6%, và AUC-ROC cũng bị lạc quan giả vì có quá nhiều mẫu âm. AUPRC tập trung vào lớp dương hiếm, so với baseline = prevalence (≈0,0039), nên phản ánh đúng năng lực phát hiện ca ác tính. AUPRC 0,62 của student tức gấp khoảng 160 lần baseline ngẫu nhiên.

**Q2: Vì sao không dùng lượng tử hóa (quantization) mà chỉ FP32?**
→ Đề tài giới hạn phạm vi ở FP32 để cô lập tác động của KD, tránh trộn thêm biến quantization vào so sánh. Quantization là hướng mở rộng tương lai. Đây là lựa chọn scope có chủ đích, không phải thiếu sót.

**Q3: Làm sao đảm bảo không rò rỉ dữ liệu giữa train và test?**
→ Ba lớp bảo vệ: (1) StratifiedGroupKFold nhóm theo patient_id; (2) tách held-out test ~17% patient-disjoint TRƯỚC khi chia fold; (3) gán tiền tố "pad_" khi ghép PAD để không trùng patient_id với ISIC.

**Q4: Vì sao chọn T=4 và α=0,3? Có tuning không?**
→ Đây là giá trị theo thông lệ trong các nghiên cứu KD (Hinton dùng T=2–4; α thiên về soft label khi teacher đáng tin). Vì trọng tâm đề tài là so sánh CÓ/KHÔNG KD trên nhiều kiến trúc chứ không phải tối ưu siêu tham số KD, em cố định để đảm bảo công bằng giữa các cặp.

**Q5: Nếu KD KHÔNG cải thiện thì sao — đề tài còn giá trị không?**
→ Vẫn có giá trị. Một kết quả "KD không giúp một cách nhất quán trên mọi paradigm" cũng là phát hiện khoa học có ý nghĩa, vì nó đính chính giả định phổ biến rằng KD luôn hiệu quả. Thiết kế đối chứng cho phép kết luận theo cả hai chiều. Thực tế kết quả bước đầu cho thấy KD cải thiện chắc chắn ở pAUC/Sens (4/4 student), còn ở AUPRC thì Δ nằm trong nhiễu — chính sự phân tách "giúp ở đâu, không giúp ở đâu" đó đã là một đóng góp, vì nó nói cho người triển khai biết nên kỳ vọng gì ở KD.

**Q6: Vì sao dùng Pixel 6a mà không phải thiết bị khác?**
→ Pixel 6a là thiết bị Android tầm trung phổ biến, đại diện tốt cho chip ARM phổ thông (Cortex-A55/A76) — đúng đối tượng người dùng cộng đồng mà đề tài nhắm tới.

**Q7: ΔpAUC/ΔAUPRC bao nhiêu thì coi là "đáng kể"?**
→ Nguyên tắc hiện tại của em: so Δ với độ lệch chuẩn giữa 5 fold — Δ nhỏ hơn 1 std thì mô tả là "trong nhiễu" và không kết luận. Đó là lý do em khẳng định KD ở pAUC/Sens (Δ dương 4/4, ổn định) nhưng *không* khẳng định ở AUPRC (std 0,015–0,053, lớn hơn mọi Δ). Bước tiếp theo trong kế hoạch là Paired t-test trên 5 fold với p<0,05 để có kết luận thống kê chính thức.

**Q8 (MỚI): Vì sao mới có ma trận KD của một teacher? Như vậy có đủ để kết luận không?**
→ Đủ cho câu hỏi "KD có giúp không", vì với teacher EfficientNetV2-M em có **ma trận đầy đủ 4/4 student × 5 fold**, tức một thí nghiệm đối chứng hoàn chỉnh. Nhưng **không** đủ cho câu hỏi "teacher nào chưng cất tốt nhất" — cái đó cần ít nhất hai teacher, và em nói rõ là chưa trả lời được. Em có kết quả của hai teacher còn lại từ đợt huấn luyện trước, nhưng đã **chủ động loại** vì chúng chưng cất từ bản teacher cũ, trộn vào sẽ so sánh hai thí nghiệm khác nhau. Em chọn báo cáo thiếu còn hơn báo cáo sai.

**Q9 (MỚI): Student có vượt được teacher không?**
→ Tùy chỉ số, và em xin trả lời chính xác. Ở **pAUC@TPR≥80% và độ nhạy** thì có — cả 4 student sau KD đều ngang hoặc hơn cả 3 teacher, dù nhẹ hơn nhiều lần. Ở **AUPRC** thì không — teacher vẫn cao hơn (0,63–0,66 so với 0,55–0,62). Lý do student làm tốt ở vùng độ nhạy cao: (1) kiến trúc student thế hệ mới rất hiệu quả trên cùng ngân sách tính toán; (2) tín hiệu mềm của teacher làm mượt biên quyết định, có lợi nhất đúng ở vùng lớp hiếm; (3) cách xử lý mất cân bằng (undersampling + Focal Loss) tối ưu trực tiếp cho vùng độ nhạy cao. Đây đúng là điều KD hướng tới: nén tri thức của teacher vào student nhỏ ở đúng vùng vận hành mà bài toán cần.

**Q10 (MỚI): Latency đảo trên mobile nghĩa là gì, vì sao quan trọng?**
→ Trên máy chủ/GPU, mô hình ít FLOPs thường nhanh hơn. Nhưng trên CPU ARM của điện thoại, FastViT (ít param hơn) lại chậm hơn EfficientFormerV2 vì các phép toán reparam/attention của nó không được tối ưu tốt trên phần cứng đó. Bài học: không thể suy độ trễ mobile từ số param/FLOPs — *phải đo on-device*. Đây chính là một đóng góp thực nghiệm của đề tài, và là lý do RQ3 (đo thật trên phone) là cần thiết chứ không thừa.

**Q11 (MỚI): Cross-domain (HAM10000) và fairness (Fitzpatrick17k) chưa có kết quả — điểm yếu?**
→ Đúng, hai phần này thuộc giai đoạn 7, hiện chưa chạy — em đã ghi rõ trạng thái "chưa" trong bảng kế hoạch. Tầng chuẩn bị dữ liệu cho cả hai đã code xong, gồm cả bước kiểm tra rò rỉ tự động dừng chương trình nếu có ảnh trùng với tập nội bộ; phần còn lại chỉ là chạy inference hậu kỳ, không cần train lại. Em ưu tiên hoàn thiện ma trận KD/baseline trước vì đó là đóng góp cốt lõi. Một lưu ý kỹ thuật em đã lường trước: Fitzpatrick17k chỉ phát hành URL chứ không phát hành ảnh, nên tỉ lệ tải về thành công là một biến chưa kiểm soát được.

**Q12 (MỚI): Sao biết trộn PAD-UFES-20 là có lợi, mà không phải chỉ làm nhiễu dữ liệu?**
→ Em không giả định mà đã chạy ablation đối chứng: mỗi teacher hai nhánh, cấu hình y hệt, chỉ khác tập huấn luyện, đánh giá trên cùng một tập test. Kết quả trên subset ảnh PAD: AUPRC tăng 0,092–0,131 cho **cả ba** teacher, và trên miền ISIC gốc thì chênh lệch nằm trong nhiễu, tức không hại. Vì nhất quán trên cả ba kiến trúc nên đây không phải may mắn của một mô hình.

**Q13 (MỚI): Xác suất mô hình đưa ra có tin được không, khi huấn luyện có undersampling?**
→ Câu hỏi rất đúng chỗ. Bộ lấy mẫu dạy mô hình theo tỉ lệ ác tính khoảng 16,7%, trong khi thực tế chỉ 0,39%, nên xác suất `sigmoid` thô **lệch cao có hệ thống** — em có đo bằng Brier score và ECE. Điểm quan trọng: điều này **không ảnh hưởng** mọi kết quả xếp hạng em vừa trình bày, vì pAUC, AUPRC và AUC đều bất biến với biến đổi đơn điệu. Nó chỉ ảnh hưởng con số phần trăm hiển thị cho người dùng, và em xử lý bằng một bước hiệu chuẩn hậu kỳ dựa trên tập validation.
