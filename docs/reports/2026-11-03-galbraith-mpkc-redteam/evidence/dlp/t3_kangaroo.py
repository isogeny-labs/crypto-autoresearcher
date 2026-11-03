"""Kangaroo checks (Galbraith 14.5-14.6).
(a) Pollard's analysis p.309-310: solve the F/B recursions exactly (F(0)=B(0)=0: distance 0 = collision)
    for jumps {1,2,...,2^(nS-1)} and report C(nS) = sum_i q(i)F(i)/m ; book: 'between 1 and 1.06 when nS>=12'.
(b) Monte Carlo of Theorem 14.5.5 (vOW serial kangaroo, tame at floor(w/2), wild uniform in [0,w),
    alternate jumps, S a uniformly random function of the position, collision detected exactly i.e.
    theta=1 limit, so the 2/theta term is absent): total jumps / sqrt(w), claim 2+o(1).
(c) Lemma 14.6.5 index formula sign check (Pollard parallel version).
(d) Example 14.5.2 replay.
"""
import math, sys
import numpy as np

def pollard_C(nS):
    J = [2 ** j for j in range(nS)]; M = J[-1]; m = sum(J) / nS
    n = M  # unknowns F(1..M-1), B(1..M-1) ; distances after a swap are 2^j - i in [0, M-1]
    idx = lambda kind, i: (i - 1) + (0 if kind == 'F' else n - 1)
    A = np.zeros((2 * (n - 1), 2 * (n - 1))); rhs = np.zeros(2 * (n - 1))
    for i in range(1, n):
        rF = idx('F', i); rB = idx('B', i)
        A[rF, rF] += 1; A[rB, rB] += 1; rhs[rB] = 1.0
        for s in J:
            if s < i:
                A[rF, idx('F', i - s)] -= 1 / nS; A[rB, idx('B', i - s)] -= 1 / nS
            elif s > i:
                A[rF, idx('B', s - i)] -= 1 / nS; A[rB, idx('F', s - i)] -= 1 / nS
            # s == i: collision, F(0)=B(0)=0 contributes nothing
    sol = np.linalg.solve(A, rhs)
    F = lambda i: sol[idx('F', i)]
    q = lambda i: sum(1 for s in J if s > i) / (m * nS)
    C = sum(q(i) * F(i) for i in range(1, M)) / m
    return m, C

def kangaroo_mc(nS, trials, seed):
    rng = np.random.default_rng(seed)
    J = np.array([2 ** j for j in range(nS)]); m = J.mean(); w = int(round((2 * m) ** 2))
    res = np.empty(trials)
    for t in range(trials):
        # random selection function on positions [0, 4w] (kangaroos travel ~w/2)
        S = rng.integers(0, nS, size=40 * w + 10)
        tame = w // 2; wild = int(rng.integers(0, w))
        T = {tame}; W = {wild}; steps = 0
        if tame == wild: res[t] = 0; continue
        while True:
            tame += int(J[S[tame]]); steps += 1
            if tame in W: break
            T.add(tame)
            wild += int(J[S[wild]]); steps += 1
            if wild in T: break
            W.add(wild)
        res[t] = steps
    return w, res / math.sqrt(w)

if __name__ == '__main__':
    print('== (a) Pollard C(nS) with F(0)=B(0)=0 ==')
    for nS in range(3, 14):
        m, C = pollard_C(nS)
        print(f'nS={nS:2d} m={m:9.3f} C={C:.4f}  (1+C)={1+C:.4f}')
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    print(f'\n== (b) MC serial kangaroo, m=sqrt(w)/2 exactly, trials={trials} ==')
    for nS in (10, 12):
        w, r = kangaroo_mc(nS, trials, 77 + nS)
        print(f'nS={nS} w={w}: total jumps/sqrt(w) = {r.mean():.4f} +- {1.96*r.std(ddof=1)/math.sqrt(trials):.4f}  (claim 2+o(1); Pollard-model 1+C)')
    print('\n== (c) Lemma 14.6.5 index formulas ==')
    bad = 0; tot = 0
    for U, V in [(3, 4), (4, 5), (5, 7), (7, 9)]:
        w = 1000; h = w // 2
        for a in range(0, w):
            # tame i exponents h + iV + l UV ; wild j exponents a + jU + l UV ; meet iff h+iV == a+jU (mod UV)
            pairs = [(i, j) for i in range(U) for j in range(V) if (h + i * V - a - j * U) % (U * V) == 0]
            assert len(pairs) == 1
            i0, j0 = pairs[0]
            ib = ((h - a) * pow(V, -1, U)) % U; jb = ((a - h) * pow(U, -1, V)) % V
            tot += 1; bad += (ib, jb) != (i0, j0)
            if a == 1 and (U, V) == (3, 4):
                print(f'U=3,V=4,w=1000,a=1: true pair (i,j)={pairs[0]}, book formula gives ({ib},{jb}), '
                      f'sign-flipped formula gives ({((a-h)*pow(V,-1,U))%U},{((h-a)*pow(U,-1,V))%V})')
    print(f'book formula wrong in {bad}/{tot} cases (U,V,a) tested')
    print('\n== (d) Example 14.5.2 replay (p=263,g=3,h=181,w=53, jumps {1,2,4,8}, S(x)=x mod 4, D: 3|x) ==')
    p, g, h = 263, 3, 181
    x, a = pow(g, 26, p), 26; y, b = h, 0; T = {}; Wd = {}
    for i in range(10):
        if x % 3 == 0: T[x] = a
        if y % 3 == 0: Wd[y] = b
        common = set(T) & set(Wd)
        if common:
            z = common.pop(); print('collision at', z, 'log =', (T[z] - Wd[z]) % 131, 'check', pow(g, (T[z] - Wd[z]) % 131, p) == h); break
        sx = x % 4; x, a = x * pow(g, 2 ** sx, p) % p, a + 2 ** sx
        sy = y % 4; y, b = y * pow(g, 2 ** sy, p) % p, b + 2 ** sy
