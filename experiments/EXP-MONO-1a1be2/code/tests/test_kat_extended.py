"""FX-16 (TASK-20261106-4c4831, DEC-20261106-843cf7 dev1_decision): the m = 3 large-q substitute cell.

NOT part of the start-up suite: this file is not in CODE_FILES, not collected by tests/test_kat.py and never run by
a cell. It stands in for the (32779, 2, m = 3) E2 cell that KX-4 asked for and DEV-1 recorded as not run (about 6e12
multisets). The substitute keeps degree n = 2, tuple size m = 3 and depth-3 multiset enumeration in the compiled kernel
on a field of the same index-width class (Q < 2^31), at about 1/30 of the multisets.

  * The field is F_{q''^2}, q'' the least prime above 10,000 (computed by trial division; disjoint from every arm-A,
    arm-B and arm-C contract pair).
  * The curve comes from the KAT curve rule under seed "kat|large|<q''>|2|m3"; the line base is used.
  * The E2 sampled counter (counters.arm_c_cell) runs at m = 3 on s = 50 sampled targets and is compared with an
    independent membership method in Python field arithmetic that never calls the kernel: a sorted numpy int64 table
    of the point indices of all pair sums (key = index * B + larger element index), queried with searchsorted.
  * Vacuity guard: the membership count is nonzero on at least 25 of the 50 targets (a property of the field size).

Budget: 14,400 s wall, 16 GB. Environment: KAT_EXT_LOG_PATH writes the raw output (KAT fields only) as JSON.
Run:  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider experiments/EXP-MONO-1a1be2/code/tests/test_kat_extended.py
Nothing here asserts a predicted value, a ratio or a cross-convention identity.
"""
from __future__ import annotations

import json
import math
import os
import resource
import shutil
import sys
import tempfile
import time

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

LOG: list = []
S_TARGETS = 50
M = 3
N_DEG = 2


def _is_prime_trial(p: int) -> bool:
    return p > 1 and all(p % d for d in range(2, math.isqrt(p) + 1))


def least_prime_above(k: int) -> int:
    p = k + 1
    while not _is_prime_trial(p):
        p += 1
    return p


Q2 = least_prime_above(10_000)           # q'' by trial division; 10,007 is expected by the rule


def substitute_instance():
    F = fqn.FQ(Q2, N_DEG)
    E, info = curves.generate_curve(F, f"kat|large|{Q2}|{N_DEG}|m3")
    D, X, t2 = E.factor_base()
    return F, E, info, D, X, t2


def pair_sum_table(E, D, rows=None):
    """Sorted int64 array of idx(D[i] + D[j]) * B + j over all i <= j (every 2-multiset of the base), with idx the
    target index (2*code(x) + sign bit, 2Q for O), by Python field arithmetic. rows limits i to range(rows)."""
    F = E.F
    B = len(D)
    parts = []
    for i in range(B if rows is None else rows):
        row = np.empty(B - i, dtype=np.int64)
        for k, j in enumerate(range(i, B)):
            row[k] = counters.target_index(F, E.add(D[i], D[j])) * B + j
        parts.append(row)
    keys = np.concatenate(parts)
    keys.sort()
    return keys


def membership_counts_m3(E, D, table, target_keys):
    """Count of 3-multisets of D summing to each target: each is a unique (pair-multiset M, largest element d) with M
    over indices <= d and sum(M) = R - d. For each target and each d, the number of table entries with index
    idx(R - D[d]) and larger-element index <= d is a difference of two searchsorted positions."""
    F = E.F
    B = len(D)
    negD = [E.neg(P) for P in D]
    out = []
    for key in target_keys:
        key = int(key)
        x = F.from_code(key >> 1)
        y = F.sqrt(E.f(x))
        ys = sorted([y, F.neg(y)], key=F.to_code)
        R = (x, ys[key & 1])
        assert counters.target_index(F, R) == key
        base = np.fromiter((counters.target_index(F, E.add(R, negD[d])) for d in range(B)), dtype=np.int64, count=B) * B
        lo = np.searchsorted(table, base, side="left")
        hi = np.searchsorted(table, base + np.arange(B, dtype=np.int64), side="right")
        out.append(int((hi - lo).sum()))
    return out


@pytest.fixture(scope="module")
def kernel():
    tmp = tempfile.mkdtemp(prefix="mono1a1be2-kat-ext-")
    k = counters.Kernel(counters.build_kernel(tmp))
    yield k
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="module", autouse=True)
def _write_log():
    yield
    path = os.environ.get("KAT_EXT_LOG_PATH")
    if path:
        with open(path, "w") as fh:
            json.dump({"task": "TASK-20261106-4c4831 FX-16", "note": "KAT-field values only; nothing here is a run",
                       "entries": LOG}, fh, indent=1)
            fh.write("\n")


def test_substitute_prime_is_the_least_prime_above_10000_and_disjoint_from_the_contract():
    assert Q2 == 10_007 and _is_prime_trial(Q2)
    assert not any(_is_prime_trial(k) for k in range(10_001, Q2))
    assert (Q2, N_DEG) not in launcher.contract_pairs()
    arm_a = mtp.contract_cells_qn()
    arm_c = {(mtp.q_rule(n), n) for n in mtp.ARM_C_NS}
    assert (Q2, N_DEG) not in arm_a and (Q2, N_DEG) not in arm_c


def test_small_scale_membership_method_agrees_with_the_kernel_on_a_sub_base(kernel):
    """The same comparison as the full cell on a sub-base of 40 points (still nondegenerate): validates the pair-sum
    table method before the long run, on the substitute curve."""
    F, E, info, D, X, t2 = substitute_instance()
    sub = D[:40]
    N = E.count_points_bsgs()[0]
    keys = [counters.target_index(F, E.add(E.add(sub[3], sub[9]), sub[17])),
            counters.target_index(F, E.add(E.add(sub[0], sub[0]), sub[0]))]
    keys = [k for k in keys if k != 2 * F.Q]
    table = pair_sum_table(E, sub)
    want = membership_counts_m3(E, sub, table, keys)
    got, st = kernel.run_sampled(E, M, sub, np.array(keys, dtype=np.uint64), len(keys))
    assert [int(c) for c in got] == want and all(c > 0 for c in want)
    assert st["multisets"] == math.comb(len(sub) + M - 1, M)
    assert N > 0


def test_m3_large_q_sampled_counter_matches_the_membership_method(kernel):
    F, E, info, D, X, t2 = substitute_instance()
    B = len(D)
    N = E.count_points_bsgs()[0]
    t0 = time.perf_counter()
    tr = curves.make_rng(f"kat|targets|large|{Q2}|{N_DEG}|m3")
    r = counters.arm_c_cell(kernel, E, D, M, S_TARGETS, tr, N)
    t_kernel = time.perf_counter() - t0
    keys = [int(k) for k in r["keys"]]
    assert len(keys) == S_TARGETS == len(set(k >> 1 for k in keys))
    for k in keys:
        assert F.chi(E.f(F.from_code(k >> 1))) == 1
    assert r["multisets"] == math.comb(B + M - 1, M)
    t1 = time.perf_counter()
    table = pair_sum_table(E, D)
    t_table = time.perf_counter() - t1
    t2_ = time.perf_counter()
    want = membership_counts_m3(E, D, table, keys)
    t_query = time.perf_counter() - t2_
    kern = [int(c) for c in r["sampled_counts"]]
    assert kern == want
    nonzero = sum(1 for c in want if c > 0)
    assert nonzero >= 25                                  # vacuity guard: a property of the field size
    LOG.append({"kat_id": "FX16-m3-large-q-substitute", "cell": f"q''={Q2},n=2,m=3,base=line",
                "q_double_prime": Q2, "B": B, "multiset_count": int(r["multisets"]), "N": N, "s": S_TARGETS,
                "count_pairs": [[a, b] for a, b in zip(kern, want)], "nonzero_membership_targets": nonzero,
                "wall_seconds": {"kernel_arm_c_cell": t_kernel, "pair_sum_table": t_table, "queries": t_query,
                                 "total": time.perf_counter() - t0},
                "peak_rss_kb_self": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
