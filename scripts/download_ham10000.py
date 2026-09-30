#!/usr/bin/env python
"""
Download HAM10000 (CROSS-DOMAIN EVALUATION ONLY — never training).

HAM10000 is published on Harvard Dataverse (DOI 10.7910/DVN/DBW86T, CC BY-NC 4.0)
as two image zips plus a metadata table. Unlike Fitzpatrick17k, every byte is
served by one open-access host, so this is a plain fetch-verify-extract job:

    dataset API  ->  file ids by NAME  ->  /api/access/datafile/<id>  ->  md5  ->  unzip

File ids are resolved from the dataset record at run time instead of being
hard-coded, so a new dataset version (Dataverse re-issues ids per version) does
not silently 404 this script.

Usage:
    python scripts/download_ham10000.py                 # ~2.8 GB, resumable
    python scripts/download_ham10000.py --rm-zip        # delete each zip after extracting
    python scripts/download_ham10000.py --skip-images   # metadata only (fast check)

Output (exactly the layout process_ham10000() expects):
    data/raw/ham10000/HAM10000_metadata.csv    <- lesion_id,image_id,dx,dx_type,age,sex,localization
    data/raw/ham10000/images/ISIC_*.jpg        <- 10015 images
    data/raw/ham10000/download_manifest.json   <- file ids, sizes, md5 verdicts

Next:  bash run/prepare_external.sh DATASET=ham10000
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from tqdm import tqdm

DATAVERSE = "https://dataverse.harvard.edu"
HAM10000_DOI = "doi:10.7910/DVN/DBW86T"
IMAGE_ZIPS = ("HAM10000_images_part_1.zip", "HAM10000_images_part_2.zip")
# Dataverse ingests the released CSV into an archival .tab; ``?format=original``
# gives the file the authors uploaded, so we ask for that and sniff the delimiter.
METADATA_NAMES = ("HAM10000_metadata.tab", "HAM10000_metadata.csv")
N_IMAGES_EXPECTED = 10015
_CHUNK = 1 << 20  # 1 MiB
# Dataverse's WAF answers the default "Python-urllib/3.x" agent with 403 — every
# request here must carry an explicit agent or the whole script dies at the API call.
_USER_AGENT = "Mozilla/5.0 (compatible; skin-cancer-detector research fetcher)"


def _request(url: str, headers: dict | None = None):
    return urllib.request.Request(url, headers={"User-Agent": _USER_AGENT, **(headers or {})})


def file_index(doi: str, timeout: float) -> dict[str, dict]:
    """Map {filename: dataFile record} for the dataset's latest version."""
    url = f"{DATAVERSE}/api/datasets/:persistentId/?persistentId={doi}"
    try:
        with urllib.request.urlopen(_request(url), timeout=timeout) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        sys.exit(f"ERROR: could not read the Dataverse record for {doi}: {e}")

    files = payload.get("data", {}).get("latestVersion", {}).get("files", [])
    if not files:
        sys.exit(f"ERROR: Dataverse returned no files for {doi} — check the DOI / API status.")

    index: dict[str, dict] = {}
    for entry in files:
        data_file = entry.get("dataFile", {})
        name = data_file.get("filename")
        if name:
            index[name] = data_file
    return index


def _md5_of(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(_CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def download_file(
    file_id: int,
    dest: Path,
    expected_size: int | None = None,
    expected_md5: str | None = None,
    original_format: bool = False,
    timeout: float = 60.0,
) -> Path:
    """Fetch one datafile, resuming a partial ``<dest>.part`` when possible.

    A 2.8 GB pull over a flaky link is the normal case here, so the download
    goes to ``.part`` and is only renamed into place after the md5 check —
    a truncated file can therefore never masquerade as a complete one.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and (expected_size is None or dest.stat().st_size == expected_size):
        print(f"[ham] {dest.name}: already on disk ({dest.stat().st_size / 1e6:.1f} MB), skipping")
        return dest

    url = f"{DATAVERSE}/api/access/datafile/{file_id}"
    if original_format:
        url += "?format=original"

    part = dest.with_suffix(dest.suffix + ".part")
    have = part.stat().st_size if part.exists() else 0
    headers = {"Range": f"bytes={have}-"} if have else {}

    try:
        with urllib.request.urlopen(_request(url, headers), timeout=timeout) as resp:
            # 206 = the server honored the range; 200 = it ignored it, so restart.
            if have and resp.status != 206:
                have = 0
                part.unlink(missing_ok=True)
            remaining = resp.headers.get("Content-Length")
            total = (int(remaining) + have) if remaining else expected_size
            mode = "ab" if have else "wb"
            # disable=None -> no progress bar when stdout is a pipe, so the
            # runner's tee'd log holds a few lines instead of a few thousand.
            with part.open(mode) as out, tqdm(
                total=total, initial=have, unit="B", unit_scale=True,
                desc=f"[ham] {dest.name}", disable=None,
            ) as bar:
                while True:
                    block = resp.read(_CHUNK)
                    if not block:
                        break
                    out.write(block)
                    bar.update(len(block))
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        sys.exit(f"ERROR: download of {dest.name} failed ({e}). Re-run to resume from {part}.")

    if expected_md5 and not original_format:
        # md5 is only meaningful for files served verbatim; ?format=original
        # returns the pre-ingest upload, whose hash differs from the archival one.
        actual = _md5_of(part)
        if actual != expected_md5:
            sys.exit(
                f"ERROR: md5 mismatch for {dest.name} (got {actual}, expected {expected_md5}).\n"
                f"       The partial file was kept at {part} — delete it and re-run."
            )
        print(f"[ham] {dest.name}: md5 OK")

    part.replace(dest)
    return dest


def extract_images(zip_path: Path, images_dir: Path, overwrite: bool = False) -> int:
    """Flatten every image in ``zip_path`` into ``images_dir``. Returns count written."""
    images_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    with zipfile.ZipFile(zip_path) as zf:
        members = [m for m in zf.infolist()
                   if not m.is_dir() and m.filename.lower().endswith((".jpg", ".jpeg", ".png"))]
        for member in tqdm(members, desc=f"[ham] extracting {zip_path.name}", disable=None):
            target = images_dir / Path(member.filename).name
            if target.exists() and not overwrite:
                continue
            with zf.open(member) as src, target.open("wb") as dst:
                while True:
                    block = src.read(_CHUNK)
                    if not block:
                        break
                    dst.write(block)
            written += 1
    return written


def write_metadata_csv(src: Path, dest: Path) -> int:
    """Normalize the downloaded metadata table to the CSV process_ham10000() reads."""
    import pandas as pd

    # sep=None + the python engine sniffs comma vs tab, so both the original CSV
    # and the archival .tab land in the same place.
    df = pd.read_csv(src, sep=None, engine="python")
    missing = [c for c in ("image_id", "lesion_id", "dx") if c not in df.columns]
    if missing:
        sys.exit(
            f"ERROR: downloaded HAM10000 metadata is missing {missing}; columns are "
            f"{sorted(df.columns)}. Dataverse may have changed the release format."
        )
    df.to_csv(dest, index=False)
    return len(df)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--raw-dir", type=Path, default=Path("data/raw/ham10000"))
    ap.add_argument("--doi", default=HAM10000_DOI)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--skip-images", action="store_true",
                    help="fetch only the metadata table (quick connectivity / format check)")
    ap.add_argument("--rm-zip", action="store_true",
                    help="delete each image zip right after it is extracted (reclaims ~2.8 GB)")
    ap.add_argument("--overwrite", action="store_true",
                    help="re-extract images that are already on disk")
    args = ap.parse_args()

    raw_dir = args.raw_dir
    raw_dir.mkdir(parents=True, exist_ok=True)
    index = file_index(args.doi, args.timeout)
    manifest: dict = {"doi": args.doi, "files": {}}

    # ---- metadata -------------------------------------------------------
    meta_name = next((n for n in METADATA_NAMES if n in index), None)
    if meta_name is None:
        sys.exit(
            f"ERROR: no HAM10000 metadata file in the Dataverse record. Files: {sorted(index)}"
        )
    meta_record = index[meta_name]
    raw_meta = download_file(
        file_id=meta_record["id"],
        dest=raw_dir / f".{meta_name}.original",
        original_format=True,
        timeout=args.timeout,
    )
    n_rows = write_metadata_csv(raw_meta, raw_dir / "HAM10000_metadata.csv")
    raw_meta.unlink(missing_ok=True)
    manifest["files"][meta_name] = {"id": meta_record["id"], "rows": n_rows}
    print(f"[ham] metadata: {n_rows} rows -> {raw_dir / 'HAM10000_metadata.csv'}")

    # ---- images ---------------------------------------------------------
    images_dir = raw_dir / "images"
    if args.skip_images:
        print("[ham] --skip-images: stopping after the metadata.")
    else:
        for zip_name in IMAGE_ZIPS:
            if zip_name not in index:
                sys.exit(f"ERROR: '{zip_name}' not in the Dataverse record. Files: {sorted(index)}")
            record = index[zip_name]
            zip_path = download_file(
                file_id=record["id"],
                dest=raw_dir / zip_name,
                expected_size=record.get("filesize"),
                expected_md5=record.get("md5"),
                timeout=args.timeout,
            )
            written = extract_images(zip_path, images_dir, overwrite=args.overwrite)
            manifest["files"][zip_name] = {
                "id": record["id"],
                "filesize": record.get("filesize"),
                "md5": record.get("md5"),
                "images_written": written,
            }
            if args.rm_zip:
                zip_path.unlink(missing_ok=True)
                print(f"[ham] removed {zip_path.name}")

    # ---- verify ---------------------------------------------------------
    n_images = sum(1 for _ in images_dir.glob("*.jpg")) if images_dir.exists() else 0
    manifest["n_images_on_disk"] = n_images
    manifest["n_metadata_rows"] = n_rows
    (raw_dir / "download_manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"\n[ham] images on disk: {n_images} (release ships {N_IMAGES_EXPECTED})")
    if not args.skip_images and n_images < N_IMAGES_EXPECTED:
        # Not fatal: prepare_external_data.py reports every metadata row it cannot
        # match to a file, so a short set degrades the eval set size, not silently
        # the labels. But it always means an incomplete download.
        print(
            f"[ham] WARN: {N_IMAGES_EXPECTED - n_images} image(s) missing — re-run this "
            f"script (it resumes) before evaluating, or the cross-domain set is short."
        )
    print("[ham] Next: bash run/prepare_external.sh DATASET=ham10000")


if __name__ == "__main__":
    main()
