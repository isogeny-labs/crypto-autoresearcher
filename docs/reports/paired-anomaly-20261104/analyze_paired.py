#!/usr/bin/env python3
"""Frozen analysis. Primary: two-sided Mann-Whitney U (normal approximation with tie correction) between u of paired
ordinary curves (class D, from pick) and independently picked ordinary curves (class E).
  REPLICATED iff p < 0.01 and mean u(D) < mean u(E);  NOT_REPLICATED iff p >= 0.05;  else INCONCLUSIVE.
Validity: positive control u >= 0.95 on >= 90% of curves; A/A: |mean(stream0) - mean(stream1)|/mean <= 3% on >= 95% of curves.
Secondary (Bonferroni over 3): each weak class A, B, C vs E by Mann-Whitney; KS of each group's u against U(0,1)."""
import json, math, sys, numpy as np
def mwu(x, y):
    x, y = np.asarray(x), np.asarray(y); allv = np.concatenate([x, y]); n1, n2 = x.size, y.size
    order = allv.argsort(); ranks = np.empty(allv.size); ranks[order] = np.arange(1, allv.size + 1)
    for v in np.unique(allv):
        m = allv == v
        if m.sum() > 1: ranks[m] = ranks[m].mean()
    U = ranks[:n1].sum() - n1*(n1+1)/2; mu = n1*n2/2
    _, cnt = np.unique(allv, return_counts=True); N = n1 + n2
    sd = math.sqrt(n1*n2/12 * ((N+1) - (cnt**3 - cnt).sum()/(N*(N-1))))
    z = (U - mu) / sd; return float(U), float(z), float(math.erfc(abs(z)/math.sqrt(2)))
def ks_unif(u):
    u = np.sort(np.asarray(u)); n = u.size; d = max(np.max(np.arange(1, n+1)/n - u), np.max(u - np.arange(n)/n))
    lam = (math.sqrt(n) + 0.12 + 0.11/math.sqrt(n)) * d
    return float(d), float(min(1, max(0, 2*sum((-1)**(j-1)*math.exp(-2*j*j*lam*lam) for j in range(1, 101)))))
def main(rows_path, out_path):
    rows = [json.loads(l) for l in open(rows_path)]; g = lambda K: [r["I1_u"] for r in rows if r["cls"] == K]
    pos = float(np.mean([r["I1_pos_u"] >= 0.95 for r in rows]))
    aa = float(np.mean([abs(r["aa_ks_streams"][0] - r["aa_ks_streams"][1]) / np.mean(r["aa_ks_streams"]) <= 0.03 for r in rows]))
    valid = pos >= 0.9 and aa >= 0.95
    U, z, p = mwu(g("D"), g("E"))
    verdict = "INVALID_CONTROLS" if not valid else ("REPLICATED" if p < 0.01 and np.mean(g("D")) < np.mean(g("E")) else "NOT_REPLICATED" if p >= 0.05 else "INCONCLUSIVE")
    sec = {K: dict(zip(("U", "z", "p"), mwu(g(K), g("E"))), mean_u=float(np.mean(g(K))), n=len(g(K)), bonferroni_p=min(1.0, 3*mwu(g(K), g("E"))[2])) for K in "ABC"}
    ks = {K: dict(zip(("D", "p"), ks_unif(g(K)))) for K in "ABCDE"}
    out = dict(verdict=verdict, primary=dict(U=U, z=z, p=p, mean_u_D=float(np.mean(g("D"))), mean_u_E=float(np.mean(g("E"))), n_D=len(g("D")), n_E=len(g("E"))),
               controls=dict(positive_frac=pos, aa_frac=aa, valid=valid), weak_vs_E=sec, ks_uniform=ks)
    json.dump(out, open(out_path, "w"), indent=1); print(json.dumps({k: out[k] for k in ("verdict", "primary", "controls")}))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
