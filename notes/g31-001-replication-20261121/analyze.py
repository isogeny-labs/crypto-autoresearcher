"""analyze.py -- STEP 3: frozen analysis.  No parameter is chosen here.

Computes, per cell (bits x arm x m x curve): z_c = (r_x - mean_j r_j)/sd_j for
both nulls; per cell across the 10 curves: mean z, cell_z = mean/(sd/sqrt(10))
with t_9 p-value, sign consistency, fraction-unit effect + 95% CI, MDE,
achieved power.  Holm over the frozen family.  Then the (pre-registered)
descriptive characterisation of the informative cells.
"""
import json
import math

import numpy as np
from scipy import stats

R = json.load(open("results.json"))
FROZEN = json.load(open("frozen_config.json"))
ALPHA = 0.05
M_FAM = len(FROZEN["predicted_cells"])          # 8 designed cells
TESTABLE = {(c["bits"], c["arm"], c["m"]) for c in FROZEN["predicted_cells"]
            if c["testable"]}
KEYS = sorted({(c["bits"], c["arm"], c["m"]) for c in R["cells"]})
out = dict(frozen_utc=R["frozen_utc"], run_start=R["run_start"],
           run_end=R["run_end"], alpha=ALPHA, family_size=M_FAM,
           testable=sorted(TESTABLE), cells=[])


def holm(pv):
    m = len(pv)
    order = sorted(range(m), key=lambda i: pv[i])
    adj = [0.0] * m
    prev = 0.0
    for rank, i in enumerate(order):
        adj[i] = min(1.0, max(prev, (m - rank) * pv[i]))
        prev = adj[i]
    return adj


def zscore(d, sd):
    return d / sd if sd > 0 else 0.0


for key in KEYS:
    bits, arm, m = key
    cs = [c for c in R["cells"] if (c["bits"], c["arm"], c["m"]) == key]
    cs.sort(key=lambda c: c["slot"])
    row = dict(bits=bits, arm=arm, m=m,
               testable=key in TESTABLE,
               frac_pred_mean=float(np.mean([c["frac_pred"] for c in cs])),
               b=[c["b"] for c in cs], n=cs[0]["n"],
               lam_ordered_mean=float(np.mean([c["lam_ordered"] for c in cs])),
               frac_x=[c["x"]["frac"] for c in cs],
               mean_r_x=[c["x"]["mean_r"] for c in cs],
               mean_r_pred=float(np.mean([c["b"] ** m / c["n"] for c in cs])),
               nulls={})
    for kind in ("symmetric", "uniform"):
        ds, zs, sds, mrs, signs = [], [], [], [], []
        for c in cs:
            fr = np.array(c["nulls"][kind]["fracs"])
            mu, sd = fr.mean(), fr.std(ddof=1)
            d = c["x"]["frac"] - mu
            ds.append(d)
            sds.append(sd)
            zs.append(zscore(d, sd))
            mrs.append(c["x"]["mean_r"] - np.mean(c["nulls"][kind]["mean_rs"]))
            signs.append(1 if d > 0 else (-1 if d < 0 else 0))
        ds, zs, sds, mrs = map(np.array, (ds, zs, sds, mrs))
        # calibrated per-curve z from the 50 null draws themselves
        zc = []
        for c in cs:
            fr = np.array(c["nulls"][kind]["fracs"])
            for j in range(len(fr)):
                others = np.delete(fr, j)
                zc.append(zscore(fr[j] - others.mean(), others.std(ddof=1)))
        zc = np.array(zc)
        ncur = len(zs)
        mean_z = float(zs.mean())
        sd_z = float(zs.std(ddof=1))
        cellz = mean_z / (sd_z / math.sqrt(ncur)) if sd_z > 0 else 0.0
        p = float(2 * stats.t.sf(abs(cellz), ncur - 1))
        se_d = ds.std(ddof=1) / math.sqrt(ncur)
        tcrit = float(stats.t.ppf(1 - ALPHA / 2, ncur - 1))
        np5 = int((np.array(signs) > 0).sum())
        nm5 = int((np.array(signs) < 0).sum())
        row["nulls"][kind] = dict(
            mean_frac=float(np.mean([np.mean(c["nulls"][kind]["fracs"]) for c in cs])),
            mean_sd_null=float(sds.mean()),
            d_mean=float(ds.mean()), d_sd=float(ds.std(ddof=1)),
            d_ci=[float(ds.mean() - tcrit * se_d), float(ds.mean() + tcrit * se_d)],
            z=[float(z) for z in zs], mean_z=mean_z, sd_z=sd_z, cell_z=float(cellz),
            p=p, sign_pos=np5, sign_neg=nm5,
            sign_consistency=max(np5, nm5),
            mean_dr=float(mrs.mean()),
            null_zdist_abs_ge_2_5=float((np.abs(zc) >= 2.5).mean()),
            null_zdist_sd=float(zc.std(ddof=1)),
        )
    out["cells"].append(row)

# ------------------------------------------------------------ Holm + verdict
for kind in ("symmetric", "uniform"):
    pv = [c["nulls"][kind]["p"] if c["testable"] else 1.0 for c in out["cells"]]
    adj = holm(pv)
    for c, a in zip(out["cells"], adj):
        c["nulls"][kind]["p_holm8"] = float(a)
    # secondary: Holm over the 4 testable cells only
    idx = [i for i, c in enumerate(out["cells"]) if c["testable"]]
    adj2 = holm([out["cells"][i]["nulls"][kind]["p"] for i in idx])
    for i, a in zip(idx, adj2):
        out["cells"][i]["nulls"][kind]["p_holm4"] = float(a)


def verdict(kind, holm_key):
    passers = [c for c in out["cells"]
               if c["testable"] and abs(c["nulls"][kind]["cell_z"]) >= 2.5
               and c["nulls"][kind][holm_key] < ALPHA
               and c["nulls"][kind]["sign_consistency"] >= 7]
    return passers


for kind in ("symmetric", "uniform"):
    out[f"passers_{kind}_holm8"] = [
        f"{c['bits']}/{c['arm']}/m={c['m']}" for c in verdict(kind, "p_holm8")]
    out[f"passers_{kind}_holm4"] = [
        f"{c['bits']}/{c['arm']}/m={c['m']}" for c in verdict(kind, "p_holm4")]

# ------------------------------------------------------------------- MDE etc.
crit8 = float(stats.t.ppf(1 - ALPHA / (2 * M_FAM), 9))
crit4 = float(stats.t.ppf(1 - ALPHA / (2 * 4), 9))
pw = float(stats.t.ppf(0.8, 9))
out["mde"] = dict(t_crit_holm8=crit8, t_crit_holm4=crit4, t_pow80=pw,
                  mde_mean_z_holm8=(crit8 + pw) / math.sqrt(10),
                  mde_mean_z_holm4=(crit4 + pw) / math.sqrt(10),
                  per_cell={})
for c in out["cells"]:
    if not c["testable"]:
        continue
    for kind in ("symmetric", "uniform"):
        n = c["nulls"][kind]
        se = n["d_sd"] / math.sqrt(10)
        mde = (crit8 + pw) * se
        # achieved power at the observed effect (noncentral t)
        nc = n["d_mean"] / se if se > 0 else 0.0
        power = float(1 - stats.nct.cdf(crit8, 9, nc) + stats.nct.cdf(-crit8, 9, nc))
        n["se_frac"] = float(se)
        n["mde_frac"] = float(mde)
        n["mde_rel_to_null"] = float(mde / n["mean_frac"])
        n["power_at_observed"] = power
        if kind == "symmetric":
            out["mde"]["per_cell"][f"{c['bits']}/{c['arm']}/m={c['m']}"] = dict(
                se_frac=float(se), mde_frac=float(mde),
                mde_rel=float(mde / n["mean_frac"]), power=power)

json.dump(out, open("analysis.json", "w"), indent=1)

# pooled informative-cell summary (4 cells x 10 curves = 40 curve-cells)
for kind in ("symmetric", "uniform"):
    zs = np.array([z for c in out["cells"] if c["testable"]
                   for z in c["nulls"][kind]["z"]])
    pos = int((zs > 0).sum())
    neg = int((zs < 0).sum())
    out[f"pooled_{kind}"] = dict(
        n=int(zs.size), mean_z=float(zs.mean()), sd_z=float(zs.std(ddof=1)),
        cell_z=float(zs.mean() / (zs.std(ddof=1) / math.sqrt(zs.size))),
        p=float(2 * stats.t.sf(abs(zs.mean() / (zs.std(ddof=1) / math.sqrt(zs.size))),
                               zs.size - 1)),
        pos=pos, neg=neg,
        sign_test_p=float(2 * stats.binom.sf(max(pos, neg) - 1, zs.size, 0.5)))
for kind in ("symmetric", "uniform"):
    for c in out["cells"]:
        if c["testable"]:
            s = c["nulls"][kind]
            k = max(s["sign_pos"], s["sign_neg"])
            s["sign_test_p"] = float(2 * stats.binom.sf(k - 1, 10, 0.5))
json.dump(out, open("analysis.json", "w"), indent=1)

# --------------------------------------------------------------------- report
def fmt(x, p=4):
    return f"{x:.{p}f}"


print(f"frozen {R['frozen_utc']}  run {R['run_start']} .. {R['run_end']}")
print(f"family = {M_FAM} cells, testable = {sorted(TESTABLE)}")
print()
hdr = ("cell            b      pred    frac_x   nullS    sd    z_S  cellZ_S pholm8 nS+/- |"
       " frac_U   z_U  cellZ_U pholm8 nU+/- | d(pp)  CI95(pp) | gapU-S")
print(hdr)
for c in out["cells"]:
    s, u = c["nulls"]["symmetric"], c["nulls"]["uniform"]
    print(f"{c['bits']}/{c['arm']}/m{c['m']}   "
          f"{min(c['b'])}-{max(c['b'])}  {c['frac_pred_mean']:.3f}  "
          f"{np.mean(c['frac_x']):.4f}  {s['mean_frac']:.4f}  {s['mean_sd_null']:.4f} "
          f"{s['mean_z']:+.2f} {s['cell_z']:+.2f} {s['p_holm8']:.4f} {s['sign_pos']}/{s['sign_neg']} | "
          f"{u['mean_frac']:.4f} {u['mean_z']:+.2f} {u['cell_z']:+.2f} {u['p_holm8']:.4f} "
          f"{u['sign_pos']}/{u['sign_neg']} | "
          f"{100*s['d_mean']:+.2f} [{100*s['d_ci'][0]:+.2f},{100*s['d_ci'][1]:+.2f}] | "
          f"{100*(u['mean_frac']-s['mean_frac']):+.2f}")
print()
print("PASSERS (|cell_z|>=2.5 & Holm & signs>=7):")
print("  symmetric (PRIMARY) holm8:", out["passers_symmetric_holm8"],
      " holm4:", out["passers_symmetric_holm4"])
print("  uniform   (secondary) holm8:", out["passers_uniform_holm8"],
      " holm4:", out["passers_uniform_holm4"])
print()
print("POOLED over the 4 informative cells (40 curve-cells):")
for kind in ("symmetric", "uniform"):
    p = out[f"pooled_{kind}"]
    print(f"  {kind}: mean z={p['mean_z']:+.3f} sd={p['sd_z']:.2f} "
          f"pooled z={p['cell_z']:+.2f} p={p['p']:.2e} "
          f"signs +{p['pos']}/-{p['neg']} sign-test p={p['sign_test_p']:.2e}")
print("  per-cell sign tests (symmetric):",
      {f"{c['bits']}/{c['arm']}/m{c['m']}": round(c['nulls']['symmetric'].get('sign_test_p', 1), 4)
       for c in out['cells'] if c['testable']})
print()
print("MDE (80% power, family 8, t9): mean(z) =", round(out["mde"]["mde_mean_z_holm8"], 3))
for k, v in out["mde"]["per_cell"].items():
    print(f"  {k}: SE={100*v['se_frac']:.2f}pp  MDE={100*v['mde_frac']:.2f}pp "
          f"({100*v['mde_rel']:.1f}% of null)  power@obs={v['power']:.2f}")
print()
print("CALIBRATION: fraction of the 50 null draws with |z'|>=2.5 (should be ~0.01-0.05)")
for c in out["cells"]:
    if c["testable"]:
        s = c["nulls"]["symmetric"]
        print(f"  {c['bits']}/{c['arm']}/m{c['m']}: S={s['null_zdist_abs_ge_2_5']:.2f} "
              f"(sd of z'={s['null_zdist_sd']:.2f})  U={c['nulls']['uniform']['null_zdist_abs_ge_2_5']:.2f}")
print()
print("TUPLE SUPPLY (mean_r_x - mean_r_null, as fraction of predicted b^m/n):")
for c in out["cells"]:
    s = c["nulls"]["symmetric"]
    print(f"  {c['bits']}/{c['arm']}/m{c['m']}: pred {c['mean_r_pred']:.2f} "
          f"x {np.mean(c['mean_r_x']):.2f} d={s['mean_dr']:+.2f} "
          f"({100*s['mean_dr']/c['mean_r_pred']:+.1f}%)")
