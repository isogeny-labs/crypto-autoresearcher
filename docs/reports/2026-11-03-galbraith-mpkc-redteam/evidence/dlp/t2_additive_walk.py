"""Galbraith p.297 (end of 14.2.5): Brent-Pollard heuristic: expected cycle length of nS-adding walk is
sqrt(c pi r/2), c = nS/(nS-1), and the text says 'nS/(nS-1) is the variance of the in-degree ...
which is the same as the expected value of n(x) = #{y != x : walk(y)=walk(x)}'.
(1) exact in-degree law of an additive walk x -> x + s_{S(x)} on Z/N with S uniformly random:
    indeg(z) = #{j : S(z - s_j) = j}  ~ Binomial(nS, 1/nS)   (s_j distinct)  -> Var = (nS-1)/nS.
    We verify exactly by enumerating all S for tiny N, and compute E[n(x)].
(2) Monte Carlo of the rho length (#distinct points before first repeat) of additive walks on Z/N,
    seeds fixed, 95% CI, vs sqrt(pi N/2) * sqrt(nS/(nS-1)).
"""
import itertools, math, sys
import numpy as np
from fractions import Fraction

def exact_indegree(N, steps):
    nS = len(steps)
    tot_var = Fraction(0); tot_nx = Fraction(0); cnt = 0
    for S in itertools.product(range(nS), repeat=N):
        f = [(x + steps[S[x]]) % N for x in range(N)]
        indeg = [0] * N
        for x in range(N): indeg[f[x]] += 1
        mean = Fraction(sum(indeg), N)
        var = sum((Fraction(d) - mean) ** 2 for d in indeg) / N
        nx = Fraction(sum(indeg[f[x]] - 1 for x in range(N)), N)
        tot_var += var; tot_nx += nx; cnt += 1
    return tot_var / cnt, tot_nx / cnt

def rho_len_additive(N, nS, rng, trials):
    out = np.empty(trials)
    for t in range(trials):
        steps = rng.choice(np.arange(1, N), size=nS, replace=False)
        S = rng.integers(0, nS, size=N, dtype=np.int64)
        x = int(rng.integers(0, N)); seen = set()
        while x not in seen:
            seen.add(x); x = (x + int(steps[S[x]])) % N
        out[t] = len(seen)
    return out

def rho_len_random_map(N, rng, trials):
    out = np.empty(trials)
    for t in range(trials):
        x = int(rng.integers(0, N)); seen = set()
        # lazily sampled random function
        f = {}
        while x not in seen:
            seen.add(x)
            if x not in f: f[x] = int(rng.integers(0, N))
            x = f[x]
        out[t] = len(seen)
    return out

if __name__ == '__main__':
    print('== exact in-degree variance and E[n(x)] for additive walks (all S enumerated) ==')
    for N, steps in [(7, (1, 2)), (7, (1, 2, 4)), (8, (1, 3, 5, 6)), (9, (1, 2, 4))]:
        v, nx = exact_indegree(N, steps)
        nS = len(steps)
        print(f'N={N} nS={nS} steps={steps}: E[Var indeg]={float(v):.5f} E[n(x)]={float(nx):.5f}  '
              f'(nS-1)/nS={(nS-1)/nS:.5f}  nS/(nS-1)={nS/(nS-1):.5f}')
    print('  (population variance; Binomial(nS,1/nS) has Var=(nS-1)/nS; for a uniformly random map Var->1)')
    N = 1_000_003; trials = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    base = math.sqrt(math.pi * N / 2)
    print(f'\n== Monte Carlo rho length / sqrt(pi N/2), N={N}, trials={trials} per arm ==')
    rng = np.random.default_rng(20261103)
    r = rho_len_random_map(N, rng, trials) / base
    print(f'random map: mean={r.mean():.4f} +- {1.96*r.std(ddof=1)/math.sqrt(trials):.4f} (theory 1 - 1/(3 sqrt(piN/2)) ~ 1.000)')
    for nS in (3, 4, 6, 8, 16, 32):
        rng = np.random.default_rng(1000 + nS)
        r = rho_len_additive(N, nS, rng, trials) / base
        print(f'nS={nS:2d}: mean={r.mean():.4f} +- {1.96*r.std(ddof=1)/math.sqrt(trials):.4f}   '
              f'Brent-Pollard sqrt(nS/(nS-1))={math.sqrt(nS/(nS-1)):.4f}')
