"""
Export a trained student checkpoint to ExecuTorch (.pte) for Android on-device.

ISOLATED from the training stack: this is the only script that imports
`executorch`, and it runs in a dedicated venv (${DATASTORE_USER_DIR}/venv-export,
created by run/setup_export_env.sh) so the ExecuTorch torch build can never
perturb the torch>=2.2 the training/eval jobs depend on. Submit via
run/export_executorch.sh.

Why ExecuTorch and not TFLite: the goal is to run the PyTorch student model
*as-is* on device without converting into another framework. ExecuTorch is the
PyTorch-native on-device path (torch.export → .pte). It uses torch.export (not
torch.jit.script), which handles the dynamic control flow that makes scripting
fail on the transformer students (fastvit / efficientformerv2).

Backends:
  - xnnpack (default): lower to the XNNPACK delegate → fast CPU on Android.
  - none: portable (reference) ops only — slower, but a fallback if a given
    architecture has an op XNNPACK can't partition.

Usage (inside the export venv):
    python scripts/export_executorch.py --model-name mobilenetv4_conv_medium \\
        --checkpoint experiments/runs/kd_..._to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import torch

from src.models.registry import MODEL_REGISTRY, build_model_from_name
from src.utils.checkpoint import load_checkpoint
from src.utils.config import load_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _import_executorch(backend: str):
    """Import the ExecuTorch AOT API, with a clear message if the venv is wrong.

    Returns (export_fn, to_edge_transform_and_lower, partitioners) where
    partitioners is [] for backend='none'.
    """
    try:
        from torch.export import export
        from executorch.exir import to_edge_transform_and_lower
    except ImportError as exc:
        raise SystemExit(
            f"ExecuTorch / torch.export unavailable ({exc}).\n"
            "This script must run in the ISOLATED export venv. On the login node:\n"
            "    bash run/setup_export_env.sh\n"
            "then submit via run/export_executorch.sh (do NOT use the "
            "training venv)."
        )
    partitioners = []
    if backend == "xnnpack":
        try:
            from executorch.backends.xnnpack.partition.xnnpack_partitioner import (
                XnnpackPartitioner,
            )
            partitioners = [XnnpackPartitioner()]
        except ImportError as exc:
            raise SystemExit(
                f"XNNPACK partitioner unavailable ({exc}). Re-run "
                "run/setup_export_env.sh, or pass --backend none for a "
                "portable-ops fallback."
            )
    return export, to_edge_transform_and_lower, partitioners


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True,
                        choices=sorted(MODEL_REGISTRY.keys()))
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", default=None,
                        help="(.pte) path, default: exports/executorch/<model>.pte")
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--backend", choices=["xnnpack", "none"], default="xnnpack",
                        help="xnnpack = fast Android CPU delegate; none = portable ops")
    args = parser.parse_args()

    export, to_edge_transform_and_lower, partitioners = _import_executorch(args.backend)

    cfg = load_config(args.config)
    image_size = int(cfg.data.image_size)
    model, _ = build_model_from_name(args.model_name, cfg)
    load_checkpoint(args.checkpoint, model, device="cpu")
    model.eval()

    # Fixed input shape — mobile inference is always batch=1 at a known size.
    example = (torch.randn(1, 3, image_size, image_size),)

    # Sanity: eager forward must produce a single logit per item, shape (1,).
    with torch.no_grad():
        eager_out = model(*example)
    if tuple(eager_out.shape) != (1,):
        logger.warning(
            f"Unexpected eager output shape {tuple(eager_out.shape)} (expected (1,)); "
            "the model head may not be squeezing to a single logit."
        )

    logger.info(f"Exporting {args.model_name} (backend={args.backend}, "
                f"input 1x3x{image_size}x{image_size})")
    exported = export(model, example)
    lowered = to_edge_transform_and_lower(
        exported, partitioner=partitioners
    ).to_executorch()

    out_path = Path(args.output or f"exports/executorch/{args.model_name}.pte")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(lowered.buffer)

    size_mb = out_path.stat().st_size / 1024 ** 2
    logger.info(f"Wrote {out_path} ({size_mb:.2f} MB)")
    logger.info(
        "On-device parity check (do this in the Android app): feed the SAME "
        "preprocessed input through PC PyTorch and this .pte; require max|Δlogit| "
        "small (e.g. <1e-3) before trusting any on-device number."
    )


if __name__ == "__main__":
    main()
