# G31-001 validation hook — pilot: Terracini/secant-rank instrument vs ECDLP decomposition rates

Subagent pilot, 2026-11-20. Everything in this directory:
`ec.py` (curve/embedding/Taylor machinery), `sanity.py` (pre-freeze
implementation verification), `run_pilot.py` (frozen experiment),
`frozen_config.json`, `results.json`, `run.log`, `analyze.py`,
`analysis.txt`, `check_extra.py` + `check_extra.log` (targeted follow-ups),
`charter_repeat.py` + `charter_repeat.log` (charter null distribution).
Repo `/Volumes/SSD990-2/crypto-autoresearcher` untouched (read-only use of the
G31-001 goal text and `harness/toycurve.py` as generator style reference).
No external sources consulted. sympy 1.14.0 (verified), numpy 2.4.4,
Python 3.12.8.

## 0. Freeze record

Parameters (curve seeds, p-bits, N-arms, m, target counts, RNG keys,
comparison-set kinds, witness budgets) were written to `frozen_config.json`
at **2026-11-20T22:26:07Z (UTC), before any target was sampled**, and were
never retuned. `sanity.py` ran before the freeze; it verifies the
implementation, not the parameters. One pre-freeze failure was found and
fixed in the *test*, not the math (see §1 multiplicity note).
Post-freeze additions (`check_extra.py`, `charter_repeat.py`) only add
measurement power with fresh seeds; they change no frozen cell.

## 1. The mathematics as implemented, and one correction to the hook text

Embeddings = complete linear systems L(d·O) on the plane cubic, basis ordered
by pole order at O (wt x = 2, wt y = 3):

    phi_3 = (1, x, y)                 in P^2  (plane cubic)
    phi_4 = (1, x, y, x^2)            in P^3
    phi_5 = (1, x, y, x^2, xy)        in P^4
    phi_6 = (1, x, y, x^2, xy, y^2)   in P^5  (the hook's r = 5, degree-6 model)

Verified in `sanity.py` before use (all PASS):

* **phi_d(O) = last coordinate**, derived as the genuine limit at O = [0:1:0]
  in F_p((u)): with local parameter u = X/Y, v = Z/Y solves
  v = u^3 + a u v^2 + b v^3, so x = u^-2 W(u), y = u^-3 W(u), W(0) = 1;
  ct(u^d · monomial) = 1 only for the monomial with pole order 2i + 3j = d.
  Passed d = 3..6. (So the hook's phi(O) = [0:0:0:0:0:1] is confirmed.)
* **Basis independence**: evaluation matrix of the d monomials at d random
  points has rank d (independent mod y^2 = x^3 + ax + b), d = 3..6.
* **Multiplicity ("Terracini") columns**: repeated points use Taylor columns
  [phi(P), phi'(P), phi''(P), ...] in a uniformizer (x if y ≠ 0, else y),
  solved order-by-order from the curve equation; tangent-line and osculating
  containment tests 200/200 PASS. (Pre-freeze bug found here: a multiplicity
  scheme of total size m < d − 1 leaves a residual of degree ≥ 2, which has no
  base point — containment then legitimately fails. The scheme must have
  total size exactly d − 1. Test fixed; machinery unchanged.)

**Correction to the hook's literal dictionary test (i).** The hook asks that
a decomposition Q = P₁+P₂+P₃ imply φ₆(Q) ∈ span(φ₆(P₁),φ₆(P₂),φ₆(P₃)) in the
degree-6 embedding. This statement is **false for degree-and-sign reasons,
not implementation reasons.** A hyperplane section of φ_d(E) is an effective
divisor ∼ d·O; on a genus-1 curve, A ∼ B ⟺ sums agree, so hyperplane-section
points sum to O. Hyperplanes through a scheme of total size m cut a residual
of degree d − m; a curve point Q ≠ P_i is in the span iff that residual has a
base point, i.e. **iff d = m + 1**, in which case the unique residual point is
**−P₁−…−P_m**. The exact dictionary is therefore

    φ_{m+1}(−P₁−…−P_m) ∈ span of the scheme columns of φ_{m+1}(P₁..P_m),

and containment for a curve point forces Q ∈ {P_i} or Q = −ΣP_i — the span
condition is *equivalent* to a decomposition, in both directions, up to the
trivial self-containments Q = P_i. Two corrections to the hook:
(1) use the degree **d = m+1** embedding (the goal text itself says
"degree r+1": for m = 3 that is the quartic in P^3, not the sextic in P^5);
(2) **sign**: containment sees −ΣP_i (classically: the third collinear point
is −P−Q, not P+Q). Neither correction affects decomposition counts: the
x-window base is closed under negation, so r(Q) = r(−Q) (spot-checked
160/160, `check_extra.py`).

Pre-run negative controls (`sanity.py` D): φ₆(±ΣP) contained in
span φ₆(P₁,P₂,P₃): 0/200 + 0/200, confirming the failure of the literal
d = 6, m = 3 form is structural (residual degree 3, base-point-free), not a
bug. The bonus m = 5 cell re-runs the hook's own r = 5 embedding where it is
correct (d = 6 = m+1).

## 2. Setup (frozen; curves deterministic from seeds; #E Hasse-searched then
verified by naive point count)

| bits | p | a, b | #E(F_p) | cofactor c | #G = n | arm | N | \|B_raw\| | \|B_G\| | targets |
|---|---|---|---|---|---|---|---|---|---|---|
| 17 | 131671 | 100982, 6100 | 131962 = 2·65981 | 2 | 65981 | N2 | 362 | 354 | 354 | 320 |
| 17 | 131671 | 100982, 6100 | 131962 = 2·65981 | 2 | 65981 | N3 | 51 | 58 | 58 | 320 |
| 18 | 265987 | 186926, 57458 | 266491 (prime) | 1 | 266491 | N2 | 515 | 488 | 488 | 320 |
| 18 | 265987 | 186926, 57458 | 266491 (prime) | 1 | 266491 | N3 | 64 | 52 | 52 | 320 |
| 20 | 1060981 | 813223, 502743 | 1061211 = 3·353737 | 3 | 353737 | N2 | 1030 | 1062 | 1062 | 320 |
| 20 | 1060981 | 813223, 502743 | 1061211 = 3·353737 | 3 | 353737 | N3 | 102 | 120 | 120 | 320 |
| 13 | 8219 | 2323, 5856 | 8123 (prime) | 1 | 8123 | N2 | 90 | 92 | 92 | 1200 |
| 13 | 8219 | 2323, 5856 | 8123 (prime) | 1 | 8123 | N3 | 20 | 20 | 20 | 1200 |
| 13 | 8219 | 2323, 5856 | 8123 (prime) | 1 | 8123 | N5 (bonus, m=5) | 6 | 4 | 4 | 1200 |

N2 = ⌊√p⌋, N3 = round(p^{1/3}), N5 = round(p^{1/5}).
B_raw = {P : 0 ≤ x(P) < N, both y-signs}; B_G = {c·P} deduped with O removed
(none collided; O-collisions 0 in every cell) — clearing-the-cofactor is
documented as a base change (standard practice). Every B_G is closed under
negation. Counts r_m(Q) = # ordered m-tuples from B_G with sum Q, by vectorized
pair-sum tables; **the vectorized r₃ and r₄ were cross-checked against
independent brute-force enumeration on a p = 2053 curve (12 targets × m ∈
{3,4}, exact agreement)**, and every dictionary witness was re-verified with
the group law (wit_bad = 0 everywhere).

## 3. Dictionary test (i): EXACT PASS in the corrected form

* **Witnesses with a decomposition: containment φ_{m+1}(−Q) ∈ scheme-span of
  the witness columns: 2923/2923 x-window PASS, 958/958 charter-set PASS.**
  Zero failures (m = 3 → φ₄, m = 4 → φ₅, m = 5 → φ₆, repeated points handled
  with tangent/osculating columns).
* **Converse.** Random-Q control (24000 draws): only 2 containments found,
  both explained (Q ∈ {P_i} trivial), 0 violations. Powered test
  (`check_extra.py`, 3 curves): for 4500 random base triples the residual
  point −ΣP is contained (4500/4500), and of 22497 random other curve points
  none was contained (0 false containments). Consistent with the exact
  equivalence of §1: **at d = m+1 there are no "secant hits outside the
  base"; that population only exists if the span is evaluated in a degree
  d > m+1 embedding, where the containment instead never occurs.**
* **Hook-literal control** (φ₆(+Q), distinct-point columns): 8/2923 hits;
  all 8 reproduced 1:1 (`check_extra.py`) and all are trivial self-
  containment (the target happened to lie in B_G, so a witness contains Q).
  Unexplained: 0.

## 4. Decomposition rate vs secant dimension count

λ = |B_G|^m / #G; naive = min(1, λ); Poisson = 1 − exp(−λ/m!) (the secant
count predicts *tuples*, so per-target fraction needs the m! unordered
correction). Full table in `analysis.txt`; informative (unsaturated) cells:

| p | m | \|B\| | λ | measured frac | Poisson | frac/Poisson | r̄/λ | frac/naive |
|---|---|---|---|---|---|---|---|---|
| 8219 | 3 | 20 | 0.985 | 0.1425 (1200 T) | 0.151 | 0.941 | 0.856 | 0.145 |
| 131671 | 3 | 58 | 2.96 | 0.3781 | 0.389 | 0.972 | 0.924 | 0.378 |
| 265987 | 3 | 52 | 0.528 | 0.0844 | 0.084 | 1.002 | 0.959 | 0.160 |
| 1060981 | 3 | 120 | 4.89 | 0.6281 | 0.557 | 1.128 | 1.059 | 0.628 |
| 8219 | 4 | 20 | 19.7 | 0.5725 (1200 T) | 0.560 | 1.023 | 0.974 | 0.573 |
| 265987 | 4 | 52 | 27.4 | 0.6813 | 0.681 | 1.000 | 0.895 | 0.681 |
| 131671 | 4 | 58 | 172 | 1.000 | 0.999 | 1.001 | 1.018 | 1.000 |
| saturated cells (λ ≥ 8·10² ) | 3,4 | — | — | 1.000 | 1.000 | 1.000 | 0.983–1.033 | 1.000 |

* **Tuple counts**: r̄/λ ∈ [0.86, 1.06] across all informative cells (m = 3, 4)
  — the dimension count |B|^m/#G predicts the mean number of decompositions
  to within ≈ 6–14%, including N2 and N3 arms and both m.
* **Target fractions** agree with the *factorial-corrected* (Poisson) secant
  prediction within 0.94–1.13×; the hook's raw min(1, |B|^m/#G) fraction
  formula is off by 6–7× exactly where λ ≲ 1 (it saturates far too early).
  The dictionary's "relation-rate heuristic IS the secant dimension count"
  holds for tuple counts, and for target fractions only with the ordering
  correction.
* **m = 5 bonus (hook's own r = 5 / φ₆ embedding, p = 8219, N5 = 6)**:
  dictionary 4/4 PASS, but |B_G| = 4 made the rate cell uninformative
  (frac 0.0033, mean r̄ 0.03 vs λ = 0.126 — within the huge small-set
  sampling variance; recorded as infeasible-to-informative, not as a
  disagreement). Documented precisely: N5 = p^{1/5} was frozen too small.

## 5. Charter test: x-window base vs generic sets of the same size

Same sizes, same targets; generic sets uniform, and symmetric under negation
(the x-window base is symmetric; uniform sets test the asymmetric case).
Single-draw comparisons in `analysis.txt`; because single draws are noisy, the
informative (N3) cells were repeated with 10 fresh generic sets per kind
(`charter_repeat.log`). x-window frac vs the 10-draw null (band, z, rank):

| p | m | x-window frac | uniform null | symmetric null | rank |
|---|---|---|---|---|---|
| 8219 | 3 | 0.1425 | 0.1713 ± 0.0158 | 0.1494 ± 0.0121 | below all 10 uniform (z ≈ −1.8); inside sym band |
| 8219 | 4 | 0.5725 | 0.6597 ± 0.0116 | 0.5793 ± 0.0498 | below all 10 uniform (z ≈ −7.5); inside sym band |
| 131671 | 3 | 0.3781 | 0.4044 ± 0.0279 | 0.3828 ± 0.0221 | inside both |
| 131671 | 4 | 1.0000 | 0.9994 ± 0.0020 | 0.9984 ± 0.0022 | above all (saturated) |
| 265987 | 3 | 0.0844 | 0.0844 ± 0.0224 | 0.0856 ± 0.0154 | dead centre |
| 265987 | 4 | 0.6813 | 0.7309 ± 0.0343 | 0.6941 ± 0.0285 | below all 10 uniform (z ≈ −1.4); inside sym |
| 1060981 | 3 | 0.6281 | 0.5644 ± 0.0178 | 0.5575 ± 0.0278 | above all 20 generic draws (z ≈ +3.6 / +2.5) |
| 1060981 | 4 | 1.0000 | 1.0000 | 1.0000 | saturated; mean_r 605 vs 585 ± 5 (high) |

**Verdict: "differently", i.e. the "identically" branch is rejected.** In 4
of the 8 informative cells the x-window fraction lies below all 10 (or above
all 20, for 1060981 m = 3) fresh generic draws of the same size — both
directions occur, effect sizes up to ~9 points of fraction, |z| up to ≈ 7.5.
(The symmetric-generic null band is wider and contains the x-window in 3 of
the 4; the one cell outside both nulls is 1060981 m = 3, high.) Mean tuple
counts r̄ are much closer (within a few %, except p = 8219 m = 3 where
r̄ = 0.84 vs null 0.97). So the x-window geometry changes the *coverage
distribution* of sums (coverage up or down depending on the curve) while
leaving total tuple supply ≈ invariant — exactly what a sumset-structure
(not dimension) effect looks like. The magnitude is small and the sign is
curve-dependent, so this is a **real signal but not yet a usable law**; a
same-size generic set is *not* an exchangeable null for x-window rates.

## 6. Scale check (p = 8219, 1200 targets)

Included above: dictionary 575/575 witnesses; converse clean; r̄/λ
0.86–1.00; charter anomalies (m = 3 and m = 4 below the uniform null) are the
strongest in the ladder and were resolved by 20-draw nulls, so they are not
noise.

## 7. What this does and does not establish

Does establish (at tested toy tier, prime fields, m ≤ 5):
1. The concrete L(d·O) embedding machinery (phi_d, φ_d(O), scheme/Terracini
   columns) is correct and exactly reproduces the divisor–group dictionary.
2. The dictionary **with correction d = m+1 and sign −ΣP_i** is an exact
   equivalence between decomposition and span-containment: 3881/3881
   witnesses, zero converse violations, zero unexplained hook hits.
3. The secant dimension count predicts **mean decomposition counts** to
   within ≈ ±15% at this tier, and target fractions once the m! ordering
   correction is applied; the hook's uncorrected min(1, |B|^m/p) fraction is
   wrong by up to 7× for sparse bases.
4. The x-window base is **not** geometrically exchangeable with a generic set
   of the same size: its coverage rate deviates from a 20-draw generic null,
   in a curve-dependent direction. Secant/sumset structure of the x-window
   base is measurable — the program's stated reason to care — but its sign
   and size are not yet predictable.

Does NOT establish:
* anything about char-2 / Weil-restriction defectivity (the validation hook's
  dichotomy arm was not in this subagent's scope — only prime fields here);
* anything above toy tier (no extrapolation to crypto scale; G30-003 protocol
  respected); nothing about Green–Lazarsfeld indices or monodromy
  replication (kill-criterion (c) needs G30-007 outputs);
* any exploitable attack signal: deviations are ≤ ~9 points in fraction,
  direction varies by curve, m ≤ 5, single curve per p;
* the hook's literal test (i) as written — it fails by construction (§1);
  a re-run of this hook must adopt d = m+1 with the −ΣP_i convention;
* the m = 5 rate cell (frozen too sparse to inform); the r̄-vs-λ agreement
  for m = 5 is untested beyond that cell's dictionary pass.
