---
id: SA-05b
campaign: semaev-alternatives-20261105
round: 2
parent: SA-05
title: "Kummer ladders with the global-relation floor subtracted"
status: preregistered
frozen_on: 2026-11-07
executor_tier: sonnet, toy scale, shared 4-core host
results_path: experiments/semaev-alternatives-20261105/results/SA-05b/
---

# SA-05b

**Why round 2.** SA-05 met its frozen success clause only through a fixed count of global (characteristic-0) relations, which the criterion did not subtract (ERRATA item 7). The real question, whether ladder structure helps random targets, was not answered.

**Protocol.**
1. Reuse SA-05's scripts and raw outputs; do not recompute finished cells.
2. For each (p, h) cell, split relations into global and wrapped (already classified). Define the corrected ratio as (wrapped relations) / (generic expectation N·B/M).
3. Push the comparison into the regime where generic relations exist at main scale: p ≈ 2^32, 2^36, 2^40 with h chosen so B ≥ p^{1/3} (B^3 ≳ p), 4 primes per p, structured base vs equal-size random base vs integer base.
4. Random-target arm: 10^5 targets per p, square-divisibility filter with the global-twist threshold, halving verification on every pass.

**Prediction (frozen).** Corrected ratio within [0.8, 1.25] at every p; random-target yield equal to the generic rate.

**Criteria (frozen).**
- SUCCESS: corrected ratio > 1.25 at every p with slope in log2 p > 0 and the bootstrap CI excluding 0, or random-target yield > 2× the generic rate with CI excluding 1.
- KILL: corrected ratio within [0.8, 1.25] at every p, and random-target yield not above the generic rate.
- INCONCLUSIVE: otherwise, with the scale reached.
