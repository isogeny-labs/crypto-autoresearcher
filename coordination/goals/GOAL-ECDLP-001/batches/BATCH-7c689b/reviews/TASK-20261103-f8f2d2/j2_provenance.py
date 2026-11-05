#!/usr/bin/env python3
"""J2 arm-provenance checks (TASK-20261103-f8f2d2), validator's own code.

Usage: python3 j2_provenance.py <repo_root> <arms_root> <out_json>
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j5_rederive as J  # noqa: E402

PIN = {"legacy": ("53a23952420f8ee724b70746eb7c872e54cbb33dc4cb24be1e88dcdcbef4817e",
                  "experiments/EXP-SEMAEV-93d5cc/implementation/vendor/semaev_legacy_53a23952.py",
                  "harness._semaev_legacy_53a23952"),
       "repaired": ("c417f1948d7df7bb1864726e169d885e4d3163cb62036393f2616ef71c630de6",
                    "harness/semaev.py", "harness.semaev")}
RUNS = {"9cab7b": ("EXP-SEMAEV-93d5cc", "icinv-m4"), "3e69b6": ("EXP-SEMAEV-93d5cc", "fib-004"),
        "4be606": ("EXP-SEMAEV-93d5cc", "fib-005"), "894e27": ("EXP-SEMAEV-93d5cc", "fib-decision"),
        "2a8498": ("EXP-SEMAEV-93d5cc", "mtic-007"), "fcd67c": ("EXP-SEMAEV-93d5cc", "mtic-008"),
        "0e5876": ("EXP-SEMAEV-6e9dcf", "mtic-010b")}
BIG = (1 << 61) - 1  # Mersenne prime; term count mod BIG equals count over Z unless a coefficient is a multiple of BIG


def my_fingerprint(kind):
    f = J.s4_exact if kind == "repaired" else J.s4_drop
    pz = f(BIG, 2, 3)
    p101 = f(101, 2, 3)
    return {"free_symbols": pz.free_vars(), "terms_over_Z": pz.nterms(), "total_degree": pz.total_degree(),
            "witness_residue_mod_101": p101.eval((1, 3, 5, 41))}


def main():
    root, arms_root, out_path = sys.argv[1:4]
    out = {"pinned_source_sha256_at_head": {}, "my_fingerprint": {}, "runs": {}}
    for arm, (h, path, _) in PIN.items():
        out["pinned_source_sha256_at_head"][arm] = hashlib.sha256(open(os.path.join(root, path), "rb").read()).hexdigest() == h
        out["my_fingerprint"][arm] = my_fingerprint(arm)
    for r, (exp, cell) in RUNS.items():
        rd = os.path.join(root, "experiments", exp, "runs", f"RUN-SEMAEV-{r}")
        res = {"cell": cell, "issues": []}
        for arm in ("legacy", "repaired"):
            ar = json.load(open(os.path.join(arms_root, r, "arms", arm, "arm-result.json")))
            prov = ar.get("provenance", {})
            a = {"fingerprint_equals_mine": ar.get("s4_fingerprint") == out["my_fingerprint"][arm],
                 "arm_field": ar.get("arm") == arm and prov.get("arm") == arm}
            if prov.get("s4_used") is False:
                a["s4_used"] = False
            else:
                a["pinned_sha"] = prov.get("s4_source_sha256") == PIN[arm][0]
                a["pinned_path"] = prov.get("s4_source") == PIN[arm][1]
                if "installed_function_module" in prov:
                    a["module"] = prov["installed_function_module"] == PIN[arm][2]
                    a["installed_fp_equals_reported"] = prov.get("installed_fingerprint") == ar.get("s4_fingerprint")
            if cell.startswith("fib-0"):
                lines = open(os.path.join(rd, f"arm-{arm}.stderr.log")).read().splitlines()
                pat = re.compile(r"^fib_child arm=(\w+) module=(\S+) sha256=([0-9a-f]+)$")
                ok = [m for m in map(pat.match, lines) if m]
                good = [m for m in ok if m.group(1) == arm and m.group(2) == PIN[arm][2] and PIN[arm][0].startswith(m.group(3))]
                raw = json.load(open(os.path.join(arms_root, r, "arms", arm, "runs",
                                                  "RUN-FIB-004" if cell == "fib-004" else "RUN-FIB-005", "raw.json")))
                n_solves = sum(len(v["measurements"]) for v in raw["per_curve"].values())
                a["child_lines"] = len(lines)
                a["child_lines_matching_arm"] = len(good)
                a["non_matching_lines"] = len(lines) - len(good)
                a["n_solves_in_arm_raw"] = n_solves
                a["child_lines_eq_solves"] = len(good) == n_solves
            bad = [k for k, v in a.items() if v is False and k != "s4_used"]
            if bad:
                res["issues"].append(f"{arm}: {bad}")
            res[arm] = a
        out["runs"][r] = res
        print(r, cell, "clean" if not res["issues"] else res["issues"],
              {arm: {k: v for k, v in res[arm].items() if not isinstance(v, bool) or v is False} for arm in ("legacy", "repaired")})
    print("my fingerprints", json.dumps(out["my_fingerprint"]))
    json.dump(out, open(out_path, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
