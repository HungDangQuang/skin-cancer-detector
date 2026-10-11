# CPUBone-B1 (P3) — đánh giá đầy đủ, so với các student khác (CHỈ BÁO CÁO, khám phá)

> **Không đổi được ứng viên.** Luật chọn chỉ trên val (commit `6475d76`, trước mọi file test) giữ **P0**; kết luận đã đăng
> ký (`docs/PREREG_CPUBONE_2026-10-10.md` §6): «CPUBone-B1 không tốt hơn MobileNetV4 trên công thức này» — giữ nguyên.
>
> **Khám phá, post-hoc.** Mọi phép so dưới đây (trừ C1/C2 đã đăng ký ở prereg §5) được đề ra 11/10/2026 **sau** khi đã thấy
> kết quả test của P3. Không hiệu chỉnh đa phép kiểm: riêng §2 đã có 3 cặp × 5 metric × 8 tập/nhóm (hơn 100 khoảng) — các ô
> sát ranh giới (cận cách 0 dưới ~0,002) **không** nên đọc như phát hiện. CI chỉ phản ánh sai số lấy mẫu tập test, không gồm
> biến thiên giữa các lần train (mỗi run một seed). Không chọn ứng viên từ HAM/Fitzpatrick (`acceptance-gates.md` §4 #9, #18).
> Bổ sung cho `reports/2026-10-11_cpubone_P3_vs_P0_external.md`.

**Ứng viên** (splits v2, `experiments/runs_newsplit_ddi`, công thức `__srcsamp`, checkpoint `best_model_auprc.pth`):
P0 = `efficientnetv2_m → mobilenetv4_conv_medium` (ứng viên ship) · P1 = `convnextv2_base → mobilenetv4_conv_medium` ·
P2 = `efficientnetv2_m → repvit_m1_0` · **P3 = `efficientnetv2_m → cpubone_b1`**. P1 khác P3 cả teacher lẫn student, nên
phép so P3 − P1 lẫn hai biến (prereg §1 chỉ nhắm P0/P2, cùng teacher). FastViT-SA12 và EfficientFormerV2-S2 chỉ có trên
splits v1 (rò rỉ bệnh nhân), nên **không** có ở phần độ chính xác; chỉ có ở phần hiệu năng (theo kiến trúc).

## 1. Tóm tắt

- **Ảnh điện thoại PAD (miền app):** AUPRC của P3 thấp hơn P0, khoảng ghép cặp vừa đủ không chứa 0 (−0,0145 [−0,0280;
  −0,0012]); không phân biệt được với P1; cao hơn P2. Tại ngưỡng app, cổng III-a của P3 = **CHƯA CHỨNG MINH (tạm)** (độ
  nhạy PAD 0,852 [0,794; 0,895], cận dưới < 0,80), trong khi P0, P1, P2 đều ĐẠT (tạm) III-a.
- **Ngoài miền:** AUPRC của P3 cao hơn P0, P1, P2 trên HAM10000 và Fitzpatrick17k headline, khoảng ghép cặp không chứa 0.
  Ba biến thể Fitzpatrick còn lại (crop70, crop50, with_non_neoplastic) cùng chiều, nhưng là **cùng bộ ảnh** (cắt hoặc thêm
  lớp), không phải xác nhận độc lập. Trên HAM, pAUC@TPR80 của P3 lại thấp hơn P0 (−0,0027 [−0,0052; −0,0000], sát ranh giới).
- **Tông da:** III-b **KHÔNG ĐẠT (tạm)** như P0, P1, P2 (độ nhạy Fitzpatrick17k-C tại ngưỡng app 0,648 / 0,535 / 0,500).
- **Triển khai:** `.pte` XNNPACK export được, **parity PASS** (max|Δlogit| 8,5e-06). Đồ thị CPUBone trong `.pte` bị chia
  thành 62 phân đoạn XNNPACK, xen 167 lệnh kernel ngoài delegate; `.pte` MobileNetV4 là 1 phân đoạn. Một proxy x86 qua
  ExecuTorch cho CPUBone chậm hơn (trung vị 18,54 so với 5,60 ms) — proxy, không phải số điện thoại. **Pixel 6a chưa đo.**

## 2. Độ chính xác — so sánh ghép cặp Δ(P3 − X), AUPRC

B = 2000, seed 42, mỗi replicate chấm cả 5 fold trên cùng tập chỉ số dòng rồi lấy trung bình; `*` = khoảng 95% không chứa 0.
Nguồn: `reports/ci_cpubone_P3vsAll_<tập>.md` (§3b toàn tập, §6 theo `source`). Tên tắt `x_p0..x_p3` → run-dir ở trên (cây
symlink `.tmp/ci_p3all/` trên server; điểm ước lượng §1 khớp các file CI riêng của từng run: `ci_gates_srcsamp_*`,
`ci_cand2_P{1,2}_*`, `ci_cpubone_P3_*`).

| Tập | Số dòng | vs P0 | vs P1 | vs P2 |
|---|---|---|---|---|
| **PAD** (in-domain, ảnh điện thoại) | 397 | −0,0145 [−0,0280; −0,0012] * | −0,0180 [−0,0414; +0,0012] | +0,0390 [+0,0131; +0,0641] * |
| ISIC (in-domain) | 58.696 | +0,0199 [+0,0021; +0,0425] * | −0,0013 [−0,0257; +0,0193] | +0,0261 [+0,0013; +0,0554] * |
| In-domain gộp | 59.093 | −0,0028 [−0,0149; +0,0103] | −0,0108 [−0,0293; +0,0069] | +0,0486 [+0,0259; +0,0715] * |
| HAM10000 headline | 7.470 | +0,0320 [+0,0214; +0,0422] * | +0,0876 [+0,0733; +0,1015] * | +0,0656 [+0,0508; +0,0807] * |
| Fitzpatrick17k headline | 4.320 | +0,0183 [+0,0119; +0,0244] * | +0,0180 [+0,0110; +0,0246] * | +0,0520 [+0,0433; +0,0613] * |
| Fitzpatrick17k crop70 | 4.320 | +0,0159 [+0,0100; +0,0215] * | +0,0113 [+0,0045; +0,0181] * | +0,0487 [+0,0400; +0,0574] * |
| Fitzpatrick17k crop50 | 4.320 | +0,0100 [+0,0046; +0,0155] * | +0,0086 [+0,0017; +0,0158] * | +0,0387 [+0,0307; +0,0467] * |
| Fitzpatrick17k with_non_neoplastic | 16.012 | +0,0195 [+0,0130; +0,0257] * | +0,0338 [+0,0260; +0,0413] * | +0,0544 [+0,0460; +0,0630] * |

Các ô âm có `*` ở metric khác (đủ danh sách trên 6 file): PAD vs P1 — AUC-ROC −0,0158 [−0,0287; −0,0038], Sens@90Spec
−0,1143 [−0,1673; −0,0088]; HAM vs P0 — pAUC@TPR80 −0,0027 [−0,0052; −0,0000]. Không so AUPRC giữa các tập (tỉ lệ ác tính khác).

Điểm ước lượng AUPRC (cùng file CI, §1 và §4) — **cao nhất trong 4 ứng viên P0–P3** in đậm:

| | PAD | ISIC | HAM10000 | Fitzpatrick17k headline |
|---|---|---|---|---|
| P0 | 0,8584 | 0,0673 | 0,4997 | 0,7022 |
| P1 | **0,8619** | **0,0885** | 0,4441 | 0,7024 |
| P2 | 0,8049 | 0,0611 | 0,4661 | 0,6684 |
| P3 | 0,8439 | 0,0872 | **0,5317** | **0,7205** |

## 3. Theo bộ cổng (chỉ báo cáo — P3 không phải ứng viên)

### 3.1 Tại ngưỡng app (fold ship, `pad_sens90`), cùng cách chấm như P0/P1/P2

Fold ship của P3 = **fold 4** (trung vị AUPRC toàn bộ val, `val_metrics_auprc.json`: 0,6033 · 0,6656 · **0,7136** · 0,7624 ·
0,7704), trùng P0/P1/P2. Ngưỡng `pad_sens90` fold 4 = 0,5752 (`reports/2026-10-11_cpubone_app_threshold/P3/summary.csv`,
sinh bằng `reports/2026-10-02_threshold_options/threshold_options.sh` với `RUN=` của P3). Wilson 95%, một fold; Wilson III-a
tính từ số đếm của dòng `4,pad_sens90` (161/189, 208 − 57 = 151/208), chưa lưu thành file riêng.

| | III-a PAD độ nhạy | III-a PAD độ đặc hiệu | III-b Fitz17k-C độ nhạy sáng · TB · tối | III-b Fitz17k-C độ đặc hiệu sáng · TB · tối |
|---|---|---|---|---|
| P0 | 0,873 [0,818; 0,913] | 0,731 [0,667; 0,786] | 0,603 · 0,503 · 0,508 | 0,742 · 0,813 · 0,824 |
| P1 | 0,894 [0,842; 0,930] | 0,707 [0,642; 0,764] | 0,706 · 0,646 · 0,723 | 0,655 · 0,720 · 0,624 |
| P2 | 0,862 [0,806; 0,904] | 0,673 [0,607; 0,733] | 0,696 · 0,530 · 0,546 | 0,609 · 0,714 · 0,768 |
| **P3** | 0,852 [0,794; 0,895] | 0,726 [0,662; 0,782] | 0,648 [0,617; 0,678] · 0,535 [0,493; 0,576] · 0,500 [0,415; 0,585] | 0,691 [0,658; 0,721] · 0,755 [0,716; 0,790] · 0,784 [0,704; 0,847] |

Nguồn P0/P1/P2: `reports/2026-10-04_round2_report_only.md` §3. P3: `…/P3/tone_at_app_threshold_fitz17kC.txt` (toàn bộ
headline: `…/P3/tone_at_app_threshold.txt` — độ nhạy 0,649 [0,621; 0,675] · 0,565 [0,530; 0,600] · 0,500 [0,433; 0,567]).
Nhãn (mốc chốt tạm S_min 0,80, Sp_min 0,60): **III-a = CHƯA CHỨNG MINH (tạm)** (ô độ nhạy: cận dưới 0,794 < 0,80 ≤ cận
trên; ô độ đặc hiệu đạt); **III-b = KHÔNG ĐẠT (tạm)** (cận trên độ nhạy mọi tông < 0,80). P0, P1, P2: III-a ĐẠT (tạm),
III-b KHÔNG ĐẠT (tạm).

**Hành vi tại ngưỡng (bắt buộc báo cáo), fold 4** — P3 `pad_sens90` 0,5752 (P0 0,5705 để đối chiếu):
PAD gắn cờ 57/208 ảnh lành (P0 56/208); Fitzpatrick bắt 1.307/2.160 ca ác, gắn cờ 609/2.160 ảnh lành (P0 1.225 · 498);
ISIC bắt 3/76, gắn cờ 13/58.620 (P0 5/76 · 23). Ngưỡng Youden toàn cục (0,2306) của P3 gắn cờ 206/208 ảnh lành PAD và
2.155/2.160 ảnh lành Fitzpatrick — không dùng được cho app, như P0.

### 3.2 C1, C2 (đã đăng ký) và các cổng báo cáo

**C2** (P3 − teacher `efficientnetv2_m`, ΔAUPRC, `lo > −δ`, δ = 0,05 × AUPRC teacher): PAD +0,0473 [+0,0247; +0,0714]
(teacher 0,7966, δ 0,0398) · Fitz +0,0251 [+0,0179; +0,0319] (0,6954, 0,0348) · HAM +0,0379 [+0,0246; +0,0517] (0,4938,
0,0247) — cả ba **ĐẠT (tạm)**, như P0. Lưu ý như với P0: teacher train **không** có sampler theo nguồn, nên phép kiểm
không kém dễ đạt hơn thực tế; C2 đạt không nói KD có tác dụng.

**C1** (P3 − `baseline_cpubone_b1__srcsamp`, ΔAUPRC): PAD −0,0143 [−0,0370; +0,0083] (không phân biệt được, như P0) · HAM
+0,0892 [+0,0778; +0,1013] * · Fitzpatrick +0,0306 [+0,0231; +0,0386] * (`reports/ci_cpubone_P3_*.md`).

**B1** (ISIC, báo cáo): AUC-ROC 0,9483 [0,9267; 0,9659] · pAUC@TPR80 0,1607 [0,1442; 0,1757].
**B2/B3/B4** — Sens@Spec80, trung bình 5 fold: PAD 0,8275 [0,7505; 0,8882] · Fitzpatrick 0,5114 [0,4853; 0,5355] · HAM
0,7388 [0,7163; 0,7605] (P0: 0,8180 · 0,4946 · 0,7259).
**C4b** (chênh AUC-ROC giữa các tông, Fitzpatrick headline, P3): sáng − trung bình +0,0360 [+0,0064; +0,0668] * · tối −
sáng +0,0010 [−0,0470; +0,0451] · tối − trung bình +0,0371 [−0,0140; +0,0848] (`reports/ci_cpubone_P3vsAll_fitzpatrick17k_headline.md` §4).

## 4. Hiệu năng triển khai

| Student | Tham số (M) | GFLOPs | FP32 (MiB) | x86 eager 1 luồng, trung vị (ms) | `.pte` | Phân đoạn XNNPACK | Pixel 6a duy trì @4 luồng (ms) |
|---|---|---|---|---|---|---|---|
| **CPUBone-B1** | 10,84 | 1,489 | 41,5 | 39,8 | 41,44 MiB, parity PASS | **62 + 167 lệnh ngoài delegate** | **chưa đo** |
| MobileNetV4-Conv-M | 8,436 | 1,653 | 32,4 | 38,1 | 32,11 MiB* | 1 | 39,5* |
| RepViT-M1.0 | 6,403 | 2,214 | 24,6 | 86,5 | 24,46 MiB* | — | 57,2* |
| FastViT-SA12 | 10,557 | 2,962 | 40,4 | — | 40,35 MiB* | — | 113,9* |
| EfficientFormerV2-S2 | 12,132 | 2,493 | 46,7 | — | 47,98 MiB* (portable) | — | 3.908,2* |

- Ba hàng đầu (tham số, GFLOPs, FP32, x86 eager) đo **cùng phiên** 11/10/2026 05:30 UTC, checkpoint fold 4 `_auprc`, 100
  lần, 1 luồng (`reports/benchmark/_cpubone_session_20261011/*.json` + `.log`). FastViT/EfficientFormerV2: tham số, GFLOPs,
  FP32 từ `reports/benchmark/*.json` (phiên 26/08); không có x86 cùng phiên (server không còn checkpoint của chúng).
- `*` = lượt Pixel 6a 27/08 (`reports/ondevice_latency.csv:22-25`, theo kiến trúc, `.pte` khác bản ship) — **không** so được
  với một lượt đo CPUBone khác phiên (nhiệt ~14%/°C, sàn lặp lại 7,70%).
- Parity: `reports/mobile_benchmark/parity_cpubone_b1.json` — max|Δlogit| 8,521e-06, 0/100 vượt 1e-3. Checkpoint dùng cho cả
  `ref_cpubone_b1.csv` và `.pte` là fold 4 `best_model_auprc.pth` (sha256 `1b62b180…`), `.pte` sha256 `8e3e1aec…`, backend
  `xnnpack` — `reports/mobile_benchmark/cpubone_pte_checks_20261011/provenance.txt`.
- Phân đoạn: đếm lệnh trong chương trình `.pte` (`…/cpubone_pte_checks_20261011/pte_ops.py` → `pte_ops.txt`). CPUBone: 62
  lệnh gọi delegate; ngoài delegate 167 lệnh — `expand_copy` 40, `native_group_norm` 20, `mul` 20, `logical_not` 20,
  `split_with_sizes_copy` 10, `eq` 10, `full_like` 10, `any` 10, `where` 10, `alias_copy` 10, `upsample_nearest2d` 5,
  `native_layer_norm` 1, `squeeze_copy` 1. MobileNetV4 (`.pte` ship): 1 lệnh gọi delegate + `squeeze_copy` 1.
- Proxy x86 qua ExecuTorch runtime (`pte_timing.py` → `pte_x86_timing.txt`; cùng phiên, xen kẽ khối, 200 lần/model, số
  luồng mặc định không ghim): CPUBone trung vị 18,54 ms, MobileNetV4 5,60 ms; p90 của cả hai ~87 ms (nhiễu lịch luồng trên
  64 lõi). Proxy x86 từng xếp đúng thứ tự nhưng không phân giải được độ lớn so với điện thoại, nên chỉ đọc như chiều.

## 5. Đọc kết quả

1. **Miền app (ảnh điện thoại PAD):** P3 không tốt hơn P0 — AUPRC thấp hơn với khoảng ghép cặp sát ranh giới, và III-a chỉ
   CHƯA CHỨNG MINH (tạm) trong khi P0 ĐẠT (tạm). Đây là miền quyết định của luận văn.
2. **Ngoài miền:** AUPRC của P3 cao nhất trong 4 ứng viên P0–P3 trên HAM10000 và Fitzpatrick17k headline; khoảng cách theo
   tông da vẫn còn (III-b KHÔNG ĐẠT (tạm), chênh sáng − trung bình có ý nghĩa).
3. **Triển khai:** `.pte` đúng số học, nhưng đồ thị bị phân mảnh trong XNNPACK và proxy x86 chậm hơn MobileNetV4. Bài báo
   CPUBone đo bằng TFLite/ONNX Runtime và **không** so với MobileNetV4-Conv-M ở bảng phân loại, nên chưa biết trên Pixel 6a
   CPUBone nhanh hay chậm hơn MobileNetV4; nguyên nhân của chênh lệch proxy (các phép ngoài delegate) chưa được xác nhận bằng
   profiler. Cần đo trên máy.
4. **Không tách được nguyên nhân** của các chênh lệch độ chính xác: khác kiến trúc **và** khác timm lúc train (P3 1.0.30, P0
   cũ hơn); với P1 còn khác teacher. Một biến thể CPUBone, một seed.

## 6. Bước còn lại cần thiết bị (tác giả)

Đo Pixel 6a **cùng phiên** với MobileNetV4 (và RepViT, FastViT nếu muốn bảng đầy đủ): rút sạc, chế độ máy bay, thứ tự xáo có
seed, 30 warmup + 200 vòng, 4 luồng, lượt 300 s cho cột duy trì. `.pte` đã có trên Mac: `exports/executorch_cpubone/cpubone_b1.pte`
(không commit; sha256 `8e3e1aec…`).

## Chưa báo cáo ở đây / chưa verify được

- Chưa báo cáo: PPV/NPV tại ngưỡng app; HAM10000 theo `dx`; khoảng cách val − test; III-b theo D2/D4 (`reports/2026-10-04_review_v2_checks`).
- Độ trễ Pixel 6a (I-1/A1) và chạy trên máy (A3/A4) của CPUBone.
- Danh sách lệnh ngoài delegate đọc tĩnh từ `.pte`, chưa xác nhận bằng profiler ExecuTorch; proxy x86 không ghim luồng.
- Phiên bản timm thực tế lúc train P0.
- Log server của lượt CI (`.tmp/ci_p3all/*.log`) chưa kéo về Mac.
- Wilson III-a của P3 tính tay từ số đếm, chưa lưu file.
