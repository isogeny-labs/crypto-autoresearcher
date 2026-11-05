# SA-03 report: decomposition as a Gamma_0(p) representation problem for binary quadratic forms

## Summary

**VERDICT: KILL** against the frozen criterion. (i) The census ratio structured / small-square-leading forms decreases as B^{-c} with c = 10.0 (exact-count fit 9.999, CI [9.998, 10.000], B = 16..128, p ~ 2^32; enumerated cells give c = 9.3..10.0), so c >= 1 by a wide margin. (ii) No sub-B enumeration was found: the best measured enumeration by discriminant (one 2-D lattice reduction per Delta in S_F) has exponent 1.81 [1.64, 1.96] in B at p ~ 2^64 (4.4 doublings), 1.97 [1.79, 2.11] for the number of discriminants alone; the CI excludes 1 from above. The small-prime sieve model has exponent 6.2 [5.9, 6.8] and is never below the generic lookup cost B. No representation-count identity separating structured forms was found (per-Delta counts of small forms are indistinguishable from controls at this scale; stated as a null, not as a proof of absence).

Deciding numbers: structured forms = exactly 1 (the planted one) among N_sq = 4B^10/p (+-1e-4) square-leading vectors of L_R, for every enumerated cell (N_dec = 1 in 100% of planted targets, 0 in every random control); ratio ~ p/(4B^10). Best enumeration exponent ~ 2 vs the required < 1.

## What was run

All scripts and raw outputs are in this directory. Curve y^2 = x^3 + 7, primes p = first prime >= 2^k with p = 3 mod 4, k in {20, 24, 28, 32} (plus 48, 64 for part (b) only). M = B^4 is the coefficient bound. Forms are normalised to c2 > 0.

* `census.c` / `census2.c` (C): for a target x_R, exact enumeration of every vector (c0,c1,c2) of L_R = {c0 + c1 x_R + c2 x_R^2 = 0 mod p} with |c0|,|c1| <= B^4, 1 <= c2 <= B^4 and c2 = square (mode 0), or all c2 (mode 1), or count only (mode 2). One 2-D coset-in-box enumeration per c2 (Gauss-reduced basis of the (c0,c1) lattice). For each vector: D = c1^2 - 4 c0 c2 tested against S_B = {16 f(x1) f(x2): 1 <= x1 < x2 <= B} (hash set), vector tested against the set of S_3(x1,x2,.) coefficient vectors, and (c0,c1,c2) mod q tested against the exact image of (x1,x2) for q = 3,5,7,11,13. Validated against a Python brute force (p ~ 2^20, B = 8: all four counts identical) and mode 2 against mode 0.
* `run_census.py`: planted targets R = P1 + P2 with x1 < x2 <= B and f(x_i) a QR (group law verified; the planted vector is checked to lie in L_R and in the box, 100% in box), plus 30 random-x_R controls where affordable. `count_scan.py`: exact N_sq to B = 128.
* `bydisc.py` (b): for each Delta = 16 f(x1) f(x2) in S_F (factor base F = {x <= B: f(x) QR}), derive r = sqrt(Delta) mod p and solve the 2-D lattice coset problem below by Gauss reduction on a rescaled box, then test squareness, integrality of c0 and the root condition. `repcount.py`: per-Delta count of small forms, structured vs controls.
* `analyze.py`, `analyze2.py`: tables, bootstrap fits (resampling targets, or B-cells for part (b)), figure `fig_sa03.png`.

### The Gamma_0(p) correspondence (mark: proved, elementary, known)

* (proved) Forms g with g(x_R) = 0 mod p of discriminant Delta are the forms [a,b,c] with p | c after translation T -> T + x_R, i.e. the Gamma_0(p)-type set for the stabiliser of x_R. For Delta < 0 the number of Gamma_0(p)-orbits is h(Delta)(1 + (Delta/p)) (each SL_2 class contributes its roots in P^1(F_p)); for Delta > 0 (our case, D = 16 f f > 0) orbits are indefinite, each contains infinitely many forms, and small ones are the points of a closed geodesic of X_0(p) inside the box. This is classical (Gauss, Gross-Kohnen-Zagier, Heegner) and is filed as a known result.
* (proved, new here only as a bookkeeping step) With c2 = s^2 the root condition becomes (c1 + 2 s^2 x_R)^2 = D (mod p), and c0 = (c1^2 - D)/(4 s^2). So for fixed Delta, a decomposition is a small point (S = s^2, c1) of the 2-D lattice {c1 + 2 x_R S = +-r mod p} of determinant p, with S <= B^2, |c1| <= 4B^3: unique and found in O(1) lattice operations whenever B^5 << p (delta < 1/5). This is exactly the "2-D lattice reduction per Delta" of the prereg. It does not help, because Delta ranges over S_B, which has ~B^2/2 elements that are listed pair by pair.

## Results

### (a) Census (planted targets; full tables in `census_table.md`, `census_controls.md`)

| p bits | B | targets | mean N_sq | 4B^10/p | N_both (mean) | N_dec (min / mean) | ratio N_both/N_sq | random controls: max N_dec |
|---|---|---|---|---|---|---|---|---|
| 24 | 8 | 200 | 251 | 256 | 1 | 1 / 1 | 4.0e-3 | 0 |
| 24 | 16 | 200 | 2.62e5 | 2.62e5 | 1.085 | 1 / 1 | 4.1e-6 | 0 |
| 24 | 23 | 200 | 9.88e6 | 9.88e6 | 1.135 | 1 / 1 | 1.2e-7 | 0 |
| 24 | 32 | 6 | 2.68e8 | 2.68e8 | 1.33 | 1 / 1 | 5.0e-9 | - |
| 32 | 11 | 200 | 26.6 | 24.2 | 1 | 1 / 1 | 3.8e-2 | 0 |
| 32 | 16 | 200 | 1031 | 1024 | 1 | 1 / 1 | 9.7e-4 | 0 |
| 32 | 23 | 200 | 3.86e4 | 3.86e4 | 1 | 1 / 1 | 2.6e-5 | 0 |
| 32 | 32 | 200 | 1.049e6 | 1.049e6 | 1.005 | 1 / 1 | 9.6e-7 | 0 |
| 32 | 45 | 30 | 3.17e7 | 3.17e7 | 1.033 | 1 / 1 | 3.3e-8 | - |

* All enumerated planted targets (3,472 across cells): the decomposition vector is found, and it is the only vector equal to an S_3(x1,x2,.) vector. N_both exceeds 1 only through chance coincidences D in S_B at small p (e.g. mean 1.4 at p~2^20, B=16); random controls (no planted decomposition) have N_dec = 0 in every cell (30 controls each) and occasionally one coincidental N_both = 1..2.
* N_sq follows 4B^10/p to 1e-4 over the whole range (exact counts to B = 128): structured forms are a vanishing fraction ~ p/(4B^10), i.e. in the regime delta > 1/10 (N_sq >= 1) they are 1 in p^{10 delta - 1}; delta < ~1/10 is where the planted vector is the only small vector (consistent with the LLL ceiling 1/12 to 0.1 of Section 6.3).
* Fit of ratio ~ B^{-c} (`census_fit.md`, bootstrap over targets): c = 9.34 [9.23, 9.53] (p 2^20), 9.81 [9.68, 9.98] (2^24), 9.92 [9.88, 9.96] (2^32), cells with N_sq >= 20, about 2 doublings each (lower than 10 where the planted vector's own contribution is still visible). With exact N_sq and N_both = 1 (`ratio_fit_exactNsq.md`): c = 9.999 [9.998, 10.000] at 2^32 over B = 16..128 (3.0 doublings), 10.000 at 2^24 and 2^28. In the 128 and 91 cells N_both was not enumerated (Deviation 2); there the only claim is the lower bound N_both/N_sq >= 1/N_sq (planted vector), and the exact N_sq.
* Number of all-leading-coefficient small forms (N_pos, mode 1, small B) is ~ 8B^12/p and N_D (D in S_B, any c2) is 1 (planted); the square-leading fraction of small forms is ~ 1/B^2 as expected.

### (b) Enumeration by discriminant (`bydisc_table.md`, `bydisc_fit.md`)

Planted targets, 20 per cell, full sweep over S_F, every target's decomposition recovered (20/20 in all 30 cells). Total work W = CVP calls + lattice i-steps + lattice candidates.

| p bits | B | |S_F| | W | integral c0 forms found over the whole sweep |
|---|---|---|---|---|
| 32 | 32 | 153 | 496 | 1.00 |
| 32 | 64 | 378 | 5296 | 1.05 |
| 32 | 128 | 2145 | 3.63e5 | 1.15 |
| 64 | 32 | 78 | 159 | 1.00 |
| 64 | 128 | 1485 | 2974 | 1.00 |

Exponents in B (bootstrap over B-cells): p~2^64: W 1.81 [1.64, 1.96], |S_F| 1.90 [1.71, 2.04] (B = 6..128, 4.4 doublings); p~2^32: |S_F| 1.97 [1.79, 2.11], W 2.30 [2.06, 2.44] for B <= 32 and 3.20 [2.51, 3.81] over the full range, rising because the candidate count per CVP is ~ 8B^5/p once B^5 approaches p (this is the Coppersmith-type blow-up, not a gain). The sweep finds, over all of S_F, exactly one valid form: the planted one. Cost to first success is half the sweep on average. The enumeration is therefore exponent ~ 2 in B (the size of S_F), against the generic lookup baseline of exponent 1 and the target < 1.

Sieve by small primes (`sieve_pred_vs_meas.md`, `sieve_model_table.md`, `sieve_fit.md`). Survival of square-leading vectors under "(c0,c1,c2) mod q in the image of (x1,x2)" matches the exact prediction (q = 3..13 cumulative: 0.2593/0.2593, 0.0477/0.0477, 0.00598/0.00598, 5.25e-4/5.26e-4, 4.07e-5/4.04e-5 at p~2^32, B = 45). Each prime cuts candidates by ~ q but multiplies the number of image cosets by ~ q^2. Best prime set per cell: e.g. p~2^32, B = 64: N_sq = 1.07e9 -> 6.8e5; B = 128: 1.1e12 -> 5.5e7, versus B = 64 / 128 for lookup and B^2/2 = 2048 / 8192 for pair listing. Exponent of the best sieved cost in B: 6.20 [5.86, 6.81] (2^32, B = 23..128), 6.32 [5.80, 7.02] (2^28), 6.34 [5.73, 6.96] (2^24); theory: Q^2 + N_sq/Q optimised at Q ~ N_sq^{1/3} gives cost ~ N_sq^{2/3} ~ B^{20/3}. The sieve reduces the candidate set but not faster than it costs relative to B; it never reaches B.

### (c) Exponent of the best variant

Best measured variant: per-Delta lattice sweep, exponent ~ 1.8 to 2.0 (pure regime), CI upper bounds 1.96 to 2.11, lower bounds 1.64 to 1.79. Success needs a CI that excludes 1 from above (i.e. < 1); none does.

### Representation-count identity attempt (`repcount.json`)

Per-Delta counts of small forms with root x_R (all c2) for Delta in S_F minus the planted one, versus controls (Delta from pairs just outside the box, and random 16*QR of equal magnitude): 0.09/0.05/0.16 (p~2^20, B=11), 0.00/0.00/0.005 (2^24, 11), 0.028/0.00/0.036 (2^24, 16), 0/0/0 (2^32, 11); square-leading counts are 0 everywhere. At this scale there is no signal separating S_B from generic discriminants; the expected count per Delta is << 1 (a Delta ~ B^6 has few small representatives), so this null is weak (see Limitations).

## Verdict reasoning

The kill criterion is census ratio structured/small-square-leading decreasing like B^{-c} with c >= 1 and no sub-B enumeration. The first part holds with c ~ 10: the exact count N_sq = 4B^10/p matches to 1e-4, and N_both = N_dec = 1 in every enumerated cell, so the ratio is 1/N_sq. The second part holds because the only enumeration with a per-Delta O(1) cost still has to run over |S_F| ~ B^2/8 discriminants (measured exponent 1.8..2.0, CI upper end < 2.2 and lower end > 1.6), which is the cost of listing pairs (x1,x2), and the vector-level enumeration with a prime sieve is worse (exponent ~6.2). The structure S_B has no multiplicative coherence: f(x1) f(x2) with independent x1, x2, so no Delta can be skipped without computing f(x1) f(x2) or an equivalent. No SUCCESS condition (exponent < 1, or a count identity) was met. The prediction of the prereg (vanishing structured fraction, no enumeration faster than B) is confirmed. The Gamma_0(p) correspondence is filed as a known result: the correspondence is correct and computable but gives nothing beyond the Coppersmith/LLL lattice, because the stabiliser of x_R and the box B^4 reproduce the 3-D lattice L_R whose short-vector ceiling is delta ~ 1/10.

## Limitations

* Toy scale: p <= 2^32 (2^64 only for part (b)), B <= 128 for counts, B <= 45 for full enumeration; 4 doublings in B exist for part (b) (p~2^64) and for the exact-count fit only 3.0 doublings (B = 16..128).
* N_both for B > 45 (2^32) was not enumerated; its value 1 is extrapolated from the enumerated cells, and the exponent 9.999 presumes it. The enumerated-cell fits (9.3..10.0) are the direct measurement.
* Target numbers were reduced for large B (Deviation 1); the sieve result is a cost model with idealised setup cost (1 op per image coset), a lower bound on any implementation; only prefix prime sets of 3..199 were used.
* The per-Delta representation count is a weak test (expected count << 1 per Delta at this scale); the Gamma_0(p)/Heegner/geodesic side was not computed (Delta > 0, no CM or class number computation). A theory that counts closed geodesics weighted by the box could in principle give a non-trivial identity; not tested.
* Results concern y^2 = x^3 + 7, m = 2 decompositions only, and are toy-scale measurements on a shared host; no security claim.

## Suggested lead-atlas update

Lead LEAD-ICP-gamma0-binary-form-decomposition (proposed): file as `closed_measured` / known correspondence (Gamma_0(p) orbits = forms with root x_R; with square leading coefficient it is a 2-D lattice coset per discriminant). Deciding numbers: structured/small-square-leading ratio ~ p/(4B^10) (fit c = 9.999 [9.998, 10.000], N_both = N_dec = 1 in all enumerated cells, N_sq = 4B^10/p to 1e-4), best enumeration by discriminant exponent 1.8..2.0 in B (CI excluding 1 from above), small-prime sieve exponent 6.2 [5.9, 6.8]. Next_action: none for the toy-scale census; only a representation-count identity via closed geodesics/Heegner sums for Delta in S_B remains open and cheap to retest only if someone supplies an explicit trace-formula count; do not reopen on enumeration grounds.
