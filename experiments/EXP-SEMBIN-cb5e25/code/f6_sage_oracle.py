"""Run under Sage:  sage -python f6_sage_oracle.py < cases.json > oracle.json

Fixture F-6 oracle. For each case builds F_{2^n} with the case's modulus,
the chained S_3 system with src/semaev_tree.py (build_chained_system_symbolic),
optionally shifts the x variables (x_i -> x_i + v_i), descends with
src/semaev_tree.py weil_descend_to_F2 and prints the generators as lists of
monomial masks in the builder's variable order (X bits then U bits), plus
Sage's #E. Nothing from the measurement path is imported.
"""
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src"))

from sage.all import GF, PolynomialRing, EllipticCurve  # noqa: E402
import semaev_tree as ST  # noqa: E402


def run_case(c):
    if c.get("E_only"):
        P2 = PolynomialRing(GF(2), "t")
        t = P2.gen()
        mod = sum(t ** i for i in range(c["n"] + 1) if (c["poly"] >> i) & 1)
        Fq = GF(2 ** c["n"], name="alpha", modulus=mod)
        alpha = Fq.gen()
        el = lambda x: sum(((x >> i) & 1) * alpha ** i for i in range(c["n"]))
        return {"num_points_E": int(EllipticCurve(Fq, [1, el(c["A"]), 0, 0, el(c["B"])]).order())}
    n, k, m = c["n"], c["k"], c["m"]
    P2 = PolynomialRing(GF(2), "t")
    t = P2.gen()
    mod = sum(t ** i for i in range(n + 1) if (c["poly"] >> i) & 1)
    Fq = GF(2 ** n, name="alpha", modulus=mod)
    alpha = Fq.gen()
    el = lambda x: sum(((x >> i) & 1) * alpha ** i for i in range(n))
    A, B, xR = el(c["A"]), el(c["B"]), el(c["x_R"])
    E = EllipticCurve(Fq, [1, A, 0, 0, B])
    R, polys, names = ST.build_chained_system_symbolic(m, Fq, B, xR)
    gens = R.gens()
    n_u = m - 2
    if any(c["v"]):
        sub = {gens[n_u + i]: gens[n_u + i] + el(c["v"][i]) for i in range(m)}
        polys = [p.subs(sub) for p in polys]
    Bring, desc = ST.weil_descend_to_F2(polys, n, k, alpha, R)
    names = Bring.variable_names()
    # variable index in the builder's layout
    def idx(name):
        base, bit = name.split("_")
        bit = int(bit)
        if base.startswith("x"):
            return (int(base[1:]) - 1) * k + bit
        return m * k + (int(base[1:]) - 1) * n + bit
    mi = [idx(nm) for nm in names]
    out = []
    for p in desc:
        mons = []
        for mon in p.monomials():
            # (BooleanMonomial.variables() returns wrong variables in this Sage; parse the text)
            mask = 0
            txt = str(mon)
            if txt != "1":
                for nm in txt.split("*"):
                    mask |= 1 << mi[names.index(nm.strip())]
            mons.append(mask)
        out.append(sorted(mons))
    return {"gens": out, "num_points_E": int(E.order())}


if __name__ == "__main__":
    cases = json.load(sys.stdin)
    print(json.dumps([run_case(c) for c in cases]))
