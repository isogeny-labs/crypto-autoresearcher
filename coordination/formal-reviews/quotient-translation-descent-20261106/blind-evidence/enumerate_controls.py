#!/usr/bin/env python3
"""Exhaustive finite check for TASK-20261106-bb6ab4 (blind re-derivation, J4).

Not an experiment: a deterministic enumeration over small explicit groups.
Group law written multiplicatively as op(a,b); in additive notation
op(a,b) = a + b, inv(a) = -a.  The statement checked, for each S, T:
  LHS(P):  iota_S then tau_T  = op(inv(op(P,S)), T)          = -(P+S) + T
  RHS(P):  tau_T then iota_S  = inv(op(op(P,T),S))           = -((P+T)+S)
  main:   (forall P, LHS=RHS) <-> T*T = e
"""
import itertools

def cyclic(n):
    G = list(range(n))
    return dict(name=f"Z/{n}", G=G, op=lambda a, b: (a + b) % n, e=0, inv=lambda a: (-a) % n)

def product(A, B):
    G = list(itertools.product(A["G"], B["G"]))
    return dict(name=f"{A['name']}x{B['name']}", G=G,
                op=lambda x, y: (A["op"](x[0], y[0]), B["op"](x[1], y[1])),
                e=(A["e"], B["e"]), inv=lambda x: (A["inv"](x[0]), B["inv"](x[1])))

def perm_group(name, gens, n):
    # closure of generators; composition (p*q)(i) = p(q(i))
    e = tuple(range(n))
    comp = lambda p, q: tuple(p[q[i]] for i in range(n))
    G = {e}; frontier = [e]
    while frontier:
        new = []
        for g in frontier:
            for h in gens:
                k = comp(g, h)
                if k not in G:
                    G.add(k); new.append(k)
        frontier = new
    inv = lambda p: tuple(sorted(range(n), key=lambda i: p[i]))
    return dict(name=name, G=sorted(G), op=comp, e=e, inv=inv)

def quaternion():
    # Q8 as unit quaternions {±1,±i,±j,±k}: encode as (sign, unit) unit in 1,i,j,k
    table = {('1','1'):(1,'1'),('1','i'):(1,'i'),('1','j'):(1,'j'),('1','k'):(1,'k'),
             ('i','1'):(1,'i'),('i','i'):(-1,'1'),('i','j'):(1,'k'),('i','k'):(-1,'j'),
             ('j','1'):(1,'j'),('j','i'):(-1,'k'),('j','j'):(-1,'1'),('j','k'):(1,'i'),
             ('k','1'):(1,'k'),('k','i'):(1,'j'),('k','j'):(-1,'i'),('k','k'):(-1,'1')}
    G = [(s, u) for s in (1, -1) for u in '1ijk']
    def op(a, b):
        s, u = table[(a[1], b[1])]
        return (a[0] * b[0] * s, u)
    inv = lambda a: a if a[1] == '1' else (-a[0], a[1])
    return dict(name="Q8", G=G, op=op, e=(1, '1'), inv=inv)

def check_group(H):
    G, op, inv, e = H["G"], H["op"], H["inv"], H["e"]
    for a in G:
        assert op(a, inv(a)) == e and op(e, a) == a
    abelian = all(op(a, b) == op(b, a) for a in G for b in G)
    res = dict(main=[], b=[], c=[], d=[], e4=[], pointwise=[], exists=[])
    for S in G:
        for T in G:
            eq = [op(inv(op(P, S)), T) == inv(op(op(P, T), S)) for P in G]
            allP, anyP = all(eq), any(eq)
            twoT = op(T, T) == e
            twoS = op(S, S) == e
            fourT = op(op(T, T), op(T, T)) == e
            eqd = all(op(op(P, S), T) == op(op(P, T), S) for P in G)  # control (d)
            if allP != twoT: res["main"].append((S, T))
            if allP != (T == e): res["b"].append((S, T))
            if allP != twoS: res["c"].append((S, T))
            if eqd != twoT: res["d"].append((S, T))
            if allP != fourT: res["e4"].append((S, T))
            if not all(x == twoT for x in eq): res["pointwise"].append((S, T))
            if anyP != twoT: res["exists"].append((S, T))
    return abelian, res

def semilattice_subtraction_comm_monoid():
    # ({0,1,2}, max, 0) with neg = id: commutative monoid with an involutive
    # negation satisfying -(a+b) = -a + -b and (a+b=0 -> -a=b); not a group.
    G = [0, 1, 2]
    op = max; neg = lambda a: a
    assert all(neg(op(a, b)) == op(neg(a), neg(b)) for a in G for b in G)
    assert all(neg(a) == b for a in G for b in G if op(a, b) == 0)
    bad = []
    for S in G:
        for T in G:
            allP = all(op(neg(op(P, S)), T) == neg(op(op(P, T), S)) for P in G)
            if allP != (op(T, T) == 0): bad.append((S, T))
    return bad

groups = [cyclic(n) for n in range(1, 9)]
groups += [product(cyclic(2), cyclic(2)), product(cyclic(2), cyclic(4)),
           product(product(cyclic(2), cyclic(2)), cyclic(2))]
groups += [perm_group("S3", [(1, 0, 2), (1, 2, 0)], 3),
           perm_group("D4", [(1, 2, 3, 0), (0, 3, 2, 1)], 4),
           quaternion()]
for H in groups:
    ab, r = check_group(H)
    print(f"{H['name']:10s} order={len(H['G']):2d} abelian={ab!s:5s} "
          + " ".join(f"{k}:{len(v)}" for k, v in r.items()))
    for k, v in r.items():
        if v:
            print(f"    first {k} counterexample (S,T) = {v[0]}")
print("max-semilattice {0,1,2}, neg=id: main counterexamples (S,T):",
      semilattice_subtraction_comm_monoid())
