#!/usr/bin/env python3
"""Re-read the H-PSEUDO character-sum ladder (EXP-ECDLP-1ed445, RUN-001) against a negation-matched null.
The EC arm is the recorded per-curve C_EC (raw-result.json, stage2.per_curve): the 8 curves per rung that feed
R_mean (curve_index < 8; calibration, already re-read in-sample by the round-2 validator) and, at bits 20 and 22, the
12 further recorded curves (curve_index 8..19; out of sample, decisive). For each such curve, at that curve's own N and B = 512:
  N_sym  : 20 negation-closed random sets {l, N-l} (B/2 distinct l in [1, (N-1)/2])   (test null)
Per rung, at the representative N: 40 uniform random B-subsets (the original null's law; replication of the
recorded C_null_mean) and a planted negation-closed AP {+-d, ..., +-(B/2)d} (positive control). EC replay: recompute C_EC with
the original code for all 8 curves at bits 20, 22 and the smallest-N curve at bits 24, 26.
Seeds: tools/experiment_protocol.py derive_seed(protocol_sha, arm, instance, draw).
Usage: hpseudo_symnull.py --protocol-sha <hex> --out rows.jsonl [--workers 3]"""
import argparse, json, math, os, sys, numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, REPO)
from tools.experiment_protocol import derive_seed
RAW = os.path.join(REPO, "experiments/EXP-ECDLP-1ed445/runs/RUN-ECDLP-1ed445-001/raw-result.json")
B = 512; DRAWS = 20; REP_DRAWS = 40; PER_RUNG = 8; OOS_BITS = (20, 22)   # curve_index 8..19 there: out of sample

def C_of(idx, N):
    v = np.zeros(N); np.add.at(v, np.asarray(idx) % N, 1.0)
    return float(np.abs(np.fft.rfft(v)[1:]).max() / math.sqrt(len(idx)))

def sym_set(rng, N):
    l = rng.choice(np.arange(1, (N - 1) // 2 + 1), B // 2, replace=False); return np.concatenate([l, N - l])
def asym_set(rng, N):
    return rng.choice(np.arange(1, N), B, replace=False)

def job(args):
    sha, kind, inst, N, draw = args
    rng = np.random.default_rng(derive_seed(sha, kind, str(inst), draw))
    s = sym_set(rng, N) if kind == "N_sym" else asym_set(rng, N)
    return dict(arm=kind, instance_id=str(inst), replicate=draw, N=N, C=C_of(s, N))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=3); a = ap.parse_args(); sha = a.protocol_sha
    raw = json.load(open(RAW)); pc = raw["stage2"]["per_curve"]
    curves = sorted([c for c in pc if c["curve_index"] < PER_RUNG or c["bits"] in OOS_BITS], key=lambda c: (c["bits"], c["curve_index"]))
    out = open(a.out, "w")
    for i, c in enumerate(curves):
        out.write(json.dumps(dict(arm="EC_recorded", instance_id=str(i), replicate=0, bits=c["bits"], curve_index=c["curve_index"],
                                  N=c["N"], p=c["p"], C=c["C_EC"], F_size=c["F_size"],
                                  sample="calibration" if c["curve_index"] < PER_RUNG else "out_of_sample")) + "\n")
    meta = raw["stage1"]["curve_metadata"]; nullrec = raw["stage1"]["null_arm"]
    tasks = [(sha, "N_sym", i, c["N"], d) for i, c in enumerate(curves) for d in range(DRAWS)]
    tasks += [(sha, "N_asym", f"rung{b}", meta[b]["N_representative"], d) for b in meta for d in range(REP_DRAWS)]
    tasks.sort(key=lambda t: -t[3])                       # big FFTs first for load balance
    with Pool(a.workers) as pool:
        for r in pool.imap_unordered(job, tasks, chunksize=2):
            if r["arm"] == "N_sym":
                c = curves[int(r["instance_id"])]; r.update(bits=c["bits"], curve_index=c["curve_index"])
            else:
                b = r["instance_id"][4:]; r.update(bits=int(b), recorded_C_null_mean=nullrec[b]["null_mean_C"])
            out.write(json.dumps(r) + "\n"); out.flush()
    print("nulls done", file=sys.stderr, flush=True)
    for bits in sorted(meta, key=int):
        Nrep = meta[bits]["N_representative"]
        rng = np.random.default_rng(derive_seed(sha, "planted", bits, 0)); d = int(rng.integers(2, Nrep - 1))
        ap_set = np.concatenate([(d * np.arange(1, B // 2 + 1)) % Nrep, (-d * np.arange(1, B // 2 + 1)) % Nrep])
        out.write(json.dumps(dict(arm="planted_sym_AP", instance_id=f"rung{bits}", replicate=0, bits=int(bits), N=Nrep, C=C_of(ap_set, Nrep))) + "\n")
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

if __name__ == "__main__":
    main()
