#!/usr/bin/env bash
# Frozen analysis for IC-C1-DEFERRED-GUARD-FP28-20261106 (PROTOCOL section 7.3 and section 8).
#
# usage: analyze-c1.sh ECBENCH OUT_DIR FROZEN_SPEC_S1 FROZEN_SPEC_S2 SESSION1 SESSION2
#
# ECBENCH          the ecbench binary extracted from the pinned image; its sha256 is checked
#                  against the pinned value below (exit 2 on a mismatch).
# OUT_DIR          written: reports/s1, reports/s2 (compare, band and replay files, per-phase tables)
#                  and verdict.json.
# FROZEN_SPEC_Sk   spec-c1-s1.json / spec-c1-s2.json as frozen (the session spec must be jq -S -c equal).
# SESSIONk         the `session/` directory of session k. Next to it (dirname) the job's own files
#                  input-spec.json and l2-gate.json are read when present.
#
# Arms are addressed by NAME, never by role. Rho arms are skipped for IC counters.
# No wall field (wall_ns, time.*, `wall` blocks of compare) is read.
#
# Exit status: 0 whenever the analysis ran to the end, whatever the verdict (read verdict.json);
# 2 for a usage error or an ecbench binary that is not the pinned one.
set -euo pipefail

PINNED_ECBENCH_SHA256=73362eed4165d6db20fe1d398baa8fabefa2497aff6e78dab9ed8f31af31dd01

usage() { echo "usage: analyze-c1.sh ECBENCH OUT_DIR FROZEN_SPEC_S1 FROZEN_SPEC_S2 SESSION1 SESSION2" >&2; exit 2; }
[[ $# -eq 6 ]] || usage
ecbench=$1; out=$2; spec1=$3; spec2=$4; s1=$5; s2=$6
[[ -f $ecbench && -x $ecbench ]] || { echo "ecbench is not an executable file: $ecbench" >&2; exit 2; }
[[ $(sha256sum "$ecbench" | cut -d' ' -f1) == "$PINNED_ECBENCH_SHA256" ]] \
  || { echo "ecbench sha256 is not $PINNED_ECBENCH_SHA256" >&2; exit 2; }
for f in "$spec1" "$spec2"; do [[ -f $f ]] || { echo "no such spec: $f" >&2; exit 2; }; done
for s in "$s1" "$s2"; do
  [[ -f $s/records.jsonl && -f $s/session.json ]] || { echo "not a session directory: $s" >&2; exit 2; }
done
mkdir -p "$out"

read -r -d '' PYSRC <<'PYEOF' || true
# ---- BEGIN C1 ANALYSIS PYTHON ----
import json, os, subprocess, sys, hashlib

PIN = "73362eed4165d6db20fe1d398baa8fabefa2497aff6e78dab9ed8f31af31dd01"
# Counts are derived from the frozen spec (set_counts), never hard-coded:
#   workloads = curves x targets_per_curve; RECORDS = workloads x (warmup + rounds) x arms;
#   PAIRS = workloads x rounds (measured pairs per arm-pair comparison);
#   PARITY_PAIRS = workloads x (warmup + rounds) (warm-ups included).
RECORDS = PAIRS = PARITY_PAIRS = None


def set_counts(spec):
    global RECORDS, PAIRS, PARITY_PAIRS
    wl = len(spec["workloads"]["curves"]) * spec["workloads"]["targets_per_curve"]
    rounds, warm = spec["measurement"]["rounds"], spec["measurement"]["warmup"]
    RECORDS = wl * (warm + rounds) * len(spec["arms"])
    PAIRS = wl * rounds
    PARITY_PAIRS = wl * (warm + rounds)
    return RECORDS, PAIRS, PARITY_PAIRS
WEIGHTS = ["0", "0.1", "1"]
RESAMPLES = 4000
IC_ARMS = ["incumbent", "candidate", "walk-eager-n304", "srenew-eager-n407",
           "srenew-deferred-n407", "srenew-eager-n304", "pc-fb2x", "incumbent-aa"]
RHO_ARMS = ["rho-neg", "rho-neg-aa"]
PARITY_COMPARISONS = [("srenew-eager-n407", "srenew-deferred-n407"), ("srenew-eager-n304", "candidate")]
# section 4.2 (descriptive) comparisons, a -> b
FACTORIAL = [("incumbent", "walk-eager-n304"), ("srenew-eager-n407", "srenew-eager-n304"),
             ("srenew-deferred-n407", "candidate"), ("incumbent", "srenew-eager-n407"),
             ("walk-eager-n304", "srenew-eager-n304"), ("srenew-eager-n407", "srenew-deferred-n407"),
             ("srenew-eager-n304", "candidate"), ("incumbent", "candidate")]
EQUIV = (0.995, 1.005)


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------- pure gate logic (testable)
def ops_ok(c):
    o = (c or {}).get("ops") or {}
    return (o.get("status") == "ok" and o.get("same_seeds") is True and o.get("unpaired_runs") == 0
            and o.get("pairs") == PAIRS and o.get("censored_pairs") == 0)


def twin_exact(c):
    o = (c or {}).get("ops") or {}
    return (o.get("status") == "ok" and o.get("same_seeds") is True and o.get("unpaired_runs") == 0
            and o.get("pairs") == PAIRS and o.get("ratio_b_over_a") == 1
            and o.get("ci95") == [1, 1] and o.get("ci95_bootstrap") in ([1, 1], None))


def pc_ok(c):
    o = (c or {}).get("ops") or {}
    return (o.get("status") == "ok" and o.get("same_seeds") is True and o.get("unpaired_runs") == 0
            and o.get("pairs") == PAIRS and o.get("censored_pairs") == 0
            and isinstance(o.get("ratio_b_over_a"), (int, float)) and o["ratio_b_over_a"] > 1
            and isinstance(o.get("ci95"), list) and o["ci95"][0] > 1)


def bounds(c):
    o = c["ops"]
    ub = max(o["ci95"][1], o["ci95_bootstrap"][1])
    lb = min(o["ci95"][0], o["ci95_bootstrap"][0])
    return lb, ub


def relp(r):
    for p in r["phases"]:
        if p["name"] == "relations":
            return p
    raise KeyError("no relations phase")


def parity_pair(a, b):
    """Rules 1-4 of PROTOCOL section 5 on one paired record (a eager, b deferred). Returns list of failures."""
    f = []
    ra, rb = relp(a), relp(b)
    na, nb = ra["native"], rb["native"]
    eq = [("status", a["outcome"]["status"], b["outcome"]["status"]),
          ("recovered", a["outcome"]["recovered"], b["outcome"]["recovered"]),
          ("matches_target", a["outcome"]["matches_target"], b["outcome"]["matches_target"])]
    for k in ("targets_tried", "relations_found", "matrix_rank", "matrix_rows", "matrix_work"):
        eq.append(("counters." + k, a["counters"][k], b["counters"][k]))
    for k in ("trials", "relations", "stride_steps", "stride_renewals", "stride_restarts"):
        eq.append(("relations.native." + k, na.get(k), nb.get(k)))
    wa, wb = ra.get("work_native", {}), rb.get("work_native", {})
    if "target_rng_draws" in wa or "target_rng_draws" in wb:
        eq.append(("target_rng_draws", wa.get("target_rng_draws"), wb.get("target_rng_draws")))
    pa = {p["name"]: p for p in a["phases"]}
    pb = {p["name"]: p for p in b["phases"]}
    if set(pa) != set(pb):
        f.append("phase names differ")
    for n in pa:
        if n == "relations" or n not in pb:
            continue
        for k in ("adds", "doubles", "scalar_mults"):
            eq.append(("phase %s %s" % (n, k), pa[n][k], pb[n][k]))
    for name, x, y in eq:
        if x != y:
            f.append("rule1 %s: %r != %r" % (name, x, y))
    # rule 2
    d = nb["target_guard_probes"] - nb["relations"]
    dg = b["cost"]["total_gae"] - a["cost"]["total_gae"]
    if not (0 <= dg <= d):
        f.append("rule2 dGAE %r outside [0, d=%r]" % (dg, d))
    if rb["adds"] - ra["adds"] != dg:
        f.append("rule2 d relations adds %r != dGAE %r" % (rb["adds"] - ra["adds"], dg))
    if rb["doubles"] - ra["doubles"] != 0 or rb["scalar_mults"] - ra["scalar_mults"] != 0:
        f.append("rule2 doubles/scalar_mults differ")
    # rule 3
    if nb["lookups"] - na["lookups"] != na["repeated_targets_skipped"]:
        f.append("rule3 d lookups %r != eager repeated_targets_skipped %r"
                 % (nb["lookups"] - na["lookups"], na["repeated_targets_skipped"]))
    # rule 4
    if nb["target_guard_probes"] > nb["relations"] + d:
        f.append("rule4 deferred guard probes > relations + d")
    if na["target_guard_probes"] != na["trials"]:
        f.append("rule4 eager guard probes %r != eager trials %r" % (na["target_guard_probes"], na["trials"]))
    return f


def parity_check(records):
    by = {}
    for r in records:
        by[(r["arm"], r["workload"]["workload_id"], r["round"])] = r
    res = {}
    for ea, de in PARITY_COMPARISONS:
        keys = sorted(k for k in by if k[0] == ea)
        fails, nd = [], 0
        for k in keys:
            other = by.get((de,) + k[1:])
            if other is None:
                fails.append({"cell": k[1:], "failures": ["missing deferred record"]})
                continue
            if by[k]["algorithm_seed"] != other["algorithm_seed"]:
                fails.append({"cell": k[1:], "failures": ["algorithm_seed differs"]})
                continue
            ff = parity_pair(by[k], other)
            if other["cost"]["total_gae"] != by[k]["cost"]["total_gae"]:
                nd += 1
            if ff:
                fails.append({"cell": k[1:], "failures": ff})
        res["%s__%s" % (ea, de)] = {"pairs": len(keys), "pairs_expected": PARITY_PAIRS,
                                      "pairs_with_dGAE_nonzero": nd, "failed_pairs": len(fails),
                                      "ok": len(keys) == PARITY_PAIRS and not fails,
                                      "first_failures": fails[:5]}
    return res


def session_verdict(x):
    """x: dict of already-evaluated booleans and comparison JSONs. Returns (verdict, detail)."""
    integrity = x["integrity"]
    controls = {"twin_incumbent_aa": all(twin_exact(c) for c in x["twin_inc"]),
                "twin_rho_neg_aa": all(twin_exact(c) for c in x["twin_rho"]),
                "pc_fb2x": all(pc_ok(c) for c in x["pc"]),
                "primary_comparison_valid": all(ops_ok(c) for c in x["primary"])}
    detail = {"integrity": integrity, "controls": controls}
    if not all(integrity.values()) or not all(controls.values()):
        return "invalid_measurement", detail
    detail["parity"] = {k: v["ok"] for k, v in x["parity"].items()}
    if not all(detail["parity"].values()):
        return "implementation_defect", detail
    lbs, ubs = zip(*[bounds(c) for c in x["primary"]])
    detail["L_w"] = dict(zip(WEIGHTS, lbs))
    detail["U_w"] = dict(zip(WEIGHTS, ubs))
    if all(u < 1 for u in ubs):
        return "pass", detail
    detail["fail_adverse"] = [w for w, lo in zip(WEIGHTS, lbs) if lo > 1]
    return "fail", detail


def guard_verdict(x):
    """C1-guard: equivalence at w=0 (both CIs inside EQUIV), superiority U_w<1 at w=0.1 and 1, both pairs."""
    out = {}
    for name, cs in x["guard"].items():
        if not all(ops_ok(c) for c in cs):
            out[name] = "invalid"
            continue
        c0, c1, c2 = cs
        eq = all(EQUIV[0] <= v <= EQUIV[1] for v in c0["ops"]["ci95"] + c0["ops"]["ci95_bootstrap"])
        sup = all(bounds(c)[1] < 1 for c in (c1, c2))
        out[name] = "pass" if (eq and sup) else "fail"
    return out


def overall(v1, v2, d1, d2, g1, g2):
    vs = [v1, v2]
    if "implementation_defect" in vs:
        o = "implementation_defect"
    elif vs == ["pass", "pass"]:
        o = "supported_within_scope"
    elif vs == ["fail", "fail"]:
        common = set(d1.get("fail_adverse", [])) & set(d2.get("fail_adverse", []))
        o = "refuted_within_scope" if common else "not_supported_within_scope"
    elif sorted(vs) == ["fail", "pass"]:
        o = "inconclusive"
    elif vs == ["invalid_measurement", "invalid_measurement"]:
        o = "invalid_measurement"
    else:  # one valid, one invalid (the permitted rerun is a separate, later invocation)
        valid = [v for v in vs if v != "invalid_measurement"][0]
        o = "single_unreplicated_pass_analyzed" if valid == "pass" else "single_unreplicated_fail_weaken"
    guard = {}
    for k in g1:
        guard[k] = "pass" if (g1[k] == "pass" and g2.get(k) == "pass") else "not_pass"
    return o, guard


# ---------------------------------------------------------------- IO
def run(ecb, args, capture=True):
    p = subprocess.run([ecb] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr


def compare(ecb, session, a, b, w, outfile):
    args = ["compare", "--dir", session, "--a", a, "--b", b, "--resamples", str(RESAMPLES), "--json"]
    if w is not None:
        args += ["--weight", w]
    rc, so, se = run(ecb, args)
    try:
        d = json.loads(so)
    except Exception:
        d = {}
    with open(outfile, "w") as fh:
        json.dump(d, fh, indent=1, sort_keys=True)
    return d


def load_records(session):
    with open(os.path.join(session, "records.jsonl")) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def read_json(p):
    try:
        with open(p) as fh:
            return json.load(fh)
    except Exception:
        return None


def integrity(ecb, session, frozen_spec_path, repdir):
    recs = load_records(session)
    sess = read_json(os.path.join(session, "session.json")) or {}
    rc, _, _ = run(ecb, ["verify", "--dir", session, "--replay-all", "--exit-code", "--out",
                         os.path.join(repdir, "audit.json")])
    audit = read_json(os.path.join(repdir, "audit.json")) or {}
    frozen = read_json(frozen_spec_path)
    spec_in_session = read_json(os.path.join(session, "spec.json"))
    input_spec_path = os.path.join(os.path.dirname(session.rstrip("/")), "input-spec.json")
    input_spec = read_json(input_spec_path) if os.path.exists(input_spec_path) else None
    l2 = read_json(os.path.join(os.path.dirname(session.rstrip("/")), "l2-gate.json"))
    invalid = [r["seq"] for r in recs if r["outcome"]["status"] != "verified" or r["outcome"]["matches_target"] is not True]
    ok = {
        "verify_exit_0": rc == 0,
        "audit_ok": bool(audit.get("ok") and audit.get("regraded") and audit.get("records_bound")
                         and audit.get("records") == audit.get("verified_records")
                         and len(audit.get("replays") or []) > 0
                         and all(r.get("reproduced") is True for r in audit.get("replays") or [])),
        "records_count_matches_spec": len(recs) == RECORDS,
        "planned_eq_written_eq_spec_count": (sess.get("executions_planned") == RECORDS
                                       and sess.get("records_written") == RECORDS and sess.get("status") == "complete"),
        "all_verified_no_invalid_outcomes": not invalid,
        "l2_gate_invalid_outcomes_empty_if_present": (l2 is None) or (l2.get("invalid_outcomes") == []),
        "session_spec_equals_frozen": frozen is not None and spec_in_session is not None and canon(frozen) == canon(spec_in_session),
        "input_spec_equals_frozen_if_present": (input_spec is None) or (frozen is not None and canon(frozen) == canon(input_spec)),
        "build_equals_pin": sess.get("binary_sha256") == PIN and all(r.get("binary_sha256") == PIN for r in recs),
    }
    return ok, recs, invalid


def phase_table(recs):
    """Per arm, per phase means per measured run of adds/doubles/scalar_mults/gae and every native/work_native counter (IC arms only)."""
    out = {}
    for arm in IC_ARMS:
        rs = [r for r in recs if r["arm"] == arm and not r["warmup"]]
        if not rs:
            continue
        acc = {}
        for r in rs:
            for p in r["phases"]:
                a = acc.setdefault(p["name"], {})
                for k in ("adds", "doubles", "scalar_mults", "gae"):
                    a[k] = a.get(k, 0) + p[k]
                for blk in ("native", "work_native"):
                    for k, v in (p.get(blk) or {}).items():
                        a[blk + "." + k] = a.get(blk + "." + k, 0) + v
        out[arm] = {ph: {k: v / len(rs) for k, v in d.items()} for ph, d in acc.items()}
        out[arm]["_measured_runs"] = len(rs)
        out[arm]["_cost_unpriced"] = rs[0]["cost"]["unpriced"]
    for arm in RHO_ARMS:
        rs = [r for r in recs if r["arm"] == arm and not r["warmup"]]
        if rs:
            out[arm] = {"_measured_runs": len(rs), "_cost_unpriced": rs[0]["cost"]["unpriced"],
                        "_mean_total_gae": sum(r["cost"]["total_gae"] for r in rs) / len(rs)}
    return out


def analyse_session(ecb, session, frozen_spec_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    ok, recs, invalid = integrity(ecb, session, frozen_spec_path, outdir)
    cm = lambda a, b, w: compare(ecb, session, a, b, w, os.path.join(outdir, "compare-%s__%s-w%s.json" % (a, b, w)))
    x = {"integrity": ok}
    x["twin_inc"] = [cm("incumbent", "incumbent-aa", w) for w in WEIGHTS]
    x["twin_rho"] = [cm("rho-neg", "rho-neg-aa", w) for w in WEIGHTS]
    x["pc"] = [cm("incumbent", "pc-fb2x", w) for w in WEIGHTS]
    x["primary"] = [cm("incumbent", "candidate", w) for w in WEIGHTS]
    x["guard"] = {"%s__%s" % p: [cm(p[0], p[1], w) for w in WEIGHTS] for p in PARITY_COMPARISONS}
    x["parity"] = parity_check(recs) if ok["records_count_matches_spec"] else {"%s__%s" % p: {"ok": False} for p in PARITY_COMPARISONS}
    v, detail = session_verdict(x)
    g = guard_verdict(x)
    # descriptive: section 4.2 factorial and rho -> each IC arm, three weights each
    desc = {}
    for a, b in FACTORIAL + [("rho-neg", arm) for arm in IC_ARMS if arm != "incumbent-aa"]:
        for w in WEIGHTS:
            c = cm(a, b, w)
            o = c.get("ops") or {}
            desc["%s__%s__w%s" % (a, b, w)] = {k: o.get(k) for k in ("status", "ratio_b_over_a", "ci95", "ci95_bootstrap", "pairs")}
    rc, so, se = run(ecb, ["band", "--dir", session, "--weights", "0,0.1,1", "--ranks", "--json", os.path.join(outdir, "band.json")])
    with open(os.path.join(outdir, "band.txt"), "w") as fh:
        fh.write(so + se)
    # The ecbench adapter (from-ecbench) copies top-level counters but drops phases[].native. These rows
    # carry every phases[].native counter, keyed to the export row (instance_id = workload_id, replicate = round).
    with open(os.path.join(outdir, "native-supplement.jsonl"), "w") as fh:
        for r in recs:
            nat = {}
            for p in r["phases"]:
                for k, cnt in (p.get("native") or {}).items():
                    nat[p["name"] + "." + k] = cnt
            fh.write(json.dumps({"seq": r["seq"], "arm": r["arm"], "instance_id": r["workload"]["workload_id"],
                                 "replicate": r["round"], "warmup": r["warmup"],
                                 "cost_unpriced": r["cost"]["unpriced"], "phases_native": nat}, sort_keys=True) + "\n")
    with open(os.path.join(outdir, "phase-table.json"), "w") as fh:
        json.dump(phase_table(recs), fh, indent=1, sort_keys=True)
    return v, detail, g, desc, x["parity"]


def main():
    ecb, out, spec1, spec2, s1, s2 = sys.argv[1:7]
    f1, f2 = read_json(spec1), read_json(spec2)
    if f1 is None or f2 is None:
        sys.exit(2)
    c1, c2 = set_counts(f1), set_counts(f2)
    if c1 != c2:
        print("the two frozen specs imply different counts: %r %r" % (c1, c2), file=sys.stderr)
        sys.exit(2)
    res = []
    for n, (spec, s) in enumerate([(spec1, s1), (spec2, s2)], 1):
        res.append(analyse_session(ecb, s, spec, os.path.join(out, "reports", "c1", "s%d" % n)))
    (v1, d1, g1, desc1, p1), (v2, d2, g2, desc2, p2) = res
    o, guard = overall(v1, v2, d1, d2, g1, g2)
    t_source = []
    for d in (desc1, desc2):
        c = d.get("incumbent__srenew-eager-n407__w0") or {}
        ci = c.get("ci95") or [None, None]
        bt = c.get("ci95_bootstrap") or [None, None]
        lo = min(ci[0], bt[0]) if None not in (ci[0], bt[0]) else None
        t_source.append(lo is not None and lo > 1)
    route_b = (o in ("not_supported_within_scope", "refuted_within_scope")) and all(
        v == "pass" for v in guard.values()) and bool(guard) and all(t_source)
    verdict = {"schema": "ic.c1.analysis/v1", "protocol_id": "IC-C1-DEFERRED-GUARD-FP28-20261106",
               "ecbench_sha256": PIN, "overall": o, "c1_guard_overall": guard,
               "route_b_trigger_roadmap_only": route_b,
               "sessions": [{"session": 1, "verdict": v1, "detail": d1, "c1_guard": g1, "parity": p1},
                            {"session": 2, "verdict": v2, "detail": d2, "c1_guard": g2, "parity": p2}],
               "note": "no wall field is read; verdict mapping is PROTOCOL section 8"}
    with open(os.path.join(out, "verdict.json"), "w") as fh:
        json.dump(verdict, fh, indent=1, sort_keys=True)
    print(o)


if __name__ == "__main__":
    main()
# ---- END C1 ANALYSIS PYTHON ----
PYEOF

python3 -I -c "$PYSRC" "$ecbench" "$out" "$spec1" "$spec2" "$s1" "$s2"
