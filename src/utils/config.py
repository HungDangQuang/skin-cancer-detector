from pathlib import Path

from omegaconf import DictConfig, OmegaConf


def load_config(config_path: str | Path) -> DictConfig:
    """Load a YAML config file into an OmegaConf DictConfig."""
    return OmegaConf.load(config_path)


def merge_configs(*configs: DictConfig) -> DictConfig:
    """Merge multiple configs left-to-right (later configs override earlier)."""
    return OmegaConf.merge(*configs)


def config_to_dict(cfg: DictConfig) -> dict:
    """Convert OmegaConf config to a plain Python dict."""
    return OmegaConf.to_container(cfg, resolve=True)


def save_config(cfg: DictConfig, path: str | Path) -> None:
    """Save config to a YAML file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    OmegaConf.save(cfg, path)
