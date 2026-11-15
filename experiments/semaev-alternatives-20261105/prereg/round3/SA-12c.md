---
id: SA-12c
campaign: semaev-alternatives-20261105
round: 3
parent: SA-12b
title: "Learned shift families with equal episode budgets and enough seeds to beat search noise"
status: preregistered
frozen_on: 2026-11-08
executor_tier: sonnet
results_path: experiments/semaev-alternatives-20261105/results/SA-12c/
---

# SA-12c

**Why round 3.** SA-12b's seed-to-seed search spread (~0.007) exceeded its 0.002 and 0.005 thresholds, and wall-clock budgets gave 477 to 16,930 episodes per run.

**Protocol.**
1. Reuse `cert.py`, `search2.py`. Fix the budget by episodes, not time: 3,000 episodes per run, n ≤ 200, 8 seeds per mode (convex, full), interleaved, single process.
2. Compute the exact convex optimum at the same n caps by exhaustive search over the convex family's parameter grid under the cert.py metric.
3. Paired comparison per seed; bootstrap 95% CI of mean(full − convex) and of mean(full − exact convex optimum).
4. If SUCCESS's precondition holds, run plant.py at the best full family's δ, 20 trials.

**Prediction (frozen).** Mean(full − convex) within ±0.002 and CI containing 0; full never exceeds the exact convex optimum by > 0.002.

**Criteria (frozen).**
- SUCCESS: mean(full − exact convex optimum) > 0.005 with 95% CI excluding 0, confirmed by ≥ 10/20 planted recovery.
- KILL: 95% CI of mean(full − exact convex optimum) has upper end < 0.005.
- INCONCLUSIVE: otherwise.
