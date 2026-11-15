# SA-24c REPORT: completion of SA-24 (Part 1) and exploratory A1-full Gaudry arm (Part 2)

All work in /home/user/semaev-runs/SA-24c/ (code in src/, raw results in results/, departures in DEVIATIONS.md, 14 items). Protocol SHA-256 03f744a7... read in full before any run. Bootstrap: 2,000 resamples, seed 24 throughout.

## Part 1 verdict for SA-24: KILL

SA-24's frozen KILL criteria, applied to the completed table:
1. A1's alpha CI lies entirely above rho's: established in SA-24 (A1 0.865 [0.821, 0.923] vs rho 0.344 [0.293, 0.395], sizes 2^10..2^20); not re-run.
2. Every A2 and A3 cell has measured/null in [0.5, 2]: YES. All 28 A2 and 15 A3 pooled cells are powered (pooled expected weighted count >= 50 in every cell) and lie in [0.961, 1.092] (A2) and [0.964, 1.149] (A3); every one is inside even the prediction band [0.8, 1.25].
3. Both per-genus pooled slope CIs (log ratio against log2 p, delta fixed effects, all cells, SA-24 and fresh samples pooled) contain 0: genus 2: +0.0022 [-0.0016, +0.0056]; genus 3: +0.0017 [-0.0091, +0.0119].

Deciding numbers are therefore: pooled ratio range 0.961 to 1.149 over 43 cells, slope CIs [-0.0016, 0.0056] and [-0.0091, 0.0119]. Verdict: KILL. All frozen predictions of Part 1 hold, including (2^24, 0.5) returning to [0.9, 1.1] (fresh 1.050 [0.990, 1.112]; pooled 1.022 [0.964, 1.080]), so SA-24's 0.845 was noise.

## What was run (Part 1)
Validations, all before any production trial (all passed; results/val1.jsonl, val2.jsonl, val3.jsonl):
1. Identical RNG stream, filtered vs unfiltered flags (genus 2): 1.4e9 trials over 14 (curve, p, delta) sets: (2^12, 0.5..0.9) on curve 0, (2^12, 0.5/0.7/0.9) on curves 1 and 2, (2^16, 0.5) on all three curves. 31,875,957 flagged u's; 0 mismatches.
2. Genus-3 stratified sampler: full root finding on 5.1e6 u's (1e6 random drawn u's per cell, plus every member of each per-c2 set and its c0+1 perturbation) at (2^16,0.5), (2^20,0.5), (2^20,0.6), (2^12,0.6): 0 mismatches; 1,138,618 set members all flagged by root finding.
3. Exhaustive cases (genus 2: p = 1019, 4091; genus 3: p = 211, 307), rerun with the root-exporting code: sum of weights = N_g and every split numerator = the combinatorial null exactly.

Production: genus 2 filter = bitset on c1 plus hash set of (-(a+b), ab) over all unordered pairs of F z-values (a = b allowed); weights computed exactly for hits only. Genus 3 filter = c2 uniform, per-c2 set of (c1, c0) over triples with sum -c2, D = 2e7 draws per c2. Denominator: unfiltered Sum w, 1e9 trials per curve (genus 2) and 2e8 (genus 3, deviation 3). Fresh trials in total: 4.1e12. Speed was 1.2 to 5 ns per filtered trial. No hit failed the root check (bad = 0 in every cell).

Cells (3 curves pooled). Events = unweighted u hits, observed / expected. Ratios are the SA-24 weighted observed/expected, with 95% block-bootstrap CI.

| arm | log2 p | delta | fresh events obs / exp | fresh ratio | SA-24 ratio (obs / exp, weighted) | pooled ratio (pooled expected weighted count) |
|---|---|---|---|---|---|---|
| A2 | 20 | 0.3 | 214 / 221 | 0.967 [0.846, 1.098] | 0.862 (52 / 60.3) | 0.961 [0.845, 1.087] (933) |
| A2 | 24 | 0.3 | 96 / 94 | 1.026 [0.849, 1.209] | 3.827 (4 / 1.0) | 1.034 [0.852, 1.216] (373) |
| A2 | 24 | 0.4 | 240 / 221 | 1.085 [0.958, 1.225] | 0.896 (24 / 26.8) | 1.079 [0.956, 1.222] (910) |
| A2 | 24 | 0.5 | 1178 / 1122 | 1.050 [0.990, 1.112] | 0.845 (604 / 715.2) | 1.022 [0.964, 1.080] (5202) |
| A3 | 16 | 0.5 | 212 / 221 | 0.964 [0.840, 1.088] | 1.058 (24 / 22.7) | 0.965 [0.840, 1.085] (1766) |
| A3 | 20 | 0.5 | 213 / 222 | 0.965 [0.842, 1.096] | 0.000 (0 / 0.4) | 0.964 [0.842, 1.096] (1767) |
| A3 | 20 | 0.6 | 213 / 196 | 1.090 [0.946, 1.243] | 0.676 (16 / 23.7) | 1.083 [0.937, 1.230] (1587) |

Per-delta slopes (reported, not used to decide), A2: 0.3: 0.0020 [-0.0204, 0.0214]; 0.4: 0.0105 [-0.0040, 0.0246]; 0.5: 0.0028 [-0.0035, 0.0089]; 0.6: 0.0001 [-0.0031, 0.0032]; 0.7: 0.0000 [-0.0006, 0.0006]; 0.8: -0.0000 [-0.0001, 0.0001]; 0.9: 0.0000 [-0.0000, 0.0000].
A3: 0.5: -0.0000 [-0.0401, 0.0391]; 0.6: 0.0107 [-0.0155, 0.0344]; 0.7: -0.0025 [-0.0304, 0.0231]; 0.8: 0.0005 [-0.0028, 0.0039]; 0.9: -0.0001 [-0.0006, 0.0003].
The SA-24 delta = 0.5 flag is gone: A2 delta 0.5 slope is now +0.0028 [-0.0035, +0.0089].

## Part 2 (exploratory, enters no verdict): A1-full Gaudry. Outcome: DEVIATES

Construction as frozen: S_i = a_i pb(P) + b_i pb(Q) + [n1]X_i, 32 entries, X_i uniform in Jac(C) (uniform u, accept w/4, uniform v); a relation = u(R) splits with both roots in F; row sigma1 l(P1) + sigma2 l(P2) - b k = a (mod n1); target |F|/2 + 10 relations; k recovered and checked by [k]P = Q. Every relation verified by a Jacobian addition before counting.

Positive control (2^10 and 2^12, 3 curves x 3 targets x 6 deltas, results/p2_control.jsonl): true n1-component log of every factor-base point by brute force; 108 runs, 39,156 relations, 0 relations violating the true logs, 0 verification failures, every run recovered k.

Main grid: 324 runs, all solved, all [k]P = Q, 0 capped, 0 relation-verification failures; 36 runs skipped as over the trial cap (deviation 9). Costs in E1-addition equivalents with in-process micro-benchmarks (mean Jacobian add 21.9 E1 adds, Legendre 1.15, sqrt 1.00, inversion 0.76, mulmod n1 0.072); LA multiply-adds counted as executed.

Fits (cost against size; optimum delta re-selected inside every bootstrap resample; 9 instances per size):
| variable | sizes | alpha (95% CI) |
|---|---|---|
| log2 p (frozen variable) | 2^10..2^22 | 1.005 [0.993, 1.018] (n=63) |
| log2 p | 2^10..2^20 | 0.990 [0.974, 1.009] (n=54) |
| log2 p | 2^14..2^22 | 1.042 [1.027, 1.056] (n=45) |
| log2 n1 | 2^10..2^22 | 0.935 [0.886, 0.996] (n=63) |
| log2 n1 | 2^10..2^20 | 0.911 [0.855, 0.987] (n=54) |
| log2 p, Jacobian-add count only | 2^10..2^22 | 1.039 [1.039, 1.040] (n=63) |
| log2 p, wall time | 2^10..2^22 | 1.057 [1.051, 1.063] (n=63) |
| log2 p, non-frozen extra scan at delta 0.95 | 2^10..2^22 | 0.945 [0.939, 0.950] (n=63) |
| log2 n1, extra scan at delta 0.95 | 2^10..2^22 | 0.879 [0.836, 0.935] |

Per size (geometric mean, n = 9; optimum in the scan = delta 0.9 at every size; delta 0.95 is the non-frozen extra):
| log2 p | p | A1-full cost, delta 0.9 | A1-full cost, delta 0.95 | trials / p, delta 0.9 | SA-24 A1 (degenerate) cost | rho E1 adds | full / degenerate |
|---|---|---|---|---|---|---|---|
| 10 | 1019 | 5.61e+04 | 6.25e+04 | 1.02 | 3.62e+04 | 98 | 1.55 |
| 12 | 4091 | 1.98e+05 | 1.82e+05 | 1.15 | 1e+05 | 128 | 1.98 |
| 14 | 16363 | 6.87e+05 | 6.29e+05 | 1.32 | 3.83e+05 | 143 | 1.80 |
| 16 | 65519 | 3.27e+06 | 2.84e+06 | 1.52 | 1.79e+06 | 256 | 1.82 |
| 18 | 262139 | 1.18e+07 | 9.05e+06 | 1.74 | 4.92e+06 | 491 | 2.41 |
| 20 | 1048571 | 5.3e+07 | 3.7e+07 | 2.00 | 2.16e+07 | 1045 | 2.45 |
| 22 | 4194287 | 2.35e+08 | 1.52e+08 | 2.30 | 9.3e+07 | 2037 | 2.52 |

Per-relation rate against the uniform null (exact stratum null of that curve and delta, relations / (trials x null), 9 instances pooled; range over all 37 cells 0.930 to 1.026, every cell inside [0.8, 1.25]; extra delta 0.95: 0.996 to 1.009):
| log2 p | delta | mean F | rate / null (95% CI) | geomean cost | trials / p |
|---|---|---|---|---|---|
| 10 | 0.4 | 36 | 0.933 [0.829, 1.071] | 1.39e+06 | 55.11 |
| 10 | 0.5 | 61 | 0.930 [0.846, 1.032] | 6.82e+05 | 25.17 |
| 10 | 0.6 | 124 | 0.965 [0.899, 1.044] | 2.92e+05 | 10.35 |
| 10 | 0.7 | 258 | 1.016 [0.968, 1.068] | 1.34e+05 | 4.36 |
| 10 | 0.8 | 514 | 1.000 [0.975, 1.024] | 7.76e+04 | 2.13 |
| 10 | 0.9 | 1044 | 1.006 [0.992, 1.017] | 5.61e+04 | 1.02 |
| 12 | 0.4 | 64 | 0.991 [0.924, 1.072] | 9.71e+06 | 90.76 |
| 12 | 0.5 | 141 | 1.012 [0.949, 1.077] | 3.71e+06 | 33.88 |
| 12 | 0.6 | 306 | 0.980 [0.940, 1.026] | 1.65e+06 | 14.92 |
| 12 | 0.7 | 707 | 1.003 [0.969, 1.031] | 6.94e+05 | 6.11 |
| 12 | 0.8 | 1567 | 0.992 [0.972, 1.013] | 3.38e+05 | 2.73 |
| 12 | 0.9 | 3636 | 1.007 [1.003, 1.013] | 1.98e+05 | 1.15 |
| 14 | 0.4 | 108 | 0.998 [0.930, 1.084] | 6.73e+07 | 179.59 |
| 14 | 0.5 | 261 | 1.015 [0.978, 1.056] | 2.52e+07 | 68.10 |
| 14 | 0.6 | 676 | 1.019 [0.996, 1.041] | 9.24e+06 | 24.55 |
| 14 | 0.7 | 1717 | 0.988 [0.968, 1.008] | 3.71e+06 | 9.78 |
| 14 | 0.8 | 4629 | 0.997 [0.984, 1.010] | 1.42e+06 | 3.56 |
| 14 | 0.9 | 12392 | 1.002 [0.995, 1.010] | 6.87e+05 | 1.32 |
| 16 | 0.4 | 170 | 0.949 [0.903, 0.995] | 7.68e+08 | 459.54 |
| 16 | 0.5 | 482 | 1.026 [1.000, 1.055] | 2.33e+08 | 138.13 |
| 16 | 0.6 | 1542 | 0.971 [0.954, 0.984] | 7.5e+07 | 44.39 |
| 16 | 0.7 | 4647 | 1.005 [0.990, 1.018] | 2.39e+07 | 14.12 |
| 16 | 0.8 | 14228 | 0.994 [0.987, 1.002] | 8.09e+06 | 4.64 |
| 16 | 0.9 | 43218 | 1.001 [0.997, 1.005] | 3.27e+06 | 1.52 |
| 18 | 0.5 | 1032 | 0.984 [0.968, 1.001] | 1.48e+09 | 263.97 |
| 18 | 0.6 | 3600 | 0.998 [0.977, 1.017] | 4.14e+08 | 73.48 |
| 18 | 0.7 | 12500 | 0.999 [0.992, 1.006] | 1.19e+08 | 21.05 |
| 18 | 0.8 | 43426 | 0.997 [0.993, 1.001] | 3.47e+07 | 6.06 |
| 18 | 0.9 | 150802 | 0.999 [0.997, 1.001] | 1.18e+07 | 1.74 |
| 20 | 0.65 | 16422 | 1.001 [0.994, 1.009] | 1.46e+09 | 63.89 |
| 20 | 0.75 | 65431 | 0.999 [0.996, 1.003] | 3.68e+08 | 16.06 |
| 20 | 0.85 | 261563 | 1.000 [0.999, 1.002] | 9.54e+07 | 4.01 |
| 20 | 0.9 | 524225 | 1.001 [1.000, 1.001] | 5.3e+07 | 2.00 |
| 22 | 0.75 | 185121 | 1.001 [0.999, 1.003] | 2.07e+09 | 22.64 |
| 22 | 0.85 | 851137 | 1.000 [0.998, 1.002] | 4.62e+08 | 4.93 |
| 22 | 0.9 | 1824926 | 1.000 [0.999, 1.001] | 2.35e+08 | 2.30 |

Outcome against the frozen words: **DEVIATES.** Alpha against log2 p is 1.005 [0.993, 1.018], not inside [1.1, 1.6]. Rate/null is inside [0.8, 1.25] everywhere (that clause holds). Other frozen predictions: optimal delta about 2/3: NOT as predicted (cost falls monotonically up to the largest scanned delta, 0.9, and is lower again at delta 0.95 for sizes 2^12 and above (higher only at 2^10); the true optimum is outside the frozen scan); cost above SA-24's A1 and above rho at every size from 2^14: YES (full / degenerate 1.5 to 2.5; above rho by 3 to 5 orders of magnitude).

**Flag for audit (frozen rule).** The alpha CI is at or just below 1.1 (its upper end 1.018 is below 1.1), so the frozen text asks for an audit flag. My reading, with the numbers behind it:
- Every relation in genus 2 has exactly two factor-base unknowns plus k. Sparse elimination therefore costs about the number of relations (the counted LA multiply-adds are 0.3% to 3.5% of the cost at delta >= 0.85, median 2%), not the B^2 or B^3 of the dense phase that gives the 4/3 prediction.
- Cost is then trials, about p^2/(2B) (relations needed about B, per-relation rate about 2B^2/p^2, confirmed by rate/null = 1). That falls as B grows, and trials / p reaches about 1.0 at delta 0.95.
- So the measured exponent is about 1 in p because the scan is bounded by delta <= 0.95 < 1 and the cost cannot go below the number of trials needed to see about B hits, i.e. the exponent in p is bounded below by 1 for g = 2. This is the "at least p" accounting stated in the SA-24 prereg, reached, not beaten. It is not a gain: measured cost at every size is 1.5 to 2.5 times the degenerate A1 and 500 to 1e5 times rho.
- Under dense-LA accounting (N^3/3 multiply-adds with N = |F|/2) the same data give alpha 1.97 [1.96, 1.98] against log2 p, but the scan is truncated at large sizes by the trial cap, so that number is not an optimum and I do not use it.
- I have not checked this against the literature (knowledge-base servers did not connect), so no claim is made about how it compares with published exponents.

## Flagged borderline readings (not resolved)
1. Part 2 alpha against log2 n1 is 0.935 [0.886, 0.996]. n1 = #E1 / cofactor with cofactor 1 to 16, so it tracks p only loosely; alpha against log2 p is the frozen variable.
2. Part 2 optimum is on the scan boundary (0.9, and 0.95 is still lower for sizes 2^12 and above). The optimum-selection step is therefore not informative about an interior optimum; no CI on it.
3. (2^24, 0.3) pooled event count rests on partial blocks for two of three curves (deviation 2); 96 observed vs 94 expected events.
4. Fresh-only CIs (about +-15%) are wider than SA-24's for powered cells; the pooled CIs are the decision quantity and all lie inside [0.81, 1.39].
5. Timing: k = 10, 12, 14(curve 0) Part 2 runs saw higher host load (3.5 to 3.9) because another process of mine ran; counts unaffected; conversion ratios are measured in-process.

## Limitations
- Basic algorithm only (no large-prime variants); bielliptic genus-2 covers only; generic Cantor (constant factor).
- Part 2: 36 low-delta runs skipped by the trial cap (listed in DEVIATIONS.md item 9); scan ends at 0.9 (0.95 extra, not frozen). No sizes above 2^22.
- Genus-3 denominators use 2e8 trials (deviation 3).
- No knowledge-base query was possible (servers failed to connect); no literature statements are made. The repository was not touched.

## Suggested lead-atlas line
SA-24 / SA-24c (Semaev-alternatives, round 6): bielliptic genus-2/3 covers, factor base in Jac(C). Frozen SA-24 verdict completed to KILL: A1 alpha 0.87 [0.82, 0.92] vs rho 0.34 [0.29, 0.40]; all 43 splitting cells powered, pooled measured/null 0.96 to 1.15, pooled slope CIs [-0.002, 0.006] (g=2) and [-0.009, 0.012] (g=3). Exploratory A1-full (uniform elements of Jac(C), g=2, p up to 2^22): rate/null 0.93 to 1.03, alpha against log2 p 1.005 [0.993, 1.018] with sparse 2-term relations, optimum at the scan boundary, cost 1.5 to 2.5 times the degenerate A1 and above rho; outcome DEVIATES (alpha below the predicted 4/3 because relations are 2-sparse and LA is cheap; at the p^1 bound, not under it). Artifacts: /home/user/semaev-runs/SA-24c/results/.
