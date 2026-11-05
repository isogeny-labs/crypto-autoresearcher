#!/usr/bin/env python3
"""Frozen analysis for the anomalous-curve follow-up.
Per curve and metric m in {log2_params (primary), r_max (secondary)}:
  u_X   = mid-rank percentile of X among its 99 null draws  ((#null < X) + 0.5 #null == X) / 99
  u_LOG = same for LOG;  u_AA = percentile of null draw 0 among draws 1..98 (A/A).
Test: stratified (within-prime) label permutation, 9999 permutations, seed fixed below, one-sided:
  statistic = mean u_X(ordinary) - mean u_X(anomalous)   (positive if anomalous curves are lower).
Validity: mean u_LOG < 0.05 in each group; pooled mean u_AA in [0.35, 0.65].
Verdict (primary): EFFECT iff p_perm < 0.01 and mean u_X(anomalous) < 0.25; NULL iff p_perm >= 0.05;
else INCONCLUSIVE; INVALID_CONTROLS if validity fails. Motivating curve reported, never tested.
"""
import json, sys, numpy as np
from collections import defaultdict

def pct(v, null):
    null = np.asarray(null); return float(((null < v).sum() + 0.5 * (null == v).sum()) / null.size)

def main(rows_path, out_path, metric="log2_params", seed=20261104):
    cur = defaultdict(lambda: {"N": []})
    for l in open(rows_path):
        r = json.loads(l); k = (r["p"], r["a"], r["b"])
        c = cur[k]; c["group"] = r["group"]
        if r["arm"] == "N": c["N"].append((r["draw"], r[metric]))
        else: c[r["arm"]] = r[metric]
    per = []
    for (p, a, b), c in sorted(cur.items()):
        null = [v for _, v in sorted(c["N"])]
        per.append(dict(p=p, a=a, b=b, group=c["group"], X=c["X"], LOG=c["LOG"],
                        u_X=pct(c["X"], null), u_LOG=pct(c["LOG"], null), u_AA=pct(null[0], null[1:]),
                        null_median=float(np.median(null))))
    test = [c for c in per if c["group"] in ("anomalous", "ordinary")]
    def stat(rows, labels):
        a = [r["u_X"] for r, l in zip(rows, labels) if l == "anomalous"]
        o = [r["u_X"] for r, l in zip(rows, labels) if l == "ordinary"]
        return float(np.mean(o) - np.mean(a))
    labels = [c["group"] for c in test]; obs = stat(test, labels)
    strata = defaultdict(list)
    for i, c in enumerate(test): strata[c["p"]].append(i)
    rng = np.random.default_rng(seed); ge = 0; B = 9999
    for _ in range(B):
        lab = list(labels)
        for idx in strata.values():
            perm = rng.permutation([labels[i] for i in idx])
            for i, l in zip(idx, perm): lab[i] = l
        ge += stat(test, lab) >= obs - 1e-12
    p_perm = (1 + ge) / (1 + B)
    ga = lambda g, k: float(np.mean([c[k] for c in test if c["group"] == g]))
    valid = ga("anomalous", "u_LOG") < 0.05 and ga("ordinary", "u_LOG") < 0.05 and \
            0.35 <= float(np.mean([c["u_AA"] for c in test])) <= 0.65
    mA = ga("anomalous", "u_X")
    verdict = "INVALID_CONTROLS" if not valid else ("EFFECT" if (p_perm < 0.01 and mA < 0.25)
              else "NULL" if p_perm >= 0.05 else "INCONCLUSIVE")
    out = dict(metric=metric, verdict=verdict, p_perm=p_perm, statistic=obs,
               n_anomalous=sum(l == "anomalous" for l in labels), n_ordinary=sum(l == "ordinary" for l in labels),
               mean_uX_anomalous=mA, mean_uX_ordinary=ga("ordinary", "u_X"),
               mean_uLOG=[ga("anomalous", "u_LOG"), ga("ordinary", "u_LOG")],
               mean_uAA=float(np.mean([c["u_AA"] for c in test])), controls_valid=valid,
               motivating=[c for c in per if c["group"] == "motivating"], per_curve=per)
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_curve",)}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(sys.argv[3:4] or []))
