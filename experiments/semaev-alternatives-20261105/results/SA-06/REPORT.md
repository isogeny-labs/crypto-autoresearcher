# SA-06 REPORT: torsion-symmetrised and special-j presentations fed to lattices

## Summary

**KILL** against the frozen criterion. At m = 4 (S_5, four small unknowns, target x_R a full-size modular parameter) every one of the six cells has JM-basic asymptotic reach exactly 1/80 = 0.0125, below the kill line 1/40 = 0.025 and 16 times below the success line 1/5. An extended-shift search over regions Newt(f) + box moved no m = 4 value by more than 0.12% (MC noise level).

Deciding numbers:
- The Newton polytope of S_{m+1}(x_1..x_m, x_R) projected onto the small variables is the full box [0, 2^{m-1}]^m in all six cells (plain generic, j = 0, j = 1728, and each with 2-torsion symmetrisation): 9/9, 125/125, 6561/6561 monomials. The j = 0 / j = 1728 sparsity (S_3: 9 or 10 monomials instead of 13; S_5: 18,882 / 24,309 instead of 54,777) lives entirely in powers of x_R, which is a modular constant for the lattice, so the polytope does not shrink.
- Reach per cell is therefore identical: 1/6, 1/24, 1/80 at m = 2, 3, 4. The prediction "1/6 to 1/5 at m = 2 for j = 0" is false in the stronger direction: the change is exactly zero.
- Planted fpylll recovery on S_3 shows the same sharp threshold in all six cells (96-bit p, 24 trials per point): t = 2 at delta_t = 0.100, t = 3 at delta_t = 0.119, asymptote 1/6 = 0.167.

## What was run

All scripts and raw outputs are in this directory.

1. `polys.py`, `supports.py`, `check.py`: S_3 explicit; S_4 = Res_Y(S_3(x1,x2,Y), S_3(x3,x4,Y)); S_5 = Res_Z(S_3(x1,x2,Z), S_4(Z,x3,x4,x5)), by PARI `polresultant`. Cells: generic (a,b) = (3,5) and (-7,11), j = 0 (0,7), j = 1728 (7,0). S_5 verified numerically: it vanishes at 3/3 random 4-point sums on a 20-bit curve; degree 8 in each variable. Exact supports saved in `supports.json`.
2. `symm2.py`: 2-torsion-symmetrised polynomial on curves with a rational 2-torsion point T = (tau, 0): generic y^2 = x^3 + 2x - 3 (tau = 1), j = 0 y^2 = x^3 - 8 (tau = 2), j = 1728 y^2 = x^3 + 7x (tau = 0). With w = x - tau, c = 3 tau^2 + a, the translation by T acts as w -> c/w, the invariant is u = w + c/w, and f(u) = S(x) * S(x_1', x_2, ...) / prod_{i>=2} w_i^d (d = 2^{n-2}). Obtained by tensor-grid interpolation mod a 61-bit prime, checked at a fresh point in all 18 cases. Zero set: some sign pattern eps with sum P_i + eps_i T = +-R (the even-flip subgroup of index 2 stabilises V(S), so only two cosets enter, giving degree d, not 2d, per u-variable). Supports in `supports_sym.json`.
3. `reach_all.py`, `finite_t.py`: asymptotic JM-basic reach from the Newton polytope (derivation below), validated against exact finite-t lattice-point sums.
4. `l2.py`: numerical search for better convex shift regions K = Newt(f) + [0,e]^n, greedy optimal levels, 3 leading vertices per cell (n <= 4).
5. `planted.py`: planted S_3 instances, JM-basic bivariate lattice at t = 2 (dim 25) and t = 3 (dim 49) with fpylll LLL, 96-bit prime, 24 trials per point, six cells. Plain cells plant R = P_1 + P_2 with x_i <= X; symmetrised cells plant integer invariants u_i <= X (both quadratics w^2 - u w + c split, points on the curve). Success = a real solver recovers the root: some pair among the first five reduced polynomials has a nonzero resultant (in x_2) vanishing at the planted x_1. All planted roots were checked to satisfy f = 0 mod p before the lattice was built.

### Derivation of the asymptotic reach (proved for the JM-basic family, my own derivation)

Let P be the Newton polytope of f(x_1..x_n) mod p, translated to touch the axes, a_0 a vertex (leading monomial, coefficient normalised to 1), V = vol P, g = centroid of P, all unknowns bounded by X = p^delta. The JM-basic lattice has monomial set M_k = (t-k)P + k a_0 (k = 0..t), rows x^{a - k a_0} f^k p^{t-k} for a in M_k \ M_{k+1}, triangular with diagonal p^{t-k} X^a. The Howgrave-Graham condition det < p^{t |M_0|} reads X^{sum_{a in M_0} |a|} < p^{sum_k k |M_k \ M_{k+1}|} = p^{sum_{k>=1} |M_k|}. As t grows, |M_k| ~ t^n V (1 - k/t)^n, so sum_{k>=1}|M_k| ~ t^{n+1} V/(n+1) and sum_{a in M_0} |a| ~ t^{n+1} V sum_i g_i. Hence

delta_JM = 1 / ((n+1) * sum_i g_i),

independent of a_0. For the box [0,d]^n this gives 2/(n(n+1)d), which with n = m, d = 2^{m-1} reproduces the campaign values 1/6, 1/24, 1/80 exactly (the sum_k (t-k)... form used in `tools/smallroot_reach.py` is the determinant exponent, not the gain, which is the CORRECTION already recorded in the repository). Check against exact finite-t sums on the three non-box S_3 all-small polytopes (3 unknowns): exact t = 4, 8, 12 values 0.0635, 0.0771, 0.0822 (generic) extrapolate to 0.0924 against formula 0.0933; j = 0: 0.0899 vs 0.0909; j = 1728: 0.0822 vs 0.0833 (`finite_t.log`). Agreement within 1.2%.

Monotonicity (proved, trivial): if supp f is contained in a polytope P', any lattice built for P' also works for f. So the best reach for a sparser polynomial is at least the best reach for the denser one; special-j can never be worse than generic under an optimal strategy, but JM-basic on the sparser hull can be worse (see all-small table).

## Results

### Table 1. Asymptotic reach, decomposition of a random target (m unknowns, x_R modular). This is the criterion cell.

Support counts are monomials in the m small variables after projecting out x_R. "full" = all monomials of the box.

| cell | S_3 (m=2) | S_4 (m=3) | S_5 (m=4) | projected support | delta_JM (m=2 / 3 / 4) |
|---|---|---|---|---|---|
| generic (a,b) | 9/9 | 125/125 | 6561/6561 | full box | 1/6, 1/24, 1/80 |
| j = 0 | 9/9 | 125/125 | 6561/6561 | full box | 1/6, 1/24, 1/80 |
| j = 1728 | 9/9 | 125/125 | 6561/6561 | full box | 1/6, 1/24, 1/80 |
| generic + 2-torsion (u-vars) | 9/9 | 125/125 | 6561/6561 | full box | 1/6, 1/24, 1/80 |
| j = 0 + 2-torsion | 9/9 | 125/125 | 6561/6561 | full box | 1/6, 1/24, 1/80 |
| j = 1728 + 2-torsion | 9/9 | 125/125 | 6561/6561 | full box | 1/6, 1/24, 1/80 |

Monomials of the full (m+1)-variable polynomial, for context: generic 13 / 439 / 54,777; j = 0 9 / 191 / 18,882; j = 1728 10 / 225 / 24,309. Degree per variable 2^{m-1} in every cell (2-torsion symmetrisation does not lower the per-u-variable degree).

Extended-shift search (`l2_results.json`, MC): generic S_3 +0.000%, S_4 +0.02%, S_5 +0.12% over JM-basic. These are within MC noise: no gain.

### Table 2. Same polytopes with all m+1 variables small (tree-internal-node / windowed setting). Not the criterion cell; shown because here the polytope does change.

| cell | S_3 monos | S_3 JM-basic | S_3 extended | S_4 monos | S_4 JM-basic | S_4 extended | S_5 monos | S_5 JM-basic |
|---|---|---|---|---|---|---|---|---|
| generic | 13 | 1/10.7 (0.0933) | 0.0938 | 439 | 1/39.0 (0.0256) | 0.0258 | 54,777 | 1/119.3 |
| j = 0 | 9 | 1/11.0 (0.0909) | 0.0920 | 191 | 1/39.1 (0.0256) | 0.0257 | 18,882 | 1/119.4 |
| j = 1728 | 10 | 1/12.0 (0.0833) | 0.0923 | 225 | 1/40.0 (0.0250) | 0.0258 | 24,309 | 1/120.0 |
| generic + 2-tors | 14 | 1/10.7 | | 479 | 1/39.0 | | 55,537 | 1/119.3 |
| j = 0 + 2-tors | 14 | 1/10.7 | | 479 | 1/39.0 | | 55,367 | 1/119.3 |
| j = 1728 + 2-tors | 10 | 1/12.0 | | 225 | 1/40.0 | | 24,309 | 1/120.0 |

Reading: fewer monomials give a smaller hull but a larger centroid sum, so JM-basic is slightly worse (not better) on the special-j polytopes. A better shift region recovers most of the loss (j = 1728 S_3: +10.5%, to 0.0923) but does not exceed the generic value within the search, and the spread across cells is at most about 10% in delta. Under an optimal strategy monotonicity gives special >= generic, but my search did not find the improvement, so it is a lower bound only. In this convention S_4 sits near 1/39 and S_5 near 1/120: nothing approaches 1/5 at m = 4.

### Table 3. Planted fpylll recovery, S_3, 96-bit p, 24 trials per point (successes / 24)

Columns are delta / delta_t, where delta_t is the JM-basic prediction at level t.

t = 2 (dimension 25, delta_t = 0.100):

| cell | 0.80 | 0.95 | 1.05 | 1.15 | 1.30 | 1.50 |
|---|---|---|---|---|---|---|
| generic | 24 | 24 | 24 | 23 | 0 | 0 |
| j = 0 | 24 | 24 | 24 | 22 | 2 | 1 |
| j = 1728 | 24 | 24 | 24 | 22 | 4 | 0 |
| generic + 2-tors | 24 | 24 | 24 | 23 | 4 | 0 |
| j = 0 + 2-tors | 24 | 24 | 24 | 23 | 1 | 0 |
| j = 1728 + 2-tors | 24 | 24 | 24 | 23 | 6 | 0 |

t = 3 (dimension 49, delta_t = 0.119):

| cell | 0.80 | 0.95 | 1.05 | 1.15 | 1.30 | 1.50 |
|---|---|---|---|---|---|---|
| generic | 24 | 24 | 24 | 2 | 0 | 0 |
| j = 0 | 23 | 24 | 24 | 1 | 0 | 0 |
| j = 1728 | 24 | 24 | 24 | 2 | 0 | 0 |
| generic + 2-tors | 24 | 24 | 24 | 0 | 0 | 0 |
| j = 0 + 2-tors | 24 | 24 | 24 | 3 | 0 | 0 |
| j = 1728 + 2-tors | 24 | 24 | 24 | 2 | 0 | 0 |

The success cliff sits at delta_t (t = 3) or just above it (t = 2) in every cell, and the cells are statistically indistinguishable (control: the generic cell). The level-t thresholds 0.100 and 0.119 climb toward the asymptote 1/6 = 0.167 as the polytope formula predicts. The single j = 0 failure at 0.80 (t = 3) is one trial in 24.

Figure: `fig_sa06.png` (left and middle: reach per cell in both conventions with the 1/5 and 1/40 lines; right: planted recovery curves). Table file: `results_table.csv`.

## Verdict reasoning

Criterion (frozen): success if any cell reaches >= 1/5 at m = 4; kill if all cells are below 1/40 at m = 4. The m = 4 cells are S_5 with four small unknowns. All six have delta = 0.0125 (1/80) under JM-basic, and the extended-shift search found at most +0.12% on the generic S_5 box. 0.0125 < 0.025, so the kill condition holds. The mechanism is structural rather than a toy-scale accident: the specialness removes monomials only in the x_R direction, and x_R is a full-size modular constant, so for the unknown variables the polytope is the same full box. For the 2-torsion cells the per-variable degree stays 2^{m-1} and the support is again a full box.

Why a smaller polytope could still help in principle, and why it does not here: the lattice reach depends on the hull and its centroid, not the monomial count (the prereg point). That is exactly what the all-small Table 2 shows: the hull does shrink there (vol/box 0.56 for j = 0 and 0.33 for j = 1728 at S_3) and the effect on reach is at most a few percent, of either sign. Neither convention comes within a factor 10 of 1/5 at m = 4.

Reading against the prediction: the prediction said polytope shrinkage raises reach by a constant factor (1/6 to 1/5 at m = 2, 1/80 to about 1/60 at m = 4). Measured: factor 1.00 in the criterion cells. The direction "never to 1/2" holds trivially. The question "is secp256k1's j = 0 a lattice-relevant specialness" is answered no, at this resolution.

## Limitations

- Reach values are for equal per-variable bounds. Unequal-bound allocations (which the repository's optimiser says stop at 1/2 per S_3 block, numerical) were not explored here.
- Not provably optimal-shift certificates: cuso, the sumset calculator, the Ehrhart check and the LP cross-check did not install or were not run (DEVIATIONS.md). My "extended" numbers are a Monte Carlo search in a restricted region family with a handful of restarts, so they are lower bounds on the best convex-shift reach. The inherited strategy-independent bound for the full box (1/70.8 for S_5, from the campaign report, not re-derived) is identical for all six criterion cells because it depends only on the polytope, which is the same box; if that bound is right the kill is strategy-independent.
- Reach assumes algebraic independence of the short vectors; planted runs confirm this for S_3 at t <= 3 only, not S_4 or S_5.
- Aut-symmetrisation (mu_3 at j = 0, mu_4 or sign at j = 1728) was not computed. Sketched: V(S) has no stabiliser in the group of automorphism actions on the x_i (x(-P) = x(P)), so the norm over the group has degree d * |G|^{m-1} in the invariant (for j = 1728, v = x^2, m = 2: degree 4 in v, bound p^{2 delta} in v), and the reach in the original x bound is expected to drop, not rise. Conjectured, not computed.
- Toy scale: one 96-bit prime, t <= 3 for the planted runs, single curves per cell (the two generic curves gave identical support counts). Nothing here is a security statement about a deployed curve.
- Symmetrised supports come from mod-61-bit-prime interpolation (small risk of an accidental zero coefficient, about 1e-17 per coefficient).

## Suggested lead-atlas update

LEAD-STR-special-j-ic-semaev and LEAD-ICP-xline-symmetry-special-j: record the lattice side as closed (disposition: closed for single-polynomial convex lattices; the open part stays Macaulay-rank only). Deciding number: the projection of S_{m+1} onto the m small variables has a full-box Newton polytope for j = 0, j = 1728 and generic, with and without 2-torsion symmetrisation (9/9, 125/125, 6561/6561 monomials), so certified reach is 1/6, 1/24, 1/80 in every cell and the m = 4 value is 1/80, a factor 2 below the kill line 1/40 and 16 below the success line 1/5; planted fpylll S_3 cliffs coincide across all six cells (t = 3 at 0.119). Add a lemma line: "special-j and 2-torsion sparsity of S_m lives in x_R-powers and does not shrink the polytope in the small unknowns". Revisit only if a presentation makes x_R (or the torsion/Aut structure) part of the unknown set with a small bound, or if a non-convex shift region is proposed. This does not enter the IC leaderboard.
