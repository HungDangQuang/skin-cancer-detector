import numpy as np
import pytest
import torch
from omegaconf import OmegaConf
from PIL import Image

from src.data.transforms import build_transforms


def make_cfg():
    return OmegaConf.create({"image_size": 224, "augmentation": {}})


def make_dummy_image(size=(300, 300)) -> Image.Image:
    arr = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
    return Image.fromarray(arr)


@pytest.mark.parametrize("split", ["train", "val", "test"])
def test_transform_output_shape(split):
    cfg = make_cfg()
    transform = build_transforms(cfg, split=split)
    img = make_dummy_image()
    tensor = transform(img)
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (3, 224, 224)


def test_transform_output_dtype():
    cfg = make_cfg()
    transform = build_transforms(cfg, split="val")
    img = make_dummy_image()
    tensor = transform(img)
    assert tensor.dtype == torch.float32
