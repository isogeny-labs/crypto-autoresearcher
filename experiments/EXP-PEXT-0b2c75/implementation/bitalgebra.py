#!/usr/bin/env python3
"""Pre-data algebra of the candidate norm-character law (no field arithmetic, no data).

Implements, verbatim, the written candidate formulas of
coordination/goals/GOAL-PEXT-4a1d6b/batches/BATCH-3e067e/tasks/TASK-20261027-e6b5bf/derivation.md
(UNREVIEWED; an unreviewed candidate, not a theorem):
  (4.2)  s12 = t b(a2-a1) b(a4-a3), s13 = t b(a3-a1) b(a4-a2), s23 = t b(a3-a2) b(a4-a1),
         b(k) = b_k (1 <= k <= (n-1)/2), eps * b_{n-k} ((n-1)/2 < k < n)
  (3.1)  W1 halvable iff s12 = s13 = +1; W2 iff eps s12 = s23 = +1; W3 iff eps s13 = eps s23 = +1
  (3.2)  |E(K)[4]| = 4 + 4 h
and the literal written tables: (5.1) for n = 5, S = (0,1,2,3); (7.1)-(7.2) for n = 7, S = (0,2,3,4).

  python3 bitalgebra.py selfcheck     exit 0 iff (i) the generic predictor equals the literal n = 5 table and the literal
                                      n = 7 formula on every bit cell, (ii) h is invariant under the 24 orderings of
                                      every 4-subset S (so the prediction does not depend on which branch is the origin),
                                      (iii) the pairwise structure: for eps = -1 h <= 1; h is never 2.
  python3 bitalgebra.py table5        print the n = 5 prediction table
"""
import itertools
import json
import sys


def predict(n, a, eps, t, bits):
    """bits: dict k -> +-1 for k = 1..(n-1)//2; a: ordered shift word (a1..a4). Returns (s, W, h, E4)."""
    hh = (n - 1) // 2

    def beta(k):
        k %= n
        return bits[k] if k <= hh else eps * bits[n - k]
    s12 = t * beta(a[1] - a[0]) * beta(a[3] - a[2])
    s13 = t * beta(a[2] - a[0]) * beta(a[3] - a[1])
    s23 = t * beta(a[2] - a[1]) * beta(a[3] - a[0])
    w = (s12 == 1 and s13 == 1, eps * s12 == 1 and s23 == 1, eps * s13 == 1 and eps * s23 == 1)
    h = sum(w)
    return (s12, s13, s23), w, h, 4 + 4 * h


# literal derivation.md table (5.1): rows (eps, t, p = b1 b2) -> |E(K)[4]|
TABLE5 = {(-1, 1, 1): 8, (-1, 1, -1): 8, (-1, -1, 1): 8, (-1, -1, -1): 8,
          (1, 1, 1): 16, (1, 1, -1): 8, (1, -1, 1): 4, (1, -1, -1): 4}


def lit7(eps, t, b1, b2, b3):
    """Literal derivation.md (7.1)-(7.2) for S = (0,2,3,4): R = b1 b2, S* = b2 b3."""
    R, S = b1 * b2, b2 * b3
    i1 = (t * R == 1 and t * S == 1)
    i2 = (eps * t * R == 1 and t * eps * R * S == 1)
    i3 = (eps * t * S == 1 and t * R * S == 1)
    return 4 * (1 + i1 + i2 + i3)


def selfcheck_dict():
    out = {"n5_table_vs_generic": 0, "n7_literal_vs_generic": 0, "ordering_variants": 0, "ordering_violations": 0,
           "h_equals_2": 0, "eps_minus_h_gt_1": 0, "cells": 0}
    for eps, t in itertools.product((1, -1), repeat=2):
        for b1, b2 in itertools.product((1, -1), repeat=2):
            e4 = predict(5, (0, 1, 2, 3), eps, t, {1: b1, 2: b2})[3]
            if e4 != TABLE5[(eps, t, b1 * b2)]:
                out["n5_table_vs_generic"] += 1
    for eps, t in itertools.product((1, -1), repeat=2):
        for b1, b2, b3 in itertools.product((1, -1), repeat=3):
            out["cells"] += 1
            if predict(7, (0, 2, 3, 4), eps, t, {1: b1, 2: b2, 3: b3})[3] != lit7(eps, t, b1, b2, b3):
                out["n7_literal_vs_generic"] += 1
    for n in (5, 7):
        hh = (n - 1) // 2
        for S in itertools.combinations(range(n), 4):
            for eps, t in itertools.product((1, -1), repeat=2):
                for bv in itertools.product((1, -1), repeat=hh):
                    bits = {k + 1: bv[k] for k in range(hh)}
                    vals = set()
                    for perm in itertools.permutations(S):
                        h = predict(n, perm, eps, t, bits)[2]
                        vals.add(h)
                        out["ordering_variants"] += 1
                        if h == 2:
                            out["h_equals_2"] += 1
                        if eps == -1 and h > 1:
                            out["eps_minus_h_gt_1"] += 1
                    if len(vals) != 1:
                        out["ordering_violations"] += 1
    out["pass"] = all(out[k] == 0 for k in ("n5_table_vs_generic", "n7_literal_vs_generic", "ordering_violations", "h_equals_2", "eps_minus_h_gt_1"))
    return out


def selfcheck():
    out = selfcheck_dict()
    print(json.dumps(out, sort_keys=True))
    return 0 if out["pass"] else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "table5":
        for k in sorted(TABLE5):
            print(k, TABLE5[k])
        return 0
    return selfcheck()


if __name__ == "__main__":
    sys.exit(main())
