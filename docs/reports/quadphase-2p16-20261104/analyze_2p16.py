#!/usr/bin/env python3
"""Frozen analysis. Validity: EC replay equals the recorded Q_EC within 1e-9; planted Q >= 3 x null max with argmax alpha in
{alpha0, N-alpha0}; A/A: two-sample means of even vs odd draws within 3%. u = mid-rank percentile of Q_EC among the 40 draws.
Verdict: EXCESS iff Q_EC > max of the 40 draws (one-sided p <= 1/41); NULL iff u <= 0.95; else BORDERLINE (0.95 < u, not above max)."""
import json, sys, numpy as np
def main(rows_path, out_path):
    rows = [json.loads(l) for l in open(rows_path)]
    ec = next(r for r in rows if r["arm"] == "EC"); pl = next(r for r in rows if r["arm"] == "planted")
    nul = np.array([r["Q"] for r in sorted((r for r in rows if r["arm"] == "N_sym"), key=lambda r: r["replicate"])])
    u = float(((nul < ec["Q"]).sum() + 0.5 * (nul == ec["Q"]).sum()) / nul.size)
    replay = abs(ec["Q"] - ec["recorded_Q_EC"]) <= 1e-9
    pos = pl["Q"] >= 3 * nul.max() and pl["alpha"] in (pl["alpha0"], ec["N"] - pl["alpha0"])
    aa = float(abs(nul[0::2].mean() - nul[1::2].mean()) / nul.mean()); aa_ok = aa <= 0.03
    valid = replay and pos and aa_ok
    verdict = "INVALID_CONTROLS" if not valid else "EXCESS" if ec["Q"] > nul.max() else "NULL" if u <= 0.95 else "BORDERLINE"
    out = dict(verdict=verdict, Q_EC=ec["Q"], u=u, null_mean=float(nul.mean()), null_max=float(nul.max()), null_sd=float(nul.std(ddof=1)),
               replay_ok=replay, planted_ratio=float(pl["Q"] / nul.max()), planted_alpha_ok=pl["alpha"] in (pl["alpha0"], ec["N"] - pl["alpha0"]), aa_rel=aa)
    json.dump(out, open(out_path, "w"), indent=1); print(json.dumps(out))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
