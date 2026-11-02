# Independent review: Schnorr special soundness

## Snapshot and permitted sources

- Producer commit: `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd` (`formal: discharge five attack corpus targets`), tree `95cf566e1d0f97e4719cc3c070b52765f8f35fd2`.
- Target: `formal/targets/attack-schnorr-special-soundness.yaml`, Git blob `aad66a2e54e5133f44b0d4a32756cc03d1eb2665`, SHA-256 `47fe013e68f7dbd1ba3957b559a9ad7309877a048234ee62a56d89e3d263cd27`.
- Claim source: only `### SCHNORR-SS — two transcripts extract only under exact fork hypotheses` from `research/cryptographic_assumption_attack_corpus_20261101/README.md`; containing README blob `47aec771e550dcd547d5357030ec35a4c8c3d266`; exact extracted subsection SHA-256 `26209f1b7fd6b4b526940a5e2ff40cde018f8bb1f9d88be81a8baf911634e367`.
- Declared toolchain: `leanprover/lean4:v4.35.0`; pinned Mathlib input revision `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`.
- Proof under review: `formal/CryptoResearch/AttackCorpus/SchnorrSpecialSoundness.lean` at the producer commit, Git blob `feddcdaab31846e4a72c8a09719718bd9130e145`, SHA-256 `495c8ffdcb943972aef7bfb18a588c454d9a4e36f20a10abc6c4be804274df94`.

## Blind-phase compliance record

This section was written before opening the assigned proof. No sibling proof module or prior review/report was read. The main review read the target YAML and requested source subsection from the producer commit, not inferred from the later checkout. One main-process `awk` delimiter mistakenly stopped only at a following level-three heading; because the requested subsection is followed by a level-two heading, that command exposed unrelated later README prose. It exposed no Lean proof or sibling review. To restore a strictly scoped blind derivation, a fresh-context reviewer then read the producer target and exact subsection with an any-heading stop condition and returned the derivation below without opening any Lean proof. Before that exact read, the fresh reviewer also opened the later checkout copy of the same target YAML; its query of the repository-root README emitted no content. These deviations are disclosed rather than presented as perfect source-isolation compliance; proof blindness was preserved.

## Blind mathematical rederivation

Put `d = c1 - c2`. Subtract the two equations in the same orientation as the desired quotient:

```text
s1 - s2
  = (r + c1*x) - (r + c2*x)
  = (c1 - c2)*x
  = d*x.
```

The shared commitment scalar `r` is exactly what cancels. If `q` is prime, `ZMod q` is a field. Distinctness `c1 != c2` gives `d != 0`, so the explicit unit represented by `d` is

```text
u = <d, d⁻¹, d*d⁻¹ = 1, d⁻¹*d = 1> : (ZMod q)ˣ.
```

Multiplying by `d⁻¹` gives

```text
x = (s1 - s2) * d⁻¹ = (s1 - s2) / (c1 - c2).
```

The opposite orientation is valid only when both numerator and denominator change sign: `x = (s2-s1)/(c2-c1)`. A proof using `(s1-s2)/(c2-c1)` would have a sign error. Uniqueness follows similarly: if another `y` obeys both equations, then `d*y = s1-s2 = d*x`, and multiplying by the inverse gives `y=x`.

Necessary hypotheses, at the scalar layer, are therefore:

1. the same scalar `r` in both response equations;
2. distinct challenges, to make `c1-c2` nonzero;
3. a field (here obtained from prime `q`), to turn that nonzero difference into a unit;
4. both scalar response equations themselves.

Prime order and distinct challenges play different roles: distinctness supplies nonzeroness, while primality supplies invertibility of every nonzero scalar. Neither one alone is sufficient over arbitrary `ZMod n`.

## Blind controls

- Positive identity: under the four hypotheses above, subtraction produces `(c1-c2)*x = s1-s2`; division by the explicit unit yields exactly the target quotient.
- Equal-challenge negative control: in `ZMod 5`, choose `c1=c2=0` and `r=s1=s2=0`. Both `x=0` and `x=1` satisfy both equations. Thus two accepting scalar equations with equal challenges need not determine a witness.
- Composite-modulus negative control: in `ZMod 4`, choose `c1=2`, `c2=0`, and `r=s1=s2=0`. The challenges are distinct and their difference is `2`, but `2` is a nonunit. Both `x=0` and `x=2` fit because `2*0 = 2*2 = 0 (mod 4)`. Multiplication by the nonzero difference therefore collides, so division is invalid.

## Post-proof audit

| Obligation | Blind expectation | Implementation / delta |
| --- | --- | --- |
| Same commitment | One shared `r` occurs in both equations. | Exact. Both `h1` and `h2` use the single argument `r`; cancellation is proved by rewriting both hypotheses and `ring`. |
| Distinct challenges | Explicit `c1 != c2`, converted to `c1-c2 != 0`. | Exact. `hc : c1 ≠ c2` is converted with `sub_ne_zero.mpr hc`. |
| Prime field | An explicit prime hypothesis/instance for `q` supplies the field structure. | Exact. `{q : ℕ} [Fact q.Prime]` is present in the audited theorem; Mathlib's prime-`ZMod` field structure is the intended dependency. |
| Unit | The nonzero difference is exposed as a unit, not merely used by an opaque cancellation. | Exact at the proposition level. The conclusion contains `IsUnit (c1-c2)`, proved via `isUnit_iff_ne_zero`; it does not return a named value of `(ZMod q)ˣ`, but `IsUnit` is precisely existence of such a unit and meets the target's invertibility claim. |
| Sign orientation | Numerator `s1-s2` is paired with denominator `c1-c2`. | Exact. After `symm`, `div_eq_iff hdiff` reduces the goal to `s1-s2 = x*(c1-c2)`; the calculation derives `(c1-c2)*x` and closes by commutativity. There is no sign reversal. |
| Uniqueness | Every satisfying witness is forced to the same quotient. | The theorem is universally quantified in `x`, so each `x` satisfying the equations equals the same expression. There is no separate two-witness uniqueness corollary, but the target statement is semantically established. |
| Equal-challenge control | Two distinct witnesses satisfy the same equations. | Stronger/general form. `equal_zero_challenge_nonunique` works over any `Field F` and explicitly supplies `x=0`, `y=1`, `x≠y`, shared zero commitment/responses, and literal zero challenges. |
| `ZMod 4` control | Difference `2` is nonzero but a nonunit, with witnesses `0` and `2`. | Substantively present. `zmod_four_distinct_challenges_nonunique` proves `c1≠c2`, `¬ IsUnit (c1-c2)`, and all four equations for the numeral witnesses `0` and `2`. Narrow delta: its conclusion does not also state `(0 : ZMod 4) ≠ 2`, so the theorem named `nonunique` leaves that trivial separation fact to a consumer. |
| Protocol boundary | No claim of transcript parsing, subgroup soundness, rewinding, PoK, or Fiat--Shamir security. | Exact. The signature contains only scalar equations and the module comment expressly excludes forks, parsers, random oracles, and proof-of-knowledge security. |

## Positive and negative controls

The positive theorem proves both parts promised by the target: the challenge difference is a unit and the witness has the claimed quotient. Its proof uses only the hypotheses visible in the signature. In particular, `hunit` is not smuggled in as an assumption; it is derived from challenge distinctness plus the prime-field instance.

The equal-challenge control is decisive: it includes two explicitly unequal witnesses and shows all four equations. The `ZMod 4` control is also arithmetically decisive: the theorem proves distinct challenges, nonunit difference, and acceptance equations for both `0` and `2`; its proof witnesses the collision through `0 = 4 = 0 + 2*2` in `ZMod 4`. For maximal standalone fidelity, its statement should add `((0 : ZMod 4) ≠ 2)` (and could additionally state `c1*0 = c1*2`) rather than relying on normalization of the displayed numerals. This is a minor control-interface omission, not a defect in the audited positive theorem.

## Machine status

**not_verified pending exact Lean 4.35**. The producer pin is Lean `v4.35.0`, while the installed complete toolchain visible during review was Lean `v4.34.1`; an entry named `leanprover/lean4:v4.35.tmp` did not establish an exact usable 4.35 installation. No proxy compile was performed because shared workspace storage was under active pressure. A 4.34 proxy would in any event be non-authoritative. Static inspection found no mathematical or apparent elaboration defect, but this review does not convert that inspection into a machine-verification claim.

## Fidelity and scoped outcome

The audited declaration name and file match the target. The theorem faithfully formalizes the scalar core and does not enlarge it into a proof-of-knowledge, forking, or Fiat--Shamir theorem. The same-commitment hypothesis is structural (one `r`), challenge distinctness is explicit, primality is explicit as `[Fact q.Prime]`, invertibility is an explicit conclusion, and the quotient orientation is correct.

The source's mention of an exact prime-order subgroup and injective scalar encoding is not silently proved here. It is correctly outside this scalar theorem: the hypotheses assume the transcript equations have already been reduced to equalities in `ZMod q`. The target's phrase “uniquely determined” is satisfied because the theorem applies to every candidate witness satisfying those equations, even though it does not package a separate `x=y` corollary.

Scoped outcome: the main claim **holds** under exactly the advertised scalar hypotheses. The only proof-interface improvement found is the missing explicit `0≠2` conjunct in the `ZMod 4` negative-control statement. Exact Lean 4.35 execution remains outstanding and is reported separately rather than treated as evidence against the mathematics.

## Missing bridges (deliberately out of scope)

- A concrete accepting-transcript predicate and a proof reducing both group verification equations to `h1` and `h2` with one shared commitment scalar.
- Exact subgroup membership/order, a generator representation for the public key, and injectivity/canonicality of scalar and group encodings.
- A bridge showing protocol-level challenge inequality becomes inequality in `ZMod q` without parsing or reduction ambiguity.
- Construction of two forks, extractor runtime and success probability, rewinding, random-oracle programming, and classical/quantum Fiat--Shamir assumptions.
- A proof-of-knowledge or discrete-log reduction tying the recovered scalar to a protocol witness.
- For the composite-ring control alone, the one-line explicit fact `(0 : ZMod 4) ≠ 2` needed to make “two distinct witnesses” a direct conjunct of that declaration.

**Attestation: holds**

## Correction-round addendum

Correction provenance: correction-plan commit `0e096a9d98` binds corrected producer commit `37cc75cfebb30c7582e90e3b632d3454ff5804dc`. This addendum reviewed only the diff from `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd` to that corrected producer and the corrected full `formal/CryptoResearch/AttackCorpus/SchnorrSpecialSoundness.lean`; no sibling module or report was opened.

Corrected module identity: Git blob `c4e44260506974a331715c482895c8a865209529`; SHA-256 `7bdb4110e6e04cff5356bd3f1e9d5e4d92eaa4e6c746efad8a1cc22d38a5c1b8`.

The correction is exact and minimal. `extract_of_distinct_challenges` is unchanged, including the prime-field instance, shared `r`, distinct-challenge hypothesis, explicit `IsUnit` conclusion, and quotient orientation. `equal_zero_challenge_nonunique` is also unchanged. The sole semantic change to the composite-ring control is the new conjunct

```lean
(0 : ZMod 4) ≠ 2
```

with proof `by decide`. The corrected control now states in one theorem that the challenges are distinct, their difference is a nonunit, the two candidate witnesses `0` and `2` are distinct, and both witnesses satisfy both response equations. It therefore establishes nonuniqueness standalone; the original review's only control-interface gap is closed.

Correction-round machine status: the Lean 4.34 proxy compile passed, but it is explicitly non-authoritative for the producer pin. Exact Lean 4.35 verification remains pending, so authoritative machine status remains **not_verified pending exact Lean 4.35**.

Residual gaps are only the previously scoped protocol bridges: accepting group transcripts to the two scalar equations, exact subgroup/order and encoding properties, protocol-to-field challenge inequality, fork construction and probability, and PoK/Fiat--Shamir or discrete-log reductions. None is claimed by this scalar module. There is no residual mathematical or control-fidelity gap in the corrected module.

**Updated attestation: holds**
