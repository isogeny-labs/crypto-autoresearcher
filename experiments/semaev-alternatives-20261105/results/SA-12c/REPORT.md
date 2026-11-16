# SA-12c report

## Summary
**Verdict: KILL** against the frozen criterion. With 3,000 episodes per run and 8 seeds per mode (n <= 200), mean(full - exact convex optimum) = -0.0058, bootstrap 95% CI [-0.0095, -0.0022]; the upper end is far below 0.005. No full run exceeds the convex reference (best full 0.13609 equals the reference). The frozen prediction also nearly holds: mean(full - convex) = +0.0010, CI [-0.0011, +0.0033] (contains 0, inside +-0.002 in mean), and full never exceeds the reference by > 0.002.

## What was run
- cert.py (sped up, output-identical, see DEVIATIONS) and the SA-12b EA (search3.py = search2.py with fixed episodes and a cache). Instance: 48-bit p, instance seed 1. 3,000 episodes per run, 8 seeds per mode, NCAP=200, interleaved order, single process, nice 10. All 16 runs completed with exactly 3,000 episodes.
- Convex reference: structured exhaustive grid (grid3.py), all 8 convex searches, and an exhaustive +-1 hill-climb (polish.py). Best = 0.13609 at n=169, layers [[5,0,5],[10,10,11],[8,8,12],[6,6,8],[4,4,9]] (t=4). Grid alone: 0.13333 (n=100).
- Planted recovery (plant.py) not run: precondition not met.

## Results (results_table.md, reach_by_seed.png)
| seed | convex | n | full | n | full-convex | full-ref |
|---|---|---|---|---|---|---|
| 0 | .12208 | 140 | .12524 | 143 | +.00316 | -.01086 |
| 1 | .12823 | 110 | .12810 | 90 | -.00013 | -.00799 |
| 2 | .12682 | 99 | .12302 | 168 | -.00381 | -.01308 |
| 3 | .13609 | 169 | .13609 | 169 | .00000 | .00000 |
| 4 | .12208 | 140 | .12454 | 130 | +.00246 | -.01155 |
| 5 | .12810 | 121 | .13554 | 121 | +.00744 | -.00056 |
| 6 | .13601 | 156 | .13454 | 167 | -.00147 | -.00156 |
| 7 | .13495 | 182 | .13538 | 182 | +.00044 | -.00071 |

Means: convex 0.12929 (sd 0.0058), full 0.13031 (sd 0.0056). Seed-to-seed spread (~0.006) again exceeds the thresholds, which is why 8 seeds and a bootstrap were needed; the CI of full-minus-reference still excludes 0 on the negative side. full > convex in 4/8 seeds; full > ref + 0.002 in 0/8.

## Verdict reasoning
KILL requires the upper 95% end of mean(full - exact convex optimum) < 0.005: it is -0.0022. SUCCESS requires mean > 0.005 with CI excluding 0: mean is -0.0058. The reference is a lower bound on the true convex optimum, which only makes full-minus-reference more favourable to full than reality, so the KILL is robust to this gap. The largest single paired gain (+0.0074, seed 5) is a convex-search shortfall (0.1281 vs the 0.1361 reference); full reaches 0.1355, still below the reference. Best full run (seed 3) is the same shift set as the best convex.

## Limitations
- One certification instance (48-bit p, S_3, cert.py asymptotic Howgrave-Graham metric); reach is a certificate bound, not measured recovery. Plateau 0.13-0.136, far below 1/6.
- Convex "exact optimum" is a best-found lower bound, not a proof (family too large for exhaustive search); n <= 200 only, TMAX=5 start, BMAX=9.
- Non-convex shift mutations are limited to the SA-12b operators (add/remove/swap in an 8-multiplier library); other learned families are untested.

## Suggested lead-atlas update
LEAD-EXO-ml-learned-models, lattice-design arm: close as negative for non-convex/non-monomial shift families on S_3 at n <= 200 under the cert.py metric. Deciding number: mean(full - best convex reference) = -0.0058, bootstrap 95% CI [-0.0095, -0.0022], 8 seeds x 3,000 episodes; max full = convex reference = 0.1361. Reopen only with a different shift-generation operator class or a different certification metric.
