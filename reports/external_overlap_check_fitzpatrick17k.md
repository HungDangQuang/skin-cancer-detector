# External-vs-internal overlap check — `fitzpatrick17k`

- internal splits scanned: `data/splits/isic2024` (11 CSV files)
- external images checked: 16012

## Layer 1 — image_id intersection

- skipped: this dataset's ids are md5-derived and share no namespace with the internal ISIC/PAD ids.

## Layer 2 — decoded-pixel md5 vs internal held-out test split

- internal test images hashed: 62040
- **overlapping images: 0**

## Verdict

✅ **No overlap.** Safe to use as an external test set.
