# SA-18 REPORT: determinant-method oracle for S_3(x1,x2,xR) = 0 mod p in a box

## Summary
**VERDICT: KILL.** The provable threshold of the determinant method (p-adic, any multiplicity, any down-closed monomial set) is at most 1/6; it does not exceed the Coppersmith ceiling. Deciding numbers: plain determinant method (multiplicity 1) provable delta* = 9/100 = 0.090 (square [0..4]^2, 25 monomials); optimum over all staircase sets and multiplicities tends to 1/6 from below (0.1646 at 160x160 shapes, t large; never above). Measured LLL thresholds on planted instances: 0.10-0.11 (t=1), 0.11-0.12 (t=2), 0.12-0.13 (t=3), at 40-128 bits. This is the empirical companion of Idea 8: the 1/6 wall is common to the determinant and Coppersmith auxiliary-polynomial methods. The prediction (nontrivial only at or below the Coppersmith reach) holds.

## What was run
- `theory.py`: closed form. Monomial set M (down-closed) in x1,x2, F = S_3(x1,x2,xR) has bidegree (2,2) and monic top term x1^2 x2^2 (coefficient e2^2 = 1). Lattice of integer polynomials on M vanishing on C_R mod p^t has rows p^(t-u(m)) F^u(m) x^.. y^.., u(m)=min(t, floor(min(mx,my)/2)); determinant = prod p^(t-u) B^(mx+my). A vector with l1 norm (scaled by B^(i+j)) below p^t vanishes over Z on every box point (Howgrave-Graham). Condition: delta < sum u(m) / sum(mx+my). Optimisation over all staircase sets by DP with bisection.
- `exp.py`: constructive oracle. Builds that lattice, LLL (fpylll, delta .99), keeps certified vectors (these are the auxiliary curves), takes pairwise resultants over Z (PARI), factors for integer roots in [1,B], gcd for the second coordinate, and verifies each candidate in the group (R = P1 +- P2). Planted known-answer instances, y^2=x^3+7 over nextprime(2^bits) (random (a,b) at 64 bits as control), bits 40/56/64/96/128, delta 0.04-0.18, 10-12 trials per cell, square sets [0..N]^2, N = 3..7, t = 1,2,3.
- `null.py`: random targets with no planted decomposition (3 configs, 49 targets): 0 false positives.
- `summarize.py`, `fig.py`: tables (`thresholds.csv`, `all_rows.json`) and `fig_sa18.png`.

## Results
Provable delta (sum u / sum w), square sets:

| t \ N | 3 | 4 | 6 | 8 | 10 | 16 | 24 |
|---|---|---|---|---|---|---|---|
| 1 | .0833 | **.0900** | .0850 | .0756 | .0669 | .0487 | .0353 |
| 2 | .0833 | .1000 | .1156 | .1142 | .1074 | .0852 | .0647 |
| 4 | .0833 | .1000 | .1190 | .1296 | .1355 | .1289 | .1080 |
| 10 | .0833 | .1000 | .1190 | .1296 | .1364 | .1471 | .1527 |

Optimum over all staircase sets (W x W grid): t=1: 0.0900 (W=40); t=2: 0.1161; t=4: 0.1364; t=8: 0.1497; t large: 0.1583 (W=40), 0.1619 (70), 0.1633 (100), 0.1646 (160). Monotone increasing, converging to 1/6 = 0.1667 from below; rectangles of aspect 4:1 are worse (0.1584).

Measured threshold (largest delta with >= 50% planted recovery, step 0.01), best N per row:

| t | 40 b | 56 b | 64 b | 96 b | 128 b |
|---|---|---|---|---|---|
| 1 | 0.10 | 0.10 | 0.10 | 0.10 | 0.11 |
| 2 | - | 0.11 | - | 0.11 | 0.12 |
| 3 | - | 0.12 | - | 0.12 | 0.13 |

Random-coefficient curve at 64 bits, t=1: 0.09 (all N). Number of auxiliary curves (certified independent vectors) below threshold grows with the lattice: mean 7-10 (N=3, dim 16), 20 (N=4), 34 (N=5), 47 (N=6, dim 49), 62 (N=7, dim 64); it drops to 0 within 0.01-0.02 above the threshold (`thresholds.csv`, last column). No fewer than 2 curves are needed to solve; recovery equals the fraction of cells with >= 2 certified vectors and coprime pair. The planted pair was always the only verified decomposition in the box.

Comparison with Probe B/C: report heuristic Coppersmith reach is 0.14-0.16 at 40-56 bits (level 3, higher dimension, convex shifts with larger multiplicity); the 3-dimensional form lattice gives 0.09-0.10. Our determinant oracle at comparable dimension (t=1: 0.10, t=3: 0.12-0.13) sits exactly on that ladder and below the Coppersmith numbers. The finite-size gain over the asymptotic formula is about +0.01 to +0.02 at dimensions 16-64 (as in Probe B/C); at larger p it does not grow (128-bit values are 0.00-0.01 higher only).

## Verdict reasoning
Frozen criterion: SUCCESS needs a provable threshold above 1/6; KILL if at or below. The determinant bound is the same existence argument as the Howgrave-Graham condition: the p-adic rank deficiency of the monomial evaluation matrix is r = |M| - |shifts|, giving delta < (s-r)/sum(weights); multiplicity-t generalisations give the formula above. Its supremum over down-closed monomial sets is 1/6 (numerically established, converging from below; the continuous limit for the square is the integral of min(x,y)/2 over the integral of (x+y), equal to 1/6; the optimality over all staircases is numerical, not proved). The plain determinant method (t=1) stops at 0.09. Nothing exceeds 1/6, so KILL. Caveat on "provable": counting-bound parts are proved (Hadamard + Howgrave-Graham), the sup = 1/6 claim is numerical for down-closed sets. Non-convex (extended) shift sets are outside this run and are covered by the existing closure map.

## Limitations
Threshold grid is 0.01, 10-12 trials per cell, LLL only (no BKZ); dimension capped at 64, so finite-size slack is not separated from asymptotics beyond what the 40->128 bit comparison shows. Single curve family at 5 sizes plus one random curve. Down-closed shape optimum only. The CCGHSZ paper (arXiv:1111.1543) was only seen at abstract level. Toy-scale measurements, not security claims.

## Suggested lead-atlas update
LEAD-ICP-determinant-method-oracle (proposed): disposition closed-negative. Next action: none beyond citing it as the numerical companion to Idea 8. Deciding numbers: plain p-adic determinant delta* = 0.090, multiplicity-extended sup -> 1/6 from below (0.1646 at 160x160), measured 0.10-0.13 at 40-128 bits, and 0 false positives on 49 unplanted targets. It confirms that determinant and Coppersmith auxiliary-polynomial methods share the 1/6 wall for S_3; the m=3 oracle needs 1/2 to be useful.
