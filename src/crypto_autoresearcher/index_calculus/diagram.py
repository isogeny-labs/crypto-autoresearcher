"""Semaev decomposition systems as string diagrams of S_3 boxes.

Graphical Algebraic Geometry (Gao, Shaikh, Kissinger, arXiv:2605.13993,
KN-LIT-c9e59d) gives a sound and complete diagrammatic calculus for networks of
polynomial constraints: a diagram's semantics is a span of affine varieties (or
of F_q-rational loci), and composing two diagrams along a shared wire is the
pullback, i.e. elimination of that wire.  A point-decomposition system is such
a network.  Each ``S_3(a, b, c) = 0`` is a box, each factor-base x-coordinate
is an outer wire, each partial sum is an internal wire, and x(R) is a constant.

What changes between presentations is only *which wires are contracted
symbolically before the solver sees the system* and *how the boxes are wired*:

``chain``       Semaev's chained presentation (ePrint 2015/310, KN-TECH-b18366),
                every partial sum kept as an unknown; the m-2 wires form a path.
``tree``        the same boxes as a balanced binary merge tree; still m-2
                internal wires (LEAD-ICE-semaev-chain-cost-model: variable and
                equation counts are topology-invariant), but different
                incidence, so different Groebner behaviour is possible.
``monolithic``  every internal wire contracted by resultants before solving,
                i.e. the classical single equation S_{m+1}(x_1..x_m, x(R)).
                Implemented here for m <= 3 (one quadratic-quadratic resultant).

All three have the same F_p-rational solutions in x_1..x_m whenever every
internal wire value of a decomposition lies in F_p, which holds for every
decomposition into F_p-rational points.  The monolithic system can in principle
admit extra x-tuples whose partial sums are not F_p-rational (they need the
order-2 coincidences of KN-TECH-b18366, "Correctness conditions", item 2); the
decomposition engine lifts and verifies every solution by point addition, so
such tuples are counted as unlifted, never as relations.

Evaluating a sub-diagram as its finite rational locus instead of solving it
symbolically is the third kind of choice the calculus names; in this package
that is what ``decompose.py`` and ``tails.py`` already do (a table of tails is
the locus of the tail sub-diagram, joined on its wire).

This module only builds systems and describes them; it makes no claim about
which presentation is cheaper.  That is a measurement question
(LEAD-ICE-gag-contraction-planner).
"""

from __future__ import annotations

from dataclasses import dataclass, field

TOPOLOGIES = ("chain", "tree", "monolithic")
MONOLITHIC_MAX_M = 3

Poly = dict[tuple[int, ...], int]


# -- terms and boxes --------------------------------------------------------------
# A term is ("x", i) for factor-base wire i (0-based), ("u", k) for internal
# wire k (0-based) or ("R",) for the target's x-coordinate.

@dataclass(frozen=True)
class Box:
    """One constraint S_3(a, b, c) = 0 over three terms."""
    a: tuple
    b: tuple
    c: tuple

    def terms(self) -> tuple[tuple, tuple, tuple]:
        return self.a, self.b, self.c


@dataclass
class Diagram:
    topology: str
    m: int
    boxes: list[Box] = field(default_factory=list)
    wires: int = 0  # internal wires u_0..u_{wires-1}

    def incidence(self) -> dict[int, list[int]]:
        """Internal wire -> indices of the boxes it touches (always exactly two)."""
        out: dict[int, list[int]] = {k: [] for k in range(self.wires)}
        for i, box in enumerate(self.boxes):
            for t in box.terms():
                if t[0] == "u":
                    out[t[1]].append(i)
        return out

    def depth(self) -> int:
        """Longest path, in boxes, from an outer wire to the R box."""
        producer = {box.c[1]: i for i, box in enumerate(self.boxes) if box.c[0] == "u"}

        def d(term) -> int:
            if term[0] != "u":
                return 0
            box = self.boxes[producer[term[1]]]
            return 1 + max(d(box.a), d(box.b))

        root = next(box for box in self.boxes if box.c == ("R",))
        return 1 + max(d(root.a), d(root.b))


def chain(m: int) -> Diagram:
    """S_3(x1, x2, u1), S_3(u_k, x_{k+2}, u_{k+1}), S_3(u_{m-2}, x_m, R)."""
    _check_m(m)
    if m == 2:
        return Diagram("chain", 2, [Box(("x", 0), ("x", 1), ("R",))], 0)
    boxes = [Box(("x", 0), ("x", 1), ("u", 0))]
    for k in range(m - 3):
        boxes.append(Box(("u", k), ("x", k + 2), ("u", k + 1)))
    boxes.append(Box(("u", m - 3), ("x", m - 1), ("R",)))
    return Diagram("chain", m, boxes, m - 2)


def tree(m: int) -> Diagram:
    """A balanced binary merge tree: split the leaves in half, recursively."""
    _check_m(m)
    dg = Diagram("tree", m)

    def build(leaves: list[int]) -> tuple:
        if len(leaves) == 1:
            return ("x", leaves[0])
        mid = len(leaves) // 2
        left, right = build(leaves[:mid]), build(leaves[mid:])
        w = ("u", dg.wires)
        dg.wires += 1
        dg.boxes.append(Box(left, right, w))
        return w

    leaves = list(range(m))
    mid = m // 2
    left, right = build(leaves[:mid]), build(leaves[mid:])
    dg.boxes.append(Box(left, right, ("R",)))
    return dg


def build(topology: str, m: int) -> Diagram:
    if topology == "chain":
        return chain(m)
    if topology == "tree":
        return tree(m)
    if topology == "monolithic":
        if m > MONOLITHIC_MAX_M:
            raise ValueError(f"monolithic topology is implemented for m <= {MONOLITHIC_MAX_M}")
        return chain(m)  # contracted symbolically by system builders
    raise ValueError(f"unknown topology {topology!r}; expected one of {TOPOLOGIES}")


def plan(topology: str, m: int) -> dict:
    """What the solver will see, before it sees it (for receipts)."""
    dg = build(topology, m)
    contracted = dg.wires if topology == "monolithic" else 0
    unknowns = m + dg.wires - contracted
    return {
        "topology": topology,
        "m": m,
        "boxes": len(dg.boxes),
        "internal_wires": dg.wires,
        "contracted_wires": contracted,
        "unknowns": unknowns,  # before the separating variable
        "semaev_equations": len(dg.boxes) - contracted,
        "max_degree_per_variable": 2 ** (m - 1) if contracted else 2,
        "depth": dg.depth(),
    }


def _check_m(m: int) -> None:
    if m < 2:
        raise ValueError("m must be >= 2")


# -- sparse multivariate arithmetic over F_p -------------------------------------

def padd(f: Poly, g: Poly, p: int) -> Poly:
    out = dict(f)
    for k, v in g.items():
        out[k] = (out.get(k, 0) + v) % p
    return {k: v for k, v in out.items() if v}


def pscale(f: Poly, c: int, p: int) -> Poly:
    return {k: v * c % p for k, v in f.items() if v * c % p}


def pmul(f: Poly, g: Poly, p: int) -> Poly:
    out: Poly = {}
    for k1, v1 in f.items():
        for k2, v2 in g.items():
            k = tuple(a + b for a, b in zip(k1, k2))
            out[k] = (out.get(k, 0) + v1 * v2) % p
    return {k: v for k, v in out.items() if v}


def coefficients_in(f: Poly, var: int) -> dict[int, Poly]:
    """f as a polynomial in variable ``var``: {exponent: coefficient with var zeroed}."""
    out: dict[int, Poly] = {}
    for k, v in f.items():
        e = k[var]
        rest = k[:var] + (0,) + k[var + 1:]
        out.setdefault(e, {})[rest] = v
    return out


def resultant_quadratic(f: Poly, g: Poly, var: int, p: int) -> Poly:
    """Res_var(f, g) for f, g of degree <= 2 in ``var`` (Sylvester, 4x4).

    With f = a2 X^2 + a1 X + a0 and g = b2 X^2 + b1 X + b0,
    Res = (a2 b0 - a0 b2)^2 - (a2 b1 - a1 b2)(a1 b0 - a0 b1).
    """
    fc, gc = coefficients_in(f, var), coefficients_in(g, var)
    if max(fc) > 2 or max(gc) > 2:
        raise ValueError("resultant_quadratic needs degree <= 2 in the eliminated variable")
    a0, a1, a2 = (fc.get(i, {}) for i in range(3))
    b0, b1, b2 = (gc.get(i, {}) for i in range(3))
    neg = p - 1
    t1 = padd(pmul(a2, b0, p), pscale(pmul(a0, b2, p), neg, p), p)
    t2 = padd(pmul(a2, b1, p), pscale(pmul(a1, b2, p), neg, p), p)
    t3 = padd(pmul(a1, b0, p), pscale(pmul(a0, b1, p), neg, p), p)
    return padd(pmul(t1, t1, p), pscale(pmul(t2, t3, p), neg, p), p)
