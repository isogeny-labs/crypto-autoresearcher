# Pre-read verdict — TASK-20261105-9d65dc (RP-BATCH-9f090a)

Sealed BEFORE opening any `derivation_tier_inputs_never_conclusions` path
(augmented-oracle-review.md, holant-h1-ggm-lemma README.md / REDTEAM.md).
Read up to this point: AGENTS.md; DEC-20260831-a9716f; DEC-20261105-c5fcb6;
review-plan.yaml; the nine frozen records; plus, to pin oracle definitions as
J1/J2 instruct ("fix its exact input/output from the record and EXP-GGM-001"),
experiments/EXP-GGM-001/specification.yaml, KN-TECH-005, KN-LIT-7606 (first
60 lines), EV-GGM-79e710, DEC-20260804-3b4258 and the KN-FIND-b7e091 producer
artifact BATCH-060/tasks/TASK-20260804-051/ggm_analysis.md. None of these is a
derivation-tier input of this plan. Checks: checks/ggm_oracle_checks.py (+ .out).

Model: Shoup GGM (random injective labels sigma: Z_N -> S, group-oracle queries
counted, local computation free, N prime or bound stated in the largest prime
factor). "Simulable with overhead C" = a k-independent generic procedure answers
each query with <= C group-oracle calls, identically distributed.

## Lemma R (reduction criterion; proved here)
If oracle O is simulable with overhead C(N), an adversary making T_g group and
T_O oracle queries with success eps yields a generic algorithm of
T_g + C*T_O queries, so T_g + C*T_O >= Omega(sqrt(eps*N)) (Shoup), i.e.
T >= Omega(sqrt(eps*N)/max(1,C)). Exponent 1/2 is preserved iff C = N^{o(1)}.
O(1) is sufficient, not necessary; O(log N), O(polylog N) also close at 1/2.
## Lemma S (direct Shoup count; proved here)
If each oracle query introduces O(1) new linear forms a+bX (labels or equality
tests on forms the adversary can name), Shoup's collision count goes through
with no reduction overhead: success <= O((T_g+T_O)^2/N).

## J1 — KN-FIND-002 tier (CC-3)
- Jet (EXP-GGM-001: (P,Q) -> (P+Q, eps-part in F_p[eps]/eps^2)), Weierstrass
  reading: output is field data whose value depends on k for a fixed public
  query (C6: 198 distinct values / 200 k). NOT Shoup-simulable (record concedes).
  In the record's "structured GGM" (curve public, labels opaque) still not
  simulable: coordinates of Q are determined by, but not computable from, the
  label. If "structured GGM" lets the simulator read coordinates, the same rule
  classifies the record's own encoding control (x-coordinate) SIMULABLE C=0 and
  no lower bound holds (concrete model; Smart on anomalous curves) -> proves too
  much. Invariant-differential reading: t(P+Q)=t(P)+t(Q) (C6), trivially
  simulable, C=1, carries no information, closed at 1/2 vacuously — not the
  record's stated mechanism. VERDICT: closure at 1/2 does NOT follow for jet in
  any model the record states. BREAKS.
- Endomorphism (P -> phi(P), label output): phi acts on E(F_p)=Z/N as [lam],
  lam public (C2). Simulable at <= 2 ceil(log2 N) group ops, NOT C=0 (C=0
  applies phi to coordinates). Closed at 1/2 by Lemma R or Lemma S. Conclusion
  HOLDS, overhead and justification WRONG.
- Elliptic net: record defines W(a,b) = aP + bQ (a label) -> that is a
  scalar-multiplication oracle, simulable at O(log N), and IS closed at 1/2
  (Lemma R/S); "not closed at 1/2" under-claims. EXP-GGM-001's oracle returns
  the field-valued net value (division-polynomial data; W(1,-1)=x_Q-x_P by
  Stange's identity, CITED/recalled, not load-bearing): NOT simulable;
  "no sub-birthday advantage" then is the open x-oracle question
  (KN-FIND-194294 non-claims) — unsupported. Record simulates a different
  oracle than its spec.
- Incidence (SEARCH, fixed arity m, factor base B, any target R): simulable
  at O(B^m) (MITM O(B^{ceil(m/2)})); "not closed at 1/2" is CORRECT and in fact
  the oracle BEATS 1/2 in the query metric: base-B digit factor base,
  B=N^{1/(m+1)}, cost O(m N^{1/(m+1)}) (m=1 is BSGS; m=2 gives 1/3; C4).
  So the title clause "providing no sub-birthday advantage" is FALSE for
  incidence in the query metric (and tautological under honest charging).
- "Structured GGM" as used gives no lower bound. KN-LIT-7606's structured GGM
  (CITED via kb, paper unread by program): bound Omega(min(sqrt q, 1/delta));
  jet output exposes structure at every queried point, delta ~ 1, no bound.
- Also: no prime-order hypothesis; exponent must be in largest prime factor.
- Tier support: EV-GGM-001 superseded by EV-GGM-002 (evidentially void);
  CORR-20260727-003 already requires a superseding/correcting KN-FIND. Recorded
  status established / confidence strong is unsupported.
J1 VERDICT: BREAKS (jet closure does not follow; endomorphism overhead wrong;
elliptic-net oracle mis-defined; incidence "no sub-birthday advantage" false).

## J2 — KN-FIND-b7e091 justification (CC-2)
- End_{F_p}(E) = Z is FALSE for every E/F_p: Frobenius is F_p-rational with
  deg p, [m] has deg m^2, p never a square (C1). (End over F_pbar is also never
  Z for E over a finite field — CITED, Deuring.) The closure does NOT need it:
  E(F_p) cyclic of prime order N, so any F_p-rational phi acts as a scalar lam
  (proved here; the producer artifact ggm_analysis.md in fact argues this).
  For ordinary E all endomorphisms are F_p-rational (CITED); prime order odd
  N>3 excludes supersingular E/F_p (N=p+1 even). "m group operations" literal is
  O(N) per query (lam ~ N; C2: lam=30778 vs 21 ops) -> fix to <= 2 ceil(log2 N).
- Incidence Oracle C: the finding sentence "reporting which factor-base subsets
  sum to the target Q" is a SEARCH oracle; SEARCH is NOT simulable at O(m): with
  F={2^i G}, one query returns the bits of k (C3); a simulator of overhead C
  would give Shoup log N + C >= Omega(sqrt N). The producer artifact defines
  CHECK ("for any queried subset I, answers whether sum_I P_i = Q"): simulable
  at |I|-1 <= m-1 ops, and closed at 1/2 by Lemma S independent of m (C5), and
  by Lemma R whenever m = N^{o(1)}. Scope: factor base given as LABELS; a
  coordinate-defined factor base (Semaev x<t) is the C_t oracle, non-simulable
  (KN-FIND-982fdf) and outside the closure — real index calculus not closed.
- "confidence proved / theorem_backed": supported for CHECK and label-valued
  endomorphism images after erratum; not as written (false premise in proof_refs
  of EV-GGM-79e710, literal O(N) overhead, SEARCH-readable definition).
J2 VERDICT: BREAKS as written (false stated premise; literal overhead
super-polylog; Oracle C sentence admits a reading under which the claim is
false); conclusions SURVIVE under pinned definitions -> scoped erratum.

## J3 — CC-1 and F-5
- CC-1: the two records define different oracles (002: SEARCH, arity m, base
  size B, any target R; b7e091 source: CHECK, base size m, target Q; letter m
  means different things). Under one definition each: SEARCH -> 002 right that
  it is not closed at 1/2 (actually broken below 1/2), b7e091 O(m) false;
  CHECK -> closed at 1/2 (Lemma S), b7e091 right, 002 silent. Not inconsistent
  once pinned; inconsistent as written because b7e091's sentence reads SEARCH.
- F-5 criterion (single): an oracle family is closed at exponent 1/2 in Shoup's
  GGM iff (sufficient condition) it has a k-independent label-only simulator
  of overhead N^{o(1)} per query, or each query adds O(1) linear forms (Lemma S);
  field-valued outputs that vary with k on GGM-indistinguishable instances are
  never simulable. Applied: jet(W) not simulable; jet(inv) closed; endo(label)
  closed, Theta(log N); net(label) closed, Theta(log N) [002 under-claims];
  net(field) not simulable; incidence SEARCH not closed (002 right, b7e091
  wrong); incidence CHECK closed (b7e091 right with erratum). 002 violates the
  criterion by refusing net(label) and by C=0 for endo; b7e091 by "m ops".
J3 VERDICT: inconsistent as written; consistent under pinned definitions and
the single criterion; both records violate O(1)-criterion consistency (F-5).

## J4 — pre-read recommendation
KN-FIND-002: SUPERSEDE (evidence void; jet closure unsupported; three of four
oracle statements need changing). KN-FIND-b7e091: SCOPED ERRATUM (premise,
overhead, CHECK definition, label factor base scope). Exact texts in REVIEW.md.
