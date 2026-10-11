# Count operators that run OUTSIDE the XNNPACK delegate in a .pte (non-delegated ops appear in the plan operator table).
import sys, collections
from executorch.exir._serialize._program import deserialize_pte_binary
for f in sys.argv[1:]:
    p = deserialize_pte_binary(open(f, "rb").read())
    p = getattr(p, "program", p)
    plan = p.execution_plan[0]
    ops = [o.name for o in plan.operators]
    kinds = collections.Counter()
    for c in plan.chains:
        for ins in c.instructions:
            a = ins.instr_args
            if type(a).__name__ == "KernelCall": kinds[ops[a.op_index]] += 1
            elif type(a).__name__ == "DelegateCall": kinds["<xnnpack delegate call>"] += 1
    print(f.split("/")[-1], dict(kinds.most_common()))
