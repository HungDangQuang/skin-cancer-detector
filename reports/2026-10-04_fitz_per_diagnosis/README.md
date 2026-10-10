# III-b mất độ nhạy ở đâu? Phân tích theo chẩn đoán trên Fitzpatrick17k-C (04/10/2026, chỉ chẩn đoán)

Câu hỏi của tác giả: đã thử nhiều cách mà III-b vẫn không đạt — còn hướng nào? Trước khi chọn hướng, file này đo III-b
mất độ nhạy ở loại tổn thương nào. P0 (`kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`, `best_model_auprc.pth`),
ngưỡng app `pad_sens90`, tập Fitzpatrick17k-C (tập chấm III-b từ 04/10). Chẩn đoán lấy từ cột `label` của CSV
Fitzpatrick17k-C (nguồn và sha256: `reports/2026-10-04_review_v2_checks/README.md`). Chạy lại:
`python3 reports/2026-10-04_fitz_per_diagnosis/per_diagnosis.py <Fitzpatrick17k-C csv>`; kết quả `output.md`.

## Nhãn "ác tính" của Fitzpatrick17k so với dữ liệu train

- **Actinic keratosis** là "malignant" trong Fitzpatrick17k (`three_partition_label`), nhưng ACK của PAD-UFES-20 được
  gán **lành** khi train (`configs/data/pad_ufes_20.yaml:19`; `src/data/preprocessing.py:263-264`). Model được dạy gọi
  AK là lành, rồi III-b tính AK là ca ác bị bỏ sót.
  DDI cũng gán 4 ảnh actinic keratosis là lành (`malignant = False` trong `ddi_metadata.csv`). ⇒ **lệch nhãn thật**.
- **Mycosis fungoides** và **Kaposi sarcoma**: ISIC 2024 và PAD-UFES-20 chỉ có BCC/SCC/melanoma ở phía ác, nhưng **DDI có
  32 ảnh mycosis fungoides và 6 ảnh Kaposi sarcoma gắn nhãn ác** (`data/raw/DDI/…zip` → `ddi_metadata.csv`; 171 ảnh ác của
  DDI gồm 18 chẩn đoán). DDI được append vào train của `runs_newsplit_ddi` (CLAUDE.md, mục Data integrity) ⇒ model **có
  thấy** MF/KS là ác, nhưng **rất ít**: 38 ảnh, trong khi một fold train có khoảng 1.077 ca ác (fold_0, CLAUDE.md).

## Kết quả (`output.md`)

- Ba nhóm AK, mycosis fungoides, Kaposi sarcoma (369 / 1.623 ca ác của fold 4): độ nhạy tại ngưỡng app 0,30–0,36 ở fold 4
  (cộng 5 fold 0,48–0,55); AUC so với ảnh lành 0,58–0,61 (trung bình 5 fold) — gần đoán ngẫu nhiên.
- **Teacher không cứu được nhóm này:** với AK / mycosis fungoides / Kaposi sarcoma, AUC của student P0, teacher
  `efficientnetv2_m` và teacher `convnextv2_base` (teacher của P1) đều trong khoảng 0,54–0,62. `convnextv2_base` khá hơn ở
  các loại melanoma (vd superficial spreading 0,667 so với 0,602 của student) nhưng BCC/SCC ngang nhau. ⇒ với AK/MF/KS,
  dung lượng model không phải nút thắt; với melanoma thì teacher mạnh hơn có giúp một phần. Hai teacher đều train **không**
  cùng công thức với student (thiếu sampler theo nguồn, checkpoint pAUC — S16).
- Bỏ ba nhóm đó khỏi nhóm ác (chỉ để chẩn đoán): độ nhạy theo tông 0,603 / 0,503 / 0,508 → 0,660 / 0,585 / 0,582 — tăng
  0,06–0,08 nhưng **vẫn dưới 0,80** với cả khoảng CI. Ngay cả BCC và SCC (nhiều nhất trong train) chỉ đạt 0,66–0,68 ở
  fold 4 (cộng 5 fold 0,80 / 0,80, nhưng các fold khác có ngưỡng thấp hơn và độ đặc hiệu thấp hơn) ⇒ nhiều khả năng phần
  còn lại là chênh lệch miền ảnh (ảnh atlas, khung hình rộng) — suy luận, chưa kiểm bằng phép thử riêng.

**Giới hạn:** độ nhạy tại ngưỡng là của một fold (cột "cộng 5 fold" dùng ngưỡng riêng của từng fold, điểm vận hành khác
nhau); ngưỡng app post-hoc; Fitzpatrick đã được nhìn nhiều lần; CSV Fitzpatrick17k-C chưa ghim commit. **Dùng bảng này để
chọn hướng làm tiếp là biến Fitzpatrick thành tập phát triển** (`acceptance-gates.md` §4 #9, #18): mọi kết quả III-b về
sau phải khai post-hoc, và muốn có nhãn đứng được thì cần tập chưa ai chạm (U8). Nếu dùng nó để đổi định nghĩa nhóm ác
của III-b thì đó thêm một lần đổi mốc post-hoc (§4 #13).
