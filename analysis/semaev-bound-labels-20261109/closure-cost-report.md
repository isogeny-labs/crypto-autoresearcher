# Complete feedback costs and evolving quadratic structure

2026-11-09. Proof and software continuation.


## Saturated closure cost bounds and the next quadratic forms

The generic strict-closure note proves a total feedback algorithm bound. Let M count degree<=D monomials and L count degree<=D-1 monomials; immutable degree-first echelon insertion processes each eligible pivot once. For R inputs, at most R+NL insertion attempts and (R+NL)M whole-row XORs suffice, including every later degree fall. Dense coefficient storage is at most M² bits, with indexing/metadata/provenance and other costs separately stated. Full Boolean cap N+1 gives M=L=2^N.

The finite-selector CLI now emits these exact combinatorial maxima in closure_algorithm_cost_bound after the original equation join passes. They describe the named hypothetical closure algorithm, not an executed native backend. Native instructions and wall time remain null; training_cost_eligible is false. Eight selector controls and four existing join controls pass. A new CLI output in operation-bound-controls preserves the previous control output unchanged.

The trace-feedback note calculates the complete first-step polynomials, including linked quadratic blocks and affine tails. A mandatory ax multiplier produces a pure-x term detected by Tr(a*x³), so the rectangular-plus-affine class cannot be invariant. This does not assert W3 differs from W2. The next obligation is stability of a larger linked-block space under all further cubic cancellations. No growing LFD bound is claimed.

No native build or new scientific/cloud run occurred. The native source remains4be27eee881663c44318ed2d9debfad05d071538; its saved owned-authentic-validation authorization is approved:false. Existing native telemetry policy still marks training_cost_eligible:false. The theorem-derived algorithm envelope does not override either condition.

Sources: generic-strict-closure-operation-bound.md and review; trace-feedback-top-structure.md and review; finite-selector-operation-bound-contract.md; prior no-wrap-uniform-cap-four.md. This continues the retained literature and definition audit; no novelty priority claim.
