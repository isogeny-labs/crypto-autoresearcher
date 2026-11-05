# Cryptographic assumption attack corpus

Date: 2026-11-01. Status: **prioritized formal-audit plan; five frozen Lean
targets are pointers, not discharged proofs or security findings**.

## Question and result

Which routinely repeated claims around elliptic-curve cryptography, polynomial
protocols, Fiat--Shamir, batching, commitments, and SNARKs can be converted into
small statements that Lean can either refute by counterexample or prove with
every premise visible?

This search produced a three-tier corpus. The first tranche freezes five
high-leverage trust-boundary targets:

1. integer equality versus equality after reduction into a circuit field;
2. ambient acceptance versus designated prime-subgroup membership;
3. adaptive cancellation in random-linear-combination batch checks;
4. formal polynomial equality versus equality as finite-field functions; and
5. the exact hypotheses of Schnorr two-transcript extraction.

These were selected because each has a small decisive countermodel, a precise
repair theorem, and direct relevance to proof-system or ECC interfaces. They do
not assert a vulnerability in an implementation. The remaining queue is ranked
below rather than prematurely frozen into theorem statements.

## Classification discipline

Every corpus item must receive exactly one primary label. A result may move
labels only when its exact statement or evidence changes.

| Label | Meaning | What a Lean artifact can establish |
| --- | --- | --- |
| **false-as-stated** | A universal or implication has a concrete model satisfying its premises and falsifying its conclusion. | Kernel-check the witness, premises, and negated conclusion. |
| **conditionally proved** | The conclusion follows after adding explicit algebraic, distributional, encoding, or order hypotheses. | Prove the implication and keep every premise in the theorem type. |
| **model-relative** | The claim is valid only in a named model such as the generic group model, ROM, AGM, or QROM. | Formalize the model and prove a theorem inside it; never erase the qualifier. |
| **open computational assumption** | No theorem currently proves the claimed real-world hardness, and the claim is intended as an assumption. | Check reductions and finite countermodels, but not prove or disprove the unbounded assumption from ordinary mathematics alone. |
| **unconnected interface** | Both endpoint statements may be sound, but no theorem connects the implementation, encoding, sampler, or algorithm to the abstract premise. | State and prove the missing refinement/transport theorem or record it as open. |

“Trust-me-bro” is therefore not a mathematical status. The actionable diagnoses
are a false quantifier, a missing premise, a model boundary, an explicitly open
assumption, or a missing interface.

## Source and repository review

The following sources were read before choosing the queue. “Retrieved” means
the relevant primary text or official specification was inspected; it does not
mean every theorem in the source was independently re-proved.

| Source | Boundary used here | Provenance |
| --- | --- | --- |
| Jacobson--Koblitz--Silverman--Stein--Teske, *Analysis of the Xedni Calculus Attack* (DCC 20, 2000) | Theorem 4.1 is explicitly conditional; its height/discriminant, Lang, approximate-relation, and repeated-trial interfaces must remain visible. | [retrieved author copy](https://pages.cpsc.ucalgary.ca/~jacobs/PDF/xedni.pdf) |
| Shoup, *Lower Bounds for Discrete Logarithms and Related Problems* (EUROCRYPT 1997) | The lower bound is about generic algorithms under random encodings, not every representation-specific algorithm. | [publisher record](https://doi.org/10.1007/3-540-69053-0_18), retrieved primary text |
| Pointcheval--Stern, *Security Arguments for Digital Signatures and Blind Signatures* (J. Cryptology 2000) | Forking arguments name random-oracle, replay, query, simulation, and distinct-fork conditions; special soundness alone is not a Fiat--Shamir theorem. | [publisher record](https://doi.org/10.1007/s001450010003), retrieved primary text |
| Bellare--Garay--Rabin, *Fast Batch Verification for Modular Exponentiation and Digital Signatures* (EUROCRYPT 1998) | Deterministic batching admits cancellation; randomized batching needs fixed errors, independent randomness, and the stated order/field boundary. | [publisher record](https://doi.org/10.1007/BFb0054130), retrieved primary text |
| Kate--Zaverucha--Goldberg, *Constant-Size Commitments to Polynomials and Their Applications* (ASIACRYPT 2010) | Degree, trusted setup, subgroup, DL/SDH/BSDH, and strong-correctness premises belong in any KZG claim. | [publisher record](https://doi.org/10.1007/978-3-642-17373-8_11), retrieved primary text |
| SEC 1 v2.0 | On-curve, public-key, subgroup, order, and nonidentity validation are separate checks. | [official specification](https://www.secg.org/sec1-v2.pdf), Sections 3.2--3.3 retrieved |
| RFC 9380, *Hashing to Elliptic Curves* | Uniform and nonuniform encodings, domain separation, subgroup clearing, and suite-specific cofactor handling are distinct contracts. | [official RFC](https://www.rfc-editor.org/rfc/rfc9380), retrieved |
| Fuchsbauer--Kiltz--Loss, *The Algebraic Group Model and its Applications* | AGM conclusions are model-relative and require algebraic representations; they are not standard-model group theorems. | [IACR ePrint 2017/620](https://eprint.iacr.org/2017/620), retrieved |
| Groth, *On the Size of Pairing-based Non-interactive Arguments*; Gabizon--Williamson--Ciobotaru, *PLONK* | Full SNARK claims depend on pairing, CRS/SRS, algebraic, polynomial, transcript, and knowledge-soundness interfaces not present in a small field lemma. | [ePrint 2016/260](https://eprint.iacr.org/2016/260), [ePrint 2019/953](https://eprint.iacr.org/2019/953), retrieved |
| Gao--Shaikh--Kissinger, *Graphical Algebraic Geometry* | `GAG_q` makes finite-field equations and elimination explicit, but its completeness theorem does not make normalization or polynomial solving cheap. | [`KN-LIT-c9e59d`](../../knowledge/literature/KN-LIT-c9e59d.md), primary text read |

Repository records checked first include the [Sadek/xedni dependency audit](../../docs/reports/xedni-sadek-20261101/README.md), its [open cutoff problem](../../problems/xedni-sadek-explicit-cutoff.md), proposed hypothesis
[`H-XEDN-292264`](../../ledger/hypotheses/H-XEDN-292264.yaml), the formal-lane
contract, and the existing subgroup/transfer targets. A sibling `crypto`
study, `research/jksst_xedni_audit_20261101/`, supplies the larger
kernel-checked JKSST finite audit. This report does not promote that sibling
artifact or the proposed Sadek repair.

The `MOD-ALIAS` warning and exact `POLY-FUNCTION` `X^2-X` example also appear
in the existing STARK semantic reviews under
`research/stark-affine-proof-20261029/`. Their inclusion here is a
formalization target and cross-protocol reuse, not a novelty claim.

## Priority 0: first formal attack surface

### MOD-ALIAS — field equality is not integer equality

- **Overbroad claim:** equality of values in `ZMod q` proves equality of the
  represented integers.
- **Countermodel:** for every positive `q`, the integers `0` and `q` are
  distinct while their casts to `ZMod q` are equal.
- **Repair theorem:** if `q>0`, `a<q`, `b<q`, and the casts of natural numbers
  `a,b` into `ZMod q` are equal, then `a=b`. Signed or multi-limb encodings
  require their own canonical range theorem.
- **Classification:** false-as-stated; conditionally proved after canonical
  range constraints.
- **Security boundary:** this proves an arithmetic alias. Calling a circuit
  vulnerable additionally requires a source-to-constraint refinement showing
  the relevant range check is actually absent.

### SUBGROUP — ambient acceptance is not subgroup membership

- **Overbroad claim:** an accepted ambient group element can be treated as a
  scalar in the intended order-`q` subgroup.
- **Countermodel:** in `ZMod 2 x ZMod 3`, designate the second-factor image
  `s |-> (0,s)` as the order-three subgroup. The point `(1,0)` is a valid
  ambient element outside that subgroup and has additive order two.
- **Repair theorem:** an exact-order-`q` generator induces an injective scalar
  map from `ZMod q`; applying it to an input additionally requires a membership
  witness (or a proven cofactor-clearing projection), and protocols may also
  require nonidentity.
- **Classification:** false-as-stated; conditionally proved after exact-order
  and membership hypotheses.
- **Security boundary:** the abstract product-group witness is not itself an
  invalid-curve exploit. Curve decoding, on-curve checking, twist handling,
  and exact implementation behavior are separate interfaces.

### BATCH-RLC — a random challenge helps only against fixed errors

- **Overbroad claim:** a random linear-combination batch equation has failure
  probability at most `d/|F|` even when invalid terms may depend on the random
  challenge.
- **Countermodel:** after observing `rho`, choose `e0(rho)=-rho` and
  `e1(rho)=1`; then `e0(rho)+rho*e1(rho)=0` for every `rho`. Deterministic unit
  coefficients also admit ordinary cancellation.
- **Repair theorem:** for errors fixed before an independent uniform challenge,
  if their coefficient polynomial is nonzero of degree at most `d` over a
  field, acceptance occurs for at most `d` challenges and hence with
  probability at most `d/|F|`.
- **Classification:** false-as-stated for adaptive errors; conditionally proved
  with commitment/independence, nonzero-polynomial, field, degree, and uniformity
  hypotheses.
- **Security boundary:** a Fiat--Shamir-derived batching coefficient needs a
  transcript-binding theorem; treating it as independent is an unconnected
  interface until then.

### POLY-FUNCTION — finite-field functions do not identify formal polynomials

- **Overbroad claim:** two polynomials equal at every field point are equal as
  formal polynomials.
- **Countermodel:** over `F_q`, the nonzero formal polynomial `X^q-X` evaluates
  to zero at every element of `F_q`.
- **Repair theorem:** a univariate polynomial of degree strictly less than
  `|F|` that vanishes on every field element is zero. Multivariate protocols
  need an individual-degree/total-degree statement appropriate to their
  evaluation domain, not the univariate slogan.
- **Classification:** false-as-stated; conditionally proved under an explicit
  degree bound.
- **Security boundary:** this does not break a polynomial commitment by itself;
  the commitment's degree bound, quotient relation, SRS, and opening verifier
  must be bound to the theorem.

### SCHNORR-SS — two transcripts extract only under exact fork hypotheses

- **Overbroad claim:** any two accepting Schnorr-like transcripts reveal the
  witness.
- **Countermodels:** two copies with the same challenge yield no invertible
  challenge difference. Over `ZMod 4`, a nonzero difference such as `2` is a
  nonunit, so division is still invalid.
- **Repair theorem:** in an exact prime-order subgroup, two accepting
  transcripts with the same commitment and distinct challenges satisfy
  `w=(s-s')/(e-e')` in the scalar field; the scalar encoding must be injective.
- **Classification:** false-as-stated; conditionally proved under same-
  commitment, distinct-challenge, prime-order, subgroup, and transcript-equation
  hypotheses.
- **Security boundary:** this is special soundness, not a ROM/QROM Fiat--Shamir
  security or proof-of-knowledge theorem. Producing the two forks remains a
  separate model-relative reduction.

## Priority 0: queue after the frozen five

| ID | Skeptical target | Decisive artifact | Primary status |
| --- | --- | --- | --- |
| COFACTOR | Treating cofactor clearing as a uniform bijection/projection without group and coprimality hypotheses | Exact kernel/image/pushforward count; product-group countermodels when factors share divisors or the assumed decomposition fails | conditional / interface |
| FS-ZERO-HASH | “Special soundness implies Fiat--Shamir security” | Constant-hash countermodel: choose `R=sG` when the challenge is always zero; then isolate domain separation and ROM programmability premises | false-as-stated / model-relative |
| PEDERSEN-IPA | “Independent generators” in a cyclic group means literal linear independence | Exhibit the scalar-relation kernel and alternate openings when a generator relation is known; state computational binding instead | false-as-stated / open assumption |
| ZK-SEPARATION | Completeness, zero knowledge, soundness, and proof of knowledge are interchangeable | Always-accept protocol is complete and perfectly ZK but unsound; HVZK and malicious-verifier definitions remain distinct | false-as-stated |
| ONE-SHOT-REPEAT | A one-shot bound implies a geometric expected waiting time | Fully correlated trials and adaptive-history countermodels; repair with a uniform conditional-hazard recurrence | false-as-stated / conditional |
| DLP-CDH-DDH | DLP, CDH, and DDH hardness are freely interchangeable | Record reduction direction; give an abstract oracle/model where DDH is easy while computation remains an assumption | model-relative / open assumption |

The sibling JKSST suite already addresses part of `ONE-SHOT-REPEAT`. The next
xedni-specific targets are: distinguish a one-shot event from conditional
hazard; show Hasse plus subgroup order needs a bounded cofactor to compare `p`
and `q`; show ten points on a cubic need not give ten independent conditions;
use the exact coefficient-box count `(2C+1)^r-1`; separate an existential
relation from an efficient finder; and connect lift congruence to selected-point
height only through a proved interface. The exact height-ball count is not
determined by rank, radius, and minimum alone; the family-uniform
height/discriminant comparison and Lang input remain assumptions, while fixed
finite-field relation events admit exact counts.

## Priority 1: protocol and implementation interfaces

1. **Exceptional elliptic-curve formulas.** Prove the affine/projective formula
   domain and exhibit exceptional denominators; refine complete implementations
   to the abstract group law.
2. **Invalid-curve and twist input paths.** Bind byte decoding, curve membership,
   subgroup membership, nonidentity, and error handling to the protocol model.
3. **Fiat--Shamir transcript encoding.** Prove injective/canonical serialization,
   statement and public-input absorption, protocol/domain tags, and length
   separation; exhibit concatenation collisions when omitted.
4. **KZG trapdoor and degree boundaries.** If toxic waste `tau` is known and
   `z != tau`, the scalar equation permits a forged proof proportional to
   `(c-y)/(tau-z)`; state this algebraic failure separately from q-SDH and SRS
   security. Freeze degree, subgroup, and setup premises.
5. **KZG batching.** Audit duplicate evaluation points, vanishing denominators,
   adaptivity to batching challenges, and the exact nonzero-polynomial bound.
6. **PLONK permutation and lookup products.** Make every nonzero denominator,
   challenge timing, domain-size, degree, and boundary-row premise explicit;
   find small-field collisions before attempting a full proof.
7. **Circuit elliptic-curve refinement.** Relate limb/range constraints and
   incomplete formulas to native curve operations and subgroup policy.
8. **ECDLP random self-reducibility.** Prove the exact-subgroup permutation and
   success preservation; do not silently randomize over the full curve group.
9. **Pollard rho heuristics.** Separate deterministic collision correctness
   from the random-map collision-time model and from usefulness of a collision.
10. **Hash-to-curve.** Bind domain separation, map suite, cofactor clearing,
    uniform/nonuniform designation, subgroup output, and exceptional cases to
    RFC 9380 rather than a generic “hash is random” premise.
11. **Concrete and multi-user security.** Track query counts, loss factors,
    constants, union bounds, and correlated users instead of retaining only an
    asymptotic adjective.

## Priority 2: foundations that need new infrastructure

1. **Generic group model.** First prove a transparent-encoding countermodel to
   overbroad “all algorithms” wording; then formalize the random-injective-
   encoding oracle and collision transcript needed for Shoup's actual scope.
2. **Forking lemma.** Build a finite random-oracle/game semantics with query
   indexing, replay, aborts, distinct challenges, and exact probability loss.
3. **ROM, AGM, KEA, q-SDH, and QROM boundaries.** Treat each as a named model or
   assumption. Prove reductions between formal games; do not recast them as
   unconditional algebra.
4. **SNARK definition separation.** Formalize completeness, knowledge
   soundness/extractability, zero knowledge, simulation soundness, and adaptive
   variants as different games before treating “secure SNARK” as one predicate.
5. **Full KZG, Groth16, and PLONK.** These require pairings, polynomial
   commitment interfaces, CRS/SRS semantics, encodings, and game proofs beyond
   the first-wave algebraic controls.
6. **Curve-selection assumptions.** Audit MOV/Frey--Ruck embedding degree,
   anomalous/supersingular exclusions, twists, cofactors, and endomorphism
   claims with exact curve and subgroup identities.

## Lean reach and missing infrastructure

Immediate targets can use existing Mathlib support for `ZMod`, finite fields,
finite groups, `Fintype`/`Finset` counting, polynomials and root bounds,
`MvPolynomial.schwartz_zippel_totalDegree`, and finite probability mass
functions. This is enough for modular aliases, abstract subgroup/cofactor
countermodels, fixed-error batch bounds, polynomial/function separation,
Schnorr special soundness, and exact finite-event bounds.

The moderate layer needs a reusable finite game/oracle library: transcripts,
adaptive adversaries, random-oracle tables, rewinding/forking, query budgets,
and statistical distance. The hard layer additionally lacks repository-ready
pairing/KZG objects, AGM algebraic-representation semantics, PPT algorithms,
negligible functions, and ROM/QROM games. Those gaps are engineering and
semantic obligations, not evidence for or against the associated hardness
assumptions.

## Ninety-day proof sequence

### Days 0--30: finite trust boundaries

- Discharge and semantically review the five frozen targets in order:
  `MOD-ALIAS`, `POLY-FUNCTION`, `BATCH-RLC`, `SUBGROUP`, `SCHNORR-SS`.
- Put counterexample and repaired theorem in the same module so a green build
  cannot silently preserve only the convenient half.
- Add an axiom audit and proof map for every module; bind any implementation
  conclusion to a separate source-refinement theorem.

### Days 31--60: composition failures

- Formalize cofactor projection/pushforward counts, constant-hash Fiat--Shamir,
  Pedersen relation kernels, the always-accept ZK/soundness separator, and
  correlated-repetition countermodels.
- Compose the existing JKSST finite theorems only where selected lifts,
  subgroup reduction, useful relation selection, and adaptive recurrence are
  explicitly supplied.
- Freeze KZG toxic-waste and degree-bound algebraic controls, without claiming
  a full commitment security proof.

### Days 61--90: minimal game framework

- Implement a finite transcript/oracle semantics and prove one exact
  random-linear-combination game and one two-fork extraction game.
- Specify the generic-group oracle boundary and transparent-encoding negative
  control before attempting Shoup's lower bound.
- Use the resulting interfaces to decide whether a faithful forking lemma or a
  KZG binding game is the next tractable end-to-end target. Record blocked
  pairings/PPT/QROM work as explicit problems rather than weakening statements.

## Acceptance rules

A corpus item is complete only when all of the following are present:

1. the human claim and Lean theorem have the same quantifier order;
2. the counterexample satisfies every stated premise, not an easier surrogate;
3. the repaired theorem exposes field, order, subgroup, degree, distribution,
   adaptivity, encoding, and setup hypotheses that it uses;
4. the exact theorem builds with no `sorry`, custom axiom, `unsafe`, or
   `native_decide` escape and passes the repository axiom audit;
5. an independent semantic review checks non-vacuity and source fidelity; and
6. implementation or protocol impact is claimed only after a checked
   source-to-model refinement.

Lean can decisively refute universal mathematical statements and verify finite
countermodels, algebraic implications, reductions, and exact bounds. It cannot
turn DLP, CDH, q-SDH, knowledge soundness, or any other unformalized
computational hardness assumption into an unconditional theorem, nor can it
establish that a deployed implementation matches an abstract model without a
refinement proof. The purpose of this corpus is to make those boundaries
unavoidable and machine-check the parts that are genuinely mathematical.
