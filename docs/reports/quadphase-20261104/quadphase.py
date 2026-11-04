#!/usr/bin/env python3
"""LEAD-EXO-quadratic-phase-small-x-leakage: quadratic-phase correlation of the small-x factor base in log order.
Q(S) = max_{alpha in [1,N-1], beta in [0,N-1]} |sum_{l in S} e((alpha l^2 + beta l)/N)| / sqrt(|S|), one FFT per alpha.
Per curve (prime-order E over F_p, N = #E prime, p the largest prime < 2^L with such curves drawn by protocol seed):
  EC      : S = discrete logs of the first B = 512 points of E sorted by (x, y)   (the H-PSEUDO small-x rule)
  N_sym   : negation-closed random sets {l, N-l}, B/2 pairs                        (null; D1 lesson)
  planted : S = {l : alpha0 l^2 mod N < B}, negation-closed, |S| ~ B              (positive control, spikes at alpha0)
Sizes: L = 12, 13, 14 (3 curves, 40 null draws each; decisive), L = 16 (1 curve, 5 draws; descriptive).
Seeds: tools/experiment_protocol.py derive_seed(protocol_sha, arm, instance, replicate).
Usage: quadphase.py --protocol-sha <hex> --out rows.jsonl [--workers 3]"""
import argparse, json, math, os, sys, numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))
from tools.experiment_protocol import derive_seed
B = 512
PLAN = [(12, 3, 40), (13, 3, 40), (14, 3, 40), (16, 1, 5)]

def isprime(n): return n > 1 and all(n % d for d in range(2, int(n**.5) + 1))
def add(P, Q, p, a):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    l = ((3*P[0]*P[0] + a) * pow(2*P[1], -1, p) if P == Q else (Q[1]-P[1]) * pow(Q[0]-P[0], -1, p)) % p
    x = (l*l - P[0] - Q[0]) % p; return (x, (l*(P[0]-x) - P[1]) % p)

def curves_for(L, count, sha):
    p = max(q for q in range(2**(L-1), 2**L) if isprime(q))
    sq = np.zeros(p, dtype=np.int64); sq[(np.arange(1, p)**2) % p] = 1
    leg = 2*sq - 1; leg[0] = 0; X = np.arange(p); out = []
    rng = np.random.default_rng(derive_seed(sha, "curve", str(L), 0))
    while len(out) < count:
        a, b = int(rng.integers(0, p)), int(rng.integers(1, p))
        if (4*a**3 + 27*b*b) % p == 0: continue
        n = p + 1 + int(leg[(X**3 + a*X + b) % p].sum())
        if isprime(n) and n != p and n not in [c[3] for c in out]: out.append((p, a, b, n))
    return out

def ec_logs(p, a, b, n):
    x = 0
    while True:
        v = (x**3 + a*x + b) % p; ys = [y for y in range(1, p) if y*y % p == v]
        if ys: G = (x, ys[0]); break
        x += 1
    dl = {}; Q = G
    for k in range(1, n):
        dl[Q] = k; Q = add(Q, G, p, a)
    F = sorted(dl.items())[:B]
    return np.array([k for _, k in F], dtype=np.int64)

def Q_of(pos, N, chunk=256):
    pos = np.asarray(pos, dtype=np.int64); l2 = (pos * pos) % N; best = 0.0; arg = (0, 0)
    rows = np.arange(chunk)[:, None]
    for a0 in range(1, N, chunk):
        al = np.arange(a0, min(N, a0 + chunk)); m = al.size
        M = np.zeros((m, N), complex)
        M[rows[:m], pos[None, :]] = np.exp(2j * np.pi * ((al[:, None] * l2[None, :]) % N) / N)
        A = np.abs(np.fft.fft(M, axis=1)); i = np.unravel_index(A.argmax(), A.shape)
        if A[i] > best: best = float(A[i]); arg = (int(al[i[0]]), int(i[1]))
    return best / math.sqrt(pos.size), arg

def job(t):
    kind, inst, rep, L, ci, N, pos = t
    q, (al, be) = Q_of(pos, N)
    return dict(arm=kind, instance_id=inst, replicate=rep, L=L, curve_index=ci, N=N, size=int(len(pos)), Q=q, alpha=al, beta=be)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=3); a = ap.parse_args(); sha = a.protocol_sha
    tasks = []; inst = 0; meta = {}
    for L, nc, nd in PLAN:
        for ci, (p, A, Bc, n) in enumerate(curves_for(L, nc, sha)):
            iid = str(inst); inst += 1; meta[iid] = dict(L=L, p=p, a=A, b=Bc, n=n)
            tasks.append(("EC", iid, 0, L, ci, n, ec_logs(p, A, Bc, n)))
            for d in range(nd):
                r = np.random.default_rng(derive_seed(sha, "N_sym", iid, d))
                h = r.choice(np.arange(1, (n - 1)//2 + 1), B//2, replace=False); tasks.append(("N_sym", iid, d, L, ci, n, np.concatenate([h, n - h])))
            r = np.random.default_rng(derive_seed(sha, "planted", iid, 0)); a0 = int(r.integers(1, n))
            l = np.arange(1, n); S = l[(a0 * l * l) % n < B]; tasks.append(("planted", iid, 0, L, ci, n, S))
            meta[iid]["alpha0"] = a0
    tasks.sort(key=lambda t: -t[5])
    with open(a.out, "w") as f, Pool(a.workers) as pool:
        for r in pool.imap_unordered(job, tasks):
            r.update(meta[r["instance_id"]]); f.write(json.dumps(r) + "\n"); f.flush()
    print("done", file=sys.stderr)

if __name__ == "__main__":
    main()
