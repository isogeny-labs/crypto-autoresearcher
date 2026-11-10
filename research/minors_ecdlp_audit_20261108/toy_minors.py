import random, math, sys
from itertools import combinations
from sympy import isprime, nextprime
def run(pbits, npr, nker, seed):
    rnd = random.Random(seed); p = nextprime(2**pbits)
    while True:  # prime-order curve y^2=x^3+ax+b over F_p, N=#E prime
        a, b = rnd.randrange(p), rnd.randrange(p)
        if (4*a**3+27*b*b) % p == 0: continue
        sq = {}; [sq.setdefault(y*y % p, []).append(y) for y in range(p)]
        pts = [(x, y) for x in range(p) for y in sq.get((x**3+a*x+b) % p, [])]
        N = len(pts)+1
        if isprime(N) and N > 100: break
    def add(P, Q):
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0] and (P[1]+Q[1]) % p == 0: return None
        s = (3*P[0]**2+a)*pow(2*P[1], -1, p) if P == Q else (Q[1]-P[1])*pow(Q[0]-P[0], -1, p)
        x = (s*s-P[0]-Q[0]) % p; return (x, (s*(P[0]-x)-P[1]) % p)
    def mul(k, P):
        R = None
        while k:
            if k & 1: R = add(R, P)
            P = add(P, P); k >>= 1
        return R
    G = rnd.choice(pts); m = rnd.randrange(2, N-1); Q = mul(m, G)
    l = 3*npr; mons = [(i, j) for i in range(npr+1) for j in range(npr+1-i)]
    zeros = tot = solved = 0
    for _ in range(nker):
        ns = rnd.sample(range(1, N), 2*l); typ = [0]*(l-1)+[1]*(l+1)  # l-1 P-rows, l+1 Q-rows
        pt = [mul(n, G) if t == 0 else mul(N-n, Q) for n, t in zip(ns, typ)]
        if len(set(pt)) < 2*l: continue  # accidental repeated point (paper: rows must be distinct)
        R = [[pow(x, i, p)*pow(y, j, p) % p for (x, y) in pt] for (i, j) in mons]  # M^T
        piv, r = [], 0
        for c in range(2*l):  # RREF of M^T mod p
            q = next((i for i in range(r, len(R)) if R[i][c]), None)
            if q is None: continue
            R[r], R[q] = R[q], R[r]; iv = pow(R[r][c], -1, p); R[r] = [v*iv % p for v in R[r]]
            for i in range(len(R)):
                if i != r and R[i][c]: f = R[i][c]; R[i] = [(u-f*v) % p for u, v in zip(R[i], R[r])]
            piv.append(c); r += 1
        free = [c for c in range(2*l) if c not in piv]
        if len(piv) != l: continue
        A = {f: [(-R[k][f]) % p for k in range(l)] for f in free}  # dense part, rows=free cols, cols=pivot cols
        for f1, f2 in combinations(free, 2):
            bucket = {}
            for k in range(l):
                if A[f2][k]: bucket.setdefault(A[f1][k]*pow(A[f2][k], -1, p) % p, []).append(k)
            for g in bucket.values():
                for k1, k2 in combinations(g, 2):
                    zeros += 1; S = [f1, f2]+[piv[k] for k in range(l) if k not in (k1, k2)]
                    sP = sum(ns[i] for i in S if typ[i] == 0); sQ = sum(ns[i] for i in S if typ[i] == 1)
                    if sQ % N and (sP*pow(sQ, -1, N)) % N == m: solved += 1
        tot += math.comb(l, 2)**2
    return p, N, l, tot, zeros, solved
for pb, npr in ((10, 4), (12, 5), (14, 6)):
    p, N, l, tot, z, s = run(pb, npr, 12, pb)
    print(f"p={p} N={N} l={l} minors tested={tot} zero minors={z} (random model {tot/N:.1f}) correct m recovered={s}; minors per hit={tot/max(z,1):.0f}, N={N}, sqrt(N)={N**.5:.0f}")
