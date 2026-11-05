# Exact formal coverage and verification

2026-11-05. The raw binary LFD upper bound is now a complete instantiated
Lean theorem. The prime growth and solving-degree comparison remain written
mathematics with the exact review/citation scopes stated below.

## Final raw binary theorem

`formal/CryptoResearch/FallDegree/BinaryCoefficientDescent.lean` proves
`CryptoResearch.FallDegree.lastFallDegree_binary_two_S3_chain_le`.
For ell>=1, raw additive K->F2 coefficient projections of the actual two-S3
chain and optional inverse guard, with three base supports of size<=ell,
arbitrary auxiliary linear forms and all bit equations, Boolean UNSAT
implies ordinary `lastFallDegree<=3ell+1`. Here K is any characteristic-two
field. It assumes no localized rows, normalized support, supplied fibre
refutations or finite LFD. BINARY-FORMAL.md gives the exact selector and
coefficient convention and its finite-field basis specialization.

The source derives coefficient projection, normalization/evaluation
compatibility, support membership from actual linear source forms, cyclic
S3 equality, raw degree four and cardinality caps. The projection is only
additive; it is never treated as a unital ring homomorphism. Scoped build
and the automatic audit of 27 declarations (23 named theorems plus generated
definition equations) pass. The source is frozen in commit98a188b4 for its
independent raw-instantiation review at coefficient-descent/review.md.

## Generic support-aware core and affine refutation

BinaryLocalization.lean proves 40 named theorems, including the actual staged
support-aware derivation, interpolation with auxiliary indeterminates,
complementary indicators, exact partition, and the final
`lastFallDegree_binary_supported_affine_le`: normalized F2 inputs in the
supported-affine span, supported on A_i subset B with |A_i|<=r, satisfy
LFD<=max(|B|+1,r+2) on actual Boolean UNSAT. The main theorem has no finite
auxiliary-type premise. Raw input rows are not substituted silently.
Its build and all 40 exact-name axiom checks pass; source and scope are in
binary-localization/status.md. A separate fresh review owns this core.

AffineFibreRefutation.lean proves three named mathematical statements:
scalar certificates for inconsistent matrix equations, their polynomial
refutation, and the arbitrary-variable affine-span refutation used by the
core. The hypothesis is NO FIELD SOLUTION. Only the F2 wrapper converts
Boolean UNSAT into that hypothesis, using the proved zero/one classification.
Its scoped build and exact `#print axioms` pass. The odd-field false-transfer
control is part of the independent core review.

## Original-degree normalization and generic global bound

BooleanNormalization.lean proves 31 named statements over any field:
original-degree `p-NF(p) in V(FE_2,deg p)`, degree nonincrease, idempotence,
multiplication laws, ordinary bounded membership invariance under NF, and
the exact bounded bit-equation kernel. Its finite-variable theorem proves
EVERY ideal consequence q is derivable by max(N+1,deg q) for multilinear
inputs; raw degree<=B gives LFD<=max(N+1,B). It assumes neither UNSAT nor a
refutation nor a pre-existing finite-last-fall premise. Source construction,
failed attempts and all31 axiom checks are in normalization-status.md.
The scoped build and fresh-kernel replay passed.

BinarySemaevShape.lean proves four named mathematical theorems (eight
automatic audit entries), including raw S3 repair at cap4 and the reduced
cubic/quadratic degree bounds. Its build, audit and fresh-kernel replay
passed. These shape facts are composed into the final raw theorem above;
they are no longer merely stand-ins for the localization theorem.

The separately defined arbitrary-system strict quotient closure W_D is
still related to ordinary V in a written proof, not a generic Lean theorem.
The complete raw binary result above is proved directly in ordinary V and
does not require that unformalized general bridge.

## Pins and scope of successful checks

Lean4.35.0, compiler commit eb6cafb7290e8bd5f2937522d8d804f58f02bafc;
Mathlib cfc55fc58714a59dc06e6e79edc6d1d95140d3c2; CryptoLean
60952c696ded7f3da4f4517006d9af6482662487. No dependency pin changed.
All new audited declarations use only propext, Classical.choice, Quot.sound;
no holes, custom axioms or compiler-trusting native_decide declarations.
Exact source hashes, fresh-kernel outcomes and command exits are in
proof-map.json and validation/final-checks.json. Failed construction attempts
are retained, including the fixed simplifier cleanup in the raw module.

## Historical local full-workspace attempts

The standard verifier was launched after the original sources/specs were
committed/pushed. Its first receipt records an infrastructure timeout after
900s while compiling uncached Mathlib. The pinned cache was then downloaded
and unpacked successfully. The second full build failed in the EXISTING
`CryptoResearch.Semaev.BooleanParityDegreeThreeRankCertificate`: Lean
exited137 after398s, and `/sys/fs/cgroup/memory.events` recorded one OOM kill
under the16GiB limit. The verifier labels this `formalization_blocked` because
`lake build` failed; no new theorem error appeared. Both receipts and
workspace-resource-failure.json remain unchanged. The remaining two original
targets were not reached by that sequential standard run.

Thus there is no passing full-workspace standard-verifier receipt. Successful
scoped builds/audits/fresh checks have their own exact scope and are not
reported as full-workspace success. The resource obstruction is recorded in
problems/workspace-rank-resource.md. No gate is bypassed or reported green.

## Research and remaining proof scope

The prime growing-family theorem is a written proof; the prime review found
no gap and supplied independent derivations/controls. It is not a Lean
formalization of the full lower bound. Solving-degree bounds use the written
Caminata--Gorla Theorem3.1 application, not formal Groebner/Macaulay machinery.
A growing characteristic-two lower bound remains unproved. Independent
source reviews do not constitute signed PCC or official scientific promotion.

The completed independent core and raw-instantiation reviews both find their
assigned joints faithful and holding at scoped source-review standing.
Core output:75ed438e5ad45865c9a5ecba72e4ec8aac968cd90bc682d5d16c09f3318dfa5e;
raw output:2f9a65df9ade8877d0aef8363f5a3c3d66a24be27bb05aa8dc2a7b33fb496537.
The core review retains a failed machine-independence-checker parse attempt;
no procedural gate pass is inferred from the mathematical review outcomes.

## Additive update: later complete-workspace CI success

GitHub job127140800110 in run41996349062 passed the full workspace build,
all discharged-target verification, and before/after installed source-pin
checks for PR head69b20afa (the actual verification revision is synthetic
merge0cfa6988e8ec1fb1c1a98379d1c876fc3754ef55). The downloaded archive contains
120 machine_verified receipts. Five unchanged LFD receipts are retained under
docs/reports/2026-11-05-lfd-publication-readiness/ci-receipts/; they match current
exact theorem/specification and every local imported-source byte hash, plus
toolchain and package-manifest digests. The archive ZIP digest also matches
GitHub's artifact metadata. This is the later positive full-workspace result
for that proof snapshot. It does not rewrite the earlier failed local receipts
or assert that a later delivery revision has already passed CI.
