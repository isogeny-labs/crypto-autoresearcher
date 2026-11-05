# SA-12 report (written by the main session from the executor's hand-back; the executor stopped before writing it)

## Summary
**Verdict: INCONCLUSIVE (incomplete run, scale-limited).** No certified reach reached the frozen success threshold 1/6 + 0.01 = 0.1767. The kill criterion (best certified reach ≤ 1/6) is not decided, because every search was capped at lattice dimension n ≤ 90, where all shift families sit below 1/6 for size reasons alone.

## What was run
- `cert.py`: certified-reach calculator for shift families on S_3(x1, x2, x_R) mod a 48-bit prime, curve y² = x³ + 7. It computes the exact p-adic Smith-form determinant exponent e of the shift lattice and reports δ* = (t·n − e)/D from the Howgrave-Graham condition. It supports non-monomial multipliers (x1 − x2), f(x1), f(x2), x1 + x2, x1·x2.
- `search.py`: CPU search over shift families (evolutionary, simulated annealing, random), 2,000 episodes per run, in two modes. "Convex" uses monomial box-type shifts only; "full" adds non-convex and non-monomial shifts.

## Results (surviving numbers; first-batch log files were deleted by the executor on restart)
| Search | Mode | Seeds | Best certified reach | Dimension of best |
|---|---|---|---|---|
| Evolutionary | convex | 5 | 0.111–0.116 (best 0.11607) | n = 64, t = 2 |
| Evolutionary | full | 2 | 0.1111, 0.1105 | n = 48, 70 |
| Evolutionary (2nd batch, 1st seed) | convex / full | 1 each | 0.1111 / 0.1111 | n ≤ 90 |
| Plain box shifts (`cert.py` self-check) | — | — | 0.09–0.10 | n = 25–81 |

Within the n ≤ 90 cap, non-convex and non-monomial shifts gave no gain over convex shifts.

## Verdict reasoning
The success criterion needs a certified reach above 0.1767. The best observed value is 0.116. The kill criterion needs evidence that the optimum over all families is at most 1/6, which requires dimensions large enough for the convex optimum to approach 1/6 (n of a few hundred). That was not reached, so no kill.

## Limitations
- Dimension cap n ≤ 90. Host shared by 18 executors.
- No planted-instance LLL validation of the best family; no confidence intervals; first-batch raw logs lost.
- No comparison with SA-01's certificate.

## Suggested lead-atlas update
None. LEAD-EXO-ml-learned-models (lattice-design arm) stays as is. Re-run with n up to about 300 on a dedicated host before any disposition change.


## Addendum: n <= 150 run (executor, after main-session edit)
Single seed each, sequential. Evolutionary search, NCAP=150, BMAX=7, TMAX=5, wall-clock caps 1100 s (full; stopped itself at 594 s of 2000 episodes' worth or earlier) and 400 s (convex).
- convex: best certified reach 0.12407 (n=72, t=3)
- full (non-convex + non-monomial shifts): best certified reach 0.12682 (n=99, t=3, 26 non-monomial shifts)
Both are far below 1/6 = 0.1667 and the success threshold 0.1767. Verdict unchanged: INCONCLUSIVE at scale n <= 150. The 0.0027 full-over-convex difference is one seed, unequal time budgets, finite dimension, and not validated by planted LLL recovery; it is not evidence that a non-convex family beats the convex ceiling asymptotically. The episode count actually completed in the wall-clock caps was not recorded (curves in out_ea_*_n150.json). Table: results_table.md. No figure was produced.
