"""Batch-shape helpers shared by the trainers and the evaluator."""


def unpack_batch(batch):
    """Normalize a DataLoader batch to ``(images, meta, mask, labels)``.

    Supports two shapes emitted by ``SkinLesionDataset``:
      * image-only 2-tuple ``(image, label)`` -> ``meta``/``mask`` are ``None``.
      * privileged 4-tuple ``(image, meta, mask, label)`` (direction A / LUPI).

    Callers branch with ``if meta is not None`` so the image-only path is
    byte-for-byte unchanged.
    """
    if len(batch) == 4:
        images, meta, mask, labels = batch
        return images, meta, mask, labels
    images, labels = batch
    return images, None, None, labels
