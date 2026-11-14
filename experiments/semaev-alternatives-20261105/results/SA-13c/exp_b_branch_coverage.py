# Exact coverage of the k*=1 branch: cov_b(A) = #{1<=x1<=x2 : exists nonzero q in Z[T], deg q<=2, |coef_j(q S_x)| <= A_j, j=0..4}
# where A_j = floor(W_j/p) (0 = coordinate forced to zero). Checks Proposition B of step_b.md: cov_b <= K * Pi_J (Pi_J = prod of A_j>=1)
# and the sharper generic form cov_b <= K' Pi_J^{2/3} + const. Exact enumeration of q (ranges from the extreme coefficients).
import random, json, math, sys, time
random.seed(13)
AMAX = 5003            # p = 10007: A_j < p/2
XMAX = 300
def Gs(x1, x2, a, b):
    e1, e2 = x1 + x2, x1 * x2
    return (e2 - a) ** 2 - 4 * b * e1, -2 * (e1 * (e2 + a) + 2 * b), (x2 - x1) ** 2
def rng(Aj, g):          # |q g| <= Aj  ->  |q| <= Aj//|g|
    return Aj // abs(g)
def covered(G, A):
    G0, G1, G2 = G
    # q0 range
    if G0: r0 = rng(A[0], G0)
    elif G1: r0 = rng(A[1], G1)
    else: r0 = rng(A[2], G2)
    if G2: r2 = rng(A[4], G2)
    elif G1: r2 = rng(A[3], G1)
    else: r2 = rng(A[2], G0)
    if (2 * r0 + 1) * (2 * r2 + 1) > 2_000_000: return None   # capped (never happened in the reported runs)
    for q0 in range(-r0, r0 + 1):
        for q2 in range(-r2, r2 + 1):
            lo, hi = -10 ** 18, 10 ** 18
            # u1 = q0 G1 + q1 G0 ; u2 = q0 G2 + q1 G1 + q2 G0 ; u3 = q1 G2 + q2 G1
            for (c, g, Aj) in ((q0 * G1, G0, A[1]), (q0 * G2 + q2 * G0, G1, A[2]), (q2 * G1, G2, A[3])):
                if g:
                    a_, b_ = (-Aj - c), (Aj - c)
                    if g < 0: a_, b_, g = -b_, -a_, -g
                    lo = max(lo, -((-a_) // g)); hi = min(hi, b_ // g)
                elif abs(c) > Aj: lo, hi = 1, 0
            if lo > hi: continue
            if q0 == 0 and q2 == 0 and lo <= 0 <= hi and lo == hi == 0: continue
            if q0 == 0 and q2 == 0:
                if hi >= 1 or lo <= -1: return True
                continue
            return True
    return False
def run(a, b, nbox, tag):
    pairs = [(x1, x2) for x2 in range(1, XMAX + 1) for x1 in range(1, x2 + 1)]
    PG = [(x, Gs(x[0], x[1], a, b)) for x in pairs]
    rows = []; sup1 = sup23 = 0; capped = 0; t0 = time.time()
    for it in range(nbox):
        A = []
        for j in range(5):
            if random.random() < 0.3: A.append(0)
            else: A.append(int(10 ** random.uniform(0, math.log10(AMAX))))
        if it < 6:   # a few structured boxes: all equal, extremes only, middle only
            A = [[50]*5, [AMAX]*5, [AMAX, 0, 0, 0, AMAX], [0, AMAX, 0, AMAX, 0], [0, 0, AMAX, 0, 0], [AMAX, AMAX, 0, 0, 0]][it]
        Amax = max(A); PiJ = 1
        for Aj in A:
            if Aj >= 1: PiJ *= Aj
        cov = 0; cov_gen = 0; cov_deg = 0
        for x, G in PG:
            G0, G1, G2 = G
            if G0 and abs(G0) > Amax: continue
            if G2 and G2 > Amax: continue
            c = covered(G, A)
            if c is None: capped += 1; c = True
            if c:
                cov += 1
                if G0 and G2: cov_gen += 1
                else: cov_deg += 1
        r1 = cov / PiJ; r23 = cov / PiJ ** (2 / 3)
        sup1 = max(sup1, r1); sup23 = max(sup23, r23)
        rows.append(dict(A=A, PiJ=PiJ, cov=cov, cov_generic=cov_gen, cov_degenerate=cov_deg, cov_over_PiJ=r1, cov_over_PiJ23=r23))
    print("curve (a,b)=(%d,%d) boxes=%d XMAX=%d AMAX=%d capped=%d time=%.0fs" % (a, b, nbox, XMAX, AMAX, capped, time.time() - t0))
    print("  sup cov_b/Pi_J = %.4f   sup cov_b/Pi_J^(2/3) = %.4f   max cov_b = %d" % (sup1, sup23, max(r['cov'] for r in rows)))
    top = sorted(rows, key=lambda r: -r['cov_over_PiJ'])[:5]
    for r in top: print("   ", r)
    big = sorted(rows, key=lambda r: -r['cov'])[:3]
    for r in big: print("   largest cov:", r)
    json.dump(rows, open('exp_b_rows_%s.json' % tag, 'w'))
    return sup1, sup23
out = {}
for (a, b, tag) in [(0, 7, '0_7'), (2, 5, '2_5'), (-3, 11, 'm3_11')]:
    out[tag] = run(a, b, 300 if tag == '0_7' else 120, tag)
print(out)
