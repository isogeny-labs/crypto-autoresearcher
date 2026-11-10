# Independent source review: retained Weil-system bound join

Date: 2026-11-09. Source-only review of `join_retained_weil.py`, its fixed controls, and the actual Rust producer at `/home/ec2-user/crypto-ml-checkpoint-integration-20261107`, HEAD `4be27eee881663c44318ed2d9debfad05d071538`, `src/ml_dataset/solvers.rs` functions `polys_json` and `boolean_solve`. No tests, native build, solver, or production-artifact join executed by this reviewer.

**The mathematical join is sound and substantially stronger than recognizing the span of a finite point list.** The adapter requires the actual retained dimensions and field modulus, canonical target value, exactly all 2^k selector values in the declared basis order, the exact two Boolean coordinate maps, and every literal reconstructed output row in order. It therefore cannot replace a cyclically padded finite-domain selector by its vector-space span. Missing, duplicated, reordered, or nonlinear selector parametrizations are refused unless they exactly match the supplied full-vector-space representation.

The actual producer sorts and deduplicates affine x-coordinates, chooses at most six selector bits, pads via `codes[i % codes.len()]`, and saves the stated metadata, coordinate maps, and polynomial masks. The adapter's k<=6 scope matches that source. Matching the entire ordered selector list against the independent full-span enumeration detects finite-list padding and is deliberately stricter than set equality. Some legitimate artifacts expressed with a different input parametrization may be refused; that is safe and does not imply they are mathematically invalid.

Polynomial terms are parsed as unique canonical bounded hex masks with matching variable declarations. Monomial order within a row is normalized without changing the polynomial, but coordinate-row order is retained. Any higher-degree term or altered equation cannot match the inspector's canonical quadratic row. Equality of all n rows binds the polynomial system, including its constant a6 contribution, even though the retained format does not separately store a6. It does not bind a2 or group lifts; those are correctly excluded from the admitted claim.

The CLI applies a one-MiB wire cap before JSON parsing, rejects duplicate JSON keys, and creates output exclusively. Integer dimensions, modulus terms, coordinate ranges, decimal selector values, and maps are independently checked. Source and raw/canonical artifact hashes distinguish the original file from its parsed representation.

The output admits only mathematical bound labels on the exact retained polynomial artifact. It correctly leaves dataset_admission, point_domain_and_group_lifts_verified, and producer_provenance_authenticated false. A matching synthetic fixture demonstrates checker behavior, not that a real production run has been admitted. The nested inspector's own original-match field remains its parameter-only result; the enclosing join carries the additional successful equality checks.

## Strict-format correction requested

The initial tuple comparison treats Python integer 1 or float 1.0 as equal to True for lifting_required. Since the adapter promises the exact retained format, require `type(lifting_required) is bool` and `lifting_required is True` explicitly. This does not undermine an otherwise accepted polynomial equality, but rejecting malformed metadata makes the stated source contract accurate. The correction was requested before publication.

The supplied fixed controls cover a manually specified r=1 polynomial system, finite-list/order mutations, equation and coordinate-map mutations, modulus and target mutations, duplicate monomials, CLI hashes, duplicate JSON keys, and non-overwrite behavior. I read those controls; I did not rerun their reported passes or inspect an actual production instance that passed the join.

### Corrected-source readback

Confirmed the explicit Boolean type guard now precedes the encoding tuple check. The mutation control includes lifting_required=1 and expects rejection. This resolves the strict-format finding; no tests were rerun by this reviewer. The corrected source is accepted for the scoped mathematical artifact join, with whole-dataset and group/provenance admission still excluded.
