#!/usr/bin/env python3
"""LEAD-EXO-weak-class-instrument-calibration: do the numeric structure instruments see curves whose DLP is easy?
Classes (prime order n): A anomalous (n = p); B small embedding degree (ord_n(p) <= 6); C j = 0 (a = 0, p = 1 mod 3)
with a zeta-stable factor base; D ordinary, one paired with each A/B/C curve over the same p (n != p, ord_n(p) > 6).
Sizes L = 10, 12, 14 (p in [2^(L-1), 2^L)), 3 curves per weak class per size.
Instruments, each as the mid-rank percentile u of the curve's statistic within its own null (40 draws):
  I1 char-sum  : C = max_k |sum_{l in F} e(k l/n)| / sqrt|F|, F = logs of the first B = 2 isqrt(n) points by (x,y)
                 (C: zeta-stable FB); null = negation-closed random log sets of size |F|; positive = negation-closed log-AP
  I2 m=2 yield : |F + F| / n (log sumset, via FFT convolution support); same null and positive control
  I3 QTT       : interleaved QTT log2_params of M (holant step b core) for L = 10 only; null = 40 random relabellings;
                 positive = discrete-log labelling
Seeds: tools/experiment_protocol.py derive_seed(protocol_sha, tag, instance, replicate)."""
import argparse, json, math, os, sys, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", ".."))); sys.path.insert(0, HERE)
from tools.experiment_protocol import derive_seed
import weak_curves as W
from qtt_core import transfer_matrix, qtt_ranks, summary
SIZES = [10, 12, 14]; PER = 3; DRAWS = 40

def add(P, Q, p, a):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    l = ((3*P[0]*P[0] + a) * pow(2*P[1], -1, p) if P == Q else (Q[1]-P[1]) * pow(Q[0]-P[0], -1, p)) % p
    x = (l*l - P[0] - Q[0]) % p; return (x, (l*(P[0]-x) - P[1]) % p)

def dl_table(p, a, b, n):
    x = 0
    while True:
        v = (x**3 + a*x + b) % p; ys = [y for y in range(1, p) if y*y % p == v]
        if ys: G = (x, ys[0]); break
        x += 1
    dl = {}; Q = G
    for k in range(1, n): dl[Q] = k; Q = add(Q, G, p, a)
    return dl

def fb_logs(dl, p, a, n, cls, Bsz):
    pts = sorted(dl)
    if cls != "C": return np.array([dl[P] for P in pts[:Bsz]], dtype=np.int64)
    z = next(z for z in range(2, p) if pow(z, 3, p) == 1)          # zeta-stable: whole orbits {x, zx, z^2 x} with both y
    S = []; seen = set()
    for (x, y) in pts:
        if x in seen: continue
        orb = {x, z*x % p, z*z*x % p}; seen |= orb
        S += [dl[P] for P in pts if P[0] in orb]
        if len(S) >= Bsz: break
    return np.array(S, dtype=np.int64)

def C_of(l, n):
    v = np.zeros(n); v[l % n] = 1.0; return float(np.abs(np.fft.rfft(v)[1:]).max() / math.sqrt(len(l)))
def Y_of(l, n):
    v = np.zeros(n); v[l % n] = 1.0; c = np.fft.irfft(np.fft.rfft(v)**2, n)
    return float((c > 0.5).sum() / n)
def sym_draw(rng, n, size):
    h = rng.choice(np.arange(1, (n-1)//2 + 1), size//2, replace=False); return np.concatenate([h, n - h])
def pct(v, null): null = np.asarray(null); return float(((null < v).sum() + 0.5*(null == v).sum())/null.size)

def pick(L, sha):
    rng = np.random.default_rng(derive_seed(sha, "pick", str(L), 0)); ps = W.primes_in(2**(L-1), 2**L); out = []
    order_ps = [ps[i] for i in rng.permutation(len(ps))]
    def paired(p, leg):
        used = {c["n"] for c in out if c["p"] == p}
        for _ in range(200000):                      # ordinary: a, b != 0 (j != 0, 1728), prime order, not anomalous, k > 6, unused order
            a, b = int(rng.integers(1, p)), int(rng.integers(1, p))
            if (4*a**3 + 27*b*b) % p == 0: continue
            n = W.order(p, a, b, leg)
            if W.isprime(n) and n != p and W.emb_degree(p, n) is None and n not in used: return a, b, n
    for p in order_ps:                                              # A: anomalous
        if sum(c["cls"] == "A" for c in out) == PER: break
        leg = W.leg_table(p); r = W.find_curve(p, lambda n: n == p, rng, leg, tries=20000)
        if r: out.append(dict(cls="A", p=p, a=r[0], b=r[1], n=r[2])); q = paired(p, leg); out.append(dict(cls="D", pair="A", p=p, a=q[0], b=q[1], n=q[2]))
    tg = [(p, n) for p in order_ps for n in W.small_k_targets(p)]
    for p, n in tg:                                                 # B: small embedding degree
        if sum(c["cls"] == "B" for c in out) == PER: break
        leg = W.leg_table(p); r = W.find_curve(p, lambda m: m == n, rng, leg, tries=200000)
        if r: out.append(dict(cls="B", p=p, a=r[0], b=r[1], n=r[2], k=W.emb_degree(p, n))); q = paired(p, leg); out.append(dict(cls="D", pair="B", p=p, a=q[0], b=q[1], n=q[2]))
    for p in [q for q in order_ps if q % 3 == 1]:                   # C: j = 0
        if sum(c["cls"] == "C" for c in out) == PER: break
        leg = W.leg_table(p); r = W.find_curve(p, lambda n: W.isprime(n) and n != p, rng, leg, a_fixed=0, tries=4000)
        if r: out.append(dict(cls="C", p=p, a=0, b=r[1], n=r[2])); q = paired(p, leg); out.append(dict(cls="D", pair="C", p=p, a=q[0], b=q[1], n=q[2]))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--protocol-sha", required=True); ap.add_argument("--out", required=True)
    a_ = ap.parse_args(); sha = a_.protocol_sha; inst = 0
    with open(a_.out, "w") as f:
        for L in SIZES:
            for c in pick(L, sha):
                iid = str(inst); inst += 1; p, a, b, n = c["p"], c["a"], c["b"], c["n"]
                dl = dl_table(p, a, b, n); Bsz = 2 * int(math.isqrt(n) // 1)
                F = fb_logs(dl, p, a, n, c["cls"], Bsz)
                row = dict(c, L=L, instance_id=iid, fb_size=int(len(F)))
                nul = [sym_draw(np.random.default_rng(derive_seed(sha, "N_sym", iid, d)), n, len(F) - len(F) % 2) for d in range(DRAWS)]
                Cn = [C_of(s, n) for s in nul]; Yn = [Y_of(s, n) for s in nul]
                r0 = np.random.default_rng(derive_seed(sha, "planted", iid, 0)); dd = int(r0.integers(2, n - 1)); h = len(F)//2
                apset = np.concatenate([(dd*np.arange(1, h+1)) % n, (-dd*np.arange(1, h+1)) % n])
                row.update(I1=C_of(F, n), I1_u=pct(C_of(F, n), Cn), I1_pos_u=pct(C_of(apset, n), Cn), I1_null_mean=float(np.mean(Cn)),
                           I2=Y_of(F, n), I2_u=pct(Y_of(F, n), Yn), I2_pos_u=pct(Y_of(apset, n), Yn), I2_null_mean=float(np.mean(Yn)),
                           aa_I1=abs(np.mean(Cn[0::2]) - np.mean(Cn[1::2])) / np.mean(Cn))
                if L == 10:
                    Lq = int(np.ceil(np.log2(p))); Ex = sorted({P[0] for P in dl}); FBx = Ex[:int(math.isqrt(p))]
                    M = transfer_matrix(p, a, b, FBx); X = summary(qtt_ranks(M, Lq, "interleaved"))["log2_params"]
                    nq = []
                    for d in range(DRAWS):
                        q = np.random.default_rng(derive_seed(sha, "N_qtt", iid, d)).permutation(p); Mn = np.zeros_like(M); Mn[np.ix_(q, q)] = M
                        nq.append(summary(qtt_ranks(Mn, Lq, "interleaved"))["log2_params"])
                    orbit = {P[0]: min(dl[P], n - dl[P]) - 1 for P in dl}; rest = [x for x in range(p) if x not in orbit]
                    perm = np.empty(p, dtype=np.int64)
                    for x, j in orbit.items(): perm[x] = j
                    for i, x in enumerate(rest): perm[x] = len(orbit) + i
                    Ml = np.zeros_like(M); Ml[np.ix_(perm, perm)] = M
                    row.update(I3=X, I3_u=pct(X, nq), I3_pos_u=pct(summary(qtt_ranks(Ml, Lq, "interleaved"))["log2_params"], nq), I3_null_mean=float(np.mean(nq)))
                f.write(json.dumps(row) + "\n"); f.flush()
                print(f"L={L} {c['cls']} p={p} n={n} done", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
