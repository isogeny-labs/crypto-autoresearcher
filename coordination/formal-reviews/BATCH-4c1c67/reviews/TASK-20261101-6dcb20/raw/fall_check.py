#!/usr/bin/env python3
"""Independent checker for BATCH-4c1c67 J2 (written from scratch, from blind-input.yaml only).

Polynomials over F_2 are frozensets of exponent tuples. For a list S and degree D the
script decides EXACTLY whether a (fake) fall exists, and prints a witness.

Exactness: deg(g*s) = deg g + deg s over the domain F_2[X], so for true falls the cofactor
g_i can be taken in the span of monomials of degree <= D - deg s_i without loss.  For fake
falls red(g*s) depends only on red(g), so cofactors range over multilinear h without loss.
Each generator's admissible products form a subspace P_i (degree <= D); a tuple is "top"
iff some slot uses a degree-exactly-D element.  With an echelon basis whose pivots are the
highest-degree monomials, a slot element has degree D iff it uses a basis vector whose pivot
has degree D.  K = {c : sum has no degree-D part}.  A fall exists iff K is contained in
neither {c_top = 0} nor ker(sum) (a vector space is never the union of two proper subspaces).
"""
from itertools import product, combinations
import sys

def mul(p, q):
    out = set()
    for a in p:
        for b in q:
            m = tuple(x + y for x, y in zip(a, b))
            out ^= {m}
    return frozenset(out)

def add(p, q): return frozenset(set(p) ^ set(q))
def deg(p): return max((sum(m) for m in p), default=-1)   # -1 stands for -infinity
def red(p):
    out = set()
    for m in p:
        out ^= {tuple(min(e, 1) for e in m)}
    return frozenset(out)

def monos(N, d):
    return [m for m in product(range(d + 1), repeat=N) if sum(m) <= d] if d >= 0 else []

def mlmonos(N): return list(product((0, 1), repeat=N))

VARS = None
def show(p):
    if not p: return "0"
    def mono(m):
        s = "".join(f"{v}" + (f"^{e}" if e > 1 else "") for v, e in zip(VARS, m) if e)
        return s or "1"
    return " + ".join(mono(m) for m in sorted(p, key=lambda m: (-sum(m), [-e for e in m])))

def P(s, names):
    """parse 'X^2 Y + X' style"""
    out = set()
    for term in s.split("+"):
        term = term.strip(); e = [0]*len(names)
        if term != "1":
            for f in term.split():
                v, _, k = f.partition("^"); e[names.index(v)] += int(k or 1)
        out ^= {tuple(e)}
    return frozenset(out)

def echelon(vecs):
    """vecs: list of (poly, cofactor_poly). Returns echelon basis keyed by pivot monomial
    (pivot = highest monomial in (degree, lex) order)."""
    key = lambda m: (sum(m), m)
    basis = {}
    for p, c in vecs:
        while p:
            piv = max(p, key=key)
            if piv in basis:
                bp, bc = basis[piv]; p = add(p, bp); c = add(c, bc)
            else:
                basis[piv] = (p, c); break
    # full reduction not needed for leading-term property
    return basis

def fall(S, N, D, fake=False, unbounded=None):
    """Return witness (cofactors, products, sum) or None.  unbounded=B: control-1 variant,
    products of any degree, cofactors up to degree B, need some product deg >= D."""
    slots = []  # per generator: list of (poly, cof, is_top)
    for s in S:
        if fake:
            imgs = [(red(mul(frozenset({m}), s)), frozenset({m})) for m in mlmonos(N)]
        elif unbounded is not None:
            imgs = [(mul(frozenset({m}), s), frozenset({m})) for m in monos(N, unbounded)]
        else:
            imgs = [(mul(frozenset({m}), s), frozenset({m})) for m in monos(N, D - deg(s))]
        imgs = [(p, c) for p, c in imgs if p]
        B = echelon(imgs)
        if unbounded is None:
            items = [(p, c, sum(piv) == D) for piv, (p, c) in B.items() if sum(piv) <= D]
        else:
            items = [(p, c, sum(piv) >= D) for piv, (p, c) in B.items()]
        slots.append(items)
    flat = [(i, p, c, t) for i, it in enumerate(slots) for (p, c, t) in it]
    # map c -> high part of sum (deg >= D); find kernel K
    rows = []
    for k, (i, p, c, t) in enumerate(flat):
        hi = frozenset(m for m in p if sum(m) >= D)
        rows.append((hi, frozenset({(k,)})))  # cof = set of indices
    K = []
    basis = {}
    key = lambda m: (sum(m), m)
    for hi, idx in rows:
        while hi:
            piv = max(hi, key=key)
            if piv in basis:
                bh, bi = basis[piv]; hi = add(hi, bh); idx = add(idx, bi)
            else:
                basis[piv] = (hi, idx); break
        if not hi: K.append(idx)
    def evaluate(idx):
        prods = [frozenset()] * len(S); cofs = [frozenset()] * len(S); top = False
        for (k,) in idx:
            i, p, c, t = flat[k]
            prods[i] = add(prods[i], p); cofs[i] = add(cofs[i], c)
        sm = frozenset()
        for p in prods: sm = add(sm, p)
        if unbounded is None:
            top = any(deg(p) == D for p in prods)
        else:
            top = any(deg(p) >= D for p in prods)
        return cofs, prods, sm, top
    a = next((k for k in K if evaluate(k)[3]), None)
    b = next((k for k in K if evaluate(k)[2]), None)
    if a is None or b is None: return None
    for cand in (a, b, add(a, b)):
        cofs, prods, sm, top = evaluate(cand)
        if top and sm and deg(sm) < D: return cofs, prods, sm
    raise AssertionError("union-of-subspaces argument failed")

def verify(S, D, cofs, fake):
    """Independent direct check of the definition for a witness."""
    prods = [mul(g, s) for g, s in zip(cofs, S)]
    if fake: prods = [red(p) for p in prods]
    sm = frozenset()
    for p in prods: sm = add(sm, p)
    if fake: sm = red(sm)
    ok = all(deg(p) <= D for p in prods) and any(deg(p) == D for p in prods) and sm and deg(sm) < D
    return bool(ok), sm

def first(S, N, fake=False, unbounded=None, Dmax=6):
    for D in range(1, Dmax + 1):
        w = fall(S, N, D, fake=fake, unbounded=unbounded)
        print(f"   D={D}: {'FALL' if w else 'none'}")
        if w:
            cofs, prods, sm = w
            print("     cofactors:", [show(c) for c in cofs])
            print("     products :", [show(p) for p in prods])
            print("     sum      :", show(sm))
            if unbounded is None:
                ok, sm2 = verify(S, D, cofs, fake)
                print("     direct re-check of definition:", ok, "| sum", show(sm2))
                assert ok
            return D
    return None

systems = {
    "A": (["X", "Y"], ["X^2 Y", "X Y + X"]),
    "B": (["X1", "X2", "X3"], ["X1 X2 + X3", "X1 X3 + X2"]),
}
results = {}
for name, (names, F) in systems.items():
    VARS = names; N = len(names)
    Fp = [P(f, names) for f in F]
    fe = [P(f"{v}^2 + {v}", names) for v in names]
    for place, S in (("F", Fp), ("F+S_fe", Fp + fe)):
        for kind, kw in (("d_F", {}), ("d'_F", {"fake": True}),
                         ("control1 d_F (upper bound dropped, cofactor deg<=4)", {"unbounded": 4})):
            print(f"== {name} {place} {kind}")
            results[(name, place, kind)] = first(S, N, **kw)

# Recovery illustration on B, v=3: fake fall (X3, X2) has unreduced products of degree <= 3.
VARS = systems["B"][0]; names = VARS
Fp = [P(f, names) for f in systems["B"][1]]; fe = [P(f"{v}^2 + {v}", names) for v in names]
g = [P("X3", names), P("X2", names)]
print("== recovery illustration B, v=3:", verify(Fp, 3, g, True))
p = add(mul(g[0], Fp[0]), mul(g[1], Fp[1]))
print("   unreduced sum p =", show(p), "; red(p) =", show(red(p)))
cof = g + [frozenset(), P("1", names), P("1", names)]
print("   lifted true fall (X3, X2, 0, 1, 1):", verify(Fp + fe, 3, cof, False))

# Control 2 on A: fake fall (1,1) at v=2, unreduced degrees 3 > 2; no true fall at 2.
VARS = systems["A"][0]; names = VARS
Fp = [P(f, names) for f in systems["A"][1]]; fe = [P(f"{v}^2 + {v}", names) for v in names]
print("== control 2 on A: fake fall (1,1) at v=2:", verify(Fp, 2, [P("1", names)]*2, True),
      "unreduced degs", [deg(f) for f in Fp], "; true fall of F+S_fe at 2:", fall(Fp + fe, 2, 2))

print("\nSUMMARY")
for k, v in results.items(): print(" ", k, "=", v)
