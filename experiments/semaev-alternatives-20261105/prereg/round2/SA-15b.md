---
id: SA-15b
campaign: semaev-alternatives-20261105
round: 2
parent: SA-15
title: "Run every calibrated decomposition solver on the frozen m = 4 instance set"
status: preregistered
frozen_on: 2026-11-07
executor_tier: sonnet, toy scale, shared 4-core host
results_path: experiments/semaev-alternatives-20261105/results/SA-15b/
---

# SA-15b

**Why round 2.** SA-15's criterion was adoption by later runs. This round adopts the instance set: every solver the campaign built is scored on the same 400 planted m = 4 instances (SHA-256 e9b681a6…, B = p^{1/5}).

**Protocol.**
1. Load `results/SA-15/instances.json`; verify its SHA-256.
2. Solvers, each with a per-instance cap of 60 s at p ≈ 2^40 and 2^56 (2^72 and 2^96 only if a solver recovers anything at 2^56):
   - pair-table meet-in-the-middle (generic baseline, cost ≈ B²);
   - S_5 lattice at the largest shift depth the host allows (SA-01 / SA-06 construction);
   - Vieta-graded lattice (SA-01 (ii));
   - SA-16's calibrated lattices (vieta_cvp, L2diag) as positive-control reference;
   - msolve on the norm presentation (SA-04) with the vanishing-polynomial base.
3. Report recovery rate, cost per instance and cost relative to matched rho (sqrt(πN/4)) per solver and size.

**Prediction (frozen).** Only the generic pair table recovers instances, at cost ≈ B² ≫ the p^{1/10} break-even; every algebraic solver recovers 0.

**Criteria (frozen).**
- SUCCESS: any non-generic solver recovers ≥ 10% of instances at p ≈ 2^56 at cost below the pair table.
- KILL: every non-generic solver recovers 0 at p ≈ 2^40 and 2^56.
- INCONCLUSIVE: otherwise.
