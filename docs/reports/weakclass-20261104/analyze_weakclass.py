#!/usr/bin/env python3
"""Frozen analysis, weak-class calibration. For each instrument I in {I1, I2, I3} and weak class K in {A, B, C}:
  at each size where I runs, the class 'is extreme' iff all 3 class curves have u <= 0.05, or all have u >= 0.95;
  DETECTS iff extreme in the same direction at >= 2 sizes (I3: at its single size L = 10), and at those sizes the
  3 paired ordinary curves are not all extreme in that direction; otherwise BLIND.
Validity per instrument: positive control u >= 0.95 or <= 0.05 (instrument-appropriate direction: I1 high, I2 low,
  I3 low) on >= 90% of all curves; A/A (I1 even/odd null means) within 5% on every curve. Instruments failing
  validity are reported INVALID, not BLIND. Descriptive: per-class mean u and the paired difference u_K - u_D."""
import json, sys, numpy as np
from collections import defaultdict
def main(rows_path, out_path):
    rows = [json.loads(l) for l in open(rows_path)]
    res = {}; valid = {}
    for I, posdir in (("I1", "high"), ("I2", "low"), ("I3", "low")):
        rI = [r for r in rows if f"{I}_u" in r]
        pos = [r[f"{I}_pos_u"] for r in rI]
        ok = np.mean([(u >= 0.95) if posdir == "high" else (u <= 0.05) for u in pos]) >= 0.9 if pos else False
        if I == "I1": ok = ok and all(r["aa_I1"] <= 0.05 for r in rI)
        valid[I] = bool(ok); sizes = sorted({r["L"] for r in rI}); res[I] = {}
        for K in ("A", "B", "C"):
            ext = {}
            for L in sizes:
                u = [r[f"{I}_u"] for r in rI if r["cls"] == K and r["L"] == L]; d = [r[f"{I}_u"] for r in rI if r.get("pair") == K and r["L"] == L]
                lo = len(u) == 3 and all(x <= 0.05 for x in u); hi = len(u) == 3 and all(x >= 0.95 for x in u)
                dlo = len(d) == 3 and all(x <= 0.05 for x in d); dhi = len(d) == 3 and all(x >= 0.95 for x in d)
                ext[L] = "low" if lo and not dlo else "high" if hi and not dhi else None
            need = 1 if len(sizes) == 1 else 2
            dirs = [v for v in ext.values() if v]; det = any(dirs.count(x) >= need for x in ("low", "high"))
            pairs = []
            for r in rI:
                if r["cls"] == K:
                    d = [q for q in rI if q.get("pair") == K and q["p"] == r["p"] and q["L"] == r["L"]]
                    if d: pairs.append(r[f"{I}_u"] - d[0][f"{I}_u"])
            res[I][K] = dict(verdict=("INVALID" if not valid[I] else "DETECTS" if det else "BLIND"), extreme_by_size=ext,
                             mean_u=float(np.mean([r[f"{I}_u"] for r in rI if r["cls"] == K])), mean_paired_diff=float(np.mean(pairs)) if pairs else None)
    out = dict(validity=valid, table=res)
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({I: {K: v["verdict"] for K, v in t.items()} for I, t in res.items()}), json.dumps(valid))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
