# SA-24c audit (main session, 2026-11-12)

**Part 1: SA-24's frozen verdict completes to KILL, as the executor states.** **Part 2: DEVIATES, as the executor states.** The deviation is a wrong prediction in the SA-24c prereg (ERRATA 10), not a gain from the cover.

## Part 1, recomputed from the raw block files

Fresh events (unweighted hits) against the conditional expectation are summed over blocks and curves. For genus 2 the expectation is events_per_trial × trials, and the audit checked that set size = M(M+1)/2. For genus 3 it is Σ setsum × D / p^2 over the c2 strata actually drawn.

| arm | log2 p | delta | fresh hits | expected | ratio | failed root checks |
|---|---|---|---|---|---|---|
| A2 | 20 | 0.3 | 214 | 221.1 | 0.968 | 0 |
| A2 | 24 | 0.3 | 96 | 93.7 | 1.025 | 0 |
| A2 | 24 | 0.4 | 240 | 221.1 | 1.085 | 0 |
| A2 | 24 | 0.5 | 1178 | 1122.0 | 1.050 | 0 |
| A3 | 16 | 0.5 | 212 | 220.7 | 0.961 | 0 |
| A3 | 20 | 0.5 | 213 | 221.6 | 0.961 | 0 |
| A3 | 20 | 0.6 | 213 | 195.7 | 1.089 | 0 |

- These agree with the executor's table.
- The filter validations (identical-stream flags, 0 mismatches in 1.4e9 trials; genus-3 root-finding check on 5.1e6 u's; exhaustive cases) were read in `val1-3.jsonl`.
- With every cell powered, the KILL clauses hold: all 43 pooled cells are in [0.96, 1.15], and both per-genus slope CIs contain 0.
- The SA-24 deficit at (2^24, 0.5), 0.845, was noise: the fresh ratio is 1.050.
- **SA-24: KILL.**

## Part 2: why alpha is 1, not 4/3

- **Raw rows at delta 0.9, n = 63.** OLS of counted cost on log2 p gives 1.008. Trials alone give 1.099, matching 2 - delta = 1.1. Trials per p grow from 1.02 to 2.30 across 2^10..2^22. Rate/null is 0.999 to 1.008. The linear-algebra share of cost falls from 3.9% to 1.3%.
- **Positive control** (`p2_control.jsonl`): 108 runs, 39,156 relations, 0 violations of the true logs, 108 of 108 solved.
- **Mechanism.** Every genus-2 relation has exactly two factor-base unknowns. The relation matrix is the incidence matrix of a graph, so it is solved by propagation in linear time with no dense phase. Cost is then trials alone: about (|F|/2) / (2B^2/p^2), so p^(2 - delta). That decreases toward p as delta tends to 1, and the optimum lies at the scan boundary.
- The frozen prediction of 4/3 assumed linear algebra quadratic in |F| (the textbook basic-algorithm balance). That is wrong for genus 2 (ERRATA 10).
- **Not a gain.** p^1 is the bound p^(2-2/g) stated in the SA-24 prereg, reached and not beaten. Cost is 1.5 to 2.5 times the degenerate A1 and 3 to 5 orders of magnitude above rho on E1 (alpha 0.5). In the Jacobian's own terms, p^1 equals rho on a genus-2 Jacobian (q^(g/2)). The cover only adds work for a target of size p.

## Caveats

- The (2^24, 0.3) cell rests on 74 and 78 of 100 blocks for two of its three curves (time limit). The completed blocks are independent samples.
- The cost slope at fixed delta (1.008) is below the trials slope (1.099) because the measured Jacobian-to-E1 cost ratio drifts with size. Trials counts are the cleaner quantity, and they match 2 - delta.
