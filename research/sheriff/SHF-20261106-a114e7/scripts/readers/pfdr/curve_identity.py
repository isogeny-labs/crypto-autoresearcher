#!/usr/bin/env python3
"""Instance identity of the census curves, own arithmetic: p prime, N prime, Hasse bound, N != p,
a b != 0 (j != 0, 1728), nonsingular; exact point count by quadratic-character table (numpy) for every
20-bit curve and the first K 24-bit curves. usage: curve_identity.py <jobs.jsonl> <out.json> [K24]"""
import json, math, sys
import numpy as np
def is_prime(n):
    if n < 2: return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0: return n == q
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True
def count(p, a, b):
    x = np.arange(p, dtype=np.int64)
    sq = np.zeros(p, dtype=bool); sq[(x * x) % p] = True
    f = ((x * x % p) * x % p + a * x % p + b) % p
    return 1 + int((f == 0).sum()) + 2 * int((sq[f] & (f != 0)).sum())
curves = {}
for l in open(sys.argv[1]):
    r = json.loads(l); curves[(r["bits"], r["c"])] = (r["p"], r["a"], r["b_coef"], r["N"])
K24 = int(sys.argv[3]) if len(sys.argv) > 3 else 5
bad = []; counted = {20: 0, 24: 0}; seen24 = 0
for (bits, c), (p, a, b, N) in sorted(curves.items()):
    ok = is_prime(p) and is_prime(N) and abs(p + 1 - N) <= 2 * math.isqrt(p) + 2 and N != p and a % p and b % p \
        and (4 * a ** 3 + 27 * b * b) % p and p.bit_length() == bits
    if not ok: bad.append((bits, c))
    if bits == 20 or (bits == 24 and seen24 < K24):
        if count(p, a, b) != N: bad.append((bits, c, "count"))
        counted[bits] += 1
        if bits == 24: seen24 += 1
res = {"curves": len(curves), "by_bits": {b: sum(1 for k in curves if k[0] == b) for b in (20, 24, 28)},
       "failures": bad, "exact_counts": counted}
json.dump(res, open(sys.argv[2], "w"), indent=1); print(res)
