# LEAD-EXO-low-degree-query-lower-bound: desk theory step (a)

Date 2026-11-04. Derivation and literature check only. No experiments were run, no repository files were edited, and nothing was committed.
Every claim carries a tag: **[proved here]**, **[cited: source]** or **[heuristic]**.

Notation. E/F_p has prime order N, P is a public generator, Q = [k]P, and k is uniform in Z/N. R := Q.
The solver holds encodings of X_i = [a_i]P + [b_i]Q = [b_i]R + [a_i]P. A test asks "f(coords of X_1..X_t) = 0?",
where f has total degree <= D and no auxiliary variables. Group ops and tests are counted. Local work is free, as in Shoup.
For each X_i, b_i is taken as the representative of b_i mod N with |b_i| <= N/2. This choice is free, because
[b]R depends only on b mod N for R in E(F_p).

## 1. Model check. Verdict: H1 as stated is false (one step is conditional and exactly checkable). The restated H1' is proved.

**1a. Single-point tests do not leak.** [proved here] The degree-1 test x(Q) = c, with c = x([j]P) computed locally,
is true for at most 2 values of k. Any degree-D test on the single point Q, or on any one X_i, is true for at most
2D (or 3D with y) values of k, unless it vanishes identically. Through "[b]R is a bijection on E(F_p)", this also covers
the case of one point with large b. So "one bit per test about membership in a set of size <= 2D" is
consistent with the T^2/N term. There is no leak at t = 1.

**1b. Where H1 breaks: many points and large multipliers.** The H1 term "T D p^(-1/2)" charges a test by the degree D of f
in the coordinates. The pulled-back function g(R) = f(x([b_1]R + a_1P), ..., ) has degree on E of up to
Delta := sum_i (2 d_{x,i} + 3 d_{y,i}) b_i^2, where d_{x,i} and d_{y,i} are the degrees of f in x_i and y_i.
Delta, not D, controls how many k a test can catch. Large b_i cost only O(log N) group ops.

*Interpolation attack.* [proved here, given the rank condition] Let V = { v(R) = (x([b_1]R),...,x([b_t]R), y(...)) : R in E(F_p) },
a set of N points (|V| = N once one y-coordinate is included). Let r be the rank of the evaluation map
Poly_{<=D}(t vars) -> F_p^V.
- For any candidate set A with |A| <= r - 1 there is an f of degree <= D that vanishes on v(A) and is not identically 0 on V
  (linear algebra, done in free local work).
- If r = N (full rank, "every function on E(F_p) is a degree-<=D polynomial in the coordinates of [b_i]R"),
  then one test answers "k in S?" for any chosen S. Binary search finds k with ceil(log2 N) tests.
  The total is T = O(t log N) group ops (double-and-add for the [b_i]Q) + log2 N tests, and the success probability is 1.
- r = N needs C(t+D, D) >= N. For example:
  - D = 3, t ~ (6N)^(1/3): T = O(N^(1/3) log N).
  - D = t ~ (log2 N)/2 + O(1): T = O(log^2 N), with D = O(log p) = p^(o(1)).
  - D = p^(1/4), t = 5: T = O(log p).
  Each of these contradicts H1, which predicts T = Omega(min(sqrt N, sqrt p / D)) for D = p^(o(1)).
- Without full rank, sequential elimination with tests "k in A_j" (|A_j| = r - 1, disjoint) succeeds after j tests
  with probability >= j(r-1)/N. **H1 therefore implies a purely public rank bound** [proved here]: for encodings costing T queries,
  r <= c1 T^2 + c2 T D N p^(-1/2) polylog p = O~(T^2 + T D sqrt p).

*Is r = min(N, C(t+D,D))?*
- [heuristic] For random large b_i (pairwise coprime, not in arithmetic progression) the points of V show no
  low-degree structure. Random point sets in F_p^t with p >> N impose independent conditions on degree-D
  polynomials w.h.p. (Schwartz-Zippel on minors). So the heuristic prediction is full rank, and H1 then fails.
- [proved here] Formal independence. If the b_i are odd, pairwise coprime, prime to p and satisfy b_i^2 > 2D sum_{j<i} b_j^2 + 1, then the monomials
  of degree <= D in x∘[b_i] are linearly independent in F_p(E). Proof by induction on t: write a relation as sum_j r_t^j G_j(r_{<t}).
  r_t = x∘[b_t] has double poles at the x-roots of psi_{b_t} ((b_t^2-1)/2 of them, disjoint from the b_i-torsion for i < t, by coprimality).
  For the top J with G_J ≢ 0 (induction), G_J(r_{<t}) has < (b_t^2-1)/2 zeros, so it is nonzero at some such root θ.
  There the J-th term has pole order exactly 2J and every other term has lower order. Contradiction unless J = 0. ∎
  Then evaluation on V is injective (r = C(t+D,D)) whenever 2D sum b_i^2 < N. That regime has C(t+D,D) << N, so it does **not**
  reach the counterexample. Full rank at C(t+D,D) ~ N stays heuristic.
- [proved here] Multiplicative analogue (sanity check that the structure of the attack is real). In F_p^* with encodings z^{b_i},
  take b = j m^l (0 <= j < m, l < h, m = ceil(p^(1/h))). Every monomial z^e factors as a product of h of these coordinates,
  so every function on F_p^* is a polynomial of degree h in t = h m coordinates. This gives T ~ h p^(1/h) + log2 p and the
  analogue of H1 is false, unconditionally. The elliptic case lacks this proof because x∘[b] is not a character.
  No polynomial in the coordinates is a homomorphism on E, which is why full rank there is heuristic.

**1c. Relation to the holant Lemma 3.** The x-oracle is vacuous because two queries plus free local work give log_P Q.
Degree-D tests are a weaker oracle (one bit each), but the same free-local-work loophole operates: the attack spends
about N^ω free local field operations to solve the interpolation systems. A query lower bound in this model therefore has to charge Delta,
or restrict local work. In the second case it becomes a complexity conjecture that no GGM-style argument can prove.

**Restatement H1'** [proved here; Lemma in §2 plus the Shoup union bound]. For any adaptive algorithm with T_g group ops and tests j = 1..T_t,
where test j has pulled-back degree Delta_j (computed with minimal representatives |b_i| <= N/2):

    Pr[success] <= ( C(T_g+2, 2) + sum_j (Delta_j + t_j) + 1 ) / N.

So sub-sqrt(N) success needs tests with sum_j Delta_j >~ N. A test with Delta ~ N/2 needs D sum b_i^2 ~ N.
This is the correct scope: the bound is meaningful for "low-degree statistics of points with small multipliers"
(bounded b_i: shifts Q + a_iP, small multiples [2]Q, [3]Q, cross-ratios of such points). H1 as written, with D in place of Delta
and arbitrary b_i, is not meaningful (heuristic counterexample above).
Remark [heuristic]: endomorphisms alpha in Z[π] with alpha ≡ b on E(F_p) could lower Delta further (deg x∘alpha = 2·Norm(alpha)).
The minimal norm in the coset b + (π-1)Z[π] is ~ N sqrt p in the worst case, so this helps only for b near N/2.

## 2. Single-test lemma [proved here]

**Hypotheses.** p > 3, E: y^2 = x^3 + ax + b over F_p, #E(F_p) = N prime, P a generator, k uniform on Z/N, R = [k]P.
Fixed (k-independent) data: integers a_i, and b_i with |b_i| <= N/2 (so p ∤ b_i, since N/2 < p by Hasse for p > 3),
and f in F_p[x_1,y_1,...,x_t,y_t] with degrees d_{x,i}, d_{y,i} in x_i, y_i. Let Delta = sum_i (2 d_{x,i} + 3 d_{y,i}) b_i^2 (<= 3D sum_i b_i^2).
Let g := f(x∘φ_1, y∘φ_1, ...) in F_p(E), where φ_i(R) = [b_i]R + [a_i]P.
Simulator answer: "yes" iff g = 0 in F_p(E) (formal vanishing). Define g ≡ 0 for "undefined" if some φ_i(R) = O; the simulator treats that as a group collision.

**Statement.** Pr_k[ true answer ≠ simulator answer, or some φ_i(R) = O ] <= (Delta + t)/N.

**Proof.** φ_i(R) = O for exactly one k when b_i ≠ 0, and for none when b_i = 0 and a_i ≠ 0 (if both are 0, X_i = O publicly). This gives <= t values.
Otherwise every coordinate is defined. If g ≡ 0 the answers agree. If g ≢ 0, the answers differ iff g(R) = 0.
x∘φ_i has poles only on φ_i^{-1}(O), which is b_i^2 points (since [b_i] is separable when p ∤ b_i), each of order 2. y∘φ_i has the same poles with order 3.
So the polar divisor of g has degree <= Delta, and g has at most Delta zeros on E(F̄_p). k -> R is a bijection, so the bad set has <= Delta + t values. ∎
Tightness [proved here]: with b_i = 1 (X_i = Q + [i]P, t group ops), the functions x_i^j (j <= D) give rank >= tD + 1 on V.
A test can therefore be made to vanish on any chosen tD points, against the bound Delta = 2tD. The lemma is tight to a factor of about 2.
Adaptive multi-test version: the simulated transcript does not depend on k, so the bad events are fixed in advance and the union bound gives H1'. [proved here, standard Shoup argument]

Note: Weil/Bombieri adds nothing here. The KS bound (3) below gives #zeros <= N/p + 2 Delta sqrt p, which is worse than Bezout's Delta. [proved here]

## 3. Multi-point status

- With small b_i, multi-point adaptive tests reduce to one function g on E of degree Delta. Bezout settles them, with no character sums needed. [proved here]
- To get H1's form with D in place of Delta, you need square-root cancellation for sums over a cyclic subgroup H = <(b_1P,...,b_tP)> (translated) of E^t(F_p):
  #Z = N/p + (1/p) sum_{λ≠0} sum_{h∈H} ψ(λ f(h+c)). H1 would follow from |sum_{h∈H} ψ(f(h+c))| <= C D sqrt p polylog p for f of degree D not vanishing on H. [proved here]
  This is **not** a Kohel–Shparlinski sum for t >= 2.
  - Completing over the characters of E^t(F_p)/H costs (|H|/|E^t|)·(|E^t|/|H|)·C p^{t/2} = C p^{t/2}, which is >= N for t >= 2, so it is vacuous. [proved here, as a computation]
  - Pulling back to E gives 2 Delta sqrt p, which is vacuous for large b_i.
  - These are elliptic analogues of sparse-polynomial sums sum ψ(f(z, z^m, ...)). For those only tiny p^(-δ) savings are known [cited: Bourgain, "Mordell's exponential sum estimate revisited", JAMS 18 (2005); recalled, not re-verified here].
  - The interpolation attack (§1b) shows the needed bound is **false** whenever full rank holds [proved here, conditional on rank]: take f = indicator of a half of V, so the sum is ~N/2.
- Status: the multi-point step does not reduce to KS. In the regime H1 needs, it is false (heuristically), and it is exactly the rank question.

## 4. Kohel–Shparlinski citation (verified)

D. R. Kohel and I. E. Shparlinski, "On Exponential Sums and Group Generators for Elliptic Curves over Finite Fields",
Algorithmic Number Theory (ANTS-IV, Leiden 2000), LNCS 1838, Springer, 2000, pp. 395–404. [cited: DBLP conf/ants/KohelS00; author preprint
https://www.i2m.univ-amu.fr/perso/david.kohel/pub/character.pdf, read in full for §§1–5]
What it actually proves:
- Thm 1: |S(ω,ψ,f)| <= sum_i m_i deg(P_i) q^(1/2), where S(ω,ψ,f) = sum_{P∈E(F_q)} ω(P)ψ(f(P)), ω is a group character, ψ is additive and non-trivial on f, and m_i <= n_i + 1. Hence (3): <= 2 deg(f) q^(1/2), and (1 + deg f) q^(1/2) when f has a single pole.
- Cor 1: the same 2 deg(f) q^(1/2) bound over any subgroup H.
- Thm 2 / Cor 2: counts of points with f(P) in an interval of F_q. Points with x in an interval of length > 5(1+deg f)(1+log p) q^(1/2) generate E(F_q).
- Thm 3: deterministic O(q^(1/2+ε)) echelon generators.
The paper has **no** stated bound for sums over k in an interval of multiples kG. That bound follows from Thm 1 together with their Lemma 2:
|sum_{k<K} ψ(f(kG))| <= 2 deg(f) q^(1/2) (1 + log N) [proved here: expand 1_{k<K} in group characters].
**Sufficiency:** KS suffices for t = 1 and any f, but Bezout is already better for zero counts. It does not suffice for t >= 2 with large b_i,
because every KS bound scales with deg of the pulled-back function (Delta), not with D.

## 5. What step (b) should measure

The planned check, "max bias over degree-<=D tests on pairs (P, kP) vs D/sqrt p", has two problems: the maximum over all f is infeasible to search, and t = 2
cannot refute H1. With t = 2, r <= C(D+2,2), so the attainable bias is ~D^2/N, which beats D/sqrt p only for D > ~sqrt p.
Replace it with an **exact rank computation** (deterministic, so no null distribution is needed for the main quantity):
- r(t, D, b) = rank over F_p of the N × C(t+D,D) evaluation matrix on V, for p from 2^8 to 2^14, choosing (t, D) so that C(t+D,D)/N spans [1/4, 4]. Include
  D = 2, 3 and D ≈ t. Use random pairwise-coprime b_i and also arithmetic-progression b_i.
- Controls:
  - Shifts b_i = 1: the rank must stay <= 2Dt + 1, a positive control for rank deficiency.
  - A uniformly random point set of size N in F_p^t: the null, expected rank min(N, #mon).
  - The multiplicative analogue: full rank, proved.
- Decision:
  - r ≈ min(N, C(t+D,D)) for random b_i means H1 is refuted as stated, with the explicit attack of §1b (T = O(t log N) + log2 N). The lead row is then restated to H1' (proved).
  - r stays <= O~(T^2 + T D sqrt p) means an unexpected structural result that is worth a note.
- Also record per test the realized |Z| against Delta and against the chosen |A|. This checks that the extra zeros stay small.
- The attack's local work (about N^ω field operations) must be reported. It is no practical threat, and no cost claim follows from it.

Sources: [DBLP record](https://dblp1.uni-trier.de/rec/conf/ants/KohelS00.html), [Kohel preprint](https://www.i2m.univ-amu.fr/perso/david.kohel/pub/character.pdf).
