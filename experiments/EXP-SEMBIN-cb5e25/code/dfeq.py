"""d_F^eq (M-6): first fall degree under the equality reading of Nagao's
Definition 5 (DC-5), computed on the true side (full ring F_2[X], field
equations among the generators when include_fe).

For d = 1, 2, ...: the homogeneous top-form map (h_i) -> sum h_i top(f_i) at
degree d, where h_i runs over the monomials of degree d - deg f_i (full ring,
squares allowed) for every generator, field equations included. A fall at d
is declared when
  * the kernel is nonzero, and
  * either some kernel element has a nonzero full sum  sum h_i f_i
    (rank of the full product rows exceeds the rank of the top forms), or some
    generator has degree < d (lower-perturbation rule).
All ranks are exact GF(2) ranks (python-int elimination). At d = 4 the
existence of a fall is certified by the explicit padding witness (DER-4); the
rank test is also available for small instances and used by the fixtures.

Monomials of the full ring are sorted tuples of variable indices with repeats.
"""
from __future__ import annotations

from itertools import combinations_with_replacement


def mask_to_mono(mask: int) -> tuple:
    out, i = [], 0
    while mask:
        if mask & 1:
            out.append(i)
        mask >>= 1
        i += 1
    return tuple(out)


def poly_from_masks(masks) -> frozenset:
    return frozenset(mask_to_mono(m) for m in masks)


def field_equation_polys(N: int):
    return [frozenset({(i, i), (i,)}) for i in range(N)]


def deg(p) -> int:
    return max((len(m) for m in p), default=-1)


def top_part(p) -> frozenset:
    d = deg(p)
    return frozenset(m for m in p if len(m) == d)


def _mul_mono(p, mu):
    out = set()
    for m in p:
        out ^= {tuple(sorted(m + mu))}
    return out


def _rank_ints(vecs):
    """Rank over GF(2) of a list of ints (highest-bit pivot elimination)."""
    piv = {}
    r = 0
    for v in vecs:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                r += 1
                break
    return r


def fall_at_degree(gens, N: int, d: int) -> dict:
    """Exact test at degree d (see module docstring). gens: list of frozensets
    of monomial tuples (field equations already included by the caller)."""
    index = {}

    def vec(poly, only_deg=None):
        v = 0
        for m in poly:
            if only_deg is not None and len(m) != only_deg:
                continue
            b = index.get(m)
            if b is None:
                b = index[m] = len(index)
            v |= 1 << b
        return v

    full_rows, top_rows = [], []
    gen_deg = [deg(g) for g in gens]
    for f, e in zip(gens, gen_deg):
        if e < 0 or e > d:
            continue
        for mu in combinations_with_replacement(range(N), d - e):
            prod = _mul_mono(f, mu)
            full_rows.append(vec(prod))
            top_rows.append(vec(prod, only_deg=d))
    nrows = len(full_rows)
    rank_top = _rank_ints(top_rows)
    rank_full = _rank_ints(full_rows)
    kernel = nrows - rank_top
    lower_gen = any(0 <= e < d for e in gen_deg)
    sum_nonzero = rank_full > rank_top
    return {"d": d, "rows": nrows, "rank_top": rank_top, "rank_full": rank_full,
            "kernel_dim": kernel, "kernel_has_nonzero_sum": sum_nonzero,
            "generator_below_d": lower_gen,
            "fall": bool(kernel > 0 and (sum_nonzero or lower_gen))}


def padding_witness(f1, f2) -> dict:
    """g1 = f2 + 1, g2 = f1: g1 f1 + g2 f2 = f1 (char 2). Verified in the full
    ring. Valid as a degree-(deg f1 + deg f2) fall when deg f1 < deg f1+deg f2
    and f1 != 0."""
    one = frozenset({()})
    g1 = frozenset(f2) ^ one
    g2 = frozenset(f1)

    def mul(p, q):
        out = set()
        for a in p:
            for b in q:
                out ^= {tuple(sorted(a + b))}
        return frozenset(out)

    p1, p2 = mul(g1, f1), mul(g2, f2)
    s = p1 ^ p2
    return {"g1": sorted(g1), "g2": sorted(g2), "deg_g1_f1": deg(p1), "deg_g2_f2": deg(p2),
            "max_product_degree": max(deg(p1), deg(p2)), "sum": sorted(s), "sum_degree": deg(s),
            "sum_nonzero": bool(s),
            "valid_fall": bool(s) and deg(s) < max(deg(p1), deg(p2))}


def d_F_eq(gens, N: int, include_fe: bool = True, dmax_rank: int = 3, rank_up_to: int = None,
           witness_degree: int = 4) -> dict:
    """gens: list of polys (iterables of monomial tuples) WITHOUT field
    equations; they are appended when include_fe. Returns dict(value, ...).

    value = least d <= dmax_rank with a fall (exact rank test), else
    witness_degree (4) if the padding witness is valid ("<= 4", certified by
    the witness, not by rank), else None.
    rank_up_to: also run the rank test at degrees up to this value (fixtures).
    """
    G = [frozenset(g) for g in gens]
    if include_fe:
        G = G + field_equation_polys(N)
    per_d = {}
    value = None
    top = max(dmax_rank, rank_up_to or 0)
    for d in range(1, top + 1):
        per_d[d] = fall_at_degree(G, N, d)
        if value is None and per_d[d]["fall"]:
            value = d
        if value is not None and rank_up_to is None:
            break
    witness = None
    if value is None or value > dmax_rank:
        # candidate pair: two field equations (true side), else the two lowest-degree generators
        cands = sorted([g for g in G if g], key=deg)
        pair = None
        if include_fe and N >= 2:
            fe = field_equation_polys(N)
            pair = (fe[0], fe[1])
        else:
            quad = [g for g in G if deg(g) == 2]
            if len(quad) >= 2:
                pair = (quad[0], quad[1])
        if pair is not None:
            w = padding_witness(*pair)
            w["generators"] = [sorted(pair[0]), sorted(pair[1])]
            if w["valid_fall"] and w["max_product_degree"] == witness_degree:
                witness = w
                if value is None:
                    value = witness_degree
    return {"value": value, "bound_by_witness_only": value == witness_degree and value > dmax_rank
            if value is not None else False,
            "per_d": per_d, "witness": witness, "include_fe": include_fe, "N": N}
