# Independent review: subgroup membership

## Review scope and snapshot

- Assigned target: `ATTACK-SUBGROUP-MEMBERSHIP-CONTROL`.
- Producer commit: `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd` (parent `362416e89f5604519b1a049d016e86c4750635a9`).
- Review scope: only the target YAML, the named `SUBGROUP` source subsection, environment pins, and `formal/CryptoResearch/AttackCorpus/SubgroupMembership.lean` at the producer commit. No sibling proof module or sibling review/report was read.
- The repository checkout was at `b60c0cec87293255f46e9f95e8ec1afef49f2e17`; all reviewed producer inputs are therefore identified below by `git show <producer>:<path>`, not by the checkout's working-tree copy.

| Input | Git blob | SHA-256 of producer bytes |
|---|---|---|
| `formal/targets/attack-subgroup-membership.yaml` | `b4cec42a34b6a3e227d47ccce6a162c793ee6e59` | `12dca1080ba2ab7e1a78f9246147cc015790dbd3dd0fc7da6753595b048404a1` |
| `research/cryptographic_assumption_attack_corpus_20261101/README.md` | `47aec771e550dcd547d5357030ec35a4c8c3d266` | `a96c1ba72851c01501622503443ea7094557f1b2aa9e7b5c0bfc5641de095bc6` |
| Exact named README subsection (heading through the line before the next level-three heading) | n/a | `54cdf441794a6e270cf75b8b82bcff7f8bd4d9c2dd9b84a0b850260c72bb38ff` |
| `formal/lean-toolchain` | `a6aff065db2882c535684f8c5bcd4f16e9a23915` | `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c` |
| `formal/lakefile.toml` | `0cc5f974173997428ce2c1d591d6a31606f896e9` | `104369773c0926608c11ccfdc5e10178041269371566ea11a46baf816f4a9b4d` |
| `formal/lake-manifest.json` | `0136ba271fdb76230c62df47fb8bf911d47bb8ee` | `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` |
| `formal/CryptoResearch/AttackCorpus/SubgroupMembership.lean` | `383eb9e409651f8a4a80cffc03ba4c3ee2710d20` | `ee33d018fead344b4b3509e1d1677bb8ebefea17c9834c1a930fcf69092e6d69` |

The exact pin requests Lean `v4.35.0`, CryptoLean `60952c696ded7f3da4f4517006d9af6482662487`, and mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`.

## Blind derivation record

This section was written before opening the assigned Lean proof. Before recording it, I read only the target YAML, the source subsection `### SUBGROUP — ambient acceptance is not subgroup membership`, and the three environment-pin files listed above. In particular, I had not read the assigned proof or any sibling proof or report.

Let

\[
A = \mathbb Z/2\mathbb Z \times \mathbb Z/3\mathbb Z,
\qquad \phi(s)=(0,s),
\qquad S=\operatorname{range}(\phi).
\]

The counterexample should be the explicit ambient element `P = (1, 0)`. It is a well-typed member of `A`; "ambient acceptance" in this abstraction is only inhabiting the product type. If `P = phi(s)`, equality of first coordinates would give `1 = 0` in `ZMod 2`, a contradiction, so `P \notin S`. Its first coordinate has additive order two and its second coordinate has additive order one, hence the product element has additive order `lcm 2 1 = 2`.

The exact finite-model repair should have two parts. From `Q \in S`, range elimination supplies `s : ZMod 3` with `Q = phi(s)`. If also `Q != 0`, then that scalar is nonzero; every nonzero element of `ZMod 3` has additive order three, so `addOrderOf Q = 3`. The nonzero premise is essential: `phi(0) = 0` belongs to the image but has additive order one.

Blind controls to apply after opening the proof:

1. `Ambient` must be `ZMod 2 x ZMod 3`, in that order.
2. The designated map must put the scalar in the second factor: `s |-> (0, s)`.
3. The outside witness must be `(1, 0)`, with the `1` in `ZMod 2`.
4. The proof must establish both non-membership in the image and additive order exactly two.
5. The repair must extract an actual `ZMod 3` preimage and must require nonzero before asserting order three.
6. The theorem must not silently identify product-type inhabitation with curve decoding, on-curve validation, twist rejection, or a concrete protocol subgroup check.

## Proof inspection

The assigned module matches the target theorem name exactly and preserves the required orientation:

- `Ambient := ZMod 2 × ZMod 3`;
- `scalarEmbedding (s : ZMod 3) := (0, s)`;
- `designatedSubgroup := Set.range scalarEmbedding`; and
- `outsidePoint := (1, 0)`.

### Mathematical derivation and proof correspondence

1. A hypothetical range witness gives `scalarEmbedding s = outsidePoint`. Applying `Prod.fst` yields `0 = 1` in `ZMod 2`, a contradiction. This positively detects a factor swap.
2. `outsidePoint_order` uses `addOrderOf_eq_iff` at `2`, checks `2 • outsidePoint = 0`, and rules out the only positive smaller multiplier, `1`. It proves exact order, not merely an upper bound.
3. Destructing `Q ∈ Set.range scalarEmbedding` supplies an actual `s : ZMod 3`, rewrites `Q` to `(0,s)`, and returns that same scalar as the preimage witness.
4. `nonzero_designated_order` uses `addOrderOf_eq_iff` at `3`. Triple addition is zero coordinatewise. Multiplier `1` contradicts nonzero directly; multiplier `2` gives `(2 : ZMod 3) * s = 0`, hence `s = 0` because `2 != 0`, again a contradiction. Thus the order is exactly three.
5. The zero exception remains at the public boundary as `Q != 0 -> addOrderOf Q = 3`; the code never assigns order three to `scalarEmbedding 0`.

The assigned module contains no `sorry`, `admit`, new axiom, or sibling project theorem. Its only imports are the shown Mathlib modules/tactics. This is a source inspection result, not an exact-toolchain axiom audit.

### Hypothesis delta

| Obligation | Frozen source/target assumptions | Formal assumptions | Assessment |
|---|---|---|---|
| Ambient acceptance | `P = (1,0)` inhabits `ZMod 2 × ZMod 3`; acceptance is expressly typing-only | None; `outsidePoint : Ambient` by construction | Exact specialization; no decoder predicate is claimed. |
| Outside `S`; order two | Explicit product and image definitions | None; both are closed results | Exact. |
| Membership supplies scalar | `Q ∈ S` | `Q ∈ designatedSubgroup` | Exact; proves existence, not uniqueness. |
| Nonzero image order | `Q ∈ S` and `Q != 0` | Membership is eliminated to `Q = scalarEmbedding s`; order remains guarded by `Q != 0` | Equivalent; no premise was weakened away. |
| Generic README repair | Exact-order-`q` generator, membership or proven cofactor projection, possibly nonidentity | Fixed `q = 3`, fixed embedding, direct range membership, explicit nonzero premise | Deliberate YAML-required narrowing; not a generic generator/cofactor theorem. |

### Controls

| Control | Result | Evidence |
|---|---|---|
| Factor and image orientation | Pass | Type is `ZMod 2 × ZMod 3`; `s : ZMod 3` occurs in `Prod.snd`. |
| Outside witness orientation | Pass | `(1,0)` has its order-two component in `Prod.fst`, which the non-membership proof projects. |
| Exact outside order | Pass | Annihilation at two and minimality below two are both proved. |
| Membership witness | Pass | Public conclusion returns `∃ s : ZMod 3, Q = scalarEmbedding s`. |
| Exact image order and zero guard | Pass | Minimality below three is proved only under nonzero. |
| Non-vacuity / escape hatches | Pass by source inspection | Witness and image are concrete; no placeholder or declared axiom occurs. |
| Security boundary | Pass | Types remain an abstract additive product; no curve or protocol conclusion appears. |

## Machine status

`not_verified` pending exact Lean `v4.35.0`.

The producer pin requests Lean `v4.35.0`. The local Lean `v4.34.1` proxy command

```text
elan run leanprover/lean4:v4.34.1 lake env lean -o /dev/null CryptoResearch/AttackCorpus/SubgroupMembership.lean
```

was attempted against a working copy whose assigned-file blob matched producer blob `383eb9e409651f8a4a80cffc03ba4c3ee2710d20`. It exited before elaboration because `Mathlib.olean` was absent from the 4.34 search path (`unknown module prefix 'Mathlib'`). This missing proxy artifact is not a proof diagnostic and supplies no machine evidence. No exact 4.35 build or axiom audit was completed in this review.

## Fidelity and scoped outcome

The code faithfully proves the YAML claim in the deliberately small model. The named constant is an explicit counterexample witness; the public theorem includes non-membership, exact order two, scalar extraction, and nonzero exact order three; and no concrete elliptic-curve or protocol claim is inferred. Relative to the frozen target and source subsection, the source-level scoped outcome is **holds**.

One nuance: `designatedSubgroup` is a `Set`, not an `AddSubgroup`. The theorem proves the requested range and order facts but does not separately package closure or cardinality three. This does not break the YAML theorem, whose prerequisite fixes the designated set as this range.

## Missing bridges

- SEC 1 decoding, on-curve acceptance, and malformed encodings;
- concrete curve/subgroup orders and cofactor;
- twist and invalid-curve rejection;
- a verified subgroup test or cofactor-clearing implementation;
- `AddSubgroup` packaging/cardinality and embedding injectivity or scalar uniqueness;
- the generic exact-order-`q` generator theorem from the source prose; and
- protocol nonidentity enforcement, attacker reachability, and impact.

## Scoped attestation

**holds**
