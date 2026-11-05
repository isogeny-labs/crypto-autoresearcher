# Independent review of support-aware binary localization

2026-11-05. Reviewer `TASK-20261105-583517`; producer `TASK-20261105-9cea2e`;
archive owner `TASK-20261105-c2c68c`.
Frozen source/input revision: `397dcae257ee7a422816103603a8dcbdd52bee46`.
Requested policy: `review-breakthrough`, effort `max`, no fallback/degradation.
This is the independent native reviewer session as dispatched; no external
inference service or model probe was used.

## Scoped finding

The frozen source proves the generic binary support-localization core in the
ordinary polynomial filtration. The final theorem derives initial row eligibility,
staged normalized products, exact polynomial interpolation, the complementary
indicator, scalar fibre refutations, the finite indicator partition, and the full
last-fall bound. I found no assumed localized-row derivability, false
Boolean-to-field transfer, or circular fibre certificate in the final theorem.

The exact theorem is
`CryptoResearch.FallDegree.BinaryLocalization.lastFallDegree_binary_supported_affine_le`.
For arbitrary base and auxiliary types `β,τ` with decidable equality, finite row
index `ι`, `B : Finset β`, rows `p : ι → MvPolynomial (β ⊕ τ) (ZMod 2)`,
supports `A : ι → Finset β`, and `r : ℕ`, it assumes:

- `∀ i, p i ∈ localAffine (A i)`;
- `∀ i, A i ⊆ B` and `∀ i, (A i).card ≤ r`;
- no Boolean base/auxiliary assignment simultaneously satisfies every row.

It concludes

```text
lastFallDegree (Set.range p ∪ fieldEqGens (β ⊕ τ) (ZMod 2) 2)
  ≤ max (B.card + 1) (r + 2).
```

`localAffine` is the actual scalar span of squarefree base monomials times
either `1` or one auxiliary variable. It does not encode derivability or
inconsistency. The auxiliary type is not assumed finite.

This snapshot does **not** prove the complete raw two-S3 coefficient-system
instantiation of `3*ell+1`. Its source and producer status preserve that boundary.
The root's later coefficient-projection/raw-S3 proof was outside this frozen
review and was not read. No solving-degree comparison, exact last-fall value,
lower bound, or proof-size claim is certified here.

## Independence and blind rederivation

I read the committed `BOUNDS.md` binary support-aware lemma before opening the
new source, producer status, proof or evidence. The handoff and AGENTS rules
were available. Before opening the new source I sent this independent derivation
to the root:

1. Each normalized intermediate is jointly affine in the auxiliary tuple and
   supported on `A_i`, hence has degree at most `|A_i|+1`. Each next degree-one
   indicator multiplication needs `|A_i|+2`. Normalizing after every factor
   preserves that invariant, so the cost does not accumulate.
2. Supported localization gives `delta_(a,A_i)*p_i(a,t)` as a polynomial with
   auxiliary indeterminates. Multiplication by the complementary indicator
   costs at most `(|A_i|+1)+(s-|A_i|)=s+1`.
3. An adequate cap is `max(2,s+1,max_i(|A_i|+2))`; a uniform support bound `r`
   gives `max(s+1,r+2)`, since `r+2≥2`.
4. Scalar affine refutation requires no **field** solution. Over F2 every
   field assignment is Boolean. Characteristic two alone over a larger field
   would not justify that implication for arbitrary coefficient rows. The
   false nearby control is F3 with `p(t)=t+1`: Boolean-UNSAT, field root `2`,
   and no scalar multiple equal to the constant polynomial one.
5. The exact indicator partition derives one. Multiplying one by arbitrary
   `q` at `max(D,deg q)` yields the full last-fall bound, not merely one
   low-degree consequence.

Source blindness was deliberately lifted after this derivation. No sibling
reviewer report or new root coefficient-descent source was read.

## Load-bearing fidelity checks

Line numbers refer to the frozen `formal/CryptoResearch/FallDegree/` sources.

| Joint | Finding |
| --- | --- |
| Ordinary filtration | `LastFall.lean:48` defines the least linear space containing degree-eligible literal inputs and closed under products when the **sum** of factor degrees fits the cap. The new proof uses this ordinary iterated closure, not an unaugmented Macaulay row span. |
| Supported affine shape | `BinaryLocalization.lean:103` spans actual monomials with base subset `T⊆A` and at most one auxiliary variable. `basis_eq_prod` (201), `localAffine_degree` (110), and `localAffine_normal` (119) establish its concrete meaning, degree, and multilinearity. |
| Staged multiplication | `staged_indicator_mem_V` (165) starts from actual ordinary membership. At 180–186 it multiplies the previous normalized row by one factor, proves the degree sum using the supported affine degree bound, and supplies the adequate original-degree premise to normalization repair. At 187 it re-establishes the same support/affine invariant. Localized membership is a conclusion. |
| Repair | `BooleanNormalization.lean:146` proves `p-NF(p)∈V(FE₂,deg p)`. Its equivalence at 158 explicitly requires `deg p≤D`; the staged proof supplies it. Multiplication compatibility at 184 and 196 follows by capping exponent vectors. No unjustified quotient-to-ordinary transfer appears. |
| Polynomial interpolation | `specializeBase` (299) assigns constants only to base variables and retains auxiliary indeterminates. The eigenrelation (267), basis induction (314), and span induction (336) prove `NF(delta_A*p)=delta_A*specializeBase(a,p)` in the polynomial ring. It does not infer polynomial equality from equality only on finite-field auxiliary points. |
| Complementary cap | `full_localized_row_mem_V` (349) first derives the supported localization. At 358–363 it combines degree bounds and `(B∖A).card+A.card=B.card`; only then is ordinary multiplication used. The cap is `B.card+1`. The proven polynomial identity and disjoint products combine the indicators at 365–370. |
| Genuine affine fibres | `specializeBase_mem_affine` (481) proves membership in the actual span `{1}∪range X`; `specializeBase_eval` (460) proves the intended evaluation semantics. The final proof does not use the optional finite-auxiliary coefficient-vector extraction lemma. |
| Scalar refutation | The actual imported theorem is `CryptoResearch.FallDegree.affine_span_refutation` (`AffineFibreRefutation.lean:84`). If one is outside the row span, dual separation produces a functional annihilating it. Normalize the functional on one; its values on `X`s then give a common field solution, because functional evaluation agrees with polynomial evaluation on the affine span. This contradicts field UNSAT. Finite row-span coefficients give the scalar certificate. No finite variable type or unproved Gaussian axiom is assumed. |
| Boolean/field bridge | `refutation_of_supported_affine_boolean_unsat` (526) explicitly requires every field element to equal zero or one. At 542–547 it converts a field assignment to `decide(t j=1)`. `zmod_two_is_bit` (573) proves this for the final F2 theorem. Conversely a Boolean solution is a field solution via `bitValue`; hence the solution notions coincide over F2. There is no odd-field transfer. |
| Finite support partition | `indicator_partition` (403) sums over `B.powerset`, rather than assuming `β` finite. `Finset.prod_add` and `X+(1-X)=1` give one. Assignments are false outside the selected subset of `B`, where the rows have no support. This covers infinite `β`, infinite `τ`, and `B=∅`. |
| Certificate assembly | The helper at 432 accepts scalar certificates, but the final chain at 499 obtains them from actual field UNSAT using `affine_span_refutation`. Their linear combinations derive each indicator, then the finite partition derives one. |
| Final input eligibility | At 562–567 the final normalized theorem derives `hrows` from literal `Set.range p` membership and `deg(p i)≤|A_i|+1≤D`. It does not assume initial row derivability, localized rows, scalar certificates or one. |
| Full last-fall bound | `ClosureCertificates.lean:48` raises the cap to `max(D,deg q)` and multiplies the derived one by arbitrary `q`. Its witness makes the last-fall set nonempty; `Nat.sInf` is not being used vacuously. |

## Hypothesis-delta table

The comparison is with the producer's exact finite normalized F2 claim. The
stronger field helper is evaluated at its use in that proof, not exported as
an unrestricted Boolean theorem.

| Binder, instance, condition | Classification and discharge |
| --- | --- |
| Arbitrary universes of `β,τ,ι` | Implied representation choice; no variable-count restriction. |
| `[DecidableEq β]`, `[DecidableEq τ]` | Implied classically; bookkeeping, not a finiteness assumption. |
| `[Fintype ι]` | Already stated finite row-family scope. No arbitrary infinite equation-family theorem is claimed. Repeated/zero rows are allowed. |
| `ZMod 2` and field instance | Exactly F2; no extension or odd-field coefficient transfer. |
| `B,A,r,haff,hsupport,hsize` | Exactly the supported, multilinear, jointly affine assumptions and cardinality bounds. `basis_eq_prod` links their implementation to visible monomials. |
| Boolean UNSAT | Exactly the simultaneous solution premise, with literal zero/one evaluation. |
| Explicit `fieldEqGens ... 2` | Exactly all bit equations `X_i²-X_i` on both variable blocks. When the written lemma's `F` already contains them, `F∪FE₂=F`; no generator change is needed. |
| Helper ordinary `hrows` | Implied in the normalized final theorem by lines 562–567. For raw-input reuse it remains an obligation requiring actual derivation and adequate raw degrees. |
| Helper local/full cap inequalities | Implied by `D=max(B.card+1,r+2)` and `hsize`; `D≥2` follows from `r+2≥2`. |
| Helper `hbinary` | Implied by `zmod_two_is_bit`; its removal fails the F3 control. |
| Helper field inconsistency | Implied from F2 Boolean UNSAT by the explicit conversion and specialization evaluation. Over general fields it is a stronger premise, not implied by Boolean UNSAT. |
| Dual separation's projectivity | Implied over a field: the quotient is a vector space. No `Projective` or finite-dimensionality hypothesis remains in the elaborated `affine_span_refutation` type. |
| `[Fintype τ]` on optional extraction lemma | Absent from the final chain and actual affine-span refutation theorem. |

There are no unexplained extra mathematical assumptions for the exact finite
normalized F2 theorem. The helper
`refutation_of_supported_affine_boolean_unsat` provides the arbitrary `F,D`
ordinary-`V` version once original row membership is supplied.

The following concrete bridges are absent from this **frozen snapshot**:

1. Define the extension-field basis and actual F2 coefficient projections of
   raw equations, and establish the intended solution equivalence.
2. Prove the projected normalized rows belong to the supported affine spaces
   on the actual disjoint coordinate blocks, including the optional guard.
3. Derive these rows in ordinary `V` of the **raw** coefficient input, with
   explicit raw degree eligibility at most four. Equality of ideals alone
   does not permit a small-cap generator replacement.
4. Discharge `B.card=3*ell`, row supports at most `2*ell`, and
   `max(4,3*ell+1,2*ell+2)=3*ell+1` under `ell≥1`.
5. A solving-degree claim additionally requires the degree-compatible-order
   and iterated-Macaulay/Gröbner comparison convention and theorem.

`BinarySemaevShape.lean` supplies extension-field shape repair at cap four;
that is not by itself the coefficient/support instantiation above. No conclusion
is drawn about the root's unread later work.

```mermaid
flowchart LR
  A[Supported affine normalized rows] --> B[Eligible ordinary V rows]
  B --> C[Staged multiplication and normalization: support + 2]
  C --> D[Exact polynomial interpolation]
  D --> E[Complement indicator: base cardinality + 1]
  U[F2 Boolean UNSAT] --> G[Field fibre inconsistency]
  G --> H[Scalar affine refutations]
  E --> I[Full indicators in V]
  H --> I
  I --> J[Finite partition gives one]
  J --> K[Full last-fall bound]
```

## Frozen identities and verification boundary

All hashes below were recomputed from the frozen Git revision and compared
byte-for-byte with live files before checking. The six project modules in the
actual import closure all matched the pin.

| File | SHA-256 |
| --- | --- |
| `formal/CryptoResearch/FallDegree/BinaryLocalization.lean` | `12ca51188d9042591a8835c92552eae3ea44670141476cce16e5fa0641125470` |
| `formal/CryptoResearch/FallDegree/AffineFibreRefutation.lean` | `a36a2d5b4977fb2a60a93804535daacfa27946d060d7f16de43da708f4dc3cc2` |
| `formal/CryptoResearch/FallDegree/BooleanNormalization.lean` | `a7fde065840c9ad19c11932fb65f5747cc95eb75d799ae9de6ae059ca8d0ab8d` |
| `formal/CryptoResearch/FallDegree/ClosureCertificates.lean` | `1fc342e21de26a5254ea81c4e797174703ee060e6b13569585b9008ae9fd3aa1` |
| `formal/CryptoResearch/FallDegree/LastFall.lean` | `1e7f005567847e46e4dc23a5649d29453a9d8b87b1a7fed1889f633c3d8b841b` |
| `formal/CryptoResearch/FallDegree/FirstFallBounded.lean` | `e2ec161641d4b93a4bf0b584882046e455cab6e3a34694ed59a2f792b8c1ee2f` |
| `formal/CryptoResearch/FallDegree/BinarySemaevShape.lean` (context) | `49988ca63423b469677c5255e37f1deeff8efbacb471905c01757361ffbf8c31` |
| `formal/lean-toolchain` | `ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c` |
| `formal/lakefile.toml` | `104369773c0926608c11ccfdc5e10178041269371566ea11a46baf816f4a9b4d` |
| `formal/lake-manifest.json` | `b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7` |
| `analysis/rigorous-lfd-solving-20261105/BOUNDS.md` | `18339b9ad8cfdaf90001abcae06bc8c305c8910de29f4960a00a23b2111a4632` |
| `analysis/rigorous-lfd-solving-20261105/binary-localization/status.md` | `2553ebec75cb6c183d8027e420321375a9ef37ec6264fabfb978142f47aa9ac3` |

Lean pin and installed version: `leanprover/lean4:v4.35.0`, commit
`eb6cafb7290e8bd5f2937522d8d804f58f02bafc`. Lake reports
`5.0.0-src+eb6cafb (Lean version 4.35.0)`.
All ten installed dependency checkouts were clean and matched the manifest:

```text
CryptoLean       60952c696ded7f3da4f4517006d9af6482662487
mathlib          cfc55fc58714a59dc06e6e79edc6d1d95140d3c2
plausible        dfa4f38190d07c37e315953e08b90fe2d95b3c24
LeanSearchClient d6b4c7be5be75ec4917c873ac50c756dc1436372
importGraph      a41f0e9a4dea23188ea9cc1c41ac9f8bbafe0b93
proofwidgets     df72b022e558978a1c50264cfc4d7fec86fa8e04
aesop            4a174c490d8707121c4a9290800489f105d85e07
Qq               dce0ad79c486cb1fb504af04f953c3466b0c6db8
batteries        66e469188fe07963e5cf666c7d4433f45b8131c5
Cli              c24fe6078c630e89b489bffe59b3e20ac30d12c8
```

Producer evidence was rehashed rather than accepted instead of fresh checks:

```text
build-12-formal.log  74066f003d22226247dd454d64c42832b2c8e30e24dbbafc749955f691878124
axiom-audit-01.log   af06e1a9e6b7be967dded3581d4238f4f1bf2c07533d62843e567327f02783b1
validation-01.log    0268202fbfef45345c35b70b290f762fc80e58646647835b4ca7f8b67c64183d
```

Fresh commands ran from `/workspace/crypto-autoresearcher/formal`:

```text
/home/agent/.elan/bin/lake build +CryptoResearch.FallDegree.BinaryLocalization
  exit 0; Build completed successfully (1769 jobs).
  Lake replayed artifacts; warnings were module-system/linter notices.

/home/agent/.elan/bin/lake env lean --stdin
  stdin = exact git-show bytes of frozen BinaryLocalization.lean
  SHA-256 = 12ca51188d9042591a8835c92552eae3ea44670141476cce16e5fa0641125470
  exit 0; fresh source elaboration/kernel check, only linter notices.
```

A comment-stripped scan of the six-module project import closure found no
`sorry`, `admit`, `axiom`, `unsafe`, `native_decide` or `implemented_by` tokens.
`lean4checker` is not installed. These checks retain the ordinary Lean/Lake and
pinned dependency-binary trust boundary; they are not an independent binary or
kernel recheck.

The root reported the older full-workspace exit-137/cgroup-OOM failure in
`BooleanParityDegreeThreeRankCertificate`. I did not rerun that large old
certificate or the full gate. No full-workspace passing result is inferred.
The shared workspace was not a separate immutable dependency checkout; target
text came directly from Git and dependency source hashes were checked. Stable
pre/post hashes cannot exclude a transient concurrent edit. The dispatcher
supplied publication/readback of the frozen commit; I did not refetch or merge
into the shared producer tree.

## Retained reviewer check failures

These concern reviewer instrumentation/controls, not the frozen theorem. No
attempted control was written into `formal/`.

1. The initial exact-name audit's Lean invocation exited zero and printed all
   40 new theorem declarations plus five dependency declarations and the
   elaborated types. Its Python allowlist wrapper exited one: universe printing
   rendered standard axioms as `Classical.choice.{u}` and `Quot.sound.{u}`, while
   the parser expected unadorned names. Audit-program SHA-256:
   `59a081c1f416d5962bedad24c7513cdb5eb92e1f2f04e77070d324b08e408571`.
   Exact tail:

   ```text
   LEAN_EXIT 0
   FORBIDDEN_AXIOMS CryptoResearch.FallDegree.BinaryLocalization.baseExponent_inl
     {'Quot.sound.{u}', 'Classical.choice.{u}'}
   ```

   The corrected audit preserves universe-rich type checks and switches off
   universe printing before axiom output. The allowed axiom set is unchanged.
2. The first F3 control used `norm_num` without its ZMod-specific extension.
   Lean exited one with ground goals `2=0`, `3=0`, `w*2+w=1`, and `2=0 ∨ 2=1`.
   Its four incomplete control declarations reported `sorryAx` and were
   **not accepted**. The F2 positive constant-row control passed with only
   standard logical axioms. Corrected controls use kernel-checked `decide` for
   closed ZMod arithmetic and evaluate at the known root before simplifying.
   The corrected programs and results are retained below.

## Sources, provenance and procedural limits

Internal sources read: `BOUNDS.md`; committed dispatch/review handoff; producer
status after blind rederivation; entire frozen `BinaryLocalization.lean` and
`AffineFibreRefutation.lean`; relevant definitions/proofs in `LastFall.lean`,
`ClosureCertificates.lean`, `BooleanNormalization.lean`, `FirstFallBounded.lean`;
and frozen `BinarySemaevShape.lean` as context. Producer logs above received
hash checks rather than a substitute independent-verification attestation.

Primary formal-library sources retrieved locally at the pinned Mathlib commit
and read: `LinearAlgebra/Dual/Lemmas.lean` (separation/projectivity),
`LinearAlgebra/Finsupp/LinearCombination.lean` (finite row coefficients),
`Algebra/BigOperators/Ring/Finset.lean` (`prod_add`), and
`Algebra/BigOperators/Group/Finset/Basic.lean` (`prod_sdiff`). They support the
exact assumptions used. This review makes no literature-priority claim or
external solving-degree comparison; that comparison still needs its separate
primary-source convention audit.

Instructions read: AGENTS and applicable extended literature/review rules;
routing; `review-evidence` and its Lean-review reference; the `formal` skill
and workspace/target READMEs; cloud runtime skill. No source correction or
official scientific transition was made. The sole authored artifact is this
Markdown file, per committed write scope. It includes a proof diagram; no
separate PDF was written because this task authorizes only this file.
Publication and any presentation rendering remain with the archive owner.

```yaml
review_attestation:
  task_id: TASK-20261105-583517
  reviewer_task: TASK-20261105-583517
  archive_owner: TASK-20261105-c2c68c
  frozen_revision: 397dcae257ee7a422816103603a8dcbdd52bee46
  requested_policy: review-breakthrough
  requested_effort: max
  fallback_allowed: false
  degraded_allowed: false
  joints_owned:
    - supported_affine_shape_and_degree
    - staged_ordinary_V_derivation
    - interpolation_with_auxiliary_indeterminates
    - complementary_indicator_cap
    - actual_affine_fibre_refutation
    - finite_support_partition
    - F2_Boolean_and_field_solution_bridge
    - final_input_eligibility_and_last_fall_scope
  blind_statement_rederivation_before_new_source: true
  source_blindness_lifted_after_rederivation: true
  sibling_review_reports_read: false
  read_sibling_reports: false
  new_root_coefficient_descent_source_read: false
  scientific_experiments: 0
  external_inference_calls: 0
  delegated_agents: 0
  official_status_changed: false
  verdicts:
    supported_affine_shape_and_degree: holds
    staged_ordinary_V_derivation: holds
    interpolation_with_auxiliary_indeterminates: holds
    complementary_indicator_cap: holds
    actual_affine_fibre_refutation: holds
    finite_support_partition: holds
    F2_Boolean_and_field_solution_bridge: holds
    final_input_eligibility_and_last_fall_scope: holds
  sources_read:
    - AGENTS.md
    - docs/agent-contract-extended.md
    - docs/skill-routing.md
    - .claude/skills/route/SKILL.md
    - .claude/skills/review-evidence/SKILL.md
    - .claude/skills/review-evidence/references/lean-review.md
    - .claude/skills/formal/SKILL.md
    - formal/README.md
    - formal/targets/README.md
    - analysis/rigorous-lfd-solving-20261105/BOUNDS.md
    - analysis/rigorous-lfd-solving-20261105/binary-dispatch.json
    - analysis/rigorous-lfd-solving-20261105/binary-localization-review-handoff.json
    - analysis/rigorous-lfd-solving-20261105/binary-localization/status.md
    - formal/CryptoResearch/FallDegree/BinaryLocalization.lean
    - formal/CryptoResearch/FallDegree/AffineFibreRefutation.lean
    - formal/CryptoResearch/FallDegree/BooleanNormalization.lean
    - formal/CryptoResearch/FallDegree/ClosureCertificates.lean
    - formal/CryptoResearch/FallDegree/LastFall.lean
    - formal/CryptoResearch/FallDegree/FirstFallBounded.lean
    - formal/CryptoResearch/FallDegree/BinarySemaevShape.lean
    - formal/lean-toolchain
    - formal/lakefile.toml
    - formal/lake-manifest.json
    - formal/.lake/packages/mathlib/Mathlib/LinearAlgebra/Dual/Lemmas.lean
    - formal/.lake/packages/mathlib/Mathlib/LinearAlgebra/Finsupp/LinearCombination.lean
    - formal/.lake/packages/mathlib/Mathlib/Algebra/BigOperators/Ring/Finset.lean
    - formal/.lake/packages/mathlib/Mathlib/Algebra/BigOperators/Group/Finset/Basic.lean
    - tools/check_review_independence.py
    - "skill://plugin_connector_1p_c5b7d5df5d7081918f2c4be5a633ed5d/cloud-environment-runtime/SKILL.md"
```

## Fresh exact-name audit and boundary controls

The appended sections retain corrected fresh Lean programs, their output and
fail-closed axiom allowlist checks. Final per-claim verdicts follow them.


### Corrected exact-name axiom audit

Command: `/home/agent/.elan/bin/lake env lean --stdin`.
Audit program SHA-256: `01d2a562b49e1e19dd0d606674d5ee9be86871fafec5775fdc854fda99b54dae`.

```lean
import CryptoResearch.FallDegree.BinaryLocalization
set_option pp.universes true
#check @CryptoResearch.FallDegree.BinaryLocalization.lastFallDegree_binary_supported_affine_le
#check @CryptoResearch.FallDegree.BinaryLocalization.staged_indicator_mem_V
#check @CryptoResearch.FallDegree.BinaryLocalization.indicator_interpolation
#check @CryptoResearch.FallDegree.BinaryLocalization.full_localized_row_mem_V
#check @CryptoResearch.FallDegree.BinaryLocalization.refutation_of_supported_affine_boolean_unsat
#check @CryptoResearch.FallDegree.affine_span_refutation
set_option pp.universes false
#print axioms CryptoResearch.FallDegree.BinaryLocalization.baseExponent_inl
#print axioms CryptoResearch.FallDegree.BinaryLocalization.baseExponent_inr
#print axioms CryptoResearch.FallDegree.BinaryLocalization.booleanExponent_basis
#print axioms CryptoResearch.FallDegree.BinaryLocalization.booleanNF_basis
#print axioms CryptoResearch.FallDegree.BinaryLocalization.wt_baseExponent
#print axioms CryptoResearch.FallDegree.BinaryLocalization.basisMonomial_degree
#print axioms CryptoResearch.FallDegree.BinaryLocalization.capped_basis_add_base
#print axioms CryptoResearch.FallDegree.BinaryLocalization.booleanNF_basis_mul_base
#print axioms CryptoResearch.FallDegree.BinaryLocalization.basis_mem_localAffine
#print axioms CryptoResearch.FallDegree.BinaryLocalization.localAffine_degree
#print axioms CryptoResearch.FallDegree.BinaryLocalization.localAffine_normal
#print axioms CryptoResearch.FallDegree.BinaryLocalization.bitFactor_degree
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_degree
#print axioms CryptoResearch.FallDegree.BinaryLocalization.localAffine_normal_factor
#print axioms CryptoResearch.FallDegree.BinaryLocalization.staged_indicator_mem_V
#print axioms CryptoResearch.FallDegree.BinaryLocalization.basis_eq_prod
#print axioms CryptoResearch.FallDegree.BinaryLocalization.bitFactor_degreeOf
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_degreeOf_le
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_aux_degreeOf
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_normal
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_aux_normal
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_mul_base
#print axioms CryptoResearch.FallDegree.BinaryLocalization.specializeBase_base
#print axioms CryptoResearch.FallDegree.BinaryLocalization.specializeBase_aux
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_basis_interpolation
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_interpolation
#print axioms CryptoResearch.FallDegree.BinaryLocalization.full_localized_row_mem_V
#print axioms CryptoResearch.FallDegree.BinaryLocalization.specializeBase_basis
#print axioms CryptoResearch.FallDegree.BinaryLocalization.specializeBase_affine
#print axioms CryptoResearch.FallDegree.BinaryLocalization.indicator_partition
#print axioms CryptoResearch.FallDegree.BinaryLocalization.refutation_of_supported_affine_certificates
#print axioms CryptoResearch.FallDegree.BinaryLocalization.specializeBase_eval
#print axioms CryptoResearch.FallDegree.BinaryLocalization.supported_affine_sum_mem
#print axioms CryptoResearch.FallDegree.BinaryLocalization.specializeBase_mem_affine
#print axioms CryptoResearch.FallDegree.BinaryLocalization.refutation_of_supported_affine_no_field_solution
#print axioms CryptoResearch.FallDegree.BinaryLocalization.refutation_of_supported_affine_boolean_unsat
#print axioms CryptoResearch.FallDegree.BinaryLocalization.lastFallDegree_supported_affine_boolean_le
#print axioms CryptoResearch.FallDegree.BinaryLocalization.zmod_two_is_bit
#print axioms CryptoResearch.FallDegree.BinaryLocalization.lastFallDegree_binary_supported_affine_le
#print axioms CryptoResearch.FallDegree.BinaryLocalization.localAffine_normal_mul_base
#print axioms CryptoResearch.FallDegree.affine_inconsistency_certificate
#print axioms CryptoResearch.FallDegree.affine_polynomial_refutation
#print axioms CryptoResearch.FallDegree.affine_span_refutation
#print axioms CryptoResearch.FallDegree.mem_V_iff_booleanNF_mem_V
#print axioms CryptoResearch.FallDegree.lastFallSet_of_refutation
```

Combined stdout/stderr and wrapper result:

```text
@CryptoResearch.FallDegree.BinaryLocalization.lastFallDegree_binary_supported_affine_le.{u_1, u_2,
    u_3} : ∀ {β : Type u_1} {τ : Type u_2} [DecidableEq.{u_1 + 1} β] [DecidableEq.{u_2 + 1} τ] {ι : Type u_3}
  [Fintype.{u_3} ι] (B : Finset.{u_1} β) (p : ι → MvPolynomial.{max u_2 u_1, 0} (Sum.{u_1, u_2} β τ) (ZMod 2))
  (A : ι → Finset.{u_1} β) (r : ℕ),
  (∀ (i : ι),
      Membership.mem.{max u_1 u_2, max u_2 u_1}
        (CryptoResearch.FallDegree.BinaryLocalization.localAffine.{u_1, u_2, 0} (A i)) (p i)) →
    (∀ (i : ι), A i ⊆ B) →
      (∀ (i : ι), LE.le.{0} (Finset.card.{u_1} (A i)) r) →
        (¬∃ a t,
              ∀ (i : ι),
                Eq.{1}
                  ((MvPolynomial.eval.{0, max u_2 u_1}
                      (Sum.elim.{u_1, u_2, 1} (fun j => CryptoResearch.FallDegree.BinaryLocalization.bitValue.{0} (a j))
                        fun j => CryptoResearch.FallDegree.BinaryLocalization.bitValue.{0} (t j)))
                    (p i))
                  0) →
          LE.le.{0}
            (CryptoResearch.FallDegree.lastFallDegree.{max u_1 u_2, 0}
              (Union.union.{max u_1 u_2} (Set.range.{max u_1 u_2, u_3 + 1} p)
                (CryptoResearch.FallDegree.fieldEqGens.{max u_2 u_1, 0} (Sum.{u_1, u_2} β τ) (ZMod 2) 2)))
            (max.{0} (HAdd.hAdd.{0, 0, 0} (Finset.card.{u_1} B) 1) (HAdd.hAdd.{0, 0, 0} r 2))
@CryptoResearch.FallDegree.BinaryLocalization.staged_indicator_mem_V.{u_1, u_2,
    u_3} : ∀ {β : Type u_1} {τ : Type u_2} {k : Type u_3} [inst : Field.{u_3} k] [DecidableEq.{u_1 + 1} β]
  [DecidableEq.{u_2 + 1} τ] {F : Set.{max u_3 u_2 u_1} (MvPolynomial.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k)} {D : ℕ}
  {A B : Finset.{u_1} β} {p : MvPolynomial.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k},
  Membership.mem.{max (max u_1 u_2) u_3, max u_3 u_1 u_2}
      (CryptoResearch.FallDegree.V.{max u_1 u_2, u_3}
        (Union.union.{max u_3 u_1 u_2} F
          (CryptoResearch.FallDegree.fieldEqGens.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k 2))
        D)
      p →
    Membership.mem.{max (max u_1 u_2) u_3, max (max u_3 u_2) u_1}
        (CryptoResearch.FallDegree.BinaryLocalization.localAffine.{u_1, u_2, u_3} A) p →
      B ⊆ A →
        LE.le.{0} (HAdd.hAdd.{0, 0, 0} (Finset.card.{u_1} A) 2) D →
          ∀ (a : β → Bool),
            Membership.mem.{max u_3 u_1 u_2, max u_3 u_1 u_2}
                (CryptoResearch.FallDegree.V.{max u_1 u_2, u_3}
                  (Union.union.{max u_3 u_1 u_2} F
                    (CryptoResearch.FallDegree.fieldEqGens.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k 2))
                  D)
                (CryptoResearch.FallDegree.booleanNF.{max u_1 u_2, u_3}
                  (HMul.hMul.{max (max u_1 u_3) u_2, max (max u_1 u_2) u_3, max u_3 u_1 u_2}
                    (CryptoResearch.FallDegree.BinaryLocalization.indicator.{u_1, u_2, u_3} B a) p)) ∧
              Membership.mem.{max u_3 u_1 u_2, max (max u_3 u_2) u_1}
                (CryptoResearch.FallDegree.BinaryLocalization.localAffine.{u_1, u_2, u_3} A)
                (CryptoResearch.FallDegree.booleanNF.{max u_1 u_2, u_3}
                  (HMul.hMul.{max (max u_1 u_3) u_2, max (max u_1 u_2) u_3, max u_3 u_1 u_2}
                    (CryptoResearch.FallDegree.BinaryLocalization.indicator.{u_1, u_2, u_3} B a) p))
@CryptoResearch.FallDegree.BinaryLocalization.indicator_interpolation.{u_1, u_2,
    u_3} : ∀ {β : Type u_1} {τ : Type u_2} {k : Type u_3} [inst : Field.{u_3} k] [DecidableEq.{u_1 + 1} β]
  [DecidableEq.{u_2 + 1} τ] {A : Finset.{u_1} β} {p : MvPolynomial.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k},
  Membership.mem.{max (max u_1 u_2) u_3, max (max u_3 u_2) u_1}
      (CryptoResearch.FallDegree.BinaryLocalization.localAffine.{u_1, u_2, u_3} A) p →
    ∀ (a : β → Bool),
      Eq.{max (u_3 + 1) ((max u_1 u_2) + 1)}
        (CryptoResearch.FallDegree.booleanNF.{max u_1 u_2, u_3}
          (HMul.hMul.{max (max u_1 u_3) u_2, max (max u_1 u_2) u_3, max u_3 u_1 u_2}
            (CryptoResearch.FallDegree.BinaryLocalization.indicator.{u_1, u_2, u_3} A a) p))
        (HMul.hMul.{max (max u_1 u_3) u_2, max (max u_1 u_2) u_3, max u_3 u_1 u_2}
          (CryptoResearch.FallDegree.BinaryLocalization.indicator.{u_1, u_2, u_3} A a)
          ((CryptoResearch.FallDegree.BinaryLocalization.specializeBase.{u_1, u_2, u_3} a) p))
@CryptoResearch.FallDegree.BinaryLocalization.full_localized_row_mem_V.{u_1, u_2,
    u_3} : ∀ {β : Type u_1} {τ : Type u_2} {k : Type u_3} [inst : Field.{u_3} k] [DecidableEq.{u_1 + 1} β]
  [DecidableEq.{u_2 + 1} τ] {F : Set.{max u_3 u_2 u_1} (MvPolynomial.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k)} {D : ℕ}
  {A B : Finset.{u_1} β} {p : MvPolynomial.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k},
  Membership.mem.{max (max u_1 u_2) u_3, max u_3 u_1 u_2}
      (CryptoResearch.FallDegree.V.{max u_1 u_2, u_3}
        (Union.union.{max u_3 u_1 u_2} F
          (CryptoResearch.FallDegree.fieldEqGens.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k 2))
        D)
      p →
    Membership.mem.{max (max u_1 u_2) u_3, max (max u_3 u_2) u_1}
        (CryptoResearch.FallDegree.BinaryLocalization.localAffine.{u_1, u_2, u_3} A) p →
      A ⊆ B →
        LE.le.{0} (HAdd.hAdd.{0, 0, 0} (Finset.card.{u_1} A) 2) D →
          LE.le.{0} (HAdd.hAdd.{0, 0, 0} (Finset.card.{u_1} B) 1) D →
            ∀ (a : β → Bool),
              Membership.mem.{max (max u_1 u_2) u_3, max u_3 u_1 u_2}
                (CryptoResearch.FallDegree.V.{max u_1 u_2, u_3}
                  (Union.union.{max u_3 u_1 u_2} F
                    (CryptoResearch.FallDegree.fieldEqGens.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k 2))
                  D)
                (HMul.hMul.{max (max u_1 u_3) u_2, max (max u_1 u_2) u_3, max (max u_1 u_2) u_3}
                  (CryptoResearch.FallDegree.BinaryLocalization.indicator.{u_1, u_2, u_3} B a)
                  ((CryptoResearch.FallDegree.BinaryLocalization.specializeBase.{u_1, u_2, u_3} a) p))
@CryptoResearch.FallDegree.BinaryLocalization.refutation_of_supported_affine_boolean_unsat.{u_1, u_2, u_3,
    u_4} : ∀ {β : Type u_1} {τ : Type u_2} {k : Type u_3} [inst : Field.{u_3} k] [DecidableEq.{u_1 + 1} β]
  [DecidableEq.{u_2 + 1} τ] {ι : Type u_4} [Fintype.{u_4} ι]
  {F : Set.{max u_3 u_2 u_1} (MvPolynomial.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k)} {D : ℕ} (B : Finset.{u_1} β)
  (p : ι → MvPolynomial.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k) (A : ι → Finset.{u_1} β),
  (∀ (i : ι),
      Membership.mem.{max (max u_1 u_2) u_3, max u_3 u_1 u_2}
        (CryptoResearch.FallDegree.V.{max u_1 u_2, u_3}
          (Union.union.{max u_3 u_1 u_2} F
            (CryptoResearch.FallDegree.fieldEqGens.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k 2))
          D)
        (p i)) →
    (∀ (i : ι),
        Membership.mem.{max (max u_1 u_2) u_3, max (max u_3 u_2) u_1}
          (CryptoResearch.FallDegree.BinaryLocalization.localAffine.{u_1, u_2, u_3} (A i)) (p i)) →
      (∀ (i : ι), A i ⊆ B) →
        (∀ (i : ι), LE.le.{0} (HAdd.hAdd.{0, 0, 0} (Finset.card.{u_1} (A i)) 2) D) →
          LE.le.{0} (HAdd.hAdd.{0, 0, 0} (Finset.card.{u_1} B) 1) D →
            (∀ (x : k), Eq.{u_3 + 1} x 0 ∨ Eq.{u_3 + 1} x 1) →
              (¬∃ a t,
                    ∀ (i : ι),
                      Eq.{u_3 + 1}
                        ((MvPolynomial.eval.{u_3, max u_2 u_1}
                            (Sum.elim.{u_1, u_2, u_3 + 1}
                              (fun j => CryptoResearch.FallDegree.BinaryLocalization.bitValue.{u_3} (a j)) fun j =>
                              CryptoResearch.FallDegree.BinaryLocalization.bitValue.{u_3} (t j)))
                          (p i))
                        0) →
                Membership.mem.{max (max u_1 u_2) u_3, max u_3 u_1 u_2}
                  (CryptoResearch.FallDegree.V.{max u_1 u_2, u_3}
                    (Union.union.{max u_3 u_1 u_2} F
                      (CryptoResearch.FallDegree.fieldEqGens.{max u_2 u_1, u_3} (Sum.{u_1, u_2} β τ) k 2))
                    D)
                  1
@CryptoResearch.FallDegree.affine_span_refutation.{u_1, u_2,
    u_3} : ∀ {ι : Type u_1} {k : Type u_2} [inst : Field.{u_2} k] [inst_1 : Fintype.{u_1} ι] {σ : Type u_3}
  (p : ι → MvPolynomial.{u_3, u_2} σ k),
  (∀ (i : ι),
      Membership.mem.{max u_2 u_3, max u_2 u_3} (CryptoResearch.FallDegree.affinePolynomialSpace.{u_3, u_2} σ k)
        (p i)) →
    (¬∃ t, ∀ (i : ι), Eq.{u_2 + 1} ((MvPolynomial.eval.{u_2, u_3} t) (p i)) 0) →
      ∃ w, Eq.{max (u_2 + 1) (u_3 + 1)} (∑ i, HSMul.hSMul.{u_2, max u_2 u_3, max u_2 u_3} (w i) (p i)) 1
'CryptoResearch.FallDegree.BinaryLocalization.baseExponent_inl' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.baseExponent_inr' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.booleanExponent_basis' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.booleanNF_basis' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.wt_baseExponent' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.basisMonomial_degree' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.capped_basis_add_base' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.booleanNF_basis_mul_base' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.basis_mem_localAffine' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.localAffine_degree' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.localAffine_normal' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.bitFactor_degree' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_degree' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.localAffine_normal_factor' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.staged_indicator_mem_V' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.basis_eq_prod' depends on axioms: [propext, Classical.choice, Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.bitFactor_degreeOf' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_degreeOf_le' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_aux_degreeOf' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_normal' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_aux_normal' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_mul_base' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.specializeBase_base' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.specializeBase_aux' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_basis_interpolation' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_interpolation' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.full_localized_row_mem_V' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.specializeBase_basis' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.specializeBase_affine' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.indicator_partition' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.refutation_of_supported_affine_certificates' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.specializeBase_eval' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.supported_affine_sum_mem' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.specializeBase_mem_affine' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.refutation_of_supported_affine_no_field_solution' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.refutation_of_supported_affine_boolean_unsat' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.lastFallDegree_supported_affine_boolean_le' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.zmod_two_is_bit' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.lastFallDegree_binary_supported_affine_le' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.BinaryLocalization.localAffine_normal_mul_base' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'CryptoResearch.FallDegree.affine_inconsistency_certificate' depends on axioms: [propext, Classical.choice, Quot.sound]
'CryptoResearch.FallDegree.affine_polynomial_refutation' depends on axioms: [propext, Classical.choice, Quot.sound]
'CryptoResearch.FallDegree.affine_span_refutation' depends on axioms: [propext, Classical.choice, Quot.sound]
'CryptoResearch.FallDegree.mem_V_iff_booleanNF_mem_V' depends on axioms: [propext, Classical.choice, Quot.sound]
'CryptoResearch.FallDegree.lastFallSet_of_refutation' depends on axioms: [propext, Classical.choice, Quot.sound]
LEAN_EXIT 0
SCOPED_THEOREM_COUNT 40
TOTAL_AUDITED 45
ALL_FOUND 45
AXIOM_UNION ['Classical.choice', 'Quot.sound', 'propext']
ALLOWLIST_ERRORS []
```

### Corrected F3 false-transfer and F2 positive controls

Command: `/home/agent/.elan/bin/lake env lean --stdin`.
Control program SHA-256: `031900386bbfd42129b3c2f0b28701d8ba3b3d3d325a45550a0cb24569c9ebdc`.

```lean
import CryptoResearch.FallDegree.BinaryLocalization
open MvPolynomial CryptoResearch.FallDegree
open CryptoResearch.FallDegree.BinaryLocalization
namespace BinaryLocalizationReviewControls
noncomputable def oddRow : MvPolynomial Unit (ZMod 3) := X () + 1

theorem oddRow_boolean_unsat :
    ¬ ∃ t : Bool, eval (fun _ : Unit => if t then 1 else 0) oddRow = 0 := by
  rintro ⟨t, ht⟩
  cases t with
  | false => simpa [oddRow] using ht
  | true =>
    have hc : (1 : ZMod 3) + 1 ≠ 0 := by decide
    exact hc (by simpa [oddRow] using ht)

theorem oddRow_field_sat :
    ∃ t : Unit → ZMod 3, eval t oddRow = 0 := by
  exact ⟨fun _ => 2, by norm_num [oddRow]; decide⟩

theorem oddRow_no_scalar_certificate :
    ¬ ∃ w : ZMod 3, w • oddRow = 1 := by
  rintro ⟨w, hw⟩
  have hz : eval (fun _ : Unit => (2 : ZMod 3)) oddRow = 0 := by
    norm_num [oddRow]
    decide
  have he := congrArg (eval (fun _ : Unit => (2 : ZMod 3))) hw
  simpa [smul_eval, hz] using he

theorem zmod_three_not_all_bits :
    ¬ (∀ x : ZMod 3, x = 0 ∨ x = 1) := by
  intro h
  exact (by decide : ¬ ((2 : ZMod 3) = 0 ∨ (2 : ZMod 3) = 1)) (h 2)

theorem positive_constant_refutation_infinite_aux :
    lastFallDegree
      (Set.range (fun _ : Unit => (1 : MvPolynomial (Empty ⊕ ℕ) (ZMod 2))) ∪
       fieldEqGens (Empty ⊕ ℕ) (ZMod 2) 2) ≤ 2 := by
  have hmem : (1 : MvPolynomial (Empty ⊕ ℕ) (ZMod 2)) ∈
      localAffine (∅ : Finset Empty) := by
    have hb := basis_mem_localAffine (β := Empty) (τ := ℕ) (k := ZMod 2)
      (A := ∅) (T := ∅) (Finset.Subset.refl _) (none : Option ℕ)
    simpa [basis_eq_prod, auxPolynomial] using hb
  have hu : ¬ ∃ a : Empty → Bool, ∃ t : ℕ → Bool,
      ∀ _ : Unit, eval (Sum.elim (fun j => bitValue (k := ZMod 2) (a j))
        (fun j => bitValue (k := ZMod 2) (t j))) (1 : MvPolynomial (Empty ⊕ ℕ) (ZMod 2)) = 0 := by
    rintro ⟨a, t, h⟩
    have hc := h ()
    norm_num at hc
  simpa using lastFallDegree_binary_supported_affine_le
    (∅ : Finset Empty) (fun _ : Unit => (1 : MvPolynomial (Empty ⊕ ℕ) (ZMod 2)))
    (fun _ => ∅) 0 (fun _ => hmem) (by simp) (by simp) hu
end BinaryLocalizationReviewControls
#print axioms BinaryLocalizationReviewControls.oddRow_boolean_unsat
#print axioms BinaryLocalizationReviewControls.oddRow_field_sat
#print axioms BinaryLocalizationReviewControls.oddRow_no_scalar_certificate
#print axioms BinaryLocalizationReviewControls.zmod_three_not_all_bits
#print axioms BinaryLocalizationReviewControls.positive_constant_refutation_infinite_aux
```

Combined stdout/stderr and wrapper result:

```text
<stdin>:11:13: warning: `simp` already closes the goal

Hint: Use `simp` instead of `simpa`:
  [apply] simp [oddRow] at ht

Note: This linter can be disabled with `set_option linter.unnecessarySimpa false`
<stdin>:27:2: warning: `simp` already closes the goal

Hint: Use `simp` instead of `simpa`:
  [apply] simp [smul_eval, hz] at he

Note: This linter can be disabled with `set_option linter.unnecessarySimpa false`
'BinaryLocalizationReviewControls.oddRow_boolean_unsat' depends on axioms: [propext, Classical.choice, Quot.sound]
'BinaryLocalizationReviewControls.oddRow_field_sat' depends on axioms: [propext, Classical.choice, Quot.sound]
'BinaryLocalizationReviewControls.oddRow_no_scalar_certificate' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'BinaryLocalizationReviewControls.zmod_three_not_all_bits' depends on axioms: [propext, Classical.choice, Quot.sound]
'BinaryLocalizationReviewControls.positive_constant_refutation_infinite_aux' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
LEAN_EXIT 0
CONTROLS_AUDITED 5
ALLOWLIST_ERRORS []
```

### Independence-checker procedural diagnostic

The theorem/control checks above pass. The machine-readable independence
checker did not pass on this packet: the required output is Markdown, while
the CLI parses whole YAML files, and the prospective handoff has a prose
`review_plan` rather than canonical joint/owner/attack mappings. The declared
blind rederivation was performed as recorded above; this diagnostic does not
claim machine certification of that procedure. The frozen plan was not edited
retroactively.

```text
The CLI was first run as:
python3 tools/check_review_independence.py --plan analysis/rigorous-lfd-solving-20261105/binary-localization-review-handoff.json --reports analysis/rigorous-lfd-solving-20261105/binary-localization/review.md --no-addenda
Exit 2: no review_attestation blocks found in the given reports

The CLI loads whole files as YAML, not fenced Markdown. For an additional
read-only diagnostic, extract the fenced review_attestation mapping in memory
with yaml.safe_load and invoke the unchanged module's check function against
the exact committed review_plan mapping. No plan translation or edit is used.

FAIL: review_plan.coordinator_prior is empty; the prior is recorded before the round so that concurrence can be told apart from agreement with the Coordinator
FAIL: review_plan.joints is empty; a review with no named load-bearing step cannot show coverage
FAIL: analysis/rigorous-lfd-solving-20261105/binary-localization/review.md: TASK-20261105-583517 owns no declared joint or required blind task; unowned attestation
FAIL: TASK-20261105-583517 claims unassigned joint 'supported_affine_shape_and_degree'
FAIL: TASK-20261105-583517 claims unassigned joint 'staged_ordinary_V_derivation'
FAIL: TASK-20261105-583517 claims unassigned joint 'interpolation_with_auxiliary_indeterminates'
FAIL: TASK-20261105-583517 claims unassigned joint 'complementary_indicator_cap'
FAIL: TASK-20261105-583517 claims unassigned joint 'actual_affine_fibre_refutation'
FAIL: TASK-20261105-583517 claims unassigned joint 'finite_support_partition'
FAIL: TASK-20261105-583517 claims unassigned joint 'F2_Boolean_and_field_solution_bridge'
FAIL: TASK-20261105-583517 claims unassigned joint 'final_input_eligibility_and_last_fall_scope'
FAIL: proves_too_much.objects is empty; a claim-changing review runs the argument against objects where its conclusion is known false
PROBLEMS 12
```

### Post-check source binding

After all Lean/control checks, the reviewed source and pins were compared
again against the frozen commit. Result:

```text
MATCH 12ca51188d9042591a8835c92552eae3ea44670141476cce16e5fa0641125470 formal/CryptoResearch/FallDegree/BinaryLocalization.lean
MATCH a36a2d5b4977fb2a60a93804535daacfa27946d060d7f16de43da708f4dc3cc2 formal/CryptoResearch/FallDegree/AffineFibreRefutation.lean
MATCH a7fde065840c9ad19c11932fb65f5747cc95eb75d799ae9de6ae059ca8d0ab8d formal/CryptoResearch/FallDegree/BooleanNormalization.lean
MATCH 1fc342e21de26a5254ea81c4e797174703ee060e6b13569585b9008ae9fd3aa1 formal/CryptoResearch/FallDegree/ClosureCertificates.lean
MATCH 1e7f005567847e46e4dc23a5649d29453a9d8b87b1a7fed1889f633c3d8b841b formal/CryptoResearch/FallDegree/LastFall.lean
MATCH e2ec161641d4b93a4bf0b584882046e455cab6e3a34694ed59a2f792b8c1ee2f formal/CryptoResearch/FallDegree/FirstFallBounded.lean
MATCH 49988ca63423b469677c5255e37f1deeff8efbacb471905c01757361ffbf8c31 formal/CryptoResearch/FallDegree/BinarySemaevShape.lean
MATCH ca5f1f601d34c49079e38d7e7041eb0f2a9c227fbc1df0f404820069a052330c formal/lean-toolchain
MATCH 104369773c0926608c11ccfdc5e10178041269371566ea11a46baf816f4a9b4d formal/lakefile.toml
MATCH b46170db7f5631f573ff808cf1bc53655f3bd5385aeecc717c009a42dc01cec7 formal/lake-manifest.json
MATCH 18339b9ad8cfdaf90001abcae06bc8c305c8910de29f4960a00a23b2111a4632 analysis/rigorous-lfd-solving-20261105/BOUNDS.md
MATCH 2553ebec75cb6c183d8027e420321375a9ef37ec6264fabfb978142f47aa9ac3 analysis/rigorous-lfd-solving-20261105/binary-localization/status.md
CHANGED_REVIEWED_INPUTS []
```

## Final per-claim verdicts

| Claim or check | Machine status | Fidelity | Review outcome |
| --- | --- | --- | --- |
| Exact finite normalized F2 support-aware last-fall theorem | passed | faithful_scoped | validated_scoped for this technical theorem |
| Arbitrary-`F,D` ordinary support-localization helper with original rows already derived | passed | faithful_scoped | validated_scoped under its explicit row-membership premises |
| Complete raw two-S3 `3*ell+1` coefficient presentation | not_verified by this snapshot | partial: generic core only | outside this review; concrete bridges require their own proof and review |
| Solving-degree comparison, exact degree, lower bound, proof size | not_verified here | not_reviewed | outside this module's stated claim |
| Canonical machine-readable review-independence packet | failed / unsupported Markdown CLI input | not a mathematical theorem check | needs_revision before claiming that every procedural gate passed |

All eight owned mathematical joints hold. The F3 false-transfer control and the
F2 empty-base/infinite-auxiliary positive control passed; every accepted control
has only the standard logical axioms. The final named theorem's transitive axiom
set contains only `propext`, `Classical.choice`, and `Quot.sound`.

No correction to the frozen proof source is requested. The technical scope is
the generic supported-affine F2 core, not the full raw two-S3 instantiation.
The independence-checker serialization failure remains explicitly open as a
procedural limitation of this packet; the prospective plan was not rewritten
to create a retrospective pass. This review makes no official scientific
promotion or full-workspace success claim.

Archive the exact source pin and this review under `TASK-20261105-c2c68c`.
Any later coefficient-projection/raw-S3 instantiation needs a separately pinned
verification and independent review of its new concrete bridges.
