# Source audit of the prospective bound inspector

Date: 2026-11-09. Inspected `analysis/semaev-bound-labels-20261109/inspect_bounds.py` in `/home/ec2-user/crypto-lfd-unbounded-20261109`. **Source-only review: no inspector invocation, experiment, build, or dataset-label admission was performed.** The parent independently identified and is fixing the negative-modulus issue; that fix is not assumed verified by this static note.

## Verdict

The reconstructed normalized m=2 algebra, finite hypothesis calculations, rank-based qualified FFD2 criterion and proposed upper-bound formulas are sound on the validated parameter domain, after requiring a positive modulus. The tool is suitable as a **prospective parameter-system inspector**, not yet as an admission checker for existing production dataset cells. Two important scope/provenance gaps need explicit rejection or labeling before integration.

## 1. Production factor-base domain mismatch: must not admit by span

The accepted schema contains a field, an independent vector basis, curve constants and target. It reconstructs the system with X,Y ranging over **every element of the full F2-linear span** of that basis. It does not accept or verify the actual original dataset equation list, finite point-code domain, signed/orbit representatives, native descent map, public-instance artifact, factor-base artifact, or cell manifest.

Consequently a caller can obtain a mathematically correct bound for a *different system* by extracting the span of a finite point list and passing that basis. This is not a bug in the standalone reconstruction, but it is a critical integration trap. A finite factor base is not promoted to a full vector space merely because its coordinates span one. Extra restrictions or auxiliary equations also cannot inherit an all-instance LFD bound by simple monotonicity.

Recommended explicit output scope:

- `subject_scope: parameter_reconstructed_full_vector_space_system`;
- `dataset_admission: false`;
- `source_equation_identity: not_checked_against_dataset`;
- `source_factor_base_domain_identity: not_checked_against_dataset`.

A future adapter must authenticate the source artifacts, reconstruct their exact allowed-variable domain and ordered normalized input list, compare them with `equation_binding`, and admit only exact agreement or a separately checked degree-preserving equivalence. Until then, preserve all production `exact_*fall_degree` fields as null. Do not attach `written_lfd_upper_bound` to a dataset row using only matching n,k,z or a shared span.

## 2. Theorem hashes are declared, not runtime-verified

`THEOREM_SOURCES` is a hardcoded mapping returned in the result. The inspector does not read those paths or verify that their current bytes match the declared hashes. Likewise, the result's proof-status text is a statement about the intended pinned arguments, not a fresh independent review or formal-kernel check.

This is acceptable as an explicitly **declared source pin** in a candidate inspection record. It must not be described downstream as `theorem_sources_verified=true`. Either verify the pinned files/readback artifacts in an admission layer, or distinguish `declared_theorem_source_sha256` from a verified source receipt. Pin the inspector source hash and exact theorem/review bundle in the eventual application receipt. A hash copied from a candidate is not itself proof of custody or applicability.

## 3. Malformed-input boundary

Confirmed from source:

- n, product limit, modulus and field elements use exact `type(...) is int` checks, rejecting booleans as integers where relevant.
- n is bounded3..64; basis length is bounded1..n; all field elements are canonical nonnegative n-bit integers; zero targets and singular a6=0 cases are rejected.
- The basis rank is computed rather than trusted; rational-target lift is computed by the correct trace condition rather than accepted from the boolean request flag.
- Unknown schema keys are refused. CLI parsing rejects duplicate JSON keys. Input wire size is bounded64KiB and the output is created exclusively, avoiding silent replacement.
- Optional product enumeration is limited to at most4096 span elements; capacity exhaustion is recorded as `not_checked_capacity`, not as nonmembership.

The identified defect is substantive: negative odd `modulus` values can satisfy `bit_length()==n+1`, and signed bit operations invalidate the polynomial arithmetic and may prevent Euclidean reduction from terminating. Require `modulus>0` before the degree/oddness test. The parent is correcting this. After that change, the Rabin irreducibility structure—prime divisors of n, gcd tests at n/q, and final Frobenius equality—is appropriate for F2 polynomials.

`inspect()` used directly accepts an already parsed dictionary, so duplicate-key evidence has already been discarded by a conventional external JSON parser. Admission should use the strict CLI parser or an equivalent shared parser; a dict-level API cannot independently guarantee absence of duplicate wire keys.

## 4. Mathematical applicability checked from source

### Canonical equations

For each basis pair v_i,v_j, the coefficient of a_i b_j is `(v_i v_j)^2+z v_i v_j`; the linear coefficients of both a_i and b_i are z²v_i²; the constant is a6. This is exactly the multilinear Boolean expansion of S3. The output coordinate basis `1,t,...,t^(n−1)` and ordered equation list are explicit. The generated equations include empty rows; the FFD calculation separately and explicitly omits literal zero rows.

### Trace and rational target

The trace constant Tr(a6/z²), traces of all basis vectors, and lift condition Tr(z+a2+a6/z²)=0 are correct. A nonzero trace vector supports the k+2 bound; zero vector with trace constant1 supports a degree≤2 refutation. A zero residual does not remove a selector.

### Subfield membership

When n=2k, rankk together with v_i^(2^k)=v_i for every basis vector proves that the span is the unique k-dimensional subfield H. The outside-target test z^(2^k)≠z is exact, giving the reviewed all-instance bound3. No subfield hypothesis is accepted from a user boolean.

### Optional product profile

The enumeration generates the entire span. For each nonzero u, checking z/u∈V counts the ordered product representations. The possible square representation is unique and detected by sqrt(z)∈V. Therefore `(len(tz)−delta)/2` is the exact number of unordered distinct pairs, and absence of such pairs supports the r≤1 refinement. The stated total fibre capacity `2^(k+1)−1+len(tz)` is consistent with the exact kernel classification; it is a capacity, not an actual solution count.

The implementation does not currently add every available theorem refinement, e.g. the full-subfield inside-target H-trace bound k+2. Omitting a stronger valid upper bound is conservative, not an unsoundness. It should not be reported as a failed hypothesis or impossibility.

### Qualified FFD2

If every nonzero original coordinate row is genuinely quadratic, `rank(full rows)>rank(quadratic parts)` is equivalent to the existence of a nonzero affine/constant combination of those quadratic rows. This correctly proves literal PQ FFD2 under the stated zero-row-omission convention. The condition does not claim syzygy-FFD equivalence for mixed-degree lists or new-class behavior after arbitrary row elimination.

The output currently records ranks rather than an explicit coefficient vector exhibiting the nonzero fall. Those ranks are reproducible from the embedded equations and pinned source, but a durable independently checkable FFD certificate should also retain a null-top combination and its nonzero residual (or a separate rank certificate). The word `witness` in the status must not be interpreted as an emitted proof vector when none is present.

## 5. Required integration disposition

Keep the current tool outside production degree-label admission. Its `solver_executed:false`, null exact LFD, null LFD lower bound and nonformal proof-status scope are appropriate. Add the parameter-reconstruction/dataset-nonadmission distinction, resolve the signed-modulus defect, and retain the exact source and theorem bundle. Then a separately scoped implementation can add authenticated original-domain joins, byte/semantic hashes, explicit witness records, typed theorem admission and negative controls from `bound-label-contract-review.md`.

No observation in this source audit establishes that the inspector runs correctly, that any dataset row has an admitted theorem bound, or that the requested unbounded binary lower bound has been proved.
