#!/usr/bin/env python3
"""WP1 / G31-004 tasks 2-4: brute-force validation of S_3/S_4 against the
group law, cross-check against harness/semaev.py, symmetry + diagonal checks.

Run:  python3 -B validate.py      (-B: keep __pycache__ out of the read-only repo)

Ground truth conventions
------------------------
S_3(x1,x2,x3) = 0  over F_p  <=>  there exist y1,y2,y3 (algebraic over F_p;
they live in F_p or F_p^2 since x_i in F_p) with (x_i,y_i) on E and
P1+P2+P3 = O.  ("Semaev statement" / algebraic-closure truth.)
The weaker repo-style statement with y_i in F_p only is checked separately
and is expected to agree only on tuples where every x_i is the abscissa of
an F_p-point; on mixed tuples it legitimately disagrees (see report).
S_4(x1..x4) = 0  <=>  exist lifts with P1+P2+P3+P4 = O  (signs absorbed
into the choice of y_i).
"""
from __future__ import annotations

import itertools
import json
import os
import random
import resource
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Volumes/SSD990-2/crypto-autoresearcher"
sys.path.insert(0, HERE)
from ecfield import CurveK  # noqa: E402

CURVES = [(101, 1, 1), (127, 1, 1), (1009, 1, 1)]
SMALL = 101
SEED = 31004

RESULTS: dict = {"seed": SEED, "curves": CURVES}
T0 = time.perf_counter()


def stamp(name):
    el = time.perf_counter() - T0
    print(f"[t+{el:7.1f}s] {name}", flush=True)


# ------------------------------------------------------------ polynomials
def build_s3_expr(a: int, b: int):
    import sympy
    x1, x2, x3 = sympy.symbols("x1 x2 x3")
    return x1, x2, x3, ((x1 - x2) ** 2 * x3 ** 2
                        - 2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3
                        + ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)))


def build_s4_expr(a: int, b: int):
    import sympy
    from sympy import Poly, resultant
    x1, x2, x3, s3 = build_s3_expr(a, b)
    x4, t = sympy.symbols("x4 t")
    left = s3.subs(x3, t)
    right = s3.subs({x1: x3, x2: x4, x3: t}, simultaneous=True)
    s4 = sympy.expand(resultant(left, right, t))
    return (x1, x2, x3, x4), s3, s4


def load_or_build_s4(a: int, b: int, p: int):
    """Return (gens, {exp tuple: coeff mod p}) for S_4 over F_p."""
    fn = f"{HERE}/polynomials/s4_mod{p}.json"
    if os.path.exists(fn):
        with open(fn) as fh:
            d = json.load(fh)
        assert d["gens"] == ["x1", "x2", "x3", "x4"], d["gens"]
        return {tuple(e): int(c) % p for e, c in
                ((t["exp"], t["coeff"]) for t in d["terms"])}
    (x1, x2, x3, x4), _, s4 = build_s4_expr(a, b)
    from sympy import Poly
    P = Poly(s4, x1, x2, x3, x4, modulus=p)
    return {e: int(c) % p for e, c in P.terms()}


def s4_eval_closure(s4d, p):
    """eval(x1,x2,x3,x4) -> S_4 mod p  (pure python, powers table)."""
    terms = [(e, c) for e, c in s4d.items() if c]
    maxe = [max(e[i] for e, _ in terms) for i in range(4)]

    def ev(x1, x2, x3, x4):
        xs = (x1, x2, x3, x4)
        pw = [[1] for _ in range(4)]
        for i in range(4):
            for _ in range(maxe[i]):
                pw[i].append(pw[i][-1] * xs[i] % p)
        acc = 0
        for e, c in terms:
            acc += c * pw[0][e[0]] * pw[1][e[1]] * pw[2][e[2]] * pw[3][e[3]]
        return acc % p
    return ev


def s3_ABC(x1, x2, a, b, p):
    """Coefficients (in x3) of S_3(x1,x2,x3) mod p."""
    A = (x1 - x2) ** 2 % p
    B = (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b)) % p
    C = ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
    return A, B, C


# ------------------------------------------------------- brute-force truth
def enc(K, P):
    """Hashable encoding of E(K) point; -1 for O."""
    if P is None:
        return -1
    (x, y) = P
    assert x[1] == 0, "point x-coordinate not in F_p"
    return x[0] * K.p * K.p + y[0] * K.p + y[1]


def truth_ext_triples(C: CurveK):
    """truth[x1*p^2 + x2*p + x3] = 1 iff exist K-lifts with P1+P2+P3=O."""
    p = C.p
    pts = {x: [((x, 0), y) for y in C.lift_ys(x)] for x in range(p)}
    truth = bytearray(p * p * p)
    for x1 in range(p):
        for x2 in range(p):
            for P1 in pts[x1]:
                for P2 in pts[x2]:
                    S = C.add(P1, P2)
                    if S is not None and S[0][1] == 0:
                        truth[x1 * p * p + x2 * p + S[0][0]] = 1
    return truth


def truth_fp_triples(C: CurveK):
    """Same over F_p points only (indexed like truth_ext_triples)."""
    p = C.p
    pts = {x: [((x, 0), y) for y in C.lift_ys(x) if y[1] == 0] for x in range(p)}
    truth = bytearray(p * p * p)
    for x1 in range(p):
        if not pts[x1]:
            continue
        for x2 in range(p):
            if not pts[x2]:
                continue
            for P1 in pts[x1]:
                for P2 in pts[x2]:
                    S = C.add(P1, P2)
                    if S is not None:
                        truth[x1 * p * p + x2 * p + S[0][0]] = 1
    return truth


def pair_sums_fp(C: CurveK, xs):
    """dict (x1,x2) -> set of encoded F_p pair-sums P+Q (incl. O -> -1)."""
    pts = {x: [((x, 0), y) for y in C.lift_ys(x) if y[1] == 0] for x in xs}
    out = {}
    for x1 in xs:
        for x2 in xs:
            s = set()
            for P in pts[x1]:
                for Q in pts[x2]:
                    s.add(enc(C.K, C.add(P, Q)))
            out[(x1, x2)] = s
    return out


def ext4_truth(C: CurveK, tup):
    """exist K-lifts of (x1,x2,x3,x4) with P1+P2+P3+P4 = O."""
    pts = [[((x, 0), y) for y in C.lift_ys(x)] for x in tup]
    s12 = set()
    for P1 in pts[0]:
        for P2 in pts[1]:
            s12.add(C.add(P1, P2))
    s34 = set()
    for P3 in pts[2]:
        for P4 in pts[3]:
            s34.add(C.add(P3, P4))
    for S in s12:
        n = C.neg(S)
        if n in s34:
            return True
    return False


def fp4_truth(C: CurveK, tup):
    pts = [[((x, 0), y) for y in C.lift_ys(x) if y[1] == 0] for x in tup]
    if not all(pts):
        return None  # not all x_i are F_p abscissae
    s12 = {C.add(P1, P2) for P1 in pts[0] for P2 in pts[1]}
    s34 = {C.add(P3, P4) for P3 in pts[2] for P4 in pts[3]}
    return any(C.neg(S) in s34 for S in s12)


# ================================================================= main
def main():
    a, b = 1, 1
    rng = random.Random(SEED)

    # ---------------------------------------------------- task 2: S_3 census-validate
    for (p, ca, cb) in CURVES:
        C = CurveK(p, ca, cb)
        rec = {}
        s3d = {}
        # sparse dict from direct Horner coeffs: build dense A,B,C tables
        # zero pattern via Horner over all triples (p^3) or 20k random at p=1009
        t0 = time.perf_counter()
        onc = [C.on_base_x(x) for x in range(p)]
        ABC = [[s3_ABC(x1, x2, ca, cb, p) for x2 in range(p)] for x1 in range(p)]
        if p <= 127:
            zp = bytearray(p * p * p)
            for x1 in range(p):
                base = x1 * p * p
                for x2 in range(p):
                    A, B, Cc = ABC[x1][x2]
                    for x3 in range(p):
                        v = (A * x3 % p * x3 + B * x3 + Cc) % p
                        zp[base + x2 * p + x3] = 1 if v == 0 else 0
            mode = "exhaustive"
        else:
            mode = f"random20000"
        if p <= 127:
            truth_ext = truth_ext_triples(C)
            truth_fp = truth_fp_triples(C)
            mm_ext = [i for i in range(p ** 3) if zp[i] != truth_ext[i]]
            all_onc_mask = None
            mm_fp = []
            zeros_total = sum(zp)
            zeros_all_onc = 0
            zeros_mixed = 0
            zeros_mixed_not_fp = 0
            fp_true_total = 0
            ext_true_all_onc = 0
            fp_vs_ext_all_onc = 0
            for x1 in range(p):
                for x2 in range(p):
                    for x3 in range(p):
                        i = x1 * p * p + x2 * p + x3
                        all_onc = onc[x1] and onc[x2] and onc[x3]
                        if all_onc:
                            ext_true_all_onc += truth_ext[i]
                            fp_true_total += truth_fp[i]
                            if truth_fp[i] != truth_ext[i]:
                                fp_vs_ext_all_onc += 1
                            if zp[i] != truth_fp[i]:
                                mm_fp.append(i)
                        else:
                            if zp[i]:
                                zeros_mixed += 1
                                if not truth_ext[i]:
                                    zeros_mixed_not_fp += 1
                        zeros_all_onc += all_onc and zp[i]
            rec = {
                "p": p, "mode": mode, "tuples_checked": p ** 3,
                "S3_zeros_total": int(zeros_total),
                "S3_zeros_all_x_on_curve": int(zeros_all_onc),
                "S3_zeros_with_some_x_off_curve": int(zeros_mixed),
                "truth_ext_true_count": int(sum(truth_ext)),
                "truth_fp_true_count": int(sum(truth_fp)),
                "mismatches_vs_ext_truth": len(mm_ext),
                "mismatch_examples": [
                    (i // (p * p), i // p % p, i % p) for i in mm_ext[:10]],
                "mismatches_vs_fp_truth_on_all_onc_tuples": len(mm_fp),
                "fp_truth_vs_ext_truth_disagree_on_all_onc": fp_vs_ext_all_onc,
                "mixed_zeros_not_explained_by_ext_truth": zeros_mixed_not_fp,
                "seconds": round(time.perf_counter() - t0, 1),
            }
        else:  # p = 1009: random sample, ext truth per tuple
            mm = 0
            zero_count = 0
            examples1009 = []
            for _ in range(20000):
                tup = (rng.randrange(p), rng.randrange(p), rng.randrange(p))
                A, B, Cc = ABC[tup[0]][tup[1]]
                z = (A * tup[2] % p * tup[2] + B * tup[2] + Cc) % p == 0
                zero_count += z
                pts = [[((x, 0), y) for y in C.lift_ys(x)] for x in tup]
                tr = any(C.add(C.add(P1, P2), P3) is None
                         for P1 in pts[0] for P2 in pts[1] for P3 in pts[2])
                if z != tr:
                    mm += 1
                    if len(examples1009) < 10:
                        examples1009.append((tup, z, tr))
            rec = {"p": p, "mode": mode, "tuples_checked": 20000,
                   "S3_zeros_in_sample": zero_count,
                   "mismatches_vs_ext_truth": mm,
                   "examples": examples1009}
        RESULTS[f"S3_validation_p{p}"] = rec
        stamp(f"S3 validated at p={p}: {rec}")

    # ---------------------------------------------------- task 2b: S_4 at p=101
    p = SMALL
    C = CurveK(p, a, b)
    s4d = load_or_build_s4(a, b, p)
    ev4 = s4_eval_closure(s4d, p)
    stamp(f"S_4 mod {p} loaded: {len(s4d)} monomials")

    # (i) random 20000 tuples, full ext truth
    t0 = time.perf_counter()
    mm = 0
    examples = []
    zeros = 0
    for k in range(20000):
        tup = (rng.randrange(p), rng.randrange(p), rng.randrange(p), rng.randrange(p))
        z = ev4(*tup) == 0
        tr = ext4_truth(C, tup)
        zeros += z
        if z != tr:
            mm += 1
            if len(examples) < 10:
                examples.append((tup, z, tr))
    RESULTS["S4_random20k_p101"] = {
        "mismatches_vs_ext_truth": mm, "examples": examples[:10],
        "zeros_in_sample": zeros, "seconds": round(time.perf_counter() - t0, 1)}
    stamp(f"S4 random20k p=101: mismatches={mm}")

    # (i-b) forced-diagonal sample x1=x2 through brute force
    mm = 0
    for k in range(4000):
        x = rng.randrange(p)
        tup = (x, x, rng.randrange(p), rng.randrange(p))
        z = ev4(*tup) == 0
        tr = ext4_truth(C, tup)
        if z != tr:
            mm += 1
    RESULTS["S4_random4k_forced_diagonal_p101"] = {"mismatches_vs_ext_truth": mm}
    stamp(f"S4 diagonal-sample 4k: mismatches={mm}")

    # (ii) exhaustive over on-curve x-tuples via vectorized quadratic resultant
    t0 = time.perf_counter()
    xs = [x for x in range(p) if C.on_base_x(x)]
    n = len(xs)
    ps = pair_sums_fp(C, xs)
    idx_pairs = [(i, j) for i in range(n) for j in range(n)]
    npn = n * n
    # relation matrix R[i,j]: pairsum(i) ∩ pairsum(j) != empty
    R = np.zeros((npn, npn), dtype=bool)
    enc_to_i = {}
    for i, (u, v) in enumerate(idx_pairs):
        for e in ps[(xs[u], xs[v])]:
            enc_to_i.setdefault(e, []).append(i)
    for j, (u, v) in enumerate(idx_pairs):
        for e in ps[(xs[u], xs[v])]:
            ii = enc_to_i.get(e)
            if ii:
                R[np.array(ii), j] = True
    # S_4 values via quadratic-res resultant of the two S_3(t) quadratics
    Aa = np.empty(npn, dtype=np.int64)
    Bb = np.empty(npn, dtype=np.int64)
    Cc_ = np.empty(npn, dtype=np.int64)
    for i, (u, v) in enumerate(idx_pairs):
        Aa[i], Bb[i], Cc_[i] = s3_ABC(xs[u], xs[v], a, b, p)
    mism_total = 0
    chunk = 256
    for lo in range(0, npn, chunk):
        hi = min(lo + chunk, npn)
        A, B, C0 = Aa[lo:hi, None], Bb[lo:hi, None], Cc_[lo:hi, None]
        D, E, F = Aa[None, :], Bb[None, :], Cc_[None, :]
        V = ((A * F - C0 * D) % p) ** 2 - ((A * E - B * D) % p) * ((B * F - C0 * E) % p)
        Z = (V % p) == 0
        mism_total += int(np.count_nonzero(Z != R[lo:hi, :]))
    RESULTS["S4_exhaustive_oncurve_x_p101"] = {
        "x_on_curve_count": n, "tuples": npn * npn,
        "mismatches_group_vs_vanishing": mism_total,
        "note": "both sides restricted to tuples where every x_i is an "
                "F_p abscissa (mirrors repo tests/test_semaev_s4_exact.py)",
        "seconds": round(time.perf_counter() - t0, 1)}
    stamp(f"S4 exhaustive on-curve p=101 ({npn*npn} tuples): mismatches={mism_total}")

    # (iii) tie resultant-formula values to the census polynomial values
    s4direct_mm = 0
    for k in range(2000):
        x1, x2, x3, x4 = (xs[rng.randrange(n)] for _ in range(4))
        A1, B1, C1 = s3_ABC(x1, x2, a, b, p)
        A2, B2, C2 = s3_ABC(x3, x4, a, b, p)
        r = ((A1 * C2 - C1 * A2) % p) ** 2 - ((A1 * B2 - B1 * A2) % p) * ((B1 * C2 - C1 * B2) % p)
        s4direct_mm += (r % p != ev4(x1, x2, x3, x4))
    RESULTS["S4_resformula_vs_census_poly_p101"] = {
        "samples": 2000, "mismatches": s4direct_mm}
    stamp(f"S4 Res-formula vs census poly: mismatches={s4direct_mm}")

    # ---------------------------------------------------- task 3: harness cross-check
    sys.path.insert(0, REPO)
    import sympy
    from harness import semaev  # noqa: E402
    from harness.toycurve import EllipticCurve  # noqa: E402
    xh1, xh2, xh3 = semaev.x1, semaev.x2, semaev.x3
    xh4 = sympy.Symbol("x4")
    cross = {"note": "repo imported read-only under python -B (no bytecode written)"}

    # exact over-Z agreement: repo S_4 construction (a=b=1) vs our universal S_4
    repo_s4_expr = sympy.expand(semaev.s4_expr(a, b))
    repo_s4_Z = {e: int(c) for e, c in
                 sympy.Poly(repo_s4_expr, xh1, xh2, xh3, xh4).terms()}
    univ_fn = f"{HERE}/polynomials/s4_universal_Z.json"
    if os.path.exists(univ_fn):
        with open(univ_fn) as fh:
            d = json.load(fh)
        assert d["gens"] == ["x1", "x2", "x3", "x4", "a", "b"], d["gens"]
        spec: dict = {}
        for term in d["terms"]:
            e, c = tuple(term["exp"]), int(term["coeff"])
            key = e[:4]                      # a=1, b=1 specialization
            spec[key] = spec.get(key, 0) + c
        spec = {k: v for k, v in spec.items() if v}
        cross["S4_universal_specialized_equals_repo_Z_exact"] = (spec == repo_s4_Z)
    else:
        cross["S4_universal_specialized_equals_repo_Z_exact"] = "universal json missing"

    for (p, ca, cb) in CURVES:
        rec = {}
        mine3 = {e: int(c) % p for e, c in
                 sympy.Poly(build_s3_expr(ca, cb)[3], xh1, xh2, xh3, modulus=p).terms()}
        theirs3 = {e: int(c) % p for e, c in
                   sympy.Poly(semaev.s3_expr(ca, cb), xh1, xh2, xh3, modulus=p).terms()}
        rec["S3_coeff_dicts_identical_modp"] = mine3 == theirs3
        theirs4d = {e: int(c) % p for e, c in
                    sympy.Poly(repo_s4_expr, xh1, xh2, xh3, xh4, modulus=p).terms()}
        mine4d = load_or_build_s4(ca, cb, p)
        rec["S4_coeff_dicts_identical_modp"] = theirs4d == mine4d
        rec["S4_monomial_count_modp"] = sum(1 for c in theirs4d.values() if c)
        # zero-set agreement on 10^4 random tuples (repo evaluator vs ours)
        ABCp = [[s3_ABC(u, v, ca, cb, p) for v in range(p)] for u in range(p)]

        def s3_here(v1, v2, v3):
            A, B, C0 = ABCp[v1][v2]
            return (A * v3 % p * v3 + B * v3 + C0) % p

        ev4_theirs = s4_eval_closure(theirs4d, p)
        ev4_mine = s4_eval_closure(mine4d, p)
        n3 = n4 = t3 = t4 = 0
        for k in range(10000):
            v1, v2, v3, v4 = (rng.randrange(p) for _ in range(4))
            t3 += semaev.s3_eval(ca, cb, v1, v2, v3, p) == 0
            t4 += ev4_theirs(v1, v2, v3, v4) == 0
            n3 += (semaev.s3_eval(ca, cb, v1, v2, v3, p) == 0) == (s3_here(v1, v2, v3) == 0)
            n4 += (ev4_theirs(v1, v2, v3, v4) == 0) == (ev4_mine(v1, v2, v3, v4) == 0)
        rec["zero_agreement_S3_10k"] = f"{n3}/10000"
        rec["zero_agreement_S4_10k"] = f"{n4}/10000"
        rec["zero_rate_S3_sample"] = round(t3 / 10000, 4)
        rec["zero_rate_S4_sample"] = round(t4 / 10000, 4)
        cross[str(p)] = rec
        stamp(f"harness cross-check p={p}: {rec}")
    RESULTS["harness_crosscheck"] = cross

    # ---------------------------------------------------- task 4: symmetry & diagonal
    p = SMALL
    C = CurveK(p, a, b)
    s4d = load_or_build_s4(a, b, p)
    ev4 = s4_eval_closure(s4d, p)
    # (a) numeric full symmetry of S_4 (and S_3) at p=101
    mm4 = 0
    for k in range(500):
        v = [rng.randrange(p) for _ in range(4)]
        base = ev4(*v)
        for perm in itertools.permutations(range(4)):
            mm4 += (ev4(*[v[i] for i in perm]) != base)
    mm3 = 0
    ABCq = [[s3_ABC(x1, x2, a, b, p) for x2 in range(p)] for x1 in range(p)]

    def s3ev(v1, v2, v3):
        A, B, C0 = ABCq[v1][v2]
        return (A * v3 % p * v3 + B * v3 + C0) % p

    for k in range(500):
        v = [rng.randrange(p) for _ in range(3)]
        base = s3ev(*v)
        for perm in itertools.permutations(range(3)):
            mm3 += (s3ev(*[v[i] for i in perm]) != base)
    RESULTS["symmetry_numeric_p101"] = {
        "S4_perm_violations": mm4, "S3_perm_violations": mm3,
        "note": "exact Z-symmetry also checked in census.py (24/6 perms)"}
    stamp(f"symmetry numeric: S3 viol={mm3} S4 viol={mm4}")

    # (b) S3 diagonal <-> duplication
    diag = {"checked_x": 0, "root_matches_doubling": 0,
            "torsion_x_constant_nonzero": 0, "row_truth_agrees": 0,
            "failures": []}
    truth_ext = truth_ext_triples(C)
    for x in range(p):
        fx = C.f(x)
        A, B, C0 = s3_ABC(x, x, a, b, p)
        assert A == 0
        diag["checked_x"] += 1
        if fx != 0:
            t0_ = (-pow(B, -1, p) * C0) % p
            xd = (pow(3 * x * x + a, 2, p) * pow(4 * fx, -1, p) - 2 * x) % p
            ok = (t0_ == xd)
            diag["root_matches_doubling"] += ok
            row = [truth_ext[x * p * p + x * p + z] for z in range(p)]
            ok2 = (row[t0_] == 1 and sum(row) == 1)
            diag["row_truth_agrees"] += ok2
            if not (ok and ok2):
                diag["failures"].append(("nontorsion", x, t0_, xd, sum(row)))
        else:
            nonzero = all(s3ev(x, x, z) != 0 for z in range(p))
            diag["torsion_x_constant_nonzero"] += nonzero
            if not nonzero:
                diag["failures"].append(("torsion", x))
    RESULTS["S3_diagonal_duplication_p101"] = diag
    stamp(f"S3 diagonal: {diag['root_matches_doubling']}/{diag['checked_x']}")

    # (c) S4 diagonal identity.  Because the Sylvester/resultant construction
    # treats both S_3 factors as formal quadratics in t, setting x1=x2 (which
    # kills the leading coefficient (x1-x2)^2 of the first factor) introduces
    # the extra factor D = (u-v)^2 (leading coeff of the second factor):
    #   S4(x,x,u,v) = (4 f(x))^2 * (u-v)^2 * S3(u, v, x([2]P))
    # (verified as an identity of polynomial *values*; zero sets agree with
    # the group statement since both extra factors are harmless squares).
    mm = 0
    tried = 0
    for k in range(2000):
        x = rng.randrange(p)
        fx = C.f(x)
        if fx == 0:
            continue
        tried += 1
        xd = (pow(3 * x * x + a, 2, p) * pow(4 * fx, -1, p) - 2 * x) % p
        u, v = rng.randrange(p), rng.randrange(p)
        lhs = ev4(x, x, u, v)
        rhs = pow(4 * fx, 2, p) * pow(u - v, 2, p) * s3ev(u, v, xd) % p
        mm += (lhs != rhs)
    RESULTS["S4_diagonal_identity_p101"] = {
        "statement": "S4(x,x,u,v) = (4f(x))^2 * (u-v)^2 * S3(u,v,x([2]P))",
        "samples": tried, "mismatches": mm}
    stamp(f"S4 diagonal identity: mismatches={mm}/{tried}")

    # ---- cross-check own F_p arithmetic vs repo EllipticCurve (defense) ----
    mm = 0
    E = EllipticCurve(p, a, b)
    pts = [(x, yr[0]) for x in range(p) if C.on_base_x(x)
           for yr in C.lift_ys(x) if yr[1] == 0]
    for k in range(3000):
        P = pts[rng.randrange(len(pts))]
        Q = pts[rng.randrange(len(pts))]
        mine = C.add(((P[0], 0), (P[1], 0)), ((Q[0], 0), (Q[1], 0)))
        mine = None if mine is None else (mine[0][0], mine[1][0])
        theirs = E.add(P, Q)
        mm += (mine != theirs)
    RESULTS["own_arith_vs_repo_toycurve"] = {"samples": 3000, "mismatches": mm}
    stamp(f"arith cross-check vs harness.toycurve: {mm}")

    RESULTS["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    RESULTS["total_seconds"] = round(time.perf_counter() - T0, 1)
    with open(f"{HERE}/results/validation_stats.json", "w") as fh:
        json.dump(RESULTS, fh, indent=2, default=str)
    stamp("wrote results/validation_stats.json")


if __name__ == "__main__":
    main()
