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
Pass --fetch-metadata to pull it from the authors' repo when it is not there yet.

Usage:
    # ALWAYS do a small trial first — it reports the md5 match rate, which tells
    # you whether the release's hash column means what this script assumes.
    # --sample takes a RANDOM (seeded) slice, so the trial covers every host;
    # --limit takes the first N rows, which are all one host and tell you little:
    python scripts/download_fitzpatrick17k.py --fetch-metadata --sample 60

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

# The release metadata CSV, from the authors' own repository (Groh et al., 2021).
# Only the CSV lives there — the images are the third-party links inside it.
_METADATA_URL = "https://raw.githubusercontent.com/mattgroh/fitzpatrick17k/main/fitzpatrick17k.csv"
_METADATA_REQUIRED_COLS = ("md5hash", "url", "fitzpatrick_scale", "three_partition_label")

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


def fetch_metadata_csv(dest: Path, url: str, timeout: float) -> None:
    """Download the release metadata CSV and verify it has the columns we rely on.

    Written only after the column check passes, so an error page or a moved file
    can never end up on disk pretending to be the release CSV.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[fitz] fetching metadata CSV: {url}")
    body, reason = _fetch(url, timeout=timeout, retries=2, backoff=1.0)
    if body is None:
        # _fetch rejects non-image content types; the CSV is text/plain, so read it here.
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            sys.exit(f"ERROR: could not download the metadata CSV ({reason or e}): {url}")

    try:
        df = pd.read_csv(io.BytesIO(body))
    except Exception as e:  # pandas raises several parser errors depending on payload
        sys.exit(f"ERROR: the metadata download is not a readable CSV ({type(e).__name__}: {e})")
    missing = [c for c in _METADATA_REQUIRED_COLS if c not in df.columns]
    if missing:
        sys.exit(
            f"ERROR: metadata CSV from {url} is missing {missing}; columns are "
            f"{sorted(df.columns)}. The release format changed — place the correct "
            f"CSV at {dest} by hand."
        )
    dest.write_bytes(body)
    print(f"[fitz] metadata CSV: {len(df)} rows -> {dest}")


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
                    help="stop after the FIRST N rows (0 = all); prefer --sample for a trial")
    ap.add_argument("--sample", type=int, default=0,
                    help="trial run over a random seeded sample of N rows (0 = off). The CSV "
                         "is host-ordered, so --limit's first N rows all hit one atlas and "
                         "hide a host-wide outage; --sample spreads across hosts")
    ap.add_argument("--sample-seed", type=int, default=42)
    ap.add_argument("--fetch-metadata", action="store_true",
                    help="download the release metadata CSV first if it is not on disk")
    ap.add_argument("--metadata-url", default=_METADATA_URL,
                    help="where --fetch-metadata pulls the release CSV from")
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
        if not args.fetch_metadata:
            sys.exit(
                f"ERROR: Fitzpatrick17k metadata CSV not found: {metadata_csv}\n"
                f"       Re-run with --fetch-metadata, or download the release CSV\n"
                f"       (columns md5hash,url,fitzpatrick_scale,three_partition_label,...)\n"
                f"       and place it there first."
            )
        fetch_metadata_csv(metadata_csv, args.metadata_url, args.timeout)

    df = pd.read_csv(metadata_csv)
    for col in ("md5hash", "url"):
        if col not in df.columns:
            sys.exit(f"ERROR: metadata CSV is missing required column '{col}' ({metadata_csv})")
    if args.limit:
        df = df.head(args.limit)
    if args.sample and args.sample < len(df):
        df = df.sample(n=args.sample, random_state=args.sample_seed)

    images_dir = raw_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    probe = _Probe()

    def work(row: dict) -> dict:
        md5hash = str(row["md5hash"])
        url = str(row["url"]).strip()
        dst = images_dir / f"{md5hash}.jpg"

        if dst.exists() and not args.overwrite:
            return {"md5hash": md5hash, "url": url, "status": "cached", "reason": "already_on_disk"}
        if probe.aborted:
            return {"md5hash": md5hash, "url": url, "status": "skipped", "reason": "probe_aborted"}
        # The release carries a few dozen rows with a blank url (pandas reads
        # them as NaN -> the string "nan"). Left unguarded, urllib raises
        # ValueError inside the worker and pool.map re-raises it in the main
        # thread, killing a 16k-row download over ~40 unusable rows.
        if not url.lower().startswith(("http://", "https://")):
            return {"md5hash": md5hash, "url": url, "status": "failed", "reason": "missing_url"}

        try:
            body, reason = _fetch(url, args.timeout, args.retries, args.backoff)
            if body is None:
                return {"md5hash": md5hash, "url": url, "status": "failed", "reason": reason}

            status, reason = _validate(body, md5hash, args.md5_check)
            if args.md5_check != "off":
                probe.record(reason.startswith("md5_match"))
            if status != "ok":
                return {"md5hash": md5hash, "url": url, "status": status, "reason": reason}

            dst.write_bytes(body)
        except Exception as e:  # one malformed row must never abort the whole fetch
            return {"md5hash": md5hash, "url": url, "status": "failed",
                    "reason": f"worker_error: {type(e).__name__}: {e}"}
        return {"md5hash": md5hash, "url": url, "status": "ok", "reason": reason}

    rows = df.to_dict("records")
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        # disable=None -> silent under the runner's tee (a 16k-row bar would
        # otherwise be most of the log file); interactive runs still show it.
        for res in tqdm(pool.map(work, rows), total=len(rows),
                        desc="Downloading Fitzpatrick17k", disable=None):
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

    # Per-host success rate. The release links two atlases, and they fail as a
    # BLOCK (one going offline takes ~76% or ~24% of the set with it), so the
    # overall rate alone hides which part of the fairness set survived.
    log_df = pd.DataFrame(results)
    log_df["host"] = log_df["url"].astype(str).str.extract(r"https?://([^/]+)", expand=False)
    print("\n  per-host outcome (a whole host at 0% = that atlas is offline/moved):")
    for host, grp in log_df.groupby("host", dropna=False):
        ok = int(grp["status"].isin(["ok", "cached"]).sum())
        top_reason = grp.loc[~grp["status"].isin(["ok", "cached"]), "reason"]
        reason = f" | top failure: {top_reason.mode().iat[0]}" if len(top_reason) else ""
        print(f"    {str(host):<32} {ok:>6}/{len(grp):<6} ({ok / len(grp):.1%}){reason}")

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
