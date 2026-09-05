"""
Offline preprocessing script helpers.
Run via: python scripts/prepare_data.py
"""
import hashlib
import io
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import StratifiedGroupKFold
from tqdm import tqdm


# Post-biopsy diagnosis / histopathology fields. Their mere presence (or NaN)
# leaks the label in ISIC 2024, so they are FORBIDDEN as training metadata even
# in the privileged teacher — see docs/metadata_training_plan.md §0.
_LEAKAGE_PREFIXES = ("iddx_", "mel_")
# Base record schema. A metadata_col colliding with one of these would OVERWRITE
# it (e.g. PAD would set patient_id/label to NaN -> group leakage / label loss).
_RESERVED_COLS = frozenset(
    {"image_id", "patient_id", "image_path", "label", "class_name", "source"}
)


def _validate_metadata_cols(metadata_cols: list[str] | None) -> None:
    """Raise if metadata_cols contains a leakage (iddx_*/mel_*) or reserved column."""
    if not metadata_cols:
        return
    bad = [c for c in metadata_cols if str(c).startswith(_LEAKAGE_PREFIXES)]
    if bad:
        raise ValueError(
            f"metadata_cols contains post-biopsy LEAKAGE columns {bad}: "
            f"iddx_*/mel_* are diagnosis/histopathology fields whose presence "
            f"(or NaN) reveals the label. Remove them "
            f"(see docs/metadata_training_plan.md §0)."
        )
    reserved = [c for c in metadata_cols if c in _RESERVED_COLS]
    if reserved:
        raise ValueError(
            f"metadata_cols may not name base schema columns {reserved} "
            f"(they would overwrite the record's {sorted(_RESERVED_COLS)} — for "
            f"PAD that means NaN patient_id/label = group leakage / label loss)."
        )


def resize_and_save(src: Image.Image | Path, dst_path: Path, size: tuple[int, int] = (224, 224)) -> None:
    """Resize a PIL image (or path) and save to destination."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    img = (Image.open(src).convert("RGB") if isinstance(src, Path) else src)
    img = img.resize(size, Image.LANCZOS)
    img.save(dst_path)


def is_uninformative(
    img: Image.Image,
    std_threshold: float = 8.0,
    extreme_frac_threshold: float = 0.97,
) -> bool:
    """Heuristic check for blank / near-uniform / no-signal images.

    Operates on the (already resized) RGB image. Returns True when the image
    carries essentially no usable signal and should be dropped:
      - global grayscale std < std_threshold  → flat / near-uniform tile, or
      - > extreme_frac_threshold of pixels are near-black or near-white
        → all-dark vignette crops and blown-out / washed-out tiles.

    Thresholds are intentionally conservative (drop only the clearly bad) and
    are tunable from the call site; verify the drop list on the cluster.
    """
    gray = np.asarray(img.convert("L"), dtype=np.float32)
    if gray.std() < std_threshold:
        return True
    extreme_frac = float((gray <= 10).mean() + (gray >= 245).mean())
    return extreme_frac > extreme_frac_threshold


# ------------------------------------------------------------------
# ISIC 2024 SLICE-3D
# ------------------------------------------------------------------

def process_isic2024(
    raw_dir: str | Path,
    processed_dir: str | Path,
    image_size: int = 224,
    image_id_col: str = "isic_id",
    label_col: str = "target",
    min_size: int = 32,
    metadata_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Extract and resize images from ISIC 2024 HDF5 archive.

    Raw structure expected:
        raw_dir/
          train-image.hdf5     <- HDF5 with keys = isic_id, values = JPEG bytes
          train-metadata.csv   <- isic_id, patient_id, target (0/1), ...

    Args:
        metadata_cols: optional extra columns to carry from ``train-metadata.csv``
            into each record (e.g. ``tbp_lv_*`` for the privileged teacher, or
            ``anatom_site_general``/``sex`` for subgroup calibration). Default
            ``None`` keeps the historical 6-column schema byte-for-byte. Leakage
            columns (``iddx_*``/``mel_*``) are rejected up front.

    Returns:
        DataFrame with columns: image_id, patient_id, image_path, label,
        class_name, source (+ any ``metadata_cols``).
    """
    _validate_metadata_cols(metadata_cols)
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    hdf5_path = raw_dir / "train-image.hdf5"
    metadata_csv = raw_dir / "train-metadata.csv"

    if not hdf5_path.exists():
        raise FileNotFoundError(f"HDF5 not found: {hdf5_path}")
    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_csv}")

    metadata = pd.read_csv(metadata_csv, low_memory=False)
    class_names = {0: "benign", 1: "malignant"}
    records = []
    excluded = []  # (image_id, reason) for corrupt / small / dup / uninformative images
    seen_hashes: set[str] = set()  # exact-duplicate detection across the dataset
    skipped = 0  # number of rows where the resized JPG already existed on disk

    with h5py.File(hdf5_path, "r") as hdf:
        for _, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing ISIC 2024"):
            image_id = row[image_id_col]
            label = int(row[label_col])
            patient_id = str(row.get("patient_id", image_id))
            class_name = class_names[label]
            dst = processed_dir / class_name / f"{image_id}.jpg"

            try:
                if dst.exists():
                    # Fast-path: a previous run already resized this image, so
                    # skip the HDF5 read + resize. Still load it back so the
                    # quality filter runs (a pre-filter run may have written a
                    # bad image to disk).
                    img = Image.open(dst).convert("RGB")
                    is_new = False
                else:
                    if image_id not in hdf:
                        continue
                    # HDF5 stores JPEG bytes as a byte string dataset
                    jpeg_bytes = hdf[image_id][()]
                    img = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
                    if min(img.size) < min_size:
                        # Native crop too small to carry detail once upscaled to
                        # image_size. Only checkable on the fresh decode — the
                        # fast-path image on disk is already resized to 224.
                        excluded.append({"image_id": image_id, "reason": f"too_small: {img.size}"})
                        continue
                    img = img.resize((image_size, image_size), Image.LANCZOS)
                    is_new = True
            except (OSError, ValueError, Image.DecompressionBombError) as e:
                excluded.append({"image_id": image_id, "reason": f"corrupt: {e}"})
                continue

            if is_uninformative(img):
                excluded.append({"image_id": image_id, "reason": "uninformative"})
                # Drop a previously-saved bad image so the on-disk dataset
                # stays consistent with the split CSVs.
                if not is_new and dst.exists():
                    dst.unlink()
                continue

            # Exact-duplicate detection on the resized pixels: first occurrence
            # kept, later identical images dropped so the same lesion cannot land
            # in two folds.
            img_hash = hashlib.md5(img.tobytes()).hexdigest()
            if img_hash in seen_hashes:
                excluded.append({"image_id": image_id, "reason": "duplicate"})
                if not is_new and dst.exists():
                    dst.unlink()
                continue
            seen_hashes.add(img_hash)

            if is_new:
                dst.parent.mkdir(parents=True, exist_ok=True)
                img.save(dst)
            else:
                skipped += 1

            record = {
                "image_id": image_id,
                "patient_id": patient_id,
                "image_path": str(dst),
                "label": label,
                "class_name": class_name,
                "source": "isic2024",
            }
            if metadata_cols:
                # Carry the requested raw metadata verbatim; missing -> NaN so the
                # column exists uniformly and NaN-masking downstream still works.
                for col in metadata_cols:
                    record[col] = row.get(col, np.nan)
            records.append(record)

    if excluded:
        processed_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(excluded).to_csv(processed_dir / "excluded_images.csv", index=False)

    df = pd.DataFrame(records)
    print(
        f"ISIC 2024 — total: {len(df)} | "
        f"benign: {(df['label']==0).sum()} | malignant: {(df['label']==1).sum()} | "
        f"skipped (already-on-disk): {skipped} | "
        f"excluded (corrupt/small/dup/uninformative): {len(excluded)}"
    )
    return df


# ------------------------------------------------------------------
# PAD-UFES-20
# ------------------------------------------------------------------

def process_pad_ufes_20(
    raw_dir: str | Path,
    processed_dir: str | Path,
    image_size: int = 224,
    min_size: int = 32,
    metadata_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Process PAD-UFES-20 dataset and map 6 classes to binary labels.

    Raw structure expected:
        raw_dir/
          images/          <- JPEG files
          metadata.csv     <- img_id, diagnostic (BCC/SCC/MEL/ACK/NEV/SEK), ...

    Label mapping (from proposal):
        Malignant (1): BCC, SCC, MEL
        Benign    (0): ACK, NEV, SEK

    Args:
        metadata_cols: extra columns kept in the ISIC records. PAD-UFES-20 has a
            different schema (no ``tbp_lv_*``), so every requested column is set
            to ``NaN`` here — the NaN mask lets the privileged tabular branch skip
            (not backprop) PAD samples. Default ``None`` keeps the 6-column schema.

    Returns:
        DataFrame with columns: image_id, patient_id, image_path, label,
        class_name, source (+ any ``metadata_cols``, all NaN for PAD).
    """
    _validate_metadata_cols(metadata_cols)
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    images_dir = raw_dir / "images"
    metadata_csv = raw_dir / "metadata.csv"

    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_csv}")

    metadata = pd.read_csv(metadata_csv)

    LABEL_MAP = {
        "BCC": 1, "SCC": 1, "MEL": 1,
        "ACK": 0, "NEV": 0, "SEK": 0,
    }
    class_names = {0: "benign", 1: "malignant"}
    records = []
    excluded = []  # (image_id, reason) for corrupt / small / dup / uninformative images
    seen_hashes: set[str] = set()  # exact-duplicate detection across the dataset
    skipped = 0

    for _, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing PAD-UFES-20"):
        img_id = str(row["img_id"])
        # PAD's metadata stores img_id WITH the file extension (e.g.
        # "PAT_8_15_820.png"); strip it for the processed filename/id so we
        # don't produce "pad_..png.jpg".
        stem = Path(img_id).stem
        diagnostic = str(row["diagnostic"]).upper()
        label = LABEL_MAP.get(diagnostic)

        if label is None:
            continue

        class_name = class_names[label]
        dst = processed_dir / class_name / f"pad_{stem}.jpg"

        try:
            if dst.exists():
                # Fast-path: already processed; reload it so the filter runs.
                img = Image.open(dst).convert("RGB")
                is_new = False
            else:
                # img_id already carries the extension; fall back to stem+ext
                # in case a mirror stored bare ids.
                src = images_dir / img_id
                if not src.exists():
                    src = images_dir / f"{stem}.png"
                if not src.exists():
                    src = images_dir / f"{stem}.jpg"
                if not src.exists():
                    continue
                img = Image.open(src).convert("RGB")
                if min(img.size) < min_size:
                    excluded.append({"image_id": f"pad_{stem}", "reason": f"too_small: {img.size}"})
                    continue
                img = img.resize((image_size, image_size), Image.LANCZOS)
                is_new = True
        except (OSError, ValueError, Image.DecompressionBombError) as e:
            excluded.append({"image_id": f"pad_{stem}", "reason": f"corrupt: {e}"})
            continue

        if is_uninformative(img):
            excluded.append({"image_id": f"pad_{stem}", "reason": "uninformative"})
            if not is_new and dst.exists():
                dst.unlink()
            continue

        img_hash = hashlib.md5(img.tobytes()).hexdigest()
        if img_hash in seen_hashes:
            excluded.append({"image_id": f"pad_{stem}", "reason": "duplicate"})
            if not is_new and dst.exists():
                dst.unlink()
            continue
        seen_hashes.add(img_hash)

        if is_new:
            dst.parent.mkdir(parents=True, exist_ok=True)
            img.save(dst)
        else:
            skipped += 1

        record = {
            "image_id": f"pad_{stem}",
            # Namespace the group key so a PAD patient_id can never collide with
            # an ISIC patient_id and leak across folds in StratifiedGroupKFold.
            "patient_id": f"pad_{row.get('patient_id', stem)}",
            "image_path": str(dst),
            "label": label,
            "class_name": class_name,
            "source": "pad_ufes_20",
        }
        if metadata_cols:
            # PAD has no tbp_lv_* — NaN so the column aligns with ISIC; the mask
            # (NaN -> 0) stops the privileged tabular branch from training on it.
            for col in metadata_cols:
                record[col] = np.nan
        records.append(record)

    if excluded:
        processed_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(excluded).to_csv(processed_dir / "excluded_images.csv", index=False)

    df = pd.DataFrame(records)
    if df.empty:
        raise RuntimeError(
            f"process_pad_ufes_20: 0 of {len(metadata)} rows produced an image. "
            f"Check that img_id values (e.g. {str(metadata['img_id'].iloc[0])!r}) match "
            f"files in {images_dir}, and that diagnostic codes are in {sorted(LABEL_MAP)}."
        )
    print(
        f"PAD-UFES-20 — total: {len(df)} | "
        f"benign: {(df['label']==0).sum()} | malignant: {(df['label']==1).sum()} | "
        f"skipped (already-on-disk): {skipped} | "
        f"excluded (corrupt/small/dup/uninformative): {len(excluded)}"
    )
    return df


# ------------------------------------------------------------------
# External EVALUATION-ONLY datasets (HAM10000, Fitzpatrick17k)
#
# These two are never trained on — they are held-out test sets for the
# cross-domain (HAM10000) and fairness (Fitzpatrick17k) reports. That flips the
# cleaning policy relative to ISIC/PAD above: every image dropped here silently
# CHANGES THE BENCHMARK, so filtering runs in two tiers:
#
#   Tier 1 — integrity (row is DROPPED, logged to excluded_images.csv):
#       unreadable / corrupt / decode bomb / native side < min_size / missing file.
#       These are not valid model inputs at all.
#   Tier 2 — quality (row is KEPT, flagged in quality_flags.csv):
#       `uninformative`, `duplicate`. Reported so metrics can be recomputed on
#       the filtered subset, proving the verdict does not depend on the filter.
#
# NB: is_uninformative's thresholds were calibrated on ISIC dermoscopy tiles; a
# flat clinical photo of uniform skin can trip them. That is exactly why tier 2
# only flags — dropping would bias the fairness numbers toward whichever skin
# tone happens to photograph flatter. See docs/PREPROCESSING.md §1.1.
# ------------------------------------------------------------------

# HAM10000 7-class dx -> binary. Mirrors configs/data/ham10000.yaml label_mapping.
# akiec (actinic keratosis / intraepithelial carcinoma) is a borderline call —
# the `dx` column is kept in the returned frame so an akiec-excluded sensitivity
# variant can be derived without reprocessing the images.
HAM10000_LABEL_MAP = {
    "mel": 1, "bcc": 1, "akiec": 1,
    "nv": 0, "bkl": 0, "df": 0, "vasc": 0,
}

# Fitzpatrick17k three_partition_label -> binary. `non-neoplastic` (inflammatory
# / infectious conditions) is outside the benign-vs-malignant task the models
# were trained for; it maps to 0 here but is tagged in the returned frame so both
# label conventions can be reported.
FITZPATRICK_LABEL_MAP = {"malignant": 1, "benign": 0, "non-neoplastic": 0}


def _clean_external_image(
    src: Path,
    dst: Path,
    image_size: int = 224,
    min_size: int = 32,
    center_crop_frac: float = 1.0,
) -> tuple[Image.Image | None, str | None]:
    """Load → (optional centre crop) → resize → save one external-test image.

    Tier-1 integrity only. Returns ``(img, None)`` on success and
    ``(None, reason)`` when the image fails integrity and the caller must drop
    the row. Tier-2 quality flags are NOT decided here — the caller runs
    ``is_uninformative`` / the md5 check and keeps the row either way.

    The resize squashes to a square exactly like ``process_isic2024`` /
    ``process_pad_ufes_20`` do, so external images reach the model with the SAME
    geometry the training images had. An aspect-preserving crop here would stack
    a preprocessing confound on top of the domain shift being measured — which
    is why ``center_crop_frac=1.0`` (no crop) is the default and the HEADLINE
    variant.

    ``center_crop_frac < 1.0`` deliberately introduces exactly one extra
    variable, for the framing experiment described in `docs/PREPROCESSING.md
    §1.2`: it keeps the central ``frac`` of BOTH sides, so the aspect ratio is
    unchanged and the squash that follows is identical to the headline path.
    The only thing that moves is the field of view — which is what an on-device
    "crop the lesion before inference" pipeline would change. Callers MUST give
    each fraction its own ``dst`` tree: the ``dst.exists()`` fast-path below
    cannot tell a 70%-crop file from an uncropped one, so sharing a directory
    would silently evaluate the headline pixels under a crop variant's name.
    """
    if not 0.0 < center_crop_frac <= 1.0:
        raise ValueError(f"center_crop_frac must be in (0, 1], got {center_crop_frac}")
    try:
        if dst.exists():
            # Fast-path: a previous run already resized this image. Reload it so
            # the caller's quality flags are still computed. min_size is not
            # re-checkable on this path (the file on disk is already image_size).
            return Image.open(dst).convert("RGB"), None
        if not src.exists():
            return None, "missing_file"
        img = Image.open(src).convert("RGB")
        # min_size is judged on the RAW frame, deliberately BEFORE any crop: a
        # crop variant must drop exactly the same rows as the headline, or the
        # framing comparison stops being paired. The cost is that a marginal
        # image can end up very small after a 50% crop; that shows up as blur in
        # the metric, which is the honest outcome, not as a silent row drop.
        if min(img.size) < min_size:
            return None, f"too_small: {img.size}"
        if center_crop_frac < 1.0:
            # Crop on the RAW pixels, before the squash — cropping the already
            # resized 224 square would throw away detail the crop is meant to
            # zoom into.
            w, h = img.size
            cw, ch = max(1, round(w * center_crop_frac)), max(1, round(h * center_crop_frac))
            left, top = (w - cw) // 2, (h - ch) // 2
            img = img.crop((left, top, left + cw, top + ch))
        img = img.resize((image_size, image_size), Image.LANCZOS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        img.save(dst)
        return img, None
    except (OSError, ValueError, Image.DecompressionBombError) as e:
        return None, f"corrupt: {e}"


def _write_external_logs(processed_dir: Path, excluded: list[dict], flagged: list[dict]) -> None:
    """Persist the two-tier logs side by side (tier 1 dropped / tier 2 kept).

    Both files are written even when empty (header only). The ISIC/PAD writers
    above guard on ``if excluded:``, which leaves a PREVIOUS run's log in place
    when a later run finds nothing — and a stale log here would be quoted as this
    run's exclusion count in the thesis.
    """
    processed_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(excluded, columns=["image_id", "reason"]).to_csv(
        processed_dir / "excluded_images.csv", index=False
    )
    pd.DataFrame(flagged, columns=["image_id", "flags"]).to_csv(
        processed_dir / "quality_flags.csv", index=False
    )


def _index_images(dirs: list[Path], exts: tuple[str, ...] = (".jpg", ".jpeg", ".png")) -> dict[str, Path]:
    """Map ``file stem -> path`` across candidate image dirs (first hit wins).

    HAM10000 ships as two zips (``HAM10000_images_part_1/2``) that people extract
    in inconsistent layouts, so the images are located by stem instead of by an
    assumed directory.
    """
    index: dict[str, Path] = {}
    for d in dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if p.suffix.lower() in exts and p.stem not in index:
                index[p.stem] = p
    return index


def process_ham10000(
    raw_dir: str | Path,
    processed_dir: str | Path,
    image_size: int = 224,
    min_size: int = 32,
    label_mapping: dict[str, int] | None = None,
) -> pd.DataFrame:
    """
    Process HAM10000 for CROSS-DOMAIN evaluation (never training).

    Raw structure expected (either layout works):
        raw_dir/
          HAM10000_metadata.csv     <- lesion_id, image_id, dx, dx_type, age, sex, localization
          images/                   <- or HAM10000_images_part_1/ + _part_2/

    Returns one row per surviving IMAGE with columns:
        image_id, patient_id, image_path, label, class_name, source, dx,
        lesion_id, quality_flags, is_lesion_representative

    ``is_lesion_representative`` marks the first image (by sorted image_id — a
    deterministic, reproducible pick) of each ``lesion_id``. HAM10000 holds
    several shots of the same lesion, which the md5 dedup below CANNOT catch
    (different shots = different pixels); treating them as independent samples
    would shrink confidence intervals artificially. ``dx`` is kept so the
    akiec-as-malignant convention can be re-tested without reprocessing.
    """
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    label_mapping = dict(label_mapping) if label_mapping else dict(HAM10000_LABEL_MAP)

    metadata_csv = raw_dir / "HAM10000_metadata.csv"
    if not metadata_csv.exists():
        metadata_csv = raw_dir / "metadata.csv"
    if not metadata_csv.exists():
        raise FileNotFoundError(
            f"HAM10000 metadata not found: {raw_dir}/HAM10000_metadata.csv (or metadata.csv)"
        )

    metadata = pd.read_csv(metadata_csv)
    for col in ("image_id", "lesion_id", "dx"):
        if col not in metadata.columns:
            raise KeyError(f"HAM10000 metadata is missing required column '{col}' ({metadata_csv})")

    image_index = _index_images([
        raw_dir / "images",
        raw_dir / "HAM10000_images_part_1",
        raw_dir / "HAM10000_images_part_2",
        raw_dir,
    ])
    if not image_index:
        raise FileNotFoundError(f"No HAM10000 image files found under {raw_dir}")

    class_names = {0: "benign", 1: "malignant"}
    records: list[dict] = []
    excluded: list[dict] = []
    flagged: list[dict] = []
    seen_hashes: dict[str, str] = {}  # md5 -> first image_id carrying it
    unmapped = 0

    for _, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing HAM10000"):
        image_id = str(row["image_id"])
        dx = str(row["dx"]).lower()
        label = label_mapping.get(dx)
        if label is None:
            unmapped += 1
            continue

        class_name = class_names[label]
        dst = processed_dir / class_name / f"{image_id}.jpg"
        img, drop_reason = _clean_external_image(
            src=image_index.get(image_id, raw_dir / f"{image_id}.jpg"),
            dst=dst,
            image_size=image_size,
            min_size=min_size,
        )
        if img is None:
            excluded.append({"image_id": image_id, "reason": drop_reason})
            continue

        # --- Tier 2: flag, never drop ---
        flags: list[str] = []
        if is_uninformative(img):
            flags.append("uninformative")
        img_hash = hashlib.md5(img.tobytes()).hexdigest()
        if img_hash in seen_hashes:
            flags.append(f"duplicate_of:{seen_hashes[img_hash]}")
        else:
            seen_hashes[img_hash] = image_id
        if flags:
            flagged.append({"image_id": image_id, "flags": ";".join(flags)})

        records.append({
            "image_id": image_id,
            # Namespaced so a HAM lesion id can never collide with an ISIC/PAD
            # patient id if these frames are ever concatenated.
            "patient_id": f"ham_{row['lesion_id']}",
            "image_path": str(dst),
            "label": label,
            "class_name": class_name,
            "source": "ham10000",
            "dx": dx,
            "lesion_id": str(row["lesion_id"]),
            "quality_flags": ";".join(flags),
        })

    _write_external_logs(processed_dir, excluded, flagged)

    df = pd.DataFrame(records)
    if df.empty:
        raise RuntimeError(
            f"process_ham10000: 0 of {len(metadata)} rows produced an image. Check that "
            f"image_id values (e.g. {str(metadata['image_id'].iloc[0])!r}) match files under {raw_dir}."
        )

    # One representative image per lesion — deterministic (first sorted image_id).
    df = df.sort_values(["lesion_id", "image_id"], kind="mergesort").reset_index(drop=True)
    df["is_lesion_representative"] = ~df.duplicated(subset="lesion_id", keep="first")

    print(
        f"HAM10000 — images: {len(df)} | lesions: {df['lesion_id'].nunique()} | "
        f"benign: {(df['label']==0).sum()} | malignant: {(df['label']==1).sum()} | "
        f"prevalence: {df['label'].mean():.4f} | "
        f"dropped (tier 1 integrity): {len(excluded)} | "
        f"flagged (tier 2 quality, KEPT): {len(flagged)} | "
        f"dx not in label_mapping: {unmapped}"
    )
    return df


def process_fitzpatrick17k(
    raw_dir: str | Path,
    processed_dir: str | Path,
    image_size: int = 224,
    min_size: int = 32,
    tone_col: str = "fitzpatrick_scale",
    label_mapping: dict[str, int] | None = None,
    center_crop_frac: float = 1.0,
) -> pd.DataFrame:
    """
    Process Fitzpatrick17k for FAIRNESS evaluation (never training).

    Raw structure expected (produced by scripts/download_fitzpatrick17k.py):
        raw_dir/
          metadata_downloaded.csv   <- rows whose image downloaded + md5-verified
          images/<md5hash>.jpg

    Row-level filters applied BEFORE any image work:
      * ``tone_col`` missing / -1  → dropped (unknown skin tone is useless for a
        fairness breakdown, and -1 is Fitzpatrick17k's explicit "unknown" code).

    ``three_partition_label`` is CARRIED THROUGH rather than filtered, so the
    caller can emit both label conventions (drop `non-neoplastic` vs merge it
    into benign) from a single pass.

    ``center_crop_frac`` (default 1.0 = the headline, uncropped variant) keeps
    the central fraction of each raw image before the squash, for the framing
    experiment in `docs/PREPROCESSING.md §1.2`. Every fraction needs its OWN
    ``processed_dir`` — see ``_clean_external_image``.

    Returns columns: image_id, patient_id, image_path, label, class_name, source,
    fitzpatrick_scale, three_partition_label, quality_flags.
    """
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    label_mapping = dict(label_mapping) if label_mapping else dict(FITZPATRICK_LABEL_MAP)

    metadata_csv = raw_dir / "metadata_downloaded.csv"
    if not metadata_csv.exists():
        raise FileNotFoundError(
            f"Fitzpatrick17k download manifest not found: {metadata_csv}. "
            f"Run: python scripts/download_fitzpatrick17k.py --raw-dir {raw_dir}"
        )

    # reset_index so the iterrows() index below is guaranteed positional and
    # stays aligned with the tone series taken via .iloc.
    metadata = pd.read_csv(metadata_csv).reset_index(drop=True)
    for col in ("md5hash", "three_partition_label"):
        if col not in metadata.columns:
            raise KeyError(f"Fitzpatrick17k metadata is missing required column '{col}' ({metadata_csv})")
    if tone_col not in metadata.columns:
        raise KeyError(
            f"Fitzpatrick17k metadata has no skin-tone column '{tone_col}'. "
            f"Available: {sorted(metadata.columns)}. Some releases annotate tone as "
            f"'fitzpatrick_centaur' instead — pick one explicitly and record it in docs."
        )
    if "fitzpatrick_centaur" in metadata.columns and tone_col != "fitzpatrick_centaur":
        print(
            f"NOTE: this release also carries 'fitzpatrick_centaur'; grouping uses "
            f"'{tone_col}'. State the choice in the fairness report."
        )

    images_dir = raw_dir / "images"
    class_names = {0: "benign", 1: "malignant"}
    records: list[dict] = []
    excluded: list[dict] = []
    flagged: list[dict] = []
    seen_hashes: dict[str, str] = {}
    dropped_tone = 0
    unmapped = 0

    tone_series = pd.to_numeric(metadata[tone_col], errors="coerce")

    for idx, row in tqdm(metadata.iterrows(), total=len(metadata), desc="Processing Fitzpatrick17k"):
        tone = tone_series.iloc[idx]
        if pd.isna(tone) or int(tone) < 1:
            dropped_tone += 1
            continue

        partition = str(row["three_partition_label"]).strip().lower()
        label = label_mapping.get(partition)
        if label is None:
            unmapped += 1
            continue

        md5hash = str(row["md5hash"])
        image_id = f"fitz_{md5hash}"
        class_name = class_names[label]
        dst = processed_dir / class_name / f"{image_id}.jpg"
        img, drop_reason = _clean_external_image(
            src=images_dir / f"{md5hash}.jpg",
            dst=dst,
            image_size=image_size,
            min_size=min_size,
            center_crop_frac=center_crop_frac,
        )
        if img is None:
            excluded.append({"image_id": image_id, "reason": drop_reason})
            continue

        flags: list[str] = []
        if is_uninformative(img):
            flags.append("uninformative")
        img_hash = hashlib.md5(img.tobytes()).hexdigest()
        if img_hash in seen_hashes:
            flags.append(f"duplicate_of:{seen_hashes[img_hash]}")
        else:
            seen_hashes[img_hash] = image_id
        if flags:
            flagged.append({"image_id": image_id, "flags": ";".join(flags)})

        records.append({
            "image_id": image_id,
            # No patient/lesion grouping exists in this atlas-sourced set — every
            # row is an independent image, so the group key is the image itself.
            "patient_id": image_id,
            "image_path": str(dst),
            "label": label,
            "class_name": class_name,
            "source": "fitzpatrick17k",
            "fitzpatrick_scale": int(tone),
            "three_partition_label": partition,
            "quality_flags": ";".join(flags),
        })

    _write_external_logs(processed_dir, excluded, flagged)

    df = pd.DataFrame(records)
    if df.empty:
        raise RuntimeError(
            f"process_fitzpatrick17k: 0 of {len(metadata)} rows produced an image. "
            f"Check that {images_dir} holds <md5hash>.jpg files."
        )

    print(
        f"Fitzpatrick17k — images: {len(df)} | "
        f"benign: {(df['label']==0).sum()} | malignant: {(df['label']==1).sum()} | "
        f"prevalence: {df['label'].mean():.4f} | "
        f"dropped (unknown skin tone): {dropped_tone} | "
        f"dropped (tier 1 integrity): {len(excluded)} | "
        f"flagged (tier 2 quality, KEPT): {len(flagged)} | "
        f"label not in mapping: {unmapped}"
    )
    return df


# ------------------------------------------------------------------
# Stratified GroupKFold splits
# ------------------------------------------------------------------

def generate_group_kfold_splits(
    df: pd.DataFrame,
    splits_dir: str | Path,
    n_splits: int = 5,
    group_col: str = "patient_id",
    label_col: str = "label",
    seed: int = 42,
    test_holdout_splits: int = 6,
) -> list[dict]:
    """
    Leak-free split layout:
      1. Carve a patient-disjoint, label-stratified **held-out test set** —
         1/test_holdout_splits of the data (~17% with the default 6) — that NO
         fold ever trains or validates on.
      2. Run StratifiedGroupKFold(n_splits) on the remaining dev pool for the
         train/val folds.

    Both steps group by `group_col` (no patient leakage) and stratify by
    `label_col` (benign:malignant ratio preserved). Because every fold's model
    is later evaluated on the SAME independent test_split, the per-fold test
    metrics are unbiased and directly comparable (e.g. paired KD vs baseline).

    NOTE: this replaces the previous design where test_split.csv was fold 0's
    val set — under which folds 1..4 trained on the test samples (leakage; their
    test metrics were optimistically inflated).

    Saves:
      splits_dir/test_split.csv                 <- independent held-out test
      splits_dir/fold_{i}/{train,val}_split.csv

    Returns:
        List of dicts with 'fold', 'train_df', 'val_df' for each fold.
    """
    splits_dir = Path(splits_dir)
    splits_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: held-out test = first fold of a group-stratified split ---
    holdout = StratifiedGroupKFold(n_splits=test_holdout_splits, shuffle=True, random_state=seed)
    dev_idx, test_idx = next(holdout.split(df, df[label_col].values, df[group_col].values))
    dev_df = df.iloc[dev_idx].reset_index(drop=True)
    test_df = df.iloc[test_idx].reset_index(drop=True)
    test_df.to_csv(splits_dir / "test_split.csv", index=False)

    # --- Step 2: n_splits-fold CV on the dev pool only (test patients excluded) ---
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    dev_groups = dev_df[group_col].values
    dev_labels = dev_df[label_col].values

    folds = []
    for fold_idx, (train_idx, val_idx) in enumerate(sgkf.split(dev_df, dev_labels, dev_groups)):
        fold_dir = splits_dir / f"fold_{fold_idx}"
        fold_dir.mkdir(exist_ok=True)

        train_df = dev_df.iloc[train_idx].reset_index(drop=True)
        val_df = dev_df.iloc[val_idx].reset_index(drop=True)

        train_df.to_csv(fold_dir / "train_split.csv", index=False)
        val_df.to_csv(fold_dir / "val_split.csv", index=False)

        folds.append({"fold": fold_idx, "train_df": train_df, "val_df": val_df})

        print(
            f"Fold {fold_idx} — train: {len(train_df)} "
            f"(mal={(train_df[label_col]==1).sum()}) | "
            f"val: {len(val_df)} "
            f"(mal={(val_df[label_col]==1).sum()})"
        )

    print(
        f"\nHeld-out test: {len(test_df)} samples "
        f"(mal={(test_df[label_col]==1).sum()}) — patient-disjoint + stratified, "
        f"1/{test_holdout_splits} of data, independent of all {n_splits} folds"
    )

    return folds
