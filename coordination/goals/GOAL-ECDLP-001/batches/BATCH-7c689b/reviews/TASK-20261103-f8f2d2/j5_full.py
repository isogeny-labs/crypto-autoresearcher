#!/usr/bin/env python3
"""J5 full-coverage extension (TASK-20261103-f8f2d2).

Uses only the validator's own S4 code in j5_rederive.py. Curve parameters come
from the archived RUN-ICINV-e0cd8f-m3class records (base (a, b) and gauge twin
(a2, b2), with a2 = u^4 a, b2 = u^6 b checked here) and from the regenerated
EXP-FIB-001 C16-1 instance. Arm and archived outputs are read only as the
values compared against, after the derivation.

Usage: python3 j5_full.py <repo_root> <arms_root> <out_json>
  arms_root holds extracted arms.tar.gz trees: <arms_root>/<run6>/arms/<arm>/...
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j5_rederive as J  # noqa: E402


def main():
    root, arms_root, out_path = sys.argv[1:4]
    out = {}

    # ---------------- ICINV: all 552 (set, index, role) records
    rd = os.path.join(root, "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class")
    p = None
    derived = {}
    gauge_law_ok = True
    for setname, fn in (("class", "per-curve-invariants.json"), ("control", "control-set-invariants.json")):
        d = json.load(open(os.path.join(rd, fn)))
        p = d["p"]
        for i, c in enumerate(d["curves"]):
            g = c["gauge"]
            if (pow(g["u"], 4, p) * c["a"] - g["a2"]) % p or (pow(g["u"], 6, p) * c["b"] - g["b2"]) % p:
                gauge_law_ok = False
            for role, a, b, arch in (("base", c["a"], c["b"], c["m4"]["s4_support"]),
                                     ("gauge", g["a2"], g["b2"], g["m4"]["s4_support"])):
                derived[(setname, i, role)] = {
                    "a": a, "b": b,
                    "exact": J.s4_exact(p, a, b).nterms(),
                    "drop": J.s4_drop(p, a, b).nterms(),
                    "archived": arch,
                }
    arms = {}
    for arm in ("legacy", "repaired"):
        recs = json.load(open(os.path.join(arms_root, "9cab7b/arms", arm, "m4-records.json")))["records"]
        arms[arm] = {(r["set"], r["index"], r["role"]): r for r in recs}
    mism = {"legacy_vs_drop": [], "repaired_vs_exact": [], "archived_vs_drop": [], "param_mismatch": [], "missing": []}
    for k, v in derived.items():
        for arm, key, field in (("legacy", "legacy_vs_drop", "drop"), ("repaired", "repaired_vs_exact", "exact")):
            r = arms[arm].get(k)
            if r is None:
                mism["missing"].append([arm, *k])
                continue
            if (r["a"], r["b"]) != (v["a"], v["b"]):
                mism["param_mismatch"].append([arm, *k])
            if r["m4"].get("s4_support") != v[field]:
                mism[key].append([arm, *k, r["m4"].get("s4_support"), v[field]])
        if v["archived"] != v["drop"]:
            mism["archived_vs_drop"].append([*k, v["archived"], v["drop"]])
    out["icinv"] = {
        "p": p, "n_records_derived": len(derived),
        "n_arm_records": {a: len(arms[a]) for a in arms},
        "gauge_law_ok": gauge_law_ok,
        "exact_values": sorted({v["exact"] for v in derived.values()}),
        "drop_values": sorted({v["drop"] for v in derived.values()}),
        "mismatches": mism,
    }

    # ---------------- FIB C16-1: all 200 targets, both polynomials
    sys.path.insert(0, os.path.join(root, "experiments/EXP-FIB-001"))
    sys.path.insert(0, root)
    from driver import instances  # noqa: E402
    spec = next(s for s in instances.MAIN_CURVES if s["id"] == "C16-1")
    ctx = instances.build_curve(spec)
    targets = instances.generate_targets(ctx, 200)
    assert "harness.semaev" not in sys.modules
    pE, aE, bE = ctx.E.p, ctx.E.a, ctx.E.b
    S4e, S4d = J.s4_exact(pE, aE, bE), J.s4_drop(pE, aE, bE)
    der = {}
    for t in targets:
        xR = t["Rx"]
        der[t["index"]] = {
            "exact": J.singular_gb(pE, J.to_xyz(S4e.subs_x4(xR)), ctx.V),
            "drop": J.singular_gb(pE, J.to_xyz(S4d.subs_x4(xR)), ctx.V),
        }

    def meas(path):
        d = json.load(open(path))
        d = d.get("per_curve", d)
        return {m["target_index"]: m for m in d["C16-1"]["measurements"]}

    srcs = {
        "archived": (os.path.join(root, "experiments/EXP-FIB-001/runs/RUN-FIB-004/raw.json"), "drop"),
        "legacy": (os.path.join(arms_root, "3e69b6/arms/legacy/runs/RUN-FIB-004/raw.json"), "drop"),
        "repaired": (os.path.join(arms_root, "3e69b6/arms/repaired/runs/RUN-FIB-004/raw.json"), "exact"),
    }
    fib = {"N": ctx.N, "B": ctx.B, "V": ctx.V, "per_source": {}}
    for name, (path, poly) in srcs.items():
        m = meas(path)
        agree = differ = capped = 0
        diffs = []
        for i, rec in m.items():
            if rec["capped"]:
                capped += 1
                continue
            n, md, tr = der[i][poly]
            got = (rec["groebner_basis_size"], rec["groebner_basis_max_degree"], rec["is_trivial_ideal"])
            if got == (n, md, tr):
                agree += 1
            else:
                differ += 1
                diffs.append([i, list(got), [n, md, tr]])
        fib["per_source"][name] = {"compared_polynomial": poly, "n_measured": len(m), "n_capped": capped,
                                   "agree": agree, "differ": differ, "diffs": diffs[:20]}
    fib["derived_summary"] = {
        k: {"basis_sizes": sorted({v[k][0] for v in der.values()}),
            "max_degrees": sorted({v[k][1] for v in der.values()}),
            "n_trivial": sum(1 for v in der.values() if v[k][2])}
        for k in ("exact", "drop")}
    out["fib_c16_1"] = fib
    json.dump(out, open(out_path, "w"), indent=1, sort_keys=True)
    print(json.dumps({"icinv": {k: v for k, v in out["icinv"].items() if k != "mismatches"},
                      "icinv_mismatch_counts": {k: len(v) for k, v in mism.items()}}, indent=1))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "diffs"} for k, v in fib["per_source"].items()}, indent=1))
    print(json.dumps(fib["derived_summary"]))


if __name__ == "__main__":
    main()
