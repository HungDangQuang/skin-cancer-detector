# x86 PROXY timing of two .pte files through the ExecuTorch runtime (XNNPACK), same session, interleaved blocks.
import time, statistics, sys, torch
from executorch.runtime import Runtime
rt = Runtime.get()
files = {"cpubone_b1": "exports/executorch_cpubone/cpubone_b1.pte",
         "mobilenetv4_conv_medium": "exports/executorch_srcsamp/mobilenetv4_conv_medium__srcsamp_auprc_fold4.pte"}
meth = {k: rt.load_program(v).load_method("forward") for k, v in files.items()}
x = torch.randn(1, 3, 224, 224)
for k, m in meth.items():
    for _ in range(30): m.execute([x])
res = {k: [] for k in meth}
for block in range(10):
    order = list(meth) if block % 2 == 0 else list(meth)[::-1]
    for k in order:
        for _ in range(20):
            t = time.perf_counter(); meth[k].execute([x]); res[k].append((time.perf_counter() - t) * 1000)
for k, v in res.items():
    v.sort(); print(f"{k:26s} n={len(v)} median={statistics.median(v):.2f} ms  p90={v[int(0.9*len(v))]:.2f}  min={v[0]:.2f}")
