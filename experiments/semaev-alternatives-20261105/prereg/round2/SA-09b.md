---
id: SA-09b
campaign: semaev-alternatives-20261105
round: 2
parent: SA-09
title: "Heegner norm relations beyond the CM toy: more conductors, a second field, and a descent test"
status: preregistered
frozen_on: 2026-11-07
executor_tier: sonnet, toy scale, shared 4-core host
results_path: experiments/semaev-alternatives-20261105/results/SA-09b/
---

# SA-09b

**Why round 2.** SA-09 measured rank/points 0.238 at conductors {1,5,7,35} on the CM curve 36a1 with one field, and extrapolated ~0.07 conjecturally. The non-CM case and the descent question (obstruction iii) were untested.

**Protocol.**
1. Non-CM curve: 37a1 (y² + y = x³ − x, rank 1, conductor 37) or 11a1 if 37a1 is too costly. Choose K with the Heegner hypothesis and class number ≤ 5, two inert primes ℓ₁, ℓ₂ with a_ℓ ≠ 0. Compute Heegner points at conductors {1, ℓ₁, ℓ₂, ℓ₁ℓ₂} as in SA-09, reduce mod 3 primes splitting completely, verify every norm relation exactly in E(F_p), and report rank/points.
2. Second field for 36a1 (a different K with h ≤ 5) at conductors up to the largest the host allows in 60 minutes, to measure the ratio at a second data point per conductor bound.
3. Descent test: for 1,000 random targets R per prime, measure whether R decomposes as a short sum over the Heegner points (sum of ≤ 3 points, signs allowed) more often than over a random point set of equal size.

**Prediction (frozen).** Non-CM rank/points ≤ 0.3 and decreasing with conductor; descent hit rate equal to the random-set control.

**Criteria (frozen).**
- SUCCESS: rank/points ≥ 1/2 at the largest conductor bound on either curve, or a descent hit rate above the random control with a 95% CI excluding equality.
- KILL: rank/points < 0.15 at the largest conductor bound on the non-CM curve with a decreasing trend over ≥ 3 conductor bounds, and descent hit rate not above control.
- INCONCLUSIVE: otherwise.
