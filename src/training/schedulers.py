import torch


def build_scheduler(cfg, optimizer: torch.optim.Optimizer):
    """
    Build LR scheduler from config, with optional linear warmup.

    Supported: cosine, step, exponential
    """
    sched_cfg = cfg.training.scheduler
    name = sched_cfg.name.lower()
    warmup_epochs = sched_cfg.get("warmup_epochs", 0)

    if name == "cosine":
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=sched_cfg.T_max,
            eta_min=sched_cfg.get("eta_min", 1e-6),
        )

    elif name == "step":
        scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer,
            step_size=sched_cfg.get("step_size", 10),
            gamma=sched_cfg.get("gamma", 0.1),
        )

    elif name == "exponential":
        scheduler = torch.optim.lr_scheduler.ExponentialLR(
            optimizer,
            gamma=sched_cfg.get("gamma", 0.95),
        )

    else:
        raise ValueError(f"Unknown scheduler '{name}'. Supported: cosine, step, exponential")

    if warmup_epochs > 0:
        warmup = torch.optim.lr_scheduler.LinearLR(
            optimizer, start_factor=0.01, end_factor=1.0, total_iters=warmup_epochs
        )
        return torch.optim.lr_scheduler.SequentialLR(
            optimizer, schedulers=[warmup, scheduler], milestones=[warmup_epochs]
        )

    return scheduler
