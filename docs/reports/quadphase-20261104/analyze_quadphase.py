#!/usr/bin/env python3
"""Frozen analysis, quadratic-phase test. Decisive curves: L in {12, 13, 14} (9 curves); L = 16 descriptive.
Per curve: u = mid-rank percentile of Q_EC among its N_sym draws; above_max = Q_EC > max(N_sym).
Validity: planted Q >= 3 x max(N_sym) on every curve, and the planted argmax alpha equals alpha0 (or N - alpha0);
          A/A: |mean(even draws) - mean(odd draws)| / mean <= 3% pooled per size.
SIGNAL iff above_max on >= 2 of 3 curves at >= 2 of the 3 decisive sizes; NULL iff u in [0.05, 0.95] on >= 8 of 9
decisive curves; else INCONCLUSIVE; INVALID_CONTROLS if validity fails."""
import json, sys, numpy as np
from collections import defaultdict
def main(rows_path, out_path):
    rows = [json.loads(l) for l in open(rows_path)]; by = defaultdict(lambda: defaultdict(list))
    for r in rows: by[r["instance_id"]][r["arm"]].append(r)
    per = []
    for iid, a in by.items():
        nul = np.array([r["Q"] for r in sorted(a["N_sym"], key=lambda r: r["replicate"])]); ec = a["EC"][0]; pl = a["planted"][0]
        per.append(dict(instance=iid, L=ec["L"], curve_index=ec["curve_index"], N=ec["N"], Q_EC=ec["Q"], alpha_EC=ec["alpha"],
            null_mean=float(nul.mean()), null_max=float(nul.max()), u=float(((nul < ec["Q"]).sum() + 0.5*(nul == ec["Q"]).sum())/nul.size),
            above_max=bool(ec["Q"] > nul.max()), planted_Q=pl["Q"], planted_ratio=float(pl["Q"]/nul.max()),
            planted_alpha_ok=pl["alpha"] in (ec["alpha0"], ec["N"] - ec["alpha0"]) if "alpha0" in ec else None,
            even=float(nul[0::2].mean()), odd=float(nul[1::2].mean())))
    dec = [c for c in per if c["L"] in (12, 13, 14)]
    pos_ok = all(c["planted_ratio"] >= 3 and c["planted_alpha_ok"] for c in per)
    aa = {L: abs(np.mean([c["even"] for c in per if c["L"] == L]) - np.mean([c["odd"] for c in per if c["L"] == L])) /
             np.mean([c["null_mean"] for c in per if c["L"] == L]) for L in sorted({c["L"] for c in per})}
    aa_ok = all(v <= 0.03 for L, v in aa.items() if L in (12, 13, 14))
    sizes_hit = sum(sum(c["above_max"] for c in dec if c["L"] == L) >= 2 for L in (12, 13, 14))
    inside = sum(0.05 <= c["u"] <= 0.95 for c in dec)
    verdict = "INVALID_CONTROLS" if not (pos_ok and aa_ok) else "SIGNAL" if sizes_hit >= 2 else "NULL" if inside >= 8 else "INCONCLUSIVE"
    out = dict(verdict=verdict, positive_ok=pos_ok, aa_rel_diff=aa, decisive_inside_90=inside, sizes_with_2of3_above_max=sizes_hit,
               per_curve=sorted(per, key=lambda c: (c["L"], c["curve_index"])))
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("verdict", "positive_ok", "aa_rel_diff", "decisive_inside_90", "sizes_with_2of3_above_max")}))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
