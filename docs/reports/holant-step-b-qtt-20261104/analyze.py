#!/usr/bin/env python3
"""Frozen analysis for holant step (b'). Reads rows.jsonl from qtt_rank.py, applies the
preregistered decision rule, writes verdict.json. Primary metric: interleaved r_max.
Rule (protocol decision_rule):
  validity  P: LOG r_max < min(null r_max) on every curve with L >= 8   (detector sees structure)
            AA: |median(stream0) - median(stream1)| <= IQR(pooled null) on every curve with L >= 8
  SIGNAL  : X r_max < min(null) (empirical one-sided p = 0.01) on all curves with L >= 8,
            and X r_max <= 0.75 * median(null) on every curve with L == max size
  NULL    : X r_max inside the null's central 90% (5th..95th percentile) on >= 7 of the 9 curves with L >= 8
  else INCONCLUSIVE; any failed validity check makes the verdict INVALID_CONTROLS.
"""
import json, sys, numpy as np
from collections import defaultdict

def main(rows_path, out_path, metric_order="interleaved"):
    rows = [json.loads(l) for l in open(rows_path)]
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[(r["L"], r["curve_index"])][r["arm"]].append(r)
    per, Lmax = [], max(k[0] for k in by)
    for (L, ci), arms in sorted(by.items()):
        nul = np.array([r[metric_order]["r_max"] for r in arms["N"]])
        s0 = np.array([r[metric_order]["r_max"] for r in arms["N"] if r["stream"] == 0])
        s1 = np.array([r[metric_order]["r_max"] for r in arms["N"] if r["stream"] == 1])
        x = arms["X"][0][metric_order]["r_max"]; lg = arms["LOG"][0][metric_order]["r_max"]
        sh = arms["SH"][0][metric_order]["r_max"]
        q5, q25, q50, q75, q95 = np.percentile(nul, [5, 25, 50, 75, 95])
        per.append(dict(L=L, curve_index=ci, p=arms["X"][0]["p"], n=arms["X"][0]["n"],
            X=x, LOG=lg, SH=sh, null_min=int(nul.min()), null_q5=float(q5), null_median=float(q50),
            null_q95=float(q95), null_max=int(nul.max()), null_draws=int(nul.size),
            p_one_sided=float((1 + (nul <= x).sum()) / (1 + nul.size)),
            aa_median_diff=float(abs(np.median(s0) - np.median(s1))), null_iqr=float(q75 - q25),
            X_over_null_median=float(x / q50)))
    big = [c for c in per if c["L"] >= 8]
    pos_ok = all(c["LOG"] < c["null_min"] for c in big)
    aa_ok = all(c["aa_median_diff"] <= c["null_iqr"] for c in big)
    signal = all(c["X"] < c["null_min"] for c in big) and \
             all(c["X"] <= 0.75 * c["null_median"] for c in per if c["L"] == Lmax)
    inside = sum(c["null_q5"] <= c["X"] <= c["null_q95"] for c in big)
    verdict = "INVALID_CONTROLS" if not (pos_ok and aa_ok) else \
              "SIGNAL" if signal else "NULL" if inside >= 7 else "INCONCLUSIVE"
    out = dict(metric=f"{metric_order}.r_max", verdict=verdict, positive_control_ok=pos_ok,
               aa_ok=aa_ok, curves_inside_null_90=inside, curves_L_ge_8=len(big), per_curve=per)
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "per_curve"}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or []))
