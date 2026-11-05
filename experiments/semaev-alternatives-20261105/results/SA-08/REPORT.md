# SA-08: capacity-theoretic certification of the lattice ceiling (S_3, m = 2)

## Summary

**Verdict: INCONCLUSIVE (null on the frozen criterion).** The criterion is "a proved threshold for the class of auxiliary-polynomial methods"; that was **not** obtained. What was obtained is a partial result of a different kind: for the realised instances, the class of all valid auxiliary functions is exactly the Rees algebra Z[x,y][f/p] (steps T2-T3 below, proved or sketched with numerical verification), and over **every** monotone support in that algebra, convex or not, the Minkowski/determinant ceiling is exactly **1/6** (m = 2) and **1/24** (m = 3). Passing from "no determinant argument beats 1/6" to "no auxiliary polynomial exists above 1/6" is the open step (T5), and I give reasons to think the capacity mechanism of CHFHS cannot supply it at 1/6.

Deciding numbers: determinant-LP minimum over all down-closed supports = 0 exactly at delta = 1/6 (grids 10, 30, 60; scales as n^3 below 1/6); m = 3 LP threshold 0.042318 = single-cube value (1/24 up to quadrature); planted 50% crossings 0.125-0.146 for dimension 9-121 lattices at 40-56 bits, rising with K as the determinant formula predicts (within -0.011 / +0.009 for K >= 3).

## What was run

All in `/home/user/semaev-runs/SA-08/`, single-threaded, nice 10.

| script | purpose | output |
|---|---|---|
| (read) `chfhs.pdf/.txt` | CHFHS arXiv:2111.14180 full text (fetched) | |
| `smooth_check.py` | is the affine curve S_3(x,y,r)=0 over F_p smooth? Groebner basis of (f,f_x,f_y) mod p | `smooth_check.json` |
| `gb_check.py` | exact HNF of I^K intersect Z^R (I=(p,f)), cancellation allowed, vs triangular determinant | `gb_check.json` |
| `lp_ceiling.py`, `lp_exact_check.py` | min-weight-closure LP (HiGHS) over all down-closed supports, m = 2, 3 | `lp_ceiling.json`, `lp_exact_check.json` |
| `planted.py`, `analyze.py` | planted 2-decompositions, Rees/Coppersmith lattice K = 1..5, fpylll LLL + PARI resultant | `planted_*_*.json/.log`, `threshold_table.md`, `fig_threshold.png` |

## The argument, step by step

Setup. E: y^2 = x^3 + a x + b over F_p, R = P_1 + P_2 with x(P_i) = x_i <= B = p^delta, r = x_R. f(x,y) := S_3(x,y,r) in Z[x,y], bidegree (2,2), monic in x^2y^2. Valid output of an auxiliary-polynomial (HG/CHFHS) method: g in Q[x,y] with (i) g(s) algebraic-integral for every algebraic-integer solution s of f(s) in pZ-bar, and (ii) |lambda(g)(x',y')| < 1 on the box for all conjugates (CHFHS Problem 1.3).

- **T0 [proved, standard]. Soundness and obstruction.** Any g with (i),(ii) vanishes on all solutions (norm argument, CHFHS section 1.2); if the set of box solutions in Z-bar is infinite and Zariski-dense in a curve, no family has finite common zero locus. (CHFHS Thm 3.4 does this for the linear case via capacity > 1 on the line g_1 = 0.)
- **T1 [proved, CHFHS]. What the paper covers.** Two-variable *linear* congruences x + t y + a = 0 mod J: first auxiliary function by Minkowski (Thm 2.1), then a capacity dichotomy on its zero line (Thm 3.4: gamma(E) > 1 gives infinitely many solutions and no second independent function; gamma(E) < 1 gives a second function). Nothing in the paper treats a bidegree-(2,2) polynomial with coefficients of size p, so **the prediction "apply CHFHS to S_3" is not a direct application**; an extension is needed.
- **T2 [proved given smoothness; smoothness checked on 180/180 instances, not proved in general]. Valid auxiliary functions = Rees algebra.** X = Spec Z[x,y,t]/(pt - f). It is regular at the fibre over p iff the affine curve C-bar: f = 0 over F_p is smooth, and equals A^2 away from p. Checked: Groebner basis of (f,f_x,f_y) mod p is [1] for 60 random planted instances at each of 40, 48, 56 bits. Then X is smooth over Z, so Z[x,y][f/p] is normal; a function in Q(x,y) integral at all Z-bar points of X (Hensel lifting of F-bar_l points is available because X is smooth) lies in it. Hence **every function satisfying (i) is a Z-combination of x^i y^j (f/p)^k**, i.e. exactly the Coppersmith shift polynomials with arbitrary shift sets and degrees; (ii) is the only remaining constraint. Gaps: smoothness for all r (expected: fails only for O(1) residues r, not proved), and the Hensel/valuative step is a sketch.
- **T3 [sketched; verified by exact computation]. Determinant of the full lattice.** For support R=[0,A]^2 the lattice Lambda = I^K (scaled) intersect Z^R has determinant prod_{(a,b) in R} p^(K - kappa), kappa = min(K, floor(min(a,b)/2)): the triangular leading-monomial family is *all* of it (strong Groebner structure of powers of (p,f), LM(f) = x^2y^2 monic). Verified with exact HNF allowing cancellation in a support enlarged to [0,8]^2: (p,A,K) = (101,4,2), (101,4,3), (65537,4,2) all give det_measured = predicted (`gb_check.json`). Not proved in general.
- **T4 [numerically verified exactly on grids; analytic proof not written -> sketched]. Determinant ceiling over all supports is the cube.** Condition for a nonzero vector of sup-norm < 1 by Minkowski: sum over support of [delta (a+b) - kappa(a)] < 0 (asymptotically kappa = min a_i / d, d = 2^(m-1)). Minimising over down-closed supports is a minimum-weight closure problem (totally unimodular LP). With exact cell integrals the minimum is **-4, -108, -864 at delta = 1/6 - 0.004 (n = 10, 30, 60; cubic in n), and 0 at delta = 1/6 and 1/6 + 0.004** (`lp_exact_check.json`). So no support, convex or not, beats 1/6 for m = 2. For m = 3 the LP threshold 0.0423176 equals the single-cube value (0.0423177 with the same quadrature; exact 1/24); m = 4 (1/80) is the cube formula only, LP **not run -> conjectured**. This reproduces the repository's 1/6, 1/24, 1/80 and shows they are the optimum of the *whole* triangular/Rees determinant family, not of convex shift sets only. (The repository's separate "strategy-independent bound 1/21.8 for S_4" is larger than 1/24; that class uses structure beyond leading-monomial triangularity and is not covered here.)
- **T5 [OPEN; conjectured both ways]. From determinant ceiling to impossibility.** Minkowski's first theorem is only sufficient: it gives a nonzero g with sup < 1 when delta < 1/6 (asymptotically). Nonexistence for delta > 1/6 needs lambda_1(Lambda) >= 1, which a determinant cannot give; the data show the Gaussian heuristic is *not* a converse at small dimension (K = 1: measured crossing 0.126 against determinant 0.056). In the CHFHS linear case the converse comes from capacity (Cantor/Rumely Fekete-Szego on the line); the analogue here is Zhang's successive-minima inequality on the arithmetic threefold X with the adelic set (polydisc B at infinity, {|f/p| <= 1} at p), which I did not compute. A heuristic count points the other way: solutions in a degree-n field number about (c B^2 / p)^n / sqrt|D_K|, so an infinite Zariski-dense family of algebraic-integer solutions (CHFHS alternative 2, the only mechanism that gives a *no-polynomial* theorem) appears only around **delta ~ 1/2**, not 1/6. If that heuristic is right, a capacity argument certifies at most the trivial 1/2 list-size bound, and the gap (1/6, 1/2) is governed by whether a *second algebraically independent* function exists, which is the finer, lattice-specific half of the dichotomy. **Conjecture A:** Lambda has no vector below Gaussian heuristic asymptotically for S_3 (would give ceiling 1/6). **Conjecture B:** capacity-type reach exceeds 1/6. Neither is supported or refuted by this run.

## Results: planted experiments (fpylll, 40-56 bits)

Lattice: shifts g_ab = x^(a-2k) y^(b-2k) f^k p^(K-k), k = min(K, floor(min(a,b)/2)), a,b <= 2K, dimension (2K+1)^2, columns scaled by B^(u+v), LLL, success = resultant of two of the six shortest polynomials is nonzero and has planted x_1 as an integer root. Curve y^2 = x^3 + 7, p = nextprime(2^bits), 24 trials/point (K <= 3), 12 (K = 4), 8 (K = 5, 56 bits only). Full tables: `planted_*.json`, `threshold_table.md`; figure `fig_threshold.png` (grey band = 0.14-0.16, dashed = 1/6).

| p bits | K | dim | determinant delta_K | delta_K + 1/bits (x ~ B/2) | measured 50% crossing |
|---|---|---|---|---|---|
| 40 | 3 | 49 | 0.1190 | 0.1440 | 0.1391 |
| 40 | 4 | 81 | 0.1296 | 0.1546 | 0.1455 |
| 48 | 3 | 49 | 0.1190 | 0.1399 | 0.1380 |
| 48 | 4 | 81 | 0.1296 | 0.1505 | 0.1462 |
| 56 | 3 | 49 | 0.1190 | 0.1369 | 0.1342 |
| 56 | 4 | 81 | 0.1296 | 0.1475 | 0.1443 |
| 56 | 5 | 121 | 0.1364 | 0.1542 | ~0.145 (8/8 at 0.14, 0/8 at 0.15) |
| 40/48/56 | 1 | 9 | 0.0556 | 0.073-0.081 | 0.131 / 0.127 / 0.126 |
| 40/48/56 | 2 | 25 | 0.1000 | 0.118-0.125 | 0.129 / 0.130 / 0.125 |

(K = 1, 2 rows summarised; the full table is in `threshold_table.md`.) Transitions are sharp (24/24 to ~0-5/24 within 0.01-0.02 in delta). The determinant formula delta_K = sum(kappa)/sum(a+b) tends to 1/6 slowly (K = 5: 0.136, K = 10: 0.151, K = 11: 0.152).

Reading against the prereg's "0.14-0.16" heuristic band: measured crossings are in the band for K = 4, 5 (0.144-0.146) and just below it for K = 3 (0.134-0.139); K <= 2 are below. The extrapolation to K -> infinity would put the finite-size crossing near 1/6 + 1/bits, i.e. 0.18-0.19, outside the band; the band is therefore a statement about K = 4-5 lattices at these sizes, not about the asymptotic ceiling. The numerics confirm the determinant model for K >= 3 (error between -0.011 and +0.001 after the B/2 correction at 48-56 bits, -0.009 at 40 bits for K = 4); they do not test the converse T5 at all, since a lattice that fails does not show no polynomial exists.

## Verdict reasoning

Frozen criterion: "a proved threshold for the class of auxiliary-polynomial methods." Not met. The prediction "capacity bound equals 1/6" is not established, and the mechanism it names (CHFHS capacity) is, by T1 and the counting heuristic in T5, unlikely to produce 1/6. The proved/verified content is a determinant ceiling over the complete set of valid auxiliary functions (T2-T4), which is a genuine strengthening of "closed for convex lattices" to "no support whatsoever beats 1/6 by the Minkowski argument," but it is not a nonexistence theorem. Per the prereg there is no kill; this is a null.

## Limitations

- T2 smoothness checked on 180 instances of one curve (a = 0, b = 7); T3 verified for three (p, A, K); T4 on grids to n = 60 (m = 2) and n = 9 (m = 3), with sub-sampled quadrature in m = 3.
- No sectional-capacity computation of any kind; Zhang/Chambert-Loir height of the arithmetic threefold not attempted.
- Triangular leading-monomial family only; extended-shift or non-triangular lattices (Jochemsz-May style, which the repository's 1/21.8 bound for S_4 may use) were not analysed. T3 shows the m = 2 full lattice has no extra vectors *in the determinant*, not that its shortest vector equals the Gaussian prediction.
- Planted data: toy sizes, one curve, K <= 5, 8-24 trials per point; 50% crossings by linear interpolation without bootstrap CIs (binomial noise at 24 trials is about +/- 0.1 in rate, roughly +/- 0.003 in delta given the slopes).
- The B/2 correction is an ad hoc 1-parameter fit of the constant, not a prediction.

## Suggested lead-atlas update

LEAD-ICP-coppersmith-smallroot-semaev: add to the closure statement that the determinant ceiling is 1/6 (m = 2) and 1/24 (m = 3) over *all* down-closed Rees-algebra supports (min-closure LP, exact at n = 60, value 0 at delta = 1/6) and that the Rees algebra Z[x,y][f/p] is the full set of valid auxiliary functions when the fibre curve is smooth (checked 180/180); keep the disposition "closed for determinant/Minkowski arguments", **not** "closed for all auxiliary-polynomial methods". Change next_action for the capacity converse follow-up to: "needs Zhang-type successive-minima computation on the arithmetic threefold, or a lower bound on lambda_1 of the Rees lattice; CHFHS covers only linear 2-variable congruences and the infinite-solution mechanism is expected only near delta = 1/2." Deciding number: LP minimum 0 at delta = 1/6 (and -4/-108/-864 just below).
