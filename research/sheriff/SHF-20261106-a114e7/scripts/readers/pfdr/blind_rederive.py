#!/usr/bin/env python3
"""Blind re-derivation for sheriff case SHF-20261106-a114e7, reader pfdr.

Load-bearing quantity: kappa = S/M, the pooled pair-sum coincidence count of
x-labels of rank-r log-GAP half-boxes against matched uniform label sets, on
prime-order toy curves. Written from the statement only (H-PFDR-727bfc / the
specification's counting_convention, log_gap_builder and null_builder text)
with my own curve generation, point arithmetic, set builders and counter. No
producer code and no producer data is read. Fresh curves from my own seed rule.

Restriction of this re-derivation (declared): p = 3 mod 4 only (square roots
by one exponentiation); bits 20 only; n in {256, 1024}; 20 null sets per
curve; numpy for the label tables and pair sums.

Proves-too-much: the same pipeline on a planted label arithmetic progression
(a known-structured set of 256 labels) and on a 16-label AP inside 240 random
labels must NOT read kappa ~ 1.

usage: python3 -I blind_rederive.py <out.json> [curves_per_cell]
"""
import json
import math
import random
import sys
import time

import numpy as np

BITS = 20


def is_probable_prime(n):
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for q in small:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:  # deterministic for n < 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


class Curve:
    def __init__(self, p, a, b):
        self.p, self.a, self.b = p, a, b
        x = np.arange(p, dtype=np.int64)
        sq = np.zeros(p, dtype=bool)
        sq[(x * x) % p] = True
        f = ((x * x % p) * x % p + a * x % p + b) % p
        self.f = f
        self.is_label = sq[f] & (f != 0)
        self.n_roots = int((f == 0).sum())
        self.N = 1 + self.n_roots + 2 * int(self.is_label.sum())
        self.labels = np.nonzero(self.is_label)[0]

    def sqrt(self, v):
        r = pow(v, (self.p + 1) // 4, self.p)
        assert r * r % self.p == v % self.p
        return r

    def add(self, P, Q):
        p = self.p
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, p - 2, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    def neg(self, P):
        return None if P is None else (P[0], (-P[1]) % self.p)

    def mul(self, k, P):
        R, Q = None, P
        if k < 0:
            k, Q = -k, self.neg(P)
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R

    def random_point(self, rng):
        x = int(self.labels[rng.randrange(len(self.labels))])
        y = self.sqrt(int(self.f[x]))
        return (x, y if rng.random() < 0.5 else (-y) % self.p)


def gen_curve(rng):
    while True:
        p = rng.randrange(2 ** (BITS - 1), 2 ** BITS)
        if p % 4 != 3 or not is_probable_prime(p):
            continue
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        E = Curve(p, a, b)
        if E.N != p and is_probable_prime(E.N) and E.N > 3:
            return E


def half_box(r, T):
    """coefficient vectors in [-T, T]^r, first nonzero entry positive, lexicographic, coords ascending from -T"""
    def rec(prefix, depth, seen_nonzero):
        if depth == r:
            if seen_nonzero:
                yield tuple(prefix)
            return
        lo = -T if seen_nonzero else 0
        for v in range(lo, T + 1):
            yield from rec(prefix + [v], depth + 1, seen_nonzero or v != 0)
    yield from rec([], 0, False)


def log_gap(E, r, n, rng, base=None):
    need = math.ceil(1.02 * n) + 8
    T = 1
    while ((2 * T + 1) ** r - 1) // 2 < need:
        T += 1
    Ps = base or [E.random_point(rng) for _ in range(r)]
    mult = [{k: E.mul(k, P) for k in range(-T, T + 1)} for P in Ps]
    seen, out, dup, enum = set(), [], 0, 0
    for c in half_box(r, T):
        enum += 1
        Q = None
        for i, ci in enumerate(c):
            Q = E.add(Q, mult[i][ci])
        if Q is None:
            continue
        if Q[0] in seen:
            dup += 1
            continue
        seen.add(Q[0])
        out.append(Q[0])
        if len(out) == n:
            return np.array(out, dtype=np.int64), {"T": T, "enumerated": enum, "dup": dup}
    return None, {"T": T, "enumerated": enum, "dup": dup, "degenerate": True}


def null_set(E, n, rng):
    chosen = set()
    while len(chosen) < n:
        x = rng.randrange(E.p)
        if E.is_label[x]:
            chosen.add(x)
    return np.array(sorted(chosen), dtype=np.int64)


def planted_ap(E, n, rng):
    """a pure label AP: x0 + k w for k = 0, 1, ..., keeping members of L, n labels (known structure)"""
    x0, w = rng.randrange(E.p), rng.randrange(1, E.p)
    out, k = [], 0
    while len(out) < n:
        x = (x0 + k * w) % E.p
        if E.is_label[x]:
            out.append(x)
        k += 1
    return np.array(out, dtype=np.int64)


def count_C(X, p):
    s = (X[:, None] + X[None, :])
    iu = np.triu_indices(len(X), k=1)
    sums = s[iu] % p
    m = np.bincount(sums, minlength=p).astype(np.int64)
    return int((m * (m - 1) // 2).sum())


def main():
    out_p = sys.argv[1]
    n_curves = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    t0 = time.time()
    crng = random.Random("sheriff-pfdr-blind-curves-20261106")
    curves = [gen_curve(crng) for _ in range(n_curves)]
    res = {"bits": BITS, "n_curves": n_curves, "curves": [(E.p, E.a, E.b, E.N) for E in curves],
           "curve_gen_seconds": round(time.time() - t0, 1), "cells": [], "controls": []}
    # sanity: |L| = (N - 1) / 2 on every curve (odd prime order, no 2-torsion)
    res["label_universe_ok"] = all(len(E.labels) == (E.N - 1) // 2 and E.n_roots == 0 for E in curves)
    for r in (1, 2, 3):
        for n in (256, 1024):
            S = M = V = 0.0
            Sp = 0.0
            per = []
            degenerate = 0
            for ci, E in enumerate(curves):
                rng = random.Random(f"sheriff-pfdr|{r}|{n}|{ci}")
                X, meta = log_gap(E, r, n, rng)
                if X is None:
                    degenerate += 1
                    continue
                g = count_C(X, E.p)
                nulls = [count_C(null_set(E, n, rng), E.p) for _ in range(20)]
                mu, var = float(np.mean(nulls)), float(np.var(nulls, ddof=1))
                S += g
                M += mu
                V += var
                per.append((g, mu))
            kappa = S / M
            z = (S - M) / math.sqrt(V * (1 + 1 / 20))
            formula = sum(3 * math.comb(n, 4) / E.p for E in curves)
            # own curve bootstrap (percentile)
            brng = random.Random(f"boot|{r}|{n}")
            ks = sorted(sum(per[i][0] for i in idx) / sum(per[i][1] for i in idx)
                        for idx in ([brng.randrange(len(per)) for _ in per] for _ in range(2000)))
            ci95 = [ks[49], ks[1950]]
            cell = {"cell": f"b{BITS}-r{r}-n{n}", "curves_ok": len(per), "degenerate": degenerate, "S": S, "M": M,
                    "kappa": kappa, "z": z, "ci95": ci95, "M_over_formula_3binom_n4_over_p": M / formula,
                    "null_by_5pct_rule": abs(kappa - 1) < 0.05 and ci95[0] >= 0.90 and ci95[1] <= 1.10}
            res["cells"].append(cell)
            print(json.dumps(cell), flush=True)
    # proves-too-much controls (n = 256, first 20 curves)
    for name in ("planted_label_AP", "plant_16_label_AP_plus_random_fill"):
        S = M = V = 0.0
        for ci, E in enumerate(curves[:20]):
            rng = random.Random(f"ptm|{name}|{ci}")
            if name == "planted_label_AP":
                X = planted_ap(E, 256, rng)
            else:
                ap = [int(v) for v in planted_ap(E, 16, rng)]
                fill = set(ap)
                while len(fill) < 256:
                    x = rng.randrange(E.p)
                    if E.is_label[x]:
                        fill.add(x)
                X = np.array(sorted(fill), dtype=np.int64)
            g = count_C(X, E.p)
            nulls = [count_C(null_set(E, 256, rng), E.p) for _ in range(20)]
            S += g
            M += float(np.mean(nulls))
            V += float(np.var(nulls, ddof=1))
        kappa = S / M
        z = (S - M) / math.sqrt(V * 1.05)
        ctl = {"control": name, "S": S, "M": M, "kappa": kappa, "z": z,
               "reads_null": abs(kappa - 1) < 0.05 and abs(z) < 4}
        res["controls"].append(ctl)
        print(json.dumps(ctl), flush=True)
    res["seconds"] = round(time.time() - t0, 1)
    json.dump(res, open(out_p, "w"), indent=1)


if __name__ == "__main__":
    main()
