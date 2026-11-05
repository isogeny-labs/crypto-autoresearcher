"""Scaling of the smallest found support vs |S| (same E instance as h1pp_check.py, p = 263, t = 9, D = 3)."""
import json, random, sys
import numpy as np
sys.path.insert(0, ".")
import h1pp_check as H
p = 263; rng = random.Random(H.SEED)
a = next(a for a in range(1, p) if H.isprime(len(H.curve_points(p, a, 1))))
E = H.curve_points(p, a, 1); N = len(E); G = E[1]; mult = [None]; R = None
for k in range(1, N): R = H.add(R, G, p, a); mult.append(R)
xs = np.array([0] + [mult[k][0] for k in range(1, N)], dtype=np.int64)
C = (N - 1)//2; ks = np.arange(1, C + 1); mons = H.monomials(9, 3); M = len(mons)
bs = [rng.randrange(2, N - 1) for _ in range(9)]
A = H.eval_matrix(np.stack([xs[(b*ks) % N] for b in bs], axis=1), mons, p)
out = []
for s in (10, 20, 35, 50, 70, 90, 110, 130):
    S = sorted(rng.sample(range(C), s)); comp = [i for i in range(C) if i not in set(S)]
    w, ex, rk = H.prange_min_support(A[S], A[comp], p, 150, rng)
    r = dict(s=s, best_support_found=w, exact=ex, gv=H.gv_weight(M, s, p), counting_lb=H.counting_lb(C, s, M, p)); out.append(r); print(json.dumps(r), flush=True)
json.dump(out, open("h1pp_scaling.json", "w"), indent=1)
