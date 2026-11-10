# Source review: `CryptoResearch.Quotient.translation_commutes_iff_two_torsion`

- **Task:** TASK-20261106-6d4fa6 (source reviewer), authorized by DEC-20261106-2f9a94
- **Handoff:** `coordination/formal-reviews/quotient-translation-descent-20261106/source-handoff.yaml`
  (read at `git:a9717726f2fd6f59f213f43d05e16604a61fe998`, branch `claude/sheriff-a114e7-records`)
- **Joints owned:** J1 (Lean statement fidelity), J2 (machine evidence), J3 (claim boundary).
  J4 (blind re-derivation) and the proves-too-much objects belong to TASK-20261106-bb6ab4 and are
  not reported here. This report gives one verdict per joint and no whole-claim outcome; the
  Coordinator composes the outcome.
- **Session:** `session_01TCbLH8Dra5BPD9qPmhUPhz`, model `claude-opus-5-5` (from `get_session`:
  `session_context.model` and `last_served_model`). Its `parent_session_id` is
  `session_01TCbLH7HXJioSw2Bzx7P9p9`, the plan author. It is a separate session with its own
  context, not one of the three excluded sessions. The lineage is disclosed in the attestation.
- **Date:** 2026-11-06

## Verdicts

| Joint | Verdict | One-line basis |
| --- | --- | --- |
| J1 | **holds** | The fresh elaborated type is exactly the claim. The hypothesis-delta table has no `scoping` or `unjustified` row. Both directions are proved, and the only axiom is `propext`. The kernel-`decide` checks agree on every (S, T) in ZMod 1, ZMod 2, ZMod 4 and ZMod 2 × ZMod 4. The theorem instantiates on Mathlib's elliptic-curve point group. |
| J2 | **holds** | The hosted `lean-verification` run 42167929729 was dispatched by this session on main `d5001059cd`. Its formal-workspace job succeeded: `lake build` and `tools/verify_formal_targets.py --min-verified 66` both passed. The receipt for the exact declaration is `machine_verified` and binds all four pinned or bound hashes. The fresh `#print axioms` output is `[propext]`, both locally and hosted. |
| J3 | **breaks** | `formal/targets/README.md:276-277` (live) cites the 2026-10-29 check as an "independent semantic review" that is `validated_scoped`. In isogeny-labs/crypto, `companion_catalogue.tex` and `build_map_ideas_corpus.py` present descent, the Corollary and the Galbraith closure as Lean-formalized. |

## Pinned inputs and head

The review used head `d5001059cd1b6c4dbfd7d7f894ac9c3b9c2b9806` (origin/main as fetched at 2026-11-06 about 05:05 UTC;
at or after fd2697b3e8). Bytes were checked with `git show <rev>:<path> | sha256sum` and in the checkout.

| Path | sha256 at d5001059cd | Pinned in handoff |
| --- | --- | --- |
| formal/CryptoResearch/Quotient/TranslationDescent.lean | 359a5cedaedd1be8aa728f7ca5e71e185377dbc9f2a9fed78e073321d6bf401e | equal |
| formal/targets/quotient-translation-descent.yaml | 12fa5950f33f807c5968337053ab402edbd6392c6b088fe0c226f6bc44bdd24b | equal |
| research/THM_QUOTIENT_DESCENT1.md | ac91debeb577ddcece45e13b190c048797662801a3a21e973df1325c9199b08e | equal |
| formal/lean-toolchain (`leanprover/lean4:v4.35.0`) | ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c | bound here |
| formal/lake-manifest.json | b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7 | bound here |

The same five hashes hold at `a9717726f2` (the handoff's branch head). Every installed package
revision under `formal/.lake/packages` equals its `lake-manifest.json` pin, and none has a dirty tree
(`source-evidence/manifest-revs.txt`, `source-evidence/installed-package-revs.txt`). The pins are
mathlib `cfc55fc58714`, CryptoLean `60952c696ded`, batteries `66e469188fe0`, aesop `4a174c490d87`,
Qq `dce0ad79c486`, plausible `dfa4f38190d0`, proofwidgets `df72b022e558`, importGraph
`a41f0e9a4dea`, LeanSearchClient `d6b4c7be5be7` and Cli `c24fe6078c63`. The local `lean --version`
was `Lean (version 4.35.0, x86_64-unknown-linux-gnu, commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc, Release)`.

## J1: Lean statement fidelity (holds)

### Claim under review (target yaml lines 19-23, verbatim)

> In an additive commutative group E, for all S and T:
> (for every P, -(P + S) + T = -(P + T + S)) holds if and only if 2 T = 0.
> That is, translation by T commutes with the involution
> iota_S(P) = -(P + S) exactly when T is 2-torsion, whatever S is.

### Elaborated type (fresh, from `source-evidence/J1Fidelity.out`)

The command was `#check @translation_commutes_iff_two_torsion` under `pp.universes true`. Pretty form:

```
theorem CryptoResearch.Quotient.translation_commutes_iff_two_torsion.{u} :
  ∀ {E : Type u} [inst : AddCommGroup.{u} E] (S T : E),
  (∀ (P : E), -(P + S) + T = -(P + T + S)) ↔ (2 : ℕ) • T = 0
```

The full `pp.explicit` output (in `J1Fidelity.out`) confirms the instance paths. Every `+`
resolves through `AddCommGroup.toAddCommMonoid inst`. Every `-` resolves through
`AddCommGroup.toDivisionAddCommMonoid inst`. `•` is `HSMul ℕ E E` via
`AddMonoid.toNSMul (AddGroup.toSubNegMonoid (AddCommGroup.toAddGroup inst))`, with the literal
`@OfNat.ofNat ℕ 2`. `0` is the group's zero. There is no other instance, `Fact` or side condition.

### Clause crosswalk

| Claim clause | Lean | Match |
| --- | --- | --- |
| "an additive commutative group E" | `{E : Type u} [AddCommGroup E]` | exact |
| "for all S and T" (outermost) | `(S T : E)` as outer Π-binders | exact |
| "(for every P, …)" on the left side only | `(∀ P : E, …)` scoped inside the left operand of `↔` | exact |
| "-(P + S) + T" | `-(P + S) + T`, i.e. `HAdd (Neg (HAdd P S)) T` | exact, same association |
| "-(P + T + S)" | `-(P + T + S)`, i.e. `Neg (HAdd (HAdd P T) S)` | exact, left-associated as written |
| "if and only if" | `Iff`, both fields `mp`, `mpr` constructed in `#print` | exact |
| "2 T = 0" | `(2 : ℕ) • T = 0` | equal to `T + T = 0` and to `(2 : ℤ) • T = 0` (proved, below) |
| "whatever S is" | no hypothesis on S (the stub's `2 • S = 0` is absent) | exact |
| gloss "translation by T commutes with iota_S" | the equation is `τ_T ∘ ι_S = ι_S ∘ τ_T` evaluated pointwise | exact (gloss only) |

**Forward direction (mp).** `#print` shows it uses `h 0` and the `abel` lemma `_abel_1_1`:
`2•T = (-(0+S)+T) - -(0+T+S)`. The hypothesis is applied to P = 0 only, which is all the claim's
"for every P" needs. **Reverse direction (mpr).** For every P it uses `_abel_1_2`:
`-(P+S)+T = -(P+T+S) + 2•T`, then `hT` and `add_zero`. Neither direction assumes its conclusion:
the only hypotheses are `h` and `hT`, and the binders carry no premise.

### Hypothesis-delta table

Each row is a binder, instance, fixed parameter or side condition of the elaborated type, set
against the claim.

| Row in the type | Claim states it? | Mark | Justification |
| --- | --- | --- | --- |
| universe `u` | implicit | implied | The claim ranges over every additive commutative group. Universe polymorphism only widens that, and the theorem instantiates at `Type` (below). |
| `{E : Type u}` implicit | yes ("group E") | implied | Determined by `S T`. Implicitness changes no content. |
| `[AddCommGroup E]` | yes | implied | This is the claim's own hypothesis. It is the only instance. |
| `(S T : E)` explicit, outermost | yes ("for all S and T") | implied | Same quantifier order as the claim. |
| `∀ P` inside the left side | yes | implied | Same placement. Not load-bearing in an abelian group: the `∃ P` and "∀ P outside the iff" variants are also proved (section 4 of `J1Fidelity.lean`). |
| `(2 : ℕ) • T` (ℕ-smul) | "2 T" | implied | `two_nsmul : 2 • T = T + T` and `two_zsmul`. All three readings are proved interchangeable (section 3). |

**No row is `scoping` or `unjustified`.** The note's curve setting (E(k̄), char k ≠ 2) adds no
row. The type mentions no field or characteristic, and `char k ≠ 2` is not needed for the
identity. It is needed only for the note's prose geometry, which is outside this claim.

### Instantiation on the note's setting (no scoping row)

`J1Fidelity.lean` section 5 elaborates `translation_commutes_iff_two_torsion S T` with E set to
Mathlib's `WeierstrassCurve.Affine.Point W` in two cases:

- over an arbitrary field `F`, with `[DecidableEq F]`;
- over `AlgebraicClosure k` for an arbitrary field `k`, using the classical instance only, so this is E(k̄) with the characteristic left free.

Both elaborate with no error. `[DecidableEq F]` is a binder of Mathlib's
`AddCommGroup W.Point` instance (Affine/Point.lean:653, 805), not of the theorem under review, and
it is always available classically. This closes the bridge the 2026-10-29 review listed as
unsupported ("no curve object in Lean"). The scope is that bridge alone: that the identity applies
to the curve's point group. It does not cover any geometric statement about quotients.

### Degenerate cases and exhaustive kernel checks

All of these are kernel `decide`, with no `native_decide`. The predicate is the reviewer's own
reading of the claim with "2 T" as `T + T`, checked against the Lean proposition, for every S and T:

| Group | Statement | Result |
| --- | --- | --- |
| ZMod 1 (trivial group) | `agreeAll`: claim ↔ (T+T=0), and (T+T=0) ↔ (2•T=0) | proved |
| ZMod 2 (exponent 2) | same | proved |
| ZMod 4 | same | proved |
| ZMod 2 × ZMod 4 | same | proved |
| ZMod 2 × ZMod 2 (exponent 2) | left side holds for every S, T, P | proved |
| ZMod 4, S = 0 | claim with S = 0, for every T | proved |
| Instrument control: ZMod 4 with `4 • T` in place of `2 • T` | the harness proves the **negation** | proved (the harness can detect a disagreement) |

The axioms of these checks are `[propext, Classical.choice, Quot.sound]`, which come from Mathlib's
`ZMod` and `Fintype` instances. That is standard.

### Commands and exit status (J1)

```
cd formal && lake env lean ../coordination/formal-reviews/quotient-translation-descent-20261106/source-evidence/J1Fidelity.lean
exit 0 (real 3.7s); output: source-evidence/J1Fidelity.out
```

## J2: machine evidence (holds)

### Fresh local evidence (module-scope check, labelled as such)

```
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain none   (elan 4.2.4)
cd formal && lake exe cache get Mathlib.Tactic.Abel Mathlib.Data.ZMod.Basic \
    Mathlib.AlgebraicGeometry.EllipticCurve.Affine.Point Mathlib.FieldTheory.IsAlgClosed.AlgebraicClosure   exit 0
cd formal && lake build +CryptoResearch.Quotient.TranslationDescent    exit 0
    "⚠ [631/631] Built CryptoResearch.Quotient.TranslationDescent (2.0s)"; "Build completed successfully (631 jobs)."
    (the only warning: module-system advisory for `import Mathlib.Tactic.Abel`)
#print axioms CryptoResearch.Quotient.translation_commutes_iff_two_torsion
    → 'CryptoResearch.Quotient.translation_commutes_iff_two_torsion' depends on axioms: [propext]
```

The module itself was compiled fresh from the pinned bytes. Its 630 dependencies are Mathlib's
prebuilt cache oleans for the pinned Mathlib revision, which is Lean/Lake's normal trust boundary.
`#print axioms` covers the declaration's whole transitive dependency chain, including the
`abel`-generated auxiliary lemmas `_abel_1_1` and `_abel_1_2`. The only axiom is `propext`: there is
no `sorryAx` and no custom axiom.

This local check does not replace the target gate. `tools/verify_formal_targets.py` (the gate)
builds the whole workspace and checks every discharged target. It was **not run locally**: the
session's disk allowance (about 11 GB free after the module cache) does not fit a full Mathlib
cache plus a workspace build. `problems/formal-workspace-build-exceeds-16gb.md` also records a
memory ceiling for the full build. The gate route was therefore taken on hosted CI, below.

`lean4checker --fresh`: **not available.** `git ls-remote --tags https://github.com/leanprover/lean4checker`
lists no tag for v4.34 or v4.35. No independent kernel replay was run, and none is claimed.

### Fresh hosted evidence (primary route)

This session dispatched `lean-verification.yml` with `workflow_dispatch` on `main` at 2026-11-06T05:21:19Z.

- Run: https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/42167929729 (run 3239, attempt 1, head `d5001059cd1b6c4dbfd7d7f894ac9c3b9c2b9806`).
- Job `formal workspace (lake build + axiom audit)` 127728745985: **success**, 05:21:37Z to 05:56:29Z. These steps all passed:
  - "Verify actual installed dependency source pins before proof checks"
  - "Build the workspace" (`lake build`, 05:26:19Z to 05:46:22Z)
  - "Machine-check every discharged formal target" (`python3 tools/verify_formal_targets.py --artifact-dir formal-receipts --min-verified 66`, 05:46:22Z to 05:55:28Z)
  - the dependency-pin check after the proof checks
- Job `kernel-controls` 127728746028: success (positive and negative controls through the harness).
- Artifact `formal-verification-receipts`, id 13481426066. Zip sha256 `3cc06bc37af67614e5e8180a812ce17cc21f6c0cdf8d3e5c0ceb253ad55dfcb6`; the GitHub-reported digest equals the sha256 of the local download. It holds 122 files, and all 120 target receipts report `machine_verified`.

Receipt `source-evidence/hosted-42167929729/quotient-translation-descent.json`, sha256 `db4824f8c60e0513049e25d40c9013b7a6ccd1a73fa4a8e92c64a41a02d66d90`:

| Field | Value | Equals pinned or bound |
| --- | --- | --- |
| verification.status | machine_verified (build_passed true, axiom_audit_passed true, forbidden_constructs []) | — |
| verification.theorem_name / task.theorem_name | CryptoResearch.Quotient.translation_commutes_iff_two_torsion | the named declaration |
| task.claim | the yaml claim, verbatim | yes |
| provenance.source_commit | d5001059cd1b6c4dbfd7d7f894ac9c3b9c2b9806 | the review head |
| provenance.theorem_sha256 | 359a5ced…f401e | yes |
| provenance.task_spec_sha256 | 12fa5950…bd24b | yes |
| provenance.lean_toolchain_sha256 | ca5f1f60…330c | yes (bound) |
| provenance.lake_manifest_sha256 | b46170db…cec7 | yes (bound) |
| provenance.workspace_inputs["CryptoResearch/Quotient/TranslationDescent.lean"] | 359a5ced…f401e | yes. The module is in the gate's audited inputs |
| provenance.lean_version | Lean 4.35.0, commit eb6cafb7290e | same as the local build |
| infrastructure_failure | null | — |
| semantic_review.status | pending | (this round) |

Audit log (`source-evidence/hosted-42167929729/audit_log.txt`): "axiom audit: 1285 theorem(s), all
standard axioms only"; "target axiom audit passed: CryptoResearch.Quotient.translation_commutes_iff_two_torsion".
It prints the same type as the local elaboration, and `'…translation_commutes_iff_two_torsion' depends on axioms: [propext]`.
`dependency-pins-before.json` and `dependency-pins-after.json` both report `passed: true` with
`manifest_sha256` b46170db…cec7. They also report `binary_or_independent_kernel_recheck: false`,
which is the trust limit disclosed above.

The receipt's `build_log` and `audit_log` say "Reused fresh … from this invocation". The workspace
build and project audit ran once in this job, and the per-target verification reused them with all
inputs unchanged. As lean-review.md section 2 says, a receipt's JSON does not by itself
authenticate execution. The run, job, step timings and artifact digest above are the hosted
provenance, and the local build and `#print axioms` are independent corroboration on this machine.

### Archived receipts (corroboration only, not J2 evidence)

| Receipt | status | theorem_sha256 | task_spec_sha256 | toolchain sha256 | manifest sha256 |
| --- | --- | --- | --- | --- | --- |
| docs/reports/2026-10-31-hosted-formal-receipts/receipts/quotient-translation-descent.json | machine_verified | 359a5ced… (equal) | 12fa5950… (equal) | 5699bbbd… (old pin) | 3adfcdc0… (old pin) |
| docs/reports/2026-11-03-stark-affine-proof-review/reviews/TASK-20261103-bf45a0/hosted/quotient-translation-descent.json | machine_verified | equal | equal | ca5f1f60… (current) | b46170db… (current) |
| docs/reports/2026-11-03-odd-torsion-review/reviews/TASK-20261103-a1d703/raw/run-41494797344/quotient-translation-descent.json | machine_verified | equal | equal | ca5f1f60… (current) | b46170db… (current) |

All three name `CryptoResearch.Quotient.translation_commutes_iff_two_torsion` and carry
`semantic_review.status: pending`. The 2026-10-31 receipt binds the old toolchain and manifest, so
it is stale against the current pins. The two 2026-11-03 receipts bind the current pins. These were
read after the J1 and J2 verdicts were drafted.

## J3: claim boundary (breaks)

### Search scope

| Tree | How | Searched |
| --- | --- | --- |
| crypto-autoresearcher `origin/main` @ d5001059cd | `git grep -I -l -E '<terms>' origin/main` over all tracked text files (binary excluded), excluding only `coordination/formal-reviews/quotient-translation-descent-20261106/blind-*` (sibling paths, forbidden) | yes: 966 files (`source-evidence/j3-autoresearcher-hits-origin-main.txt.gz`) |
| crypto-autoresearcher `origin/claude/sheriff-a114e7-records` @ a9717726f2 | same grep, diffed against main | yes. Extra hits: this round's handoffs, DEC-20261106-2f9a94, DEC-20261106-0c4c43 and `pcc/ledger.jsonl` (records of this round, not classified) |
| isogeny-labs/crypto (default branch, commit 12a2b3d85f1796a9e793b7206763691e994012cd per the search result URLs) | `gh api search/code` with text-match fragments, one query per term | yes, but only through search fragments. `add_repo` was denied by the session permission policy and the contents API returned 403, so whole files were not read and line numbers are not available |
| isogeny-labs/cryptanalysis | `gh api search/code`, same terms | yes: 0 hits for every term |
| aburan28/crypto, aburan28/cryptanalysis | `gh api search/code` | yes: 0 hits (these may be renamed or redirected repositories) |
| **Not searched** | non-default branches of the sibling repositories; isogeny-labs/crypto-lean; any file GitHub code search does not index (large files, or a stale index); research/sheriff/SHF-20261106-a114e7/, which is not present on either fetched ref of crypto-autoresearcher | — |

The terms were `translation_commutes_iff_two_torsion`, `translation_descends_iff_two_torsion`,
`THM_QUOTIENT_DESCENT1`, `quotient-translation-descent`, `TranslationDescent`,
`2026-10-29-quotient-translation-descent-review` and, in the siblings, also `"Galbraith closure"`,
`"Lean-formalized" "2-torsion"`, `"larger group actions"` and `only 2-torsion translations descend`.

### Breaks (live records citing beyond the identity)

| # | Record (path:line) | Sentence (abridged) | Class | Owner for routing |
| --- | --- | --- | --- | --- |
| B1 | crypto-autoresearcher `formal/targets/README.md:276-277` (origin/main d5001059cd) | "[independent semantic review of 2026-10-29](…) finds it faithful to the target's claim (`faithful_scoped`, `validated_scoped` for that claim only)" | **cites the review as independent and validated_scoped** | formal-target lane: `formal/targets/` maintainers, through the Coordinator. Lines 273-275 and 278-279 correctly bound the claim to the identity, so only the review citation breaks. |
| B2 | isogeny-labs/crypto `papers/ecdlp-index-calculus-program/sections/companion_catalogue.tex` (blob 2bb7712687c168ea462fd37ec342cdde592f9616; the handoff cites line 317, which this review could not confirm because it had search fragments only) | row `research/THM_QUOTIENT_DESCENT1.md`: "Proved (Lean-formalized) that only 2-torsion translations descend through a degree-2 quotient of E, closing Galbraith's 'larger group actions?' question for x-type coordinates." | **cites descent and the Galbraith closure as formal** | isogeny-labs/crypto: maintainers of the paper `ecdlp-index-calculus-program` |
| B3 | isogeny-labs/crypto `research/ic_mega_pass_20261031/brief/build_map_ideas_corpus.py` (blob e0d4af032390d4954061fe8244826cd1bf1ca03c) and its output `research/ic_mega_pass_20261031/brief/MAP_ideas_corpus.json` (blob f3c894d19c35a50ebef7b59c87544f85c532973c) | "PROVED (elementary, Lean-formalised as translation_commutes_iff_two_torsion): … translation tau_T descends through the degree-2 quotient E/<iota_S> -> P^1 iff 2T=O. Corollary: … Closes Galbraith's 'larger group actions?' question …" | **cites descent, the Corollary and the Galbraith closure as formal**, because the Lean name is attached to the descent statement | isogeny-labs/crypto: owners of the `ic_mega_pass_20261031` brief |

On B3's liveness: the script lives in a dated pass directory. It does not quote an old state,
because the rename and scoping (2026-10-23) predate the pass (2026-10-31). The generator still emits
the sentence on re-run. It is counted as a break. The Coordinator may weigh it below B1 and B2.

The companion **data row** for B2, which the sheriff case calls LNX-1, was **not located**. Code
search for the catalogue wording in data files returned only the `.tex`. With file reads denied,
whether a separate data source generates that row is unresolved.

### Records checked and not breaking

| Record (path:line) | Class | Note |
| --- | --- | --- |
| research/THM_QUOTIENT_DESCENT1.md:1 (title "Only 2-torsion translations descend …") | prose Lemma title, no formal claim | the note's mathematical Lemma, not a formal citation |
| research/THM_QUOTIENT_DESCENT1.md:3-9 (Status) | identity only | "The Lemma's group-law identity is formalized as …; descent follows by the prose argument" |
| research/THM_QUOTIENT_DESCENT1.md:11-12 (Closes) | prose claim, not attributed to Lean | the Galbraith closure is stated as a consequence of the prose Lemma. This is outside this round's claim, but it does not say "formalized" |
| research/THM_QUOTIENT_DESCENT1.md:80-92, 131-143 | identity only | "It formalizes the Lemma's computation only" |
| formal/CryptoResearch/Quotient/TranslationDescent.lean:1-24, 31-38 | identity only | explicit "WHAT IS NOT PROVED" block and docstring |
| formal/targets/quotient-translation-descent.yaml:7, 11-23 | identity only | "The group-law identity only" |
| formal/targets/README.md:273-275, 278-279 | identity only | (B1 is lines 276-277 only) |
| ledger/decisions/DEC-20260920-11b44c.yaml:57, 66-67 | dated, immutable; old name | plan to mint the target; no formal-descent claim |
| ledger/decisions/DEC-20260921-683a85.yaml:181, 404 | dated; cites the note | "closes a slide question as a scoped theorem", written before the formalization; it does not say Lean |
| ledger/decisions/DEC-20260923-d86ff2.yaml:294; ledger/corrections/CORR-20260923-064d0d.yaml:112 | dated; cites the note | revisit condition met; no formal claim |
| ledger/decisions/DEC-20261017-edb475.yaml:2, 20, 48 | dated; about the note's status line | no formal-descent claim |
| ledger/goals/GOAL-GFPN-380702/goal.yaml:13, 1113, 3442 | live; cites the note | criterion C5 "closures filed" (OPEN); no formal claim |
| ledger/handoffs/TASK-20260923-aa277e.yaml:62-63, 115; ledger/proposals/IDEA-20260920-0490f5.yaml:81, 115 | dated; cite the note or stub | "cite it only as far as its proof is checked" |
| experiments/EXP-GFPN-05ff43/amendments/v1_to_v2_reanchor_and_arm_iii.yaml:498-512, 1280 | dated; cites the note | re-derives the group-law step and lists the Corollary and the `.lean` stub as NOT RELIED ON |
| research/gfp5_deployed_curves_20260920.md:69 | cites the note | "carries the proof"; no formal claim |
| problems/formal-workspace-build-exceeds-16gb.md:42; problems/sheriff-sibling-execution-and-lean-not-covered-20261028.md:11, 20 | infrastructure records | identity only |
| docs/reports/2026-10-23-translation-commutes-rename/report.md:1-24 and evidence/ | dated | identity only (the rename record) |
| docs/reports/2026-10-29-quotient-translation-descent-review/review.yaml:51-53, review.md | the reviewed record itself (frozen) | it self-labels `validated_scoped`. Listed, but not counted as a citation of itself. Its `claims_not_supported` excludes descent, the Corollary and Galbraith |
| research/sheriff/SHF-20261016-3caa6f/*, SHF-20261017-e4d7f6/*, SHF-20261028-0f3f64/*, SHF-20261024-46b7da/scripts/* | dated sheriff cases | listed, not breaks |
| Review attestations in other rounds (docs/reports/2026-10-31-lastfall-fidelity/lean/review_attestation.yaml:59, 140; 2026-11-03-bsgs-coverage…:74; 2026-11-03-stark-affine…:96; research/binstd_formal_review_round2…:215; …type_supplement…:66, 146; research/lean_review_evidence_20261018/…/review_attestation.yaml) | `sources_read` entries only | identity only (path citations) |
| About 900 machine receipts, build logs and inventories (`*/receipts/*.json`, `*.log`, `docs/reports/2026-10-31-formal-target-links/links.json`, `…/provenance.json` (old name), pointer-coverage inventories) | machine or pointer records | name the declaration, target or note with hashes; no semantic claim (identity only by construction). Listed in the gzipped hit list |
| isogeny-labs/crypto `research/ic_mega_pass_20261031/verdicts/MP-symmetry-2.refute.json`, `…/MP-additive_comb-1.collision.json`, `…/ideas/symmetry.json` | **unclassified** | search matched `THM_QUOTIENT_DESCENT1`, but the returned fragments do not include the citing sentence. With file reads denied, they cannot be classified. Left open for a session with read access |

## Order of reading

1. Inputs, the formal workspace, the verifier and the workflow, then the J1 and J2 machine checks.
2. J1 and J2 verdicts drafted at 2026-11-06T05:25:40Z. J2 was then pending the hosted run, and its
   local module-scope evidence was in hand.
3. After that, the prior-verdict records: docs/reports/2026-10-29-quotient-translation-descent-review/review.yaml
   (headline fields) and the archived receipts. Sheriff case files were read only as J3 grep hits,
   meaning the matched lines and the surrounding context quoted above.
4. Sibling files `blind-report.md` and `blind-attestation.yaml` were **not read**. They were absent
   from both refs, and the grep excluded `blind-*`. The J4 handoff `blind-handoff.yaml` was viewed
   (its first 30 lines) only to check session independence. That file is a commissioning record,
   not a sibling report.

## Evidence files

| File | sha256 |
| --- | --- |
| `source-evidence/J1Fidelity.lean` | `5cd9ae19fe2fd3caadfacac943ca47f9ed1bd6226081ea7318756b3e70d93c90` |
| `source-evidence/J1Fidelity.out` | `7f76e741bb0c8cf0347a9b5546e57f8aa445e8cadce04e25980cc0033022136b` |
| `source-evidence/hosted-42167929729/artifact-SHA256SUMS` | `3e19d5aed3e2db50aa795a6b82baf12d7f62a9f8092e839aea20d2d363beed08` |
| `source-evidence/hosted-42167929729/artifact-zip.sha256` | `fe548bb0e78627de445094d81ba888a5d1017201973ad1120c0f20f2bffb400f` |
| `source-evidence/hosted-42167929729/audit_log.txt` | `d75e23966fd5f785750ea5ca7abc9c7249907b213988b41ccec1c5db2c6669d4` |
| `source-evidence/hosted-42167929729/dependency-pins-after.json` | `7b0e77d5881e525ae397dad9df5ef31220117b5dc0d9d1c17cfd03eb6499c7c5` |
| `source-evidence/hosted-42167929729/dependency-pins-before.json` | `7b0e77d5881e525ae397dad9df5ef31220117b5dc0d9d1c17cfd03eb6499c7c5` |
| `source-evidence/hosted-42167929729/quotient-translation-descent.json` | `db4824f8c60e0513049e25d40c9013b7a6ccd1a73fa4a8e92c64a41a02d66d90` |
| `source-evidence/installed-package-revs.txt` | `ee96941369bccb46793fd1281cd7a099d3eb330b23a51d7ec786abffe493d958` |
| `source-evidence/j3-autoresearcher-hits-origin-main.txt.gz` | `ef33d947e2e9e0b619cdba42099599f7b6912726abfe046afe197e6a8435c25a` |
| `source-evidence/j3-autoresearcher-prose-hits.txt` | `d25c42e8128e6ce3572bb7a78164a19b1eb5592b991727a656465e5e3a28e524` |
| `source-evidence/local-cache-get.log` | `84bfa833983f633881d211eecbfc8ba909b3022885bc987be5bed5091d582421` |
| `source-evidence/local-lake-build-module.log` | `d7c21ba6c84a095d3edb345f08a56748468c5f3384e173977957c31cc17cc5b5` |
| `source-evidence/manifest-revs.txt` | `03a64ebf8db507946d4f505af84715b18eba56ce3c4975d264ba8f937d1771f8` |
| `source-evidence/search-THM_QUOTIENT_DESCENT1.json` | `955743c26501fa9c4c050b683a57081327b55ccc6e62779fab62a0935cb11546` |
| `source-evidence/search-translation_commutes_iff_two_torsion.json` | `b221294c47ab826f0bbbcc251ce4a3d7c9cf9980f6d7357a4495f59bb33cd761` |

## Limits

- J2 local is module scope. The gate on the full workspace is the hosted run.
- No independent kernel re-checker (lean4checker) was available.
- J3 for isogeny-labs/crypto rests on GitHub code-search fragments. Line numbers and whole-file
  context were not available, and the search index covers only the default branch.
- This review does not judge the prose descent argument, the Corollary or the Galbraith closure.
  J3 records only whether a record presents them as formalized.
