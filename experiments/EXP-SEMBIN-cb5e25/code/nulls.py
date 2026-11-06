"""Nulls: NULL-PROF (profile-matched planted random system) and NULL-SHUF
(support-shuffled copy of the EQS4 instance), both multilinear with a planted
uniform solution s. Deterministic given the HashRng.
"""
from __future__ import annotations

from math import comb

from descent import eval_poly


def profile_of(eqs):
    """Per equation: {degree: number of monomials of that degree}, degrees >= 1."""
    out = []
    for e in eqs:
        c = {}
        for x in e:
            d = bin(x).count("1")
            if d >= 1:
                c[d] = c.get(d, 0) + 1
        out.append(c)
    return out


def _random_monomials(nv, d, count, rng, banned=()):
    """`count` distinct uniformly drawn d-subsets of range(nv) as masks."""
    if count > comb(nv, d):
        raise ValueError("support larger than the number of monomials")
    chosen = set()
    while len(chosen) < count:
        # uniform d-subset by partial Fisher-Yates over a small pool
        pool = list(range(nv))
        m = 0
        for i in range(d):
            j = i + rng.randbelow(nv - i)
            pool[i], pool[j] = pool[j], pool[i]
            m |= 1 << pool[i]
        chosen.add(m)
    return sorted(chosen)


def _plant_constants(eqs, s):
    out = []
    for e in eqs:
        e = [m for m in e if m != 0]
        if eval_poly(e, s):
            e = [0] + e
        out.append(sorted(e))
    return out


def null_prof(nv: int, profile, rng):
    """Random multilinear system with exactly the per-equation per-degree
    monomial counts of `profile`, coefficient 1 on each support, constants set
    so that the uniform planted s is a solution. Returns (eqs, s)."""
    s = rng.getrandbits(nv)
    eqs = []
    for prof in profile:
        mons = []
        for d in sorted(prof):
            mons += _random_monomials(nv, d, prof[d], rng)
        eqs.append(mons)
    return _plant_constants(eqs, s), s


def null_shuf(nv: int, source_eqs, rng):
    """Same global (equation slot, monomial) incidences as the source system:
    the multiset of monomials of each degree d >= 1 is permuted uniformly over
    the d-slots of the equations (duplicates inside one equation repaired by
    swaps); constants re-set to plant a fresh uniform s. Returns (eqs, s)."""
    s = rng.getrandbits(nv)
    slots = {}   # d -> list of equation indices (one per slot)
    pool = {}
    for i, e in enumerate(source_eqs):
        for m in e:
            d = bin(m).count("1")
            if d >= 1:
                slots.setdefault(d, []).append(i)
                pool.setdefault(d, []).append(m)
    new = [set() for _ in source_eqs]
    for d in sorted(slots):
        mons = list(pool[d])
        rng.shuffle(mons)
        for _ in range(100000):
            seen, bad = {}, []
            for t, (i, m) in enumerate(zip(slots[d], mons)):
                if (i, m) in seen:
                    bad.append(t)
                seen[(i, m)] = t
            if not bad:
                break
            for t in bad:
                u = rng.randbelow(len(mons))
                mons[t], mons[u] = mons[u], mons[t]
        else:
            raise RuntimeError("could not remove duplicate incidences")
        for i, m in zip(slots[d], mons):
            new[i].add(m)
    return _plant_constants([sorted(x) for x in new], s), s
