#!/usr/bin/env python3
"""bench_wp2.py -- WP2 / G31-004: per-candidate cost of Semaev S_3 / S_4
evaluation over F_p, at p ~ 2^20 and p = 2^31-1, curve y^2 = x^3 + 7.

Modes (each timed over >= 5 repetitions; median and IQR in ns/candidate)

  A    "one-shot": per-candidate evaluation, power tables rebuilt inside each
       call, full sparse monomial accumulate.  No reuse whatsoever.
  A2   "pre-tabulated powers": power table for every field element built once
       per batch, then a pure per-monomial multiply-accumulate loop.  This is
       the variant that hides memory traffic; reported separately, never as
       the headline.
  B    "sieve sweep" (HEADLINE): nested grid sweep with incrementally updated
       powers, all operands full-size field elements, one reduction per
       candidate.  For m=4 the 5 coefficients of S_4 in x4 are computed once
       per (x1,x2,x3) triple and reused over a window of x4 values (the
       realistic inner loop).
  C    "batched / multipoint-style": numpy-vectorised coefficient arrays per
       triple, reused across the x4 window; S_3 analogue over the x3 window.

Every optimised loop is first checked value-for-value against the reference
evaluator in semaev_eval.py, so a fast-but-wrong loop cannot be timed.

Run:  python3 -B bench_wp2.py        (writes results_wp2.json)
"""
from __future__ import annotations

import ctypes
import json
import os
import platform
import resource
import statistics
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import semaev_eval as SE

P20 = 1048573          # largest prime < 2^20
P31 = 2147483647       # 2^31-1, largest prime < 2^31 (Mersenne prime)
A, B = 0, 7            # curve y^2 = x^3 + 7, disc = 1323 != 0
REPS = 5
SEED = 31004

OUT = {}


# ---------------------------------------------------------------- machinery
def ns_per(seconds, count):
    return seconds * 1e9 / count


def timed_reps(fn, reps=REPS):
    """Run fn() `reps` times; median/IQR of the ns/candidate values it reports."""
    vals = sorted(fn() for _ in range(reps))
    med = statistics.median(vals)
    q1, q3 = np.percentile(vals, 25), np.percentile(vals, 75)
    return {"median_ns": med, "iqr_ns": float(q3 - q1),
            "min_ns": vals[0], "max_ns": vals[-1],
            "spread_pct": 100.0 * (vals[-1] - vals[0]) / med,
            "all_ns": vals}


def rng_stream(n, p, seed=SEED):
    """Deterministic full-size field elements, generated outside the timing."""
    r = np.random.default_rng(seed)
    return [int(v) for v in r.integers(0, p, size=n, dtype=np.int64)]


def try_pin_to_cpu():
    """Best-effort CPU affinity on Darwin.

    macOS exposes no hard pinning (no sched_setaffinity).  The Mach
    THREAD_AFFINITY_POLICY is only a *hint* and is a no-op on Apple Silicon;
    we call it anyway and record the kernel return code, then rely on
    repetition + IQR rather than claiming a pinned CPU.
    """
    try:
        libc = ctypes.CDLL(None)
        libc.mach_thread_self.restype = ctypes.c_uint32
        th = libc.mach_thread_self()
        # struct thread_affinity_policy { integer_t affinity_tag; }
        tag = ctypes.c_int(1)
        THREAD_AFFINITY_POLICY, COUNT = 4, 1
        kr = libc.thread_policy_set(ctypes.c_uint32(th), ctypes.c_int(THREAD_AFFINITY_POLICY),
                                    ctypes.byref(tag), ctypes.c_uint32(COUNT))
        return {"attempted": True, "kern_return": int(kr),
                "note": "Darwin THREAD_AFFINITY_POLICY is a hint, not a pin; "
                        "no-op on Apple Silicon -- variance reported instead"}
    except Exception as exc:                                  # pragma: no cover
        return {"attempted": False, "error": f"{type(exc).__name__}: {exc}"}


# --------------------------------------------------- mode A: one-shot sparse
def bench_A(p, n, m, terms):
    xs = [rng_stream(n, p) for _ in range(m)]

    def run():
        t0 = time.perf_counter()
        acc = 0
        if m == 3:
            f = SE.s3_eval_sparse
            for i in range(n):
                acc += f(xs[0][i], xs[1][i], xs[2][i], terms, p)
        else:
            f = SE.s4_eval_sparse
            for i in range(n):
                acc += f(xs[0][i], xs[1][i], xs[2][i], xs[3][i], terms, p)
        dt = time.perf_counter() - t0
        assert acc >= 0
        return ns_per(dt, n)
    return timed_reps(run)


# ------------------------------------------- mode A2: pre-tabulated powers
def bench_A2(p, n, m, terms):
    xs = [rng_stream(n, p, SEED + 1 + i) for i in range(m)]
    md = [0] * m
    for e in terms:
        for i in range(m):
            md[i] = max(md[i], e[i])
    tables = []
    for i in range(m):
        tbl = {}
        for v in set(xs[i]):
            row = [1]
            for _ in range(md[i]):
                row.append(row[-1] * v % p)
            tbl[v] = row
        tables.append(tbl)
    items = list(terms.items())

    def run():
        t0 = time.perf_counter()
        acc = 0
        if m == 3:
            t0_, t1_, t2_ = tables
            for i in range(n):
                a0 = t0_[xs[0][i]]
                a1 = t1_[xs[1][i]]
                a2 = t2_[xs[2][i]]
                s = 0
                for e, c in items:
                    s += c * a0[e[0]] * a1[e[1]] * a2[e[2]]
                acc += s % p
        else:
            t0_, t1_, t2_, t3_ = tables
            for i in range(n):
                a0 = t0_[xs[0][i]]
                a1 = t1_[xs[1][i]]
                a2 = t2_[xs[2][i]]
                a3 = t3_[xs[3][i]]
                s = 0
                for e, c in items:
                    s += c * a0[e[0]] * a1[e[1]] * a2[e[2]] * a3[e[3]]
                acc += s % p
        dt = time.perf_counter() - t0
        assert acc >= 0
        return ns_per(dt, n)
    return timed_reps(run)


# ------------------------------------------------- mode B: sieve sweep (m=3)
def sweep_s3(p, a, b, L1, L2, W, x0=0, y0=0, z0=0, reduce_powers=True):
    """Grid sweep x1 in [x0,x0+L1), x2 in [y0,y0+L2), x3 in [z0,z0+W).

    x1/x2 powers are hoisted to their loop levels; x3^2 is updated
    incrementally, (X+1)^2 = X^2 + (2X+1).  With reduce_powers=True the
    running square and step are reduced mod p each step (the realistic
    implementation); False keeps them unreduced (bounded by p + 2W^2).
    Returns (count, checksum, zeros).
    """
    cnt = chk = nz = 0
    for i1 in range(L1):
        X1 = x0 + i1
        for i2 in range(L2):
            X2 = y0 + i2
            d = X1 - X2
            A_ = d * d % p
            X1X2 = X1 * X2 % p
            B_ = (-2 * ((X1 + X2) * (X1X2 + a) + 2 * b)) % p
            C_ = ((X1X2 - a) * (X1X2 - a) - 4 * b * (X1 + X2)) % p
            X3 = z0
            X3s = X3 * X3 % p
            step = (2 * X3 + 1) % p
            if reduce_powers:
                for _ in range(W):
                    v = (A_ * X3s + B_ * X3 + C_) % p
                    chk += v
                    if v == 0:
                        nz += 1
                    X3s = (X3s + step) % p
                    step = (step + 2) % p
                    X3 += 1
            else:
                for _ in range(W):
                    v = (A_ * X3s + B_ * X3 + C_) % p
                    chk += v
                    if v == 0:
                        nz += 1
                    X3s += step
                    step += 2
                    X3 += 1
            cnt += W
    return cnt, chk, nz


def bench_B_s3(p, a, b, L1, L2, W, reduce_powers=True):
    z0 = p - W - 1                      # full-size x3 operands

    def run():
        t0 = time.perf_counter()
        cnt, chk, nz = sweep_s3(p, a, b, L1, L2, W, x0=p // 2, y0=p // 3,
                                z0=z0, reduce_powers=reduce_powers)
        dt = time.perf_counter() - t0
        assert chk >= 0
        return ns_per(dt, cnt)
    return timed_reps(run)


# ------------------------------------------------- mode B: sieve sweep (m=4)
def sweep_s4(p, a, b, groups, L1, L2, L3, W, x0=0, y0=0, z0=0, w0=0):
    """(x1,x2,x3) over a box; inner x4 window of length W.

    The 5 coefficient polynomials in x4 are evaluated once per triple; each of
    the W x4 candidates then costs 4 mulmods + 5 reductions (Horner).
    Returns (count, checksum, zeros).
    """
    cnt = chk = nz = 0
    gs = [list(groups[d].items()) for d in range(5)]
    for i1 in range(L1):
        X1 = x0 + i1
        X1sq = X1 * X1 % p
        p1 = (1, X1 % p, X1sq, X1sq * X1 % p, X1sq * X1 % p * X1 % p)
        for i2 in range(L2):
            X2 = y0 + i2
            X2sq = X2 * X2 % p
            p2 = (1, X2 % p, X2sq, X2sq * X2 % p, X2sq * X2 % p * X2 % p)
            for i3 in range(L3):
                X3 = z0 + i3
                X3sq = X3 * X3 % p
                p3 = (1, X3 % p, X3sq, X3sq * X3 % p, X3sq * X3 % p * X3 % p)
                cs = []
                for g in gs:
                    acc = 0
                    for (e1, e2, e3), c in g:
                        acc += c * p1[e1] * p2[e2] * p3[e3]
                    cs.append(acc % p)
                c0, c1, c2, c3, c4 = cs
                X4 = w0
                for _ in range(W):
                    v = ((((c4 * X4 + c3) % p * X4 + c2) % p * X4 + c1) % p
                         * X4 + c0) % p
                    chk += v
                    if v == 0:
                        nz += 1
                    X4 += 1
                cnt += W
    return cnt, chk, nz


def bench_B_s4(p, a, b, groups, L1, L2, L3, W):
    w0 = p - W - 1

    def run():
        t0 = time.perf_counter()
        cnt, chk, nz = sweep_s4(p, a, b, groups, L1, L2, L3, W,
                                x0=p // 2, y0=p // 3, z0=p // 5, w0=w0)
        dt = time.perf_counter() - t0
        assert chk >= 0
        return ns_per(dt, cnt)
    return timed_reps(run)


def bench_B_s4_coeff_only(p, a, b, groups, ntrip):
    """Cost of the 5 coefficient polynomials per (x1,x2,x3) triple, no x4 loop.
    Sets the amortisation: per-candidate coef share = this / W."""
    gs = [list(groups[d].items()) for d in range(5)]
    xs = [rng_stream(ntrip, p, SEED + 20 + i) for i in range(3)]

    def run():
        t0 = time.perf_counter()
        acc = 0
        for i in range(ntrip):
            X1, X2, X3 = xs[0][i], xs[1][i], xs[2][i]
            X1sq = X1 * X1 % p
            p1 = (1, X1 % p, X1sq, X1sq * X1 % p, X1sq * X1 % p * X1 % p)
            X2sq = X2 * X2 % p
            p2 = (1, X2 % p, X2sq, X2sq * X2 % p, X2sq * X2 % p * X2 % p)
            X3sq = X3 * X3 % p
            p3 = (1, X3 % p, X3sq, X3sq * X3 % p, X3sq * X3 % p * X3 % p)
            for g in gs:
                s = 0
                for (e1, e2, e3), c in g:
                    s += c * p1[e1] * p2[e2] * p3[e3]
                acc += s % p
        dt = time.perf_counter() - t0
        assert acc >= 0
        return ns_per(dt, ntrip)
    return timed_reps(run)


def bench_horner_only(p, n, W):
    """Pure degree-4-in-x4 Horner cost: the asymptotic (W -> inf) per-candidate
    cost of mode B for m=4, with coefficient work fully amortised away."""
    r = np.random.default_rng(SEED + 30)
    cs = [int(v) for v in r.integers(0, p, size=5 * n)]
    w0 = p - W - 1

    def run():
        t0 = time.perf_counter()
        chk = 0
        for i in range(n):
            c0, c1, c2, c3, c4 = cs[5 * i:5 * i + 5]
            X4 = w0
            for _ in range(W):
                v = ((((c4 * X4 + c3) % p * X4 + c2) % p * X4 + c1) % p
                     * X4 + c0) % p
                chk += v
                X4 += 1
        dt = time.perf_counter() - t0
        assert chk >= 0
        return ns_per(dt, n * W)
    return timed_reps(run)


# ------------------------------------------------------------ mode C: numpy
def c_s3_matrix(p, a, b, X1, X2, W, w0=0):
    """numpy S_3 values for (X1[i],X2[i]) over x3 = w0..w0+W-1, shape (n1,W)."""
    X3 = np.arange(w0, w0 + W, dtype=np.int64)
    X3s = X3 * X3 % p
    d = X1 - X2
    A_ = d * d % p
    X1X2 = X1 * X2 % p
    B_ = (-2 * ((X1 + X2) * (X1X2 + a) + 2 * b)) % p
    C_ = ((X1X2 - a) ** 2 - 4 * b * (X1 + X2)) % p
    return (A_[:, None] * X3s[None, :] % p + B_[:, None] * X3[None, :]
            + C_[:, None]) % p


def bench_C_s3(p, a, b, n1, W):
    r = np.random.default_rng(SEED + 1)
    X1 = r.integers(0, p, size=n1, dtype=np.int64)
    X2 = r.integers(0, p, size=n1, dtype=np.int64)
    w0 = p - W - 1

    def run():
        t0 = time.perf_counter()
        V = c_s3_matrix(p, a, b, X1, X2, W, w0)
        nz = int(np.count_nonzero(V == 0))
        dt = time.perf_counter() - t0
        return ns_per(dt, n1 * W) if nz >= 0 else 0.0
    return timed_reps(run)


def c_s4_matrix(p, groups, X1, X2, X3, W, w0=0):
    """numpy S_4 values for triples over x4 = w0..w0+W-1, shape (n3,W)."""
    n3 = len(X1)
    pw = []
    for X in (X1, X2, X3):
        row = [np.ones(n3, dtype=np.int64), X % p]
        row.append(row[1] * X % p)
        row.append(row[2] * X % p)
        row.append(row[3] * X % p)
        pw.append(row)
    cs = []
    for d in range(5):
        acc = np.zeros(n3, dtype=np.int64)
        for (e1, e2, e3), c in groups[d].items():
            acc = (acc + c * pw[0][e1] % p * pw[1][e2] % p
                   * pw[2][e3] % p) % p
        cs.append(acc)
    X4 = np.arange(w0, w0 + W, dtype=np.int64)
    V = cs[4][:, None]
    for c in (cs[3], cs[2], cs[1], cs[0]):
        V = (V * X4[None, :] + c[:, None]) % p
    return V


def bench_C_s4(p, a, b, groups, n3, W):
    r = np.random.default_rng(SEED + 2)
    X1 = r.integers(0, p, size=n3, dtype=np.int64)
    X2 = r.integers(0, p, size=n3, dtype=np.int64)
    X3 = r.integers(0, p, size=n3, dtype=np.int64)
    w0 = p - W - 1

    def run():
        t0 = time.perf_counter()
        V = c_s4_matrix(p, groups, X1, X2, X3, W, w0)
        nz = int(np.count_nonzero(V == 0))
        dt = time.perf_counter() - t0
        return ns_per(dt, n3 * W) if nz >= 0 else 0.0
    return timed_reps(run)


def bench_C_s4_noamortise(p, a, b, terms, n, W):
    """Vectorised full-monomial evaluation with no coefficient reuse: the
    honest 'vectorised but not multipoint' baseline."""
    r = np.random.default_rng(SEED + 3)
    xs = [r.integers(0, p, size=n * W, dtype=np.int64) for _ in range(4)]
    md = [max(e[i] for e in terms) for i in range(4)]
    pw = []
    for i in range(4):
        row = [np.ones(n * W, dtype=np.int64)]
        for _ in range(md[i]):
            row.append(row[-1] * xs[i] % p)
        pw.append(row)
    items = list(terms.items())

    def run():
        t0 = time.perf_counter()
        acc = np.zeros(n * W, dtype=np.int64)
        for e, c in items:
            acc = (acc + c * pw[0][e[0]] % p * pw[1][e[1]] % p
                   * pw[2][e[2]] % p * pw[3][e[3]] % p) % p
        nz = int(np.count_nonzero(acc == 0))
        dt = time.perf_counter() - t0
        return ns_per(dt, n * W) if nz >= 0 else 0.0
    return timed_reps(run)


# --------------------------------------------------- reference group op (F_p)
def bench_group_add(p, a, b, n):
    C = SE.Curve(p, a, b)
    r = np.random.default_rng(SEED + 4)
    pts = []
    while len(pts) < 2 * n:
        x = int(r.integers(0, p))
        fx = C.f(x)
        if fx == 0:
            continue
        if pow(fx, (p - 1) // 2, p) == 1:
            y = C._sqrt_p1m4(fx)
            pts.append((x, min(y, p - y)))
    P = pts[0:2 * n:2]
    Q = pts[1:2 * n:2]

    def run():
        t0 = time.perf_counter()
        acc = 0
        for i in range(n):
            acc += C.add(P[i], Q[i])[0]
        dt = time.perf_counter() - t0
        return ns_per(dt, n) if acc >= 0 else 0.0

    def run_dbl():
        t0 = time.perf_counter()
        acc = 0
        for i in range(n):
            acc += C.add(P[i], P[i])[0]
        dt = time.perf_counter() - t0
        return ns_per(dt, n) if acc >= 0 else 0.0
    return timed_reps(run), timed_reps(run_dbl)


def bench_mulmod(p, n):
    """Calibration: one (a*b) % p with full-size operands.  Isolates the
    CPython 30-bit-digit effect between p ~ 2^20 (1 digit) and 2^31 (2)."""
    r = np.random.default_rng(SEED + 5)
    xs = [int(v) for v in r.integers(0, p, size=n)]
    ys = [int(v) for v in r.integers(0, p, size=n)]

    def run():
        t0 = time.perf_counter()
        acc = 0
        for i in range(n):
            acc += xs[i] * ys[i] % p
        dt = time.perf_counter() - t0
        return ns_per(dt, n) if acc >= 0 else 0.0
    return timed_reps(run)



# ---------------------------------------------------------- scaling probe
P30A = 1073741789      # largest prime < 2^30  (single 30-bit CPython digit)
P30B = 1073741827      # smallest prime > 2^30  (two CPython digits)


def scaling_probe(reps=3):
    """Per-candidate cost across the CPython 30-bit digit boundary.

    If per-candidate cost were flat at fixed machine word size, p ~ 2^20 and
    p just below 2^30 would agree, and p just above 2^30 would agree with
    2^31.  Any jump at 2^30 is a CPython bignum artefact, not a log p effect.
    """
    out = {}
    for p in (P20, P30A, P30B, P31):
        a, b = A % p, B % p
        s3 = SE.s3_mod(a, b, p)
        s4 = SE.s4_mod(a, b, p)
        g4 = SE.s4_grouped_by_x4(a, b, p, s4)
        rec = {
            "digits": 1 if p < 2 ** 30 else 2,
            "S3_terms": len(s3), "S4_terms": len(s4),
            "mulmod": bench_mulmod(p, 300_000),
            "B_s3": bench_B_s3(p, a, b, 60, 60, 400, True),
            "B_s4_horner": bench_horner_only(p, 1_500, 400),
        }
        out[str(p)] = rec
        print(f"  probe p={p} (digits={rec['digits']}): mulmod "
              f"{rec['mulmod']['median_ns']:.1f}  S3 {rec['B_s3']['median_ns']:.1f}"
              f"  S4-horner {rec['B_s4_horner']['median_ns']:.1f} ns", flush=True)
    return out


# -------------------------------------------------------------- verification
def verify_loops():
    """Every optimised loop must agree value-for-value with the reference."""
    rep = {}
    for p in (101, P20):
        a, b = A % p, B % p
        s3t = SE.s3_mod(a, b, p)
        s4t = SE.s4_mod(a, b, p)
        g4 = SE.s4_grouped_by_x4(a, b, p, s4t)
        # mode B, m=3
        L1, L2, W = 7, 5, 11
        for red in (True, False):
            cnt, chk, nz = sweep_s3(p, a, b, L1, L2, W, x0=3, y0=5, z0=0,
                                    reduce_powers=red)
            ref_chk = sum(SE.s3_eval(x, y, z, a, b, p)
                          for x in range(3, 3 + L1) for y in range(5, 5 + L2)
                          for z in range(W))
            ref_nz = sum(1 for x in range(3, 3 + L1) for y in range(5, 5 + L2)
                         for z in range(W) if SE.s3_eval(x, y, z, a, b, p) == 0)
            assert (cnt, chk, nz) == (L1 * L2 * W, ref_chk, ref_nz), \
                (p, "s3 sweep", red, chk, ref_chk, nz, ref_nz)
        # mode B, m=4
        L, W = 3, 5
        cnt4, chk4, nz4 = sweep_s4(p, a, b, g4, L, L, L, W,
                                   x0=1, y0=2, z0=4, w0=0)
        ref4 = sum(SE.s4_eval(x, y, z, w, a, b, p)
                   for x in range(1, 1 + L) for y in range(2, 2 + L)
                   for z in range(4, 4 + L) for w in range(W))
        ref4z = sum(1 for x in range(1, 1 + L) for y in range(2, 2 + L)
                    for z in range(4, 4 + L) for w in range(W)
                    if SE.s4_eval(x, y, z, w, a, b, p) == 0)
        assert (cnt4, chk4, nz4) == (L ** 3 * W, ref4, ref4z), \
            (p, "s4 sweep", chk4, ref4, nz4, ref4z)
        # grouped coefficients == s4_coeffs_in_x4
        for (xx, yy, zz) in [(1, 2, 3), (0, 0, 0), (5, 5, 5)]:
            lo = list(SE.s4_coeffs_in_x4(xx, yy, zz, a, b, p, g4))
            hi = []
            for d in range(5):
                s = 0
                for (e1, e2, e3), c in g4[d].items():
                    s += c * xx ** e1 * yy ** e2 * zz ** e3
                hi.append(s % p)
            assert lo == hi, (p, lo, hi)
        # numpy batch paths, every cell vs reference
        X1 = np.asarray([3, 77, 101 % p, 5, 0], dtype=np.int64)
        X2 = np.asarray([9, 4, 0, 5, 1], dtype=np.int64)
        X3 = np.asarray([2, 8, 1, 0, 6], dtype=np.int64)
        W = 7
        V = c_s3_matrix(p, a, b, X1, X2, W)
        for i in range(len(X1)):
            for w in range(W):
                assert int(V[i, w]) == SE.s3_eval(int(X1[i]), int(X2[i]), w,
                                                 a, b, p), (p, "c_s3", i, w)
        V4 = c_s4_matrix(p, groups=g4, X1=X1, X2=X2, X3=X3, W=W)
        for i in range(len(X1)):
            for w in range(W):
                assert int(V4[i, w]) == SE.s4_eval(int(X1[i]), int(X2[i]),
                                                  int(X3[i]), w, a, b, p), \
                    (p, "c_s4", i, w)
        # no-amortise numpy term loop vs reference
        r = np.random.default_rng(SEED + 9)
        xs = [r.integers(0, p, size=8, dtype=np.int64) for _ in range(4)]
        md = [max(e[i] for e in s4t) for i in range(4)]
        pws = []
        for i in range(4):
            row = [np.ones(8, dtype=np.int64)]
            for _ in range(md[i]):
                row.append(row[-1] * xs[i] % p)
            pws.append(row)
        acc = np.zeros(8, dtype=np.int64)
        for e, c in s4t.items():
            acc = (acc + c * pws[0][e[0]] % p * pws[1][e[1]] % p
                   * pws[2][e[2]] % p * pws[3][e[3]] % p) % p
        for k in range(8):
            assert int(acc[k]) == SE.s4_eval(*[int(xs[i][k]) for i in range(4)],
                                             a, b, p), (p, "noamort", k)
        # mode A2 pattern: pre-tabulated powers, per-monomial accumulate
        for m, terms in ((3, s3t), (4, s4t)):
            md = [max(e[i] for e in terms) for i in range(m)]
            vals = [(3, 1, 4, 2)[:m], (0, 0, 0, 0)[:m],
                    tuple((p - 1 - i) for i in range(m))]
            tables = []
            for i in range(m):
                tbl = {}
                for v in {x[i] for x in vals}:
                    row = [1]
                    for _ in range(md[i]):
                        row.append(row[-1] * v % p)
                    tbl[v] = row
                tables.append(tbl)
            for x in vals:
                tabs = [tables[i][x[i]] for i in range(m)]
                acc = 0
                for e, c in terms.items():
                    s = c
                    for i in range(m):
                        s *= tabs[i][e[i]]
                    acc += s
                acc %= p
                ref = (SE.s3_eval(*x, a, b, p) if m == 3
                       else SE.s4_eval(*x, a, b, p))
                assert acc == ref, (p, "A2 pattern", m, x, acc, ref)
        rep[str(p)] = "all loops verified against semaev_eval reference"
    return rep


# ------------------------------------------------------------------- main
def main():
    t_start = time.perf_counter()
    OUT["provenance"] = {
        "script": os.path.abspath(__file__),
        "python": sys.version.split()[0],
        "python_int_digit_bits": int(sys.int_info.bits_per_digit),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "cpu": os.popen("sysctl -n machdep.cpu.brand_string").read().strip(),
        "ncpu": os.cpu_count(),
        "cpu_pinning": try_pin_to_cpu(),
        "seed": SEED,
        "curve": "y^2 = x^3 + 7 (a=0,b=7), 4a^3+27b^2 = 1323 != 0 mod both p",
        "primes": {"P20": P20, "P31": P31,
                   "why": "largest primes below 2^20 and 2^31; 2^31-1 is prime"},
        "reps": REPS,
        "timing": "time.perf_counter, single-threaded, nothing else running",
    }
    print("== provenance ==")
    print(json.dumps(OUT["provenance"], indent=2), flush=True)

    OUT["verification"] = verify_loops()
    print("== verified ==", OUT["verification"], flush=True)

    OUT["polynomials"] = {}
    OUT["timings"] = {}
    OUT["calibration_mulmod"] = {}

    for p in (P20, P31):
        pk = str(p)
        a, b = A % p, B % p
        SE.Curve(p, a, b)                       # raises if singular
        s3 = SE.s3_mod(a, b, p)
        s4 = SE.s4_mod(a, b, p)
        groups = SE.s4_grouped_by_x4(a, b, p, s4)
        s3_11 = SE.s3_mod(1, 1, p)
        s4_11 = SE.s4_mod(1, 1, p)
        OUT["polynomials"][pk] = {
            "p": p, "a": a, "b": b, "disc_nonzero": True,
            "S3_terms": len(s3), "S4_terms": len(s4),
            "S3_terms_a1b1": len(s3_11), "S4_terms_a1b1": len(s4_11),
            "S4_support_by_x4_degree": {d: len(groups[d]) for d in range(5)},
            "max_deg_per_x": [max(e[i] for e in s4) for i in range(4)],
        }
        print(f"p={p}: S3 {len(s3)} terms, S4 {len(s4)} terms "
              f"(a=b=1: {len(s3_11)}/{len(s4_11)})", flush=True)

        T = {}
        nA3 = 200_000 if p == P20 else 120_000
        nA4 = 12_000 if p == P20 else 8_000
        T["A_s3_oneshot"] = bench_A(p, nA3, 3, s3)
        T["A_s4_oneshot"] = bench_A(p, nA4, 4, s4)
        T["A2_s3_pretab"] = bench_A2(p, nA3, 3, s3)
        T["A2_s4_pretab"] = bench_A2(p, nA4, 4, s4)
        print(f"  A  S3 {T['A_s3_oneshot']['median_ns']:.0f}  "
              f"S4 {T['A_s4_oneshot']['median_ns']:.0f} ns/cand", flush=True)
        print(f"  A2 S3 {T['A2_s3_pretab']['median_ns']:.0f}  "
              f"S4 {T['A2_s4_pretab']['median_ns']:.0f} ns/cand", flush=True)

        if p == P20:
            L1, L2, W = 96, 96, 400
            trip = 3_000
        else:
            L1, L2, W = 80, 80, 400
            trip = 2_000
        T["B_s3_sweep"] = bench_B_s3(p, a, b, L1, L2, W, reduce_powers=True)
        T["B_s3_sweep_unreduced"] = bench_B_s3(p, a, b, L1, L2, W,
                                               reduce_powers=False)
        print(f"  B  S3 {T['B_s3_sweep']['median_ns']:.1f} "
              f"(unreduced {T['B_s3_sweep_unreduced']['median_ns']:.1f}) "
              f"ns/cand", flush=True)

        T["B_s4_coeff_per_triple"] = bench_B_s4_coeff_only(
            p, a, b, groups, 100_000 if p == P20 else 60_000)
        print(f"  B  S4 coef/triple {T['B_s4_coeff_per_triple']['median_ns']:.0f} ns",
              flush=True)
        T["B_s4_sweep_by_W"] = {}
        for W4, ntrip in ((32, 12_000), (96, 4_000), (384, 1_000)):
            r = bench_B_s4(p, a, b, groups, ntrip, 1, 1, W4)
            T["B_s4_sweep_by_W"][str(W4)] = r
            print(f"     S4 sweep W={W4:4d}: {r['median_ns']:.1f} ns/cand",
                  flush=True)
        T["B_s4_horner_only"] = bench_horner_only(p, 2_000, 400)
        print(f"  B  S4 Horner-only {T['B_s4_horner_only']['median_ns']:.1f} ns/cand",
              flush=True)

        T["C_s3_batch"] = bench_C_s3(p, a, b, 4096, 256)
        T["C_s4_batch_W128"] = bench_C_s4(p, a, b, groups, 512, 128)
        T["C_s4_batch_W512"] = bench_C_s4(p, a, b, groups, 256, 512)
        T["C_s4_noamortise"] = bench_C_s4_noamortise(p, a, b, s4, 128, 128)
        print(f"  C  S3 {T['C_s3_batch']['median_ns']:.2f}  "
              f"S4(W=128) {T['C_s4_batch_W128']['median_ns']:.2f}  "
              f"S4(W=512) {T['C_s4_batch_W512']['median_ns']:.2f}  "
              f"S4-noamort {T['C_s4_noamortise']['median_ns']:.2f} ns/cand", flush=True)

        ng = 20_000 if p == P20 else 12_000
        add_r, dbl_r = bench_group_add(p, a, b, ng)
        T["ref_group_add"] = add_r
        T["ref_group_double"] = dbl_r
        T["calib_mulmod"] = bench_mulmod(p, 400_000)
        OUT["calibration_mulmod"][pk] = T["calib_mulmod"]
        print(f"  ref add {add_r['median_ns']:.0f}  dbl {dbl_r['median_ns']:.0f}  "
              f"mulmod {T['calib_mulmod']['median_ns']:.1f} ns", flush=True)

        b_head = T["B_s4_sweep_by_W"]["96"]["median_ns"]
        T["ratio"] = {
            "B_s3_over_python_add": T["B_s3_sweep"]["median_ns"] / add_r["median_ns"],
            "B_s4_over_python_add": b_head / add_r["median_ns"],
            "B_s3_over_python_double": T["B_s3_sweep"]["median_ns"] / dbl_r["median_ns"],
            "B_s4_over_python_double": b_head / dbl_r["median_ns"],
            "B_s3_in_mulmods": T["B_s3_sweep"]["median_ns"] / T["calib_mulmod"]["median_ns"],
            "B_s4_in_mulmods": b_head / T["calib_mulmod"]["median_ns"],
            "B_s4_horner_only_in_mulmods":
                T["B_s4_horner_only"]["median_ns"] / T["calib_mulmod"]["median_ns"],
        }
        OUT["timings"][pk] = T

    # census-comparable a=b=1 constants at P31
    p = P31
    s3_11 = SE.s3_mod(1, 1, p)
    s4_11 = SE.s4_mod(1, 1, p)
    OUT["timings"][f"{p}_a1b1"] = {
        "S3_terms": len(s3_11), "S4_terms": len(s4_11),
        "A_s4_oneshot": bench_A(p, 6_000, 4, s4_11),
        "A2_s4_pretab": bench_A2(p, 6_000, 4, s4_11),
        "A_s3_oneshot": bench_A(p, 60_000, 3, s3_11),
    }

    print("== scaling probe across the 30-bit digit boundary ==", flush=True)
    OUT["scaling_probe"] = scaling_probe()

    OUT["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    OUT["wall_seconds"] = round(time.perf_counter() - t_start, 1)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "results_wp2.json"), "w") as fh:
        json.dump(OUT, fh, indent=2, default=str)
    print("wrote results_wp2.json", flush=True)


if __name__ == "__main__":
    main()
