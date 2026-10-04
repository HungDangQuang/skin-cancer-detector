"""R11 (docs/PROGRESS.md): PPV / NPV at the frozen app threshold under ASSUMED prevalences.

Stdlib only. Reads the fold-4 `pad_sens90` row of reports/2026-10-02_threshold_options/summary.csv
(PAD test rows of the ship candidate P0). PAD test is ~48% malignant, so the PPV measured on it
directly is meaningless for a screening app; Bayes' rule re-weights sens/spec to a target prevalence.

Interval: sens and spec each get a Wilson 95% CI; PPV and NPV are monotone in both, so the bound
pair (sens_lo, spec_lo) / (sens_hi, spec_hi) brackets them. That bracket is CONSERVATIVE (it is not
a joint 95% interval) and it ignores uncertainty in the assumed prevalence itself.
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "reports/2026-10-02_threshold_options/summary.csv"
FOLD, RULE = "4", "pad_sens90"
PREVALENCES = (0.01, 0.05)


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def ppv(se, sp, p):
    return se * p / (se * p + (1 - sp) * (1 - p))


def npv(se, sp, p):
    return sp * (1 - p) / (sp * (1 - p) + (1 - se) * p)


row = next(r for r in csv.DictReader(open(SUMMARY)) if r["fold"] == FOLD and r["rule"] == RULE)
tp, pos, fp, neg = (int(row[k]) for k in ("pad_tp", "pad_pos", "pad_fp", "pad_neg"))
tn = neg - fp
se, sp = tp / pos, tn / neg
se_lo, se_hi = wilson(tp, pos)
sp_lo, sp_hi = wilson(tn, neg)

print(f"fold {FOLD}, rule {RULE}, threshold {float(row['threshold']):.4f}")
print(f"PAD test: TP {tp}/{pos} -> sens {se:.3f} [{se_lo:.3f}, {se_hi:.3f}]; "
      f"TN {tn}/{neg} -> spec {sp:.3f} [{sp_lo:.3f}, {sp_hi:.3f}]")
print("| prevalence (assumed) | PPV | PPV bracket | NPV | NPV bracket | referrals per 1000 | of which malignant |")
print("|---|---|---|---|---|---|---|")
for p in PREVALENCES:
    pos_rate = se * p + (1 - sp) * (1 - p)
    print(f"| {p:.0%} | {ppv(se, sp, p):.3f} | [{ppv(se_lo, sp_lo, p):.3f}, {ppv(se_hi, sp_hi, p):.3f}] "
          f"| {npv(se, sp, p):.4f} | [{npv(se_lo, sp_lo, p):.4f}, {npv(se_hi, sp_hi, p):.4f}] "
          f"| {1000 * pos_rate:.0f} | {1000 * se * p:.1f} |")
