# SA-13b: closing the lattice-query lower bound (volume step, modulus p^2, structured enumeration)

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write.)

## Summary
**Verdict: INCONCLUSIVE** against the frozen criteria. SUCCESS needs a complete proof for modulus p and p^2, or a structured enumeration with exponent < 1 (CI excluding 1); neither was reached. KILL needs a counterexample to the volume inequality; there is none, the inequality is now proved.

| Step | Status | Number |
|---|---|---|
| 1. Volume inequality c(W) <= C (W0W1W2)^{2/9} | PROVED (section 2.1), C = (9/5)2^{2/3} = 2.86 plus additive M(1+ln M) for the finitely many small pairs | worst measured c/omega^{2/9} = 0.79 (curves (0,7), (2,5), (-3,11); c up to 10^6, W0 up to 3.6e12); plateau 0.679 for c >= 10^3 |
| 1'. Content gap (extraction from any vector parallel to G(x)) | PROVED (Nullstellensatz certificate, verified by exact expansion) | gcd(G0,G1,G2)(x) divides N0 = 3528 / 5656 / 8424 for (0,7) / (2,5) / (-3,11) |
| 1''. SA-13 Theorem 5, modulus p | PROVED now for per-target non-adaptive queries (class CE-na); SA-13's adaptivity corollary was over-claimed | cost Omega(p^{7/9}) per relation |
| 2a. Mod p^2 list length | PROVED (van der Corput, index p^2) | list >= 2 floor(omega/p^2); holds in 10/10 brute-force boxes |
| 2b. Mod p^2 sparsity/equidistribution | best proved bound is trivial D(V-1); equidistribution not proved and measurably false in elongated boxes | list/heuristic 0.96 to 1.5 (balanced), up to 8.3 (elongated); trivial bound loose by 10x to 2600x |
| 2c. Mod p^2 certificate classification and coverage | SKETCHED under no-wraparound hypothesis H-sep; one branch open | covered set <= C omega^{1/15} (numerical sup ratio 0.59), giving cost Omega(p^{13/15}) if the open branch closes; gains an exponent over 7/9 |
| 3. Structured enumeration (c2 = d^2) | measured | outer loop B+1 iterations exactly; nodes/(B+1) = 1.001 to 1.005 at B = 2^10..2^12 (p = 2^96); exponent 1.016, CI [1.011, 1.023]; 30/30 settings recover the planted decomposition |

What decides it: the p^2 proof fails at two named steps (section 3.3): classifying certificates for the ideal (S^2, pS, p^2) without the no-wraparound assumption, and coverage for the p-multiple branch with non-monomial multipliers q(T). A proof of either decides the p^2 half of SUCCESS. A sub-B^1 search over d would decide the other half; nothing here suggests one exists.

## 1. What was run
All single-threaded under `nice -n 10`, about 25 minutes wall clock in total.
* `exp1_nullstellensatz.py`: exact integer cofactors A_i with sum A_i G_i = N0, verified by expansion.
* `exp2_volume_sweep.py`: all pairs 1 <= x1 <= x2 with x1x2 <= E = 3e6 (22.6M pairs). For a log grid of (W0,W1), W2 = k-th smallest G2 among eligible pairs, every k scanned (tight boxes); top 20 tightened to actual maxima. Boxes with W0 < E^2/2.5 are exact. Output `exp2_out.txt`, `exp2_volume_rows_E*.json`.
* `exp3_p2_equidist.py`: brute force over all T in [0,p), p = 10007, modulus p^2, form (1,T,T^2), 10 boxes. `exp3_out.txt`, `exp3_rows.json`.
* `exp4_planted_levels.py`: 1,034,289 planted targets R = P1 +- P2 on y^2 = x^3 + 7 over F_10007. `exp4_out.txt`.
* `exp5_level2_volume.py`: coverage of the S_3^2 certificate (n = 5), region scan plus hill climbing on general 5-dimensional boxes. `exp5_out.txt`.
* `exp6_structured_enum.py`, `exp6_fit.py`: square-restricted enumeration, p of 40, 52, 64 and 96 bits, B = 2^2..2^13, 12 to 40 planted instances per cell. `exp6_out.txt`, `exp6_fit_out.txt`.
* `fig.py` -> `fig_sa13b.png` (volume ratio, mod p^2 equidistribution, enumeration cost).

## 2. Modulus p
### 2.1 Lemma 5 (volume inequality): full proof
Setting: y^2 = x^3 + ax + b, integers a, b, b != 0. For positive integers x1 <= x2: e1 = x1+x2, e2 = x1x2, and S_3 = G0 + G1 T + G2 T^2 with G2 = (x2-x1)^2, G1 = -2(e1(e2+a)+2b), G0 = (e2-a)^2 - 4b e1.

Claim: for all W0,W1,W2 >= 1, c(W) = #{1 <= x1 <= x2 : |G_k| <= W_k} <= (9/5)2^{2/3}(W0W1W2)^{2/9} + M(1+ln M), M = max(4|a|, 128|b|, 4).

Proof (every step proved):
1. Pairs with e2 < M number at most M(1+ln M) (sum over x1 <= sqrt(M) of M/x1); the main term is >= 1, so this is an additive constant.
2. For e2 >= M: e1 >= 2 and e1 <= e2+1 <= 2e2 (since (x1-1)(x2-1) >= 0). From e2 >= 4|a|, |e2-a| >= 3e2/4. Then |G0| >= (9/16)e2^2 - 4|b|e1 >= (9/16)e2^2 - 8|b|e2 >= e2^2/2 (uses e2 >= 128|b|). Also |G1| >= 2e1(3e2/4) - 4|b| >= e1e2 (uses 4|b| <= e2/32 <= e1e2/2). So a covered pair has x1x2 <= A0 := sqrt(2W0), x1x2^2 <= e1e2 <= W1 (as e1 >= x2), and x2 <= x1 + sqrt(W2).
3. For fixed x1 the integers x2 lie in [x1, min(A0/x1, sqrt(W1/x1), x1 + sqrt(W2))], so their number is at most min(A0/x1, sqrt(W1/x1), 2sqrt(W2)) (sqrt(W2)+1 <= 2sqrt(W2) since W2 >= 1). Nonzero only for x1 <= X1 := min((2W0)^{1/4}, W1^{1/3}).
4. min(u,v,w) <= u^{1/3}v^{2/9}w^{4/9} gives 2^{4/9}(2W0)^{1/6}W1^{1/9}W2^{2/9}x1^{-4/9}.
5. Sum of x1^{-4/9} over 1 <= x1 <= X1 is <= (9/5)X1^{5/9}, and min(s,t) <= s^{2/5}t^{3/5} gives X1^{5/9} <= (2W0)^{1/18}W1^{1/9}.
6. Exponents: W0: 1/6+1/18 = 2/9; W1: 1/9+1/9 = 2/9; W2: 2/9. Constants multiply to (9/5)2^{4/9+1/6+1/18} = (9/5)2^{2/3}. QED. The diagonal x1 = x2 is included (interval starts at x1).

Numerical check (`exp2_out.txt`, 22.6M pairs, boxes with c up to about 10^6):

| curve (a,b) | worst c/omega^{2/9} (tightened) | at c, W | worst c^{9/2}/omega |
|---|---|---|---|
| (0,7) | 0.774 | 21, (175,448,36) | 0.316 |
| (2,5) | 0.790 | 25, (161,548,64) | 0.346 |
| (-3,11) | 0.763 | 30, (344,538,81) | 0.296 |

The worst ratio by decade of c is 0.66 to 0.77, plateau 0.679 for c >= 10^3. SA-13's random-box maximum of 0.041 for c^{9/2}/omega was about 8x below the tight-box worst case (0.35); both are far below the proved bound.

### 2.2 The class for which Theorem 5 is now complete
**Content lemma (proved).** sum_i A_i G_i = N0 holds in Z[x1,x2] with deg A_i = 3 (exact expansion, `exp1_nullstellensatz.json`). Hence gcd(G0,G1,G2)(x) divides N0 for every integer pair. If a box contains any nonzero integer vector parallel to G(x), then G(x) lies in the N0-scaled box, so the covered set is at most c(N0 W) <= N0^{2/3} C omega^{2/9}. This closes the part of SA-13 gap G3 about vectors proportional to the planted direction, at the cost of a constant (N0^{2/3} = 232 for y^2 = x^3 + 7).

**Class CE-na:** m = 2, query degree D <= 2, monomial form (1,T,T^2) (so n = 3 forced), certificate scheme with identity over Z (H-int), each target R_i gets queries fixed independently of R_i (they may depend on transcripts of earlier independent targets).

**Theorem 5 for CE-na (proved).** With C' = N0^{2/3}C: Pr[some target has a certificate in its answer] <= 4C'p^{2/9}(sum of deterministic cost lower bounds)/N.
Proof: comparing T-degrees gives rank n = 3 and phi = lambda(X)G(X) with lambda in Z[X] (no Gauss lemma needed, since deg_T of both sides is <= 2). Per query, the target must lie in {+-P1 +- P2} (at most 4 points) for a covered x, so success probability is <= 4c(N0W)/N. Cost is >= max(1, 2 floor(omega/p)) by van der Corput; the ratio is maximal at omega = p, giving C'p^{2/9}. The lower bounds are deterministic given query sets independent of R_i, so summing over targets is a martingale-style union bound. QED.

**Correction to SA-13.** Its "adaptivity corollary" covers only the all-empty transcript. A non-empty answer already reveals x(R) up to 2 candidates (the vector's quadratic), after which the algorithm can do anything free on that target (SA-13 section 1.1). Leak probability per query (about 2DV/N) far exceeds success probability (about omega^{2/9}/N). So Theorem 5 must be read for algorithms that do not re-query a target adaptively on its own answers. Re-querying after a leak is a limit of the model, not a proof gap.

## 3. Modulus p^2
Model CE2: T = x(R) is the integer representative in [0,p); a query is a box W with all W_j < p^2/2; the answer lists nonzero v in the box with sum_j v_j T^j = 0 mod p^2.

### 3.1 List length (proved), sparsity (trivial only)
* Proved: the kernel lattice has index exactly p^2 (coefficient 1 at T^0), so van der Corput gives |V_f(R)| >= 2 floor(omega/p^2) for every R. Brute force at p = 10007 (`exp3_out.txt`): (W1,W2) = (30,20) boxes have minimum list 4, 16, 60 at omega/p^2 = 0.125, 0.5, 2 against bounds 0, 0, 2; (300,200) boxes have minimum 0, 0, 4 against 0, 0, 2; holds in all 10 boxes.
* Proved (trivial): a nonzero v with |v_j| < p/2 gives f_v nonzero mod p, so <= D roots in [0,p), hence sum_T cnt(T) <= D(V-1). The Gaussian-heuristic value is (V-1)/p, so the bound is p times too large; measured sum/(D(V-1)) was 3.8e-4 to 1.0e-1.
* Equidistribution fails by structure: (a) if W0 + W1T + W2T^2 < p^2, every box vector satisfies the congruence over Z, so the list is the exact integer relation lattice; this segment T < T* is 22% of all T in the (30,20) boxes and 7% in the (300,200) boxes. (b) Beyond T*, mean list / Gaussian heuristic:

| omega/p^2 | (W1,W2) = (300,200) | (30,20) |
|---|---|---|
| 0.001 | 1.50 | 2.69 |
| 0.012 | 1.44 | 0.96 |
| 0.125 | 1.15 | 7.73 |
| 0.5 | 1.02 | 8.28 |
| 2 | 1.02 | 4.49 |

Balanced boxes are within about 1.5 of the heuristic; boxes with W0 much larger than W1, W2 are up to 8.3 times higher (T near sqrt(k p^2) makes T^2 mod p^2 small). Non-empty fractions are also far from Poisson: at omega/p^2 = 0.125 (balanced) 38% of T have a non-empty list against a Poisson 63%. Short quadratic Weyl sums of length p against modulus p^2 have no non-trivial bound by completion (length = sqrt of modulus), so the trivial D(V-1) is the best I can prove.

### 3.2 Planted forms (`exp4_out.txt`, 1,034,289 targets, p = 10007)
G(x) is in the mod-p lattice 1,034,289/1,034,289 times; in the mod-p^2 lattice 86 times (rate 8.3e-5 vs 1/p = 1.0e-4, about 1.7 sd low); the S_3^2 coefficient vector s2(x) is in the mod-p^2 lattice every time. So the level-1 certificate does not survive at level 2; the level-2 certificate is the S_3^2 vector (n = 5, T-degree 4).

### 3.3 Certificate classification and coverage at level 2: sketched
Hypothesis H-sep: psi(X,p) in Z[p,X]^5 with sum_j psi_j T^j in (S^2, pS, p^2) in Z[p,X,T] (p an indeterminate), evaluated at integer x with all digit vectors psi_k(x) having entries < p/4 (no wraparound: B^deg < p/4).
1. Expand psi = psi_0 + p psi_1 + ...; psi_0 = a(X)s2(X) (s2 = coefficient vector of S_3^2); the p^1 part is the coefficient vector of q(T)S with q in Z[T], deg q <= 2.
2. Digit uniqueness: if k* is the lowest index with psi_{k*}(x) != 0 then |v_j| >= p^{k*}|psi_{k*,j}(x)|; as W_j < p^2/2, k* is 0 or 1.
3. Branch k* = 0: x in Phi2 = {x : |s2_j(x)| <= W_j all j}. Branch k* = 1: a nonzero q(T)s(T) in the box W/p.

Coverage:
* Branch k* = 0: numerical sup of c2/omega^{1/15} is 0.59 (hill climbing, 12 starts, c up to 1600; 0.57 over regions; max log c/log omega 0.0638 for c >= 2000). Heuristic exponent 2/(8+7+6+5+4) = 1/15. The level-1 inequality applied to U = (sqrt W0, sqrt W2, sqrt W4) gives only c2 <= C(W0W2W4)^{1/9}; exact 1/15 needs the W1, W3 constraints and is numerical, not proved.
* Branch k* = 1, monomial q = T^i: coverage <= c(W_i..W_{i+2}/p) <= C(omega/p^3)^{2/9}, empty for omega < p^3, so cost >= omega/p^2 >= p. Proved for monomial q.
* Branch k* = 1, general q: OPEN. Middle coordinates of qs can vanish; a Mahler-measure argument gives only the maximum weight, which drops the cost bound to p^{1/3}. This blocks a complete proof.

If the open branch closes with exponent >= 1/15, the section 2.2 ratio argument gives cost Omega(p^{13/15}) per relation, against p^{7/9} at level 1. So "loses at most a constant in the exponent" is met in the strong sense for the primal model: the p^2 lattice is a strict sublattice of the p lattice, offering fewer certificates. The Coppersmith ladder gain lives in the dual model, outside CE (SA-13 gap G5).

## 4. Structured enumeration (`exp6_*`)
Task: find all (c0,c1,c2) in the weighted box W = (B^4+.., 4B^3+.., B^2) of L_R with c2 = d^2. Algorithm: Fincke-Pohst with c2 outermost restricted to squares d^2 <= W2; inner level = exact enumeration in the 2-dimensional kernel lattice L2 = {c0 + c1T = 0 mod p} (weighted Gauss reduction, exact integers). Cost = outer iterations + inner points. Planted 2-decompositions on y^2 = x^3 + 7, p ~ 2^40, 2^52, 2^64, 2^96, random x1,x2 <= B. All 30 (bits, B) settings recovered the planted G(x) in every trial.
* The outer loop has exactly B+1 iterations (every d <= B must be tested); the inner enumeration adds about 16B^7/p points per d.
* p = 2^96, B = 2^7..2^12: median nodes/(B+1) = 1.023, 1.014, 1.004, 1.003, 1.001, 1.005. At B = 2^13 the inner term 16B^7/p = 0.5 appears (ratio 1.50).
* p = 2^64: same up to B = 2^8; at B = 2^9 the inner term 16B^7/p = 8 dominates (4626 nodes vs 514), exponent rises above 1 beyond p^{1/9}, as expected.
* Log-log fit of median nodes, p = 2^96, k = 5..13 (8 doublings): slope 1.016, 95% CI [1.011, 1.023] (bootstrap over trials). Sub-1 slopes in some windows (0.97 for k = 5..12) are an artifact of the additive constant in B+2 and of degenerate trials; the ratio test is the clean statement.
* No sub-linear exponent: the criterion fails, the prediction (cost >= B^1) is confirmed at this scale.

Interpretation: per relation (a target decomposes with x <= B with probability about B^2/(2N)) cost is about N/B while the inner term is O(1), and about NB^6/p beyond B = p^{1/7}; the minimum is p^{6/7} at B = p^{1/7}, above the p^{7/9} bound, so no contradiction. A sub-linear enumeration would need d <= B with d^2T^2 mod p close to L2 in o(B) time, a one-dimensional quadratic Diophantine-approximation problem for generic T with no known algorithm. The 2-sum collision (store P(x), x <= B, look up R - P(x)) has the same B^1 cost, so square-restricted lattice enumeration is no better than meet-in-the-middle.

## 5. Verdict reasoning
* Prediction 1 (volume inequality holds): met and now proved.
* Prediction 2 (mod p^2 loses at most a constant in the exponent): met in the conditional sense (3.3); unconditional version not proved.
* Prediction 3 (structured enumeration costs at least B^1): met, measured to p = 2^96 over 8 doublings.
* SUCCESS fails (p^2 proof incomplete, no sub-B^1 enumeration). KILL fails (no counterexample).
* What would decide it: a proof classifying the module {psi : sum psi_j T^j in (S^2, pS, p^2)} without H-sep, or coverage for general q(T), plus the exact volume inequality c2 <= C omega^{1/15}. Scale is not the obstacle.

## 6. Limitations
* The mod p^2 section depends on H-sep and has one open branch; the cost Omega(p^{13/15}) claim is conditional on both and on the numerical s2 volume inequality.
* Theorem 5 holds for per-target non-adaptive queries only.
* The model is still SA-13's box-oracle model (all-list oracle charged by list length, polynomial extraction, monomial form, m = 2, D <= 2, n = 3 at level 1). Non-monomial forms, D > 2, m >= 3 and the dual form are not covered.
* Section 4 reads "40-64 bits" as the bit size of p (extended to 96 for more doublings); 40- and 52-bit series have only 2 and 3 usable doublings and are not used for the claim. Mean node counts are distorted by a few degenerate trials; medians are used.
* The volume scan covers W0 up to 3.6e12; larger boxes rely on the proof.
* Toy scale on a shared host; no security statement about any deployed curve.

## 7. Suggested lead-atlas update
Lead LEAD-EXO-lattice-query-lower-bound: move disposition from `partial_theorem_restricted_model` to `partial_theorem_restricted_model_volume_step_closed`. Record as proved: the volume inequality c(W) <= 2.86 (W0W1W2)^{2/9} + M(1+ln M) (worst measured ratio 0.79), and the content lemma (gcd of the T-coefficients of S_3 divides N0 = 3528 for y^2 = x^3 + 7). Record the per-target non-adaptive restriction as a correction to the SA-13 adaptivity corollary. Set next_action to "classify the certificate module for (S^2, pS, p^2) without the no-wraparound hypothesis and prove coverage for general q(T); expect cost Omega(p^{13/15}) at level 2 in the primal model, so seek the Coppersmith ladder gain in the dual model". Record structured enumeration of c2 = d^2 as closed at exponent 1 in B (nodes/(B+1) = 1.001 to 1.005 for B = 2^10..2^12 at p = 2^96), no better than 2-sum meet-in-the-middle. Deciding numbers: worst volume ratio 0.79, N0 = 3528, mod p^2 list ratio up to 8.3 in elongated boxes, enumeration exponent 1.016 (CI [1.011, 1.023]).
