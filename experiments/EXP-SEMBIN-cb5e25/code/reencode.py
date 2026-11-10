"""Random invertible affine change of variables (X = A Y + b over F_2) and a
random invertible M x M recombination of the equations: the A/A re-encoding
(EQS4-AA) and the hiding step of PC-TRI.

Both act on multilinear systems given as lists of mask lists. Linear forms are
idempotent in B, so the substitution is a degree-preserving automorphism of B
(DER-6). The solution set maps as Y = A^{-1}(X + b).
"""
from __future__ import annotations

import hashlib
import json


def _rank_rows(rows):
    piv = {}
    r = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                r += 1
                break
    return r


def random_invertible(n: int, rng, density: float = 0.5, tries: int = 200):
    """Random invertible n x n matrix over F_2 as list of row ints (row i, bit j).
    density = probability of a 1 (uses 16-bit thresholds, deterministic)."""
    thr = int(density * 65536)
    for _ in range(tries):
        rows = []
        for _i in range(n):
            v = 0
            for j in range(n):
                if rng.getrandbits(16) < thr:
                    v |= 1 << j
            rows.append(v)
        if _rank_rows(rows) == n:
            return rows
    # fall back: identity plus random strictly-lower part is always invertible
    rows = []
    for i in range(n):
        v = 1 << i
        for j in range(i):
            if rng.getrandbits(16) < thr:
                v |= 1 << j
        rows.append(v)
    perm = list(range(n))
    rng.shuffle(perm)
    return [rows[p] for p in perm] if _rank_rows([rows[p] for p in perm]) == n else rows


def mat_inverse(rows, n):
    aug = [(rows[i], 1 << i) for i in range(n)]
    for col in range(n):
        p = next(i for i in range(col, n) if (aug[i][0] >> col) & 1)
        aug[col], aug[p] = aug[p], aug[col]
        for i in range(n):
            if i != col and (aug[i][0] >> col) & 1:
                aug[i] = (aug[i][0] ^ aug[col][0], aug[i][1] ^ aug[col][1])
    return [aug[i][1] for i in range(n)]


def random_encoding(nv: int, M: int, rng, density: float = 0.5):
    A = random_invertible(nv, rng, density)
    b = rng.getrandbits(nv)
    T = random_invertible(M, rng.substream("T"), density)
    h = hashlib.sha256(json.dumps([A, b, T]).encode()).hexdigest()
    return {"A": A, "b": b, "T": T, "summary": {"density": density, "sha256": h, "nv": nv, "M": M}}


def _mul_sets(P, Q):
    out = {}
    for a in P:
        for b in Q:
            m = a | b
            out[m] = out.get(m, 0) ^ 1
    return {m for m, p in out.items() if p}


def substitute_affine(nv, eqs, A, b):
    """X_i = (xor_j A[i] bit j * Y_j) xor b_i, reduced to multilinear."""
    forms = []
    for i in range(nv):
        f = {1 << j for j in range(nv) if (A[i] >> j) & 1}
        if (b >> i) & 1:
            f ^= {0}
        forms.append(f)
    cache = {0: {0}}

    def expand(mask):
        r = cache.get(mask)
        if r is not None:
            return r
        low = mask & -mask
        rest = mask ^ low
        r = _mul_sets(expand(rest), forms[low.bit_length() - 1])
        cache[mask] = r
        return r

    out = []
    for e in eqs:
        acc = set()
        for m in e:
            acc ^= expand(m)
        out.append(sorted(acc))
    return out


def recombine(eqs, T):
    out = []
    for row in T:
        acc = set()
        for j, e in enumerate(eqs):
            if (row >> j) & 1:
                acc ^= set(e)
        out.append(sorted(acc))
    return out


def apply_encoding(nv, eqs, enc, Zs):
    """Returns (new eqs, mapped solutions) for the encoding enc."""
    A, b, T = enc["A"], enc["b"], enc["T"]
    new = recombine(substitute_affine(nv, eqs, A, b), T)
    Ainv = mat_inverse(A, nv)
    out = []
    for z in Zs:
        x = z ^ b
        y = 0
        for i in range(nv):
            if bin(Ainv[i] & x).count("1") & 1:
                y |= 1 << i
        out.append(y)
    return new, sorted(out)
