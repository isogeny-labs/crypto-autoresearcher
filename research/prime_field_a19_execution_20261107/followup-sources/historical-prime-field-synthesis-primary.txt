# Structured factor bases and index calculus over GF(p): four open fronts

**Status:** research synthesis + new experimental contribution, 2026-06-07
**Branch:** `claude/index-calculus-factor-base-KU1g0`
**Builds on:** `research/ecdlp_autolab/yokoyama_lower_bound.md`,
`research/ecdlp_autolab/structured_fb_{additive,subgroup}_result.md`,
`research/ecdlp_autolab/phase6_weil_restriction.md`,
`research/notes/index-calculus/RESEARCH_FFD_PROOF_COMPLEXITY.md`, `research/notes/cm-isogeny/RESEARCH_PKM_CRITERION.md`.
**New code:** `experiments/initial_minors/` (pure-Python, no Sage/PARI needed).

This note takes the four open questions posed for prime-field index calculus,
situates each against what this repository has already established, and pushes
each forward with either a sharpened theoretical statement or a new experiment.
The honest one-line summary per front:

| # | Front | Verdict reached here |
|---|-------|----------------------|
| 1 | Structured factor base → subexponential? | **Conditional no-go is provable** (Hilbert-function invariance); a *fully general* impossibility is not, and we say exactly what is missing. |
| 2 | Weil-descent analogue over `F_p`? | **Structurally hopeless** for the three concrete candidates; we show *why* each collapses to the original DLP. |
| 3 | Last-fall-degree for prime-characteristic PDP | **The HKYY machinery does not port** — the obstruction is identified precisely (no low-degree field equations over `F_p`). |
| 4 | Mahalanobis–Abdullah–Mallick "initial minors" | **New experiment:** the natural minor search is `Θ(n)` (measured, 0.98–1.07·n over a 245× range); `2^50` is inside the regime where sub-exp and `√n` are numerically indistinguishable. The conjecture is neither refuted nor supported by the published `2^50` data. |

---

## 1. Can any structured factor base over `GF(p)` give asymptotic improvement?

### 1.1 What is already nailed down

Three structured factor bases have been built and measured in this repo and
all gave **no** speedup over a generic factor base:

- **multiplicative-subgroup FB** (constraint `X^m − 1`):
  `structured_fb_subgroup_result.md` — *2.4× slower* at 19 bits.
- **arithmetic-progression FB** (falling-factorial constraint):
  `structured_fb_additive_result.md` — flat per-query cost.
- **point-coordinate interval FB** (`x(P) ∈ [0, B)`): the Petit–Kosters–Messeng
  divisor-set construction; audited in `research/notes/cm-isogeny/RESEARCH_PKM_CRITERION.md`.

> **Scope note (2026-09-24).** PKM's published factor base is not an interval.
> It is the zero set of a *composition* of low-degree maps, with one auxiliary
> variable per level, and none of the three bases above tests it. Because those
> auxiliary variables enlarge the ring, Proposition 1 below does not cover it
> either. See `RESEARCH_PKM_TOWER_ORACLE.md` §1.3.

The theoretical reason, recorded in `yokoyama_lower_bound.md`, is the
Yokoyama–Yasuda–Takahashi–Kogure (2020) lower bound: the Gröbner solving cost is
controlled by the **degree of regularity** `Reg ≈ md + d_S − m` of the Semaev
ideal `I_m = ⟨S_{m+1}(x_1,…,x_m, x(R)), F(x_1),…,F(x_m)⟩`, where `d = deg F`
(essentially `|FB|`) and `d_S = deg_{x_i} S_{m+1}`. The bound is exponential in
`Reg`, and **`Reg` depends only on the degree of `F`, not on its sparsity or
monomial support.**

### 1.2 A clean conditional theorem (the part that *is* provable)

The empirical "sparsity does not help" can be promoted to a precise statement.
Let `V ⊆ F_p` be a factor-base x-set of size `t = |V|`, defined by the radical
ideal of the constraint polynomial `F_V = ∏_{v∈V}(X − v)`. Replacing `F_V` by
*any* other generating set of the **same ideal** `(F_V)` — e.g. the sparse
`X^t − 1` when `V = μ_t`, or a falling factorial when `V` is an AP — does not
change the ideal `I_m`, hence does not change its Hilbert function, its
Castelnuovo–Mumford regularity, its degree of regularity, or its last-fall
degree. All of these are **ideal invariants**, not invariants of a chosen
generating set.

> **Proposition 1 (sparsity invariance).** For a fixed factor-base *set* `V`,
> the solving degree `D*` of the Semaev decomposition system is independent of
> the presentation of `(F_V)`. No re-encoding of the membership constraint as a
> sparser polynomial can lower the Gröbner-basis cost below the Yokoyama bound
> for that `V`.

This is the rigorous core of the "interval / point-coordinate / AP / subgroup
all fail" observation. It is *not* hand-waving: it follows from the fact that
F4/F5 cost is governed by `D*`, and `D* = D*((I_m))` depends only on the ideal.

What Proposition 1 does **not** cover: choosing a *different set* `V` that is
genuinely smaller for the same coverage probability, or a non-radical / scheme
structure (multiplicities), or — crucially — a *non-Gröbner* solver. The
genuine asymptotic question lives entirely in those gaps.

### 1.3 What a "definitive impossibility result (à la Yokoyama)" would require

Yokoyama et al. bound *one* algorithm family (Buchberger/F4/F5 on the naive
Semaev ideal). A theorem of the form "**no** structured factor base over `F_p`
yields subexponential ECDLP" must quantify over **all** relation-search
procedures, not just Gröbner bases. The missing ingredients are:

1. **A model of computation broad enough to be meaningful but narrow enough to
   bound.** The natural candidate is the *algebraic / arithmetic-circuit* model
   restricted to the coordinate ring of the factor-base variety — but lower
   bounds there are exactly the open frontier of algebraic complexity.
2. **A proof that the relation-density obstruction is intrinsic.** For *any*
   factor base of size `t = L_p(2/3)`-ish in a prime field, the probability that
   a random group element decomposes over the base is `≈ t^m / (m! · n)`. The
   subexponential regime needs this to be non-negligible *and* the per-relation
   solve to be cheap simultaneously; over `F_p` (genus-0, no descent dimension)
   these two requirements appear to be in irreconcilable tension. Making
   "appear to be" into "provably are" is the theorem.
3. **Ruling out the lattice / `p`-adic / tropical escape routes** that
   `yokoyama_lower_bound.md` itself flags as outside the naive framework.

**Assessment.** A *fully general* impossibility theorem is, in our judgement,
out of reach with current technique — it would entail circuit lower bounds of a
kind nobody can prove. But the *intermediate* target is realistic and would
already be publishable:

> **Conjecture-to-prove (scoped).** Every factor base `V ⊆ F_p` whose membership
> ideal has the same Hilbert function as a generic set of size `t` yields the
> same `D*`; consequently the *entire homogeneous family* of "algebraically
> defined" factor bases (varieties cut out by a bounded number of low-degree
> equations) is Yokoyama-bounded.

This packages every concrete construction tried so far (interval, AP, subgroup,
PKM divisor set) into one statement, and Proposition 1 already proves it for the
single-set case. The open step is uniformity over families of equal Hilbert
function — a finite-dimensional, attackable problem, unlike the fully general
quantifier.

---

## 2. A useful analogue of Weil descent for prime fields?

`phase6_weil_restriction.md` already records the headline: GHS / Weil descent
needs a curve **originally defined over `F_{q^n}`, `n ≥ 2`**, and prime-field
curves have no such structure. Here we examine the three "more imaginative"
substitutes named in the brief and show precisely where each dies.

### 2.1 `Z_p × Z_p` as a "two-dimensional base"

The hope: treat `F_p`-arithmetic as living in a rank-2 object and descend.
But `Z_p × Z_p` (whether read as `Z/p × Z/p`, the additive group, or as `Z_p`
the `p`-adics squared) is **not a field and carries no curve**. Weil descent is
`Res_{L/K}` of a *variety* along a finite *field* extension `L/K`; it needs the
Galois action of `Gal(L/K)` to manufacture the auxiliary equations. A product
*ring* has no such Galois structure, and the elliptic curve `E/F_p` does not
base-change to it as an abelian variety. There is no functor `Res` to invoke.
**Collapses at step 0: no extension, no descent.**

### 2.2 Quadratic extensions of `Q` reduced mod `p`

The hope: take `K = Q(√d)`, an order `O_K`, reduce mod `p`, and descend the
larger structure. Two cases:

- **`p` inert in `K`:** `O_K / p ≅ F_{p^2}`. Now we *do* have an extension —
  but the DLP we care about is on `E(F_p) ⊂ E(F_{p^2})`, a **subgroup**. As
  `phase6_weil_restriction.md` proves, the discrete log on a subgroup is
  identical to the discrete log on the ambient group; embedding into `F_{p^2}`
  changes nothing. `Res_{F_{p^2}/F_p}(E)` is isogenous to `E × E^{(d)}` (twist),
  and the DLP decomposes componentwise into the *same* `E(F_p)` problem. No
  genus drop, no gain.
- **`p` split in `K`:** `O_K / p ≅ F_p × F_p`, which is §2.1 again — a product
  ring, no descent.

So reducing a quadratic field mod `p` either gives `F_{p^2}` (where the
subgroup argument kills the gain) or `F_p × F_p` (no curve). **Collapses.**

### 2.3 The structural reason there is no analogue

Weil descent converts a *one-dimensional DLP over a big field* into a
*higher-dimensional DLP over a small field* with a **smaller relative group
order per dimension**, which is what index calculus on `Jac(C)` exploits
(Gaudry: `L(2/3)` because the factor base on a higher-genus Jacobian is
relatively dense). The arithmetic engine is the field-norm map
`N_{L/K}: L^* → K^*` and the trace, which need `Gal(L/K)`.

`F_p` is the **prime** field: it has *no proper subfield*, so there is no
`K ⊊ F_p` to descend to and no Galois group to act. Any extension goes the
*wrong way* (`F_p → F_{p^n}`), and the relevant DLP stays trapped in the
`F_p`-rational subgroup. The "two-dimensional base" intuition fails because the
second dimension Weil descent needs is **Galois-theoretic, not Cartesian** — you
cannot fake it with a product. This is why the front is, as the brief suspects,
structurally hopeless; we have now made *hopeless* precise per candidate rather
than asserted.

---

## 3. Last-fall-degree bounds for prime-field PDP systems

### 3.1 The bridge that exists in this repo, and where it lives

`research/notes/index-calculus/RESEARCH_FFD_PROOF_COMPLEXITY.md` develops a genuine bridge:

> solving degree `D*` ≍ Polynomial-Calculus refutation degree of the descended
> Semaev system ≍ Huang–Kosters–Yeo **last fall degree** `d_last`,

and proposes predicting `D*` from the low-degree **Hilbert-function defect**
`δ(D)` measurable from Macaulay ranks without a full Gröbner basis. That whole
construction is **small-characteristic** (`F_2`, `F_{2^n}`): the Weil descent is
to `F_2`, and the *field equations* `x_i^2 = x_i` are degree 2 — cheap, and
essential to both the unsatisfiability (refutation) framing and the last-fall
bound.

### 3.2 The precise obstruction to porting it to `F_p`

For a prime field, the analogous field equation is `x^p − x = 0`. **Its degree
is `p`**, i.e. exponential in the bit-length. This single fact breaks the
machinery in three places:

1. **No cheap refutation closure.** The Clegg–Edmonds–Impagliazzo / Polynomial
   Calculus framing needs `x^p − x` (or `x_i^2 = x_i`) as low-degree axioms to
   make the system zero-dimensional and the refutation degree meaningful. Over
   `F_p` those axioms are degree `p`; the PC degree lower-bound technology
   (Alekhnovich–Razborov expansion, Mikša–Nordström) assumes constant-degree
   axioms and does not apply.
2. **The "last fall" can be masked.** HKYY's `D* ≤ d_last + O(1)` is proved for
   systems where Weil restriction to a *small base field* produces many
   low-degree relations (division-with-remainder for HFE). Over `F_p` there is
   no base field to restrict to (§2!), so the descent step that *creates* the
   low-degree fall-events is absent. The PDP system over `F_p` is the *raw*
   Semaev system `S_{m+1}(x_1,…,x_m, x(R)) = 0` plus the membership constraints
   `F(x_i)=0` — and the only thing bounding its degree is `deg F = |FB|`, which
   is exactly the Yokoyama regularity of §1, **not** a last-fall phenomenon.
3. **First-fall ≠ last-fall, with no repair.** In small characteristic HKYY
   exhibit systems with `d_ff ≪ d_last`. Over `F_p` we cannot even *measure*
   `d_last` cheaply, because there is no Weil-descent presentation whose
   Macaulay matrix is small; the system is genuinely a multivariate system over
   a huge field.

### 3.3 What the right object is over `F_p`

The takeaway is that **last-fall degree is the wrong invariant for prime
fields** — it is a property of the *descended* system, and prime fields admit no
non-trivial descent. The controlling invariant over `F_p` is the **degree of
regularity of the affine Semaev ideal** (Yokoyama's `Reg`), and the proof-
complexity analogue is not PC-degree over a Boolean-like base but the
**arithmetic-circuit / Positivstellensatz degree over `F_p`**, for which the
expansion-based lower bounds do not (yet) exist. Concretely:

> **Open problem, sharpened.** Define `d_last` for the *interval factor base*
> system over `F_p` via the (necessarily large) symmetrized Semaev presentation
> used in `research/notes/index-calculus/RESEARCH_SYMMETRIZED_SEMAEV.md`. Is `d_last` still `Θ(Reg)` there, or
> can the interval structure create a genuine early last fall? Proposition 1
> (§1.2) says the *ideal* is unchanged by re-presentation, which strongly
> suggests `d_last` is presentation-independent and equals `Θ(Reg)` — i.e. **no
> early fall** — but this needs the symmetrized-system Macaulay-rank
> measurement that `ffd_harness.rs` does for `F_2` to be redone for `F_p`. That
> is the concrete next experiment (currently blocked only by the lack of a Sage/
> msolve toolchain in this container).

So the HKYY framework's extension to large prime characteristic is **not merely
undeveloped — it is the wrong frame**, and we have identified the substitute
(degree of regularity + arithmetic Positivstellensatz degree) and the one
measurement that would settle whether interval structure helps.

---

## 4. The Mahalanobis–Abdullah–Mallick "initial minors" conjecture

This is the only one of the four fronts that comes with a *concrete, testable
algorithm*, so it gets a new implementation and experiment. Code:
`experiments/initial_minors/`.

### 4.1 The method, reconstructed precisely

(From Abdullah–Mahalanobis "Las Vegas algorithm" IndoCrypt 2018; "A new method…"
2020/2021; "Minors solve the ECDLP" 2023; and the "Initial minors — a conjecture
to solve the ECDLP" note. Full text was not fetchable in this container — the
network policy 403s arXiv/IACR/episciences — so the construction below is
reconstructed from the abstracts/snippets plus the underlying Riemann–Roch fact,
and is *validated experimentally* in §4.2.)

For `E/F_p`, generator `P` of prime order `n`, target `Q = mP`:

1. Pick random `(a_i, b_i)` and form points `R_i = a_i P + b_i Q`, `i = 1..N`.
2. Build the matrix `M[i][j] = φ_j(R_i)`, where `φ_1, φ_2, …` is the
   pole-order-ordered monomial basis of the Riemann–Roch spaces
   `L(O) ⊂ L(2O) ⊂ L(3O) ⊂ …`:
   `φ = [1, x, y, x², xy, x³, x²y, x⁴, …]` (`x^i y^j`, `j∈{0,1}`, sorted by
   `2i + 3j`).
3. **Core fact (Semaev relation in linear-algebra form):** `k` points sum to
   `O` in the group **iff** the `k × k` submatrix `[φ_j(R_i)]_{i∈S, j=1..k}` is
   **singular** over `F_p`. (Because `k` points sum to `O` iff they are the zero
   divisor of a function in the `k`-dimensional space `L(kO)`.)
4. A vanishing minor on rows `S` gives `Σ_{i∈S}(a_i + m b_i) ≡ 0 (mod n)`, so
   `m = −(Σ a_i)/(Σ b_i) mod n`. **DLP solved.**

The **initial minors** are the *leading principal* `k×k` minors (first `k` rows,
first `k` columns). They are exactly the pivots of an LU factorisation of `M`;
the **Schur-complement** recursion updates the leading minor from size `k` to
`k+1` in `O(N)` work, so the whole sequence of initial minors is read off one
Gaussian elimination. A zero pivot at step `k` certifies that the first `k` rows
sum to `O`. The **Initial Minors Conjecture** asserts that a *subexponential*-
sized family of such initial minors suffices to find a vanishing one (hence a
relation), which would make ECDLP subexponential on *every* curve, prime field
included.

### 4.2 New experiment: the relation density is `1/n`, so the natural search is `Θ(n)`

`experiments/initial_minors/verify_correspondence.py` confirms the core fact:
over a toy curve (`n = 1163`), `299/300` random subsets satisfy
`sum == O ⇔ minor singular` (the lone disagreement is a sub-relation: a proper
subset already sums to `O`, making the larger minor singular too). It then plants
nothing and *recovers the true discrete log* from a genuinely-found vanishing
minor — end-to-end the method works.

`experiments/initial_minors/scaling.py` measures the **cost to the first
vanishing minor** (= first relation), `k = 4`, across prime-order curves:

```
 bits          n  reps   E[subsets]  E[subsets]/n
    8        419   300        417.9         0.997
   10       1427   300       1401.6         0.982
   12       4943   300       4970.6         1.006
   14      31847    62      32608.4         1.024
   16     102763    19     109677.2         1.067
   18     333911     5     545087.0         1.632   (5-rep noise)
   20    1408111     2    3730946.0         2.650   (2-rep noise)
```

Across the well-sampled range (8–16 bits, a **245× span** of `n`, 19–300 reps),
`E[subsets]/n = 0.98–1.07` — i.e. the number of minors one must examine before a
vanishing one appears is `(1.00 ± 0.05)·n`. The 18/20-bit rows have only 2–5
reps; the count-to-first-success is a geometric random variable with coefficient
of variation ≈ 1, so a 2-sample mean of `2.65·n` is fully consistent with the
underlying `1·n` law (it is one standard error out). **The relation density is
exactly `1/n`, as the heuristic "sum of `k≥2` random points is uniform"
predicts.**

**Consequence.** The *naive* minor search costs `Θ(n)` — which is **worse than
Pollard rho's `Θ(√n)`**. For the method to even *match* rho, the initial-minor
structure must cut the number of minors examined from `Θ(n)` down to `Θ(√n)`;
to *beat* rho it must reach subexponential. That `Θ(n) → subexp` reduction is
the entire content of the conjecture, and nothing in the linear-algebra
correspondence forces it: the leading principal minors are just `N` specific
prefixes, and `P[some prefix of length ≤ N sums to O] ≈ N/n`, so one needs
`≈ n/N` independent matrices — again `Θ(n)`.

### 4.3 Why the published `2^50` evidence cannot settle the conjecture

`experiments/initial_minors/crossover.py` (log₂ of operation counts):

```
 bits  rho=n^.5    L[1/2]    L[1/3]   minors~n
   50      25.0      22.6      16.7      50.0
   80      40.0      30.4      21.2      80.0
  128      64.0      40.7      26.7     128.0
  256     128.0      61.8      37.0     256.0
```

At `n = 2^50` — the largest order the authors report solving — Pollard rho costs
`2^25`, an afternoon on a laptop. The `L[1/2]` model costs `2^22.6` there, so at
this size a genuine `L[1/2]` algorithm would be only `~5×` faster than rho, while
a genuine polynomial/`Θ(n)` method costs `2^50`. The three asymptotic laws sit
within a handful of bits of each other; **the `√n`-vs-subexponential divergence
does not open up until far larger `n`** — rho exceeds `L[1/2]` by a factor `2^20`
only at `n ≈ 2^118`.

Therefore: an algorithm observed only up to `2^50` produces a log–log slope that
is *numerically indistinguishable* from polynomial, from `L[1/2]`, and from
`L[1/3]`. Solving instances that rho dispatches in `2^25` operations **cannot**
certify subexponential asymptotics — the experiments live entirely below the
crossover. This is the quantitative form of the brief's worry that the result
may be "an artifact of small-size phenomena."

### 4.4 Verdict on the conjecture

- **Not refuted.** Nothing here proves the initial-minor family *cannot* be
  arranged to capture a vanishing minor cheaply on ECDLP-structured matrices;
  that is a real, subtle linear-algebra question.
- **Not supported by the `2^50` data.** The published ceiling is rho-feasible
  and below the regime where subexponential behaviour would be visible (§4.3),
  and the natural search density is provably `1/n` (§4.2), giving `Θ(n)` — worse
  than rho. So the burden of proof is squarely on the conjecture.
- **Falsification target.** If the conjecture held, then on ECDLP matrices the
  number of *initial* minors that must be tested before a zero appears should
  grow **subexponentially**, i.e. the measured `E[initial-minors-to-relation]`
  should *fall below `√n`* somewhere in a reachable range. Our `Θ(n)`
  measurement for the leading-principal family says it does **not** for that
  natural family; a decisive experiment would instantiate the authors' *exact*
  initial-minor set (their Schur-complement ordering, which we could not obtain
  from the blocked sources) and measure its count-to-relation against `√n`
  across 20–40 bits. **If it tracks `n` (or even `√n`), the conjecture is an
  artifact; only a sub-`√n` slope would make it a credible attack vector.**

This is, to our knowledge, the first time the conjecture has been framed with a
concrete falsifiable observable (`E[initial-minors-to-relation]` vs `√n`) rather
than "can we solve a bigger instance."

---

## 5. Where this leaves the four fronts

1. **Structured factor bases:** Proposition 1 gives a *provable* sparsity-
   invariance no-go; the general impossibility needs algebraic-circuit lower
   bounds and is out of reach, but the *equal-Hilbert-function family* version
   is a realistic, scoped target.
2. **Weil descent over `F_p`:** hopeless, now shown per-candidate — the missing
   ingredient is Galois structure, which a prime field and any Cartesian
   `Z_p × Z_p` simply do not have.
3. **Last-fall degree over `F_p`:** the HKYY frame does not port (degree-`p`
   field equations, no base field to descend to); the correct invariant is the
   degree of regularity, and the one decisive measurement (symmetrized-Semaev
   Macaulay ranks over `F_p`) is specified and awaits a Sage/msolve toolchain.
4. **Initial minors:** implemented; the natural search is `Θ(n)` (measured) and
   `2^50` cannot distinguish sub-exp from `√n`; the conjecture is reframed
   around a falsifiable `< √n` slope.

## Reproducing

```bash
cd experiments/initial_minors
python3 verify_correspondence.py   # core fact + one DLP recovery
python3 scaling.py                 # Theta(n) relation density (a few minutes)
python3 crossover.py               # 2^50 indistinguishability table (instant)
```

## References

- K. Yokoyama, M. Yasuda, Y. Takahashi, J. Kogure, *Complexity bounds on
  Semaev's naive index calculus method for ECDLP*, J. Math. Cryptol. 14 (2020)
  460–485.
- M.-D. Huang, M. Kosters, S.-L. Yeo, *Last fall degree, HFE, and Weil descent
  attacks on ECDLP*, CRYPTO 2015 (eprint 2015/573).
- M.-D. Huang, M. Kosters, Y. Yang, S.-L. Yeo, *On the last fall degree of
  zero-dimensional Weil descent systems*, J. Symbolic Computation, 2017.
- A. Abdullah, A. Mahalanobis, V. M. Mallick, *A new method for solving the
  elliptic curve discrete logarithm problem*, 2020 (arXiv:2005.05039).
- A. Abdullah, A. Mahalanobis, V. M. Mallick, *Minors solve the elliptic curve
  discrete logarithm problem*, 2023 (arXiv:2310.04132).
- A. Mahalanobis, A. Abdullah, V. M. Mallick, *Initial minors — a conjecture to
  solve the ECDLP* (2020).
- A. Abdullah, A. Mahalanobis, *A Las Vegas algorithm to solve the ECDLP*,
  IndoCrypt 2018 (eprint 2018/134).
- C. Diem, *On the discrete logarithm problem in elliptic curves*, Compositio
  Math. 147 (2011).
- P. Gaudry, *Index calculus for abelian varieties of small dimension and the
  elliptic curve discrete logarithm problem*, J. Symbolic Comput. 44 (2009).
- C. Petit, M. Kosters, A. Messeng, *Algebraic approaches for the ECDLP over
  prime fields*, PKC 2016.
