# CPUBone-B1 (P3) so với MobileNetV4 (P0) ngoài miền — phép kiểm ghép cặp (CHỈ BÁO CÁO, khám phá)

> **Ngoài đăng ký trước.** `docs/PREREG_CPUBONE_2026-10-10.md` §5 chỉ đăng ký C1 và C2; phép so P3 − P0 trên tập test
> được tác giả yêu cầu ngày 11/10/2026, **sau** khi đã thấy các khoảng không ghép cặp của P3 và P0 (P3 nhỉnh hơn theo
> điểm ước lượng). Đây là phân tích khám phá, post-hoc.
>
> **Không đổi được ứng viên.** Lựa chọn chỉ trên val đã commit trước mọi file test (`reports/2026-10-10_cpubone_selection/`,
> commit `6475d76`): **giữ P0**. Chọn P3 từ bảng dưới đây là chọn trên HAM10000/Fitzpatrick17k, bị cấm ở
> `acceptance-gates.md` §4 #9 và #18.
>
> **Kết luận đã đăng ký (prereg §6) giữ nguyên:** «CPUBone-B1 không tốt hơn MobileNetV4 trên công thức này». Phần dưới
> là khám phá, không thay kết luận đó.

- P3 = KD `efficientnetv2_m → cpubone_b1` `__srcsamp`; P0 = KD `efficientnetv2_m → mobilenetv4_conv_medium` `__srcsamp`.
  Cùng teacher, cùng công thức, splits v2 (`runs_newsplit_ddi`). Cả hai: checkpoint `best_model_auprc.pth`, ngưỡng đóng
  băng từ val của chính run (`reports/external_newsplit_srcsamp_auprc/<ds>/headline/<run>/fold_*/test_metrics.json` ghi
  `"checkpoint": "best_model_auprc.pth"`).
- Nguồn dự đoán: `reports/external_newsplit_srcsamp_auprc/<ds>/headline/<run>/fold_{0..4}/predictions.csv`. Cột `y_true`
  của P3 và P0 trùng từng dòng ở cả 5 fold (kiểm trước khi chạy).
- CI: `run/bootstrap_ci.sh`, B = 2000, seed 42, mỗi replicate chấm cả 5 fold trên cùng tập chỉ số dòng rồi lấy trung bình
  (không gộp fold); `PAIR="x_p3:x_p0"` (x_p3 → P3, x_p0 → P0, symlink trong `.tmp/ci_p3p0/` trên server). Ánh xạ đã kiểm bằng cách đối chiếu §1 của
  file CI với `aggregated.json` của cây trên: x_p3 HAM AUPRC/AUC/pAUC 0,5317/0,8436/0,1045 =
  `kd_efficientnetv2_m_to_cpubone_b1__srcsamp`; x_p0 0,4997/0,8416/0,1073 =
  `kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`; Fitzpatrick 0,7205 / 0,7022 tương ứng. Kết quả:
  `reports/ci_cpubone_P3vsP0_ham10000_headline.md`, `reports/ci_cpubone_P3vsP0_fitzpatrick17k_headline.md` (+ `.json`).
- `*` = khoảng 95% không chứa 0. Không hiệu chỉnh đa phép kiểm (5 metric × 2 tập, + 3 tông da); metric dẫn là AUPRC.
  Hệ quả: các ô sát ranh giới (pAUC HAM, cận trên −0,0000; Sens@80Spec tông sáng, cận dưới +0,0012) không nên đọc như
  phát hiện. CI chỉ phản ánh sai số lấy mẫu của tập test, không gồm biến thiên giữa các lần train (mỗi bên một seed).

## 1. Kết quả — Δ(P3 − P0), ghép cặp

| Tập (biến thể headline) | Số dòng · tỉ lệ ác tính | ΔAUPRC | ΔAUC-ROC | ΔpAUC@TPR80 | ΔSens@90Spec | ΔSens@80Spec |
|---|---|---|---|---|---|---|
| HAM10000 | 7.470 · 15,6% (1.169 ca) | **+0,0320 [+0,0214; +0,0422]** * | +0,0021 [−0,0021; +0,0063] | −0,0027 [−0,0052; −0,0000] * | +0,0260 [+0,0108; +0,0400] * | +0,0128 [−0,0005; +0,0264] |
| Fitzpatrick17k | 4.320 · 50,0% (2.160 ca) | **+0,0183 [+0,0119; +0,0244]** * | +0,0132 [+0,0087; +0,0176] * | +0,0038 [+0,0020; +0,0056] * | +0,0029 [−0,0112; +0,0153] | +0,0168 [+0,0042; +0,0292] * |

Điểm ước lượng từng bên (AUPRC): HAM P3 0,5317 · P0 0,4997; Fitzpatrick P3 0,7205 · P0 0,7022. Không so AUPRC giữa hai
tập (tỉ lệ ác tính khác nhau).

## 2. Fitzpatrick17k headline theo tông da — Δ(P3 − P0)

| Tông | n · ca ác | ΔAUPRC | ΔAUC-ROC | ΔpAUC@TPR80 | ΔSens@90Spec | ΔSens@80Spec |
|---|---|---|---|---|---|---|
| Sáng | 2.310 · 1.195 | +0,0185 [+0,0103; +0,0258] * | +0,0117 [+0,0057; +0,0177] * | +0,0032 [+0,0008; +0,0058] * | +0,0174 [−0,0042; +0,0335] | +0,0197 [+0,0012; +0,0346] * |
| Trung bình | 1.599 · 757 | +0,0171 [+0,0063; +0,0276] * | +0,0165 [+0,0088; +0,0248] * | +0,0048 [+0,0017; +0,0079] * | −0,0100 [−0,0310; +0,0130] | +0,0116 [−0,0132; +0,0344] |
| Tối | 411 · 208 | +0,0033 [−0,0177; +0,0251] | +0,0108 [−0,0061; +0,0273] | +0,0039 [−0,0025; +0,0098] | +0,0163 [−0,0369; +0,0704] | +0,0221 [−0,0330; +0,0696] |

Khoảng cách sáng − trung bình vẫn còn ở cả hai. Dùng AUC-ROC (không phụ thuộc tỉ lệ ác tính, vốn khác nhau giữa các
tông: sáng 51,7%, trung bình 47,3%): P0 +0,0409 [+0,0119; +0,0708] *, P3 +0,0360 [+0,0064; +0,0668] * (§4 của file CI). Các số này **không** thay cổng III-b (cận dưới độ nhạy ≥ 0,80 **và** độ đặc hiệu ≥ 0,60, từng nhóm tông, tại
ngưỡng app, trên fold ship, Fitzpatrick17k-C), vốn không tính cho P3.

## 3. Đọc kết quả

- **AUPRC: P3 hơn P0 có ý nghĩa trên cả hai tập ngoài miền** (HAM +0,0320, Fitzpatrick +0,0183). Trên Fitzpatrick, P3
  cũng hơn ở AUC-ROC, pAUC và Sens@80Spec; theo tông da, phần hơn có ý nghĩa ở tông sáng và trung bình, tông tối
  (411 ảnh) không phân biệt được.
- **Không đồng nhất trên HAM:** pAUC@TPR80 của P3 **thấp hơn** P0 một chút (−0,0027, cận trên −0,0000), AUC-ROC không
  phân biệt được. Tức là trên HAM, P3 có độ nhạy cao hơn tại độ đặc hiệu 90% (Sens@90Spec), nhưng diện tích ROC trong
  vùng độ nhạy ≥ 80% (pAUC@TPR80) lại thấp hơn. AUPRC lấy trên toàn dải recall nên không chỉ ra được vùng.
- **Trên ảnh PAD trong miền, AUPRC ngược hướng (chưa kiểm ghép cặp, chỉ điểm ước lượng):** 397 ảnh PAD của test
  in-domain, AUPRC P3 0,8439 so với P0 0,8584 (AUC-ROC và Sens@90Spec cũng thấp hơn; pAUC 0,1247 so với 0,1232 và
  Sens@80Spec 0,8275 so với 0,8180 thì P3 cao hơn) — `reports/ci_cpubone_P3_indomain.md`,
  `reports/ci_gates_srcsamp_indomain.md`. Trên val PAD, AUPRC P3 cũng thấp hơn (0,8766 so với 0,8831) — đó là lý do luật
  chọn giữ P0. Trên phần ISIC trong miền, P3 cao hơn P0 ở cả 5 metric theo điểm ước lượng (vd AUPRC 0,0872 so với
  0,0673).
- **Không tách được nguyên nhân:** P3 và P0 khác kiến trúc student **và** khác phiên bản timm lúc train (P3: 1.0.30;
  P0: bản cũ hơn — `docs/PREREG_CPUBONE_2026-10-10.md` §2). Một biến thể CPUBone, một công thức, một seed.

**Câu được phép viết:** "Trong một phân tích khám phá, post-hoc (đề ra sau khi đã thấy điểm ước lượng trên chính các
tập này, không hiệu chỉnh đa phép kiểm), student CPUBone-B1 có AUPRC ngoài miền cao hơn MobileNetV4 với khoảng ghép cặp
không chứa 0 (HAM10000 +0,0320 [+0,0214; +0,0422]; Fitzpatrick17k +0,0183 [+0,0119; +0,0244]). Kết quả không đồng
nhất: trên HAM10000, pAUC@TPR80 lại thấp hơn (−0,0027 [−0,0052; −0,0000]). Trên ảnh điện thoại PAD, AUPRC của P3 thấp
hơn theo điểm ước lượng, và P3 không được chọn theo luật định trước." **Không được viết:** "CPUBone tốt hơn MobileNetV4", hay đổi ứng viên
ship sang P3.

## 4. Nếu muốn dùng kết quả này

Muốn P3 thành ứng viên thì cần một vòng mới, đăng ký trước, với tiêu chí chọn **không** dùng HAM/Fitzpatrick (đã thành
tập phát triển cho câu hỏi này), ví dụ một tập xác nhận chưa từng nhìn; rồi P3 phải qua **toàn bộ** luật gộp của
`acceptance-gates.md` §2.1 (I-1, II-1, II-2, II-3, III-a, III-b, C2), không chỉ phần đo trên thiết bị — tức là còn phải
export `.pte`, kiểm parity, đo trên Pixel 6a, và tính III-a/III-b tại ngưỡng app.

## Chưa verify được / chưa làm

- Phép kiểm ghép cặp P3 − P0 trên ảnh PAD trong miền: chưa chạy (chỉ có hai khoảng không ghép cặp).
- Các biến thể Fitzpatrick crop50, crop70, with_non_neoplastic: chưa so P3 − P0.
- Phiên bản timm thực tế lúc train P0: chỉ biết "cũ hơn 1.0.30" (server dùng 1.0.28 tới 10/10).
- Ánh xạ x_p3/x_p0 dựa vào cây symlink chỉ có trên server; trên Mac chỉ suy ra được bằng cách đối chiếu điểm ước lượng.
- Log server của lượt chạy CI này (`.tmp/ci_p3p0/{ham,fitz}.log`) chưa kéo về.
- Sổ các lần mở tập test (`reports/2026-10-04_test_set_openings.md`) chỉ tới 04/10; lần mở test của CPUBone (11/10) và
  phép so cặp này chưa được ghi vào đó.
