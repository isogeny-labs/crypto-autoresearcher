---
id: SA-08c
campaign: semaev-alternatives-20261105
round: 3
parent: SA-08b
title: "Resolve the excess-sign flag: K = 7, 8 and exact SVP checks"
status: preregistered
frozen_on: 2026-11-08
executor_tier: sonnet
results_path: experiments/semaev-alternatives-20261105/results/SA-08c/
---

# SA-08c

**Why round 3.** SA-08b's kill read the monotone-excess clause as a signed excess. In magnitude, the excess over the determinant threshold δ_K grows slightly (to 0.004) after crossing zero at 48 and 64 bits. Round 3 tests whether that magnitude keeps growing or stabilises.

**Protocol.**
1. Reuse SA-08b's `lam.py`. At 64 bits, extend to K = 7 and 8 (box support), 4 instances per δ point, grid step 0.005 near the crossing; BKZ-30 with mpfr where needed.
2. Exact SVP (fpylll `SVP.shortest_vector`) at K ≤ 4, 48 bits, to bound the BKZ-20 proxy error on λ₁ and λ₂ at the crossing.
3. Report the signed and absolute excess at every K, and the λ₂ crossing extrapolation with leave-one-out ranges over K = 3..8.

**Prediction (frozen).** The absolute excess stays ≤ 0.005 for K = 5..8; the crossing extrapolates to ≤ 1/6.

**Criteria (frozen).**
- SUCCESS: the crossing extrapolates to > 1/6 + 0.01 with the leave-one-out range above 1/6, or the excess becomes positive and grows with K beyond 0.01.
- KILL: absolute excess ≤ 0.005 at K = 7 and 8, and the extrapolation's leave-one-out range lies at or below 1/6 + 0.005.
- INCONCLUSIVE: otherwise.
