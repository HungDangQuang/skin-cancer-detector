#!/usr/bin/env python
"""
Run one checkpoint (or one .pte) over the mobile-eval bundle, emitting the SAME
`sample_id,logit,error` CSV the phone emits.

Contract: docs/MOBILE_EVAL_PIPELINE.md. Deliberately one image at a time on CPU,
because that is what the phone does — the project's routine evaluation
(run/evaluate_external.sh) uses CUDA with batch 64, and comparing that against a
phone number mixes four divergence sources into one delta instead of two.

Three arms are possible, and the pairs isolate different things:

    --checkpoint  PyTorch eager, host CPU      -> arm "server"
    --pte         ExecuTorch, host CPU         -> arm "host-executorch"
    (the phone)   ExecuTorch, phone CPU        -> arm "mobile"

    server vs host-executorch  = graph lowering alone (same decoder, same CPU)
    host-executorch vs mobile  = Android JPEG decoder + phone hardware

Venvs differ: --checkpoint needs the training venv (./.venv-linux), --pte needs
the isolated export venv (./.venv-export). run/infer_bundle.sh picks for you.

Usage:
    python scripts/infer_bundle.py --bundle data/mobile_eval_bundle \
        --model-name mobilenetv4_conv_medium \
        --checkpoint experiments/runs_newsplit_ddi/kd_.../fold_4/checkpoints/best_model.pth \
        --out reports/mobile_eval/server_logits.csv

    python scripts/infer_bundle.py --bundle data/mobile_eval_bundle \
        --pte exports/executorch_v2/mobilenetv4_conv_medium__ddi_fold4.pte \
        --out reports/mobile_eval/host_executorch_logits.csv

    # parity gate only: feed the pre-normalised tensors, skipping decode+normalise
    python scripts/infer_bundle.py --bundle data/mobile_eval_bundle --pte <pte> \
        --from-gate-bins --out reports/mobile_eval/gate_logits.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_preprocessor(meta: dict):
    """Steps 2-6 of the pipeline spec. Returns f(path) -> (1,3,H,W) float32."""
    from PIL import Image

    size = int(meta["image_size"])
    mean = np.asarray(meta["mean"], dtype=np.float32)
    std = np.asarray(meta["std"], dtype=np.float32)

    def prep(path: Path) -> np.ndarray:
        img = Image.open(path).convert("RGB")
        if img.size != (size, size):
            # Spec step 3: assert, never scale. A silent resize here would be
            # unattributable error in the final delta.
            raise ValueError(f"unexpected_size_{img.size[0]}x{img.size[1]}")
        arr = np.asarray(img, dtype=np.float32) / 255.0
        arr = (arr - mean) / std
        arr = np.ascontiguousarray(arr.transpose(2, 0, 1))
        return arr[None, ...]  # batch dim = 1

    return prep


def build_torch_runner(model_name: str, checkpoint: Path, config: str, threads: int):
    import torch

    from src.models.registry import build_model_from_name
    from src.utils.checkpoint import load_checkpoint
    from src.utils.config import load_config

    # Batch-1 inference over a tiny 224x224 graph does NOT benefit from all cores:
    # measured on a 64-core box, the default thread count gave 723 ms/image against
    # 29 ms at 8 threads and 43 ms at 1 — a 25x penalty from synchronisation
    # overhead. Pin it, and record the value in the output metadata.
    torch.set_num_threads(threads)

    cfg = load_config(config)
    model, _ = build_model_from_name(model_name, cfg)
    load_checkpoint(str(checkpoint), model, device="cpu")
    model.eval()

    def run(x: np.ndarray) -> float:
        with torch.no_grad():
            out = model(torch.from_numpy(x))
        return float(np.asarray(out).reshape(-1)[0])

    return run, "pytorch-eager"


def build_pte_runner(pte: Path):
    """Same dual-API dance as scripts/check_pte_parity.py — ExecuTorch renamed it."""
    try:
        from executorch.runtime import Runtime

        method = Runtime.get().load_program(pte).load_method("forward")

        def run(x: np.ndarray) -> float:
            import torch

            return float(np.asarray(method.execute([torch.from_numpy(x)])[0]).reshape(-1)[0])

        return run, "executorch(runtime)"
    except Exception as exc:  # noqa: BLE001 — any failure just means "try the older API"
        logger.debug(f"executorch.runtime unavailable ({exc}); trying pybindings")

    try:
        from executorch.extension.pybindings.portable_lib import _load_for_executorch
    except ImportError as exc:
        raise SystemExit(
            f"ExecuTorch runtime unavailable ({exc}).\n"
            "This needs the ISOLATED export venv: bash run/setup_export_env.sh"
        )
    module = _load_for_executorch(str(pte))

    def run(x: np.ndarray) -> float:
        import torch

        return float(np.asarray(module.forward([torch.from_numpy(x)])[0]).reshape(-1)[0])

    return run, "executorch(pybindings)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--config", default="configs/config.yaml")
    ap.add_argument("--model-name", default=None)
    ap.add_argument("--checkpoint", type=Path, default=None)
    ap.add_argument("--pte", type=Path, default=None)
    ap.add_argument(
        "--from-gate-bins",
        action="store_true",
        help="read l1_gate/inputs/*.bin (already normalised) instead of decoding JPEGs",
    )
    ap.add_argument(
        "--threads",
        type=int,
        default=8,
        help="CPU threads for the PyTorch arm. NOT the default: batch-1 inference is "
        "25x slower with all 64 cores than with 8 (see build_torch_runner).",
    )
    ap.add_argument("--start", type=int, default=0, help="first manifest row (shard support)")
    ap.add_argument("--end", type=int, default=None, help="one past the last row (exclusive)")
    ap.add_argument("--log-every", type=int, default=2000)
    ap.add_argument("--flush-every", type=int, default=500, help="rows between disk flushes")
    ap.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        help="overwrite the output instead of skipping rows already present",
    )
    args = ap.parse_args()

    if bool(args.checkpoint) == bool(args.pte):
        ap.error("pass exactly one of --checkpoint or --pte")
    if args.checkpoint and not args.model_name:
        ap.error("--checkpoint requires --model-name")

    meta = json.loads((args.bundle / "meta.json").read_text())
    with open(args.bundle / "manifest.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    n_total = len(rows)
    rows = rows[args.start : (args.end if args.end is not None else n_total)]
    logger.info(
        f"Bundle: {n_total} rows | shard [{args.start}:{args.end}] -> {len(rows)} rows "
        f"| spec {meta.get('spec')}"
    )

    if args.checkpoint:
        run, runtime = build_torch_runner(
            args.model_name, args.checkpoint, args.config, args.threads
        )
        runtime = f"{runtime}(threads={args.threads})"
    else:
        # ExecuTorch picks its own threading; there is no set_num_threads equivalent
        # on the runtime API, so the value is recorded but not enforced here.
        run, runtime = build_pte_runner(args.pte)
    logger.info(f"Runtime: {runtime} | device cpu | batch 1")

    prep = build_preprocessor(meta)
    shape = tuple(meta.get("input_shape", [3, 224, 224]))
    expected = int(np.prod(shape))

    args.out.parent.mkdir(parents=True, exist_ok=True)

    # Resume: the spec requires the phone harness to be restartable (section 5.2.2),
    # and a 70k-row host run deserves the same. Rows already present are skipped and
    # the file is appended to, so a killed run does not start over.
    done: set[str] = set()
    if args.resume and args.out.is_file():
        with open(args.out, newline="") as f:
            for rec in csv.DictReader(f):
                if rec.get("sample_id"):
                    done.add(rec["sample_id"])
        logger.info(f"Resuming: {len(done)} row(s) already in {args.out}")

    n_err = 0
    n_written = 0
    mode = "a" if done else "w"
    # newline="" keeps csv from doubling line endings; the reader side must still
    # tolerate CRLF (docs/GOTCHAS.md).
    with open(args.out, mode, newline="") as f:
        w = csv.writer(f)
        if not done:
            w.writerow(["sample_id", "logit", "error"])
        for i, rec in enumerate(rows):
            sid = rec["sample_id"]
            if sid in done:
                continue
            try:
                if args.from_gate_bins:
                    bin_path = args.bundle / "l1_gate" / "inputs" / f"{sid}.bin"
                    if not bin_path.is_file():
                        continue  # gate covers only the first --gate-n rows
                    arr = np.fromfile(bin_path, dtype=np.float32)
                    if arr.size != expected:
                        raise ValueError(f"bin_has_{arr.size}_floats_expected_{expected}")
                    x = arr.reshape(1, *shape)
                else:
                    x = prep(args.bundle / rec["image_file"])
                w.writerow([sid, f"{run(x):.7g}", ""])
                n_written += 1
            except Exception as exc:  # noqa: BLE001 — spec step 6: never drop a row
                n_err += 1
                w.writerow([sid, "", str(exc).replace(",", ";")[:120]])
                n_written += 1
            # Spec §5.2.1 requires the phone to flush every <=500 rows; the host arm
            # holds itself to the same rule, so a crash at row 70000 keeps 69500.
            if args.flush_every and (i + 1) % args.flush_every == 0:
                f.flush()
            if args.log_every and (i + 1) % args.log_every == 0:
                logger.info(f"  {i + 1}/{len(rows)}")

    logger.info(
        f"Wrote {args.out} | {n_written} new row(s) | {len(done)} resumed "
        f"| {n_err} error(s) | shard covered {len(rows)} manifest row(s)"
    )
    if n_err:
        logger.warning(f"{n_err} row(s) carry an error string — inspect before comparing arms.")


if __name__ == "__main__":
    main()
