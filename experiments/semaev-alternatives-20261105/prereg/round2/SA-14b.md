---
id: SA-14b
campaign: semaev-alternatives-20261105
round: 2
parent: SA-14
title: "PKM tower F4 degree at tower length 10–12, and m = 3 towers"
status: preregistered
frozen_on: 2026-11-07
executor_tier: sonnet, toy scale, shared 4-core host
results_path: experiments/semaev-alternatives-20261105/results/SA-14b/
---

# SA-14b

**Why round 2.** SA-14 measured F4 degree 4,4,4,4,4,5,5,5,5 at t = 1..9 (m = 2, q = 2). A single step cannot separate slope 1/4 from a slower slope or a plateau. SA-14 named t = 10 as the deciding cell.

**Protocol.**
1. msolve on SA-14's encoding at t = 10, 11, 12 (m = 2, q = 2), 3 seeds each, single thread, memory capped near 2 GB; record the max degree and largest matrix.
2. m = 3 Kummer towers at t = 1..6 (q = 2), 2 seeds each.
3. Matched random-support null at the same t (as SA-11 did) for the new cells.

**Prediction (frozen).** The repository fit 4 + ⌊(t − 2)/4⌋ gives degree 6 at t = 10.

**Criteria (frozen).**
- SUCCESS: degree stays 5 at t = 10, 11 and 12 on all seeds (plateau or slower slope than 1/4), which reopens the tower route.
- KILL: degree reaches 6 at t = 10 on all seeds and the null matches the real tower degree.
- INCONCLUSIVE: mixed seeds, or the t = 10 cell does not finish within the memory cap.
