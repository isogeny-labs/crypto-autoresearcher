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
    return {"M1": m1(rows, D), "M2": r["M2"], "M4": m4, "final_dim": r["engine"]["final_dim"]}


def analyze(run_dir):
    inst, clos, summ = load(run_dir)
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
                diffs.append({"D": D, "aa": a_ and {k: a_[k] for k in ("M1", "M2", "final_dim")},
                              "src": b_ and {k: b_[k] for k in ("M1", "M2", "final_dim")}})
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
    decisive = [t for t in table if t["arm"] in ("EQS4", "EQS4-U")]
    nc = [t for t in decisive if (t["M1_at_4"] or {}).get("contained") is False]
    cert_rows = []
    for key in [t["key"] for t in nc]:
        for r_ in clos[key]:
            for c in (r_.get("certificates") or []):
                cert_rows.append({"key": key, "D": r_["D"], **{k: c.get(k) for k in ("kind", "path", "cert_sha256", "form", "not_emitted")}})
    # tail checks
    tails = {"largest_deficit_per_cell": {}, "m7_vs_m1_differences": [], "latest_iteration_per_cell": {}}
    for key, rows in clos.items():
        cell, arm, _ = key.split("/")
        if arm not in ("EQS4", "EQS4-U"):
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
               "decisive_count": len(decisive), "certificates_for_not_contained": cert_rows, "tails": tails,
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
    a = ap.parse_args()
    controls, summary = analyze(a.run_dir)
    out = a.out_dir or a.run_dir
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "controls.json"), "w") as f:
        json.dump(controls, f, indent=1, sort_keys=True, default=str)
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True, default=str)
    print(json.dumps({"flags": summary["flags"], "decisive": summary["decisive_count"],
                      "not_contained": len(summary["decisive_not_contained"])}))


if __name__ == "__main__":
    main()
