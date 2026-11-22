"""charter_repeat.py — null distribution for the charter test.

For each informative (sparse) cell: 10 fresh generic sets per kind
(uniform / symmetric), same size, same frozen target set, 10 decomposition
rates; compare the x-window rate against the 20-draw null.
"""
import math
import random

from run_pilot import Ctx, InvTable, find_curve, seed_int, run_cell, make_generic
from check_extra import cell_repro

CELLS = [(13, 31011, "N3"), (17, 31001, "N3"), (18, 31002, "N3"),
         (20, 31003, "N3")]
REPEATS = 10

for bits, seed, arm in CELLS:
    class L:
        def __call__(self, *a):
            pass
    E, nE, c, n, g = find_curve(bits, seed, L())
    invt = InvTable(E.p)
    N = round(E.p ** (1 / 3))
    raw = E.points_x_window(N)
    Bset = {}
    for P in raw:
        cP = E.mul(c, P)
        if cP is not None:
            Bset[cP] = None
    B = list(Bset)
    b = len(B)
    nT = 1200 if bits == 13 else 320
    rng_key = seed_int(seed, f"{arm}.targets")
    trng = random.Random(rng_key + 1)
    targets = [E.mul(trng.randrange(1, n), g) for _ in range(nT)]
    xrng = random.Random(rng_key)  # unused, mirrors run_pilot
    for m in (3, 4):
        ctx = Ctx(E, invt)
        ctx.n, ctx.g = n, g
        ctx.pair_table(B)
        st = run_cell(ctx, E, targets, m, random.Random(rng_key),
                      n_wit_dict=0, converse_n=0)
        fx = st["dec"] / nT
        mx = st["r_tot"] / nT
        fracs = {"uniform": [], "symmetric": []}
        means = {"uniform": [], "symmetric": []}
        for kind in ("uniform", "symmetric"):
            for rep in range(REPEATS):
                B2 = make_generic(E, n, g, b, kind,
                                  random.Random(seed_int(seed, f"null.{arm}.{kind}.{m}.{rep}")))
                ctx2 = Ctx(E, invt)
                ctx2.n, ctx2.g = n, g
                ctx2.pair_table(B2)
                st2 = run_cell(ctx2, E, targets, m, random.Random(1),
                               n_wit_dict=0, converse_n=0)
                fracs[kind].append(st2["dec"] / nT)
                means[kind].append(st2["r_tot"] / nT)
        for kind in ("uniform", "symmetric"):
            arr = fracs[kind]
            above = sum(1 for v in arr if v > fx)
            mu = sum(arr) / len(arr)
            sd = (sum((v - mu) ** 2 for v in arr) / (len(arr) - 1)) ** 0.5
            arrm = means[kind]
            mumu = sum(arrm) / len(arrm)
            msd = (sum((v - mumu) ** 2 for v in arrm) / (len(arrm) - 1)) ** 0.5
            print(f"p={E.p} {arm} m={m} b={b} [{kind}] x-window frac={fx:.4f} "
                  f"mean_r={mx:.2f} | null frac {mu:.4f}±{sd:.4f} "
                  f"mean_r {mumu:.2f}±{msd:.2f} | draws>x-window: {above}/{REPEATS}")
