#!/usr/bin/env python3
"""Holant lead step (b'): QTT (binary-digit tensor-train) ranks of the decomposition transfer
matrix M[y,z] = #{x in FB : S_3(x,y,z) = 0} over the full F_p alphabet, under
  X   natural x-coordinate labelling                     (candidate)
  N   uniformly random relabelling of F_p, 99 draws      (negative control / null)
  LOG E-block labelled by discrete-log orbit index       (positive control: circulant-like)
  SH  shift matrix [z = y + 1 mod p]                     (detector sanity control)
Ranks are exact counts (numeric rank of integer unfoldings, tol below). No clock is measured.
Usage: qtt_rank.py --protocol-sha <hex> --out rows.jsonl [--sizes 6,7,8,9,10] [--curves 3] [--null 99]
"""
import argparse, hashlib, json, sys, numpy as np

def isprime(n): return n > 1 and all(n % d for d in range(2, int(n**.5) + 1))
def legendre(v, p): v %= p; return 0 if v == 0 else (1 if pow(v, (p-1)//2, p) == 1 else -1)

def curve_points(p, a, b):
    sq = {}
    for y in range(p): sq.setdefault(y*y % p, []).append(y)
    return [None] + [(x, y) for x in range(p) for y in sq.get((x**3 + a*x + b) % p, [])]

def add(P, Q, p, a):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    l = ((3*P[0]*P[0] + a) * pow(2*P[1], -1, p) if P == Q else (Q[1]-P[1]) * pow(Q[0]-P[0], -1, p)) % p
    x = (l*l - P[0] - Q[0]) % p
    return (x, (l*(P[0]-x) - P[1]) % p)

def S3(x1, x2, x3, p, a, b):
    return ((x1-x2)**2*x3*x3 - 2*((x1+x2)*(x1*x2+a)+2*b)*x3 + (x1*x2-a)**2 - 4*b*(x1+x2)) % p

def derive_seed(protocol_sha, *tags):
    h = hashlib.sha256((protocol_sha + "|" + "|".join(map(str, tags))).encode()).digest()
    return int.from_bytes(h[:8], "big")

def pick_curves(L, count, protocol_sha):
    """Largest prime p < 2^L; curves y^2 = x^3 + a x + b with a, b drawn from a protocol-derived
    stream, nonsingular, cyclic group of ODD prime order n (so E(F_p) has no 2-torsion and is cyclic)."""
    p = max(q for q in range(2**(L-1), 2**L) if isprime(q))
    rng = np.random.default_rng(derive_seed(protocol_sha, "curves", L))
    out, seen = [], set()
    while len(out) < count:
        a, b = int(rng.integers(0, p)), int(rng.integers(1, p))
        if (4*a**3 + 27*b*b) % p == 0 or (a, b) in seen: continue
        seen.add((a, b))
        E = curve_points(p, a, b)
        if isprime(len(E)) and len(E) > 2: out.append((p, a, b, E))
    return out

def transfer_matrix(p, a, b, FB):
    X = np.arange(p, dtype=np.int64)
    M = np.zeros((p, p), dtype=np.int64)
    for x in FB:
        M += (S3(x, X[:, None], X[None, :], p, a, b) == 0)
    return M

def qtt_ranks(M, L, order):
    """Ranks of all 2L-1 unfoldings of M (padded to 2^L x 2^L) seen as a 2L-way binary tensor.
    order 'interleaved': (y_L-1, z_L-1, ..., y_0, z_0) most significant first; 'blocked': (y..., z...)."""
    N = 2**L
    A = np.zeros((N, N)); A[:M.shape[0], :M.shape[1]] = M
    T = A.reshape([2]*L + [2]*L)                       # axes: y bits (msb first), z bits (msb first)
    axes = [ax for i in range(L) for ax in (i, L+i)] if order == "interleaved" else list(range(2*L))
    T = np.transpose(T, axes)
    ranks = []
    for c in range(1, 2*L):
        U = T.reshape(2**c, -1)
        s = np.linalg.svd(U, compute_uv=False)
        tol = s[0] * max(U.shape) * 1e-12 if s.size and s[0] > 0 else 0
        ranks.append(int((s > tol).sum()))
    return ranks

def summary(ranks): return {"r_max": max(ranks), "log2_params": float(sum(np.log2(np.maximum(ranks, 1))))}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--sizes", default="6,7,8,9,10"); ap.add_argument("--curves", type=int, default=3)
    ap.add_argument("--null", type=int, default=99)
    args = ap.parse_args()
    with open(args.out, "w") as f:
        for L in map(int, args.sizes.split(",")):
            for ci, (p, a, b, E) in enumerate(pick_curves(L, args.curves, args.protocol_sha)):
                n = len(E)
                Ex = sorted({P[0] for P in E[1:]})
                B = int(np.floor(np.sqrt(p))); FB = Ex[:B]          # fixed rule: smallest-x
                M = transfer_matrix(p, a, b, FB)
                base = dict(L=L, p=p, a=a, b=b, n=n, curve_index=ci, fb_size=len(FB))
                def emit(arm, Mx, draw=None, stream=None):
                    row = dict(base, arm=arm, draw=draw, stream=stream)
                    for order in ("interleaved", "blocked"):
                        r = qtt_ranks(Mx, L, order); row[order] = dict(ranks=r, **summary(r))
                    f.write(json.dumps(row) + "\n"); f.flush()
                emit("X", M)
                # positive control: label x(P) by discrete-log orbit index; twist x's keep their order after
                G = E[1]; R = None; logof = {}
                for k in range(n): logof[R] = k; R = add(R, G, p, a)
                orbit = {P[0]: min(logof[P], n - logof[P]) - 1 for P in E[1:]}
                twist = [x for x in range(p) if x not in orbit]
                perm = np.empty(p, dtype=np.int64)                  # perm[old] = new label
                for x, j in orbit.items(): perm[x] = j
                for i, x in enumerate(twist): perm[x] = len(orbit) + i
                Ml = np.zeros_like(M); Ml[np.ix_(perm, perm)] = M
                emit("LOG", Ml)
                Sh = np.zeros((p, p), dtype=np.int64); Sh[np.arange(p), (np.arange(p) + 1) % p] = 1
                emit("SH", Sh)
                for d in range(args.null):
                    rng = np.random.default_rng(derive_seed(args.protocol_sha, "null", L, ci, d))
                    q = rng.permutation(p); Mn = np.zeros_like(M); Mn[np.ix_(q, q)] = M
                    emit("N", Mn, draw=d, stream=d % 2)            # stream: A/A split of the null
                print(f"L={L} curve {ci} p={p} n={n} done", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
