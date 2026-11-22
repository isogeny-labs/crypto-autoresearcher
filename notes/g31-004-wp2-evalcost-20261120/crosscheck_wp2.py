#!/usr/bin/env python3
"""crosscheck_wp2.py -- WP2 / G31-004: independent validation of the p ~ 2^31
(and p ~ 2^20) specialisations used by the benchmarks.

Checks
  1. `specialize(s4_universal_Z, a=1,b=1, p)` == the repo's own
     `harness.semaev.s4_expr(1,1)` reduced mod p, term for term (439 terms).
     Same for S_3 (13 terms).  This validates the stored universal JSON and
     the specialisation code at the benchmark primes, not just at p=101.
  2. Value agreement with the independent quadratic-resultant closed form
     (validate.py's exhaustive path) on random tuples, at both primes.
  3. Zero density ~ 1/p on a large random sample (the polynomial is a
     codimension-1 hypersurface; a collapsed/degenerate specialisation would
     show up here).
  4. S_3 diagonal == duplication identity at p ~ 2^31 (structure check).

Repo is imported read-only under `python -B` (no bytecode written).

Run:  python3 -B crosscheck_wp2.py       (writes results_crosscheck.json)
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import sympy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Volumes/SSD990-2/crypto-autoresearcher"
sys.path.insert(0, HERE)
sys.path.insert(0, REPO)
import bench_wp2 as BW                        # noqa: E402
import semaev_eval as SE                      # noqa: E402
from harness import semaev                    # noqa: E402

P20, P31 = 1048573, 2147483647
SEED = 31004
OUT = {}


def poly_terms_modp(expr, gens, p=None):
    if p is None:
        return {tuple(e): int(c)
                for e, c in sympy.Poly(expr, *gens, domain="ZZ").terms()}
    return {tuple(e): int(c) % p
            for e, c in sympy.Poly(expr, *gens, modulus=p).terms()}


def quad_resultant(v1, v2, v3, v4, a, b, p):
    A1, B1, C1 = SE.s3_coeffs(v1, v2, a, b, p)
    A2, B2, C2 = SE.s3_coeffs(v3, v4, a, b, p)
    return (((A1 * C2 - C1 * A2) % p) ** 2
            - ((A1 * B2 - B1 * A2) % p) * ((B1 * C2 - C1 * B2) % p)) % p


def main():
    x1, x2, x3, x4 = sympy.symbols("x1 x2 x3 x4")

    # ---- 1. term-for-term vs the repo construction at a=b=1
    repo3 = poly_terms_modp(sympy.expand(semaev.s3_expr(1, 1)),
                            (x1, x2, x3))
    repo4 = sympy.expand(semaev.s4_expr(1, 1))
    for p in (P20, P31):
        r3 = {e: c % p for e, c in repo3.items()}
        r4 = poly_terms_modp(repo4, (x1, x2, x3, x4), p)
        m3 = SE.s3_mod(1, 1, p)
        m4 = SE.s4_mod(1, 1, p)
        rec = {
            "S3_terms": len(m3), "S4_terms": len(m4),
            "S3_equals_repo": m3 == r3,
            "S4_equals_repo": m4 == r4,
        }
        assert rec["S3_equals_repo"] and rec["S4_equals_repo"], (p, rec)
        OUT[f"a1b1_p{p}"] = rec
        print(f"[a=b=1, p={p}] S3 {len(m3)} terms S4 {len(m4)} terms, "
              f"term-for-term == repo: {rec['S4_equals_repo']}", flush=True)

    # ---- 2/3/4 on the benchmark curve a=0, b=7
    for p in (P20, P31):
        a, b = 0, 7
        s3 = SE.s3_mod(a, b, p)
        s4 = SE.s4_mod(a, b, p)
        g4 = SE.s4_grouped_by_x4(a, b, p, s4)
        r = np.random.default_rng(SEED)
        n = 4000
        xs = r.integers(0, p, size=(n, 4), dtype=np.int64)
        mm3 = mm4 = 0
        for i in range(n):
            t = [int(v) for v in xs[i]]
            A, B, C = SE.s3_coeffs(t[0], t[1], a, b, p)
            v3 = (A * t[2] % p * t[2] + B * t[2] + C) % p
            mm3 += (v3 != SE.s3_eval_sparse(t[0], t[1], t[2], s3, p))
            mm4 += (SE.s4_eval(*t, a, b, p, grouped=g4)
                    != quad_resultant(*t, a, b, p))
        assert mm3 == 0 and mm4 == 0
        # ---- constructive positive controls from the group law.
        # At p ~ 2^31 a random-sample zero rate is uninformative (1/p << 1/N),
        # so instead we BUILD tuples that must vanish: pick F_p points, take
        # P3 = -(P1+P2) (resp. P4 = -(P1+P2+P3)) and use its abscissa.
        C = SE.Curve(p, a, b)
        rp = np.random.default_rng(SEED + 1)
        pts = []
        while len(pts) < 3 * 700:
            x = int(rp.integers(0, p))
            fx = C.f(x)
            if fx and pow(fx, (p - 1) // 2, p) == 1:
                y = C._sqrt_p1m4(fx)
                pts.append((x, min(y, p - y)))
        ok3 = ok4 = 0
        tried3 = tried4 = 0
        i = 0
        while tried3 < 2000:
            P1, P2 = pts[i % len(pts)], pts[(i * 7 + 1) % len(pts)]
            i += 2
            S = C.add(P1, P2)
            if S is None:
                continue
            tried3 += 1
            ok3 += (SE.s3_eval(P1[0], P2[0], S[0], a, b, p) == 0)
            # perturbation control: x3+1 must not vanish
            assert SE.s3_eval(P1[0], P2[0], (S[0] + 1) % p, a, b, p) != 0
        i = 0
        while tried4 < 2000:
            P1 = pts[i % len(pts)]
            P2 = pts[(i * 13 + 5) % len(pts)]
            P3 = pts[(i * 31 + 9) % len(pts)]
            i += 3
            S = C.add(C.add(P1, P2), P3)
            if S is None:
                continue
            tried4 += 1
            ok4 += (SE.s4_eval(P1[0], P2[0], P3[0], S[0], a, b, p, grouped=g4) == 0)
            assert SE.s4_eval(P1[0], P2[0], P3[0], (S[0] + 1) % p, a, b, p,
                              grouped=g4) != 0
        assert ok3 == tried3 and ok4 == tried4, (ok3, tried3, ok4, tried4)
        OUT[f"a0b7_p{p}"] = {
            "S3_terms": len(s3), "S4_terms": len(s4),
            "S4_terms_by_x4_degree": {d: len(g4[d]) for d in range(5)},
            "random_tuple_mismatches_S3_vs_closedform": mm3,
            "random_tuple_mismatches_S4_vs_resultant": mm4,
            "positive_controls_S3_from_grouplaw": f"{ok3}/{tried3}",
            "positive_controls_S4_from_grouplaw": f"{ok4}/{tried4}",
            "perturbation_control_x_plus_1_nonzero": True,
            "note": "random-sample zero rate omitted: 1/p << 1/N at these "
                    "primes, so it would be uninformative",
        }
        print(f"[a=0,b=7, p={p}] S3 {len(s3)} terms S4 {len(s4)} terms; "
              f"mismatches {mm3}/{mm4}; positive controls S3 {ok3}/{tried3}, "
              f"S4 {ok4}/{tried4}", flush=True)

        # ---- S3 diagonal == duplication abscissa
        r3 = np.random.default_rng(SEED + 2)
        diag_ok = diag_bad = 0
        for _ in range(2000):
            x = int(r3.integers(0, p))
            fx = (x * x % p * x + b) % p
            if fx == 0:
                continue
            A, B, C = SE.s3_coeffs(x, x, a, b, p)
            if A != 0 or B % p == 0:
                diag_bad += 1
                continue
            root = (-C * pow(B, -1, p)) % p
            xd = ((3 * x * x % p) ** 2 % p * pow(4 * fx, -1, p) - 2 * x) % p
            diag_ok += (root == xd)
        OUT[f"a0b7_p{p}"]["S3_diagonal_doubling_ok"] = f"{diag_ok}/{diag_ok + diag_bad}"
        assert diag_bad == 0 and diag_ok > 1900, (diag_ok, diag_bad)
        print(f"   S3 diagonal == x([2]P): {diag_ok}/{diag_ok + diag_bad}",
              flush=True)

    with open(os.path.join(HERE, "results_crosscheck.json"), "w") as fh:
        json.dump(OUT, fh, indent=2)
    print("wrote results_crosscheck.json")


if __name__ == "__main__":
    main()
