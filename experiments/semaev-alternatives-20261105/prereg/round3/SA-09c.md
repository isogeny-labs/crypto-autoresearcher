---
id: SA-09c
campaign: semaev-alternatives-20261105
round: 3
parent: SA-09b
title: "Heegner relations at conductor bounds 1000–2000, a second non-CM curve, and descent where hits are rare"
status: preregistered
frozen_on: 2026-11-08
executor_tier: sonnet
results_path: experiments/semaev-alternatives-20261105/results/SA-09c/
---

# SA-09c

**Why round 3.** SA-09b's kill rests on the largest bound reached (B = 500); the ratio saw-tooths and hit 0.151 at B = 300. The descent test ran where control hit rates were 0.2–0.45, so it had little power.

**Protocol.**
1. 37a1 with K = Q(√−7): extend the class-group rank pipeline (`arith.py`, `rank_arith2.py`) to B = 750, 1000, 1500, 2000 within the memory cap; random-projection rank with two independent primes per point.
2. A second non-CM curve, 43a1 or 53a1, with an h = 1 or 2 field satisfying the Heegner hypothesis: rank/points up to B = 1000.
3. Descent at a rare-hit scale: p ≈ 2^30 on 37a1, splitting completely in the ring class field used, Heegner set of the conductors verified so far, 2·10⁴ targets per prime, 3 primes, random-set control. Report hit rate with exact counts.

**Prediction (frozen).** rank/points stays in [0.12, 0.15] for B ≥ 750 on 37a1 and below 0.15 on the second curve; descent hit rate equals control.

**Criteria (frozen).**
- SUCCESS: rank/points ≥ 1/2 at any B ≥ 750, or a descent hit rate above control with a 95% CI excluding equality.
- KILL: rank/points < 0.15 at every B ≥ 750 on 37a1 and at the largest B on the second curve, and descent not above control.
- INCONCLUSIVE: otherwise.
