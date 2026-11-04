#!/usr/bin/env python3
"""Rerun of instrument I1 (character-sum maximum of the factor base's log set) of WEAKCLASS-20261104 with a calibrated
A/A gate, on curves picked afresh from this protocol's seed, plus 30 extra ordinary prime-order curves per size for an
out-of-sample overdispersion test. Reuses weakclass.py (byte copy of the frozen N1 script) for curve picking, DL tables,
factor bases, the statistic and the null law. Per curve: 200 negation-closed null draws in two streams of 100 (A/A),
one planted negation-closed log-AP set (positive control)."""
import argparse, json, math, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))
from tools.experiment_protocol import derive_seed
import weak_curves as W, weakclass as N1
DRAWS = 200; EXTRA = 30

def extra_ordinary(L, sha, k):
    rng = np.random.default_rng(derive_seed(sha, "extra", str(L), 0)); ps = W.primes_in(2**(L-1), 2**L); out = []
    for p in (ps[i] for i in rng.permutation(len(ps))):
        if len(out) == k: break
        leg = W.leg_table(p)
        for _ in range(2000):
            a, b = int(rng.integers(1, p)), int(rng.integers(1, p))
            if (4*a**3 + 27*b*b) % p == 0: continue
            n = W.order(p, a, b, leg)
            if W.isprime(n) and n != p and W.emb_degree(p, n) is None:
                out.append(dict(cls="E", p=p, a=a, b=b, n=n)); break
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    a_ = ap.parse_args(); sha = a_.protocol_sha; inst = 0
    with open(a_.out, "w") as f:
        for L in N1.SIZES:
            for c in N1.pick(L, sha) + extra_ordinary(L, sha, EXTRA):
                iid = str(inst); inst += 1; p, a, b, n = c["p"], c["a"], c["b"], c["n"]
                dl = N1.dl_table(p, a, b, n); F = N1.fb_logs(dl, p, a, n, c["cls"], 2 * math.isqrt(n))
                Cn = [N1.C_of(N1.sym_draw(np.random.default_rng(derive_seed(sha, "N_sym", iid, d)), n, len(F) - len(F) % 2), n) for d in range(DRAWS)]
                r0 = np.random.default_rng(derive_seed(sha, "planted", iid, 0)); dd = int(r0.integers(2, n - 1)); h = len(F)//2
                apset = np.concatenate([(dd*np.arange(1, h+1)) % n, (-dd*np.arange(1, h+1)) % n])
                x = N1.C_of(F, n)
                f.write(json.dumps(dict(c, L=L, instance_id=iid, fb_size=int(len(F)), I1=x, null=Cn, I1_u=N1.pct(x, Cn),
                                        I1_pos_u=N1.pct(N1.C_of(apset, n), Cn))) + "\n"); f.flush()
            print(f"L={L} done", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
