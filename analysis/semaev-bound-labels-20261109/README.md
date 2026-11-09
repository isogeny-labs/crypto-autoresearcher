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
