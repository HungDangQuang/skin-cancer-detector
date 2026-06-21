# QA 004 — Knowledge Distillation vs Transfer Learning: phương pháp nào tốt hơn cho khoá luận này?

**Status:** verified 2026-06-21 · experiment-design

## Question
Trong khoá luận này đang sử dụng knowledge distillation, tôi đang cân nhắc với
transfer learning. Hãy so sánh giữa 2 phương pháp này, phương pháp nào sẽ tốt hơn
trong khoá luận này?

## Answer
**Đây không phải lựa chọn loại trừ — khoá luận đang dùng cả hai, và đó là cách
đúng.** Knowledge Distillation (KD) và Transfer Learning (TL) trả lời hai câu hỏi
khác nhau, nên không nên đóng khung "chọn cái nào".

- **Transfer Learning** = khởi tạo backbone bằng trọng số pre-trained ImageNet rồi
  fine-tune trên dữ liệu da liễu. Trong repo, *mọi* mô hình — teacher
  EfficientNet-B4 lẫn cả 3 student — đều load `pretrained: true`
  ([efficientnet.py:14-17](../src/models/efficientnet.py#L14-L17),
  [mobilenet.py:17](../src/models/mobilenet.py#L17),
  [mobilevit.py:17](../src/models/mobilevit.py#L17); config
  [efficientnet_b4.yaml:4](../configs/teacher/efficientnet_b4.yaml#L4) và 3 config
  student). Nghĩa là **TL là nền tảng có ở mọi arm**, không phải một phương án
  thay thế.
- **Knowledge Distillation** = lớp *cộng thêm* trên nền TL: student vừa load
  ImageNet weights, vừa học soft labels (T=4.0) từ teacher B4 đã fine-tune trên
  *chính dữ liệu da liễu* này. Soft labels mang thông tin về độ giống/độ khó giữa
  các ca mà hard label 0/1 không có.

Do đó, "so sánh TL vs KD" trong khoá luận này **chính là** so sánh có kiểm soát đã
thiết kế sẵn giữa hai arm:

| Arm | `training=` | Nội dung | Run-dir |
|---|---|---|---|
| **Baseline (TL thuần)** | `baseline` (`use_kd: false`) | ImageNet weights + fine-tune trên hard labels (focal loss), không teacher | `baseline_<student>/` |
| **KD (TL + KD)** | `distillation` (`use_kd: true`) | ImageNet weights + soft labels từ teacher | `kd_<teacher>_to_<student>/` |

Cùng hyperparameter / seed / split, chỉ khác KD (xác nhận ở
[baseline.yaml](../configs/training/baseline.yaml) vs
[distillation.yaml](../configs/training/distillation.yaml); cơ chế `use_kd` mô tả
trong CLAUDE.md "Baseline (no-KD) student training").

**Phương pháp nào tốt hơn?** Bằng chứng định lượng trên student MobileNetV3-Large
(test set độc lập, đọc 2026-06-21) cho thấy **KD tốt hơn TL thuần** ở các chỉ số
quan trọng:

| Chỉ số | Baseline (TL) | KD (TL+KD) | Δ (KD − TL) |
|---|---|---|---|
| pauc_at_tpr80 | ~0.1858 | 0.1881 | **+0.0023** |
| auc_roc | ~0.9852 | 0.9873 | **+0.0021** |
| sensitivity | ~0.9336 | 0.9552 | **+0.0216** |
| specificity | ~0.9564 | 0.9364 | −0.0200 |

KD đổi một ít specificity để lấy **sensitivity cao hơn rõ rệt** (+2.2 điểm %) —
đánh đổi có lợi cho bài toán sàng lọc ung thư (bỏ sót ác tính nguy hiểm hơn báo
động giả). KD cũng nhỉnh hơn nhẹ ở pAUC@TPR80 (chỉ số chính) và AUC. Ngoài ra
student KD còn **vượt cả teacher B4** ở pAUC (0.1881 vs 0.1785) và sensitivity
(0.9552 vs 0.9087) — xác nhận KD mang giá trị cộng thêm thật, không chỉ là TL.

**Caveat về số liệu:** số KD và teacher lấy từ `aggregated.md` (mean ± std qua
5 fold, qua `aggregate_folds.py`). Số baseline ở đây tự tính tay từ 5 file
`fold_*/test_metrics.json` vì **arm baseline chưa chạy `aggregate_folds.py`** (chưa
có `aggregated.md`). Trước khi trích vào báo cáo cuối, cần chạy `22_aggregate_folds`
cho các `baseline_*` để có mean ± std chính thức, và lặp lại so sánh cho B0 +
MobileViT-S (hiện baseline của chúng cũng chưa aggregate).

## Evidence
- [src/models/efficientnet.py:14-17](../src/models/efficientnet.py#L14-L17),
  [mobilenet.py:17](../src/models/mobilenet.py#L17),
  [mobilevit.py:17](../src/models/mobilevit.py#L17) — mọi backbone dùng
  `pretrained=True` ⇒ TL là nền tảng chung của mọi arm.
- [configs/teacher/efficientnet_b4.yaml:4](../configs/teacher/efficientnet_b4.yaml#L4)
  + 3 config student `pretrained: true` — teacher lẫn student đều TL.
- [configs/training/baseline.yaml](../configs/training/baseline.yaml) (`use_kd: false`)
  vs [configs/training/distillation.yaml](../configs/training/distillation.yaml)
  (`use_kd: true`, `temperature: 4.0`, `alpha: 0.3`) — hai arm chỉ khác KD.
- CLAUDE.md "Baseline (no-KD) student training — FIXED 2026-06-04" — cơ chế
  `use_kd` chọn `Trainer` vs `KDTrainer`, run-dir `baseline_*` vs `kd_*`.
- `experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/aggregated.md` (đọc
  2026-06-21) — KD: pauc 0.1881±0.0010, auc 0.9873, sens 0.9552, spec 0.9364.
- `experiments/runs/teacher/efficientnet_b4/aggregated.md` (đọc 2026-06-21) —
  teacher: pauc 0.1785, sens 0.9087 ⇒ student KD vượt teacher.
- `experiments/runs/baseline_mobilenetv3_large/fold_{0..4}/test_metrics.json` (đọc
  2026-06-21) — baseline per-fold; mean tự tính: pauc ~0.1858, auc ~0.9852, sens
  ~0.9336, spec ~0.9564. **Chưa qua `aggregate_folds.py` — re-confirm bằng
  `aggregated.md` trước khi trích số cuối.**

## For the thesis
Transfer Learning và Knowledge Distillation không phải hai phương án thay thế:
toàn bộ mô hình trong nghiên cứu đều khởi tạo bằng transfer learning (backbone
pre-trained ImageNet), và Knowledge Distillation được đánh giá như một đóng góp
*bổ sung* trên nền đó thông qua so sánh có kiểm soát giữa arm baseline (chỉ TL) và
arm KD (TL + KD) với cùng hyperparameter, seed và data split. Trên MobileNetV3-Large,
KD cải thiện sensitivity (~+2,2 điểm %) và pAUC@TPR≥80% so với baseline, đồng thời
giúp student vượt cả teacher — cho thấy giá trị cộng thêm của distillation đối với
bài toán sàng lọc ung thư da trên thiết bị di động.
