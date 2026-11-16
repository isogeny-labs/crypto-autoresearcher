---
id: SA-24c
campaign: semaev-alternatives-20261105
round: 6
parent: SA-24 (verdict INCONCLUSIVE on unpowered cells; main-session audit results/SA-24/audit/AUDIT.md)
title: "Completing SA-24: power the unpowered splitting cells, and an exploratory full-Jacobian (Gaudry) arm"
status: preregistered
frozen_on: 2026-11-12
executor_tier: sonnet
results_path: experiments/semaev-alternatives-20261105/results/SA-24c/
---

# SA-24c

**Why.** SA-24 came back INCONCLUSIVE. The first half of its KILL clause holds: A1's alpha CI [0.821, 0.923] lies entirely above rho's [0.293, 0.395]. The second half needs the measured/null ratio in [0.5, 2] at every A2 and A3 cell. Five cells were never powered (expected 0.04 to 7 events), although the SA-24 protocol asks for more samples when the expected count is below 50. Part 1 finishes that measurement, so SA-24's frozen criteria can be evaluated on a complete table. Part 2 is exploratory. The frozen A1 kept every element inside pb(E1), so its relations were hits of a small subset of E1 (audit, section 1). A1-full tests index calculus with elements uniform in the whole Jacobian, which was the question behind SA-24.

## Part 1. Completion of SA-24 A2/A3 (decides SA-24's verdict)

**Cells.**
- A2 (genus 2): (2^20, 0.3), (2^24, 0.3), (2^24, 0.4), plus a top-up of (2^24, 0.5).
- A3 (genus 3): (2^16, 0.5), (2^20, 0.5), (2^20, 0.6).

**Unchanged from SA-24.** The same three curves per p (SA-24 `results/facts.jsonl` and the A2/A3 curve lines). The same factor base. The same weighted uniform-u estimator (SA-24 deviation 1). The same null code.

**New: a filtered sampler.**
- Genus 2. Draw (c1, c0) uniformly from F_p^2. Look it up in a hash set of (-(a + b), ab) over all unordered pairs {a, b}, a = b allowed, of z-values whose points lie in F. Compute w(u) exactly only for hits. The denominator sum of w is estimated on an unfiltered subsample of at least 1e9 trials per curve.
- Genus 3. Draw c2 uniformly. Build the per-c2 set of (c1, c0) over triples of F z-values with sum -c2. Draw at least 1e7 (c1, c0) per c2, then draw a fresh c2. The sampler is stratified, and unbiased because c2 is uniform. The denominator is estimated as in genus 2.

**Validation before use (all must pass, or the run stops).**
1. On an identical RNG stream of 1e8 trials at (2^12, 0.5..0.9) and (2^16, 0.5), the filtered and unfiltered samplers flag exactly the same u's.
2. For the genus-3 stratified sampler, full root-finding on a random subsample of 1e6 drawn u's agrees with the filter on every one.
3. The exhaustive cases (genus 2 at p = 1019 and 4091, genus 3 at p = 211 and 307) still match exactly.

**Target.** At least 50 expected split events (unweighted u hits) per cell, pooled over the 3 curves. For the (2^24, 0.5) top-up, at least 500. Report each cell three ways: fresh samples alone, SA-24 samples alone, and pooled. Block bootstrap, 2,000 resamples, seed 24.

**Verdict for SA-24 (frozen criteria, applied to the completed table).**
- Every A2 and A3 cell is now powered. The pooled per-genus slope of the log ratio against log2 p is refit on all cells, with delta fixed effects, as in SA-24.
- KILL if: A1's alpha CI lies entirely above rho's (already established), every A2 and A3 cell has measured/null in [0.5, 2], and both per-genus slope CIs contain 0.
- INCONCLUSIVE otherwise.
- Per-delta slopes are reported, not used to decide. That includes delta 0.5, which SA-24 flagged.

**Predictions (frozen).** Every completed cell in [0.8, 1.25]. The (2^24, 0.5) top-up returns to within [0.9, 1.1], so the SA-24 deficit (0.845) was noise. Both pooled slope CIs contain 0. SA-24 becomes KILL.

## Part 2. Exploratory: A1-full, Gaudry index calculus in Jac(C)[n1] (enters no verdict)

**Construction.**
- Use the SA-24 A1 curves.
- Walk table entries: S_i = a_i pb(P) + b_i pb(Q) + T_i, i = 1..32. Here T_i = [n1] X_i, with X_i uniform in Jac(C): a uniform-u draw, then a uniform choice of v.
- T_i has a zero n1-component, because n1 exactly divides #Jac. So R_j = Sum a pb(P) + Sum b pb(Q) + (cofactor part) is uniform in a coset structure whose n1-projection is a + b k.
- Restart every 256 steps from a fresh random combination.

**Relation.** u(R_j) splits into linear factors over F_p, all with roots whose points lie in F. That gives Sum_i e_i l(P_i) = a + b k (mod n1), where l(P) is the n1-component log of P - infinity and l(-P) = -l(P). Collect |F|/2 + 10 relations. Solve mod n1: dense elimination if |F| <= 6000, otherwise structured Gaussian elimination then dense. Recover k and verify [k]P = Q on E1.
- Verify every relation by a Jacobian addition before it is counted.
- Positive control at 2^10 and 2^12: the true l(P) for all P in F by brute force. Every relation must hold.

**Grid.** Sizes 2^10 to 2^20 in steps of 2 bits, with 2^22 if each run finishes within the 2-hour chunk limit. Use 3 curves x 3 targets. Scan delta over {0.4, 0.5, ..., 0.9} at <= 2^18 and over {0.55, 0.65, 0.75} at 2^20 and above.

**Metrics.** Count Jacobian additions, Legendre symbols, square roots and linear-algebra multiply-adds. Convert to E1-addition equivalents with SA-24's micro-benchmark method, run in the same process. Also record wall time.
- Fit alpha against log2 n1 and against log2 p, with the optimum delta re-selected inside each bootstrap resample (2,000 resamples, seed 24).
- Compare with SA-24's A1 (degenerate) and rho at matched sizes.
- Also report the per-relation rate against the uniform null, which is SA-24's A2 null at that (p, delta).

**Predictions (frozen).**
- Per-relation rate/null in [0.8, 1.25] at every powered cell.
- Optimal delta about 2/3.
- Alpha against log2 p about 4/3, with the CI inside [1.1, 1.6].
- Cost above SA-24 A1 and above rho at every size from 2^14 up.

Outcome words for Part 2: CONSISTENT (the alpha CI is inside [1.1, 1.6] and rate/null is in [0.8, 1.25] everywhere), DEVIATES (otherwise), with no further interpretation. A DEVIATES with alpha's CI below 1.1 would be the first sign of a cover-based gain and is flagged for audit.

**Limitations known before the run.** The basic algorithm only; single- and double-large-prime variants, which give exponents 6/5 and 1 in genus 2, are not run. Only bielliptic genus-2 covers. Generic Cantor (constant factor only).

**Cost and tier.** Sonnet executor (resume of the SA-24 executor, which owns the code). Part 1 is about 4 core-hours: the (2^24, 0.3) cell is about 1.2e12 filtered trials. Part 2 is about 3 core-hours. One heavy process at a time, two while SA-23b is idle. Chunks under 2 hours.
