# SA-07 REPORT: mixed Z / F_p integer programming (SCIP) for Semaev decompositions

(Saved by the main session verbatim from the resumed executor's final message; the harness refused the executor's own write.)

## Summary
**Verdict: KILL** (frozen criterion: kill if all exponents ≥ 0.95). At m = 3, the node-count exponents in B, fitted with timeouts as lower bounds (Tobit), are:
- raw 7.6 [5.3, 10.8]
- LLL 8.6 [6.4, 13.4]
- Vieta 10.0 [7.7, 13.1]

(95% bootstrap CI.) At m = 2 they are 5.0 [2.9, 8.0], 6.0 [5.5, 6.5] and 11.4 [8.9, 16.5]. No formulation comes near the success threshold (< 0.85 with the CI excluding 1).

SCIP solved 0 of 76 m = 3 instances with B ≥ 32 and 0 of 89 m = 2 instances with B ≥ 128. Brute force would finish those boxes almost at once (m = 2: at most 1.3·10^5 points; m = 3: at most 3.6·10^5).

This is a toy-scale kill of SCIP branch-and-bound in double precision on these three formulations. It does not rule out an exact-arithmetic lattice-reduced branch-and-bound (Aardal–Hurkens–Lenstra / Coppersmith style); see Limitations. The run was interrupted and then resumed by a different model (DEVIATIONS.md, item 8).

## What was run
- **Instances.** Curve y^2 = x^3 + 7 over F_p, p = nextprime(2^bits + 7919·seed). Each instance plants P_1 + … + P_m = R with x(P_i) in [1, B] and gives the solver x(R). m = 2 uses S_3(x_1, x_2, x_R); m = 3 uses S_4 = Res_T(S_3(x_1, x_2, T), S_3(x_3, x_R, T)). Every planted solution was checked exactly and every SCIP solution re-verified in exact integers.
- **Formulations** (sa07.py, unchanged from the predecessor):
  - raw: S(x) − p·c = 0, with c a bounded integer (the carry).
  - lll: orbit-monomial sums written as z = u·Basis, Basis an LLL-reduced basis (fpylll) of {z : Σ c_λ z_λ ≡ 0 mod p}, column-scaled by the box bounds; SCIP branches on the integer coordinates u, with z_λ = m_λ(x) as a constraint.
  - vieta: variables are the elementary symmetric e_k; for m = 2 the constraint e_1^2 − 4e_2 = w^2 is added.
- **Solver settings.** SCIP via pyscipopt, one thread, CPU clock, stop at first solution.
- **Predecessor phase** (raw_m2/m3.jsonl, 264 rows): 5 s CPU cap, seeds 1–2, p ≈ 2^28, 2^32, 2^36, 2^40, B = 16..512 (m = 2) and 4..128 (m = 3).
- **Resume phase** (driver2.py, raw2_m2/m3.jsonl, 180 rows): 20 s CPU cap, seeds 3–5, p ≈ 2^28 and 2^36, B = 16..256 (m = 2) and 4..64 (m = 3). Both phases together span at least 4 doublings in B for every (m, formulation).
- **Analysis.** analyze2.py: Tobit fit of log2 nodes on log2 B with timeouts as lower bounds at the nodes reached, 300-replicate bootstrap over instances; also a solved-runs-only fit and per-B tables. analyze_quantile.py: a model-free lower bound on the exponent from quantiles of nodes and CPU time.
- **Totals:** 444 rows: 121 solved and verified, 272 timeouts, 17 SCIP false negatives, 34 skipped.
- **False negatives:** in all 17, SCIP returned "infeasible" although the planted solution re-verified exactly. Cause: double precision (this SCIP build has no GMP exact arithmetic).

## Results
### Exponent fits (nodes vs B, all rows pooled; fits_table.md)
| m | form | Tobit exponent [95% CI] | solved-runs-only fit [95% CI] | solved / timed-out points |
|--|--|--|--|--|
| 2 | raw | 5.03 [2.86, 7.97] | 1.93 [0.14, 3.79] | 21 / 39 |
| 2 | lll | 5.99 [5.49, 6.46] | 5.07 [4.24, 5.89] | 38 / 36 |
| 2 | vieta | 11.36 [8.85, 16.46] | 7.36 [5.70, 8.63] | 18 / 47 |
| 3 | raw | 7.63 [5.28, 10.82] | −0.56 [−2.27, 0.60] | 14 / 52 |
| 3 | lll | 8.57 [6.36, 13.38] | −2.18 [−5.68, 0.00] | 10 / 51 |
| 3 | vieta | 10.00 [7.73, 13.12] | 0.71 [0.00, 2.14] | 20 / 47 |

The solved-runs-only slopes at m = 3 are below 1 but are not a valid estimate: at large B the only solved runs are 1-node presolve or heuristic hits while the solved fraction falls to 0, so those slopes measure root-heuristic luck, not tree growth.

Model-free check (10% quantile of nodes, B from 4 to 64 at m = 3): lower bound 2.68 [2.68, 3.08] for raw and 3.25 [3.25, 3.57] for vieta. For lll it is not informative: 0.00 [−0.65, 2.34] by nodes and 0.61 [−0.74, 2.24] by time, because an lll node is an expensive LP and few nodes are reached before the cap.

### Solve rate and nodes vs box size (pooled; results_table.md)
| m | form | B: solved/run | min nodes at timeout ÷ box size |
|--|--|--|--|
| 3 | raw | 4: 6/14, 8: 5/13, 16: 3/13, 32: 0/11, 64: 0/8, 128: 0/7 | 163 at B = 4 (box 20) |
| 3 | lll | 4: 6/14, 8: 4/14, 16: 0/12, 32: 0/10, 64: 0/7, 128: 0/7 | 10.5 at B = 4 |
| 3 | vieta | 4: 10/14, 8: 7/14, 16: 3/13, 32: 0/11, 64: 0/8, 128: 0/7 | 2537 at B = 4 |
| 2 | raw | 16: 12/14, 32: 6/14, 64: 3/13, ≥128: 0/29 | 81 at B = 32 |
| 2 | lll | 16: 14/14, 32: 14/14, 64: 10/14, ≥128: 0/32 | — |
| 2 | vieta | 16: 13/14, 32: 2/14, 64: 3/13, ≥128: 0/28 | 321 at B = 16 |

At m = 3, B = 4 the box holds only 20 sorted triples, yet raw and vieta time out after 1.6·10^4 to 2·10^5 nodes. Nodes are not lattice points in the box: SCIP branches on the carry and on auxiliary variables with huge ranges, under severe numerical trouble. Runs either solve at about 1 node or time out; the regime where nodes track box lattice points never appears.

fig_nodes.png shows nodes vs B for each (m, formulation), marking solved runs, timeouts (lower bounds) and SCIP false-infeasible runs, with the box size C(B+m−1, m) for reference.

## Verdict reasoning
- **Success is not met.** Success needs an exponent < 0.85 with the CI excluding 1 for some formulation at m = 3. No estimator that handles timeouts correctly gives that; the only slopes below 1 come from the solved-runs-only fit, invalidated by selection bias (it discards 52, 51 and 47 timed-out runs).
- **Kill is met.** Under the primary estimator (Tobit), all six exponents are ≥ 5 and every CI lower bound is ≥ 2.86. For raw and vieta at m = 3 the model-free check independently gives an exponent ≥ 2.7.
- **The deciding m = 3 lll case rests on the Tobit model.** Its model-free bound is not significant, but it solved 0 of 36 runs at B ≥ 16, where the box has at most 816 points.
- **The prediction is not borne out.** The prereg predicted exponent 1.0 ± 0.05 with tree size equal to box lattice points. Measured trees are far larger, and failures appear at a fixed small B. Numerics drive the growth, not lattice counting.

## Limitations
- The SCIP build has no GMP: tolerances ~1e-10, double precision. Coefficient × monomial values exceed 2^70 for m = 2 and are far larger for m = 3 (S_4 total degree 12). That causes the 17 verified false negatives and probably most timeouts. An exact rational MINLP or a hand-written lattice-reduced branch-and-bound in exact integers might behave quite differently. This run measures off-the-shelf SCIP on these formulations, not the mathematical idea.
- Toy scale, small samples: 7–14 runs per (m, form, B), CPU caps 5 s / 20 s, contended host. The resume phase covered only p ≈ 2^28 and 2^36; pooling across primes assumes the exponent does not depend on p.
- Planting with replacement produces some degenerate instances at small B (repeated x, doubling relations), inflating 1-node solves there and biasing the fitted exponent upward. It cannot rescue success, since solved fractions are 0 at B ≥ 32.
- The Tobit model (log-normal nodes) fits the bimodal data poorly; read its point values (5–11) as "far above 1", not as precise exponents.
- The skip rule (34 rows) and the false negatives are excluded from the fits; both remove hard instances, biasing exponents downward and keeping the KILL conservative.
- The lll basis uses one weighting (scaling by the box bounds); other weightings and BKZ were not tried.
- This executor ran outside the repository per BRIEF rule 1, so no `.resume/RESUME.md` checkpoint was pushed before the resume runs.

## Suggested lead-atlas update
Add LEAD-ICE-mixed-integer-carry-formulation, disposition **killed (toy scale, off-the-shelf MINLP)**. Deciding numbers: at m = 3, Tobit node exponents raw 7.6 [5.3, 10.8], lll 8.6 [6.4, 13.4], vieta 10.0 [7.7, 13.1]; SCIP solved 0 of 76 instances with B ≥ 32 (box < 6·10^3 points) and gave 17 false negatives in double precision. Next action: reopen only with an exact-arithmetic branch-and-bound over lattice-reduced coordinates (no floating-point carry), which must first beat exhaustive enumeration of the box at m = 3, B = 16.

## Files
- sa07.py (instances and formulations); driver.py (predecessor phase); driver2.py (resume phase); analyze.py (superseded); analyze2.py, analyze_quantile.py (current analysis).
- raw_m2.jsonl, raw_m3.jsonl, raw2_m2.jsonl, raw2_m3.jsonl (raw rows).
- fits_table.md, results_table.md, fig_nodes.png, DEVIATIONS.md, d2.log, d3.log.
