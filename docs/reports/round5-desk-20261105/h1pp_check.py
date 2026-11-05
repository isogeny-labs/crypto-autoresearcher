"""H1'' toy derivation checks (not a measurement; exact arithmetic, fixed seeds).

Model: candidates are classes {k,-k}, k = 1..(N-1)/2, of a prime-order curve E/F_p
(x-coordinates only, so x([b]R) depends on the class). Coordinates of t encodings
X_i = [b_i]R, monomials of total degree <= D in x_1..x_t (no Weierstrass relations).

(a) "Short tests are weak": for L = 2 (exhaustive) and L = 3 (sampled, all middle
    coefficients), the largest minority set mu(f) = min(|Z|, C-|Z|) of an L-term f.
    Arms: E random b_i; null = uniform random matrix of the same shape; positive control
    = F_p^* coordinates z^{b_i} with one pair b_2 = b_1 + (p-1)/2 (Legendre split, mu ~ C/2);
    prime-order multiplicative analogue (subgroup of order q, p = 2q+1).
(b) "Prescribed balanced S needs many monomials": for random S with |S| = C/2, the
    smallest support of an f vanishing on S found by Prange-style information-set search,
    against s+1 (trivial upper bound), the GV estimate and the counting lower bound.
Usage: python3 h1pp_check.py [out.json]
"""
import itertools, json, math, random, sys
import numpy as np

SEED = 20261105

def isprime(n): return n > 1 and all(n % d for d in range(2, int(n**.5) + 1))

def curve_points(p, a, b):
    sq = {}
    for y in range(p): sq.setdefault(y * y % p, []).append(y)
    return [None] + [(x, y) for x in range(p) for y in sq.get((x**3 + a*x + b) % p, [])]

def add(P, Q, p, a):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    l = ((3*P[0]*P[0] + a) * pow(2*P[1], -1, p) if P == Q else (Q[1]-P[1]) * pow(Q[0]-P[0], -1, p)) % p
    x = (l*l - P[0] - Q[0]) % p
    return (x, (l*(P[0]-x) - P[1]) % p)

def monomials(t, D):
    return [e for e in itertools.product(range(D+1), repeat=t) if sum(e) <= D]

def eval_matrix(coords, mons, p):
    # coords: C x t array of field elements
    C = coords.shape[0]
    A = np.ones((C, len(mons)), dtype=np.int64)
    pw = [np.stack([np.array([pow(int(v), e, p) for v in coords[:, i]]) for e in range(max(map(max, mons)) + 1)])
          for i in range(coords.shape[1])]
    for j, e in enumerate(mons):
        col = np.ones(C, dtype=np.int64)
        for i, ei in enumerate(e):
            if ei: col = col * pw[i][ei] % p
        A[:, j] = col
    return A

def rank_mod(A, p):
    M = A.copy() % p; r = 0; rows, cols = M.shape
    for c in range(cols):
        nz = np.nonzero(M[r:, c])[0]
        if nz.size == 0: continue
        piv = r + nz[0]; M[[r, piv]] = M[[piv, r]]
        M[r] = M[r] * pow(int(M[r, c]), -1, p) % p
        f = M[:, c].copy(); f[r] = 0
        M = (M - np.outer(f, M[r])) % p
        r += 1
        if r == rows: break
    return r

def inv_vec(v, p):
    out = np.zeros_like(v)
    nz = v != 0
    out[nz] = np.array([pow(int(x), -1, p) for x in v[nz]])
    return out

def max_minority_L2(A, p):
    """Exact max over all 2-term f = m1 + c m2 (c != 0) of min(|Z|, C-|Z|), f not identically 0."""
    C, M = A.shape; best = (0, None)
    invs = [inv_vec(A[:, j], p) for j in range(M)]
    for j1 in range(M):
        for j2 in range(j1+1, M):
            a1, a2 = A[:, j1], A[:, j2]
            both0 = int(np.sum((a1 == 0) & (a2 == 0)))
            ok = a2 != 0
            ratio = (a1[ok] * invs[j2][ok]) % p          # f = 0  <=>  ratio == -c
            ratio = ratio[(a1[ok] != 0)]                  # c != 0 needs a1 != 0
            if ratio.size == 0: continue
            cnt = np.bincount(ratio, minlength=p)
            z = int(cnt.max()) + both0
            if z == C: continue                          # identically zero on V
            mu = min(z, C - z)
            if mu > best[0]: best = (mu, [j1, j2])
    return best

def max_minority_L3(A, p, trials, rng):
    """Sampled triples; for each, exact max over (c2, c3) in F_p x F_p^* of mu(m1 + c2 m2 + c3 m3)."""
    C, M = A.shape; best = (0, None)
    cs = np.arange(p, dtype=np.int64)[:, None]
    for _ in range(trials):
        j1, j2, j3 = rng.sample(range(M), 3)
        a1, a2, a3 = A[:, j1], A[:, j2], A[:, j3]
        num = (a1[None, :] + cs * a2[None, :]) % p       # p x C
        ok = a3 != 0
        i3 = inv_vec(a3, p)
        vals = (num[:, ok] * i3[ok]) % p                 # f = 0 <=> vals == -c3 (and num=0 & a3=0 rows)
        extra = (num[:, ~ok] == 0).sum(axis=1)
        for ci in range(p):
            v = vals[ci]; v = v[v != 0]
            if v.size == 0: continue
            z = int(np.bincount(v, minlength=p).max()) + int(extra[ci])
            if z == C: continue
            mu = min(z, C - z)
            if mu > best[0]: best = (mu, [j1, j2, j3, ci])
    return best

def prange_min_support(AS, Acomp, p, trials, rng):
    """Smallest-weight kernel vector of AS (f vanishing on S) found from random information sets.
    Returns (best weight, whether best vanishes exactly on S, rank of AS)."""
    s, M = AS.shape; best = (M + 1, None); rk = None
    for _ in range(trials):
        perm = np.array(rng.sample(range(M), M))
        B = AS[:, perm] % p; r = 0; pivcols = []
        for c in range(M):
            nz = np.nonzero(B[r:, c])[0] if r < s else np.array([])
            if nz.size == 0: continue
            piv = r + nz[0]; B[[r, piv]] = B[[piv, r]]
            B[r] = B[r] * pow(int(B[r, c]), -1, p) % p
            f = B[:, c].copy(); f[r] = 0
            B = (B - np.outer(f, B[r])) % p
            pivcols.append(c); r += 1
            if r == s: break
        rk = r
        free = [c for c in range(M) if c not in set(pivcols)]
        for fc in free[:40]:
            vec = np.zeros(M, dtype=np.int64); vec[fc] = 1
            for row, pc in enumerate(pivcols): vec[pc] = (-B[row, fc]) % p
            w = int(np.count_nonzero(vec))
            if w < best[0]:
                f = np.zeros(M, dtype=np.int64); f[perm] = vec
                exact = bool(np.all(Acomp.dot(f) % p != 0))
                best = (w, exact)
    return best[0], best[1], rk

def gv_weight(M, s, p):
    # smallest w with C(M,w) (p-1)^(w-1) >= p^s (expected number of weight-w kernel vectors >= 1)
    for w in range(1, M + 1):
        if math.lgamma(M+1) - math.lgamma(w+1) - math.lgamma(M-w+1) + (w-1)*math.log(p-1) >= s*math.log(p):
            return w
    return M

def counting_lb(C, s, M, p):
    # #sets cut out by L-term f <= C(M,L) p^(L-1); need >= C(C,s) for a generic S: smallest such L
    need = math.lgamma(C+1) - math.lgamma(s+1) - math.lgamma(C-s+1)
    for L in range(1, M + 1):
        if math.lgamma(M+1) - math.lgamma(L+1) - math.lgamma(M-L+1) + (L-1)*math.log(p) >= need:
            return L
    return M

def main():
    rng = random.Random(SEED); nrng = np.random.default_rng(SEED)
    out = {"seed": SEED, "cells": []}
    p = 263
    a = next(a for a in range(1, p) if isprime(len(curve_points(p, a, 1))))
    E = curve_points(p, a, 1); N = len(E); G = E[1]
    mult = [None]; R = None
    for k in range(1, N): R = add(R, G, p, a); mult.append(R)
    xs = np.array([0] + [mult[k][0] for k in range(1, N)], dtype=np.int64)
    C = (N - 1) // 2; ks = np.arange(1, C + 1)
    out["curve"] = {"p": p, "a": a, "b": 1, "N": N, "classes": C}
    t, D = 9, 3
    mons = monomials(t, D); M = len(mons)
    bs = [rng.randrange(2, N - 1) for _ in range(t)]
    coordsE = np.stack([xs[(b * ks) % N] for b in bs], axis=1)
    AE = eval_matrix(coordsE, mons, p)
    Anull = nrng.integers(0, p, size=(C, M), dtype=np.int64)
    # multiplicative: z = g^k in F_p^*, candidates k = 1..p-2 (k and -k not merged); same t, D
    g = next(g for g in range(2, p) if all(pow(g, (p-1)//q, p) != 1 for q in range(2, p) if (p-1) % q == 0 and isprime(q)))
    km = np.arange(1, p - 1)
    bm = [rng.randrange(2, p - 1) for _ in range(t)]; bm[1] = (bm[0] + (p - 1)//2) % (p - 1)
    Amult = eval_matrix(np.stack([np.array([pow(g, int(b*k % (p-1)), p) for k in km]) for b in bm], axis=1), mons, p)
    # prime-order multiplicative subgroup: p = 2q+1 with q prime; h = g^2 generates order q
    q = (p - 1) // 2
    pq = p if isprime(q) else None
    arms = [("E_random_b", AE), ("null_uniform", Anull), ("posctrl_Fpstar_halfshift", Amult)]
    if pq:
        h = g * g % p; kq = np.arange(1, (q - 1)//2 + 1)  # merge k,-k is NOT valid here; use all 1..q-1
        kq = np.arange(1, q)
        bq = [rng.randrange(2, q) for _ in range(t)]
        Aq = eval_matrix(np.stack([np.array([pow(h, int(b*k % q), p) for k in kq]) for b in bq], axis=1), mons, p)
        arms.append(("Fpstar_prime_order_subgroup", Aq))
    for name, A in arms:
        Cc = A.shape[0]
        cell = {"arm": name, "candidates": Cc, "monomials": M, "rank": rank_mod(A, p)}
        mu2 = max_minority_L2(A, p); cell["L2_max_mu"] = mu2[0]; cell["L2_argmax"] = [mons[j] for j in mu2[1]] if mu2[1] else None
        mu3 = max_minority_L3(A, p, 600, rng); cell["L3_max_mu_sampled600"] = mu3[0]
        out["cells"].append(cell); print(json.dumps(cell), flush=True)
    # (b) prescribed balanced S
    sres = []
    for name, A in [("E_random_b", AE), ("null_uniform", Anull)]:
        for rep in range(3):
            S = sorted(rng.sample(range(C), C // 2)); comp = [i for i in range(C) if i not in set(S)]
            w, exact, rk = prange_min_support(A[S], A[comp], p, 300, rng)
            r = {"arm": name, "rep": rep, "s": len(S), "rank_AS": rk, "best_support_found": w, "best_exact_on_S": exact,
                 "trivial_upper_s_plus_1": len(S) + 1, "gv_estimate": gv_weight(M, len(S), p),
                 "counting_lower_bound": counting_lb(C, len(S), M, p)}
            sres.append(r); print(json.dumps(r), flush=True)
    out["prescribed_S"] = sres
    out["b_E"] = bs
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "h1pp_check.json", "w"), indent=1)

if __name__ == "__main__":
    main()
