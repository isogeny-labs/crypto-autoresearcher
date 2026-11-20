# Cluster 12 — LIFT: Goal Draft G31-002

Theme: a characteristic-0 point-supply barrier, stated as a derivation artifact
before any further lift experiment is commissioned.
Claim tier: toy for the numerical arm; the barrier itself is a derivation, not a
proof, and is labeled `proof_status: derivation` per
`docs/claims-and-verification.md`. No universal impossibility claim is made or
implied: the conclusion is scoped to the hypothesis ledger written inside the
goal.

Non-duplication and interface rules honored:

- Distinct from G30-019/020/021 (isogeny-walk collision, A2 transfer boundary,
  PO96 residual labels): those are transfer-side, not lift-supply side.
- Relates to `LEAD-TRF-global-lift-small-height`, whose obstruction already
  records that the fixed-arity C0/p bound "does not cover every selected-lift rule
  over Q or bounded-degree K". This goal attacks exactly that uncovered scope, on
  the supply side, and must cite the lead's obstruction text rather than restate
  it as new.
- Does not re-run EXP-CZLIFT panels; consumes no ledger evidence; commissions no
  experiment on lift families other than the height-counting check specified here.

## G31-002: Characteristic-0 point-supply barrier — no height-bounded lift supplies a factor base

- **Cluster:** 12 LIFT
- **Type:** barrier
- **Long-term chain:** the lift/transfer family has been closed by one negative
  experiment at a time (`LEAD-TRF-global-lift-small-height`,
  `LEAD-TRF-kernel-of-reduction-lemma`, `LEAD-TRF-anomalous-padic-lift`,
  `LEAD-TRF-padic-canonical-section`, EXP-CZLIFT rounds), and its own obstruction
  record states that the residual scope — arbitrary selected-lift rules over Q or
  bounded-degree K — is still open. This goal converts the *supply* half of that
  residual into a theorem-shaped derivation: if the height-bounded reduction set is
  polylogarithmic, no rule that draws its factor base from the lift can reach the
  base size and relation surplus an index-calculus engine needs. The outcome gates
  reallocation of lift budget and gives the barrier track its first characteristic-0
  entry, replacing a further sweep with a scoped closure certificate.
- **Mechanism:** three steps, each with its own artifact.
  1. **Supply lemma.** For E_K/K of Mordell–Weil rank r, the number of K-rational
     points of canonical height ≤ B satisfies
     #{P ∈ E_K(K) : ĥ(P) ≤ B} ≤ C(E_K)·B^(r/2) for B ≥ 1 (Northcott; the
     lattice/Masser–Wüstholz form). Put B = c·log p for reductions at a prime
     above p of good reduction, exclude torsion and points reducing to O, and get
     |B_p(c)| ≤ C·c^(r/2)·(log p)^(r/2) = p^(o(1)) for fixed (E_K, c, r).
  2. **Supply–engine composition.** For an s-point decomposition over a base of
     size b, one full sweep of b^(s−1) trials yields ≈ b^s/p relations
     (uniform-decomposition heuristic — to be registered as a numbered heuristic
     before activation, per the heuristic-conditional two-record rule). Linear
     algebra needs ≈ b relations, so a base with b = p^(o(1)) yields < 1 relation
     per sweep for every s ≥ 3, and the required trial count is p^(1−o(1)) ≥ √p.
     The deficit factor is p^(1/(s−1))/b → ∞.
  3. **Hypothesis ledger and loopholes.** The barrier holds only under: H1 fixed
     (K, E_K) with bounded height, conductor and coefficients, uniformly in p;
     H2 the base is any rule computable from the reduction of E_K(K) (adaptive
     rules included); H3 r(E_K) = o(log p / log log p) over the regime addressed.
     Three loopholes are named as the attack surface, not hidden: L1 growing rank
     (the bound survives up to the H3 boundary and the goal reports the exact
     crossing exponent); L2 non-MW selections — p-adic uniformization or formal
     group/Teichmüller sections outside the Mordell–Weil lattice, the anomalous
     channel already excluded in `LEAD-TRF-kernel-of-reduction-lemma`; L3 variable
     K with degree n growing in p, where the bound degrades to (log p)^(nr/2) and
     the barrier needs n·r = o(log p / log log p) — the sharpest open gap.
  Deliverables: a `derivation` artifact (statement, proof of the lemma application,
  hypothesis ledger, loophole analysis), a supply table on three explicit curves,
  and an N_min(s,b) ledger stated as an operation count against √p and explicitly
  **not** routed through the GOE ruler (no rho-relative cost claim).
- **Quantified prediction:** for the three test curves, the fitted exponent of
  |B_p(c)| against log p is within ±0.2 of r/2 (r = 1, 2, 3 arms), the fitted
  constant C(E_K) does not drift with p beyond the O(1) canonical-vs-naive height
  gap, and the log-log slope of |B_p(c)| against p lies in [−0.5, 0] at every
  rung — i.e. the supply is decreasing in units of the engine's √p requirement.
  The derivation closes H1–H3 with L1–L3 recorded as the only exits; no cell is
  predicted to produce b ≥ p^(1/3) at any rung.
- **Test boundary / scope:** derivation plus a height-counting check only. Three
  curves over Q with pinning verified before the run (start from 37a1, 389a1,
  5077a1 for ranks 1, 2, 3; if a rank disagrees with the committed instance table,
  the cell is re-pinned and the change logged, never silently re-selected). Primes
  of good reduction only, ≥ 12 per curve on the ladder p ∈ {2^10, 2^13, 2^16,
  2^20}; bad primes and primes dividing denominators are censored and listed.
  Heights exact (canonical height; floating point never decides a comparison or a
  fit). Scope is fixed (K, E_K) and the H1–H3 regime — never "index calculus
  cannot beat rho over prime fields", which no claim tier permits.
- **Primary metric:** fitted exponent of |B_p(c)| vs log p per curve, with the
  supply table and the N_min(s,b) deficit factor / **Secondary metrics:** exact
  counts per rung, fitted constants, torsion-image count (excluded from supply,
  reported separately), the H3 crossing exponent r*(p) = log p / log log p, and the
  height-gap between canonical and naive conventions per rung.
- **Controls:** a rank-0 curve must give |B_p(c)| = 0 at every rung (phantom
  control — any nonzero count is an implementation bug by construction); a rank-1
  arm must fit exponent 0.5 ± 0.2; a torsion-inflation control (a base built only
  from torsion images must produce zero usable relations, and torsion must be
  excluded from b); a height-convention control (canonical vs naive heights differ
  by O(1); the fitted constant must not trend with p); bad-reduction censoring
  control (a bad prime must never silently enter a fit).
- **Falsification criteria:** (i) the rank-2 arm fits an exponent > 1.25 with
  stable re-runs → the lemma application or its implementation is broken; the
  barrier is suspended, never weakened, and the artifact is withheld; (ii) an
  admissible selection rule satisfying H1–H3 yields b ≥ p^(1/3) at two or more
  rungs with construction cost charged inside H2 → the supply claim is refuted in
  scope, and the surviving rule is routed to the transfer family as an attack lead
  with its own next_action; (iii) the loophole ledger cannot be closed for the
  addressed regime (e.g. a known rank-growth family forces n·r ≫ log p/log log p)
  → the deliverable is the exact boundary exponent, reported as a boundary, not as
  a barrier. Each exit names the artifact that survives, so a falsification is an
  output, not a failure.
- **Negative-outcome value:** if the derivation holds, the fixed-lift family gets a
  closure certificate at derivation scope, the "one more lift experiment" branch is
  closed without compute, and the barrier track gains an entry whose loophole list
  *is* the precise attack surface for any future lift proposal. If falsified, the
  falsification identifies the one surviving selection rule, which replaces a broad
  sweep with a single specified experiment — the best available failure mode for
  this family.
- **Budget:** wall_clock 10h, memory 4 GiB, max_runs 24
- **Stopping rule:** stop when the derivation artifact, the hypothesis ledger, the
  loophole analysis, and the three-curve supply table are committed in the same
  snapshot, OR at 10h wall clock, OR when a falsification criterion fires (early
  exit; the surviving artifact is committed before any decision record relies on
  it). Censored primes and re-pinned cells are listed explicitly.
- **Harness dependency:** existing `harness/toycurve.py` for the reduced curves'
  group law; commissions one module, `harness/height_supply.py`: exact canonical
  heights over Q for the three curves, bounded-height point enumeration over
  Mordell–Weil basis combinations, reduction with torsion exclusion, fit and supply
  ledger. Pure Python + sympy; a Sage height cross-check goes through G30-025's
  environment-capture registry where available. No GOE dependency; the only
  numeric comparison is the model-free b ≪ √p separation, recorded as a count, not
  as a cost.
- **Claim tier:** toy
- **Dependencies:** none hard. Interface: consumes the obstruction text of
  `LEAD-TRF-global-lift-small-height` as its starting scope statement. Literature
  to ingest before activation (NoveltyGate, absent from the corpus on 2026-11-20):
  Flannery–Lenstra–Wesolowski-type low-point counting and the 2024–25
  decomposition-implementations-over-E(Q) work; until ingested, the supply lemma is
  cited only from the classical Northcott/Masser–Wüstholz side.
- **Novelty screen (2026-11-20):** `docs/ecdlp-literature-review-20260926.md`
  contains no height, Mordell–Weil, lift or characteristic-0 material (0 hits);
  the corpus's Mordell/Hensel entries are incidental. No goals30 goal states a
  supply barrier; `LEAD-TRF-global-lift-small-height` states the relation-side
  obstruction and explicitly leaves the selected-lift scope open. No novelty beyond
  "absent from this program" is claimed.
