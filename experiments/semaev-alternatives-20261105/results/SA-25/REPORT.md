# SA-25 REPORT: closed Hecke and Atkin-Lehner relations inside trace classes of X0(11)(F_p)

## Verdict: KILL

Frozen KILL rule: "for every p >= 10^5, the minimum over classes of c_t/|S_t| is at least 0.05, and the measured or projected cost exceeds rho at the two largest primes."

Deciding numbers:
- Over the 16 primes used with p >= 10^5 (all classes, all sizes), the smallest c_t/|S_t| is 0.133 (at p = 3000199). It never approaches 0.05. Over all 29 primes the minimum is also 0.133.
- No class has c_t = 0. Corank is 13% to 50% of the class size in every class of every prime.
- At the two largest primes the projected cost (c_t+1)p/|S_t| + |S_t| log2 p is 1.82e6 (p = 10000169) and 1.93e6 (p = 10000019), against rho sqrt(pi n/4) of 1254 and 34. Measured end-to-end wall time through the best classes is 2.2e3 to 2.9e4 times matched rho, with every 95% CI far above 1.
- SUCCESS is also excluded independently: at each of the two largest primes no class has c_t <= 10 (at 10000169 and 10000019 the count is 0). At the three largest primes of the base list (483317, 695207, 1000003) the counts are 1, 0, 2, and the end-to-end solves lose to rho by factors 300 to 1400.
- The frozen predictions hold (see Predictions), with one caveat on prediction 4.

"Relation source complete" (reported in any case): literal rule (some class has c_t <= 10 at three or more primes) is met at 20 of 29 primes, but only by tiny classes (81 classes in total, |S_t| <= 36, c_t/|S_t| >= 0.25, at most 18 Hecke rows each, mostly Atkin-Lehner only). No class with |S_t| >= 50 ever has c_t <= 10 (smallest c_t among such classes: 14). I do not count this as a relation source. See Flagged readings.

## What was run

All code, logs and results are in /home/user/semaev-runs/SA-25/ (src/, results/*.jsonl, logs/, work/). Host: shared 4-core, load average 2.5 to 4.7 during runs, every process under nice -n 10, one heavy process at a time.

(a) Maps. x011check.sage re-run (p = 1009, 4001): j, j' on 11a1 with denominator x-16, all 23 and 13 coefficients are integers (no bad primes). Independent numpy/C re-implementation checked at every prime used: Phi_11(j,j') = 0 at all points (29 primes, 0 nonzero out of about 6.6e7 points), Atkin-Lehner s + w(s) = (16,-61) at every uniquely matched pair (0 failures), point count equals p+1-a_p(11a1) at every prime.
(b) Classes S_t = {s : |a_p(E_j)| = t} (PARI ellap on a curve with that j). Points with x = 16 (2 per prime) excluded; j in {0,1728} and ambiguous (j,j') keys recorded separately and excluded. Relations: Atkin-Lehner (including w(s)=s, giving 2s = c0) and T_l for l in {2,3,5,7,13,17,19,23} at every s whose l+1 neighbours are all rational and uniquely matched. Every relation was verified as an exact point identity in E11(F_p) in C before use: Every AL and Hecke relation passed (0 failures at all 31 prime runs, including the 4001 and 10007 control runs). Hecke relations verified at p = 10000169: T_2 1,667,882; T_5 166,294; T_7 59,854; T_13 9,048; T_17 4,590; AL pairs 5,001,545.
(c) Rank over F_n (n = largest prime factor of #E11(F_p)), corank c_t = |S_t| - rank, per class, with Atkin-Lehner pairs eliminated by substitution then dense elimination mod n in C. Primes: 20 log-spaced primes in [1e3, 1e6] (two candidates replaced by the next prime for n = 5 or n^2 | #E: 1439 and 2069 skipped), plus 9 primes in [1.5e6, 1e7]: six chosen by target (1.5e6, 2.2e6, 3.3e6, 4.6e6, 6.8e6, 1e7, literal n rule) and three (3000199, 6000823, 10000169) chosen as the first prime above 3e6, 6e6, 1e7 with n >= #E/12, see Deviations. Positive control at all 22 primes p <= 2^20 (the 20 base primes plus 4001 and 10007): true logs by baby-step giant-step on the n-component for 10 classes per prime (5 with most Hecke rows, 5 random, seed 25): 153,275 relations checked against true logs, 0 violations, every class with a nonzero true-log vector has c_t >= 1.
(d) Covariates per class (D = t^2-4p, f, primes dividing f, sigma(f), |S_t|, number of Cl(D0)-orbits as divisors of f) are in results/classes_p<p>.jsonl. Cost and exponent fits with 2000-resample bootstrap, seed 25 (resampling primes).
(e) End to end at the three largest primes used (6800033, 10000019, 10000169) and also at the three largest of the base list (483317, 695207, 1000003): kernel basis, c_t+1 connections by random walk R += S_m with S_m = aP + bQ + T (T in the cofactor subgroup), hash lookup of R in the class, solve, verify [k]P = Q. 5 targets x 10 repetitions per class and prime, all 600 solves correct. Matched rho (distinguished points, same point-addition routine, same language): 5 targets x 200 repetitions per prime, all 6000 correct.

## Tables

All 29 primes (c = corank; "excl." = ambiguous-key points + j in {0,1728} points; |S|>=50 columns restrict to classes of at least 50 points):

| p | n | points | excl. (amb+j0/1728) | classes | min c/|S| all | min c/|S| (|S|>=50) | min c (|S|>=50) | #classes c<=10 (all / |S|>=50) | min proj. cost | rho sqrt(pi n/4) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1009 | 17 | 1017 | 146+0 | 28 | 0.312 | 0.312 | 20 | 9 / 0 | 618 | 3.7 |
| 1447 | 71 | 1417 | 20+2 | 34 | 0.250 | 0.250 | 16 | 9 / 0 | 707 | 7.5 |
| 2081 | 7 | 2097 | 56+2 | 41 | 0.250 | 0.250 | 20 | 4 / 0 | 1.27e+03 | 2.3 |
| 2999 | 11 | 3077 | 10+4 | 50 | 0.202 | 0.202 | 19 | 4 / 0 | 1.53e+03 | 2.9 |
| 4283 | 283 | 4242 | 2+0 | 72 | 0.250 | 0.250 | 14 | 14 / 0 | 1.62e+03 | 14.9 |
| 6163 | 37 | 6102 | 18+0 | 86 | 0.167 | 0.167 | 16 | 10 / 0 | 2.23e+03 | 5.4 |
| 8861 | 59 | 8847 | 18+2 | 85 | 0.200 | 0.200 | 24 | 2 / 0 | 3.57e+03 | 6.8 |
| 12743 | 83 | 12862 | 6+0 | 123 | 0.250 | 0.250 | 14 | 7 / 0 | 4.18e+03 | 8.1 |
| 18341 | 181 | 18097 | 32+6 | 148 | 0.250 | 0.250 | 20 | 4 / 0 | 6.34e+03 | 11.9 |
| 26371 | 19 | 26597 | 54+4 | 177 | 0.167 | 0.167 | 20 | 3 / 0 | 7.02e+03 | 3.9 |
| 37951 | 61 | 38122 | 50+4 | 212 | 0.143 | 0.143 | 14 | 2 / 0 | 1.03e+04 | 6.9 |
| 54559 | 1087 | 54347 | 46+2 | 213 | 0.133 | 0.133 | 28 | 0 / 0 | 1.66e+04 | 29.2 |
| 78479 | 181 | 78732 | 12+0 | 306 | 0.200 | 0.200 | 24 | 3 / 0 | 2.18e+04 | 11.9 |
| 112901 | 151 | 113247 | 12+2 | 306 | 0.200 | 0.200 | 25 | 1 / 0 | 3.17e+04 | 10.9 |
| 162389 | 83 | 162677 | 2+2 | 367 | 0.214 | 0.214 | 30 | 1 / 0 | 4.45e+04 | 8.1 |
| 233591 | 389 | 233397 | 28+4 | 440 | 0.200 | 0.200 | 28 | 0 / 0 | 5.85e+04 | 17.5 |
| 335999 | 6121 | 336652 | 2+0 | 632 | 0.200 | 0.200 | 21 | 2 / 0 | 7.72e+04 | 69.3 |
| 483317 | 1609 | 482697 | 14+2 | 633 | 0.214 | 0.214 | 27 | 1 / 0 | 1.27e+05 | 35.5 |
| 695207 | 23197 | 695907 | 6+4 | 758 | 0.214 | 0.214 | 20 | 0 / 0 | 1.66e+05 | 135.0 |
| 1000003 | 2777 | 999717 | 32+4 | 1092 | 0.149 | 0.149 | 30 | 2 / 0 | 1.83e+05 | 46.7 |
| 1500007 | 389 | 1501537 | 6+0 | 1336 | 0.167 | 0.167 | 24 | 0 / 0 | 2.67e+05 | 17.5 |
| 2200013 | 673 | 2200707 | 26+2 | 1348 | 0.214 | 0.214 | 34 | 0 / 0 | 5.13e+05 | 23.0 |
| 3000199 | 599891 | 2999452 | 22+4 | 1890 | 0.133 | 0.133 | 28 | 0 / 0 | 4.76e+05 | 686.4 |
| 3300001 | 13 | 3303297 | 118+10 | 1982 | 0.145 | 0.145 | 32 | 1 / 0 | 5.95e+05 | 3.2 |
| 4600003 | 757 | 4598772 | 24+4 | 2340 | 0.143 | 0.143 | 26 | 0 / 0 | 7.53e+05 | 24.4 |
| 6000823 | 1201049 | 6005242 | 6+0 | 2672 | 0.154 | 0.154 | 24 | 1 / 0 | 1.06e+06 | 971.2 |
| 6800033 | 1360237 | 6801182 | 34+0 | 2845 | 0.214 | 0.214 | 29 | 1 / 0 | 1.57e+06 | 1033.6 |
| 10000019 | 1499 | 9998327 | 20+4 | 2875 | 0.171 | 0.171 | 36 | 0 / 0 | 1.93e+06 | 34.3 |
| 10000169 | 2000629 | 10003142 | 50+0 | 3450 | 0.179 | 0.179 | 24 | 0 / 0 | 1.82e+06 | 1253.5 |

Fits of the minimum projected cost (3 variants of the minimum: over all classes, over usable classes with c>=1 and nonzero logs, over classes with |S|>=50; usable and all coincide almost everywhere). Bootstrap 2000 resamples, seed 25. These are count-based, not timing-based, so no timing floor applies:

| quantity | regressor | subset | slope | 95% CI | n |
|---|---|---|---|---|---|
| min_cost_all | log2 n | all primes | 0.516 | [0.373, 0.683] | 29 |
| min_cost_all | log2 n | p>=1e4 | 0.350 | [0.186, 0.499] | 22 |
| min_cost_all | log2 p | all primes | 0.878 | [0.858, 0.901] | 29 |
| min_cost_all | log2 p | p>=1e4 | 0.907 | [0.884, 0.929] | 22 |
| min_cost_usable | log2 n | all primes | 0.516 | [0.377, 0.697] | 29 |
| min_cost_usable | log2 n | p>=1e4 | 0.350 | [0.182, 0.496] | 22 |
| min_cost_usable | log2 p | all primes | 0.878 | [0.859, 0.902] | 29 |
| min_cost_usable | log2 p | p>=1e4 | 0.907 | [0.882, 0.928] | 22 |
| min_cost_ge50 | log2 n | all primes | 0.507 | [0.364, 0.678] | 29 |
| min_cost_ge50 | log2 n | p>=1e4 | 0.350 | [0.184, 0.503] | 22 |
| min_cost_ge50 | log2 p | all primes | 0.856 | [0.828, 0.892] | 29 |
| min_cost_ge50 | log2 p | p>=1e4 | 0.907 | [0.883, 0.930] | 22 |
| rho | log2 n | rho formula | 0.500 | [0.500, 0.500] | 29 |

Covariate trend (pooled over the 29 primes, classes with |S_t| >= 50, 26173 classes; classes of different primes are not independent):

| class group (|S|>=50) | n classes | mean c/|S| | min | max |
|---|---|---|---|---|
| f=1 (sigma(f) = sum 1/l, l|f, l<=23) | 15692 | 0.500 | 0.500 | 0.509 |
| sigma<0.5 (sigma(f) = sum 1/l, l|f, l<=23) | 3820 | 0.406 | 0.286 | 0.500 |
| 0.5-0.8 (sigma(f) = sum 1/l, l|f, l<=23) | 5984 | 0.305 | 0.187 | 0.500 |
| >=0.8 (sigma(f) = sum 1/l, l|f, l<=23) | 677 | 0.226 | 0.133 | 0.323 |

Spearman correlation of c_t/|S_t| with sigma(f): -0.756, 95% bootstrap CI [-0.838, -0.727], n = 26173.

End to end (wall time includes class hash build and the 32-step table setup for both methods; ours = walk + C/ctypes solve; kernel build is a one-time per-prime setup of 0.2 ms to 2 s, not included in "ours ms"; host load 4.0 to 4.6; ratio CI by independent bootstrap of ours and rho run times, 2000 resamples, seed 25):

| p | n | class | \|S\| | c_t | solved | mean trials (adds) | ours ms | rho us | ratio ours/rho (95% CI) | rho walk adds |
|---|---|---|---|---|---|---|---|---|---|---|
| 1000003 | 2777 | min c_t | 16 | 8 | 50/50 | 3.14e+06 | 465.3 | 336 | 1386 [1208, 1578] | 104 |
| 1000003 | 2777 | min proj. cost | 1692 | 252 | 50/50 | 4.87e+05 | 104.0 | 336 | 310 [284, 341] | 104 |
| 695207 | 23197 | min c_t | 36 | 18 | 50/50 | 2.83e+06 | 422.5 | 371 | 1140 [1021, 1267] | 239 |
| 695207 | 23197 | min proj. cost | 540 | 120 | 50/50 | 7.07e+05 | 111.0 | 371 | 299 [262, 336] | 239 |
| 483317 | 1609 | min c_t | 24 | 8 | 50/50 | 5.75e+05 | 85.5 | 236 | 362 [311, 414] | 82 |
| 483317 | 1609 | min proj. cost | 176 | 44 | 50/50 | 1.13e+06 | 170.5 | 236 | 722 [645, 800] | 82 |
| 6800033 | 1360237 | min c_t | 14 | 7 | 50/50 | 2.03e+07 | 3345.2 | 784 | 4264 [3686, 4855] | 1822 |
| 6800033 | 1360237 | min proj. cost | 2304 | 512 | 50/50 | 1.84e+07 | 3182.8 | 784 | 4057 [3691, 4426] | 1822 |
| 10000019 | 1499 | min c_t | 32 | 16 | 50/50 | 4.01e+07 | 6527.0 | 257 | 25396 [22148, 28746] | 79 |
| 10000019 | 1499 | min proj. cost | 9240 | 1584 | 50/50 | 5.7e+06 | 7383.1 | 257 | 28727 [26265, 31739] | 79 |
| 10000169 | 2000629 | min c_t | 40 | 20 | 50/50 | 4.31e+07 | 6946.2 | 915 | 7593 [6645, 8608] | 2012 |
| 10000169 | 2000629 | min proj. cost | 1344 | 240 | 50/50 | 1.18e+07 | 1990.0 | 915 | 2175 [2033, 2297] | 2012 |

"mean trials" counts point additions in the connection walk; "rho walk adds" counts point additions in the rho walk (excluding start-point scalar multiplications and step-table setup, which dominate rho's wall time at small n). Smallest mean time in the comparison: rho 236 us, ours 85 ms, both orders of magnitude above the nanosecond clock; no ratio rests on a timing floor.

## Predictions (frozen)

1. "c_t/|S_t| decreases with sigma(f) but stays at or above 0.1 in every class with |S_t| >= 50": holds. Mean ratio 0.500 (f=1), 0.406 (sigma<0.5), 0.305 (0.5-0.8), 0.226 (>=0.8); minimum 0.133 over 26,173 classes.
2. "Atkin-Lehner alone leaves c_t about |S_t|/2": holds. Classes with f = 1 (no Hecke relations): mean ratio 0.50000, range 0.5 to 0.509 (the excess is points without an Atkin-Lehner partner).
3. "No class reaches bounded corank": holds for classes with |S_t| >= 50 (smallest c_t = 14, and 14..36 across primes, no downward trend with p). Tiny classes (|S_t| <= 36) have c_t <= 10 trivially.
4. "Minimal projected total exponent at least 0.5": regressed on log2 p the slope is 0.878 (95% CI [0.858, 0.901], n = 29), 0.907 for p >= 1e4. Regressed on log2 n as the prereg words it, 0.516 (CI [0.373, 0.683]), 0.350 for p >= 1e4 (CI [0.186, 0.499]). The log2 n fit is ill-posed (see Flagged readings). The cost is c_t p/|S_t| with c_t/|S_t| about 0.13 to 0.2, so it is linear in p, not sqrt(p).
5. "Measured end-to-end cost above rho at every prime tested": holds at all 6 primes, both classes.

## Flagged borderline readings (not resolved)

- n is not about p. n is the largest prime factor of #E11(F_p) = 5 x (smooth), and ranges from 7 to 2.0e6 (below 2000 at most primes). The prereg only replaces n = 5 or n^2 | #E, which I applied literally. So the prereg's "fit exponent against log2 n" gives 0.516 with a CI reaching 0.37, and a fit against log2 n for p >= 1e4 gives 0.350 [0.186, 0.499], whose CI excludes 0.5 from below. Prediction 4 is therefore not decisive in n; it is clearly met in p. This does not affect the verdict: neither KILL nor SUCCESS depends on the exponent.
- The literal "c_t <= 10 in some class" is satisfied at 20 of 29 primes by tiny classes. At the three largest primes used it is 0, 0, 1 (10000169, 10000019, 6800033), so SUCCESS fails even on the literal reading, and under the literal reading "relation source complete" is met. I report both and consider the second a degenerate artefact. The "three largest primes" depend on which extras count: using all primes run they are 6800033, 10000019, 10000169; the base list alone gives 483317, 695207, 1000003; if the three large-n primes are excluded they are 4600003, 6800033, 10000019. Verdict is KILL under each choice (the e2e solves at 4600003 were not run; its projected cost is 7.5e5 against rho 24, and its min c/|S| is 0.143).
- KILL's first clause read literally (minimum over all classes) is true (0.133); restricted to |S_t| >= 50 it is also 0.133. The two agree.
- Points with ambiguous (j,j') keys (two distinct points of X0(11)(F_p) with the same key; the plane model Phi_11 has nodes) are excluded: 14% of points at p = 1009, at most 1.2e-4 of points for p >= 1e5 (3.2e-5 at p = 1e6). Relations with an excluded neighbour are dropped, which can only raise c_t. This is the prereg's rule, and for p >= 1e5 the excluded fraction is far too small to move the minimum ratio from 0.133 to 0.05.
- Rho comparison: the wall-time ratio is dominated by the connection count (about 0.13 p to 0.2 p trials) against sqrt(n) rho steps; n is small, so rho wins by a large margin. Even if n were about p, projected connection cost (>= 0.13 p) exceeds rho sqrt(pi p/4) for p >= 100.

## Limitations

- One modular curve X0(11), one target curve up to isogeny; partial neighbourhoods excluded, so Hecke coverage is the full-rational-neighbourhood subset only.
- n varies from 7 to 2.0e6 and is not tied to p, so "rho on E11[n]" is cheap at most primes. Three extra primes (3000199, 6000823, 10000169) were chosen for n >= #E/12 to test the method where rho is not trivial; the verdict is the same on the other 26.
- Class sizes up to 9,240 points at p = 1e7; dense mod-n elimination, no sparse tricks. Peak RAM 2.6 GB.
- Random-walk connections are correlated; the c_t+1 independent equations needed were obtained in all 600 solves with a small surplus (c_t+3 requested at first).
- Spearman and fits pool classes/primes that are not independent; CIs are bootstrap over primes (fits) or classes (Spearman) and are only indicative.
- Host load 2.5 to 4.7 (three executors); timings are wall time, not isolated CPU time.

## Deviations
See /home/user/semaev-runs/SA-25/DEVIATIONS.md (resume-checkpoint step not done by executor; x=16 exclusion; ambiguous/special points excluded; Hecke prefilter l^2 | D validated identical to unfiltered at p = 1009, 4001, 10007; class-selection rule for end to end; orbit definition; extra primes up to 1e7 including 3 chosen for large n; rho and our methods both time their own setup (step table, class hash) inside the timer; rho wall times in the table come from a separate rho-only run with fresh targets, 5 x 200 runs per prime, because the first e2e run stored only rho means; an earlier e2e run used an oversized rho hash table and a step-selection bug in rho, both fixed before the reported runs, outputs kept as work/e2e_run1_badrho.jsonl).

## Suggested lead-atlas line

SA-25 (X0(11) trace-class Hecke + Atkin-Lehner relation module, p up to 1e7, 29 primes): KILL. Relations are real and verified (point identities, true-log control: 153,275 relations, 0 violations) but the relation module has corank 13% to 50% of every trace class (never c_t <= 10 for |S_t| >= 50); logs are determined only up to c_t ~ 0.13..0.2 |S_t| unknowns, so the connection step costs about 0.13p..0.2p trials (exponent 0.88 in p), 3e2 to 3e4 times matched rho on E11[n]. Atkin-Lehner pairs alone give corank |S_t|/2; each added Hecke prime lowers it by sigma(f) only. No decomposition-free relation source of useful size on one curve.
