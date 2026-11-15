---
id: SA-08b
campaign: semaev-alternatives-20261105
round: 2
parent: SA-08
title: "First-minimum bound for the Rees lattice: does any auxiliary-polynomial method pass 1/6?"
status: preregistered
frozen_on: 2026-11-07
executor_tier: sonnet, toy scale, shared 4-core host
results_path: experiments/semaev-alternatives-20261105/results/SA-08b/
---

# SA-08b

**Why round 2.** SA-08 proved the 1/6 and 1/24 ceilings for determinant (Minkowski) arguments only, which are sufficient, not necessary. At small shift depth the measured reach (0.126 at K = 1) exceeded the determinant prediction (0.056), so the gap between the Gaussian heuristic and the true first minimum is real and unmeasured.

**Protocol.**
1. For the Rees lattices of SA-08 (S_3, m = 2, K = 1..6, all down-closed supports up to the dimension the host allows), compute exactly, on planted and on random (no-solution) instances at 48–96 bits: λ_1 and λ_2 of the reduced basis (BKZ-20 as a proxy where exact SVP is too costly), the determinant-predicted λ, and the ratio.
2. Fit the δ at which λ_2 of the planted lattice crosses the Howgrave-Graham bound, per K, and extrapolate in 1/K.
3. Write the strongest successive-minima argument you can (Zhang-type or Banaszczyk transference) for why λ_2 cannot beat the determinant bound asymptotically, marking every step proved, sketched or conjectured.

**Prediction (frozen).** The λ_2 crossing extrapolates to 1/6; the small-K excess is a finite-size effect that vanishes as K grows.

**Criteria (frozen).**
- SUCCESS: the λ_2 crossing extrapolates to > 1/6 + 0.01 with a leave-one-out range above 1/6, or a written argument shows a family of auxiliary-polynomial lattices whose first minima beat the determinant bound by a factor that grows with K.
- KILL: the λ_2 crossing extrapolates within 0.01 of 1/6 or below, and the excess over the determinant prediction shrinks monotonically in K.
- INCONCLUSIVE: otherwise.
