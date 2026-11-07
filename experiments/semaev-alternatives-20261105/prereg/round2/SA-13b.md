---
id: SA-13b
campaign: semaev-alternatives-20261105
round: 2
parent: SA-13
title: "Closing the lattice-query lower bound: the volume step, moduli p^k, and structured enumeration"
status: preregistered
frozen_on: 2026-11-07
executor_tier: sonnet, toy scale, shared 4-core host
results_path: experiments/semaev-alternatives-20261105/results/SA-13b/
---

# SA-13b

**Why round 2.** SA-13 proved a restricted lower bound (cost Ω(p^{7/9}) per relation for one congruence mod p in the 3-dimensional form lattice) with one step, the volume inequality c(W) ≤ C·∏W^{2/9}, only sketched. The gaps to the conjecture are moduli p^k, several congruences, and structured search inside the lattice.

**Protocol.**
1. Prove or refute the volume inequality. Check it numerically on all weight boxes W up to the largest the host enumerates in 30 minutes; report the worst ratio.
2. Extend the sparsity and list-length lemmas to modulus p² (Coppersmith level 2). Measure equidistribution of T ↦ g(T) mod p² for planted forms by brute force at p ≈ 10^4, and prove the best bound you can.
3. Structured enumeration: implement the best known enumeration of short vectors of L_R with square leading coefficient (Fincke–Pohst restricted to squares) and measure its cost exponent in B at 40–64 bits; compare with the p^{7/9} bound.

**Prediction (frozen).** The volume inequality holds; the mod p² extension loses at most a constant in the exponent; structured enumeration costs at least B^1.

**Criteria (frozen).**
- SUCCESS: a complete proof (every step proved) of the restricted bound for modulus p and p², or a structured enumeration with exponent < 1 in B (95% CI excluding 1), which would contradict the conjecture.
- KILL: a counterexample to the volume inequality that breaks the restricted bound, with no repair.
- INCONCLUSIVE: otherwise, with each step's status.
