"""Monte Carlo cross-check of the Pollard F/B abstraction (t3_kangaroo.pollard_C):
wild's first footprint >= w is at w+i with prob q(i) (renewal overshoot law), tame sits at w with i.i.d.
uniform jumps from {1,..,2^(nS-1)}; the trailing kangaroo always jumps; count wild jumps until it lands
on the tame's current position (or tame lands on wild's). Report E[wild jumps]/m. seed fixed."""
import numpy as np, math, sys
from t3_kangaroo import pollard_C
for nS in (6, 8, 10, 12):
    rng = np.random.default_rng(5 + nS)
    J = 2 ** np.arange(nS); m = J.mean(); M = J[-1]
    qi = np.array([np.sum(J > i) for i in range(M)], float); qi /= qi.sum()
    trials = 40000; acc = np.empty(trials)
    for t in range(trials):
        i = int(rng.choice(M, p=qi))
        wild = i; tame = 0; ws = 0
        while wild != tame:
            if wild < tame: wild += int(J[rng.integers(nS)]); ws += 1
            else: tame += int(J[rng.integers(nS)])
        acc[t] = ws
    r = acc / m
    print(f'nS={nS}: MC C={r.mean():.4f} +- {1.96*r.std(ddof=1)/math.sqrt(trials):.4f}   solver C={pollard_C(nS)[1]:.4f}')
