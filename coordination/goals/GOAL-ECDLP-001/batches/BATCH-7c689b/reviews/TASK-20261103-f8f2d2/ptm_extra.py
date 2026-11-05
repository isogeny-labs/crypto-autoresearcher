#!/usr/bin/env python3
"""PTM-2 perturbation for the runs j34_extract.py did not perturb (fib-005, mtic-008, fib-decision).

Usage: python3 ptm_extra.py <repo_root> <arms_root> <out_json>
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j34_extract as X  # noqa: E402


def main():
    X.ROOT, X.ARMS, out = sys.argv[1:4]
    res = {}
    a5 = X.fib_raw(os.path.join(X.run_dir("EXP-FIB-001", "RUN-FIB-005"), "raw.json"))
    l5 = X.fib_raw(X.arm_path("4be606", "legacy", "runs", "RUN-FIB-005", "raw.json"))
    base = X.fib_control(a5, l5)["pass"]
    p = copy.deepcopy(l5)
    p["C20-1"]["measurements"][0]["capped"] = False
    res["fib005_C20-1_target0_capped_flipped"] = {"unperturbed_pass": base, "perturbed_pass": X.fib_control(a5, p)["pass"]}
    a8 = X.jl(X.run_dir("EXP-MTIC-001", "RUN-MTIC-008"), "raw.json")
    l8 = X.jl(X.arm_path("fcd67c", "legacy", "out-root", "runs", "RUN-MTIC-008", "raw.json"))
    base = X.mtic_control(a8, l8)["pass"]
    p = copy.deepcopy(l8)
    p["raw"]["per_target"]["24"][0]["capped"] = False
    res["mtic008_24bit_target0_capped_flipped"] = {"unperturbed_pass": base, "perturbed_pass": X.mtic_control(a8, p)["pass"]}
    arch = X.fib_decision_extract(X.fib_raw(os.path.join(X.run_dir("EXP-FIB-001", "RUN-FIB-004"), "raw.json")),
                                  X.fib_raw(os.path.join(X.run_dir("EXP-FIB-001", "RUN-FIB-005"), "raw.json")))[1]
    leg = X.fib_decision_extract(X.fib_raw(X.arm_path("3e69b6", "legacy", "runs", "RUN-FIB-004", "raw.json")),
                                 X.fib_raw(X.arm_path("4be606", "legacy", "runs", "RUN-FIB-005", "raw.json")))[1]
    keys = ("correlation_gate_pass_overall", "correlation_gate_curves_passing", "per_curve_status")
    base = all(arch[k] == leg[k] for k in keys)
    p = copy.deepcopy(leg)
    p["per_curve_status"]["C16-2"] = "measured"
    res["fibdecision_C16-2_status_flipped"] = {"unperturbed_pass": base, "perturbed_pass": all(arch[k] == p[k] for k in keys)}
    for v in res.values():
        v["ok"] = v["unperturbed_pass"] is True and v["perturbed_pass"] is False
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
