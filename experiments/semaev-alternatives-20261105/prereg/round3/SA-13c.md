---
id: SA-13c
campaign: semaev-alternatives-20261105
round: 3
parent: SA-13b
title: "The two open proof steps for the modulus-p² lattice-query bound"
status: preregistered
frozen_on: 2026-11-08
executor_tier: fable (theory)
results_path: experiments/semaev-alternatives-20261105/results/SA-13c/
---

# SA-13c

**Why round 3.** SA-13b closed the volume step and completed the restricted bound at modulus p for per-target non-adaptive queries. The p² extension has two named gaps: (a) classifying certificates for (S², pS, p²) without the no-wraparound hypothesis H-sep; (b) coverage for the k* = 1 branch with general (non-monomial) multipliers q(T).

**Protocol.**
1. Attempt (b) first: bound the number of x in a box for which some nonzero q(T)·S_3(x, T) lies in W/p, for deg q ≤ 2. Use the structure of S_3's coefficients (content lemma, N0) and a Bombieri–Pila or determinant-method count; check numerically on all boxes reachable in 30 minutes.
2. Attempt (a): remove H-sep, or prove a weaker statement that suffices for the cost bound.
3. Attempt the numerical volume inequality c₂ ≤ C·ω^{1/15} for the S_3² certificate as a proof.
4. Mark every step proved, sketched or conjectured; give numerical checks for every computable consequence.

**Prediction (frozen).** (b) holds with exponent ≥ 1/15 and the level-2 bound Ω(p^{13/15}) follows conditionally on (a).

**Criteria (frozen).**
- SUCCESS: complete proofs of (a), (b) and the 1/15 volume inequality, giving Ω(p^{13/15}) for modulus p², or a construction giving a structured search with cost exponent < 1 in B (which would refute the conjecture).
- KILL: a counterexample family showing level-2 coverage ≥ ω^{c} with c giving cost below p^{7/9}, with no repair.
- INCONCLUSIVE: otherwise, with each step's status.
