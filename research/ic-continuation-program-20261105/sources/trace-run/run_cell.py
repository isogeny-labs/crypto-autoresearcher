"""One grid cell: python run_cell.py CURVE N L VARM SEED OUTDIR [DCAP]. Writes OUTDIR/cell_<...>.json (append-safe)."""
import json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f4t
from math import comb

curve, n, l, varm, seed, outdir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), sys.argv[6]
DCAP = int(sys.argv[7]) if len(sys.argv) > 7 else 9
N_UNSAT, N_SAT, RATE_DRAWS = 30, 30, 200
tag = f"{curve}_n{n}_l{l}_{varm}"
path = os.path.join(outdir, f"cell_{tag}.json")
os.makedirs(outdir, exist_ok=True)

cell = f4t.make_cell(curve, n, l, varm, seed)
N = cell["N"]
t_start = time.time()
log = {"cell": tag, "curve": curve, "n": n, "l": l, "V": varm, "N": N, "seed": seed, "dcap": DCAP, "a": cell["E"].a, "b": cell["E"].b,
       "basis": cell["basis"], "natural_draws": [], "targets": [], "trace": None}


def jac(a, b):
    a, b = set(map(int, a)), set(map(int, b))
    return len(a & b) / max(1, len(a | b))


def save():
    json.dump(log, open(path + ".tmp", "w"))
    os.replace(path + ".tmp", path)


# natural stream: S labels by enumeration (cheap), keep first 31 UNSAT; extra draws only for the empirical SAT rate
unsat, nat_total, nat_sat = [], 0, 0
while len(unsat) < 1 + N_UNSAT or nat_total < RATE_DRAWS:
    R = f4t.natural_draw(cell)
    sols, cnt = f4t.enum_solutions(cell["E"], cell["basis"], R[0])
    nat_total += 1
    nat_sat += cnt > 0
    log["natural_draws"].append({"xR": R[0], "S": cnt})
    if cnt == 0 and len(unsat) < 1 + N_UNSAT:
        unsat.append(R)
log["natural_rate"] = {"draws": nat_total, "sat": nat_sat}
planted = [f4t.planted_draw(cell) for _ in range(N_SAT + 1)]  # +1: the SAT-trace target (secondary arm)
log["fb_size_note"] = len(set(f4t.D.span(cell["basis"])))

tx = unsat[0]
eqs_t, S_t, dn_t, _ = f4t.target_system(cell, tx[0])
assert S_t == 0
t0 = time.time()
res_t, trace = f4t.fresh(eqs_t, N, DCAP, S_t, dn_t, record=True)
log["trace"] = {"xR": tx[0], "fresh": {k: v for k, v in res_t.items() if k not in ("pivdeg_at",)}, "items": len(trace) if trace else 0,
                "wall": time.time() - t0}
print(tag, "trace", {k: v for k, v in res_t.items() if k not in ("rank_le", "pivdeg_at")}, flush=True)
save()
if not res_t["certified"]:
    log["censored"] = "trace target not certified within dcap/memory"
    save(); sys.exit(0)

# SAT-trace (secondary arm): first planted target
sat_tx = planted[0]
eqs_s, S_s, dn_s, _ = f4t.target_system(cell, sat_tx[0])
res_s, trace_s = f4t.fresh(eqs_s, N, DCAP, S_s, dn_s, record=True)
log["sat_trace"] = {"xR": sat_tx[0], "S": S_s, "d_need": dn_s, "fresh": {k: v for k, v in res_s.items() if k not in ("pivdeg_at",)},
                    "items": len(trace_s) if trace_s else 0}
save()


def do_target(label, R, k):
    eqs, S, dn, sols = f4t.target_system(cell, R[0])
    rec = {"label": label, "xR": R[0], "S": S, "d_need": dn, "genuine": None}
    if label == "SAT":
        rec["genuine"] = f4t.D.binary_decompositions(cell["E"], [cell["basis"]] * 3, R, sols) if len(sols) < 200 else None
    t0 = time.time()
    fr, _ = f4t.fresh(eqs, N, DCAP, S, dn)
    rec["fresh"] = {k2: v for k2, v in fr.items() if k2 not in ("pivdeg_at",)}
    rec["fresh"]["wall"] = time.time() - t0
    for name, tr, only_sat in (("replay", trace, False), ("replay_sattrace", trace_s, True)):
        if only_sat and label != "SAT":
            continue
        t0 = time.time()
        rp = f4t.replay(eqs, tr)
        rp["wall"] = time.time() - t0
        d_end = tr.dmax
        codim = f4t.ncols_le(N, d_end) - rp["rank"]
        rp["codim"] = codim
        rp["success"] = bool(d_end >= dn and codim == S and not rp["overflow"])
        rp["strict"] = bool(rp["success"] and rp["zero_events"] == 0 and rp["lead_dev"] == 0 and rp["skipped"] == 0)
        rec[name] = rp
    # support drift of the equations against the trace target (first 10 targets only)
    if k < 10:
        rec["jaccard_mean"] = sum(f4t.jac(a, b) if hasattr(f4t, "jac") else jac(a, b) for a, b in zip(eqs, eqs_t)) / len(eqs)
    log["targets"].append(rec)
    save()
    print(tag, label, k, "S", S, "fresh", "%.3g" % rec["fresh"]["ops"], "cert", rec["fresh"]["certified"], "st", rec["fresh"]["final_stage"],
          "replay", "%.3g" % rec["replay"]["ops"], "ok", rec["replay"]["success"], "z", rec["replay"]["zero_events"], "dev", rec["replay"]["lead_dev"],
          "sk", rec["replay"]["skipped"], flush=True)


for k in range(N_UNSAT):
    do_target("UNSAT", unsat[1 + k], k)
for k in range(N_SAT):
    do_target("SAT", planted[1 + k], k)
log["total_wall"] = time.time() - t_start
save()
