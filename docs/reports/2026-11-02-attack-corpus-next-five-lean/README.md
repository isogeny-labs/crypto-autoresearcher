# Five more cryptographic-assumption boundaries in Lean

Status: **five scoped declarations machine-verified; original failed snapshot
and independent reviews preserved; no paper-level or ECDLP break claimed**.

This tranche attacks five informal inference patterns with finite
countermodels and then states the extra hypotheses that repair them.  Lean
proves the declarations in the target manifests.  It does not prove that a
deployed protocol is broken, that the cited primary sources make the rejected
inference, or that elliptic-curve discrete logarithms are easy.

## Exact result

| Boundary | Lean-checked countermodel or separation | Lean-checked repair | Literature scope |
| --- | --- | --- | --- |
| `ONE-SHOT-HISTORY` | Equal one-trial success counts can have different joint survival, and one outcome can fail every trial. | An explicitly assumed history-uniform recurrence gives the sharp geometric pointwise bound and a finite tail inequality. | JKSST Theorem 4.1 is a conditional one-attempt bound; the target does not instantiate xedni histories or expectation. |
| `CUBIC-EVAL-RANK` | Ten distinct triples `(i,0,1)` have the nonzero cubic `Y*Z^2` in their evaluation kernel, so the square determinant is zero. | A nonzero determinant makes the coefficient map injective. | JKSST already rank-tests its `r <= 9` matrix.  This is a guardrail, not an erratum; the witness cubic is reducible and singular. |
| `COFACTOR-PUSHFORWARD` | Multiplication by two collapses `ZMod 2 x ZMod 2`. | On `K x S`, annihilation on `K` plus bijectivity on `S` gives image `{0} x S` and exact constant fibres; `ZMod 2 x ZMod 3` is the finite control. | RFC 9380 does not say cofactor clearing alone uniformizes an encoder. |
| `FS-ZERO-HASH` | A zero challenge accepts `R=sG` for every public key; any known constant accepts an adaptively chosen `R=sG-cX`. | A nonzero challenge gives uniqueness only for one fixed transcript. | A constant function is outside the random-oracle model.  No Pointcheval--Stern, ROM, QROM, replay, or extraction theorem is refuted. |
| `PEDERSEN-RELATION-KERNEL` | If the nonzero relation `H=alpha*G` is known, `(alpha,-1)` is in the kernel, openings can be changed to any message, and a different-message collision recovers `alpha`. | Faithful scalar action and nonzero `alpha` give the exact kernel and recovery formulas. | Pedersen already makes the relation computationally unknown.  Algebraic dependence is not a practical DLP or binding break. |

The readable source statements are in
[`research/cryptographic_assumption_attack_corpus_tranche2_20261102/README.md`](../../../research/cryptographic_assumption_attack_corpus_tranche2_20261102/README.md).
The exact claims and exclusions are frozen in the five
[`formal/targets/attack-*.yaml`](../../../formal/targets/) manifests; their
audited declarations live under
[`formal/CryptoResearch/AttackCorpus`](../../../formal/CryptoResearch/AttackCorpus/).

## Evidence chain

The first submitted proof snapshot was not accepted merely because its
mathematics looked plausible.  Exact run
[`41503944712`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41503944712)
built only the cubic module; the other four modules failed.  Six mutually
blind reviews were sealed against those exact bytes and correctly separated
source-level derivations from failed formal targets.  Their result and the
diagnostics remain in
[`initial-snapshot-evidence.md`](initial-snapshot-evidence.md).

A first correction run built four modules but left one closed `ZMod 5` goal
in the Pedersen control.  The final correction uses ordinary kernel `decide`
after normalization, not `native_decide`.  Exact run
[`41512636120`](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41512636120)
then passed the 9,135-job Lean 4.35 workspace build, all-target verifier,
named-declaration and axiom checks, dependency-pin checks, and kernel controls.
The verifier reported `113 verified, 0 not verified, 0 infrastructure, 0
undischarged`, including all five declarations above.  Full run, artifact,
hash, failure-history, and trust details are in
[`machine-evidence.md`](machine-evidence.md).

The fresh correction-review plan was committed before dispatch and binds the
exact five final source hashes.  Four mutually blind reviewers separately
audited the corrected OneShot, Cofactor, Fiat--Shamir, and Pedersen proofs.
Every correction joint received `holds`, `passed`, and `faithful_scoped`; the
independence checker reported:

```text
PASS: 4 report(s), every joint owned and attested, blindness respected, controls declared
```

The unchanged Cubic proof remains covered by the original source review and
the final exact machine gate.  Reports and attestations are under
[`correction-reviewers-v2`](correction-reviewers-v2/).  Machine acceptance and
semantic review are both required: neither substitutes for the other.

## JKSST height, Lang, and probability status

The merged core audit is
[isogeny-labs/crypto#3252](https://github.com/isogeny-labs/crypto/pull/3252),
merge commit `0f569fd66eb17a5291252aaa3fdb7ac90ef91d25`.  Together, that audit and
this tranche establish the following narrower conclusions:

- The integer coefficient box has exact count `(2*C+1)^r`, or one fewer when
  the zero vector is removed.
- Rank, radius, and minimum separation do **not** determine an exact height-
  ball count.  Explicit equal-coarse-data lattices have Euclidean counts `5`
  versus `3` and sup-norm counts `9` versus `3`.  A finite packing inequality,
  with torsion/fibre multiplicity visible, is the proved substitute.
- Given a nontorsion point, a fixed model discriminant cannot uniformly bound
  the canonical heights of all multiples.  That refutes the universal-over-
  all-points reading; it does not refute a family-uniform statement about the
  particular lifts selected by xedni.  A global-minimal-discriminant bridge is
  still missing.
- Lang's elliptic-curve height conjecture remains open.  Quadraticity,
  positivity, and finite rank alone do not force the required uniform gap;
  the direct height-gap/packing theorem is therefore conditional.
- For a fixed nonzero coefficient direction in a prime subgroup of order
  `q`, the ordinary relation event has exact probability `1/q`; the useful
  nonzero-denominator event has exact probability `(q-1)/q^2`.  A union bound
  or useful-relation selection certificate is still needed.  Replacing `/q`
  with `/p` additionally needs an explicit Hasse/cofactor size bridge.
- A one-shot event bound does not imply a repeated or adaptive conditional-
  hazard law.  The new `ONE-SHOT-HISTORY` model makes that missing interface
  explicit.

Accordingly, these proofs do **not** definitively remove every possible xedni
route to ECDLP.  They show that the published conditional obstruction cannot
silently be upgraded to an unconditional end-to-end exclusion.  Such an
exclusion still needs all of the following:

1. A specified lift-selection algorithm and a family-uniform selected-height
   comparison to a global minimal discriminant.
2. Lang for that family, or an unconditional direct height gap.
3. Mordell--Weil finite generation, rank, separation, projection, torsion, and
   fibre instantiation for the selected lifts.
4. Good reduction and exact correspondence to the intended finite curve and
   prime subgroup.
5. A theorem that algorithmic success selects a bounded relation, and a
   nonzero denominator when the useful probability is claimed.
6. A uniform cofactor/Hasse comparison connecting subgroup order `q` to
   field prime `p`.
7. A repeated/adaptive conditional-hazard theorem derived from the actual
   sampler and history.
8. Full row rank for the actual cubic evaluation conditions whenever the
   `r <= 9` step is used.

## Next skeptical tranche: ranks 1--5

[`next-wave.md`](next-wave.md) is an attack-corpus queue, not a finding list.
The recommended order is:

1. `ZK-SEPARATION`: separate completeness, simulability, soundness, and
   knowledge soundness with explicit games.
2. `SCHNORR-GROUP-SCALAR-BRIDGE`: require subgroup order, membership, and
   injectivity before cancelling a group equality to scalar equality.
3. `FS-TRANSCRIPT-ENCODING`: make serialization canonical, injective,
   ordered, public-input-bound, and domain-separated.
4. `KZG-TOXIC-WASTE`: freeze the exact pairing equation and binding game,
   then isolate what knowledge of the setup trapdoor permits.
5. `SURVIVAL-TAIL-EXPECTATION`: distinguish almost-sure termination from
   finite expectation and connect tail sums only under explicit integrability
   and hazard premises.

Each target must begin with an immutable primary-source statement and exact
quantifiers.  A tiny countermodel to a slogan is valuable as a proof-interface
test, but it is not permission to claim that a correctly scoped theorem or
deployed scheme has been broken.

## Trust boundary

The formal evidence relies on the Lean kernel, pinned dependencies, the
repository verifier, CI execution, and the correspondence between the theorem
types and the prose.  It does not instantiate concrete adversaries, parsers,
curves, encoders, random oracles, setup ceremonies, runtimes, or reductions.
Those interfaces are exactly where subsequent attack-corpus targets should
concentrate.
