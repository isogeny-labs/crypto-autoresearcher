# Independent source review: bounded exact Boolean LFD reference computation

Date: 2026-11-09. Source-only review of `exact_boolean_lfd.py`, `test_exact_boolean_lfd.py`, and `inspect_retained_lfd.py`. No tests, enumeration, or scientific closure execution by this reviewer.

**No mathematical correctness defect was found.** The implementation follows the separately reviewed all-cap deficiency criterion and labels its result as a reference computation, not an independently checked certificate.

The API validates N in 0,...,12, equation/term caps, canonical integer masks, duplicate-free ANF rows, and finite integer budget before computational allocation. It evaluates every assignment of the full Boolean cube against the actual input rows. The solution count is set only after the entire enumeration completes; short-circuit rejection of an assignment after a nonzero row is logically sound.

For each cap, monomials are listed in decreasing degree and echelon pivots use the least occupied column. Therefore the earliest pivot is the highest relevant degree, and low-pivot rows span the complete eligible intersection. Immutable row insertion, queueing each eligible row once, and shifting only sources of degree strictly below cap implement full strict closure. Input rows are admitted according to their actual maximum monomial degree. All cap-zero, zero-row, and zero-variable cases follow the same logic safely.

Evaluation columns are built on the complete solution list. Their rank gives the exact evaluation-map rank on the cap's monomials. Ideal dimension is then M_D minus that rank. The implementation checks closure rank cannot exceed it, records each fully completed cap, and updates the last deficient cap. It checks that the final N+1 cap is not deficient before setting exact_lfd=last_missing+1. Thus zero is correctly returned when no cap is deficient.

Budget exhaustion at any stage leaves exact_lfd null and status budget_exhausted. Completed earlier caps and an already completed zero count may remain as partial observations, but no partial run becomes an exact label. Counters cannot exceed the requested limit. The bounded shape-validation pass is explicitly outside charged algebraic work; the accounting model is not native instructions or wall time.

The wrapper first performs the independently reviewed exact finite-selector map/equation join, then analyzes those literal rows. It binds original files and implementation sources, retains the normalized strict-cap definition, and keeps dataset/group/provenance/training-cost admission false. Its operation limit governs the reference analysis; the preceding field validation and truth-table reconstruction performed by the join are separate bounded work and should remain clearly described as outside that counter. The wrapper's smaller ten-million cap is compatible with the API's finite upper ceiling.

The tests cover affine no-fall degree zero, affine UNSAT degree one, quadratic UNSAT degree two, genuine feedback, empty/constant systems, mixed input eligibility, both immediate and late budget exhaustion, accounting categories, and malformed masks/budgets. I inspected their logic but did not rerun their reported passes. No standalone derivation artifact or independent verifier is emitted by this implementation, and its `independently_checked_certificate: false` declaration accurately states that limitation.

### Wrapper scope and controls readback

Confirmed the wrapper now emits `operation_limit_scope` explicitly excluding input loading, the polynomial join, source hashing, and output I/O. Read the three CLI controls: complete analysis on the independently specified repeated-code fixture with the expected four code solutions; budget exhaustion returning a null exact degree; and a corrupted equation refused before any output artifact is created. Non-overwrite behavior is checked as well. These are appropriate software controls, not production evidence, and were not rerun by this reviewer.
