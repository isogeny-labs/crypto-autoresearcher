#!/usr/bin/env python3
"""Frozen analysis, low-degree rank experiment.
Decisive cells: arm 'rand' on instances whose monomial/candidate ratio >= 1.5 (the ratio-2 targets).
  F_L = fraction of those (instance, replicate) cells with full rank (rank == candidates), per size L.
Validity: null arm full (rank == min(C, #monomials)) in >= 95% of null cells; shift arm rank <= 3Dt+1 in every
  shift cell (Riemann-Roch bound for X_i = R + [a_i]P).
Verdict: HOLDS iff F_L >= 0.9 for every L; FAILS iff F_L <= 0.5 for L = 10 and L = 11; else MIXED;
  INVALID_CONTROLS if validity fails. Descriptive: deficits expected_generic - rank by arm, ratio band and size.
"""
import json, sys, numpy as np
from collections import defaultdict
def main(rows_path, out_path):
    rows = [json.loads(l) for l in open(rows_path)]
    ratio = lambda r: r["monomials"] / r["candidates"]
    dec = defaultdict(list)
    for r in rows:
        if r["arm"] == "rand" and ratio(r) >= 1.5: dec[r["L"]].append(r["full"])
    F = {L: float(np.mean(v)) for L, v in sorted(dec.items())}
    nulls = [r for r in rows if r["arm"] == "null"]
    null_ok = float(np.mean([r["rank"] == min(r["candidates"], r["monomials"]) for r in nulls]))
    shift_ok = all(r["rank"] <= 3 * r["D"] * r["t"] + 1 for r in rows if r["arm"] == "shift")
    valid = null_ok >= 0.95 and shift_ok
    verdict = "INVALID_CONTROLS" if not valid else ("HOLDS" if all(v >= 0.9 for v in F.values())
              else "FAILS" if F.get(10, 1) <= 0.5 and F.get(11, 1) <= 0.5 else "MIXED")
    band = lambda r: "<0.75" if ratio(r) < 0.75 else ("0.75-1.5" if ratio(r) < 1.5 else ">=1.5")
    desc = defaultdict(list)
    for r in rows: desc[(r["arm"], r["L"], band(r))].append(r["expected_generic"] - r["rank"])
    out = dict(verdict=verdict, full_rate_rand_ratio2=F, null_full_rate=null_ok, shift_within_bound=shift_ok,
               deficits={f"{a}|L{L}|{b}": dict(n=len(v), mean=float(np.mean(v)), max=int(max(v)), zero_frac=float(np.mean(np.array(v) == 0)))
                         for (a, L, b), v in sorted(desc.items())})
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("verdict", "full_rate_rand_ratio2", "null_full_rate", "shift_within_bound")}))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
