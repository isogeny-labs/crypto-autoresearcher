# SA-24 REPORT: factor base in Jac(C) of bielliptic genus-2 / genus-3 covers

## Verdict: INCONCLUSIVE (literal reading of the frozen criteria)

Deciding numbers
- SUCCESS not met. (i) A1 alpha CI is entirely above rho's, not below: A1 0.865 [0.821, 0.923] vs rho 0.344 [0.293, 0.395] (sizes 2^10..2^20, counted E1-addition equivalents; bootstrap 2,000, seed 24). (ii) Splitting-ratio slope against log2 p, pooled per genus: genus 2 -0.0040 [-0.0142, +0.0027]; genus 3 -0.0007 [-0.0096, +0.0076]. Neither CI is above 0; no per-delta slope CI is above 0.
- KILL, first half met: A1 alpha CI entirely above rho's (also for 2^10..2^24, 2^14..2^24, fixed delta, wall time, raw Jacobian-add counts).
- KILL, second half NOT met literally: it requires measured/null in [0.5, 2] at EVERY A2 and A3 cell. Two cells are outside, both unmeasurable: A2 p=2^24, delta=0.3 (observed 4, expected 1.05, ratio 3.8; Poisson P(>=4 | 1.05) = 0.02) and A3 p=2^20, delta=0.5 (observed 0, expected 0.35, ratio 0). Reaching 50 expected hits there would need ~3e11 and ~4e10 trials. Also the A2 per-delta slope at delta=0.5 has CI [-0.035, -0.002], which excludes 0 (negative, driven by one cell, p=2^24 delta=0.5, ratio 0.845 [0.721, 0.979]).
- FLAGGED, NOT RESOLVED: if only the 26 of 28 (A2) and 12 of 15 (A3) cells with at least 50 expected hits are counted, and the pooled slopes are the "slope CIs", every KILL condition holds. The frozen text says "every cell", so the verdict is INCONCLUSIVE. The data point to KILL.

Structural result (found while building the executor, so it is stated outside the frozen criteria). A relation in A1 needs R_j = a pb(P) + b pb(Q) = pb(T) with T in E1, so a relation is a point T of E1 with x(T) = x0^2, |x0| <= B. Each relation constrains only the sum l(Q) + l(sigma Q) of two factor-base logs, and carries a single unknown plus k. The "Jacobian" relation search is therefore a hit-the-small-set search on E1, with probability about B/p per trial; |F|/2 + 10 relations cost about p trials for every B. A2/A3 are identities for uniform elements (see below), so they cannot show an excess.

## What was run (all in /home/user/semaev-runs/SA-24/)
Facts (step a), `results/facts.jsonl`, `results/facts_g3check.jsonl`:
- 24 A1 curves (8 sizes x 3), p = largest prime < 2^k with p = 3 mod 4, k = 10,12,...,24. #Jac(C)(F_p) = #E1 * #E2 confirmed against the Frobenius polynomial of the odd quintic at p = 1009, 65537 and every A1 instance with k <= 16. n1 = largest prime factor of #E1, cofactor <= 16, n1 not dividing #E2 and n1 || #Jac; factorisations are in `results/facts.jsonl`.
- Exact pullback homomorphism, no sign slack, in Sage: pb(P+Q) == pb(P)+pb(Q) on 199/199 (p=1009), 200/200 (65537) and 99-100/100 for each A1 instance with k <= 16. `only_up_to_sign` was 0 in every case. In C: 991/991 (k=10) and 998/998 (k=16), plus u | Fz - v^2 for every pullback.
- Genus 3: C3: y^2 = g4(x^2), odd degree-7 model via x = r + 1/z. Direct Frobenius polynomial of the odd model equals P_E1 * P_H at p = 211, 307, 1009 (2 curves each); #Jac(C3) = #E1 * #Jac(H) there (and p^2+1-trace(F^2) agrees). 9 curves for A3 (p = 2^12, 2^16, 2^20) use that decomposition.
Cantor in C (step b): generic Cantor, cross-checked against Sage on 1250 random operations (5 primes up to 1.6e7; 250 doublings, 125 sums that are the identity, weight-1 and weight-0 operands): 0 mismatches (`results/cantor_crosscheck.txt`).
Splitting law (step c): sampler validated by exhaustive enumeration of every u (g=2: p=1019, 4091; g=3: p=211, 307): the weight sum equals N_g and every split numerator equals the combinatorial null exactly at all delta (`results/exact_*.jsonl`).
- A2: 4 sizes x 3 curves x 2e9 trials, delta = 0.3..0.9. A3: 3 sizes x 3 curves x 1e8 trials, delta = 0.5..0.9.
- Fibre control: 2e8 uniform affine E1 points per curve, 12 curves, all deltas; 28 of 28 (p, delta) cells have >= 50 expected hits; ratio observed/null between 0.997 and 1.004, |z| <= 1.9.
A1 + rho (step d): per size 3 curves x 3 targets; delta scanned 0.30..0.95 in steps of 0.05 for 2^10..2^22, and {0.5,0.6,0.7,0.8,0.9,0.95} at 2^24. 936 A1 runs: all runs that reach their target solve k and pass [k]P = Q (30 runs fail, all at delta <= 0.4 with p <= 2^16, zero relations because no factor-base point lies in the n1-subgroup; logged, and a delta is used in an optimum only if all 9 instances solved). Zero relation-verification failures (every counted relation is checked as Q1 + Q2 == R by a Jacobian addition; walk bookkeeping is checked every 1000th relation). Rho: DP rho with negation map, 8 sizes x 15 solves, all solved.
Conversion to E1-addition equivalents: ratios measured by in-process micro-benchmarks run before and after each (size, curve) batch, same C code, same host (load 2.6-3.0 at the time; 4 cores shared with 2 other executors). Means: Jacobian add = 22.0 E1 adds (range 16-35), Legendre 1.21, sqrt 1.08, inversion 0.80, mulmod n1 0.071. Linear algebra counted at 1 multiply-add each.
Bug fixes during the run (superseded results kept, not used): a wrong Horner form in the fibre sampler (null was correct) and a possible identity in the walk table at small n1. Everything affected was re-run. See DEVIATIONS.md (13 items).

## A1 and rho
| log2 p | p | opt delta | B | F | mean trials / p | A1 cost (E1-add eq, geomean, n=9) | early-solve cost | rho E1 adds (geomean, n=15) | A1 wall s | rho wall us |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 1019 | 0.65 | 90 | 178 | 1.04 | 3.62e+04 | 1.89e+03 | 98 | 0.003 | 23 |
| 12 | 4091 | 0.45 | 42 | 96 | 0.93 | 1e+05 | 7.84e+03 | 128 | 0.009 | 21 |
| 14 | 16363 | 0.65 | 548 | 1064 | 0.96 | 3.83e+05 | 5.33e+03 | 143 | 0.043 | 25 |
| 16 | 65519 | 0.65 | 1350 | 2670 | 1.01 | 1.79e+06 | 1.67e+04 | 256 | 0.173 | 40 |
| 18 | 262139 | 0.4 | 147 | 256 | 0.87 | 4.92e+06 | 1.56e+05 | 491 | 0.565 | 75 |
| 20 | 1048571 | 0.55 | 2047 | 4174 | 0.94 | 2.16e+07 | 1.94e+05 | 1045 | 2.518 | 163 |
| 22 | 4194287 | 0.45 | 955 | 1906 | 0.91 | 9.3e+07 | 1.34e+06 | 2037 | 10.479 | 325 |
| 24 | 16777199 | 0.7 | 114104 | 228821 | 0.98 | 3.38e+08 | 5.01e+05 | 3063 | 46.255 | 489 |

Note the cost per trial is dominated by one generic-Cantor Jacobian addition (22 E1-add equivalents); explicit formulas would be several times cheaper. This scales A1 by a constant and does not move alpha.

Fits (log2 cost on log2 n1, resampling instances within each size, bootstrap 2,000, seed 24; "opt" re-selects the best delta per size inside each resample):

| variant | sizes | A1 alpha (95% CI) | rho steps alpha | rho wall alpha |
|---|---|---|---|---|
| 2^10..2^20 (prereg sizes), primary | 10-20 | 0.865 [0.821, 0.923] (n=54) | 0.344 [0.293, 0.395] (n=90) | 0.299 [0.245, 0.351] (n=90) |
| 2^10..2^24 | 10-24 | 0.931 [0.895, 0.973] (n=72) | 0.388 [0.344, 0.434] (n=120) | 0.361 [0.316, 0.408] (n=120) |
| 2^14..2^24 (drops the smallest, overhead-dominated sizes) | 14-24 | 0.883 [0.835, 0.954] (n=54) | 0.447 [0.381, 0.512] (n=90) | 0.436 [0.373, 0.500] (n=90) |

Other A1 readings, sizes 10-20 (10-24): fixed delta 0.5: 0.813 [0.759, 0.886] (0.881 [0.840, 0.932]); delta 0.7: 0.867 [0.818, 0.932] (0.928 [0.890, 0.974]); delta 0.9: 0.840 [0.789, 0.912] (0.907 [0.867, 0.956]); wall time at optimum: 0.917 [0.874, 0.986] (0.978 [0.943, 1.026]); Jacobian-add count only: 0.912 [0.864, 0.975] (0.965 [0.928, 1.009]); fixed mean conversion ratios: 0.911 [0.863, 0.974] (0.965 [0.928, 1.009]).
Early-solve diagnostic (cost when k is first determined by a collision among relations, not the frozen protocol): alpha 0.558 [0.517, 0.611] (10-20), 0.610 [0.590, 0.646] (10-24). This is a birthday effect on the E1 hit set, about p / sqrt(B) trials, and it stays above rho.

## A2 splitting law, genus 2 (3 curves per p pooled; ratio = observed hits / (null x total weight); CI by block bootstrap)
| log2 p | delta | B | |F| | observed | expected (null) | ratio | 95% CI | powered (exp>=50) |
|---|---|---|---|---|---|---|---|---|
| 12 | 0.3 | 12 | 20 | 82936 | 82218.7 | 1.009 | [0.996, 1.022] | yes |
| 12 | 0.4 | 27 | 52 | 467342 | 464632.0 | 1.006 | [1.000, 1.012] | yes |
| 12 | 0.5 | 63 | 136 | 3124894 | 3125252.3 | 1.000 | [0.998, 1.002] | yes |
| 12 | 0.6 | 146 | 288 | 15726086 | 15719025.3 | 1.000 | [1.000, 1.001] | yes |
| 12 | 0.7 | 337 | 688 | 83022216 | 82987184.4 | 1.000 | [1.000, 1.001] | yes |
| 12 | 0.8 | 775 | 1568 | 435755810 | 435719877.2 | 1.000 | [1.000, 1.000] | yes |
| 12 | 0.9 | 1780 | 3676 | 2309436626 | 2309548108.3 | 1.000 | [1.000, 1.000] | yes |
| 16 | 0.3 | 27 | 32 | 1312 | 1341.8 | 0.978 | [0.884, 1.079] | yes |
| 16 | 0.4 | 84 | 164 | 16058 | 15933.7 | 1.008 | [0.979, 1.038] | yes |
| 16 | 0.5 | 255 | 492 | 166932 | 166851.2 | 1.000 | [0.991, 1.010] | yes |
| 16 | 0.6 | 775 | 1540 | 1661834 | 1663736.6 | 0.999 | [0.996, 1.002] | yes |
| 16 | 0.7 | 2352 | 4780 | 15205000 | 15206656.5 | 1.000 | [0.999, 1.001] | yes |
| 16 | 0.8 | 7130 | 14563 | 139782175 | 139809302.6 | 1.000 | [1.000, 1.000] | yes |
| 16 | 0.9 | 21613 | 43259 | 1285960607 | 1285977838.6 | 1.000 | [1.000, 1.000] | yes |
| 20 | 0.3 | 63 | 160 | 52 | 60.3 | 0.862 | [0.398, 1.326] | yes |
| 20 | 0.4 | 255 | 516 | 808 | 739.9 | 1.092 | [0.941, 1.238] | yes |
| 20 | 0.5 | 1023 | 2092 | 12142 | 12002.3 | 1.012 | [0.977, 1.044] | yes |
| 20 | 0.6 | 4095 | 8268 | 182622 | 182131.8 | 1.003 | [0.993, 1.012] | yes |
| 20 | 0.7 | 16383 | 32828 | 2923114 | 2914984.3 | 1.003 | [1.001, 1.005] | yes |
| 20 | 0.8 | 65535 | 131440 | 47058262 | 47037959.1 | 1.000 | [1.000, 1.001] | yes |
| 20 | 0.9 | 262142 | 525269 | 749088610 | 749124531.7 | 1.000 | [1.000, 1.000] | yes |
| 24 | 0.3 | 147 | 304 | 4 | 1.0 | 3.827 | [3.827, 11.482] | NO |
| 24 | 0.4 | 776 | 1568 | 24 | 26.8 | 0.896 | [0.299, 1.642] | NO |
| 24 | 0.5 | 4095 | 8320 | 604 | 715.2 | 0.845 | [0.721, 0.979] | yes |
| 24 | 0.6 | 21618 | 43188 | 19880 | 19872.6 | 1.000 | [0.974, 1.029] | yes |
| 24 | 0.7 | 114104 | 228276 | 553608 | 553823.2 | 1.000 | [0.994, 1.005] | yes |
| 24 | 0.8 | 602248 | 1205860 | 15447528 | 15453390.8 | 1.000 | [0.999, 1.001] | yes |
| 24 | 0.9 | 3178685 | 6359548 | 430894692 | 430877119.0 | 1.000 | [1.000, 1.000] | yes |
Per-delta slopes of log2 ratio on log2 p, A2 (CI): 0.3: -0.028 [-0.166, 0.050]; 0.4: 0.015 [-0.012, 0.038]; 0.5: -0.018 [-0.035, -0.002]; 0.6: 0.0001 [-0.003, 0.003]; 0.7: 0.0000 [-0.0006, 0.0006]; 0.8, 0.9: below 1e-4 in magnitude. Pooled (delta fixed effects): -0.0040 [-0.0142, 0.0027], n_boot 2000. Powered cells only enter slopes (needs >= 3 powered sizes per delta).

## A3 splitting law, genus 3
| log2 p | delta | B | |F| | observed | expected (null) | ratio | 95% CI | powered (exp>=50) |
|---|---|---|---|---|---|---|---|---|
| 12 | 0.5 | 63 | 116 | 1332 | 1380.9 | 0.965 | [0.811, 1.118] | yes |
| 12 | 0.6 | 146 | 296 | 19932 | 19521.8 | 1.021 | [0.982, 1.063] | yes |
| 12 | 0.7 | 337 | 713 | 226346 | 225045.5 | 1.006 | [0.994, 1.018] | yes |
| 12 | 0.8 | 775 | 1565 | 2520670 | 2518292.3 | 1.001 | [0.998, 1.004] | yes |
| 12 | 0.9 | 1780 | 3585 | 31715626 | 31706631.1 | 1.000 | [0.999, 1.001] | yes |
| 16 | 0.5 | 255 | 544 | 24 | 22.7 | 1.058 | [0.353, 2.468] | NO |
| 16 | 0.6 | 775 | 1612 | 736 | 640.7 | 1.149 | [0.924, 1.399] | yes |
| 16 | 0.7 | 2352 | 4796 | 18016 | 18134.8 | 0.993 | [0.956, 1.037] | yes |
| 16 | 0.8 | 7130 | 14132 | 502336 | 498934.9 | 1.007 | [0.998, 1.015] | yes |
| 16 | 0.9 | 21613 | 42562 | 13915740 | 13916840.1 | 1.000 | [0.999, 1.001] | yes |
| 20 | 0.5 | 1023 | 1948 | 0 | 0.4 | 0.000 | [1.000, 1.000] | NO |
| 20 | 0.6 | 4095 | 8228 | 16 | 23.7 | 0.676 | [0.338, 1.691] | NO |
| 20 | 0.7 | 16383 | 32906 | 1528 | 1540.1 | 0.992 | [0.857, 1.138] | yes |
| 20 | 0.8 | 65535 | 131434 | 97884 | 97500.6 | 1.004 | [0.986, 1.022] | yes |
| 20 | 0.9 | 262142 | 524406 | 6243008 | 6245810.5 | 1.000 | [0.997, 1.002] | yes |
Per-delta slopes, A3: 0.7: -0.0025 [-0.029, 0.022]; 0.8: 0.0005 [-0.003, 0.004]; 0.9: -0.0001 [-0.0006, 0.0004]. Pooled: -0.0007 [-0.0096, 0.0076].

Why A2/A3 cannot show an excess: for a uniform element the split probability is exactly (number of reduced divisors supported on F)/#Jac. The measured/null ratio therefore only tests the sampler and the counting formula, and both agree to sampling noise (and exactly in the exhaustive runs). The factor base in Jac(C) gives no density advantage over the E1 hit set because the elements of interest, the R_j, are not uniform in Jac(C) but lie in the pullback subgroup of size about p.

## Flagged borderline readings (not resolved)
1. INCONCLUSIVE vs KILL rests on two unmeasurable cells and one per-delta slope (see Verdict). 4 of 26 powered A2 cells have a CI that excludes 1 (2^12/0.4 [1.000, 1.012], 2^12/0.7 [1.000, 1.001], 2^20/0.7 [1.001, 1.005], 2^24/0.5 [0.721, 0.979]); all ratios are within [0.8, 1.25] and 3 of 4 are within 0.6% of 1. With 38 powered cells, a few such CIs are expected by chance (CIs are percentile block-bootstrap intervals over 3 curves, which can be too narrow for cells with large weights).
2. Prediction "A1 alpha at least 1 under every B" is not met on 2^10..2^20: fixed-delta alphas 0.81 to 0.87 (CIs exclude 1); 10-24 they reach 0.88-0.93. Trials per relation-set are about 0.9-1.04 p at every size, so the slope below 1 comes from small-size overhead (+10 relations, tiny sizes, noise in the measured conversion ratios, 16-35 across batches) and from picking the minimum over noisy deltas. Not resolved.
3. Prediction "rho alpha = 0.50 +- 0.03" is not met: 0.34-0.45 depending on sizes, because DP-rho has size-independent overhead at small n1 (table build, restarts, fruitless trails). This favours the KILL comparison; the A1 minus rho gap (0.5 or more) is far larger than any such effect.
4. Timing floors: rho wall time is 21-25 microseconds for 2^10..2^14 (near the resolution of this harness) and the 2^10 and 2^12 A1 points are overhead-heavy; fits are reported with and without 2^10 and 2^12 and the verdict does not depend on them. The fits are on counted operations; wall time is secondary. Host load 2-5 throughout; the conversion ratios were measured under the load of each batch.
5. The optimum delta per size is not sharp: cost varies by up to 1.7x over delta 0.3..0.95, with a broad minimum at delta 0.4-0.7 and the best delta jumping between sizes (0.40 to 0.70), so "optimum B about p^(2/3)" is neither confirmed nor refuted. The cost rises at delta 0.95 (larger factor base: more Legendre tests and elimination work per trial).

## Limitations
- Generic Cantor (22 E1-adds per Jacobian add) instead of explicit formulas; constant factor only.
- Rho is a plain DP implementation, not tuned; E1 additions use affine inversion for both rho and the Jacobian ratio.
- Cells with fewer than 50 expected hits are reported but cannot be judged (A2: 2 of 28; A3: 3 of 15).
- Slope CIs resample blocks within 3 curves per size, not curves; curve-to-curve variation of the null is only partly in the CI.
- The point at infinity of the odd model (x = r) is excluded from F; lower-weight divisors (probability about 1/p) are not sampled.
- Degree-3 covers (Frey-Kani) not tested (as frozen). Only bielliptic covers.
- Only the A1 sizes 2^10..2^24 were run; the 2^24 point scans 6 deltas.
- The kb/cairn knowledge servers did not connect in this session, so no prior-art query was made; no literature claim is made here. The repository was not touched and no `.resume` checkpoint was created (brief: work only in this directory); the main session stages results.

## Suggested lead-atlas line
SA-24 (Semaev-alternatives, round 6): factor base in Jac(C) for bielliptic genus-2 cover of E1 (and genus-3 splitting statistics), p = 2^10..2^24. Pullback exact; #Jac = #E1 #E2. Relations from pb(T) reduce to hits in the set {T in E1 : x(T) = small square}: A1 alpha = 0.87 [0.82, 0.92] (counted E1-add equivalents) vs rho 0.34 [0.29, 0.40]; splitting ratios measured/null = 1 within noise at both genera (pooled slope CI contains 0). Verdict INCONCLUSIVE only because two cells with expected count <= 1 cannot meet the "every cell in [0.5, 2]" clause; on powered cells it is a KILL. Cover Jacobians give no relation source beyond E1 itself. Artifacts: /home/user/semaev-runs/SA-24/results/.
