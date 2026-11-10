"""PC-TRI: hidden triangular planted system (DER-6).

f_j = X_j + s_j + q_j(X_0..X_{j-1}) + q_j(s), j = 0..N-1, followed by
extra equations q_e(X) + q_e(s) (q random multilinear of degree <= 3), then a
random invertible affine variable map and a random invertible recombination of
the equations (reencode.apply_encoding). Provably D_solve <= 3 and |Z| = 1.
"""
from __future__ import annotations

from math import comb

from descent import eval_poly
from nulls import _random_monomials, profile_of
from reencode import apply_encoding, random_encoding


def tri_system(nv: int, M: int, profile, rng):
    """Plain triangular planted system. M < nv is raised to nv (declared
    mismatch, returned as M_eff). Returns (eqs, s, M_eff)."""
    s = rng.getrandbits(nv)
    M_eff = max(M, nv)
    profs = sorted(profile + [{}] * max(0, M_eff - len(profile)),
                   key=lambda p: -sum(p.values()))
    # heaviest profiles to the equations with most room: triangular equation j
    # (0-indexed) can use variables < j; extras can use all variables.
    eqs = []
    # assignment: triangular j gets profs[nv-1-j] (largest at j = nv-1);
    # extras get the remaining (smallest) profiles
    tri_profs = [profs[nv - 1 - j] for j in range(nv)]
    extra_profs = profs[nv:]
    for j in range(nv):
        avail = j
        mons = []
        for d in (1, 2, 3):
            c = min(tri_profs[j].get(d, 0), comb(avail, d)) if avail >= d else 0
            if c:
                # monomials over variables 0..j-1 only
                mons += _random_monomials(avail, d, c, rng)
        f = [(1 << j)] + mons
        if eval_poly(f, s):
            f = [0] + f
        eqs.append(sorted(f))
    for prof in extra_profs:
        mons = []
        for d in (1, 2, 3):
            c = min(prof.get(d, 0), comb(nv, d))
            if c:
                mons += _random_monomials(nv, d, c, rng)
        f = list(mons)
        if eval_poly(f, s):
            f = [0] + f
        eqs.append(sorted(f))
    return eqs, s, M_eff


def pc_tri(nv: int, M: int, profile, rng, density: float = 0.5):
    """Hidden PC-TRI instance. Returns dict(eqs, Z=[s'], M_eff, encoding)."""
    eqs, s, M_eff = tri_system(nv, M, profile, rng)
    enc = random_encoding(nv, M_eff, rng.substream("hide"), density=density)
    eqs2, s2 = apply_encoding(nv, eqs, enc, [s])
    return {"eqs": eqs2, "Z": s2, "M_eff": M_eff, "mismatch": M_eff != M, "encoding": enc["summary"],
            "plain_eqs": eqs, "plain_s": s}
