# SA-15: The m = 4 box problem as the canonical open primitive

## Summary

**INCONCLUSIVE against the frozen criterion** ("adoption: every later oracle result cites the instance set; no kill"). Adoption is a property of future runs, so it cannot be decided here. What exists now is the deliverable the criterion presupposes: a frozen, fully verified instance set (400 planted instances), a written three-way equivalence, and a matched-rho reference. There is no kill condition, so there is no KILL.

Deciding numbers:
- 400/400 planted instances verified in the group by two independent code paths plus PARI (R = sum of four signed small-x points, [N]R = O, all x_i in [1, B]). 100/100 also pass the true S_5 resultant chain at 2^40 (degree 8 in T, 120 permutation checks).
- `instances.json` SHA-256 `e9b681a6cd073f307ab434158bd18ab3c36d15c7f400ab7f0cb973c1f2958d62`; `witnesses.json` (answers) SHA-256 `5a4080178acc85cdcd4cfbe84b8ca830318ba86929f28d76cf73adfcd3fe2645`.
- The prereg prediction, as worded ("RR has exactly one more full-size unknown than Vieta has small ones"), is **not supported**: the count is 3 full-size alphas against 4 small e's. The corrected statement is in Section 3.3.
- The cost bridge gives break-even oracle cost T* about p^{1/10}/1.5 at B = p^{1/5} (T* = 6.8, 26, 84, 456 group operations at 2^40, 2^56, 2^72, 2^96), not p^{1/4}. The p^{1/4} figure is the limit as B goes to p^{1/4}.

## What was run

All scripts are in this directory and ran single-threaded in under a minute in total.

| file | role |
|---|---|
| `gen_instances.py` | builds both JSON files; asserts nine checks per instance at generation time |
| `verify.py` | reads only the JSON files; PARI group law, S_5 resultant chain, uniqueness census at 2^40 |
| `control_s5.py` | negative control: S_5 does not vanish at x_R + 1, +2, +3 |
| `reference.py` | matched-rho reference, break-even table, `fig_reference.png` |
| `gen_output.txt`, `verify_output.txt`, `control_s5_output.txt`, `verify_summary.json`, `rho_reference.json`, `reference_table.md` | raw outputs |

Instance construction. Curve y^2 = x^3 + 7. For k in {40, 56, 72, 96}, p is the first prime at or above 2^k with p = 1 mod 3 and prime group order N (N != p), found with PARI `ellcard`. B = floor(p^{1/5}). Each instance draws four distinct x_i uniformly in [1, B] with x^3 + 7 a square, random y signs, and sets R = P_1 + P_2 + P_3 + P_4. Instances with x_R equal to some x_i are discarded. The public file holds (p, N, a, b, B, R); the witness file holds the points, the Vieta vector e, and the Riemann-Roch alphas.

Checks per instance (generation asserts all; `verify.py` re-does the group part from the JSON alone):
1. R from affine addition left to right equals R from Jacobian addition in the order (P4+P2)+(P3+P1) equals PARI `elladd`.
2. R is on the curve and [N]R = O.
3. The S_3 relations hold along the chain: S_3(x_1,x_2,x(P_1+P_2)) = S_3(x(P_1+P_2),x_3,x(P_1+P_2+P_3)) = S_3(x(P_1+P_2+P_3),x_4,x_R) = 0 mod p.
4. Exactly one sign pattern eps with sum eps_i P_i = R (max 1 on all 400), and x_R is one of 8 distinct roots of the octic over the sign classes.
5. Riemann-Roch (Abel) check: f = xy + c_1 x^2 + c_2 y + c_3 x + c_4, fixed by vanishing at P_1..P_4, also vanishes at -R.
6. The quadratic map (c_1,c_2,c_3) to (e_1..e_4) of Section 3.2 reproduces the true elementary symmetric values.
7. Vieta box: e_1 <= 4B, e_2 <= 6B^2, e_3 <= 4B^3, e_4 <= B^4.
8. At 2^40: true S_5(x_1..x_4, T) = Res_X(S_3(x_1,x_2,X), Res_Y(S_3(X,x_3,Y), S_3(Y,x_4,T))) computed with PARI over F_p vanishes at x_R for 100/100 instances, has degree exactly 8 in T, and vanishes at x_R under all 24 orderings for the first 5 instances (120 checks). Control: no spurious root at x_R + 1, 2, 3 (0 of 300).
9. Uniqueness census at 2^40 (pair table over all 272 signed base points, every pair sum tested against R minus pair sum): exactly one x-quadruple (any signs) sums to R in 100/100 instances.

## Results

### 3.1 The frozen instance set

| log2 p | p | N (prime) | B | instances | verified in group |
|---|---|---|---|---|---|
| 40 | 1099511631331 | 1099513086253 | 256 | 100 | 100 |
| 56 | 72057594037929931 | 72057594484027153 | 2352 | 100 | 100 |
| 72 | 4722366482869645217743 | 4722366482754923571001 | 21618 | 100 | 100 |
| 96 | 79228162514264337593543951293 | 79228162514263776329423687389 | 602248 | 100 | 100 |

Instance ids are `p<k>-000` to `p<k>-099`. Citation form for later runs: "SA-15 instance set, instances.json sha256 e9b681a6...8d62".

### 3.2 Matched-rho reference and break-even oracle cost

Cost model (report Section 3.1): total = (m!/2^m) p T_dec / B^{m-1} + m B^2, m = 4, so 1.5 p T_dec / B^3 + 4 B^2. T* is the T_dec that makes this equal sqrt(pi N / 4). Units are group operations.

| log2 p | rho sqrt(pi N/4) | log2 rho | plain rho sqrt(pi N/2) | p^{1/4} | generic MITM T = B^2 | break-even T* | hit probability of a random R | Vieta box volume / p |
|---|---|---|---|---|---|---|---|---|
| 40 | 9.29e5 | 19.83 | 1.31e6 | 1.0e3 | 6.55e4 | 6.8 | 1.6e-4 | 1.1e14 |
| 56 | 2.38e8 | 27.83 | 3.36e8 | 1.6e4 | 5.53e6 | 26.0 | 1.8e-5 | 6.9e18 |
| 72 | 6.09e10 | 35.83 | 8.61e10 | 2.6e5 | 4.67e8 | 84.2 | 1.9e-6 | 4.5e23 |
| 96 | 2.50e14 | 47.83 | 3.53e14 | 1.7e7 | 3.63e11 | 455.8 | 6.9e-8 | 7.6e30 |

Figure: `fig_reference.png`. The generic MITM oracle (pair table, time and space B, then B^2 lookups) sits 3 to 4 orders of magnitude above T*, and it is what the 2^40 census above actually ran (it found the planted quadruple every time).

Three consequences:
- The hit probability of a random R is about B^4/(24 p) times 16, so about p^{-1/5}. A planted instance therefore almost surely has a unique solution (census: 100/100 unique at 2^40, expected number of extra solutions 1.6e-4 per instance). An oracle result on these instances measures "find the planted point", not "decide existence". The decision version needs a null set, which this release does not include (see Limitations).
- Exponent mismatch. T* scales as p^{1/10}/1.5, since the first term is 1.5 p^{2/5} T and rho is p^{1/2}. The prereg and report phrase the m = 4 target as "T_dec much less than p^{1/4} at B = p^{1/5}". That threshold belongs to B near p^{1/4}, where the box is no longer small (hit probability near 1). At the frozen B = p^{1/5}, an oracle with T_dec = p^{1/5} loses to rho. Oracle results scored on this set should compare to the T* column, and say so.
- The LEAD-EXO-ksum yaml says the 4-SUM oracle must run "in time much less than sqrt(|S_B|)". With n = |S_B| about B, sqrt(n) is p^{1/10}, and T* is p^{1/10}/1.5, so the yaml is consistent with the cost bridge and not with p^{1/4}. The p^{1/4} wording in the report is the outlier.

### 3.3 The three forms and their equivalences

Setting: E : y^2 = f(x) = x^3 + a x + b over F_p, group order N prime, R in E(F_p), B = floor(p^{1/5}). Status tags: **[P]** proved here or standard, **[S]** sketched, **[C]** conjectured or heuristic, **[N]** checked numerically on all 400 instances.

**BOX4(E, p, B, R).** Find distinct x_1..x_4 in [1, B] and points P_i = (x_i, y_i) in E(F_p) with sum eps_i P_i = R for some signs. (x-only knowledge identifies R up to sign, so the problem is the same for R and -R.)

**Form X (S_5, x-coordinates).** Find integers x_1..x_4 in [1, B] with f(x_i) a square mod p and S_5(x_1, x_2, x_3, x_4, x_R) = 0 mod p. S_5 is symmetric of degree 8 in each variable, S_5 = Res_X(S_3(x_1,x_2,X), S_4(X,x_3,x_4,x_5)).
- X <=> BOX4. [P] Semaev's theorem, given the square condition (without it a root can correspond to a relation on the twist or over F_{p^2}, so the square test is part of the form). [N] degree 8 and vanishing on 100/100 at 2^40, all-permutation invariance, and the control above.

**Form V (Vieta).** Let e_k be the elementary symmetric polynomials of x_1..x_4. Find integers e = (e_1..e_4) with 0 < e_1 <= 4B, 0 < e_2 <= 6B^2, 0 < e_3 <= 4B^3, 0 < e_4 <= B^4 such that
 (V1) F_R(e) = 0 mod p, where F_R(e_1..e_4) := S_5(x_1..x_4, x_R) written in e, and
 (V2) T^4 - e_1 T^3 + e_2 T^2 - e_3 T + e_4 has four distinct integer roots in [1, B] (and f at each is a square).
- V <=> X. [P] Fundamental theorem of symmetric polynomials (F_R exists with coefficients in Z[a,b,x_R]; it contains at most C(12,4) = 495 monomials, because degree 8 in each x_i bounds the total degree in the e's by 8). The box bounds follow from x_i <= B.
- The box and (V1) alone are a relaxation. [C] Heuristically (V1) has about 96 B^10 / p solutions in the box, since the box volume is 4B * 6B^2 * 4B^3 * B^4 = 96 B^10. At B = p^{1/5} that is about 96 p spurious solutions against one planted. The last column of the table above is this quantity, box volume divided by p (1.1e14 at 2^40 to 7.6e30 at 2^96); it grows like p, so the relaxation is hopelessly non-unique. The condition (V2) carries all the identifying information. This is the m = 4 analogue of the m = 2 statement in report Section 3.2 (a conic point with square discriminant).
- General m: box volume is B^{m(m+1)/2}, so the relaxation is unique only for delta < 2/(m(m+1)) = 1/3, 1/6, 1/10 for m = 2, 3, 4. [C] **Observed identity, not derived:** the report's certified reach 1/(m(m+1) 2^{m-2}) equals exactly this ceiling divided by 2^{m-1}, the degree of S_{m+1} in each variable (1/6, 1/24, 1/80 against 1/3, 1/6, 1/10). This suggests the reach is "box-relaxation ceiling over degree" and explains why presentation changes that keep the same box and degree cannot move it. It is a numerical coincidence until someone derives the Newton-polytope argument.

**Form RR (Riemann-Roch, Diem II over F_p).** L(5O) has basis 1, x, y, x^2, xy. The five points P_1, P_2, P_3, P_4, -R sum to O, so by Abel's theorem and Riemann-Roch there is f = xy + c_1 x^2 + c_2 y + c_3 x + c_4 vanishing exactly at them. Its norm is N(f)(X) = (c_1 X^2 + c_3 X + c_4)^2 - (X + c_2)^2 f(X) = -(X - x_R)(X^4 - e_1 X^3 + e_2 X^2 - e_3 X + e_4).
- Matching the X^4..X^1 coefficients, with (x_R, y_R^-) the coordinates of -R and c_4 = -(x_R y_R^- + c_1 x_R^2 + c_2 y_R^- + c_3 x_R) (affine-linear in the alphas), gives
 s_1 = c_1^2 - 2 c_2, s_2 = a + c_2^2 - 2 c_1 c_3, s_3 = c_3^2 + 2 c_1 c_4 - b - 2 a c_2, s_4 = 2 b c_2 + a c_2^2 - 2 c_3 c_4,
 e_1 = s_1 - x_R, e_2 = s_2 - x_R e_1, e_3 = s_3 - x_R e_2, e_4 = s_4 - x_R e_3.
 Every e_k is a quadratic polynomial in the three full-size alphas (c_1, c_2, c_3). The X^0 equation holds automatically because N(f)(x_R) = 0. [P] direct computation; [N] the formulas reproduce the true e on 400/400 instances, and f vanishing at -R is the Abel-Jacobi check on 400/400.
- RR <=> V. [P] The zeros of f are F_p-rational points (y = -(c_1 x^2 + c_3 x + c_4)/(x + c_2), so no square test is needed once the quartic splits), and they sum to R. So: find alpha in F_p^3 such that Q(alpha) = (e_1..e_4), lifted to [0, p), lies in the Vieta box and satisfies (V2). The alphas are the affine chart of the projective-space fibre of Sym^4 E over R (Riemann-Roch: this fibre is P^3). Only about one alpha in 24 gives a fully split quartic, which matches the count N^3/24 of unordered rational decompositions against p^3 alphas. [S] The map alpha to e is birational onto the hypersurface {F_R = 0}: exactly one of the 16 sign patterns sums to +R. [N] "exactly one sign pattern" holds on 400/400.
- Unknown count (corrects the prereg prediction). Vieta: 4 small unknowns, 1 equation (V1). RR: 3 full-size unknowns alpha, with the 4 small unknowns e defined by 4 quadratic equations; eliminating alpha is a resultant that leaves exactly (V1). So RR carries exactly m - 1 = 3 extra full-size unknowns matched by m - 1 = 3 extra equations, and the same m = 4 small unknowns. Net dimension is 3 in both. The prereg's "one more full-size unknown than the Vieta form has small ones" does not match this count (3 against 4); the true relation is "m - 1 extra unknowns, m - 1 extra equations". [C] That the lattice reaches of the two forms coincide because of this is the Idea 1 / Idea 4 question and is not decided here; the evidence in this run is only the matching dimension count and the matching box.

### 3.4 Fine-grained relatives

- **4-SUM on an implicit set** (LEAD-EXO-ksum-conjecture-s5-oracle). The set is S_B = {+-P : 1 <= x(P) <= B}, n = |S_B| about B, membership O(1). BOX4 is 4-SUM on S_B with target R in the group. [P] The generic pair-table (meet in the middle) solves it in time and space about B (build) plus B^2 (lookups); the 2^40 census ran exactly this and recovered the planted solution 100/100. [C] Under the 4-SUM conjecture, structureless instances need n^2 = B^2 = p^{2/5}, a factor p^{3/10} above T*. The caveat of the lead stands: no Shoup-style proof exists, so this is conditional.
- **Points in boxes** (Chang, Cilleruelo, Garaev, Hernandez, Shparlinski, Zumalacarregui 2014, arXiv:1111.1543). I did not re-read this paper in this run. From its title it bounds points of curves in small boxes; I make no claim that it applies to the 3-fold {F_R = 0} or to the (V2) condition. The statement to look for is an upper bound on the number of solutions of (V1) in the Vieta box, which would turn the [C] count above into a theorem.

### 3.5 Scoring rule for later oracle runs

For each of the 400 instances report: success (outputs x_i and signs that verify in the group), wall time and group-operation-equivalent count T_dec, and the ratio T_dec / T* from the table. Report the success rate with instance ids that failed. State B (it is fixed in the file). Claims of "faster than rho" require the ratio below 1 at all four sizes and a stated exponent over the four sizes with a confidence interval; the p^{1/4} threshold alone is not sufficient. Because planted instances are almost surely unique, an oracle should also be run on random unplanted R (hit probability about p^{-1/5}), which this release does not provide.

## Verdict reasoning

The frozen criterion is adoption by later runs. That cannot be observed at execution time, and the brief forbids reinterpretation, so the verdict is INCONCLUSIVE with the status "deliverable complete, adoption pending". Nothing here contradicts the criterion and nothing triggers a kill (there is none). The one prediction in the prereg that can be checked now, the unknown-count statement, fails as worded and holds in the corrected form of Section 3.3.

## Limitations

- Toy scale only; no oracle was run beyond the generic pair-table at 2^40. Reference numbers are formulas (sqrt(pi N/4) and the report's cost bridge), not measured rho runs.
- The S_5 resultant check is done at 2^40 only. Larger sizes use the S_3 chain and the octic-root checks, which are consistent with the same statement but are not a computation of S_5 itself.
- Uniqueness was counted exhaustively only at 2^40 (B = 256). At larger sizes it rests on the heuristic count 1.8e-5 and below.
- The heuristic count of spurious Vieta solutions and the reach identity are [C]. No planted-null set is included.
- The curve is the single family y^2 = x^3 + 7 with prime order; results say nothing about curves with other a, b or composite order. The set is not a security claim about any deployed curve.
- I did not re-verify the report's reach numbers 1/6, 1/24, 1/80; the identity in Section 3.3 takes them as given.

## Suggested lead-atlas update

LEAD-EXO-ksum-conjecture-s5-oracle: attach the frozen instance set (`SA-15/instances.json`, sha256 e9b681a6cd073f307ab434158bd18ab3c36d15c7f400ab7f0cb973c1f2958d62) as the common benchmark and keep disposition open_next_step. Add one correction to the next_action text: at B = p^{1/5} the break-even oracle cost against matched rho is about p^{1/10}/1.5 (T* = 6.8, 26, 84, 456 group operations at 2^40 to 2^96), not p^{1/4}; the generic MITM oracle costs B^2 = p^{2/5}, 3 to 4 orders above T* at these sizes. Also note that the Riemann-Roch and Vieta presentations differ by m - 1 unknowns and m - 1 equations (net zero) and share the same small-variable box, with the box-relaxation ceiling 2/(m(m+1)) times 1/2^{m-1} reproducing the recorded reach 1/80 at m = 4 (observed, not derived). The deciding numbers are 400/400 verified instances and the T* column.
