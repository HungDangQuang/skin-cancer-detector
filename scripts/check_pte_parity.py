"""
PC<->.pte numerical parity check (parity layer 1).

Runs the exported ExecuTorch program on the SAME fully-preprocessed inputs the
PyTorch reference logits were computed from, and asserts the two agree to within
a tolerance. Nothing on-device is trustworthy until this passes: a latency number
from a .pte that computes different logits is a number for a different model.

This is layer 1 of two. It isolates the *graph lowering* (torch.export ->
edge -> XNNPACK delegate) by feeding both sides identical float32 tensors from
data/benchmark_set/inputs/. Layer 2 — whether the Android app's own JPEG decode +
resize + normalize reproduces those tensors — is a separate check that belongs in
the app (docs/ANDROID_APP_SPEC.md; bilinear vs LANCZOS is the known trap there).

Runs in the ISOLATED export venv (./.venv-export) because it imports
`executorch`. Note that venv is installed with `pip install -e . --no-deps`, so
the training stack (pandas/albumentations/...) is NOT importable here — this
script deliberately uses only numpy, torch and the stdlib.

Usage (via the runner, which selects the export venv for you):
    bash run/check_pte_parity.sh MODEL=mobilenetv4_conv_medium

Or directly, inside ./.venv-export:
    python scripts/check_pte_parity.py --model-name mobilenetv4_conv_medium

Exit codes: 0 = parity holds, 1 = parity FAILED (max|dlogit| over tolerance).
"""
import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch

from src.utils.logger import get_logger

logger = get_logger(__name__)


def _load_pte_runner(pte_path: Path):
    """Return `run(tensor) -> np.ndarray` backed by the ExecuTorch runtime.

    ExecuTorch renamed its Python entry-point between releases, so try the
    modern `executorch.runtime` API first and fall back to the older pybindings
    one rather than pinning this script to a single ExecuTorch version.
    """
    try:
        from executorch.runtime import Runtime  # ExecuTorch >= 0.4-ish

        method = Runtime.get().load_program(pte_path).load_method("forward")

        def run(tensor):
            return np.asarray(method.execute([tensor])[0]).reshape(-1)

        return run, "executorch.runtime.Runtime"
    except Exception as exc:  # noqa: BLE001 - any failure here just means "try the older API"
        # Not only ImportError: the modern API has also changed its load_program
        # signature between releases. Fall through to the pybindings entry-point
        # rather than making this script version-locked.
        logger.debug(f"executorch.runtime unavailable ({exc}); trying pybindings")

    try:
        from executorch.extension.pybindings.portable_lib import (
            _load_for_executorch,
        )
    except ImportError as exc:
        raise SystemExit(
            f"ExecuTorch runtime unavailable ({exc}).\n"
            "This script must run in the ISOLATED export venv. On the server:\n"
            "    bash run/setup_export_env.sh\n"
            "then submit via run/check_pte_parity.sh (do NOT use the training venv)."
        )

    module = _load_for_executorch(str(pte_path))

    def run(tensor):
        return np.asarray(module.forward([tensor])[0]).reshape(-1)

    return run, "executorch.extension.pybindings"


def _read_reference(ref_csv: Path):
    """Read ref_<model>.csv -> (ids, logits). Stdlib csv: no pandas in this venv."""
    ids, logits = [], []
    with open(ref_csv, newline="") as f:
        for row in csv.DictReader(f):
            ids.append(row["id"])
            logits.append(float(row["logit"]))
    return ids, np.asarray(logits, dtype=np.float64)


def _read_manifest(manifest_csv: Path):
    """Read manifest.csv -> {id: input_bin}. Order comes from the reference CSV."""
    mapping = {}
    with open(manifest_csv, newline="") as f:
        for row in csv.DictReader(f):
            mapping[row["id"]] = row["input_bin"]
    return mapping


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True,
                        help="Used to locate the .pte and ref_<model>.csv by convention")
    parser.add_argument("--pte", default=None,
                        help="Default: exports/executorch/<model>.pte")
    parser.add_argument("--benchmark-dir", default="data/benchmark_set")
    parser.add_argument("--ref-csv", default=None,
                        help="Default: <benchmark-dir>/ref_<model>.csv")
    parser.add_argument("--tolerance", type=float, default=1e-3,
                        help="Max allowed |logit_pytorch - logit_pte| (default 1e-3)")
    parser.add_argument("--output", default=None,
                        help="JSON report (default: reports/mobile_benchmark/parity_<model>.json)")
    args = parser.parse_args()

    bench = Path(args.benchmark_dir)
    pte_path = Path(args.pte or f"exports/executorch/{args.model_name}.pte")
    ref_csv = Path(args.ref_csv or bench / f"ref_{args.model_name}.csv")
    manifest_csv = bench / "manifest.csv"
    meta_path = bench / "meta.json"

    for p, hint in [
        (pte_path, "bash run/export_executorch.sh MODEL=... CKPT=..."),
        (ref_csv, f"bash run/make_benchmark_set.sh N=100 MODEL={args.model_name} CKPT=..."),
        (manifest_csv, "bash run/make_benchmark_set.sh N=100"),
    ]:
        if not p.exists():
            raise SystemExit(f"Missing {p}\n  Produce it first:  {hint}")

    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    # inputs/*.bin are raw float32 dumps with no shape header — take the shape
    # from meta.json (written by make_benchmark_set.py) so a config change in
    # image_size can never silently reinterpret the bytes.
    shape = tuple(meta.get("input_shape", [3, 224, 224]))

    ids, ref_logits = _read_reference(ref_csv)
    bins = _read_manifest(manifest_csv)
    run_pte, api = _load_pte_runner(pte_path)
    logger.info(f"ExecuTorch API: {api} | .pte: {pte_path} ({pte_path.stat().st_size / 1024**2:.2f} MB)")
    logger.info(f"Benchmark set: {len(ids)} samples | input shape {shape} | tolerance {args.tolerance:g}")

    pte_logits = np.empty(len(ids), dtype=np.float64)
    for i, sample_id in enumerate(ids):
        bin_path = bench / "inputs" / bins[sample_id]
        arr = np.fromfile(bin_path, dtype=np.float32)
        expected = int(np.prod(shape))
        if arr.size != expected:
            raise SystemExit(
                f"{bin_path} has {arr.size} floats, expected {expected} for shape {shape}. "
                "The benchmark set and meta.json disagree — regenerate the set."
            )
        # The .pte was exported at a fixed batch of 1, so feed one at a time.
        tensor = torch.from_numpy(arr.reshape(1, *shape).copy())
        out = run_pte(tensor)
        if out.size != 1:
            raise SystemExit(
                f"Sample {sample_id}: .pte returned {out.size} values, expected 1 logit."
            )
        pte_logits[i] = float(out[0])

    delta = pte_logits - ref_logits
    abs_delta = np.abs(delta)
    ref_probs = _sigmoid(ref_logits)
    pte_probs = _sigmoid(pte_logits)
    abs_dprob = np.abs(pte_probs - ref_probs)

    max_abs = float(abs_delta.max())
    worst = int(abs_delta.argmax())
    n_over = int((abs_delta > args.tolerance).sum())
    passed = max_abs <= args.tolerance

    report = {
        "model_name": args.model_name,
        "pte_path": str(pte_path),
        "pte_size_mb": round(pte_path.stat().st_size / 1024 ** 2, 3),
        "executorch_api": api,
        "reference_csv": str(ref_csv),
        "n_samples": len(ids),
        "input_shape": list(shape),
        "tolerance": args.tolerance,
        "max_abs_logit_delta": max_abs,
        "mean_abs_logit_delta": float(abs_delta.mean()),
        "p99_abs_logit_delta": float(np.percentile(abs_delta, 99)),
        "max_abs_prob_delta": float(abs_dprob.max()),
        "n_over_tolerance": n_over,
        "worst_sample": {
            "id": ids[worst],
            "pytorch_logit": float(ref_logits[worst]),
            "pte_logit": float(pte_logits[worst]),
            "abs_delta": float(abs_delta[worst]),
        },
        "passed": bool(passed),
    }

    out_path = Path(args.output or f"reports/mobile_benchmark/parity_{args.model_name}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))

    logger.info(
        f"max|dlogit|={max_abs:.3e}  mean={abs_delta.mean():.3e}  "
        f"max|dprob|={abs_dprob.max():.3e}  over-tolerance={n_over}/{len(ids)}"
    )
    logger.info(f"Wrote {out_path}")

    if passed:
        logger.info(f"PARITY PASS — max|dlogit| {max_abs:.3e} <= {args.tolerance:g}")
        return 0
    logger.error(
        f"PARITY FAIL — max|dlogit| {max_abs:.3e} > {args.tolerance:g} "
        f"(worst sample {ids[worst]}: pytorch={ref_logits[worst]:.6f} "
        f"pte={pte_logits[worst]:.6f}). Do NOT report on-device numbers for this .pte."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
