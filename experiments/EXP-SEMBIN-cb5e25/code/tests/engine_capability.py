"""Engine capability probe on SYNTHETIC random systems (not the measurement grid):
construction + Macaulay build + W_4 closure timing/RSS at several N, to extrapolate
to N = 40 (C4 = 102091) against the 10 GB RSS cap. Output: engine_capability.json.
Run: python3 engine_capability.py N [N ...]
"""
import json, os, resource, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
import closure as CL
from crypto_autoresearcher.gf2 import kernels
from rng import HashRng


def synth(nv, neq, rng):
    """neq equations: ~nv/2 degree-1/2 terms and a few cubic terms, random."""
    eqs = []
    for k in range(neq):
        e = set()
        for d, cnt in ((1, 3), (2, nv // 2), (3, nv // 4 if k % 2 == 0 else 0)):
            for _ in range(cnt):
                pool = list(range(nv))
                m = 0
                for i in range(d):
                    j = i + rng.randbelow(nv - i)
                    pool[i], pool[j] = pool[j], pool[i]
                    m |= 1 << pool[i]
                e ^= {m}
        eqs.append(sorted(e))
    return eqs


def synth_planted(nv, neq, rng):
    """NULL-PROF-style planted system with profile {1:3, 2:nv//2, 3:nv//4} per equation
    (random multilinear, constants set to plant a uniform s): dim W_4 close to C4."""
    import nulls
    prof = [({1: 3, 2: nv // 2} if k < neq // 2 else {1: 3, 2: nv // 2, 3: nv // 4}) for k in range(neq)]
    eqs, s = nulls.null_prof(nv, prof, rng)
    return eqs


def synth_pc(nv, neq, rng):
    """Hidden triangular planted system (positive control shape): W_4 reaches
    C4 - 1, the contained-case elimination size (worst case for time/memory)."""
    import positive_control
    prof = [({1: 3, 2: nv // 2} if k < neq // 2 else {1: 3, 2: nv // 2, 3: nv // 4}) for k in range(neq)]
    return positive_control.pc_tri(nv, neq, prof, rng)["eqs"]


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def main():
    out = []
    for nv in map(int, sys.argv[1:]):
        rng = HashRng(1, f"cap{nv}")
        eqs = synth_pc(nv, nv, rng) if os.environ.get('CAP_PC') else synth(nv, nv - 2, rng)
        r0 = {}
        r = {"nv": nv, "D": 4, "C": CL.C_le(nv, 4)}
        t = time.time()
        cl = CL.SembinClosure(nv, 4, eqs)
        r["construct_s"] = round(time.time() - t, 2)
        t = time.time(); M = cl.build_M(eqs); r["build_M_s"] = round(time.time() - t, 2)
        r["M_rows"], r["M_bytes"] = int(M.shape[0]), int(M.nbytes)
        r["rss_after_build_mb"] = round(rss_mb())
        t = time.time(); c0 = time.process_time()
        log = kernels.column_pass(M, cl.C, keep_ops=False)
        r["M4_elim_s"] = round(time.time() - t, 2); r["M4_rank"] = int(log.K)
        r["M4_cpu_s"] = round(time.process_time() - c0, 2)
        r["rss_after_elim_mb"] = round(rss_mb())
        del M
        if nv <= int(os.environ.get("CAP_W_MAX", "30")):
            t = time.time()
            rec, _ = CL.w_closure_record(nv, 4, eqs)
            r["W4_wall_s"] = round(time.time() - t, 2)
            r["W4_final_dim"], r["W4_iterations"] = rec["final_dim"], rec["iterations_to_fixpoint"]
            r["W4_stack_rows"] = rec["stack_rows_per_iteration"]
            r["rss_after_W4_mb"] = round(rss_mb())
        print(json.dumps(r), flush=True)
        out.append(r)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine_capability.json")
    old = json.load(open(path)) if os.path.exists(path) else []
    json.dump(old + out, open(path, "w"), indent=1)


main()
