#!/usr/bin/env python3
"""Follow-up to holant step (b'): is the x-labelled transfer matrix M of ANOMALOUS curves (#E = p)
less QTT-complex, relative to its own random-relabelling null, than M of ordinary prime-order curves
over the same primes?  Core routines are qtt_core.py (byte copy of the frozen step-(b') qtt_rank.py).
Per curve: X (natural labelling), LOG (discrete-log orbit labelling), 99 random relabellings (null).
Rows record interleaved r_max and log2_params; the analysis uses percentiles within each curve's null.
Usage: anomalous_qtt.py --protocol-sha <hex> --out rows.jsonl
"""
import argparse, json, sys, numpy as np
from qtt_core import (isprime, curve_points, add, transfer_matrix, qtt_ranks, summary, derive_seed)

PRIMES = [q for q in range(37, 128) if isprime(q)]
EXCLUDED = {(61, 21, 57)}           # the motivating curve from step (b'): reported separately, not in the test
PER_GROUP = 4                       # isomorphism classes per group per prime (fewer if fewer exist)
NULL = 99

def counts(p):
    """#E(F_p) for every (a, b) with 4a^3+27b^2 != 0, via Legendre sums (vectorised)."""
    x = np.arange(p)
    leg = np.zeros(p, dtype=np.int64)
    sq = set((y * y) % p for y in range(1, p))
    for v in range(1, p): leg[v] = 1 if v in sq else -1
    out = {}
    for a in range(p):
        base = (x**3 + a * x) % p
        for b in range(p):
            if (4 * a**3 + 27 * b * b) % p == 0: continue
            out[(a, b)] = p + 1 + int(leg[(base + b) % p].sum())
    return out

def iso_class(p, a, b):
    """Canonical representative of {(a u^4, b u^6) : u in F_p^*}."""
    return min(((a * pow(u, 4, p)) % p, (b * pow(u, 6, p)) % p) for u in range(1, p))

def pick(p, protocol_sha):
    cnt = counts(p)
    anom, ordi = {}, {}
    for (a, b), n in cnt.items():
        if (p, a, b) in EXCLUDED: continue
        c = iso_class(p, a, b)
        if any((p,) + c == (p,) + iso_class(p, ea, eb) for (ep, ea, eb) in EXCLUDED if ep == p): continue
        if n == p: anom.setdefault(c, n)
        elif isprime(n): ordi.setdefault(c, n)
    rng = np.random.default_rng(derive_seed(protocol_sha, "pick", p))
    A = sorted(anom); O = sorted(ordi)
    A = [A[i] for i in rng.permutation(len(A))[:PER_GROUP]]
    O = [O[i] for i in rng.permutation(len(O))[:len(A)]]    # matched count per prime
    return [("anomalous", c, anom[c]) for c in A] + [("ordinary", c, ordi[c]) for c in O]

def run_curve(f, p, a, b, group, protocol_sha):
    E = curve_points(p, a, b); n = len(E)
    L = int(np.ceil(np.log2(p)))
    Ex = sorted({P[0] for P in E[1:]}); FB = Ex[:int(np.floor(np.sqrt(p)))]
    M = transfer_matrix(p, a, b, FB)
    base = dict(p=p, a=a, b=b, n=n, L=L, group=group, fb_size=len(FB))
    def emit(arm, Mx, draw=None):
        r = qtt_ranks(Mx, L, "interleaved")
        f.write(json.dumps(dict(base, arm=arm, draw=draw, **summary(r), ranks=r)) + "\n")
    emit("X", M)
    G = E[1]; R = None; logof = {}
    for k in range(n): logof[R] = k; R = add(R, G, p, a)
    orbit = {P[0]: min(logof[P], n - logof[P]) - 1 for P in E[1:]}
    rest = [x for x in range(p) if x not in orbit]
    perm = np.empty(p, dtype=np.int64)
    for x, j in orbit.items(): perm[x] = j
    for i, x in enumerate(rest): perm[x] = len(orbit) + i
    Ml = np.zeros_like(M); Ml[np.ix_(perm, perm)] = M
    emit("LOG", Ml)
    for d in range(NULL):
        q = np.random.default_rng(derive_seed(protocol_sha, "anull", p, a, b, d)).permutation(p)
        Mn = np.zeros_like(M); Mn[np.ix_(q, q)] = M
        emit("N", Mn, d)
    f.flush()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--include-excluded", action="store_true", help="also run the motivating curve (reported separately)")
    args = ap.parse_args()
    with open(args.out, "w") as f:
        for p in PRIMES:
            for group, (a, b), n in pick(p, args.protocol_sha):
                run_curve(f, p, a, b, group, args.protocol_sha)
            print(f"p={p} done", file=sys.stderr, flush=True)
        if args.include_excluded:
            for (p, a, b) in sorted(EXCLUDED): run_curve(f, p, a, b, "motivating", args.protocol_sha)

if __name__ == "__main__":
    main()
