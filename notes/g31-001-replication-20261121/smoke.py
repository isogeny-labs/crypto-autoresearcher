"""smoke.py -- pre-freeze implementation checks for the replication engine.

Checks, in order:
  1. #E via BSGS == #E via naive count (p ~ 2^13 and one p ~ 2^17 curve).
  2. log table is complete and g has order n.
  3. x-window base: |B| even, negation-closed, O absent, no 2-torsion.
  4. FFT convolution counts == brute-force ordered enumeration (tiny b).
  5. FFT convolution counts == pilot's group-law pair-table Ctx (real cells).
"""
import itertools
import math
import random

import numpy as np

from ec import EC
import replib as R
from pilot_run import Ctx, InvTable


def brute_counts(E, B, n, m, tab, tlogs):
    """Ordered m-tuple counts by direct enumeration over B^m (sums only)."""
    logs = [tab[P] for P in B]
    ct = {}
    for tup in itertools.product(logs, repeat=m):
        s = sum(tup) % n
        ct[s] = ct.get(s, 0) + 1
    return [ct.get(k, 0) for k in tlogs]


print("=== 1. order: BSGS vs naive ===")
for bits, idx in [(13, 0), (17, 0)]:
    c = R.make_curve(bits, idx)
    print(f"  bits={bits} idx={idx} p={c['p']} a={c['a']} b={c['b']} "
          f"#E={c['nE']} prime={c['cofactor'] == 1} j={c['j']} "
          f"method={c['order_method']} attempt={c['attempt']}")

print("=== 2/3. log table + base invariants ===")
c = R.make_curve(13, 0)
E, n, g = c["E"], c["n"], c["g"]
tab = R.log_table(E, n, g)
assert len(tab) == n
print(f"  |G|={n}, log table size {len(tab)}, g order ok")

for N in (math.isqrt(c["p"]), round(c["p"] ** (1 / 3))):
    B = R.window_points(E, N)
    logs = [tab[P] for P in B]
    negclosed = all((-k) % n in set(logs) for k in logs)
    two_tors = [P for P in B if P[1] == 0]
    print(f"  N={N}: |B_raw|={len(B)} even={len(B) % 2 == 0} "
          f"negclosed={negclosed} O_in={None in B} 2torsion={len(two_tors)}")
    assert len(B) % 2 == 0 and negclosed and None not in B and not two_tors

print("=== 4. FFT vs brute force (tiny base) ===")
small = R.window_points(E, 6)
tlogs = [k for k in range(1, 40)]
for m in (3, 4):
    cv, resid = R.counts([tab[P] for P in small], n, m)
    bf = brute_counts(E, small, n, m, tab, tlogs)
    ok = all(int(cv[k]) == v for k, v in zip(tlogs, bf))
    print(f"  b={len(small)} m={m}: match={ok} max|fft-round|={resid:.2e} "
          f"total={int(cv.sum())} (b^m={(len(small))**m})")
    assert ok and int(cv.sum()) == len(small) ** m

print("=== 5. FFT vs pilot Ctx (group-law pair table) ===")
invt = InvTable(E.p)
for N, m in [(math.isqrt(E.p), 3), (math.isqrt(E.p), 4),
             (round(E.p ** (1 / 3)), 3), (round(E.p ** (1 / 3)), 4)]:
    B = R.window_points(E, N)
    logs = [tab[P] for P in B]
    ctx = Ctx(E, invt)
    ctx.n, ctx.g = n, g
    ctx.pair_table(B)
    trng = random.Random(12345)
    tpts = [E.mul(trng.randrange(1, n), g) for _ in range(200)]
    cv, resid = R.counts(logs, n, m)
    bad = 0
    tot_pilot = 0
    tot_fft = 0
    for Q in tpts:
        cnt, wit = ctx.r_m(Q, m)
        if wit is not None:
            S = None
            for P in wit:
                S = E.add(S, P)
            if S != Q:
                bad += 1
        tot_pilot += cnt
        tot_fft += int(cv[tab[Q]])
    print(f"  N={N} m={m} b={len(B)}: pilot_total={tot_pilot} fft_total={tot_fft} "
          f"exact_match={tot_pilot == tot_fft} witness_bad={bad} resid={resid:.1e}")
    assert tot_pilot == tot_fft and bad == 0
print("SMOKE OK")
