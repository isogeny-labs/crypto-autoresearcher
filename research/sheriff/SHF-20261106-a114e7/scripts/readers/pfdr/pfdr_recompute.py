#!/usr/bin/env python3
"""Independent recomputation of the EXP-PFDR-bb0d26 headline numbers from the raw
job records (sheriff case SHF-20261106-a114e7, reader pfdr).

Written from the statistics text of experiments/EXP-PFDR-bb0d26/specification.yaml
(inputs.statistics, cell_classes, calibration_gate, toy_reading_rules, headline)
only. It imports nothing from the producer's implementation/ or review/ trees.

usage: python3 -I pfdr_recompute.py <jobs.jsonl> <design.json> <analysis.json> <EV yaml> <out.json>
       [--boot-seed N] [--tamper-cell CELL --tamper-factor F]  (proves-too-much control)
"""
import json
import math
import random
import statistics
import sys
import zlib
from collections import defaultdict


def load_jobs(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def mean(xs):
    return sum(xs) / len(xs)


def svar(xs):  # sample variance, ddof = 1
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def cell_stats(recs, boot_seed, n_boot=2000):
    recs = sorted(recs, key=lambda r: r["c"])
    mu = [mean(r["null_C"]) for r in recs]
    va = [svar(r["null_C"]) for r in recs]
    g = [r["gap_C"] for r in recs]
    pl = [r["plant_C"] for r in recs]
    S, M, V = sum(g), sum(mu), sum(va)
    se = math.sqrt(V * (1 + 1 / 20))
    kappa = S / M
    z = (S - M) / se
    # z_cal: replicate 0 against replicates 1..19
    S0 = sum(r["null_C"][0] for r in recs)
    M0 = sum(mean(r["null_C"][1:]) for r in recs)
    V0 = sum(svar(r["null_C"][1:]) for r in recs)
    z_cal = (S0 - M0) / math.sqrt(V0 * (1 + 1 / 19))
    plant_kappa = sum(pl) / M
    plant_z = (sum(pl) - M) / se
    # own curve-cluster percentile bootstrap (own seed; the spec fixes no seed derivation)
    rng = random.Random(boot_seed)
    k = len(recs)
    ks = []
    for _ in range(n_boot):
        idx = [rng.randrange(k) for _ in range(k)]
        ks.append(sum(g[i] for i in idx) / sum(mu[i] for i in idx))
    ks.sort()
    lo = ks[int(math.floor(0.025 * (n_boot - 1)))]
    hi = ks[int(math.ceil(0.975 * (n_boot - 1)))]
    # even / odd curve halves (C-aa-curves): kappa per half
    ev = [i for i, r in enumerate(recs) if r["c"] % 2 == 0]
    od = [i for i, r in enumerate(recs) if r["c"] % 2 == 1]
    def half(ids):
        s, m, v = sum(g[i] for i in ids), sum(mu[i] for i in ids), sum(va[i] for i in ids)
        return s, m, v
    se_, me_, ve_ = half(ev)
    so_, mo_, vo_ = half(od)
    k_even, k_odd = se_ / me_, so_ / mo_
    # one natural A/A z for the even/odd split: difference of the two halves' excesses
    z_eo = ((se_ - me_) / me_ - (so_ - mo_) / mo_) / math.sqrt(
        (ve_ * 1.05) / me_ ** 2 + (vo_ * 1.05) / mo_ ** 2)
    return dict(curves=k, S=S, M=M, V=V, kappa=kappa, z=z, z_cal=z_cal, plant_kappa=plant_kappa,
                plant_z=plant_z, plant_feasible_all=all(r["plant_feasible"] for r in recs),
                own_ci95=[lo, hi], kappa_even=k_even, kappa_odd=k_odd, z_eo=z_eo, se=se)


def classify(st, n_ok, n_curves, ci):
    if st is None or n_ok < n_curves:
        return "invalid"
    if st["M"] < 2500:
        return "inconclusive_underpowered"
    if not (st["plant_feasible_all"] and st["plant_kappa"] >= 1.15 and st["plant_z"] > 4):
        return "inconclusive_plant_not_recovered"
    if abs(st["kappa"] - 1) >= 0.10 and abs(st["z"]) > 4:
        return "flagged"
    if abs(st["kappa"] - 1) < 0.05 and ci[0] >= 0.90 and ci[1] <= 1.10:
        return "null"
    return "intermediate"


def norm_sf(x):
    return 0.5 * math.erfc(x / math.sqrt(2))


def chi2_sf_even(x, k):  # survival of chi-square with even k degrees of freedom
    assert k % 2 == 0
    t = x / 2
    term, acc = 1.0, 1.0
    for i in range(1, k // 2):
        term *= t / i
        acc += term
    return math.exp(-t) * acc


def main(argv):
    jobs_p, design_p, analysis_p, ev_p, out_p = argv[:5]
    opts = argv[5:]
    boot_seed = 20261106
    tamper_cell, tamper_factor = None, None
    if "--boot-seed" in opts:
        boot_seed = int(opts[opts.index("--boot-seed") + 1])
    if "--tamper-cell" in opts:
        tamper_cell = opts[opts.index("--tamper-cell") + 1]
        tamper_factor = float(opts[opts.index("--tamper-factor") + 1])
    jobs = load_jobs(jobs_p)
    design = json.load(open(design_p, encoding="utf-8"))
    analysis = json.load(open(analysis_p, encoding="utf-8"))
    if tamper_cell:  # proves-too-much: inflate the gap count of one cell's records
        for r in jobs:
            if r["cell"] == tamper_cell and r["status"] == "ok":
                r["gap_C"] = int(round(r["gap_C"] * tamper_factor))
    out = {"inputs": {"jobs": jobs_p, "design": design_p, "analysis": analysis_p}, "boot_seed": boot_seed,
           "tamper": {"cell": tamper_cell, "factor": tamper_factor}}

    # ---- census-level facts ----
    status = defaultdict(int)
    for r in jobs:
        status[r["status"]] += 1
    keys = [(r["cell"], r["block"], r["c"]) for r in jobs]
    curves = {(r["bits"], r["c"]) for r in jobs}
    curve_params = defaultdict(set)
    for r in jobs:
        curve_params[(r["bits"], r["c"])].add((r["p"], r["a"], r["b_coef"], r["N"]))
    ok = [r for r in jobs if r["status"] == "ok"]
    degenerate = [r for r in jobs if r["status"] == "degenerate"]
    planned = sum(c["n_curves"] for c in design["toy_cells"])
    out["census"] = {
        "jobs": len(jobs), "planned_keys_from_design": planned, "status_counts": dict(status),
        "duplicate_keys": len(keys) - len(set(keys)), "distinct_curves_bits_c": len(curves),
        "curves_with_inconsistent_params_across_cells": sum(1 for v in curve_params.values() if len(v) != 1),
        "ok_jobs_with_duplicate_skips": sum(1 for r in ok if r["gap_meta"]["duplicate_skips"] != 0),
        "degenerate": [{"cell": r["cell"], "c": r["c"], "gap_meta": r["gap_meta"]} for r in degenerate],
        "seed_c_max": max(r["c"] for r in jobs), "blocks": sorted({r["block"] for r in jobs}),
    }

    # ---- per-cell statistics ----
    by_cell = defaultdict(list)
    for r in ok:
        by_cell[r["cell"]].append(r)
    rec_cells = {c["cell"]: c for c in analysis["cells"]}
    cells = []
    for d in design["toy_cells"]:
        cid = d["cell"]
        recs = by_cell.get(cid, [])
        st = cell_stats(recs, boot_seed + zlib.crc32(cid.encode())) if recs else None
        rc = rec_cells[cid]
        ci_rec = rc.get("ci95")
        cls_own = classify(st, len(recs), d["n_curves"], st["own_ci95"] if st else None)
        cls_with_rec_ci = classify(st, len(recs), d["n_curves"], ci_rec) if ci_rec else cls_own
        row = {"cell": cid, "bits": d["bits"], "r": d["r"], "n": d["n"], "n_curves": d["n_curves"],
               "ok_curves": len(recs), "cls_recorded": rc["cls"], "cls_own_ci": cls_own,
               "cls_with_recorded_ci": cls_with_rec_ci}
        if st:
            row.update({k: st[k] for k in ("S", "M", "V", "kappa", "z", "z_cal", "plant_kappa", "plant_z",
                                           "own_ci95", "kappa_even", "kappa_odd", "z_eo", "se")})
            row["powered"] = st["M"] >= 2500
            row["recorded"] = {k: rc.get(k) for k in ("S", "M", "V", "kappa", "z", "z_cal", "plant_kappa",
                                                       "plant_z", "ci95", "kappa_even", "kappa_odd", "curves")}
            if "S" in rc:
                row["max_rel_diff_vs_recorded"] = max(
                    abs(row[k] - rc[k]) / max(abs(rc[k]), 1e-300) for k in
                    ("S", "M", "V", "kappa", "z", "z_cal", "plant_kappa", "plant_z", "kappa_even", "kappa_odd"))
            else:
                row["max_rel_diff_vs_recorded"] = None
                row["note"] = "recorded cell carries no statistics (class invalid); own descriptive values only"
            row["ci95_endpoint_diff_vs_recorded"] = (max(abs(row["own_ci95"][0] - ci_rec[0]),
                                                         abs(row["own_ci95"][1] - ci_rec[1]))
                                                     if ci_rec else None)
        cells.append(row)
    out["cells"] = cells

    powered = [c for c in cells if c.get("powered") and c["cls_own_ci"] != "invalid"]
    zc = [c["z_cal"] for c in powered]
    cal_mean = mean(zc)
    cal_sd = statistics.pstdev(zc)
    cal_pass = 0.75 <= cal_sd <= 1.25 and abs(cal_mean) <= 0.35
    valid = [c for c in cells if c["cls_own_ci"] in ("null", "flagged", "intermediate")]
    frac_valid = len(valid) / 45
    flagged = [c["cell"] for c in cells if c["cls_own_ci"] == "flagged"]
    all_valid_null = all(c["cls_own_ci"] == "null" for c in valid)
    if not cal_pass or frac_valid < 0.5:
        outcome = "O-INVALID"
    elif flagged:
        outcome = "O-PENDING-REPLICATION (flagged cells present; replication not modelled here)"
    elif all_valid_null and frac_valid >= 0.8:
        outcome = "O-NULL"
    else:
        outcome = "O-MIXED"
    headline = {"O-INVALID": "NOT_EVIDENCE", "O-NULL": "SUPPORT_SCOPED"}.get(outcome, "INCONCLUSIVE")
    out["reading"] = {"powered_cells": len(powered), "calibration": {"n": len(zc), "mean": cal_mean, "sd": cal_sd,
                                                                       "pass": cal_pass},
                      "fraction_valid": frac_valid, "flagged_cells": flagged, "outcome": outcome,
                      "headline": headline,
                      "classes_own": {k: sum(1 for c in cells if c["cls_own_ci"] == k) for k in
                                      sorted({c["cls_own_ci"] for c in cells})},
                      "class_disagreements_vs_recorded": [
                          (c["cell"], c["cls_recorded"], c["cls_own_ci"], c["cls_with_recorded_ci"]) for c in cells
                          if c["cls_own_ci"] != c["cls_recorded"] or c["cls_with_recorded_ci"] != c["cls_recorded"]],
                      "recorded": {k: analysis[k] for k in ("calibration", "fraction_valid", "flagged_cells",
                                                              "outcome", "headline", "powered_cells",
                                                              "largest_abs_z")}}

    # ---- the EV / KN-FIND headline numbers ----
    P = powered
    def arg(f, key=max):
        c = key(P, key=f)
        return c["cell"], f(c)
    dev = lambda c: abs(c["kappa"] - 1)
    zs = [c["z"] for c in P]
    sum_z2 = sum(z * z for z in zs)
    sum_zcal2 = sum(z * z for z in zc)
    sum_zeo2 = sum(c["z_eo"] ** 2 for c in P)
    weakest = min(P, key=lambda c: c["M"])
    rel_se_weak = weakest["se"] / weakest["M"]
    halfw = [(c["cell"], (c["recorded"]["ci95"][1] - c["recorded"]["ci95"][0]) / 2) for c in P]
    # log-kappa slope on log2 n per (bits, r), over valid cells (least squares)
    slopes = {}
    for bits in (20, 24, 28):
        for r in (1, 2, 3):
            pts = [(math.log2(c["n"]), math.log(c["kappa"])) for c in valid
                   if c["bits"] == bits and c["r"] == r and c.get("kappa", 0) > 0]
            if len(pts) >= 3:
                mx = mean([p[0] for p in pts]); my = mean([p[1] for p in pts])
                slopes[f"b{bits}-r{r}"] = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
    p_maxz = 1 - (1 - 2 * norm_sf(max(abs(z) for z in zs))) ** len(zs)
    p_any3 = 1 - (1 - 2 * norm_sf(3.0)) ** len(zs)
    # expected max |z| over 44 iid N(0,1) by numeric integration of 1 - F(x)^44, F the |Z| cdf
    def F(x):
        return 1 - 2 * norm_sf(x)
    steps = 20000
    e_max = sum((1 - F((i + 0.5) * 8 / steps) ** len(zs)) * 8 / steps for i in range(steps))
    out["headline_numbers"] = {
        "largest_abs_kappa_minus_1": arg(dev),
        "max_abs_kappa_minus_1_n_ge_1024": max(dev(c) for c in P if c["n"] >= 1024),
        "max_abs_kappa_minus_1_n_ge_2048": max(dev(c) for c in P if c["n"] >= 2048),
        "lowest_recorded_ci95_lower": min(((c["cell"], c["recorded"]["ci95"][0]) for c in P), key=lambda t: t[1]),
        "lowest_own_ci95_lower": min(((c["cell"], c["own_ci95"][0]) for c in P), key=lambda t: t[1]),
        "largest_abs_z": max(((c["cell"], c["z"]) for c in P), key=lambda t: abs(t[1])),
        "smallest_plant_kappa": min(((c["cell"], c["plant_kappa"]) for c in P), key=lambda t: t[1]),
        "smallest_plant_z": min(((c["cell"], c["plant_z"]) for c in P), key=lambda t: t[1]),
        "max_abs_logkappa_slope": max(abs(v) for v in slopes.values()), "slopes": slopes,
        "recorded_slopes": analysis["secondary_slope_logkappa_per_log2n"],
        "sum_z2": sum_z2, "z_mean": mean(zs), "z_pop_sd": statistics.pstdev(zs),
        "p_chi2_44_ge_sum_z2": chi2_sf_even(sum_z2, len(zs)),
        "cells_abs_z_gt_2": sorted(c["cell"] for c in P if abs(c["z"]) > 2),
        "cells_ci95_recorded_excluding_1": sorted(c["cell"] for c in P if not (c["recorded"]["ci95"][0] <= 1 <= c["recorded"]["ci95"][1])),
        "sum_z_cal2": sum_zcal2, "p_chi2_44_ge_sum_z_cal2": chi2_sf_even(sum_zcal2, len(zc)),
        "sum_z_evenodd2_own_definition": sum_zeo2,
        "weakest_cell": weakest["cell"], "weakest_M": weakest["M"],
        "mde_abs_z_gt_4": 4 * rel_se_weak,
        "mde_nonnull_95pct_normal_approx": 0.05 + 1.6448536 * rel_se_weak,
        "widest_ci95_half_width": max(halfw, key=lambda t: t[1]),
        "p_max_abs_z_ge_observed": p_maxz, "p_any_abs_z_gt_3": p_any3, "expected_max_abs_z_44": e_max,
        "n_cells_abs_z_gt_3": sum(1 for z in zs if abs(z) > 3),
    }

    # ---- EV-PFDR-07d608 per-cell table (5 decimals) against analysis.json ----
    try:
        import yaml  # noqa: PLC0415  (only to parse the ledger record)
        ev = yaml.safe_load(open(ev_p, encoding="utf-8"))["evidence"]
        table = ev["obstruction"]["value"]["cells"]
        mism = []
        for row in table:
            rc = rec_cells[row["cell"]]
            if row["kappa"] is None:
                if rc["cls"] != "invalid":
                    mism.append((row["cell"], "null row but recorded class", rc["cls"]))
                continue
            if round(rc["kappa"], 5) != row["kappa"] or [round(x, 5) for x in rc["ci95"]] != row["ci95"] \
                    or rc["curves"] != row["curves"]:
                mism.append((row["cell"], row, {"kappa": rc["kappa"], "ci95": rc["ci95"], "curves": rc["curves"]}))
        out["ev_table_vs_analysis"] = {"rows": len(table), "mismatches": mism}
    except Exception as exc:  # pragma: no cover
        out["ev_table_vs_analysis"] = {"error": repr(exc)}

    with open(out_p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    hn = out["headline_numbers"]
    print(json.dumps({"census": {k: out["census"][k] for k in out["census"] if k != "degenerate"},
                      "reading": {k: v for k, v in out["reading"].items() if k != "recorded"},
                      "recorded_reading": out["reading"]["recorded"],
                      "max_rel_diff_any_cell": max((c.get("max_rel_diff_vs_recorded") or 0) for c in cells),
                      "max_ci95_endpoint_diff": max((c.get("ci95_endpoint_diff_vs_recorded") or 0) for c in cells),
                      "headline_numbers": hn, "ev_table": out["ev_table_vs_analysis"]}, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1:])
