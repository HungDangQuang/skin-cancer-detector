from pathlib import Path

from omegaconf import DictConfig, OmegaConf


def load_config(config_path: str | Path) -> DictConfig:
    """Load a YAML config file into an OmegaConf DictConfig.

    If the file is a Hydra *root* config (i.e. it has a ``defaults:`` list
    that composes config groups like ``data``/``teacher``/``student``), plain
    ``OmegaConf.load`` would leave those groups unmerged and accessing
    ``cfg.data`` would raise ``Missing key data``. In that case compose the
    config through Hydra so the groups are merged. Already-resolved configs
    (e.g. a saved ``experiments/<run>/config.yaml``) have no ``defaults`` key
    and are loaded as-is.
    """
    cfg = OmegaConf.load(config_path)

    if "defaults" in cfg:
        from hydra import compose, initialize_config_dir
        from hydra.core.global_hydra import GlobalHydra

        path = Path(config_path).resolve()
        if GlobalHydra.instance().is_initialized():
            GlobalHydra.instance().clear()
        with initialize_config_dir(version_base=None, config_dir=str(path.parent)):
            cfg = compose(config_name=path.stem)

    return cfg


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
