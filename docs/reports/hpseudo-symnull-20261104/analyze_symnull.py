#!/usr/bin/env python3
"""Frozen analysis for the H-PSEUDO negation-matched null re-read.
Per curve: R_sym = C_EC / mean(N_sym draws at that curve's N); u_sym = mid-rank percentile of C_EC in its N_sym draws.
Per rung: mean R_sym over the 8 curves, 95% percentile bootstrap CI over curves (10000 resamples, seed 20261104).
Validity (all required):
  V1 replication: mean of the 40 asymmetric draws at N_rep within 2% of the recorded C_null_mean, every rung;
  V2 positive control: planted symmetric AP C >= 3 x the max N_sym draw of that rung, every rung;
  V3 replay: every EC_replay C equals the recorded C_EC within 1e-5 relative, and every replayed F is negation-closed;
  V4 A/A: per rung, |mean(even draws) - mean(odd draws)| / mean <= 2% over the rung's pooled N_sym draws (normalised per curve).
Decisive cells: the out-of-sample curves (curve_index 8..19) at bits 20 and 22; the 8 R_mean curves per rung are calibration.
Verdict: EXPLAINED iff at both out-of-sample rungs the CI of mean R_sym contains 1 and |mean R_sym - 1| <= 0.05;
         RESIDUAL iff at both out-of-sample rungs mean R_sym > 1.05 and the CI excludes 1;  else INCONCLUSIVE;
         INVALID_CONTROLS if any of V1-V4 fails. Descriptive: R_asym_recorded (= recorded R_mean) beside R_sym."""
import json, sys, numpy as np
from collections import defaultdict
def main(rows_path, out_path):
    rows = [json.loads(l) for l in open(rows_path)]
    ec = {r["instance_id"]: r for r in rows if r["arm"] == "EC_recorded"}
    sym = defaultdict(list)
    for r in rows:
        if r["arm"] == "N_sym": sym[r["instance_id"]].append((r["replicate"], r["C"]))
    per = []
    for i, e in ec.items():
        d = np.array([c for _, c in sorted(sym[i])]); m = d.mean()
        per.append(dict(bits=e["bits"], curve_index=e["curve_index"], N=e["N"], C_EC=e["C"], sample=e["sample"], sym_mean=float(m), sym_sd=float(d.std(ddof=1)),
                        R_sym=float(e["C"] / m), u_sym=float(((d < e["C"]).sum() + 0.5 * (d == e["C"]).sum()) / d.size),
                        even_mean=float(d[0::2].mean() / m), odd_mean=float(d[1::2].mean() / m), sym_max=float(d.max())))
    rng = np.random.default_rng(20261104); rung = {}
    raw_rmean = {}
    for b in sorted({p["bits"] for p in per}):
        R = np.array([p["R_sym"] for p in per if p["bits"] == b and p["sample"] == "calibration"])
        boots = [rng.choice(R, R.size).mean() for _ in range(10000)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        ev = [p["even_mean"] for p in per if p["bits"] == b]; od = [p["odd_mean"] for p in per if p["bits"] == b]
        rung[b] = dict(mean_R_sym=float(R.mean()), ci95=[float(lo), float(hi)], n=int(R.size),
                       aa_rel_diff=float(abs(np.mean(ev) - np.mean(od))), max_sym=max(p["sym_max"] for p in per if p["bits"] == b),
                       mean_u_sym=float(np.mean([p["u_sym"] for p in per if p["bits"] == b])))
    asym = defaultdict(list); rec = {}
    for r in rows:
        if r["arm"] == "N_asym": asym[r["bits"]].append(r["C"]); rec[r["bits"]] = r["recorded_C_null_mean"]
    planted = {r["bits"]: r["C"] for r in rows if r["arm"] == "planted_sym_AP"}
    replay = [r for r in rows if r["arm"] == "EC_replay"]
    V1 = {b: abs(np.mean(v) / rec[b] - 1) for b, v in asym.items()}
    V2 = {b: planted[b] / rung[b]["max_sym"] for b in rung}
    v1 = all(x <= 0.02 for x in V1.values()); v2 = all(x >= 3 for x in V2.values())
    v3 = bool(replay) and all(abs(r["C"] / r["recorded"] - 1) <= 1e-5 and r["neg_closed"] for r in replay)
    v4 = all(r["aa_rel_diff"] <= 0.02 for r in rung.values())
    valid = v1 and v2 and v3 and v4
    oos = {}
    for b in sorted({p["bits"] for p in per if p["sample"] == "out_of_sample"}):
        R = np.array([p["R_sym"] for p in per if p["bits"] == b and p["sample"] == "out_of_sample"])
        boots = [rng.choice(R, R.size).mean() for _ in range(10000)]; lo, hi = np.percentile(boots, [2.5, 97.5])
        oos[b] = dict(mean_R_sym=float(R.mean()), ci95=[float(lo), float(hi)], n=int(R.size))
    expl = all(r["ci95"][0] <= 1 <= r["ci95"][1] and abs(r["mean_R_sym"] - 1) <= 0.05 for r in oos.values())
    resid = all(r["mean_R_sym"] > 1.05 and r["ci95"][0] > 1 for r in oos.values())
    verdict = "INVALID_CONTROLS" if not valid else "EXPLAINED" if expl else "RESIDUAL" if resid else "INCONCLUSIVE"
    out = dict(verdict=verdict, decisive_out_of_sample=oos, calibration_rungs=rung, validity=dict(V1_replication_rel_err=V1, V2_planted_over_symmax=V2, V3_replay_ok=v3,
               V4_aa_ok=v4, replay=[{k: r[k] for k in ("bits", "curve_index", "N", "C", "recorded", "neg_closed")} for r in replay]),
               per_curve=sorted(per, key=lambda p: (p["bits"], p["curve_index"])))
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({"verdict": verdict, "oos": {b: (round(r["mean_R_sym"], 3), [round(x, 3) for x in r["ci95"]]) for b, r in oos.items()}, "calibration": {b: (round(r["mean_R_sym"], 3), [round(x, 3) for x in r["ci95"]]) for b, r in rung.items()},
                      "V1": {b: round(x, 4) for b, x in V1.items()}, "V2": {b: round(x, 2) for b, x in V2.items()}, "V3": v3, "V4": v4}))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
