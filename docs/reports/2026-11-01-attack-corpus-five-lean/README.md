# Five cryptographic-assumption boundaries in Lean

Review opened 2026-11-01; correction round completed 2026-11-02.

## Result

Five frozen finite algebraic targets now have Lean proof sources containing
both the countermodel/control and the premise that repairs the overbroad
inference. Five separately assigned reviewers re-derived their joints before
reading the producer proof and returned `holds`. Their first pass found four
audit-surface defects; the corrected producer snapshot resolves all four and
the affected reviewers confirmed the deltas.

The corrected snapshot passed the exact pinned Lean 4.35 workspace build,
all-target named-declaration verifier, project axiom audit, forbidden-construct
checks, and dependency-pin checks in
[GitHub Actions run 41365419446](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41365419446).

These are scoped mathematical results. They do **not** establish a flaw in a
named circuit or protocol, do not prove an ECDLP attack, and do not settle an
unformalized computational-hardness or model assumption.

![Countermodels, repairs, and missing bridges](proof-boundary.svg)

[Two-page PDF packet](report.pdf) · [exact machine-evidence record](machine-evidence.md)

## The five proved boundaries

| joint | rejected inference / finite control | explicit repair in Lean | still outside the theorem |
| --- | --- | --- | --- |
| `MOD-ALIAS` | `0` and positive `q` are distinct naturals but have equal images in `ZMod q` | both representatives are naturals strictly below `q`; a sharp companion includes `q = 1` and a `q = 0` boundary control | circuit, limb, signed, byte, and compiler-to-constraint refinement |
| `BATCH-RLC` | after seeing `rho`, `e0(rho)=-rho` and `e1(rho)=1` cancel for every challenge | fixed nonzero coefficient pair over a finite field has at most one accepting challenge | uniform PMF, probability conversion, commitment timing, Fiat--Shamir binding, higher degree |
| `POLY-FUNCTION` | nonzero `X^2-X` over `ZMod 2` evaluates to zero everywhere | a univariate polynomial with `natDegree P < |F|` that vanishes everywhere is formally zero | committed-polynomial, quotient, multivariate, domain, and SRS semantics |
| `SUBGROUP` | `(1,0)` is a valid element of `ZMod 2 x ZMod 3`, lies outside the image `(0,s)`, and has order two | image membership supplies a `ZMod 3` scalar; every nonzero image point has order three | curve decoding, on-curve/twist checks, concrete orders, cofactor clearing, implementation policy |
| `SCHNORR-SS` | equal challenges do not constrain a witness; over `ZMod 4`, distinct challenges can differ by a nonunit and admit two distinct witnesses | same commitment, distinct challenges, and a prime scalar field give an explicit unit and `x=(s1-s2)/(c1-c2)` | group-to-scalar refinement, fork construction/probability, transcript encoding, ROM/QROM, proof of knowledge |

The exact audited declarations are:

- `CryptoResearch.AttackCorpus.ModAlias.modulus_alias_and_bounded_repair`;
- `CryptoResearch.AttackCorpus.AdaptiveBatching.adaptive_rlc_cancellation`;
- `CryptoResearch.AttackCorpus.PolynomialFunctionAlias.nonzero_polynomial_zero_function`;
- `CryptoResearch.AttackCorpus.SubgroupMembership.ambient_membership_does_not_imply_designated_subgroup`; and
- `CryptoResearch.AttackCorpus.SchnorrSpecialSoundness.extract_of_distinct_challenges`.

For batching and polynomial/function aliasing, the correction round puts the
repair directly in the exact named theorem type; a verifier keyed to the
frozen name can no longer check only the convenient counterexample half.

## Evidence boundary

### Immutable inputs

- Initial producer: `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd`.
- Corrected producer: `37cc75cfebb30c7582e90e3b632d3454ff5804dc`.
- Correction plan: `0e096a9d9889c5eb7f74e4142cb55b0cdde1f2bf`.
- Frozen specs: the five `formal/targets/attack-*.yaml` files; none was edited.
- Toolchain: `leanprover/lean4:v4.35.0`, Mathlib revision
  `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`.

The four corrected source hashes and unchanged subgroup hash are recorded in
[the pre-review plan](review-plan.md). The available Lean/Mathlib 4.34.1 proxy
elaborated all five final modules; it is only a compatibility control, not the
authoritative receipt. The final focused target/verifier tests pass 340/340, all
five target manifests validate, the generated root is current, and a scoped
scan finds no `sorry`, `admit`, custom `axiom`, `unsafe`, or `native_decide`.
The exact run metadata, receipt-artifact identity, and artifact-download trust
limit are recorded separately in [machine-evidence.md](machine-evidence.md).
The PDF was rendered with Typst 0.15.0; both pages were visually inspected
after the final status update for clipping, overlap, and legibility.

### Semantic review

Each reviewer owned one joint, read only its frozen spec and matching source
subsection before recording a blind derivation, then inspected only its
assigned proof. The individual reports contain hypothesis-delta tables,
worked positive and known-false controls, machine/source separation, and
missing bridges:

- [modular alias](reviews/mod-alias/review.md);
- [adaptive batching](reviews/adaptive-batching/review.md);
- [polynomial/function alias](reviews/polynomial-function-alias/review.md);
- [subgroup membership](reviews/subgroup-membership/review.md); and
- [Schnorr scalar extraction](reviews/schnorr-special-soundness/review.md).

The first round found:

1. the frozen modular target's `2 <= q` is sufficient but not tight;
2. the batching repair was adjacent to, rather than inside, the exact named
   target;
3. the polynomial repair had the same named-target traceability gap; and
4. the `ZMod 4` Schnorr control did not explicitly state that witnesses `0`
   and `2` differ.

The corrected snapshot adds the sharp `0 < q` modular theorem and zero-modulus
control, bundles both repairs into their exact declarations, and adds the
explicit Schnorr witness inequality. The same four owners re-reviewed only
their assigned diffs and marked each finding `resolved`; subgroup source was
byte-identical. All five final mathematical attestations are `holds`.

### Procedure deviations

This is a technical proof-review packet, not an official research-state
transition. The pre-review plan was committed before dispatch and reviewers
worked in separate agent sessions, but they were collaboration subagents
rather than durable `TASK-*` handoffs, the plan is Markdown rather than the
machine-readable schema accepted by `tools/check_review_independence.py`, and
all sessions used one model family. The Schnorr reviewer also records a
source-subsection delimiter mistake; a fresh-context blind derivation repaired
the scope without exposing the proof. These deviations are why this packet
does not claim a canonical independent-review quorum or change a ledger,
hypothesis, experiment, or goal status.

## What this does not prove about JKSST or hardness

Nothing here turns the Jacobson--Koblitz--Silverman--Stein--Teske xedni
analysis into an unconditional attack or an unconditional impossibility
result. In particular:

- a rank/radius/minimum triple does not determine an exact uniform
  Mordell--Weil height-ball count;
- the required family-uniform height/discriminant comparison and the selected-
  lift bridge need their own theorem;
- Lang's conjecture, or a sufficient substitute, remains an explicit
  assumption rather than something Lean can honestly prove or disprove here;
- the phrase “approximately `(2 C2)^r / p`” still needs a specified finite
  probability space and an exact counting/probability theorem; and
- a marginal one-shot event bound does not by itself imply independent or
  geometric repeated trials.

The finite algebra in this tranche is decisive because it has concrete models.
DLP, CDH, q-SDH, ROM, AGM, QROM, and analogous claims are open computational
assumptions or model-relative statements; the useful skeptical action is to
formalize their games and reductions, not relabel them false without a
countermodel to the actual statement.

## Recommended next five

1. **`ONE-SHOT-HISTORY` (direct JKSST/xedni).** Refute the inference from
   per-trial marginal bounds to a geometric waiting time using fully
   correlated and complementary-event models. Repair it with a uniform
   conditional-hazard premise and a survival/tail-sum recurrence.
2. **`CUBIC-EVAL-RANK` (direct JKSST/xedni).** Ten distinct points on one line
   do not impose ten independent conditions on bivariate cubics: `Y` vanishes
   on all of them. Repair with an explicit full-rank 10-by-10 evaluation
   matrix premise.
3. **`COFACTOR-PUSHFORWARD`.** Multiplication by a cofactor is not
   automatically a bijective projection or uniformizer. Prove exact image and
   fiber counts only from a verified `K x S` decomposition and the right
   scalar actions.
4. **`FS-ZERO-HASH`.** A constant-zero challenge makes the Schnorr-style
   noninteractive equation accept `R=sG` without knowledge of the public-key
   witness. Keep the finite countermodel separate from the still-missing
   ROM/QROM forking theorem.
5. **`PEDERSEN-RELATION-KERNEL`.** In a cyclic group, `H=[alpha]G` creates an
   explicit alternate-opening kernel when `alpha` is known. State binding as
   computational under a hidden-relation/DLP setup assumption, not literal
   algebraic linear independence.

`ZK-SEPARATION` is the sixth target: an always-accept protocol cleanly
separates completeness and perfect zero knowledge from soundness. The selected-
lift height/discriminant comparison remains an interface-proof program, not a
known-false universal statement.
