# Independent contract audit: GF(2) feasibility to DIMACS

Date: 2026-11-09. Source-only review of the proposed translation and the existing `encode_certificate.py` encoding layout. No solver execution or compilation. The new translator implementation was not yet supplied at this review stage; this is an exact mathematical and admission contract for its subsequent source review.

## Gate correctness and constants

An original feasibility unknown with zero-based encoding ID j maps to DIMACS ID j+1. Every auxiliary ID must be fresh and greater than the original variable count. DIMACS ID zero is reserved for clause termination.

For t equivalent to a AND b, the three clauses are

    (-t OR a), (-t OR b), (t OR -a OR -b).

For w equivalent to a XOR b, four correct clauses are

    (a OR b OR -w), (-a OR -b OR -w),
    (a OR -b OR w), (-a OR b OR w).

These enforce both directions. One-direction implications are insufficient for parity translation. Given original bits, each gate output is uniquely determined.

Canonical GF(2) terms must first reduce repeated Boolean factors and cancel duplicate monomials modulo two. Each surviving quadratic monomial receives an AND gate (or an explicitly deterministic reused gate). Let the remaining nonconstant term signals be s_1,...,s_m and let c be the constant parity. The equation is equivalent to XOR(s_i)=c. An XOR chain computes its left side; the final unit clause is positive when c=1 and negative when c=0. For m=1 use that signal directly. For m=0, c=0 requires no clause and c=1 requires an empty clause, emitted as a line containing only 0. The latter is UNSAT, not an export error and not a skipped equation.

## Equisatisfiability and bounded allocation

For each assignment of original unknowns, gate equivalences uniquely extend it to auxiliary values. That extension satisfies the parity unit exactly when the original equation vanishes. Combining equations therefore proves equisatisfiability and, for this deterministic gate construction, a unique auxiliary extension for each satisfying original assignment. No solver behavior or heuristic is involved.

The original encoder performs finite preflight before descent and monomial allocation. SAT export must add its own cap check before allocating clauses or output strings. If T is the total number of canonical nonconstant terms and E the equation count, the no-sharing construction has at most T AND gates and T XOR gates. Thus original_variables+2T variables, 7T+E clauses, and 21T+E literal occurrences are conservative preallocation envelopes. Exact counting before clause construction is preferable. Caller limits may only reduce finite defaults; booleans, negatives, unbounded overrides, and huge declared integers must not bypass validation. Headers must count every emitted empty or unit clause correctly.

The algebraic request must be validated and the feasibility encoding reconstructed from it. A caller-supplied encoding payload or hash cannot substitute for reconstruction. Bind canonical request, normalized input, equation binding, reconstructed encoding, variable mapping, and exact DIMACS bytes. Preserve deterministic IDs and source hashes; a hash declaration alone does not prove translation correctness.

## Model-to-certificate route

A SAT model is a proposed witness, not a mathematical conclusion by itself. Require every original feasibility unknown needed by the extraction to have an unambiguous Boolean value. Reject conflicting assignments, literal zero as a variable, out-of-range IDs, malformed integers, and incomplete assignments unless a documented completion is independently verified. Preserve the distinction between solver UNSAT, solver UNKNOWN, and a missing/incomplete model. Bare UNSAT text is not a checked proof of infeasibility and cannot establish an LFD conclusion.

The existing layout places C at offset zero with shape [monomial_count, quotient_dimension], row-major, followed by T and R. For monomial index j, the candidate C column is the bit vector whose coordinate a is original model bit C_offset+j*q+a. Monomial ordering must be reconstructed from the request, not read from untrusted model metadata. Values for AND/XOR auxiliaries are never C coordinates.

The extracted C, original normalized input, D, and q must then pass the independent direct candidate checker: full rank, C(1) nonzero, annihilation of the independently reconstructed original equations, and all low-degree-kernel shifts. This independent check ignores claimed T/R correctness and suffices to validate the mathematical certificate even if a candidate model originated from a faulty exporter or solver. If reporting that the model satisfies the exported feasibility instance, separately verify the entire reconstructed equation assignment or every DIMACS clause; do not conflate that report with the independently accepted C certificate.

Successful export alone has no certificate-found, exact-LFD, or dataset-admission consequence. A direct accepted C establishes its stated closure nonmembership/codimension. An LFD label additionally requires the separate verified solution-count, capacity, or named-ideal-consequence bridge. The original source-specific hypothesis bindings remain necessary.

## Required fixed software cases

Truth-table checks should cover all assignments of both gates, parity lengths zero/one/two/longer with both constants, duplicate cancellation, Boolean squares, fresh-ID boundaries, header counts, and preflight refusals. Model parsing should cover conflicting and omitted original IDs, invalid literals, auxiliary/original boundary confusion, and mutated request or mapping bindings. These are bounded implementation controls, not scientific solver runs. None were executed by this reviewer.

## Actual source review: certificate_sat.py

The implementation and `test_certificate_sat.py` were subsequently read. No tests were run by this reviewer. **No certificate soundness defect was found.**

`build` reconstructs the bounded canonical encoding from the request. `translate` deterministically shares sorted quadratic AND gates, then allocates XOR chains. Both gate clause sets are correct, the final parity sign is correct, and the empty-equation/constant-one cases are correctly distinguished. The exact gate and clause counts agree with the construction. The byte envelope includes signed literal lengths and clause terminators; its fixed overhead covers the header and comment. Pair-set precomputation occurs before CNF preflight but remains bounded by the original encoder's term cap. Clause and string allocations occur after CNF preflight.

`check_model` rebuilds the CNF, requires a complete assignment, checks every clause, and additionally evaluates every original GF(2) equation. It extracts C with the correct zero-based-to-DIMACS offset, then calls the independently reconstructing capacity/candidate checker. Capacity refusal leaves the LFD bound null and explicitly distinguishes a checked model from an unchecked certificate. Inconsistent evidence has its own status and nonzero CLI exit. UNSAT/UNKNOWN reports are rejected as unverified, not interpreted as proofs. The direct checker remains the certificate acceptance authority.

The parser rejects repeated IDs (even repeated identical values), missing assignments, oversized literals, out-of-range IDs, and missing SAT status or terminator. It is somewhat permissive about where terminator zero appears: it can accept additional nonzero literals after a zero and does not require status to precede assignment lines. This does not permit a false certificate, since complete assignment, CNF, GF(2), and direct-kernel checks still follow. If strict conventional model formatting is desired, enforce final termination explicitly; this is a syntax refinement, not a mathematical correctness blocker.

The supplied controls cover gate/parity truth assignments, an explicitly supplied hand-derived F8 certificate assignment, mutations, partial/UNSAT/UNKNOWN models, determinism, header counts, and a capacity refusal. Reading these tests does not constitute an independent execution of their reported passes. The implementation invokes no SAT solver. Source hashes and reconstructed request/encoding/CNF bindings accompany outputs; immutable export files preserve the mapping.
