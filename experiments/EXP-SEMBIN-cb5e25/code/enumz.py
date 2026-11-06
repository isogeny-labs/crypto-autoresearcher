"""Solution set Z of EQS4(m, R): algebraic chain enumeration, brute-force
bit-sliced cross-check, the reduced grevlex Groebner basis of I(Z) and the
EQS4-U uniqueness selection.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np

from descent import Field, plant, pack_solution, eval_poly


# --------------------------------------------------------------------------
# algebraic enumeration (no point arithmetic, no Boolean evaluation)
# --------------------------------------------------------------------------
def enumerate_Z(F: Field, B: int, v: list, k: int, x_R: int) -> list:
    """All s in F_2^N (as ints) solving the chained S_3 system."""
    m, n = len(v), F.n
    low = (1 << k) - 1
    out = set()

    def in_V(i, val):
        return ((val ^ v[i]) >> k) == 0

    def rec(t, prevU, xs, Us):
        # t = index of the next X to choose; prevU = last U chosen
        if t == m - 1:
            for xm in F.roots_S3(prevU, x_R, B):
                if in_V(m - 1, xm):
                    out.add(pack_solution(n, k, v, xs + [xm], Us))
            return
        for w in range(1 << k):
            xt = v[t] ^ w
            for u in F.roots_S3(prevU, xt, B):
                rec(t + 1, u, xs + [xt], Us + [u])

    for w1 in range(1 << k):
        x1 = v[0] ^ w1
        for w2 in range(1 << k):
            x2 = v[1] ^ w2
            for u in F.roots_S3(x1, x2, B):
                rec(2, u, [x1, x2], [u])
    return sorted(out)


# --------------------------------------------------------------------------
# brute force (bit-sliced) over F_2^N
# --------------------------------------------------------------------------
def brute_force_Z(nv: int, eqs, max_nv: int = 26) -> list:
    """All 0/1 points where every generator vanishes. Bit-sliced: variable i is
    the bitset (over all 2^nv points) of point index bit i. Points are indexed
    by their own integer value, so the result is the sorted list of solutions."""
    if nv > max_nv:
        raise ValueError("brute force limited")
    npts = 1 << nv
    if nv < 6:
        # tiny: plain loop (a bitset of < 64 points does not fill a word)
        return [p for p in range(npts) if all(eval_poly(e, p) == 0 for e in eqs)]
    W = npts >> 6
    idx = np.arange(npts, dtype=np.uint64)
    vars_ = []
    for i in range(nv):
        bits = ((idx >> np.uint64(i)) & np.uint64(1)).astype(np.uint8)
        vars_.append(np.packbits(bits, bitorder="little").view(np.uint64).copy())
    del idx
    ones = np.full(W, np.uint64(0xFFFFFFFFFFFFFFFF))
    cache = {0: ones}

    def mono(mask):
        r = cache.get(mask)
        if r is not None:
            return r
        low = mask & -mask
        rest = mask ^ low
        r = mono(rest) & vars_[low.bit_length() - 1]
        if bin(mask).count("1") <= 2 and nv <= 22:
            cache[mask] = r
        return r

    bad = np.zeros(W, dtype=np.uint64)
    for e in eqs:
        acc = np.zeros(W, dtype=np.uint64)
        for mk in e:
            acc ^= mono(mk)
        bad |= acc
    good = ~bad
    sol = []
    nz = np.flatnonzero(good)
    for w in nz.tolist():
        word = int(good[w])
        while word:
            b = (word & -word).bit_length() - 1
            sol.append(w * 64 + b)
            word &= word - 1
    return sorted(sol)


def affine_subspace_Z(nv: int, eqs, lin_forms, max_free: int = 16):
    """Z by exhaustive search inside the affine subspace cut out by linear forms
    known to lie in the ideal (e.g. the degree <= 1 part of W_D). Returns
    (Z sorted list, n_free) or None if more than max_free free variables.
    lin_forms: list of polynomials (lists of masks of degree <= 1)."""
    rows = []   # (coeff mask over variables, const)
    for f in lin_forms:
        c, const = 0, 0
        for mk in f:
            if mk == 0:
                const ^= 1
            else:
                c |= mk
        rows.append((c, const))
    # Gaussian elimination to RREF (pivot = lowest set variable)
    piv = {}
    for c, const in rows:
        for p, (pc, pk) in piv.items():
            if (c >> p) & 1:
                c ^= pc
                const ^= pk
        if c == 0:
            if const:
                return [], 0       # inconsistent: no points
            continue
        p = (c & -c).bit_length() - 1
        for q in list(piv):
            pc, pk = piv[q]
            if (pc >> p) & 1:
                piv[q] = (pc ^ c, pk ^ const)
        piv[p] = (c, const)
    free = [i for i in range(nv) if i not in piv]
    if len(free) > max_free:
        return None
    pts = np.zeros(1 << len(free), dtype=np.uint64)
    idx = np.arange(1 << len(free), dtype=np.uint64)
    for j, fv in enumerate(free):
        pts |= ((idx >> np.uint64(j)) & np.uint64(1)) << np.uint64(fv)
    for p, (c, const) in piv.items():
        rest = c & ~(1 << p)
        # x_p = const + sum_{q in rest} x_q
        val = np.full(pts.shape, np.uint64(const), dtype=np.uint64)
        r = rest
        while r:
            q = (r & -r).bit_length() - 1
            val ^= (pts >> np.uint64(q)) & np.uint64(1)
            r &= r - 1
        pts |= val << np.uint64(p)
    ok = np.ones(pts.shape, dtype=bool)
    for e in eqs:
        acc = np.zeros(pts.shape, dtype=np.uint64)
        for mk in e:
            acc ^= ((pts & np.uint64(mk)) == np.uint64(mk)).astype(np.uint64)
        ok &= (acc == 0)
    return sorted(int(x) for x in pts[ok]), len(free)


# --------------------------------------------------------------------------
# reduced grevlex Groebner basis of I(Z) in B (field equations omitted)
# --------------------------------------------------------------------------
def groebner_from_Z(Z: list, nv: int, max_candidates: int = 3_000_000) -> dict:
    """Standard monomials and reduced Groebner basis of the vanishing ideal of
    the finite point set Z in B = F_2[X]/(X^2+X), grevlex (X_0 > X_1 > ...;
    ascending order inside a degree = descending mask).

    The set of leading monomials of I(Z) is closed under supersets, so only
    monomials whose every (d-1)-subset is standard are candidates at degree d.
    Returns dict(standard=[masks ascending grevlex], gens=[(mask, tail)],
    d_GB, std_count_by_deg, z).
    """
    z = len(Z)
    if z == 0:
        return {"standard": [], "gens": [(0, [])], "d_GB": 0, "std_count_by_deg": [], "z": 0}
    Zarr = np.array(Z, dtype=np.uint64)

    def column(mask):
        ok = (Zarr & np.uint64(mask)) == np.uint64(mask)
        v = 0
        for i in np.flatnonzero(ok).tolist():
            v |= 1 << i
        return v

    basis = []   # (pivot-ordered reduced) list of (vec, combo)
    std = []     # standard masks in order of acceptance == ascending grevlex
    std_set = {0}
    gens = []

    def reduce(vec):
        combo = 0
        for bv, bc in basis:
            if vec ^ bv < vec:           # lead (highest bit) of bv is set in vec
                vec ^= bv
                combo ^= bc
        return vec, combo

    # degree 0
    v0 = column(0)
    basis.append((v0, 1))
    std.append(0)
    std_by_deg = [1]
    prev = [0]
    d = 0
    d_GB = 0
    while prev:
        d += 1
        cands = set()
        prev_set = set(prev)
        for s in prev:
            for j in range(nv):
                b = 1 << j
                if s & b:
                    continue
                m_ = s | b
                if m_ in cands:
                    continue
                if all((m_ ^ (1 << i)) in prev_set for i in _bits(m_)):
                    cands.add(m_)
        if len(cands) > max_candidates:
            raise MemoryError("too many candidates")
        cur = []
        for m_ in sorted(cands, reverse=True):      # ascending grevlex
            vec = column(m_)
            res, combo = reduce(vec)
            if res:
                # independent -> standard; keep basis sorted so that reduce()
                # works with highest-bit pivots
                _insert(basis, res, combo | (1 << len(std)))
                std.append(m_)
                cur.append(m_)
            else:
                tail = [std[i] for i in _bits(combo)]
                gens.append((m_, tail))
                d_GB = d
        std_by_deg.append(len(cur))
        std_set.update(cur)
        prev = cur
    # d_GB: degree of the highest minimal generator (1 for a single point)
    return {"standard": std, "gens": gens, "d_GB": d_GB, "std_count_by_deg": std_by_deg, "z": z}


def _bits(x):
    out = []
    i = 0
    while x:
        if x & 1:
            out.append(i)
        x >>= 1
        i += 1
    return out


def _insert(basis, vec, combo):
    """Insert (vec, combo) keeping highest-bit pivots distinct and the list
    ordered by decreasing pivot (so sequential reduction is correct)."""
    basis.append((vec, combo))
    basis.sort(key=lambda t: -t[0].bit_length())


def gb_polys(gb: dict):
    """The reduced GB as sorted lists of masks (m + tail), in (degree, mask desc)
    order of the leading monomial, i.e. ascending grevlex of leads."""
    return [sorted([m_] + list(tail)) for m_, tail in gb["gens"]]


def rank_ev_by_deg(gb: dict, D: int) -> list:
    """rank(ev_{Z,d}) for d = 0..D = number of standard monomials of degree <= d."""
    c = gb["std_count_by_deg"] + [0] * (D + 2)
    out, acc = [], 0
    for d in range(D + 1):
        acc += c[d]
        out.append(acc)
    return out


# --------------------------------------------------------------------------
# EQS4-U selection (depends on |Z| only)
# --------------------------------------------------------------------------
def select_unique(attempt_fn, max_attempts: int = 32):
    """attempt_fn(a) -> dict(inst=..., Z=[...]) . Returns (chosen or None, log).
    Rejected attempts are logged with |Z| (never closure-evaluated)."""
    log = []
    for a in range(max_attempts):
        rec = attempt_fn(a)
        log.append({"attempt": a, "z": len(rec["Z"]), "rec": rec})
        if len(rec["Z"]) == 1:
            return rec, a, log
    return None, None, log
