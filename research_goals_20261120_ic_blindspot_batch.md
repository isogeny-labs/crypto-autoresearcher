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
   tuple counts match λ = |B|^m/#G within [0.86, 1.06]; the naive *fraction*
   formula min(1, |B|^m/p) requires the m!-ordering (Poisson) correction,
   after which ratios are 0.94–1.13. This charges the G30 relation-rate
   heuristic geometrically at tested scope, including the correction term
   the raw heuristic omits.
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
is the *only* structural fact prime fields have that F_{2^n} lacks. The one
genuinely structured factor base in the published literature comes from that
side: lift E/F_p to Ẽ/Q, take the factor base from low-height points of
Ẽ(Q) (Flannery–Lenstra–Wesolowski, *Low points on elliptic curves and
class groups*: heuristically #{P : ĥ(P) ≤ c} grows like (log p)^{c+1}), and
decompose the lift of the target. Height supplies what no x-line geometry
supplies over F_p: an **ordering** on candidate base points. This program has
never touched it: the 2026-09-26 review has zero hits for rational-point /
height / characteristic-0 lifting as an attack axis, and the 14 "Mordell"
findings in `knowledge/` are Iwasawa-theory corpus entries, not attack records.

**Design decision (house rule): staff the barrier, not another negative
experiment.** The expected wall is known in advance — supply (log p)^{c+1}
against the n ≈ p^{1/2} requirement, and rank Ẽ(Q) unbounded-but-tiny — so a
decomposition experiment would be the 762nd predictable null. What has value:

- **Theorem arm (primary):** state and prove a *scoped closure certificate*:
  for any lift Ẽ/Q of the given E/F_p (any integral model, any choice of base
  defined by height ≤ c(log p)), the number of usable low points available to
  the decomposition engine at height budget c is O((log p)^{f(c)}) — hence
  relation density is inverse-polynomial in p at every fixed m, hence
  characteristic-0-lift factor bases are super-polynomially sub-rho at every
  height budget polynomial in log p. Conditional on FLW's conjecture, this
  must be stated with the conjecture *named as a dependency*, and the
  unconditional weak-supply variant (what is provable with known
  average-results, e.g. via average rank / parity results) stated separately
  at its own strength. A conditional barrier with named dependencies is
  admissible evidence for *this lane only*; it may not be promoted across the
  D1–D3 family.
- **Measurement arm (one cell, confirming):** at 20–24 bits, enumerate low
  height budgets on 2–3 models of toy curves, fit the supply exponent against
  the FLW prediction, and verify the *scoping* of the barrier — i.e. check no
  height budget ≤ 6 gives a base large enough to reach even toy relation
  rates. This cell validates the theorem's hypotheses against practice; it
  claims nothing else.
- **Escape hatch (the honest loophole probe):** the model-dependence of the
  lift. Different integral models of the same reduction give different
  Mordell–Weil groups; record whether any model family with unusually small
  regulator/torsion-free rank interplay produces supply deviating from the
  fitted law. If one exists, it is the successor goal; if none does across
  the sampled models with fresh held-out models, that null is part of the
  closure certificate.

**Falsification / kill criteria:** the barrier is refuted (scoped, at tested
tier) if any sampled model at any tested size reaches the G30-010 alive
criterion yield with a height-budget base; the theorem arm fails if the FLW
dependency cannot be stated crisply, in which case only the measurement cell
survives and it is filed as census, not barrier.

**Novelty screen:** the 2024–2026 line implementing decomposition algorithms
over E(Q) (Bochníček–Degot–Futamura–Johnston and successors) must be read
first — if any of them already proves a supply non-existence of the scoped
form, this goal collapses into a KN-LIT entry with a pointer. That screen is
the first work package, not an afterthought.

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
