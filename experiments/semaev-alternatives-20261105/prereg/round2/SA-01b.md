---
id: SA-01b
campaign: semaev-alternatives-20261105
round: 2
parent: SA-01
title: "Certified ceilings for the norm and chained presentations at m = 3, and m = 4 lattices at t ≥ 2"
status: preregistered
frozen_on: 2026-11-07
executor_tier: sonnet, toy scale, shared 4-core host
results_path: experiments/semaev-alternatives-20261105/results/SA-01b/
---

# SA-01b

**Why round 2.** SA-01 was INCONCLUSIVE because (iii) the Riemann–Roch norm system and (iv) chained S_3 were only computed at t ≤ 3 for m = 3 (all 0), the m = 4 lattice reached t = 1, and the certificates came from substitute tools.

**Protocol.**
1. Make one more honest attempt to install `cuso` (Ryan, EUROCRYPT 2025; artifact at artifacts.iacr.org/eurocrypt/2025/a13) or the sumset bound calculator (ePrint 2024/1330). If both fail within 30 minutes, write a non-relaxed upper bound instead: the exact MILP of SA-01 extended to t = 4..6 for (iii) and (iv) at m = 3, using Gröbner-basis generators (as SA-01 did for (iii) at m = 2), plus the SA-06 polytope formula applied to the elimination ideal.
2. Extend (i) at m = 4 to t = 2, 3 with the exact MILP.
3. Planted fpylll recovery for (iii)-Gröbner and (iv) at m = 3 at the best certified δ, 64- and 96-bit p, 20 trials per cell.

**Prediction (frozen).** (iii) and (iv) converge to the single-polynomial value 1/24 at m = 3; (i) at m = 4 tracks toward 1/80.

**Criteria (frozen).**
- SUCCESS: any presentation certifies reach > 1/24 + 0.005 at m = 3 (or > 1/80 + 0.002 at m = 4), confirmed by ≥ 10/20 planted recovery at that δ.
- KILL: (iii) and (iv) at m = 3 certify a finite-t sequence whose 1/t extrapolation lies within 0.005 of 1/24, or below it, with a leave-one-out range inside that band.
- INCONCLUSIVE: anything else, with the t reached.
