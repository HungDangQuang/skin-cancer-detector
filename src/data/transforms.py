import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
from PIL import Image


def build_transforms(cfg, split: str = "train"):
    """
    Build an Albumentations transform pipeline from config.

    Args:
        cfg: augmentation config (OmegaConf DictConfig)
        split: 'train', 'val', or 'test'

    Returns:
        A callable that accepts a PIL Image and returns a tensor.
    """
    image_size = getattr(cfg, "image_size", 224)
    aug_cfg = cfg.augmentation if hasattr(cfg, "augmentation") else None

    if split == "train" and aug_cfg is not None:
        transform = A.Compose([
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.2, rotate_limit=45, p=0.5),
            A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
            A.GaussianBlur(blur_limit=(3, 7), p=0.2),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])
    else:
        transform = A.Compose([
            A.Resize(image_size, image_size),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])

    def apply(image: Image.Image):
        img_np = np.array(image)
        result = transform(image=img_np)
        return result["image"]

    return apply
