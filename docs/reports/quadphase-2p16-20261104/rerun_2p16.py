#!/usr/bin/env python3
"""Settle the descriptive 2^16 curve of QUADPHASE-20261104 (p=65521, a=48322, b=6694, n=65167), whose Q_EC = 4.7249 sat above
all 5 null draws. Recompute Q_EC (EC replay against the recorded value), 40 fresh negation-closed null draws, and the planted
control, with quadphase.py (byte copy of the frozen QUADPHASE script). Seeds: derive_seed(protocol_sha, arm, '0', replicate)."""
import argparse, json, os, sys, numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))
from tools.experiment_protocol import derive_seed
import quadphase as Q
P, A, B_, N = 65521, 48322, 6694, 65167; REC_Q = 4.724867280594446; DRAWS = 40
def job(t):
    kind, rep, pos = t; q, (al, be) = Q.Q_of(pos, N)
    return dict(arm=kind, instance_id="0", replicate=rep, N=N, size=int(len(pos)), Q=q, alpha=al, beta=be)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=3); a = ap.parse_args(); sha = a.protocol_sha
    tasks = [("EC", 0, Q.ec_logs(P, A, B_, N))]
    for d in range(DRAWS):
        r = np.random.default_rng(derive_seed(sha, "N_sym", "0", d)); h = r.choice(np.arange(1, (N-1)//2 + 1), Q.B//2, replace=False)
        tasks.append(("N_sym", d, np.concatenate([h, N - h])))
    r = np.random.default_rng(derive_seed(sha, "planted", "0", 0)); a0 = int(r.integers(1, N)); l = np.arange(1, N)
    tasks.append(("planted", 0, l[(a0 * l * l) % N < Q.B]))
    with open(a.out, "w") as f, Pool(a.workers) as pool:
        for row in pool.imap_unordered(job, tasks):
            row.update(p=P, recorded_Q_EC=REC_Q, alpha0=a0); f.write(json.dumps(row) + "\n"); f.flush()
    print("done", file=sys.stderr)
if __name__ == "__main__":
    main()
