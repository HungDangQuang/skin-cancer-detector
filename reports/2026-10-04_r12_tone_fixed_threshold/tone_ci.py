"""R12 (docs/PROGRESS.md; review luận văn ThesisForge Issue 6 Fix 1-2) — REPORT ONLY.

Fitzpatrick17k headline, ship fold, frozen app threshold (`pad_sens90` of that fold's val):
  * per tone group: sensitivity / specificity at the threshold, and sens@95spec (threshold-free);
  * between tone groups: gaps in sensitivity, specificity and sens@95spec,
with a row bootstrap (B replicates; every replicate resamples the whole set once and scores all groups on it, so the
gaps are computed on the same replicate). Percentile 95% interval. Stdlib only; run from the repo root:
    python3 reports/2026-10-04_r12_tone_fixed_threshold/tone_ci.py [FITZ_DIR SUMMARY_CSV SHIP_FOLD] [B] [SEED]
Defaults = P0. sens@95spec follows src/evaluation/metrics.py::sensitivity_at_specificity (best TPR among
thresholds whose specificity, computed as 1 - fp/N, is still >= 0.95).
Fitzpatrick has no patient id, so rows are treated as independent (as in acceptance-gates.md §2.1).
"""
import csv
import random
import sys

A = sys.argv[1:] + [None] * 5
FITZ = A[0] or ("reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/headline/"
                "kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp")
SUMMARY = A[1] or "reports/2026-10-02_threshold_options/summary.csv"
if A[0] is not None and A[2] is None:
    sys.exit("ERROR: FITZ_DIR given -> SUMMARY_CSV and SHIP_FOLD are required too")
SHIP = int(A[2]) if A[2] is not None else 4
B = int(A[3]) if A[3] is not None else 2000
SEED = int(A[4]) if A[4] is not None else 42
TONES = ["light", "medium", "dark"]
PAIRS = [("light", "medium"), ("light", "dark"), ("medium", "dark")]

thr = next(float(r["threshold"]) for r in csv.DictReader(open(SUMMARY))
           if r["rule"] == "pad_sens90" and int(r["fold"]) == SHIP)
rows = [(r["tone_group"], int(float(r["y_true"])), float(r["y_prob"]))
        for r in csv.DictReader(open(f"{FITZ}/fold_{SHIP}/predictions.csv"))]


def sens_at_spec(pos, neg, s=0.95):
    """Best TPR with specificity >= s, thresholds = observed scores (predict positive if p >= t)."""
    if not pos or not neg:
        return float("nan")
    n = len(neg)
    desc = sorted(neg, reverse=True)
    kmax = -1  # largest fp count whose specificity still meets the floor
    for fp in range(n + 1):
        if 1.0 - fp / n >= s:
            kmax = fp
        else:
            break
    if kmax >= n:
        return 1.0
    cut = desc[kmax]  # thresholds must sit strictly above the (kmax+1)-th largest benign score
    return sum(p > cut for p in pos) / len(pos)


def score(sample):
    out = {}
    for g in TONES:
        pos = [p for t, y, p in sample if t == g and y == 1]
        neg = [p for t, y, p in sample if t == g and y == 0]
        out[g] = {
            "sens": sum(p >= thr for p in pos) / len(pos) if pos else float("nan"),
            "spec": sum(p < thr for p in neg) / len(neg) if neg else float("nan"),
            "sens95": sens_at_spec(pos, neg),
            "n_pos": len(pos), "n_neg": len(neg),
        }
    return out


def pct(v, q):
    v = sorted(x for x in v if x == x)
    i = q * (len(v) - 1)
    lo, hi = int(i), min(int(i) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


point = score(rows)
rng = random.Random(SEED)
reps = []
for _ in range(B):
    reps.append(score([rows[rng.randrange(len(rows))] for _ in range(len(rows))]))

print(f"Fitzpatrick17k headline · fold {SHIP} · threshold pad_sens90 = {thr:.4f} · B = {B}, seed {SEED} · {FITZ}")
print("\n| Tông | n ác / n lành | Độ nhạy tại ngưỡng [95%] | Độ đặc hiệu tại ngưỡng [95%] | sens@95spec [95%] |")
print("|---|---|---|---|---|")
for g in TONES:
    c = point[g]
    cells = [f"{c[m]:.3f} [{pct([r[g][m] for r in reps], .025):.3f}, {pct([r[g][m] for r in reps], .975):.3f}]"
             for m in ("sens", "spec", "sens95")]
    print(f"| {g} | {c['n_pos']} / {c['n_neg']} | " + " | ".join(cells) + " |")
print("\n| Chênh (A − B), cùng replicate | Độ nhạy tại ngưỡng [95%] | Độ đặc hiệu tại ngưỡng [95%] | sens@95spec [95%] |")
print("|---|---|---|---|")
for a, b in PAIRS:
    cells = []
    for m in ("sens", "spec", "sens95"):
        d = [r[a][m] - r[b][m] for r in reps]
        lo, hi = pct(d, .025), pct(d, .975)
        star = " *" if lo > 0 or hi < 0 else ""
        cells.append(f"{point[a][m] - point[b][m]:+.3f} [{lo:+.3f}, {hi:+.3f}]{star}")
    print(f"| {a} − {b} | " + " | ".join(cells) + " |")
print("\n`*` = khoảng loại trừ 0.")
