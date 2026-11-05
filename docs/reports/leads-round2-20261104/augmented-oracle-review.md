# Red-team review: LEAD-EXO-augmented-oracle-ggm (closed_obstructed)

Reviewer: Red Team (Claude Opus 5.5), 2026-11-04. Review only. I edited nothing in the repository and
changed no status. The Coordinator decides; the Validator records.

* Frozen evidence: isogeny-labs/crypto-autoresearcher, main @ `e4a78f9826a834aa5db8d200126555821a68b08f`
  (shallow sparse clone at `/home/user/crypto-autoresearcher`). Every file quoted below is tracked at
  that commit (`git ls-files` confirmed for both report directories). Line numbers are `cat -n` of
  those bytes.
* Row under review: `knowledge/leads/ecdlp/exotic/LEAD-EXO-augmented-oracle-ggm.yaml`, lines 9-22,
  `last_reviewed: '2026-10-29'`.
* Model fixed for this review: **Shoup's GGM.** Elements are seen only as labels sigma(R) under a random
  injection. The algorithm pays for group-oracle queries, and local computation is free. "Simulable with
  overhead s" means each augmented-oracle answer can be produced from labels with at most s group
  queries. Then a q-query augmented algorithm becomes a generic algorithm with q*s queries, and Shoup
  gives q*s = Omega(sqrt N'), where N' is the largest prime factor of N (KN-TECH-005 line 7).
* No experiment was run. None is needed: every item is settled by reading committed records or by a
  reduction of three lines or fewer. A toy run cannot discriminate, because Shoup's bound is vacuous at
  toy N (holant REDTEAM.md F3, line 201).

## 1. The row as written

`LEAD-EXO-augmented-oracle-ggm.yaml`:

> 4: "Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability"
> 13-15: "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent
> to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 (KN-FIND-002,
> KN-FIND-b7e091, KN-FIND-194294; EV-GGM-001 strong)."
> 17-18: "Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."
> 19-21: revisit_when "A publicly computable oracle that is NOT GGM-simulable is exhibited (the threshold
> oracle is the minimal non-simulable identifier, KN-FIND-982fdf, but needs private data)."

`forecloses` includes "x-coordinate oracle meet in the middle", "y-coordinate oracle guided
decomposition", "full-point oracle", "endomorphism image oracle", "halving query oracle" and "generic
group model simulable oracle".

The row uses one word, "oracle", for three different kinds of object. Separating them settles most of
the review:

* **Type L (label oracles).** Input is a label. The output is a label, or a bit fixed by group relations
  among labelled elements. Shoup simulability is meaningful for these, and it usually holds.
* **Type C (coordinate oracles).** Input is a label and the output is field data about that element: a
  coordinate, a function of coordinates, or a coordinate predicate. Shoup simulability fails.
* **Type P (public-data "oracles").** There is no instance input; the input is a field element or an
  index (x0 -> factor-base membership, O_y(x0), O_full on an index space, "is P in phi(E)?"). These are
  not GGM augmentations at all. They cost 0 queries and give a concrete attacker nothing it lacks. Any
  use of them on instance-derived points needs Type C access.

## 2. Per-oracle verdict (Shoup's GGM)

| oracle (reading) | simulable? | overhead s | proof or counterexample (1-2 lines) |
|:--|:--|:--|:--|
| **x**: sigma(R) -> x(R) (KN-FIND-194294 l.17-19) | **No** | **Theta(sqrt N')**, i.e. a DLP oracle up to O(log N) | Two X-queries give x(G) and x(Q). Free local brute force gives k up to sign, and sigma([k]G) by double-and-add (O(log N) queries) fixes the sign. So 2s + O(log N) >= c sqrt N'. BSGS on the queried label plus local evaluation gives O(sqrt N'). (holant README l.46-51; REDTEAM F3 l.165-176.) Holds on every curve. |
| **y**: sigma(R) -> y(R) | **No** | Theta(sqrt N') | x^3+ax+b = y0^2 has at most 3 roots, so y(R) leaves at most 3 candidate points. Local brute force on each, then verify with O(log N) group queries each. Same bound as x. |
| **full point**: sigma(R) -> (x,y)(R) | **No** | Theta(sqrt N') | One query on Q plus local brute force gives k exactly. Sanity check: if s = o(sqrt N), Shoup would bound *concrete* ECDLP by Omega(sqrt N) on every curve. Smart's attack (anomalous curves, 2 point reads plus polynomial local work) refutes that. |
| **halving**, x-valued: Q -> x([2^-1]Q) (KN-FIND-194294 l.17-21) | **No** | Theta(sqrt N') | X(sigma R) = H(sigma(2R)) costs 1 doubling, and H(sigma R) = X(sigma([(N+1)/2]R)) costs O(log N). So H is equivalent to X (DEC-20260806-08b9ed l.26-38, 98-100). |
| halving, label-valued: sigma(R) -> sigma([2^-1]R) | Yes | Theta(log N) | Scalar (N+1)/2 by double-and-add. |
| **endomorphism image**, label-valued: sigma(R) -> sigma(phi R) | **Yes** | **Theta(log N)** (O(1) only for small lambda) | phi is F_p-rational, so it preserves the prime-order group G and acts there as a scalar lambda in Z/N. lambda depends only on the curve and the generator, so it is public. The simulator returns sigma([lambda]R). The KN-FIND-b7e091 premise "End_{F_p}(E) = Z" (l.27) is false (Frobenius, EV-ECDLP-048824 CC-2); this eigenvalue argument replaces it. The bound is q = Omega(sqrt N'/log N), so exponent 1/2 is preserved. (CORR-20260727-003 l.70-74; EV-GGM-002 l.189-198.) |
| endomorphism image, coordinate-valued (e.g. (zeta x, y)) | No | Theta(sqrt N') | It reveals y(R), so it reduces to the y row. |
| endomorphism-image membership "P in phi(E(F_p))?" (IDEA-20260808-c5f9a2) | trivially yes | 0 | It is constant "yes" on prime-order G and carries 0 bits (H-ECDLP-29400c). This is Type P; it needs no GGM argument. |
| **incidence CHECK**, factor base given as labels | **Yes** | **O(m)** | m-1 additions and 1 equality test (KN-FIND-b7e091 l.22-24; DEC-20260901-e24d15 l.83-90). |
| incidence SEARCH (list decompositions), factor base as labels | Yes | O(B^ceil(m/2)) by label meet-in-the-middle; O(B^m) brute force (KN-FIND-002 l.74-77) | Hashing labels is free local work. At yield-admissible B (B^m >= m!N), s >= sqrt N, so the per-query bound is vacuous (H-ECDLP-5a484e). The total-cost Omega(sqrt N') bound still holds for the generic implementation. |
| incidence with membership of *instance-derived* points in a coordinate-defined factor base (x(F) < L, as in H-XOR-YIELD) | **No** | not pinned | Membership is the threshold oracle C_L. Two GGM-indistinguishable instances answer differently (KN-FIND-982fdf (b), l.29-33). |
| **jet**, private reading: eps-part of [k]G~ | No, and **not public** | equivalent to a DLP oracle | G~ = G + eps*tau gives [k]G~ = ([k]G, k*tau). That depends on the integer k, not on Q (EV-GGM-79e710 O-4, l.46-51). It is not a candidate public oracle. |
| jet, canonical-lift reading (unique order-N lift in E(F_p[eps])) | trivially yes | 0 | When p does not divide N, the order-N lift is the image of the inclusion E(F_p) -> E(F_p[eps]), so its eps-part is 0. Constant, 0 bits. |
| jet, field-valued at instance points (derivative of the addition map, chord slope) | **No** | Theta(sqrt N') | With G public, the slope of the chord through G and Q leaves Q in {Q, -(G+Q)}: 2 candidates. Then as for x. The row's "jet O(1)" is the structured-GGM C=1 verdict, withdrawn (CORR-20260727-003 l.37-42, 59-63). |
| **net**, label-valued sigma(aP+bQ) (KN-FIND-002 reading, l.67-72) | Yes | Theta(log N) | Double-and-add. This is scalar multiplication, not an elliptic net. |
| net, field-valued W(a,b) in F_p (Stange; EV-GGM-79e710 O-5 l.52-59) | **No** | Theta(sqrt N') | The net based at Q contains W(2) = psi_2(Q) = 2y(Q) (division polynomial; standard, provenance recalled). So it reduces to the y row. |
| threshold C_t (KN-FIND-982fdf) | **No** | not pinned by proof. Heuristically Omega(sqrt N/log N): O(log N) bits on random multiples [b_i]Q plus local brute force single out k | Two-instance witness, KN-FIND-982fdf l.29-33. **Publicly computable** (l.29, l.55-56). |
| degree-D coordinate tests | No in general | one test errs on at most (Delta + t)/N of k, Delta = sum_i (2d_x,i + 3d_y,i) b_i^2. Large b_i cost O(log N) | Low-degree desk §1b-§2 (l.20-41, 64-72, 84-89). If the rank condition holds, log2 N tests give k (conditional). |
| Type P: x0 -> FB-membership (EXP-SEMAEV-f48dd1 "x-oracle"), O_y(x0), O_full on an index space | not GGM augmentations | 0 | They have no instance input. Their recorded dispositions are model-free: Rel_guided is a subset of Rel_exhaust (H-ECDLP-cd7072), a tautological relation of rank 0 (H-ECDLP-5cb5d0), measured Y_A = Y_B. Any use on R = Q + ... needs x(R), which is Type C. |

The structured-GGM verdicts (KN-FIND-002 jet C=1, endomorphism C=0) are vacuous. In that model the
simulator holds coordinates, so it is the concrete model, and no lower bound exists there (KN-FIND-002
l.81-84; holant README l.59-60; REDTEAM table row C').

## 3. Findings, ordered by severity

Tags: **wrong** (contradicted by committed evidence or by proof), **unsupported** (no evidence carries
the claim), **unpriced** (a cost or scope left out).

### F1 (critical; wrong). "Each named oracle is GGM-simulable" is false for x, y, full point, x-valued halving, and field-valued jet and net.
* The row cites KN-FIND-194294, which says the opposite. Lines 25-26: "O_D inherits the classification
  of O_x: it is NON-SIMULABLE (Tier 3) in the GGM sense." Lines 40-42: "The x-oracle-alone sub-rho
  question is OPEN".
* DEC-20260806-08b9ed l.98-100: "The implied GGM-simulable realization for O_D — struck. O_D carries the
  encoding (x-coordinate) observable, so it is non-simulable Tier-3".
* holant README l.46-51 (Lemma 3): "On every curve, X cannot be simulated with o(sqrt n') group queries
  per query."
* EV-GGM-79e710 (via KN-FIND-b7e091 l.37-41) classifies jet and net as NON-SIMULABLE. KN-FIND-002
  classifies them as simulable. The row adopts KN-FIND-002's numbers while citing both records.
* Cheapest test: read the four records above (zero compute). The reductions in §2 are the proof.

### F2 (critical; wrong). "so the Shoup lower bound closes its candidate family at exponent 1/2"
* For Type C oracles the GGM gives **no** bound, because two queries plus free local work already solve
  the DLP.
* For the structured-GGM verdicts, the source itself disclaims Shoup. KN-FIND-002 l.81-84: "The
  classification uses the **structured GGM** (curve equation is public), not the strictest Shoup GGM
  (opaque labels). Under the strictest GGM, jet and endomorphism would be NON-SIMULABLE because they
  require coordinate access."
* EV-ECDLP-048824 CC-3 (l.328-343): KN-FIND-002 closes jet and endomorphism at 1/2 "WHILE declaring the
  structured GGM as its model ... no lower bound can be certified in the structured GGM because Shoup
  theorem does not hold there".
* KN-TECH-005 l.8 limits applicability to "opaque labels accessed only via the group-operation oracle".
  Lines 39-43 add: "says nothing about attacks exploiting concrete structure (... summation-polynomial
  index calculus ...)".
* The full-point sanity check in §2 shows the inference proves too much.
* Unpriced arm: the GGM charges nothing for local work. That gap is exactly why coordinate-oracle
  simulability fails, and why the remaining question is time-bounded (holant README l.55-57).

### F3 (high; unsupported). The cited evidence base is void, withdrawn, or awaiting a rule-12 round
* "EV-GGM-001 strong": EV-GGM-002 l.3 `supersedes: EV-GGM-001`. Lines 145-146: "This run set is
  EVIDENTIALLY VOID with respect to H-GGM-001". Lines 182-184: "THE CLOSURE LANGUAGE OF EV-GGM-001 IS NOT
  CARRIED FORWARD. 'Closure at exponent 1/2' ... appear nowhere in this record". Lines 213-216: "Whether
  the jet, elliptic-net, incidence and endomorphism oracles are GGM-simulable under a single frozen model
  is UNDETERMINED by this record and is not decided anywhere in the ledger."
* `kind: theorem`: CORR-20260727-003 l.101-105: "COUNTERMANDED. No theorem exists, no candidate family is
  closed by this archive, and no such closure is authorized. Any closure of a live candidate family is a
  closure result requiring an independent review-breakthrough review at max under AGENTS.md rule 12".
  Lines 108-110 say the KN-FIND-002 promotion is "NOT WARRANTED ON THE SUPERSEDED EVIDENCE".
* The rule-12 round is still unopened:
  * EV-ECDLP-048824 l.344-355 routed CC-1/2/3 to "a SEPARATE round ... review-breakthrough, max effort".
  * DEC-20260901-34e038 l.60-63 and DEC-20260901-255ebd l.152 say they "remain unresolved and unopened".
  * GOAL-ECDLP-001 goal.yaml l.12926-12927: "KN-FIND-002 and KN-FIND-b7e091's routed tier objections
    remain unopened per DEC-20260831-a9716f."
  * I found no later record that opens the round (searched `ledger/` at e4a78f98 for KN-FIND-002 together
    with review-breakthrough).
* Cheapest test: the Coordinator opens the routed round. That is zero compute.

### F4 (high; wrong). revisit_when is mis-stated, and it had fired before the 2026-10-29 review
* "but needs private data" contradicts KN-FIND-982fdf l.29-30: "C_t is not GGM-simulable; it is
  encoding-dependent and publicly computable". Lines 55-56: "public computability from the concrete model
  (no k required)".
* The trigger "A publicly computable oracle that is NOT GGM-simulable is exhibited" is met by:
  * KN-FIND-982fdf (added 2026-08-05);
  * KN-FIND-194294 (added 2026-08-06; O_x is publicly computable in the concrete model);
  * holant Lemma 3 (2026-11-03, every curve);
  * the low-degree desk §1c (2026-11-04, l.59-62): "The x-oracle is vacuous because two queries plus free
    local work give log_P Q ... the same free-local-work loophole operates".
* The holant README l.118-120 already says so: "the row's own `revisit_when` condition ... has fired.
  This note does not change the row. The routed round decides."
* **Verdict: fired**, and the first two triggers predate `last_reviewed: 2026-10-29`.

### F5 (medium; wrong). The per-oracle overhead figures in the row
* "jet ... O(1)": withdrawn. CORR-20260727-003 l.39-41: "not earned for the jet oracle under either
  model the reviewer formalised".
* "endomorphism O(1)": the right count is Theta(log N). CORR-20260727-003 l.70-74: "C = 0 is not [correct]
  ... the honest count is Theta(log N), at which exponent 1/2 is still preserved".
* "incidence O(m)": true only for the CHECK interface. DEC-20260901-e24d15 l.88-91: "KN-FIND-002 item 4
  prices a DIFFERENT interface, the SEARCH interface, at O(B to the m) ... Two oracle interfaces share
  one name in this corpus". The row does not say which interface it means, and does not disclose the
  CC-1 conflict.
* "net O(log N)": true only for the label-valued reading (§2).
* Also: the exponent-1/2 statement needs N prime, or must be stated in terms of N'
  (EV-ECDLP-048824 O-6).

### F6 (medium; unsupported scope). forecloses and coverage overreach
* "x-coordinate oracle meet in the middle", "y-coordinate oracle guided decomposition", "full-point
  oracle" and "halving query oracle" are not foreclosed by any GGM argument.
* x-membership-filtered MITM is a Semaev IC pipeline step. Its hypothesis H-XOR-YIELD is mapped in
  `coverage.tsv` l.1329 to LEAD-ICE-semaev-yield-model-coset-typing, not to this row.
* "Scope: oracles, not resources" contradicts the title. An x-oracle *is* resource R1 (field data)
  delivered as oracle answers (IDEA-20260808-ea3b4f claim (B)).
* The row covers a live, specified hypothesis on exactly the frontier it claims to close: H-AOM-8d4a83
  (degree-d algebraic oracles; status `specified`).

### F7 (low; stale/unpriced). best_measured and scope of the measurements
* EV-ECDLP-284817 ("oracle increases candidates", B/C = 3.754) was also lowered strong -> preliminary
  (CORR-20261026-c94668 l.101-107). The row notes the downgrade only for fd61e4.
* No measurement in the row states its scope. All are toy, 7-8 field bits, m = 3, one implementation,
  one exploitation strategy (EV-ECDLP-fd61e4 l.47-49; EV-ECDLP-7367e2 boundaries).

## 4. What survives and what does not

**Survives**, rescoped:
1. **Label oracles (Type L)**:
   * endomorphism image as labels, Theta(log N);
   * label halving, Theta(log N);
   * incidence CHECK over a label factor base, O(m);
   * incidence SEARCH over a label factor base, O(B^ceil(m/2)); the per-query bound is vacuous at
     yield-admissible B, but the total-cost bound stands;
   * label-valued net sigma(aP+bQ), Theta(log N).

   An algorithm that touches the instance only through these and the group oracle is generic, so Shoup's
   Omega(sqrt N') applies to its total group-operation count.
   * The corpus derivations behind this are the REV-20260727-002 reviewer derivation (EV-GGM-002
     l.189-198: "attributed here, is not adopted as a finding, and needs its own independent review") and
     REDTEAM F1 "What survives in Shoup's model" (l.93-97).
   * LEAD-STR-endo-scalar-action-generic already states the endomorphism part correctly ("End(G) = Z/N";
     revisit_when "returns field data").
   * This class closes no algorithm that reads coordinates. In particular it cannot apply any F_p-basis
     change (holant README l.36-40).
2. **Type P dispositions**: O_y(x0) generative (set inclusion), O_full on an index space (tautology,
   rank 0), and "P in phi(E)?" (constant). These are model-free derivations in `proposed` hypothesis
   records (H-ECDLP-cd7072, -5cb5d0, -29400c). They survive as derivations, not as GGM results, and they
   do not reach the label-to-coordinate oracles of the same name.
3. **Measurements** (scoped, preliminary):
   * Y_A = Y_B in 40/40 cells (EV-ECDLP-fd61e4);
   * B/A field operations 0.0557, attributable to the split (EV-ECDLP-7367e2);
   * B/C candidates verified 3.754 (EV-ECDLP-284817).

   These are measurements of one strategy at 7-8 bits, not a lower bound.

**Does not survive**:
* "each named oracle is GGM-simulable";
* "Shoup ... closes its candidate family at exponent 1/2" for x, y, full point, x-halving, field-valued
  jet, field-valued net, C_t, coordinate-defined incidence, and degree-D tests;
* "jet O(1)", "endomorphism O(1)", and "incidence O(m)" without naming the interface;
* the "EV-GGM-001 strong" citation;
* `kind: theorem` for the stated scope;
* the "needs private data" clause;
* the forecloses phrases for the x, y, full-point and halving oracles.

## 5. Proposed replacement (for the Coordinator; not applied)

This follows the README "Pursuit invariant" (`knowledge/leads/ecdlp/README.md` l.75-77): "If a
`closed_obstructed` row is later found to cover only one submechanism, reopen or split the uncovered
mechanism; do not let the broad title inherit a narrow obstruction." The proposal is a split.

### Row A: keep the id, narrow it to label and public-data oracles

```yaml
id: LEAD-EXO-augmented-oracle-ggm
title: >-
  Label-valued augmented oracles (endomorphism image, label halving, incidence over a label
  factor base, label-valued net) and public-data oracles: Shoup-GGM simulability
disposition: closed_obstructed
obstruction:
  kind: theorem
  statement: >-
    Scope: oracles whose input and output are group labels (or bits fixed by group relations
    among labelled elements), and public-data oracles with no instance input. Model: Shoup's
    GGM (opaque labels, queries counted, local work free). Each in-scope oracle has an explicit
    generic simulator: endomorphism image acts on the prime-order group as a public scalar
    lambda, Theta(log N) group operations (the End_{F_p}(E) = Z premise of KN-FIND-b7e091 is
    false, EV-ECDLP-048824 CC-2; the eigenvalue argument replaces it); label halving is
    [(N+1)/2], Theta(log N); incidence CHECK over a factor base given as labels is m-1
    additions and one equality, O(m); incidence SEARCH over such a base is label
    meet-in-the-middle, O(B^ceil(m/2)), so at yield-admissible B the per-query bound is vacuous
    (H-ECDLP-5a484e) but the total-cost bound holds; a label-valued net sigma(aP+bQ) is
    double-and-add, Theta(log N). An algorithm that touches the instance only through these
    and the group oracle is generic, so Omega(sqrt N') group operations, N' the largest prime
    factor of N (KN-TECH-005). Public-data oracles (x0 -> factor-base membership, O_y(x0), a
    full-point oracle on an index space, "is P in phi(E)?") take no instance input; their
    recorded dispositions are model-free (H-ECDLP-cd7072, H-ECDLP-5cb5d0, H-ECDLP-29400c).
    NOT in scope: any oracle returning coordinates or coordinate predicates of instance points
    (x, y, full point, x-valued halving, field-valued jet and net, C_t, degree-D tests); see
    LEAD-EXO-coordinate-revealing-oracles. Measured, toy 7-8 bits, m = 3, one strategy,
    strength preliminary (CORR-20261026-c94668): x-membership-filtered MITM gives Y_A = Y_B in
    40/40 cells (EV-ECDLP-fd61e4); B/A field operations 0.0557, attributable to the split
    (EV-ECDLP-7367e2); B/C candidates verified 3.754 (EV-ECDLP-284817). Measurements, not a
    bound. Derivation tier: the simulators are the REV-20260727-002 derivation (EV-GGM-002)
    and holant REDTEAM F1, not yet ratified by the rule-12 round routed in DEC-20260831-a9716f.
  revisit_when: >-
    An in-scope oracle is redefined to return field data about instance points or to test
    their membership in a coordinate-defined set (it then moves to
    LEAD-EXO-coordinate-revealing-oracles), or the routed review-breakthrough round corrects a
    simulator stated here.
best_measured: >-
  toy 7-8 bits, m = 3: Y_A = Y_B (40/40 cells); B/A field ops 0.0557 (split); B/C candidates
  3.754 (all preliminary)
forecloses:
- endomorphism image oracle returning group elements
- label-valued halving oracle
- incidence check oracle over a factor base given as group elements
- generic group model simulable oracle
- endomorphism-image membership oracle on a prime-order group
```

Evidence edits for Row A:
* Drop `EV-GGM-001` as support, or cite it only as superseded by EV-GGM-002.
* Add `ledger/evidence/EV-GGM-002.yaml`, `ledger/corrections/CORR-20260727-003.yaml` and
  `docs/reports/holant-h1-ggm-lemma-20261103/REDTEAM.md`.
* Keep KN-FIND-b7e091 for the CHECK interface only, with the CC-2 caveat.

### Row B: new id, reopened (name proposed)

```yaml
id: LEAD-EXO-coordinate-revealing-oracles
family: exotic
title: >-
  Coordinate-revealing oracles (x, y, full point, x-valued halving, field-valued jet and net,
  threshold C_t, degree-D coordinate tests): the GGM gives no bound
mechanism: >-
  Give the solver coordinates, or functions or predicates of coordinates, of instance points
  and hope they supply sub-birthday information or guided decomposition.
disposition: open_next_step
next_action:
  step: >-
    The GGM gives no bound for this class. Two x-queries plus free local work give log_P Q up
    to sign on any curve, so x, y, full point, x-valued halving and field-valued jet and net
    have simulation overhead Theta(sqrt N') (holant-h1-ggm-lemma-20261103 Lemma 3;
    KN-FIND-194294), and C_t and degree-D tests are non-simulable (KN-FIND-982fdf;
    ecdlp-leads-desk-20261104 low-degree-desk §1). The open question is time-bounded advantage
    from coordinate access on prime-order prime-field curves, i.e. index calculus itself
    (KN-OPEN-001). Concrete steps: (1) zero-compute: open the review-breakthrough round routed
    by DEC-20260831-a9716f with this per-oracle table as subject, in Shoup's model, separating
    label-valued from field-valued readings and CHECK from SEARCH, and record a finding that
    supersedes the x, jet and net verdicts of KN-FIND-002 and KN-FIND-b7e091; (2) literature:
    read the body of KN-LIT-7606 (Corrigan-Gibbs, Henzinger, Wu, ePrint 2026/384, EUROCRYPT
    2026; the record states the body was not read) and decide whether its elliptic-curve-point
    bound covers an algorithm that sees coordinates of a delta-fraction of elements or of a
    coordinate-defined factor base; (3) bit-valued low-degree tests proceed under
    LEAD-EXO-low-degree-query-lower-bound (rank computation); (4) field-valued x/y/full-point
    access is pursued as prime-field index calculus in the ic-prime and ic-engine rows (e.g.
    LEAD-ICE-semaev-yield-model-coset-typing, which already holds H-XOR-YIELD), priced against
    matched rho under the boundary-table-ratio rule.
  discriminates: >-
    If the CHW structured-GGM bound covers partial coordinate access, that sub-class gets a
    non-vacuous query bound Omega(min(sqrt N, 1/delta)) and can close by theorem at that delta;
    if not, no query-model closure exists for this class, and it is decided only by
    time-bounded index-calculus measurements against matched rho.
best_measured: >-
  toy 7-8 bits, m = 3, x-membership-filtered Semaev MITM: Y_A = Y_B; split-attributable
  constant-factor saving B/A 0.0557 (preliminary). Not a bound.
related:
- LEAD-EXO-augmented-oracle-ggm
- LEAD-EXO-low-degree-query-lower-bound
- LEAD-EXO-coordinate-statistic-leakage
- LEAD-ICE-semaev-yield-model-coset-typing
- LEAD-EXO-holant-decomposition-count-network
forecloses: []   # open row; the old x/y/full-point/halving phrases move here as match phrases
```

**Alternative (b)**: create no new id. Absorb the coordinate half by `related` links into
LEAD-EXO-low-degree-query-lower-bound (bit-valued tests), LEAD-EXO-coordinate-statistic-leakage
(statistics), and LEAD-ICE-semaev-yield-model-coset-typing (field-valued x access in IC). Then remove
the x, y, full-point and halving phrases from Row A's `forecloses` and title. The risk is that nobody
owns the KN-FIND-002 supersession; step (1) would need a home.

### Coverage re-map (19 rows in `coverage.tsv` point at this id)

* Move to Row B, or to LEAD-ICE-semaev-yield-model-coset-typing:
  * the x-oracle MITM measurement chain: H-ECDLP-76c89f, H-ECDLP-9b5aa9, H-ECDLP-9d5e78,
    IDEA-20260808-3f8a2b, IDEA-20260808-4f3ef4 and IDEA-20260808-7c4e9d.
* Move to Row B or LEAD-EXO-low-degree-query-lower-bound:
  * the AOM degree model: IDEA-20260806-530fdd and H-AOM-8d4a83 (`specified`, live).
* Stay on Row A:
  * Type P: IDEA-20260808-a3f7c1 / H-ECDLP-cd7072, IDEA-20260808-b8e2d4 / H-ECDLP-5cb5d0, and
    IDEA-20260808-c5f9a2 / H-ECDLP-29400c;
  * screen and method records: H-GGM-001, IDEA-20260727-004 / H-ECDLP-5a484e, and
    IDEA-20260807-0f49b6 / H-ECDLP-dd2edc.

## 6. Dependents

`grep -rn LEAD-EXO-augmented-oracle-ggm knowledge/leads` at e4a78f98 finds three places.

| row | where | load-bearing? |
|:--|:--|:--|
| LEAD-EXO-low-degree-query-lower-bound (open_next_step) | mechanism l.7-8: "LEAD-EXO-augmented-oracle-ggm closes every named oracle that the generic group model can simulate, and reopens when a publicly computable oracle that it cannot simulate appears"; related l.77; evidence l.67-68 cites KN-FIND-002 "this lead targets the oracles it cannot cover" | **Framing only.** Its H1' (Bezout, Delta) and the interpolation attack do not depend on the closure. Read with the row's title, the sentence implies x, y and full point are closed, which its own desk §1c contradicts. After a split it should name Row B as parent. |
| LEAD-EXO-holant-decomposition-count-network (open_next_step) | related l.81; evidence l.71-72 "KN-FIND-002 ... the template for H1" | **Not load-bearing.** Its H1 (l.24-30) already states that the x-oracle is not GGM-simulable "on any curve", which contradicts the row. The "template" note is stale. |
| `knowledge/leads/ecdlp/coverage.tsv` | 19 mappings (l.3, 341, 417, 422, 452, 503, 505, 567, 581, 791, 1344, 1442, 1455, 1583, 1590, 1598, 1606, 1610, 1616) | **Yes**, for triage. These records read as covered by a closure; see the re-map in §5. |

Adjacent rows do not cite the row id but rest on the same contested records. They are listed for the
Coordinator, outside the strict grep:
* LEAD-EXO-padic-jet-canonical-lift (open), l.15-16: "jet oracles are GGM-simulable with O(1) overhead
  (KN-FIND-002)". This is withdrawn by CORR-20260727-003. It does not drive the disposition.
* LEAD-EXO-elliptic-net-eds (open), l.13-14: "KN-FIND-002: net oracle GGM-simulable with O(log N)
  overhead". This holds for the label reading only. The field-valued net is non-simulable (EV-GGM-79e710
  O-5). It also cites superseded EV-GGM-001 at l.49.
* LEAD-EXO-lattes-xline-dynamics (open), part (a): "any forward-dynamics algorithm is simulable in the
  generic group model ... (KN-FIND-002 pattern)". That is true only for algorithms limited to applying
  phi_d plus equality on x-values. Field-level work on x(Q) is Type C; its part (c) treats that
  separately.
* LEAD-STR-endo-scalar-action-generic (closed_obstructed): correct as worded (End(G) = Z/N; revisit_when
  scoped to field data). It cites EV-GGM-79e710 "closed at exponent 1/2"; the overhead should read
  Theta(log N). This row survives and is the model for Row A.
* Ledger, not a lead: IDEA-20260920-376b00 l.262, 307 and 420 routes a coordinate residue to "a
  KN-FIND-002 simulability screen". For a coordinate residue that screen is either trivially
  non-simulable (Shoup) or vacuous (structured GGM).
* Record hygiene: H-GGM-001.yaml l.133 reads `status: analyzed`, while CORR-20260727-003 says
  DEC-20260727-007 returns it to `specified`.

**Checkout drift during the review.** The local checkout advanced to `9a23c9f2` while I was working.
I checked `git diff e4a78f98 HEAD` over `knowledge/leads`, `knowledge/findings`, the cited evidence and
corrections, and both report directories:
* The row under review is byte-identical at both commits.
* The holant row changed only in its anomalous-curve pointer. Its `related` entry moved from l.81 to
  l.85.
* LEAD-ICE-generic-oracle-arity-cost-floor and LEAD-EXO-invertible-hint-subset changed but cite neither
  this row nor KN-FIND-002/-b7e091.
* The dependents list is unchanged at `9a23c9f2`. Line numbers above are at e4a78f98.

## 7. What this review did not do

* It edited nothing, ran no experiment, and touched no EKS, S3 or resume checkpoint.
* It did not read the body of KN-LIT-7606. I retrieved the abstract only (eprint.iacr.org/2026/384),
  which confirms the paper exists, the EUROCRYPT 2026 venue, and an elliptic-curve-point lower bound;
  its coverage of coordinate oracles is undetermined.
* It did not independently re-derive the low-degree desk's rank claims or the Type P derivations in the
  proposed H-ECDLP records. They are cited at their stated tier.
* The net identity W(2) = psi_2(Q) = 2y(Q) and Smart's attack are recalled standard facts (provenance:
  recalled).
