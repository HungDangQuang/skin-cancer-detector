import torch
import torch.nn as nn


def build_optimizer(cfg, model: nn.Module) -> torch.optim.Optimizer:
    """
    Build optimizer with differential learning rates for backbone vs head.

    If cfg.training.optimizer has lr_backbone and lr_head, uses differential LR.
    Otherwise falls back to a single lr for all parameters.

    Supported: adamw, adam, sgd
    """
    opt_cfg = cfg.training.optimizer
    name = opt_cfg.name.lower()
    weight_decay = opt_cfg.get("weight_decay", 1e-4)
    betas = tuple(opt_cfg.get("betas", [0.9, 0.999]))

    # Differential LR: backbone gets lower LR, head gets higher LR
    lr_backbone = opt_cfg.get("lr_backbone", None)
    lr_head = opt_cfg.get("lr_head", None)

    if lr_backbone is not None and lr_head is not None:
        head_params, backbone_params = [], []
        for pname, param in model.named_parameters():
            if not param.requires_grad:
                continue
            if "head" in pname:
                head_params.append(param)
            else:
                backbone_params.append(param)

        param_groups = [
            {"params": backbone_params, "lr": lr_backbone},
            {"params": head_params, "lr": lr_head},
        ]
    else:
        lr = opt_cfg.get("lr", 1e-4)
        param_groups = [{"params": [p for p in model.parameters() if p.requires_grad], "lr": lr}]

    if name == "adamw":
        return torch.optim.AdamW(param_groups, weight_decay=weight_decay, betas=betas)
    elif name == "adam":
        return torch.optim.Adam(param_groups, weight_decay=weight_decay, betas=betas)
    elif name == "sgd":
        momentum = opt_cfg.get("momentum", 0.9)
        return torch.optim.SGD(param_groups, momentum=momentum, weight_decay=weight_decay)
    else:
        raise ValueError(f"Unknown optimizer '{name}'. Supported: adam, adamw, sgd")
