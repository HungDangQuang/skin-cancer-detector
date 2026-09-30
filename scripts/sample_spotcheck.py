#!/usr/bin/env python
"""
Sample N processed images for a MANUAL spot-check, then summarize the answers.

Motivation (Fitzpatrick17k): its pictures come from clinical atlases and many of
them frame a whole limb or face rather than a lesion close-up, while every image
the models trained on is lesion-centered. A model doing badly on such images is
failing on FRAMING, not on skin tone — quoting the gap as a fairness result
without quantifying that confound would attribute the cause wrongly.

There is no lesion detector in this repo, and inventing a "wide-field" heuristic
risks filtering unevenly across skin tones — precisely the variable being
measured. So this quantifies the confound by hand on a small, seeded sample and
lets the reported percentage go in the Limitations section.

Sampling is stratified by ``tone_group`` when the split has one, so the check can
also answer the sharper question: is wide-field framing more common in some skin
tone groups than others?

Usage:
    # 1. draw the sample (copies images + writes a CSV with a blank column)
    python scripts/sample_spotcheck.py --split-csv data/splits/fitzpatrick17k/test_split.csv

    # 2. open reports/spotcheck/<name>/images/ and fill is_wide_field with 1/0
    #    in reports/spotcheck/<name>/spotcheck.csv

    # 3. read the answers back
    python scripts/sample_spotcheck.py --summarize reports/spotcheck/fitzpatrick17k/spotcheck.csv
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

ANNOTATION_COL = "is_wide_field"


def summarize(csv_path: Path) -> None:
    df = pd.read_csv(csv_path)
    if ANNOTATION_COL not in df.columns:
        sys.exit(f"ERROR: {csv_path} has no '{ANNOTATION_COL}' column.")

    answers = pd.to_numeric(df[ANNOTATION_COL], errors="coerce")
    done = answers.notna()
    if not done.any():
        sys.exit(f"ERROR: no rows annotated yet — fill '{ANNOTATION_COL}' with 1/0 first.")

    n_done, n_total = int(done.sum()), len(df)
    rate = float(answers[done].mean())
    print(f"Annotated: {n_done}/{n_total} | wide-field: {rate:.1%}")

    if "tone_group" in df.columns:
        print("\nBy tone group (an uneven rate here means framing is entangled with")
        print("skin tone — say so explicitly in the fairness report):")
        grouped = df[done].groupby("tone_group")[ANNOTATION_COL].agg(["count", "mean"])
        grouped.columns = ["n", "wide_field_rate"]
        print(grouped.to_string(float_format=lambda v: f"{v:.1%}"))

    print(
        f"\nFor Limitations: {rate:.0%} of a random sample of {n_done} images are framed "
        f"wider than the lesion-centered crops the models were trained on."
    )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--summarize", type=Path, default=None,
                    help="read back a filled spotcheck.csv instead of drawing a new sample")
    ap.add_argument("--split-csv", type=Path, default=Path("data/splits/fitzpatrick17k/test_split.csv"))
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42, help="fixed so the sample is reproducible")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="default: reports/spotcheck/<split-csv parent name>")
    args = ap.parse_args()

    if args.summarize:
        summarize(args.summarize)
        return

    if not args.split_csv.is_file():
        sys.exit(f"ERROR: split CSV not found: {args.split_csv}")

    df = pd.read_csv(args.split_csv)
    n = min(args.n, len(df))

    if "tone_group" in df.columns and df["tone_group"].nunique() > 1:
        # Proportional stratified draw; the largest group absorbs the rounding.
        sample = df.groupby("tone_group", group_keys=False).apply(
            lambda g: g.sample(max(1, round(n * len(g) / len(df))), random_state=args.seed)
        )
        sample = sample.sample(min(n, len(sample)), random_state=args.seed)
    else:
        sample = df.sample(n, random_state=args.seed)
    sample = sample.reset_index(drop=True)

    out_dir = args.out_dir or Path("reports/spotcheck") / args.split_csv.parent.name
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for i, row in sample.iterrows():
        src = Path(row["image_path"])
        dst = images_dir / f"{i:03d}_{src.name}"
        if src.is_file():
            shutil.copy2(src, dst)
        rows.append({
            "idx": i,
            "file": dst.name,
            "image_id": row.get("image_id", ""),
            "tone_group": row.get("tone_group", ""),
            "label": row.get("label", ""),
            ANNOTATION_COL: "",   # fill by hand: 1 = wider than a lesion close-up, 0 = close-up
            "notes": "",
        })

    csv_path = out_dir / "spotcheck.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(
        f"Sampled {len(rows)} images (seed={args.seed}) from {args.split_csv}\n"
        f"  images: {images_dir}\n"
        f"  sheet:  {csv_path}\n\n"
        f"Fill '{ANNOTATION_COL}' with 1 (framed wider than a lesion close-up) or 0, then:\n"
        f"  python scripts/sample_spotcheck.py --summarize {csv_path}"
    )


if __name__ == "__main__":
    main()
