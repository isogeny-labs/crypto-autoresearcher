#!/usr/bin/env python3
"""WP1 / G31-004 task 1: explicit census of Semaev summation polynomials
S_3, S_4 over odd-characteristic prime fields, computed via the standard
resultant recursion (repo convention, harness/semaev.py).

Outputs:
  polynomials/*.json   sparse {exponent-vector: coefficient} encodings
  results/census_stats.json   all stats + timings + provenance

Run:  python3 census.py            (expect a few minutes wall clock)
"""
from __future__ import annotations

import itertools
import json
import platform
import resource
import subprocess
import sys
import time

import numpy
import sympy
from sympy import Poly, expand, resultant, symbols

# ------------------------------------------------------------------ provenance
HERE = "/Volumes/SSD990/llm/tmp/opencode/g31-004"
REPO = "/Volumes/SSD990-2/crypto-autoresearcher"
PRIMES = [101, 127, 1009]
CURVE = (1, 1)  # (a, b), used for all primes; disc = 4a^3+27b^2 = 31 != 0 mod p
SEED = 31004    # master RNG seed for any random sampling here

x1, x2, x3, x4, t = symbols("x1 x2 x3 x4 t")
a, b = symbols("a b")

PROV = {
    "python": sys.version.split()[0],
    "sympy": sympy.__version__,
    "numpy": numpy.__version__,
    "platform": platform.platform(),
    "repo_path": REPO,
    "repo_head": None,
    "script": f"{HERE}/census.py",
    "seed": SEED,
    "curve_choice": "no fixed curve exists in harness/toycurve.py (instances "
                    "are seed-generated); documented concrete choice a=1,b=1 "
                    "for all p; discriminant 4a^3+27b^2=31 nonzero mod 101,127,1009",
}
try:
    PROV["repo_head"] = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=10).stdout.strip() or None
except Exception as exc:  # pragma: no cover
    PROV["repo_head"] = f"unavailable: {exc}"

TIMINGS: dict[str, float] = {}
MEM: dict[str, int] = {}


def rss() -> int:
    """Peak RSS of this process in bytes (ru_maxrss is bytes on macOS)."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def timed(name, fn):
    t0 = time.perf_counter()
    out = fn()
    TIMINGS[name] = time.perf_counter() - t0
    MEM[name] = rss()
    print(f"[{name}] {TIMINGS[name]:.3f}s  peakRSS={MEM[name]/1e6:.1f}MB", flush=True)
    return out


# ------------------------------------------------------------- construction
def s3_expr(e1, e2, e3):
    """Third summation polynomial for y^2 = x^3 + a x + b (generic a, b).
    Same closed form as harness/semaev.s3_expr (Semaev, ePrint 2004/031,
    cleared-denominator form for odd characteristic)."""
    return ((e1 - e2) ** 2 * e3 ** 2
            - 2 * ((e1 + e2) * (e1 * e2 + a) + 2 * b) * e3
            + ((e1 * e2 - a) ** 2 - 4 * b * (e1 + e2)))


def quad_quad_resultant(A_, B_, C_, D_, E_, F_):
    """Res_t of (A t^2 + B t + C) and (D t^2 + E t + F) as a closed
    expression -- an independent check against sympy.resultant.
    (Formal 4x4 Sylvester determinant: agrees with sympy's generic
    resultant for polynomial coefficients; only differs from sympy's
    *evaluated* resultant when a leading coefficient is numerically 0.)"""
    return (A_ * F_ - C_ * D_) ** 2 - (A_ * E_ - B_ * D_) * (B_ * F_ - C_ * E_)


import itertools as _it
_PERMS4 = []
for _pm in _it.permutations(range(4)):
    _inv = sum(1 for i in range(4) for j in range(i + 1, 4) if _pm[i] > _pm[j])
    _PERMS4.append((_pm, -1 if _inv % 2 else 1))


def poly_stats_modp(P: Poly, p: int, height_mode: str = "modp"):
    """Census statistics of a Poly (over F_p, or over Z with height_mode='Z')."""
    gens = P.gens
    terms = P.terms()
    monoms = [tr[0] for tr in terms]
    coeffs = ([abs(int(tr[1])) for tr in terms] if height_mode == "Z"
              else [int(tr[1]) % p for tr in terms])
    degs = []
    for i in range(len(gens)):
        degs.append(max(m[i] for m in monoms))
    box = 1
    for d in degs:
        box *= (d + 1)
    return {
        "gens": [str(g) for g in gens],
        "total_degree": P.total_degree(),
        "per_variable_degrees": {str(g): d for g, d in zip(gens, degs)},
        "monomial_count": len(monoms),
        "dense_box_size": box,
        "support_fraction": round(len(monoms) / box, 6),
    ("coeff_heights_Z" if height_mode == "Z" else "coeff_stats_modp"): {
        "min": min(coeffs), "max": max(coeffs),
        "mean": round(sum(coeffs) / len(coeffs), 3),
    },
    }


def save_poly(name: str, P: Poly):
    gens = [str(g) for g in P.gens]
    data = {
        "gens": gens,
        "terms": [{"exp": list(tr[0]), "coeff": str(tr[1])} for tr in P.terms()],
    }
    with open(f"{HERE}/polynomials/{name}.json", "w") as fh:
        json.dump(data, fh)
    print(f"    saved polynomials/{name}.json ({len(P.terms())} terms)", flush=True)


def main():
    print("== provenance ==")
    print(json.dumps(PROV, indent=2), flush=True)

    # ---------------- universal S_3 and S_4 over Z[a,b,x1..x4] -------------
    s3u = timed("S3_universal_expand", lambda: expand(s3_expr(x1, x2, x3)))
    S3U = Poly(s3u, x1, x2, x3, a, b, domain="ZZ")

    def s4_universal_sympy():
        left = s3u.subs(x3, t)
        right = s3u.subs({x1: x3, x2: x4, x3: t}, simultaneous=True)
        return expand(resultant(left, right, t))

    s4u = timed("S4_universal_Z_resultant", s4_universal_sympy)
    S4U = Poly(s4u, x1, x2, x3, x4, a, b, domain="ZZ")
    save_poly("s3_universal_Z", S3U)
    save_poly("s4_universal_Z", S4U)

    # universal (symbolic-a,b) stats: degrees etc. are p-independent
    univ_stats = {
        "S3_universal_Z": poly_stats_modp(S3U, 0, height_mode="Z"),
        "S4_universal_Z": poly_stats_modp(S4U, 0, height_mode="Z"),
    }

    # symmetric-function check: S_m must be invariant under every permutation
    def sym_check(P: Poly, nvars):
        sup = {tr[0]: tr[1] for tr in P.terms()}
        bad = []
        for perm in itertools.permutations(range(nvars)):
            for m, c in sup.items():
                key = list(m)
                for i in range(nvars):
                    key[i] = m[perm[i]]
                if sup.get(tuple(key)) != c:
                    bad.append((perm, m, tuple(key)))
                    break
            if bad:
                break
        return {"symmetric": not bad, "first_violation": bad[:1]}

    univ_stats["S3_symmetry_Z_exact"] = sym_check(S3U, 3)
    univ_stats["S4_symmetry_Z_exact"] = sym_check(S4U, 4)

    # ---------------- independent derivation of S_3 (collinearity) ---------
    # S_3 = 0  <=>  (x1,y1),(x2,y2),(x3,y3) collinear for some lifts
    # (collinear triples sum to O).  Eliminate y3 (linear in the determinant),
    # then y2, then y1 by iterated resultants; compare with s3u.
    y1, y2, y3 = symbols("y1 y2 y3")

    def indep_s3():
        f1 = y1 ** 2 - (x1 ** 3 + a * x1 + b)
        f2 = y2 ** 2 - (x2 ** 3 + a * x2 + b)
        f3 = y3 ** 2 - (x3 ** 3 + a * x3 + b)
        det = y1 * (x2 - x3) - y2 * (x1 - x3) + y3 * (x1 - x2)
        n2 = expand(resultant(det, f3, y3))       # linear in y3 -> closed form
        r1 = expand(resultant(Poly(n2, y2), Poly(f2, y2), y2))
        r0 = expand(resultant(Poly(r1, y1), Poly(f1, y1), y1))
        return r0

    r0 = timed("S3_independent_elimination_Z", indep_s3)
    indep = {}
    try:
        R = Poly(r0, x1, x2, x3, a, b, domain="ZZ")

        def s3_power_divides(e):
            """True if numeric evidence says s3u^e divides R (random Z points)."""
            import random
            rng = random.Random(SEED)
            for _ in range(40):
                pt = tuple(rng.randrange(-9, 10) for _ in range(5))
                rv = R(*pt)
                sv = s3u.subs({x1: pt[0], x2: pt[1], x3: pt[2], a: pt[3], b: pt[4]})
                if sv == 0:
                    continue
                if rv % sv ** e != 0:
                    return False
            return True
        found = 0
        for e in range(1, 9):
            if s3_power_divides(e):
                found = e
        indep["iterated_resultant_total_degree"] = R.total_degree()
        indep["iterated_resultant_monomial_count"] = len(R.terms())
        indep["max_e_with_s3_power_e_dividing_R_numeric"] = found or None
        if found:
            cf_deg = R.total_degree() - found * 4
            indep["residual_cofactor_total_degree"] = cf_deg
            # zero-set agreement of R vs closed form over F_101, random points
            import random
            p = 101
            rng = random.Random(SEED + 1)
            fR = sympy.lambdify((x1, x2, x3, a, b), R.as_expr(), "math")
            fS = sympy.lambdify((x1, x2, x3, a, b), s3u, "math")
            mm_diag = mm_offdiag = missed_s3_zero = 0
            for _ in range(4000):
                pt = tuple(rng.randrange(p) for _ in range(5))
                zr = int(fR(*pt)) % p == 0
                zs = int(fS(*pt)) % p == 0
                if zr != zs:
                    if zs and not zr:
                        missed_s3_zero += 1
                    elif pt[0] == pt[1] or pt[0] == pt[2] or pt[1] == pt[2]:
                        mm_diag += 1
                    else:
                        mm_offdiag += 1
            indep["vs_closed_form_mod101_random4000"] = {
                "mismatch_on_diagonal_xi_xj_extraneous_factor_zeros": mm_diag,
                "mismatch_off_diagonal": mm_offdiag,
                "S3_zero_but_elimination_nonzero": missed_s3_zero}
    except Exception as exc:
        indep["error"] = f"{type(exc).__name__}: {exc}"
    univ_stats["S3_independent_elimination"] = indep

    # ---------------- per-prime census with 3 S_4 methods ------------------
    per_prime = {}
    rng = numpy.random.default_rng(SEED)
    for p in PRIMES:
        rec = {"p": p, "a": CURVE[0], "b": CURVE[1]}
        s3p_expr = s3u.subs({a: CURVE[0], b: CURVE[1]})
        S3p = Poly(s3p_expr, x1, x2, x3, modulus=p)
        rec["S3_stats"] = poly_stats_modp(S3p, p)
        rec["S3_Z_then_reduce"] = "yes"

        # S_4 method A: universal Z resultant, specialize a,b, reduce mod p
        def mA():
            return Poly(s4u.subs({a: CURVE[0], b: CURVE[1]}), x1, x2, x3, x4, modulus=p)

        # S_4 method B: own Sylvester 4x4 determinant with polynomial
        # entries over F_p (no sympy resultant, no closed form)
        def t_coeff(P, e):
            """Coefficient polynomial (in x1..x4) of t^e, as {exp4: coeff} mod p."""
            out = {}
            for m, c in P.terms():
                if m[4] == e:
                    key = m[:4]
                    out[key] = (out.get(key, 0) + int(c)) % p
            return {k: v for k, v in out.items() if v}

        def mB():
            P = Poly(s3p_expr.subs(x3, t), x1, x2, x3, x4, t, modulus=p)
            Q = Poly(s3p_expr.subs({x1: x3, x2: x4, x3: t}, simultaneous=True),
                     x1, x2, x3, x4, t, modulus=p)

            def pmul(f, g):
                out = {}
                for m1, c1 in f.items():
                    for m2, c2 in g.items():
                        mm = tuple(i + j for i, j in zip(m1, m2))
                        out[mm] = (out.get(mm, 0) + c1 * c2) % p
                return {m: c for m, c in out.items() if c}

            A_, B_, C_ = [t_coeff(P, e) for e in (2, 1, 0)]
            D_, E_, F_ = [t_coeff(Q, e) for e in (2, 1, 0)]
            Z = {}
            M = [[A_, B_, C_, Z], [Z, A_, B_, C_],
                 [D_, E_, F_, Z], [Z, D_, E_, F_]]
            total = {}
            for perm, sign in _PERMS4:
                blk = {(0, 0, 0, 0): 1}
                for i in range(4):
                    blk = pmul(blk, M[i][perm[i]])
                for mm, cc in blk.items():
                    total[mm] = (total.get(mm, 0) + sign * cc) % p
            total = {mm: cc % p for mm, cc in total.items() if cc % p}
            return Poly(total, x1, x2, x3, x4, modulus=p)

        # S_4 method C: quadratic-resultant closed form over Z, then reduce
        def mC():
            P = Poly(s3p_expr.subs(x3, t), x1, x2, x3, x4, t, domain="ZZ")
            Q = Poly(s3p_expr.subs({x1: x3, x2: x4, x3: t}, simultaneous=True),
                     x1, x2, x3, x4, t, domain="ZZ")

            def t_expr(Poly_, e):
                acc = sympy.Integer(0)
                for m, c in Poly_.terms():
                    if m[4] == e:
                        mon = 1
                        for gi, mm in enumerate(m[:4]):
                            if mm:
                                mon = mon * Poly_.gens[gi] ** mm
                        acc += c * mon
                return acc

            A_, B_, C_ = [t_expr(P, e) for e in (2, 1, 0)]
            D_, E_, F_ = [t_expr(Q, e) for e in (2, 1, 0)]
            return Poly(quad_quad_resultant(A_, B_, C_, D_, E_, F_),
                        x1, x2, x3, x4, modulus=p)

        SA = timed(f"S4_p{p}_Z_then_reduce", mA)
        SB = timed(f"S4_p{p}_sympy_poly_modp", mB)
        SC = timed(f"S4_p{p}_quadform", mC)
        dA, dB, dC = (dict(P.terms()) for P in (SA, SB, SC))
        rec["S4_method_agreement"] = {
            "A_equals_B": dA == dB, "A_equals_C": dA == dC,
        }
        rec["S4_stats"] = poly_stats_modp(SA, p)
        if p == PRIMES[0]:
            save_poly(f"s4_mod{p}", SA)
            save_poly(f"s3_mod{p}", S3p)

        # zero-set sampling with numpy vectorized evaluation of S4 mod p
        def sample_zeros(P: Poly, n: int, nvars: int, seed_i: int):
            r = numpy.random.default_rng(SEED + 7 * seed_i)
            arrays = [r.integers(0, p, size=n, dtype=numpy.int64) for _ in range(nvars)]
            pows = [[numpy.ones(n, dtype=numpy.int64)] for _ in range(nvars)]
            for i in range(nvars):
                for e in range(1, P.degree(i) + 1):
                    pows[i].append(pows[i][-1] * arrays[i] % p)
            acc = numpy.zeros(n, dtype=numpy.int64)
            for monom, c in P.terms():
                blk = numpy.full(n, int(c) % p, dtype=numpy.int64)
                for i, e in enumerate(monom):
                    if e:
                        blk = blk * pows[i][e] % p
                acc += blk
                acc %= p
            return int(numpy.count_nonzero(acc == 0))

        if p in (101, 127):  # S3 full zero census (p^3 <= 2.1M) is in validate.py;
            rec["S3_full_zero_census"] = "see validate.py (exhaustive)"
        rec["S3_zero_rate_sample200k"] = round(sample_zeros(S3p, 200_000, 3, p) / 200_000, 5)
        rec["S4_zero_rate_sample200k"] = round(sample_zeros(SA, 200_000, 4, p) / 200_000, 5)
        per_prime[str(p)] = rec

    out = {
        "provenance": PROV,
        "universal": univ_stats,
        "per_prime": per_prime,
        "timings_sec": TIMINGS,
        "peak_rss_bytes_final": rss(),
    }
    with open(f"{HERE}/results/census_stats.json", "w") as fh:
        json.dump(out, fh, indent=2, default=str)
    print("== summary ==")
    print(json.dumps({"universal": univ_stats,
                      "S4_stats_by_p": {k: v["S4_stats"] for k, v in per_prime.items()},
                        "S3_stats_by_p": {k: v["S3_stats"] for k, v in per_prime.items()},
                        "timings_sec": TIMINGS}, indent=2, default=str))


if __name__ == "__main__":
    main()
