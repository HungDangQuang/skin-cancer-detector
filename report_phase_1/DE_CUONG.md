# ĐỀ CƯƠNG LUẬN VĂN THẠC SĨ

**Tên đề tài (tiếng Việt):** PHÁT HIỆN UNG THƯ DA TRÊN THIẾT BỊ BIÊN SỬ DỤNG MÔ HÌNH HỌC SÂU KẾT HỢP CHƯNG CẤT TRI THỨC

**Tên đề tài (tiếng Anh):** KNOWLEDGE-DISTILLED DEEP LEARNING MODELS FOR SKIN CANCER DETECTION ON EDGE DEVICES

**Học viên:** Đặng Quang Hưng · MSHV: 230101006 · Khóa 18 · Đợt 1

**Người hướng dẫn khoa học:** TS. Nguyễn Thanh Bình · binhnt@uit.edu.vn

*Cập nhật: 19/09/2026 — đồng bộ với toàn văn luận văn [`thesis/LUAN_VAN.md`](../thesis/LUAN_VAN.md) (5 chương, 140/140 lượt huấn luyện, ba tầng đánh giá, benchmark Pixel 6a). Danh mục tài liệu tham khảo đã được rà soát lại theo lượt kiểm chứng trích dẫn 12–16/09/2026; nguồn số liệu: [`reports/BAO_CAO_TONG_HOP.md`](../reports/BAO_CAO_TONG_HOP.md).*

---

## 1. NỘI DUNG

### a. Giới thiệu về đề tài

Ung thư da là một trong những loại ung thư phổ biến nhất trên toàn cầu. Theo dữ liệu GLOBOCAN 2022, ước tính có khoảng 331.722 ca mắc mới u hắc tố ác tính (melanoma) và gần 58.667 ca tử vong trong năm 2022; melanoma đứng thứ mười bảy còn ung thư da không phải hắc tố đứng thứ năm trong các loại ung thư phổ biến nhất [40]. Số ca mắc mới ở phần lớn quốc gia vẫn đứng yên hoặc tăng lên trong khi tỉ lệ tử vong đã giảm, phần giảm ấy được quy cho việc nhận biết yếu tố nguy cơ, chẩn đoán sớm và tiến bộ điều trị [4]. Sức nặng của chẩn đoán sớm hiện ra rõ nhất ở một con số lâm sàng: tiên lượng sống sót sau 5 năm đạt tới 99% nếu bệnh được phát hiện ở giai đoạn khu trú [33]. Nói cách khác, phần lớn tử vong do melanoma không đến từ việc thiếu phương pháp điều trị mà đến từ việc **phát hiện muộn**.

Chẩn đoán lâm sàng truyền thống dựa vào kinh nghiệm bác sĩ da liễu qua kỹ thuật soi da (dermoscopy) và các quy tắc hình thái. Quy trình này có hai điểm yếu hệ thống: độ chính xác biến động mạnh theo trình độ người đọc ảnh [17], và chi phí tiếp cận khiến việc tự theo dõi định kỳ — cách hiệu quả nhất để bắt melanoma sớm — bất khả thi với phần lớn dân số. Khoảng cách giữa hai vế ấy là động lực của các hệ thống hỗ trợ chẩn đoán tự động (Computer-Aided Diagnosis — CAD). Bước ngoặt kỹ thuật đến từ Esteva và cộng sự (2017): một mạng nơ-ron tích chập thuần, huấn luyện đầu–cuối chỉ từ điểm ảnh và nhãn bệnh, đạt hiệu năng ngang 21 bác sĩ da liễu có chứng chỉ trên hai bài toán phân loại nhị phân [9]. Kể từ đó các kiến trúc như EfficientNet [34] và Vision Transformer [7] liên tục nâng trần hiệu năng trên các tập chuẩn ISIC.

Tiến bộ đó đi kèm một hệ quả ít được nói tới: **mô hình càng chính xác càng xa tầm với của triển khai thực tế**. Giải pháp thắng ISIC 2020 là một ensemble 18 mô hình, trong đó 16 thuộc họ EfficientNet cùng hai backbone SE-ResNeXt-101 và ResNeSt-101 [12] — hiệu năng rất cao nhưng không chạy được trực tiếp trên điện thoại. Triển khai theo mô hình đám mây kéo theo ba rào cản đồng thời: độ trễ và phụ thuộc kết nối ở đúng những nơi thiếu bác sĩ da liễu nhất, nguy cơ về quyền riêng tư dữ liệu y tế [28], và chi phí biên theo mỗi lượt sử dụng. Xu hướng đưa xử lý AI xuống thiết bị (**Edge AI**) giải quyết cả ba, nhưng đặt ra một đánh đổi riêng: các mô hình gọn nhẹ như EfficientNet-B0 [34], MobileNetV3 [14] hay MobileViT [23] thường phải chấp nhận suy giảm độ chính xác. Trong bài toán y tế, suy giảm này **không đối xứng về hậu quả** — bỏ sót một ca ác tính có thể dẫn tới tử vong, còn một dương tính giả chỉ dẫn tới một lần khám xác nhận. Yêu cầu bất đối xứng đó được phản ánh trực tiếp trong thước đo chính thức của ISIC 2024: **pAUC@TPR≥80%**, chỉ tính phần diện tích dưới đường ROC ở vùng độ nhạy tối thiểu 80% [15].

**Chưng cất tri thức (Knowledge Distillation — KD)** [13] là hướng đề tài chọn để thu hẹp khoảng cách này: dùng một mô hình *giáo viên* (teacher) lớn hướng dẫn *học sinh* (student) gọn nhẹ qua các **nhãn mềm** — thứ mang thông tin về mức độ tự tin của teacher trên từng mẫu mà nhãn cứng 0/1 không chứa. Tuy nhiên văn liệu KD trong da liễu hầu như chỉ khảo sát **một** cặp teacher–student, báo cáo accuracy tuyệt đối mà thiếu nhánh đối chứng, và chưa khai thác bộ ISIC 2024 — bộ dữ liệu gần ảnh smartphone nhất hiện có [15].

Từ khoảng trống đó, đề tài đặt câu hỏi nghiên cứu trung tâm: *"Liệu chưng cất tri thức có thực sự mang lại cải thiện đáng kể và nhất quán cho các mô hình gọn nhẹ thuộc nhiều paradigm thiết kế khác nhau, và chất lượng của teacher ảnh hưởng như thế nào đến hiệu quả KD trên student?"* Để trả lời, đề tài thiết kế một thực nghiệm so sánh đối chứng có kiểm soát (*ceteris paribus*): mỗi kiến trúc student được huấn luyện song song hai lần — có KD và không KD — với cùng dữ liệu, cùng seed, cùng siêu tham số, chỉ khác hàm mất mát. Hiệu số **ΔAUPRC** và **ΔpAUC** giữa hai nhánh, kết luận bằng khoảng tin cậy chứ không bằng đếm số trận thắng, là đóng góp khoa học cốt lõi.

### b. Mục tiêu của đề tài

Mục tiêu tổng quát là đánh giá một cách có hệ thống hiệu quả của chưng cất tri thức trong việc cải thiện hiệu năng phân loại ung thư da của các mô hình gọn nhẹ, đồng thời kiểm chứng tính khả thi triển khai trên thiết bị biên Android. Mục tiêu này được tách thành **sáu câu hỏi kiểm chứng được**, mỗi câu gắn với một phần bằng chứng cụ thể.

**Bảng 1.** Sáu câu hỏi nghiên cứu và lý do đặt ra mỗi câu

| Mã | Câu hỏi | Vì sao cần hỏi |
|---|---|---|
| **Q1** | Trộn PAD-UFES-20 vào tập huấn luyện có làm mô hình tốt hơn không? | Là một lựa chọn thiết kế dữ liệu, không phải chân lý; nếu không chứng minh thì mọi kết quả sau đó dựa trên giả định chưa kiểm |
| **Q2** | Teacher mạnh hơn có tạo ra student tốt hơn không? | Văn liệu KD ngoài da liễu ghi nhận hiện tượng *teacher quá mạnh dạy kém* [3, 24]; cần biết hiện tượng đó có xảy ra ở bài toán này không |
| **Q3** | Chưng cất có cải thiện student nhất quán qua các paradigm kiến trúc khác nhau không? | Nếu chỉ đúng với một họ kiến trúc thì kết luận không tổng quát hoá được |
| **Q4** | Student sau chưng cất có vượt được teacher không? | Là mục tiêu tối hậu của nén mô hình; nếu có thì cần biết vượt ở độ đo nào |
| **Q5** | Nếu chỉ được triển khai một mô hình duy nhất thì chọn gì? | Câu hỏi kỹ thuật thực tiễn mà một luận văn ứng dụng phải trả lời được |
| **Q6** | Tỉ lệ undersampling 1:5 có phải lựa chọn đúng không? | Cùng lý do như Q1 — một siêu tham số quan trọng không nên được chọn theo thói quen |

Ba nhóm công việc tuần tự phục vụ sáu câu hỏi trên. **Nhóm thứ nhất** xây dựng nền tảng dữ liệu: khai thác ISIC 2024 SLICE-3D (ảnh non-dermoscopic gần ảnh smartphone) kết hợp PAD-UFES-20 [26] để nâng prevalence từ ~0,1% lên 0,3885%, với quy trình chia dữ liệu patient-disjoint stratified 5-fold chống rò rỉ. **Nhóm thứ hai** là trọng tâm: huấn luyện và so sánh đối chứng trên ma trận 3 teacher × 4 student, kèm hai thí nghiệm loại trừ ở phía dữ liệu (Q1, Q6). **Nhóm thứ ba** kiểm chứng tổng quát hoá và tính công bằng trên HAM10000 [35] và Fitzpatrick17k [11], rồi khép vòng bằng export ExecuTorch và đo trên thiết bị Pixel 6a.

Qua đó luận văn kỳ vọng đóng góp trên hai phương diện: **khoa học** — bằng chứng thực nghiệm có hệ thống về cơ chế và giới hạn của KD ở bài toán nhị phân một logit, cùng ảnh hưởng của chất lượng teacher qua nhiều miền ảnh; **kỹ thuật** — một pipeline tái lập được từ dữ liệu thô tới mô hình chạy trên điện thoại, kèm cổng kiểm tra tương đương số học bảo đảm con số đo trên thiết bị thuộc về đúng mô hình đã đánh giá.

### c. Nội dung nghiên cứu của đề tài

#### 1. Xây dựng bài toán

Bài toán được đặt trong khung **phân loại nhị phân**: cho ảnh tổn thương da 224×224, xây dựng hàm $f_\theta$ cho ra **một logit duy nhất** $z$, sao cho $\sigma(z)$ ước lượng xác suất ác tính. Ánh xạ nhãn theo quy ước lâm sàng: melanoma, BCC và SCC là ác tính (1); nevus, dày sừng lành tính và các tổn thương lành tính khác là lành tính (0). Riêng dày sừng ánh sáng là tổn thương tiền ung thư mà các bộ dữ liệu dùng hai quy ước khác nhau — đề tài giữ nguyên quy ước của từng bộ và ghi rõ khi so sánh.

Bốn bộ dữ liệu được dùng với vai trò phân biệt rõ ràng; chúng không được chọn song song mà là lời giải cho một chuỗi nhu cầu nối tiếp, mỗi bộ giải quyết một vấn đề do bộ trước tạo ra.

**Bảng 2.** Bốn bộ dữ liệu, quy mô thực dùng và vai trò (ISIC 2024 và PAD-UFES-20 gộp một dòng vì cùng tạo nên tập nội bộ)

| Bộ dữ liệu | Số ảnh công bố | Số ảnh thực dùng | Loại ảnh | Vai trò |
|---|---:|---:|---|---|
| ISIC 2024 SLICE-3D [15] (401.059) + PAD-UFES-20 [26] (2.298) | 403.357 | **372.242** | Non-dermoscopic (cắt từ chụp toàn thân 3D) + lâm sàng chụp điện thoại | **Huấn luyện chính** + tập test nội bộ (62.040 ảnh) |
| HAM10000 [35] | 10.015 | **7.470** | Soi da (dermoscopic) | **Chỉ** kiểm chứng chéo miền |
| Fitzpatrick17k [11] | 16.577 | **16.574** tải và xác minh được (99,98%) | Lâm sàng trường rộng, 114 bệnh + thang tông da I–VI | **Chỉ** phân tích công bằng |

*Hai bộ đánh giá ngoài không bao giờ tham gia huấn luyện. Fitzpatrick17k chỉ phát hành danh sách URL chứ không phát hành ảnh; 76% URL trong bản release đã chết nên một lần tải trực tiếp chỉ khôi phục 23,4% — độ phủ 99,98% đạt được nhờ một bản sao lưu công khai có tên tệp chính là mã băm nội dung, xác minh được với mã băm bản gốc công bố. Biến thể chính dùng cho phân tích công bằng còn 4.320 ảnh sau khi loại các ảnh thiếu nhãn tông da và nhóm bệnh không phải u.*

Bài toán mang ba thách thức đặc trưng, và cả ba định hình toàn bộ thiết kế.

**Thách thức 1 — mất cân bằng lớp cực đoan.** ISIC 2024 chỉ chứa khoảng 0,1% mẫu ác tính; sau khi trộn PAD-UFES-20, prevalence của tập test đo được là **0,3885%**. Ở mức đó *accuracy* mất hoàn toàn ý nghĩa: một mô hình luôn dự đoán "lành tính" đạt 99,61% accuracy mà không phát hiện được ca nào, còn AUC-ROC bị lạc quan hoá vì phần lớn diện tích dưới đường cong do các mẫu âm tính rất dễ phân loại đóng góp. Vì vậy **AUPRC là chỉ số chính** — đường cơ sở ngẫu nhiên của nó *chính bằng* prevalence nên không thể bị thổi phồng bởi lớp đa số [32] — còn **pAUC@TPR≥80%** [21] là chỉ số thứ hai để so với benchmark ISIC. Giải pháp gồm hai mức can thiệp độc lập: lấy mẫu giảm động 1:5 ở **mức dữ liệu** và Focal Loss ($\gamma=2{,}0$, $\alpha=0{,}25$) [19] ở **mức gradient**. Không mức nào thay thế được mức kia: ở prevalence 0,39%, một lô 64 ảnh rút ngẫu nhiên có xác suất ~78% không chứa ca ác tính nào, mà Focal Loss chỉ phân bổ lại trọng số *giữa những mẫu có mặt trong lô*.

**Thách thức 2 — rò rỉ dữ liệu.** Một bệnh nhân trong ISIC 2024 có thể đóng góp hàng chục ảnh, còn PAD-UFES-20 chụp nhiều lần cho *cùng một* tổn thương. Chia ngẫu nhiên theo ảnh sẽ khiến mô hình "nhận diện bệnh nhân" thay vì "nhận diện tổn thương", và kiểu rò rỉ này **hoàn toàn im lặng** — biểu hiện duy nhất là điểm số cao hơn bình thường. Ràng buộc patient-disjoint vì thế là điều kiện bắt buộc: tập test (~17%) được cắt ra **trước**, patient-disjoint và giữ nguyên tỉ lệ ca ác tính, rồi `StratifiedGroupKFold(K=5)` mới áp lên phần còn lại; `patient_id` của PAD được gắn tiền tố `pad_` để hai bộ không gán trùng định danh.

**Thách thức 3 — ràng buộc triển khai biên.** Mô hình cuối phải đủ nhỏ và nhanh để chạy thời gian thực trên Android phổ thông, và quan trọng hơn, phải được **đo trên thiết bị thật** thay vì suy diễn từ FLOPs — vì hai hiệu ứng chi phối độ trễ thực tế đều không nằm trong FLOPs: nền tảng thực thi có thể nới khoảng cách giữa hai kiến trúc ra tới 181 lần, và điều tiết nhiệt làm mô hình chậm thêm 45–49% sau năm phút chạy liên tục.

**Hình 1.** Chiến lược chia dữ liệu chống rò rỉ — từ nguy cơ tới bốn lớp chặn.

![Hình 1 — Chiến lược chia dữ liệu chống rò rỉ](figures/split_strategy.png)

Hai bước chia để lại ba mức quy mô rất khác nhau: tập test giữ lại **62.040 ảnh** (241 ca ác tính) dùng chung cho **mọi** fold và **mọi** run; pool huấn luyện của mỗi fold **248.161 ảnh**; và tập thực dùng mỗi epoch sau lấy mẫu giảm 1:5 chỉ **5.790 ảnh** (965 ác tính + 4.825 lành tính rút lại khác nhau ở mỗi epoch). Một tập test duy nhất dùng chung chính là điều kiện để hai nhánh có KD và không KD so sánh được với nhau.

#### 2. Các nghiên cứu liên quan

**Giai đoạn đặt nền móng (2015–2019).** Esteva và cộng sự (2017) [9] chứng minh một CNN thuần có thể phân loại ung thư da ngang 21 bác sĩ có chứng chỉ chỉ với dữ liệu ảnh, mở ra niềm tin rằng học sâu có thể trở thành công cụ CAD thực tiễn. Cùng giai đoạn, Hinton và cộng sự (2015) đề xuất chưng cất tri thức [13] như một phương pháp nén mô hình — ý tưởng công bố sớm nhưng lúc đó chưa được cộng đồng da liễu chú ý; Gou và cộng sự (2021) sau này hệ thống hoá lĩnh vực thành ba nhóm theo loại tri thức được truyền (theo đáp ứng, theo đặc trưng, theo quan hệ), trong đó đề tài dùng nhóm **theo đáp ứng** (logit) [10]. Năm 2019 ra đời hai kiến trúc gọn nhẹ nền tảng: EfficientNet [34] với co giãn đồng hợp, và MobileNetV3 [14] với tích chập tách theo chiều sâu tối ưu qua tìm kiếm kiến trúc.

**Giai đoạn mô hình lớn thống trị (2020–2021).** Áp lực cạnh tranh trên bảng xếp hạng ISIC đẩy các nhóm theo hướng mô hình ngày càng lớn; ensemble 18 mô hình thắng ISIC 2020 [12] là ví dụ tiêu biểu. Năm 2021, Vision Transformer [7] đưa self-attention vào phân loại ảnh, mở ra khả năng mô hình hoá quan hệ toàn cục nhưng nặng hơn cả EfficientNet. Hai năm này bộc lộ rõ nghịch lý trung tâm của đề tài.

**Giai đoạn tìm kiếm kiến trúc cân bằng (2022–2023).** MobileViT [23] tích hợp self-attention toàn cục vào backbone CNN cục bộ, giảm tham số xuống mức mobile mà vẫn nắm được đặc trưng toàn cục. Tiếp nối, Ding và cộng sự (2023) đề xuất HI-MViT — biến thể MobileViT có thêm module giải thích — đạt F1 = 0,931 và AUC = 0,977 trên ISIC 2018 [6], cho thấy kiến trúc lai có thể cạnh tranh với mô hình lớn trên bài toán da liễu.

**Giai đoạn KD ứng dụng vào da liễu (2024–2025).** Năm 2024 đánh dấu hai chuyển biến đồng thời. *Về phía dữ liệu*, ISIC 2024 công bố SLICE-3D với hơn 400.000 ảnh non-dermoscopic thu bằng thiết bị chụp toàn thân trong điều kiện gần ảnh smartphone [15] — bộ dữ liệu thực tế nhất từ trước tới nay cho kịch bản ứng dụng cộng đồng. *Về phía kỹ thuật*, KD bắt đầu được chú ý nghiêm túc trong lĩnh vực này; Bảng 3 điểm lại các công trình tiêu biểu, với cột thứ ba là cột quyết định.

**Bảng 3.** Các công trình chưng cất tri thức trong da liễu, giai đoạn 2024–2025

| Công trình | Thiết kế | Nhánh đối chứng không chưng cất | Accuracy tuyệt đối đã báo cáo |
|---|---|---|---|
| Islam et al. (2024) [16] | Chưng cất từ ensemble 3 teacher (ResNet152V2, ConvNeXt, ViT) → student 2,03 MB | Không | 98,75% (HAM10000) |
| Saha et al. (2025) [31] | Hai pha: pha một chưng cất giữa bốn teacher và bốn student đều thuộc họ CNN cổ điển, pha hai chưng cất tiếp sang một mạng 0,29 M tham số | Không | 88,6–88,9% (HAM10000) |
| Winata et al. (2025) [42] | MTAKD — nhiều teacher "bỏ phiếu" đồng thuận trước khi truyền tri thức | Không — hiệu số **+0,75%** và **+1,1%** mà bài báo cáo là so với framework chưng cất khác, không phải so với student của chính họ | 87,53% (ISIC 2019) |
| Pavel et al. (2025) [27] | KD đa tầng với layer fusion, teacher lai ViT + ConvNeXT | **Có** — "hybrid student baseline" | 95,88% (HAM10000) |

Song song, các kiến trúc cổ điển vẫn tiếp tục được áp dụng cho bài toán này và đều báo cáo theo cùng một cách — accuracy tuyệt đối trên một bộ ISIC hoặc HAM10000 [1], [22], [25], [38]. Cũng trong giai đoạn này, các kiến trúc mobile-SOTA thế hệ mới — MobileNetV4 [30], FastViT [37], EfficientFormerV2 [18], RepViT [39] — trưởng thành và cho hiệu năng vượt trội trên ARM; đây chính là dải student đề tài sử dụng thay cho các kiến trúc gọn nhẹ thế hệ 2019–2022.

Nhìn lại toàn bộ hành trình đó, các hướng nghiên cứu vừa nêu **chưa bao giờ thực sự hội tụ**. Đề tài xác định bốn khoảng trống: (i) các nghiên cứu KD trong da liễu hầu như không so sánh chính student ấy ở hai trạng thái có và không chưng cất, nên phần do KD mang lại không tách được khỏi phần vốn đã thuộc về kiến trúc; (ii) khi có nhiều teacher, các công trình hoặc gộp chúng thành một nguồn tri thức duy nhất, hoặc chỉ xếp hạng trên cùng một miền ảnh, nên cả hai câu hỏi *teacher mạnh hơn có dạy tốt hơn không* và *thứ tự teacher có đổi khi đổi miền không* đều còn bỏ ngỏ; (iii) ISIC 2024 chưa được khai thác trong bối cảnh KD; (iv) rất ít công trình đi tới câu hỏi cuối — sau chưng cất, student có hoạt động tốt hơn trên điện thoại thật không, và số đo có thuộc về đúng mô hình đã đánh giá không. Bốn thành phần của thiết kế thực nghiệm ở mục sau ứng với đúng bốn khoảng trống này.

#### 3. Giải pháp đề xuất

**Ma trận teacher–student đa kiến trúc.** Thay vì một cặp duy nhất, đề tài huấn luyện **ba teacher có chất lượng khác nhau** ghép với **bốn student trải bốn paradigm thiết kế**. Chỉ khi làm vậy mới đồng thời hỏi được *paradigm student nào hưởng lợi nhiều nhất từ KD* (Q3) và *teacher mạnh hơn có tạo ra student tốt hơn không* (Q2).

**Bảng 4.** Bộ teacher và bộ student, thông số thực đo

| Vai trò | Mô hình | Paradigm | Params ↓ | GFLOPs ↓ | Size FP32 ↓ |
|---|---|---|---:|---:|---:|
| Teacher | MaxViT-Base [36] | CNN–Transformer hybrid (multi-axis attention) | 118,699 M | 47,843 | 453,37 MB |
| Teacher | ConvNeXtV2-Base [43] | Modern ConvNet + GRN | 87,694 M | 30,707 | 334,53 MB |
| Teacher | EfficientNetV2-M | CNN fused-MBConv | 52,860 M | 10,722 | 202,76 MB |
| Student | EfficientFormerV2-S2 [18] | Hybrid attention–CNN | 12,132 M | 2,493 | 46,75 MB |
| Student | FastViT-SA12 [37] | CNN + tái tham số hoá | 10,557 M | 2,962 | 40,41 MB |
| Student | MobileNetV4-Conv-Medium [30] | CNN depthwise-separable | 8,436 M | 1,653 | 32,44 MB |
| Student | RepViT-M1.0 [39] | CNN mang thiết kế ViT | 6,403 M | 2,214 | 24,64 MB |

*Toàn bộ 7 mô hình được đo lại trên **cùng một máy** ngày 26/08/2026 để các con số so được với nhau. Tỉ lệ nén của cặp đem đi triển khai `MaxViT-Base → FastViT-SA12` là **11,2× tham số / 11,2× dung lượng / 16,2× FLOPs**; lưu ý FLOPs và params **không tỉ lệ với nhau** — RepViT-M1.0 nén params/size mạnh nhất còn MobileNetV4 nén FLOPs mạnh nhất.*

Cả bảy mô hình dùng **một cách dựng duy nhất**: backbone nạp từ `timm ≥ 1.0` [41] với trọng số tiền huấn luyện ImageNet, đầu phân loại luôn là `GAP → Dropout → Linear(in_features, 1)`, đầu ra một logit thô và `sigmoid` chỉ áp tại suy luận. Không có nhánh xử lý riêng cho kiến trúc nào, nhờ vậy **kiến trúc mới thật sự là biến độc lập duy nhất** giữa các thí nghiệm, và mười hai cặp chưng cất là mười hai dòng cấu hình chứ không phải mười hai lần lập trình.

**Hàm mất mát chưng cất.** Dạng nhị phân của công thức Hinton [13], với thành phần nhãn cứng thay bằng Focal Loss [19] để xử lý mất cân bằng:

$$\mathcal{L}_{\text{total}} = \alpha\,\mathcal{L}_{\text{hard}} + (1-\alpha)\,T^{2}\,\mathcal{L}_{\text{soft}}, \qquad \mathcal{L}_{\text{hard}} = \text{Focal}(z_s, y), \qquad \mathcal{L}_{\text{soft}} = \text{BCE}(z_s/T,\ \tilde{y}),\quad \tilde{y} = \sigma(z_t/T)$$

với $T = 4{,}0$ và $\alpha = 0{,}3$ (30% nhãn cứng, 70% nhãn mềm), cố định cho **cả mười hai cặp** chứ không dò riêng — cái giá phải trả để các hiệu số còn so được với nhau. Việc dùng BCE thay cho độ đo KL của công thức gốc chỉ là khác biệt hình thức: với một logit, khai triển KL giữa hai biến Bernoulli cho entropy chéo nhị phân cộng một hằng số không chứa tham số student, nên hai cách cực tiểu hoá cho **đúng một gradient**.

> **Lưu ý về cơ chế.** Văn liệu KD đa lớp quy tác dụng của nhãn mềm cho *"dark knowledge"* — thông tin nằm ở phân phối tương đối giữa **các lớp sai**. Bài toán ở đây là **nhị phân một logit**, nên không tồn tại "lớp sai" nào để mang thông tin đó: $\sigma(z_t/T)$ chỉ là **một số vô hướng** cho mỗi mẫu. Cơ chế thực sự vận hành là **làm mượt nhãn thích ứng theo từng mẫu** (per-sample adaptive label smoothing): teacher thay nhãn cứng bằng một mục tiêu mềm phản ánh độ khó của chính mẫu đó, làm giảm phương sai gradient trên các mẫu mơ hồ. Luận văn phát biểu theo cơ chế này và **không dùng thuật ngữ "dark knowledge"** — dùng nó ở bài toán một logit là sai về khái niệm. Dự đoán rút ra từ cơ chế (student đã mạnh thì KD còn ít chỗ để cải thiện) được kiểm chứng ở mục e.

Teacher **đóng băng hoàn toàn** trong giai đoạn hai, và điều đó cần ba cơ chế tách rời chứ không phải một dòng cấu hình: khoá đạo hàm cho mọi tham số, chạy lượt truyền xuôi trong ngữ cảnh không dựng đồ thị đạo hàm, và — chỗ dễ sai nhất — đặt teacher ở **chế độ đánh giá** lại ở đầu mỗi epoch, vì các tầng chuẩn hoá theo lô tích luỹ thống kê ngay trong lượt truyền xuôi và hoàn toàn không chịu tác động của cờ khoá đạo hàm. Thiếu cơ chế thứ ba, teacher vẫn đang học mà không ai nhìn thấy, và cụm từ "chưng cất từ teacher X" mất nghĩa.

**Thiết kế thực nghiệm so sánh đối chứng.** Nhánh baseline được định nghĩa bằng **sự vắng mặt** của teacher chứ không phải bằng việc đặt trọng số của nó về 0 — một teacher vẫn hiện diện vẫn chiếm tài nguyên và vẫn tham gia từng bước huấn luyện, khi đó hai nhánh đã khác nhau ở nhiều hơn một điểm. Ngoài hàm mất mát, hai nhánh chia sẻ mọi thứ: cùng fold, cùng seed, chế độ tính toán tất định, cùng bộ tối ưu và lịch trình học. Đơn vị so sánh là một **cặp** ghép **theo từng fold**, không ghép hai giá trị trung bình [5].

**Hình 2.** Ba bước của quy trình huấn luyện; điểm mấu chốt ở bước hai là student được huấn luyện hai lần trên cùng một fold để bước ba quy được chênh lệch về đúng một nguyên nhân.

![Hình 2 — Quy trình huấn luyện hai giai đoạn và nhánh đối chứng](figures/kd_pipeline.png)

**Bảng 5.** Tổng số lượt huấn luyện theo toàn bộ ma trận

| Nhóm | Số lượt (fold-run) | Trạng thái |
|---|---:|---|
| 3 teacher × 5 fold | 15 | ✅ xong |
| 3 teacher × 5 fold, **nhánh ISIC-only** (ablation PAD — Q1) | 15 | ✅ xong |
| 4 student baseline × 5 fold | 20 | ✅ xong |
| 4 student × 5 fold, **nhánh ISIC-only** (ablation PAD — Q1) | 20 | ✅ xong |
| Ablation bộ lấy mẫu, tỉ lệ 1:3 và 1:10 (Q6) | 10 | ✅ xong |
| KD: 3 teacher × 4 student × 5 fold | 60 | ✅ xong |
| **Tổng** | **140** | **140 / 140** |

> Nhánh *with-PAD* của ablation không phải huấn luyện riêng: ở tầng teacher nó chính là `runs/teacher/<name>`, ở tầng student chính là `runs/baseline_<student>` (cùng seed, cùng siêu tham số). Vì vậy ablation PAD chỉ tốn 15 + 20 lượt chứ không phải 70.

**Kết luận thống kê.** Đề cương ban đầu dự định dùng kiểm định t ghép cặp trên năm fold; phương pháp ấy đã được thay bằng **khoảng tin cậy bootstrap ghép cặp** [8] (B = 2.000, seed 42), vì một hạn chế thống kê thực chất chứ không phải sự tiện lợi: **5 fold ở đây là 5 *mô hình* chấm trên CÙNG một tập test, không phải 5 mẫu độc lập**, nên độ lệch chuẩn giữa các fold đo mức bất đồng giữa các mô hình chứ không đo sai số lấy mẫu của tập test — đúng đại lượng mà t-test giả định. Mỗi lần lặp rút một bộ chỉ số **hàng của tập test**, chấm cả năm fold của cả hai nhánh trên đúng bộ chỉ số ấy rồi mới lấy hiệu. Hai chỗ dễ làm sai: nối kết quả năm fold thành một bảng lớn rồi bootstrap sẽ nhân bản mỗi hàng năm lần và làm khoảng tin cậy hẹp đi giả tạo ~$\sqrt{5}$ lần; và bỏ phép ghép cặp sẽ vứt đi tương quan giữa hai mô hình chấm trên cùng dữ liệu, phóng đại độ bất định — mục e ghi lại một trường hợp cạm bẫy này thực sự bật ra. Kèm theo đó là một quy tắc đọc áp cho toàn mục e: độ lệch chuẩn giữa năm fold ở AUPRC nằm trong khoảng 0,0127–0,0531, lớn hơn phần lớn các Δ quan sát được, nên mọi Δ nhỏ hơn một độ lệch chuẩn đều chỉ được mô tả là *nằm trong nhiễu* chứ không phải một cải thiện.

**Hai thí nghiệm loại trừ ở phía dữ liệu.** Khuôn so sánh trên không gắn riêng với chưng cất: thứ duy nhất được phép khác giữa hai lượt có thể thay bằng một lựa chọn thiết kế khác. Với **PAD-UFES-20** (Q1), hai nhánh chỉ khác tập TRAIN+VAL rồi **đánh giá trên cùng một tập test**; ô quyết định là tập con 377 ảnh PAD trong test — miền lâm sàng mà nhánh ISIC-only chưa từng thấy. Ablation chạy ở **cả hai tầng** teacher và student, và tầng student **bắt buộc dùng nhánh baseline không KD**: nếu dùng KD thì teacher vốn đã học trên ISIC+PAD sẽ rò tri thức PAD sang nhánh ISIC-only qua nhãn mềm và làm hỏng phép so sánh. Với **tỉ lệ lấy mẫu** (Q6), ba mức 1:3, 1:5 và 1:10 được chạy thật trên cùng cặp chưng cất và cùng tập test; nhánh *tắt hoàn toàn* bộ lấy mẫu bị loại **vì chi phí tính toán** (epoch tăng 42,9 lần), không phải vì đã thử và thất bại.

**Triển khai biên.** Toàn bộ **16 biến thể student** (4 kiến trúc × 3 teacher KD + 1 baseline) được export sang **ExecuTorch `.pte`** [29] ở FP32, mỗi run-dir đóng góp **fold có hành vi trung vị** theo nguyên tắc *"chọn fold trung vị, không bao giờ chọn fold tốt nhất"* — vì trên mười hai cặp, fold tốt nhất vượt trung bình năm fold tới +0,0263 AUPRC, lớn hơn cả toàn bộ hiệu quả chưng cất trong miền (+0,0235), nên chọn fold đẹp nhất đã tạo ra mức tăng lớn hơn chính hiệu ứng cần đo. Điểm mấu chốt của quy trình là **cổng kiểm tra tương đương số học**: `.pte` chỉ hợp lệ khi $\max|\Delta \text{logit}|$ so với bản PyTorch gốc nhỏ hơn $10^{-3}$ trên 100 mẫu cố định. Cổng này **không phải thủ tục hình thức** — nó đã bắt được một trường hợp trong đó backend tăng tốc lower sai một kiến trúc mà **không phát sinh bất kỳ thông báo lỗi nào**, cho logit $\approx -2{,}2\times10^{10}$ thay vì $-3{,}15$. Hiệu năng thực tế đo trên **Pixel 6a** (Tensor G1) ở cả 1 và 4 luồng, gồm khởi động nguội, độ trễ khi máy còn nguội, độ trễ **duy trì** sau 5 phút chạy liên tục và bộ nhớ đỉnh, rồi phân tích Pareto giữa AUPRC và độ trễ duy trì.

### d. Phương pháp thực hiện

**Chuẩn bị dữ liệu.** Tiền xử lý chia hai giai đoạn để tách chi phí cố định khỏi vòng huấn luyện. Giai đoạn *offline* (chạy một lần, sáu bước) gồm giải mã ảnh, lọc toàn vẹn, resize 224×224, lọc ảnh không mang thông tin, khử trùng lặp theo mã băm, và chuẩn hoá nhãn kèm gắn tiền tố `pad_` cho `patient_id`. Trật tự sáu bước chịu một ràng buộc duy nhất: **mỗi phép lọc chỉ đúng trên một dạng biểu diễn nhất định của ảnh** — bộ lọc toàn vẹn cần kích thước gốc nên phải đứng trước bước resize, còn lọc chất lượng và khử trùng lặp cần ảnh đã chuẩn hoá nên phải đứng sau; đặt sai bên thì cả hai hỏng mà không báo lỗi. Giai đoạn *online* dùng Albumentations [2]: lật ngang/dọc, xoay 90°, ShiftScaleRotate, jitter độ sáng/tương phản/bão hoà, hue shift, CLAHE và làm mờ Gauss xác suất thấp. MixUp, CutMix và CutOut bị **cấm trong mã nguồn** (chương trình dừng nếu ai đó thêm vào cấu hình), mỗi kỹ thuật vì một lý do riêng: MixUp và CutMix tạo **nhãn phân số** cho một lớp vốn đã chỉ chiếm 0,39%, đi ngược mọi nỗ lực xử lý mất cân bằng; MixUp còn **phá tính nhất quán của chưng cất** vì nhãn mềm của teacher tính trên ảnh gốc, nên nếu student học trên ảnh đã trộn thì hai vế của hàm mất mát không còn nói về cùng một đầu vào; còn CutOut che ngẫu nhiên một vùng ảnh, mà tổn thương thường chỉ chiếm một phần nhỏ khung hình nên có xác suất đáng kể nó **xoá đúng tổn thương** trong khi nhãn vẫn ghi ác tính.

Hai bộ đánh giá ngoài đi qua một **bộ lọc hai tầng** riêng, và đây là một trong những quyết định dễ làm sai nhất của khâu dữ liệu. **Tầng 1 — thực sự loại bỏ** chỉ áp cho lỗi toàn vẹn: một tệp không mở được thì không phải dữ liệu, và loại nó không thể thiên lệch theo tông da. **Tầng 2 — chỉ đánh dấu**: các cờ chất lượng và trùng lặp vẫn được tính đủ nhưng chỉ ghi thành cột metadata, ảnh vẫn nằm trong tập test. Lý do: trên tập test, xoá một ảnh là **sửa chính thước đo**; nghiêm trọng hơn, ngưỡng "ảnh kém thông tin" vốn hiệu chỉnh trên ảnh soi da sẽ kích hoạt thường xuyên hơn trên ảnh da sẫm màu, nên dùng nó trước khi đo công bằng sẽ **tạo ra hoặc che giấu đúng cái khoảng cách mà phép đo đi tìm**. Bước chuẩn bị kết thúc bằng một phép đối chiếu với toàn bộ ảnh nội bộ, **dừng chương trình với mã thoát 2** nếu phát hiện trùng lặp; cả hai bộ đều đã qua kiểm tra này và sạch.

**Huấn luyện.** Mọi mô hình dùng chung một thiết lập tối ưu hoá: AdamW [20] với learning rate phân tầng (1e-4 backbone, 1e-3 head), weight decay 1e-4; cosine annealing kèm 3 epoch warmup; gradient clipping 1,0; tối đa 50 epoch; batch size 32 (teacher) / 64 (student); seed 42 và cuDNN ở chế độ tất định. Teacher được huấn luyện trước với Focal Loss thuần, student huấn luyện sau bằng hàm mất mát KD (nhánh KD) hoặc Focal Loss thuần (nhánh baseline). Trong quy trình có một chỗ **cố ý không đối xứng**: dừng sớm theo `val_loss` (patience 10) còn checkpoint lưu theo `val pAUC@TPR≥80%`. Lý do là pAUC chỉ dựa trên một số rất ít mẫu ác tính trong tập validation nên có thể nhảy vọt chỉ vì vài mẫu đổi thứ hạng; lấy một đại lượng dao động như vậy làm căn cứ dừng sẽ khiến huấn luyện kết thúc ở một vòng may mắn thay vì đúng lúc mô hình bắt đầu quá khớp.

Toàn bộ thực nghiệm cấu hình bằng **Hydra** và khởi chạy qua lớp script `run/*.sh` với cú pháp `KEY=VALUE` (ví dụ `bash run/train_teacher.sh TEACHER=efficientnetv2_m`). Mỗi lệnh là **một tiến trình chạy tuần tự cả 5 fold**, ghi log ra `logs/<tên>_<timestamp>.log` để không mất kết quả khi mất kết nối SSH. Lớp chạy **không có hệ quản lý hàng đợi**: mỗi job chỉ là một tiến trình, khởi chạy dưới `tmux` và theo dõi bằng script chỉ-đọc `run/progress.sh`; toàn bộ phụ thuộc cô lập trong virtualenv nội bộ của dự án nên không đụng tới môi trường hệ thống của máy chủ.

**Đánh giá.** Sau mỗi lượt huấn luyện, best checkpoint được nạp lại và chạy suy luận một lần trên tập test đã niêm phong, ghi: pAUC@TPR≥80%, AUPRC, AUC-ROC, sensitivity, specificity, F1, các điểm vận hành ở độ đặc hiệu cố định (Sens@90%Spec, Sens@95%Spec), đếm thô TP/FP/TN/FN, và hai chỉ số hiệu chuẩn. Ngưỡng nhị phân chọn theo Youden's J [44] — lưu ý ngưỡng này **khác nhau giữa các fold**, nên khi triển khai phải lấy đúng ngưỡng của fold được ship. Mỗi lượt còn ghi `predictions.csv` (test) và `val_predictions.csv` (validation), nhờ đó mọi phân tích — đường PR, phân rã theo miền ảnh, khoảng tin cậy bootstrap, cắt theo nhóm nhân khẩu — đều tính lại được **offline, không cần chạy lại suy luận**. Đây là lựa chọn thiết kế trả lãi lớn: một số phân tích quan trọng nhất chỉ nảy sinh **sau khi** toàn bộ huấn luyện đã kết thúc. Kết quả năm fold tổng hợp theo mean ± std kèm min/max và giá trị từng fold; **không khẳng định nào dựa trên một fold đơn lẻ**.

**Hình 3.** Ba tầng đánh giá độc lập và câu hỏi mỗi tầng trả lời.

![Hình 3 — Ba tầng đánh giá độc lập](figures/eval_tiers.png)

Ba tầng hỏi ba câu khác nhau trên ba bộ dữ liệu khác nhau: *(i) in-domain* trên tập test nội bộ — điều kiện thuận lợi nhất; *(ii) cross-domain* trên HAM10000, ảnh soi da tức **miền ngược** với dữ liệu huấn luyện, nên nếu lợi ích của KD chỉ là hiệu ứng riêng của tập huấn luyện thì đây là chỗ nó biến mất; *(iii) fairness* trên Fitzpatrick17k, chấm riêng theo ba nhóm tông da (light 2.310 / medium 1.599 / dark 411 ảnh). Hai ràng buộc giữ ba tầng tách bạch: không bộ ngoài nào từng tham gia huấn luyện, và **ngưỡng quyết định của mỗi lượt chạy được đóng băng từ tập validation nội bộ của chính nó** — hiệu chỉnh lại ngưỡng trên tập ngoài sẽ khiến kết quả xuyên miền lạc quan một cách có hệ thống mà gần như không phát hiện được từ bảng số. Một ràng buộc thứ ba thuộc về cách đọc: tỉ lệ ca ác tính ba tầng lần lượt là 0,39%, 15,6% và 50,0%, mà đường cơ sở ngẫu nhiên của AUPRC lại **chính bằng tỉ lệ ấy**, nên một điểm AUPRC ở tầng này không bao giờ được đặt cạnh điểm AUPRC ở tầng khác.

**Triển khai và benchmark.** Toàn bộ 16 mô hình vượt cổng kiểm tra tương đương rồi được đo trong **cùng một phiên** trên Pixel 6a — ràng buộc bắt buộc vì máy nóng dần theo thời gian nên hai phiên khác nhau cho hai nền nhiệt khác nhau. Điều kiện đo cố định trước và xác minh lại **trên từng dòng dữ liệu**: không cắm sạc, chế độ máy bay, độ sáng giữ nguyên, thứ tự 16 mô hình xáo trộn theo seed cố định, mỗi mô hình 30 vòng khởi động rồi 200 vòng đo.

### e. Kết quả, sản phẩm dự kiến

Luận văn tạo ra hai loại sản phẩm có giá trị độc lập. Về **khoa học**: ma trận so sánh KD vs baseline đầy đủ cho 12 cặp teacher–student (5-fold CV) với ΔpAUC và ΔAUPRC kèm khoảng tin cậy ghép cặp; phân tích ảnh hưởng của chất lượng teacher qua ba miền ảnh; hai thí nghiệm loại trừ ở phía dữ liệu; và kết quả kiểm chứng ba tầng. Về **kỹ thuật**: pipeline tái lập được (mã nguồn Python + Hydra, lớp script `run/*.sh`, bộ artifact chuẩn hoá cho phép tái tính mọi metric offline) và báo cáo triển khai Android kèm cổng kiểm tra tương đương số học.

**Kết quả đã đạt được (cập nhật 19/09/2026).** Toàn bộ 140/140 lượt huấn luyện và cả ba tầng đánh giá đã hoàn tất. Bảng 6 trả lời sáu câu hỏi của Bảng 1, mỗi câu kèm **mức chắc chắn mà bằng chứng cho phép**.

**Bảng 6.** Câu trả lời cho sáu câu hỏi nghiên cứu

| Mã | Câu trả lời và bằng chứng |
|---|---|
| **Q1** | **Có, ở cả hai tầng.** Cả 3 teacher hưởng lợi trên miền ảnh lâm sàng (ΔAUPRC +0,0920…+0,1311); ở tầng student **3/4 kiến trúc có CI loại trừ 0** (+0,1045…+0,1200), ngoại lệ là RepViT-M1.0 (+0,0404 [−0,0092; +0,0908]) — nhưng chính nó lại đạt ý nghĩa ở ΔAUC và ΔpAUC. Trộn PAD **không làm hại miền ISIC**: 3/4 student còn cải thiện có ý nghĩa ngay trên miền ấy |
| **Q2** | **Có khi đo trong miền, nhưng không có đáp án độc lập với miền triển khai.** In-domain, thứ tự ΔAUPRC trùng khớp thứ tự AUPRC của chính teacher (MaxViT 0,6566 > ConvNeXtV2 0,6506 > EfficientNetV2-M 0,6298) — song với n = 3 thì chỉ phát biểu được là *trùng thứ tự*, không phải một tương quan. Trên HAM10000 thứ tự **đảo ngược hoàn toàn**, còn trên Fitzpatrick17k chính teacher tốt nhất của HAM lại rơi xuống cuối và **gây hại có ý nghĩa trên AUC cho 2/4 student** |
| **Q3** | **Có, xét về hướng.** Cả 4 paradigm student đều hưởng lợi; 12/12 cặp dương trên pAUC, độ nhạy và Sens@fixed-Spec. Nhưng theo CI thì in-domain chỉ **5/12** cặp trên AUPRC và **8/12** trên pAUC, **không cặp nào xấu đi có ý nghĩa ở bất kỳ độ đo nào**. Bằng chứng quyết định nằm ở **xuyên miền**: 11/12 cặp có CI loại trừ 0, ΔAUPRC trung vị +0,0304, cao nhất **+0,0713 [+0,0598; +0,0819]**. Nguyên nhân chênh lệch đã xác định được là **cỡ mẫu** (241 ca dương in-domain so với 1.169 của HAM10000), không phải hiệu ứng yếu đi |
| **Q4** | **Không vượt trên mọi độ đo, nhưng không thua đáng kể ở nơi bài toán quan tâm.** Student vượt teacher trên pAUC ở **11/12** cặp và trên độ nhạy; chưa vượt trên AUPRC. Cặp ship: pAUC **0,1851** so với 0,1830 của teacher, AUPRC **0,6510** so với 0,6566 — chênh 0,0056, nhỏ hơn độ lệch chuẩn năm fold của chính mỗi bên. Chính KD tạo ra khoảng cách đó: cùng kiến trúc nhưng không KD chỉ đạt 0,6082, tức **xét điểm ước lượng** thì KD lấp được khoảng **88%** quãng đường từ baseline lên teacher, đổi lại mô hình nhẹ hơn **11,2×** |
| **Q5** | **`MaxViT-Base → FastViT-SA12`** cho kịch bản sàng lọc thực tế: thắng ứng viên còn lại ở **8/8 độ đo xuyên miền** với CI loại trừ 0, mạnh nhất ở **nhóm da tối** (+0,0646 AUPRC). Nếu ràng buộc thiết bị là cứng thì chọn `ConvNeXtV2-Base → MobileNetV4-Conv-Medium` — nhanh hơn **2,9×** và tương đương trong miền, đổi lại là suy giảm khi dịch chuyển miền |
| **Q6** | **Có, và đã chứng minh chứ không phải giả định.** 1:5 thắng 1:10 có ý nghĩa (ΔAUPRC **+0,0570 [+0,0343; +0,0781]**) nhưng **không phân biệt được với 1:3** (−0,0097 [−0,0222; +0,0044]). Chi tiết thứ hai đáng nhớ hơn: nếu chỉ nhìn điểm ước lượng thì 1:3 trông như nhỉnh hơn, và chỉ khoảng tin cậy mới cho thấy không có cơ sở để đổi |

Ngoài sáu câu hỏi trên, thực nghiệm còn cho **bốn phát hiện không nằm trong đề cương ban đầu**:

1. **Khả năng tận dụng KD tỉ lệ nghịch với chất lượng sẵn có của student** — tương quan Pearson giữa pAUC baseline và ΔpAUC là **r = −0,963** (n = 12), gần như tuyến tính hoàn hảo. Quy luật này khớp với cơ chế "làm mượt nhãn thích ứng" đã nêu ở mục c.3, và nó lặp lại trên cả trục **miền ảnh**: KD giúp nhiều nhất đúng ở miền mà baseline còn yếu nhất. Hệ quả thực tiễn: **KD phát huy đúng ở chỗ ta muốn nén mạnh nhất**. Quy theo phần khoảng cách còn lại tới trần, KD xoá được trung bình **22,7% headroom pAUC** — cách trình bày đúng cho một độ đo đã bão hoà, nơi mọi giá trị nằm trong dải 0,1718–0,1859 trên trần 0,20.
2. **Tập test in-domain có cấu trúc bất thường, và điều đó đảo chiều cách đọc hai cặp mô hình.** 61.663 ảnh ISIC chỉ chứa **61 ca ác tính**, còn 377 ảnh PAD chứa **180 ca** — tức 0,6% số ảnh nắm ba phần tư số ca bệnh. Hai cặp có ΔAUPRC âm trên toàn tập thực ra **dương rõ trên miền ISIC** (+19,4% và +33,1% tương đối), phần âm hoàn toàn đến từ tập con lâm sàng. Hệ quả khi trích dẫn: con số AUPRC ≈ 0,65 là **thống kê hỗn hợp**, còn con số đại diện cho riêng ISIC 2024 là **0,045–0,069**.
3. **Bất bình đẳng theo tông da nằm ở nhóm *trung bình*, không phải nhóm tối.** Thứ tự ba nhóm **trên AUC** là light 0,6755 > dark 0,6474 > medium 0,6286 — **không đơn điệu theo độ sẫm của da**. Khoảng cách `light − medium` (+0,0469 AUC) tái lập được với **19/19 lượt chạy có CI loại trừ 0** trên cả AUC lẫn AUPRC; `light − dark` chỉ 4/19 trên AUC và 1/19 trên AUPRC; còn `dark − medium` tuy có điểm ước lượng nghiêng về phía nhóm tối (+0,0188 AUC) nhưng **0/19 lượt có CI loại trừ 0**, nên chỉ nói được là *có hướng, chưa phân định được*. Bằng chứng chỉ dứt khoát sau khi độ phủ Fitzpatrick17k được khôi phục lên 99,98%: trên bản 23,4% chỉ 1/19 lượt phân định được, và bản nhỏ còn **dựng lên một tín hiệu không có thật** (9/19 trên AUPRC cho cặp dark − medium, tụt về 1/19 khi có đủ dữ liệu).
4. **Đường triển khai đã đóng bằng bằng chứng số học ở cả hai đầu.** 16/16 mô hình vượt cổng kiểm tra tương đương ở **cả máy chủ lẫn chính điện thoại**. Đo trên thiết bị thật cho thấy **Pareto frontier chỉ còn hai kiến trúc**, điều tiết nhiệt làm ba kiến trúc chạy trên backend tăng tốc chậm đi **45–49%** sau 5 phút (ba tỉ số gần nhau tới mức phải coi là giới hạn toả nhiệt của máy chứ không phải phẩm chất kiến trúc), **dung lượng tệp không dự đoán được tốc độ**, và **chọn teacher là miễn phí trên trục tốc độ** vì bốn biến thể của một kiến trúc chỉ khác nhau ở giá trị trọng số.

**Hình 4.** Độ chính xác so với tốc độ của 16 mô hình trên Pixel 6a; trục ngang là độ trễ sau 5 phút chạy liên tục (thang log), nên mô hình càng gần góc trên bên trái càng đáng triển khai.

![Hình 4 — Pareto AUPRC vs latency trên Pixel 6a](../reports/pareto_auprc_vs_latency.png)

**Bảng 7.** Hai ứng viên còn lại trên Pareto frontier

| Chiều | MaxViT-Base → FastViT-SA12 | ConvNeXtV2-Base → MobileNetV4 |
|---|--:|--:|
| AUPRC in-domain ↑ | **0,6510** | 0,6351 |
| pAUC@80 in-domain ↑ | **0,1851** | 0,1835 |
| AUPRC HAM10000 ↑ | **0,4572** | 0,4198 |
| AUPRC Fitzpatrick17k ↑ | **0,6623** | 0,6172 |
| Độ trễ sau 5 phút chạy liên tục ↓ | 113,9 ms | **39,5 ms** |
| Size `.pte` ↓ | 40,35 MiB | **32,11 MiB** |
| std giữa 5 fold trên HAM10000 ↓ | 0,1036 | **0,0341** |

Chính cặp số trên HAM10000 cho thấy **vì sao phải ghép cặp**: ước lượng độ bất định riêng cho từng mô hình thì hai khoảng tin cậy chồng lấn ([0,4313; 0,4824] so với [0,3942; 0,4459]) và sẽ kết luận hai mô hình ngang nhau; hiệu số ghép cặp lại cho **+0,0374 [+0,0245; +0,0495]**, không chạm 0.

**Hạn chế đã xác định.** (i) Tập test in-domain chỉ có 241 ca dương, và 74,7% trong số đó đến từ 377 ảnh PAD — đây là nguyên nhân khiến bằng chứng in-domain mỏng hơn xuyên miền. (ii) Ở ngưỡng đóng băng, Sens@90%Spec rơi xuống 0,324–0,510 trên HAM10000 và độ đặc hiệu gần bằng 0 trên Fitzpatrick17k; **không cách chọn ngưỡng nào nâng được trần đó** vì giới hạn nằm ở khả năng xếp hạng chứ không ở chỗ cắt. (iii) Dịch chuyển miền gây khó cho **cả teacher lẫn student** — ba teacher cũng tụt Sens@90%Spec xuống 0,481–0,498 trên HAM10000 — nên khoảng cách còn lại ngoài miền **không phải cái giá của việc nén mô hình** mà là giới hạn của chính dữ liệu huấn luyện. (iv) Mọi kết luận đều là **hồi cứu**: về mặt kỹ thuật luận văn kết luận dứt khoát, còn về mặt lâm sàng chỉ kết luận trong phạm vi dữ liệu đã dùng.

### f. Tài liệu tham khảo

**Tiếng Anh**

[1] Aboulmira A., et al. (2025), "Hybrid Model with Wavelet Decomposition and EfficientNet for Accurate Skin Cancer Classification", *Journal of Cancer* Vol.16 (2), pp.506-520.

[2] Buslaev A., et al. (2020), "Albumentations: Fast and Flexible Image Augmentations", *Information* Vol.11 (2), pp.125.

[3] Cho J. H., Hariharan B. (2019), "On the Efficacy of Knowledge Distillation", *ICCV 2019*, pp.4794-4802.

[4] De Pinto G., et al. (2024), "Global trends in cutaneous malignant melanoma incidence and mortality", *Melanoma Research* Vol.34 (3), pp.265-275.

[5] Dietterich T. G. (1998), "Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms", *Neural Computation* Vol.10 (7), pp.1895-1923.

[6] Ding Y., et al. (2023), "HI-MViT: A lightweight model for explainable skin disease classification based on modified MobileViT", *Digital Health* Vol.9, pp.20552076231207197.

[7] Dosovitskiy A., et al. (2021), "An Image is Worth 16×16 Words: Transformers for Image Recognition at Scale", *ICLR 2021*.

[8] Efron B., Tibshirani R. J. (1993), *An Introduction to the Bootstrap*, Chapman & Hall/CRC, New York.

[9] Esteva A., et al. (2017), "Dermatologist-level classification of skin cancer with deep neural networks", *Nature* Vol.542 (7639), pp.115-118.

[10] Gou J., Yu B., Maybank S. J., Tao D. (2021), "Knowledge Distillation: A Survey", *International Journal of Computer Vision* Vol.129 (6), pp.1789-1819.

[11] Groh M., et al. (2021), "Evaluating Deep Neural Networks Trained on Clinical Images in Dermatology with the Fitzpatrick 17k Dataset", *CVPR 2021 Workshops*, pp.1820-1828.

[12] Ha Q., Liu B., Liu F. (2020), "Identifying Melanoma Images using EfficientNet Ensemble: Winning Solution to the SIIM-ISIC Melanoma Classification Challenge", *arXiv:2010.05351*.

[13] Hinton G., Vinyals O., Dean J. (2015), "Distilling the Knowledge in a Neural Network", *arXiv:1503.02531*.

[14] Howard A., et al. (2019), "Searching for MobileNetV3", *ICCV 2019*, pp.1314-1324.

[15] International Skin Imaging Collaboration (2024), *ISIC 2024 - Skin Cancer Detection with 3D-TBP*, cuộc thi Kaggle và bộ dữ liệu SLICE-3D, DOI: 10.34970/2024-slice-3d, https://www.kaggle.com/competitions/isic-2024-challenge

[16] Islam N., Hasib K. M., Joti F. A., Karim A., Azam S. (2024), "Leveraging Knowledge Distillation for Lightweight Skin Cancer Classification: Balancing Accuracy and Computational Efficiency", *arXiv:2406.17051*.

[17] Kittler H., et al. (2002), "Diagnostic accuracy of dermoscopy", *The Lancet Oncology* Vol.3 (3), pp.159-165.

[18] Li Y., et al. (2023), "Rethinking Vision Transformers for MobileNet Size and Speed", *ICCV 2023*. (EfficientFormerV2.)

[19] Lin T. Y., Goyal P., Girshick R., He K., Dollár P. (2017), "Focal Loss for Dense Object Detection", *ICCV 2017*, pp.2980-2988.

[20] Loshchilov I., Hutter F. (2019), "Decoupled Weight Decay Regularization", *ICLR 2019*. (Bộ tối ưu AdamW.)

[21] McClish D. K. (1989), "Analyzing a Portion of the ROC Curve", *Medical Decision Making* Vol.9 (3), pp.190-195.

[22] Mehboob S., Bukhari M., Shah Y. A., Khan S., Sharif M. (2025), "Enhanced Skin Cancer Classification with MobileNetV3 and Morphological Preprocessing: A Deep Learning-Based Extension", *International Journal of Innovations in Science & Technology* Vol.7 (7), pp.1-12.

[23] Mehta S., Rastegari M. (2022), "MobileViT: Light-weight, General-purpose, and Mobile-friendly Vision Transformer", *ICLR 2022*.

[24] Mirzadeh S. I., Farajtabar M., Li A., Levine N., Matsukawa A., Ghasemzadeh H. (2020), "Improved Knowledge Distillation via Teacher Assistant", *AAAI 2020*, pp.5191-5198.

[25] Ozdemir B., Pacal I. (2025), "A robust deep learning framework for multiclass skin cancer classification", *Scientific Reports* Vol.15 (1), pp.4938.

[26] Pacheco A. G. C., Lima G. R., Salomão A. S., et al. (2020), "PAD-UFES-20: A skin lesion dataset composed of patient data and clinical images collected from smartphones", *Data in Brief* Vol.32, pp.106221.

[27] Pavel M. A., Asad R., Michael G. K. O., et al. (2025), "Multi-stage knowledge distillation with layer fusion-based deep learning approach for skin cancer classification", *Scientific Reports* Vol.15 (1), pp.39792.

[28] Price W. N., Cohen I. G. (2019), "Privacy in the age of medical big data", *Nature Medicine* Vol.25 (1), pp.37-43.

[29] PyTorch Team (2024), *ExecuTorch: On-device AI inference runtime*, tài liệu chính thức của PyTorch Foundation, https://docs.pytorch.org/executorch/stable/ (truy cập 09/2026)

[30] Qin D., et al. (2024), "MobileNetV4: Universal Models for the Mobile Ecosystem", *ECCV 2024*, pp.78-96.

[31] Saha S., Hemal M. M., Eidmum M. Z. A., Mridha M. F. (2025), "Knowledge distillation approach for skin cancer classification on lightweight deep learning model", *Healthcare Technology Letters* Vol.12 (1), e12120.

[32] Saito T., Rehmsmeier M. (2015), "The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets", *PLoS ONE* Vol.10 (3), e0118432.

[33] Siegel R. L., Miller K. D., Jemal A. (2020), "Cancer statistics, 2020", *CA: A Cancer Journal for Clinicians* Vol.70 (1), pp.7-30.

[34] Tan M., Le Q. V. (2019), "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks", *ICML 2019*, PMLR 97, pp.6105-6114.

[35] Tschandl P., Rosendahl C., Kittler H. (2018), "The HAM10000 dataset: A large collection of multi-source dermatoscopic images of common pigmented skin lesions", *Scientific Data* Vol.5, pp.180161.

[36] Tu Z., et al. (2022), "MaxViT: Multi-Axis Vision Transformer", *ECCV 2022*, pp.459-479.

[37] Vasu P. K. A., et al. (2023), "FastViT: A Fast Hybrid Vision Transformer using Structural Reparameterization", *ICCV 2023*, pp.5785-5795.

[38] Venkatachalam C., Venkatachalam S., Balakrishnan A. (2025), "Enhanced skin cancer classification using modified EfficientNetV2L with adaptive early stopping mechanism", *Scientific Reports* Vol.15 (1), pp.38304.

[39] Wang A., et al. (2024), "RepViT: Revisiting Mobile CNN From ViT Perspective", *CVPR 2024*, pp.15909-15920.

[40] Wang M., Gao X., Zhang L. (2025), "Recent global patterns in skin cancer incidence, mortality, and prevalence", *Chinese Medical Journal* Vol.138 (2), pp.185-192.

[41] Wightman R. (2019), *PyTorch Image Models (timm)*, kho mã GitHub, https://doi.org/10.5281/zenodo.4414861

[42] Winata A., Andryani N. A. C., Gunawan A. A. S., Gaol F. L., Matsuo T. (2025), "MTAKD: multi-teacher agreement knowledge distillation for edge AI skin disease diagnosis", *Scientific Reports* Vol.15 (1), pp.44314.

[43] Woo S., et al. (2023), "ConvNeXt V2: Co-designing and Scaling ConvNets with Masked Autoencoders", *CVPR 2023*, pp.16133-16142.

[44] Youden W. J. (1950), "Index for rating diagnostic tests", *Cancer* Vol.3 (1), pp.32-35.

---

## 2. KẾ HOẠCH THỰC HIỆN

| Giai đoạn | Nội dung | Thời gian | Trạng thái |
|---|---|---|---|
| 1 | Xây dựng pipeline huấn luyện; tiền xử lý ISIC 2024 + PAD-UFES-20; thiết lập 5-fold CV patient-disjoint + test holdout độc lập | 06/2026 | ✅ xong |
| 2 | Huấn luyện 3 teacher (EfficientNetV2-M, ConvNeXtV2-Base, MaxViT-Base) — 5 fold mỗi mô hình | 07/2026 | ✅ xong (15/15) |
| 3 | **Ablation dữ liệu (Q1, Q6)**: nhánh ISIC-only ở tầng teacher (3 × 5 fold) **và tầng student** (4 × 5 fold); ablation tỉ lệ lấy mẫu 1:3 / 1:10 | 07–08/2026 | ✅ xong (15/15 + 20/20 + 10/10) |
| 4 | Huấn luyện 4 student nhánh baseline (không KD) — 5 fold mỗi mô hình | 07–08/2026 | ✅ xong (20/20) |
| 5 | Huấn luyện ma trận KD: 3 teacher × 4 student × 5 fold | 08–09/2026 | ✅ xong (60/60) |
| 6 | Export ExecuTorch `.pte` + cổng kiểm tra tương đương; benchmark on-device Pixel 6a; phân tích Pareto | 09/2026 | ✅ xong — parity **16/16 PASS ở cả PC lẫn Pixel 6a**; độ trễ (cold/steady/sustained) + bộ nhớ đỉnh đo 27/08; **Pareto chỉ còn 2 điểm** |
| 7 | Đánh giá chéo miền HAM10000; phân tích công bằng Fitzpatrick17k (nhóm tông da I–VI) | 09–10/2026 | ✅ xong cả hai bộ, kèm các biến thể kiểm độ nhạy của cách cắt tập |
| 8 | Tổng hợp 5-fold, **khoảng tin cậy paired bootstrap** trên cả ba miền, phân tích ảnh hưởng chất lượng teacher | 10/2026 | ✅ xong — CI đủ 3 miền + cả hai ablation + paired A-vs-B giữa hai ứng viên ship; quy luật r = −0,963 đã xác định |
| 9 | Viết luận văn (chương lý thuyết, thực nghiệm, kết quả và thảo luận) | 09–11/2026 | ✅ **bản đầy đủ 5 chương** tại `thesis/LUAN_VAN.md` |
| 10 | Rà soát toàn văn theo quy định trình bày của Trường; kiểm chứng trích dẫn; hoàn thiện, nộp và chuẩn bị bảo vệ | 09–11/2026 | 🔄 đang thực hiện — đã rà soát trích dẫn (12–16/09) và đóng phần lớn khoản bố cục; theo `docs/QUY_DINH_TRINH_BAY_LUAN_VAN.md` §12b còn **5 khoản mở** (định dạng Word; tên chương cuối; bốn nội dung bắt buộc của MỞ ĐẦU; thiếu công trình trong nước; Phụ lục B tồn tại hai bản), cộng với dựng slide bảo vệ |

> *Ghi chú.* **Đường găng đã đi qua**: giai đoạn 5 (ma trận KD 60 lượt) — từng là rủi ro số một của đề cương — đã hoàn tất cùng toàn bộ 140/140 lượt huấn luyện. Phần việc còn lại không cần GPU.
>
> *Hai rủi ro theo dõi trước đây đều đã hoá giải:* (i) giai đoạn 5 hoàn tất nên câu hỏi "teacher nào chưng cất tốt nhất" đã trả lời được — và câu trả lời hoá ra **phụ thuộc miền triển khai**, không có đáp án tuyệt đối; (ii) Fitzpatrick17k ban đầu chỉ tải được **23,4%** ảnh do 76% URL trong bản release đã chết, nhưng một bản mirror xác minh **byte-identical bằng md5** đã nâng độ phủ lên **99,98%** — và chính bản đầy đủ mới cho thấy bất bình đẳng nằm ở nhóm **trung bình**, điều mà bản 23,4% không những không thấy được mà còn dựng lên một tín hiệu sai.
>
> *Sai lệch so với đề cương ban đầu, ghi rõ để không bị hiểu nhầm:* (a) kiểm định thống kê đổi từ **paired t-test** sang **paired bootstrap CI**, vì 5 fold là 5 *mô hình* chấm trên cùng một tập test nên vi phạm giả định mẫu độc lập của t-test; (b) nhánh ablation **tắt hoàn toàn bộ lấy mẫu** bị loại **vì chi phí tính toán** (epoch tăng 42,9 lần), không phải vì đã thử và thất bại; (c) mục tiêu **hiệu chuẩn xác suất** từng nêu trong đề cương đã được thực hiện nhưng sau đó **gỡ khỏi luận văn** (09/09/2026) vì nằm ngoài phạm vi sáu câu hỏi Q1–Q6; kết quả được lưu riêng ở `reports/2026-09-09_calibration_findings.md`. Ghi chú thêm về các nhánh mở rộng, vì bản đề cương trước ghi gộp chúng thành một nhóm "chưa huấn luyện" và điều đó **không còn đúng**:

| Nhánh mở rộng | Tình trạng thực tế | Vị trí trong luận văn |
|---|---|---|
| Teacher đặc quyền (LUPI) nhận metadata bảng `tbp_lv_*` | **Đã huấn luyện** (2026-09-05, 15 fold) — metadata **không** cải thiện teacher (ΔpAUC = 0,0000) và **0/8 phép kiểm** có ý nghĩa ở tầng student | Ngoài phạm vi báo cáo; số liệu ở `reports/bootstrap_ci_dirA.md` |
| Chưng cất theo quan hệ (RKD) | **Đã huấn luyện** (nhánh đối chứng 2026-09-05/06, 10 fold) — RKD **làm giảm pAUC có ý nghĩa** cho student dung lượng thấp nhất | Ngoài phạm vi báo cáo; số liệu ở `reports/bootstrap_ci_dirA_decomp.md` |
| Biến thể MSE-logit · teacher nền tảng theo miền PanDerm | Đã cài đặt, **chưa huấn luyện** | Ngoài phạm vi |
| Cổng phát hiện ảnh ngoài phân phối | Mới ở mức thiết kế | Luận văn Mục 5.3 — **điều kiện bắt buộc** trước khi dùng thật |
| Lượng tử hoá INT8 | Không thực hiện | Luận văn Mục 1.7 ghi rõ **"ngoài phạm vi"**, không phải hướng phát triển |

Riêng chưng cất theo đặc trưng nằm ngoài phạm vi vì cần lớp chiếu để khớp số chiều — điều kiện mà ma trận 3 teacher × 4 student không cho phép; còn chưng cất theo quan hệ tuy **không** cần lớp chiếu nhưng vẫn phải lấy thêm vector đặc trưng của student ngoài logit và kèm các trọng số riêng phải tinh chỉnh lại cho bài toán nhị phân.
