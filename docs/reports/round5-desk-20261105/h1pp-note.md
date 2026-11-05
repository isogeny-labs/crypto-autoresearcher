# LEAD-EXO-low-degree-query-lower-bound: description-length-charged bound (H1'')

Date 2026-11-05. Desk step plus a tiny exact check. No repository files were edited. [pcc:unverified]
Tags: **[proved here]**, **[cited: source]**, **[heuristic]**, **[open]**.
Inputs read: the lead row; `docs/reports/ecdlp-leads-desk-20261104/low-degree-desk.md` (H1', interpolation attack);
`docs/reports/lowdeg-rank-20261104/README.md`; `docs/reports/leads-round2-20261104/new-leads-memo.md` §D2 (HD2c).

Notation follows the desk note. E/F_p has prime order N, Q = [k]P, k is uniform. Encodings X_i = [a_i]P + [b_i]Q.
A test is a polynomial f of total degree <= D in the affine coordinates of t encodings. Its zero set is
Z_f = { k : f(v(k)) = 0 } ⊆ Z/N, where v(k) is the coordinate tuple. Its **minority size** is mu(f) = min(|Z_f|, N - |Z_f|).

## 1. Model

A solver makes T_g group operations (Shoup encodings) and T_t tests. Test j uses t_j encodings and a polynomial f_j.
Each test is charged one of these description measures:
- L(f): the number of nonzero monomials (sparsity);
- s(f): the straight-line-program size over F_p (+, ×, constants);
- B(f): the bit length, about L(f)(log2 p + log2 M), where M = C(2t+D, D) is the number of monomials.

The multipliers b_i are free (O(log N) group operations each), as in the desk note. Local work stays unbounded. The
charged resource is the description, not the computation. A bound that charges local work alone would be an
unconditional computational lower bound, which no GGM-style argument gives (desk note §1c). I do not pursue it.

## 2. Results

**Lemma A (exact reduction to minority sets)** [proved here]. For any adaptive solver, [pcc:unverified]

    Pr[success] <= ( C(T_g+2, 2) + 1 + sum_j ( mu_j + t_j ) ) / N,

where mu_j is the minority size of test j, computed for the encodings and f_j that the simulated transcript fixes.
*Proof.* This is Shoup's simulation, with one change: the simulator answers each test with its **majority**
answer over k. That answer is well defined because the simulated transcript, and with it (a_i, b_i, f_j), does not depend on k.
The real and simulated transcripts differ only if k lies in a minority set Z_j or its complement (at most mu_j values), or
some X_i = O (at most t_j values), or two encodings collide (at most C(T_g+2,2) values). The union bound and the final guess give the rest. ∎
Lemma A is the exact form. Every bound on mu feeds it directly, and H1' is the special case mu <= |Z| <= Delta
(Bezout, desk note §2).

**Lemma B (no description bound can beat sum_j L_j)** [proved here]. Take any L monomials whose columns are independent on [pcc:unverified]
the candidate evaluation matrix. Then there is an f supported on them that vanishes on any L - 1 prescribed candidates
and is not identically zero (kernel of an (L-1) × L system). So max mu over L-term tests is at least L - 1, as soon as L - 1 <= N/2 and
an independent L-set exists. The rank experiment shows such sets exist up to L = N at M ≈ 2N. So the strongest
possible charged bound is Pr <= (T_g^2 + sum_j L_j · polylog)/N.

**Lemma C (counting: prescribed balanced S need many monomials)** [proved here]. Fix the encodings. [pcc:unverified]
An L-term test is determined by its support (C(M, L) choices) and, up to scale, by its coefficients (p^(L-1)). So L-term tests
cut out at most C(M,L) p^(L-1) distinct zero sets. For a uniformly random S with |S| = s, the probability that some L-term f
has Z_f = S is at most C(M,L) p^(L-1) / C(N,s). For s = N/2 and M = N^(O(1)), this gives:

    L >= (N - O(log N)) / (log2 p + log2(eM/L)) = Omega(N / log N)   for all but a 2^(-Omega(N)) fraction of S.

The same count over SLPs (at most (c(s+t)^2 p)^s programs of size s) gives s(f) = Omega(N / log(pN)) for generic S. [pcc:unverified]
This is the rigorous form of HD2c ("about N/2 monomials"), up to the log factor. The GV estimate below suggests the true
generic minimum is a constant times s.
*Scope* [proved here]. Lemma C bounds nothing in the worst case. A solver chooses its own S, and a depth-log2 N
decision tree uses only N - 1 distinct sets. So a family of tests with only about N members could still contain a perfect halving tree.
Counting therefore refutes "the interpolation attack is cheap for an arbitrary S", but it cannot give H1''.

**Reduction of H1'' to one open quantity** [proved here, from A and B]. Let mu*(L) be the maximum of mu(f) over all multipliers, [pcc:unverified]
all t, and all L-term f of degree <= D with prime-order E. Then Pr <= (C(T_g+2,2) + 1 + sum_j (mu*(L_j) + t_j))/N, and
mu*(L) >= L - 1. Charging the description restores a square-root-type bound **iff** mu* grows slowly:
- **H1''-strong** [heuristic]: mu*(L) <= L · N^(o(1)) (+ O(D)). Then success needs T_g ≳ sqrt N or sum_j L_j ≳ N^(1-o(1)).
  The tests would be worth no more than a DL table, so the interpolation attack is optimal in this measure.
- **H1''-weak** [heuristic]: mu*(L) <= L · N^(1/2+o(1)). This already gives sum_j L_j ≳ N^(1/2-o(1)), a sqrt(N)-type bound in the charged measure.
- **Status** [open]: neither is proved, even for **L = 2**. A binomial test c1 m1 + c2 m2 has as zero set a fiber of the
  pulled-back function m1/m2 ∘ v on E. Weil and Kohel–Shparlinski bound fibers only by 2 deg · sqrt p, and that degree scales
  with Delta = sum (2d_x + 3d_y) b_i^2, which is vacuous for large b_i (desk note §§2–4). With small multipliers, mu <= Delta (H1') remains the only theorem.
- **Prime order matters** [proved here]. Over F_p^* (composite order p - 1), the 2-term, degree-1 test x_1 - x_2 with b_2 = b_1 + (p-1)/2
  cuts out the quadratic residues, so mu = (p-1)/2. Its answer is interpretable without enumeration (Pohlig–Hellman). On E of prime order,
  [b_1]R = [b_2]R forces k = 0, and no subgroup-coset test of that kind exists.
- **Multiplicative prime-order analogue** [cited, recalled and not re-verified: Bourgain, JAMS 18 (2005), sparse-polynomial sums under
  gcd conditions on the exponents]. That result gives mu <= N/p + p^(1-delta(L)), with delta(L) > 0 tiny and decaying in L. This is a genuine but
  very weak description-charged bound (T_t ≳ p^(delta(L))), and only for the analogue. No elliptic counterpart is known to me [open].

**Interpreting short tests** [heuristic]. Short tests with large zero sets but degree > D, such as the Legendre symbol of x (degree (p-1)/2), lie outside the
model. Inside it, the toy data show that short tests have small, pseudo-random zero sets. Their answers carry about
mu/N bits and, if local work is charged, cost Θ(N) local work to interpret (enumerate Z). That is the D2 picture.

## 3. Exact toy check (scripts `h1pp_check.py`, `h1pp_scaling.py`; about 30 s total, 1 core)

The curve is y^2 = x^3 + 4x + 1 over F_263, of prime order N = 281. Candidates are the classes {k, -k}, of which there are C = 140 (x-only).
The test uses t = 9 points with multipliers b = (67, 79, 52, 212, 88, 218, 154, 89, 235), D = 3, and M = 220 monomials. The rank is 140 (full).

(a) Largest minority set of short tests. L = 2 is exhaustive: all 24,090 binomials and every coefficient. L = 3 is sampled: 600 triples, every
pair of coefficients.

| arm | candidates | rank | max mu, L=2 (exact) | max mu, L=3 (sampled) |
|:--|--:|--:|--:|--:|
| E, random b_i | 140 | 140 | 10 | 8 |
| null, uniform random matrix | 140 | 140 | 8 | 9 |
| positive control: F_263^*, b_2 = b_1 + 131 | 261 | 157 | **130** | 130 |
| F_263^*, prime-order subgroup (q = 131) | 130 | 104 | 1 | 5 |

The positive control confirms that the search detects a balanced split. On E, the worst binomial is (x_8/x_1)^2 = c. That is two
fibers of a ratio, giving 10 of 140 classes, at the level of the random-matrix null. So no short balanced tests appear at toy size. This is consistent
with H1''-strong and not evidence for its asymptotics.

(b) Smallest support of an f that vanishes on a random S, found by Prange-style information-set search with 150–300 trials. Each value is an upper bound
on the true minimum.

| s = abs(S) | 10 | 20 | 35 | 50 | 70 | 90 | 110 | 130 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| best support found (E) | 9 | 19 | 34 | 48 | 68 | 85 | 107 | 127 |
| GV estimate (random code) | 7 | 13 | 24 | 35 | 51 | 68 | 86 | 105 |
| counting lower bound (Lemma C) | 4 | 7 | 9 | 10 | 11 | 10 | 8 | 4 |

At s = 70 (3 replicates), E gives 67–68 and the null gives 66–67, against the trivial bound s + 1 = 71. The found f vanish exactly on S in 4 of the 6 cells. [pcc:unverified]
The supports scale linearly in s, at about 0.97 s found and about 0.73 s by GV. E is indistinguishable from the null.
At this size the counting bound is weak (about N/(2 log2 p)). It is a proved floor only. Note that (b) concerns *prescribed* S. By Lemma C's scope note,
it says nothing about a solver that picks S.

Outputs: `h1pp_check.json` (sha256 665b74e0…), `h1pp_scaling.json` (d2d42539…). Scripts: `h1pp_check.py` (9aab45c4…; docstring says p = 251 but runs p = 263),
`h1pp_scaling.py` (766f878c…).

## 4. Proposed row text and implications

**H1'' (proved reduction).** Pr[success] <= (C(T_g+2,2) + 1 + sum_j (mu(f_j) + t_j))/N, where mu(f) = min(|Z_f|, N - |Z_f|). [pcc:unverified]
Proved consequences:
- mu <= Delta (this is H1');
- max mu over L-term tests is at least L - 1, so no description bound beats sum_j L_j;
- a prescribed generic balanced S needs L = Omega(N / log N) monomials, or SLP size Omega(N / log(pN)). This is the rigorous HD2c.

**Conjecture H1''-strong** [heuristic]. On prime-order E, every L-term degree-<=D test has mu <= L·N^(o(1)) + O(D).
That gives Pr <= (T_g^2 + sum_j L_j N^(o(1)))/N. It is supported only at toy size (max mu 10 of 140 for all binomials, matching the null), and it is open already at L = 2 (fibers of
pulled-back monomial ratios with large multipliers).

**Implication.** Charging the description restores a sqrt(N)-type (indeed linear-in-L) bound **only conditionally**, on a sparse-fiber
equidistribution statement along cyclic subgroups of E^t. That statement is the elliptic analogue of Bourgain's sparse sums, with no known proof route.
Unconditionally, what survives is the trivial part:
- the Delta bound (H1') for small multipliers;
- the fact that the specific interpolation attack pays description length Omega(N / log N) for almost every S it might target, which is dominated by a DL table.

Suggested disposition: keep `open_next_step`. The next step is the L = 2 fiber question: bound the largest fiber of ∏ x([b_i]R)^(e_i) on E(F_p). [pcc:unverified]
It should be tried first for t = 2 as a desk question, with a toy max-fiber sweep over N as an optional check of whether max mu grows faster than log N.
