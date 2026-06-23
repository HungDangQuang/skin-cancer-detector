import os
import random

import numpy as np
import torch


def set_seed(seed: int = 42, deterministic: bool = True) -> None:
    """Set all random seeds for reproducibility.

    Args:
        seed: Base seed for python/numpy/torch RNGs.
        deterministic: When True (default — the 30-run baseline behavior), force
            cuDNN to deterministic algorithms (benchmark off) for bit-exact
            reproducibility. Set False for heavy attention backbones (e.g.
            maxvit_base) whose deterministic backward path can raise
            `CUDNN_STATUS_INTERNAL_ERROR`; this lets cuDNN pick a working
            algorithm (benchmark on) at the cost of run-to-run determinism.
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = deterministic
    torch.backends.cudnn.benchmark = not deterministic
