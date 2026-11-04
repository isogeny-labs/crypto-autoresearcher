#!/usr/bin/env python3
"""Frozen analysis for the I1 rerun.
A/A gate (calibrated): per curve, two-sample KS between null draws 0..99 and 100..199 (asymptotic p-value);
  gate passes iff the number of curves with p < 0.05 is <= the 99th percentile of Binomial(#curves, 0.05).
Positive control: planted u >= 0.95 on >= 90% of curves.
(a) Weak-class cells (classes A, B, C vs their paired D, sizes 10/12/14): DETECTS iff all 3 class curves are beyond the
  5-95% band in one direction at >= 2 sizes and the paired ordinary curves are not all extreme in that direction; else BLIND.
(b) Overdispersion (out of sample): among the extra ordinary curves (class E), X = #(u <= 0.05 or u >= 0.95);
  OVERDISPERSED iff P(Binomial(n_E, 0.10) >= X) < 0.01; else CALIBRATED. Direction split reported.
INVALID_CONTROLS if the gate or the positive control fails."""
import json, math, sys, numpy as np
def ks_p(a, b):
    a, b = np.sort(a), np.sort(b); allv = np.concatenate([a, b])
    d = np.max(np.abs(np.searchsorted(a, allv, side="right")/a.size - np.searchsorted(b, allv, side="right")/b.size))
    en = math.sqrt(a.size*b.size/(a.size+b.size)); lam = (en + 0.12 + 0.11/en) * d
    return float(min(1.0, max(0.0, 2*sum((-1)**(j-1)*math.exp(-2*j*j*lam*lam) for j in range(1, 101)))))
def binom_sf(k, n, p): return float(sum(math.comb(n, i)*p**i*(1-p)**(n-i) for i in range(k, n+1)))
def binom_q99(n, p):
    c = 0.0
    for k in range(n+1):
        c += math.comb(n, k)*p**k*(1-p)**(n-k)
        if c >= 0.99: return k
def main(rows_path, out_path):
    rows = [json.loads(l) for l in open(rows_path)]
    ks = [ks_p(np.array(r["null"][:100]), np.array(r["null"][100:])) for r in rows]
    rej = sum(p < 0.05 for p in ks); q99 = binom_q99(len(rows), 0.05); gate = rej <= q99
    pos = float(np.mean([r["I1_pos_u"] >= 0.95 for r in rows])); pos_ok = pos >= 0.9
    cells = {}
    for K in "ABC":
        ext = {}
        for L in (10, 12, 14):
            u = [r["I1_u"] for r in rows if r["cls"] == K and r["L"] == L]; d = [r["I1_u"] for r in rows if r.get("pair") == K and r["L"] == L]
            lo = len(u) == 3 and all(x <= 0.05 for x in u); hi = len(u) == 3 and all(x >= 0.95 for x in u)
            dlo = len(d) == 3 and all(x <= 0.05 for x in d); dhi = len(d) == 3 and all(x >= 0.95 for x in d)
            ext[L] = "low" if lo and not dlo else "high" if hi and not dhi else None
        dirs = [v for v in ext.values() if v]; det = any(dirs.count(x) >= 2 for x in ("low", "high"))
        cells[K] = dict(verdict="DETECTS" if det else "BLIND", extreme_by_size=ext, mean_u=float(np.mean([r["I1_u"] for r in rows if r["cls"] == K])))
    E = [r["I1_u"] for r in rows if r["cls"] == "E"]; X = sum(u <= 0.05 or u >= 0.95 for u in E)
    p_od = binom_sf(X, len(E), 0.10)
    od = dict(verdict="OVERDISPERSED" if p_od < 0.01 else "CALIBRATED", n=len(E), extreme=X, low=sum(u <= 0.05 for u in E), high=sum(u >= 0.95 for u in E),
              p_binomial=p_od, by_size={L: [round(r["I1_u"], 3) for r in rows if r["cls"] == "E" and r["L"] == L] for L in (10, 12, 14)})
    valid = gate and pos_ok
    out = dict(controls=dict(aa_rejections=rej, aa_q99=q99, aa_pass=gate, positive_frac=pos, positive_ok=pos_ok),
               weak_cells={K: (v if valid else dict(v, verdict="INVALID")) for K, v in cells.items()},
               overdispersion=(od if valid else dict(od, verdict="INVALID")))
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({"controls": out["controls"], "cells": {K: v["verdict"] for K, v in out["weak_cells"].items()},
                      "overdispersion": {k: out["overdispersion"][k] for k in ("verdict", "n", "extreme", "low", "high", "p_binomial")}}))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
