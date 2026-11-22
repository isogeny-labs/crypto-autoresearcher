"""run_replication.py -- STEP 2: the frozen measurement.  Reads
frozen_config.json only; re-derives nothing that could be tuned.

Per curve: 1000 targets (shared across arms, m, null draws).  Per cell
(curve x arm x m): x-window rate + 50 symmetric-null draws + 50 uniform-null
draws.  Writes results.json (incrementally).
"""
import json
import math
import time

import replib as R

F = json.load(open("frozen_config.json"))
assert "frozen_utc" in F and "curves" in F, "no frozen config"
RUN_START = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
MASTER = F["master_seed"]
N_NULL = F["n_null_draws"]
NT = F["n_targets_per_cell"]

logf = open("run.log", "w")
OUT = dict(frozen_utc=F["frozen_utc"], run_start=RUN_START, master_seed=MASTER,
           n_targets=NT, n_null_draws=N_NULL, curves=[], cells=[])


def L(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(f"{s}   [+{time.time()-T0:.1f}s]\n")
    logf.flush()


def save():
    json.dump(OUT, open("results.json", "w"), indent=1)


T0 = time.time()
L(f"run start {RUN_START}   (frozen {F['frozen_utc']})")

for c in F["curves"]:
    bits, slot = c["bits"], c["slot"]
    rec = R.make_curve(bits, slot)
    assert (rec["p"], rec["a"], rec["b"], rec["nE"], rec["j"]) == \
        (c["p"], c["a"], c["b"], c["nE"], c["j"]), "curve mismatch vs freeze"
    E, n, g = rec["E"], rec["n"], rec["g"]
    tab = R.log_table(E, n, g)
    trng = R.rng_for(MASTER, bits, slot, "targets")
    tlogs = [trng.randrange(1, n) for _ in range(NT)]
    n_distinct = len(set(tlogs))          # uniform draws may repeat; kept as frozen
    OUT["curves"].append(dict(bits=bits, slot=slot, p=c["p"], a=c["a"],
                              b=c["b"], nE=c["nE"], n=c["n"], j=c["j"],
                              cm=c["cm"], cofactor=c["cofactor"],
                              n_targets_distinct=n_distinct,
                              target_seed_tag=f"{MASTER}|{bits}|{slot}|targets"))
    for arm in ("N3", "N2"):
        N = math.isqrt(E.p) if arm == "N2" else int(round(E.p ** (1 / 3)))
        B = R.window_points(E, N)
        logs = [tab[P] for P in B]
        b = len(logs)
        assert b == c["arms"][arm]["b"]
        ss_x = R.sumset_size(logs, n)
        for m in (3, 4):
            lam_o = b ** m / n
            cvec, resid = R.counts(logs, n, m)
            ev = R.evaluate(cvec, tlogs)
            cell = dict(bits=bits, slot=slot, arm=arm, m=m, p=E.p, n=n, b=b, N=N,
                        lam_ordered=lam_o, lam_task=lam_o / math.factorial(m),
                        frac_pred=1 - math.exp(-lam_o / math.factorial(m)),
                        sumset_BB=ss_x, fft_resid=resid,
                        x=dict(dec=ev["dec"], nT=ev["nT"], frac=ev["frac"],
                               r_tot=ev["r_tot"], mean_r=ev["mean_r"],
                               r_max=ev["r_max"]),
                        nulls={})
            for kind in ("symmetric", "uniform"):
                fr, mr, ss, dec = [], [], [], []
                t1 = time.time()
                for j in range(N_NULL):
                    rng = R.rng_for(MASTER, bits, slot, arm, m, kind, j)
                    nl = R.null_logs(n, b, kind, rng)
                    c2, r2 = R.counts(nl, n, m)
                    e2 = R.evaluate(c2, tlogs)
                    fr.append(e2["frac"])
                    mr.append(e2["mean_r"])
                    dec.append(e2["dec"])
                    ss.append(R.sumset_size(nl, n))
                cell["nulls"][kind] = dict(fracs=fr, mean_rs=mr, decs=dec,
                                           sumsets=ss,
                                           fft_resid_max=r2, secs=round(time.time() - t1, 2))
                mu = sum(fr) / len(fr)
                sd = (sum((x - mu) ** 2 for x in fr) / (len(fr) - 1)) ** 0.5
                L(f"  bits={bits} slot={slot} {arm} m={m} b={b}: x frac={ev['frac']:.4f} "
                  f"mean_r={ev['mean_r']:.2f} | {kind} {mu:.4f}±{sd:.4f} "
                  f"mean_r={sum(mr)/len(mr):.2f} |B+B|={ss_x} nullBB~{sum(ss)/len(ss):.0f}")
            OUT["cells"].append(cell)
        save()
    L(f"curve bits={bits} slot={slot} done")

OUT["run_end"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
save()
L(f"WROTE results.json  run_end={OUT['run_end']}  total {time.time()-T0:.0f}s")
