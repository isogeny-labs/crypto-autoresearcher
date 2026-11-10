# Admission contract for finite-selector total algorithmic cost bounds

Date: 2026-11-09. Source-only derivation for a possible metadata extension. No algorithm executed or performance measured.

A conservative total bound can be attached only to an explicitly named algorithm on the exactly joined Boolean polynomial system. It must remain distinct from the existing join's validation cost and from measured native instructions. The joined input already supplies actual N selector bits, field degree n, exact maps/equations, and the producer's full cyclic code semantics; those bindings are sufficient to instantiate a mathematical bound, not to claim an implementation ran.

## One explicit reference algorithm

Set M=2^N. Work in the complete Boolean monomial basis, at strict cap N+1. Insert the n reconstructed coordinate equations into a dense echelon basis. Each independent row has actual degree at most N and is therefore eligible for every variable multiplication. Queue each immutable inserted row exactly once, shift it by each of the N variables using Boolean mask union, and insert the shifted rows until the queue is exhausted. At most M independent rows can appear and at most N*M shifts are attempted. Input containment plus closure gives the entire Boolean ideal.

A dense insertion performs at most M row XORs, each on M bits. Thus a conservative arithmetic bound is

    O((n+N*M)*M²)

binary operations, plus mask/index construction and shifts. Explicit straightforward mask bookkeeping adds at most O(N²*M²) bit operations under binary-index arithmetic, which can be retained as a separate term rather than hidden in a unit-access assumption. Stored echelon rows require O(M²) bits; a replayable provenance vector per row adds another O(M²), while queued row references add polynomial indexing overhead. Reporting this as O((n+N*2^N)*4^N + N²*4^N) avoids suggesting a constant-degree polynomial bound as N grows. In the current adapter N<=12, the bound is finite but need not be small or tight.

The zero-variable case is handled separately: the coefficient equations are constants and can be inspected directly. The cap-one theorem remains valid but does not imply a positive amount of variable-multiplication work.

## Costs outside the closure core

Total input-to-output cost must also include the work needed to obtain the joined input. For schoolbook binary polynomial arithmetic, a field multiplication costs O(n²) bit operations. The finite truth-table reconstruction uses O(2^N*n²) field-evaluation work, plus O(N*2^N*n) for the vector-valued Mobius transform and O(n*2^N) equation inspection. Selector-map reconstruction has its own bounded tables and is dominated by these terms for nonzero N. Field irreducibility verification is polynomial in n and should be charged explicitly according to its implementation, rather than called free.

Parsing and hashing cost depends on actual input bytes, not merely n and N. Retained polynomial strings and maps can be larger than their algebraic dimension; use the enforced wire cap or actual byte count. Saving a derivation DAG, complete solution list, or every ideal row has separate output-size cost. Solution extraction may instead enumerate the 2^N code assignments; a full list requires at least its encoded output size. Distinct field-pair deduplication is a separate operation because codes can repeat.

## Required metadata and nonclaims

Any emitted record should identify:

- the exact input/equation/domain hashes and actual n,N;
- the reference algorithm and its cap N+1;
- whether the expression counts bit operations, dense row-XOR operations, or word operations, including indexing assumptions;
- preprocessing, closure, output, and storage terms, with unspecified representation-dependent costs retained explicitly;
- whether the bound is asymptotic or a numerically justified inequality with explicit constants;
- `algorithm_executed: false`, no measured instruction count, and no timing or throughput claim;
- the written proof/source identity and the unchanged separation from dataset/group/provenance admission.

An O-expression is not a numerical upper count unless its hidden constants are fixed by a specified implementation and argument. A cap theorem alone is also not a cost theorem: the finite closure algorithm and insertion count are the additional proof. This reference construction is valid for the exact normalized Boolean system, including nonlinear or repeated selectors, but does not transport a full-vector-space solver bound through an unverified coordinate map.
