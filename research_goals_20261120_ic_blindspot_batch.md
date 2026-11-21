# Research Goals 2026-11-20 — Index-calculus blind-spot batch: five suspiciously ignored ideas

**Date anchor:** 2026-11-20

**Status:** Planning record. Five proposals, one of them a literature-reading
gate that must run before the others are staffed. **Nothing here is evidence.**
No experiment was run, no hypothesis status changed, no decision record was
written. All five proposals are subject to the standing NoveltyGate rule
(G30-028) before any "novel" label, and none may be dispatched as an attack
probe until it clears G30-001 cost gating.

**Input:** operator question of 2026-11-20 — *"any underrepresented ideas here
that we've completely ignored, suspiciously ignored from an index-calculus
perspective?"* — audited against the G30 program
(`research_goals_20260723.md`), the literature review of 2026-09-26
(`docs/ecdlp-literature-review-20260926.md`), `knowledge/`, and the corpus
index (`knowledge/sources.json`, 23k documents).

**Precedent for this batch format:** `research_goals_20260831_coverage_gap_batch.md`
(external gap audit → verified ledger state → staff the residue).

---

## 0. Screening performed before writing this file

Every claim below of "ignored" was tested by grep across `knowledge/findings`,
`knowledge/leads`, `knowledge/open-problems`, `knowledge/frontiers`,
`docs/ecdlp-literature-review-20260926.md`, and by corpus-title search. The
audit was run *against the working tree at 2026-11-20*, not against memory.

| Idea | Corpus status (ingested?) | Program status (staffed?) | Verdict |
|---|---|---|---|
| Secant varieties / secant rank of elliptic normal curves | **Yes** — `KN-LIT-1861` (arXiv:2604.02046, *Secant rank and syzygies of projections of elliptic normal curves*, `citation_verified: read`) | **Zero** grep hits for `secant|Terracini` anywhere in findings/leads/open-problems/frontiers/literature-review | Ingested, never touched |
| Characteristic-0 / Mordell–Weil factor bases (FLW low points, heights, lifts to Q) | Partially — 14 findings match "Mordell", all Iwasawa/number-theory corpus entries; "Hensel" appears 6 times, never attack-side | **Zero** hits in the 2026-09-26 review for rational-point / height / char-0 lifting as an attack axis | Unstaffed |
| Large-prime variation | **Yes** — `KN-LIT-164` (Gaudry–Thomé–Thériault–Diem, ePrint 2004/153); cited once, in `KN-FIND-61347e` §genus-2 caveat | **Zero** G30 goals; no relation-search goal in the 05 RELATIONS cluster has a large-prime arm | Cited, never staffed |
| Fast computation of summation polynomials in **odd** characteristic | Partially — symmetrized variants (`faugere_huot_joux_renault_vitse_2014_symmetrized`), Gröbner-free evaluation (`mcguire_mueller_2017_grobner_free`), Trimoska 4th-summation benchmark freeze (`SRC-ICPERF-TRIMOSKA-ECICB-2024`). **No** Patault–Plesis record in the corpus | Zero goals on the polynomial-computation and per-candidate evaluation-cost axis | Unstaffed; external char-2 breakthrough not even ingested |
| Diem's obstruction / non-existence side (Compositio Math. 147 (2011) and ANTS 7(6) (2013)) | **Yes** — `KN-LIT-003`, `KN-LIT-65f76d` | Records exist but are **abstract-depth only**: `KN-LIT-65f76d` states "Only the bibliographic record and the abstract … were read" and relays only the subexponentiality range; the correspondence/obstruction content (§4–§5 of Diem II) has never been read into any finding or barrier | The load-bearing half of a paper we already own has never been read |

This is exactly the failure shape the 2026-08-31 batch documented, mirrored:
that audit found external reviewers claiming as absent what the ledger held;
this one finds the program holding records it never opened.

---

## G31-001: Decomposition length as secant rank — dictionary, Terracini instrument, and a second instrument for D2

**Cluster:** 03 MONODROMY (shared ownership with G30-009) / new geometric sub-lane.
**Type:** measurement + barrier-instrument proposal. **Depends on:** G30-004 (measurement arm), G30-007 outputs (dictionary validation). **Gates:** provides an independent instrument for G30-009 (D2).

**The idea.** Fix an embedding φ_L : E → P^r by a complete linear system L of
degree r+1 (for the plane model, L = O(3·O), r = 2). The statement
"Q = P₁ + … + P_m with all P_i in a base B" has a direct geometric reading:
the point φ_L(Q) lies on an (m−1)-secant P^{m−1} meeting φ_L(E) in points
above B. `KN-LIT-1861` studies exactly the relevant invariant — the **secant
rank** of a point with respect to a projected elliptic normal curve — and
bounds the Green–Lazarsfeld syzygy index in terms of it. The dictionary claims:

1. The Semaev decomposition problem for embedding L is the problem of upper-
   bounding the secant rank of φ_L(Q) with respect to φ_L(B), and the
   expected dimension of the length-m decomposition variety is the classical
   expected dimension of the m-secant variety Σ^m (join formula), i.e. the
   n^m/p relation-rate heuristic **is** the secant dimension count.
2. Non-generic relation rates ⇔ unexpected components / defectivity of the
   relevant secant construction for the chosen embedding and base geometry.
   This is the geometric face of what G30-007/008/009 measure arithmetically
   as summation-cover monodromy: monodromy is the Galois shadow, secant
   defectivity is the variety-theoretic object casting it.
3. Terracini's lemma gives a **rank test on a small matrix of derivatives**
   for the tangent/first-secant defect at general points — strictly cheaper
   than the Chebotarev census (G30-007) and the resolvent test (G30-008), and
   independent of both.

**Validation hook (the cheap killer test).** Re-derive a known phenomenon, not
a new one: for binary subfield curves under Weil restriction, the image of the
restricted surface in the Jacobian's projective space is classically the
defective-secant case (this is *why* descent index calculus works), while for
generic prime-field curves the secant dimension counts are expected. If the
dictionary reproduces that dichotomy at toy scale, the instrument is real; if
it cannot, it is decoration and gets archived.

**Test boundary / scope:** Toy tier only — the existing 8–20 bit ladder and
G30-026 curves; embeddings r ∈ {2, 3, 5}; m ≤ 4. Secant-rank strata measured
by exact linear algebra over F_p; Terracini ranks computed at ≥ 3 curve
models per size. Green–Lazarsfeld-style indexing is *not* to be computed —
only referenced as the reason the strata are the right invariant. No claims
above toy tier; no crypto-scale extrapolation (G30-003 protocol applies).

**Falsification / kill criteria:** (a) the dictionary fails to reproduce the
char-2-defective vs prime-expected dichotomy on known cases → instrument
invalid, archive; (b) Terracini-rank deviations on structured bases
(G30-010 geometries) show no correlation with measured decomposition yields
across the ladder → the geometric and arithmetic instruments are decoupled,
close the lane and record the decoupling as evidence for G30-009; (c) any
positive correlation must replicate against G30-007 monodromy outputs on the
same curves before it may be cited for D2.

**Novelty screen (NoveltyGate, pre-run):** classical secant-variety theory of
elliptic normal curves (Castelnuovo bound tradition); secant varieties of
elliptic curves in the additive-combinatorics literature (sumset growth on
curves — check this specifically, it is adjacent and unread); `KN-LIT-1861`
itself (syzygy-side only; it does not touch relation rates). The claimed new
object is only the *dictionary to relation-rate heuristics and its use as an
IC instrument*, and that claim is provisional until the screen is run against
the additive-combinatorics literature.

**Screen result (2026-11-20, partial).** Two prior-art families must be
screened before the charter comparison is read as a claim about x-window
bases: (i) **Petit–Kosters–Messeng-style prime-field factor bases defined by
preimages of small-degree rational maps** — McGuire–Mueller (`eprint
2017/1262`, in corpus) describes this as "the first working case for curves
defined over prime fields", which means the x-window base is *not* the only
structured prime-field base and a charter result about x-windows does not by
itself characterize "structured bases" in general; (ii) the public
`ebarschkis/SemaevSummationPolynomials` package, which enforces explicit
prime-field factor-base coordinate sets and could serve as an independent
implementation for the geometric arm. The pilot's generic-set null remains a
valid null for *x-window vs unstructured*, and its finding (4/8 cells, both
directions) stands as measured; what is withdrawn is any implication that
"generic sets" exhaust the structured alternatives.

**Pilot outcome (2026-11-20, same day, unreviewed):** validation hook executed
at toy tier; artifacts archived at
`notes/g31-001-terracini-pilot-20261120/` (scripts, frozen config, results).
Three findings, one correction:

1. **Correction (load-bearing).** The dictionary as stated in item 1 above is
   *false in its literal form*: for the degree-6 embedding, containment sees
   −ΣPᵢ, and the containment statement only becomes exact at embedding degree
   d = m+1 (residuals of degree ≥ 2 are base-point-free on genus 1 — the
   literal m=3/d=6 test failed its own controls, 0/400, as the theory now
   predicts). The **correct dictionary**: `φ_{m+1}(−Σ Pᵢ) ∈ span(scheme
   columns of φ_{m+1}(Pᵢ))`. Verified 3881/3881 witnesses, 4500/4500 residual
   containments, zero converse violations.
2. **Dimension count confirmed as the supply predictor:** mean decomposition-
   tuple counts match λ = |B|^m/#G within [0.86, 1.06]; the *fraction* formula
   min(1, |B|^m/p) requires the m!-ordering (Poisson) correction, after which
   ratios are 0.94–1.13. **Cross-reference, so this is not over-read:** the
   program already carries the m! factor in its own yield statements
   (`KN-FIND-c93d45`: yield ≤ B^m/(m!N); `KN-FIND-d4f820`: same with an
   O(C^m B^{m/2}/N^{...}) error term). The pilot's contribution is therefore
   *confirmation at geometric scope*, not a new correction to program claims;
   the earlier chat-level suggestion that the m! factor might silently affect
   existing G30 predictions is withdrawn — the ledger has it.
3. **Charter test answered "differently":** x-window base decomposition rates
   fall outside 20-draw generic-set null bands in 4/8 informative cells, in
   **both directions**, with total tuple supply ≈ invariant — a genuine,
   small, curve-dependent sumset-structure signal. This is the alive signal
   G30-010 was looking for, seen from the geometric side; it is not yet a
   law and does not survive promotion.
   Successor (to be staffed by Coordinator, not implicitly): (a) replicate the
   charter signal with a frozen larger null and ≥ 8 curves per cell;
   (b) run the unexecuted char-2-defectivity arm (the dictionary's other
   dichotomy); (c) the G30-007 cross-check before any D2 citation.
   Scope stays toy (p ≤ 2^20, m ≤ 5); the m=5 rate cell was frozen too sparse
   to inform and is recorded as such.

---

## G31-002: Characteristic-0 supply barrier — no Mordell–Weil lift yields sub-rho factor-base supply

**Cluster:** 08 BARRIERS (fourth arm beside D1/D2/D3).
**Type:** barrier theorem + one measurement cell. **Depends on:** G30-025 (registration), G30-022 pattern (proof-first, one confirming cell).

**The idea.** F_p is not just a finite field: it is the reduction of Z, and it
is the *only* structural fact prime fields have that F_{2^n} lacks. A
structured factor base that exploits this side: lift E/F_p to Ẽ/Q, take the
factor base from points of Ẽ(Q) of bounded height, and decompose the lift of
the target. Height supplies what no x-line geometry supplies over F_p: an
**ordering** on candidate base points. This program has
never touched it: the 2026-09-26 review has zero hits for rational-point /
height / characteristic-0 lifting as an attack axis, and the 14 "Mordell"
findings in `knowledge/` are Iwasawa-theory corpus entries, not attack records.
(The published Isogeny Labs note `notes/index-calculus-three-settings.html`
likewise frames the prime-field case as "the algebra has nowhere to hide" and
does not consider the characteristic-0 side — so this is a blind spot in the
public framing as well as the internal one.)

**Design decision (house rule): staff the barrier, not another negative
experiment.** The expected wall is known in advance — bounded-height point
supply against the n ≈ p^{1/2} requirement, and rank Ẽ(Q) unbounded-but-tiny
— so a decomposition experiment would be the 762nd predictable null. What has
value:

- **Theorem arm (primary, and better than first drafted):** the supply bound
  does *not* need a heuristic. Masser (*Counting points of small height on
  elliptic curves*, Bull. SMF 117 (1989)) gives effective upper bounds on the
  number of points of bounded canonical height over any extension of bounded
  degree; Dujella (*Uniform bounds for the number of rational points of
  bounded height*, Acta Arith. 2024) gives the uniform bound
  exp(C log B / log log B) for curves with rational ℓ-torsion (ℓ = 2 over Q),
  following Bombieri–Zannier and Naccarato. So the scoped closure certificate
  can be stated unconditionally: for a fixed height budget B = (log p)^c, the
  usable base has at most exp(C log B / log log B) = (log p)^{O(1)} points —
  polylogarithmic in p — hence relation density at fixed m is
  at most (log p)^{c'm}/p, inverse-polynomial, hence no sub-rho advantage at
  any height budget polynomial in log p. Two honest caveats to state in the
  theorem: (i) Masser/Dujella bounds are upper bounds — they *are* the
  supply side, so this direction is sound; (ii) reaching n ≈ p^{1/2} points
  requires B = exp(Θ((log p)(log log p))) — a power of p, not a polylog — so
  the "low height" premise fails quantitatively, and the theorem must say
  that explicitly rather than only bounding the base. **Citation hygiene:**
  the author line "Flannery–Lenstra–Wesolowski, *Low points on elliptic
  curves and class groups*" used in the first draft of this goal is an
  unverified recollection and is **withdrawn**; it must not be cited until the
  paper is located and read. The verified supply literature is Masser 1989,
  Dujella 2024, and Krumm (*Computing points of bounded height*, Math. Comp.
  2015) for the enumeration side.
- **Measurement arm (one cell, confirming):** at 20–24 bits, enumerate
  points of bounded height on 2–3 integral models of toy curves via a
  Krumm-style bounded-height enumeration, fit the supply exponent, and verify
  the *scoping* of the barrier — i.e. check no height budget that stays
  polylogarithmic gives a base large enough to reach even toy relation rates.
  This cell validates the theorem's hypotheses against practice; it claims
  nothing else.
- **Escape hatch (the honest loophole probe):** the model-dependence of the
  lift. Different integral models of the same reduction give different
  Mordell–Weil groups; record whether any model family with unusually small
  regulator/rank interplay produces supply deviating from the fitted law. If
  one exists, it is the successor goal; if none does across the sampled
  models with fresh held-out models, that null is part of the closure
  certificate.

**Falsification / kill criteria:** the barrier is refuted (scoped, at tested
tier) if any sampled model at any tested size reaches the G30-010 alive
criterion yield with a polylog-height base; the theorem arm fails if the
Masser/Dujella bounds cannot be transplanted to the scoped statement (e.g.
degree-growth or effectivity problems), in which case only the measurement
cell survives and it is filed as census, not barrier.

**Novelty screen (first work package):** the recent line implementing point
decomposition over E(Q) and bounded-height enumeration must be located and
read — if any of it already proves a supply non-existence of the scoped form,
this goal collapses into a KN-LIT entry with a pointer. A Crossref/arXiv
search for bounded-height decomposition implementations returned nothing
load-bearing beyond the enumeration literature above; the earlier draft's
"Bochníček–Degot–Futamura–Johnston" author line was **unverified and is
withdrawn** — the exact bibliographic identity must come from the screen, not
from this document.

---

## G31-003: The large-prime variation, armed for prime-field engines

**Cluster:** 05 RELATIONS.
**Type:** measurement (extends G30-014) + one engine modification cell. **Depends on:** G30-014 (counting law), G30-001 (charging).

**The idea.** `KN-LIT-164` (double large prime) is in the corpus, and its only
appearance in program knowledge is a genus-2 caveat in `KN-FIND-61347e`.
Historically it is where the only *practical* index-calculus constant wins
live — converting "all m coordinates B-smooth" into "m−2 smooth, two
coordinates above B that must pair-match" changes the relation-rate exponent
at fixed base size. Every engine in the 05 RELATIONS cluster (Semaev x-line
bases via G30-026, split-Jacobian via G30-015, cyclic-cover labels via
G30-013) charges a full-smoothness density. If G30-014's "exact relation-
count law" is a pure-smoothness law, the program's own counting instrument is
systematically pessimistic relative to what an IC practitioner would deploy —
an uncharged axis of precisely the kind G30-001 exists to police.

**Scope.** (i) Extend the B1 enumerator calculus to count double-large-prime
relations (pairing condition = a curve/surface condition on the two free
coordinates; its geometry must be stated, not waved at — this is the same
"special linear systems" object as Diem–Kochinke, `KN-LIT` record pending,
and the Faugère–Huot–Joux–Renault–Vitse symmetrized variant is the char-2
precedent in-corpus). (ii) Measure the yield-ratio and the *net* cost on the
G30-026 ladder: extra pair-matching cost charged in GOE, relation-probability
gain measured, verdict only as a fully-charged ratio. (iii) Explicit negative
control: if the pairing condition has no rational structure over prime fields
(the honest fear — subfield-vector-space factor bases are what make the
binary large-prime work), that is a scoped KN-FIND closing the variant *for
this family*, which is still a new closure certificate, not a wasted cell.

**Falsification / kill criteria:** fully-charged ratio ≥ 1 at every ladder
rung with the pairing cost charged → closed-scoped; a rung with ratio < 1 →
scaling study gated through mandatory independent review, same as G30-013/015
positives.

**Formulation sketch (so WP1 can start from equations, not vibes).** Over a
prime field with base B = {P : x(P) < N} and target Q ∈ ⟨P⟩, the standard
m-relation density is ρ_m = |B|^m/(m!·#G) (the repo's own statement, e.g.
`KN-FIND-c93d45`). The double-large-prime variant fixes a second window
L = {P : N ≤ x(P) < N'} with |L| = κ|B| and asks for Q = A₁+A₂+C₁+C₂ with
A_i ∈ B, C_i ∈ L, |C₁|,|C₂| ≥ 1. Then:

- Density: ρ_{2LP} ≈ |B|²|L|²/(#G) · (ordering factors) — a gain of κ² relative
  to the 4-in-B density, at the price that only the A_i contribute matrix
  columns (the C_i are matched, not logged).
- Pairing cost: a table of L+L pairs costs ~|L|² additions to build (one-time
  per base) and O(1) lookup per candidate; matching requires
  Q − (A₁+A₂) ∈ L+L, i.e. a second pair table over B+B of size |B|². Net
  candidate cost ≈ |B|² table lookups per relation attempt, so the charged
  cost per relation is (1/ρ_{2LP})·(|B|² + |L|²) additions against
  (1/ρ_m)·|B|^m for the plain engine — the ratio decides.
- The honest structural question for prime fields: L+L has ~|L|²/2 distinct
  sums, but the matching condition needs *collisions between two structured
  sets*, and unlike the binary subfield-vector-space case there is no
  linear-algebra mechanism forcing those collisions. If the L+L vs B+B
  intersection behaves like two random sets of the same sizes, the gain is
  exactly κ² and the cost is κ²·lookup — a wash; any deviation in either
  direction is the empirical content of the cell.

This is deliberately written so a null ("random-set behaviour, wash") is a
clean closure certificate and a positive is a measurable κ²-scale effect.

**Novelty screen:** Gaudry's original large-prime-for-ECDLP formulation and
the Diem–Kochinke special-linear-systems line must be screened first; the
claimed contribution is the *prime-field counting law under the B1 calculus*,
not the variation itself.

---

## G31-004: Odd-characteristic summation-polynomial census and evaluation-cost curve

**Cluster:** 02 GROEBNER / 09 HARNESS.
**Type:** infrastructure + standalone measurement. **Depends on:** G30-025, Sage environment capture. **Gates:** de-risks every m=4 cell in G30-006 and G30-026 by providing independently validated polynomials.

**The idea.** The external state of the art moved and the corpus did not
notice: Patault–Plesis (2023) compute the 3-summation polynomial via modular
forms on the Galois orbifold, breaking a 20-year computation bottleneck —
**in characteristic 2 only**, by their own statement. Zero corpus hits.
Meanwhile the published record contains no S₄ (or S₅) over a moderate
prime field, and this program's m=4 cells rest on self-computed polynomials
with no external check. Two deliverables:

1. **Census (mathematical, publishable standalone):** explicit S₃ and S₄ over
   short-Weierstrass prime fields via the Diem-style resultant recursion, at
   a generic curve (parameters as coefficients) plus 3 concrete curves at
   ~2³¹; monomial counts, coefficient heights, symmetry-reduced (S_m-quotient)
   forms cross-checked against the in-corpus symmetrized-polynomial
   machinery; brute-force decomposition agreement checks at small p (verify
   S₃(x₁,x₂,x₃)=0 ⟺ 3-sum relation, ≥ 10⁶ random trials per curve).
2. **Evaluation-cost curve (instrument):** per-candidate cost of
   S₃/S₄ evaluation over F_p (p ~ 2³¹, cache-resident) as a function of
   representation and precomputation strategy, calibrated so G30-001's GOE
   ledger can charge relation search honestly instead of assuming the
   group-operation cost dominates. `mcguire_mueller_2017_grobner_free` is the
   in-corpus anchor for the Gröbner-free evaluation line; this goal measures
   what it implies at prime characteristic.

**Scope:** m ≤ 4 for the explicit census (m=5 is a stretch row, declared
provisional); odd characteristic only — the char-2 side is deliberately left
to the Patault–Plesis line, cited not re-done.

**Falsification / kill criteria:** none scientific — this is instrumentation;
the failure mode is engineering (S₄ explicit form too large to publish in
generic form), handled by falling back to per-curve specialization, recorded
as such.

**Novelty screen:** confirm the char-2-only claim of Patault–Plesis against
the paper itself (not the abstract), and screen 2024–2026 ePrint for
odd-characteristic summation-polynomial computation before claiming the
census is new. Ingest both into KN-LIT regardless of outcome — that part is
worth doing even if the census is scooped.

**Screen result (2026-11-20, partial; recorded before any novelty claim).**
The "no published S₄/S₅ over a moderate prime field" framing used to motivate
this goal is **over-claimed and is corrected here**: Faugère–Huot–Joux–
Renault–Vitse (EUROCRYPT 2014, `faugere_huot_joux_renault_vitse_2014_symmetrized`)
state that "the largest Semaev polynomial ever computed is the 6-th", with
symmetrized records up to the 8-th. McGuire–Mueller (`eprint 2017/1262`, in
corpus) also treat S₃–S₆ explicitly. So S₄ is *not* a first computation, and
this goal's defensible contribution narrows to: (i) **explicit universal
S₄ over ℤ[a,b] with three independent computations agreeing**, (ii) exhaustive
zero-set validation against F_{p²}-lift ground truth at odd characteristic,
(iii) the exact over-ℤ re-derivation of this repo's own `harness/semaev.py`
`s4_expr`, and (iv) the evaluation-cost curve (WP2). All four are
verification/instrumentation value, not a novelty claim. Two further prior-art
items surfaced and must be screened before any "first" language: the public
`ebarschkis/SemaevSummationPolynomials` SageMath package (exact point
decomposition with explicit prime-field factor-base coordinate sets,
char 2 and 3 included — direct prior art for any "exact prime-field
decomposition harness" claim) and the Petit–Kosters–Messeng line on
rational-map prime-field factor bases (prior art for factor-base geometry
claims, see G31-001 screen note). Neither is yet in the corpus.

**WP1 outcome (2026-11-20, same day, unreviewed):** census executed;
artifacts at `notes/g31-004-odd-char-census-20261120/` (scripts, universal and
per-prime polynomials, validation logs). Headline numbers:

- **Explicit universal polynomials over Z[a,b]:** S₃ = 13 monomials (total
  degree 4, deg 2/variable); **S₄ = 540 monomials (total degree 12, deg
  4/variable, 6 generators)**; per-prime support at (a=b=1, p ∈ {101,127,1009})
  is 439/625 monomials (70.2% of the degree-box). Three independent
  computations (Z-resultant→reduce, own Sylvester determinant over F_p,
  quadratic-resolvent closed form) agree coefficient-for-coefficient.
  Pipeline cost: ~16 s, <450 MB — the computation is *cheap*, which is itself
  a datum for the evaluation-cost question.
- **Validation: zero mismatches.** S₃ exhaustively at p=101 and p=127
  (≈3.1M tuples) against exact F_{p²}-lift ground truth; S₄ exhaustively over
  on-curve abscissae at p=101 (7.3M tuples). Off-curve mixed tuples disagree
  exactly on the predicted [2]-doubling sign branch — counted, not hidden.
- **Harness cross-check exact over Z:** `harness/semaev.py`'s `s4_expr(1,1)`
  equals the independently computed universal S₄ — the program's own m=4
  cells (G30-006, G30-026) now sit on externally re-derived polynomials,
  which was this goal's de-risking purpose.
- **Structure results:** exact S_m symmetry over Z; the diagonal restriction
  identity S₄(x,x,u,v) = (4f(x))²(u−v)²S₃(u,v,x∘[2]) (the (u−v)² factor is a
  formal-resultant leading-coefficient artifact — recorded because the naive
  prediction misses it, 1947/2000); independent collinearity-elimination
  re-derivation reproduces S₃² × diagonal junk with zero misses.
- **Brief correction:** S₂ in odd characteristic is x₁−x₂, not
  (f(x₁)−f(x₂))/(x₁−x₂) (the latter is the slope numerator); the repo and
  Semaev 2004 are right, the WP brief was wrong, documented in the report.

**Successors (Coordinator-staffed):** (a) WP2 — the evaluation-cost curve at
p ≈ 2³¹ for GOE charging (WP1 showed generation is cheap; evaluation per
candidate is the open cost axis); (b) reconcile against the frozen
`SRC-ICPERF-TRIMOSKA-ECICB-2024` fourth-summation benchmark using the now
Z-verified universal S₄ — a free consistency check on a frozen external
record; (c) the Patault–Plesis full-text novelty screen remains open; (d)
m ≥ 5 and 2-torsion diagonal branch unexercised, stated as gaps.

**WP2 outcome (2026-11-20, same day, unreviewed):** evaluation-cost curve
measured; artifacts at `notes/g31-004-wp2-evalcost-20261120/` (bench scripts,
`semaev_eval.py`, two full result JSONs). Headline numbers:

- **Sieve-mode cost (the ledger-relevant mode):** 245 ns/candidate for S₃ and
  433 ns for S₄ at p ≈ 2³¹ with window W = 384, decomposing exactly as
  `362 + 23517/W` ns — the parametric form a cost model needs. One-shot
  evaluation is 54 µs and pre-tabulated-power evaluation 31 µs; a numpy
  batched variant is 12 ns. **The same S₄ candidate ranges 12 ns → 54 µs
  across modes (≈4500×)**, so any quoted ns/candidate is meaningless without
  its mode; this is now the governing caveat on the whole cost axis.
- **Curve-shape effect, larger than expected:** on `y² = x³ + 7` (a = 0) the
  S₄ support collapses from 439 to **191 monomials** (and S₃ from 13 to 9) —
  every a-bearing term vanishes. Real prime-field targets are largely
  a ∈ {0, −3} curves, so cost tables computed at a = b = 1 overstate the
  inner loop roughly twofold. Recorded as a correction to how this program
  should quote Semaev evaluation costs.
- **Normalisation:** 0.25 (S₃) and 0.45 (S₄) Python-affine-group-op ratios —
  explicitly *not* a GOE conversion factor; must be re-measured in harness
  units. Reported with medians and IQRs; CPU pinning was refused by Mach
  (`KERN_NOT_SUPPORTED`), and between-run drift is reported (≤5.4% in
  sieve mode).
- **Scaling artifact identified:** the 2²⁰ → 2³¹ growth (1.6–2.0×) is a
  CPython 30-bit-limb boundary effect, not a log p law — cost is flat within
  a limb class (151 vs 146 ns) and steps at 2³⁰. In a 64-bit C core it should
  be constant. This matters because a naive fit of Python timings across the
  limb boundary would manufacture a spurious "cost grows with log p" term in
  any GOE ledger.
- Two internal bugs were caught and fixed before timing (F_{p²} oracle
  truncation; small-operand grids flattering multiplications), and each timed
  loop is verified value-for-value against a reference — recorded in the
  report rather than silently repaired.

---

## G31-005: Read Diem II's obstruction side — theorem-level closure test for the correspondence-transfer family

**Cluster:** 08 BARRIERS (serves 05 RELATIONS closure).
**Type:** literature-reading gate, deep adjudication, then either a barrier
import or a localized gap. **Depends on:** nothing; **pre-empts:** any further
staffing of correspondence engines after G30-013/G30-015.

**The idea.** The program is closing the auxiliary-cover / correspondence
family *empirically* — TRANSFER-NR-003..052, one negative experiment at a
time, with G30-013 and G30-015 as the last two open engines. Diem I
(Compositio 147, 2011) and Diem II (ANTS 7(6), 2013) are in the corpus
(`KN-LIT-003`, `KN-LIT-65f76d`) but **recorded at abstract depth only**; the
relief that the records carry is the subexponentiality range, while the
papers' correspondence/obstruction machinery — the conditions under which
their decomposition algorithms do *not* apply, and the structural reasons —
has never been read into any finding, barrier, or closure certificate.

**Work package 1 (one deep read, adjudication-grade per the 2026-09-26
"started but did not finish" backlog):** extract, statement by statement,
(i) the hypotheses their relation-density propositions need (their Condition
2.7-type ramification conditions), (ii) every contrapositive that applies to
prime fields (n = 1), (iii) exactly how their correspondence construction
differs from the bielliptic/Plücker/Prym/Kummer/Hesse/split-Jacobian engines
this program has tested. Output: a source-level KN-LIT upgrade of both
records from `abstract` to `read`, plus a one-page mapping table: engine ×
Diem hypothesis × satisfied/violated/unknown.

**Work package 2 (the payoff, conditional on WP1):** for every 05 RELATIONS
engine whose configuration violates a proved Diem hypothesis *for a reason
that provably obstructs its relation density*, the empirical negative is
upgraded to a theorem-scoped closure — the cheapest barrier in the program,
replacing remaining experiment budget with a citation. For every engine where
the mapping is "unknown", that unknown is the sharpest localized attack
surface in the cluster and gets a successor probe. Neither outcome is a null.

**Guard rails:** no import of any complexity claim without re-derivation of
the specific proposition at use-depth (the AGENTS.md literature-first rule;
`KN-FIND-61347e` precedent for treating abstract-depth citations as
non-load-bearing). Diem's theorems are for extension fields; any statement
transplanted to n = 1 must be re-proved, not quoted.

**Kill criteria:** if WP1 finds no proposition with prime-field contrapositive
force, record that explicitly — "Diem's machinery contains no free closure for
this family" — and the cluster's closure stays empirical. That record itself
protects against future re-proposal.

**WP1 outcome (2026-11-20, same day, draft):** the kill criterion fired.
Full-text extraction of both papers (Cambridge and MSP publisher PDFs, both
read at statement depth; the previously assumed arXiv posting for Diem II does
not exist — `KN-LIT-65f76d`'s identifier list should gain the MSP open-access
URL) is at `notes/diem-obstruction-extraction-draft-20261120.md`. Verdict:
**no proposition in either paper has prime-field contrapositive force.** The
strongest citable content is scope admission (Diem II p. 1283: Theorem 2 "does
not give a nontrivial result if q is set to p"), Condition 2.7 is vacuously
*satisfiable* at n = 1 (so it cannot obstruct there), and the only n = 1
phenomenon is a compression degeneracy of Diem's own factor base (it becomes
the whole group). Per this goal's guard rail, that negative is recorded as:
**the 05 RELATIONS correspondence closure stays empirical; no theorem import
is available from Diem I/II, and any future proposal citing "Diem proves an
n = 1 obstruction" is unsupported by these records.** The draft awaits
independent review before its KN-LIT records are promoted from abstract depth;
WP2 is closed-not-executed (no importable theorem exists).

---

## Sequencing and portfolio note

1. **G31-005 first** — pure reading, zero compute, and it can cancel or
   sharpen G30-013/G30-015 follow-ups and G31-003's engine arm before they
   spend anything.
2. **G31-004 in parallel** — instrumentation with standalone value and no
   dependency on the above.
3. **G31-001 next** — its validation hook (char-2-defective vs prime-expected
   dichotomy) is cheap and either founds a new instrument or closes a lane in
   one cycle; its outputs feed G30-009 (D2), not compete with it.
4. **G31-003 after G30-014's counting law lands** — the large-prime arm is an
   extension of that calculus, not a parallel one.
5. **G31-002 last** — theorem-first shape means it wants the D1/D3 proof
   machinery (G30-022/023) warmed up, and its novelty screen (the E(Q)
   decomposition line) needs the same reading budget as G31-005.

None of the five moves an exponent by itself. Together they close the known
blind spots of the G30 portfolio against the classical IC anatomy — geometry
of the secant picture, the characteristic-0 axis, the large-prime variation,
the polynomial-computation layer, and the theorem-side literature the program
owns but has not opened — and each is built to pay rent as a closure
certificate even in the expected-negative case, per the program's standing
logic.
