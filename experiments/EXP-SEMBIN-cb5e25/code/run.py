#!/usr/bin/env python3
"""Launcher for ONE trial = one (cell, arm, r) of EXP-SEMBIN-cb5e25.

    python3 experiments/EXP-SEMBIN-cb5e25/code/run.py --run-dir <DIR> \\
        --cell m3n06 --arm EQS4 --r 0 --protocol-sha256 <hex>

The run directory is allocated by the caller (this script allocates nothing,
never deletes, and refuses to overwrite a finished trial). It APPENDS records:
  instances.jsonl.gz   M-10 + Z + redraw logs (one gzip member per instance)
  closures.jsonl.gz    M-1..M-7 per instance per D, and a per-instance summary
  cost.jsonl           M-9 (wall, CPU, peak RSS, load, poll interval)
  certificates/        ann-v1 / wdag-v1 (gzipped) ; systems/ canonical serialisations
  trials/<id>.json     trial status and provenance
Every closure runs in a forked child that the parent watches (wall cap and an
RSS watchdog on VmRSS; never RLIMIT_AS).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing
import os
import resource
import sys
import time
import traceback

import _paths  # noqa: F401
import cells as CE
import certs
import closure as CL
import descent as DS
import dfeq
import enumz
import fullring
import nulls
import positive_control
import provenance
import reencode
from rng import HashRng, seed_for

POLL_INTERVAL_S = 0.25
RSS_CAP_BYTES = 10 * 1024 ** 3
WALL_CAP = {"N_le_32": 1800, "N_40": 7200}
CERT_D = 4          # default claim degree for certificates (override: --cert-degree)
BRUTE_TARGET_MAX = 20
BRUTE_NULL_MAX = 26   # spec: nulls brute-forced at N <= 24; extended to 26 so that NULL-SHUF (N <= 26) has a Z


# --------------------------------------------------------------------------
# small io helpers
# --------------------------------------------------------------------------
def append_gz_jsonl(path, obj):
    data = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with open(path, "ab") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as g:
            g.write(data)


def append_jsonl(path, obj):
    with open(path, "a") as f:
        f.write(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n")


def safe(key):
    return key.replace("/", "_")


def rss_bytes(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        pass
    return 0


# --------------------------------------------------------------------------
# isolated execution with wall cap and RSS watchdog
# --------------------------------------------------------------------------
def _child_main(fn, arg, conn):
    try:
        out = fn(arg)
        out["_child_maxrss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        conn.send(("ok", out))
    except BaseException as exc:      # noqa: BLE001
        conn.send(("error", {"error": repr(exc), "traceback": traceback.format_exc()}))
    finally:
        conn.close()


def run_isolated(fn, arg, wall_cap_s, rss_cap=RSS_CAP_BYTES, isolate=True):
    """Returns (status, payload, meta). status in ok | censored_wall | censored_rss |
    failed_infrastructure | error."""
    t0, c0 = time.time(), time.process_time()
    if not isolate:
        try:
            out = fn(arg)
            return "ok", out, {"wall_s": time.time() - t0, "cpu_s": time.process_time() - c0,
                               "peak_rss_polled_bytes": None,
                               "peak_rss_ru_maxrss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        except Exception as exc:     # noqa: BLE001
            return "error", {"error": repr(exc), "traceback": traceback.format_exc()}, {"wall_s": time.time() - t0}
    ctx = multiprocessing.get_context("fork")
    parent, child = ctx.Pipe(False)
    p = ctx.Process(target=_child_main, args=(fn, arg, child))
    p.start()
    child.close()
    peak, status, payload = 0, None, None
    while True:
        if parent.poll(POLL_INTERVAL_S):
            try:
                kind, payload = parent.recv()
            except EOFError:
                kind, payload = "crash", {"error": "pipe closed"}
            status = "ok" if kind == "ok" else ("error" if kind == "error" else "failed_infrastructure")
            break
        peak = max(peak, rss_bytes(p.pid))
        if peak > rss_cap:
            p.kill()
            status, payload = "censored_rss", {"error": f"RSS {peak} exceeded {rss_cap}"}
            break
        if time.time() - t0 > wall_cap_s:
            p.kill()
            status, payload = "censored_wall", {"error": f"wall cap {wall_cap_s}s exceeded"}
            break
        if not p.is_alive() and not parent.poll():
            status, payload = "failed_infrastructure", {"error": f"child exited with {p.exitcode}"}
            break
    p.join(timeout=30)
    meta = {"wall_s": time.time() - t0, "cpu_s_parent": time.process_time() - c0,
            "peak_rss_polled_bytes": peak, "poll_interval_s": POLL_INTERVAL_S,
            "child_exitcode": p.exitcode}
    if status == "ok":
        meta["peak_rss_ru_maxrss_kb"] = payload.get("_child_maxrss_kb")
    return status, payload, meta


# --------------------------------------------------------------------------
# the closure task (runs in the child)
# --------------------------------------------------------------------------
def closure_task(task):
    nv, D, eqs = task["nv"], task["D"], task["eqs"]
    out = {}
    rec, cl = CL.w_closure_record(nv, D, eqs)
    out["rec"] = {k: rec[k] for k in ("iterations_to_fixpoint", "dims", "final_dim", "one",
                                       "one_first_iteration", "dims_by_deg", "new_fallen_per_iteration",
                                       "stack_rows_per_iteration", "series", "C", "macaulay_rows",
                                       "wall_s", "cpu_s", "linear_forms", "const_in_W")}
    gbt = task.get("gb")
    dec = None
    if gbt is not None:
        gb = {"z": gbt["z"], "d_GB": gbt["d_GB"]}
        dec = CL.decide(nv, D, rec, gb, gbt["rank_ev"][D])
        out["decision"] = dec
        gpolys = gbt["gens"]
        if task.get("direct_membership") and len(gpolys) <= 4000 and gbt["d_GB"] <= D:
            r = CL.gb_membership(cl, gpolys)
            out["direct_membership"] = {"all_in_W": r[0], "per_element": r[1]}
            if r[0] != dec["contained"]:
                out["der3_mismatch"] = True
    if task.get("lin_forms"):
        out["lin_forms"] = cl.linear_part()
    if task.get("compute_m7"):
        mrec, mcl = CL.m_closure_record(nv, D, eqs)
        m7 = {"rank": mrec["rank"], "one": mrec["one"], "dims_by_deg": mrec["dims_by_deg"]}
        if gbt is not None and gbt["d_GB"] <= D:
            m7["gb_in_M"] = all(bool(mcl.member(g)) for g in gbt["gens"]) if len(gbt["gens"]) <= 4000 else None
        elif gbt is not None:
            m7["gb_in_M"] = False
        out["m7"] = m7
        del mcl
    return out


WDAG_WALL_CAP_S = 900
WDAG_MAX_JSON_BYTES = 400 * 10 ** 6


def cert_task(task):
    """Certificate child (separate from the closure child). Recomputes W_D, must
    reproduce the recorded final dimension, then emits one certificate."""
    nv, D, eqs = task["nv"], task["D"], task["eqs"]
    rec, cl = CL.w_closure_record(nv, D, eqs)
    if rec["final_dim"] != task["expected_final_dim"]:
        return {"info": {"status": "not_emitted", "reason": "dimension_mismatch",
                         "recomputed": rec["final_dim"], "expected": task["expected_final_dim"], "flag": True}}
    gp = task["gens"]
    prefix = task["cert_prefix"]
    if task["kind"] == "ann":
        idx = next((i for i, g in enumerate(gp) if not cl.member(g)), None)
        if idx is None:
            return {"info": {"status": "not_emitted", "reason": "no GB element outside W_D found", "flag": True}}
        c = certs.make_ann_cert(cl, nv, eqs, gp[idx], idx, task["cert_meta"], task["Z"],
                                max_bytes=task.get("ann_max_bytes", 512 << 20))
        if "not_emitted" in c:
            return {"info": {"status": "not_emitted", "reason": c["not_emitted"], "form": c.get("form")}}
        info = certs.write_cert(prefix + ".ann.json.gz", c)
        info.update(status="pending_checker", form=c["form"], g_gb_index=idx, g=c["g"],
                    cert_sha256=certs.cert_sha256(c))
    else:
        c = certs.make_wdag_cert(cl, nv, eqs, gp, task["cert_meta"], task["Z"],
                                 expected_final_dim=rec["final_dim"])
        info = certs.write_cert(prefix + ".wdag.json.gz", c, max_bytes=task.get("max_json_bytes", WDAG_MAX_JSON_BYTES))
        if "not_emitted" in info:
            return {"info": {"status": "not_emitted", "reason": info["not_emitted"]}}
        info.update(status="pending_checker", nodes=len(c["nodes"]), cert_sha256=certs.cert_sha256(c))
    info["path"] = os.path.relpath(info["path"], task["run_dir"])
    return {"info": info}


def emit_certificate(run_dir, cfile, costfile, key, cell_id, kind, D, nv, eqs, Z, gens, meta, expected_dim,
                     isolate=True, ann_max_bytes=512 << 20, wall_cap=WDAG_WALL_CAP_S):
    """Run the certificate child and append a certificate record (M-8 status vocabulary:
    pending_checker | not_emitted). Never alters any closure record."""
    task = {"nv": nv, "D": D, "eqs": eqs, "Z": Z, "gens": gens, "kind": kind, "cert_meta": meta,
            "expected_final_dim": expected_dim, "run_dir": run_dir, "ann_max_bytes": ann_max_bytes,
            "max_json_bytes": WDAG_MAX_JSON_BYTES,
            "cert_prefix": os.path.join(run_dir, "certificates", safe(key) + f".D{D}")}
    st, payload, m9 = run_isolated(cert_task, task, wall_cap if kind == "wdag" else 7200, isolate=isolate)
    if st == "ok":
        info = payload["info"]
    elif st == "censored_wall":
        info = {"status": "not_emitted", "reason": f"wall cap exceeded ({wall_cap}s)"}
    elif st == "censored_rss":
        info = {"status": "not_emitted", "reason": "RSS watchdog (10 GB)"}
    else:
        info = {"status": "not_emitted", "reason": f"{st}: {payload}"}
    m9.update(kind="certificate", cert_kind=kind)
    append_gz_jsonl(cfile, {"kind": "certificate", "key": key, "cell": cell_id, "D": D, "cert_kind": kind,
                            "M8": info, "M9": m9})
    append_jsonl(costfile, {"key": key, "D": D, "status": st, "what": "certificate_" + kind, **m9})
    return info


def wdag_policy(a, N):
    """wdag emission rule (DR-8): 'now' (N <= 20), 'selection_pass' (21..26, two per cell by the
    nonce, see certify.py), 'none' (N >= 27). --wdag always/never override (tests, repairs)."""
    if a.wdag == "never":
        return "none"
    if a.wdag == "always":
        return "now"
    if N <= 20:
        return "now"
    if N <= 26:
        return "selection_pass"
    return "none"


# --------------------------------------------------------------------------
# instance construction
# --------------------------------------------------------------------------
_E_CACHE = {}


def shared_part(cell, r, proto):
    n, k, m = cell["n"], cell["k"], cell["m"]
    F = DS.Field(n)
    rng = HashRng(seed_for(proto, "SHARED", cell["id"], r), "shared")
    A, B, v, info = DS.draw_shared(F, m, k, rng)
    curve = DS.Curve(F, A, B)
    key = (n, A, B)
    if key not in _E_CACHE:
        _E_CACHE[key] = curve.count_points()
    return {"F": F, "curve": curve, "A": A, "B": B, "v": v, "info": info, "E": _E_CACHE[key]}


def plant_stream(proto, arm, cell_id, r, a):
    if arm == "EQS2":
        return HashRng(seed_for(proto, "EQS2", cell_id, r), "plant")
    if a == 0:
        return HashRng(seed_for(proto, "EQS4", cell_id, r), "plant")
    return HashRng(seed_for(proto, "EQS4-U", f"{cell_id}/a{a}", r), "plant")


def eqs_instance(cell, sh, arm, r, proto, a=0, with_system=True):
    """EQS4 (nonzero shifts) or EQS2 (v = 0) at attempt a."""
    F, curve, B = sh["F"], sh["curve"], sh["B"]
    k, m, n = cell["k"], cell["m"], cell["n"]
    v = [0] * m if arm == "EQS2" else sh["v"]
    pl = DS.plant(F, curve, v, k, plant_stream(proto, arm, cell["id"], r, a))
    Z = enumz.enumerate_Z(F, B, v, k, pl["x_R"])
    inst = {"arm": arm, "cell": cell["id"], "r": r, "attempt": a, "plant": pl, "v": v, "Z": Z,
            "z_method": "algebraic_chain", "x_R": pl["x_R"]}
    if with_system:
        sysd = DS.build_system(F, B, v, k, pl["x_R"])
        inst["raw_eqs"] = sysd["eqs"]
        inst["nv"] = sysd["nv"]
    return inst


def base_meta(cell, sh, inst):
    F = sh["F"]
    pl = inst["plant"]
    return {"n": F.n, "field_poly": F.poly, "A": sh["A"], "B": sh["B"], "m": cell["m"], "k": cell["k"],
            "v": inst["v"], "x_R": inst["x_R"], "num_points_E": sh["E"]}


def validate_shifts(cell, v, EQS4=True):
    k = cell["k"]
    ok_out = all(x >> k for x in v)
    distinct = all(((v[i] ^ v[j]) >> k) != 0 for i in range(len(v)) for j in range(i))
    return ok_out and distinct


# --------------------------------------------------------------------------
# the trial
# --------------------------------------------------------------------------
def run_trial(a):
    if a.require_fixtures:
        if not os.path.exists(a.require_fixtures):
            raise SystemExit("SR-1: fixtures.json missing; fixtures must run first")
        fx = json.load(open(a.require_fixtures))["fixtures"]
        if any(x["verdict"] != "pass" for x in fx) or len(fx) < 8:
            raise SystemExit("SR-1: a fixture failed or is not_covered (counts as failure) or F-1..F-8 incomplete; "
                             "no target instance may run")
    cell = CE.CELLS[a.cell]
    CE.check_cell(cell)
    run_dir = a.run_dir
    os.makedirs(os.path.join(run_dir, "trials"), exist_ok=True)
    os.makedirs(os.path.join(run_dir, "certificates"), exist_ok=True)
    os.makedirs(os.path.join(run_dir, "systems"), exist_ok=True)
    tid = f"{a.cell}__{a.arm}__r{a.r}" + (f"__{a.aa_source}" if a.arm == "EQS4-AA" else "")
    tpath = os.path.join(run_dir, "trials", tid + ".json")
    if os.path.exists(tpath) or os.path.exists(tpath + ".started"):
        raise SystemExit(f"refusing to overwrite finished/started trial {tid}")
    t_start = time.time()
    with open(tpath + ".started", "w") as f:
        json.dump({"started": t_start}, f)
    key = f"{a.cell}/{a.arm}/r{a.r}" + ("-U" if a.arm == "EQS4-AA" and a.aa_source == "EQS4-U" else "")
    N, M = cell["N"], cell["M"]
    wall_cap = a.wall_cap or (WALL_CAP["N_40"] if N >= 40 else WALL_CAP["N_le_32"])
    status = {"trial": tid, "key": key, "cell": a.cell, "arm": a.arm, "r": a.r,
              "provenance": {"git": provenance.git_state(), "env": provenance.environment(),
                             "engine": CL.engine_provenance(), "generator_mode": a.generator_mode,
                             "protocol_sha256": a.protocol_sha256,
                             "code_sha256_loaded": provenance.loaded_code_hashes()},
              "args": vars(a)}
    cfile = os.path.join(run_dir, "closures.jsonl.gz")
    ifile = os.path.join(run_dir, "instances.jsonl.gz")
    costfile = os.path.join(run_dir, "cost.jsonl")
    try:
        sh = shared_part(cell, a.r, a.protocol_sha256)
        arm = a.arm
        results = {"instances": []}
        if arm in ("EQS4", "EQS2", "EQS4-U"):
            if arm == "EQS4-U":
                inst = pick_unique(cell, sh, a, results)
            else:
                try:
                    inst = eqs_instance(cell, sh, arm, a.r, a.protocol_sha256)
                except DS.PlantInfeasible as exc:
                    inst = None
                    results["not_available"] = f"{arm}: {exc} (not a result)"
            if inst is not None:
                finish_and_evaluate(a, cell, sh, inst, key, arm, wall_cap, ifile, cfile, costfile, results)
        elif arm in ("NULL-PROF", "NULL-SHUF", "PC-TRI", "EQS4-AA", "EQS4-FULLFE", "EQS4-NOFE"):
            src_arm = "EQS4"
            src = eqs_instance(cell, sh, src_arm, a.r, a.protocol_sha256)
            if arm == "EQS4-AA" and a.aa_source == "EQS4-U":
                src = pick_unique(cell, sh, a, results, evaluate=False)
                if src is None:
                    status["note"] = "EQS4-U not available for this seed"
            if src is not None:
                derived_instance(a, cell, sh, src, key, arm, wall_cap, ifile, cfile, costfile, results)
        else:
            raise SystemExit(f"unknown arm {arm}")
        status["status"] = "completed"
        status["results"] = results
    except SystemExit:
        raise
    except Exception as exc:      # noqa: BLE001
        status["status"] = "error"
        status["error"] = repr(exc)
        status["traceback"] = traceback.format_exc()
    status["wall_s"] = time.time() - t_start
    with open(tpath, "w") as f:
        json.dump(status, f, indent=1, sort_keys=True, default=str)
    return status


def pick_unique(cell, sh, a, results, evaluate=True):
    """EQS4-U: first of 32 attempts with |Z| = 1 (depends on |Z| only)."""
    log = []
    chosen = None
    for att in range(32):
        try:
            inst = eqs_instance(cell, sh, "EQS4", a.r, a.protocol_sha256, a=att, with_system=False)
        except DS.PlantInfeasible as exc:
            log.append({"attempt": att, "z": None, "plant_infeasible": str(exc),
                        "curve": [sh["A"], sh["B"]], "counted_as": "non-unique"})
            continue
        # arm stream: attempt 0 uses the EQS4 stream (same instance), a>=1 EQS4-U/<cell>/a<a>
        log.append({"attempt": att, "z": len(inst["Z"]), "R": list(inst["plant"]["R"]),
                    "curve": [sh["A"], sh["B"]], "x_R": inst["x_R"]})
        if len(inst["Z"]) == 1:
            chosen = att
            break
    results["u_attempts"] = log
    if chosen is None:
        results["eqs4u"] = "not_available"
        return None
    inst = eqs_instance(cell, sh, "EQS4", a.r, a.protocol_sha256, a=chosen)
    inst["arm"] = "EQS4-U"
    inst["attempt"] = chosen
    results["eqs4u"] = {"attempt": chosen, "same_as_EQS4": chosen == 0}
    if chosen == 0 and evaluate:
        results["note"] = "a = 0 is unique: EQS4-U is the EQS4 instance and is evaluated once (under EQS4)"
        append_gz_jsonl(os.path.join(a.run_dir, "instances.jsonl.gz"),
                        {"key": f"{a.cell}/EQS4-U/r{a.r}", "duplicate_of": f"{a.cell}/EQS4/r{a.r}",
                         "attempt": 0, "u_attempts": log})
        return None
    return inst


def instance_record(key, cell, sh, inst, eqs_raw, eqs_used, adapt_stats, extra=None):
    nv = inst["nv"]
    rec = {
        "key": key, "arm": inst["arm"], "cell": cell["id"], "r": inst["r"], "attempt": inst.get("attempt", 0),
        "N": nv, "M": len(eqs_raw), "M_effective": len(eqs_used),
        "raw_degree_profile": DS.degree_profile(eqs_raw),
        "raw_system_sha256": DS.system_sha256(nv, eqs_raw),
        "system_sha256": DS.system_sha256(nv, eqs_used),
        "adapted": adapt_stats,
        "z": len(inst["Z"]) if inst.get("Z") is not None else None,
        "Z_hex": [format(z, "x") for z in inst["Z"][:4096]] if inst.get("Z") is not None else None,
        "z_method": inst.get("z_method"),
        "meta": base_meta(cell, sh, inst) if "plant" in inst and inst["arm"] in ("EQS4", "EQS4-U", "EQS2") else None,
    }
    if "plant" in inst:
        pl = inst["plant"]
        rec["planted"] = {"P": [list(p) for p in pl["P"]], "R": list(pl["R"]), "U": pl["U"], "s": pl["s"],
                          "redraws": pl["redraws"]}
        rec["shared_info"] = sh["info"]
    if extra:
        rec.update(extra)
    return rec


def save_system(run_dir, key, nv, eqs):
    path = os.path.join(run_dir, "systems", safe(key) + ".sys.json.gz")
    data = DS.canonical_bytes(nv, eqs)
    with gzip.GzipFile(path, "wb", mtime=0) as g:
        g.write(data)
    return {"path": os.path.relpath(path, run_dir), "content_sha256": hashlib.sha256(data).hexdigest(),
            "content_bytes": len(data)}


def finish_and_evaluate(a, cell, sh, inst, key, arm, wall_cap, ifile, cfile, costfile, results):
    nv = inst["nv"]
    F, B, k = sh["F"], sh["B"], cell["k"]
    raw = inst["raw_eqs"]
    errs = {}
    # IR-3 checks
    if arm != "EQS2":
        errs["IR3_shifts_valid"] = validate_shifts(cell, inst["v"])
    errs["IR3_planted_solves"] = all(DS.eval_poly(e, inst["plant"]["s"]) == 0 for e in raw)
    dchk = DS.descent_check(F, B, inst["v"], k, inst["x_R"], {"nv": nv, "eqs": raw}, inst["plant"]["s"],
                            HashRng(seed_for(a.protocol_sha256, "DESCENT-CHECK", key, a.r), "dc"))
    errs["descent_check"] = dchk
    brute = None
    if nv <= BRUTE_TARGET_MAX:
        bz = enumz.brute_force_Z(nv, raw)
        brute = {"agree": bz == inst["Z"], "brute_size": len(bz)}
    errs["IR2_brute"] = brute
    valid = dchk["ok"] and errs["IR3_planted_solves"] and (brute is None or brute["agree"]) \
        and errs.get("IR3_shifts_valid", True) and inst["plant"]["s"] in inst["Z"]
    eqs_used, st = (CL.adapted_basis(raw) if a.generator_mode == "adapted" else (raw, {"mode": "raw"}))
    sysref = save_system(a.run_dir, key, nv, eqs_used)
    d = dfeq_record(raw, nv, include_fe=True)
    rec = instance_record(key, cell, sh, inst, raw, eqs_used, st,
                          {"checks": errs, "valid": valid, "system_file": sysref, "M6": d,
                           "u_attempts": results.get("u_attempts")})
    append_gz_jsonl(ifile, rec)
    results["instances"].append({"key": key, "valid": valid, "z": len(inst["Z"])})
    if not valid:
        results["invalid"] = "IR-1/IR-2/IR-3 failure: closures not run"
        return
    evaluate_closures(a, cell, key, arm, nv, eqs_used, inst["Z"], base_meta(cell, sh, inst), cfile,
                      costfile, wall_cap, results, want_certs=(arm in ("EQS4", "EQS4-U")),
                      sysref=sysref)


def dfeq_record(raw_eqs, nv, include_fe):
    gens = [dfeq.poly_from_masks(e) for e in raw_eqs]
    t0 = time.time()
    r = dfeq.d_F_eq(gens, nv, include_fe=include_fe, dmax_rank=3)
    per = {str(d): {k_: v for k_, v in x.items()} for d, x in r["per_d"].items()}
    out = {"d_F_eq": r["value"], "bound_by_witness_only": r["bound_by_witness_only"], "per_d": per,
           "witness": r["witness"], "include_fe": include_fe, "wall_s": round(time.time() - t0, 3),
           "label": "measured"}
    return out


def load_avg():
    return os.getloadavg()[0]


def evaluate_closures(a, cell, key, arm, nv, eqs, Z, meta, cfile, costfile, wall_cap, results,
                      want_certs, sysref, z_unknown=False, null_route=False):
    """Walk D = 2.. for one instance; append one record per D and a summary."""
    N = nv
    Dmax = cell["D_max"]
    if arm in CE.NULL_ARMS:
        Dcap = max(4, min(Dmax, 5))
    elif arm == "PC-TRI":
        Dcap = 4
    else:
        Dcap = Dmax
    gb = None
    if Z is not None:
        gbd = enumz.groebner_from_Z(Z, nv)
        gb = {"z": gbd["z"], "d_GB": gbd["d_GB"], "gens": enumz.gb_polys(gbd), "gbd": gbd}
        rank_ev = enumz.rank_ev_by_deg(gbd, Dcap)
        gb["rank_ev"] = rank_ev
    d_solve, reached, censored = None, 1, False
    summary = {"key": key, "kind": "summary", "arm": arm, "cell": cell["id"], "r": a.r, "N": N}
    recs = []
    for D in range(2, Dcap + 1):
        CD = CL.C_le(N, D)
        # SR-3: budget skip from measured timings
        skip = budget_skip(a, CD, D)
        if skip:
            row = {"key": key, "D": D, "status": "not_attempted_budget", "detail": skip}
            append_gz_jsonl(cfile, row)
            summary["stopped"] = row
            break
        task = {"nv": nv, "D": D, "eqs": eqs,
                "gb": ({"z": gb["z"], "d_GB": gb["d_GB"], "gens": gb["gens"], "rank_ev": gb["rank_ev"]}
                       if gb is not None else None),
                "direct_membership": CD <= 30000, "compute_m7": CD <= 30000 and not a.skip_m7,
                "lin_forms": null_route and D == 4,
                }
        la = load_avg()
        st, payload, m9 = run_isolated(closure_task, task, wall_cap, isolate=not a.no_isolate)
        m9.update(load_avg_1min_at_start=la, C=CD, D=D)
        append_jsonl(costfile, {"key": key, "D": D, "status": st, **{k_: v for k_, v in m9.items()}})
        row = {"key": key, "arm": arm, "cell": cell["id"], "r": a.r, "D": D, "N": N, "status": st, "M9": m9}
        if st != "ok":
            row["error"] = payload
            row["M1"] = {"contained": "censored" if st.startswith("censored") else "failed",
                         "note": "a censored measurement is never 'false'"}
            append_gz_jsonl(cfile, row)
            censored = True
            summary["stopped"] = {"D": D, "status": st}
            break
        rec = payload["rec"]
        reached = D
        row.update({"engine": rec, "M2": {"linear_forms": rec["linear_forms"], "one_in_W": rec["const_in_W"]},
                    "M4": rec["series"], "M5": ({"z": gb["z"], "d_GB": gb["d_GB"],
                                                  "rank_ev_D": gb["rank_ev"][D],
                                                  "codim_W_in_B_le_D": CD - rec["final_dim"]}
                                                 if gb else {"z": None}),
                    "M7": payload.get("m7"),
                    "direct_membership": payload.get("direct_membership"),
                    "der3_mismatch": payload.get("der3_mismatch", False)})
        if gb is not None:
            dec = payload["decision"]
            row["M1"] = dec
        elif null_route:
            # decided after the linear-form route (below); provisional marker
            row["M1"] = {"contained": "pending_Z"}
            row["lin_forms"] = payload.get("lin_forms")
        append_gz_jsonl(cfile, row)
        recs.append(row)
        # certificates: a SEPARATE child, started only after the closure record is on disk
        if D == a.cert_degree and gb is not None and (want_certs or a.always_ann):
            dec = row["M1"]
            ck = dict(run_dir=a.run_dir, cfile=cfile, costfile=costfile, key=key, cell_id=cell["id"], D=D,
                      nv=nv, eqs=eqs, Z=Z, gens=gb["gens"], meta=meta, expected_dim=rec["final_dim"],
                      isolate=not a.no_isolate)
            if not dec["contained"] and dec["type"] in ("L", "G"):
                emit_certificate(kind="ann", ann_max_bytes=a.ann_max_bytes, **ck)
            elif dec["contained"] and want_certs:
                pol = wdag_policy(a, N)
                if pol == "now":
                    emit_certificate(kind="wdag", **ck)
                else:
                    append_gz_jsonl(cfile, {"kind": "certificate", "key": key, "cell": cell["id"], "D": D,
                                            "cert_kind": "wdag",
                                            "M8": {"status": "not_attempted_by_rule",
                                                   "rule": "N<=20 all; 21..26 two per cell by nonce "
                                                           "(certify.py selection pass); N>=27 none",
                                                   "policy": pol}})
            elif not dec["contained"]:
                append_gz_jsonl(cfile, {"kind": "certificate", "key": key, "cell": cell["id"], "D": D,
                                        "cert_kind": "none", "M8": {"status": "not_attempted_by_rule",
                                                                    "rule": "Type-D needs no closure certificate"}})
        if gb is not None and row["M1"]["contained"] and d_solve is None:
            d_solve = D
        if null_route and gb is None and D >= 4:
            # affine-subspace Z from the D=4 linear forms (soundness: W_D is inside the ideal)
            lf = payload.get("lin_forms") or []
            zr = enumz.affine_subspace_Z(nv, eqs, lf)
            if zr is None:
                summary["Z_unknown"] = "more than 16 free variables after the linear forms"
                summary["M1_undetermined"] = {"contained": "undetermined_Z_unknown",
                                              "linear_forms": rec["linear_forms"], "final_dim": rec["final_dim"],
                                              "note": "contained would need Z = {s}; not decidable without Z"}
                break
            Z, free = zr
            summary["Z_method"] = f"affine_subspace_from_W4_linear_forms(free={free})"
            gbd = enumz.groebner_from_Z(Z, nv)
            gb = {"z": gbd["z"], "d_GB": gbd["d_GB"], "gens": enumz.gb_polys(gbd), "gbd": gbd,
                  "rank_ev": enumz.rank_ev_by_deg(gbd, Dcap)}
            for rr in recs:
                dd = rr["D"]
                dec = CL.decide(nv, dd, {"final_dim": rr["engine"]["final_dim"]},
                                {"z": gb["z"], "d_GB": gb["d_GB"]}, gb["rank_ev"][dd])
                rr["M1_after_Z"] = dec
                append_gz_jsonl(cfile, {"key": key, "D": dd, "kind": "M1_after_Z", "M1": dec,
                                        "Z_method": summary["Z_method"], "z": gb["z"]})
                if dec["contained"] and d_solve is None:
                    d_solve = dd
        if D >= 4 and (d_solve is not None):
            break
        # null route without Z: stop when linear forms are complete (implies contained)
        if gb is None and D >= 2 and rec["linear_forms"] == N and not rec["const_in_W"]:
            d_solve = D
            summary["note"] = "linear forms complete: Z = {s}, contained (decided without Z)"
            if D >= 4:
                break
    summary.update({"D_reached": reached, "censored": censored,
                    "d_solve": d_solve if d_solve is not None else f"> {reached}",
                    "M3": d_solve if d_solve is not None else f"> {reached}",
                    "M1_at_4": summary.get("M1_undetermined") or next((r_["M1"] for r_ in recs if r_["D"] == 4), None),
                    "z": (gb["z"] if gb else None), "system_file": sysref})
    if summary["M1_at_4"] is None:
        if d_solve is not None and d_solve <= 4:
            summary["M1_at_4"] = {"contained": True, "inferred": "monotone in D from D_solve (DC-1, not measured at D = 4)"}
        elif censored or summary.get("stopped"):
            summary["M1_at_4"] = {"contained": "censored", "note": "a censored M-1 is never false"}
    append_gz_jsonl(cfile, summary)
    results["summary"] = summary


def budget_skip(a, CD, D):
    """SR-3: predicted cost = (largest measured W_4 seconds) * (C4_new/C_meas)^3 vs
    remaining total budget minus the 1200 s reserve. Only checked at D = 4 and
    only when a timings file and a remaining budget are supplied."""
    if a.remaining_seconds is None or not a.timings_file or D != 4:
        return None
    best = None
    if os.path.exists(a.timings_file):
        for line in open(a.timings_file):
            try:
                t = json.loads(line)
            except ValueError:
                continue
            if t.get("D") == 4 and t.get("status") == "ok" and t.get("C"):
                if best is None or t["wall_s"] > best["wall_s"]:
                    best = t
    if best is None:
        return None
    pred = best["wall_s"] * (CD / best["C"]) ** 3
    if pred > a.remaining_seconds - 1200:
        return {"predicted_s": pred, "remaining_s": a.remaining_seconds, "reserve_s": 1200,
                "measured_basis": best}
    return None


def derived_instance(a, cell, sh, src, key, arm, wall_cap, ifile, cfile, costfile, results):
    """NULL-*, PC-TRI, EQS4-AA, EQS4-FULLFE/NOFE built from the EQS4 source instance."""
    nv, M = src["nv"], len(src["raw_eqs"])
    raw_src = src["raw_eqs"]
    rng = HashRng(seed_for(a.protocol_sha256, arm, cell["id"], a.r), "arm")
    Z = None
    zmethod = None
    inst = {"arm": arm, "cell": cell["id"], "r": a.r, "attempt": 0, "nv": nv}
    null_route = False
    if arm == "NULL-PROF":
        raw, s = nulls.null_prof(nv, nulls.profile_of(raw_src), rng)
        inst["planted_s"] = s
    elif arm == "NULL-SHUF":
        if nv > 26:
            results["note"] = "NULL-SHUF runs at N <= 26 only"
            return
        raw, s = nulls.null_shuf(nv, raw_src, rng)
        inst["planted_s"] = s
    elif arm == "PC-TRI":
        pc = positive_control.pc_tri(nv, M, nulls.profile_of(raw_src), rng)
        raw, Z = pc["eqs"], pc["Z"]
        zmethod = "constructed (triangular, unique)"
        inst["pc"] = {k_: pc[k_] for k_ in ("M_eff", "mismatch", "encoding")}
    elif arm == "EQS4-AA":
        enc = reencode.random_encoding(nv, M, rng, density=a.aa_density)
        raw, Z = reencode.apply_encoding(nv, raw_src, enc, src["Z"])
        zmethod = "mapped from the source Z by the affine map"
        inst["aa"] = enc["summary"]
    elif arm in ("EQS4-FULLFE", "EQS4-NOFE"):
        raw = raw_src
        Z = src["Z"]
    if arm in CE.NULL_ARMS:
        if nv <= BRUTE_NULL_MAX:
            Z = enumz.brute_force_Z(nv, raw)
            zmethod = "brute_force_bit_sliced"
            if inst["planted_s"] not in Z:
                results["invalid"] = "IR-3: planted s does not solve the null"
                return
        else:
            null_route = True
            zmethod = "pending_affine_route"
    inst["Z"] = Z
    inst["z_method"] = zmethod
    inst["raw_eqs"] = raw
    if arm in ("EQS4-FULLFE", "EQS4-NOFE"):
        return fullfe_instance(a, cell, sh, inst, src, key, arm, ifile, cfile, costfile, wall_cap, results)
    eqs_used, st = (CL.adapted_basis(raw) if a.generator_mode == "adapted" else (raw, {"mode": "raw"}))
    sysref = save_system(a.run_dir, key, nv, eqs_used)
    extra = {"system_file": sysref, "M6": dfeq_record(raw, nv, include_fe=True), "z_method": zmethod,
             "valid": True}
    for k_ in ("pc", "aa"):
        if k_ in inst:
            extra[k_] = inst[k_]
    rec = instance_record(key, cell, sh, inst, raw, eqs_used, st, extra)
    rec["profile_source_key"] = f"{a.cell}/EQS4/r{a.r}"
    rec["meta"] = base_meta(cell, sh, src)
    append_gz_jsonl(ifile, rec)
    results["instances"].append({"key": key, "z": None if Z is None else len(Z)})
    evaluate_closures(a, cell, key, arm, nv, eqs_used, Z, rec["meta"], cfile, costfile, wall_cap, results,
                      want_certs=(arm == "EQS4-AA" and a.aa_certs), sysref=sysref, null_route=null_route)


def fullfe_task(task):
    nv, D, eqs, with_fe = task["nv"], task["D"], task["eqs"], task["with_fe"]
    t0 = time.time()
    rec = fullring.full_ring_closure(nv, D, eqs, with_fe)
    rec["wall_s"] = round(time.time() - t0, 3)
    brec, _ = CL.w_closure_record(nv, D, task["bool_eqs"])
    comp = {"final_dim": brec["final_dim"], "dims_by_deg": brec["dims_by_deg"],
            "linear_forms": brec["linear_forms"], "one": brec["one"]}
    return {"rec": rec, "boolean_companion": comp}


def fullfe_instance(a, cell, sh, inst, src, key, arm, ifile, cfile, costfile, wall_cap, results):
    nv = inst["nv"]
    if nv > 20:
        results["note"] = "FULLFE/NOFE run at N <= 20 only"
        return
    raw = inst["raw_eqs"]
    with_fe = arm == "EQS4-FULLFE"
    # both arms run on the SAME adapted generators (C-FE-OUT differs in S_fe only)
    eqs_ad, st_ad = CL.adapted_basis(raw)
    rec = instance_record(key, cell, sh, inst, raw, eqs_ad, st_ad,
                          {"system_file": save_system(a.run_dir, key, nv, eqs_ad), "valid": True,
                           "M6": dfeq_record(raw, nv, include_fe=with_fe)})
    rec["meta"] = base_meta(cell, sh, src)
    append_gz_jsonl(ifile, rec)
    out = []
    for D in range(2, min(cell["D_max"], 4) + 1):
        st, payload, m9 = run_isolated(fullfe_task, {"nv": nv, "D": D, "eqs": eqs_ad,
                                                      "with_fe": with_fe, "bool_eqs": eqs_ad}, 1800, isolate=not a.no_isolate)
        row = {"key": key, "arm": arm, "cell": cell["id"], "r": a.r, "D": D, "status": st, "M9": m9}
        if st == "ok":
            row["full_ring"] = payload["rec"]
            brec = payload["boolean_companion"]     # Boolean closure of the same generators (child process)
            row["boolean_companion"] = brec
            row["C_FE_EQ_agree"] = (with_fe and payload["rec"]["multilinear_part_dims_by_deg"] == brec["dims_by_deg"]
                                    and payload["rec"]["rho_rank"] == brec["final_dim"])
        else:
            row["error"] = payload
        append_gz_jsonl(cfile, row)
        append_jsonl(costfile, {"key": key, "D": D, "status": st, **m9})
        out.append({"D": D, "status": st})
    results["instances"].append({"key": key, "runs": out})


def parse(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-dir", required=True)
    p.add_argument("--cell", required=True, choices=sorted(CE.CELLS))
    p.add_argument("--arm", required=True, choices=CE.ARMS)
    p.add_argument("--r", type=int, required=True)
    p.add_argument("--protocol-sha256", required=True)
    p.add_argument("--aa-source", default="EQS4", choices=["EQS4", "EQS4-U"])
    p.add_argument("--aa-density", type=float, default=0.5)
    p.add_argument("--aa-certs", action="store_true", help="also emit certificates for the AA instance")
    p.add_argument("--always-ann", action="store_true", help="also emit ann certificates for non-decisive arms (AA)")
    p.add_argument("--generator-mode", default="adapted", choices=["adapted", "raw"])
    p.add_argument("--cert-degree", type=int, default=4, help="closure degree D at which certificates are emitted")
    p.add_argument("--wdag", default="auto", choices=["auto", "always", "never"])
    p.add_argument("--wall-cap", type=float, default=None, help="override per-instance-per-D wall cap (tests)")
    p.add_argument("--remaining-seconds", type=float, default=None)
    p.add_argument("--timings-file", default=None)
    p.add_argument("--ann-max-bytes", type=int, default=512 << 20)
    p.add_argument("--skip-m7", action="store_true")
    p.add_argument("--require-fixtures", default=None,
                   help="path of fixtures.json; refuse to run unless it exists and has no 'fail' verdict (SR-1)")
    p.add_argument("--no-isolate", action="store_true", help="run closures in-process (tests only)")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse()
    st = run_trial(args)
    print(json.dumps({k: st[k] for k in ("trial", "status", "wall_s") if k in st}))
    if st.get("status") != "completed":
        print(st.get("traceback", ""), file=sys.stderr)
        sys.exit(1)
