#!/usr/bin/env python3
"""Exact finite checks behind DERIVATION-n1-F4-class-exhausted.md. Stdlib only.

No rank profile, fall or Groebner quantity is computed. Elements of F_4 are ints
a0 + 2*a1, z^2 = z + 1; names 0, 1, z, z+1 = 0, 1, 2, 3.
"""
N = {0: "0", 1: "1", 2: "z", 3: "z+1"}


def mul(a, b):
    a0, a1, b0, b1 = a & 1, a >> 1, b & 1, b >> 1
    return ((a0 & b0) ^ (a1 & b1)) | (((a0 & b1) ^ (a1 & b0) ^ (a1 & b1)) << 1)


def sq(a):
    return mul(a, a)


CONJ = {0: 0, 1: 1, 2: 3, 3: 2}      # Frobenius of F_4 over F_2: z <-> z+1


def npts(a2, a6):
    return 1 + sum(1 for x in range(4) for y in range(4)
                   if sq(y) ^ mul(x, y) == mul(sq(x), x) ^ mul(a2, sq(x)) ^ a6)


def s3(a6, p, q, r):
    t = mul(p, q) ^ mul(p, r) ^ mul(q, r)
    return sq(t) ^ mul(mul(p, q), r) ^ a6


def equations(a6, rx, x, u1, u2):
    x1, x2, x3, x4 = x
    return (s3(a6, u1, x1, x2), s3(a6, u1, u2, x3), s3(a6, u2, x4, rx))


def tr(a):
    return a ^ sq(a)                 # absolute trace; takes values 0 or 1


if __name__ == "__main__":
    print("1. point counts: ordinary models y^2+xy = x^3+a2 x^2+a6 over F_4")
    for a6 in (1, 2, 3):
        print(f"   a6={N[a6]:>3}: " + ", ".join(
            f"a2={N[a2]}: #E={npts(a2, a6)} (t={5 - npts(a2, a6):+d})" for a2 in range(4)))
    # a2 and a2+1 give isomorphic curves over F_4 (same trace), so classes are (a6, Tr a2)
    assert all(npts(a2, a6) == npts(a2 ^ 1, a6) for a2 in range(4) for a6 in (1, 2, 3))
    assert all(tr(a2) == tr(a2 ^ 1) for a2 in range(4))
    print("   a2 and a2+1 always have equal #E and equal Tr(a2): classes are (a6, Tr a2).")

    print("\n2. the 2-isogeny with kernel (0, s), s^2 = a6, has codomain a6'' = a6 + s + s^2")
    for a6 in (1, 2, 3):
        s = next(s for s in range(1, 4) if sq(s) == a6)
        c = a6 ^ s ^ sq(s)
        print(f"   a6={N[a6]:>3} -> a6''={N[c]:>3}   (a6 unchanged: {c == a6}; "
              f"a6'' = conj(a6): {c == CONJ[a6]})")
        assert (c == a6) if a6 == 1 else (c == CONJ[a6])

    print("\n3. conjugation is a ring automorphism of F_4, additive on the bits, and fixes V = {0,1}")
    assert all(CONJ[a ^ b] == CONJ[a] ^ CONJ[b] and CONJ[mul(a, b)] == mul(CONJ[a], CONJ[b])
               for a in range(4) for b in range(4))
    assert CONJ[0] == 0 and CONJ[1] == 1
    print("   verified.")

    print("\n4. system(a6, R_X) and system(conj a6, conj R_X) are linearly equivalent:")
    print("   conj(E_i^{(a6,R)}(x, u1, u2)) == E_i^{(conj a6, conj R)}(x, conj u1, conj u2)")
    print("   for all 3 equations, all 256 assignments (x in {0,1}^4, u in F_4^2), all (a6, R_X).")
    checked = 0
    for a6 in range(4):
        for rx in range(4):
            for x in range(16):
                xs = (x & 1, x >> 1 & 1, x >> 2 & 1, x >> 3 & 1)
                for u1 in range(4):
                    for u2 in range(4):
                        lhs = tuple(CONJ[e] for e in equations(a6, rx, xs, u1, u2))
                        rhs = equations(CONJ[a6], CONJ[rx], xs, CONJ[u1], CONJ[u2])
                        assert lhs == rhs
                        checked += 1
    print(f"   {checked} assignment/parameter combinations checked, 0 mismatches.")
    print("   So the substitution u -> conj(u) (F_2-linear on the 4 bits of u1, u2, identity on x)")
    print("   carries one system's component functions onto F_2-linear combinations of the other's:")
    print("   equal r(d), falls and solving degree for every d follow from the same invariance")
    print("   as GL-8. This is a derivation from the finite check, not a run.")
