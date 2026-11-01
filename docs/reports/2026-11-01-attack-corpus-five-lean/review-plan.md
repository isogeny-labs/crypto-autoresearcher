# Review plan: first five cryptographic-assumption targets

Date: 2026-11-01

This is the pre-review plan required by the formal-review workflow. It changes
no hypothesis, evidence, or knowledge status.

## Bound producer snapshot

- Branch: `codex/attack-corpus-five-lean-20261101`
- Producer commit: `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd`
- Source note:
  `research/cryptographic_assumption_attack_corpus_20261101/README.md`
  (`a96c1ba72851c01501622503443ea7094557f1b2aa9e7b5c0bfc5641de095bc6`)
- Toolchain: `leanprover/lean4:v4.35.0`
  (`ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c`)
- Dependency manifest:
  `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7`

| joint | frozen spec SHA-256 | producer source SHA-256 | exact declaration |
| --- | --- | --- | --- |
| modular alias | `3b6a5a7226655323b2e266f079311f5417f0b6d9d4dfaa9a40cb85a82624e498` | `d789bc60d85a7849564ae41e94d3c76de7e6d5cabead35763a197ed6d5cb42d2` | `CryptoResearch.AttackCorpus.ModAlias.modulus_alias_and_bounded_repair` |
| adaptive batching | `74c98067481b5a67087dffd1a3847ed02460c791468f8cfab4a5057d17c228a7` | `a9de20b3b470bade8c151b90f57775f8846bd29d71f3f6d6871bc3621529711b` | `CryptoResearch.AttackCorpus.AdaptiveBatching.adaptive_rlc_cancellation` |
| polynomial/function alias | `d7beb7c95e6588ba70b0bf64346854367f859eb6b23ef0e9fb62a85a4d023760` | `a8eefb2b425b7148b789eaa552008241ce62d7fc7b58ce5faf8c6b6be324a503` | `CryptoResearch.AttackCorpus.PolynomialFunctionAlias.nonzero_polynomial_zero_function` |
| subgroup membership | `12dca1080ba2ab7e1a78f9246147cc015790dbd3dd0fc7da6753595b048404a1` | `ee33d018fead344b4b3509e1d1677bb8ebefea17c9834c1a930fcf69092e6d69` | `CryptoResearch.AttackCorpus.SubgroupMembership.ambient_membership_does_not_imply_designated_subgroup` |
| Schnorr scalar extraction | `47fe013e68f7dbd1ba3957b559a9ad7309877a048234ee62a56d89e3d263cd27` | `495c8ffdcb943972aef7bfb18a588c454d9a4e36f20a10abc6c4be804274df94` | `CryptoResearch.AttackCorpus.SchnorrSpecialSoundness.extract_of_distinct_challenges` |

## Prior

The five finite algebraic claims are expected to hold, but a green proof is
not presumed faithful. The highest risks are a reversed subgroup factor, a
root bound whose fixed-error quantifier order became adaptive, a polynomial
repair missing its strict degree premise, a Schnorr sign/division reversal,
or a requested repair living only in prose. No protocol-security or
implementation conclusion is expected to survive this review because no
source-to-model refinement is supplied.

## Independent ownership and attacks

Each joint has one reviewer. Reviewers do not read sibling review outputs or
sibling proof modules. They first read only the frozen spec and its named
source subsection, write a blind derivation of the expected statement, and
only then inspect their assigned producer source and run checks.

| reviewer joint | worked attack | known-false / proves-too-much control |
| --- | --- | --- |
| modular alias | Check that `0` and `q` are distinct naturals, their casts alias, and cast injectivity exposes both `< q` hypotheses rather than a hidden predicate. | Remove either range premise; `0` and `q` must prevent unrestricted injectivity. Inspect the `q=0,1` boundary against the explicit `2 ≤ q` binder. |
| adaptive batching | Check that the counterexample functions genuinely depend on `rho`, `e1` is nonzero, and the repair fixes `a,b` outside the accepting-set binder with cardinality at most one. | Permit adaptive `a(rho),b(rho)` and recover universal cancellation. Exercise fixed `b=0,a≠0` and `b≠0` cases. |
| polynomial/function alias | Check formal nonzeroness and pointwise zero over exactly `ZMod 2`; check the repair is univariate over a finite field with strict `natDegree P < |F|`. | Remove the strict degree bound and reuse `X^|F|-X`; distinguish formal equality from function equality. |
| subgroup membership | Check the designated image is the second `ZMod 3` factor, `(1,0)` is outside it with additive order two, and every nonzero image member has order three. | The zero image member must be excluded from the order-three conclusion; swapping factors must be detected. |
| Schnorr extraction | Re-derive the subtraction and division orientation from the two same-`r` equations; check prime-field and distinct-challenge premises and the explicit unit conclusion. | Equal challenges must admit two witnesses; in `ZMod 4`, challenge difference `2` must be nonzero but nonunit and admit the documented `0/2` collision. |

## Permitted and forbidden reads

Permitted before blind derivation: the assigned frozen YAML, the matching
source-note subsection, Lean/Mathlib reference material, and the toolchain
pins. Forbidden until the derivation is recorded: the assigned Lean proof.
Forbidden throughout each individual review: sibling proof modules, sibling
review reports, producer discussions, and other reviewers' verdicts. The
composition author may read all reports only after every reviewer returns.

## Machine-evidence plan

The available local proxy is Lean/Mathlib 4.34.1 and may catch elaboration
errors only. It is not the pinned receipt. The exact Lean 4.35.0 workspace
must pass:

1. explicit module discovery through the generated root;
2. `lake build` and the fail-closed project axiom audit;
3. the verifier's exact named-declaration audit for all five frozen specs;
4. the forbidden-construct and input-hash checks.

Until that succeeds, machine status is `not_verified`. Even after it succeeds,
the strongest possible review outcome is `validated_scoped` for the five
finite statements only; every protocol, circuit, elliptic-curve decoder,
Fiat--Shamir, commitment, and proof-of-knowledge bridge remains out of scope.

## Completion gate

Each reviewer must provide sources read, blind-rederivation compliance,
hypothesis-delta table, positive and negative controls, machine status,
fidelity, scoped outcome, missing bridges, and a `holds | breaks |
inconclusive` attestation. The composition must reconcile all five without
promoting official research state.
