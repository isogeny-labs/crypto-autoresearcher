# Adaptive batching source-to-Lean fidelity review

Signed reviewer attestation: `/root/mod_alias_source_review`, independent source-review session, 2026-11-02 UTC. Subject: crypto-autoresearcher PR #2955, claim `ATTACK-BATCH-RLC-ADAPTIVE-CANCELLATION`, frozen target task `TASK-20261101-a0f198`.

**Source-joint verdict: `holds`; fidelity: `faithful_scoped` at exact producer head `8a9daca52daa3c121424bad54c0260cfaedb33b2`.** The declaration states adaptive cancellation over arbitrary fields and a cardinality bound for a nonzero pair fixed across the challenge set of a finite field. The original missing-binder defect is corrected at this head. Static source inspection found no forbidden constructs.

**Machine receipt: pending. Machine status: `not_verified` by this reviewer.** No Lean, Lake, axiom audit, benchmark or build was invoked. No hosted receipt, elaborated environment or transitive axiom inventory was read. This source verdict does not assert the combined `validated_scoped` outcome.

## Inputs, hashes and head amendments

The review plan is `/var/tmp/adaptive-batching-review-plan-20261102.md`: 1988 bytes, SHA-256 `399e4373e5a010728a87e8ac28b85b10d6daca9fd5e39243f6866645a44c4492`. The plan still names original producer head `4018237b567f1a565b3f7296c8c6175b3703cd2e`. The coordinator's explicit replacement-review handoff selected `ce4e8b315cb5c2e4fce457f3699d4cec0d544d13`, then amended the reviewed head to `8a9daca52daa3c121424bad54c0260cfaedb33b2` after the binder finding. These amendments are declared rather than treating the stale plan pointer as current. This reviewer did not inspect the original `4018237…` producer snapshot or the prior reviewer's incomplete output.

All producer inputs were read from immutable Git blobs using `git show REV:PATH` in `/home/ec2-user/crypto-autoresearcher`. The current commit resolved to the full hash above. No mutable working-tree copy supplied the reviewed claim or proof.

| Input at current head | Bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| `formal/targets/attack-batch-rlc-adaptive.yaml` | 2239 | `74c98067481b5a67087dffd1a3847ed02460c791468f8cfab4a5057d17c228a7` | `f1de7bc2652c11d44a5e255367a4785fb054090b` |
| `research/cryptographic_assumption_attack_corpus_20261101/README.md` | 21053 | `a96c1ba72851c01501622503443ea7094557f1b2aa9e7b5c0bfc5641de095bc6` | `47aec771e550dcd547d5357030ec35a4c8c3d266` |
| `formal/CryptoResearch/AttackCorpus/AdaptiveBatching.lean` | 1693 | `2d0526c1773dfdbcf348162a1df68cd2c7387ff596be6ab7c6292073a89ec76c` | `ba5f16bda13474141952718d4e645aa5e5c479c4` |

The source section actually reviewed is the BATCH-RLC subsection beginning at README line 109 and ending before the next subsection at line 127. The extracted section is 1044 bytes, SHA-256 `ce54194127afc1acb0be1b617bcfa8598ed52653dacef703b22225ba04e16b67`. Its extraction starts at `### BATCH-RLC` and stops before the following `\n### ` heading. The full README blob was hashed, but no other README section was used for this replacement review.

The target and README are unchanged between the two reviewed heads. At the initial reviewed head `ce4e8b315cb5c2e4fce457f3699d4cec0d544d13`, the Lean module was 1691 bytes, SHA-256 `1187c37a457cee7a8ca037071af06ec69931d243a4423067cb34cedf0ee71ebb`, Git blob `e5fb227c310273ce1a34588f1a68b56de81380ef`. The only difference in these three inputs is the additional introductory binder at module line 29.

## Claim and quantifier comparison

The named declaration is exactly `CryptoResearch.AttackCorpus.AdaptiveBatching.adaptive_rlc_cancellation`. Its explicit source type, current module lines 20–25, is:

```lean
theorem adaptive_rlc_cancellation :
    (∀ (F : Type u) [Field F] (ρ : F),
      (-ρ) + ρ * (1 : F) = 0 ∧ (1 : F) ≠ 0) ∧
    (∀ (F : Type u) [Field F] [Fintype F] [DecidableEq F] (a b : F),
      ¬ (a = 0 ∧ b = 0) →
        (Finset.univ.filter (fun ρ : F => a + ρ * b = 0)).card ≤ 1)
```

| Owned joint | Comparison and verdict |
| --- | --- |
| Arbitrary-field adaptive half | The first conjunct universally quantifies a universe-polymorphic type with `Field F` and then every challenge `ρ : F`. It has no finiteness hypothesis. The expressions inline the target's exact functions `e0(ρ) = -ρ` and `e1(ρ) = 1`. Both cancellation and nonzero `e1` are present in the same conjunct. Holds. |
| Fixed coefficients | The second conjunct chooses `a,b : F` outside the challenge filter. Every candidate `ρ` in the counted set uses these same values. This is the fixed-pair mathematical statement requested by the target. Holds. |
| Finite scope and count | The repaired half explicitly requires `Fintype F` and `DecidableEq F`. `Finset.univ` enumerates the whole finite field; filtering uses the exact equation, and `.card ≤ 1` bounds the resulting natural-number count. There is no sample, incomplete subset or opaque acceptance predicate. Holds. |
| Nonzero pair | The premise is exactly `¬ (a = 0 ∧ b = 0)`. It permits `b = 0` with `a ≠ 0`, rather than replacing the target with the narrower condition `b ≠ 0`. Holds. |
| Algebraic assumptions | Both halves use a field, whose nontriviality supplies `1 ≠ 0`. The finite half is not silently stated for all rings. Holds. |
| README scope | The adaptive example matches the subsection verbatim in mathematical content. The README repair discusses arbitrary degree `d` and an independent uniform challenge. The target deliberately specializes that repair to two fixed coefficients, at most one root, and no probability theorem. This declaration is faithful to that explicit scoped target; it does not discharge the README's general-degree probability statement. |
| Timing interpretation | Quantification outside the filter represents coefficients that are constant throughout that set. It is not itself a commitment, sampler, transcript or adversary model. The target explicitly identifies quantifier order as the only timing model supplied. Holds at that mathematical scope. |

`Fintype` and `DecidableEq` supply finite enumeration and a decidable filter. They are explicit representation requirements for this `Finset` statement, with no additional arithmetic restriction such as a fixed characteristic or field size. The type is universe-polymorphic through `u`; it is not confined to a named small field.

## Proof-source inspection and corrected binder finding

The adaptive branch simplifies multiplication by one and additive cancellation, retaining the field fact that one is nonzero. In the finite branch, `Finset.card_le_one.mpr` reduces the cardinality assertion to equality of any two members. The membership simplification yields two equations with the same `a,b`.

The proof then handles both coefficient cases. If `b = 0`, any root would force `a = 0`, contradicting the nonzero-pair hypothesis; this correctly covers the constant nonzero case with no roots. If `b ≠ 0`, the two root equations imply `ρ*b = σ*b`, hence `(ρ-σ)*b = 0`. The field's zero-product property forces `ρ-σ = 0` because the alternative contradicts `b ≠ 0`; thus `ρ = σ`. This proves the intended at-most-one count at the source-argument level.

The inspected imports are `Mathlib.Algebra.Field.Basic` and `Mathlib.Data.Finset.Card`. The proof names `Finset.card_le_one`, `Finset.mem_filter`, `Finset.mem_univ`, `add_left_cancel`, `sub_mul`, `sub_self`, `mul_eq_zero` and `sub_eq_zero`, plus simplification. Their intended uses match the field and finite-set argument. Under the requested four-input reading boundary, this reviewer did not inspect dependency trees, toolchain files or imported module definitions; availability and elaboration at the pinned dependencies remain part of the machine gate.

At the initial reviewed head, line 29 was:

```lean
intro F _ _ a b hab
```

After the second conjunct's binders `F`, `[Field F]`, `[Fintype F]`, `[DecidableEq F]`, `a`, `b`, and the implication hypothesis, this introduction supplied one name too few. At the source level, the name `a` would introduce the equality-decision instance, the names `b` and `hab` would introduce the two field elements, and the nonzero-pair implication would remain before the attempted cardinality proof. This was reported as a concrete binder-alignment defect without claiming a local Lean error log.

At the current exact head, line 29 is:

```lean
intro F _ _ _ a b hab
```

There are now seven introductions, matching the type's binders and hypothesis. The substantive statement and subsequent proof are unchanged. **The reported binder-alignment defect is corrected by source inspection.** No source revision was made by this reviewer.

A static scan of the entire producer Lean module at both reviewed heads found no occurrences of `sorry`, `admit`, `axiom`, `unsafe`, `native_decide` or `sorryAx`. There are no visible unfinished tactic placeholders or producer-defined axioms. The `classical` command is explicit use of the classical environment, not a custom axiom declaration. A token scan cannot replace elaboration or a transitive axiom audit; no zero-axiom claim is made here.

## Worked attacks required by the plan

**Dropping fixedness breaks the root bound.** Choose `a(ρ) = -ρ` and `b(ρ) = 1`. The pair is nonzero for every challenge, yet its equation vanishes for every challenge. In `F₂`, the accepted challenges are both field elements, so the count is `2`, exceeding `1`. The actual fixed-pair theorem cannot be applied to this entire adaptive set: choosing a different coefficient pair for each member is a different predicate from filtering with one fixed pair.

**Allowing the zero pair breaks the root bound.** If `a = b = 0`, then every field element satisfies the equation. In `F₂`, there are two roots. The actual theorem excludes this pair with its explicit premise. Conversely, the proof preserves the legitimate case `b = 0`, `a ≠ 0`, where there are zero roots.

These are exact symbolic counterexamples derived in this source-review session, not claimed Lean-executed or measured controls. They show the role of the fixed-pair quantification and nonzero-pair premise. They were not obtained from a sibling report.

## Boundary and next gate

A probability statement requires a defined distribution and a proof that the counting event is the event sampled; the familiar division by field cardinality requires uniform sampling. A batching-protocol result additionally needs a refinement connecting actual errors and acceptance to this scalar equation and a proof that the errors are fixed independently of the challenge. Fiat–Shamir use needs its transcript-binding and challenge model. General degree, multiple equations, group equations and encodings need their own corresponding statements. The frozen target explicitly leaves these interfaces outside this declaration.

The next gate is the current-head hosted Lean result, including this exact named declaration, its elaborated type, source and dependency identity, complete-source coverage and allowed transitive axioms. The coordinator reported a new hosted attempt as pending; this reviewer has not inspected that attempt or its predecessor. Both independent review dimensions and that machine evidence are required before a combined validation verdict. `source_status: STATED` and all experiment/hypothesis statuses are unchanged by this report.

## Independence and actual-read attestation

Joints owned: source/target-to-type fidelity; arbitrary-field versus finite-field scope; fixed-coefficient quantifiers; explicit cardinality and nonzero-pair bound; static forbidden-construct inspection; import/declaration inspection; and the missing-fixedness/zero-pair attacks.

Actual source reads for this replacement review were limited to:

1. `/var/tmp/adaptive-batching-review-plan-20261102.md`, read before source review and again after the head amendment; its bytes were unchanged.
2. The exact frozen target YAML at `ce4e8b315cb5c2e4fce457f3699d4cec0d544d13`, then its identical bytes at `8a9daca52daa3c121424bad54c0260cfaedb33b2`.
3. The BATCH-RLC source README section at those heads, with the whole blob retrieved only to extract and hash the relevant section and bind the full source hash.
4. The full producer Lean module at both heads, and the scoped Git diff between these three allowed producer inputs.

No sibling blind review, prior source-review report, producer discussion, PR body, CI log, machine receipt, unrelated repository source, dependency source or external literature was read. No memory file was consulted for this replacement review. The source reviewer intentionally read the producer proof and makes no blind-rederivation claim. The signature above attests to these actual reads and scoped findings; the separately returned SHA-256 identifies the report bytes and is not represented as a public-key digital signature.

Procedure amendments: replacement of the service-limited reviewer; selection of the newer exact head by the coordinator; and affected-joint re-review after the binder correction. No service-limit error occurred in this replacement session. Only this requested report was written; no repository or PR mutation, build, cloud launch or scientific state transition was performed.
