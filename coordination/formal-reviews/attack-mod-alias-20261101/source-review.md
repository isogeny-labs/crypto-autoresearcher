# MOD-ALIAS source and type fidelity review

Reviewer: `/root/mod_alias_source_review`, independent source-review session. Date: 2026-11-01 UTC. Archival task: Conductor T-1344. Subject: crypto-autoresearcher PR #2942, claim `ATTACK-MOD-ALIAS-BOUNDED-REPAIR`, target task `TASK-20261101-f3a40d`.

**Source-joint verdict: holds at current producer head `288d5612b599501119f6c0d130a56241b7e2c9b4`. Fidelity: `faithful_scoped` for the frozen natural-number statement with `2 ≤ q`.** Both arithmetic halves and both strict range hypotheses are present. The original missing-import defect has been removed. The README's broader positive-modulus wording still includes an additional `q = 1` case outside this declaration. No circuit or proof-system conclusion follows from this statement.

This verdict is independent of CI status. This reviewer did not invoke Lean, Lake, an axiom audit, a cloud build, or a benchmark; no fresh elaborated environment or transitive axiom inventory was obtained in this session. Machine status is `not_verified` by this reviewer, and this report does not assert the combined `validated_scoped` outcome. The coordinator owns the separate machine gate and synthesis.

## Frozen inputs and revision amendment

The initial assigned head was `7c7d879bdaf660c47a0bc519056545e7749d3d1d`. After the source reviewer identified a missing import, the producer requested a source review of newly pushed head `288d5612b599501119f6c0d130a56241b7e2c9b4`. The amended plan was read before the revised verdict. The original finding and affected-joint re-review are retained here; no finding was erased by the amendment.

All producer bytes were retrieved with `git show REV:PATH` from `/home/ec2-user/crypto-autoresearcher`, avoiding the mutable working tree. Hashes below are SHA-256 of the exact Git blob bytes.

| Input at current head | Bytes | SHA-256 |
| --- | ---: | --- |
| `formal/targets/attack-mod-alias.yaml` | 2055 | `3b6a5a7226655323b2e266f079311f5417f0b6d9d4dfaa9a40cb85a82624e498` |
| `research/cryptographic_assumption_attack_corpus_20261101/README.md` | 21053 | `a96c1ba72851c01501622503443ea7094557f1b2aa9e7b5c0bfc5641de095bc6` |
| `formal/CryptoResearch/AttackCorpus/ModAlias.lean` | 1364 | `62ebbc6c75c51ba72bfb7bb64a4128527428e1d8ec71776ff9ccc71c66481bae` |
| `formal/lean-toolchain` | 25 | `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c` |
| `formal/lake-manifest.json` | 3581 | `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` |
| `formal/lakefile.toml` | 1364 | `104369773c0926608c11ccfdc5e10178041269371566ea11a46baf816f4a9b4d` |

The target, source README, toolchain, manifest and Lake configuration are unchanged between reviewed heads. The original theorem source was 1290 bytes, SHA-256 `adfe6467f8901d53fdc7fb8efa01ee74f91ede4c2a108594106e0d9d1e606bea`. Its Git blob was `388599d3c5cd07836ef7cf7b4e8959659e95aa9d`; the revised theorem blob is `893ba18aff6792e1e1e7d3b915aada6811c10ef8`.

Plan: `/var/tmp/mod-alias-review-plan-20261101.md`. Initial read: 2033 bytes, SHA-256 `b5950868b342081d082bf306633ec38c29d58648b64cf9f41b39b499222a0228`. Amended read: 2454 bytes, SHA-256 `097ddf41a937a1dd4c254c05bf811ffdb7d2357f54a18c0f71be1b6f8b52ed82`. The amendment is explicitly headed 2026-11-01 23:38 UTC and binds the revised head.

Pins inspected: Lean `leanprover/lean4:v4.35.0`; Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`; CryptoLean `60952c696ded7f3da4f4517006d9af6482662487`. The revised module imports only `Mathlib.Data.ZMod.Basic`; it imports no producer helper module or CryptoLean theorem.

## Statement and source correspondence

The named declaration is `CryptoResearch.AttackCorpus.ModAlias.modulus_alias_and_bounded_repair`. Its explicit source type at current head, lines 18–22, is:

```lean
(q : ℕ) (hq : 2 ≤ q) :
  (0 : ℕ) ≠ q ∧
    (0 : ZMod q) = (q : ZMod q) ∧
    ∀ x y : ℕ, x < q → y < q →
      (x : ZMod q) = (y : ZMod q) → x = y
```

The target asks for exactly this joint statement. Its presentation of the alias sometimes reverses the equality, which changes no content. The nested conjunction retains both the counterexample and the repaired implication under the same modulus hypothesis.

| Owned joint | Check and result |
| --- | --- |
| Quantifiers | `q` is arbitrary in `ℕ`, then the explicit premise `2 ≤ q`; `x` and `y` are arbitrary natural numbers inside the third conjunct. There is no fixed modulus, existential substitute, or assumed conclusion. Holds. |
| Distinctness and alias | The first conjunct concerns inequality in `ℕ`; the second equality concerns the two images in the same `ZMod q`. These are different types intentionally, with natural casting of `q`. Holds. |
| Canonical range | Both `x < q` and `y < q` are explicit implications. Their natural-number types supply nonnegativity. There is no opaque well-formedness predicate and no inclusive-upper-bound substitution. Holds. |
| Modulus assumptions | No primality, field instance, or no-zero-divisors premise is used. The theorem includes composite moduli. `q ≥ 2` implies positivity and gives nonempty canonical representatives; it is satisfiable at `q = 2`. Holds. |
| README correspondence | MOD-ALIAS describes the same alias and the same natural-number repair, with explicit restrictions for signed and limb representations. Its prose says `q > 0`, which also covers `q = 1`; the exact target and declaration use `q ≥ 2`. Faithful to the frozen target and this stated restricted source scope; incomplete as a discharge of every positive-modulus case. |
| Model bridge | The theorem contains no circuit, wire, parser, constraint-system, encoding, or verifier object. Target notes and source prose acknowledge this boundary. Holds for arithmetic scope. |

The README's reference to the integers `0` and `q` does not require a signed-generalization theorem to witness the overbroad equality claim: these two particular values are natural numbers as well. The repaired theorem explicitly concerns natural representatives. It does not prove injectivity of arbitrary signed integer encodings.

The `q = 1` omission is a scope note, not an arithmetic counterexample: `0` and `1` are distinct naturals with the same residue, and the canonical interval has only `0`. A future claim to discharge the README's full positive-modulus wording should either include that case or state the narrower modulus bound. The present frozen target already states the narrower bound.

## Proof source and dependencies

At current head, lines 23–26 derive `0 < q`, then `q ≠ 0`, then the local `NeZero q` instance and `0 ≠ q`. These are proved from `hq`; they add no axiom. The closed `by decide` term is for the concrete proposition `0 < 2`; there is no `native_decide` or external evaluation escape. The alias reverses the standard self-cast equality. Applying `congrArg` to `.val` transports the residue equality; rewriting each representative's value using its own strict bound yields `x = y`.

The pinned official Mathlib sources were inspected, rather than recalling current lemma names. `ZMod.natCast_self` supplies the zero self-cast for arbitrary natural modulus. `ZMod.val_natCast_of_lt` recovers a bounded natural representative and requires its explicit bound; its proof uses `val_natCast` and `Nat.mod_eq_of_lt`. These dependencies impose no primality hypothesis. The characteristic proof underlying the self-cast reaches `CharP.cast_eq_zero`, whose definition uses self-divisibility. The separately available `CharP.natCast_injOn_Iio` is consistent with the intended interval restriction; the producer does not invoke it. [Pinned ZMod source](https://raw.githubusercontent.com/leanprover-community/mathlib4/cfc55fc58714a59dc06e6e79edc6d1d95140d3c2/Mathlib/Data/ZMod/Basic.lean), [characteristic basic lemmas](https://raw.githubusercontent.com/leanprover-community/mathlib4/cfc55fc58714a59dc06e6e79edc6d1d95140d3c2/Mathlib/Algebra/CharP/Basic.lean), [characteristic definitions](https://raw.githubusercontent.com/leanprover-community/mathlib4/cfc55fc58714a59dc06e6e79edc6d1d95140d3c2/Mathlib/Algebra/CharP/Defs.lean).

Official source byte hashes obtained independently through HTTPS:

| Pinned Mathlib path | Bytes | SHA-256 |
| --- | ---: | --- |
| `Mathlib/Data/ZMod/Basic.lean` | 49339 | `f86120453447f00e0c87188381e0e8d15e0d8c85a080c8f8a8ba2da04f5e2f8a` |
| `Mathlib/Algebra/CharP/Basic.lean` | 8039 | `a6692fd078bc04c65a70a530f1aaf3ef2871c2e4c2925d90ff6a39edd9436daf` |
| `Mathlib/Algebra/CharP/Defs.lean` | 16636 | `829bd1854db661787013279f2c49eb5284f5bb19da59dedc7dbeecb4eb8f02e2` |

A static token scan of both producer versions found no occurrences of `sorry`, `admit`, `axiom`, `unsafe`, `native_decide`, or `sorryAx`. The two `?_` placeholders occur in a `refine` step followed by the two supplying proof branches; their presence is ordinary tactic structure, not a use of `sorry`. This source inspection cannot certify that elaboration solves every metavariable or enumerate transitive axioms. The inspected `formal/AxiomAudit.lean` allows only `propext`, `Classical.choice`, and `Quot.sound`, but this reviewer did not execute that audit.

## Resolved original-head dependency finding

Original head line 13 imported `Mathlib.Tactic.Omega`. The official Git tree for the pinned Mathlib commit contains no `Mathlib/Tactic/Omega.lean`. The GitHub tree API returned HTTP 200, `truncated: false`, 10,758 entries, and tree identifier `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`; the requested path was absent. The raw file request separately returned HTTP 404. This is a concrete source dependency defect at the original head, independent of any CI interpretation. [Exact pinned tree](https://api.github.com/repos/leanprover-community/mathlib4/git/trees/cfc55fc58714a59dc06e6e79edc6d1d95140d3c2?recursive=1).

The tree response was 2,818,620 bytes, SHA-256 `27d566f8181f0b3baab40f02308423e94cc8aeb8997deb4f8e1ad0e760700217`. The web reader could not open this API endpoint; a direct standard-library HTTPS request succeeded. No credentials were supplied.

The new head removes that import and both `omega` uses. It replaces them with the explicit positivity/nonzero derivation described above. The theorem type, substantive Mathlib lemmas, target and source claim are unchanged. **Finding resolved by source inspection at the revised head.** A successful build of the revised exact head is still the machine gate's responsibility.

## Worked attack on the missing-bound variant

For any `q ≥ 2`, choose `x = 0` and `y = q`. Then `x ≠ y` in `ℕ` because `q` is positive, while the residue images are equal. Thus the proposed unbounded statement

```text
∀ x y : ℕ, (x : ZMod q) = (y : ZMod q) → x = y
```

is false. This is a symbolic arithmetic counterexample, not a claimed Lean-executed control.

The same witness satisfies `x < q`; it therefore refutes the variant retaining only the bound on `x`. Interchanging the pair refutes the variant retaining only the bound on `y`. Replacing both strict bounds by `≤` also admits the original pair and fails. In the actual declaration, `y < q` becomes `q < q`, so the attack is excluded at exactly the intended hypothesis.

At `q = 2`, the offending pair is `(0,2)` and the bounded representatives are `0,1`. At composite `q = 4`, the pair is `(0,4)` and the bounded representatives are `0,1,2,3`. The proof needs no division or field property. At `q = 0`, the interval `x < 0` is empty and the alias pair no longer consists of distinct values; the main assumption excludes this case. These checks expose the role of the assumptions without asserting a local kernel check.

## Required implementation bridge

Applying this arithmetic result to a named circuit would require, individually:

1. A definition of the concrete parser, external values, encoding and modulus, with a refinement connecting the actual wires to the relevant natural casts.
2. A theorem or source-level constraint analysis establishing which range constraints are enforced and which are absent, including limb and carry rules where applicable.
3. A lifting argument that the alias assignments satisfy the complete concrete constraint system and violate its intended external relation. Equality of one wire expression alone does not supply a satisfying assignment for all constraints.
4. If a protocol-security conclusion is desired, its acceptance relation and security statement connected to that concrete relation and the actual verifier.

None of these bridges is present in the declaration. Their absence matches the frozen target's explicit scope and is not treated as a defect in the arithmetic lemma.

## Attestation, actual reads and procedure limits

Owned joints: source-to-type fidelity at the explicit declaration; quantifiers and bounds; static hole/custom-axiom inspection; official Mathlib dependency correspondence; missing circuit bridge; and the specified `x = 0, y = q` attack. Each holds at the stated arithmetic scope on the revised source. The original import joint broke and was re-reviewed after amendment.

Actual reads were:

- The initial and amended `/var/tmp/mod-alias-review-plan-20261101.md`.
- Exact Git blobs for the target, producer source README, theorem, toolchain, manifest and Lake file at both heads. Semantic attention to the README covered its opening scope/classification/prior-source material, MOD-ALIAS subsection and final acceptance rules; the entire blob was hashed. The full revised theorem and the six-input revision diff were inspected.
- Repository `AGENTS.md` and the literature-first/review-architecture passages of `docs/agent-contract-extended.md` at the original head; formal workspace guidance in `formal/README.md`; and the allowlist/audit logic excerpts of `formal/AxiomAudit.lean`. The latter two reads describe the intended gate, not a passing execution receipt.
- The exact pinned official Mathlib files listed above, focusing on residue values, natural casts, characteristic definitions and interval injectivity. The complete official Git tree was queried for the missing import path.
- Reviewer-method instructions `/var/lib/spot-codex/home/skills/review-evidence/SKILL.md` and its `references/lean-review.md`; memory registry lines 400–430, used for the distinction between kernel validity and source fidelity, not for a result on this theorem.

No sibling reviewer output, blind derivation, producer success report, CI result or build receipt was read. This is the source reviewer, so it has intentionally read the producer proof and does not claim a blind re-derivation. The sibling's separate blindness remains intact from this session's side.

Read-only discovery also attempted a nonexistent local `formal/.lake/packages/mathlib` and a generated, uncommitted `formal/CryptoResearch.lean`; neither supplied source. A filename-only search for `Omega.lean` under `/home/ec2-user` was stopped after unrelated permission errors; no matching source content or sibling report was opened. The failed web/API lookup was replaced by the successful exact-tree request described above. These discovery failures are not theorem failures.

Only the requested report was written. No repository, PR, task state or research status was changed. The source review used no cloud submission and no heavy local process. The producer-head amendment is the sole substantive procedure change; it was explicit, reread and bound before this final verdict.

Coordinator next step: combine this scoped source verdict with the separately obtained blind report and exact-current-head declaration/build/transitive-axiom checks. Retain `source_status: STATED` and preserve protocol-security claims as instructed by the plan.
