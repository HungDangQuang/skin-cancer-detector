from pathlib import Path

from omegaconf import OmegaConf, open_dict

from .panderm import PanDermModel
from .privileged import PrivilegedTimmBackboneModel
from .timm_backbone import TimmBackboneModel

MODEL_REGISTRY: dict = {
    # SOTA set — one generic timm wrapper (`TimmBackboneModel`) covers every timm
    # arch; there is no per-arch logic, so no family-specific wrapper is needed.
    # Requires timm>=1.0 (mobilenetv4/fastvit/efficientformerv2/repvit are not in
    # 0.9.x). The lone exception is `panderm`, a domain-foundation teacher whose
    # weights ship OUT of timm (BEiT-style checkpoint) -> its own `PanDermModel`.
    # Teachers (high-capacity, frozen during KD)
    "efficientnetv2_m": TimmBackboneModel,
    "convnextv2_base": TimmBackboneModel,
    "maxvit_base": TimmBackboneModel,
    "panderm": PanDermModel,
    # Privileged (LUPI) teachers — image ⊕ tabular `tbp_lv_*` metadata fusion
    # (direction A). Same timm backbone as their plain counterpart; require
    # data.metadata_cols set. Student stays image-only (distills the fused
    # feature structure via RKD). See docs/metadata_training_plan.md §A.
    "efficientnetv2_m_privileged": PrivilegedTimmBackboneModel,
    "convnextv2_base_privileged": PrivilegedTimmBackboneModel,
    # Students (mobile-/on-device-latency-optimized)
    "mobilenetv4_conv_medium": TimmBackboneModel,
    "fastvit_sa12": TimmBackboneModel,
    "efficientformerv2_s2": TimmBackboneModel,
    "repvit_m1_0": TimmBackboneModel,
}


def build_model(cfg):
    """Instantiate the model specified in cfg.model.name."""
    name = cfg.model.name
    if name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model '{name}'. Available: {list(MODEL_REGISTRY.keys())}")
    return MODEL_REGISTRY[name](cfg)


def build_model_from_name(model_name: str, base_cfg) -> tuple:
    """
    Convenience helper for scripts that need to build a model by name.

    Looks up the model config in cfg.teacher or cfg.student,
    merges it into base_cfg under 'model', and returns (model, merged_cfg).

    Args:
        model_name: One of the keys in MODEL_REGISTRY.
        base_cfg: The full Hydra config (must have cfg.teacher and cfg.student).
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model '{model_name}'. Available: {list(MODEL_REGISTRY.keys())}")

    if base_cfg.teacher.name == model_name:
        model_subcfg = base_cfg.teacher
    elif base_cfg.student.name == model_name:
        model_subcfg = base_cfg.student
    else:
        # base_cfg's composed teacher/student doesn't match the requested name
        # (e.g. evaluate.py loading configs/config.yaml — student is always
        # mobilenetv4_conv_medium by default). Fall back to the standalone group config
        # so callers don't need to also pass a Hydra override.
        configs_dir = Path(__file__).resolve().parents[2] / "configs"
        for group in ("student", "teacher"):
            candidate = configs_dir / group / f"{model_name}.yaml"
            if candidate.is_file():
                model_subcfg = OmegaConf.load(candidate)
                break
        else:
            raise ValueError(
                f"Model '{model_name}' not in cfg.teacher / cfg.student and "
                f"no configs/{{teacher,student}}/{model_name}.yaml found. "
                f"Teacher: {base_cfg.teacher.name}, Student: {base_cfg.student.name}"
            )

    with open_dict(base_cfg):
        merged_cfg = OmegaConf.merge(base_cfg, {"model": OmegaConf.to_container(model_subcfg, resolve=True)})
    model = MODEL_REGISTRY[model_name](merged_cfg)
    return model, merged_cfg
