#!/usr/bin/env python3
"""Aggregate trial records of a run directory into controls.json (controls first)
and summary.json. Observations only: no hypothesis verdict is computed here
(the Reviewer and Coordinator judge). Validity gates (SR-4, SR-5) are reported
as flags.

    python3 analyze.py --run-dir <DIR> [--out-dir <DIR>]
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
from collections import defaultdict


def read_gz_jsonl(path):
    if not os.path.exists(path):
        return []
    raw = gzip.open(path, "rb").read().decode()
    return [json.loads(l) for l in raw.splitlines() if l.strip()]


def load(run_dir):
    inst = {}
    for d in read_gz_jsonl(os.path.join(run_dir, "instances.jsonl.gz")):
        inst[d["key"]] = d
    clos = defaultdict(list)
    summ = {}
    for d in read_gz_jsonl(os.path.join(run_dir, "closures.jsonl.gz")):
        if d.get("kind") == "certificate":
            continue
        if d.get("kind") == "summary":
            summ[d["key"]] = d
        elif d.get("kind") == "M1_after_Z":
            clos[d["key"]].append(d)
        else:
            clos[d["key"]].append(d)
    return inst, clos, summ


def by_D(rows):
    return {r["D"]: r for r in rows if "D" in r and r.get("status") == "ok"}


def m1(rows, D):
    r = by_D(rows).get(D)
    if not r:
        return None
    m = r.get("M1")
    if isinstance(m, dict) and m.get("contained") in (True, False):
        return m
    # null route: decision after Z
    for x in rows:
        if x.get("kind") == "M1_after_Z" and x.get("D") == D:
            return x["M1"]
    return None


def split_key(key):
    cell, arm, r = key.split("/")
    return cell, arm.split("-U")[0] if False else arm, r


def metrics_signature(rows, D):
    r = by_D(rows).get(D)
    if not r:
        return None
    # M-4 compared on its exact content only (rank and lead-degree profile per iteration;
    # wall time and the stack row counts are not metrics)
    m4 = [(x["rank"], x["dims_by_deg"]) for x in r["M4"]]
    m7 = r.get("M7")
    m7 = None if m7 is None else {k_: m7.get(k_) for k_ in ("rank", "one", "dims_by_deg", "gb_in_M")}
    m5 = dict(r.get("M5") or {})
    return {"M1": m1(rows, D), "M2": r["M2"], "M4": m4, "M5": m5, "M7": m7,
            "final_dim": r["engine"]["final_dim"]}


M8_VOCAB = ("accepted", "rejected", "not_emitted", "not_attempted_by_rule", "pending_checker")
DECISIVE = ("EQS4", "EQS4-U")
CARRYING_CELLS = ("m3n09", "m3n10", "m3n11", "m3n12", "m3n13", "m3n14", "m4n08", "m4n09")


def cert_records(run_dir, verdicts=None):
    """Latest certificate record per (key, cert_kind), with the M-8 status mapped through the
    independent checker's verdicts {cert_sha256: accept|reject} when supplied."""
    latest = {}
    for d in read_gz_jsonl(os.path.join(run_dir, "closures.jsonl.gz")):
        if d.get("kind") != "certificate":
            continue
        m8 = dict(d["M8"])
        if verdicts and m8.get("cert_sha256") in verdicts and m8.get("status") in ("pending_checker", "accepted", "rejected"):
            m8["status"] = "accepted" if verdicts[m8["cert_sha256"]] in ("accept", "accepted", True) else "rejected"
        assert m8["status"] in M8_VOCAB, m8["status"]
        latest[(d["key"], d["cert_kind"])] = {**d, "M8": m8}
    return latest


def analyze(run_dir, verdicts=None):
    inst, clos, summ = load(run_dir)
    certrec = cert_records(run_dir, verdicts)
    controls, flags = {}, {}
    # C-PC / SR-4
    pc = []
    for key, s in summ.items():
        if s["arm"] != "PC-TRI":
            continue
        ok = (isinstance(s["M3"], int) and s["M3"] <= 3 and (s["M1_at_4"] or {}).get("contained") is True)
        pc.append({"key": key, "M3": s["M3"], "M1_at_4": s["M1_at_4"], "ok": ok})
    controls["C-PC"] = {"rows": pc, "all_ok": all(p["ok"] for p in pc) if pc else None}
    flags["SR-4_pc_violation"] = any(not p["ok"] for p in pc)
    # C-AA-ENC / SR-5
    aa = []
    for key, s in summ.items():
        if s["arm"] != "EQS4-AA":
            continue
        cell, _, r = key.split("/")
        src_arm = "EQS4-U" if r.endswith("-U") else "EQS4"
        rr = r[:-2] if r.endswith("-U") else r
        skey = f"{cell}/{src_arm}/{rr}"
        if skey not in clos:
            skey = f"{cell}/EQS4/{rr}"
        diffs = []
        for D in sorted(set(by_D(clos[key])) | set(by_D(clos.get(skey, [])))):
            a_, b_ = metrics_signature(clos[key], D), metrics_signature(clos.get(skey, []), D)
            if a_ != b_:
                diffs.append({"D": D, "aa": a_ and {k: a_[k] for k in ("M1", "M2", "M5", "M7", "final_dim")},
                              "src": b_ and {k: b_[k] for k in ("M1", "M2", "M5", "M7", "final_dim")}})
        sm = summ.get(skey)
        aa.append({"key": key, "source": skey, "source_present": skey in clos,
                   "M3_aa": s["M3"], "M3_src": sm and sm["M3"], "discrepancies": diffs,
                   "identical": skey in clos and not diffs and (sm and sm["M3"]) == s["M3"]})
    controls["C-AA-ENC"] = {"rows": aa, "zero_discrepancies": all(x["identical"] for x in aa) if aa else None}
    flags["SR-5_aa_discrepancy"] = any((not x["identical"]) and x["source_present"] for x in aa)
    # C-FE-EQ / C-FE-OUT
    fe_eq, fe_out = [], defaultdict(dict)
    for key, rows in clos.items():
        for r_ in rows:
            if r_.get("arm") == "EQS4-FULLFE" and r_.get("status") == "ok":
                fe_eq.append({"key": key, "D": r_["D"], "agree": r_["C_FE_EQ_agree"]})
                fe_out[key.split("/")[0] + "/" + key.split("/")[2]][("FULLFE", r_["D"])] = (
                    r_["full_ring"]["linear_forms"], r_["full_ring"]["one_in_W"])
            if r_.get("arm") == "EQS4-NOFE" and r_.get("status") == "ok":
                fe_out[key.split("/")[0] + "/" + key.split("/")[2]][("NOFE", r_["D"])] = (
                    r_["full_ring"]["linear_forms"], r_["full_ring"]["one_in_W"])
    controls["C-FE-EQ"] = {"rows": fe_eq, "all_agree": all(x["agree"] for x in fe_eq) if fe_eq else None,
                           "label": "structurally forced (DER-1); a disagreement invalidates (SR-5)"}
    controls["C-FE-OUT"] = {"rows": {k: {f"{a}@D{d}": v for (a, d), v in vv.items()} for k, vv in fe_out.items()},
                            "note": "descriptive; decides nothing"}
    flags["SR-5_fe_eq_disagreement"] = bool(fe_eq) and not all(x["agree"] for x in fe_eq)
    # per-instance table
    table = []
    for key, s in summ.items():
        cell, arm, r = key.split("/")
        i = inst.get(key, {})
        table.append({"key": key, "cell": cell, "arm": arm, "r": r, "N": s["N"], "z": s.get("z"),
                      "D_solve": s["M3"], "D_reached": s["D_reached"], "censored": s["censored"],
                      "M1_at_4": s.get("M1_at_4"), "d_F_eq": (i.get("M6") or {}).get("d_F_eq"),
                      "stopped": s.get("stopped")})
    # C-NULL / C-NULL-SHUF / C-SHIFT per cell
    per_cell = defaultdict(lambda: defaultdict(list))
    for t in table:
        per_cell[t["cell"]][t["arm"]].append(t)
    nullrep, shiftrep = {}, {}
    for cell, arms in per_cell.items():
        for nm in ("NULL-PROF", "NULL-SHUF"):
            rows = arms.get(nm, [])
            if rows:
                nullrep.setdefault(cell, {})[nm] = {
                    "n": len(rows),
                    "M1_false_at_4": sum(1 for x in rows if (x["M1_at_4"] or {}).get("contained") is False),
                    "z_eq_1": sum(1 for x in rows if x["z"] == 1),
                    "M1_false_and_z1": sum(1 for x in rows if (x["M1_at_4"] or {}).get("contained") is False and x["z"] == 1)}
        e4 = {x["r"]: x for x in arms.get("EQS4", [])}
        e2 = {x["r"]: x for x in arms.get("EQS2", [])}
        pairs = [(e4[r], e2[r]) for r in e4 if r in e2]
        if pairs:
            shiftrep[cell] = {"pairs": len(pairs), "equal_D_solve": sum(1 for a_, b_ in pairs if a_["D_solve"] == b_["D_solve"]),
                              "rows": [{"r": a_["r"], "EQS4": [a_["D_solve"], a_["z"]], "EQS2": [b_["D_solve"], b_["z"]]} for a_, b_ in pairs]}
    controls["C-NULL"] = nullrep
    controls["C-SHIFT"] = shiftrep
    # decisive observations (no interpretation)
    decisive = [t for t in table if t["arm"] in DECISIVE]
    nc = [t for t in decisive if (t["M1_at_4"] or {}).get("contained") is False]
    # ---- M-8 and non_containment_uncertified (IR-4a rejected / IR-4b not_emitted / pending)
    m8_table, uncertified, certified, type_d = [], [], [], []
    for t in decisive:
        for kind in ("ann", "wdag", "none"):
            c = certrec.get((t["key"], kind))
            if c:
                m8_table.append({"key": t["key"], "cert_kind": kind, **{k_: c["M8"].get(k_) for k_ in
                                 ("status", "cert_sha256", "path", "reason", "form", "nodes", "content_bytes")}})
    for t in nc:
        typ = t["M1_at_4"].get("type")
        if typ == "D":
            type_d.append(t["key"])
            continue
        c = certrec.get((t["key"], "ann"))
        status = c["M8"]["status"] if c else "not_emitted"
        aa_key = f'{t["cell"]}/EQS4-AA/{t["r"]}' + ("-U" if t["arm"] == "EQS4-U" else "")
        aa = summ.get(aa_key)
        row = {"key": t["key"], "type": typ, "system_sha256": inst.get(t["key"], {}).get("system_sha256"),
               "ann_status": status, "guard_or_reason": (c or {}).get("M8", {}).get("reason"),
               "dims_by_deg_W4": next((r_["engine"]["dims_by_deg"] for r_ in clos[t["key"]]
                                       if r_.get("D") == 4 and r_.get("status") == "ok"), None),
               "M2": next((r_["M2"] for r_ in clos[t["key"]] if r_.get("D") == 4 and r_.get("status") == "ok"), None),
               "M4": next((r_["M4"] for r_ in clos[t["key"]] if r_.get("D") == 4 and r_.get("status") == "ok"), None),
               "missing_gb_element": (c or {}).get("M8", {}).get("g"),
               "aa_rerun": (aa["M1_at_4"] if aa else "not_run (mandatory, SR-6)")}
        (certified if status == "accepted" else uncertified).append(row)
    cert_rows = [{"key": k_[0], "cert_kind": k_[1], "status": v["M8"]["status"]} for k_, v in certrec.items()]
    # ---- containment at N >= 27: engine-decided, uncertified
    big = [{"key": t["key"], "N": t["N"], "label": "engine-decided, uncertified"}
           for t in decisive if t["N"] >= 27 and (t["M1_at_4"] or {}).get("contained") is True]
    # ---- F-MAIN gate (observations only; no hypothesis verdict)
    carrying = {}
    for cell in CARRYING_CELLS:
        rows = [t for t in table if t["cell"] == cell and t["arm"] == "NULL-PROF"]
        ver = [t for t in rows if t["z"] == 1]
        false = [t for t in ver if (t["M1_at_4"] or {}).get("contained") is False]
        carrying[cell] = {"seeds": len(rows), "z1_verified": len(ver), "z1_and_M1_false": len(false),
                          "threshold_3_of_5_met": len(false) >= 3}
    all_null = [t for t in table if t["arm"] == "NULL-PROF" and 18 <= t["N"] <= 26]
    ver_all = [t for t in all_null if t["z"] == 1]
    false_all = [t for t in ver_all if (t["M1_at_4"] or {}).get("contained") is False]
    p3 = {"pooled_fraction_over_Z1_verified": (len(false_all) / len(ver_all)) if ver_all else None,
          "numerator": len(false_all), "denominator": len(ver_all), "seeds_total": len(all_null),
          "per_cell": {cell: {"z1_verified": c["z1_verified"], "M1_false": c["z1_and_M1_false"]}
                       for cell, c in carrying.items()},
          "cells": "N = 18..26 (the eight carrying cells)"}
    decisive_contained = [t for t in decisive if (t["M1_at_4"] or {}).get("contained") is True]
    other = [t for t in decisive if (t["M1_at_4"] or {}).get("contained") not in (True, False)]
    fmain_gate = {
        "uncertified_non_containments": [u["key"] for u in uncertified],
        "gate": ("incomplete_censored" if uncertified else
                 "incomplete_censored" if other else "no_block_from_certificates"),
        "detail": ("certificate_pending" if uncertified else
                   "censored_or_undetermined_decisive_instances" if other else None),
        "C-NULL_threshold_cells_met": [c for c, v in carrying.items() if v["threshold_3_of_5_met"]],
        "note": "gate only; the verdict (S-MAIN / F-MAIN) is the Reviewer's and Coordinator's"}
    # ---- M-6 and D_solve against 2 and 3 (S-AS1-EXACT descriptive; P-7 calibration d_F^eq <= 2)
    m6 = [{"key": t["key"], "d_F_eq": t["d_F_eq"], "D_solve": t["D_solve"],
           "D_solve_gt_2": (t["D_solve"] if not isinstance(t["D_solve"], int) else t["D_solve"] > 2),
           "D_solve_gt_3": (t["D_solve"] if not isinstance(t["D_solve"], int) else t["D_solve"] > 3)}
          for t in table if t["arm"] in ("EQS4", "EQS4-U", "EQS2")]
    p7_calibration = {"instances": len(m6),
                      "all_d_F_eq_le_2": all(x["d_F_eq"] is not None and x["d_F_eq"] <= 2 for x in m6) if m6 else None,
                      "violations": [x["key"] for x in m6 if x["d_F_eq"] is None or x["d_F_eq"] > 2]}
    # tail checks
    tails = {"largest_deficit_per_cell": {}, "m7_vs_m1_differences": [], "latest_iteration_per_cell": {}}
    for key, rows in clos.items():
        cell, arm, _ = key.split("/")
        if arm not in DECISIVE:
            continue
        for r_ in rows:
            if r_.get("D") == 4 and r_.get("status") == "ok":
                d = (r_["M1"] or {}).get("deficit", 0) or 0
                cur = tails["largest_deficit_per_cell"].get(cell)
                if cur is None or d > cur["deficit"]:
                    tails["largest_deficit_per_cell"][cell] = {"key": key, "deficit": d, "M4": r_["M4"]}
                it = r_["engine"]["iterations_to_fixpoint"]
                if it > tails["latest_iteration_per_cell"].get(cell, {"it": -1})["it"]:
                    tails["latest_iteration_per_cell"][cell] = {"key": key, "it": it}
                m7 = r_.get("M7")
                if m7 and m7.get("gb_in_M") is not None and m7["gb_in_M"] != (r_["M1"] or {}).get("contained"):
                    tails["m7_vs_m1_differences"].append({"key": key, "M7": m7["gb_in_M"], "M1": r_["M1"]["contained"]})
    summary = {"instances": table, "decisive_not_contained": [t["key"] for t in nc],
               "decisive_count": len(decisive), "decisive_contained": len(decisive_contained),
               "M8": m8_table, "certificate_records": cert_rows,
               "non_containment_uncertified": uncertified, "non_containment_certified": certified,
               "type_D_not_counted": type_d,
               "F-MAIN_gate": fmain_gate, "F-MAIN_count_per_carrying_cell": carrying, "P-3": p3,
               "M6_vs_2_and_D_solve_vs_2_and_3": m6, "P-7_calibration": p7_calibration,
               "containment_N_ge_27": big, "tails": tails,
               "der3_mismatches": [k for k, rows in clos.items() for r_ in rows if r_.get("der3_mismatch")],
               "censored_or_failed": [{"key": k, "D": r_.get("D"), "status": r_.get("status")}
                                       for k, rows in clos.items() for r_ in rows
                                       if r_.get("status") not in (None, "ok")],
               "flags": flags,
               "note": "observations only; no verdict on the hypothesis or heuristic is made here"}
    return controls, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--checker-verdicts", default=None,
                    help="JSON {cert_sha256: accept|reject} from the independent checker")
    a = ap.parse_args()
    verdicts = json.load(open(a.checker_verdicts)) if a.checker_verdicts else None
    controls, summary = analyze(a.run_dir, verdicts)
    out = a.out_dir or a.run_dir
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "controls.json"), "w") as f:
        json.dump(controls, f, indent=1, sort_keys=True, default=str)
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({"flags": summary["flags"], "decisive": summary["decisive_count"],
                      "not_contained": len(summary["decisive_not_contained"]),
                      "F-MAIN_gate": summary["F-MAIN_gate"]["gate"]}))


if __name__ == "__main__":
    main()
