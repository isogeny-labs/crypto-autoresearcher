# Numerical check of Theorem V2 (step_volume.md): c2(W) = #{1<=x1<=x2 : |s2_j(x)| <= W_j} <= C_2 omega^{1/15} + M(1+ln M), C_2 < 8.7.
# Tight boxes: for every pair with x1*x2 <= E we take W = |s2(x)| coordinatewise maxima over random subsets? No: we scan a log grid of
# (W0,W1,W3,W4) and for each take W2 = k-th smallest |s2_2| among eligible pairs for all k (tight boxes), as SA-13b did at level 1.
import numpy as np, math, json, sys, time, random
random.seed(5)
E = int(sys.argv[1]) if len(sys.argv) > 1 else 300000
def pairs_s2(a, b):
    xs = []
    for x1 in range(1, int(E ** 0.5) + 1):
        for x2 in range(x1, E // x1 + 1):
            e1, e2 = x1 + x2, x1 * x2
            G0 = (e2 - a) ** 2 - 4 * b * e1; G1 = -2 * (e1 * (e2 + a) + 2 * b); G2 = (x2 - x1) ** 2
            xs.append((abs(G0 * G0), abs(2 * G0 * G1), abs(2 * G0 * G2 + G1 * G1), abs(2 * G1 * G2), abs(G2 * G2)))
    return np.array(xs, dtype=np.float64)
out = {}
for (a, b) in [(0, 7), (2, 5), (-3, 11)]:
    t = time.time(); S = pairs_s2(a, b); n = len(S)
    best = (0, None); bestbig = (0, None); rows = []
    grids = [np.exp(np.linspace(0, np.log(S[:, j].max()), 14)) for j in (0, 1, 3, 4)]
    for it in range(1500):
        W0 = random.choice(grids[0]); W1 = random.choice(grids[1]); W3 = random.choice(grids[2]); W4 = random.choice(grids[3])
        el = (S[:, 0] <= W0) & (S[:, 1] <= W1) & (S[:, 3] <= W3) & (S[:, 4] <= W4)
        v = np.sort(S[el, 2])
        if len(v) == 0: continue
        v = np.maximum(v, 1.0)
        ks = np.arange(1, len(v) + 1)             # W2 = v[k-1] gives count >= k (exactly k if distinct); use count = k
        om = max(W0, 1) * max(W1, 1) * v * max(W3, 1) * max(W4, 1)
        r = ks / om ** (1 / 15)
        i = int(np.argmax(r))
        if r[i] > best[0]: best = (float(r[i]), (int(ks[i]), [float(W0), float(W1), float(v[i]), float(W3), float(W4)]))
        big = ks >= 200
        if big.any():
            j = int(np.argmax(np.where(big, r, 0)))
            if r[j] > bestbig[0]: bestbig = (float(r[j]), (int(ks[j]), [float(W0), float(W1), float(v[j]), float(W3), float(W4)]))
    # balanced boxes W_j = B^{8-j}: exact count and ratio
    bal = []
    for B in [4, 8, 16, 32, 64, 128]:
        W = [B ** 8, B ** 7, B ** 6, B ** 5, B ** 4]
        if W[0] > S[:, 0].max() / 4: break
        c = int(np.all(S <= np.array(W, dtype=np.float64), axis=1).sum()); om = float(np.prod([float(w) for w in W]))
        bal.append((B, c, c / om ** (1 / 15)))
    print("curve (a,b)=(%d,%d): %d pairs (x1x2<=%d), %.0fs; sup c2/omega^(1/15) = %.3f at (c,W)=%s; sup over c>=200: %.3f at %s; balanced: %s" % (
        a, b, n, E, time.time() - t, best[0], best[1], bestbig[0], bestbig[1], [(B, c, round(r, 3)) for B, c, r in bal]), flush=True)
    out[str((a, b))] = dict(pairs=n, E=E, sup=best, sup_c200=bestbig, balanced=bal)
json.dump(out, open('exp_vol_level2.json', 'w'), indent=1)
