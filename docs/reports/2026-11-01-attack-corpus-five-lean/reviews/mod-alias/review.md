# Independent review: MOD-ALIAS

Date: 2026-11-01
Joint: modular alias / bounded repair
Bound producer commit: `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd`
Producer tree: `95cf566e1d0f97e4719cc3c070b52765f8f35fd2`
Exact declaration: `CryptoResearch.AttackCorpus.ModAlias.modulus_alias_and_bounded_repair`

## Snapshot, hashes, and sources read

The producer artifacts were read from Git objects at the bound commit rather
than from the later review worktree. Hashes are SHA-256 unless identified as a
Git object ID.

| Artifact | Revision/read scope | Identity |
| --- | --- | --- |
| Producer snapshot | bound commit | commit `f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd`; tree `95cf566e1d0f97e4719cc3c070b52765f8f35fd2` |
| Review plan | complete file | `e905afe5ee9d354490b273174fee1b1988ded8f096479d2f37d5f734ab8a0e13` |
| Frozen target `formal/targets/attack-mod-alias.yaml` | producer commit, complete file | `3b6a5a7226655323b2e266f079311f5417f0b6d9d4dfaa9a40cb85a82624e498` |
| Attack-corpus source note | producer commit, only `### MOD-ALIAS — field equality is not integer equality` | whole-file hash `a96c1ba72851c01501622503443ea7094557f1b2aa9e7b5c0bfc5641de095bc6`; extracted-subsection hash `a2b079e5a8f5d0c86915d5e86a2c20104d5dd046cc5c4ea12e8bfd156bbd9685` |
| Assigned proof `formal/CryptoResearch/AttackCorpus/ModAlias.lean` | producer commit, opened only after the blind derivation | `d789bc60d85a7849564ae41e94d3c76de7e6d5cabead35763a197ed6d5cb42d2`; Git blob `ed9ac9a128a85cf8a8f24db5bac78c30ffa1fb26` |
| `formal/lean-toolchain` | producer commit | `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c` (`leanprover/lean4:v4.35.0`) |
| `formal/lakefile.toml` | producer commit | `104369773c0926608c11ccfdc5e10178041269371566ea11a46baf816f4a9b4d` |
| `formal/lake-manifest.json` | producer commit | `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` |

Governing/reference sources read were `AGENTS.md` (complete), the
`Literature first` subsection of `docs/agent-contract-extended.md`,
`.claude/skills/route/SKILL.md`, `docs/skill-routing.md`,
`docs/skill-catalog.json`, `.claude/skills/review-evidence/SKILL.md`,
`.claude/skills/formal/SKILL.md`,
`.claude/skills/review-evidence/references/lean-review.md`,
`formal/README.md`, `formal/targets/README.md`, and
`orchestration/formal/cli.py`. The relevant literature/source review was the
frozen internal source note: this elementary quotient/injectivity check makes
no novelty claim and required no external paper. No sibling proof module or
sibling review report was read.

## Blind-derivation compliance

The derivation below was recorded at `2026-11-01T23:58:02Z`, before opening
`formal/CryptoResearch/AttackCorpus/ModAlias.lean`. Before this record was
written, the reviewer read only the governing review/agent/skill references,
the assigned frozen target, the matching `MOD-ALIAS` source-note subsection,
and the formal workspace pins. No sibling proof module, sibling review report,
producer discussion, or producer proof source was read. The Lean/source
inspection fields later in this report were deliberately left pending at this
point.

## Blind mathematical derivation

Let `q` be a natural modulus. For `q > 0`, casting a natural into `ZMod q`
retains only its residue modulo `q`. Since `q mod q = 0`, the natural witnesses
`0` and `q` have the same image:

```text
(0 : ZMod q) = (q : ZMod q).
```

They are distinct exactly when `q > 0`. Thus the alias counterexample works at
the boundary `q = 1`; at `q = 0`, the proposed natural witnesses coincide, so
there is no counterexample with distinct `0` and `q`. The frozen hypothesis
`2 <= q` is sufficient but is one step stronger than the source note's minimal
positive-modulus condition.

For the repair, suppose `x < q`, `y < q`, and the casts of `x` and `y` into
`ZMod q` are equal. Equality in the quotient implies
`x mod q = y mod q`. The strict bounds make each natural its own canonical
remainder, so `x = x mod q = y mod q = y`. Nonnegativity needs no separate
hypothesis because `x` and `y` are naturals. This establishes injectivity on
the explicit half-open interval `[0,q)`.

Both strict upper bounds are load-bearing:

- If `x < q` is removed while `y < q` remains, take `x = q` and `y = 0` for
  any positive `q`.
- If `y < q` is removed while `x < q` remains, take `x = 0` and `y = q`.
- If both are removed, either pair is the unrestricted-injectivity
  counterexample. Replacing either strict bound by a non-strict `<= q` also
  admits the corresponding endpoint alias.

Boundary controls derived without the proof:

- `q = 0`: distinctness of `0` and `q` fails; the repair hypotheses `x < 0`
  and `y < 0` are impossible and hence only give a vacuous implication.
- `q = 1`: `0` and `1` are distinct and alias in `ZMod 1`; bounded repair
  still holds because every natural below `1` is `0`.
- `q = 2`: `0` and `2` are distinct and alias, while the only bounded
  representatives are `0` and `1`, providing a concrete positive control for
  the repair.

## Hypothesis-delta table

| Obligation | Source note | Frozen target | Lean declaration |
| --- | --- | --- | --- |
| Modulus binder | Every natural `q` subject to positivity | `(q : Nat)` | `(q : Nat)`; exact |
| Positivity/range of moduli | `q > 0` | `(hq : 2 <= q)` | `(hq : 2 <= q)`; exact to frozen target, but a **scoping delta** from the source that excludes the valid `q = 1` case |
| Distinct natural witnesses | Says `0` and `q` are distinct | Required under `2 <= q` | Explicit first conjunct `(0 : Nat) != q`; no assumed distinctness |
| Alias equality | Casts of `0` and `q` into `ZMod q` are equal | Explicitly required | Explicit second conjunct `(0 : ZMod q) = (q : ZMod q)`; equality orientation is equivalent to the note's alternate wording |
| Repair domain/quantifiers | For all naturals `a,b`, after fixing `q` | For all naturals `x,y`, after fixing `q` | `forall x y : Nat` inside the same declaration; same order and uniformity |
| First canonical bound | `a < q` | Explicit `x < q` | Explicit arrow premise `x < q`; consumed by `ZMod.val_natCast_of_lt` |
| Second canonical bound | `b < q` | Explicit `y < q` | Explicit arrow premise `y < q`; independently consumed by `ZMod.val_natCast_of_lt` |
| Cast-equality premise | Explicit | Explicit | Explicit `(x : ZMod q) = (y : ZMod q)` |
| Repair conclusion | `a = b` | `x = y` | Exact `x = y` |
| Extra instances, `Fact`s, or side conditions | None | None | None. The auxiliary repair lemma omits a separate `q > 0`; either satisfiable strict bound already implies it. |
| Protocol/model scope | Separate canonical theorem needed for signed/multi-limb encodings; source-to-constraint bridge required for a circuit claim | Finite-ring equality only; named-system soundness excluded | Module documentation preserves this boundary; the theorem type contains no protocol object or implementation bridge |

## Controls

### Positive controls

- Alias at `q = 2`: the theorem's premise is inhabited, its distinctness
  conjunct is true, and `ZMod.natCast_self` supplies the alias.
- Repair at `q = 2`: the only canonical representatives are `0` and `1`, so
  cast equality identifies the same representative.
- Boundary `q = 1`: although the main declaration cannot be instantiated,
  the mathematical source claim still holds: `0 != 1`, the casts alias in
  `ZMod 1`, and the only bounded representative is `0`. This is a positive
  control that exposes nonminimal `2 <= q`, not a counterexample to the result.
- General repair: lines 25--26 apply `congrArg ZMod.val` and rewrite with
  `ZMod.val_natCast_of_lt` once for each explicit bound; lines 41--42 pass all
  three premises to that helper. No opaque encoding predicate appears.

### Known-false / proves-too-much controls

- Remove `x < q`: `x = q`, `y = 0` must refute the resulting statement.
- Remove `y < q`: `x = 0`, `y = q` must refute the resulting statement.
- Remove both range premises: residue equality must not become unrestricted
  natural-number injectivity.
- Admit `q = 0` while retaining the claim that `0` and `q` are distinct: the
  claimed counterexample must fail.
- Treat `2 <= q` as necessary: `q = 1` refutes that necessity, since both the
  alias and bounded repair still hold there.

These controls are mathematical/source inspections, not exact-toolchain
machine results. The one-sided range weakenings are genuinely false, rather
than merely unavailable through this proof.

## Producer-source inspection

The exact declaration at lines 34--42 is a conjunction of all three required
facts: explicit natural-number distinctness, the `ZMod q` alias, and the
universally quantified bounded repair. `hq` is used to prove distinctness;
`ZMod.natCast_self` proves the alias; and the repair invokes the separately
stated `bounded_natCast_injective` helper. The helper proves injectivity by
applying `ZMod.val` to cast equality and using each strict range premise to
identify the stored values with the original naturals.

The source contains no textual `sorry`, `admit`, custom `axiom`, or `unsafe`
declaration. This static observation is not a replacement for compilation or
the fail-closed transitive axiom audit.

## Machine status

`not_verified` pending the exact pinned Lean/Mathlib 4.35.0 build, generated-root
module discovery, fail-closed axiom audit, exact named-declaration audit,
forbidden-construct checks, and input-hash checks. Any local Lean 4.34.1 proxy
result is non-authoritative.

The available executables report Lean `4.34.1` (commit
`5045d0056413266e57c625dcd7c365b10e377c52`) and Lake
`5.0.0-src+5045d00`. A temporary proxy copy was hash-matched to the producer
source, but the optional compile was stopped before completion when the shared
overlay fell to approximately 117 MiB free. Therefore there is no fresh proxy
elaboration result to count, and no status is inferred from the resource stop.
The exact 4.35 CI evidence remains the only authoritative pending check.

## Fidelity and scoped outcome

- **Frozen-target fidelity:** `faithful_scoped`. The exact named declaration
  includes the requested counterexample and explicit bounded repair in one
  theorem, with the two natural range premises visible.
- **Source-note fidelity:** `partial`. The source states the result for every
  positive `q`, while both the frozen target and Lean declaration require
  `2 <= q`. The omitted `q = 1` case satisfies the same result, so this is an
  unnecessary narrowing, not a false theorem. Under the formal-review rule,
  this scoping delta prevents an unqualified source-fidelity rating.
- **Mathematical scoped finding:** the declaration's finite `ZMod` statement
  survives the quantifier and boundary attacks. Both bounds are necessary for
  unrestricted natural inputs, and the repair is explicit.
- **Review outcome:** `inconclusive` for machine validation because the exact
  4.35 build/audits are pending. It cannot yet be `validated_scoped` even
  though the assigned mathematical joint holds by independent derivation and
  source inspection.

No protocol, circuit, elliptic-curve decoder, commitment, Fiat--Shamir, or
proof-of-knowledge conclusion follows from this finite `ZMod` statement alone.

## Missing protocol bridges

The following remain wholly outside the declaration:

- identification of a named protocol/circuit wire type with the relevant
  `ZMod q`, including the concrete modulus;
- a refinement from external integers/bytes to natural canonical
  representatives in `[0,q)`;
- source/compiler-to-constraint semantics showing whether both range checks
  are present or absent at the relevant equality;
- signed-value conventions, limb decomposition and carry constraints,
  non-native/foreign-field reduction, and inter-gate overflow behavior;
- host-language and byte serialization/deserialization correctness;
- connection from an arithmetic alias to an accepting forged transcript,
  circuit unsoundness, commitment failure, Fiat--Shamir failure, or a
  proof-of-knowledge/security-game violation.

## Attestation

`joints_owned`: modular alias and explicit bounded repair.
`sibling_report_access`: none.
`blind_rederivation`: compliant; recorded before assigned-proof access.
`machine_status`: `not_verified` pending exact 4.35 CI.
`verdict`: **`holds`** — the assigned mathematical joint and frozen statement
survive the attacks; source fidelity is narrowed at `q = 1`, and machine
validation remains pending.

## Correction-round addendum — 2026-11-02

### Bound correction and review scope

This addendum preserves the original review and re-reviews only the MOD-ALIAS
change from producer commit
`f5a8f8ac8c3cbae424b5cc56170f2e5db2dfa7cd` to corrected producer commit
`37cc75cfebb30c7582e90e3b632d3454ff5804dc`, under the correction-round plan
committed at `0e096a9d98`. The corrected producer tree is
`e243b992c16f79a68277320be130b485fc0035b2`.

Sources newly read were the correction amendment in the bound review plan,
the assigned `ModAlias.lean` producer-to-correction diff, and the corrected
full `ModAlias.lean` module. No sibling module or sibling report was read.
The corrected module has SHA-256
`81353b007ec158f8383504d7614717551eaa477197ef7d925fe06ff2d52f1420`
and Git blob `af53e85fc702bcd0259884e2750f332a2a7507ca`, matching the correction
plan. The frozen target remains byte-identical at SHA-256
`3b6a5a7226655323b2e266f079311f5417f0b6d9d4dfaa9a40cb85a82624e498`.

### Correction checks

| Check | Corrected evidence | Assessment |
| --- | --- | --- |
| Sharp source boundary | New `modulus_alias_and_positive_bounded_repair (q : Nat) (hq : 0 < q)` concludes distinctness, alias equality, and the same explicitly bounded universal repair | Resolves the source note's positive-modulus scope at module level |
| `q = 1` coverage | The sharp theorem is directly instantiable with `q = 1`; its type includes all three conclusions, not merely the alias | Resolves the omitted positive boundary identified in the first review |
| `q = 0` control | New `zero_modulus_witness_not_distinct` proves `not ((0 : Nat) != (0 : Nat))` | Explicitly records why zero is outside the distinct-witness counterexample |
| Frozen exact name/type | `modulus_alias_and_bounded_repair (q : Nat) (hq : 2 <= q)` retains exactly the prior conjunction and quantifier order | Preserved; the frozen verifier target and spec hash do not drift |
| Relationship between sharp and frozen theorems | The frozen theorem is now a corollary of the sharp theorem after deriving `0 < q` from `2 <= q` | Makes the narrowing deliberate and proof-visible |
| Bounded repair | Both `x < q` and `y < q` remain explicit; the sharp theorem passes both and cast equality to `bounded_natCast_injective` | The one-sided counterexamples remain blocked for the right reason |
| `omega` dependency | The corrected module contains no `omega`; positivity gives `q != 0` via `Nat.ne_of_gt`, distinctness via `Ne.symm`, and the frozen premise is converted with elementary order facts plus `decide` | Extraneous tactic dependency removed without adding a semantic premise |
| Forbidden source constructs | No textual `sorry`, `admit`, custom `axiom`, or `unsafe` appears in the corrected module | Static control passes; not a substitute for the exact axiom audit |

The earlier source-fidelity delta is therefore **resolved for the corrected
module**: the new sharp declaration formalizes exactly the source note's
`q > 0` scope, including `q = 1`, while the old exact name remains the required
frozen `2 <= q` corollary. A citation that intends the full source claim should
cite `modulus_alias_and_positive_bounded_repair`; citing only the frozen exact
name still communicates the intentionally narrower modulus range.

### Correction-round machine status

The corrected SHA passed the available Lean/Mathlib 4.34 proxy compile as
reported for the correction round. That is a non-authoritative elaboration
control only. Machine status remains **`not_verified`** pending the exact
pinned Lean/Mathlib 4.35 build, generated-root discovery, fail-closed project
and transitive axiom audits, exact named-declaration audit, forbidden-construct
gate, and input-hash checks at corrected commit
`37cc75cfebb30c7582e90e3b632d3454ff5804dc`. The earlier exact-toolchain run,
if any, cannot validate these changed bytes.

### Residual gaps and updated scoped attestation

The mathematical correction leaves no MOD-ALIAS quantifier or boundary defect
found by this review. Residual gaps are machine verification on exact 4.35 and
all protocol/refinement obligations enumerated in the original review. In
particular, neither the sharp theorem nor the explicit zero control establishes
that a named circuit lacks a range check or that an arithmetic alias yields a
protocol-security violation.

`correction_scope`: assigned MOD-ALIAS diff and corrected full module only.
`source_fidelity`: `faithful_scoped` for the corrected module; frozen exact
declaration remains deliberately scoped to `2 <= q`.
`machine_status`: `not_verified` pending exact 4.35 CI at the corrected SHA.
`updated_verdict`: **`holds`** — the source-fidelity finding is resolved at
module level, the frozen exact target remains intact, and only the stated
machine and protocol bridges remain open.
