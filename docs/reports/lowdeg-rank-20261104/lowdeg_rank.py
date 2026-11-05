#!/usr/bin/env python3
"""LEAD-EXO-low-degree-query-lower-bound, step (b): exact rank over F_p of the evaluation matrix
V[k, m] = m(x_1, y_1, ..., x_t, y_t) at the coordinates of X_i = [b_i]R + [a_i]P, R = [k]P, over all
candidate logs k (rows with some X_i = O dropped), for monomials m of total degree <= D in 2t variables.
Full rank (r = #candidates) means every subset of candidates is cut out by one degree-<=D test, which is the
interpolation attack's condition. Arms (3 replicates each):
  rand  : b_i uniform in [2, N-2] (protocol seeds), a_i = 0              (candidate)
  ap    : b_i = 1 + rep*t + i (small arithmetic progression), a_i = 0   (reference: small multipliers)
  shift : b_i = 1, a_i = 1 + rep + i  (X_i = R + [a_i]P)                (positive control: rank <= 3Dt+1 by Riemann-Roch)
  null  : uniformly random points of F_p^{2t} in place of V (protocol seeds) (negative control: generic full rank)
Seeds: tools/experiment_protocol.py derive_seed(protocol_sha, arm, instance, replicate), the checker's own rule.
Usage: lowdeg_rank.py --protocol-sha <hex> --out rows.jsonl
"""
import argparse, itertools, json, math, os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from tools.experiment_protocol import derive_seed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modrank import rank_mod_p

def isprime(n): return n > 1 and all(n % d for d in range(2, int(n**.5) + 1))
def legendre_table(p):
    t = np.full(p, -1, dtype=np.int64); t[0] = 0; t[(np.arange(1, p)**2) % p] = 1; return t
def add(P, Q, p, a):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    l = ((3*P[0]*P[0] + a) * pow(2*P[1], -1, p) if P == Q else (Q[1]-P[1]) * pow(Q[0]-P[0], -1, p)) % p
    x = (l*l - P[0] - Q[0]) % p; return (x, (l*(P[0]-x) - P[1]) % p)
def find_point(p, a, b):
    for x in range(p):
        v = (x**3 + a*x + b) % p
        for y in range(p):
            if y*y % p == v and y: return (x, y)

SIZES = [8, 9, 10]
TARGETS = [0.5, 1.0, 2.0]
DEGREES = [2, 3]
ARMS = ["rand", "ap", "shift", "null"]
REPS = 3

def curves_for(L, count, sha):
    p = max(q for q in range(2**(L-1), 2**L) if isprime(q))
    leg = legendre_table(p); X = np.arange(p); out = []
    rng = np.random.default_rng(derive_seed(sha, "curve", str(L), 0))
    while len(out) < count:
        a, b = int(rng.integers(0, p)), int(rng.integers(1, p))
        if (4*a**3 + 27*b*b) % p == 0: continue
        n = p + 1 + int(leg[(X**3 + a*X + b) % p].sum())
        if isprime(n) and n != p and n not in [c[3] for c in out]: out.append((p, a, b, n))
    return out

def nmon(t, D): return math.comb(2*t + D, D)
def expected_generic(C, t, D):
    rel = t * math.comb(2*t + D - 3, D - 3) if D >= 3 else 0    # t cubic curve equations times monomials, valid for D < 6
    return min(C, nmon(t, D) - rel)

def instances(sha):
    inst = []
    for L in SIZES:
        for (p, a, b, n) in curves_for(L, 2, sha):
            for D in DEGREES:
                ts = sorted({min(range(1, 40), key=lambda t: abs(math.log(nmon(t, D) / (n - 1) / g))) for g in TARGETS})
                for t in ts: inst.append(dict(L=L, p=p, a=a, b=b, n=n, D=D, t=t))
    (p, a, b, n), = curves_for(11, 1, sha)
    t = min(range(1, 40), key=lambda t: abs(math.log(nmon(t, 3) / (n - 1) / 2.0)))
    inst.append(dict(L=11, p=p, a=a, b=b, n=n, D=3, t=t))
    return inst

def monomials(nv, D):
    return [e for e in itertools.product(range(D + 1), repeat=nv) if sum(e) <= D] if nv <= 6 else \
           [e for d in range(D + 1) for e in _compositions(nv, d)]
def _compositions(nv, d):
    for c in itertools.combinations_with_replacement(range(nv), d):
        e = [0]*nv
        for i in c: e[i] += 1
        yield tuple(e)

def eval_matrix(coords, mons, p):
    """coords: (C, nv) int array; returns (C, len(mons)) monomial values mod p."""
    C, nv = coords.shape; D = max(sum(m) for m in mons)
    pw = np.ones((D + 1, C, nv), dtype=np.int64)
    for d in range(1, D + 1): pw[d] = (pw[d-1] * coords) % p
    out = np.ones((C, len(mons)), dtype=np.int64)
    for j, e in enumerate(mons):
        col = np.ones(C, dtype=np.int64)
        for v, k in enumerate(e):
            if k: col = (col * pw[k, :, v]) % p
        out[:, j] = col
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args(); sha = args.protocol_sha
    with open(args.out, "w") as f:
        for i, I in enumerate(instances(sha)):
            p, a, b, n, D, t = I["p"], I["a"], I["b"], I["n"], I["D"], I["t"]
            G = find_point(p, a, b); mult = [None]; R = None
            for k in range(1, n): R = add(R, G, p, a); mult.append(R)
            mons = monomials(2*t, D)
            for arm in ARMS:
                for rep in range(REPS):
                    seed = derive_seed(sha, arm, str(i), rep); rng = np.random.default_rng(seed)
                    if arm == "rand": bs, As = [int(x) for x in rng.integers(2, n - 1, t)], [0]*t
                    elif arm == "ap": bs, As = [1 + rep*t + j for j in range(t)], [0]*t
                    elif arm == "shift": bs, As = [1]*t, [1 + rep + j for j in range(t)]
                    else: bs, As = None, None
                    if arm == "null":
                        C = n - 1; coords = rng.integers(0, p, (C, 2*t))
                    else:
                        rows = []
                        for k in range(1, n):
                            pts = [mult[(bi*k + ai) % n] for bi, ai in zip(bs, As)]
                            if any(P is None for P in pts): continue
                            rows.append([c for P in pts for c in P])
                        coords = np.array(rows, dtype=np.int64); C = len(rows)
                    r = rank_mod_p(eval_matrix(coords, mons, p), p)
                    f.write(json.dumps(dict(run_id=f"{i}-{arm}-{rep}", instance_id=str(i), arm=arm, replicate=rep, seed=seed,
                        L=I["L"], p=p, a=a, b=b, n=n, D=D, t=t, monomials=len(mons), candidates=C, rank=r,
                        expected_generic=(min(C, len(mons)) if arm == "null" else expected_generic(C, t, D)),
                        full=int(r == C), multipliers=bs, a_offsets=As)) + "\n"); f.flush()
            print(f"instance {i} L={I['L']} p={p} D={D} t={t} done", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
