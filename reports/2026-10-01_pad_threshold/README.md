# Ngưỡng riêng cho ảnh điện thoại (bước 4) — 01/10/2026

Ứng viên ship: `experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp`,
`best_model_auprc.pth`. Ngưỡng luôn chọn trên **hàng PAD-UFES-20 của val** (`val_predictions_auprc.csv`
ghép theo thứ tự dòng với `data/splits/isic2024/fold_N/val_split.csv`), rồi áp nguyên lên test PAD và
Fitzpatrick17k headline. `pad_threshold_5fold.sh` (bash + awk + jq) sinh `summary.csv` (một dòng mỗi fold × quy tắc).

| Quy tắc | Test PAD: độ nhạy / độ đặc hiệu | Fitzpatrick17k: độ nhạy / độ đặc hiệu |
|---|---|---|
| Youden trên toàn bộ val (hiện tại) — fold 4 | 1,000 / 0,005 | 1,000 / 0,001 |
| Độ nhạy 90% trên val PAD — fold 4 (ngưỡng 0,5705) | 0,873 / 0,731 | 0,567 / 0,769 |
| Youden toàn val — gộp 5 fold | 0,998 / 0,016 | 1,000 / 0,002 |
| Độ nhạy 90% val PAD — gộp 5 fold | 0,891 / 0,713 | 0,692 / 0,590 |

Gộp = cộng số đếm của 5 fold; 5 fold chấm **cùng** các hàng test, nên đây là trung bình theo fold, không phải thêm dữ liệu.

**Giới hạn — phải khai khi trích:**
- Mục tiêu "độ nhạy 90%" là **post-hoc**: chọn sau khi đã chấm 3 điểm vận hành (spec 80%, sens 90%, sens 95%) trên
  test PAD của fold 4; mọi fold dùng chung các hàng test đó, nên fold 0–3 không phải xác nhận sạch.
- Fitzpatrick17k là phép kiểm duy nhất chưa bị đụng, và ở đó độ nhạy rớt còn 0,69 (fold 4: 0,57).
- Cùng tập val đã dùng để chọn checkpoint và fold; val PAD nhỏ (351–403 dòng/fold); không có CI.
- Ảnh camera thật (L3) chưa đo; ảnh dermoscopy cần điểm riêng.

Dùng ở: `docs/ANDROID_APP_SPEC.md` §3.5a, `.claude/skills/eval-results/reference/acceptance-gates.md`
("Báo cáo bắt buộc"), `~/Documents/materials_for_mobile/models/catalog.json` (`operating_points`, chỉ tham khảo).
