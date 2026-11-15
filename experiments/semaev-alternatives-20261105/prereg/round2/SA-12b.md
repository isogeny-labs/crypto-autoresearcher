---
id: SA-12b
campaign: semaev-alternatives-20261105
round: 2
parent: SA-12
title: "Learned shift families at lattice dimension up to 300, with planted validation"
status: preregistered
frozen_on: 2026-11-07
executor_tier: sonnet, toy scale, shared 4-core host
results_path: experiments/semaev-alternatives-20261105/results/SA-12b/
---

# SA-12b

**Why round 2.** SA-12 capped lattice dimension at n ≤ 150, where every family sits far below 1/6 for size reasons, so the kill criterion could not be decided. Full-mode (non-convex, non-monomial) shifts were 0.003 above convex on one seed with unequal time.

**Protocol.**
1. Reuse `cert.py` and `search.py`. Run convex and full modes with identical wall-clock budgets (25 min each), 3 seeds each, at n ≤ 300, sequentially, single process.
2. Compute the exact convex optimum at the same n caps (SA-01's MILP is acceptable) so each search result has a matched reference.
3. Validate the best full-mode family by planted fpylll recovery at its certified δ, 64-bit p, 20 trials.

**Prediction (frozen).** Full mode never exceeds the matched convex optimum by more than 0.002 at any n; both approach 1/6 as n grows.

**Criteria (frozen).**
- SUCCESS: a full-mode family exceeds the matched convex optimum at the same n by > 0.005 on ≥ 2 of 3 seeds, confirmed by ≥ 10/20 planted recovery.
- KILL: at n ≤ 300 the best full-mode family is within 0.002 of (or below) the matched convex optimum on all seeds.
- INCONCLUSIVE: otherwise.
