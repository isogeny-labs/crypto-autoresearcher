# Support-aware Boolean localization: formal construction

2026-11-05. Producer: `TASK-20261105-9cea2e`.
Archive owner: `TASK-20261105-c2c68c`.
Committed handoff/input pin: `766830c1e419dfb802e93a570abfc0b016c43aa8`.
Additional affine-refutation dependency, published by the root during this task:
`a655ddcab9849648462e7cbbab4dc01cf441263e`.

Source: `formal/CryptoResearch/FallDegree/BinaryLocalization.lean`, 606 lines.
Source SHA-256: `12ca51188d9042591a8835c92552eae3ea44670141476cce16e5fa0641125470`.
The scoped Lake build and exact-name axiom audit of all 40 theorem declarations
pass. No localized-row derivability, scalar fibre certificate, or interpolation
identity is assumed by the final binary theorem.

## Exact final theorem

Namespace: `CryptoResearch.FallDegree.BinaryLocalization`.

`lastFallDegree_binary_supported_affine_le` has:

- arbitrary base and auxiliary types `β`, `τ`, with decidable equality;
- a finite equation index type `ι`;
- a finite full base support `B : Finset β`;
- rows `p : ι → MvPolynomial (β ⊕ τ) (ZMod 2)`;
- individual finite base supports `A : ι → Finset β` and a bound `r : ℕ`;
- `p i ∈ localAffine (A i)`, `A i ⊆ B`, and `(A i).card ≤ r` for every row;
- actual Boolean inconsistency:
  no `a : β → Bool` and `t : τ → Bool` make every row evaluate to zero,
  using the literal values zero and one in `ZMod 2`.

Its conclusion is

```text
lastFallDegree (Set.range p ∪ fieldEqGens (β ⊕ τ) (ZMod 2) 2)
  ≤ max (B.card + 1) (r + 2).
```

The auxiliary type is not assumed finite. There is no characteristic transfer
from odd fields: the concrete theorem is over `ZMod 2`. The more general
`refutation_of_supported_affine_boolean_unsat` explicitly assumes
`∀ x : k, x = 0 ∨ x = 1`; the ordinary-field variant instead assumes no
field solution in any Boolean base fibre. The distinction is load-bearing.

`localAffine A` is the actual coefficient-field span of the polynomials

```text
(∏ i ∈ T, X (Sum.inl i)) * q,
T ⊆ A,
q = 1 or q = X (Sum.inr j) for one auxiliary variable j.
```

Thus the hypothesis describes precisely multilinear base coefficients using
only `A`, and affine dependence on the whole auxiliary tuple. It is not a
predicate naming localized derivability. Finite linear combinations and zero
rows are included. `basis_eq_prod` links the Finsupp monomial implementation
to the displayed products.

## Proven derivation and degree accounting

1. `localAffine_degree` proves `deg p ≤ A.card + 1` from membership in that
   supported affine span. `localAffine_normal` proves that such a row is
   already in Boolean normal form.
2. `localAffine_normal_factor` proves that after multiplying by either
   indicator factor `X_i` or `1-X_i` for `i ∈ A` and taking normal form, the
   row remains in the same supported affine span.
3. `staged_indicator_mem_V` starts with an actual ordinary derivation
   `p ∈ V (F ∪ FE₂) D`. For any subset of the support it derives its partial
   indicator product after normalization, and proves the resulting supported
   affine membership. Each next ordinary multiplication costs at most
   `(A.card+1)+1`, so the hypothesis is `A.card+2 ≤ D`. The normalization
   step uses the prior original-degree repair theorem.
4. `indicator_interpolation` proves the exact polynomial identity
   `NF(indicator A a * p) = indicator A a * specializeBase a p`.
   `specializeBase` is an algebra homomorphism assigning only base variables;
   auxiliary variables remain polynomial indeterminates. The identity follows
   from the proved indicator eigenrelation on each base variable and induction
   on the supported affine span, rather than an assumed evaluation bridge.
5. `full_localized_row_mem_V` derives
   `indicator B a * specializeBase a p ∈ V (F ∪ FE₂) D` for `A ⊆ B`,
   `A.card+2 ≤ D`, `B.card+1 ≤ D`. It multiplies by the complementary
   indicator only after supported localization. The degree sum is derived as
   `(A.card+1)+(B \ A).card = B.card+1`.
6. `specializeBase_mem_affine` proves that each fibre belongs to the actual
   affine polynomial span `{1} ∪ range X`. The separately proved
   `affine_span_refutation` supplies constant scalar refutations from no field
   solution. `specializeBase_eval` proves that these are the intended fibres.
7. `zmod_two_is_bit` proves every element of `ZMod 2` is zero or one, so actual
   Boolean inconsistency gives the field inconsistency needed in step 6.
8. `indicator_partition` proves the exact polynomial sum of full indicators
   over the powerset of `B` is one. The scalar combinations of the derived
   rows yield each full indicator, and their sum derives one at the stated cap.
9. The existing `lastFallSet_of_refutation` converts that unit derivation into
   the full last-fall bound: every ideal consequence `q` is available at
   `max D (deg q)`. The final theorem derives input eligibility from the
   supported affine degree bound; it does not assume raw high-degree inputs
   were eligible at a smaller cap.

The internal helper `refutation_of_supported_affine_certificates` accepts
scalar certificates for convenience, but the final F2 theorem obtains those
certificates from Boolean UNSAT. None of the final-theorem hypotheses assumes
the conclusion of steps 3--8.

Useful APIs for coefficient-table instantiation:

- `basis_mem_localAffine hT j` includes a supported basis monomial;
- `basis_eq_prod` identifies it with the visible base-variable product times
  one optional auxiliary variable;
- `supported_affine_sum_mem` includes arbitrary finite scalar combinations;
- `localAffine_normal_mul_base hp hi` proves
  `NF(X (Sum.inl i) * p) ∈ localAffine A` when `p ∈ localAffine A`, `i ∈ A`;
- `specializeBase_affine` additionally extracts a constant and an auxiliary
  coefficient vector when the auxiliary type is finite.

## Verification and preserved attempts

Commands ran from `/workspace/crypto-autoresearcher/formal`:

```text
/home/agent/.elan/bin/lake env lean ../analysis/rigorous-lfd-solving-20261105/binary-localization/BinaryLocalization.lean
/home/agent/.elan/bin/lake build +CryptoResearch.FallDegree.BinaryLocalization
/home/agent/.elan/bin/lake env lean --stdin
```

The first command was used for construction outside the formal source tree.
The staged formal source contains only complete proofs. The final scoped
build `build-12-formal.log` exited zero (`1769 jobs`). Its SHA-256 is
`74066f003d22226247dd454d64c42832b2c8e30e24dbbafc749955f691878124`.

`axiom-audit-01.log` contains the exact source hash, complete audit program,
output for all 40 declarations, checked main theorem types, and exit zero.
SHA-256: `af06e1a9e6b7be967dded3581d4238f4f1bf2c07533d62843e567327f02783b1`.
Every declaration depends only on Lean's standard logical axioms
`propext`, `Classical.choice`, and `Quot.sound`. No custom axiom or proof hole
is introduced. The forbidden-construct scan found zero matches.

`validation-01.log` records the versions, input/source hashes, all-theorem
coverage, axiom dependency union, and source scan. SHA-256:
`0268202fbfef45345c35b70b290f762fc80e58646647835b4ca7f8b67c64183d`.
Lean is the pinned `leanprover/lean4:v4.35.0`, commit
`eb6cafb7290e8bd5f2937522d8d804f58f02bafc`; Mathlib is pinned to
`cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`.
The new affine dependency source SHA-256 is
`a36a2d5b4977fb2a60a93804535daacfa27946d060d7f16de43da708f4dc3cc2`.

Failed compilations `build-01.log` through `build-07.log`, `build-09.log`,
and `build-10.log` are retained. They record typeclass/inference, finite-sum
simplification, and rewrite failures; they are not negative mathematical
results. `build-08.log` and `build-11.log` are successful intermediate checks.
The corresponding attempt snapshots are retained in this directory; the first
three are explicitly named `attempt-01-reconstructed.lean` through
`attempt-03-reconstructed.lean` because they were recovered from the recorded
edit history rather than copied before modification. Their original byte
hashes were not recorded before editing; they are labeled reconstructions,
not original immutable snapshots.
The working analysis candidate and the staged formal source have equal bytes.

During initial file creation a working-directory mistake briefly placed the
candidate under `formal/analysis/.../binary-localization`; it was immediately
moved to the intended analysis directory and the root was notified. No existing
`formal/CryptoResearch` source was changed. Staging the new actual module was
coordinated after the root released its verification freeze.

The root separately reported that its broader existing-workspace verification
hit exit 137 with an OOM kill in the pre-existing
`BooleanParityDegreeThreeRankCertificate` module. This scoped successful build
and audit do not assert that the broader workspace gate passed. The root owns
those independent receipts and their interpretation.

## Source review and remaining concrete instantiation

Sources read: the committed `BOUNDS.md` binary support-aware proof and exact
presentation, `BooleanNormalization.lean`, `ClosureCertificates.lean`,
`BinarySemaevShape.lean`, and the published `AffineFibreRefutation.lean`.
The pinned primary Mathlib sources for Finsupp, monomials, coordinate/total
degrees, finite products, and affine dual separation were inspected to check
the assumptions used above. The preceding normalization task retrieved and
read Caminata--Gorla Definition 1.5; this module continues to use that exact
ordinary filtration rather than a plain unaugmented Macaulay row space.
No literature-priority claim is made.

The general support-aware binary theorem requested in the handoff is now
proved at its stated scope. This module does not itself instantiate the raw
Semaev coefficient equations over an extension field, prove their projection
maps preserve the required supported affine form, or prove the raw input
repair at the final family cap. Those are the root's separate coefficient
descent/composition obligations. Consequently this module alone is not labeled
as a Lean theorem for the complete raw two-S3 `3*ell+1` presentation.
It also proves no solving-degree comparison, exact last-fall value, lower
bound, or proof-size bound. Independent semantic review remains separate.

No scientific trials, external model/API calls, delegation, official status
transitions, or archival commits were performed by this producer.
