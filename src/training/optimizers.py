import torch
import torch.nn as nn


def build_optimizer(cfg, model: nn.Module) -> torch.optim.Optimizer:
    """
    Build optimizer from config.

    Supported: adam, adamw, sgd
    """
    opt_cfg = cfg.training.optimizer
    name = opt_cfg.name.lower()
    lr = opt_cfg.lr
    weight_decay = opt_cfg.get("weight_decay", 1e-4)

    params = [p for p in model.parameters() if p.requires_grad]

    if name == "adamw":
        betas = tuple(opt_cfg.get("betas", [0.9, 0.999]))
        return torch.optim.AdamW(params, lr=lr, weight_decay=weight_decay, betas=betas)

    elif name == "adam":
        betas = tuple(opt_cfg.get("betas", [0.9, 0.999]))
        return torch.optim.Adam(params, lr=lr, weight_decay=weight_decay, betas=betas)

    elif name == "sgd":
        momentum = opt_cfg.get("momentum", 0.9)
        return torch.optim.SGD(params, lr=lr, momentum=momentum, weight_decay=weight_decay)

    else:
        raise ValueError(f"Unknown optimizer '{name}'. Supported: adam, adamw, sgd")
