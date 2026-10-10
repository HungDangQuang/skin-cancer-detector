# Đăng ký trước — thử CPUBone-B1 làm student (10/10/2026)

> Viết và commit **trước** khi train. Khuôn theo `docs/PREREG_CANDIDATE2_2026-10-02.md`.
> Đây là thí nghiệm **khám phá, post-hoc**: mọi tập test (in-domain, HAM10000, Fitzpatrick17k) đã được nhìn ở
> vòng 1 và vòng 2, và ý tưởng thử CPUBone đến sau khi đã thấy phán quyết 04/10 (P0 KHÔNG ĐẠT tạm vì III-b).

## 1. Câu hỏi

Tác giả cho rằng bốn student hiện tại (2023–2024) đã cũ. Thí nghiệm hỏi: **một backbone mới hơn, thiết kế riêng cho
CPU (CPUBone, arXiv 2603.26425, 27/03/2026), có cho student tốt hơn P0 trên cùng công thức không?**

Phạm vi so sánh: chỉ với các arm cùng teacher `efficientnetv2_m` trong `runs_newsplit_ddi` (splits v2), tức P0
(MobileNetV4) và P2 (RepViT).
Không so với ma trận 3×4 trên splits v1 (rò rỉ bệnh nhân, CLAUDE.md "Data integrity").

## 2. Mô hình

- Student: `cpubone_b1` = timm `cpubone_b1_bfrobust.r224_in1k` (12,4 triệu tham số theo bài báo), dropout 0,2.
- Lý do chọn B1, quyết định **trước** mọi dữ liệu của CPUBone: cỡ gần nhất với dải student hiện có (6,8–12,6 triệu
  theo bài báo gốc của từng kiến trúc, tức kèm đầu 1000 lớp — `docs/DE_CUONG.md` Bảng 2), nên so sánh với P0
  (MobileNetV4, 9,2 triệu cùng cách tính) công bằng về dung lượng. Khác các student khác, CPUBone giữ một head MLP khi
  `num_classes=0` (`in_conv` 256→1536 + `pre_classifier` 1536→1600), nên đặc trưng vào đầu 1 logit có 1600 chiều;
  `infer_backbone_out_dim` đo đúng chiều này. Số tham số thực của student chưa đo (sẽ có trong `reports/benchmark/`). Bản `_bfrobust` vì timm không có trọng số cho
  `cpubone_b1` thường và README CPUBone khuyên dùng bản này. timm còn có `cpubone_b1_dwnorm.timm_r256_in1k`, nhưng
  bản đó pretrain ở 256×256 còn pipeline dùng 224×224, nên bị loại.
- **Lệch so với kế hoạch đã bàn:** bỏ bước đo tốc độ trên Pixel 6a trước khi train (tác giả muốn có kết quả trước).
  Hệ quả: A1/A3/A4 cho CPUBone CHƯA ĐO cho tới khi export + parity + đo máy.
- **Biến số thêm so với P0:** server phải nâng timm 1.0.28 → **1.0.30** (bản cũ không có module cpubone). Teacher và
  P3 chạy trên timm 1.0.30, còn P0 đã train trên timm cũ. Checkpoint teacher nạp `strict`, nên lệch khoá sẽ báo lỗi;
  lệch số học nhỏ thì không phát hiện được. Phiên bản timm thực tế được ghi vào log driver.

## 3. Các arm (đúng công thức P0)

Server `vastnew`, `GPU=0`, chạy tuần tự, seed 42, AUG light, 5 fold, splits `data/splits/` dựng lại 22/09 (+656 dòng DDI).

```
E="output_dir=experiments/runs_newsplit_ddi run_suffix=__srcsamp data.sampler_stratify_by=source training.callbacks.checkpoint.extra_monitors=[auprc]"
1. bash run/train_student.sh STUDENT=cpubone_b1 TEACHER=efficientnetv2_m TRAINING=distillation GPU=0 EXTRA="$E"
2. bash run/train_student.sh STUDENT=cpubone_b1 TEACHER=efficientnetv2_m TRAINING=baseline     GPU=0 EXTRA="$E"
```

Run-dir mới: `kd_efficientnetv2_m_to_cpubone_b1__srcsamp` (gọi là **P3**) và `baseline_cpubone_b1__srcsamp`.
Teacher dùng lại `experiments/runs_newsplit_ddi/teacher/efficientnetv2_m` (teacher của P0). Không run-dir nào bị ghi đè.

## 4. Luật chọn (chỉ val) — giống prereg vòng 2 §4, §7.1

`bash run/select_candidate.sh CANDIDATES="P0=… P3=…"` (thứ tự đăng ký: P0 trước):
trung bình 5 fold AUPRC trên hàng PAD của `val_predictions_auprc.csv`; checkpoint `best_model_auprc.pth`; P3 phải hơn
P0 **≥ 0,005**, hoà thì giữ P0; fold ship = trung vị val AUPRC. Bước chọn chạy ngay sau khi train xong (driver
`.tmp/cpubone_driver.sh`, chỉ đọc file `val_*`), rồi driver **dừng**. `selection.{json,md}` được **commit vào git
trước** khi chạy `.tmp/cpubone_eval.sh` (aggregate, eval ngoài miền, CI) hay mở bất kỳ file test nào của P3.

**Không nhìn số test trong lúc train:** trainer in metric test vào `logs/train_student_*.log` cuối mỗi fold (đúng đường
gây sự cố ở vòng 2). Theo dõi tiến độ chỉ bằng `bash run/progress.sh`, file `.tmp/cpubone_status/*.ok|failed` và các
dòng `[cpubone]` của `.tmp/cpubone_driver.log`; **không** `tail`/`grep` log train cho tới khi đã commit kết quả chọn.

## 5. Báo cáo (không đổi kết quả chọn ở §4)

Như vòng 2 (`.tmp/cand2_eval.sh` trên server), qua `.tmp/cpubone_eval.sh`: aggregate (bản chính + `_auprc`); eval ngoài miền HAM10000 headline +
Fitzpatrick17k 4 biến thể với `CKPT_NAME=best_model_auprc.pth`, vào `reports/external_newsplit_srcsamp_auprc`;
CI bootstrap ghép cặp: **C2** = P3 − teacher `efficientnetv2_m`, **C1** = P3 − `baseline_cpubone_b1__srcsamp`,
in-domain (`SUBGROUP=source`), HAM headline, Fitzpatrick headline (`SUBGROUP=tone_group`). III-b theo
`acceptance-gates.md` nếu P3 được chọn.

## 6. Diễn giải đã cam kết

- P3 không thắng ở §4 → báo cáo "CPUBone-B1 không tốt hơn MobileNetV4 trên công thức này", không đổi ứng viên ship.
- P3 thắng ở §4 → mới xét ba trụ; ship chỉ khi qua các cổng và export/parity/đo máy (A1/A3/A4).
- Không chọn lại biến thể CPUBone, checkpoint hay ngưỡng sau khi xem test. Thêm biến thể khác (B0/B2) = vòng mới,
  đăng ký riêng.
