#!/usr/bin/env python3
"""Infrastructure completion of the HPSEUDO-SYMNULL-20261104 run after its multiprocessing pool hung (worker loss on
the two N ~ 33.6M curves). Recomputes exactly the missing (arm, instance, draw) tasks with the frozen
hpseudo_symnull.job (same derive_seed inputs, so identical values to an uninterrupted run), sequentially in one process,
then runs the frozen script's control and replay stages (code copied verbatim from hpseudo_symnull.main) and appends
everything to rows.jsonl. It changes no design parameter."""
import json, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import hpseudo_symnull as H
from hpseudo_symnull import derive_seed, C_of, B, DRAWS, PER_RUNG, OOS_BITS, RAW, REPO
sha, out_path = sys.argv[1], sys.argv[2]
raw = json.load(open(RAW)); pc = raw["stage2"]["per_curve"]
curves = sorted([c for c in pc if c["curve_index"] < PER_RUNG or c["bits"] in OOS_BITS], key=lambda c: (c["bits"], c["curve_index"]))
have = {(r["arm"], r["instance_id"], r["replicate"]) for r in map(json.loads, open(out_path))}
missing = [("N_sym", i, d) for i in range(len(curves)) for d in range(DRAWS) if ("N_sym", str(i), d) not in have]
print(f"missing N_sym tasks: {len(missing)}", file=sys.stderr, flush=True)
out = open(out_path, "a")
for kind, i, d in missing:
    r = H.job((sha, kind, i, curves[i]["N"], d)); c = curves[i]; r.update(bits=c["bits"], curve_index=c["curve_index"])
    out.write(json.dumps(r) + "\n"); out.flush()
print("nulls done", file=sys.stderr, flush=True)
meta = raw["stage1"]["curve_metadata"]
for bits in sorted(meta, key=int):                                   # verbatim from hpseudo_symnull.main
    Nrep = meta[bits]["N_representative"]
    rng = np.random.default_rng(derive_seed(sha, "planted", bits, 0)); d = int(rng.integers(2, Nrep - 1))
    ap_set = np.concatenate([(d * np.arange(1, B // 2 + 1)) % Nrep, (-d * np.arange(1, B // 2 + 1)) % Nrep])
    out.write(json.dumps(dict(arm="planted_sym_AP", instance_id=f"rung{bits}", replicate=0, bits=int(bits), N=Nrep, C=C_of(ap_set, Nrep))) + "\n"); out.flush()
print("controls done", file=sys.stderr, flush=True)
sys.path.insert(0, os.path.join(REPO, "experiments/EXP-ECDLP-1ed445"))
import run_character_sum_ladder as L
replay = [c for c in curves if c["bits"] in (20, 22) and c["curve_index"] < PER_RUNG]
for bits in (24, 26):
    replay.append(min((c for c in curves if c["bits"] == bits), key=lambda c: c["N"]))
for c in replay:
    dl = L.build_dl_table(tuple(c["G"]), c["N"], c["a"], c["p"])
    tau, F, F_dls = L.build_factor_base(dl, B); C, k = L.compute_C_fft(F_dls, c["N"]); del dl
    neg_closed = len(set(F_dls)) == len({min(x, c["N"] - x) for x in F_dls}) * 2
    out.write(json.dumps(dict(arm="EC_replay", instance_id=f"b{c['bits']}c{c['curve_index']}", replicate=0, bits=c["bits"], curve_index=c["curve_index"],
                              N=c["N"], C=C, recorded=c["C_EC"], neg_closed=neg_closed)) + "\n"); out.flush()
    print(f"replay bits={c['bits']} ci={c['curve_index']} N={c['N']} done", file=sys.stderr, flush=True)
