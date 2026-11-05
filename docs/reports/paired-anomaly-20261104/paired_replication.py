#!/usr/bin/env python3
"""Replication of the paired-curve anomaly (WEAKCLASS-I1-20261104: the 27 paired ordinary curves had mean I1 percentile 0.28 vs
0.53 for independently picked ones). For each size L in {10, 12, 14} and k = 0..3, run the frozen weak-class pick() under seed
'<sha>:k' and score every curve it returns (weak classes A, B, C and paired ordinary D); also score 36 independently picked
ordinary curves (extra_ordinary procedure, class E) per size. Statistic: I1 = character-sum maximum of the small-x log set
(zeta-orbit FB for class C), percentile u among 200 negation-closed null draws. Reuses weakclass.py, weak_curves.py and
weakclass_i1.py (byte copies). Records curve features for mechanism hunting."""
import argparse, json, math, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))
from tools.experiment_protocol import derive_seed
import weak_curves as W, weakclass as N1, weakclass_i1 as I1
K = 4; EXTRA = 36; DRAWS = 200
def features(p, a, b, n):
    sq = lambda v: v % p != 0 and pow(v % p, (p - 1)//2, p) == 1
    return dict(trace=p + 1 - n, p_mod3=p % 3, p_mod4=p % 4, a_is_sq=sq(a), b_is_sq=sq(b), j0=(a % p == 0))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    a_ = ap.parse_args(); sha = a_.protocol_sha; inst = 0
    with open(a_.out, "w") as f:
        for L in N1.SIZES:
            curves = []
            for k in range(K):
                for c in N1.pick(L, f"{sha}:{k}"): curves.append(dict(c, pick_seed=k, source="pick"))
            for c in I1.extra_ordinary(L, sha, EXTRA): curves.append(dict(c, source="extra"))
            for c in curves:
                iid = str(inst); inst += 1; p, a, b, n = c["p"], c["a"], c["b"], c["n"]
                dl = N1.dl_table(p, a, b, n); F = N1.fb_logs(dl, p, a, n, c["cls"], 2 * math.isqrt(n))
                Cn = [N1.C_of(N1.sym_draw(np.random.default_rng(derive_seed(sha, "N_sym", iid, d)), n, len(F) - len(F) % 2), n) for d in range(DRAWS)]
                r0 = np.random.default_rng(derive_seed(sha, "planted", iid, 0)); dd = int(r0.integers(2, n - 1)); h = len(F)//2
                apset = np.concatenate([(dd*np.arange(1, h+1)) % n, (-dd*np.arange(1, h+1)) % n]); x = N1.C_of(F, n)
                f.write(json.dumps(dict(c, L=L, instance_id=iid, fb_size=int(len(F)), I1=x, I1_u=N1.pct(x, Cn), I1_pos_u=N1.pct(N1.C_of(apset, n), Cn),
                                        aa_ks_streams=[float(np.mean(Cn[:100])), float(np.mean(Cn[100:]))], **features(p, a, b, n))) + "\n"); f.flush()
            print(f"L={L} done ({len(curves)} curves)", file=sys.stderr, flush=True)
if __name__ == "__main__":
    main()
