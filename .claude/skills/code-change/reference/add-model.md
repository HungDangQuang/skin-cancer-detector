---
name: add-model
description: Add a new model architecture to the project. Use when the user asks to "add a new model", "support <arch>", "add ResNet/ViT/etc as student", or wants to extend MODEL_REGISTRY. NOT for reviewing model code you already changed (use review-training).
---

# add-model

Adds a new model architecture to the registry so it can be used as teacher or student. Must touch 3 places in lockstep — `src/models/<file>.py`, `src/models/registry.py`, and `configs/<role>/<name>.yaml`.

## When to use

- "Add ResNet50 as another student"
- "Support a new MobileViT variant"
- "Wire up <some timm backbone> for KD"

## Invariants every model must obey

These are enforced by `BaseModel` (`src/models/base_model.py`) and the rest of the pipeline. Breaking them silently corrupts training.

1. **Output shape**: `forward(x) -> Tensor of shape (B,)`. **Single raw logit.** No sigmoid, no two-class softmax, no `(B, 1)` shape — must be 1D.
2. **Backbone via timm**: use `timm.create_model(name, pretrained=True, num_classes=0)` so it returns features only.
3. **Head**: always `build_head(in_features, dropout=...)` from `src/models/heads.py` — this is `Dropout → Linear(in_features, 1)`. Never write a custom head unless you know what you're doing.
4. **Subclass `BaseModel`**: get `freeze_backbone()` / `unfreeze()` / `num_parameters()` for free.

## Step-by-step

### Step 1 — New model class

Create `src/models/<arch>.py` mirroring the existing pattern. Look at `src/models/efficientnet.py` for the simplest reference (~25 lines).

```python
import timm
import torch

from .base_model import BaseModel
from .heads import build_head


class MyArchModel(BaseModel):
    """<one-line description>."""

    def __init__(self, cfg):
        super().__init__()
        backbone_name = cfg.model.get("backbone", "<timm_default>")
        pretrained    = cfg.model.get("pretrained", True)
        dropout       = cfg.model.head.get("dropout", 0.2)

        self.backbone = timm.create_model(backbone_name, pretrained=pretrained, num_classes=0)
        in_features = self.backbone.num_features
        self.head = build_head(in_features, dropout=dropout)

        if cfg.model.get("freeze_backbone", False):
            self.freeze_backbone()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.backbone(x)).squeeze(1)
```

### Step 2 — Register it

Edit `src/models/registry.py`:
```python
from .myarch import MyArchModel

MODEL_REGISTRY: dict = {
    # ... existing entries ...
    "<my_arch_key>": MyArchModel,
}
```

### Step 3 — Add a config

Create `configs/student/<my_arch_key>.yaml` (or `configs/teacher/...` if it's a teacher):
```yaml
name: <my_arch_key>
role: student              # or teacher
paradigm: <one of: compound_scaling | nas_optimized | hybrid_cnn_transformer | other>
backbone: <timm name>
pretrained: true
num_classes: 1

head:
  dropout: 0.2

freeze_backbone: false
```

The `name:` field must match the registry key.

### Step 4 — Verify

```bash
# Quick local sanity check (no training):
python -c "
from omegaconf import OmegaConf
from src.models.registry import MODEL_REGISTRY, build_model_from_name
import yaml
cfg = OmegaConf.load('configs/config.yaml')
cfg.student = OmegaConf.load('configs/student/<my_arch_key>.yaml')
cfg.teacher = OmegaConf.load('configs/teacher/efficientnetv2_m.yaml')
model, _ = build_model_from_name('<my_arch_key>', cfg)
import torch
out = model(torch.randn(2, 3, 224, 224))
assert out.shape == (2,), f'Expected (2,), got {out.shape}'
print('OK', model.num_parameters(), 'params')
"
```

### Step 5 — Test on the POC pipeline

```bash
make poc-teacher                     # if you added a teacher
bash slurm/submit.sh slurm/03_poc_student.slurm STUDENT=<my_arch_key>
```
Confirm it produces a checkpoint and `val_pauc` is non-zero.

### Step 6 — Add to docs

Update the model table in `docs/POC.md §1` and `CLAUDE.md` if needed.

## Common mistakes

- ❌ `forward` returns shape `(B, 1)` — breaks `BinaryFocalLoss` and `BinaryDistillationLoss` silently. Always `.squeeze(1)`.
- ❌ Sigmoid inside `forward` — losses expect raw logits.
- ❌ Forgot to add the registry entry — `build_model_from_name` raises `ValueError: Unknown model`.
- ❌ Config `name:` doesn't match registry key — same `ValueError`.
- ❌ Copy-pasted dropout from another model without checking — `MobileViT-S` uses 0.1, `MobileNetV3` uses 0.2, `EfficientNet-*` uses 0.3. Tune per arch if needed.
