# SA-19 report: lowering the degree budget of the form lattice (alternative relation polynomials)

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write.)

## Summary

**INCONCLUSIVE** against the frozen criteria, with the question itself decided: the smallest degree budget attainable in the prereg's families a–d at m = 2 is **8, not 9**, and 8 is attained only by the twisted-Edwards y-coordinate class (a degree-2 even coordinate whose two poles are a pair of points of exact order 4). Its predicted reach is 1/8 = 0.125, which falls between the KILL ceiling (1/9 + 0.01 = 0.121) and the SUCCESS line (1/9 + 0.02 = 0.131), so neither frozen criterion can be met.

Deciding numbers:

- Budget of S_3 in twisted-Edwards y: degree sequence [2, 2, 4], **w = 8** (Weierstrass/Montgomery x: [2, 3, 4], w = 9). Every other coordinate class computed has w ≥ 9 (table below); for all even degree-2 coordinates w ≥ 8 is **proved** (computer algebra), with equality exactly at the order-4 pole pair.
- Measured planted-recovery threshold of the budget-8 form lattice (40 trials per δ, LLL, exact proportionality to the planted vector): **0.1246 [0.1229, 0.1280] at 64 bits, 0.1267 [0.1250, 0.1278] at 96 bits, 0.1245 [0.1234, 0.1262] at 128 bits**; control (Weierstrass x, budget 9): 0.1120, 0.1135, 0.1132 (SA-17/SA-13: 1/9). Recovery at δ = 0.135 is 6/40, 4/40, 1/40: the SUCCESS requirement (≥ 50% above 0.131) fails; the KILL requirement (no threshold above 0.121) also fails.
- End-to-end: 20/20 recovered Edwards vectors at 96 bits, δ = 0.11, solve to (y_1, y_2), lift to points and verify P_1 + P_2 = R in the group.
- Multi-equation lattices at modulus p (family c): minimum effective budget w/r over all searched coefficient spaces is 9 (Weierstrass) and 8 (Edwards), attained only at r = 1; symmetric (Vieta) spaces reach at best w/r = 14.4, total-degree spaces 15.7, box spaces 11.1 (counting only). Multi-equation at modulus p buys nothing.
- m = 3: budget of S_4 in Edwards y is **46** against 50 (reach 0.0217 vs 0.020; the SUCCESS line 0.025 would need w ≤ 40).

The prereg prediction "no relation in families a–d has budget < 9" is **refuted** (by exactly one unit); the prediction that multi-equation lattices gain at most a constant factor below 2 is **met** (they gain nothing at modulus p).

## What was run

All runs single-threaded under `nice -n 10` on the shared host, about 35 minutes of compute in total, memory under 300 MB.

1. **Budget machinery** (`lib19.py`). A relation F = Σ_l c_l(x) M_l(R) has coefficient space W = span(c_l); its budget w(W) is the sum of the degree sequence of W (SA-13 convention, basis invariant), computed by rank over F_p, p = 2^31 − 1, at random specialisations (checked at two). For a coefficient space with r = dim(W ∩ (S_R)) independent congruences the effective budget is w/r. Summation polynomials S^φ for an arbitrary coordinate φ ∈ k(E) are obtained by interpolation over F_p (nullspace of the monomial evaluation matrix at random triples P_1 + P_2 + P_3 = O), restricted to the symmetry classes of monomials when φ is a torsion-translation eigenfunction.
2. **Family (a), coordinates** (`coords.py`, `coords2.py`, `coords3.py`): Weierstrass x, affine/Montgomery x, generic Möbius functions of x, 1/(x − x_Q) for Q of every order 2..16 (except 15) and generic Q on random curves found with PARI, twisted-Edwards y, odd Edwards x, non-even degree-2 functions with pole sum a 3-torsion point or generic, degree-3 functions (generic, L(O + T + 2T) generic, and the ω-eigenfunction of translation by the 3-torsion point T = the Hessian coordinate class).
3. **Proof for the Möbius family** (`moebius_proof.py`): S^φ for φ = 1/(x − c) is (u_1 u_2 u_3)^2 S_3(c + 1/u_1, c + 1/u_2, c + 1/u_3); the two rank conditions that lower the degree sequence are computed symbolically in Z[a, b, c] and compared with the 4-division polynomial.
4. **Family (b)/(c), multi-equation** (`search_c.py`, `search_c.py ed`, `sym_budget.py`): w/r for total-degree spaces P_{≤d}, boxes, rectangles, symmetric (Vieta) spaces in (e_1, e_2) with weights (1, 2), x-side spans of multiplier sets {x^α X^j S_3}, 600 random sparse multiplier sets, 1586 exhaustive monomial sets (box plus degree-5 monomials), 12 hill climbs over monomial sets of degree ≤ 8; all for Weierstrass S_3 and again for the Edwards polynomial.
5. **Planted recovery** (`lattice19.py`, `analyze.py`, `e2e_edwards.py`): generalised form lattice with the degree-echelon basis of W over Q (so the unknown vector has the degree-sequence sizes), r congruences mod p, columns weighted B^{deg}, fpylll LLL (δ = 0.99), success = first reduced vector proportional to the planted vector. δ from 0.09 to 0.16 in steps of 0.005, 40 trials each, random 64/96/128-bit primes, curves y^2 = x^3 + x + 1 and v^2 = u^3 + 6u^2 + u (twisted Edwards a = 8, d = 4; y = (u − 1)/(u + 1); planted y_i ∈ [2, B + 1]). Multi-congruence lattices (symmetric spaces, boxes, multiplier spans) at 64/96 bits, 20 trials.
6. **m = 3** (`m3.py`): interpolated S_4 in Weierstrass x and Edwards y (4 variables, degree 4 each) and their budgets; w/r of total-degree spaces against S_4.

## Results

### Family (a): single-relation budget by coordinate class (`results/coords*.json`)

| coordinate φ (degree, pole divisor) | model | deg_{u_3} S^φ | coefficient degrees | degree sequence | w | reach 1/w |
|---|---|---|---|---|---|---|
| x, αx + β (2, 2(O)) | Weierstrass, Montgomery x | 2 | 4, 3, 2 | [2, 3, 4] | 9 | 0.111 |
| 1/(x − x_Q), Q generic or of order 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16 (2, (Q) + (−Q)) | generic Möbius, Edwards-y-like with other poles | 2 | 2, 4, 4 (order 2: 2, 3, 4) | [2, 3, 4] | 9 | 0.111 |
| **1/(x − x_Q), Q of exact order 4 (2, (Q) + (−Q))** | **twisted Edwards y** | 2 | 4, 2, 4 | **[2, 2, 4]** | **8** | **0.125** |
| double pole at a 3-torsion point; poles (O) + (−T), T 3-torsion (2, non-even) | — | 2 | 4, 3, 2 / 4, 4, 3 | [2, 3, 4] | 9 | 0.111 |
| double pole at generic Q (2, non-even) | — | 4 | 8, 8, 8, 8, 8 | [5, 6, 6, 7, 8] | 32 | 0.031 |
| odd Edwards x = u/v (2, two 2-torsion poles) | Edwards x | 4 | 4, –, 6, –, 8 | [4, 6, 8] | 18 | 0.056 |
| ω-eigenfunction in L(O + T + 2T), T of order 3 (3) | Hessian class | 9 | 18, 14, 16, …, 9 | [8, 9, …, 18] | 126 | 0.0079 |
| generic element of L(O + T + 2T) (3) | — | 9 | 18, 16, 16, …, 9 | [9, 10, …, 18] | 134 | 0.0075 |
| y/(x − c) (3, generic) | — | 9 | 18, 17, 18, …, 11 | [11, 12, …, 18] | 147 | 0.0068 |

The Edwards summation polynomial with A = 6 (a = 8, d = 4) lifts to the integers as y_1^2 y_2^2 y_3^2 − (y_1^2 y_2^2 + y_1^2 y_3^2 + y_2^2 y_3^2) + 2(y_1^2 + y_2^2 + y_3^2) − 2 y_1 y_2 y_3 − 2; its coefficient space is span(y_1 y_2, y_1^2 + y_2^2, y_1^2 y_2^2 − y_1^2 − y_2^2 + 2): all odd-degree terms in (y_1, y_2) vanish because y(P + T_2) = −y(P) forces e_1 ≡ e_2 ≡ e_3 (mod 2) on every monomial, so after cancelling the quartic top the next element already has degree 2.

### Lower bound for even degree-2 coordinates (`results/moebius_proof.json`)

For φ = 1/(x − c) (every Möbius function of x is an affine function of such a φ or of x; affine changes preserve the degree filtration):

- the u_3-coefficient vectors of the degree-4 and degree-3 monomials of S^φ in (u_1, u_2) are c_22 = (0, −4(c^3 + ac + b), a^2 − 6ac^2 − 12bc − 3c^4), c_21 = c_12 = (0, −2(a + 3c^2), −4(c^3 + ac + b)); the degree sequence drops from [2, 3, 4] to [2, 2, 4] iff rank{c_22, c_21} = 1, and the ideal of 2 × 2 minors is generated by c^6 + 5ac^4 + 20bc^3 − 5a^2c^2 − 4abc − 8b^2 − a^3 = ψ_4(c)/(4y), the 4-division polynomial: equality iff c is the x-coordinate of a point of exact order 4;
- a degree ≤ 1 element in W would need rank{c_22, c_21, c_12, c_20, c_02, c_11} ≤ 2; the ideal of the 3 × 3 minors together with 1 − t(4a^3 + 27b^2) is the unit ideal, so this never happens on a nonsingular curve;
- the top of the degree sequence is 4 for every degree-2 coordinate (the plane curve {(φ(P), φ(R − P))} is the pullback of a degree-4 linear system, so its affine equation has degree 4).

Hence **w ≥ 8 for every even degree-2 coordinate, with equality exactly for the order-4 pole pair (PROVED, computer algebra)**. The computed table confirms it at orders 2–16. For coordinates of degree k ≥ 3 the top degree alone is 2k·(number of lifts) ≥ 6 and the coefficient count is ≥ k + 1, giving w ≥ 8 as a dimension count (and ≥ 126 in every computed case); for non-even degree-2 coordinates with a 3-torsion pole sum the computed budget is 9, and with a generic pole sum 32. Lower bound in full generality: **conjectured** (w ≥ 8 over all coordinates), with the proof covering the even degree-2 case.

### Structure theorem for families (b) and (c)

- (Proved) Every relation F ∈ k[x_1, x_2] ⊗ k(E) vanishing on all decompositions P_1 + P_2 = R is H · S_3(x; x_R) with H ∈ k(E)[x_1, x_2]: the Semaev curve C_R ≅ E is geometrically irreducible, so the vanishing ideal in k(E)[x] is the prime ideal (S_3). In particular relations using y_R, x(2R), x(R + T), or any other function of R are multiples of S_3 by a coefficient in k(E)[x].
- (Proved) The budget is monotone under inclusion of coefficient spaces and invariant under change of the R-function basis; writing H = H_0 + y_R H_1 and clearing denominators, W(F) ⊇ W(H_0' S_3) with H_0' ∈ k[X][x] polynomial. So y_R and other target coordinates cannot lower the single-relation budget below the polynomial-multiplier value, which is SA-13's Conjecture W (≥ 9 in Weierstrass x, 38,000 multipliers tested there; 600 random and 25 structured multiplier sets here, minimum 9, and 8 in Edwards y).
- (Proved) Several known coordinates of R give several congruences on the same unknown vector only through W ∩ (S_R): r = dim_{k(X)}(W ⊗ k(X) ∩ (S_3)), and this dimension is unchanged by adjoining y_R (intersection of subspaces defined over k(X) commutes with base change). Multi-coordinate lattices are therefore the same objects as multi-multiplier lattices with effective budget w/r.

### Family (c): effective budgets at modulus p (`results/search_c*.json`, `results/sym_budget.json`)

| coefficient space W (Weierstrass x) | dim | w | r | w/r | predicted reach |
|---|---|---|---|---|---|
| span(A, B, C) = coefficients of S_3 | 3 | 9 | 1 | 9.0 | 0.111 |
| x-side span of {x^α X^j S_3}, \|α\| ≤ 1 | 9 | 33 | 3 | 11.0 | 0.091 |
| \|α\| ≤ 2 / ≤ 3 | 18 / 29 | 72 / 127 | 6 / 10 | 12.0 / 12.7 | |
| symmetric (Vieta) {e_1^i e_2^j : i + 2j ≤ d}, best d = 8 | 25 | 130 | 9 | 14.4 | 0.069 |
| symmetric boxes, best | 30 | 195 | 12 | 16.3 | |
| P_{≤d}, best d = 9, 10 | 55, 66 | 330, 440 | 21, 28 | 15.7 | 0.064 |
| boxes [0, 2 + h]^2, best h = 2 | 25 | 100 | 9 | 11.1 | 0.090 |
| exhaustive box + degree-5 monomials (1586 sets) | 12 | 30 | 2 | 15.0 | |
| 600 random sparse multiplier sets | | | | min 9.0 (r = 1) | |
| 12 hill climbs over monomial sets, degree ≤ 8 | | | | min 11.45 | |
| same families with the Edwards polynomial | | | | min 8.0 (r = 1); best r > 1: 10.0 | |

No coefficient space with r ≥ 2 has w/r below 9 (Weierstrass) or 8 (Edwards). The non-symmetric monomial spaces (P_{≤d}, boxes) are counting upper bounds only: their primal lattices contain unit vectors on coordinates no congruence touches and antisymmetric short vectors, and multiplier spans decompose into blocks whose best block is the r = 1 relation; the planted tests of these r > 1 lattices returned 0/20 at every δ (reported in `results/lattice_multi.log`, not used). The modulus-p dual version of these lattices is SA-17's (s, t) = (2, 1) box lattice, measured at 0.118–0.125 (56–101 bits) and extrapolated to 0.110: the same 1/9 wall. The Coppersmith ladder (modulus p^k, ceiling 1/6, SA-08/SA-17/SA-18) is a different relation-amplification mechanism, outside the prereg's candidate families; SA-17's (6, 3) cells at 76–101 bits measured δ_Z = 0.133–0.138 at dimension 49, which the reader should keep in mind when comparing with the SUCCESS line.

### Planted recovery, r = 1 form lattices (`results/lattice.jsonl`, `results/thresholds.json`, `fig_sa19.png` panel A)

| lattice | bits | threshold (50% crossing) [bootstrap 95% CI] | rate at δ = 0.120 / 0.125 / 0.130 / 0.135 |
|---|---|---|---|
| Edwards y, w = 8, theory 0.125 | 64 | 0.1246 [0.1229, 0.1280] | 31/40, 19/40, 13/40, 6/40 |
| | 96 | 0.1267 [0.1250, 0.1278] | 38/40, 26/40, 8/40, 4/40 |
| | 128 | 0.1245 [0.1234, 0.1262] | 38/40, 18/40, 6/40, 1/40 |
| Weierstrass x, w = 9, theory 0.111 | 64 | 0.1120 [0.1095, 0.1212] | 17/40, 10/40, 7/40, 1/40 |
| | 96 | 0.1135 [0.1119, 0.1160] | 10/40, 6/40, 2/40, 2/40 |
| | 128 | 0.1132 [0.1121, 0.1150] | 6/40, 0/40, 0/40, 0/40 |

The gap between the two lattices is 0.011–0.013 at every size, against the predicted 1/8 − 1/9 = 0.0139. End-to-end (`results/e2e_edwards.json`): at 96 bits and δ = 0.11, all 20 recovered vectors solve (sympy, exact) to the planted (y_1, y_2), lift to points, and satisfy P_1 + P_2 = R.

### m = 3 (`results/m3.json`)

| relation | coefficient degrees in (x_1, x_2, x_3) | degree sequence | w | reach |
|---|---|---|---|---|
| S_4, Weierstrass x | 12, 11, 10, 9, 8 | [8, 9, 10, 11, 12] | 50 | 0.0200 |
| S_4, twisted Edwards y | 12, 9, 10, 9, 8 | [7, 8, 9, 10, 12] | 46 | 0.0217 |

Total-degree multi-equation spaces against S_4 have w/r ≥ 459 (d ≤ 15) and are useless. The m = 3 SUCCESS line (0.025) needs w ≤ 40.

## Verdict reasoning

- SUCCESS requires a measured threshold above 0.131 with ≥ 10/20 recovery at 64 and 96 bits. The best candidate reaches 0.125–0.127 and 6/40 at δ = 0.135. Not met, and not reachable: the budget lower bound 8 (proved on the degree-2 even class, computed elsewhere) caps the predicted reach at 0.125.
- KILL requires every candidate to have budget ≥ 9 and no threshold above 0.121. Both fail: the Edwards-y relation has budget 8 and its threshold CIs lie entirely above 0.121.
- Hence INCONCLUSIVE by the frozen letter. What would decide it is not scale: the two frozen lines bracket 1/8, so no run at any size changes the outcome. A re-registration with the honest question ("is 8 the minimum budget over all coordinates, including degree ≥ 3 and non-even ones?") would be decided by extending the computer-algebra proof from the Möbius family to L(D) for deg D = 2 non-even (two cases computed: 9, 32) and deg D = 3 (three cases computed: ≥ 126).
- Interpretation: the only mechanism that lowers the budget is a torsion-translation symmetry of the coordinate (y(P + T_2) = −y(P)), which removes the odd-degree layer of the coefficient space; the 3-torsion (Hessian) and 2 × 2-torsion (Jacobi) symmetries do not help because their coordinates have degree ≥ 3, where the top of the degree sequence alone is ≥ 6 and the coefficient count grows. The gain 9 → 8 is the lattice-side shadow of the known Edwards speed-up of Semaev polynomials (Faugère–Gaudry–Huot–Renault): one factor of B in the per-relation cost, p^{1 − 1/9} → p^{1 − 1/8} in the SA-13 accounting, nowhere near the existence threshold 1/2.

## Limitations

- The lower bound 8 is proved only for even degree-2 coordinates (all Möbius functions of x); other classes are covered by representative computations, not proofs. Degree-4 E[2]-eigenfunctions (Jacobi intersection class) were not interpolated (killed after 15 minutes); the degree lemma shows their top term alone is ≥ 8.
- Budgets assume small curve constants (a = b = 1; Edwards a = 8, d = 4), as in SA-13/SA-17. For a curve with a large constant (P-256's b, Ed25519's d) the coefficient polynomials are no longer small and the correct unknown vector is the monomial vector: 12 for Weierstrass (monomials 1, e_1, e_2, (x_1 − x_2)^2, e_1 e_2, e_2^2), about 10 for Edwards; the Edwards advantage persists but the absolute numbers change.
- The r > 1 primal lattices were not made to work (block decomposition, unconstrained coordinates); the multi-equation conclusion rests on counting and on SA-17's dual lattices. The dual Coppersmith ladder at modulus p^k is excluded by scope, not refuted; its ceiling is 1/6 (SA-08/SA-18).
- Thresholds are toy scale (64–128 bits, 40 trials per δ, bootstrap CIs over binomial resampling of the 50% crossing); exponents were not fitted (none is a criterion).
- The m = 3 result is a budget computation only.
- Ranks are computed modulo a 31-bit prime at random specialisations (generic rank with high probability, checked twice); the Möbius proof is exact over Q.

## Suggested lead-atlas update

LEAD-ICP-function-field-mirror / the lattice lens on summation polynomials: move the mechanism statement from "budget 9 (m = 2), 50 (m = 3)" to "**budget 8 in twisted-Edwards y (poles at an order-4 pair), 9 in every other coordinate of degree 2, proved minimal among even degree-2 coordinates; 46 vs 50 at m = 3**"; record the structure theorem (every relation is H · S_3 with H ∈ k(E)[x], so y_R and other target coordinates add nothing, and multi-equation lattices at modulus p have effective budget w/r with minimum at r = 1). Disposition: lattice route **killed up to a constant** — the best single-relation reach is 1/8 (measured 0.125–0.127 at 64–128 bits against 0.112–0.114 for 1/9), still a factor 4 below the existence threshold 1/2; next_action: none on the lattice side unless a proposal applies the modulus-p^k ladder to the Edwards polynomial (expected ceiling ≤ 1/6, unchanged mechanism). Deciding numbers: w = 8 (degree sequence [2, 2, 4]), threshold 0.1267 [0.1250, 0.1278] at 96 bits, min w/r = 8 at r = 1.

## Files

`lib19.py` (budget, r(W), interpolation, curves), `coords.py`, `coords2.py`, `coords3.py` (family a), `moebius_proof.py` (Möbius-family proof), `search_c.py`, `sym_budget.py` (family c), `lattice19.py`, `analyze.py`, `e2e_edwards.py` (planted recovery), `m3.py`, `fig.py`, `t_lib.py` (library self-test), `run_all.sh`, `run2.sh`, `run3.sh`; results in `results/`; figure `fig_sa19.png`; `DEVIATIONS.md` (6 items).
