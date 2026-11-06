#!/usr/bin/env python3
"""Timing-only throughput calibration for EXP-MONO-1a1be2 (TASK-20261105-ac5ad6 KX-7, DEC-20261105-f0b7c7 TP-0).

An instrument calibration, not a benchmark result and not a run. It never calls `launcher.py cell` or
`launcher.run_cell`, computes no contract cell, and writes only to a temporary directory that is deleted
unread. Every counter result (tallies, splits, chi patterns, histograms, coverage, residuals) is discarded
inside the measuring process at once and is never printed, recorded or kept; only wall time, CPU time, peak
RSS, the worker count, the host and the NUMBER OF INPUTS PROCESSED (tuples or multisets, fixed by the input
parameters) leave the process.

Measurements (each in its own child process, so that peak RSS is per measurement):
  b1       B1 analysis (launcher._analyse_all, the contract code path) at the proxies (257, 2), (43, 3),
           (29, 4), (13, 5), >= 10^4 tuples, worker counts 1 and the usable core count, group-law subsample
           every 100th tuple as in the contract.
  b1detail the same analysis with the group-law check on every tuple (the B2 code path), few tuples, 1 worker.
  armA     the arm-A exhaustive cell proxy (103, 4): line, matched-random and half-size twin base, each with
           the independent recount, in full.
  armC     the arm-C enumeration proxy (q'_2, 2) = (32779, 2): the line base, in full (s = the contract s_2).
Seed strings are prefixed "f15270|throughput|". The projections (modeled, not measured) to every contract cell
class are computed in `project` from the measured numbers and the identity fields (B, t2, |X|, Q) of the
preview trial plan; each carries its model and its assumptions.

Usage:  throughput_calibration.py --out PATH [--tuples 10000] [--trial-plan PATH]
        throughput_calibration.py --child JSON          (internal: one measurement, JSON on stdout)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import resource
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PREFIX = "f15270|throughput|"
B1_PROXIES = [(257, 2), (43, 3), (29, 4), (13, 5)]
ARM_A_PROXY = (103, 4)
MEM_CAP_BYTES = 16 * 2 ** 30
TP1_HOURS = 24.0
GL_STEP = 100                      # contract B1 group-law subsample fraction 0.01
CONTRACT_B1_TUPLES = 10 ** 6
B2_TUPLES_PER_INSTANCE = 10 ** 4
B2_INSTANCES = 2


def usable_cores() -> int:
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:  # pragma: no cover
        return os.cpu_count() or 1


def host_record() -> dict:
    u = platform.uname()
    model = None
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("model name"):
                    model = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    mem = None
    try:
        with open("/proc/meminfo") as fh:
            mem = int(fh.readline().split()[1])
    except (OSError, ValueError):
        pass
    return {"node": u.node, "system": u.system, "release": u.release, "machine": u.machine, "cpu_model": model,
            "cpu_count": os.cpu_count(), "usable_cores": usable_cores(), "mem_total_kb": mem,
            "python": sys.version.split()[0]}


# ----------------------------------------------------------------------------- child: one measurement
def _cpu_seconds() -> dict:
    t = os.times()
    return {"user": t.user + t.children_user, "system": t.system + t.children_system}


def _peaks() -> dict:
    return {"peak_rss_self_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "peak_rss_children_max_kb": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}


def _timed(fn):
    c0, t0 = _cpu_seconds(), time.perf_counter()
    fn()
    wall = time.perf_counter() - t0
    c1 = _cpu_seconds()
    return {"wall_s": wall, "cpu_user_s": c1["user"] - c0["user"], "cpu_system_s": c1["system"] - c0["system"]}


def child_b1(cfg: dict, detail: bool) -> dict:
    import curves
    import fqn
    import launcher
    q, n, T, W = cfg["q"], cfg["n"], cfg["tuples"], cfg["workers"]
    F = fqn.FQ(q, n)
    E, _ = curves.generate_curve(F, f"{PREFIX}curve|{q}|{n}")
    rng = curves.make_rng(f"{PREFIX}tuples|{'detail|' if detail else ''}{q}|{n}")
    xs = rng.integers(0, q, size=(T, n, n))
    gl = [True] * T if detail else [(i % GL_STEP == 0) for i in range(T)]
    box = {}

    def work():
        box["r"] = launcher._analyse_all(F, E, xs, gl, W)
        del box["r"]                                     # the tally is discarded unread

    out = _timed(work)
    out.update(kind="b1detail" if detail else "b1", q=q, n=n, workers=W, tuples=T,
               group_law_tuples=T if detail else sum(1 for g in gl if g), analysis_block_size=2000)
    return out


def child_arm_a(cfg: dict) -> dict:
    import counters
    import curves
    import fqn
    q, n = cfg["q"], cfg["n"]
    tmp = tempfile.mkdtemp(prefix="mono1a1be2-calib-kernel-", dir=cfg["tmpdir"])
    kernel = counters.Kernel(counters.build_kernel(tmp))
    F = fqn.FQ(q, n)
    t0 = time.perf_counter()
    E, _ = curves.generate_curve(F, f"{PREFIX}A|{n}|{q}|0")
    N, mask = kernel.valid_mask(E)
    D, X, t2 = E.factor_base()
    B = len(D)
    out = {"kind": "armA", "q": q, "n": n, "m": n, "Q": F.Q, "B": B, "t2": t2, "size_X": len(X),
           "setup_wall_s": time.perf_counter() - t0, "bases": {}, "partial_fraction": 1.0}
    seeds = {"line": None, "matched_random": f"{PREFIX}base|A-n{n}-q{q}-c0|random|0",
             "half_twin": f"{PREFIX}base|A-n{n}-q{q}-c0|twin|0"}
    for role, seed in seeds.items():
        if role == "line":
            pts = D
        elif role == "matched_random":
            pts = counters.matched_random_base(E, B, t2, curves.make_rng(seed))
        else:
            pts = counters.twin_base(E, B, t2, curves.make_rng(seed))
        Xl = counters.x_lifts(F, pts)
        box = {}

        def work():
            box["r"] = counters.exhaustive_cell(kernel, E, pts, Xl, n, N, mask, recount=True)
            del box["r"]                                 # histograms, tallies and residuals discarded unread

        t = _timed(work)
        t.update(B=len(pts), t2=sum(1 for P in pts if F.is_zero(P[1])), size_X=len(Xl), recount=True)
        out["bases"][role] = t
    return out


def child_arm_c(cfg: dict) -> dict:
    import counters
    import curves
    import fqn
    import make_trial_plan as mtp
    q, n = cfg["q"], cfg["n"]
    tmp = tempfile.mkdtemp(prefix="mono1a1be2-calib-kernel-", dir=cfg["tmpdir"])
    kernel = counters.Kernel(counters.build_kernel(tmp))
    F = fqn.FQ(q, n)
    t0 = time.perf_counter()
    E, _ = curves.generate_curve(F, f"{PREFIX}C|{n}|{q}|0")
    N, _ = E.count_points_bsgs()
    D, X, t2 = E.factor_base()
    setup = time.perf_counter() - t0
    s = mtp.sample_size_rule(n)
    tr = curves.make_rng(f"{PREFIX}targets|C-n{n}-q{q}-c0")
    box = {}

    def work():
        box["r"] = counters.arm_c_cell(kernel, E, D, n, s, tr, N)
        del box["r"]

    out = _timed(work)
    out.update(kind="armC", q=q, n=n, m=n, Q=F.Q, B=len(D), t2=t2, size_X=len(X), s=s, setup_wall_s=setup,
               multisets=math.comb(len(D) + n - 1, n), bases_enumerated=1, partial_fraction=1.0)
    return out


def child_main(cfg: dict) -> int:
    resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP_BYTES, MEM_CAP_BYTES))
    kind = cfg["kind"]
    if kind == "b1":
        res = child_b1(cfg, detail=False)
    elif kind == "b1detail":
        res = child_b1(cfg, detail=True)
    elif kind == "armA":
        res = child_arm_a(cfg)
    elif kind == "armC":
        res = child_arm_c(cfg)
    else:
        raise ValueError(kind)
    res.update(_peaks())
    res["total_process_wall_s"] = time.perf_counter() - cfg.get("_t0", time.perf_counter())
    print(json.dumps(res))
    return 0


# ----------------------------------------------------------------------------- parent: orchestration
def run_child(cfg: dict, tmpdir: str, log) -> dict:
    cfg = dict(cfg, tmpdir=tmpdir)
    log(f"measuring {cfg['kind']} {cfg.get('q')} {cfg.get('n')} workers={cfg.get('workers', 1)}")
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--child", json.dumps(cfg)],
                       capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=tmpdir))
    if r.returncode != 0:
        raise RuntimeError(f"measurement {cfg} failed (rc={r.returncode}); stderr tail: {r.stderr[-600:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


# ----------------------------------------------------------------------------- projections (modeled)
def _leaf_work(B: int, t2: int, m: int) -> float:
    """Ordered-type enumeration leaves of one arm-A base: passes T_A, T_A weighted, recount A (B^m each) and T_S,
    recount S ((B+t2)^m each), plus the multiset passes (3 x C(B+m-1, m)); the x-multiset passes are bounded by the
    multiset-pass count times 2^(m-1) and are added likewise (2 passes)."""
    return (3 * B ** m + 2 * (B + t2) ** m + 3 * math.comb(B + m - 1, m)
            + 2 * math.comb(B + m - 1, m) * 2 ** (m - 1))


def project(meas: dict, plan_cells: list, usable: int) -> dict:
    out = {"label": "MODELED (projected from the measured proxy timings; not measured)", "usable_workers": usable}
    # ---- B1: per-tuple wall from the proxies, projected to 10^6 tuples
    b1 = {}
    for (q, n) in B1_PROXIES:
        rows = {w: r for (k, qq, nn, w), r in meas["b1"].items() if (qq, nn) == (q, n)}
        entry = {"proxy": [q, n]}
        for w, r in sorted(rows.items()):
            per_tuple = r["wall_s"] / r["tuples"]
            entry[f"workers_{w}"] = {"measured_wall_s_per_tuple": per_tuple,
                                     "modeled_wall_s_per_1e6_tuples": per_tuple * CONTRACT_B1_TUPLES,
                                     "modeled_wall_h_per_1e6_tuples": per_tuple * CONTRACT_B1_TUPLES / 3600,
                                     "modeled_wall_h_with_aa_sample_2e6_tuples": 2 * per_tuple * CONTRACT_B1_TUPLES / 3600}
        b1[f"n{n}"] = entry
    top = max(b1.values(), key=lambda e: e[f"workers_{usable}"]["modeled_wall_h_per_1e6_tuples"])
    worst_h = top[f"workers_{usable}"]["modeled_wall_h_per_1e6_tuples"]
    worst_h_aa = top[f"workers_{usable}"]["modeled_wall_h_with_aa_sample_2e6_tuples"]
    out["B1"] = {"model": "per-tuple wall at the proxy (q', n) x 10^6 tuples; the contract second-rung q is smaller "
                          "than the proxy q, so only the n-dependence is transferred (F_q arithmetic is a small factor)",
                 "per_n": b1,
                 "tp1_rule": f"one B1 cell of 10^6 tuples > {TP1_HOURS:.0f} h wall at the sustainable worker count",
                 "worker_count_used": usable,
                 "worst_cell_hours_1e6_tuples": worst_h,
                 "worst_cell_hours_with_aa_sample": worst_h_aa,
                 "tp1_triggers_literal_rule": worst_h > TP1_HOURS,
                 "tp1_triggers_if_aa_sample_counted": worst_h_aa > TP1_HOURS,
                 "tp1_triggers_at_one_worker_for_reference": any(
                     e["workers_1"]["modeled_wall_h_per_1e6_tuples"] > TP1_HOURS for e in b1.values())}
    # ---- B2: all tuples carry the group-law check
    b2 = {}
    for (q, n) in B1_PROXIES:
        d = meas["b1detail"][(q, n)]
        t_det = d["wall_s"] / d["tuples"]
        r1 = meas["b1"][("b1", q, n, 1)]
        ru = meas["b1"][("b1", q, n, usable)]
        speed = (r1["wall_s"] / r1["tuples"]) / (ru["wall_s"] / ru["tuples"])
        total = B2_INSTANCES * B2_TUPLES_PER_INSTANCE * t_det
        b2[f"n{n}"] = {"measured_detail_wall_s_per_tuple_1_worker": t_det,
                       "measured_B1_speedup_at_usable_workers": speed,
                       "modeled_cell_wall_s_1_worker": total,
                       "modeled_cell_wall_s_usable_workers": total / speed,
                       "assumption": "2 instances x 10^4 tuples (the maximum; C(|X|, n) may be smaller), "
                                     "group-law check on every tuple, parallel speed-up as measured for B1"}
    out["B2"] = b2
    # ---- arm A: per-base proxy time scaled by the larger of two analytic ratios
    a = meas["armA"]
    pq, pn = a["q"], a["n"]
    proxy = {role: v for role, v in a["bases"].items()}
    cls = {}
    for c in plan_cells:
        if c["arm"] != "A":
            continue
        n, q, ident = c["n"], c["q"], c["identity"]
        B, t2, Q = ident["B"], ident["t2"], ident["Q"]
        twin_B = t2 + 2 * (-(-(B - t2) // 4))
        parts = {}
        for role, Bb in (("line", B), ("matched_random", B), ("half_twin", twin_B), ("matched_random_reseeded_aa", B)):
            pr = proxy["matched_random" if role == "matched_random_reseeded_aa" else role]
            tb = pr["t2"]
            lr = _leaf_work(Bb, t2 if role != "half_twin" else t2, n) / _leaf_work(pr["B"], tb, pn)
            qr = Q / a["Q"]
            parts[role] = pr["wall_s"] * max(lr, qr)
        key = f"n{n}-q{q}"
        cls.setdefault(key, []).append({"curve_index": c["curve_index"], "B": B, "t2": t2, "Q": Q,
                                        "modeled_cell_wall_s": sum(parts.values()),
                                        "modeled_per_base_wall_s": parts})
    out["armA"] = {"model": "per base: measured proxy wall of the same base role x max(leaf-work ratio, Q ratio); "
                            "4 bases per cell (line, matched random, half twin, matched random re-seeded); wall at 1 worker "
                            "(the exhaustive cell is single-process); recount included",
                   "proxy": [pq, pn], "classes": cls}
    # ---- arm C
    c_meas = meas["armC"]
    per_multiset = c_meas["wall_s"] / c_meas["multisets"]
    setup_proxy = c_meas["setup_wall_s"]
    ccls = {}
    for c in plan_cells:
        if c["arm"] != "C":
            continue
        n, q, ident = c["n"], c["q"], c["identity"]
        B = ident["B"]
        mult = math.comb(B + n - 1, n)
        base_opt = per_multiset * mult
        base_n2 = per_multiset * (n / 2) ** 2 * mult
        key = f"n{n}-q{q}"
        ccls.setdefault(key, []).append({
            "curve_index": c["curve_index"], "B": B, "multisets_per_base": mult,
            "modeled_cell_wall_s_optimistic_equal_per_multiset_cost": 2 * base_opt + setup_proxy,
            "modeled_cell_wall_s_headline_per_multiset_cost_x_(n/2)^2": 2 * base_n2 + setup_proxy})
    out["armC"] = {"model": "measured per-multiset wall at the proxy (q'_2, 2) x multisets of the cell x 2 bases (line and "
                            "matched random) + the proxy's measured setup (curve, BSGS count, factor base) as an upper "
                            "bound; headline scales the per-multiset cost by (n/2)^2 (field multiplication grows about "
                            "as n^2), 'optimistic' keeps it constant. Proxy enumerates one base, in full.",
                   "measured_wall_s_per_multiset_proxy": per_multiset, "proxy_setup_wall_s": setup_proxy,
                   "classes": ccls}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--child")
    ap.add_argument("--out")
    ap.add_argument("--tuples", type=int, default=10 ** 4)
    ap.add_argument("--detail-tuples", type=int, default=500)
    ap.add_argument("--trial-plan", default=os.path.join(HERE, "..", "implementation", "trial-plan.preview.json"))
    ap.add_argument("--skip-arm-a", action="store_true")
    ap.add_argument("--skip-arm-c", action="store_true")
    args = ap.parse_args(argv)
    if args.child:
        return child_main(json.loads(args.child))
    if not args.out:
        ap.error("--out is required")
    if args.tuples < 10 ** 4:
        ap.error("the card requires at least 10^4 tuples per B1 proxy")
    usable = usable_cores()
    tmpdir = tempfile.mkdtemp(prefix="mono1a1be2-calibration-")
    t_start = time.time()
    msgs = []

    def log(s):
        msgs.append(s)
        print(s, file=sys.stderr, flush=True)

    meas = {"b1": {}, "b1detail": {}}
    try:
        for (q, n) in B1_PROXIES:
            for w in sorted({1, usable}):
                r = run_child({"kind": "b1", "q": q, "n": n, "tuples": args.tuples, "workers": w}, tmpdir, log)
                meas["b1"][("b1", q, n, w)] = r
        for (q, n) in B1_PROXIES:
            meas["b1detail"][(q, n)] = run_child({"kind": "b1detail", "q": q, "n": n, "tuples": args.detail_tuples,
                                                  "workers": 1}, tmpdir, log)
        if not args.skip_arm_a:
            meas["armA"] = run_child({"kind": "armA", "q": ARM_A_PROXY[0], "n": ARM_A_PROXY[1]}, tmpdir, log)
        if not args.skip_arm_c:
            import make_trial_plan as mtp
            import fqn
            qp = fqn.next_prime_above(mtp.q_rule(2))
            meas["armC"] = run_child({"kind": "armC", "q": qp, "n": 2}, tmpdir, log)
        with open(args.trial_plan) as fh:
            plan_cells = json.load(fh)["cells"]
        proj = project(meas, plan_cells, usable) if not (args.skip_arm_a or args.skip_arm_c) else None
        doc = {
            "task": "TASK-20261105-ac5ad6", "experiment": "EXP-MONO-1a1be2", "kind": "instrument throughput calibration",
            "note": "Timing only (DEC-20261105-f0b7c7 TP-0). Not a run and not a benchmark; no performance claim. No "
                    "tally, split or chi-pattern count, histogram, coverage or residual was printed, recorded or kept; "
                    "the temporary directory was deleted unread. MEASURED fields are timings of the proxy cells; the "
                    "'projection' section is MODELED.",
            "seed_prefix": PREFIX, "host": host_record(), "worker_counts": sorted({1, usable}),
            "memory_cap_gb": 16, "started_unix": t_start, "total_wall_s": time.time() - t_start,
            "measured": {
                "b1": [meas["b1"][k] for k in sorted(meas["b1"])],
                "b1detail": [meas["b1detail"][k] for k in sorted(meas["b1detail"])],
                "armA": meas.get("armA"), "armC": meas.get("armC")},
            "projection": proj,
            "tp1": {"rule": "DEC-20261105-f0b7c7 TP-1: a projection for one B1 cell of 10^6 tuples above 24 h wall at the "
                            "sustainable worker count means no approval and a compiled-B1-port task instead",
                    "would_trigger": None if proj is None else proj["B1"]["tp1_triggers_literal_rule"]},
        }
        with open(args.out, "w") as fh:
            fh.write(json.dumps(doc, indent=1, sort_keys=True) + "\n")
        print(f"wrote {args.out}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
