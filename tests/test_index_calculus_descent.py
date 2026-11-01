"""Tests for index_calculus.descent: Gaudry/Diem decomposition over F_{p^n} by Weil descent."""

from __future__ import annotations

import json
import random

import pytest

from crypto_autoresearcher.index_calculus import descent as dsc
from crypto_autoresearcher.index_calculus import diagram
from crypto_autoresearcher.index_calculus import msolve as ms
from crypto_autoresearcher.index_calculus.__main__ import main

needs_msolve = pytest.mark.skipif(not ms.available(), reason="msolve not installed")


# -- field and curve ---------------------------------------------------------------

@pytest.mark.parametrize("p,n", [(31, 2), (101, 3), (53, 4), (17, 5)])
def test_extension_field_arithmetic(p, n):
    F = dsc.ExtField(p, n)
    assert dsc.is_irreducible(F.modulus, p)
    rng = random.Random(p * n)
    for _ in range(40):
        a, b, c = F.random(rng), F.random(rng), F.random(rng)
        assert F.mul(a, F.add(b, c)) == F.add(F.mul(a, b), F.mul(a, c))
        assert F.mul(F.mul(a, b), c) == F.mul(a, F.mul(b, c))
        if any(a):
            assert F.mul(a, F.inv(a)) == F.one()
        s = F.mul(a, a)
        r = F.sqrt(s)
        assert r is not None and F.mul(r, r) == s and r == min(r, F.neg(r))
    x = F.elem([0, 1])
    assert F.pow(x, F.q) == x  # Frobenius^n is the identity on F_q


def test_reducible_modulus_is_refused():
    p = 31
    reducible = [30, 0, 1]  # x^2 - 1 = (x - 1)(x + 1)
    assert not dsc.is_irreducible(reducible, p)
    with pytest.raises(ValueError, match="reducible"):
        dsc.ExtField(p, 2, modulus=reducible)


def test_group_law_over_the_extension():
    F = dsc.ExtField(101, 3)
    E = dsc.ExtCurve.random(F, random.Random(1))
    rng = random.Random(2)
    pts = []
    while len(pts) < 3:
        P = E.lift_x(F.random(rng))
        if P is not None:
            pts.append(P)
    P, Q, S = pts
    assert all(E.on_curve(T) for T in (P, Q, S, E.add(P, Q), E.add(P, P)))
    assert E.add(E.add(P, Q), S) == E.add(P, E.add(Q, S))
    assert E.add(P, E.neg(P)) is None
    R, xs = dsc.planted_target(E, 3, random.Random(3))
    assert E.on_curve(R) and dsc.signed_relation(E, xs, R) is not None


# -- the descended systems -----------------------------------------------------------

def _signed_points(E, m, rng):
    pts = []
    while len(pts) < m:
        P = E.factor_base_point(rng.randrange(E.F.p))
        if P is not None:
            pts.append(P if rng.random() < 0.5 else E.neg(P))
    return pts


def _wire_coords(E, dg, pts):
    producer = {b.c[1]: b for b in dg.boxes if b.c[0] == "u"}
    cache = {}

    def point(term):
        if term[0] == "x":
            return pts[term[1]]
        if term[1] not in cache:
            b = producer[term[1]]
            cache[term[1]] = E.add(point(b.a), point(b.b))
        return cache[term[1]]

    return [c for k in range(dg.wires) for c in point(("u", k))[0]]


@pytest.mark.parametrize("topology,m,n", [("chain", 2, 2), ("chain", 3, 3), ("chain", 4, 4),
                                          ("tree", 3, 3), ("tree", 4, 4), ("chain", 3, 2),
                                          ("monolithic", 2, 2), ("monolithic", 3, 3),
                                          ("monolithic", 3, 4)])
def test_descended_system_vanishes_at_a_planted_decomposition(topology, m, n):
    F = dsc.ExtField(101, n)
    E = dsc.ExtCurve.random(F, random.Random(10 + m))
    pts = _signed_points(E, m, random.Random(20 + m))
    R = None
    for P in pts:
        R = E.add(R, P)
    system = dsc.descent_system(E, R[0], m, random.Random(0), topology)
    xs = [P[0][0] for P in pts]
    values = xs if topology == "monolithic" else xs + _wire_coords(E, diagram.build(topology, m), pts)
    assert system.names == dsc.descent_names(m, n, topology)
    assert len(system.names) == len(values) + 1
    form = system.polys[-1]
    z = (-sum(c * values[e.index(1)] for e, c in form.items() if e[-1] == 0)) % F.p
    for poly in system.polys:
        assert ms.evaluate(poly, values + [z], F.p) == 0
    plan = dsc.descent_plan(topology, m, n)
    assert plan["unknowns"] == len(values)
    assert len(system.polys) - 1 <= plan["equations"]
    assert "(" not in system.render()


def test_monolithic_descent_has_the_s4_degree():
    F = dsc.ExtField(101, 3)
    E = dsc.ExtCurve.random(F, random.Random(4))
    R, _ = dsc.planted_target(E, 3, random.Random(4))
    system = dsc.descent_system(E, R[0], 3, random.Random(0), "monolithic")
    for poly in system.polys[:-1]:
        assert max(k[i] for k in poly for i in range(3)) == 4
    with pytest.raises(ValueError, match="m <= 3"):
        dsc.descent_system(E, R[0], 4, random.Random(0), "monolithic")


# -- solving, against the group law -----------------------------------------------------

@needs_msolve
@pytest.mark.parametrize("p,n,targets", [(31, 2, 4), (503, 3, 2)])
def test_descent_decomposition_agrees_with_group_law(p, n, targets):
    # p = 503 at n = 3: msolve's separating-form check is unreliable at small p
    # (see decompose_descent); the brute force is computed once per target.
    m = n
    F = dsc.ExtField(p, n)
    E = dsc.ExtCurve.random(F, random.Random(7))
    rng = random.Random(8)
    nonempty = 0
    for k in range(targets):
        if k % 2:
            R = None
            while R is None:
                R = E.lift_x(F.random(rng))
        else:
            R, _ = dsc.planted_target(E, m, rng)
        truth = dsc.decompositions_bruteforce(E, R, m)
        nonempty += bool(truth)
        for topology in diagram.TOPOLOGIES:
            out = dsc.decompose_descent(E, R, m, topology=topology, timeout=300)
            assert out.status in ("ok", "no_solution"), out
            assert out.topology == topology and out.plan["topology"] == topology
            assert out.relations == truth, topology
    assert nonempty >= 1  # the planted targets


@needs_msolve
def test_descent_cli(capsys):
    rc = main(["descent", "--p", "31", "--n", "2", "--check"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert [r["topology"] for r in out["runs"]] == list(diagram.TOPOLOGIES)
    assert all(r["agrees_with_bruteforce"] for r in out["runs"])
    assert out["bruteforce_relations"]
