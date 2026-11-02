# Adaptive batching review

## Blindness record

This derivation was recorded before opening `formal/CryptoResearch/AttackCorpus/AdaptiveBatching.lean`. At this point the only claim-bearing inputs read were the target manifest and the named BATCH-RLC source subsection. No sibling proof module or sibling review/report was read.

## Snapshot and permitted sources

- Producer commit: `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd`.
- Review worktree HEAD at start: `b60c0cec87293255f46e9f95e8ec1afef49f2e17`.
- Target: `formal/targets/attack-batch-rlc-adaptive.yaml`, Git blob `f1de7bc2652c11d44a5e255367a4785fb054090b`.
- Source: only `### BATCH-RLC — a random challenge helps only against fixed errors` in `research/cryptographic_assumption_attack_corpus_20261101/README.md`, whose full-file Git blob is `47aec771e550dcd547d5357030ec35a4c8c3d266`.
- Assigned proof (not yet opened when this section was written): `formal/CryptoResearch/AttackCorpus/AdaptiveBatching.lean`, Git blob `040c0236dfdcda127c2a0bc60ab0c210a9a991cd`.

## Blind mathematical derivation

For an arbitrary field `F`, choose the challenge-dependent functions
`e0 rho = -rho` and `e1 rho = 1`. Then, pointwise in `rho`,
`e0 rho + rho * e1 rho = -rho + rho * 1 = 0`, while
`e1 rho = 1 != 0`. The relevant order is therefore “choose functions that
may inspect `rho`, then for every `rho`”; this gives universal acceptance and
is not a fixed-polynomial root-count setting.

For the repair, fix `a b : F` before binding the challenge in
`{rho | a + rho * b = 0}`, assume `not (a = 0 and b = 0)`, and assume the
field is finite so that `Set.ncard` is an ordinary finite cardinality.

- If `b = 0`, the nonzero-pair premise forces `a != 0`. The acceptance
  equation reduces to `a = 0`, so the accepting set is empty and has ncard
  zero.
- If `b != 0`, two accepting challenges `x,y` give
  `(x - y) * b = 0`; field cancellation yields `x = y`. Thus the accepting
  set is subsingleton (equivalently, its only possible element is `-a / b`)
  and has ncard at most one.

Dropping the nonzero-pair premise admits `a = b = 0`, when every challenge
accepts. Allowing the errors to depend on `rho` admits the witness above and
again makes acceptance universal even though the second error is everywhere
nonzero. Uniform sampling would be needed to turn the fixed-set bound into a
probability bound; independence/commitment, transcript binding, Fiat--Shamir,
higher-degree batching, group encodings, and multiple equations remain
outside this scalar lemma.

## Machine status

Machine status: `not_verified`.

The producer pins `leanprover/lean4:v4.35.0`. Its toolchain, Lake configuration,
and manifest blobs are respectively
`a6aff065db2882c535684f8c5bcd4f16e9a23915`,
`0cc5f974173997428ce2c1d591d6a31606f896e9`, and
`0136ba271fdb76230c62df47fb8bf911d47bb8ee`; the manifest pins Mathlib at
`cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`. The current working copy of the
assigned Lean file hashed to the same `040c0236...` blob as the producer
commit, so it was suitable for an exact-source proxy attempt.

The available proxy was Lean 4.34.1 (Lean commit
`5045d0056413266e57c625dcd7c365b10e377c52`). The command
`elan run leanprover/lean4:v4.34.1 lake env lean
CryptoResearch/AttackCorpus/AdaptiveBatching.lean` did not reach source
checking: initial dependency materialization collided with another checkout,
and a retry reported that `Mathlib.olean` was absent. No further proxy build
was attempted because workspace capacity was constrained. Those are
infrastructure outcomes, not negative evidence about the theorem. No result
from the authoritative 4.35 build or axiom audit was available to this review.

## Hypothesis delta

| Surface | Formal statement | Delta and consequence |
|---|---|---|
| Adaptive cancellation | `{F} [Field F]`, with the concrete functions `adaptiveError0 rho := -rho` and `adaptiveError1 rho := 1` | No finiteness or probability premise is needed. The functions are selected as an adaptive strategy before the pointwise `forall rho`, but their outputs may inspect `rho`. |
| Nontrivial error | `adaptiveError1 rho != 0` is conjoined with cancellation for every `rho` | This rules out explaining acceptance by both errors being zero. It is exactly as strong as the target's requested nonzero second error. |
| Fixed repair | `[Fintype F] (a b : F) (hfixed : not (a = 0 and b = 0))` precedes `{rho | a + rho * b = 0}` | `a,b` cannot vary inside the accepting-set binder. `Fintype` supplies a concrete finite enumeration, a benign implementation-level strengthening of “finite field.” The nonzero-pair premise says the linear coefficient polynomial is not identically zero; it does not require both coefficients separately nonzero. |
| Repair conclusion | `Set.ncard {rho | a + rho * b = 0} <= 1` | This is the exact degree-one counting conclusion requested by the target. It is not yet a probability statement. |
| README's general repair | Nonzero degree-at-most-`d` polynomial, uniform challenge, probability at most `d / |F|` | The assigned target intentionally covers only the scalar degree-one cardinality lemma. General root counting, uniform PMFs, and the cardinality-to-probability bridge are absent. |
| Timing/security interpretation | Fixedness is represented only by binder placement | There is no commitment game, independence theorem, transcript binding, Fiat--Shamir model, group encoding, or named protocol theorem. No such security conclusion may be imported from this lemma alone. |

## Proof attack and controls

The adaptive theorem reduces definitionally to `-rho + rho * 1 = 0` and
`1 != 0`; `simp` is the expected field proof. Importantly, the theorem does
not accidentally specialize to one challenge: it proves the conjunction for
every `rho`, and the second component is nonzero at every challenge.

For the repair, rewriting `ncard <= 1` to subsingletonness exposes the right
obligation. Given two accepting challenges `rho,sigma`, the proof handles both
load-bearing cases:

- Positive control, fixed `b = 0` and `a != 0`: acceptance would simplify to
  `a = 0`, a contradiction, so the set is empty and has ncard zero. The Lean
  branch derives `a = 0` from an alleged member and contradicts `hfixed`.
- Positive control, fixed `b != 0`: subtracting the two acceptance equations
  gives `(rho - sigma) * b = 0`. Field no-zero-divisors and `b != 0` force
  `rho = sigma`; equivalently the only possible root is `-a / b`. For example,
  `b = 1` gives the singleton root `-a`, showing that the upper bound can be
  tight.
- Negative control, remove `hfixed`: at `a = b = 0`, the accepting set is the
  whole field, whose finite-field cardinality is at least two, so `ncard <= 1`
  is false. The hypothesis is therefore material rather than decorative.
- Negative control, permit challenge-dependent errors: the already-defined
  `e0(rho) = -rho`, `e1(rho) = 1` makes the accepting predicate true for all
  challenges while retaining an everywhere-nonzero error. Thus restoring
  adaptivity destroys the fixed-root counting argument exactly as claimed.

Static inspection found no `sorry`, `admit`, custom axiom, `unsafe`
declaration, explicit classical assumption, or vacuous antecedent in the assigned
module. The algebraic proof steps are coherent with the blind derivation, but
this observation is not a substitute for the pending pinned-toolchain check.

## Fidelity and scoped outcome

Within the YAML target's deliberately narrow scalar model, the statement is
faithful and the proof argument holds. The adaptive witness has the required
challenge dependence and nonzero `e1`; the repair visibly fixes `a,b` outside
the challenge binder and proves the exact `ncard <= 1` bound. The module's
comment “fixed nonzero errors” is slightly loose English—the proposition needs
the coefficient pair to be nonzero, not each coefficient—but the proposition
and proof use the correct condition.

Statement fidelity/mathematics and machine verification are separate here:
the former holds under the stated scalar hypotheses; the latter remains
`not_verified` until the exact Lean 4.35 gate and axiom audit complete.

This outcome does not establish the README's general degree-`d` probability
claim or any protocol security theorem. The missing bridges are: a general
nonzero-polynomial root bound; a uniform sampler/PMF and conversion of ncard to
probability; a formal commitment or independence mechanism enforcing the
fixed quantifier order; transcript binding for Fiat--Shamir; and any encoding,
group-equation, multi-equation, or named-protocol connection. Authoritative
Lean 4.35 compilation and an axiom receipt are also still missing machine
evidence.

## Attestation

holds

## Correction-round addendum

### Corrected snapshot and scope

This addendum preserves the original review and examines only the assigned
module's diff from producer commit
`f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd` to corrected producer commit
`37cc75cfebb30c7582e90e3b632d3454ff5804dc`, followed by the complete corrected
`formal/CryptoResearch/AttackCorpus/AdaptiveBatching.lean`. No sibling proof
module or report was read in this round. The binding correction-round commit
and current review HEAD was
`0e096a9d9889c5eb7f74e4142cb55b0cdde1f2bf`.

The corrected module has SHA-256
`4c6feaa0109a6b8b27e8f009db08973c3fc634e1a13daa5f80832f370b17a656`
and Git blob `a92e50541e7814923eaf83cad6be3b86acfaf09c`; the baseline Git blob was
`040c0236dfdcda127c2a0bc60ab0c210a9a991cd`.

### Corrected theorem and quantifier audit

The exact frozen name `adaptive_rlc_cancellation` now exposes both required
claims in one proposition:

1. Its first conjunct is still over arbitrary `{F} [Field F]` and says
   `forall rho`, the concrete challenge-dependent witnesses
   `adaptiveError0 rho = -rho` and `adaptiveError1 rho = 1` cancel, while
   `adaptiveError1 rho != 0`.
2. Its second conjunct is
   `forall [Fintype F] (a b : F), not (a = 0 and b = 0) ->
   Set.ncard {rho | a + rho * b = 0} <= 1`.

This is the correct separation of generalities: finiteness is not imposed on
the adaptive counterexample and is introduced only for the counting repair.
Within the repair, the `Fintype` structure and then `a,b` are bound before the
set's `rho`; the coefficients therefore cannot adapt to the challenge. The
nonzero-pair premise remains load-bearing, and the conclusion remains the
exact at-most-one cardinality bound. The helper
`fixed_error_acceptance_card_le_one` still supplies the algebraic proof,
including the `b = 0` empty-set and `b != 0` subsingleton branches, but the
named theorem's own type now contains that conclusion rather than merely
referring readers to a separate declaration.

### Auditability resolution

Resolved. At the baseline commit, the theorem selected by the target's
`theorem_name` exposed only adaptive cancellation; the fixed-error repair was
a separate theorem, so an audit keyed exactly to the frozen name could miss
half of the target. At the corrected commit, the named theorem is explicitly
the conjunction of the adaptive witness and fixed-error repair. Delegating
the second proof branch to the helper does not weaken auditability because the
full repaired proposition is visible at the audited name. The corrected
documentation also replaces the loose phrase “fixed nonzero errors” with the
precise “fixed nonzero coefficient pair.”

### Machine evidence and residual gaps

The correction-round Lean 4.34 proxy compilation passed. It remains
non-authoritative: exact pinned Lean 4.35 compilation and an axiom-audit result
are still pending, so authoritative machine status remains `not_verified`.

No new semantic bridge is supplied or claimed. Residual boundaries are the
same intentional ones identified above: there is no general degree-`d` root
bound, uniform sampler or ncard-to-probability theorem, commitment/independence
game, transcript-binding or Fiat--Shamir semantics, group encoding,
multi-equation model, or named-protocol security theorem. The concrete
challenge-response functions establish the requested algebraic adaptive
cancellation, not a full interactive adversary model.

### Updated attestation

Statement fidelity and mathematics: `holds`. Exact-name auditability finding:
`resolved`. Authoritative machine status: `not_verified` pending Lean 4.35.

holds
