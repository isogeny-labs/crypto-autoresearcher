# Authenticated Boolean compilation and canonical-range completion

Prospective fixed software contract. No implementation or suite execution is authorized until native admission, ownership and required checkpoint succeed. Full projected SAT/chart comparison remains downstream work.

## Required production path

`compile_block(public_descriptor)` calls the frozen authenticated.canonical_circuit(public_descriptor). It never derives that descriptor from submitted IR. Substitute each field variable z by its little-endian value sum(2^j bit_j), with b=ceil(log2 p). Inputs follow the frozen circuit projection order; auxiliary field variables follow their frozen order. All projected value bits occupy the first m positions. Compressed range states follow all value bits and are outside projection. Preserve equation ordering and names, combining coefficients modulo p and Boolean monomial masks by bitwise OR, including repeated-variable squares. Reject noncanonical or degree-above-two source equations rather than silently dropping terms.

The exported document binds source circuit content/hash, public descriptor, p, n, m, named value-bit blocks, recurrence-state positions, ordered polynomial list, ordered value-only bootstrap CNF, generator indices and projection decoding. It is JSON-serializable with canonical decimal monomial-mask keys and nonzero canonical residues. Canonical content authentication recomputes this document from the trusted descriptor and compares types and all content; JSON numeric equality alone is insufficient. Input assignments never specialize equations.

`encode_assignment` and `decode_assignment` preserve all frozen field-variable names, enforce complete canonical field values and disjoint bit positions, and uniquely reconstruct compressed states. Assignment decoding/evaluation is separate from document authentication. A root of the compiled system must decode to a source-circuit root and conversely; reference evaluation is independent of candidate acceptance.

This compiles the accepted rationality blocks, not the entire chart norm or interval collector. Do not label it a full relation generator. The later chart integration retains outer arity, all strata, finite-target signs and signed recovery checks.

## Canonical range subsystem

Expose a separately authenticated low-level descriptor for fixed tests: caller-supplied trusted arithmetic polynomials, p, n, projected_bits, and field blocks each with distinct little-endian value positions and specified compressed-state positions. It may interleave blocks or cross the projection boundary. Every state position is outside projection; no value/state collision, duplicate position or out-of-ring bit is allowed. Every value block has b bits and every state block has popcount(p-1)-1 positions. Strictly parse types and residues. The generic descriptor binds exact arithmetic content; its caller is responsible for that content's mathematical meaning. Only the production wrapper binds the accepted field circuit.

Append recurrence generators in block order, then forbidden generators in increasing local zero-bit order; record exact indices. Use s1 as the highest value-bit alias and introduce states only for subsequent threshold-one positions in decreasing local order. Recurrences are sr-s(r-1)*x[jr]; forbidden generators are s[r(j)]*x[j]. Build value-only comparator CNF: for each threshold-zero position j in increasing order, the negative x[j] literal followed by negatives of higher threshold-one positions q in increasing order. No SAT-only variables or recurrence/sorting/ordinate-half-range CNF.

## Completion and final checking

`complete_transcript` authenticates the system against its trusted public descriptor before traversing. Validate bounded integer prefixes before constructing a trie. Preserve raw status, every original model and every original learned record, including malformed records shadowed by another trie terminal; final validation must reject malformed content. The original learned list is an unchanged prefix of the augmented list. Retain a deep copy or immutable serialization of raw answer and actual bootstrap CNF as separate provenance; never rewrite them to resemble the verification input.

Use an iterative prefix trie with the adapter's LSB-first convention. Model terminals cover m-bit projections existentially. Maintain each block's minimum value under fixed prefix bits and a count of invalid blocks; state bits do not enter value minima. At a domain-empty nonterminal choose the first invalid block in declaration order. The highest differing bit against p-1 supplies a forbidden generator; emit multiplier +1 there and -1 on preceding recurrence generators, zeros elsewhere. Restrict against the exact prefix and verify the resulting identity with the unchanged adapter.

Missing branches with all value minima below p are unresolved coverage gaps, not roots. Do not close them using domain reasoning, fabricate a model or promote censored status. Call frozen adapter.verify_transcript with domain_cnf=[] and aux_bound=None on the complete augmented answer. Preserve the adapter's rejection on a false complete answer. Return the original and augmented records, the adapter result or explicit failure, gap information and separate accounting. Never remove a rejected original record to make verification pass.

## Cost and immutability boundaries

Count source authentication, bit substitution products/merges, range construction, typed comparison, trie visits, per-bit updates, emitted multiplier-vector length/nonzeros, polynomial restriction, certificate identity arithmetic, model evaluation, decoding and final coverage separately. Count serialization bytes and discarded/cancelled terms where applicable. Do not add heterogeneous counters into a speedup metric. No timing comparison, solver invocation, parameter sweep or field census in this stage.

Frozen source files and producer/reviewer attempts remain immutable. Use additive compiler.py and independent test modules. Retain every bounded attempt, exact command, source hashes, stdout/stderr and exit status. Four suite attempts maximum per producer and reviewer, 240 seconds and 2 GiB per attempt. Checkpoint before any suite. Root owns queue, claims, Git, snapshots and report rendering. A fresh reviewer sees source and this prospective contract but not producer tests/results/README or interpretations.

## Additive F1/F2 correction contract

This stage corrects the retained findings in TASK-20261031-3e6f7e. Do not edit predecessor source or evidence. Reject an empty string equation label at the exposed substitute_equations boundary; keep canonical polynomial expansion unchanged.

Provide encode_assignment_counted returning bits and nested authentication/reconstruction costs. Retain encode_assignment as an integer-only compatibility wrapper, explicitly unsuitable as a cost receipt. decode_assignment returns its assignment and distinct authentication, decoding and reconstruction phase receipts. Each public call authenticates exactly once from the trusted descriptor. A private reconstruction helper may avoid a second authentication but must not be exposed as an authenticated public entrypoint or rely on a cached unbound trust token.

Retain the exact authenticate return under the authentication phase, including construction and typed comparisons. Reconstruction counters declare threshold-bit visits, canonical-value checks, value-bit writes, initial-state reads, recurrence products and state-bit writes; decoding declares value-bit reads and state-bit checks. No mixed-unit totals. Zero-event units may be absent. Receipt mutation must not change the input document or later results.

The F5 constant descriptor (a=0,b=1,projection b0) with b0=2,z=3 gives bits26. Independently observe one canonical build for each counted public operation; derive phase counts from the literal loop/work, not just field-name existence. Check the F7 x6 interleaved-position witness bits52 and its wrong-state/noncanonical negatives. Preserve every original18 obligation group, all prescribed accepted field descriptors/witnesses and certificate controls.

Counters cover successful operations. Rejected-operation accounting is not claimed by this fixed software suite; a full solver comparison must separately retain and charge all failures and rejected witnesses. Fixing this interface alone does not provide workload costs.
