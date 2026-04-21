import os
import tempfile

import pandas as pd
import pytest
from PIL import Image

from src.data.dataset import SkinLesionDataset


@pytest.fixture
def tmp_dataset(tmp_path):
    """Create a minimal fake dataset with CSV and dummy images."""
    images_dir = tmp_path / "images"
    images_dir.mkdir()

    records = []
    for i in range(6):
        img_path = images_dir / f"img_{i}.jpg"
        Image.new("RGB", (224, 224), color=(i * 40, 100, 150)).save(img_path)
        records.append({"image_path": str(img_path), "label": i % 2, "class_name": ["benign", "malignant"][i % 2]})

    csv_path = tmp_path / "split.csv"
    pd.DataFrame(records).to_csv(csv_path, index=False)
    return csv_path


def test_dataset_len(tmp_dataset):
    ds = SkinLesionDataset(tmp_dataset)
    assert len(ds) == 6


def test_dataset_getitem_returns_image_and_label(tmp_dataset):
    ds = SkinLesionDataset(tmp_dataset)
    img, label = ds[0]
    assert isinstance(img, Image.Image)
    assert isinstance(label, int)


def test_dataset_labels_property(tmp_dataset):
    ds = SkinLesionDataset(tmp_dataset)
    labels = ds.labels
    assert len(labels) == 6
    assert all(isinstance(l, int) for l in labels)
