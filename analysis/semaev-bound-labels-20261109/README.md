# Fixed-m=2 bound annotation prototype and proof continuation

This source-only continuation does not prove unbounded LFD. Existing finite certificates remain finite-instance evidence. The requested infinite family with a growing lower bound is still an open obligation.

`inspect_bounds.py` reconstructs canonical normalized quadratic Boolean S3 coordinate equations from an exact field, vector basis, curve and target input. It applies the written upper-bound arguments cited by SHA-256 in each output. These are independently reviewed written arguments, not proof-kernel certification. This prototype is not integrated into the Rust dataset producer and does not promote a scientific ledger status.

The accepted JSON has exactly these keys:

```json
{"schema":"semaev.normalized-binary-m2-input/v1","n":4,"modulus":19,"basis":[1,6],"a2":8,"a6":1,"z":2,"require_rational_target":true}
```

Run `python3 inspect_bounds.py input.json --output new-result.json --product-limit 4`. The output must not exist. The product scan defaults to disabled; a cap too small returns unknown, never product exclusion. Supported field degree is 3 through 64, basis dimension 1 through n, and product scan cap at most 4096 elements. Field irreducibility, basis independence, canonical field words and (when required) rational target lifting are reconstructed. The equation binding includes the exact ordered canonical coordinate list and explicit Boolean field-equation convention. Raw quartic, point-list or auxiliary-variable presentations are not admitted.

Outputs distinguish written upper bounds, unknown exact LFD, unknown lower bound, and the qualified literal PQ first-fall criterion. They contain no measured solver work or native instruction estimate. The original certificate dossier and prior reports remain authoritative for their separate finite-instance results.

Validation: `python3 -m unittest -v test_inspect_bounds.py` checks exact fixed-fixture descent on all 16 assignments, rejection controls, unknown-state handling and input/equation binding. The separate `check_algebra_controls.py` checks formal factorization/substitution and the independently encoded F16 presentation example. Its first run failed on a Python 3.9 API incompatibility after 26 checks; the corrected run passed all 34. Both the failed source and failure receipt are preserved. No random trials, closure engine, native build or cloud job ran.

`inside-subfield-next-obligation.md` derives an alternate quadratic model and explains the degree-doubling obstacle. It is a proof candidate, not an admitted lower-bound theorem. `bound-label-contract-review.md` describes the fuller dataset integration contract; this prototype implements only the restricted standalone inspector. Plan/cell-manifest bindings, production export integration and formal proof validation remain outstanding.

## Dataset integration boundary and input regression

The inspector describes a **parameter-reconstructed full vector space**, not an authenticated existing dataset system. Outputs explicitly set `dataset_admission=false`, `original_dataset_equations_match=not_checked`, and `theorem_sources_runtime_verified=false`. The theorem-source digests pin the reviewed written references; this CLI does not reread and authenticate those files at runtime.

Inspection of the current Rust producer at commit `4be27eee881663c44318ed2d9debfad05d071538` found retained binary inputs using finite point-code lists and resultant constructions (for example `src/ml_dataset/binary_m3_retained_input.json`). Neither m=3 nor a finite point list is the full-space m=2 system here. Taking the span of codes would change the represented problem. A future production join must reconstruct the actual original equations, match the exact presentation and variable domain, and bind original input artifacts before admitting a bound. Existing Rust exact-degree-null guards remain unchanged.

The follow-up rejects negative moduli before arithmetic. Seven software tests now cover the prior five controls plus subprocess checks for negative-modulus termination, duplicate JSON keys and output non-overwrite. The earlier five-test validation receipt is preserved for its source hashes; the follow-up receipt binds the corrected source separately.

## Full-closure certificate search encoding

`encode_certificate.py` implements the finite C/T/R formulation in `certificate-feasibility-contract.md`. Run:

```sh
python3 encode_certificate.py examples/software-control-request.json --output new-encoding.json
```

The request wraps the exact normalized input with `degree_cap` and `quotient_dimension`. The output lists Boolean unknowns and canonical quadratic XOR equations for unit separation, generator annihilation, every eligible monomial multiplication and a right inverse. A monomial is a list of unknown IDs; `[]` denotes one. Each equation is the XOR of its monomials, set equal to zero. Boolean unknowns are intrinsic. Matrices are flattened in the documented row-major layout. No solver runs.

Hard defaults are 10,000 unknown bits, 10,000 equations and a conservative envelope of 100,000 nonzero terms. CLI caps can only lower those bounds. Combinatorial counts are checked before monomial allocation. The emitted formula is suitable for a later XOR/AND SAT translation; it is not itself DIMACS and no SAT integration or certificate search is claimed.

Seven encoder controls pass. `examples/` preserves an actual CLI emission with a hand-specified rank-two quotient for the two solutions of a tiny fixed system. All 24 encoded equations independently evaluate to zero. This is a software control, outside the scientific production panel. It is not a new unboundedness measurement. A learned model could propose partial multiplication actions or quotient columns; each proposed certificate would still need direct kernel-closure verification and an independent UNSAT, solution-count or missing-consequence bridge before contributing an LFD label. Failed search at one quotient dimension and timeouts do not imply an upper bound.

The source-only transfer note adds a restriction-indicator lower-bound lemma and describes the normal form as one quadratic definitional bit after trace elimination. Its additive degree comparison concerns UNSAT refutation degree, not arbitrary SAT last fall degree. The infinite-family construction remains open.
