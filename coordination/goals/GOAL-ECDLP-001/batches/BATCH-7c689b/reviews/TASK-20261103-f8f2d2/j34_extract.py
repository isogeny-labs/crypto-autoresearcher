#!/usr/bin/env python3
"""J3 (legacy-reproduction control), J4 (independent extraction) and the
proves-too-much controls for RP-BATCH-7c689b (TASK-20261103-f8f2d2).

The validator's own code. It reads raw arm outputs (extracted arms.tar.gz) and
the archived runs, recomputes every metric and conclusion field named by the
specifications, applies CTRL-LEGACY-REPRO as the specification text defines it,
and only afterwards compares with the values recorded in each run's
raw-result.json `comparison` block. compare.py is never imported or executed.

Usage: python3 j34_extract.py <repo_root> <arms_root> <out_json>
"""
from __future__ import annotations

import copy
import json
import math
import os
import random
import statistics
import sys
from collections import Counter

ROOT = ARMS = None
CAP_FIB, CAP_MTIC = 20.0, 60.0


def jl(*p):
    return json.load(open(os.path.join(*p)))


def arm_path(run6, arm, *rest):
    return os.path.join(ARMS, run6, "arms", arm, *rest)


def run_dir(exp, run):
    return os.path.join(ROOT, "experiments", exp, "runs", run)


# ------------------------------------------------------------------ ICINV
def icinv_tuple(m4):
    return (m4.get("s4_support"), m4.get("singular_locus_dim"), m4.get("singular_locus_degree"),
            m4.get("singular_locus_is_unit_ideal"))


def icinv_archived():
    rd = run_dir("EXP-ICINV-e0cd8f", "RUN-ICINV-e0cd8f-m3class")
    recs = {}
    for setname, fn in (("class", "per-curve-invariants.json"), ("control", "control-set-invariants.json")):
        for i, c in enumerate(jl(rd, fn)["curves"]):
            recs[(setname, i, "base")] = {"ab": (c["a"], c["b"]), "m4": c["m4"]}
            recs[(setname, i, "gauge")] = {"ab": (c["gauge"]["a2"], c["gauge"]["b2"]), "m4": c["gauge"]["m4"]}
    return recs


def icinv_arm(arm):
    return {(r["set"], r["index"], r["role"]): {"ab": (r["a"], r["b"]), "m4": r["m4"]}
            for r in jl(arm_path("9cab7b", arm, "m4-records.json"))["records"]}


def icinv_extract(recs):
    out = {"max_wall_seconds": max(v["m4"].get("wall_seconds", 0) for v in recs.values()),
           "n_records": len(recs), "n_error": sum(1 for v in recs.values() if v["m4"].get("returncode") not in (0, None) or v["m4"].get("error"))}
    for s in ("class", "control"):
        base = [v for k, v in recs.items() if k[0] == s]
        out[f"{s}_s4_support_counts"] = dict(sorted(Counter(str(v["m4"]["s4_support"]) for v in base).items()))
        out[f"{s}_singular_locus_dim_degree_counts"] = dict(sorted(Counter(
            f"{v['m4']['singular_locus_dim']}/{v['m4']['singular_locus_degree']}" for v in base).items()))
        out[f"{s}_unit_ideal_count"] = sum(1 for v in base if v["m4"]["singular_locus_is_unit_ideal"])
    pairs = {(k[0], k[1]) for k in recs}
    agree = sum(1 for p in pairs if icinv_tuple(recs[(*p, "base")]["m4"]) == icinv_tuple(recs[(*p, "gauge")]["m4"]))
    out["gauge_m4_pairs"], out["gauge_m4_agree"] = len(pairs), agree
    cls = {icinv_tuple(v["m4"]) for k, v in recs.items() if k[0] == "class"}
    ctl = {icinv_tuple(v["m4"]) for k, v in recs.items() if k[0] == "control"}
    out["class_m4_tuple_distinct"] = len(cls)
    out["class_and_control_m4_tuple_sets_equal"] = cls == ctl
    concl = {"m4_s4_support_values": sorted({v["m4"]["s4_support"] for v in recs.values()}),
             "m4_singular_locus_dim_degree_values": sorted({f"{v['m4']['singular_locus_dim']}/{v['m4']['singular_locus_degree']}" for v in recs.values()}),
             "gauge_m4_all_agree": agree == len(pairs),
             "class_and_control_m4_tuple_sets_equal": cls == ctl}
    return out, concl


def icinv_control(arch, leg):
    keys = set(arch) | set(leg)
    eq = sum(1 for k in keys if k in arch and k in leg and arch[k]["ab"] == leg[k]["ab"]
             and icinv_tuple(arch[k]["m4"]) == icinv_tuple(leg[k]["m4"]))
    return {"records_equal": f"{eq}/{len(keys)}", "pass": eq == len(keys) == 552,
            "compared_fields": ["a", "b", "s4_support", "singular_locus_dim", "singular_locus_degree", "singular_locus_is_unit_ideal"]}


# ------------------------------------------------------------------ FIB measure
def fib_raw(path):
    d = jl(path)
    return d.get("per_curve", d)


def fib_extract(pc):
    out, concl = {}, {}
    for c, v in pc.items():
        ms = v["measurements"]
        unc = [m for m in ms if not m["capped"]]
        out[c] = {"n_measured": len(ms), "n_capped": len(ms) - len(unc),
                  "n_solved": sum(1 for m in unc if m["is_trivial_ideal"] is False),
                  "n_trivial_ideal": sum(1 for m in unc if m["is_trivial_ideal"]),
                  # upper median (sorted[n//2]): the convention of the archived EXP-FIB-001 pipeline, verified by
                  # reproducing the archived RUN-FIB-007/008 predictor ratio 8.618669826845604e-06 exactly
                  "median_cost_seconds": statistics.median_high([m["cost_seconds"] for m in ms]) if ms else None,
                  "median_cost_seconds_mean_of_middle_two": statistics.median([m["cost_seconds"] for m in ms]) if ms else None,
                  "basis_size_counts": dict(sorted(Counter(str(m["groebner_basis_size"]) for m in unc).items())),
                  "basis_max_degree_counts": dict(sorted(Counter(str(m["groebner_basis_max_degree"]) for m in unc).items())),
                  "resource_exhaustion": len(ms) < 100,
                  "resource_exhaustion_recorded": v["resource_exhaustion"] in (True, "True"),
                  "stop_reason": v["stop_reason"],
                  "n_worker_error": sum(1 for m in ms if m.get("worker_error"))}
        concl[c] = {"resource_exhaustion": out[c]["resource_exhaustion_recorded"],
                    "all_measured_capped": bool(ms) and all(m["capped"] for m in ms)}
    return out, concl


def fib_tuple(m):
    return (m["capped"], m["groebner_basis_size"], m["groebner_basis_max_degree"], m["is_trivial_ideal"])


def fib_control(a, l):
    res = {}
    for c in a:
        am = {m["target_index"]: m for m in a[c]["measurements"]}
        lm = {m["target_index"]: m for m in l[c]["measurements"]}
        common = sorted(set(am) & set(lm))
        # "every target both measured": compare the deterministic tuple only where neither is capped,
        # and the capped flag itself on every common target.
        tuple_eq = all(fib_tuple(am[i]) == fib_tuple(lm[i]) for i in common)
        allcap = (all(m["capped"] for m in am.values()), all(m["capped"] for m in lm.values()))
        r = {"n_common": len(common), "per_target_equal_on_common": tuple_eq,
             "resource_exhaustion_equal": (len(am) < 100) == (len(lm) < 100),
             "all_capped_pattern_equal": allcap[0] == allcap[1],
             "n_measured_diff": len(lm) - len(am),
             "n_uncapped_common": sum(1 for i in common if not am[i]["capped"] and not lm[i]["capped"])}
        r["pass"] = tuple_eq and r["resource_exhaustion_equal"] and r["all_capped_pattern_equal"] and abs(r["n_measured_diff"]) <= 2
        res[c] = r
    return {"checks": res, "pass": all(v["pass"] for v in res.values()),
            "compared_fields": ["capped", "groebner_basis_size", "groebner_basis_max_degree", "is_trivial_ideal", "resource_exhaustion", "all-capped", "n_measured"]}


# ------------------------------------------------------------------ FIB decision
def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def fib_decision_extract(r4, r5):
    """Recompute the fib-decision fields from FIB-004/005 measurements, archived n_R (RUN-FIB-002/003)
    and archived amortized predictor seconds (RUN-FIB-007); statement from the EXP-FIB-001 spec:
    correlation gate |rho_s| >= 0.4 with permutation p < 0.01 on curves with >= 100 measured targets;
    cost gate ratio <= 0.1 on >= 3 curves; gate = correlation AND cost; RUN-FIB-008 runs only if gate."""
    nr = {}
    for run in ("RUN-FIB-002", "RUN-FIB-003"):
        for c, v in fib_raw(os.path.join(run_dir("EXP-FIB-001", run), "raw.json")).items():
            if "n_R_per_target" in v:  # 16-bit exact tables; 20-bit curves carry sampled estimates only
                x = v["n_R_per_target"]
                nr[c] = json.loads(x) if isinstance(x, str) else x
    pred = jl(run_dir("EXP-FIB-001", "RUN-FIB-007"), "summary.json")
    meas = {**r4, **r5}
    status, corr, ratios = {}, {}, {}
    rng = random.Random(12345)
    for c in sorted(meas):
        ms = meas[c]["measurements"]
        status[c] = "measured" if len(ms) >= 100 else "resource_exhaustion"
        if status[c] == "measured":
            cost = [m["cost_seconds"] for m in sorted(ms, key=lambda m: m["target_index"])]
            n_r = [nr[c][m["target_index"]] for m in sorted(ms, key=lambda m: m["target_index"])]
            rho = spearman(n_r, cost)
            perm = [spearman(n_r, rng.sample(cost, len(cost))) for _ in range(2000)]
            p = (1 + sum(1 for q in perm if abs(q) >= abs(rho))) / (1 + len(perm))
            corr[c] = {"rho_s": rho, "p_perm_validator_2000": p, "passes": abs(rho) >= 0.4 and p < 0.01}
        ratios[c] = pred[c]["amortized_predictor_seconds_per_target"] / statistics.median_high([m["cost_seconds"] for m in ms])
    passing = sorted(c for c, v in corr.items() if v["passes"])
    cost_curves = sorted(c for c, r in ratios.items() if r <= 0.1)
    out = {"per_curve_status": status, "per_curve_correlation_validator": corr,
           "correlation_gate_curves_passing": passing, "correlation_gate_pass_overall": len(passing) > 0,
           "predictor_cost_ratios": ratios, "cost_gate_curves": cost_curves,
           "predictor_cost_gate_pass": len(cost_curves) >= 3}
    out["gate_pass"] = out["correlation_gate_pass_overall"] and out["predictor_cost_gate_pass"]
    out["run_fib_008_outcome"] = "cancelled_by_gate" if not out["gate_pass"] else "would_run"
    concl = {k: out[k] for k in ("correlation_gate_pass_overall", "correlation_gate_curves_passing", "per_curve_status",
                                 "predictor_cost_gate_pass", "gate_pass", "run_fib_008_outcome")}
    return out, concl


# ------------------------------------------------------------------ MTIC 007/008
def mtic_extract(raw):
    out, concl = {}, {}
    for size, pts in raw["raw"]["per_target"].items():
        inst = raw["metrics"]["instances"][size]
        unc = [t for t in pts if not t["capped"]]
        med = statistics.median([t["charged_seconds"] for t in pts]) if pts else None
        out[size] = {"n_targets": inst["n_targets"], "n_attempted": len(pts), "n_capped": len(pts) - len(unc),
                     "n_uncapped": len(unc), "n_trivial_ideal": sum(1 for t in pts if t.get("trivial_ideal") is True),
                     "n_aux_decomposition_found": sum(1 for t in pts if t.get("aux_decomposition_found")),
                     "n_cancelled_by_budget": inst["n_targets"] - len(pts),
                     "n_cancelled_by_budget_recorded": inst["n_cancelled_by_budget"],
                     "t_desc_median_seconds": med,
                     "t_desc_uncapped_median_seconds": statistics.median([t["charged_seconds"] for t in unc]) if unc else None,
                     "ideal_enumeration_disagreements": inst["ideal_enumeration_disagreements"]}
        concl[size] = {"all_attempted_capped": bool(pts) and not unc, "t_desc_median_at_cap": med is not None and med >= CAP_MTIC}
    return out, concl


def mtic_tuple(t):
    return (t["capped"], t["basis_size"], t["basis_max_degree"], t.get("trivial_ideal"))


def mtic_control(a, l):
    res = {}
    for size in a["raw"]["per_target"]:
        am = {t["index"]: t for t in a["raw"]["per_target"][size]}
        lm = {t["index"]: t for t in l["raw"]["per_target"][size]}
        common = sorted(set(am) & set(lm))
        r = {"n_common": len(common),
             "per_target_equal_on_common": all(mtic_tuple(am[i]) == mtic_tuple(lm[i]) for i in common),
             "uncapped_equal": sum(1 for t in am.values() if not t["capped"]) == sum(1 for t in lm.values() if not t["capped"]),
             "n_attempted_diff": len(lm) - len(am),
             "n_common_uncapped_both": sum(1 for i in common if not am[i]["capped"] and not lm[i]["capped"])}
        r["pass"] = r["per_target_equal_on_common"] and r["uncapped_equal"] and abs(r["n_attempted_diff"]) <= 2
        res[size] = r
    return {"checks": res, "pass": all(v["pass"] for v in res.values()),
            "compared_fields": ["capped", "basis_size", "basis_max_degree", "trivial_ideal", "uncapped count", "n_attempted"]}


# ------------------------------------------------------------------ MTIC 010b
def kstar(acc):
    """K* and regime from the accounting's recorded inputs (S, T_desc, T_verify, sqrt_n)."""
    den = acc["sqrt_n"] - acc["T_desc"] - acc["T_verify"]
    k = "infinite" if den <= 0 else math.ceil(acc["S"] / den)
    regime = "(i) K* infinite" if acc["T_desc"] >= acc["sqrt_n"] else ("(ii) K* finite" if k != "infinite" else "?")
    return k, regime


def mtic010b_extract(raw, t007, t008):
    """Decision matrix: T_desc recomputed from the arm's RUN-MTIC-007/008 per-target rows, converted with the
    recorded calibration rates; K* and regime recomputed. Ablation: the arm's raw keeps only run_mtic's own
    per-base summary (no per-target rows); K* and regime recomputed from it."""
    out = {"decision_matrix": {}, "ablation": {}}
    concl = {}
    per_target = {}
    for src in (t007, t008):
        per_target.update(src["raw"]["per_target"])
    for size, dm in raw["metrics"]["decision_matrix"].items():
        pts = per_target[size]
        med = statistics.median([t["charged_seconds"] for t in pts])
        accs = dm["accountings"]
        rates = accs["calibration_rates"]
        ks, reg, inputs_ok = {}, {}, {}
        for name in ("group_ops_rho", "group_ops_bsgs", "wall_seconds"):
            a = accs[name]
            rate = {"group_ops_rho": rates["rho_walk_rate"], "group_ops_bsgs": rates["bsgs_construction_rate"], "wall_seconds": 1.0}[name]
            t_desc = med * rate
            sqrt_n = math.sqrt(dm["N"]) / (rates["rho_walk_rate"] if name == "wall_seconds" else 1.0)
            inputs_ok[name] = math.isclose(t_desc, a["T_desc"], rel_tol=1e-9) and math.isclose(sqrt_n, a["sqrt_n"], rel_tol=1e-9)
            ks[name], reg[name] = kstar({"S": a["S"], "T_desc": t_desc, "T_verify": a["T_verify"], "sqrt_n": sqrt_n})
        n_unc = sum(1 for t in pts if not t["capped"])
        out["decision_matrix"][size] = {"t_desc_seconds_median": med, "t_desc_n_attempted": len(pts),
                                        "t_desc_n_capped": sum(1 for t in pts if t["capped"]),
                                        "n_uncensored_solves": n_unc, "K_star_per_accounting": ks,
                                        "regime_per_accounting": reg, "recorded_T_desc_and_sqrt_n_match_recomputed": inputs_ok,
                                        "below_frontier_observed_any_accounting": any(accs[n]["below_frontier"] for n in ks)}
        concl[f"K_star.{size}"] = ks
        concl[f"regime.{size}"] = reg
    for name, ab in raw["metrics"]["ablation"].items():
        full = raw["raw"]["ablation_full"][name]["accountings"]
        ks = {}
        for acc in ("group_ops_rho", "group_ops_bsgs", "wall_seconds"):
            ks[acc] = kstar(full[acc])[0]
        out["ablation"][name] = {"B": ab["B"], "t_desc_median_seconds": ab["t_desc_median_seconds"],
                                 "t_desc_n_attempted": ab["t_desc_n_attempted"], "t_desc_n_capped": ab["t_desc_n_capped"],
                                 "K_star_per_accounting": ks, "granularity": "run_mtic per-base summary (no per-target rows recorded)"}
        concl[f"ablation_K_star.{name}"] = ks
    return out, concl


def mtic010b_control(a, l):
    res = {}
    for size in a["decision_matrix"]:
        A, L = a["decision_matrix"][size], l["decision_matrix"][size]
        r = {"regime_equal": A["regime_per_accounting"] == L["regime_per_accounting"],
             "K_star_equal": A["K_star_per_accounting"] == L["K_star_per_accounting"],
             "n_uncensored_equal": A["n_uncensored_solves"] == L["n_uncensored_solves"]}
        r["pass"] = all(r.values())
        res[f"decision_matrix.{size}"] = r
    for name in a["ablation"]:
        A, L = a["ablation"][name], l["ablation"][name]
        r = {"K_star_equal": A["K_star_per_accounting"] == L["K_star_per_accounting"],
             "n_capped_eq_attempted_pattern": (A["t_desc_n_capped"] == A["t_desc_n_attempted"]) == (L["t_desc_n_capped"] == L["t_desc_n_attempted"]),
             "n_attempted_diff": L["t_desc_n_attempted"] - A["t_desc_n_attempted"]}
        r["pass"] = r["K_star_equal"] and r["n_capped_eq_attempted_pattern"] and abs(r["n_attempted_diff"]) <= 2
        res[f"ablation.{name}"] = r
    return {"checks": res, "pass": all(v["pass"] for v in res.values()),
            "compared_fields": ["regime per accounting", "K* per accounting", "uncensored counts", "ablation K*", "ablation capped pattern", "ablation n_attempted"]}


# ------------------------------------------------------------------ recorded-value comparison
def diff(mine, rec, path=""):
    """List leaf mismatches between my value and the recorded value (floats to 1e-12 relative)."""
    out = []
    if isinstance(mine, dict) and isinstance(rec, dict):
        for k in rec:
            if k not in mine:
                out.append([f"{path}.{k}", "recorded-only (not recomputed)", rec[k]])
                continue
            out += diff(mine[k], rec[k], f"{path}.{k}")
        return out
    if isinstance(mine, float) and isinstance(rec, (int, float)) and not isinstance(rec, bool):
        if not math.isclose(mine, rec, rel_tol=1e-12, abs_tol=1e-15):
            out.append([path, mine, rec])
        return out
    if isinstance(mine, tuple):
        mine = list(mine)
    if mine != rec:
        out.append([path, mine, rec])
    return out


def changed(c_a, c_b):
    return {k: c_a[k] != c_b[k] for k in c_a}


def main():
    global ROOT, ARMS
    ROOT, ARMS, out_path = sys.argv[1:4]
    R = {}

    def record(run6, exp, cell, arch, leg, rep, ctrl, ca, cl, cr, extra=None):
        rec = jl(run_dir(exp, f"RUN-SEMAEV-{run6}"), "raw-result.json")["comparison"]
        mine = {"archived": arch, "legacy": leg, "repaired": rep}
        diffs = {k: diff(mine[k], rec[k]) for k in mine}
        my_concl = {"archived": ca, "legacy": cl, "repaired": cr}
        concl_diffs = {k: diff(my_concl[k], rec["conclusion_fields"][k]) for k in my_concl}
        ch_ra, ch_rl = changed(cr, ca), changed(cr, cl)
        R[run6] = {"cell": cell, "mine": mine, "my_conclusion_fields": my_concl,
                   "my_changed_repaired_vs_archived": ch_ra, "my_changed_repaired_vs_legacy": ch_rl,
                   "my_ctrl_legacy_repro": ctrl,
                   "diff_vs_recorded": diffs, "conclusion_diff_vs_recorded": concl_diffs,
                   "changed_diff_vs_recorded": {"r_vs_a": diff(ch_ra, rec["conclusion_changed_repaired_vs_archived"]),
                                                "r_vs_l": diff(ch_rl, rec["conclusion_changed_repaired_vs_legacy"])},
                   "ctrl_pass_recorded": rec["ctrl_legacy_repro"]["pass"], "ctrl_pass_mine": ctrl["pass"],
                   "conclusion_fields_compared_in_ctrl": None}
        if extra:
            R[run6].update(extra)
        nd = sum(len(v) for v in diffs.values()) + sum(len(v) for v in concl_diffs.values())
        print(f"{run6} {cell}: ctrl mine={ctrl['pass']} recorded={rec['ctrl_legacy_repro']['pass']}; "
              f"leaf diffs vs recorded={nd}; changed r-vs-a={ch_ra}; r-vs-l={ch_rl}")
        for k, v in list(diffs.items()) + [("concl." + k, v) for k, v in concl_diffs.items()]:
            for d in v[:6]:
                print("    ", k, d)

    # ICINV
    A, L, P = icinv_archived(), icinv_arm("legacy"), icinv_arm("repaired")
    (ea, ca), (el, cl), (er, cr) = icinv_extract(A), icinv_extract(L), icinv_extract(P)
    diff_arms = sum(1 for k in L if icinv_tuple(L[k]["m4"]) != icinv_tuple(P[k]["m4"]))
    record("9cab7b", "EXP-SEMAEV-93d5cc", "icinv-m4", ea, el, er, icinv_control(A, L), ca, cl, cr,
           {"records_differing_repaired_vs_legacy": diff_arms})

    # FIB-004 / FIB-005
    for run6, rid in (("3e69b6", "RUN-FIB-004"), ("4be606", "RUN-FIB-005")):
        a = fib_raw(os.path.join(run_dir("EXP-FIB-001", rid), "raw.json"))
        l = fib_raw(arm_path(run6, "legacy", "runs", rid, "raw.json"))
        r = fib_raw(arm_path(run6, "repaired", "runs", rid, "raw.json"))
        (ea, ca), (el, cl), (er, cr) = fib_extract(a), fib_extract(l), fib_extract(r)
        record(run6, "EXP-SEMAEV-93d5cc", "fib-004" if rid.endswith("4") else "fib-005", ea, el, er, fib_control(a, l), ca, cl, cr)

    # fib-decision
    arch4 = fib_raw(os.path.join(run_dir("EXP-FIB-001", "RUN-FIB-004"), "raw.json"))
    arch5 = fib_raw(os.path.join(run_dir("EXP-FIB-001", "RUN-FIB-005"), "raw.json"))
    res = {}
    for arm in ("legacy", "repaired"):
        res[arm] = fib_decision_extract(fib_raw(arm_path("3e69b6", arm, "runs", "RUN-FIB-004", "raw.json")),
                                        fib_raw(arm_path("4be606", arm, "runs", "RUN-FIB-005", "raw.json")))
    res["archived"] = fib_decision_extract(arch4, arch5)
    # archived recorded decision for comparison of the gate chain (RUN-FIB-006C/008 summaries)
    s6 = jl(run_dir("EXP-FIB-001", "RUN-FIB-006C"), "summary.json")
    s8 = jl(run_dir("EXP-FIB-001", "RUN-FIB-008"), "summary.json")
    ctrl = {"checks": {k: res["archived"][1][k] == res["legacy"][1][k] for k in
                       ("correlation_gate_pass_overall", "correlation_gate_curves_passing", "per_curve_status")}}
    ctrl["pass"] = all(ctrl["checks"].values())
    ctrl["compared_fields"] = list(ctrl["checks"])
    record("894e27", "EXP-SEMAEV-93d5cc", "fib-decision", res["archived"][0], res["legacy"][0], res["repaired"][0], ctrl,
           res["archived"][1], res["legacy"][1], res["repaired"][1],
           {"archived_summaries_agree_with_my_archived_recompute": {
               "006C_per_curve_status": s6["per_curve_status"] == res["archived"][0]["per_curve_status"],
               "006C_correlation_gate_pass_overall": s6["correlation_gate_pass_overall"] == res["archived"][0]["correlation_gate_pass_overall"],
               "008_gate_pass": s8["gate_pass"] == res["archived"][0]["gate_pass"]}})

    # MTIC-007 / 008
    for run6, rid in (("2a8498", "RUN-MTIC-007"), ("fcd67c", "RUN-MTIC-008")):
        a = jl(run_dir("EXP-MTIC-001", rid), "raw.json")
        l = jl(arm_path(run6, "legacy", "out-root", "runs", rid, "raw.json"))
        r = jl(arm_path(run6, "repaired", "out-root", "runs", rid, "raw.json"))
        (ea, ca), (el, cl), (er, cr) = mtic_extract(a), mtic_extract(l), mtic_extract(r)
        record(run6, "EXP-SEMAEV-93d5cc", "mtic-007" if rid.endswith("7") else "mtic-008", ea, el, er, mtic_control(a, l), ca, cl, cr)

    # MTIC-010b (successor): arms read RUN-MTIC-007/008 from the parent arms (copies inside this run's archive)
    a = jl(run_dir("EXP-MTIC-001", "RUN-MTIC-010b"), "raw.json")
    t7a, t8a = jl(run_dir("EXP-MTIC-001", "RUN-MTIC-007"), "raw.json"), jl(run_dir("EXP-MTIC-001", "RUN-MTIC-008"), "raw.json")
    ea, ca = mtic010b_extract(a, t7a, t8a)
    arm_out = {}
    for arm in ("legacy", "repaired"):
        raw = jl(arm_path("0e5876", arm, "out-root", "runs", "RUN-MTIC-010b", "raw.json"))
        t7 = jl(arm_path("0e5876", arm, "out-root", "runs", "RUN-MTIC-007", "raw.json"))
        t8 = jl(arm_path("0e5876", arm, "out-root", "runs", "RUN-MTIC-008", "raw.json"))
        arm_out[arm] = mtic010b_extract(raw, t7, t8)
    record("0e5876", "EXP-SEMAEV-6e9dcf", "mtic-010b", ea, arm_out["legacy"][0], arm_out["repaired"][0],
           mtic010b_control(ea, arm_out["legacy"][0]), ca, arm_out["legacy"][1], arm_out["repaired"][1])

    # ------------------------------------------------------------ proves-too-much controls
    ptm = {}
    # PTM-1: repaired arm vs archive in ICINV -- polynomials differ by construction; comparator must break.
    c1 = icinv_control(A, P)
    ptm["PTM-1_icinv_repaired_vs_archive"] = {"comparator_pass": c1["pass"], "records_equal": c1["records_equal"],
                                             "required": "breaks", "ok": c1["pass"] is False}
    # PTM-2: one deterministic field perturbed in a copy of a legacy output; comparator must break that field.
    Lp = copy.deepcopy(L)
    k0 = sorted(Lp)[0]
    Lp[k0]["m4"]["singular_locus_degree"] += 1
    c2a = icinv_control(A, Lp)
    l4 = fib_raw(arm_path("3e69b6", "legacy", "runs", "RUN-FIB-004", "raw.json"))
    l4p = copy.deepcopy(l4)
    l4p["C16-1"]["measurements"][0]["groebner_basis_size"] += 1
    c2b = fib_control(fib_raw(os.path.join(run_dir("EXP-FIB-001", "RUN-FIB-004"), "raw.json")), l4p)
    lm7 = jl(arm_path("2a8498", "legacy", "out-root", "runs", "RUN-MTIC-007", "raw.json"))
    lm7p = copy.deepcopy(lm7)
    lm7p["raw"]["per_target"]["16"][0]["capped"] = False
    c2c = mtic_control(jl(run_dir("EXP-MTIC-001", "RUN-MTIC-007"), "raw.json"), lm7p)
    e010 = copy.deepcopy(arm_out["legacy"][0])
    e010["decision_matrix"]["20"]["K_star_per_accounting"]["group_ops_rho"] = 7
    c2d = mtic010b_control(ea, e010)
    ptm["PTM-2_perturbed_legacy_copy"] = {
        "icinv_singular_locus_degree+1": {"comparator_pass": c2a["pass"], "ok": c2a["pass"] is False},
        "fib004_C16-1_target0_basis_size+1": {"comparator_pass": c2b["pass"], "ok": c2b["pass"] is False},
        "mtic007_target0_capped_flipped": {"comparator_pass": c2c["pass"], "ok": c2c["pass"] is False},
        "mtic010b_Kstar20_rho_set_finite": {"comparator_pass": c2d["pass"], "ok": c2d["pass"] is False}}
    # PTM-3: both arms in all-capped units: comparator reports equality, which must not be read as polynomial agreement.
    cap_units = {}
    for run6, info in R.items():
        if info["cell"] in ("mtic-007", "mtic-008"):
            rid = "RUN-MTIC-007" if info["cell"] == "mtic-007" else "RUN-MTIC-008"
            l = jl(arm_path(run6, "legacy", "out-root", "runs", rid, "raw.json"))
            r = jl(arm_path(run6, "repaired", "out-root", "runs", rid, "raw.json"))
            c = mtic_control(l, r)
            for size, chk in c["checks"].items():
                cap_units[f"{info['cell']}.{size}"] = {"legacy_vs_repaired_comparator_pass": chk["pass"],
                                                       "n_common_uncapped_both": chk["n_common_uncapped_both"]}
        if info["cell"] in ("fib-004", "fib-005"):
            rid = "RUN-FIB-004" if info["cell"] == "fib-004" else "RUN-FIB-005"
            l = fib_raw(arm_path(run6, "legacy", "runs", rid, "raw.json"))
            r = fib_raw(arm_path(run6, "repaired", "runs", rid, "raw.json"))
            c = fib_control(l, r)
            for curve, chk in c["checks"].items():
                cap_units[f"{info['cell']}.{curve}"] = {"legacy_vs_repaired_comparator_pass": chk["pass"],
                                                        "n_common_uncapped_both": chk["n_uncapped_common"]}
    ptm["PTM-3_all_capped_units"] = {
        "units": cap_units,
        "reading": "units with n_common_uncapped_both == 0 compare only capped flags and counts; equality there is "
                   "censored and is not evidence that the legacy and repaired polynomials agree (J5 shows they differ "
                   "on every curve: 227 vs 439 terms generically)."}
    R["_ptm"] = ptm
    print(json.dumps(ptm, indent=1))
    json.dump(R, open(out_path, "w"), indent=1, sort_keys=True, default=str)


if __name__ == "__main__":
    main()
