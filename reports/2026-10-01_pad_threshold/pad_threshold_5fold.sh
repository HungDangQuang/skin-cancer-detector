#!/usr/bin/env bash
# Step 4 benefit check, PRE-REGISTERED 2026-10-01 before running:
#   operating point = sensitivity 90% on the VAL PAD rows of each fold (screening app: do not miss
#   malignant phone photos). Threshold chosen on val only; applied unchanged to
#   (a) TEST PAD rows (in-domain phone photos) and (b) Fitzpatrick17k headline (clinical photos, never
#   used for any choice). Compared against the current global val-Youden threshold.
# fold_4's test-PAD numbers were already seen (post-hoc); folds 0-3 were not.
# Student = __srcsamp, best_model_auprc.pth. awk only (no Python on the Mac).
set -euo pipefail
cd /Users/hungdang/Documents/skin-cancer-detector
W=${W:-$(pwd)/.tmp/padthr5}
mkdir -p "$W"
RUN=experiments/runs_newsplit_ddi/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp
FITZ=reports/external_newsplit_srcsamp_auprc/fitzpatrick17k/headline/kd_efficientnetv2_m_to_mobilenetv4_conv_medium__srcsamp

count() {  # $1 file (y_true,prob), $2 threshold -> "tp m fp b"
    awk -F, -v t="$2" '{ if ($1==1) { m++; if ($2>=t) tp++ } else { b++; if ($2>=t) fp++ } }
        END { printf "%d %d %d %d", tp, m, fp, b }' "$1"
}

printf "%-6s %-9s %-8s | %-27s | %-27s | %-27s\n" fold rule thr "VAL PAD  caught / flagged" "TEST PAD caught / flagged" "FITZ     caught / flagged"
for k in 0 1 2 3 4; do
    R=$RUN/fold_$k
    paste -d, <(tr -d '\r' < $R/val_predictions_auprc.csv) <(tr -d '\r' < data/splits/isic2024/fold_$k/val_split.csv | cut -d, -f4,6) \
      | awk -F, 'NR>1 { if ($1!=$4) bad++; if ($5=="pad_ufes_20") print $1","$2 }
                 END { if (bad) { print "LABEL MISMATCH fold " bad > "/dev/stderr"; exit 3 } }' > $W/val_$k.csv
    tr -d '\r' < $R/predictions_auprc.csv | awk -F, 'NR>1 && $4=="pad_ufes_20" {print $1","$2}' > $W/test_$k.csv
    tr -d '\r' < $FITZ/fold_$k/predictions.csv | awk -F, 'NR>1 {print $1","$2}' > $W/fitz_$k.csv
    t_glob=$(jq -r .threshold $R/val_metrics_auprc.json)
    t_pad=$(awk -F, '$1==1{print $2}' $W/val_$k.csv | sort -g | awk '{a[NR]=$1} END{k=int(NR*0.10)+1; print a[k]}')
    for rule in "global:$t_glob" "pad_sens90:$t_pad"; do
        n=${rule%%:*}; t=${rule#*:}
        read -r a1 a2 a3 a4 <<< "$(count $W/val_$k.csv $t)"
        read -r b1 b2 b3 b4 <<< "$(count $W/test_$k.csv $t)"
        read -r c1 c2 c3 c4 <<< "$(count $W/fitz_$k.csv $t)"
        printf "fold_%s %-10s %.4f | %3d/%3d  %3d/%3d          | %3d/%3d  %3d/%3d          | %4d/%4d %4d/%4d\n" \
            $k $n $t $a1 $a2 $a3 $a4 $b1 $b2 $b3 $b4 $c1 $c2 $c3 $c4
        echo "$k,$n,$t,$a1,$a2,$a3,$a4,$b1,$b2,$b3,$b4,$c1,$c2,$c3,$c4" >> $W/summary.csv.tmp
    done
done
mv $W/summary.csv.tmp $W/summary.csv
echo "--- pooled over 5 folds (sum of counts; folds share the same test rows, so this is a fold-average, not more data)"
awk -F, '{ for (i=8;i<=15;i++) s[$2,i]+=$i }
  END { for (r in rule) ; split("global pad_sens90", R, " ");
        for (j=1;j<=2;j++) { n=R[j];
          printf "%-10s TEST PAD sens %.3f spec %.3f | FITZ sens %.3f spec %.3f\n", n,
            s[n,8]/s[n,9], 1-s[n,10]/s[n,11], s[n,12]/s[n,13], 1-s[n,14]/s[n,15] } }' $W/summary.csv
