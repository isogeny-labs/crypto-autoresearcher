# SA-13: A lower bound in the lattice-query model

## Summary

**Verdict: INCONCLUSIVE** against the frozen criterion ("a theorem reviewed by two models and one human, or a counterexample that is a working oracle").
No counterexample was found or attempted to be built. The full conjecture (T >= p^{1/2-o(1)} for every m in the lattice-query model) is **not proved**.
What is proved is a precise, restricted theorem plus an exact accounting of what is missing. Deciding numbers:

* The literal model of the report ("generic algorithm that may submit any lattice and receives a reduced basis") is **vacuous**: it contains the x-coordinate oracle (proved, 1.2), and with coordinates visible a lower bound would imply P != NP (proved, 1.1). So the conjecture needs a different model, and the output rule of the oracle is where all the content sits.
* In a defined "box-oracle" model (section 2) I proved: per-query sparsity (Theorem 1), a rigorous list-length lower bound (Theorem 2), and, for arity m = 2 with query degree D <= 2, an exact classification of certificate schemes (Theorem 3/4) giving **certificate weight w = 9, hence reach delta* = 1/9 and a cost bound Omega(p^{7/9}) per relation** (Theorem 5; one step, the volume inequality, is sketched with a proof outline that is complete up to constants and a numerical check, max c^{9/2}/omega = 0.041).
* The bound 1/9 is for the bottom rung (one congruence, modulus p). It does **not** match Jochemsz-May (1/6 for S_3): the Coppersmith ladder lives at k >= 2 / several congruences, where my sparsity bound loses a factor p^{r-1}. So prediction 2 (matching J-M asymptotically) is not met, and prediction 1 (polylog dimension) is not met either (my constants carry 3^n, so n must be O(log p / log log p) at best; the theorem proved has n = 3).
* Numerical sanity checks: exact brute force of Theorems 1 and 2 on p = 100003 (all pass); LLL on the 3-dim lattice with weights (B^4,B^3,B^2): recovery crosses 50% at delta = 0.106 / 0.104 / 0.112 for 72 / 96 / 128-bit primes (theory 1/9 = 0.111) versus 0.093 / 0.088 / 0.092 unweighted (the repository's 1/12 = 0.083 prediction). Weighting is a free improvement of the Section 3.2 / 6.3 "1/12" number to 1/9 for the same lattice.
* No multiplier H(X,T) among about 38,000 tested produces a certificate of weight below 9 (section 3.4).

## 1. Why the literal model cannot be what is meant

**1.1 (proved).** If the algorithm sees coordinates of the points it holds, it can run LLL itself; the "oracle" is a polynomial-time subroutine and the model is the RAM model. Decomposition (find x_i <= B with sum P_i = R) is a search problem in FNP, so an unconditional super-polynomial lower bound in this model would give P != NP. No capacity-theory argument can be expected to reach that.

**1.2 (proved).** If coordinates are hidden but the oracle returns a reduced basis, it leaks them. Take n = 2, g = (1, T): the lattice {(c0,c1): c0 + c1 x(P) = 0 mod p} contains (-x,1), so some basis vector has c1 a unit mod p and x(P) = -c0/c1 mod p. So "GGM + reduced-basis oracle" contains "GGM + full x-coordinate oracle", and from there 1.1 applies.

Consequence: the report's sentence "lattice reduction is not a test and not simulable by a few tests" is correct, and the right fix is not a stronger simulation but an **output restriction plus a cost rule** for the oracle. Everything below is conditional on that choice, which is the modelling content of the problem.

## 2. The model that I could work with (box-oracle model CE)

Public data: E: y^2 = x^3 + ax + b over F_p with N = #E(F_p) prime (so N ~ p), generator G, Semaev polynomials S_{m+1}(X_1..X_m, T) (T = x_R). Targets R_1, R_2, ... are uniform in <G> (marginally; this is what randomising R = aG + bQ gives). Only the lattice oracle touches x(R_i).

* **Query** f = (g_1..g_n; W_1..W_n): integer polynomials g_j in T of degree <= D, linearly independent mod p; weights 1 <= W_j < p/2.
* **Answer** on target R: the list V_f(R) = { v in Z^n \ {0} : |v_j| <= W_j, sum_j v_j g_j(x(R)) = 0 mod p } (all box vectors of the kernel lattice).
* **Cost** of a query: 1 + |V_f(R)| (the oracle is charged for the list it hands over). This is an idealisation: it is **stronger than LLL in information** (all box vectors, not just a reduced basis) and **weaker in accounting** (LLL is cheap even when the list is long).
* **Certificate scheme** for arity m (hypothesis H-int): phi in Z[X_1..X_m]^n with sum_j phi_j(X) g_j(T) = H(X,T) S_{m+1}(X,T) in Z[X,T], H != 0. For a decomposition x (x_i positive integers) with phi(x) in the box, v = phi(x) is in V_f(R) for every R = sum +-P(x_i) (because S_{m+1}(x, x(R)) = 0 mod p). The *covered set* is Phi_f = { x : phi(x) in box, nonzero }.
* **Success** of a trial: the answer contains phi(x) for a decomposition x of that target (extraction = inverting phi, assumed free).
* Everything else is generic: nothing else about coordinates is revealed (so a trial with all answers empty carries no information about x(R_i)).

This captures "LLL on the kernel lattice of coordinates of the target, then read off a planted short vector". It is the *primal / planted-vector* form of Coppersmith. It does **not** capture: dual (polynomial-side) usage of longer reduced vectors, multi-target lattices, lattices using coordinates of other held points, filtered/structured enumeration of the list, or non-polynomial extraction (section 4).

## 3. Results (every step marked)

### 3.1 Theorem 1 (sparsity). PROVED, verified exactly.
For any query f: Pr_R[ V_f(R) != empty ] <= 2D (V - 1) / N, with V = prod_j (2W_j + 1).
*Proof.* A nonzero v with |v_j| < p/2 is nonzero mod p, so v.g(T) is a nonzero polynomial in F_p[T] (the g_j are independent), of degree <= D, hence has <= D roots in F_p. Each root is x(R) for <= 2 points R. Sum over the V - 1 nonzero v. QED.
Corollary (adaptivity): along the all-empty transcript the queries are a fixed sequence, so q queries return anything non-empty with probability <= (2D/N) sum_i (V_i - 1) (union bound, only marginal uniformity of each R_i used).

### 3.2 Theorem 2 (list length). PROVED, from van der Corput (1935).
Every kernel lattice L(x(R)) has index <= p in Z^n; the box K = prod [-W_j, W_j] is convex and symmetric with volume 2^n prod W_j. Van der Corput: |L cap K| >= 2 floor(vol K / (2^n det L)) + 1. Hence **|V_f(R)| >= 2 floor(omega / p) for every R, omega = prod W_j.** There is no 2^n loss in this direction.
Corollary: a query with omega >= p costs at least omega/p, a query with omega < p is non-empty only on a <= 3^n 2D omega/N fraction of targets.

### 3.3 Theorem 3 (rank, m = 2). PROVED.
Any certificate scheme for S_3 has n >= 3.
*Proof.* n = 1 contradicts irreducibility of S_3 (checked: S_3 is irreducible over Q for symbolic and three numeric (a,b), gcd of the T-coefficients is 1; `exp6_primitive_out.txt`). For n = 2: on the surface S_3 = 0, phi_1(X) g_1(tau) + phi_2(X) g_2(tau) = 0 at both roots tau_{1,2} = x(P_1 +- P_2). So the non-constant rational function r = g_1/g_2 of T satisfies r(x(P_1+P_2)) = r(x(P_1-P_2)) for all P_1, P_2 on E (over the algebraic closure). Put P_2 = P_1: r(x(2P_1)) = r(x(O)) is constant, so r is constant, contradiction. QED.

### 3.4 Theorem 4 (certificate module, m = 2, D <= 2, monomial g = (1,T,T^2)). PROVED.
n = 3, and every certificate scheme is phi = lambda(X) * G(X) with lambda in Z[X] nonzero and G = (G_0,G_1,G_2) the T-coefficients of S_3 (degrees 4, 3, 2; Gauss's lemma, because S_3 is primitive and has T-degree exactly 2 with leading coefficient (x_1 - x_2)^2). Since |lambda(x)| >= 1 on integers where lambda(x) != 0, the box must contain a vector of weighted size at least that of G(x). In the basis-invariant form (degree sequence of the span of the components, `exp2_weights.py`): **w = 2 + 3 + 4 = 9 for every tested curve** (a,b) = (0,7), (2,5), (-3,11).
Evidence beyond the proved range (D > 2, n > 3, not proved):
* all 35 monomial supports {a<b<c} in [0,6] (rank-3 certificates by the cross-product formula): minimum w = 9, attained only by consecutive supports (5 of 35); the next value is 17 (`exp4A_rows.json`);
* exhaustive search over multipliers Q(X,T) with coefficients in {-1,0,1} for (T-degree 1, X-degree 1) [728 cases] and (2,1) [19,682 cases], plus 6000 random draws each for (1,2), (3,1), (2,2). **Minimum w* found: 9 in both exhaustive families; 14, 12, 15 in the three random families; never below 9** (w* = degree-sequence sum of the X-side span of Q*S_3) (`exp4B_rows.json`).
This supports, but does not prove, **Conjecture W: w*(F) >= 9 for every nonzero F in (S_3)**.

### 3.5 Lemma 5 (volume inequality). SKETCHED (complete up to constants), numerically supported.
For the box with weights W and a = 0 (similarly general a,b): the covered set satisfies c(W) = |Phi_W| <= C (W_0 W_1 W_2)^{2/9}.
*Outline.* With x_1 < x_2: x_1 <= X_1 := min(W_0^{1/4}, (W_1/2)^{1/3}), and for given x_1 the number of admissible x_2 is <= min( sqrt(W_2), sqrt(W_0)/x_1, sqrt(W_1/x_1) ) (from G_2, G_0 ~ (x_1x_2)^2, G_1 ~ 2 x_1x_2(x_1+x_2)). Bound the minimum by the weighted geometric mean with exponents (4/9, 1/3, 2/9) on (sqrt(W_2), sqrt(W_0)/x_1, sqrt(W_1/x_1)): this gives sqrt(W_2)^{4/9} sqrt(W_0)^{1/3} sqrt(W_1)^{2/9} x_1^{-4/9}. Sum over x_1 <= X_1: sum x_1^{-4/9} <= (9/5) X_1^{5/9}, and X_1^{5/9} <= W_0^{1/18} W_1^{1/9} (take X_1 <= W_0^{1/4} to the power 2/5 and W_1^{1/3} to the power 3/5). Total exponents: W_0: 1/6 + 1/18 = 2/9; W_1: 1/9 + 1/9 = 2/9; W_2: 2/9. So c <= (9/5)(W_0W_1W_2)^{2/9}. The finitely many small pairs where the leading terms of G_0, G_1 do not dominate (an O_{a,b}(1) set) are not written out.
Numerical check (`exp5_volume_ineq.py`): max over 212 random weight triples of c^{9/2}/omega = **0.041**; balanced weights (B^4,B^3,B^2) give 0.009 to 0.020 for B = 10..160 and rising slowly to a limit. Never above 0.05. (The exponent bookkeeping in the outline was done by hand and re-checked by hand; the numerical check is the independent evidence.)

### 3.6 Theorem 5 (main). PROVED modulo Lemma 5 and hypothesis H-int.
Model CE, m = 2, query degree D <= 2, monomial g, (H-int). For any algorithm with total oracle cost Theta,
Pr[ some trial finds a decomposition certificate ] <= 4 C Theta p^{2/9} / N.
*Proof.* Per query i, success requires R in the set of <= 4 |Phi_{W_i}| points sum +-P(x_i) over covered x, so Pr <= 4 C omega_i^{2/9}/N (Lemma 5); its cost is >= max(1, omega_i/p) (Theorem 2). The ratio is maximised at omega = p, giving 4C p^{2/9}/N per unit cost; union bound over trials (Theorem 1's corollary justifies adaptivity). QED.
Reading: a constant-probability relation costs Omega(p^{7/9}) in this class, **worse than the generic sqrt(p)**; the largest factor base the class can serve cheaply is B = p^{1/9}; with the standard index-calculus accounting (B relations, cost N/B^m each) the total is p^{1-(m-1)/w} = p^{8/9}.

### 3.7 The same computation for m = 3 and m = 4 (certificate weight only).
Exact degree sequences (`exp2_weights.py`, three curves identical): **m = 3: S_4 has T-degree 4, coefficient degrees 12, 11, 10, 9, 8, w = 50, bottom-rung reach 1/50 = 0.020** (Coppersmith convex-shift ceiling quoted in the report: 1/24). m = 4: not computed (S_5 resultant did not finish; DEVIATIONS 2). **Conjecture (extrapolation):** deg G_k = m 2^{m-1} - k exactly, so w_S(m) = D(D+1)(2m-1)/2 with D = 2^{m-1}: 9, 50, 252 for m = 2, 3, 4. The Theorem 5 analogue for m >= 3 needs Theorem 4's argument (immediate: F = lambda S when D = D_S) plus a volume inequality c(W) <= C omega^{m/w} that I did not check.

### 3.8 Numerical sanity checks (computable consequences)
(a) `exp1_lemma_bruteforce.py`, p = 100003, n = 3, D = 2, all T in F_p enumerated exactly. Theorems 1 and 2 hold in all 7 weight settings:

| W | V/p | Pr[nonempty] measured | Thm 1 bound | mean list | min list | vdC lower bound |
|---|---|---|---|---|---|---|
| (6,4,3) | 0.0082 | 0.0024 | 0.016 | 0.0087 | 0 | 0 |
| (12,8,5) | 0.047 | 0.0148 | 0.093 | 0.048 | 0 | 0 |
| (24,12,8) | 0.21 | 0.075 | 0.42 | 0.22 | 0 | 0 |
| (40,20,12) | 0.83 | 0.29 | 1 | 0.85 | 0 | 0 |
| (80,40,20) | 5.3 | 0.99 | 1 | 5.5 | 0 | 0 |
| (100,60,40) | 19.7 | 1.0 | 1 | 20.3 | 6 | 4 |
| (200,100,60) | 97.5 | 1.0 | 1 | 99.5 | 40 | 22 |

The mean list length tracks V/p (the Gaussian-heuristic count) to within 7%, and Theorem 1 is loose by a factor of about 3 to 7 at small V (v and -v share roots, and the average root count of a random quadratic is 1, not D = 2). Rows with omega < p have min list 0 as they must.
Slack for r = 2 congruences (n = 4, p = 20011): measured sum of common roots / (D * #vectors) = 0.0094 and 0.0042, against the p^{-1} behaviour a sharp bound would need; Theorem 1 does not see the second congruence. This is the quantitative form of gap G1 below.
(b) `exp3_weighted_lll.py`, 40 planted 2-decompositions per cell, y^2 = x^3 + 7, 3-dim lattice, columns scaled by (1, B, B^2) (the Coppersmith scaling X -> BX):

| p bits | unweighted crossing of 50% | weighted crossing of 50% | theory |
|---|---|---|---|
| 72 | 0.093 | 0.106 | 1/12 = 0.083 / 1/9 = 0.111 |
| 96 | 0.088 | 0.104 | same |
| 128 | 0.092 | 0.112 | same |

Weighted recovery at 128 bits: 29/40 at delta = 0.10, 26/40 at 0.11, 9/40 at 0.115, 0/40 at 0.13. The unweighted crossings sit 0.005 to 0.010 above 1/12, the weighted ones between 0.007 below and 0.001 above 1/9, and the shift between them (0.013, 0.016, 0.020) is smaller than the 0.028 the exponents predict; the exponent is asymptotic and the boxes are not full (typical x ~ B/2), so I read the data as consistent with 1/9 but not as a precise confirmation. Figure: `fig_sa13.png`.

## 4. The exact gap to the full conjecture
In order of how much each would buy.

* **G1 (Coppersmith ladder: several congruences / modulus p^k). Not proved.** Theorem 1 bounds the non-empty probability by D V / p for any number r of congruences, but a sharp (and the Jochemsz-May) count needs V / p^r (resp. p^k). The missing input is equidistribution of the polynomial curve T -> g(T) mod p^k for T < p (a short-segment exponential-sum problem; for k = 1, r = 1 root counting suffices, which is why Theorem 1 works). Without it nothing above delta = 1/9 (m = 2) can be excluded, and the known reach 1/6 shows the true answer for the full class differs from the bottom-rung value.
* **G2 (general multiplier / non-monomial g / D > 2).** Proved only for D <= 2 monomial g. Evidence for Conjecture W above is computational (about 38,000 multipliers). A proof needs a lower bound on the degree sequence of the X-side span of H*S_3 for arbitrary H; I see a filtration argument (top X-degree part of H*S_3 is in(H)*(x_1 x_2)^2) but did not close it.
* **G3 (identity over Z).** (H-int) assumes the certificate identity holds over Z. A scheme that uses p essentially (identity only mod p, vectors reduced mod p) is excluded. Extending needs: (i) a Schwartz-Zippel-on-the-variety step turning "phi(x) in L(x(R)) for a positive fraction of box decompositions" into "F lies in (S, p)" (sketched, constants not done), and (ii) handling sparse subfamilies of decompositions (algebraic subvarieties), which reduce to arity m-1 enumeration at a factor-B cost.
* **G4 (extraction beyond listing).** The cost rule charges for the whole list. An algorithm that searches inside the kernel lattice for vectors lying on the surface Im(phi) (for m = 2: c_2 a perfect square, discriminant of the form 16 f(x_1) f(x_2)) without listing is outside CE. That structured search is exactly the "elliptic Cornacchia problem" of Section 3.2 of the report; the list-length bound says nothing about it. Counting alone cannot, because Im(phi) is a surface with ~omega^{2/9} points in a box with ~omega/p lattice points.
* **G5 (reduced basis instead of list).** The model returns every box vector; LLL/BKZ return a basis. Sufficiency (unique-SVP regime, omega < p) is clear; the converse (a planted vector in the long-list regime is not in the returned basis except by luck) is true under Gaussian-heuristic assumptions but I have no unconditional statement. Transference (Banaszczyk, factor n) would relate the primal form used here to the dual polynomial form used by Howgrave-Graham; not carried out.
* **G6 (other held points).** Lattices whose entries involve coordinates of [b]Q-type points with large multiplier b: the relation h(x(P), x([b]P)) = 0 has degree ~ b^2 as a divisor on E, vacuous for b ~ N. An equidistribution statement (Weil-type for correlated multiples, or a random-coordinate hypothesis, which would trivialise the question) is needed. Single-target lattices avoid this because randomisation makes R uniform.
* **G7 (dimension).** Theorem 1 has 3^n in V <= 3^n omega. The prediction "polylog(p) dimension" would need the count in the form omega * (small)^n or a different argument; as written it holds for n = O(log p / log log p) at best. Theorem 2 has no such loss.
* **G8 (what "T >= p^{1/2-o(1)} for every m" needs).** Given a reach bound delta*(m) <= 1/(2(m-1)), the cost bound p^{1-(m-1)delta*} >= p^{1/2} is one line. So the content of the conjecture is entirely the reach bound; the bottom rung gives 1/9, 1/50, 1/252 (last extrapolated), all far below 1/(2(m-1)).

## 5. Verdict reasoning
* Criterion: not met (no reviewed theorem, no counterexample). Cannot be SUCCESS here. Not KILL: the conjecture was not refuted, and no oracle was constructed.
* Prediction 1 ("provable for D-bounded lattices of dimension polylog(p)"): **not established**; what is proved has n = 3, D <= 2, m = 2 (and the evidence for D > 2 is computational).
* Prediction 2 ("bound matching Jochemsz-May asymptotically"): **not met**; the proved class has reach 1/9 (m = 2), 1/50 (m = 3, certificate weight only), not 1/6, 1/24.
* The pre-registered mechanism "capacity theory + simulation" is not what produced the partial result. Root counting (one variable, x(R) uniform) and van der Corput did. Capacity theory would be needed exactly at G1 (several congruences, p^k), where the one-variable root-counting argument stops. I did not attempt the capacity computation of Idea 8.

## 6. Limitations
* The model in section 2 is my construction, justified by 1.1 and 1.2. A reviewer could reasonably say a different oracle rule (e.g. returning only a reduced basis) is the "real" lattice-query model; for that model I have no unconditional result (G5).
* Lemma 5 is sketched; its numerical check covers m = 2 and weights up to 1e9. The arithmetic of the exponent-matching step in the outline was done by hand, the check by machine.
* van der Corput's theorem is cited, not re-proved. I did not re-derive the claim in the report that the Chinburg et al. capacity results are for two-variable congruences; my recollection is that the Asiacrypt 2016 paper (Chinburg-Hemenway-Heninger-Scherr) is univariate, which, if right, makes G1 harder, not easier. Unverified.
* All timing and numeric results are toy scale on a shared host. Nothing here is a security statement about a deployed curve.

## 7. Suggested lead-atlas update
Open **LEAD-EXO-lattice-query-lower-bound** with disposition `partial_theorem_restricted_model` and next_action "attack G1 (equidistribution of T -> g(T) mod p^k, T < p, or capacity-theoretic replacement) and G4 (structured enumeration inside the kernel lattice)", and record two facts as closed: (i) the literal lattice-query model is vacuous (reduced basis leaks coordinates, 1.2; RAM-equivalent, 1.1), so any future statement must fix an output rule and a cost rule; (ii) for the single-congruence, modulus-p, planted-certificate class the reach is exactly 1/9 for m = 2 (certificate weight 2+3+4) with list-length cost p^{7/9} per relation, 1/50 for m = 3, and the repository's "3-dimensional lattice ceiling 1/12" in Section 3.2/6.3 should read 1/9 once the columns are weighted (measured crossing 0.104 to 0.112 at 72 to 128 bits). Deciding number: w = 9 (certificate weight of the T-coefficients of S_3), equivalently delta* = 1/9.

## Files
`exp1_lemma_bruteforce.py` (+`exp1_out.txt`, `exp1_rows.json`), `exp2_weights.py` (+`exp2_out.txt`, `exp2_rows.json`, `lib_w.py`), `exp3_weighted_lll.py` (+`exp3_out.txt`, `exp3_rows.json`, `exp3_crossings.txt`), `exp4_rank_search.py` (+`exp4_out.txt`, `exp4A_rows.json`, `exp4B_rows.json`), `exp5_volume_ineq.py` (+`exp5_rows.json`), `exp6_primitive_out.txt`, `fig.py`, `fig_sa13.png`, `DEVIATIONS.md`. All outputs are far below 5 MB.
