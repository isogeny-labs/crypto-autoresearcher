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

## Direct candidate verification

`check_candidate.py` consumes only the original normalized input, D, q and quotient columns C. It does not accept the encoder's T/R matrices as closure evidence. Run:

```sh
python3 check_candidate.py examples/software-control-candidate.json --output new-direct-check.json
```

The candidate schema is `semaev.closed-kernel-candidate/v1`; columns are q-bit integers in degree-then-numeric-mask monomial order. The checker validates the input, independently reconstructs S3 by evaluations using separate carryless arithmetic, and derives a basis of the entire degree-(D-1) kernel. Every variable product of each kernel relation is checked, alongside rank, generator annihilation and C(1)!=0. The shared inspector is used for input-promise validation, not for the checked coefficient rows; this is implementation separation, not a claim of wholly independent provenance.

Limits are N<=16 variables, at most 512 monomials, q<=64, 256 KiB wire input and two million explicitly scoped vector steps, with conservative preflight rejection. The checker is intended for bounded candidate development; existing large historical binary certificates retain their separate verifier. This CLI does not replay those certificates or establish an original dataset join.

Results distinguish `checked`, `rejected_input_or_predicate` and `not_checked_capacity`. Refusals exit 2 and retain no lower-bound conclusion. A capacity stop is not solver infeasibility. Successful results establish a closed containing kernel, nonmembership of 1 and a codimension lower bound, not equality with the exact closure. Exact LFD and LFD lower-bound fields remain null because no UNSAT/count/missing-consequence bridge is supplied.

Eight controls pass. They include a generator-annihilating map rejected for failing full kernel closure, an arbitrary quotient-coordinate basis, and CLI acceptance/refusal/non-overwrite checks. The initial test-file path failure and earlier seven-control source are retained. `direct-checker-final-validation/` preserves final acceptance, predicate rejection and capacity refusal artifacts. No scientific search or closure-engine execution occurred.

The SAT extension note supplies a solution-count-sensitive theorem: with M>0 solutions and b=max(2,floor(log2(M+1))), dF<=max(dG,b)+2 and dG<=max(dF,b+1). Its generic counterexample to additive invariance has a degree-n input generator; it does not settle the all-quadratic Semaev case. The growing-family lower-bound goal remains open.

## Structural capacity bridge

`attach_capacity_bound.py` reruns the direct checker on a candidate and reconstructs an upper bound U on the number of ordered Boolean solutions. It accepts no supplied verdict, rank or solution count. If the checked quotient rank q is strictly greater than U, the dimension argument establishes LFD>=D+1 for the reconstructed system. A contradiction with the independently written upper bound suppresses the lower-bound label and records inconsistent evidence. Exact LFD and production dataset admission remain unset.

```sh
python3 attach_capacity_bound.py examples/software-control-candidate.json --output new-capacity-check.json --profile-limit 2
```

Default bounds use trace and the square-root membership test. With Q=2^k and delta indicating sqrt(z) in V, the universal capacity is at most 3Q-3+delta. Nonconstant restricted trace improves this to 2Q-3+delta when the trace constant is zero, or 2Q-2 when it is one. A complete optional scan of at most 256 subspace elements can sharpen the bound by counting eligible distinct-product pairs. The scan never checks affine-fibre consistency, so capacities remain upper bounds rather than exact counts. If the scan is disabled or too small, its pair count stays unknown; square membership is still checked by linear-span rank.

Code and proof/audit hashes accompany CLI results. Capacity refusals, rejected inputs/predicates, internal consistency failures and inconclusive capacities remain separate from an established lower bound. Six fixed controls and actual CLI controls pass. The initial six controls did not exercise a positive lower-bound fixture. The later hand-derived F8 control below exercises that path; it remains separate from a production dataset campaign. The two-solution control correctly remains inconclusive because q equals U, rather than exceeding it.

The accompanying averaging proof establishes that for every odd n>=3 some dimension-(n+1)/2 subspace containing1 has exactly two solutions at z=a6=1. It does not identify an efficient basis formula or prove that an arbitrary such subspace has two solutions. The existence theorem must never be used as a count certificate for an unverified input V. The target has order four; no claim for generic prime-order targets follows. Growing LFD remains an additional obligation.

The separate reviewed `trace-active-unsat-family.md` establishes, for infinitely many odd n, an existential unsatisfiable subspace excluding1 with nonzero restricted trace. This removes the particular constant trace contradiction from the selected population. It does not exclude other degree-two refutations or establish growing degree. It has the same order-four target and nonconstructive basis-selection limitations.

## Positive fixed control and infinite degree-three lower bounds

`verify_degree_three_control.py degree-three-control/candidate.json --output new-exact-control.json` checks a hand-derived F8 instance with V=span(1,t), t³+t+1=0, z=a6=1. The literal rank-five quotient at D=2 passes the full kernel check and exceeds the reconstructed capacity four. The upper witness uses g=b+d+bd, with b*g=b and d*g=d at cap3, plus the input affine equation a+c+1. Triangular affine reduction then yields exact LFD3. Three focused controls pass, including a wrong system and a corrupted quotient. This is a deterministic proof/control check, not a random search or a new dataset campaign. Its source, witness, CLI result and review are retained in degree-three-control/.

The reviewed degree-two family theorem now proves LFD>=3 for every qualifying two-solution subspace containing1, and for infinitely many nonexceptional trace-active UNSAT subspaces. The exact nonexceptional degree-two quotient has dimension (N²-3N+6)/2. Growth of this dimension at fixed D=2 is not growth of LFD.

For a verified two-point input, LFD>D is equivalent to a known affine ideal generator missing from W_D, and to exact closure codimension exceeding2. A quantitative density estimate states the exceptional-set bound that would suffice for growing lower bounds. That bound on the low-degree-easy set has not been proved. The remaining next degree is D=3.


## SAT export and supplied-model verification

`certificate_sat.py encode request.json --output-dir new-bundle` reconstructs the bounded GF2 encoding and exports deterministic DIMACS, a variable mapping, and a hash manifest. `certificate_sat.py check-model request.json model.txt --profile-limit 4 --output new-result.json` checks a complete supplied SAT assignment against every reconstructed CNF clause and GF2 equation, then extracts C and runs the independent closed-kernel and capacity checks. No solver is launched. Bare UNSAT/UNKNOWN reports are unverified and produce no LFD bound.

The additional hard limits are 200,000 CNF variables, 500,000 clauses, a 32 MiB preflight serialization envelope, and an 8 MiB model. The earlier encoder and direct-checker limits still apply. A direct-checker capacity refusal does not admit a certificate. Exact LFD and production dataset admission remain unset by this interface.

Five software controls pass. `sat-control/receipt.json` records actual CLI export and verification of a hand-derived F8 model: 1,770 variables, 5,610 clauses, independently checked serialized clauses, and a checked lower bound of three. This reuses the fixed exact-degree-three control; it is not a new search result.

The reviewed degree-three notes reduce the two-point family to a unique-zero branch H with h <= LFD(F) <= h+1. They give an exact saturated W3 fixed-point obligation. An explicit non-Semaev family has the same W2 dimension profile yet exact LFD3 for every size, ruling out dimension-profile-only extrapolation to growing degree. A field-specific obstruction is still required.
