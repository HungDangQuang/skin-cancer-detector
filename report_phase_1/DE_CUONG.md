# ĐỀ CƯƠNG LUẬN VĂN THẠC SĨ

**Tên đề tài (tiếng Việt):** PHÁT HIỆN UNG THƯ DA TRÊN THIẾT BỊ BIÊN SỬ DỤNG MÔ HÌNH HỌC SÂU KẾT HỢP CHƯNG CẤT TRI THỨC

**Tên đề tài (tiếng Anh):** KNOWLEDGE-DISTILLED DEEP LEARNING MODELS FOR SKIN CANCER DETECTION ON EDGE DEVICES

**Học viên:** Đặng Quang Hưng · MSHV: 230101006 · Khóa 18 · Đợt 1

**Người hướng dẫn khoa học:** TS. Nguyễn Thanh Bình · binhnt@uit.edu.vn

*Cập nhật: 29/08/2026 — bản hoàn chỉnh. Đồng bộ với 140/140 fold-run, cả hai ablation dữ liệu, khoảng tin cậy paired bootstrap trên cả ba miền, benchmark tĩnh 7/7 mô hình và benchmark on-device Pixel 6a (parity + latency + bộ nhớ). Toàn văn luận văn: [`thesis/LUAN_VAN.md`](../thesis/LUAN_VAN.md); nguồn số liệu duy nhất: [`reports/BAO_CAO_TONG_HOP.md`](../reports/BAO_CAO_TONG_HOP.md).*

---

## 1. NỘI DUNG

### a. Giới thiệu về đề tài

Ung thư da là một trong những loại ung thư phổ biến nhất trên toàn cầu. Theo dữ liệu GLOBOCAN 2022, ước tính có khoảng 331.722 ca mắc mới ung thư hắc tố (Melanoma) và gần 58.667 ca tử vong trong năm 2022 [1]. Mặc dù Melanoma chỉ chiếm khoảng 10% tổng số ca ung thư da, nó lại gây ra tới 80% số ca tử vong liên quan [2]. Tuy nhiên, tiên lượng sống sót sau 5 năm có thể đạt tới 99% nếu bệnh được phát hiện ở giai đoạn khu trú [3], nhấn mạnh tầm quan trọng sống còn của việc chẩn đoán sớm.

Các phương pháp chẩn đoán lâm sàng truyền thống chủ yếu dựa vào kinh nghiệm của bác sĩ da liễu thông qua kỹ thuật soi da (dermoscopy) và quy tắc nhận diện ABCD [4]. Sự thiếu hụt chuyên gia da liễu tại các khu vực hạn chế nguồn lực y tế, cùng với chi phí thăm khám cao, đã thúc đẩy nhu cầu cấp thiết về các hệ thống hỗ trợ chẩn đoán tự động (Computer-Aided Diagnosis — CAD). Sự phát triển của Học sâu, đặc biệt là Mạng nơ-ron tích chập (CNN), đã chứng minh khả năng đạt độ chính xác ngang tầm hoặc vượt trội so với bác sĩ da liễu trong phân loại tổn thương da [5]. Các kiến trúc như EfficientNet [6] và Vision Transformer [7] liên tục cải thiện hiệu năng trên các tập dữ liệu chuẩn ISIC. Tuy nhiên, phần lớn các mô hình đạt hiệu suất cao có kích thước lớn và thường được triển khai trên nền tảng đám mây, đặt ra các rào cản đáng kể về độ trễ, yêu cầu kết nối internet ổn định, và đặc biệt là nguy cơ về bảo mật dữ liệu y tế riêng tư [8]. Xu hướng chuyển dịch xử lý AI trực tiếp xuống thiết bị biên (Edge AI) vì thế đang trở thành hướng đi tất yếu, cho phép sàng lọc thời gian thực và bảo vệ quyền riêng tư người dùng [9].

Thách thức cốt lõi của Edge AI trong lĩnh vực y tế nằm ở sự đánh đổi giữa độ chính xác và hiệu năng tính toán. Các mô hình gọn nhẹ như EfficientNet-B0 [6], MobileNetV3 [10] hay MobileViT [11] được tối ưu cho thiết bị di động nhưng thường phải chấp nhận mức suy giảm đáng kể về độ chính xác. Trong bối cảnh bài toán y tế, việc bỏ sót một ca ác tính có thể dẫn đến hậu quả nghiêm trọng, đặt ra yêu cầu khắt khe về độ nhạy — được phản ánh qua chỉ số **pAUC@TPR≥80%** mà cuộc thi ISIC 2024 áp dụng làm thước đo chính thức [12].

**Chưng cất tri thức (Knowledge Distillation — KD)** là kỹ thuật đầy hứa hẹn để thu hẹp khoảng cách này: sử dụng một mô hình giáo viên (teacher) lớn, chính xác cao để hướng dẫn quá trình học của mô hình học sinh (student) gọn nhẹ thông qua các nhãn mềm (soft labels), cho phép mô hình nhỏ tiếp thu các biểu diễn đặc trưng tinh vi mà việc huấn luyện trực tiếp khó đạt được [13]. Tuy nhiên, hầu hết các nghiên cứu hiện tại chỉ khảo sát một cặp teacher–student duy nhất và chưa đánh giá hệ thống ảnh hưởng của KD trên nhiều kiến trúc thuộc các paradigm thiết kế khác nhau — đặc biệt trên tập dữ liệu ISIC 2024 với ảnh non-dermoscopic gần giống ảnh chụp smartphone [12].

Để giải quyết khoảng trống này, đề tài đặt ra câu hỏi nghiên cứu trung tâm: *"Liệu phương pháp chưng cất tri thức có thực sự mang lại cải thiện đáng kể và nhất quán về hiệu năng cho các mô hình lightweight thuộc nhiều paradigm thiết kế khác nhau, và chất lượng của teacher có ảnh hưởng như thế nào đến hiệu quả KD trên student?"* Để trả lời, đề tài thiết kế một thực nghiệm so sánh đối chứng kiểm soát (controlled comparative experiment) trong đó mỗi kiến trúc student được huấn luyện song song theo hai điều kiện — có KD và không KD — với cùng dữ liệu, cùng siêu tham số, cùng quy trình đánh giá. Sự chênh lệch hiệu năng định lượng qua **ΔpAUC** và **ΔAUPRC** chính là đóng góp khoa học cốt lõi của đề tài.

### b. Mục tiêu của đề tài

Đề tài đặt ra mục tiêu tổng quát là nghiên cứu và đánh giá một cách có hệ thống hiệu quả của phương pháp chưng cất tri thức trong việc cải thiện hiệu năng phân loại ung thư da của các mô hình học sâu nhỏ gọn, đồng thời kiểm chứng tính khả thi triển khai của các mô hình này trên thiết bị biên Android. Để đạt được mục tiêu đó, luận văn được tổ chức theo ba nhóm mục tiêu cụ thể có quan hệ tuần tự.

Nhóm mục tiêu thứ nhất tập trung vào xây dựng nền tảng dữ liệu và pipeline thực nghiệm. Đề tài khai thác bộ dữ liệu ISIC 2024 SLICE-3D (ảnh non-dermoscopic gần với ảnh chụp smartphone trong điều kiện thực tế) kết hợp PAD-UFES-20 [16] để bổ sung mẫu ác tính, qua đó cải thiện prevalence từ ~0,1% lên ~0,39%. Quy trình phân chia dữ liệu được thiết kế theo nguyên tắc patient-disjoint stratified 5-fold cross-validation nhằm ngăn chặn rò rỉ dữ liệu và đảm bảo tính tái lập của kết quả.

Nhóm mục tiêu thứ hai là phần trọng tâm của luận văn: huấn luyện và so sánh đối chứng trên một ma trận teacher × student. Phía teacher gồm ba kiến trúc tiên tiến với chất lượng khác nhau (EfficientNetV2-M, ConvNeXtV2-Base, MaxViT-Base); phía student gồm bốn kiến trúc được tối ưu cho độ trễ trên thiết bị di động, trải nhiều paradigm thiết kế (MobileNetV4-Conv-Medium — depthwise-separable CNN; FastViT-SA12 — CNN + reparameterization; EfficientFormerV2-S2 — attention–CNN hybrid; RepViT-M1.0 — CNN mang thiết kế ViT). Mỗi kiến trúc student được huấn luyện song song theo hai điều kiện hoàn toàn kiểm soát — có KD và không có KD — nhằm tách biệt tác động của phương pháp chưng cất khỏi các yếu tố nhiễu. Bên cạnh đó, đề tài phân tích tương quan giữa chất lượng teacher (AUPRC teacher) và mức độ cải thiện của student (ΔAUPRC), một câu hỏi nghiên cứu bổ sung có giá trị hướng dẫn thiết kế thực nghiệm KD trong tương lai. Một mục tiêu phụ nhưng cần thiết là **ablation dữ liệu**: chứng minh bằng thực nghiệm rằng việc trộn PAD-UFES-20 vào tập huấn luyện thực sự cải thiện mô hình, thay vì chỉ giả định.

Nhóm mục tiêu thứ ba bao gồm kiểm chứng khả năng tổng quát hóa và tính công bằng của mô hình, cùng với đo lường hiệu năng triển khai thực tế. Cụ thể, đề tài thực hiện kiểm chứng chéo miền trên HAM10000 [17] (ảnh dermoscopic lâm sàng) và phân tích công bằng trên Fitzpatrick17k [18] (phân nhóm theo thang sắc tố da Fitzpatrick I–VI); đồng thời, mô hình tốt nhất được export sang định dạng ExecuTorch .pte và đo hiệu năng thực tế trên thiết bị Pixel 6a. Thành công của nhóm mục tiêu này không chỉ hoàn chỉnh đánh giá khoa học mà còn xác lập tính khả thi thực tiễn của hướng tiếp cận được đề xuất.

Qua ba nhóm mục tiêu trên, luận văn kỳ vọng đóng góp trên hai phương diện: đóng góp khoa học là bằng chứng thực nghiệm có hệ thống về tác động của chất lượng teacher đến hiệu quả KD trên nhiều paradigm kiến trúc student; đóng góp kỹ thuật là quy trình đầy đủ từ huấn luyện đến triển khai Android, tái sử dụng được cho các bài toán phân loại ảnh y tế tương tự.

### c. Nội dung nghiên cứu của đề tài

#### 1. Xây dựng bài toán

Bài toán phát hiện ung thư da được đặt trong khung phân loại nhị phân: nhận ảnh tổn thương da kích thước 224×224 pixel làm đầu vào và cho ra một logit duy nhất, áp `sigmoid` tại suy luận để thu được xác suất ác tính. Ánh xạ nhãn tuân theo quy ước lâm sàng tiêu chuẩn: melanoma, BCC và SCC được gán nhãn ác tính (1), trong khi nevus, keratosis và các tổn thương lành tính khác được gán nhãn lành tính (0).

Đề tài sử dụng bốn bộ dữ liệu với vai trò phân biệt rõ ràng, được tổng hợp trong bảng sau:

| Bộ dữ liệu | Số ảnh | Loại ảnh | Nhãn → nhị phân | Vai trò |
|---|---|---|---|---|
| ISIC 2024 SLICE-3D [12] | 401.059 | Non-dermoscopic (TBP crop) | Nhị phân sẵn | Huấn luyện chính + test nội bộ |
| PAD-UFES-20 [16] | 2.298 | Lâm sàng, smartphone | 6 lớp → nhị phân | Bổ sung mẫu ác tính |
| HAM10000 [17] | 10.015 | Dermoscopic | 7 lớp → nhị phân | Kiểm chứng chéo miền |
| Fitzpatrick17k [18] | 16.577 | Lâm sàng | 114 bệnh + thang da I–VI | Phân tích công bằng |

*(Số ảnh là con số công bố của từng bộ dữ liệu. Với hai bộ đánh giá ngoài, số ảnh thực dùng sẽ nhỏ hơn: Fitzpatrick17k **chỉ phát hành danh sách URL chứ không phát hành ảnh**, phải tải về rồi kiểm tra toàn vẹn trước; và cả hai bộ đều đi qua bộ lọc hai tầng mô tả ở mục d.)*

Thách thức đặc trưng nhất của bài toán là mất cân bằng lớp cực đoan: ISIC 2024 chỉ chứa khoảng 0,1% mẫu ác tính (tỷ lệ 1:1000), và sau khi gộp PAD-UFES-20, prevalence tăng lên khoảng 0,39%. Ở mức prevalence thấp như vậy, AUC-ROC có xu hướng lạc quan giả (optimistic bias), vì thế **AUPRC được chọn làm chỉ số chính** và **pAUC@TPR≥80%** (metric chính thức ISIC 2024) là chỉ số ưu tiên thứ hai — phản ánh yêu cầu không bỏ sót ca ác tính trong sàng lọc lâm sàng. Để xử lý mất cân bằng, đề tài kết hợp dynamic undersampling (tỷ lệ 1:5 mỗi epoch) và Focal Loss (γ=2, α=0,25) [28]. Thách thức thứ hai là ngăn chặn rò rỉ dữ liệu: toàn bộ tổn thương của một bệnh nhân phải nằm trong cùng một fold, do đó `StratifiedGroupKFold(K=5)` được áp dụng sau khi đã tách held-out test set (~17%) độc lập từ trước. Khi ghép PAD-UFES-20, `patient_id` được gán tiền tố `pad_` để tránh xung đột với ISIC. Thách thức thứ ba là yêu cầu triển khai biên: mô hình cuối cùng phải đủ nhỏ và nhanh để chạy thời gian thực trên thiết bị Android phổ thông, đặt ra ràng buộc cứng về tham số, FLOPs và latency.

Quy trình xử lý dữ liệu gồm hai giai đoạn: tiền xử lý *offline* (giải mã ảnh, resize 224×224, lọc ảnh hỏng và trùng lặp, chuẩn hóa nhãn) và tăng cường *online* trong huấn luyện bằng Albumentations (lật ngang/dọc, xoay 90°, ShiftScaleRotate, jitter màu sắc, CLAHE, làm mờ Gauss). MixUp, CutMix và CutOut không được sử dụng vì không phù hợp với bài toán có vùng tổn thương tập trung.

#### 2. Các nghiên cứu liên quan

Để hiểu vì sao đề tài này được đặt ra, cần nhìn lại quá trình phát triển của lĩnh vực theo trục thời gian — từ chỗ học sâu chỉ là thí nghiệm trong phòng lab, qua giai đoạn mô hình ngày càng mạnh nhưng ngày càng nặng, đến điểm hiện tại khi áp lực triển khai biên buộc cộng đồng nghiên cứu phải tìm lời giải mới.

**Giai đoạn đặt nền móng (2015–2019).** Trước năm 2017, ứng dụng học sâu trong da liễu vẫn còn rất hạn chế. Bước ngoặt đến từ công trình của Esteva và cộng sự (2017), lần đầu tiên chứng minh rằng một mạng CNN thuần — không cần đặc trưng thủ công — có thể phân loại ung thư da đạt độ chính xác ngang tầm bác sĩ chuyên khoa chỉ với dữ liệu ảnh [5]. Kết quả này mở ra niềm tin rằng học sâu có thể trở thành công cụ CAD thực tiễn. Cũng trong giai đoạn này, Hinton et al. (2015) đề xuất kỹ thuật chưng cất tri thức (KD) như một phương pháp nén mô hình: thay vì học từ nhãn cứng 0/1, student được huấn luyện để khớp với phân phối xác suất "mềm" của teacher — phân phối này mang theo thông tin về mức độ tương đồng giữa các lớp mà nhãn cứng bỏ qua [13] — một kỹ thuật mà Gou et al. (2021) sau này hệ thống hóa thành một lĩnh vực nghiên cứu đầy đủ [25]. Dù được công bố sớm, ý tưởng này lúc đó chưa được cộng đồng da liễu chú ý. Cùng năm 2019, hai kiến trúc gọn nhẹ quan trọng ra đời: EfficientNet (Tan & Le) với chiến lược co giãn đồng hợp cân bằng chiều sâu, chiều rộng và độ phân giải [6], và MobileNetV3 (Howard et al.) với depthwise separable convolution tối ưu qua NAS [10] — cả hai đặt nền tảng cho dòng mô hình edge AI sau này.

**Giai đoạn mô hình lớn thống trị (2020–2021).** Bước vào thập niên 2020, áp lực cạnh tranh trên các bảng xếp hạng ISIC đẩy các nhóm nghiên cứu theo hướng xây dựng mô hình ngày càng lớn hơn. Tại ISIC 2020, các giải pháp hàng đầu đều dựa trên ensemble EfficientNet nhiều tầng [19] — hiệu năng rất cao, nhưng không một hệ thống nào trong số đó có thể chạy trực tiếp trên điện thoại. Năm 2021, Vision Transformer (Dosovitskiy et al.) đưa cơ chế self-attention vào phân loại ảnh y tế [7], mở ra khả năng mô hình hóa quan hệ toàn cục giữa các vùng tổn thương — nhưng ViT gốc thậm chí còn nặng hơn cả EfficientNet. Hai năm này cho thấy rõ một nghịch lý: mô hình càng chính xác thì càng xa tầm tay triển khai biên.

**Giai đoạn tìm kiếm kiến trúc cân bằng (2022–2023).** Nhận ra giới hạn của mô hình lớn, cộng đồng bắt đầu tích cực tìm kiến trúc vừa chính xác vừa gọn nhẹ. MobileViT (Mehta & Rastegari, 2022) là bước đi tiêu biểu: tích hợp self-attention toàn cục vào backbone CNN cục bộ trong một kiến trúc duy nhất, giảm số tham số xuống mức mobile mà không mất đi khả năng nắm bắt đặc trưng toàn cục [11]. Tiếp nối, Ding et al. (2023) đề xuất HI-MViT — một biến thể MobileViT bổ sung module giải thích — đạt F1 = 0,931 và AUC = 0,977 trên ISIC 2018 [24], cho thấy kiến trúc hybrid có thể cạnh tranh với mô hình lớn trên bài toán da liễu. Tuy nhiên, dù khoảng cách đang dần thu hẹp, những mô hình này vẫn chưa đáp ứng đủ yêu cầu về tốc độ và độ chính xác khi triển khai thực tế trên thiết bị ARM phổ thông.

**Giai đoạn KD ứng dụng vào da liễu và dữ liệu smartphone (2024–2025).** Năm 2024 đánh dấu hai chuyển biến quan trọng xảy ra đồng thời. Về phía dữ liệu, ISIC 2024 công bố bộ SLICE-3D với hơn 400.000 ảnh non-dermoscopic thu thập bằng thiết bị total-body photography trong điều kiện gần với ảnh smartphone [12] — đây là bộ dữ liệu thực tế nhất từ trước đến nay cho kịch bản ứng dụng cộng đồng. Cũng trong năm này, Dhar et al. (2024) lần đầu hệ thống hóa các thách thức của Edge AI trong chẩn đoán da liễu, khẳng định rằng việc chứng minh hiệu năng thực tế trên thiết bị là điều kiện không thể bỏ qua để các mô hình y tế đi vào ứng dụng [9]. Về phía kỹ thuật, đây cũng là lúc KD bắt đầu được chú ý nghiêm túc trong lĩnh vực da liễu: Islam et al. (2024) xây dựng pipeline distill từ ensemble ba teacher (ResNet152V2, ConvNeXt, ViT) sang student chỉ 2,03 MB và thu được 98,75% accuracy [14], lần đầu tiên cho thấy rằng KD có thể thu hẹp đáng kể khoảng cách giữa mô hình lớn và mô hình nhỏ trong bài toán này. Sang năm 2025, xu hướng này tiếp tục phát triển theo nhiều hướng: Saha et al. nén student xuống còn 0,26M tham số — nhỏ hơn teacher 160 lần — trong khi vẫn giữ được 91,7% accuracy và tốc độ suy luận nhanh gấp 6× [15]; Suryakanth et al. đề xuất MTAKD trong đó nhiều teacher "bỏ phiếu" đồng thuận trước khi truyền tri thức, cải thiện thêm 0,75–1,1% so với KD một teacher trên ISIC 2019 [26]; một hướng độc lập khác áp dụng KD đa tầng với layer fusion, đạt kết quả tương đương với chi phí tính toán thấp hơn đáng kể [27]. Song song với làn sóng KD, nhiều nghiên cứu ứng dụng độc lập tiếp tục xác nhận giá trị của các kiến trúc cổ điển: các biến thể EfficientNet đạt 89–94% accuracy trên bài toán da liễu [21][22], MobileNetV3 đạt 89% accuracy trên ISIC [23], trong khi Ozdemir & Pacal (2025) đẩy mức trần với kiến trúc lai ConvNeXtV2 đạt 93,48% accuracy trên ISIC 2019 [20] — song vẫn nằm ngoài tầm với của triển khai biên. Cũng trong giai đoạn này, các kiến trúc mobile-SOTA thế hệ mới — MobileNetV4, FastViT, EfficientFormerV2, RepViT — đang trưởng thành và cho thấy hiệu năng vượt trội trên thiết bị ARM. Đây chính là dải student mà đề tài sử dụng, thay cho các kiến trúc gọn nhẹ thế hệ 2019–2022.

Tuy nhiên, nhìn lại toàn bộ hành trình mười năm đó, một điều đáng chú ý là các hướng nghiên cứu vừa nêu chưa bao giờ thực sự hội tụ lại với nhau. Các nghiên cứu KD trong da liễu, dù ngày càng nhiều, đều được thực hiện với một cặp teacher–student duy nhất, trên bộ dữ liệu dermoscopic cũ, và kết thúc ở việc báo cáo accuracy trên tập test — chưa có công trình nào so sánh có hệ thống xem *kiến trúc student thuộc paradigm nào hưởng lợi nhiều nhất từ KD*, cũng chưa có ai hỏi *teacher mạnh hơn có thực sự tạo ra student tốt hơn không*. Bộ dữ liệu ISIC 2024 với đặc điểm gần smartphone nhất hoàn toàn chưa được khai thác trong bối cảnh KD. Và quan trọng nhất, chưa có nghiên cứu nào đặt câu hỏi mang tính quyết định: *sau khi distill, mô hình có thực sự chạy được trên điện thoại với độ trễ chấp nhận được không?* Đề tài này được xây dựng để trả lời đồng thời ba câu hỏi còn bỏ ngỏ đó.

#### 3. Giải pháp đề xuất

Để trả lời câu hỏi nghiên cứu trung tâm, đề tài xây dựng một khung thực nghiệm hai tầng với mục tiêu kép: vừa định lượng hiệu quả KD trên từng paradigm student, vừa phân tích vai trò của chất lượng teacher trong quá trình chưng cất.

**Ma trận teacher–student đa kiến trúc.** Thay vì một cặp teacher–student duy nhất, đề tài huấn luyện **một dải teacher có chất lượng khác nhau** ghép với **một dải student trải nhiều paradigm thiết kế**. Chỉ khi làm vậy mới trả lời được đồng thời hai câu hỏi: *paradigm student nào hưởng lợi nhiều nhất từ KD?* và *teacher mạnh hơn có tạo ra student tốt hơn không?*

| Vai trò | Model | Params | GFLOPs | Size FP32 | Paradigm |
|---|---|---|---|---|---|
| Teacher | MaxViT-Base | 118,70M | 47,84 | 453,37 MB | CNN–Transformer hybrid |
| Teacher | ConvNeXtV2-Base | 87,69M | 30,71 | 334,53 MB | Modern ConvNet |
| Teacher | EfficientNetV2-M | 52,86M | 10,72 | 202,76 MB | CNN cải tiến (fused-MBConv) |
| Student | EfficientFormerV2-S2 | 12,13M | 2,49 | 46,75 MB | Attention–CNN hybrid |
| Student | FastViT-SA12 | 10,56M | 2,96 | 40,41 MB | CNN + Reparameterization |
| Student | MobileNetV4-Conv-Medium | 8,44M | 1,65 | 32,44 MB | Depthwise-separable CNN |
| Student | RepViT-M1.0 | 6,40M | 2,21 | 24,64 MB | CNN mang thiết kế ViT |

Tất cả mô hình chia sẻ cùng một classification head (Global Average Pooling → Dropout → Dense(1)) và áp `sigmoid` tại inference. Backbone được load từ thư viện `timm` (yêu cầu `timm≥1.0` — MobileNetV4 / FastViT / EfficientFormerV2 / RepViT không có trong 0.9.x). Teacher luôn đóng băng trong quá trình KD.

*(Params/GFLOPs/size là số **thực đo** bằng `run/benchmark.sh`, đo lại **cả 7 mô hình trên cùng một máy** ngày 26/08/2026 để các con số nằm trong một bảng so được với nhau; nguồn `reports/benchmark/<model>.json`. Tỉ lệ nén của cặp đem đi triển khai `MaxViT-Base → FastViT-SA12` là **11,2× tham số / 11,2× dung lượng / 16,2× FLOPs**. Lưu ý FLOPs và params **không tỉ lệ với nhau**: RepViT-M1.0 nén params/size mạnh nhất, còn MobileNetV4 nén FLOPs mạnh nhất.)*

Ngoài ba teacher trên, repo còn cài đặt sẵn hai hướng mở rộng **chưa được huấn luyện**, để ngỏ cho giai đoạn sau: teacher nền tảng theo miền **PanDerm** (ViT-B/16, Nature Medicine 2025 — trọng số ngoài `timm`, giấy phép CC-BY-NC-4.0) và **teacher đặc quyền (LUPI)** nhận thêm metadata bảng `tbp_lv_*` ở đầu vào trong khi student vẫn hoàn toàn image-only.

**Hàm mất mát chưng cất.** Hàm mất mát KD được xây dựng theo nguyên lý của Hinton et al. [13], trong đó thành phần hard-label được thay bằng Focal Loss để giải quyết mất cân bằng lớp:

```
L_total = α · L_hard + (1 − α) · T² · L_soft
```

trong đó `L_hard = FocalLoss(z_student, y_true)` (γ=2, α=0,25) [28] cung cấp tín hiệu từ nhãn cứng; `L_soft = BCE(σ(z_student/T), σ(z_teacher/T))` truyền tín hiệu mềm của teacher với nhiệt độ `T = 4,0`; hệ số cân bằng `α = 0,3` phân bổ 30% nhãn cứng và 70% nhãn mềm.

> **Lưu ý về cơ chế.** Trong văn liệu KD đa lớp, tác dụng của nhãn mềm thường được quy cho *"dark knowledge"* — thông tin nằm ở **phân phối tương đối giữa các lớp sai**. Bài toán ở đây là **nhị phân với một logit duy nhất**, nên không tồn tại "các lớp sai" để mang thông tin đó: `σ(z_teacher/T)` chỉ là **một số vô hướng** cho mỗi mẫu. Cơ chế thực sự vận hành là **làm mượt nhãn thích ứng theo từng mẫu** (per-sample adaptive label smoothing): teacher thay nhãn cứng 0/1 bằng một mục tiêu mềm phản ánh độ khó của chính mẫu đó, làm giảm phương sai gradient trên các mẫu mơ hồ. Luận văn phát biểu theo cơ chế này, không dùng thuật ngữ "dark knowledge" — dùng nó ở bài toán một logit là sai về khái niệm.

Nhánh baseline được kích hoạt bằng một cờ cấu hình (`use_kd: false`): khi đó chương trình dùng `Trainer` + Focal Loss thuần thay cho `KDTrainer` + hàm mất mát chưng cất, và **không nạp teacher** — tương đương `α = 1,0`, đảm bảo tính kiểm soát hoàn toàn của thí nghiệm.

Hai biến thể chưng cất khác đã được cài đặt sẵn và **mặc định tắt**, để ngỏ như hướng mở rộng mà không làm thay đổi kết quả chính: thay thành phần mềm bằng **MSE trên logit thô** (Kim et al. 2021 — không nhiệt độ, không hệ số T²), và bổ sung một thành phần **chưng cất quan hệ ở mức đặc trưng (RKD**, Park et al. 2019 — khớp cấu trúc khoảng cách/góc giữa các mẫu trong batch, không cần projector nên teacher và student có thể khác số chiều).

**Thiết kế thực nghiệm so sánh đối chứng.** Điểm mấu chốt của thiết kế là nguyên tắc *ceteris paribus*: mỗi kiến trúc student được huấn luyện song song theo hai nhánh (có KD / không KD) với cùng dữ liệu, seed ngẫu nhiên, siêu tham số và quy trình đánh giá — chỉ khác ở hàm mất mát. Tổng số lượt huấn luyện theo toàn bộ ma trận:

| Nhóm | Số lượt (fold-run) | Trạng thái |
|---|---|---|
| 3 teacher × 5 fold | 15 | ✅ xong |
| 3 teacher × 5 fold, **nhánh ISIC-only** (ablation PAD) | 15 | ✅ xong |
| 4 student baseline × 5 fold | 20 | ✅ xong |
| 4 student × 5 fold, **nhánh ISIC-only** (ablation PAD) | 20 | ✅ xong |
| Ablation bộ lấy mẫu (tỉ lệ 1:3 và 1:10) | 10 | ✅ xong |
| KD: 3 teacher × 4 student × 5 fold | 60 | ✅ xong |
| **Tổng** | **140** | **140 / 140** |

> Nhánh *with-PAD* của ablation không phải huấn luyện riêng: ở tầng teacher nó chính là
> `runs/teacher/<name>`, ở tầng student chính là `runs/baseline_<student>` (cùng seed, cùng
> siêu tham số, `train_sources: null`). Vì vậy ablation PAD chỉ tốn 15 + 20 lượt chứ không phải 70.

Hiệu quả KD được định lượng qua **ΔpAUC** và **ΔAUPRC** (KD trừ baseline). Vì độ lệch chuẩn giữa các fold ở AUPRC (0,015–0,053) lớn hơn phần lớn các Δ quan sát được, mọi Δ nhỏ hơn một độ lệch chuẩn đều được mô tả là *"nằm trong nhiễu"*.

Để kết luận "khác biệt có thật hay không", đề tài dùng **paired bootstrap confidence interval** (B = 2.000 lần lặp) thay cho kiểm định t ghép cặp. Lý do là một hạn chế thống kê thực chất chứ không phải lựa chọn tiện lợi: **5 fold ở đây là 5 *mô hình* được chấm trên CÙNG một tập test, không phải 5 mẫu độc lập**, nên độ lệch chuẩn giữa các fold đo mức bất đồng giữa các mô hình chứ không đo sai số lấy mẫu của tập test — đúng đại lượng mà t-test giả định. Bootstrap khắc phục bằng cách lấy mẫu lại **các dòng của tập test**: mỗi lần lặp rút một bộ chỉ số dòng, chấm cả năm fold trên đúng bộ dòng đó rồi lấy trung bình. Vì hai nhánh được so sánh dùng chung bộ chỉ số, hiệu số giữa chúng là **ghép cặp thật**, giữ được tương quan giữa hai mô hình — khoảng tin cậy không ghép cặp sẽ vứt bỏ tương quan đó và phóng đại độ bất định. Công cụ: `scripts/bootstrap_ci.py`.

**Ablation chiến lược dữ liệu.** Song song với ma trận KD, đề tài chạy một thí nghiệm đối chứng riêng để *chứng minh* thay vì giả định các lựa chọn dữ liệu. Với PAD-UFES-20: hai nhánh được huấn luyện trên cùng một cấu hình, chỉ khác tập TRAIN+VAL (ISIC+PAD so với ISIC-only), rồi **đánh giá trên cùng một tập test** — nhờ vậy hiệu số quy hoàn toàn về việc có trộn PAD hay không. Ô quyết định là **subset ảnh PAD trong tập test** (miền lâm sàng mà nhánh ISIC-only chưa từng thấy). Ablation được chạy ở **cả hai tầng**: 3 teacher và 4 student. Tầng student bắt buộc dùng nhánh **baseline (không KD)** — nếu dùng KD thì teacher vốn đã học trên ISIC+PAD sẽ rò tri thức PAD sang nhánh ISIC-only qua nhãn mềm và làm hỏng phép so sánh. Tương tự, bộ lấy mẫu undersampling cũng có nhánh bật/tắt để đo đóng góp riêng của nó; riêng nhánh *tắt hoàn toàn* làm kích thước epoch tăng gấp 42,9 lần (5.790 → 248.161 ảnh) nên chi phí tính toán là rào cản thực tế cần cân nhắc.

**Triển khai biên.** Toàn bộ **16 biến thể student** (4 kiến trúc × 3 teacher KD + 1 baseline) được export sang định dạng **ExecuTorch .pte** (FP32) phục vụ Android on-device inference; mỗi run-dir đóng góp **fold có hành vi trung vị**, theo nguyên tắc *"chọn fold trung vị, không bao giờ chọn fold tốt nhất"*. Điểm mấu chốt của quy trình là **cổng kiểm tra tương đương số học (parity gate)**: `.pte` chỉ được coi là hợp lệ khi `max|Δlogit|` so với bản PyTorch gốc nhỏ hơn 1e-3 trên 100 mẫu. Cổng này **không phải thủ tục hình thức** — nó đã thực sự bắt được một lỗi nghiêm trọng trong đó backend XNNPACK lower sai một kiến trúc mà **không phát sinh bất kỳ thông báo lỗi nào**, và chỉ bị lộ khi so logit. Hiệu năng thực tế được đo trực tiếp trên thiết bị **Pixel 6a** (Tensor G1: 2×Cortex-X1 + 2×A76 + 4×A55) ở cả 1 và 4 threads, gồm cold start, latency trung vị ở trạng thái ổn định, latency **duy trì** sau 5 phút chạy liên tục (để bắt hiệu ứng điều tiết nhiệt), và peak PSS. Phân tích Pareto giữa AUPRC và latency **duy trì** được thực hiện để xác định frontier tối ưu, đồng thời trả lời câu hỏi thực tiễn: *mô hình nào đạt cân bằng tốt nhất giữa độ chính xác lâm sàng và khả năng chạy thời gian thực trên điện thoại phổ thông?*

### d. Phương pháp thực hiện

**Chuẩn bị dữ liệu.** Quy trình tiền xử lý được chia thành hai giai đoạn nhằm tách biệt chi phí tính toán cố định khỏi vòng huấn luyện. Giai đoạn *offline* (chạy một lần) bao gồm giải mã ảnh, resize về 224×224, lọc ảnh hỏng và trùng lặp, thống nhất nhãn đa lớp về nhị phân, và gán tiền tố `pad_` cho `patient_id` của PAD-UFES-20 [16] để tránh xung đột khi ghép dataset. Sau đó, held-out test set (~17%, patient-disjoint + stratified) được tách ra trước khi chia fold; `StratifiedGroupKFold(K=5)` được áp dụng trên development pool còn lại để đảm bảo không có bệnh nhân nào xuất hiện ở cả train lẫn val. Giai đoạn *online* trong huấn luyện sử dụng Albumentations để tăng cường ảnh ngẫu nhiên: lật ngang/dọc (p=0,5), xoay 90°, ShiftScaleRotate (±10% dịch, ±20% co giãn, ±180° xoay), jitter độ sáng/tương phản/bão hòa (±20%), hue shift (±10%), CLAHE và làm mờ Gauss với xác suất thấp.

**Huấn luyện.** Tất cả mô hình sử dụng cùng thiết lập tối ưu hóa: AdamW (learning rate phân tầng — 1e-4 cho backbone, 1e-3 cho classification head; weight decay 1e-4), cosine annealing scheduler với 3 epoch warmup, gradient clipping 1.0, tối đa 50 epoch, batch size 32 (teacher) / 64 (student), seed cố định 42 và cuDNN ở chế độ tất định. Early stopping theo `val_loss` (patience 10), còn **checkpoint được lưu theo `val pAUC@TPR≥80%`** — hai tiêu chí tách biệt có chủ đích. Teacher được huấn luyện trước với Focal Loss thuần [28] (không có soft label). Student được huấn luyện sau, dùng hàm mất mát KD (nhánh KD) hoặc Focal Loss thuần (nhánh baseline). Cả bảy kiến trúc đều yêu cầu `timm≥1.0`; ba teacher cần phân bổ VRAM cao hơn đáng kể.

Toàn bộ thực nghiệm cấu hình bằng **Hydra** và khởi chạy qua lớp script `run/*.sh` với cú pháp `KEY=VALUE` (ví dụ `bash run/train_teacher.sh TEACHER=efficientnetv2_m`). Mỗi lệnh là **một tiến trình chạy tuần tự cả 5 fold**, ghi log ra `logs/<tên>_<timestamp>.log` để không mất kết quả khi mất kết nối SSH. Môi trường chạy là **máy chủ GPU thuê ngoài (2 máy, mỗi máy 1×RTX 3090)**, không có hệ quản lý hàng đợi — job được chạy dưới `tmux`, theo dõi tiến độ bằng script chỉ-đọc `run/progress.sh`. Toàn bộ phụ thuộc được cô lập trong virtualenv nội bộ của dự án.

**Đánh giá.** Sau mỗi lần huấn luyện, best checkpoint được tải lại và chạy inference trên tập test độc lập để tính: pAUC@TPR≥80% (metric chính thức ISIC 2024), AUPRC (headline metric ở prevalence ~0,4%), AUC-ROC, sensitivity, specificity, F1-score, các điểm vận hành ở độ đặc hiệu cố định (Sens@90%Spec, Sens@95%Spec) và hai chỉ số hiệu chuẩn (Brier, ECE). Ngưỡng quyết định được chọn theo Youden's J statistic — lưu ý ngưỡng này **khác nhau giữa các fold**, nên khi triển khai phải lấy đúng ngưỡng của fold được ship. Mỗi lần chạy còn ghi lại `predictions.csv` (test) và `val_predictions.csv` (validation) để mọi metric đều tính lại được offline mà không cần chạy lại inference — trong đó `val_predictions.csv` là tập fit cho bước **hiệu chuẩn xác suất**: do bộ lấy mẫu undersampling dạy mô hình theo prior ~16,7% trong khi prevalence thật là 0,39%, xác suất `sigmoid` thô lệch cao có hệ thống. Hiệu chuẩn chỉ ảnh hưởng con số phần trăm hiển thị cho người dùng, **không** làm đổi bất kỳ metric xếp hạng nào (pAUC/AUPRC/AUC bất biến với biến đổi đơn điệu).

Kết quả 5 fold được tổng hợp theo mean ± std, kèm min/max và giá trị từng fold. Đánh giá được tổ chức theo ba tầng độc lập: *(i) in-domain* trên ISIC 2024 + PAD-UFES-20 test split; *(ii) cross-domain* trên HAM10000 [17] (ảnh dermoscopic, không tham gia huấn luyện); *(iii) fairness* trên Fitzpatrick17k [18], phân nhóm theo sắc tố da Fitzpatrick I–VI (sáng I–II / trung bình III–IV / tối V–VI), đo khoảng cách hiệu năng lớn nhất–nhỏ nhất giữa các nhóm. Hai bộ dữ liệu ngoài được chuẩn bị bằng một quy trình **riêng biệt** với quy trình huấn luyện và áp dụng bộ lọc **hai tầng**: chỉ loại ảnh hỏng ở mức toàn vẹn, còn các cờ "ảnh kém thông tin"/trùng lặp chỉ *đánh dấu* chứ không loại — vì ngưỡng phát hiện ảnh kém thông tin vốn được hiệu chỉnh trên ảnh dermoscopy sẽ kích hoạt nhầm trên ảnh lâm sàng phẳng, và mức kích hoạt đó **không độc lập với tông da**, tức sẽ làm sai lệch chính phép đo công bằng. Bước chuẩn bị kết thúc bằng một kiểm tra rò rỉ, dừng chương trình nếu có bất kỳ ảnh nào trùng với tập nội bộ.

**Triển khai và benchmark.** Mô hình tốt nhất theo phân tích Pareto được export sang ExecuTorch .pte (FP32) và đo hiệu năng trực tiếp trên Pixel 6a với 4 threads: latency trung vị, throughput (FPS), kích thước file. Phân tích Pareto (AUPRC vs latency) cung cấp cơ sở khuyến nghị model deploy cuối cùng, tách biệt rõ ràng giữa lựa chọn "chính xác tối đa" và "latency tối thiểu".

### e. Kết quả, sản phẩm dự kiến

Luận văn dự kiến tạo ra hai loại sản phẩm có giá trị độc lập: sản phẩm khoa học và sản phẩm kỹ thuật.

Về khoa học, kết quả trung tâm là **ma trận so sánh KD vs baseline** đầy đủ cho toàn bộ 12 cặp teacher–student (3 teacher × 4 student, 5-fold CV), trình bày ΔpAUC và ΔAUPRC (mean ± std) kèm kiểm định ý nghĩa thống kê. Trên cơ sở đó, đề tài phân tích tương quan giữa chất lượng teacher (AUPRC teacher) và mức độ cải thiện của student (ΔAUPRC), cung cấp bằng chứng thực nghiệm trả lời câu hỏi *"teacher tốt hơn có dẫn đến KD hiệu quả hơn không?"*. Bổ sung vào đó là **kết quả ablation dữ liệu** (có/không PAD-UFES-20; bật/tắt undersampling) — bằng chứng định lượng cho từng lựa chọn thiết kế thay vì giả định. Kết quả kiểm chứng 3 tầng — in-domain, cross-domain (HAM10000) và fairness (Fitzpatrick17k) — hoàn thiện đánh giá toàn diện về khả năng tổng quát hóa và tính công bằng của mô hình được đề xuất.

Về kỹ thuật, đề tài cung cấp **pipeline hoàn chỉnh và tái lập được**: mã nguồn Python + Hydra, lớp script khởi chạy `run/*.sh` cho máy chủ GPU, và bộ artifact chuẩn hóa (`aggregated.json/md`, `test_metrics.json`, `val_metrics.json`, `predictions.csv`, `val_predictions.csv`) cho phép tái tính toán mọi metric — kể cả đường PR, phân tích theo miền ảnh và khoảng tin cậy bootstrap — mà không cần chạy lại inference. Bổ sung vào đó là **báo cáo triển khai Android**: latency trung vị, throughput và kích thước `.pte` trên Pixel 6a cùng phân tích Pareto, kèm bước **kiểm tra tương đương số học** giữa mô hình `.pte` và bản PyTorch gốc để bảo đảm con số on-device thuộc về đúng mô hình đã đánh giá. Toàn bộ sản phẩm này cùng với luận văn được hoàn thành thành văn là đầu ra khép kín của nghiên cứu.

**Kết quả đã đạt được tại thời điểm cập nhật đề cương (29/08/2026).** Toàn bộ **140/140 lượt huấn luyện** và cả ba tầng đánh giá đã hoàn tất; các kết quả cốt lõi được tổng hợp trong `reports/BAO_CAO_TONG_HOP.md` và trình bày đầy đủ trong luận văn (`thesis/LUAN_VAN.md`):

| Nội dung | Kết quả |
|---|---|
| Hiệu quả KD, in-domain | 12/12 cặp dương trên pAUC@80 và Sensitivity theo điểm ước lượng; theo paired bootstrap CI thì **8/12 cặp có ý nghĩa trên pAUC** và **5/12 trên AUPRC**, **không cặp nào xấu đi có ý nghĩa**. Trung bình KD xoá **22,7% headroom pAUC** còn lại |
| Hiệu quả KD, xuyên miền | **Quyết định hơn hẳn in-domain**: trên HAM10000, ΔAUPRC của cặp tiêu biểu là **+0,0713 [+0,0598, +0,0819]**, 11/12 cặp có CI loại trừ 0 |
| Quy luật tìm được | Mức lãi của KD **tỉ lệ nghịch với chất lượng sẵn có của student** — tương quan Pearson giữa pAUC baseline và ΔpAUC là **r = −0,963** (n = 12) |
| Ảnh hưởng chất lượng teacher | Thứ tự ΔAUPRC in-domain **trùng khớp** thứ tự AUPRC standalone của teacher (maxvit > convnextv2 > efficientnetv2_m), nhưng **đảo chiều khi đổi miền** — không tồn tại "teacher tốt nhất" độc lập với miền triển khai |
| Ablation PAD-UFES-20 | **Có ích ở cả hai tầng**: 3/3 teacher (ΔAUPRC +0,092…+0,131 trên miền lâm sàng) và **3/4 student có CI loại trừ 0** (+0,105…+0,120) |
| Ablation bộ lấy mẫu | 1:5 **thắng 1:10 có ý nghĩa** (+0,0570 [+0,0343, +0,0781]) và **không phân biệt được với 1:3** — lựa chọn 1:5 là lựa chọn được chứng minh |
| Công bằng theo tông da | Khoảng cách tái lập được là **light − medium** (+0,0469 AUC, **19/19 run** có CI loại trừ 0), **không phải** light − dark (4/19) |
| Triển khai | **16/16 `.pte` PASS cổng parity ở cả PC lẫn Pixel 6a**; latency đo đủ (cold / ổn định / duy trì) + peak PSS; **Pareto frontier chỉ còn 2 điểm** (MobileNetV4-Conv-Medium và FastViT-SA12) |

### f. Tài liệu tham khảo

[1] Wang, M., Gao, X., & Zhang, L. (2025). "Recent global patterns in skin cancer incidence, mortality, and prevalence." *Clinics in Dermatology*, 43(1), 33–40.

[2] De Pinto, G., et al. (2024). "Global trends in cutaneous malignant melanoma incidence and mortality." *Melanoma Research*, 34(3), 265–275.

[3] Siegel, R. L., Miller, K. D., & Jemal, A. (2020). "Cancer statistics, 2020." *CA: A Cancer Journal for Clinicians*, 70(1), 7–30.

[4] Kittler, H., et al. (2002). "Diagnostic accuracy of dermoscopy." *The Lancet Oncology*, 3(3), 159–165.

[5] Esteva, A., et al. (2017). "Dermatologist-level classification of skin cancer with deep neural networks." *Nature*, 542(7639), 115–118.

[6] Tan, M., & Le, Q. V. (2019). "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks." *ICML*, 6105–6114.

[7] Dosovitskiy, A., et al. (2021). "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale." *ICLR 2021*.

[8] Price, W. N., & Cohen, I. G. (2019). "Privacy in the age of medical big data." *Nature Medicine*, 25(1), 37–43.

[9] Dhar, T., et al. (2024). "Challenges and opportunities in edge AI for skin disease diagnosis." *Scientific Reports*, 14, 17323.

[10] Howard, A., et al. (2019). "Searching for MobileNetV3." *ICCV*, 1314–1324.

[11] Mehta, S., & Rastegari, M. (2022). "MobileViT: Light-weight, General-purpose, and Mobile-friendly Vision Transformer." *ICLR 2022*.

[12] Kurtansky, N. R., et al. (2024). "ISIC 2024 Challenge: Skin Cancer Detection with 3D-TBP." Kaggle Competition / ISIC Archive. DOI: 10.34970/2024-slice-3d.

[13] Hinton, G., Vinyals, O., & Dean, J. (2015). "Distilling the Knowledge in a Neural Network." *arXiv:1503.02531*.

[14] Islam, N., et al. (2024). "Leveraging Knowledge Distillation for Lightweight Skin Cancer Classification." *arXiv:2406.17051*.

[15] Saha, S., et al. (2025). "Knowledge distillation approach for skin cancer classification on lightweight deep learning model." *Healthcare Technology Letters*, 14(1), e12120.

[16] Pacheco, A. G., & Krohling, R. A. (2020). "The impact of patient clinical information on automated skin cancer detection." *Computers in Biology and Medicine*, 116, 103545.

[17] Tschandl, P., Rosendahl, C., & Kittler, H. (2018). "The HAM10000 dataset." *Scientific Data*, 5, 180161.

[18] Groh, M., et al. (2021). "Evaluating Deep Neural Networks Trained on Clinical Images in Dermatology with the Fitzpatrick 17k Dataset." *CVPR 2021 Workshop*.

[19] Ha, Q., Liu, B., & Liu, F. (2020). "Identifying Melanoma Images using EfficientNet Ensemble." *arXiv:2010.05351*.

[20] Ozdemir, B., & Pacal, I. (2025). "A robust deep learning framework for multiclass skin cancer classification." *Scientific Reports*, 15(1), 4938.

[21] Aboulmira, A., et al. (2025). "Hybrid Model with Wavelet Decomposition and EfficientNet for Accurate Skin Cancer Classification." *Journal of Cancer*, 16(2), 506–520.

[22] Venkatachalam, C., et al. (2025). "Enhanced skin cancer classification using modified EfficientNetV2L." *Scientific Reports*, 15(1), 38304.

[23] Mehboob, S., et al. (2025). "Enhanced Skin Cancer Classification with MobileNetV3 and Morphological Preprocessing." *International Journal of Innovations in Science & Technology*, 7(7), 1–12.

[24] Ding, Y., et al. (2023). "HI-MViT: A lightweight model for explainable skin disease classification based on modified MobileViT." *Digital Health*, 9, 20552076231207197.

[25] Gou, J., et al. (2021). "Knowledge Distillation: A Survey." *International Journal of Computer Vision*, 129(6), 1789–1826.

[26] Suryakanth, P., et al. (2025). "MTAKD: multi-teacher agreement knowledge distillation for edge AI skin disease diagnosis." *Scientific Reports*, 15, Article 27038.

[27] Anonymous. (2025). "Multi-stage knowledge distillation with layer fusion-based deep learning approach for skin cancer classification." *Scientific Reports*, 15, Article 23403.

[28] Lin, T. Y., et al. (2017). "Focal Loss for Dense Object Detection." *ICCV*, 2980–2988.

---

## 2. KẾ HOẠCH THỰC HIỆN

| Giai đoạn | Nội dung | Thời gian | Trạng thái |
|---|---|---|---|
| 1 | Xây dựng pipeline huấn luyện; tiền xử lý ISIC 2024 + PAD-UFES-20; thiết lập 5-fold CV patient-disjoint + test holdout độc lập | 06/2026 | ✅ xong |
| 2 | Huấn luyện 3 teacher (EfficientNetV2-M, ConvNeXtV2-Base, MaxViT-Base) — 5 fold mỗi mô hình | 07/2026 | ✅ xong (15/15) |
| 3 | **Ablation dữ liệu**: nhánh ISIC-only ở tầng teacher (3 × 5 fold) **và tầng student** (4 × 5 fold) để đo đóng góp của PAD-UFES-20; ablation bộ lấy mẫu (tỉ lệ 1:3 / 1:10) | 07–08/2026 | ✅ **xong** (15/15 + 20/20 + 10/10) |
| 4 | Huấn luyện 4 student nhánh baseline (không KD) — 5 fold mỗi mô hình | 07–08/2026 | ✅ xong (20/20) |
| 5 | Huấn luyện ma trận KD: 3 teacher × 4 student × 5 fold | 08–09/2026 | ✅ xong (60/60) |
| 6 | Export ExecuTorch `.pte` + kiểm tra tương đương số học; benchmark on-device Pixel 6a; phân tích Pareto (AUPRC vs latency) | 09/2026 | ✅ **xong** — parity 16/16 PASS ở cả PC lẫn Pixel 6a; latency (cold/steady/sustained) + peak PSS đo xong 27/08; **Pareto đã chốt: chỉ còn 2 điểm trên frontier** |
| 7 | Đánh giá chéo miền HAM10000; phân tích công bằng Fitzpatrick17k (nhóm sắc tố da I–VI) | 09–10/2026 | ✅ **xong cả hai bộ**, 5 biến thể split |
| 8 | Tổng hợp 5-fold, **khoảng tin cậy paired bootstrap**, phân tích tương quan chất lượng teacher ↔ ΔAUPRC; hiệu chuẩn xác suất cho mô hình chốt | 10/2026 | ✅ **xong** — CI bootstrap đủ 3 miền + cả hai ablation + paired A-vs-B giữa hai ứng viên ship; hiệu chuẩn xong in-domain + hai bộ ngoài; tương quan teacher↔Δ và r = −0,963 đã phân tích |
| 9 | Viết luận văn (chương lý thuyết, thực nghiệm, kết quả và thảo luận) | 09–11/2026 | ✅ **bản đầy đủ 5 chương** tại `thesis/LUAN_VAN.md` |
| 10 | Hoàn thiện, nộp luận văn và chuẩn bị bảo vệ | 11/2026 | 🔄 rà soát, dựng slide bảo vệ |

> *Ghi chú:* Kế hoạch được cập nhật ngày **29/08/2026** theo tiến độ thực tế. **Đường găng đã đi qua**: giai đoạn 5 (ma trận KD 60 lượt) — từng là rủi ro số một của đề cương — đã hoàn tất, cùng toàn bộ 140/140 lượt huấn luyện. Phần việc còn lại không cần GPU.
>
> *Hai rủi ro theo dõi trước đây đều đã hoá giải:* (i) giai đoạn 5 hoàn tất nên câu hỏi "teacher nào chưng cất tốt nhất" đã trả lời được — và câu trả lời hoá ra **phụ thuộc miền triển khai**, không có đáp án tuyệt đối; (ii) Fitzpatrick17k ban đầu chỉ tải được **23,4%** ảnh do 76% URL trong bản release đã chết, nhưng một bản mirror được xác minh **byte-identical bằng md5** đã nâng coverage lên **99,98%** — và chính bản đầy đủ mới phát hiện được rằng bất bình đẳng nằm ở nhóm **medium**, điều mà bản 23,4% không thể thấy.
>
> *Sai lệch so với đề cương ban đầu, ghi rõ để không bị hiểu nhầm:* (a) kiểm định thống kê được đổi từ **paired t-test** sang **paired bootstrap CI** vì 5 fold là 5 *mô hình* chấm trên cùng một tập test, vi phạm giả định mẫu độc lập của t-test; (b) nhánh ablation **tắt hoàn toàn bộ lấy mẫu** bị loại **vì chi phí tính toán** (epoch tăng 42,9 lần), không phải vì đã thử và thất bại; (c) các hướng đã cài đặt sẵn nhưng **cố ý không huấn luyện** (teacher nền tảng PanDerm, teacher đặc quyền LUPI, biến thể MSE-logit và RKD, cổng OOD, lượng tử hoá INT8) được đặt ở mục "Hướng phát triển" kèm ghi chú *"mã nguồn đã sẵn sàng, chưa huấn luyện"*.
