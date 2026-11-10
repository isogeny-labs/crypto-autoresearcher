#!/usr/bin/env python3
"""Independent receipt checks for sheriff case SHF-20261106-a114e7, joint ICV (icperf-receipts).

Reads only committed files of crypto-autoresearcher and this reader's own audit replays.
Does not import any producer code (run.py, check.py) or tools/runbook.py.

Checks:
  R1  every execution-receipt.json artifact_sha256 matches the file bytes
  R2  journal unit entries' artifact digests match the run directory files
  R3  journal hash chain: each entry's prev equals the previous entry's hash (structure only;
      the entry-hash recomputation is tools/runbook.py's and is re-run separately)
  R4  raw rows against the blind re-derivation (blind_rederive.json) and the frozen control pass conditions
  R5  internal arithmetic of each raw row (cv_sq_num = 64*ssq - ssum^2, ratios reduce, etc.)
  R6  manifest/launch/plan/trial consistency (trial ids, run ids, N planned == N run, task id, approval id)
  R7  this reader's audit replays: full-document comparison of replay raw-result.json against recorded,
      ignoring only /interpreter, /elapsed_seconds and /run_id-derived paths
"""
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
EXPS = {
    "EXP-ICPERF-284bc4": "RBS-ICPERF-8cdc92",
    "EXP-ICPERF-283a70": "RBS-ICPERF-67df7d",
}
out = {"checks": {}, "problems": []}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prob(msg):
    out["problems"].append(msg)


blind = json.loads((HERE / "blind_rederive.json").read_text())

for exp, sess in EXPS.items():
    ed = REPO / "experiments" / exp
    plan = json.loads((ed / "trial-plan.json").read_text())
    journal = [json.loads(l) for l in (ed / "runbook-sessions" / sess / "journal.jsonl").read_text().splitlines() if l.strip()]
    rec = out["checks"].setdefault(exp, {})
    # R3 chain structure
    chain_ok = all(journal[i]["prev"] == journal[i - 1]["hash"] for i in range(1, len(journal))) and journal[0]["prev"] == "0" * 64
    seqs_ok = [e["seq"] for e in journal] == list(range(len(journal)))
    rec["R3_chain_prev_links"] = chain_ok
    rec["R3_seq_contiguous"] = seqs_ok
    if not (chain_ok and seqs_ok):
        prob(f"{exp}: journal chain/seq broken")
    units = [e for e in journal if e.get("run_id")]
    rec["units_in_journal"] = len(units)
    rec["trials_in_plan"] = len(plan["trials"])
    rec["N_equal_planned"] = len(units) == len(plan["trials"]) and sorted(u["run_id"] for u in units) == sorted(t["run_id"] for t in plan["trials"])
    runs_on_disk = sorted(p.name for p in (ed / "runs").iterdir() if p.is_dir())
    rec["run_dirs_on_disk"] = runs_on_disk
    rec["run_dirs_equal_plan"] = runs_on_disk == sorted(t["run_id"] for t in plan["trials"])
    rec["unit_validity"] = {u["run_id"]: {k: u.get(k) for k in ("trial_id", "valid", "control", "receipt_status", "failure_class")} for u in units}
    r1 = {}
    for t in plan["trials"]:
        rd = ed / "runs" / t["run_id"]
        er = json.loads((rd / "execution-receipt.json").read_text())
        bad = [n for n, h in er["artifact_sha256"].items() if not (rd / n).is_file() or sha(rd / n) != h]
        extra = sorted(p.name for p in rd.iterdir() if p.is_file() and p.name not in er["artifact_sha256"] and p.name != "execution-receipt.json")
        r1[t["run_id"]] = {"artifacts": len(er["artifact_sha256"]), "mismatch": bad, "unlisted_files": extra,
                           "status": er.get("status"), "returncode": er.get("returncode"), "check_returncode": er.get("check_returncode"),
                           "plan_sha256_ok": er.get("plan_sha256") == sha(ed / "trial-plan.json")}
        if bad or extra:
            prob(f"{exp}/{t['run_id']}: receipt mismatch {bad} unlisted {extra}")
        # R2 journal digests
        u = next(u for u in units if u["run_id"] == t["run_id"])
        jbad = [n for n, h in u["artifacts"].items() if sha(rd / n) != h]
        if sha(rd / "execution-receipt.json") != u.get("receipt_sha256"):
            jbad.append("execution-receipt.json(receipt_sha256)")
        r1[t["run_id"]]["journal_digest_mismatch"] = jbad
        if jbad:
            prob(f"{exp}/{t['run_id']}: journal digest mismatch {jbad}")
        # R6 manifest consistency
        man = json.loads((rd / "manifest.yaml").read_text())["run"]
        raw = json.loads((rd / "raw-result.json").read_text())
        launch = json.loads((rd / "launch.json").read_text())
        env = json.loads((rd / "environment.json").read_text())
        cons = {
            "manifest_trial": man["trial_id"] == t["id"] == raw["trial_id"] == launch["trial_id"],
            "manifest_run": man["id"] == t["run_id"] == raw["run_id"] == launch["run_id"],
            "task_id": man["task_id"] == plan["task_id"],
            "approved_by": man["approved_by"] == plan["approved_by"],
            "env_source_sha_matches_plan": env["source_sha256"] == plan["source_sha256"],
            "env_spec_sha_matches_plan": env["specification_sha256"] == plan["specification_sha256"],
            "commit": env["commit"],
            "dirty_recorded_in_run": any(k in json.dumps(man) for k in ('"dirty"', "tracked_dirty")),
            "started": man["timing"]["started_at"],
        }
        r1[t["run_id"]]["consistency"] = cons
        for k in ("manifest_trial", "manifest_run", "task_id", "approved_by", "env_source_sha_matches_plan", "env_spec_sha_matches_plan"):
            if not cons[k]:
                prob(f"{exp}/{t['run_id']}: {k} inconsistent")
    rec["R1_R2_R6_runs"] = r1

# R4/R5 284bc4 against blind values
ed = REPO / "experiments" / "EXP-ICPERF-284bc4"
plan = json.loads((ed / "trial-plan.json").read_text())
rows = {t["id"]: json.loads((ed / "runs" / t["run_id"] / "raw-result.json").read_text()) for t in plan["trials"]}
B = {"primary": blind["284bc4_primary"], "neg1": blind["284bc4_NEG1_c_probe_371"], "neg2": blind["284bc4_NEG2_precomp_10"]}


def frac(x):
    if isinstance(x, dict):
        return F(x["num"], x["den"])
    return F(x)


def cell_ok(cell, bcell, with_bsgs):
    ok = (cell["r"], cell["A"]) == (bcell["r"], bcell["A"])
    ok &= frac(cell["probes"]) == F(bcell["probes"]) and frac(cell["bl_steps"]) == F(bcell["bl_steps"])
    ok &= frac(cell["ic_online_ns"]) == F(bcell["ic_online_ns"]) and frac(cell["bl_online_ns"]) == F(bcell["bl_online_ns"])
    ok &= [cell["ratio_num"], cell["ratio_den"]] == bcell["online_ratio"]
    # R5 internal: ratio reduces from the row's own online times
    q = frac(cell["ic_online_ns"]) / frac(cell["bl_online_ns"])
    ok &= (q.numerator, q.denominator) == (cell["ratio_num"], cell["ratio_den"])
    if with_bsgs:
        ok &= cell["bsgs_probes"] == bcell["bsgs_enumerated"]
    return bool(ok)


bycell = lambda b: {(c["r"], c["A"]): c for c in b["cells"]}
r4 = {}
p = rows["price-ratio-identity"]
bp = bycell(B["primary"])
r4["price-ratio-identity"] = {
    "price_ratio": [p["price_ratio_num"], p["price_ratio_den"]] == B["primary"]["price_ratio"],
    "precomputation_steps": str(p["precomputation_steps"]) == B["primary"]["precomputation_steps"],
    "ratios_agree": p["ratios_agree"] is True and B["primary"]["ratios_agree"] is True,
    "all_match_bsgs": p["all_match_bsgs"] is True,
    "matches_preregistered": p["matches_preregistered"] is True,
    "cells": [cell_ok(c, bp[(c["r"], c["A"])], True) for c in p["cells"]],
    "n_cells": len(p["cells"]),
    "all_integer_in_primary": all(not isinstance(c[k], dict) for c in p["cells"] for k in ("probes", "bl_steps", "ic_online_ns", "bl_online_ns")),
}
for tid in ("ctl-consistency-a-change", "ctl-consistency-r-change"):
    r = rows[tid]
    r4[tid] = {"cells": [cell_ok(c, bp[(c["r"], c["A"])], True) for c in r["cells"]],
               "cell_keys": [(c["r"], c["A"]) for c in r["cells"]],
               "same_reduced_ratio": r["same_reduced_ratio"], "matches_preregistered": r["matches_preregistered"],
               "same_recomputed": len({(c["ratio_num"], c["ratio_den"]) for c in r["cells"]}) == 1}
r = rows["ctl-bsgs-enumeration"]
r4["ctl-bsgs-enumeration"] = {"cells": [(c["r"], c["A"], c["enumerated_probes"], c["formula_probes"],
                                         bp[(c["r"], c["A"])]["bsgs_enumerated"], c["match"]) for c in r["cells"]],
                              "all_match": r["all_match"],
                              "blind_enum_equals_recorded": all(c["enumerated_probes"] == bp[(c["r"], c["A"])]["bsgs_enumerated"] for c in r["cells"])}
r = rows["ctl-neg-perturbed-price"]
bn = bycell(B["neg1"])
r4["ctl-neg-perturbed-price"] = {"price": [r["price_ratio_num"], r["price_ratio_den"]], "blind_price": B["neg1"]["price_ratio"],
                                 "online": [r["online_ratio_num"], r["online_ratio_den"]],
                                 "cells": [cell_ok(c, bn[(c["r"], c["A"])], False) for c in r["cells"]],
                                 "matches_preregistered": r["matches_preregistered"],
                                 "declared_pass": r["matches_preregistered"] is False and [r["price_ratio_num"], r["price_ratio_den"], r["online_ratio_num"], r["online_ratio_den"]] == [1855, 8, 1855, 8]}
r = rows["ctl-neg-precomputation-model"]
bn = bycell(B["neg2"])
r4["ctl-neg-precomputation-model"] = {"online": [r["online_ratio_num"], r["online_ratio_den"]],
                                      "cells": [cell_ok(c, bn[(c["r"], c["A"])], False) for c in r["cells"]],
                                      "precomputation_steps": r["precomputation_steps"],
                                      "price_ratio_recorded": "price_ratio_num" in r,
                                      "matches_preregistered": r["matches_preregistered"],
                                      "noninteger_cells": [c["name"] for c in r["cells"] if any(isinstance(c[k], dict) for k in ("bl_steps", "ic_online_ns", "bl_online_ns", "probes"))],
                                      "declared_pass": r["matches_preregistered"] is False and [r["online_ratio_num"], r["online_ratio_den"]] == [185, 42]}
out["checks"]["R4_R5_284bc4"] = r4

# R4/R5 283a70
ed = REPO / "experiments" / "EXP-ICPERF-283a70"
plan = json.loads((ed / "trial-plan.json").read_text())
rows = {t["id"]: json.loads((ed / "runs" / t["run_id"] / "raw-result.json").read_text()) for t in plan["trials"]}
G = blind["283a70"]
mp = {"geometric-probe-sample": "primary", "ctl-neg-wrong-triple": "CTL1_wrong_triple_1_2_14", "ctl-neg-support-zero": "CTL2_support_zero"}
keys = ["sample_sum", "sum_squares", "median", "median_split", "exact_match", "cv_sq_num", "cv_sq_den",
        "median_ratio_num", "median_ratio_den", "cv_in_band", "median_ratio_in_band"]
r4 = {}
for tid, bk in mp.items():
    r = rows[tid]
    diff = {k: (r.get(k), G[bk][k]) for k in keys if r.get(k) != G[bk][k]}
    internal = (r["cv_sq_num"] == 64 * r["sum_squares"] - r["sample_sum"] ** 2 and r["cv_sq_den"] == r["sample_sum"] ** 2
                and r["median_ratio_num"] == r["median"] * 64 and r["median_ratio_den"] == r["sample_sum"]
                and r["cv_in_band"] == (F(81, 100) <= F(r["cv_sq_num"], r["cv_sq_den"]) <= F(121, 100))
                and r["median_ratio_in_band"] == (F(3, 5) <= F(r["median_ratio_num"], r["median_ratio_den"]) <= F(4, 5)))
    r4[tid] = {"diff_vs_blind": diff, "internal_arithmetic_ok": internal,
               "shifts": r["shifts"], "support_min": r["support_min"], "seed": r["seed"],
               "raw_draws_recorded": any(k in r for k in ("draws", "sample", "values", "counts"))}
    if diff or not internal:
        prob(f"283a70/{tid}: diff {diff} internal {internal}")
out["checks"]["R4_R5_283a70"] = r4

# R7 full-document replay comparison (this reader's audit)
r7 = {}
for exp, sess in EXPS.items():
    ad = HERE / f"audit-{sess}" / "replay"
    if not ad.is_dir():
        r7[exp] = "no replay directory"
        continue
    for rd in sorted(ad.iterdir()):
        rec_raw = json.loads((REPO / "experiments" / exp / "runs" / rd.name / "raw-result.json").read_text())
        rep_raw = json.loads((rd / "raw-result.json").read_text())
        ign = {"interpreter", "elapsed_seconds"}
        ka, kb = set(rec_raw) - ign, set(rep_raw) - ign
        diffs = sorted(k for k in ka | kb if rec_raw.get(k, "<absent>") != rep_raw.get(k, "<absent>"))
        r7[f"{exp}/{rd.name}"] = {"keys_compared": len(ka | kb), "differing_keys": diffs,
                                  "replay_interpreter": rep_raw.get("interpreter", {}).get("version")}
        if diffs:
            prob(f"{exp}/{rd.name}: replay differs in {diffs}")
out["checks"]["R7_replay_full_document"] = r7

json.dump(out, sys.stdout, indent=1, sort_keys=True, default=str)
print()
