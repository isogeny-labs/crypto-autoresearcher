"""Known-answer tests for the EXP-MONO-1a1be2 toolchain (TASK-20261029-a97206).

Rules these tests follow (card constraints IM-2, IM-3, IM-4, IM-5):
  * Cells are KAT cells disjoint from every contract cell: F_Q with q in {5, 13} at degree n <= 7, F_Q with
    q = q'_n (the least prime above the arm-C q_n) at n = 2..7 (DEC-20261105-f0b7c7 F-1, IM-3 widened), and
    prime fields (n = 1) with q not a contract (q, n) pair. No contract cell is computed.
  * Every counter test compares the optimised (kernel) counter with a naive enumeration written directly
    from the definition on the same cell. No test asserts an identity between different conventions, a
    predicted ratio, a split frequency, or any value from the specification's predictions.
  * Raw outputs are recorded: set KAT_LOG_PATH to write them (as text) to a JSON file at session end.

Run:  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider experiments/EXP-MONO-1a1be2/code/tests/test_kat.py
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import shutil
import sys
import tempfile
from collections import Counter

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, CODE)

import counters  # noqa: E402
import curves  # noqa: E402
import fqn  # noqa: E402
import launcher  # noqa: E402
import make_trial_plan as mtp  # noqa: E402
import semaev  # noqa: E402
from curves import Curve, WCurve  # noqa: E402
from fqn import FQ, FQ2  # noqa: E402

LOG: list[dict] = []


def record(kat_id: str, cell: str, output) -> None:
    LOG.append({"kat_id": kat_id, "cell": cell,
                "output_text": output if isinstance(output, str) else json.dumps(output, sort_keys=True, default=str)})


@pytest.fixture(scope="session", autouse=True)
def _write_log():
    yield
    path = os.environ.get("KAT_LOG_PATH")
    if path:
        with open(path, "w") as fh:
            json.dump({"task": "TASK-20261029-a97206 (extended by TASK-20261105-ac5ad6)", "note": "raw KAT outputs as text; KAT cells are disjoint from "
                       "every contract cell; no contract cell computed; nothing here is a run",
                       "entries": LOG}, fh, indent=1)
            fh.write("\n")


@pytest.fixture(scope="session")
def kernel():
    tmp = tempfile.mkdtemp(prefix="mono1a1be2-kat-kernel-")
    k = counters.Kernel(counters.build_kernel(tmp))
    record("K1-build", "-", {"compiler": counters.compiler_record(), "so_sha256": counters.file_sha256(k.so_path),
                             "kernel_c_sha256": counters.file_sha256(os.path.join(CODE, "kernel.c"))})
    yield k
    shutil.rmtree(tmp, ignore_errors=True)


# KAT cells. Field/curve KATs: q in {5, 13}, n <= 3, plus prime fields. None is a contract (q, n) pair.
EXT_FIELDS = [(5, 2), (5, 3), (13, 2), (13, 3)]
PRIME_FIELDS = [7, 11, 17, 19, 23, 101, 1009]
ALL_FIELDS = EXT_FIELDS + [(p, 1) for p in PRIME_FIELDS]


def fld(q, n):
    return FQ(q, n)


def kat_curve(q, n, tag):
    F = fld(q, n)
    E, info = curves.generate_curve(F, f"kat|{tag}|{q}|{n}")
    return F, E, info


def rng_for(tag):
    return curves.make_rng("kat|rng|" + tag)


def disjoint_from_contract(q, n):
    return (q, n) not in mtp.contract_cells_qn()


# =============================================================================== K: kernel / disjointness
def test_kat_cells_disjoint_from_contract():
    for q, n in ALL_FIELDS:
        assert disjoint_from_contract(q, n), (q, n)
        if n > 1:
            assert q in (5, 13) and n <= 3
    record("K0-disjoint", "-", {"kat_fields": ALL_FIELDS, "contract_pairs": sorted(mtp.contract_cells_qn())})


def test_no_binary_in_code_dir():
    found = [f for f in os.listdir(CODE) if f.endswith((".so", ".o", ".dll", ".dylib"))]
    assert not found


# =============================================================================== F: field
def brute_least_irreducible(q, n):
    """Definition: first monic degree-n polynomial (lexicographic by constant term upward) with no factor of
    degree 1..n//2, found by trial division by every monic polynomial of those degrees."""
    def polymod(a, b):  # a, b low-first, b monic
        a = list(a)
        while len(a) >= len(b):
            c = a[-1]
            if c:
                for j in range(len(b)):
                    a[len(a) - len(b) + j] = (a[len(a) - len(b) + j] - c * b[j]) % q
            a.pop()
        return a
    for c in itertools.product(range(q), repeat=n):
        g = list(c) + [1]
        ok = True
        for d in range(1, n // 2 + 1):
            for h in itertools.product(range(q), repeat=d):
                if not any(polymod(g, list(h) + [1])):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return tuple(c)


@pytest.mark.parametrize("q,n", EXT_FIELDS)
def test_least_irreducible_matches_definition(q, n):
    got = fqn.least_irreducible(q, n)
    want = brute_least_irreducible(q, n)
    assert got == want
    record("F1-least-irreducible", f"q={q},n={n}", {"g": got})


@pytest.mark.parametrize("q,n", ALL_FIELDS)
def test_field_arithmetic(q, n, kernel):
    F = fld(q, n)
    rng = rng_for(f"field{q}{n}")
    els = [F.random_element(rng) for _ in range(40)]
    squares = {F.mul(e, e) for e in F.elements()} if F.Q <= 2197 else None
    for a, b, c in zip(els, els[1:], els[2:]):
        assert F.mul(a, F.mul(b, c)) == F.mul(F.mul(a, b), c)
        assert F.mul(a, F.add(b, c)) == F.add(F.mul(a, b), F.mul(a, c))
        assert F.mul(a, b) == F.mul(b, a)
        assert F.pow(a, 5) == F.mul(F.mul(F.mul(F.mul(a, a), a), a), a)
        assert F.frobenius(a) == F.pow(a, q)
        if not F.is_zero(a):
            assert F.inv(a) == F.inv_fermat(a)
            assert F.mul(a, F.inv(a)) == F.one
            assert F.pow(a, F.Q - 1) == F.one
        r = F.sqrt(F.mul(a, a))
        assert r is not None and F.mul(r, r) == F.mul(a, a)
        if squares is not None:
            assert (F.chi(a) >= 0) == (a in squares)
    if squares is not None:
        # chi from definition: +1 for nonzero squares
        for e in F.elements():
            want = 0 if F.is_zero(e) else (1 if e in squares else -1)
            assert F.chi(e) == want
    record("F2-field-arithmetic", f"q={q},n={n}", {"checked_elements": len(els), "g": F.g})


@pytest.mark.parametrize("q,n", ALL_FIELDS)
def test_kernel_field_ops_match_python(q, n, kernel):
    F, E, _ = kat_curve(q, n, "kfield")
    rng = rng_for(f"kfield{q}{n}")
    for _ in range(60):
        a, b = F.random_element(rng), F.random_element(rng)
        assert kernel.mul(E, a, b) == F.mul(a, b)
        if not F.is_zero(a):
            assert kernel.inv(E, a) == F.inv(a)
            assert kernel.inv(E, a, ref=True) == F.inv(a)
    record("F3-kernel-field", f"q={q},n={n}", {"pairs": 60})


@pytest.mark.parametrize("q,n", ALL_FIELDS)
def test_quadratic_extension(q, n):
    F = fld(q, n)
    F2 = FQ2(F)
    rng = rng_for(f"f2{q}{n}")
    assert F.chi(F2.d) == -1
    for _ in range(30):
        a = (F.random_element(rng), F.random_element(rng))
        b = (F.random_element(rng), F.random_element(rng))
        assert F2.mul(a, b) == F2.mul(b, a)
        if not F2.is_zero(a):
            assert F2.mul(a, F2.inv(a)) == F2.one
        y2 = F.random_element(rng)
        y = F2.lift_y(y2)
        assert F2.mul(y, y) == F2.embed(y2)


# =============================================================================== C: seeds, curves, counting
def test_seed_rule():
    for s in ["f15270|A|2|61|0", "f15270|C|7|23|2", "f15270|base|A-n2-q61-c0|random|0"]:
        digest = hashlib.sha256(s.encode("utf-8")).digest()
        want = int.from_bytes(digest[:16], "big")
        assert curves.seed_int(s) == want
        g1 = curves.make_rng(s)
        g2 = np.random.Generator(np.random.PCG64(want))
        assert g1.integers(0, 10 ** 9, size=8).tolist() == g2.integers(0, 10 ** 9, size=8).tolist()
        assert curves.make_rng(s).integers(0, 97, size=5).tolist() == curves.make_rng(s).integers(0, 97, size=5).tolist()
    record("C1-seed-rule", "-", {s: str(curves.seed_int(s)) for s in ["f15270|A|2|61|0", "f15270|C|7|23|2"]})


def test_plan_seed_strings():
    assert mtp.curve_seed("A", 2, 61, 0) == "f15270|A|2|61|0"
    assert mtp.base_seed("A-n2-q61-c0", "twin", 1) == "f15270|base|A-n2-q61-c0|twin|1"
    assert mtp.tuple_seed("B1-n2-q251-c0", 0) == "f15270|tuples|B1-n2-q251-c0|0"
    assert mtp.target_seed("C-n2-q32771-c0") == "f15270|targets|C-n2-q32771-c0"


@pytest.mark.parametrize("q,n", EXT_FIELDS)
def test_curve_selection_rules(q, n):
    F = fld(q, n)
    # explicit rejects
    zero = F.zero
    one = F.one
    assert Curve(F, zero, one).j_in_Fq()                       # a = 0: j = 0
    assert Curve(F, one, zero).j_in_Fq()                       # b = 0: j = 1728
    sing = Curve(F, F.neg(F.from_int(3)), F.from_int(2))       # x^3 - 3x + 2 = (x-1)^2 (x+2)
    assert sing.is_singular()
    for i in range(30):
        E, info = curves.generate_curve(F, f"kat|sel|{q}|{n}|{i}")
        assert not E.is_singular() and not E.j_in_Fq()
        # j in F_q iff j^q = j (independent test)
        j = E.j_invariant()
        assert F.pow(j, q) != j
    # a generated sequence includes at least one rejected attempt across seeds is not asserted (data dependent)


@pytest.mark.parametrize("p", PRIME_FIELDS)
def test_curve_selection_prime_fields(p):
    F = fld(p, 1)
    for i in range(10):
        E, info = curves.generate_curve(F, f"kat|selp|{p}|{i}")
        assert not E.is_singular()
        assert E.j_in_Fq()          # vacuous at n = 1: documented, only singular rejected


@pytest.mark.parametrize("q,n", EXT_FIELDS)
def test_group_law(q, n):
    F, E, _ = kat_curve(q, n, "grp")
    rng = rng_for(f"grp{q}{n}")
    pts = []
    while len(pts) < 12:
        x = F.random_element(rng)
        P = E.lift(x)
        if P is not None:
            pts.append(P)
    for P in pts:
        assert E.on_curve(P)
        assert E.add(P, E.neg(P)) is None
        assert E.add(P, None) == P
    for P, R, S in zip(pts, pts[1:], pts[2:]):
        assert E.on_curve(E.add(P, R))
        assert E.add(P, R) == E.add(R, P)
        assert E.add(E.add(P, R), S) == E.add(P, E.add(R, S))
        assert E.mul(5, P) == E.add(E.add(E.add(E.add(P, P), P), P), P)
    N = E.count_points_naive()
    for P in pts[:4]:
        assert E.mul(N, P) is None            # Lagrange: N P = O


def naive_points(E):
    """All affine points by the definition (x, y) with y^2 = f(x), plus nothing else."""
    F = E.F
    out = []
    for x in F.elements():
        fx = E.f(x)
        for y in F.elements():
            if F.mul(y, y) == fx:
                out.append((x, y))
    return out


@pytest.mark.parametrize("q,n", [(5, 2), (5, 3), (13, 2), (7, 1), (11, 1), (23, 1)])
def test_point_counting_all_methods_and_definition(q, n, kernel):
    for i in range(3):
        F, E, _ = kat_curve(q, n, f"cnt{i}")
        pts = naive_points(E)                                   # Q^2 pairs from the definition
        N_def = len(pts) + 1
        assert E.count_points_naive() == N_def
        assert E.count_points_chi() == N_def
        assert kernel.count_points(E) == N_def
        assert E.count_points_bsgs()[0] == N_def
        assert abs(N_def - (F.Q + 1)) <= 2 * math.isqrt(F.Q) + 2
        Nk, mask = kernel.valid_mask(E)
        assert Nk == N_def and int(np.count_nonzero(mask & 1)) == N_def
        # target index: kernel equals the Python formula on every point
        assert kernel.point_index(E, None) == counters.target_index(F, None) == 2 * F.Q
        idxs = set()
        for P in pts[:200]:
            ki = kernel.point_index(E, P)
            assert ki == counters.target_index(F, P)
            assert mask[ki] & 1
            idxs.add(ki)
        record("C3-point-count", f"q={q},n={n},curve={i}", {"a": E.a, "b": E.b, "N": N_def})


def _twenty_random_curves():
    """20 curves with Q < 2^27 outside the contract cells: 8 prime fields and 12 over q in {5, 13}, n in {2, 3}."""
    cells = []
    for p in [1009, 10007, 65537, 100003, 1000003, 4000037, 16000057, 100000007]:
        cells.append((fqn.next_prime_above(p - 1), 1))
    for q, n in EXT_FIELDS:
        cells += [(q, n)] * 3
    return cells


def test_point_counting_twenty_random_curves_exhaustive_vs_bsgs(kernel):
    cells = _twenty_random_curves()
    assert len(cells) == 20
    rows = []
    for k, (q, n) in enumerate(cells):
        F = fld(q, n)
        assert F.Q < 2 ** 27 and disjoint_from_contract(q, n)
        E, _ = curves.generate_curve(F, f"kat|twenty|{k}|{q}|{n}")
        N_exh = kernel.count_points(E)
        N_bsgs, used = E.count_points_bsgs()
        assert N_exh == N_bsgs
        rows.append({"q": q, "n": n, "a": E.a, "b": E.b, "N_exhaustive": N_exh, "N_bsgs": N_bsgs, "bsgs_point_pairs": used})
    record("C4-twenty-random-curves", "Q<2^27 outside contract", rows)


def test_bsgs_beyond_exhaustive_range_agrees_with_independent_count(kernel):
    """A prime field above 2^27 (not a contract cell): BSGS against the quadratic-character sum done in the
    compiled kernel through the exhaustive routine is too slow in Python, so cross-check with the group
    order property instead: the BSGS value N satisfies N P = O for random P and lies in the Hasse interval."""
    p = fqn.next_prime_above(2 ** 28)
    F = fld(p, 1)
    E, _ = curves.generate_curve(F, "kat|bigp")
    N, used = E.count_points_bsgs()
    rng = rng_for("bigp")
    assert abs(N - (p + 1)) <= 2 * math.isqrt(p) + 1
    k = 0
    while k < 5:
        P = E.lift(F.random_element(rng))
        if P is not None:
            assert E.mul(N, P) is None
            k += 1
    # and the exhaustive routine (kernel) agrees; p ~ 2.7e8 is a few seconds of C
    assert kernel.count_points(E) == N
    record("C5-bsgs-above-2^27", f"p={p}", {"N": N, "point_pairs": used})


@pytest.mark.parametrize("q,n", [(5, 2), (13, 2), (5, 3), (13, 3), (11, 1), (23, 1)])
def test_factor_base_and_torsion_from_definition(q, n):
    F, E, _ = kat_curve(q, n, "fb")
    pts = naive_points(E) if F.Q <= 2197 else None
    D, X, t2 = E.factor_base()
    if pts is None:
        pts = []
        for xv in range(q):
            x = F.from_int(xv)
            for y in F.elements():
                if F.mul(y, y) == E.f(x):
                    pts.append((x, y))
    line = [P for P in pts if F.is_scalar(P[0])]
    assert sorted(D) == sorted(line)
    assert len(D) == len(line)
    assert t2 == sum(1 for P in line if F.is_zero(P[1]))
    assert sorted(X) == sorted({P[0] for P in line})
    # two-torsion over F_Q from the definition
    roots = sorted((x for x in F.elements() if F.is_zero(E.f(x))), key=F.to_code)
    assert E.two_torsion_roots() == roots
    assert len(D) == t2 + 2 * (len(X) - t2)
    record("C6-factor-base", f"q={q},n={n}", {"B": len(D), "t2": t2, "size_X": len(X), "r2": len(roots)})


# =============================================================================== P: polynomials, S_{n+1}
def test_polynomial_tools():
    F = fld(13, 2)
    rng = rng_for("poly")
    # f = (x - r1)(x - r2)(x^2 + c)(irreducible quadratic) with known factors
    rts = [F.from_code(5), F.from_code(77), F.from_code(100)]
    f = [F.one]
    for r in rts:
        f = fqn.pmul(F, f, [F.neg(r), F.one])
    assert fqn.roots(F, f) == sorted(rts, key=F.to_code)
    # an irreducible quadratic over F_{13^2}: x^2 - nonsquare-of-F_Q-in-the-quadratic-sense: x^2 - d with d nonsquare
    d = F.nonsquare()
    irr = [F.neg(d), F.zero, F.one]
    g = fqn.pmul(F, f, irr)
    assert fqn.is_squarefree(F, g)
    fac = fqn.ddf(F, g)
    assert [(dd, len(h) - 1) for dd, h in fac] == [(1, 3), (2, 2)]
    assert not fqn.splits_completely_ddf(F, g) and not fqn.splits_completely_xq(F, g)
    assert fqn.splits_completely_ddf(F, f) and fqn.splits_completely_xq(F, f)
    assert fqn.roots(F, g) == sorted(rts, key=F.to_code)
    assert not fqn.is_squarefree(F, fqn.pmul(F, g, [F.neg(rts[0]), F.one]))
    # roots by brute force on random polynomials
    for _ in range(10):
        poly = [F.random_element(rng) for _ in range(5)]
        fqn.ptrim(F, poly)
        if len(poly) < 2:
            continue
        brute = sorted((x for x in F.elements() if F.is_zero(fqn.peval(F, poly, x))), key=F.to_code)
        assert fqn.roots(F, poly) == brute
    record("P1-polynomial-tools", "F_{13^2}", {"known_factorisation": "3 linear + 1 irreducible quadratic"})


def _random_points(F, E, rng, k):
    pts = []
    while len(pts) < k:
        P = E.lift(F.random_element(rng))
        if P is None or F.is_zero(P[1]):
            continue
        if rng.integers(0, 2):
            P = E.neg(P)
        pts.append(P)
    return pts


SEMAEV_FIELDS = [(13, 2), (5, 3), (13, 3), (101, 1), (1009, 1)]


SEMAEV_CASES = [(q, n, L) for (q, n) in SEMAEV_FIELDS for L in (2, 3, 4, 5) if not ((q, n) == (13, 3) and L >= 4)]
SEMAEV_CASES += [(5, 4, 4), (13, 4, 4), (5, 5, 5)]          # KX-3: S_{n+1} defining property at k = n


@pytest.mark.parametrize("q,n,tuple_len", SEMAEV_CASES)
def test_semaev_defining_property_200_tuples(q, n, tuple_len):
    """S_{k+1}(x(P_1), ..., x(P_k), x(P_1 + ... + P_k)) = 0 for 200 random point tuples (sum != O).
    (13, 3) is run for tuple lengths 2 and 3 only; lengths 4 and 5 are covered by the other fields."""
    F, E, _ = kat_curve(q, n, "sem")
    assert F.Q >= 2 ** tuple_len + 2           # enough points to interpolate
    rng = rng_for(f"semdp{q}{n}{tuple_len}")
    done = 0
    while done < 200:
        P = _random_points(F, E, rng, tuple_len)
        S = None
        for R in P:
            S = E.add(S, R)
        if S is None:
            continue
        xs = [R[0] for R in P]
        val = semaev.semaev_eval(F, E.a, E.b, xs, S[0])
        assert F.is_zero(val), (q, n, tuple_len)
        done += 1
    record("S1-defining-property", f"q={q},n={n},tuple_len={tuple_len}", {"tuples": done})


@pytest.mark.parametrize("q,n", [(13, 2), (5, 3), (101, 1)])
@pytest.mark.parametrize("tuple_len", [2, 3, 4, 5])
def test_semaev_roots_agree_with_group_law_signed_sums(q, n, tuple_len):
    F, E, _ = kat_curve(q, n, "sem2")
    assert F.Q >= 2 ** tuple_len + 2
    rng = rng_for(f"semgl{q}{n}{tuple_len}")
    F2 = FQ2(F)
    k = 0
    agree = 0
    while k < 200:
        xs = [F.random_element(rng) for _ in range(tuple_len)]
        if any(F.is_zero(E.f(x)) for x in xs):
            continue
        res = semaev.analyse_fibre(F, E, xs)
        roots_gl, ninf = semaev.roots_via_group_law(F, E, xs, F2)
        if res["squarefree"] and res["full_degree"]:
            assert res["roots_Fq"] == roots_gl, (xs,)
            agree += 1
            # the two completeness tests agree
            assert res["split_completely"] == res["split_check_xq"]
            # number of distinct x of the signed sums over F_{Q^2} equals the degree for generic tuples
        k += 1
    record("S2-roots-vs-group-law", f"q={q},n={n},tuple_len={tuple_len}", {"tuples": k, "generic_compared": agree})


def test_semaev_s3_matches_definition_and_known_answer():
    """S_3 as a polynomial identity: vanishes on x-triples of points summing to O, checked exhaustively on a
    small curve; and the n = 2 resultant recursion is S_3 itself (formal degree 2)."""
    F, E, _ = kat_curve(13, 2, "s3")
    D, X, t2 = E.factor_base()
    pts = naive_points(E)
    zero_triples = set()
    for P in pts[:40]:
        for R in pts[:40]:
            S = E.add(P, R)
            if S is None:
                continue
            T = E.neg(S)
            assert F.is_zero(semaev.s3_eval(F, E.a, E.b, P[0], R[0], T[0]))
            zero_triples.add((P[0], R[0], T[0]))
    # converse on a sample: if S_3(x1,x2,x3)=0 then some sign choice sums to O (exhaustive over x3 for fixed x1,x2)
    x1, x2 = pts[3][0], pts[7][0]
    P1, P2 = E.lift(x1), E.lift(x2)
    sums = set()
    for s1, s2 in itertools.product((1, -1), repeat=2):
        S = E.add(P1 if s1 == 1 else E.neg(P1), P2 if s2 == 1 else E.neg(P2))
        if S is not None:
            sums.add(S[0])
    roots = {x3 for x3 in F.elements() if F.is_zero(semaev.s3_eval(F, E.a, E.b, x1, x2, x3))}
    assert roots == sums
    poly = semaev.semaev_poly(F, E.a, E.b, [x1, x2])
    assert poly == semaev.s3_quad(F, E.a, E.b, x1, x2)
    record("S3-s3-definition", "q=13,n=2", {"x1": x1, "x2": x2, "roots": sorted(F.to_code(r) for r in roots)})


def test_semaev_recursion_matches_nested_definition():
    """S_4 two ways over a small field: the interpolating recursion against the resultant of S_3(x1,x2,X) and
    S_3(X,x3,T) computed by an independent Sylvester determinant over F_Q[T] evaluated at every T."""
    F, E, _ = kat_curve(13, 2, "s4")
    rng = rng_for("s4")

    def sylvester_res(A, B):
        """Resultant of A, B (low-first coefficient lists with formal degrees len-1) by determinant."""
        m, n = len(A) - 1, len(B) - 1
        size = m + n
        M = [[F.zero] * size for _ in range(size)]
        for i in range(n):
            for j, c in enumerate(reversed(A)):
                M[i][i + j] = c
        for i in range(m):
            for j, c in enumerate(reversed(B)):
                M[n + i][i + j] = c
        det = F.one
        for col in range(size):
            piv = next((r for r in range(col, size) if not F.is_zero(M[r][col])), None)
            if piv is None:
                return F.zero
            if piv != col:
                M[col], M[piv] = M[piv], M[col]
                det = F.neg(det)
            det = F.mul(det, M[col][col])
            inv = F.inv(M[col][col])
            for r in range(col + 1, size):
                if not F.is_zero(M[r][col]):
                    f = F.mul(M[r][col], inv)
                    for c in range(col, size):
                        M[r][c] = F.sub(M[r][c], F.mul(f, M[col][c]))
        return det

    for _ in range(6):
        x1, x2, x3 = (F.random_element(rng) for _ in range(3))
        poly = semaev.semaev_poly(F, E.a, E.b, [x1, x2, x3])        # S_4(x1,x2,x3,T)
        A = semaev.s3_quad(F, E.a, E.b, x1, x2)                      # S_3(x1,x2,X) in X
        for T in [F.from_code(c) for c in range(0, 40, 3)]:
            Bq = semaev.s3_quad(F, E.a, E.b, x3, T)                  # S_3(x3,T,X) in X (symmetric)
            assert sylvester_res(A, Bq) == fqn.peval(F, poly, T)
    record("S4-recursion-vs-sylvester", "q=13,n=2", {"tuples": 6, "T_points_each": 14})


# =============================================================================== E: counters vs naive
def pt_sum(E, pts):
    S = None
    for P in pts:
        S = E.add(S, P)
    return S


def naive_TA(E, D, m):
    c = Counter()
    for tup in itertools.product(D, repeat=m):
        c[counters.target_index(E.F, pt_sum(E, tup))] += 1
    return c


def naive_TM(E, D, m):
    c = Counter()
    for tup in itertools.combinations_with_replacement(D, m):
        c[counters.target_index(E.F, pt_sum(E, tup))] += 1
    return c


def naive_TS(E, lifts, m):
    c = Counter()
    for xt in itertools.product(lifts, repeat=m):
        for eps in itertools.product((1, -1), repeat=m):
            pts = [P if e == 1 else E.neg(P) for P, e in zip(xt, eps)]
            c[counters.target_index(E.F, pt_sum(E, pts))] += 1
    return c


def naive_TX_TMre(E, D, m):
    """x-multisets over the distinct x of D; for each, all distinct point multisets over it (each x
    contributes any of the points of D with that x); c(R) = number of those multisets with sum R."""
    F = E.F
    by_x = {}
    for P in D:
        by_x.setdefault(P[0], []).append(P)
    xs = sorted(by_x, key=F.to_code)
    TX, TMre = Counter(), Counter()
    for xm in itertools.combinations_with_replacement(xs, m):
        choices = [by_x[x] for x in xm]
        multisets = {tuple(sorted(c, key=lambda P: (F.to_code(P[0]), F.to_code(P[1]))))
                     for c in itertools.product(*choices)}
        cR = Counter(counters.target_index(F, pt_sum(E, ms)) for ms in multisets)
        for R, c in cR.items():
            TX[R] += 1
            TMre[R] += c
    return TX, TMre


def arr_to_counter(arr):
    nz = np.nonzero(arr)[0]
    return Counter({int(i): int(arr[i]) for i in nz})


def naive_S_and_masks(E, D, m, N):
    F = E.F
    S = set()
    for mp in range(m - 2, -1, -2):
        for ms in itertools.combinations_with_replacement(D, mp):
            S.add(counters.target_index(F, pt_sum(E, ms)))
    return S


EXH_CELLS = [  # (q, n, m): KAT cells only
    (13, 2, 2), (13, 2, 3), (5, 2, 4), (5, 3, 2), (5, 3, 3), (13, 3, 2), (13, 3, 3), (7, 1, 4), (11, 1, 3), (7, 1, 5),
    # KX-3 widening (TASK-20261105-ac5ad6): (5,4,m=2..4), (13,4,m=2), (5,5,m=2..5)
    (5, 4, 2), (5, 4, 3), (5, 4, 4), (13, 4, 2), (5, 5, 2), (5, 5, 3), (5, 5, 4), (5, 5, 5),
]


@pytest.mark.parametrize("q,n,m", EXH_CELLS)
@pytest.mark.parametrize("base_kind", ["line", "random", "twin"])
def test_exhaustive_counters_match_naive_enumeration(q, n, m, base_kind, kernel):
    F, E, _ = kat_curve(q, n, "exh")
    N, vmask = kernel.valid_mask(E)
    D, X, t2 = E.factor_base()
    rng = rng_for(f"exh{q}{n}{m}{base_kind}")
    if base_kind == "random":
        base = counters.matched_random_base(E, len(D), t2, rng)
    elif base_kind == "twin":
        base = counters.twin_base(E, len(D), t2, rng)
    else:
        base = D
    lifts = counters.x_lifts(F, base)
    res = counters.exhaustive_cell(kernel, E, base, lifts, m, N, vmask, recount=True, keep=True)
    arr = res["arrays"]
    assert arr_to_counter(arr["A"]) == naive_TA(E, base, m)
    assert arr_to_counter(arr["M"]) == naive_TM(E, base, m)
    assert arr_to_counter(arr["S"]) == naive_TS(E, lifts, m)
    TXn, TMren = naive_TX_TMre(E, base, m)
    assert arr_to_counter(arr["X"]) == TXn
    assert arr_to_counter(arr["Mre"]) == TMren
    # the weighted helper arrays equal their own naive definitions
    cw = Counter()
    for tup in itertools.product(base, repeat=m):
        j = sum(1 for P in tup if F.is_zero(P[1]))
        cw[counters.target_index(F, pt_sum(E, tup))] += 2 ** j
    assert arr_to_counter(arr["A2"]) == cw
    cm = Counter()
    for tup in itertools.combinations_with_replacement(range(len(base)), m):
        w = math.factorial(m)
        for _, grp in itertools.groupby(tup):
            w //= math.factorial(len(list(grp)))
        cm[counters.target_index(F, pt_sum(E, [base[i] for i in tup]))] += w
    assert arr_to_counter(arr["MW"]) == cm
    # S set, special targets, generic targets against the definition
    Sset = naive_S_and_masks(E, base, m, N)
    assert res["S_size"] == len(Sset)
    mask = res["mask"]
    special = {i for i in range(len(mask)) if (mask[i] & 3) == 3}
    two_tors = {counters.target_index(F, (r, F.zero)) for r in E.two_torsion_roots()} | {2 * F.Q}
    assert special == two_tors
    n_generic = int(N - len(two_tors | Sset))
    assert res["generic_targets"] == n_generic
    # generic histogram of T_M from the naive counter
    nm = naive_TM(E, base, m)
    hist_gen = Counter()
    for i in range(len(mask)):
        if (mask[i] & 7) == 1:
            hist_gen[nm.get(i, 0)] += 1
    assert {int(k): v for k, v in res["conventions"]["M"]["hist_gen"].items()} == dict(hist_gen)
    # recount agrees with the primary pass in every convention (self-consistency of two code paths)
    for key, ent in res["recount"].items():
        assert ent["differ"] == 0 and ent.get("differ_second", 0) == 0, key
    # raw output (no cross-convention quantity is recorded)
    raw = {c: {"hist_all": res["conventions"][c]["hist_all"], "hist_gen": res["conventions"][c]["hist_gen"]}
           for c in ("A", "M", "S", "X")}
    if (q, n) in [(5, 2), (5, 3), (13, 2), (13, 3), (5, 4), (13, 4), (5, 5)]:
        record("E1-exhaustive-vs-naive", f"q={q},n={n},m={m},base={base_kind}",
               {"B": len(base), "t2": res["t2"], "N": N, "size_X": len(lifts), "S_size": res["S_size"],
                "generic_targets": res["generic_targets"], "raw_histograms": raw, "recount": res["recount"]})
    else:
        record("E1-exhaustive-vs-naive", f"q={q},n={n},m={m},base={base_kind}",
               {"B": len(base), "N": N, "recount": res["recount"]})


def test_ncf_coefficient_function_matches_series_expansion():
    """The function that evaluates the generating-function coefficient, against an independent expansion
    (each +- pair contributes 1 + 2z + 2z^2 + ..., each 2-torsion point 1 + z). Arithmetic of the formula
    only: no comparison with any enumerated count."""
    def series(B, t2, m):
        poly = [1] + [0] * m
        for _ in range((B - t2) // 2):
            new = [0] * (m + 1)
            for i, c in enumerate(poly):
                for j in range(m + 1 - i):
                    new[i + j] += c * (1 if j == 0 else 2)
            poly = new
        for _ in range(t2):
            new = poly[:]
            for i in range(m):
                new[i + 1] += poly[i]
            poly = new
        return poly[m]
    for B, t2 in [(6, 0), (7, 1), (10, 2), (13, 3), (24, 0)]:
        if (B - t2) % 2:
            continue
        for m in range(0, 6):
            assert counters.ncf_coefficient(B, t2, m) == series(B, t2, m)


# =============================================================================== A: arm C counter vs naive
ARMC_CELLS = [(13, 2, 2), (13, 2, 3), (5, 2, 4), (5, 3, 3), (13, 3, 2), (101, 1, 2), (103, 1, 2),
              (5, 6, 6), (5, 7, 7)]          # KX-3 widening: E2 at (5,6,m=6) and (5,7,m=7), line and random bases


@pytest.mark.parametrize("q,n,m", ARMC_CELLS)
@pytest.mark.parametrize("base_kind", ["line", "random"])
def test_sampled_counter_matches_naive_enumeration(q, n, m, base_kind, kernel):
    F, E, _ = kat_curve(q, n, "armc")
    N, _ = kernel.valid_mask(E)
    D, X, t2 = E.factor_base()
    rng = rng_for(f"armc{q}{n}{m}{base_kind}")
    base = D if base_kind == "line" else counters.matched_random_base(E, len(D), t2, rng)
    Sx0 = {i >> 1 for i in naive_S_and_masks(E, base, m, N) if i != 2 * F.Q}
    eligible = sum(1 for x in F.elements() if F.chi(E.f(x)) == 1 and F.to_code(x) not in Sx0)
    assert eligible >= 2, "KAT cell has fewer than two eligible generic classes"
    s = max(min(30, eligible // 2), 1)
    tr = curves.make_rng(f"kat|targets|{q}|{n}|{m}|{base_kind}")
    r = counters.arm_c_cell(kernel, E, base, m, s, tr, N)
    Sset = naive_S_and_masks(E, base, m, N)
    keys = [int(k) for k in r["keys"]]
    # sampled targets: distinct classes, chi = +1, not in S, uniform-rule structure
    assert len(keys) == s == len(set(k >> 1 for k in keys))
    Sx = {i >> 1 for i in Sset if i != 2 * F.Q}
    for k in keys:
        x = F.from_code(k >> 1)
        assert F.chi(E.f(x)) == 1 and (k >> 1) not in Sx
    cnt = Counter()
    ncf = mS = 0
    for ms in itertools.combinations_with_replacement(base, m):
        idx = counters.target_index(F, pt_sum(E, ms))
        cnt[idx] += 1
        cf = True
        for P in ms:
            if ms.count((P[0], F.neg(P[1]))) > 0 and not F.is_zero(P[1]):
                cf = False
            if F.is_zero(P[1]) and ms.count(P) >= 2:
                cf = False
        if cf:
            ncf += 1
            if idx in Sset:
                mS += 1
    assert [cnt.get(k, 0) for k in keys] == [int(c) for c in r["sampled_counts"]]
    sorted_S = sorted(Sset)
    assert [cnt.get(k, 0) for k in sorted_S] == [int(c) for c in r["S_counts"]]
    assert r["S_size"] == len(Sset)
    assert r["cancellation_free"] == ncf and r["m_S"] == mS
    assert r["multisets"] == math.comb(len(base) + m - 1, m)
    # determinism
    r2 = counters.arm_c_cell(kernel, E, base, m, s, curves.make_rng(f"kat|targets|{q}|{n}|{m}|{base_kind}"), N)
    assert [int(k) for k in r2["keys"]] == keys
    record("A1-sampled-vs-naive", f"q={q},n={n},m={m},base={base_kind}",
           {"B": len(base), "N": N, "s": s, "sampled_counts": [int(c) for c in r["sampled_counts"]],
            "S_counts": [int(c) for c in r["S_counts"]], "cancellation_free": ncf, "m_S": mS})


def test_poisson_helpers_against_independent_computation():
    rng = np.random.default_rng(12345)
    counts = rng.poisson(0.4, size=500)
    lam = 0.4
    summ = counters.poisson_summary(counts, lam)
    # independent: pmf by exp/factorial, cdf cumulative sums
    pm = [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(int(counts.max()) + 1)]
    cdf = np.cumsum(pm)
    emp = np.cumsum([int((counts == k).sum()) for k in range(int(counts.max()) + 1)]) / counts.size
    assert max(abs(emp - cdf)) == pytest.approx(summ["ks_stat"], abs=1e-12)
    assert summ["zero_fraction"] == pytest.approx(float((counts == 0).mean()))
    assert summ["dispersion_index"] == pytest.approx(float(counts.var(ddof=1) / counts.mean()))
    tail = 1 - sum(pm[: int(counts.max())])
    assert counters.poisson_upper_tail(lam, int(counts.max())) == pytest.approx(tail, rel=1e-6)
    pmax = 1 - (1 - tail) ** counts.size
    assert summ["p_max_pred"] == pytest.approx(pmax, rel=1e-6)
    assert summ["max_count"] == int(counts.max()) and sum(summ["hist"].values()) == counts.size


def test_poisson_chi2_known_answer_when_counts_equal_expectation():
    lam, s = 1.0, 200000
    pm = [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(12)]
    counts = np.concatenate([np.full(int(round(s * p)), k) for k, p in enumerate(pm)])
    summ = counters.poisson_summary(counts, lam)
    assert summ["chi2_stat"] < 1.0 and summ["chi2_df"] >= 5
    assert summ["ks_stat"] < 1e-3


# =============================================================================== B: bases and samplers
@pytest.mark.parametrize("q,n", EXT_FIELDS)
def test_random_and_twin_bases_structure(q, n):
    F, E, _ = kat_curve(q, n, "bases")
    D, X, t2 = E.factor_base()
    B = len(D)
    roots = set(E.two_torsion_roots())
    for kind in ("random", "twin"):
        rng = curves.make_rng(f"kat|base|{q}|{n}|{kind}")
        base = (counters.matched_random_base(E, B, t2, rng) if kind == "random"
                else counters.twin_base(E, B, t2, rng))
        again = (counters.matched_random_base(E, B, t2, curves.make_rng(f"kat|base|{q}|{n}|{kind}")) if kind == "random"
                 else counters.twin_base(E, B, t2, curves.make_rng(f"kat|base|{q}|{n}|{kind}")))
        assert base == again                                          # deterministic by seed
        assert all(E.on_curve(P) for P in base) and len(set(base)) == len(base)
        assert set(E.neg(P) for P in base) == set(base)               # symmetric
        tors = [P for P in base if F.is_zero(P[1])]
        assert len(tors) == t2 and all(P[0] in roots for P in tors)   # t2 matched, from E(F_Q)[2]
        pairs = (B - t2) // 2 if kind == "random" else -(-(B - t2) // 4)
        assert len(base) == t2 + 2 * pairs
        assert len({P[0] for P in base if not F.is_zero(P[1])}) == pairs   # distinct classes


def test_target_sampler_chi_and_uniform_rule(kernel):
    F, E, _ = kat_curve(13, 2, "tsamp")
    rng = curves.make_rng("kat|targets|sampler")
    keys, draws = counters.sample_targets(kernel, E, 25, rng, set())
    assert len(set(k >> 1 for k in keys.tolist())) == 25
    for k in keys.tolist():
        x = F.from_code(k >> 1)
        assert F.chi(E.f(x)) == 1 and (k & 1) in (0, 1)
    # kernel chi equals Python chi on random x
    rr = rng_for("chi")
    xs = rr.integers(0, 13, size=(200, 2))
    kc = kernel.chi_batch(E, xs).tolist()
    assert kc == [F.chi(E.f(tuple(int(v) for v in row))) for row in xs]
    for (qq, nn) in [(5, 3), (13, 3), (101, 1)]:
        F3, E3, _ = kat_curve(qq, nn, "chi3")
        xs = rr.integers(0, qq, size=(200, nn))
        assert kernel.chi_batch(E3, xs).tolist() == [F3.chi(E3.f(tuple(int(v) for v in row))) for row in xs]


# =============================================================================== T: trial plan rules
def _sieve_least_prime(n):
    limit = 2 ** 20
    sieve = bytearray([1]) * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    for p in range(4, limit + 1):
        if sieve[p] and p ** n >= 2 ** 30:
            return p


def test_q_rule_against_sieve_and_report_against_expected_list():
    got = {n: mtp.q_rule(n) for n in range(2, 8)}
    assert got == {n: _sieve_least_prime(n) for n in range(2, 8)}
    record("T1-q-rule", "n=2..7", {"generated": got, "specification_list": mtp.EXPECTED_QN,
                                   "agrees_with_specification_list": got == mtp.EXPECTED_QN})


def test_sample_size_rule_against_float_formula():
    got = {n: mtp.sample_size_rule(n) for n in range(2, 8)}
    for n in range(2, 8):
        lam = 1 / math.factorial(n)
        c = -math.expm1(-lam)
        val = math.exp(-lam) / (c * 0.03 ** 2)
        assert abs(got[n] - val) <= 1.0
        assert got[n] == math.ceil(val) or abs(val - round(val)) < 1e-6
    record("T2-sample-size-rule", "n=2..7", {"generated": got})


class _StubBuilder:
    def __init__(self):
        self.calls = []

    def get(self, arm, n, q, i):
        self.calls.append((arm, n, q, i))
        return {"q": q, "n": n, "stub": True, "curve_seed": {"seed_string": mtp.curve_seed(arm, n, q, i), "seed_int": "0"},
                "B": 2 * n + 1}


def test_trial_plan_enumeration_and_seed_derivation():
    sb = _StubBuilder()
    plan = mtp.build_plan(None, builder=sb)
    assert plan["cell_counts"] == {"A": 54, "B1": 12, "B2": 12, "C": 18}
    ids = [c["cell_id"] for c in plan["cells"]]
    assert len(ids) == len(set(ids)) == 96
    for c in plan["cells"]:
        if c["arm"] == "A":
            assert c["base_roles"]["matched_random"]["seed_string"] == f"f15270|base|{c['cell_id']}|random|0"
            assert c["base_roles"]["half_twin"]["seed_string"] == f"f15270|base|{c['cell_id']}|twin|0"
        if c["arm"] in ("B1", "B2"):
            assert c["tuple_seed"]["seed_string"] == f"f15270|tuples|{c['cell_id']}|0"
        if c["arm"] == "C":
            assert c["target_seed"]["seed_string"] == f"f15270|targets|{c['cell_id']}"
    # arm B reuses the arm-A curves of the same (n, q)
    assert {arm for (arm, _, _, _) in sb.calls} == {"A", "C"}          # arm B instances use arm-A seed strings
    b_calls = {(n, q, i) for (arm, n, q, i) in sb.calls if arm == "A"}
    for n in (2, 3, 4, 5):
        for q in (mtp.ARM_A_LADDER[n][0], mtp.ARM_A_LADDER[n][1]):
            for i in range(3):
                assert (n, q, i) in b_calls
    a_cells = [c for c in plan["cells"] if c["arm"] == "A"]
    assert sorted({c["n"] for c in a_cells}) == [1, 2, 3, 4, 5]
    assert set(plan["arm_c_q_n"]) == {"2", "3", "4", "5", "6", "7"}


def test_plan_is_deterministic_for_a_cell_subset(kernel):
    """Identity fields of two small cells built twice are identical (the full plan is regenerated twice
    separately and compared byte for byte; see kat-report)."""
    ib1, ib2 = mtp.InstanceBuilder(kernel), mtp.InstanceBuilder(kernel)
    # contract cells are not computed here: use the builder on KAT parameters through the same code path
    for (arm, n, q, i) in [("K", 2, 13, 0), ("K", 3, 5, 1), ("K", 1, 101, 2)]:
        assert json.dumps(ib1.get(arm, n, q, i), sort_keys=True) == json.dumps(ib2.get(arm, n, q, i), sort_keys=True)
    ident = ib1.get("K", 2, 13, 0)
    assert set(["q", "n", "g", "a", "b", "N", "t2", "B", "size_X", "curve_seed"]) <= set(ident)
    assert ident["N_exhaustive"] == ident["N_bsgs"] == ident["N"]


# =============================================================================== L: launcher
def test_launcher_refuses_contract_cell_while_specification_not_approved(tmp_path):
    import yaml
    if yaml.safe_load(open(launcher.SPEC_PATH))["experiment"]["status"] == "approved":
        pytest.skip("specification is approved; the refusal is exercised with synthetic specs below")
    runs_before = os.path.exists(launcher.RUNS_DIR)
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"cells": [{"cell_id": "A-n2-q61-c0"}]}))
    ok, reasons = launcher.check_approval(plan_path=str(plan))
    assert not ok
    assert any("status" in r for r in reasons) and any("lock missing" in r for r in reasons)
    rc = launcher.main(["cell", "--cell-id", "A-n2-q61-c0", "--plan", str(plan), "--run-id", "RUN-should-not-exist"])
    assert rc == launcher.EXIT_REFUSED
    assert os.path.exists(launcher.RUNS_DIR) == runs_before
    assert not os.path.exists(os.path.join(launcher.RUNS_DIR, "RUN-should-not-exist"))
    record("L1-refusal", "status as on disk", {"exit_code": rc, "reasons": reasons})


def test_launcher_approval_gate_logic_with_synthetic_specs(tmp_path):
    spec = tmp_path / "specification.yaml"
    lock = tmp_path / "approval.lock"
    plan = tmp_path / "plan.json"
    plan.write_text("{}")
    approved = "experiment:\n  status: approved\n  approved_by: someone\n  execution_authorized: true\n  frozen: true\n"
    spec.write_text(approved)
    ok, reasons = launcher.check_approval(str(spec), str(lock), str(plan))
    assert not ok and any("lock missing" in r for r in reasons)
    lock.write_text(json.dumps({"approved_by": "someone", "specification_sha256": "0" * 64,
                                "code_sha256": "0" * 64, "trial_plan_sha256": "0" * 64,
                                "test_file_sha256": "0" * 64}))
    ok, reasons = launcher.check_approval(str(spec), str(lock), str(plan))
    assert not ok and len(reasons) == 4
    lock.write_text(json.dumps({"approved_by": "someone", "specification_sha256": launcher.sha256_file(str(spec)),
                                "code_sha256": launcher.code_sha256(), "trial_plan_sha256": launcher.sha256_file(str(plan)),
                                "test_file_sha256": launcher.sha256_file(launcher.TEST_FILE)}))
    assert launcher.check_approval(str(spec), str(lock), str(plan)) == (True, [])
    spec.write_text("experiment:\n  status: approved\n  approved_by: null\n")
    ok, reasons = launcher.check_approval(str(spec), str(lock), str(plan))
    assert not ok and any("approved_by" in r for r in reasons)
    spec.write_text("experiment:\n  status: review_required\n  approved_by: null\n")
    assert not launcher.check_approval(str(spec), str(lock), str(plan))[0]


def test_launcher_kat_flag_required_and_contract_cells_refused():
    assert launcher.main(["kat", "--arm", "A", "--q", "13", "--n", "2", "--curve-seed", "x"]) == launcher.EXIT_REFUSED
    assert launcher.main(["--kat", "kat", "--arm", "A", "--q", "61", "--n", "2", "--curve-seed", "x"]) == launcher.EXIT_REFUSED
    assert launcher.main(["--kat", "cell", "--cell-id", "A-n2-q61-c0", "--plan", "x", "--run-id", "x"]) == launcher.EXIT_REFUSED


@pytest.mark.parametrize("arm,q,n", [("A", 13, 2), ("C", 13, 2), ("B1", 13, 3), ("B2", 5, 3)])
def test_launcher_kat_cell_writes_package_in_temp_dir_only(arm, q, n, kernel, capsys):
    runs_before = os.path.exists(launcher.RUNS_DIR)
    rc = launcher.main(["--kat", "kat", "--arm", arm, "--q", str(q), "--n", str(n), "--curve-seed", "kat|launcher",
                        "--s", "20", "--tuples", "20"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    d = out["kat_dir"]
    try:
        assert not os.path.abspath(d).startswith(os.path.abspath(launcher.RUNS_DIR))
        for f in ("manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json",
                  "summary.json"):
            assert os.path.getsize(os.path.join(d, f)) > 0 or f == "stderr.log"
        man = open(os.path.join(d, "manifest.yaml")).read()
        assert "kat: true" in man and "code_sha256" in man and "derived_statistics_withheld: true" in man
        raw = json.load(open(os.path.join(d, "raw-result.json")))
        if arm == "A":
            for role, r in raw["bases"].items():
                assert "identities" not in r                        # no cross-convention comparison in KAT mode
        if arm == "C":
            assert os.path.exists(os.path.join(d, "results", "KAT-C-n2-q13.cdf.json"))
        record("L2-kat-cell-package", f"arm={arm},q={q},n={n}", {"files": sorted(os.listdir(d))})
    finally:
        shutil.rmtree(d, ignore_errors=True)
    assert os.path.exists(launcher.RUNS_DIR) == runs_before


def test_environment_record_has_compiler_and_flags():
    env = launcher.environment_record()
    assert env["compiler"]["flags"] and env["compiler"]["version"]
    assert set(launcher.CODE_FILES) == set(env["code_file_sha256"])
    assert env["libraries"]["numpy"]


def test_launcher_derived_summaries_on_synthetic_inputs_only():
    """The derived-statistics paths (used on contract cells, withheld on KAT cells) are exercised here on
    fabricated inputs, not on any counted cell."""
    from fractions import Fraction
    r = {"sampled_counts": np.array([0, 0, 1, 2, 0, 1, 0, 3]), "S_counts": np.array([5, 7]), "t2": 1, "S_size": 2,
         "draws": 1024, "multisets": 100, "cancellation_free": 80, "m_S": 4, "N_cf_formula": 80,
         "lambda": Fraction(3, 8)}
    e = launcher.arm_c_entry(r, 10, True, 0.5)
    flat = launcher.arm_c_flat(e, True)
    for k in ("hist", "lambda", "exceptional_targets", *launcher.CDF_POISSON_KEYS):
        assert k in flat
    assert flat["coverage"] == pytest.approx(0.5) and flat["zero_fraction"] == pytest.approx(0.5)
    assert flat["exceptional_targets"] == [5, 7] and flat["max_count"] == 3
    e2 = launcher.arm_c_flat(launcher.arm_c_entry(r, 10, False, 0.5), False)
    assert "coverage" not in e2 and "hist" in e2
    fake = {"line": {"B": 4, "t2": 0, "N": 9, "size_X": 2, "S_size": 1, "generic_targets": 6,
                     "special_targets_O_and_E2": 1, "identities": {}, "recount": {},
                     "conventions": {c: {"stats": {"all": {"targets": 9, "sum": 9, "sumsq": 9, "zeros": 3, "max": 2},
                                                   "generic": {"targets": 6, "sum": 6, "sumsq": 6, "zeros": 2, "max": 2}}}
                                     for c in ("A", "M", "S", "X")}}}
    summ = launcher._cell_summary_arm_a(fake, True)
    assert summ["line"]["derived"]["M"]["coverage_generic"] == [4, 6] and summ["line"]["derived"]["A"]["mean_all"] == "1"
    assert "derived" not in launcher._cell_summary_arm_a(fake, False)["line"]


def test_launcher_watchdog_marks_cell_failed_resource_exhaustion(tmp_path, kernel):
    spec = {"arm": "B1", "cell_id": "KAT-B1-watchdog", "n": 3, "q": 13, "m": 3, "curve_index": 0,
            "curve_seed": "kat|watchdog", "tuples": 400000, "group_law_subsample_fraction": 0.1,
            "tuple_seed": "kat|tuples|watchdog|0", "instances": [{"q": 13, "curve_seed": "kat|watchdog"}]}
    man = launcher.run_cell(spec, str(tmp_path / "w"), kat=True, kernel=kernel, timeout_seconds=0.3)
    assert man["status"] == "failed" and man["failure_class"] == "resource_exhaustion"
    assert "watchdog" in open(tmp_path / "w" / "stderr.log").read()


def test_launcher_arm_b_chi_patterns_are_recorded(tmp_path, kernel):
    spec = {"arm": "B1", "cell_id": "KAT-B1-patterns", "n": 3, "q": 13, "m": 3, "curve_index": 0,
            "curve_seed": "kat|patterns", "tuples": 60, "group_law_subsample_fraction": 0.1,
            "tuple_seed": "kat|tuples|patterns|0", "instances": [{"q": 13, "curve_seed": "kat|patterns"}]}
    man = launcher.run_cell(spec, str(tmp_path / "p"), kat=True, kernel=kernel)
    assert man["status"] == "completed"
    raw = json.load(open(tmp_path / "p" / "raw-result.json"))
    tally = raw["instances"][0]["tally"]
    assert sum(tally["chi_patterns"].values()) == tally["tuples"] == 60
    record("L3-arm-B-kat-tally", "q=13,n=3 (60 tuples)", {"tally_keys": sorted(tally)})


def test_launcher_approval_gate_refuses_empty_or_non_object_lock(tmp_path):
    spec = tmp_path / "specification.yaml"
    lock = tmp_path / "approval.lock"
    plan = tmp_path / "plan.json"
    plan.write_text("{}")
    spec.write_text("experiment:\n  status: approved\n  approved_by: someone\n")
    for content in ("{}", "[]", "null", "0", '""'):
        lock.write_text(content)
        ok, reasons = launcher.check_approval(str(spec), str(lock), str(plan))
        assert not ok and any("empty or not a JSON object" in r for r in reasons), content
        assert any("approved_by" in r for r in reasons) and any("code_sha256" in r for r in reasons), content


def test_launcher_empty_tuple_list_yields_complete_zero_tally():
    F, E, _ = kat_curve(13, 2, "empty-tally")
    tally = launcher._analyse_all(F, E, [], [], 1)
    assert all(tally[k] == 0 for k in launcher.TALLY_KEYS)
    assert tally["chi_patterns"] == {}
    record("L4-empty-tally", "q=13,n=2 (0 tuples)", {"tally_keys": sorted(tally)})


def test_launcher_b1_runs_the_aa_tuple_sample(tmp_path, kernel):
    cell = {"arm": "B1", "cell_id": "B1-synthetic", "n": 3, "q": 13, "tuple_size_m": 4, "tuples": 30,
            "group_law_subsample_fraction": 0.1, "tuple_seed": {"seed_string": "kat|tuples|aa|0"},
            "tuple_seed_aa": {"seed_string": "kat|tuples|aa|1"},
            "identity": {"curve_seed": {"seed_string": "kat|aa"}}}
    spec = launcher.spec_from_plan_cell(cell)[0]
    assert spec["tuple_seed_aa"] == "kat|tuples|aa|1"
    spec["cell_id"] = "KAT-B1-aa"
    spec["instances"] = [{"q": 13, "curve_seed": "kat|aa"}]                # no contract identity to check
    man = launcher.run_cell(spec, str(tmp_path / "aa"), kat=True, kernel=kernel)
    assert man["status"] == "completed"
    inst = json.load(open(tmp_path / "aa" / "raw-result.json"))["instances"]
    assert [i["sample"] for i in inst] == ["primary", "aa"]
    assert [i["tuple_seed"] for i in inst] == ["kat|tuples|aa|0", "kat|tuples|aa|1"]
    assert all(i["tally"]["tuples"] == 30 for i in inst)
    summary = json.load(open(tmp_path / "aa" / "summary.json"))
    assert [i["sample"] for i in summary["instances"]] == ["primary", "aa"]
    no_aa = dict(cell)
    del no_aa["tuple_seed_aa"]
    assert launcher.spec_from_plan_cell(no_aa)[0]["tuple_seed_aa"] is None
    record("L5-b1-aa-sample", "q=13,n=3 (30 tuples x 2 seeds)", {"samples": [i["sample"] for i in inst]})


@pytest.mark.parametrize("q,n,tuple_len", [(13, 2, 3), (5, 3, 3), (13, 3, 4), (101, 1, 4)])
def test_analyse_fibre_fast_path_agrees_with_detailed_path(q, n, tuple_len):
    F, E, _ = kat_curve(q, n, "fast")
    rng = rng_for(f"fast{q}{n}{tuple_len}")
    for _ in range(40):
        xs = [F.random_element(rng) for _ in range(tuple_len)]
        a = semaev.analyse_fibre(F, E, xs, detail=True)
        b = semaev.analyse_fibre(F, E, xs, detail=False)
        for k in ("degree", "full_degree", "squarefree", "chis", "split_completely", "zero_poly"):
            assert a[k] == b[k]


# =============================================================================== W: widened cells (TASK-20261105-ac5ad6)
# DEC-20261105-f0b7c7 F-1 (IM-3 widened): q in {5, 13} at n = 4..7; q'_n = least prime above the arm-C q_n at
# degree n = 2..7. Naive against optimised only; no cross-convention identity, residual or predicted value is
# asserted or recorded anywhere below.
import functools  # noqa: E402
from bisect import bisect_right  # noqa: E402

WIDE_FIELDS = [(q, n) for q in (5, 13) for n in (4, 5, 6, 7)]


def _is_prime_trial(p):
    return p > 1 and all(p % d for d in range(2, math.isqrt(p) + 1))


def _least_prime_above_trial(k):
    p = k + 1
    while not _is_prime_trial(p):
        p += 1
    return p


# q'_n by independent trial division from the arm-C q_n of the trial-plan rule
LARGE_FIELDS = [(_least_prime_above_trial(mtp.q_rule(n)), n) for n in range(2, 8)]
Q_PRIME_EXPECTED = {2: 32779, 3: 1033, 4: 193, 5: 71, 6: 41, 7: 29}


def test_widened_kat_fields_disjoint_from_every_contract_pair():
    """The check is itself a test (KX-2): every widened KAT (q, n) pair is disjoint from every arm-A, arm-B and
    arm-C contract pair, and q'_n is the least prime above the arm-C q_n."""
    arm_a = mtp.contract_cells_qn()
    arm_c = {(mtp.q_rule(n), n) for n in mtp.ARM_C_NS}
    assert arm_c == launcher.arm_c_pairs() and launcher.contract_pairs() == arm_a | arm_c
    assert len(arm_c) == 6
    for q, n in WIDE_FIELDS + LARGE_FIELDS + ALL_FIELDS:
        assert (q, n) not in arm_a and (q, n) not in arm_c, (q, n)
        assert (q, n) not in launcher.contract_pairs()
    assert {n: q for q, n in LARGE_FIELDS} == Q_PRIME_EXPECTED
    for n in range(2, 8):
        qn, qp = mtp.q_rule(n), dict((nn, q) for q, nn in LARGE_FIELDS)[n]
        assert qp > qn and _is_prime_trial(qp) and not any(_is_prime_trial(k) for k in range(qn + 1, qp))
        assert fqn.next_prime_above(qn) == qp
    rows = [{"q": q, "n": n, "Q": q ** n} for q, n in WIDE_FIELDS + LARGE_FIELDS]
    record("W0-disjointness", "widened KAT fields", {"arm_a_b_pairs": sorted(arm_a), "arm_c_pairs": sorted(arm_c),
                                                     "widened_kat_fields": rows})


@functools.lru_cache(maxsize=None)
def large_instance(q, n):
    F = FQ(q, n)
    E, info = curves.generate_curve(F, f"kat|large|{q}|{n}")
    return F, E, info


@functools.lru_cache(maxsize=None)
def large_base(q, n):
    F, E, _ = large_instance(q, n)
    return E.factor_base()


def _legendre_int(c, q):
    r = pow(c % q, (q - 1) // 2, q)
    return 0 if r == 0 else (1 if r == 1 else -1)


def _check_field_axioms(F, els):
    """Axioms, Frobenius = q-th power, norm-method inverse = Fermat inverse, sqrt, and chi two independent
    ways (Euler's criterion in F_Q, and chi_q of the norm as an integer Legendre symbol)."""
    q, Q = F.q, F.Q
    minus_one = F.neg(F.one)
    for a, b, c in zip(els, els[1:], els[2:]):
        assert F.mul(a, F.mul(b, c)) == F.mul(F.mul(a, b), c)
        assert F.mul(a, F.add(b, c)) == F.add(F.mul(a, b), F.mul(a, c))
        assert F.mul(a, b) == F.mul(b, a)
        assert F.add(a, F.neg(a)) == F.zero and F.sub(a, b) == F.add(a, F.neg(b))
        assert F.frobenius(a) == F.pow(a, q)
        if not F.is_zero(a):
            ia = F.inv(a)
            assert ia == F.inv_fermat(a) and F.mul(a, ia) == F.one
            euler = F.pow(a, (Q - 1) // 2)
            assert euler in (F.one, minus_one)
            e_chi = 1 if euler == F.one else -1
            nrm = F.norm(a)
            assert F.is_scalar(nrm)
            assert _legendre_int(nrm[0], q) == e_chi == F.chi(a)
            r = F.sqrt(F.mul(a, a))
            assert r is not None and F.mul(r, r) == F.mul(a, a)
            if e_chi == 1:
                s = F.sqrt(a)
                assert s is not None and F.mul(s, s) == a
            else:
                assert F.sqrt(a) is None
    assert F.chi(F.zero) == 0


@pytest.mark.parametrize("q,n", WIDE_FIELDS)
def test_wide_least_irreducible_matches_definition(q, n):
    got = fqn.least_irreducible(q, n)
    assert got == brute_least_irreducible(q, n)
    record("W1-least-irreducible", f"q={q},n={n}", {"g": got})


@pytest.mark.parametrize("q,n", WIDE_FIELDS)
def test_wide_field_axioms_and_kernel_ops(q, n, kernel):
    F, E, _ = kat_curve(q, n, "wfield")
    rng = rng_for(f"wfield{q}{n}")
    els = [F.random_element(rng) for _ in range(400)]
    _check_field_axioms(F, els)
    for a, b in zip(els[::2], els[1::2]):
        assert kernel.mul(E, a, b) == F.mul(a, b)
        if not F.is_zero(a):
            assert kernel.inv(E, a) == F.inv(a)
            assert kernel.inv(E, a, ref=True) == F.inv(a)
    F2 = FQ2(F)
    assert F.chi(F2.d) == -1
    record("W2-field-and-kernel-ops", f"q={q},n={n}", {"elements": len(els), "g": F.g})


@pytest.mark.parametrize("q,n", LARGE_FIELDS)
def test_large_q_field_axioms_inverses_chi_10k(q, n):
    F, E, _ = large_instance(q, n)
    rng = rng_for(f"lfield{q}{n}")
    els = [F.random_element(rng) for _ in range(10_000)]
    _check_field_axioms(F, els)
    record("W3-large-q-field", f"q={q},n={n}", {"elements": len(els), "g": F.g, "Q": F.Q})


@pytest.mark.parametrize("q,n", LARGE_FIELDS)
def test_large_q_kernel_ops_match_python(q, n, kernel):
    F, E, _ = large_instance(q, n)
    rng = rng_for(f"lkfield{q}{n}")
    pairs = 500
    for _ in range(pairs):
        a, b = F.random_element(rng), F.random_element(rng)
        assert kernel.mul(E, a, b) == F.mul(a, b)
        if not F.is_zero(a):
            assert kernel.inv(E, a) == F.inv(a)
            assert kernel.inv(E, a, ref=True) == F.inv(a)
    xs = rng.integers(0, q, size=(300, n))
    assert kernel.chi_batch(E, xs).tolist() == [F.chi(E.f(tuple(int(v) for v in row))) for row in xs]
    record("W4-large-q-kernel-ops", f"q={q},n={n}", {"pairs": pairs, "chi_x_tuples": 300})


def _check_curve_rules(F, q, n, tag):
    zero, one = F.zero, F.one
    assert Curve(F, zero, one).j_in_Fq()
    assert Curve(F, one, zero).j_in_Fq()
    assert Curve(F, F.neg(F.from_int(3)), F.from_int(2)).is_singular()
    for i in range(20):
        E, info = curves.generate_curve(F, f"kat|{tag}|sel|{q}|{n}|{i}")
        assert not E.is_singular() and not E.j_in_Fq()
        assert F.pow(E.j_invariant(), q) != E.j_invariant()


@pytest.mark.parametrize("q,n", WIDE_FIELDS)
def test_wide_curve_rules(q, n):
    _check_curve_rules(fld(q, n), q, n, "w")


@pytest.mark.parametrize("q,n", LARGE_FIELDS)
def test_large_q_curve_rules(q, n):
    _check_curve_rules(large_instance(q, n)[0], q, n, "l")


def kernel_chi_sum_count(kernel, E):
    """N = Q + 1 + sum_x chi(f(x)) with chi evaluated by the compiled batch routine over every x of F_Q."""
    F = E.F
    total, chunk = 0, 1 << 20
    for start in range(0, F.Q, chunk):
        c = np.arange(start, min(F.Q, start + chunk), dtype=np.int64)
        xs = np.empty((c.size, F.n), dtype=np.uint32)
        for i in range(F.n):
            xs[:, i] = c % F.q
            c //= F.q
        total += int(kernel.chi_batch(E, xs).astype(np.int64).sum())
    return F.Q + 1 + total


def _check_group_law(F, E, N, tag):
    rng = rng_for(f"{tag}{F.q}{F.n}")
    pts = []
    while len(pts) < 10:
        P = E.lift(F.random_element(rng))
        if P is not None:
            pts.append(P)
    for P in pts:
        assert E.on_curve(P) and E.add(P, E.neg(P)) is None and E.add(P, None) == P
    for P, R, S in zip(pts, pts[1:], pts[2:]):
        assert E.on_curve(E.add(P, R)) and E.add(P, R) == E.add(R, P)
        assert E.add(E.add(P, R), S) == E.add(P, E.add(R, S))
        assert E.mul(5, P) == E.add(E.add(E.add(E.add(P, P), P), P), P)
    for P in pts[:5]:
        assert E.mul(N, P) is None                         # Lagrange: N P = O


@pytest.mark.parametrize("q,n", WIDE_FIELDS)
def test_wide_group_law_and_point_count_three_ways(q, n, kernel):
    """Group law (associativity on random triples, N P = O) and the point count: compiled exhaustive = BSGS =
    kernel character sum for every Q < 2^27 (all wide fields); plus the definition-level square table and the
    Python character sum where Q <= 10^6."""
    F, E, _ = kat_curve(q, n, "wcount")
    assert F.Q < 2 ** 27
    N_exh = kernel.count_points(E)
    N_bsgs, used = E.count_points_bsgs()
    N_chi_kernel = kernel_chi_sum_count(kernel, E)
    assert N_exh == N_bsgs == N_chi_kernel
    assert abs(N_exh - (F.Q + 1)) <= 2 * math.isqrt(F.Q) + 2
    if F.Q <= 10 ** 6:
        assert E.count_points_naive() == N_exh == E.count_points_chi()
    Nk, mask = kernel.valid_mask(E)
    assert Nk == N_exh and int(np.count_nonzero(mask & 1)) == N_exh
    _check_group_law(F, E, N_exh, "wgrp")
    record("W5-wide-point-count-group-law", f"q={q},n={n}",
           {"a": E.a, "b": E.b, "N_exhaustive": N_exh, "N_bsgs": N_bsgs, "N_kernel_chi_sum": N_chi_kernel,
            "bsgs_point_pairs": used, "definition_level_checked": F.Q <= 10 ** 6})


@pytest.mark.parametrize("q,n", [(5, 4), (13, 4), (5, 5), (13, 5), (5, 6), (5, 7)])
def test_wide_factor_base_from_definition(q, n):
    """D, X, t2 from the definition (Q <= 10^6): all (x, y) with x in F_q and y^2 = f(x), by a table of squares
    built by direct multiplication of every element of F_Q."""
    F, E, _ = kat_curve(q, n, "wfb")
    assert F.Q <= 10 ** 6
    square_roots = {}
    for y in F.elements():
        square_roots.setdefault(F.mul(y, y), []).append(y)
    line = [(F.from_int(xv), y) for xv in range(q) for y in square_roots.get(E.f(F.from_int(xv)), [])]
    D, X, t2 = E.factor_base()
    assert sorted(D) == sorted(line) and len(D) == len(line)
    assert t2 == sum(1 for P in line if F.is_zero(P[1]))
    assert sorted(X) == sorted({P[0] for P in line})
    roots = sorted((x for x in F.elements() if F.is_zero(E.f(x))), key=F.to_code)
    assert E.two_torsion_roots() == roots
    assert len(D) == t2 + 2 * (len(X) - t2)
    record("W6-wide-factor-base", f"q={q},n={n}", {"B": len(D), "t2": t2, "size_X": len(X)})


@pytest.mark.parametrize("q,n,tuple_len", [(5, 4, 4), (13, 4, 4), (5, 5, 5)])
def test_wide_semaev_roots_agree_with_group_law_signed_sums(q, n, tuple_len):
    """Roots of S_{n+1}(x_1..x_n, T) against the group-law signed sums at k = n (over F_{5^4} and F_{5^5}; the
    F_{13^4} cell is added at no cost and is not required)."""
    F, E, _ = kat_curve(q, n, "sem2")
    rng = rng_for(f"wsemgl{q}{n}{tuple_len}")
    F2 = FQ2(F)
    k = agree = 0
    while k < 100:
        xs = [F.random_element(rng) for _ in range(tuple_len)]
        if any(F.is_zero(E.f(x)) for x in xs):
            continue
        res = semaev.analyse_fibre(F, E, xs)
        roots_gl, ninf = semaev.roots_via_group_law(F, E, xs, F2)
        if res["squarefree"] and res["full_degree"]:
            assert res["roots_Fq"] == roots_gl
            assert res["split_completely"] == res["split_check_xq"]
            agree += 1
        k += 1
    record("W7-wide-semaev-roots-vs-group-law", f"q={q},n={n},tuple_len={tuple_len}",
           {"tuples": k, "generic_compared": agree})


@pytest.mark.parametrize("q,n", LARGE_FIELDS)
def test_large_q_curve_count_hasse_group_order_and_twist(q, n):
    """BSGS N inside the Hasse interval, N P = O on 5 random points, N + N_twist = 2Q + 2."""
    F, E, _ = large_instance(q, n)
    N, used = E.count_points_bsgs()
    assert F.Q >= 2 ** 27                                   # BSGS regime of the specification
    assert abs(N - (F.Q + 1)) <= 2 * math.isqrt(F.Q) + 1
    rng = rng_for(f"lgrp{q}{n}")
    k = 0
    while k < 5:
        P = E.lift(F.random_element(rng))
        if P is not None:
            assert E.mul(N, P) is None
            k += 1
    N_tw, used_tw = E.twist().count_points_bsgs()
    assert N + N_tw == 2 * F.Q + 2
    _check_group_law(F, E, N, "lgrp2")
    record("W8-large-q-count", f"q={q},n={n}", {"N": N, "N_twist": N_tw, "bsgs_pairs": [used, used_tw], "Q": F.Q})


@pytest.mark.parametrize("q,n", LARGE_FIELDS)
def test_large_q_factor_base_symmetric_on_curve_and_t2_from_roots_in_Fq(q, n):
    F, E, _ = large_instance(q, n)
    D, X, t2 = large_base(q, n)
    S = set(D)
    assert len(S) == len(D)
    assert all(E.on_curve(P) for P in D) and {E.neg(P) for P in D} == S
    assert all(F.is_scalar(P[0]) for P in D)
    # t2 = number of roots of f in F_q, by integer arithmetic mod q (independent of F_Q field code):
    # x in F_q is a root of x^3 + a x + b iff the t^0 part x^3 + a0 x + b0 is 0 and a_i x + b_i = 0 for i >= 1.
    roots = [x for x in range(q)
             if (x ** 3 + E.a[0] * x + E.b[0]) % q == 0 and all((E.a[i] * x + E.b[i]) % q == 0 for i in range(1, n))]
    assert t2 == len(roots)
    assert sorted(P[0][0] for P in D if F.is_zero(P[1])) == roots
    assert len(D) == t2 + 2 * (len(X) - t2)
    record("W9-large-q-factor-base", f"q={q},n={n}", {"B": len(D), "t2": t2, "size_X": len(X)})


def membership_counts(E, D, m, keys):
    """Independent count of m-multisets of D summing to each target key. Each m-multiset is uniquely a
    (m-1)-multiset M together with its largest-index element d; so count the pairs (M, d), M over the
    (m-1)-multisets of indices <= d, whose remainder R - d lies in the sums of M. D is code-sorted."""
    F = E.F
    B = len(D)
    sums: dict = {}

    def rec(prev, acc, remaining):
        if remaining == 0:
            sums.setdefault(acc, []).append(prev)
            return
        for i in range(prev, B):
            rec(i, E.add(acc, D[i]), remaining - 1)

    rec(0, None, m - 1)
    for lst in sums.values():
        lst.sort()
    out = []
    for key in keys:
        x = F.from_code(int(key) >> 1)
        y = F.sqrt(E.f(x))
        ys = sorted([y, F.neg(y)], key=F.to_code)
        R = (x, ys[int(key) & 1])
        assert counters.target_index(F, R) == int(key)
        cnt = 0
        for d in range(B):
            lst = sums.get(E.add(R, E.neg(D[d])))
            if lst:
                cnt += bisect_right(lst, d)
        out.append(cnt)
    return out


# (n = 2, m = 3) has C(B+2, 3) ~ 6e12 multisets with B ~ 32780: not runnable in the task budget (recorded as
# scope note DEV-1 in kat-report-ac5ad6.md); n = 2 is checked at m = 2 only.
LARGE_E2_CELLS = [(q, n, m) for q, n in LARGE_FIELDS for m in (2, 3) if not (n == 2 and m == 3)]


def constructed_target_keys(F, E, D, m, count, rng):
    """`count` distinct target keys drawn as sums of m base points (a uniform multiset of D, summed with the group
    law), excluding O and E[2]. A property of the construction: every one has a nonzero membership count."""
    keys = []
    seen = set()
    while len(keys) < count:
        idx = rng.integers(0, len(D), size=m)
        R = None
        for i in idx:
            R = E.add(R, D[int(i)])
        if R is None or F.is_zero(R[1]):
            continue
        k = counters.target_index(F, R)
        if k in seen:
            continue
        seen.add(k)
        keys.append(k)
    return keys


@pytest.mark.parametrize("q,n,m", LARGE_E2_CELLS)
def test_large_q_sampled_counter_against_membership_method(q, n, m, kernel):
    F, E, _ = large_instance(q, n)
    D, X, t2 = large_base(q, n)
    N = E.count_points_bsgs()[0]
    s = 50
    tr = curves.make_rng(f"kat|targets|large|{q}|{n}|{m}")
    r = counters.arm_c_cell(kernel, E, D, m, s, tr, N)
    keys = [int(k) for k in r["keys"]]
    assert len(keys) == s == len(set(k >> 1 for k in keys))
    for k in keys:
        assert F.chi(E.f(F.from_code(k >> 1))) == 1
    # FX-7: for n >= 3 the count comparison must not be vacuous. A second set of 50 targets is drawn as sums of m
    # base points (so at least half of this test's 100 targets are constructed), and compared through run_sampled.
    ckeys = []
    if n >= 3:
        ckeys = constructed_target_keys(F, E, D, m, 50, curves.make_rng(f"kat|constructed|large|{q}|{n}|{m}"))
    want_all = membership_counts(E, D, m, keys + ckeys)
    want = want_all[:s]
    assert [int(c) for c in r["sampled_counts"]] == want
    assert r["multisets"] == math.comb(len(D) + m - 1, m)
    out = {"B": len(D), "N": N, "s": s, "sampled_counts": [int(c) for c in r["sampled_counts"]],
           "membership_counts": want}
    if ckeys:
        assert len(ckeys) >= s // 2 and len(set(ckeys)) == len(ckeys)
        assert all(c > 0 for c in want_all[s:])                     # property of the construction, not a prediction
        c2, _ = kernel.run_sampled(E, m, D, np.array(ckeys, dtype=np.uint64), len(ckeys))
        assert [int(c) for c in c2] == want_all[s:]
        out["constructed_keys_count"] = len(ckeys)
        out["constructed_counts"] = [int(c) for c in c2]
        out["constructed_nonzero_membership"] = int(sum(1 for c in want_all[s:] if c > 0))
    record("W10-large-q-sampled-vs-membership", f"q={q},n={n},m={m},base=line", out)


# =============================================================================== X: composition residuals (KX-5)
def _series_csym(size_X, B, t2, m):
    """[z^m] (1+z)^(|X|-1) (1-z)^(-(B-t2)/2-1) by truncated power-series arithmetic only: multiply by (1+z)
    |X|-1 times and by 1/(1-z) (a prefix sum) (B-t2)/2 + 1 times."""
    poly = [1] + [0] * m
    for _ in range(size_X - 1):
        new = poly[:]
        for i in range(m):
            new[i + 1] += poly[i]
        poly = new
    for _ in range((B - t2) // 2 + 1):
        acc, new = 0, []
        for c in poly:
            acc += c
            new.append(acc)
        poly = new
    return poly[m]


def test_csym_coefficient_against_independent_series_expansion():
    for size_X, B, t2 in [(1, 0, 0), (1, 1, 1), (2, 3, 1), (3, 4, 0), (4, 8, 2), (7, 10, 2), (9, 16, 0), (12, 21, 3),
                          (30, 40, 0)]:
        for m in range(0, 7):
            assert counters.csym_coefficient(size_X, B, t2, m) == _series_csym(size_X, B, t2, m)
    assert counters.csym_coefficient(1, 0, 0, 5) == 1                     # (1+z)^0 (1-z)^-1: all coefficients 1
    assert counters.csym_coefficient(5, 6, 0, 0) == 1
    with pytest.raises(ValueError):
        counters.csym_coefficient(3, 5, 0, 2)                            # B - t2 odd
    with pytest.raises(ValueError):
        counters.csym_coefficient(0, 2, 0, 2)


def _fake_arrays():
    # targets 0..8; valid: 0,1,2,3,5,6,7,8 (target 4 is not on the curve); special (O or E[2], mask value 3): 1 and 7
    mask = np.array([1, 3, 1, 1, 0, 1, 1, 3, 1], dtype=np.uint8)
    h_s = np.array([4, 2, 0, 3, 9, 1, 0, 6, 5], dtype=np.uint32)
    h_a2 = np.array([4, 2, 1, 3, 0, 1, 0, 4, 5], dtype=np.uint32)
    h_m = np.array([0, 3, 2, 0, 8, 1, 0, 1, 1], dtype=np.uint32)
    h_x = np.array([0, 1, 2, 1, 8, 0, 0, 1, 1], dtype=np.uint32)
    return mask, h_s, h_a2, h_m, h_x


def test_composition_residuals_on_fabricated_inputs_only():
    mask, h_s, h_a2, h_m, h_x = _fake_arrays()
    # (vii) only the special targets {1, 7} are compared: h_s = (2, 6) against h_a2 = (2, 4): one differs
    assert counters.residual_special_targets(h_s, h_a2, mask) == {"differ": 1, "compared": 2}
    # target 2 differs (0 vs 1) but is not special: it is not counted
    # (viii) valid non-special targets {0, 2, 3, 5, 6, 8}: h_m != h_x only at 3 (0 vs 1) and 5 (1 vs 0)
    assert counters.residual_n2_tm_vs_tx(h_m, h_x, mask) == {"differ": 2, "compared": 6}
    # (ix) valid targets with h_m >= 1: 1, 2, 5, 7, 8 (target 4 is invalid and excluded): observed 5
    out = counters.symmetric_coverage_ceiling(h_m, mask, N=8, B=4, t2=0, size_X=3, m=2)
    assert out["observed"] == 5 and out["N"] == 8
    assert out["C_sym"] == _series_csym(3, 4, 0, 2)
    assert out["bound_min_N_C_sym"] == min(8, out["C_sym"]) and out["margin"] == out["bound_min_N_C_sym"] - 5
    # the min(N, .) branch and a negative margin (an excess) are reported, not hidden
    big = counters.symmetric_coverage_ceiling(h_m, mask, N=3, B=40, t2=0, size_X=21, m=2)
    assert big["bound_min_N_C_sym"] == 3 and big["margin"] == -2


@pytest.mark.parametrize("m", [2, 3])
def test_exhaustive_cell_carries_the_three_residual_fields_without_recording_values(m, kernel):
    """Only the presence of the fields is asserted; no residual value at a KAT cell is asserted or recorded."""
    F, E, _ = kat_curve(13, 2, "resid")
    N, vmask = kernel.valid_mask(E)
    D, X, t2 = E.factor_base()
    res = counters.exhaustive_cell(kernel, E, D, counters.x_lifts(F, D), m, N, vmask, recount=False)
    ident = res["identities"]
    assert "vii_TS_vs_TA_weighted_2j_special" in ident and "ix_symmetric_coverage_ceiling" in ident
    assert ("viii_n2_TM_eq_TX_off_2torsion" in ident) == (m == 2)
    assert {"differ", "compared"} <= set(ident["vii_TS_vs_TA_weighted_2j_special"])
    assert ident["ix_symmetric_coverage_ceiling"]["C_sym"] == counters.csym_coefficient(len(X), len(D), t2, m)
    assert ident["ix_symmetric_coverage_ceiling"]["N"] == N
    record("X1-residual-fields-present", f"q=13,n=2,m={m}", {"fields": sorted(k for k in ident if k[:3] in ("vii", "vii_", "ix_") or k.startswith(("vii", "viii", "ix")))})


def test_launcher_summary_names_residuals_when_derived_and_withholds_them_in_kat_mode():
    ident = {"vii_TS_vs_TA_weighted_2j_special": {"differ": 0, "compared": 3},
             "viii_n2_TM_eq_TX_off_2torsion": {"differ": 0, "compared": 5},
             "ix_symmetric_coverage_ceiling": {"observed": 1, "C_sym": 2, "N": 9, "bound_min_N_C_sym": 2, "margin": 1},
             "i_sum_A": {"observed": 1, "expected": 1}}
    fake = {"line": {"B": 4, "t2": 0, "N": 9, "size_X": 2, "S_size": 1, "generic_targets": 6,
                     "special_targets_O_and_E2": 1, "identities": ident, "recount": {},
                     "conventions": {c: {"stats": {"all": {"targets": 9, "sum": 9, "sumsq": 9, "zeros": 3, "max": 2},
                                                   "generic": {"targets": 6, "sum": 6, "sumsq": 6, "zeros": 2, "max": 2}}}
                                     for c in ("A", "M", "S", "X")}}}
    d = launcher._cell_summary_arm_a(fake, True)["line"]
    assert set(d["composition_residuals"]) == {"vii_TS_vs_TA_weighted_2j_special", "viii_n2_TM_eq_TX_off_2torsion",
                                              "ix_symmetric_coverage_ceiling"}
    assert "composition_residuals" not in launcher._cell_summary_arm_a(fake, False)["line"]


# =============================================================================== L: launcher KAT refusal of arm-C pairs (KX-6)
@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7])
@pytest.mark.parametrize("arm", ["A", "B1", "C"])
def test_launcher_kat_refuses_every_arm_c_pair(n, arm, capsys):
    q = mtp.q_rule(n)
    assert launcher.main(["--kat", "kat", "--arm", arm, "--q", str(q), "--n", str(n), "--curve-seed", "x"]) \
        == launcher.EXIT_REFUSED
    assert "REFUSED" in capsys.readouterr().err


def test_launcher_kat_accepts_widened_fields_beyond_the_refusal_list():
    assert (5, 4) not in launcher.contract_pairs() and (13, 7) not in launcher.contract_pairs()
    assert all(pair not in launcher.contract_pairs() for pair in LARGE_FIELDS)


# =============================================================================== T: plan determinism (KX-8)
def test_trial_plan_dumps_is_independent_of_instance_builder_cache_state():
    """build_plan twice with fresh stub builders gives byte-identical text (the full regeneration against the
    committed preview is compared by the task, see kat-report-ac5ad6)."""
    a = mtp.dumps(mtp.build_plan(None, builder=_StubBuilder()))
    b = mtp.dumps(mtp.build_plan(None, builder=_StubBuilder()))
    assert a == b


# =============================================================================== FX: TASK-20261106-4c4831 fixes
# Each test below closes a finding of TASK-20261105-165da2 (F-1, N-1 to N-5). They run on scratch experiment roots
# in temporary directories and on stub suites; none computes a contract cell or asserts a predicted value.
import subprocess  # noqa: E402
import types  # noqa: E402

STUB_OK = "def test_one(): pass\ndef test_two(): pass\ndef test_three(): pass\n"
STUB_EXTRA_SKIP = STUB_OK + "import pytest\ndef test_four(): pytest.skip('extra')\n"
STUB_FEWER = "def test_one(): pass\ndef test_two(): pass\n"
STUB_XPASS = "import pytest\n@pytest.mark.xfail\ndef test_x(): pass\ndef test_two(): pass\ndef test_three(): pass\n"
STUB_XFAIL = "import pytest\n@pytest.mark.xfail\ndef test_x(): assert 0\ndef test_two(): pass\ndef test_three(): pass\n"
STUB_FAIL = "def test_one(): pass\ndef test_two(): pass\ndef test_three(): assert 0\n"


def _scratch(tmp_path, monkeypatch, *, status="approved", approved_by="coord", authorized=True, frozen=True,
             stub=STUB_OK, lock=None, patch=True):
    """A scratch experiment root: specification, five-field lock, plan, stub suite. With patch=True the launcher's
    module paths point at it. The real selftest-receipts/ and runs/ are never touched."""
    d = tmp_path / "exp"
    (d / "stub").mkdir(parents=True)
    spec = d / "specification.yaml"
    spec.write_text(f"experiment:\n  status: {status}\n  approved_by: {approved_by}\n"
                    f"  execution_authorized: {str(authorized).lower()}\n  frozen: {str(frozen).lower()}\n")
    stub_file = d / "stub" / "test_stub.py"
    stub_file.write_text(stub)
    plan = d / "plan.json"
    plan.write_text(json.dumps({"cells": [{"cell_id": "A-fake", "arm": "A"}, {"cell_id": "A-fake2", "arm": "A"},
                                          {"cell_id": "B1-fake", "arm": "B1"}]}))
    ns = types.SimpleNamespace(dir=d, spec=spec, stub=stub_file, plan=plan, lock=d / "approval.lock",
                               runs=d / "runs", receipts=d / "selftest-receipts")
    ns.write_lock = lambda **over: ns.lock.write_text(json.dumps(
        {"approved_by": approved_by, "specification_sha256": launcher.sha256_file(str(spec)),
         "code_sha256": launcher.code_sha256(), "trial_plan_sha256": launcher.sha256_file(str(plan)),
         "test_file_sha256": launcher.sha256_file(str(stub_file)), **over}))
    if lock is not False:
        ns.write_lock()
    if patch:
        for name, val in (("SPEC_PATH", str(spec)), ("LOCK_PATH", str(ns.lock)), ("RUNS_DIR", str(ns.runs)),
                          ("RECEIPTS_DIR", str(ns.receipts)), ("TEST_FILE", str(stub_file)),
                          ("EXPECTED_KAT_ITEMS", 3), ("DESIGNED_SKIPS", {})):
            monkeypatch.setattr(launcher, name, val, raising=False)
    return ns


def _cli_cell(ns, cell_id="B1-fake", run_id="RUN-x", receipt=None):
    argv = ["cell", "--cell-id", cell_id, "--plan", str(ns.plan), f"--run-id={run_id}"]
    if receipt:
        argv += ["--selftest-receipt", str(receipt)]
    return launcher.main(argv)


def _spy_run_cell(monkeypatch):
    """Replace run_cell and spec_from_plan_cell: records that a cell would have run, computes nothing."""
    calls = []
    monkeypatch.setattr(launcher, "spec_from_plan_cell", lambda cell: [{"arm": cell["arm"], "cell_id": cell["cell_id"]}])

    def fake(spec, outdir, kat, **kw):
        calls.append(spec["cell_id"])
        return {"status": "completed", "validity": {"status": "valid"}}
    monkeypatch.setattr(launcher, "run_cell", fake)
    return calls


# ---- FX-2 (F-1 a): the lock binds tests/test_kat.py
def test_fx2_lock_binds_the_test_file(tmp_path, monkeypatch, capsys):
    ns = _scratch(tmp_path, monkeypatch)
    assert launcher.check_approval(str(ns.spec), str(ns.lock), str(ns.plan)) == (True, [])
    ns.write_lock(test_file_sha256=None)
    ok, reasons = launcher.check_approval(str(ns.spec), str(ns.lock), str(ns.plan))
    assert not ok and any("test_file_sha256" in r for r in reasons)
    lock = json.loads(ns.lock.read_text())
    del lock["test_file_sha256"]
    ns.lock.write_text(json.dumps(lock))
    assert not launcher.check_approval(str(ns.spec), str(ns.lock), str(ns.plan))[0]
    ns.write_lock()
    assert launcher.check_approval(str(ns.spec), str(ns.lock), str(ns.plan))[0]
    ns.stub.write_text("def test_placeholder(): pass\n")                  # replaced after the lock was written (S14)
    ok, reasons = launcher.check_approval(str(ns.spec), str(ns.lock), str(ns.plan))
    assert not ok and any("test_file_sha256" in r for r in reasons)
    spy = _spy_run_cell(monkeypatch)
    rc = _cli_cell(ns)
    assert rc == launcher.EXIT_REFUSED and spy == [] and not ns.runs.exists()
    assert "test_file_sha256" in capsys.readouterr().err
    assert launcher.CODE_FILES == ["fqn.py", "curves.py", "semaev.py", "counters.py", "kernel.c", "launcher.py",
                                   "make_trial_plan.py"]


# ---- FX-3 (F-1 b): the self-test is isolated from repository configuration
def test_fx3_hostile_repository_tree_still_collects_every_item(tmp_path):
    root = tmp_path / "repo"
    code = root / "experiments" / "EXP-MONO-1a1be2" / "code"
    (code / "tests").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[tool.pytest.ini_options]\naddopts = '-k no_such_name'\n")
    (root / "conftest.py").write_text("def pytest_collection_modifyitems(items): del items[1:]\n")
    tf = code / "tests" / "test_stub.py"
    tf.write_text(STUB_OK)
    res = launcher.run_selftest_suite(str(tmp_path / "out"), str(tf), str(code), expected_items=3, designed=[])
    assert res["passed"], res["reasons"]
    assert res["collected"] == 3 and res["parsed"]["tests"] == 3
    assert os.path.realpath(res["rootdir"]) == os.path.realpath(code)


def test_fx3_pytest_addopts_in_the_parent_environment_does_not_deselect(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTEST_ADDOPTS", "-k no_such_name")
    monkeypatch.setenv("PYTEST_PLUGINS", "no_such_plugin_module")
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "elsewhere"))
    d = tmp_path / "c"
    d.mkdir()
    tf = d / "test_stub.py"
    tf.write_text(STUB_OK)
    res = launcher.run_selftest_suite(str(tmp_path / "out"), str(tf), str(d), expected_items=3, designed=[])
    assert res["passed"], res["reasons"]
    env = launcher.selftest_environment(str(d))
    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1" and env["PYTHONDONTWRITEBYTECODE"] == "1"
    assert "PYTEST_ADDOPTS" not in env and "PYTEST_PLUGINS" not in env and "PYTHONPATH" not in env
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([str(tmp_path / "elsewhere"), str(d)]))
    assert launcher.selftest_environment(str(d))["PYTHONPATH"] == str(d)


# ---- FX-4 (F-1 c): "pass in full" is checked
@pytest.mark.parametrize("stub,designed,why", [
    (STUB_EXTRA_SKIP, [], "skipped"), (STUB_FEWER, [], "expected 3"), (STUB_XFAIL, [], "xfail"),
    (STUB_XPASS, [], "xpassed"), (STUB_FAIL, [], "failures"), (STUB_OK, ["test_stub.py::test_one"], "skipped node ids"),
    (STUB_EXTRA_SKIP, ["test_stub.py::test_other"], "skipped node ids")],
    ids=["extra_skip", "one_fewer", "xfail", "xpass", "failure", "designed_skip_missing", "wrong_skip"])
def test_fx4_pass_in_full_refuses_extra_skip_fewer_items_xfail_failure_or_missing_designed_skip(
        tmp_path, stub, designed, why):
    d = tmp_path / "c"
    d.mkdir()
    tf = d / "test_stub.py"
    tf.write_text(stub)
    res = launcher.run_selftest_suite(str(tmp_path / "out"), str(tf), str(d), expected_items=3, designed=designed)
    assert not res["passed"] and any(why in r for r in res["reasons"]), res["reasons"]


def test_fx4_designed_skip_as_a_function_of_status_and_node_id_form(tmp_path):
    assert launcher.designed_skips("review_required") == [] and launcher.designed_skips(None) == []
    assert launcher.designed_skips("approved") == [
        "tests/test_kat.py::test_launcher_refuses_contract_cell_while_specification_not_approved"]
    # the exact designed skip passes; the node id form is the one parse_junit produces for tests/test_kat.py
    d = tmp_path / "code"
    (d / "tests").mkdir(parents=True)
    tf = d / "tests" / "test_kat.py"
    tf.write_text("import pytest\ndef test_a(): pass\ndef test_b(): pass\n"
                  "def test_launcher_refuses_contract_cell_while_specification_not_approved(): pytest.skip('d')\n")
    res = launcher.run_selftest_suite(str(tmp_path / "o"), str(tf), str(d), expected_items=3,
                                      designed=launcher.designed_skips("approved"))
    assert res["passed"], res["reasons"]
    res2 = launcher.run_selftest_suite(str(tmp_path / "o2"), str(tf), str(d), expected_items=3, designed=[])
    assert not res2["passed"]


# ---- FX-5 (F-1 d): launcher-written, host-keyed receipts, refused on any mismatch
def _make_receipt(ns):
    rc, path, msgs = launcher.write_selftest_receipt()
    assert rc == 0, msgs
    return path


def test_fx5_launcher_written_receipt_verifies_and_is_accepted_by_the_gate(tmp_path, monkeypatch):
    ns = _scratch(tmp_path, monkeypatch)
    path = _make_receipt(ns)
    assert os.path.realpath(path).startswith(os.path.realpath(ns.receipts) + os.sep)
    assert sorted(os.listdir(os.path.dirname(path))) == ["junit.xml", "receipt.json"]
    rec = json.loads(open(path).read())
    assert set(rec) == set(launcher.RECEIPT_FIELDS)
    assert rec["lock_sha256"] == launcher.sha256_file(str(ns.lock)) and rec["counts"]["tests"] == 3
    assert {"python_version", "numpy", "pytest", "compiler_path", "compiler_version_sha256", "compile_flags", "machine",
            "node", "kernel_release", "cpu_model"} <= set(rec["env_key"])
    ok, reasons, _, _ = launcher.verify_receipt(path)
    assert ok, reasons
    g = launcher.gate(str(ns.plan), path)
    assert g.startup_selftest["mode"] == "receipt" and g.startup_selftest["receipt_sha256"] == launcher.sha256_file(path)


def test_fx5_hand_written_receipt_is_refused_by_cell(tmp_path, monkeypatch, capsys):
    ns = _scratch(tmp_path, monkeypatch)
    spy = _spy_run_cell(monkeypatch)
    monkeypatch.setattr(launcher, "run_selftest_suite", lambda *a, **k: pytest.fail("fell through to a full run"),
                        raising=False)
    hand = {"code_sha256": launcher.code_sha256(), "test_file_sha256": launcher.sha256_file(str(ns.stub)),
            "result": "passed"}                                              # the 165da2 repro S12
    for where in (tmp_path / "hand.json", ns.receipts / "r1" / "receipt.json"):
        where.parent.mkdir(parents=True, exist_ok=True)
        where.write_text(json.dumps(hand))
        assert _cli_cell(ns, receipt=where) == launcher.EXIT_REFUSED
    assert spy == [] and not ns.runs.exists()
    assert "receipt" in capsys.readouterr().err


@pytest.mark.parametrize("field,value", [
    ("python_version", "3.0.0"), ("numpy", "0.0"), ("pytest", "0.0"), ("compiler_path", "/usr/bin/cc-other"),
    ("compiler_version_sha256", "0" * 64), ("compile_flags", ["-O0"]), ("machine", "other"), ("node", "other-host"),
    ("kernel_release", "0.0"), ("cpu_model", "other cpu")])
def test_fx5_receipt_with_one_env_key_field_altered_is_refused(tmp_path, monkeypatch, field, value, capsys):
    ns = _scratch(tmp_path, monkeypatch)
    path = _make_receipt(ns)
    rec = json.load(open(path))
    rec["env_key"][field] = value
    json.dump(rec, open(path, "w"))
    spy = _spy_run_cell(monkeypatch)
    monkeypatch.setattr(launcher, "run_selftest_suite", lambda *a, **k: pytest.fail("fell through to a full run"),
                        raising=False)
    assert _cli_cell(ns, receipt=path) == launcher.EXIT_REFUSED
    assert spy == [] and not ns.runs.exists()
    assert "env_key" in capsys.readouterr().err


def test_fx5_receipt_outside_the_directory_or_with_edited_junit_or_fields_is_refused(tmp_path, monkeypatch):
    ns = _scratch(tmp_path, monkeypatch)
    path = _make_receipt(ns)
    outside = tmp_path / "elsewhere"
    shutil.copytree(os.path.dirname(path), outside)
    ok, reasons, _, _ = launcher.verify_receipt(str(outside / "receipt.json"))
    assert not ok and any("inside" in r for r in reasons)
    link = tmp_path / "link"
    link.symlink_to(os.path.dirname(path))
    assert launcher.verify_receipt(str(link / "receipt.json"))[0]            # resolves inside: accepted
    ok, reasons, _, _ = launcher.verify_receipt(str(ns.receipts / ".." / "elsewhere" / "receipt.json"))
    assert not ok
    junit = os.path.join(os.path.dirname(path), "junit.xml")
    text = open(junit).read()
    open(junit, "w").write(text.replace("test_one", "test_uno"))             # junit.xml edited
    ok, reasons, _, _ = launcher.verify_receipt(path)
    assert not ok and any("junit_sha256" in r for r in reasons)
    open(junit, "w").write(text)
    assert launcher.verify_receipt(path)[0]
    good = json.load(open(path))
    p2 = os.path.join(os.path.dirname(path), "receipt.json")
    for field, value in (("code_sha256", "0" * 64), ("test_file_sha256", "0" * 64), ("lock_sha256", "0" * 64),
                         ("junit_sha256", "0" * 64), ("pytest_version", "0.0"), ("rootdir", "/tmp"),
                         ("skipped_node_ids", ["x"]), ("counts", {})):
        json.dump({**good, field: value}, open(p2, "w"))
        assert not launcher.verify_receipt(p2)[0], field
    json.dump({**good, "extra": 1}, open(p2, "w"))
    assert not launcher.verify_receipt(p2)[0]
    json.dump(good, open(p2, "w"))
    assert launcher.verify_receipt(p2)[0]


def test_fx5_selftest_subcommand_refuses_before_approval_and_writes_nothing():
    real_dir = launcher.RECEIPTS_DIR
    before = os.path.exists(real_dir)
    assert launcher.main(["selftest"]) == launcher.EXIT_REFUSED            # the specification is not approved
    assert os.path.exists(real_dir) == before


# ---- FX-6 (F-1 e): the package records the gate and the self-test
def _fake_ident(F, E, seed="x"):
    return {"q": F.q, "n": F.n, "g": list(F.g), "a": list(E.a), "b": list(E.b), "N": 10, "t2": 0, "B": 4,
            "size_X": 2, "curve_seed": {"seed_string": seed, "seed_int": "1"}}


def _fake_b1(cell_id="B1-fake", mismatch=0, ident=None):
    F, E, _ = kat_curve(13, 2, "fx6")
    ident = ident or _fake_ident(F, E)
    spec = {"arm": "B1", "cell_id": cell_id, "n": 2, "m": 2, "q": 13, "curve_seed": "x", "tuple_seed": "t",
            "instances": [{"q": 13, "curve_seed": "x", "identity": ident}]}
    tally = dict.fromkeys(launcher.TALLY_KEYS, 0)
    tally.update(tuples=5, gl_mismatch_generic=mismatch, chi_patterns={"++|split": 5})
    raw = {"arm": "B1", "cell_id": cell_id, "instances": [{"q": 13, "n": 2, "sample": "primary", "tuple_seed": "t",
                                                           "B": 4, "t2": 0, "size_X": 2, "tally": tally,
                                                           "wall_seconds": 0.1}]}
    summ = {"cell_id": cell_id, "instances": [{"q": 13, "sample": "primary", "tally": tally}]}
    return spec, raw, summ


def _fake_ident_fields():
    F, E, _ = kat_curve(13, 2, "fx6")
    return F, E


def _stub_counters(monkeypatch):
    monkeypatch.setattr(launcher.counters, "build_kernel", lambda *a, **k: "unused.so")
    monkeypatch.setattr(launcher.counters, "Kernel", lambda path: object())


def test_fx6_run_cell_without_a_gate_result_raises(tmp_path):
    spec, raw, summ = _fake_b1()
    with pytest.raises(PermissionError):
        launcher.run_cell(spec, str(tmp_path / "p"), kat=False, kernel=object())
    with pytest.raises(PermissionError):
        launcher.run_cell(spec, str(tmp_path / "p"), kat=False, kernel=object(), gate=object())
    assert not (tmp_path / "p").exists()


@pytest.mark.parametrize("mode", ["ran", "receipt"])
def test_fx6_contract_package_carries_gate_and_selftest_blocks_and_copies(tmp_path, monkeypatch, mode):
    import yaml
    ns = _scratch(tmp_path, monkeypatch)
    path = _make_receipt(ns) if mode == "receipt" else None
    g = launcher.gate(str(ns.plan), path)
    spec, raw, summ = _fake_b1()
    monkeypatch.setattr(launcher, "run_arm_b", lambda spec, kernel, derived, log, workers=1: (raw, summ, None))
    out = tmp_path / "pkg"
    launcher.run_cell(spec, str(out), kat=False, kernel=object(), gate=g, run_id="RUN-t")
    man = yaml.safe_load((out / "manifest.yaml").read_text())
    gb, sb = man["gate"], man["startup_selftest"]
    assert gb == {"specification_sha256": launcher.sha256_file(str(ns.spec)), "lock_sha256": launcher.sha256_file(str(ns.lock)),
                  "trial_plan_sha256": launcher.sha256_file(str(ns.plan)), "code_sha256": launcher.code_sha256(),
                  "test_file_sha256": launcher.sha256_file(str(ns.stub)), "check_approval_passed": True}
    assert set(sb) == {"mode", "receipt_sha256", "junit_sha256", "tests", "passed", "skipped_node_ids", "failures",
                       "errors", "pytest_version", "rootdir", "inifile", "env_key"}
    assert sb["mode"] == mode and sb["tests"] == 3 and sb["failures"] == sb["errors"] == 0
    assert sb["junit_sha256"] == launcher.sha256_file(str(out / "selftest" / "junit.xml"))
    if mode == "receipt":
        assert sb["receipt_sha256"] == launcher.sha256_file(str(out / "selftest" / "receipt.json"))
    else:
        assert sb["receipt_sha256"] is None and not (out / "selftest" / "receipt.json").exists()


# ---- FX-7 (N-1): the large-Q index KAT that kills the 32-bit truncation mutant (M5)
@pytest.mark.parametrize("q,n", [(41, 6), (29, 7)])
def test_large_q_kernel_point_index_matches_python_index_beyond_2_32(q, n, kernel):
    F, E, _ = large_instance(q, n)
    pts = _random_points(F, E, curves.make_rng(f"kat|index|{q}|{n}"), 300)
    big = 0
    for P in pts:
        want = counters.target_index(F, P)
        assert kernel.point_index(E, P) == want
        big += want >= 2 ** 32
    assert kernel.point_index(E, None) == counters.target_index(F, None) == 2 * F.Q
    assert big >= 100                                    # vacuity guard: a property of the field size
    record("N1-large-q-point-index", f"q={q},n={n}", {"points": len(pts), "index_ge_2_32": int(big)})


@pytest.mark.parametrize("q,n", [(41, 6), (29, 7)])
def test_large_q_sampled_counter_on_constructed_targets_matches_membership_method(q, n, kernel):
    F, E, _ = large_instance(q, n)
    D, X, t2 = large_base(q, n)
    m, s = 2, 50
    keys = constructed_target_keys(F, E, D, m, s, curves.make_rng(f"kat|constructed|m2|{q}|{n}"))
    assert sum(1 for k in keys if k >= 2 ** 32) >= 10    # vacuity guards: properties of the construction
    want = membership_counts(E, D, m, keys)
    assert all(c > 0 for c in want)
    counts, st = kernel.run_sampled(E, m, D, np.array(keys, dtype=np.uint64), len(keys))
    assert [int(c) for c in counts] == want
    assert st["multisets"] == math.comb(len(D) + m - 1, m)
    record("N1-large-q-constructed-targets", f"q={q},n={n},m=2",
           {"keys_ge_2_32": int(sum(1 for k in keys if k >= 2 ** 32)), "counts": [int(c) for c in counts],
            "membership_counts": want})


# ---- FX-8 (N-2): validity and the F2 family stop
def _fake_conv_base(sum_obs=10, sum_exp=10, differ=0, with_ident=True):
    base = {"B": 4, "t2": 0, "N": 9, "size_X": 2, "S_size": 1, "generic_targets": 6, "special_targets_O_and_E2": 1,
            "recount": {"A": {"differ": differ, "compared": 9}, "M": {"differ": 0, "compared": 9},
                        "X": {"differ": 0, "differ_second": 0, "compared": 9}, "S": {"differ": 0, "compared": 9}},
            "conventions": {c: {"stats": {"all": {"targets": 9, "sum": 9, "sumsq": 9, "zeros": 3, "max": 2},
                                          "generic": {"targets": 6, "sum": 6, "sumsq": 6, "zeros": 2, "max": 2}}}
                            for c in ("A", "M", "S", "X")}, "wall_seconds": 0.1}
    if with_ident:
        base["identities"] = {"i_sum_M": {"observed": sum_obs, "expected": sum_exp}}
    return base


def _fake_a(cell_id="A-fake", f2_fail=False, recount_differ=0, ident=None):
    F, E, _ = kat_curve(13, 2, "fx6")
    spec = {"arm": "A", "cell_id": cell_id, "q": 13, "n": 2, "m": 2, "curve_seed": "x",
            "identity": ident or _fake_ident(F, E), "base_seeds": {}}
    raw = {"arm": "A", "cell_id": cell_id, "N": 9, "curve_generation": {},
           "bases": {"line": _fake_conv_base(differ=recount_differ),
                     "matched_random": _fake_conv_base(sum_obs=11 if f2_fail else 10)}}
    return spec, raw, launcher._cell_summary_arm_a(raw["bases"], True)


def _run_fake(tmp_path, monkeypatch, spec, raw, summ, name="pkg", kat=False, runs_parent=None):
    ns = _scratch(tmp_path / ("s" + name), monkeypatch) if not kat else None
    g = launcher.gate(str(ns.plan), None) if not kat else None
    arm = spec["arm"]
    fn = {"A": "run_arm_a", "B1": "run_arm_b", "B2": "run_arm_b", "C": "run_arm_c"}[arm]
    monkeypatch.setattr(launcher, fn, lambda spec, kernel, derived, log, *a, **k: (raw, summ, None))
    out = (runs_parent or tmp_path / "runs") / name
    import yaml
    launcher.run_cell(spec, str(out), kat=kat, kernel=object(), gate=g, run_id=name)
    return yaml.safe_load((out / "manifest.yaml").read_text()), out


def test_fx8_valid_baseline_and_status_field_is_kept_separate(tmp_path, monkeypatch):
    spec, raw, summ = _fake_b1()
    man, _ = _run_fake(tmp_path, monkeypatch, spec, raw, summ)
    assert man["status"] == "completed" and man["validity"] == {"status": "valid", "reasons": [], "readings_withheld": []}


def test_fx8_recount_differing_makes_the_cell_void(tmp_path, monkeypatch):
    spec, raw, summ = _fake_a(recount_differ=3)
    man, _ = _run_fake(tmp_path, monkeypatch, spec, raw, summ)
    assert man["status"] == "completed" and man["validity"]["status"] == "void"
    assert any("R1 recount differs" in r for r in man["validity"]["reasons"])


@pytest.mark.parametrize("key", ["gl_mismatch_generic", "gl_mismatch_nongeneric"])
def test_fx8_group_law_mismatch_makes_the_cell_void(tmp_path, monkeypatch, key):
    spec, raw, summ = _fake_b1()
    raw["instances"][0]["tally"][key] = 1
    man, _ = _run_fake(tmp_path, monkeypatch, spec, raw, summ)
    assert man["validity"]["status"] == "void" and any(key in r for r in man["validity"]["reasons"])


def test_fx8_raw_summary_disagreement_makes_the_cell_void(tmp_path, monkeypatch):
    spec, raw, summ = _fake_b1()
    orig = launcher._write_file

    def corrupt(path, text):
        if path.endswith("summary.json"):
            text = text.replace('"tuples": 5', '"tuples": 6')
        orig(path, text)
    monkeypatch.setattr(launcher, "_write_file", corrupt, raising=False)
    man, _ = _run_fake(tmp_path, monkeypatch, spec, raw, summ)
    assert man["validity"]["status"] == "void"
    assert any("summary.json differs" in r for r in man["validity"]["reasons"])


def test_fx8_raw_summary_agreement_reads_the_files_on_disk(tmp_path, monkeypatch):
    spec, raw, summ = _fake_b1()
    man, out = _run_fake(tmp_path, monkeypatch, spec, raw, summ)
    assert launcher.raw_summary_agreement(str(out), spec, True) == []
    (out / "summary.json").write_text(json.dumps({"cell_id": "B1-fake", "instances": []}))
    assert launcher.raw_summary_agreement(str(out), spec, True)
    (out / "summary.json").unlink()
    assert launcher.raw_summary_agreement(str(out), spec, True)


def test_fx8_identity_completeness_invalid_and_curve_rule_void(tmp_path, monkeypatch):
    F, E, _ = kat_curve(13, 2, "fx6")
    ident = _fake_ident(F, E)
    del ident["size_X"]
    spec, raw, summ = _fake_b1(ident=ident)
    man, _ = _run_fake(tmp_path, monkeypatch, spec, raw, summ, name="inv")
    assert man["validity"]["status"] == "invalid" and any("size_X" in r for r in man["validity"]["reasons"])
    ident = _fake_ident(F, E)
    ident["curve_seed"] = {"seed_string": "", "seed_int": "1"}
    spec, raw, summ = _fake_b1(ident=ident)
    man, _ = _run_fake(tmp_path, monkeypatch, spec, raw, summ, name="inv2")
    assert man["validity"]["status"] == "invalid" and any("seed" in r for r in man["validity"]["reasons"])
    F13 = fqn.FQ(13, 2)
    sing = _fake_ident(F13, E)
    sing.update(a=[10, 0], b=[2, 0])                      # in F_13: 4a^3 + 27b^2 = 0, singular (n = 2 coefficients)
    spec, raw, summ = _fake_b1(ident=sing)
    man, _ = _run_fake(tmp_path, monkeypatch, spec, raw, summ, name="sing")
    assert man["validity"]["status"] == "void" and any("singular" in r for r in man["validity"]["reasons"])
    jfq = _fake_ident(F13, E)
    jfq.update(a=[1, 0], b=[1, 0])                        # constant coefficients: j lies in F_13 (n = 2)
    spec, raw, summ = _fake_b1(ident=jfq)
    man, _ = _run_fake(tmp_path, monkeypatch, spec, raw, summ, name="jfq")
    assert man["validity"]["status"] == "void" and any("j in F_q" in r for r in man["validity"]["reasons"])


def test_fx8_failed_execution_is_void_and_keeps_its_execution_status(tmp_path, monkeypatch):
    spec, raw, summ = _fake_b1()
    ns = _scratch(tmp_path, monkeypatch)
    g = launcher.gate(str(ns.plan), None)

    def boom(*a, **k):
        raise RuntimeError("fabricated infrastructure failure")
    monkeypatch.setattr(launcher, "run_arm_b", boom)
    import yaml
    out = tmp_path / "failed"
    launcher.run_cell(spec, str(out), kat=False, kernel=object(), gate=g)
    man = yaml.safe_load((out / "manifest.yaml").read_text())
    assert man["status"] == "failed" and man["validity"]["status"] == "void"


def test_fx8_f2_failure_writes_the_sentinel_and_the_next_arm_a_cell_is_refused(tmp_path, monkeypatch, capsys):
    ns = _scratch(tmp_path, monkeypatch)
    _stub_counters(monkeypatch)
    spec, raw, summ = _fake_a(cell_id="A-fake", f2_fail=True)
    monkeypatch.setattr(launcher, "run_arm_a", lambda spec, kernel, derived, log: (raw, summ, None))
    monkeypatch.setattr(launcher, "spec_from_plan_cell", lambda cell: [spec if cell["arm"] == "A" else _fake_b1()[0]])
    assert _cli_cell(ns, cell_id="A-fake", run_id="RUN-a1") == 0          # execution status completed; validity void
    sentinel = ns.runs / "STOP-F2.json"
    assert sentinel.exists()
    stop = json.loads(sentinel.read_text())
    assert stop["cell_id"] == "A-fake" and stop["identity"] == "i_sum_M" and stop["utc"].endswith("Z")
    import yaml
    man = yaml.safe_load((ns.runs / "RUN-a1" / "manifest.yaml").read_text())
    assert man["validity"]["status"] == "void" and any("F2" in r for r in man["validity"]["reasons"])
    capsys.readouterr()
    # the next arm-A cell is refused; an arm-B cell is not
    ran = []
    monkeypatch.setattr(launcher, "run_cell", lambda spec, outdir, kat, **k: ran.append(spec["cell_id"]) or
                        {"status": "completed", "validity": {"status": "valid"}})
    assert _cli_cell(ns, cell_id="A-fake2", run_id="RUN-a2") == launcher.EXIT_REFUSED
    assert "F2 family stop" in capsys.readouterr().err and ran == []
    assert _cli_cell(ns, cell_id="B1-fake", run_id="RUN-b1") == 0 and ran == ["B1-fake"]
    # a second sentinel write never overwrites the first
    launcher.write_stop_f2(str(ns.runs), "A-other", "i_sum_M", "matched_random")
    assert json.loads(sentinel.read_text())["cell_id"] == "A-fake"


def test_fx8_kat_mode_never_writes_a_sentinel(tmp_path, monkeypatch):
    spec, raw, summ = _fake_a(f2_fail=True)
    monkeypatch.setattr(launcher, "run_arm_a", lambda spec, kernel, derived, log: (raw, summ, None))
    runs = tmp_path / "runs"
    launcher.run_cell(spec, str(runs / "k"), kat=True, kernel=object())
    assert not (runs / "STOP-F2.json").exists()
    import yaml
    assert "validity" not in yaml.safe_load((runs / "k" / "manifest.yaml").read_text())


def test_fx8_sentinel_is_not_written_for_a_passing_identity(tmp_path, monkeypatch):
    spec, raw, summ = _fake_a()
    man, out = _run_fake(tmp_path, monkeypatch, spec, raw, summ)
    assert man["validity"]["status"] == "valid" and not (out.parent / "STOP-F2.json").exists()


# ---- FX-9 (N-3) and FX-10 (N-4): arm-C lambda from the counted total; derived keys withheld in KAT mode
class _FakeKernel:
    def __init__(self, cf):
        self.cf = cf

    def run_sampled(self, E, m, pts, keys, nsampled):
        return np.arange(keys.size, dtype=np.uint32), {"multisets": 100, "cancellation_free": self.cf, "m_S": 4}


def _fake_armc(monkeypatch, counted):
    F, E, _ = kat_curve(13, 2, "fx9")
    D, X, t2 = E.factor_base()
    monkeypatch.setattr(counters, "s_set_indices", lambda kernel, E, D, m: np.array([0, 2], dtype=np.int64))
    monkeypatch.setattr(counters, "sample_targets", lambda kernel, E, s, rng, ex: (np.array([10, 20, 30], dtype=np.uint64), 7))
    r = counters.arm_c_cell(_FakeKernel(counted), E, D, 2, 3, None, 1000)
    return r, len(D), t2


def test_fx9_lambda_follows_the_counted_cancellation_free_total(monkeypatch):
    F, E, _ = kat_curve(13, 2, "fx9")
    D, X, t2 = E.factor_base()
    formula = counters.ncf_coefficient(len(D), t2, 2)
    r, B, t2 = _fake_armc(monkeypatch, formula + 7)
    assert r["lambda"] == Fraction(formula + 7 - 4, 1000 - 2)
    assert r["N_cf_formula"] == formula and r["ncf_counted_equals_formula"] is False
    r2, _, _ = _fake_armc(monkeypatch, formula)
    assert r2["lambda"] == Fraction(formula - 4, 998) and r2["ncf_counted_equals_formula"] is True


from fractions import Fraction  # noqa: E402


def _fake_c(counted_equals):
    F, E, _ = kat_curve(13, 2, "fx6")
    ident = _fake_ident(F, E)
    spec = {"arm": "C", "cell_id": "C-fake", "q": 13, "n": 2, "m": 2, "s": 8, "curve_seed": "x", "identity": ident,
            "target_seed": "kat|targets|fx", "base_seeds": {}}
    r = {"sampled_counts": np.array([0, 0, 1, 2, 0, 1, 0, 3]), "S_counts": np.array([5, 7]), "t2": 0, "S_size": 2,
         "draws": 64, "multisets": 100, "cancellation_free": 80, "m_S": 4,
         "N_cf_formula": 80 if counted_equals else 81, "lambda": Fraction(76, 90)}
    entry = launcher.arm_c_entry(r, 10, True, 0.1, "kat|targets|fx", None)
    raw = {"arm": "C", "cell_id": "C-fake", "N": 100, "N_method": "bsgs", "curve_generation": {}, "bases": {"line": entry}}
    cdf = {"cell_id": "C-fake", **launcher.arm_c_flat(entry, True)}
    summ = launcher._summary_arm_c("C-fake", 8, 10, 0, 100, raw["bases"], True)
    return spec, raw, summ, cdf


def test_fx9_ncf_mismatch_sets_the_flag_the_reason_and_withholds_p6(tmp_path, monkeypatch):
    for equal in (True, False):
        spec, raw, summ, cdf = _fake_c(equal)
        assert raw["bases"]["line"]["ncf_counted_equals_formula"] is equal
        ns = _scratch(tmp_path / f"s{equal}", monkeypatch)
        g = launcher.gate(str(ns.plan), None)
        monkeypatch.setattr(launcher, "run_arm_c", lambda spec, kernel, derived, log: (raw, summ, cdf))
        import yaml
        out = tmp_path / f"c{equal}"
        launcher.run_cell(spec, str(out), kat=False, kernel=object(), gate=g)
        v = yaml.safe_load((out / "manifest.yaml").read_text())["validity"]
        if equal:
            assert v == {"status": "valid", "reasons": [], "readings_withheld": []}
        else:
            assert "P2(vi) mismatch; P6 reading withheld (F7 first)" in v["reasons"] and v["readings_withheld"] == ["P6"]


def test_fx10_kat_mode_arm_c_package_omits_the_derived_keys(capsys, kernel):
    rc = launcher.main(["--kat", "kat", "--arm", "C", "--q", "13", "--n", "2", "--curve-seed", "kat|fx10", "--s", "10"])
    assert rc == 0
    d = json.loads(capsys.readouterr().out.strip().splitlines()[-1])["kat_dir"]
    try:
        keys = ("lambda", "lambda_exact", "N_cf_formula", "ncf_counted_equals_formula")
        raw = json.load(open(os.path.join(d, "raw-result.json")))
        cdf = json.load(open(os.path.join(d, "results", "KAT-C-n2-q13.cdf.json")))
        summ = json.load(open(os.path.join(d, "summary.json")))
        for role, e in raw["bases"].items():
            assert not any(k in e for k in keys)
        assert not any(k in cdf for k in keys) and not any(k in cdf.get("matched_random", {}) for k in keys)
        assert all(not any(k in b for k in keys) for b in summ["bases"].values())
    finally:
        shutil.rmtree(d, ignore_errors=True)
    r = {"sampled_counts": np.array([0, 1]), "S_counts": np.array([1]), "t2": 0, "S_size": 1, "draws": 4,
         "multisets": 9, "cancellation_free": 8, "m_S": 1, "N_cf_formula": 8, "lambda": Fraction(1, 2)}
    assert all(k in launcher.arm_c_entry(r, 3, True, 0.0) for k in keys)
    assert not any(k in launcher.arm_c_entry(r, 3, False, 0.0) for k in keys)


# ---- FX-11 (N-5): gate and record hardening, one test per item
@pytest.mark.parametrize("kw,needle", [({"authorized": False}, "execution_authorized"), ({"frozen": False}, "frozen")])
def test_fx11_1_gate_requires_execution_authorized_and_frozen(tmp_path, monkeypatch, kw, needle):
    ns = _scratch(tmp_path, monkeypatch, **kw)                  # the S15 repro: approved yet not authorized / frozen
    ok, reasons = launcher.check_approval(str(ns.spec), str(ns.lock), str(ns.plan))
    assert not ok and any(needle in r for r in reasons)


def test_fx11_1_lock_approved_by_must_equal_the_specifications(tmp_path, monkeypatch):
    ns = _scratch(tmp_path, monkeypatch)
    ns.write_lock(approved_by="someone-else")
    ok, reasons = launcher.check_approval(str(ns.spec), str(ns.lock), str(ns.plan))
    assert not ok and any("approved_by differs" in r for r in reasons)


@pytest.mark.parametrize("run_id", ["../x", "/abs/path", "a/b", "", ".hidden", "-x", "x" * 129, "a b", "..", "x\n"])
def test_fx11_2_run_id_is_sanitised_and_confined_to_runs(tmp_path, monkeypatch, run_id, capsys):
    ns = _scratch(tmp_path, monkeypatch)
    spy = _spy_run_cell(monkeypatch)
    with pytest.raises(ValueError):
        launcher.resolve_run_dir(run_id, str(ns.runs))
    assert _cli_cell(ns, run_id=run_id) == launcher.EXIT_REFUSED and spy == [] and not ns.runs.exists()
    assert launcher.resolve_run_dir("RUN-ok_1.2", str(ns.runs)) == os.path.join(str(ns.runs), "RUN-ok_1.2")


def test_fx11_3_cdf_json_carries_target_and_base_seeds(capsys, kernel):
    rc = launcher.main(["--kat", "kat", "--arm", "C", "--q", "13", "--n", "2", "--curve-seed", "kat|fx11", "--s", "10"])
    assert rc == 0
    d = json.loads(capsys.readouterr().out.strip().splitlines()[-1])["kat_dir"]
    try:
        cdf = json.load(open(os.path.join(d, "results", "KAT-C-n2-q13.cdf.json")))
        ts = "kat|targets|KAT-C-n2-q13"
        assert cdf["target_seed"] == {"string": ts, "int": curves.seed_int(ts)}
        assert cdf["base_seed"] == {"string": None, "int": None}               # the line base is not seeded
        bs = "kat|base|KAT-C-n2-q13|random|0"
        assert cdf["matched_random"]["base_seed"] == {"string": bs, "int": curves.seed_int(bs)}
        assert cdf["matched_random"]["target_seed"] == {"string": ts, "int": curves.seed_int(ts)}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_fx11_4_peak_rss_is_recorded_for_self_and_children(tmp_path):
    import yaml
    spec, raw, summ = _fake_b1()
    d = tmp_path / "k"
    spec = dict(spec, instances=[{"q": 13, "curve_seed": "kat|rss"}], tuples=10, group_law_subsample_fraction=0.1,
                max_tuples_per_instance=10)
    man = launcher.run_cell(spec, str(d), kat=True, kernel=object())
    on_disk = yaml.safe_load((d / "manifest.yaml").read_text())
    for src in (man, on_disk):
        assert {"peak_rss_kb_self", "peak_rss_kb_children", "peak_rss_kb_total_upper"} <= set(src)


def test_fx11_5_stray_python_file_in_code_dir_refuses_the_launcher(tmp_path):
    code = tmp_path / "code"
    (code / "tests").mkdir(parents=True)
    shutil.copy(os.path.join(CODE, "launcher.py"), code / "launcher.py")
    (code / "numpy.py").write_text("raise SystemExit(0)\n")
    assert launcher.stray_python_files(str(code)) == ["numpy.py"]
    r = subprocess.run([sys.executable, str(code / "launcher.py"), "environment", "--out", str(tmp_path / "e.json")],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert r.returncode == launcher.EXIT_REFUSED and "numpy.py" in r.stderr and not (tmp_path / "e.json").exists()
    (code / "numpy.py").unlink()
    (code / "tests" / "conftest.py").write_text("")
    (code / "tests" / "__init__.py").write_text("")
    (code / "yaml.py").write_text("")
    assert launcher.stray_python_files(str(code)) == ["tests/__init__.py", "tests/conftest.py", "yaml.py"]
    assert launcher.stray_python_files(CODE) == []                     # the real code directory is clean


# ---- FX-13: the start-up suite's expected size is the collected count
def test_expected_kat_items_equals_the_collected_count_and_the_designed_skip_is_a_collected_node():
    argv = [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "--noconftest", "-c",
            os.devnull, "--rootdir", CODE, os.path.join(CODE, "tests", "test_kat.py")]
    r = subprocess.run(argv, capture_output=True, text=True, cwd=CODE,
                       env=launcher.selftest_environment(CODE))
    ids = [ln for ln in r.stdout.splitlines() if "::" in ln]
    assert len(ids) == launcher.EXPECTED_KAT_ITEMS, (len(ids), launcher.EXPECTED_KAT_ITEMS)
    assert launcher.SKIP_NODE_REFUSAL in ids
    record("FX13-collected", "tests/test_kat.py", {"collected": len(ids), "EXPECTED_KAT_ITEMS": launcher.EXPECTED_KAT_ITEMS})
