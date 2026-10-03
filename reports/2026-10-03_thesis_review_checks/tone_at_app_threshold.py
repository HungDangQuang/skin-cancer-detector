# Độ nhạy / độ đặc hiệu theo tông da TẠI NGƯỠNG APP (pad_sens90 của từng fold), Fitzpatrick17k headline,
# ứng viên P0 (checkpoint AUPRC). Chỉ thư viện chuẩn; chạy từ gốc repo: python3 <file này>
import csv, math
R = "reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/headline/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp"
thr = {int(r["fold"]): float(r["threshold"]) for r in csv.DictReader(open("reports/2026-10-02_threshold_options/summary.csv")) if r["rule"] == "pad_sens90"}
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)); return (c-h)/d, (c+h)/d
pool = {}
for f in range(5):
    cnt = {}
    for r in csv.DictReader(open(f"{R}/fold_{f}/predictions.csv")):
        c = cnt.setdefault(r["tone_group"], [0, 0, 0, 0])  # tp, P, tn, N
        y = int(float(r["y_true"])); flag = float(r["y_prob"]) >= thr[f]
        if y: c[1] += 1; c[0] += flag
        else: c[3] += 1; c[2] += (not flag)
    for g, c in cnt.items():
        p = pool.setdefault(g, [0, 0, 0, 0]); [p.__setitem__(i, p[i] + c[i]) for i in range(4)]
    if f == 4:
        print(f"fold 4 (model ship), ngưỡng {thr[4]:.4f}  — Wilson CI một fold")
        for g in ["light", "medium", "dark"]:
            tp, P, tn, N = cnt[g]; a = wilson(tp, P); b = wilson(tn, N)
            print(f"  {g:6s} sens {tp}/{P}={tp/P:.3f} [{a[0]:.3f}, {a[1]:.3f}]  spec {tn}/{N}={tn/N:.3f} [{b[0]:.3f}, {b[1]:.3f}]")
print("cộng số đếm 5 fold (mỗi fold ngưỡng pad_sens90 của nó)")
for g in ["light", "medium", "dark"]:
    tp, P, tn, N = pool[g]; print(f"  {g:6s} sens {tp/P:.3f}  spec {tn/N:.3f}")
