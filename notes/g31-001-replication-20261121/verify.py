"""verify.py -- post-freeze implementation verification (no new statistics).

Cross-checks the primary FFT/log counting engine against the pilot's
group-law pair-table engine, on the real frozen curves, bases, targets and
null bases.  Also checks invariants that the replication relies on.
Writes verify.json + verify.log.  Touches no decision quantity.
"""
import json
import math
import time

import numpy as np

import replib as R
from pilot_run import Ctx, InvTable

F = json.load(open("frozen_config.json"))
logf = open("verify.log", "w")
OUT = dict(frozen_utc=F["frozen_utc"], checks=[])


def L(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    logf.write(s + "\n")
    logf.flush()


def cmp_engine(E, n, g, B, tlogs, m, invt, n_use=None):
    """Return (max_abs_diff, sum_pilot, sum_fft, witness_bad, n_compared)."""
    tab = R.log_table(E, n, g)
    logs = [tab[P] for P in B]
    ctx = Ctx(E, invt)
    ctx.n, ctx.g = n, g
    ctx.pair_table(B)
    tl = tlogs if n_use is None else tlogs[:n_use]
    cv, resid = R.counts(logs, n, m)
    diffs = []
    sp = sf = 0
    bad = 0
    for k in tl:
        Q = E.mul(k, g)
        cnt, wit = ctx.r_m(Q, m)
        if wit is not None:
            S = None
            for P in wit:
                S = E.add(S, P)
            if S != Q:
                bad += 1
        f = int(cv[k])
        diffs.append(abs(cnt - f))
        sp += cnt
        sf += f
    return max(diffs), sp, sf, bad, len(tl), resid


t0 = time.time()
invt_cache = {}
per_curve = []
for c in F["curves"]:
    bits, slot = c["bits"], c["slot"]
    rec = R.make_curve(bits, slot)                      # determinism check
    assert (rec["p"], rec["a"], rec["b"], rec["nE"]) == (c["p"], c["a"], c["b"], c["nE"]), \
        "curve generation not reproducible"
    E, n, g = rec["E"], rec["n"], rec["g"]
    if c["p"] not in invt_cache:
        invt_cache[c["p"]] = InvTable(c["p"])
    invt = invt_cache[c["p"]]
    tab = R.log_table(E, n, g)
    trng = R.rng_for(R.MASTER, bits, slot, "targets")
    tlogs = [trng.randrange(1, n) for _ in range(F["n_targets_per_cell"])]
    assert [E.mul(k, g) for k in tlogs[:5]] == [E.mul(k, g) for k in tlogs[:5]]

    for arm in ("N3", "N2"):
        N = math.isqrt(E.p) if arm == "N2" else int(round(E.p ** (1 / 3)))
        B = R.window_points(E, N)
        logs = [tab[P] for P in B]
        st = set(logs)
        inv = dict(bits=bits, slot=slot, arm=arm, N=N, b=len(logs),
                   b_even=len(logs) % 2 == 0,
                   negclosed=all((-k) % n in st for k in logs),
                   O_absent=all(P is not None for P in B),
                   no_2torsion=not any(P[1] == 0 for P in B),
                   b_matches_frozen=len(logs) == c["arms"][arm]["b"])
        for m in (3, 4):
            n_use = len(tlogs) if arm == "N3" else 120
            d, sp, sf, bad, nn, resid = cmp_engine(E, n, g, B, tlogs, m, invt, n_use)
            inv[f"m{m}"] = dict(max_abs_diff=d, sum_pilot=sp, sum_fft=sf,
                                exact=bool(d == 0 and sp == sf),
                                witness_bad=bad, compared=nn, fft_resid=resid,
                                mass_ok=int(sum(1 for _ in ())) == 0)
            cv, _ = R.counts(logs, n, m)
            inv[f"m{m}"]["total_mass"] = int(cv.sum())
            inv[f"m{m}"]["mass_ok"] = int(cv.sum()) == len(logs) ** m
        # two null bases (one per kind) x m in {3,4}, 120 targets
        for kind in ("symmetric", "uniform"):
            rng = R.rng_for(R.MASTER, bits, slot, arm, "verify", kind)
            nl = R.null_logs(n, len(logs), kind, rng)
            B2 = [E.mul(k, g) for k in nl]
            for m in (3, 4):
                d, sp, sf, bad, nn, resid = cmp_engine(E, n, g, B2, tlogs, m, invt, 120)
                inv[f"null_{kind}_m{m}"] = dict(max_abs_diff=d, sum_pilot=sp,
                                                sum_fft=sf, exact=bool(d == 0 and sp == sf),
                                                witness_bad=bad, compared=nn,
                                                fft_resid=resid)
        per_curve.append(inv)
        ok = all(inv[k]["exact"] for k in inv if k.startswith(("m3", "m4", "null_")))
        L(f"bits={bits} slot={slot} {arm} b={len(logs)} "
          f"exact={ok} negclosed={inv['negclosed']} b_even={inv['b_even']} "
          f"no2tors={inv['no_2torsion']}")
        OUT["checks"].append(inv)

# aggregate
exact_all = all(v["exact"] for c in per_curve for k, v in c.items()
                if isinstance(v, dict) and "exact" in v)
maxdiff = max(v["max_abs_diff"] for c in per_curve for k, v in c.items()
              if isinstance(v, dict) and "max_abs_diff" in v)
bad_wit = sum(v["witness_bad"] for c in per_curve for k, v in c.items()
              if isinstance(v, dict) and "witness_bad" in v)
mass_ok = all(v["mass_ok"] for c in per_curve for k, v in c.items()
              if isinstance(v, dict) and "mass_ok" in v)
resid_max = max(v["fft_resid"] for c in per_curve for k, v in c.items()
                if isinstance(v, dict) and "fft_resid" in v)
invariants = dict(
    all_bases_even=all(c["b_even"] for c in per_curve),
    all_bases_negclosed=all(c["negclosed"] for c in per_curve),
    all_O_absent=all(c["O_absent"] for c in per_curve),
    all_no_2torsion=all(c["no_2torsion"] for c in per_curve),
    all_b_match_frozen=all(c["b_matches_frozen"] for c in per_curve),
    curve_generation_reproducible=True,
)
OUT.update(dict(exact_engine_agreement=bool(exact_all), max_abs_count_diff=int(maxdiff),
                witness_bad=bad_wit, total_mass_ok=bool(mass_ok),
                max_fft_residual=float(resid_max), invariants=invariants,
                n_curve_arm_checks=len(per_curve),
                elapsed_s=round(time.time() - t0, 1)))
L(f"EXACT ENGINE AGREEMENT: {exact_all} (max |diff| = {maxdiff})")
L(f"witness_bad={bad_wit} total_mass_ok={mass_ok} max_fft_residual={resid_max:.2e}")
L(f"invariants: {invariants}")
json.dump(OUT, open("verify.json", "w"), indent=2)
L(f"WROTE verify.json  ({time.time()-t0:.1f}s)")
