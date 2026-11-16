#!/usr/bin/env python3
"""Feasibility facts for the EXP-DREG-afca27 proposal. Standalone, stdlib only.

Counts common zeros of the chained t=4 system over F_4 for every (a6, R_X), and
the isogeny-transported target R_X' = x + s/x. It computes NO rank profile r(d),
no fall and no Groebner quantity: the preregistered outcome is not touched here.
Elements of F_4 are ints a0 + 2*a1, z^2 = z + 1; names 0, 1, z, z+1 = 0, 1, 2, 3.
"""
NAME = {0: "0", 1: "1", 2: "z", 3: "z+1"}


def mul(a, b):
    a0, a1, b0, b1 = a & 1, a >> 1, b & 1, b >> 1
    return ((a0 & b0) ^ (a1 & b1)) | (((a0 & b1) ^ (a1 & b0) ^ (a1 & b1)) << 1)


INV = {a: next(b for b in range(1, 4) if mul(a, b) == 1) for a in range(1, 4)}


def s3(a6, p, q, r):
    t = mul(p, q) ^ mul(p, r) ^ mul(q, r)
    return mul(t, t) ^ mul(mul(p, q), r) ^ a6


def zeros(a6, rx):
    """Assignments x1..x4 in {0,1}, u1, u2 in F_4 with the three equations = 0."""
    n = 0
    for x in range(16):
        x1, x2, x3, x4 = x & 1, x >> 1 & 1, x >> 2 & 1, x >> 3 & 1
        for u1 in range(4):
            for u2 in range(4):
                if s3(a6, u1, x1, x2) == s3(a6, u1, u2, x3) == s3(a6, u2, x4, rx) == 0:
                    n += 1
    return n


def sqrt(a):
    return next(s for s in range(1, 4) if mul(s, s) == a)


if __name__ == "__main__":
    print("common zeros over F_2^8 (0 means the ideal is the unit ideal)")
    print("  a6 \\ R_X " + "".join(f"{NAME[r]:>6}" for r in range(4)))
    Z = {}
    for a6 in (1, 2, 3):
        Z[a6] = [zeros(a6, r) for r in range(4)]
        print(f"  {NAME[a6]:>8} " + "".join(f"{v:6d}" for v in Z[a6]))
    print("\nedge: domain a6 -> codomain a6'' = a6 + s + s^2 (s = sqrt(a6)); transport R' = R + s/R")
    for a6 in (1, 2, 3):
        s = sqrt(a6)
        a6c = a6 ^ s ^ mul(s, s)
        print(f"  a6={NAME[a6]:>3}: s={NAME[s]:>3}, a6''={NAME[a6c]:>3}")
        for r in range(1, 4):
            rt = r ^ mul(s, INV[r])
            same = (Z[a6][r], Z[a6c][r])
            tran = (Z[a6][r], Z[a6c][rt])
            print(f"      R_X={NAME[r]:>3}: same-target zeros {same};  transported R_X'={NAME[rt]:>3}: zeros {tran}"
                  f"{'   both non-unit' if min(tran) > 0 else ''}")
    # Galois conjugation z <-> z+1 is F_2-linear on bits and fixes V = {0, 1}
    conj = {0: 0, 1: 1, 2: 3, 3: 2}
    ok = all(zeros(conj[a6], conj[r]) == Z[a6][r] for a6 in (1, 2, 3) for r in range(4))
    print("\nconjugation z<->z+1 maps (a6, R_X) -> (conj a6, conj R_X) and preserves the zero count:", ok)
