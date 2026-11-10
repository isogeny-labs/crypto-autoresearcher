# Scalar-constant prefix extractor — source snapshot, 2026-11-07

**Status: source_only_unvalidated.** TASK-20261107-898896 implements standalone direct restriction, a binary-search reference and an original-term incidence sweep. No candidate function or module was executed or imported; no solver, tests, benchmark, field enumeration or cloud work ran. The runtime and provider/model identity remain unauthenticated under the published scoped inference amendment. Source inspection is not runtime equality evidence.

## Implemented construction

The public functions in extractor.py accept an externally prime modulus p, a variable count, a complete LSB-first assignment and canonical multilinear coefficient dictionaries. Validation rejects bool-as-int, out-of-range masks/assignments and zero or unreduced coefficients. Only built-in lists/tuples and dictionaries are accepted. All inputs are copied; caller mutation during a call is outside the contract. Invalid inputs and interruptions raise, rather than becoming no_scalar_witness.

The reference independently restricts original terms at each binary-search query, merges residual coefficients modulo p and checks the monotone nonzero-constant predicate. It handles P(0), P(n), n=0 and empty generator lists. A retained true endpoint includes its witness. Ascending generator order selects the lowest index at the least qualifying depth. The direct all-generator restriction entry point is also provided for later validation.

The sweep stores original term IDs with coefficients, residual masks and live flags, plus original variable-incidence buckets. Aggregate cancellation removes a dictionary entry, never an original term. Subtraction from a missing aggregate starts from zero. Nonconstant entry counts update on zero/nonzero transitions. The qualifying set is refreshed only for touched generators, strictly after the complete variable batch. Its lowest index is scanned once at the first successful stop. Final empty residual assertions precede a no-witness result.

The two implementations share input validation and output/counter formatting, not restriction state or their restriction algorithms. Their intended equality follows from the bound written invariant, but has not been executed or independently software-validated. Witness output contains depth, prefix, generator index, constant and counters. No certificate, inverse, clause or callback is produced.

## Static evidence and costs

Permitted evidence is AST parsing plus written source review only. Root's snapshot report-inputs records hashes and any independent static-reading disposition. Source has no imports, top-level calls, solver references or exception handler converting errors to validity. The reference's partial generator scan is sufficient because ascending order returns the first qualifying generator; a false full-depth predicate visits every generator. The sweep's final full-depth check asserts every residual empty.

Let s be generator count, T term count and I term-variable incidence count. Reference work is bounded by O((s+T)(1+log(n+1))) named structural events plus validation; sweep work and storage are O(n+s+T+I) entries under expected constant hash probes. Sweep initialization still builds all buckets even if P(0) will succeed. The reference snapshots all input polynomials; up to two residual dictionaries can coexist transiently during extraction because the old local remains referenced while the next dictionary is constructed. The asymptotic O(s+T) entry bound remains. restrict_reference separately materializes all returned residuals, O(s+T) output entries. Bit lengths, hash costs, integer allocation, mask extraction and modular arithmetic remain non-unit costs. These are analytical source bounds, not measured runtimes or byte ceilings.

interface.json defines counters precisely. Validation copying, original term visits, generator headers, incidence construction/visits, coefficient adds/subtractions, mask operators, whole-prefix predicates, touched-generator and qualifying-set work and tie scans are separate. Some counters describe overlapping events; their sum is not a primitive-work total. Inverse and multiplier counters remain zero. Bit_length extraction is associated with incidence creation; mask_operations excludes arithmetic subtraction/negation and hashing.

## Independent static reading and corrections

The independent reader reported a conditional static pass for witness semantics and identified two documentation defects. Both are corrected in this package without changing extractor.py: validation now requires identical witness/residual outcomes across input insertion-order permutations, while counters need only reproduce on identical ordered input; actual intermediate deletion-count differences are retained. The storage description now allows two transient residual dictionaries during reference extraction and separately accounts for all residual outputs of restrict_reference.

The review reasoned through validation, endpoints, original-term custody, absent-key subtraction, complete batches, lowest-index witnesses and no-witness validity. It requested no witness-semantic source change. Its source SHA-256 was adecd892151bc50723063bef1122960ebace951e527ff0a4a62e347c4b8a8631, unchanged by these corrections. The staged review is .resume/prime-transform-scalar-prefix-source-20261107/independent-static-review.md; root owns its exact custody binding and final disposition. This is static evidence only: software equality and observed resource behavior remain untested. Status remains source_only_unvalidated.

## Required integration boundary

No engine or checker is edited. Future integration must run on original self.polys, then independently recompute ALL restrictions through _residuals(depth,bits). Check that the selected result equals {0:constant}, construct its inverse and the full multiplier vector, and only then call unchanged _record_proof. Inspection of engine_counted.py confirms that _record_proof checks supplied residuals; it does not itself reconstruct them. Trusting producer sweep dictionaries there would miss this boundary.

Preserve _reject(bits) and valid-model checks. Charge extraction, independent restrictions, inverse, full multiplier allocation, certificate checking and witness reconstruction separately; do not silently relabel historical leaf_* counters. A shorter clause derived from an invalid complete model remains model-triggered, not partial-assignment pruning. Prefixes extending beyond projected coordinates retain all auxiliary literals. Complete projected sets require coverage and witness checks regardless of local clause correctness.

## Evidence lineage and next work

Internal sources checked before implementation: the published derivation-v2.md, refinement-v2.md, independent-critique.md and disposition.md under coordination/prime_scalar_prefix_source_20261107; source-contract.json/input-bindings.json; and the public engine residual/proof/fallback/model paths. These establish the exact fixed-order, scalar-inverse single-original-generator family and its projection limit. They do not claim global proof minimality or regularity reduction.

Retrieved primary context: Deharbe, Fontaine, Le Berre and Mazure, *Computing prime implicants*, FMCAD 2013, https://www.verit-solver.org/papers/fmcad2013.pdf. It studies reducing existing satisfying assignments using solver structures, including clause/cardinality cases. That establishes relevant prior sufficient-assignment minimization, not this finite-field sweep or novelty. The implementation reuses the published internal derivation; no novelty finding is sought.

validation-plan.md proposes finite standalone software checks, not an admitted launch. Separate admission must freeze its exact cases, limits and evidence before any execution. Both producer slots remain consumed and the blind independent software slot reserved. Preserve all 106 coordinate plus six coefficient cells, three encodings, all five leads, complete charts, identical projected-model sets and reconstruction/certificate costs.

The new diagram is a source architecture view, not measured data. No canonical frontier graph changes because this source-only task establishes no new measured or officially promoted claim. Root owns PDF rendering/all-page inspection, report-inputs hashes, source snapshot and Git publication.
