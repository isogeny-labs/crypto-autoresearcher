"""check_extra.py — targeted follow-ups (no frozen parameter is re-tuned):
1. classify every hook-literal containment hit (Q in witness?) for the cells
   that showed hits;
2. POWERED converse test at d=4: for random triples from B_G the residual
   point -sum is contained (positive control) and random other points are NOT
   (negative control) — exact dictionary equivalence with O(1) power per draw;
3. r(Q) = r(-Q) symmetry spot check for the symmetric x-window base.
"""
import math
import random

from ec import EC
from run_pilot import (find_curve, InvTable, Ctx, seed_int, scheme_cols,
                       dict_check)
from ec import phi, rank_p


def cell_repro(bits, seed, arm):
    class L:
        def __call__(self, *a):
            pass
    E, nE, c, n, g = find_curve(bits, seed, L())
    invt = InvTable(E.p)
    N = math.isqrt(E.p) if arm == "N2" else round(E.p ** (1 / 3))
    raw = E.points_x_window(N)
    Bset = {}                       # EXACT same construction/order as run_pilot
    for P in raw:
        cP = E.mul(c, P)
        if cP is not None:
            Bset[cP] = None
    B = list(Bset)
    ctx = Ctx(E, invt)
    ctx.n, ctx.g = n, g
    ctx.pair_table(B)
    return E, n, g, ctx, B


def hook_classify(bits, seed, arm, m):
    E, n, g, ctx, B = cell_repro(bits, seed, arm)
    rng_key = seed_int(seed, f"{arm}.targets") + 1
    trng = random.Random(rng_key)
    nT = 1200 if bits == 13 else 320
    budget, hits, trivial, bad = 200, 0, 0, 0
    for _ in range(nT):
        Q = E.mul(trng.randrange(1, n), g)
        r, wit = ctx.r_m(Q, m)
        if r and budget > 0:
            budget -= 1
            ok, hook = dict_check(E, Q, wit)
            assert ok
            if hook:
                hits += 1
                if Q in set(wit):
                    trivial += 1
                else:
                    bad += 1
    print(f"hook-literal {p_str(bits)} arm={arm} m={m}: hits={hits} "
          f"(self-containment Q in witness: {trivial}, unexplained: {bad})")
    return bad


def p_str(bits):
    return {17: "p=131671", 18: "p=265987", 20: "p=1060981",
            13: "p=8219"}[bits]


def powered_converse(bits, seed, arm, draws=1500):
    E, n, g, ctx, B = cell_repro(bits, seed, arm)
    p = E.p
    rng = random.Random(seed_int(seed, "poweredconverse"))
    b = len(B)
    pos_fail = neg_fail = pos = neg = 0
    for _ in range(draws):
        Ps = [B[rng.randrange(b)] for _ in range(3)]
        S = None
        for P in Ps:
            S = E.add(S, P)
        R = E.neg(S)
        cols = scheme_cols(E, 4, Ps)
        rk = rank_p(p, cols)
        pos += 1
        if rank_p(p, cols, phi(E, 4, R)) != rk:
            pos_fail += 1
        for _ in range(5):
            Q = E.mul(rng.randrange(1, n), g)
            if Q in Ps or Q == R:
                continue
            neg += 1
            if rank_p(p, cols, phi(E, 4, Q)) == rk:
                neg_fail += 1
    print(f"powered converse {p_str(bits)} arm={arm}: residual-contained "
          f"fails {pos_fail}/{pos}; random-point false-containments "
          f"{neg_fail}/{neg}")
    return pos_fail, neg_fail


def symmetry(bits, seed, arm):
    E, n, g, ctx, B = cell_repro(bits, seed, arm)
    rng = random.Random(seed_int(seed, "sym"))
    ok3 = ok4 = 0
    for _ in range(40):
        Q = E.mul(rng.randrange(1, n), g)
        r3, _ = ctx.r_m(Q, 3)
        r3n, _ = ctx.r_m(E.neg(Q), 3)
        r4, _ = ctx.r_m(Q, 4)
        r4n, _ = ctx.r_m(E.neg(Q), 4)
        ok3 += r3 == r3n
        ok4 += r4 == r4n
    print(f"r(Q)=r(-Q) {p_str(bits)} arm={arm}: m3 {ok3}/40, m4 {ok4}/40")


if __name__ == "__main__":
    bad = 0
    for bits, seed, arm, m in [(17, 31001, "N2", 3), (18, 31002, "N2", 3),
                               (18, 31002, "N2", 4), (20, 31003, "N2", 3),
                               (13, 31011, "N3", 3)]:
        bad += hook_classify(bits, seed, arm, m)
    for bits, seed, arm in [(17, 31001, "N3"), (20, 31003, "N3"),
                            (13, 31011, "N3")]:
        powered_converse(bits, seed, arm)
    for bits, seed, arm in [(17, 31001, "N3"), (20, 31003, "N2")]:
        symmetry(bits, seed, arm)
    print("UNEXPLAINED-HOOK-HITS:", bad)
