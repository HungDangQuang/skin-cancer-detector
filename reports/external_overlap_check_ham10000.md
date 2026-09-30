# External-vs-internal overlap check — `ham10000`

- internal splits scanned: `data/splits/isic2024` (11 CSV files)
- external images checked: 10015

## Layer 1 — image_id intersection

- internal image_ids: 372242
- **overlapping ids: 0**

## Layer 2 — decoded-pixel md5 vs internal held-out test split

- internal test images hashed: 62040
- **overlapping images: 0**

## Verdict

✅ **No overlap.** Safe to use as an external test set.
