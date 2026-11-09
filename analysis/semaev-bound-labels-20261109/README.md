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


## Explicit polynomial family and transport limits

`polynomial-subspace-candidate.md` constructs V=span(1,t,...,t^r) in any degree-n field with n>4r, z=a6=1. The unique highest-degree term rules out two nonconstant polynomial coordinates; constant substitution gives exactly (0,1),(1,0). This is an explicit infinite bounded-count family, but the odd-diagonal lower bounds do not apply. Symbolic coefficient derivations give LFD<=2 for r=1,2. A uniform all-r cap and a growing lower bound remain separate open alternatives.

The field-pencil note gives explicit trace-dual equations. Degree-c dual separators on all coordinate-one slices imply branch LFD<=c+3. Their absence does not prove a full-closure lower bound without a normalization theorem. The transport note proves degree-controlled substitution and explains why unchanged field towers and disjoint products cannot amplify degree. Each note has an independent written review.

`publication-validation.json` preserves the local global benchmark-gate failure caused by missing historical artifacts in this sparse checkout. No historical benchmark records were changed. Focused SAT controls passed; hosted checks are tracked separately on the PR.


## Frozen degree-two campaign and explicit infinite lower bound

`no-wrap-w2/protocol.json` was frozen and published with exact source before the sole bounded local attempt. All12 cells completed; all controls and independent DAG/full-closure replays passed. For r1..5 the full affine ideal is available at cap2. For r6..12 a known affine consequence is absent, giving LFD>=3. No timing, instruction-count, or production dataset claim follows. The campaign source, raw derivation DAGs, limits, process receipt, validated export, metadata deviation, rendered report and independent reviews are retained.

The r6 result is now explained by a symbolic polynomial-gcd proof: after five affine eliminations, the reduced11-dimensional quadratic span has no affine member and is already closed. It gives original rank71, affine dimension5, codimension35. Independent targeted replay reproduces those values. A selector argument brackets the first obstruction by3<=LFD<=4.

Restriction and the exact two-point ideal extend the lower bound to every r>=6 and every irreducible field polynomial of degree n>4r. This is an explicit infinite constant lower bound3, not a growing bound. Pulling back the seed's closed space yields an explicit certificate construction of constant codimension35. Next: saturated degree3 closure at r6, then a construction whose required cap grows.

Replay a saved certificate without rerunning the campaign: `python3 no-wrap-w2/replay.py no-wrap-w2/attempt-1/r6-certificate.json NEW-RESULT.json` (Python3.10+, assertions enabled). The output must match the retained result; output paths are exclusive. The original attempt must not be repeated under its consumed one-attempt allowance.


## Uniform boundedness theorem for the no-wrap family

The reviewed `no-wrap-uniform-cap-four.md` settles the no-wrap family's boundedness: LFD<=4 for every r, for z=a6=1 and V=span(1,t,...,t^r) with n>4r. Descending highest q-coordinates uses two selector levels and stays at cap4 without accumulating degree. Thus3<=LFD<=4 for every r>=6. This family cannot supply the requested unboundedness construction; modular-reduction families remain outside the theorem.

`no-wrap-r6-exact-degree-three.md` proves exact LFD3 at r6 by two irreducible-cubic trace functionals, before the degree-three computation. The single frozen cap3 attempt subsequently confirmed full affine-ideal derivability: rank468, eligible dimension104, affine dimension13, no missing forms. Controls, full DAG replay and independent targeted replay pass. Protocol/export/source/receipts/plots are in `no-wrap-w3/`; its one-attempt allowance is consumed.

`no-wrap-first-fall-two.md` gives an original-row telescoping witness proving FFD2 for every r>=1 under the explicitly defined literal nonzero-fall and operational new-consequence conventions. The claim is presentation-qualified and is not a syzygy-definition equivalence. The family consequently has a bounded first/last gap.

The uniform theorem also gives a conservative dense incremental closure algorithm bound O(N^12) binary operations and O(N^8) stored bits, N=2(r+1), in the stated indexed-bit model plus input conversion. This is not an instruction count, timing measurement, or a claim that generic closure is necessary to find the already explicit solutions.


## Executable no-wrap labels and exact retained-system join

The inspector now recognizes any independent basis of the full low-polynomial subspace by checking support below bit k, rank k, n>4(k-1), k>=2 and z=a6=1. It reports exact LFD2 for r1..5, exact3 for r6, and interval3..4 for larger recognized members. FFD2 is valid because it reconstructs literal polynomial-coordinate output rows; arbitrary output-row mixing is not covered. The theorem is applied to reconstructed inputs, not inferred from a finite point list.

`python3 join_retained_weil.py NORMALIZED.json WEIL-SYSTEM.json --output NEW.json` additionally checks the retained Rust m2 selector format: original ordered selector codes, both coordinate maps, modulus terms, target, dimensions, and every literal equation row. Only exact equality admits the polynomial bound labels. Unknown formats, finite lists masquerading as spans, affine offsets, repeated selectors and equation/map changes fail. Inputs are capped at1MiB and the producer's six-selector-bit limit; outputs cannot overwrite files.

This joins polynomial evidence, not whole dataset provenance: dataset_admission, point_domain_and_group_lifts_verified and producer_provenance_authenticated remain false. The control artifact is hand-specified in the actual producer format, not a claimed production record. Twenty-three distinct focused controls pass, including the existing capacity bridge; actual CLI acceptance and refusal receipts are in bound-join-controls/. The initial path error is retained in validation.json.

The modular quotient note isolates the missing structure beyond no-wrap: corrected dyadic relations have quadratic quotient terms, and the exact quotient-variable system has variable-count-independent factor-two refutation transport. It supplies no growing lower bound and no unrestricted SAT LFD equivalence.


## Modular degree-three feedback and exact selector scope

The reviewed modular-degree-three-field-falls.md writes the odd half-diagonal system as ell=0 and G=xy+B(x,y)+epsilon=0, with B=J(s+Tr(s))^2 and s=x+y+1. Projection keeps J on its trace-zero domain, including subspaces not containing1. The field identities xG and yG have quadratic Boolean coordinates and are available at cap3. Scalar-output cubic cancellation is governed by explicit trace-orthogonality conditions; trace elimination can add further cancellations. These are mandatory consequences, not a completed W3 invariant or a growing bound.

The separately reviewed finite-selector note proves the safe normalized Boolean bound LFD<=N+1 for exact nonlinear/repeated selector maps. It preserves code multiplicities and gives sufficient nonlinear transport hypotheses. It supplies no growing lower bound and does not replace finite factor bases with their span. No new dataset replay or scientific trial accompanied these proofs. See modular-feedback-report.md and modular-feedback.pdf for the frontier and evidence links.


The Frobenius follow-up proves that simultaneously twisting xG produces no new coordinate span. Nonzero relative twists cannot cancel the entire field-valued cubic on a half-diagonal subspace. Scalar trace cancellation has an exact trilinear criterion; for coprime shifts it forces a specific inverse-power permutation to preserve the nonzero elements of V. This is a necessary condition before trace elimination, not a full closure certificate. See modular-frobenius-multiplier-obstruction.md and its review.


## Exact trace-slice feedback and finite-selector CLI

The trace-slice note replaces x,y by independent x in V and t in W=V intersect kerTr. Its exact affine-multiplier conditions characterize the complete first quadratic feedback step. The epsilon multiplier space (VW)^perp has dimension at most one, with an exact rank-one trace-form characterization. Full iterative stability remains open. The inverse-Gold note supplies an F8 counterexample to blanket exclusion of inverse-power invariant subspaces, an exact subspace-polynomial divisibility criterion, and the inverse-cube necessary condition c2*c0^2=c1^3. None is a growing LFD lower bound.

`python3 join_finite_selector.py PARAMETERS.json WEIL-SYSTEM.json --output NEW.json` checks the exact cyclic sorted-code producer format, including repeated/nonlinear selectors and zero selector bits. Parameters use schema semaev.finite-selector-parameters/v1 with n,modulus,a6,z. It independently reconstructs maps and every original S3 row by field evaluation and Mobius inversion, then labels only LFD<=N+1. No solution count, exact LFD, FFD or whole-dataset admission is inferred. Wire limits are1MiB, n3..64 and selector bits0..6 per summand.

Seven new symbolic software controls and four existing retained-join controls pass. The accepted artifact in finite-selector-controls is a hand-constructed software fixture, not a production record. The saved CLI46 audit was inspected: its m2 cases are enumeration/PKM/double-large-prime; F4/F5 cases are m3. It therefore does not provide a production m2 Weil artifact for this join. No new scientific trial, solver run, native build or cloud job occurred.


## Saturated closure cost bounds and the next quadratic forms

The generic strict-closure note proves a total feedback algorithm bound. Let M count degree<=D monomials and L count degree<=D-1 monomials; immutable degree-first echelon insertion processes each eligible pivot once. For R inputs, at most R+NL insertion attempts and (R+NL)M whole-row XORs suffice, including every later degree fall. Dense coefficient storage is at most M² bits, with indexing/metadata/provenance and other costs separately stated. Full Boolean cap N+1 gives M=L=2^N.

The finite-selector CLI now emits these exact combinatorial maxima in closure_algorithm_cost_bound after the original equation join passes. They describe the named hypothetical closure algorithm, not an executed native backend. Native instructions and wall time remain null; training_cost_eligible is false. Eight selector controls and four existing join controls pass. A new CLI output in operation-bound-controls preserves the previous control output unchanged.

The trace-feedback note calculates the complete first-step polynomials, including linked quadratic blocks and affine tails. A mandatory ax multiplier produces a pure-x term detected by Tr(a*x³), so the rectangular-plus-affine class cannot be invariant. This does not assert W3 differs from W2. The next obligation is stability of a larger linked-block space under all further cubic cancellations. No growing LFD bound is claimed.

No native build or new scientific/cloud run occurred. The native source remains4be27eee881663c44318ed2d9debfad05d071538; its saved owned-authentic-validation authorization is approved:false. Existing native telemetry policy still marks training_cost_eligible:false. The theorem-derived algorithm envelope does not override either condition.


## Bounded exact Boolean LFD reference checker

`python3 inspect_retained_lfd.py PARAMETERS.json WEIL-SYSTEM.json --operation-limit 1000000 --output NEW.json` first verifies the exact finite-selector equation join, then enumerates the actual Boolean zero set and saturates every cap0..N+1. Evaluation ranks give the dimensions of the vanishing ideal in each cap. Exact LFD is one plus the last deficient cap, or zero when none is deficient. This preserves the normalized strict-closure convention and literal input presentation.

The core supports N<=12 and has explicit input/operation limits. CLI operation limits are1..10000000; the budget covers the reference analysis, separately from bounded loading/join/hashing/I/O. Exhaustion leaves exact_lfd null and retains completed cap summaries. Results are computed reference outputs, not standalone independently checked certificates; group-lift, authenticated producer, native-instruction and whole-dataset admission remain false. FFD is not inferred.

Twenty-four software controls pass across the core, CLI, finite-selector join and existing retained join. A hand-constructed F8 repeated-selector fixture produces six completed cap rows, four code solutions and reference LFD4, using36481 charged arithmetic units. These units are not retired instructions. The cutoff1 control produces no exact label. No production artifact or new scientific sample was executed. Source snapshots and outputs are in exact-lfd-controls/.

The parallel proof note shows every half-diagonal first-feedback space has at least r independent pure-x quadratic projections when n=2r+1. This rules out adding only a bounded number of such directions to the original rectangular ansatz. It is dimension growth at fixed degree3, not growth of LFD. A full stable linked-block space remains missing.


The single independent set-span software cross-check failed before validation: Python3.12 raised MemoryError importing pathlib under the fixed128MiB address-space limit. The fixture was not read and no closure computed. No retry or limit increase occurred. Source, logs and failure receipt are preserved in exact-lfd-controls/independent-attempt/. The reference LFD4 output therefore has source review but no successful independent-method computational confirmation.


## Independently checked all-cap certificates

The exact-LFD CLI now accepts --certificate-output NEW-CERTIFICATE.json. A complete run emits every cap's basis with a derivation for each row: eligible literal input or prior-row variable product, followed by XORs of prior rows. The certificate binds the exact input equations. Trace storage is budgeted and capped at200000 entries; exhaustion emits neither a partial certificate nor an exact label. The result binds the separately written certificate by SHA256.

`python3 verify_boolean_lfd_certificate.py CERTIFICATE.json --operation-limit 1000000 --output NEW-RESULT.json` uses no producer imports. It recomputes every derivation, validates degree-first independent pivots, checks all input containment and all eligible basis-variable products, and independently computes zero assignments and evaluation ranks. Every cap is required. Invalid proofs fail; budget exhaustion returns verified:false and exact_lfd:null. Wire input is capped at16MiB and N<=12. This verifies the supplied normalized mathematical system; its linkage to original curve/group data remains a separate exact join.

Thirty-five software controls pass, including altered rows, forward references, missing caps, unsaturated bases, invalid domains, budget exhaustion and an actual two-CLI certificate/hash roundtrip. The new hand-fixture certificate independently verifies LFD4 and four code solutions with68441 verifier accounting units. The earlier set-span cross-check failure remains unchanged; this is a new proof-carrying implementation, not a retry of that script or a production scientific sample.

The parallel proof eliminates epsilon exactly, obtaining an original trace-slice linear pencil in x for each t. A degree-c polynomial dual separator in t gives a direct original cap c+2 refutation. Explicit linear conditions characterize affine t-only separators and hence this particular cap-three refutation construction. Their solvability for an infinite family remains open, and their failure would not exclude arbitrary W3 refutations.
