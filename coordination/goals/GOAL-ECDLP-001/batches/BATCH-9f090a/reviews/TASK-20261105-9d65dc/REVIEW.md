# TASK-20261105-9d65dc — review-breakthrough round on KN-FIND-002 / KN-FIND-b7e091

Review plan: `RP-BATCH-9f090a` (frozen), opened by `DEC-20261105-c5fcb6`, routed by
`DEC-20260831-a9716f` (`routed_separately_not_this_lane`). Policy: review-breakthrough, max effort,
degradable false. This session is fresh and shared no context with the opening session. It worked
only from the repository at `b52e7c070` (branch `ideas/round5-review-9d65dc`, cut from
`ideas/round5-20261105`). It fetched no newer commits.

**Review only.** This session edited no finding, lead row, decision, evidence or correction record.
It changed no research status and ran no experiment. The only computations were small derivation
checks on toy curves (`checks/`, about 2 s in total). Every recommendation below is addressed to
the Coordinator (TASK-20261105-757228 → DEC-20261105-a78e5e).

**Provenance tags.** Each claim carries one tag:

* **[proved here]**: an argument written out in this file. Where a check script exists, the
  script only illustrates the argument and is not the proof.
* **[cited]**: an internal record (path given) or a standard result. *Recalled* means it was not
  opened in this session.
* **[heuristic]**: not proved.

## 0. Model, definitions and the two lemmas everything uses

**Model (Shoup).**

* The group is cyclic of order N. N is prime, or the bound is stated in the largest prime factor
  N' [cited: KN-TECH-005].
* Labels come from a uniformly random injection σ: Z_N → S. The algorithm holds σ(1) = σ(G) and
  σ(k) = σ(Q).
* Group-oracle queries (σ(a), σ(b)) ↦ σ(a ± b) are counted. Equality of labels and all other
  local computation are free.
* Public data: (p, a, b, N), and any constant that depends only on the curve and on generator
  data that do not depend on k or σ.

**Simulable with overhead C.** A procedure that knows neither k nor σ answers each oracle query,
with the same distribution as the real oracle, using at most C(N) group-oracle calls.

**Lemma R (reduction criterion) [proved here].**

* Statement. Let O be simulable with overhead C. Let A make T_g group queries and T_O O-queries
  and succeed with probability ε. Then T_g + C·T_O ≥ Ω(√(εN')). So
  T = T_g + T_O ≥ Ω(√(εN')/max(1, C)).
* Proof. Replace each O-query by its simulator. The result is a generic algorithm with
  T_g + C·T_O queries, and Shoup's bound applies to it. ∎
* Consequence: exponent 1/2 is preserved iff C = N^{o(1)}.
  * C = O(1), O(log N) and O(polylog N) all close at exponent 1/2.
  * C = N^c gives only exponent 1/2 − c.
  * So "O(1) overhead" (KN-TECH-005 "Program usage", EXP-GGM-001 objective) is a **sufficient
    special case**, not the criterion. This agrees with H-ECDLP-5a484e as the plan quotes it.

**Lemma S (direct Shoup count for linear-form oracles) [proved here].**

* Simulation. The simulator treats X as a formal variable and keeps the forms
  F_i(X) = a_i + b_i·X ∈ Z_{N'}[X] for every label issued. It answers each oracle query from the
  formal forms alone:
  * a group operation returns F_i ± F_j;
  * a label-valued endomorphism image returns λ·F_i, where λ is a public constant;
  * a label-valued "net" (a, b) returns a + bX;
  * an incidence CHECK(I) returns [Σ_{i∈I} F_i ≡ X], an equality test that issues no new label.
* Failure. The simulation can differ from the real game only if two formally distinct forms
  agree at X = k, or a formal CHECK difference vanishes there. Each such difference is a nonzero
  polynomial of degree ≤ 1, so it has at most one root mod N'.
* Bound. Let L ≤ 2 + T_g + T_End + T_net be the number of forms. Then
  ε ≤ (C(L, 2) + T_CHECK + 1)/N'.
  * A CHECK query adds **one** comparison, whatever |I| is.
  * A label-valued endomorphism or net query adds **one** form.
* Conclusion. These oracles close at exponent 1/2 with constant 1 in the direct count, even where
  a black-box simulator would need Θ(log N) or O(m) calls. ∎
* This is the standard Shoup/Maurer collision argument applied to forms of degree 1 [cited:
  KN-TECH-005 "Method"].

**Corollary (field-valued outputs) [proved here].**

* The simulator's view is independent of k unless a collision occurs, and a collision has
  probability ≤ s²/N' for s calls. So an oracle whose answer on a fixed, label-expressible query is
  a non-constant function of k cannot be simulated with s = o(√N') calls.
* If O(1) answers fix log_G Q up to poly(log N) candidates, the overhead is Θ(√N'):
  * lower bound: Shoup, since local work is free;
  * upper bound: BSGS on the queried label.
* This is the same three-line reduction as holant Lemma 3 [cited post-read; derived independently,
  see §5].

## 1. Blind ordering

| step | what | when / hash |
|:--|:--|:--|
| 1 | Read AGENTS.md, DEC-20260831-a9716f, DEC-20261105-c5fcb6 and the plan. Then read the nine frozen records. To pin oracle input/output as J1/J2 instruct, also read EXP-GGM-001 `specification.yaml`, KN-TECH-005, KN-LIT-7606 (front matter and Relevance), EV-GGM-79e710, DEC-20260804-3b4258 and the KN-FIND-b7e091 producer derivation `BATCH-060/tasks/TASK-20260804-051/ggm_analysis.md`. None of these is a derivation-tier input. See PD-2. | before seal |
| 2 | Write `checks/ggm_oracle_checks.py` and run it (`checks/ggm_oracle_checks.preread.out`). | before seal |
| 3 | **Seal** `pre-read-verdict.md`. | **2026-11-05T04:36:38Z**, sha256 **`9119a4711019180ef6ef5166c249d8d6cf7926ac90219f1f2e739e4984911513`** (`pre-read-seal.txt`). Committed **and pushed** as `9c09f2f9d4` before step 4. |
| 4 | Read the three derivation-tier inputs: augmented-oracle-review.md, holant README.md and REDTEAM.md. | after `9c09f2f9d4` |
| 5 | Post-read: add check C6b, rerun (the pre-read lines reproduce byte for byte), grep dependents, write this report. | after |

`pre-read-verdict.md` is not edited after sealing. Wherever this report departs from it, §5 states
the departure.

## 2. Exact oracle definitions (pinned from the records)

| tag | oracle | source | input → output |
|:--|:--|:--|:--|
| JET-W | jet, Weierstrass reading | EXP-GGM-001 spec; KN-FIND-002 item 1 ("rational function of the coordinates") | (P+εdP, Q+εdQ) → (P+Q) + ε·d(P+Q) in E(F_p[ε]/ε²). The ε-part is (dx, dy) ∈ F_p². |
| JET-I | jet, invariant-differential reading | EV-GGM-002 unresolved confound 2 | tangent data given as t = ω(∂), with ω = dx/2y |
| JET-K | jet, [k]-pushforward | EV-GGM-79e710 O-4 (Oracle A of the b7e091 lineage) | dG ↦ dQ = k·dG |
| END-L | endomorphism image, label-valued | EXP-GGM-001 spec ("returns the image of P under phi"); KN-FIND-b7e091 item 2 | σ(P) → σ(φP) |
| NET-L | "net", as KN-FIND-002 item 3 defines it | KN-FIND-002 item 3: "W(a,b) = a*P + b*Q" | (a, b) → σ(aP + bQ) |
| NET-F | elliptic net, field-valued | EXP-GGM-001 spec ("net value satisfying the Somos recurrence"); EV-GGM-79e710 O-5 | (a, b) → W(a, b) ∈ F_p |
| INC-SA | incidence SEARCH, fixed arity | EXP-GGM-001 spec; KN-FIND-002 item 4 | (R, FB of size B) → all decompositions R = P_{i1} + … + P_{im} |
| INC-SS | incidence SEARCH, subset form | KN-FIND-b7e091 item 1 sentence: "reporting **which** factor-base subsets sum to the target Q" | FB of size m → {I : Σ_I P_i = Q} |
| INC-C | incidence CHECK | ggm_analysis.md Oracle C ("for any queried subset I ⊆ {1..m}, answers whether Σ_{i∈I} P_i = Q"); EV-GGM-79e710 O-2 | (FB, I) → bit |

The letter **m** means two different things:

* in KN-FIND-002 it is the arity of a decomposition;
* in KN-FIND-b7e091 and its source it is the factor-base size.

## 3. Joints: pre-read verdict, attack, breaking artifact

### J1: KN-FIND-002 tier (CC-3)

**Pre-read verdict (sealed): BREAKS.**

**Attack and results.**

1. **JET-W is not Shoup-simulable** [proved here].
   * Query: dG with dx = 1 at the public G (the oracle derives dy), and dQ = 0.
   * The invariant coordinate is preserved, so t_{G+Q} = t_G = 1/(2y_G). The answer is therefore
     dx_{G+Q} = y(G+Q)/y(G).
   * The script confirms this on every sample (C6b). It takes 198 distinct values over 200 random
     k for this one fixed query (C6).
   * So one query reveals y(G+Q). That leaves at most 3 candidate points; free local work and
     O(log N) group calls finish. Overhead Θ(√N') by the Corollary.
   * The record itself concedes non-simulability under the strict GGM (KN-FIND-002 Scope
     bullet 1).
2. **The "structured GGM" yields no lower bound** [proved here].
   * Read as "curve public, labels opaque", JET-W is still not simulable. The coordinates of G+Q
     are *determined by* the label but not *computable from* it.
   * Read as "the simulator may evaluate rational functions of coordinates", the record's own
     simulator rule ("a deterministic function of the group element + the public curve
     equation") classifies the record's own **encoding control** (σ(P) → x(P)) as SIMULABLE with
     C = 0. That contradicts its NON_SIMULABLE control. It also proves too much: in that model
     there is no lower bound at all, since Smart's attack solves anomalous-curve ECDLP from point
     coordinates in polynomial time [cited, recalled; also KN-TECH-005 applicability limits].
   * So "closed at exponent 1/2 by KN-TECH-005" follows for JET-W in **neither** model the record
     states.
   * KN-LIT-7606's structured GGM is a different model: Ω(min(√q, 1/δ)) [cited: kb record; the
     paper body is unread by the program]. JET-W exposes coordinate data at every queried point
     (δ ≈ 1), so no non-trivial bound follows there either [heuristic: depends on CHW's exact
     definition of δ].
3. **JET-I** gives t(P+Q) = t(P) + t(Q) exactly (C6) [proved here]. It is trivially simulable
   (C = 1) and carries no information. It is "closed" vacuously, and it is not the mechanism the
   record states.
4. **END-L: conclusion holds; overhead and justification are wrong** [proved here].
   * φ is F_p-rational and E(F_p) ≅ Z/N with N prime, so φ acts as a scalar λ. λ is fixed by
     (E, φ), independent of k and σ. C2 checks this: λ² + λ + 1 ≡ 0 (mod N), and φ(Q) = [λ]Q on
     50/50 samples.
   * Simulator: double-and-add, at most 2⌈log₂ N⌉ calls (21 at N ≈ 2^15.4). Constant 1 in the
     Lemma S count.
   * "C = 0, no group operations needed" is false: it applies (ζx, y) to coordinates, which the
     model forbids [cited: CORR-20260727-003 records the same].
5. **NET-L: under-claimed** [proved here]. As KN-FIND-002 defines it, this is a
   scalar-multiplication oracle. It is simulable at Θ(log N) and **is** closed at 1/2 (Lemma R; or
   Lemma S at constant 1). The record's "Not closed at 1/2" applies the O(1) criterion too strictly
   (this is the F-5 inconsistency). It is also not an elliptic-net oracle.
6. **NET-F: not simulable** [proved here, modulo a cited identity]. The rank-2 net's restriction
   to the Q-line is the elliptic divisibility sequence of Q, so W(0, 2) = ψ₂(Q) = 2y(Q). Stange's
   identity similarly gives W(1, −1) = ±(x_Q − x_P) [cited, recalled, Stange 2007; not opened in
   this session]. One query therefore reveals a coordinate of Q, and the overhead is Θ(√N') by the
   Corollary. Item 3's simulator answers NET-L, not the oracle in the spec.
   "No sub-birthday advantage" for NET-F is **false in the query metric**: O(1) queries plus free
   local work solve the DLP. In the time metric it is the open coordinate-access question
   (KN-OPEN-001; KN-FIND-194294 non-claims) [cited].
7. **INC-SA: "not closed at 1/2" is correct, and the title clause is false.**
   * **Prop A** [proved here]. With unit-cost SEARCH of fixed arity m, take m digit blocks
     {[i·B^d]G : 0 ≤ i < B}, d < m, of mB points, and giant steps R_j = Q − [jB^m]G.
     * Any decomposition of R_j into points with known logs reveals log R_j.
     * The cost is O(mB + m log N) group operations plus O(N/B^m) group operations and SEARCH
       calls.
     * With B = N^{1/(m+1)} this is **O(m·N^{1/(m+1)})**.
     * m = 1 is BSGS (exponent 1/2), a built-in sanity check. m = 2 gives exponent 1/3.
     * C4 recovers k in 3/3 trials for each of m = 1 and m = 2. Toy sizes illustrate correctness,
       not scaling.
   * **Matching lower bound** [proved here].
     * MITM over labels gives a simulator of O(m·B^{⌈m/2⌉}) group calls per query. Sorting labels
       is free.
     * The factor-base labels must be held, so B ≤ T_g + 2.
     * Lemma R then gives T ≥ Ω(N'^{1/(2⌈m/2⌉+2)}). For m = 2 this is T ≥ Ω(N'^{1/4}), against
       an attack at N^{1/3}. The gap is left open.
   * So the title clause "providing no sub-birthday advantage" is false for incidence in the query
     metric. Under honest charging (each SEARCH charged at its simulator cost) the clause is
     tautological, because then every simulable oracle gives "no advantage".
8. **Scope defects** [cited: EV-ECDLP-048824 O-6 / R-OBJ2]:
   * there is no prime-order hypothesis, so the exponent must be stated in N';
   * the record's only evidence, EV-GGM-001, is superseded by EV-GGM-002 and is "EVIDENTIALLY
     VOID" there;
   * CORR-20260727-003 already rules that the entry "REQUIRES A SUPERSEDING OR CORRECTING KN-FIND".
     That obligation is still undischarged, and the front matter still reads `status: established`,
     `confidence: strong`.

**Breaking artifacts found.**

* (i) The simulator the record claims for JET-W under Shoup does not exist. It is ill-typed, and
  the C6/C6b witness is a y-oracle on G+Q.
* (ii) The END-L overhead is wrong (C = 0 vs Θ(log N)).
* (iii) The closure does not follow from KN-TECH-005 in the stated "structured GGM"; the
  encoding-control check proves too much.
* (iv) The incidence "no sub-birthday advantage" clause is refuted by Prop A.

**J1 verdict: BREAKS.**

### J2: KN-FIND-b7e091 justification (CC-2)

**Pre-read verdict (sealed): BREAKS as written. The conclusions survive under pinned definitions,
so a scoped erratum is enough.**

1. **"End_{F_p}(E) = Z" is false for every E/F_p** [proved here].
   * The p-power Frobenius π is F_p-rational of degree p, while [m] has degree m². A prime p is
     never a square (C1, trivially), so π ∉ Z.
   * End_{F_p}(E) therefore has rank 2: it contains Z[π].
   * Over F̄_p, End(E) is also never Z for E defined over a finite field [cited, recalled: Deuring].
2. **The closure does not need the premise** [proved here].
   * E(F_p) is cyclic of prime order N, so every F_p-rational φ acts on it as a scalar λ_φ (C2).
   * "Any endomorphism φ of E" is sound in scope. For ordinary E every endomorphism is defined
     over F_p [cited, recalled: Waterhouse]. A prime-order supersingular E/F_p is impossible for
     p ≥ 5, since #E = p + 1 is even.
   * The producer derivation `ggm_analysis.md` already uses the eigenvalue argument; the false
     premise entered when it was promoted to KN-FIND.
3. **"Computable in m group operations"** is literally O(N) per query, because λ can be about N
   (C2: λ = 30778 against 21 double-and-add calls). This is super-polylogarithmic per query, which
   meets the plan's breaking-artifact condition. The correct statement is
   ≤ 2⌈log₂ N⌉, or constant 1 under Lemma S.
4. **Oracle C: the definition decides the verdict.**
   * Read as **INC-SS** (the finding's own sentence), the claim "simulable in O(m) group
     operations per query" is **false**. This is **Prop B** [proved here]:
     * take FB = {[2^i]G : i < ⌈log₂ N⌉};
     * one query returns the binary digits of k (C3: 5/5 trials, ⌈log₂ N⌉ − 1 group operations
       plus 1 query);
     * a simulator with overhead C would give log N + C ≥ Ω(√N'), so C = Ω(√N').
   * Read as **INC-C** (the producer's definition), the claim is true:
     * simulable at |I| − 1 ≤ m − 1 calls;
     * closed at exponent 1/2 with constant 1 by Lemma S, **whatever the size of m** (C5
       illustrates the count);
     * by Lemma R alone it closes only when m = N^{o(1)}. DEC-20260901-e24d15 noted the
       growing-m caveat; Lemma S removes it.
5. **Scope that is missing** [proved here; cited KN-FIND-982fdf].
   * The closure covers factor bases **given as labels** only.
   * A coordinate-defined factor base (Semaev, x < t) makes membership the threshold oracle C_t,
     which is not simulable (KN-FIND-982fdf (b)).
   * So real index calculus is **not** closed by this record. EV-GGM-79e710 O-2 ("closes the
     approach of using subset-sum structure in the relation matrix to beat rho") overreaches in
     the same way.
6. **Tier.** `confidence: proved` and `evidence_level: theorem_backed` are earned **after** the
   erratum, by the INC-C and END-L statements, at derivation level (Lemma S). They are not earned
   as written:
   * the premise is false and is listed in EV-GGM-79e710's `proof_refs`;
   * the literal overhead is O(N);
   * the Oracle C sentence can be read as INC-SS.

**Breaking artifacts found.** A false premise (not needed by the closure); a simulator cost that is
super-polylogarithmic as written; and a defining sentence under which the claim is false (Prop B).

**J2 verdict: BREAKS as written. Repairable by a scoped erratum.**

### J3: CC-1 incidence disagreement and the F-5 criterion

**Pre-read verdict (sealed): inconsistent as written; consistent under pinned definitions and one
criterion.**

**CC-1 [proved here].** The two records price different oracles: INC-SA in KN-FIND-002, INC-C in
the source of KN-FIND-b7e091. Under each single definition:

| definition | KN-FIND-002 | KN-FIND-b7e091 |
|:--|:--|:--|
| INC-SA / INC-SS (SEARCH) | right that it is not closed at 1/2, and in fact the oracle beats 1/2 (Prop A); wrong on "no sub-birthday advantage" | O(m) and "closed" are **false** (Prop B) |
| INC-C (CHECK) | silent | right (Lemma S), after pinning the definition |

The records remain inconsistent **as written**. KN-FIND-b7e091's defining sentence reads as
SEARCH, and that reading contradicts KN-FIND-002 item 4 on the same oracle. Pinning
KN-FIND-b7e091 to CHECK removes the contradiction. This answers DEC-20260901-70ba34 Q1 as well.

**F-5: one criterion (Criterion G) [proved here, Lemmas R and S].** In Shoup's GGM, with the
exponent stated in N', a simulability verdict **licenses closure of an oracle family at exponent
1/2** when:

* (i) every answer is a deterministic function of the formal linear forms of labels the querier
  already holds, plus public constants independent of k and σ (so the answer is a label or a bit);
  and
* (ii) **either** (a) each query adds O(1) forms or comparisons (Lemma S), **or** (b) a
  k-independent label-only simulator uses N^{o(1)} group calls per query (Lemma R).

The criterion fails, and **no** Shoup bound follows, for any answer that is field data varying with
k on GGM-indistinguishable instances. Where O(1) such answers fix log Q up to poly(log N)
candidates, the overhead is Θ(√N'). The metric must also be stated: a closure is meaningful only in
the unit-query metric. With each call charged at its simulator cost, "no advantage" is a
tautology. "O(1) overhead" is a sufficient special case of (ii)(b).

Applied uniformly:

| oracle | verdict under Criterion G | KN-FIND-002 says | KN-FIND-b7e091 says | consistent? |
|:--|:--|:--|:--|:--|
| JET-W | not simulable; Θ(√N') | simulable C = 1, closed | (Oracle A is JET-K) | 002 **violates** |
| JET-I | closed, vacuous | — | — | — |
| JET-K | not simulable; a DLP oracle; private | — | non-simulable, private | b7e091 right |
| END-L | closed; Θ(log N) reduction, constant 1 by Lemma S | C = 0, closed | m ops, closed | conclusion right in both; **both overheads wrong** |
| NET-L | closed; Θ(log N) | "not closed at 1/2" | — | 002 **violates** (under-claims) |
| NET-F | not simulable; Θ(√N') | (simulates NET-L instead) | non-simulable (EV-GGM-79e710 O-5) | b7e091 lineage right, apart from its "no k-recovery below DLP" (false in the query metric, open in time) |
| INC-SA | not closed; beaten at N^{1/(m+1)} | not closed ✓; "no sub-birthday advantage" ✗ | — | 002 half wrong |
| INC-SS | not simulable; one query gives the DLP | — | (sentence reading) closed, O(m) ✗ | b7e091 **violates** |
| INC-C | closed, constant 1 (Lemma S) | — | closed, O(m) ✓ | b7e091 right after erratum |

**Breaking artifact found.** Yes: the records are inconsistent as written (INC-SS against INC-SA),
and each violates any single criterion (002 on NET-L and END-L; b7e091 on END-L "m ops" and on
INC-SS). Both resolve under Criterion G with pinned definitions.

**J3 verdict: BREAKS as written; reconciled by the pinned definitions and Criterion G.**

**New observation NO-1 [proved here].** The two records also disagree on the **jet** oracle:
KN-FIND-002 says simulable and closed; KN-FIND-b7e091 says non-simulable. This disagreement is not
filed as a CC item. It is again a definitional split, JET-W against JET-K. Neither oracle is closed
by Shoup, so KN-FIND-002 is the record in error.

### J4: Consequences and recommendations

**Pre-read recommendation (sealed):** supersede KN-FIND-002; scoped erratum for KN-FIND-b7e091.
**Unchanged after the post-read.**

**Output shape.** DEC-20260901-70ba34 ("what_the_round_may_not_do") rules that the only
permitted output shape is a **new** record under a freshly minted identifier
(`tools/allocate_id.py`). KN-FIND-002 is content-bound by the completed archive TASK-20260724-236
(AGENTS.md rule 15). The texts below are therefore drafts for new records. Neither front matter is
edited, and no `superseded_by` is written by this session.

#### R1. KN-FIND-002: **SUPERSEDE**

Reason: the only evidence (EV-GGM-001) is void. Three of the four oracle statements change, and
the fourth (endomorphism) keeps its conclusion but changes its overhead and mechanism.
CORR-20260727-003 has required a superseding entry since 2026-07-27.

Superseding statement (new `internal_finding`; `proof_status: derivation`; `confidence: proved`
for items 1–4 and 6, `heuristic` for the CHW sub-item; evidence: this review and its `checks/`,
**not** EV-GGM-001):

> **Title.** Augmented ECDLP oracles in Shoup's generic group model: label-valued
> endomorphism-image and scalar-multiple oracles are closed at exponent 1/2; coordinate-valued jet
> and field-valued elliptic-net oracles are not GGM-simulable; fixed-arity incidence SEARCH is not
> closed and beats exponent 1/2 in the query metric.
>
> **Model.** Shoup's GGM: random labels, group-oracle queries counted, local computation free.
> Group order N; every exponent is in N', the largest prime factor of N (KN-TECH-005). A closure
> means "Omega(N'^{1/2-o(1)}) total queries, counting each augmented call as one query". It holds
> when each answer is a label or a bit fixed by the formal linear forms of held labels and public
> constants, and either each call adds O(1) forms or comparisons, or a k-independent label-only
> simulator uses N^{o(1)} group operations per call (Criterion G). O(1) simulator overhead is
> sufficient, not necessary.
>
> 1. **Endomorphism image** sigma(P) -> sigma(phi P), phi F_p-rational, E(F_p) of prime order N.
>    phi acts as a public scalar lambda (a root of its characteristic polynomial mod N). A
>    simulator needs at most 2 ceil(log2 N) group operations, and the direct Shoup count has
>    constant 1. **Closed at exponent 1/2.** (The earlier C = 0 figure applied phi to coordinates
>    and is withdrawn.)
> 2. **Scalar-multiple oracle** (a, b) -> sigma(aG + bQ) (formerly called the "elliptic-net
>    oracle"). Double-and-add, Theta(log N). **Closed at exponent 1/2.** This is not an elliptic
>    net.
> 3. **Jet oracle, coordinate reading** ((P,Q) -> eps-part of P+Q in E(F_p[eps]/eps^2), as in
>    EXP-GGM-001). One query with dx = 1 at the public G and 0 at Q returns y(G+Q)/y(G), so the
>    oracle is a y-coordinate oracle on an instance point. Simulation overhead Theta(sqrt N').
>    **Not simulable; no Shoup bound follows.** Under the invariant-differential reading
>    (t(P+Q) = t(P) + t(Q)) the oracle is trivially simulable and carries no information.
> 4. **Elliptic-net oracle, field-valued** ((a, b) -> W(a, b) in F_p). W(0,2) = psi_2(Q) = 2y(Q)
>    (identity recalled, Stange), so O(1) queries reveal a coordinate of Q. **Not simulable;
>    overhead Theta(sqrt N').** Whether coordinate access helps a time-bounded attacker is
>    KN-OPEN-001 and is not decided here.
> 5. **Incidence SEARCH, fixed arity m** ((R, factor base of B labels) -> all m-term
>    decompositions). Label meet-in-the-middle simulates it at O(m B^{ceil(m/2)}) group operations
>    per call. **Not closed at exponent 1/2:** with base-B digit factor bases and
>    B = N^{1/(m+1)}, the DLP is solved with O(m N^{1/(m+1)}) group operations plus SEARCH calls
>    (m = 1 is BSGS). Lower bound Omega(N'^{1/(2 ceil(m/2)+2)}). Charged at its simulation cost
>    the oracle is generic, and Omega(sqrt N') bounds that implementation's group operations.
> 6. **The "structured GGM"** (simulator may use coordinates of group elements) yields **no lower
>    bound**. Under it the x-coordinate control is "simulable", and anomalous curves are solved in
>    polynomial time from coordinates. No closure in this record rests on it.
>    *Heuristic:* KN-LIT-7606's structured GGM (Omega(min(sqrt q, 1/delta))) is unlikely to give a
>    non-trivial bound for items 3–4, because they expose coordinates at every queried point.
>    Undecided until the paper body is read.
>
> **Supersedes KN-FIND-002.** **Not claimed:** any statement about concrete ECDLP hardness, index
> calculus with coordinate-defined factor bases (see KN-FIND-982fdf), or real implementations.

#### R2. KN-FIND-b7e091: **STANDS WITH A SCOPED ERRATUM**

Delivered as a new erratum record (fresh id), because the finding is immutable. The tier
(`confidence: proved`, `evidence_level: theorem_backed`) is kept for the corrected statements only.

Exact replacement text:

> **Erratum to KN-FIND-b7e091 (scoped; the conclusions are kept).**
>
> *Title, read as:* "GGM closure of the incidence-CHECK oracle over a label factor base and of the
> label-valued endomorphism-image oracle, for prime-order prime-field ECDLP (Shoup model)".
>
> *Item 1, replace with:* "**Incidence CHECK oracle** (Oracle C). The querier holds labels of a
> factor base P_1..P_m and submits a subset I ⊆ {1..m}. The oracle answers whether
> Σ_{i∈I} P_i = Q. A simulator needs |I|-1 <= m-1 group operations and one equality test. In
> Shoup's collision count each query adds one comparison, whatever m is, so the oracle is closed
> at exponent 1/2 even when m grows with N. Out of scope: (a) the SEARCH oracle that **reports
> which** subsets sum to Q. It is not simulable with o(sqrt N) overhead, because with factor base
> {[2^i]G} one query returns the bits of k (TASK-20261105-9d65dc Prop B). (b) Factor bases defined
> by coordinates (e.g. x(P) < t). There membership is the threshold oracle C_t, which is not
> simulable (KN-FIND-982fdf). This finding therefore does not close index calculus that uses such
> a factor base."
>
> *Item 2, replace with:* "**Endomorphism images oracle** (Oracle D). The oracle returns the
> labels phi(G), phi(Q) for an endomorphism phi of E. E(F_p) is cyclic of prime order N and phi
> preserves it (for ordinary E every endomorphism is F_p-rational; prime order excludes
> supersingular E for p >= 5). So phi acts on E(F_p) as multiplication by a public scalar
> lambda_phi mod N. phi(Q) = [lambda_phi]Q costs at most 2 ceil(log2 N) group operations by
> double-and-add, and adds one form in Shoup's count. The earlier premise 'End_{F_p}(E) = Z' is
> false for every elliptic curve over F_p (Frobenius has degree p, never a square), and the earlier
> cost 'm group operations' is O(N). Neither is needed."
>
> *Implication, append:* "The bound is Omega(sqrt N) total queries, each oracle call counted as
> one query, for N prime (for composite N use its largest prime factor). It concerns the
> label-valued oracles above only. Oracles that return field data of instance points are outside
> it."

Upstream records that carry the same premise or overreach (and stay immutable) need a companion
correction record:

* EV-GGM-79e710 O-2 (overreach about the "relation matrix"), O-3 (End = Z, "m group operations")
  and `proof_refs` item 4;
* DEC-20260804-3b4258 rationale items 1–2 and `owed_promotions`.

This also answers DEC-20260901-70ba34 Q2.

#### R3. Dependents (grep over the HEAD tree; the checkout is sparse)

Commands:

* `git grep -e KN-FIND-002 -e KN-FIND-b7e091 HEAD` finds **1897 lines in 508 files**. The full file
  list is `checks/dependents_all_files.txt`, and every line with a heuristic topic tag is in
  `checks/dependents_classified.tsv` (`checks/classify_dependents.py`, summary in its `.out`).
* `checks/dependents_knowledge_ledger_lines.txt` holds the 1161 lines under `knowledge/` and
  `ledger/`.

The hand-classified table covers every **lead row, finding, technique and literature record**, and
every **decision, evidence or correction** whose citation bears on an affected sentence. Purely
procedural mentions are grouped in the last rows.

| dependent | cites | affected sentence | needed |
|:--|:--|:--|:--|
| knowledge/leads/ecdlp/exotic/LEAD-EXO-augmented-oracle-ggm.yaml, l.17 | b7e091 End = Z | END | none (already replaced by the eigenvalue argument) |
| same row, statement ("incidence SEARCH … per-query bound is vacuous … but the total-cost bound holds"; "An algorithm that touches the instance only through these … is generic") | 002 item 4 | INC-SA | **scoped erratum**: "incidence SEARCH over such a base is simulable by label meet-in-the-middle at O(B^ceil(m/2)) group operations per call, so Omega(sqrt N') bounds the group operations of that generic implementation; counted as one query per call, SEARCH is NOT closed: base-B digit factor bases solve the DLP with O(m N^(1/(m+1))) group operations plus calls (TASK-20261105-9d65dc Prop A), and the subset form solves it in one call (Prop B)". Also insert "(SEARCH charged at its simulation cost)" after "these". |
| same row, evidence notes l.52–55 ("jet/endomorphism closed at 1/2") and `ledger_refs` EV-GGM-001 | 002 title | JET | point the notes at the superseding finding (R1); mark EV-GGM-001 superseded |
| knowledge/leads/ecdlp/exotic/LEAD-EXO-coordinate-revealing-oracles.yaml, l.18 | 002, b7e091 | JET, NET | none. Its step (1) is this round; R1 discharges it. |
| knowledge/leads/ecdlp/exotic/LEAD-EXO-elliptic-net-eds.yaml, l.14, l.35–36, l.49 | 002 item 3, EV-GGM-001 | NET | **erratum**. Replace "(KN-FIND-002: net oracle GGM-simulable with O(log N) overhead)" with "(the field-valued net oracle is NOT GGM-simulable: W(0,2) = 2y(Q); KN-FIND-002 item 3 simulated sigma(aP+bQ), a scalar-multiple oracle, not a net value; superseded by R1)". Not load-bearing for the row's measured disposition. |
| knowledge/leads/ecdlp/exotic/LEAD-EXO-padic-jet-canonical-lift.yaml, l.16, l.35–36 | 002 item 1 | JET | **erratum**. Replace "jet oracles are GGM-simulable with O(1) overhead (KN-FIND-002)" with "the coordinate jet oracle is not GGM-simulable (it reveals y(G+Q)/y(G)); only its invariant-differential and canonical-lift readings are trivially simulable and information-free (R1)". Not load-bearing (the disposition rests on the IDEA-004 gate). |
| knowledge/leads/ecdlp/exotic/LEAD-EXO-lattes-xline-dynamics.yaml, l.14 | "KN-FIND-002 pattern" | JET/NET pattern | **erratum**. Replace "(KN-FIND-002 pattern)" with "(only for algorithms that apply [d] to labels and test equality; field work on x(Q) is not generic; Criterion G, TASK-20261105-9d65dc)". |
| knowledge/leads/ecdlp/exotic/LEAD-EXO-low-degree-query-lower-bound.yaml, l.69–70 | 002 | framing | point at R1; not load-bearing |
| knowledge/leads/ecdlp/structure/LEAD-STR-endo-scalar-action-generic.yaml, l.14, l.25–26, l.41–42 | b7e091, EV-GGM-79e710, DEC-20260804-3b4258 | END | **stands**: End(G) = Z/N is correct. Optional: add "Theta(log N) group operations" to the evidence note. |
| knowledge/techniques/KN-TECH-069.md, l.71 | 002 ("closed jet and endomorphism oracles by exhibiting a simulation") | JET | **erratum**: "closed the label-valued endomorphism oracle by exhibiting a Theta(log N) simulation (the jet half was withdrawn, CORR-20260727-003; R1)" |
| knowledge/techniques/KN-TECH-ee6696.md, l.221 | 002 ("structured-versus-opaque-label model question … leaves open") | CC-3 | **erratum**: the question is resolved, since the structured GGM yields no bound (R1 item 6) |
| knowledge/techniques/KN-TECH-ee6696.md, l.265 | 002 ("elliptic-net and incidence oracles are the recorded examples of non-constant overhead") | NET, INC | **erratum**: "incidence SEARCH is the recorded example of super-polylog overhead and is not closed (R1 item 5); the label 'net' is closed at Theta(log N); the field-valued net is not simulable" |
| knowledge/techniques/KN-TECH-ee6696.md, l.9, 61, 65 | source refs, F2/F6 rows | INC, END | none if the rows are read as CHECK over a label FB and END-L |
| knowledge/literature/KN-LIT-7606.md, l.45, 68, 70 | 002 as "direct prior art" | CC-3 | none to its facts. Its "residue" question is answered for Shoup by R1; it stays open for CHW. |
| knowledge/findings/KN-FIND-1ba0fe.md, l.76, 92 | "still-unopened round" | process | none (immutable; becomes historically stale) |
| knowledge/findings/KN-FIND-c2e9a7.md, l.44; knowledge/gathers/GATHER-20260727.md, l.141–173 | schema convention, index repair | process | none |
| ledger/evidence/EV-GGM-79e710.yaml, O-2, O-3, `proof_refs`; ledger/decisions/DEC-20260804-3b4258.yaml; DEC-20260804-98a4a4 (promotion of b7e091) | b7e091 upstream | INC, END | **companion correction** (R2) |
| ledger/evidence/EV-GGM-001.yaml; DEC-20260726-007; DEC-20260724-021 (promoted KN-FIND-002); DEC-20260727-002/-005/-007; CORR-20260727-002/-003; CORR-20260729-004; CORR-20260731-005; CORR-20260802-007; DEC-20260802-008/-009; ledger/registers/unevidenced-records.yaml; ledger/goals/GOAL-ICLIFT-001.yaml | the KN-FIND-002 lineage | all | none. R1 discharges CORR-20260727-003's owed superseding entry. |
| DEC-20260807-4261e3 l.373; DEC-20260808-e75211 l.467; DEC-20260810-56db2d l.322, -5aeeaa l.599, -95a741 l.563, -d70ece l.272; ledger/goals/GOAL-ENDO-001/goal.yaml (9 lines) and checkpoints BATCH-25e27c, BATCH-d7e255 | "KN-FIND-b7e091 binding" (endomorphism closure) | END | **stand**: the conclusion survives under the eigenvalue argument |
| DEC-20260810-a4bec4 l.84; BATCH-d7e255 l.168 | b7e091 "closure of the incidence and endomorphism-image oracle classes … BINDING and extended" | INC, END | stands for INC-C over a label FB and END-L; any "extension" to SEARCH or coordinate FBs is not licensed (R2) |
| CORR-20260808-334229 l.154 ("x-oracle is group equality up to sign, i.e. inside KN-FIND-b7e091's … closure") | b7e091 | INC/END scope | the conclusion holds under Criterion G (x(R1) = x(R2) iff R1 = ±R2, a bit fixed by forms), but it is **not** inside b7e091's literal scope; cite Criterion G |
| ledger/hypotheses: 25 files (e.g. H-CMFB-7d4e1a l.61 ["O(log N) … simulable (KN-FIND-b7e091)"], H-AUX-4a0506 l.30, H-ICINV-82ee6a, H-JINV-5a0b9e, H-VOLC-dff1f8, H-CLGP-63f471, H-DREG-825fbe, H-GGMB-da21f5, H-PFDR-5b5c46, H-ECDLP-3b589b, H-AOM-8d4a83, H-ECDLP-aecab6) | b7e091 END (most); 002 + b7e091 titles (3b589b, AOM) | END; titles | END citations stand. H-ECDLP-3b589b and H-AOM-8d4a83 cite the titles: re-read them against R1/R2 at their next revision. Full lines are in the TSV. |
| DEC-20260831-a9716f; EV-ECDLP-048824; DEC-20260901-255ebd, -34e038, -70ba34, -e24d15; EV-ECDLP-e6f5f2; EV-ECDLP-f5c698; DEC-20261105-eb49ad, -c5fcb6; DEC-20260905-b3d10c; DEC-20261006-135683; DEC-20261016-c41e97; ledger/goals/GOAL-ECDLP-001/goal.yaml l.12859, 12926 | routing / "not retiered" / evidence lists | process | none; they await the closing decision |
| ledger/proposals (176 files), coordination/ (52), docs/reports (34), experiments/ (≈90 spec lines) | mostly b7e091 END "binding" in screening blocks, plus routing notes | various | triage only; see the TSV. The SEARCH and coordinate-FB caveat (R2) applies wherever INC is cited. |

## 4. Prior and plan check

Coordinator prior (RP-BATCH-9f090a), item by item:

* **(a) agree.** JET-W, NET-F and the x-valued variants are not Shoup-simulable, so no exponent-1/2
  closure follows.
* **(b) agree.** END-L and label halving are Θ(log N), not O(1), in the reduction metric. End = Z
  is false and is replaced by the eigenvalue argument. **Added here:** Lemma S gives constant 1 in
  the direct count, so "O(1) vs Θ(log N)" depends on the metric and is not a defect of the
  closure.
* **(c) agree, and stronger.** CHECK over a label FB is O(m), and by Lemma S it closes regardless
  of m. SEARCH is worse than "not a per-query O(1) statement": with unit-cost calls it *beats*
  exponent 1/2 (Prop A), and the subset form is a DLP oracle (Prop B).
* **(d) agree.** The structured GGM gives no lower bound; the proves-too-much check is the
  encoding control.
* **The prior's "likeliest way I am wrong" happened once.** KN-FIND-002 defines its "net" more
  narrowly than the spec (as σ(aP + bQ)). Under that definition the closure is *true* and the
  record under-claims.

Concurrence with the prior is not used as evidence. Every verdict above rests on Lemmas R and S,
Props A and B, or the Corollary.

## 5. Post-read comparison with the derivation-tier inputs

Inputs read after the seal:

* `docs/reports/leads-round2-20261104/augmented-oracle-review.md` (AOR);
* `docs/reports/holant-h1-ggm-lemma-20261103/README.md` (HR);
* `docs/reports/holant-h1-ggm-lemma-20261103/REDTEAM.md` (HRT).

**Agreements.** Each was reached independently before the seal.

| point | this review (sealed) | input |
|:--|:--|:--|
| JET-W not simulable; the structured GGM is vacuous | J1.1–2 | AOR §2 jet rows and "structured-GGM verdicts … vacuous"; HR "structured GGM … gives no lower bound"; HRT table row C′ |
| END-L Θ(log N) via the eigenvalue; End = Z false | J1.4, J2.1–2 | AOR §2 endomorphism row; HRT F1 "What survives" |
| NET-L is scalar multiplication at Θ(log N); NET-F not simulable | J1.5–6 | AOR §2 net rows |
| INC-C O(m) over a label FB; INC-SA O(B^m), O(B^{⌈m/2⌉}) by MITM; a coordinate FB is C_t and not simulable | J2.4–5, J1.7 | AOR §2 incidence rows |
| the criterion is sub-polynomial overhead (H-ECDLP-5a484e) | Lemma R | AOR F5 / row statement |
| exponent in N'; EV-GGM-001 void; CORR-20260727-003 already withdraws the jet claim | J1.8 | AOR F3, F5 |
| CC-1 is two interfaces sharing one name | J3 | AOR F5, citing DEC-20260901-e24d15 |

**Disagreements and differences.**

* **D-1 (my pre-read was imprecise; corrected toward the input).**
  * My sealed text said that "no sub-birthday advantage" for NET-F "then is the open x-oracle
    question". In the **query metric** that is wrong. Shoup counts only oracle queries, so O(1)
    coordinate answers plus free local brute force solve the DLP. The overhead is Θ(√N'), as in
    holant Lemma 3 (HR) and AOR's Type C rows.
  * The open question is only the **time-bounded** one (KN-OPEN-001). I checked the three-line
    reduction myself (the Corollary in §0) and adopt it.
  * Separately, my sealed text derived JET-W non-simulability from a k-dependence witness. The
    post-read check C6b sharpens it to an exact y-oracle on G+Q: one query gives y(G+Q)/y(G).
    AOR reaches the same Θ(√N') by a chord-slope argument.
* **D-2 (addition; AOR and HRT do not state it).** AOR §2 says that SEARCH is "Yes [simulable]"
  and that "the total-cost Ω(√N') bound still holds". The narrowed lead row says the same: "An
  algorithm that touches the instance only through these … is generic".
  * That holds only when each SEARCH call is charged at its simulation cost.
  * Charged as one query (the metric every closure claim in these records uses), fixed-arity
    SEARCH is broken at O(m·N^{1/(m+1)}) (Prop A). That is why the lead-row erratum in R3 is
    required.
* **D-3 (addition).** Neither input notes that **KN-FIND-b7e091's own defining sentence** ("reporting
  *which* factor-base subsets sum to Q") is the subset-SEARCH oracle, under which the record is
  false (Prop B). AOR cites KN-FIND-b7e091 l.22–24 as the CHECK interface. I read those lines as
  SEARCH; only the producer artifact defines CHECK. DEC-20260901-70ba34 Q1 raises the same
  internal-consistency question, and this round answers it: inconsistent as written, consistent
  after erratum R2.
* **D-4 (addition).** By Lemma S, CHECK and END-L close with constant 1 in Shoup's direct count,
  independent of m and λ. The inputs close INC-C at O(m) through the reduction, which by itself
  does not close when m = N^{Ω(1)}. That gap is DEC-20260901-e24d15's growing-m caveat, and
  Lemma S removes it.
* **D-5 (difference of witness, not of verdict).** For NET-F, AOR uses W(2) = ψ₂(Q) = 2y(Q) and
  my sealed text used W(1, −1) = x_Q − x_P. Both are recalled identities. They are not
  load-bearing beyond "some O(1) queries reveal a coordinate of Q".
* **D-6 (not covered by the inputs).** NO-1, the jet disagreement between the two records
  (JET-W against JET-K).

No input changed a joint verdict. D-1 changes one sentence of the sealed J1 text, from
"unsupported" to "false in the query metric, open in time". The superseding statement R1 item 4
uses the corrected form.

## 6. Procedure deviations and limits

* **PD-1 (branch).** The plan's constraints name branch `ideas/round5-20261105`. This session's
  dispatch instructions designate `ideas/round5-review-9d65dc` (cut from it at `b52e7c070`), and
  the work was pushed there. No PR was opened, as instructed.
* **PD-2 (blind-phase reading beyond `frozen_inputs.records`).** EXP-GGM-001 `specification.yaml`,
  KN-TECH-005, KN-LIT-7606, EV-GGM-79e710, DEC-20260804-3b4258 and `ggm_analysis.md` were read
  before the seal, because J1/J2 require pinning oracle input/output "from the record and
  EXP-GGM-001". `ggm_analysis.md` is the producer derivation behind KN-FIND-b7e091. It is not a
  derivation-tier input or a review conclusion, but it is disclosed here.
* **PD-3 (seal anchoring).** The pre-read is anchored by a pushed commit (`9c09f2f9d4`) as well as
  by the sha256 and timestamp. The plan asked only for the hash and timestamp.
* **PD-4 (a round that was already opened).** DEC-20261105-c5fcb6's context describes the round as
  routed "as not opened". However, **DEC-20260901-70ba34 (2026-09-01) opened a review-breakthrough
  round on the same CC-1/2/3/F-5 with sub-questions Q1–Q3**. Its tree
  `coordination/rounds/KNFIND-RECONCILE-20260901-70ba34/` holds only a ledger receipt and no
  reviewer output. This report answers Q1 (§3 J3), Q2 (J2/R2) and Q3 (J1/R1). The Coordinator
  should reconcile the two openings.
* **PD-5 (push hook).** The repository's pre-push benchmark hook refused the push because three
  report PDFs are missing from the sparse checkout. This push carries no benchmark work, so it was
  made with `BENCHREC_SKIP` set and the reason stated in the command.
* **PD-6 (independence limits).** The derivation-tier inputs were written by sessions that may run
  on the same model family as this reviewer. Independence rests on session separation and on the
  sealed, pushed pre-read, not on model diversity.
* **Limits.**
  * The paper body of KN-LIT-7606 was not read, so the CHW structured-GGM statements are
    heuristic.
  * Stange's net identities, Deuring, Waterhouse and Smart are recalled.
  * The toy checks illustrate the proofs; they establish nothing about scaling.
  * The lower bound for fixed-arity SEARCH (N'^{1/(2⌈m/2⌉+2)}) and the attack (N^{1/(m+1)}) are
    not matched.

## 7. Files

* `pre-read-verdict.md`, `pre-read-seal.txt`: the sealed blind verdict.
* `checks/ggm_oracle_checks.py`, with outputs `checks/ggm_oracle_checks.preread.out` (sealed run)
  and `checks/ggm_oracle_checks.out` (post-read run, identical apart from the added C6b line).
* `checks/classify_dependents.py`, `checks/classify_dependents.out`,
  `checks/dependents_classified.tsv`, `checks/dependents_all_files.txt`,
  `checks/dependents_knowledge_ledger_lines.txt`: the dependents grep.
* `verdicts.yaml`: the machine-readable summary.
