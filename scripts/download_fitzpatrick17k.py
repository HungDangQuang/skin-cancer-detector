#!/usr/bin/env python
"""
Download the Fitzpatrick17k images (FAIRNESS EVALUATION ONLY — never training).

Fitzpatrick17k ships as a metadata CSV of **URLs**, not as images: the pictures
live on third-party dermatology atlas sites. So unlike ISIC 2024 / PAD-UFES-20,
the raw data has to be fetched link by link, and a meaningful share of the links
are dead. The single most common failure mode is a dead link returning an HTML
error page that gets saved as "<something>.jpg" — which PIL sometimes even opens.
This script therefore validates every download in four escalating steps:

    HTTP 200  ->  Content-Type: image/*  ->  PIL can decode it  ->  md5 matches

The md5 check is free here and available for no other dataset in this repo: the
metadata CSV carries an ``md5hash`` column, so a byte-exact identity check is
possible. It is what catches the HTML-error-page case for good.

Prereq — the metadata CSV (from the Fitzpatrick17k release):
    data/raw/fitzpatrick17k/fitzpatrick17k.csv
    columns: md5hash, url, fitzpatrick_scale, three_partition_label,
             nine_partition_label, label

Usage:
    # ALWAYS do a small trial first — it reports the md5 match rate, which tells
    # you whether the release's hash column means what this script assumes:
    python scripts/download_fitzpatrick17k.py --limit 50

    # Then the full run (resumable — re-running skips what is already on disk):
    python scripts/download_fitzpatrick17k.py

Output:
    data/raw/fitzpatrick17k/images/<md5hash>.jpg
    data/raw/fitzpatrick17k/download_log.csv        <- md5hash,url,status,reason
    data/raw/fitzpatrick17k/metadata_downloaded.csv <- rows that produced a valid
                                                       image (input to prepare)

The download success rate this prints belongs in the thesis: images that could
not be fetched are a coverage limitation of the fairness analysis, and the rate
may differ by skin-tone group.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

import pandas as pd
from PIL import Image
from tqdm import tqdm

# Some atlas hosts reject the default urllib agent outright.
_USER_AGENT = "Mozilla/5.0 (compatible; skin-cancer-detector research fetcher)"

# Early-abort guard: if the first _PROBE_N verified downloads mostly FAIL the md5
# check, the release's hash column does not mean "md5 of the image bytes" and a
# strict run would reject the entire dataset after hours of downloading.
_PROBE_N = 25
_PROBE_MIN_MATCH = 0.5


class _Probe:
    """Thread-safe md5 match-rate probe over the first few successful fetches."""

    def __init__(self) -> None:
        self.lock = Lock()
        self.checked = 0
        self.matched = 0
        self.aborted = False

    def record(self, ok: bool) -> None:
        with self.lock:
            self.checked += 1
            self.matched += int(ok)

    def should_abort(self) -> bool:
        with self.lock:
            if self.checked < _PROBE_N or self.aborted:
                return False
            if self.matched / self.checked >= _PROBE_MIN_MATCH:
                return False
            self.aborted = True
            return True


def _fetch(url: str, timeout: float, retries: int, backoff: float) -> tuple[bytes | None, str | None]:
    """GET a URL with retry/backoff. Returns (body, None) or (None, reason)."""
    last = "unknown_error"
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status != 200:
                    return None, f"http_{resp.status}"
                ctype = resp.headers.get_content_type()
                body = resp.read()
            if not ctype.startswith("image/"):
                # Dead link serving an HTML error page — the classic scrape trap.
                return None, f"not_an_image: {ctype}"
            return body, None
        except urllib.error.HTTPError as e:
            return None, f"http_{e.code}"          # 404/410 will not change on a retry
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = f"network: {type(e).__name__}"
        if attempt < retries:
            time.sleep(backoff * (2 ** attempt))
    return None, last


def _validate(body: bytes, expected_md5: str, md5_check: str) -> tuple[str, str]:
    """Return (status, reason) after decode + md5 verification of the payload."""
    try:
        Image.open(io.BytesIO(body)).verify()
    except Exception as e:  # PIL raises a wide, version-dependent set here
        return "failed", f"undecodable: {type(e).__name__}"

    actual = hashlib.md5(body).hexdigest()
    if actual == expected_md5:
        return "ok", "md5_match"
    if md5_check == "strict":
        return "failed", f"md5_mismatch: got {actual}"
    if md5_check == "warn":
        return "ok", f"md5_mismatch_kept: got {actual}"
    return "ok", "md5_check_off"


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--raw-dir", type=Path, default=Path("data/raw/fitzpatrick17k"))
    ap.add_argument("--metadata", type=Path, default=None,
                    help="metadata CSV (default: <raw-dir>/fitzpatrick17k.csv)")
    ap.add_argument("--limit", type=int, default=0,
                    help="stop after N rows — use for the trial run (0 = all)")
    ap.add_argument("--workers", type=int, default=8,
                    help="parallel downloads (default 8; keep modest, these are third-party hosts)")
    ap.add_argument("--timeout", type=float, default=20.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--backoff", type=float, default=1.0, help="seconds, doubled per retry")
    ap.add_argument("--md5-check", choices=["strict", "warn", "off"], default="strict",
                    help="strict (default): reject a payload whose md5 differs from the "
                         "metadata column; warn: keep it but record the mismatch; off: skip")
    ap.add_argument("--overwrite", action="store_true",
                    help="re-download images already on disk (default: resume/skip)")
    args = ap.parse_args()

    raw_dir = args.raw_dir
    metadata_csv = args.metadata or (raw_dir / "fitzpatrick17k.csv")
    if not metadata_csv.is_file():
        sys.exit(
            f"ERROR: Fitzpatrick17k metadata CSV not found: {metadata_csv}\n"
            f"       Download the release CSV (columns md5hash,url,fitzpatrick_scale,\n"
            f"       three_partition_label,...) and place it there first."
        )

    df = pd.read_csv(metadata_csv)
    for col in ("md5hash", "url"):
        if col not in df.columns:
            sys.exit(f"ERROR: metadata CSV is missing required column '{col}' ({metadata_csv})")
    if args.limit:
        df = df.head(args.limit)

    images_dir = raw_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    probe = _Probe()

    def work(row: dict) -> dict:
        md5hash = str(row["md5hash"])
        url = str(row["url"])
        dst = images_dir / f"{md5hash}.jpg"

        if dst.exists() and not args.overwrite:
            return {"md5hash": md5hash, "url": url, "status": "cached", "reason": "already_on_disk"}
        if probe.aborted:
            return {"md5hash": md5hash, "url": url, "status": "skipped", "reason": "probe_aborted"}

        body, reason = _fetch(url, args.timeout, args.retries, args.backoff)
        if body is None:
            return {"md5hash": md5hash, "url": url, "status": "failed", "reason": reason}

        status, reason = _validate(body, md5hash, args.md5_check)
        if args.md5_check != "off":
            probe.record(reason.startswith("md5_match"))
        if status != "ok":
            return {"md5hash": md5hash, "url": url, "status": status, "reason": reason}

        dst.write_bytes(body)
        return {"md5hash": md5hash, "url": url, "status": "ok", "reason": reason}

    rows = df.to_dict("records")
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for res in tqdm(pool.map(work, rows), total=len(rows), desc="Downloading Fitzpatrick17k"):
            results.append(res)
            if probe.should_abort():
                print(
                    f"\nABORTING: only {probe.matched}/{probe.checked} downloads matched their "
                    f"md5hash. This release's hash column likely is not the md5 of the image "
                    f"bytes. Re-run with --md5-check warn (and record that choice in the "
                    f"fairness report) — do NOT silently keep a strict run.",
                    file=sys.stderr,
                )

    log_path = raw_dir / "download_log.csv"
    with log_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["md5hash", "url", "status", "reason"])
        writer.writeheader()
        writer.writerows(results)

    status_by_hash = {r["md5hash"]: r["status"] for r in results}
    ok_hashes = {h for h, s in status_by_hash.items() if s in ("ok", "cached")}
    kept = df[df["md5hash"].astype(str).isin(ok_hashes)].copy()
    manifest = raw_dir / "metadata_downloaded.csv"
    kept.to_csv(manifest, index=False)

    n_total = len(results)
    n_ok = len(ok_hashes)
    print(
        f"\nFitzpatrick17k download — attempted: {n_total} | valid images: {n_ok} "
        f"({n_ok / n_total:.1%}) | failed: {n_total - n_ok}\n"
        f"  log:      {log_path}\n"
        f"  manifest: {manifest}\n"
        f"Report the success rate in the fairness section: unfetchable images are a "
        f"coverage limitation, and the loss may not be uniform across skin-tone groups "
        f"(check it with: groupby fitzpatrick_scale on the log)."
    )
    if probe.aborted:
        sys.exit(2)


if __name__ == "__main__":
    main()
