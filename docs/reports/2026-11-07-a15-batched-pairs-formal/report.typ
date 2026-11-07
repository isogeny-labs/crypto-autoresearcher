#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set heading(numbering: "1.")
= A15 batched-pair algebra: technical proof review

#text(size: 8pt)[2026-11-07 UTC · Crypto Autoresearcher · TASK-20261107-b23fd5]

The named Lean theorem proves two product-tree inverse propagation identities for nonzero field elements and two simultaneous-sign identities for A15 affine candidate formulas. The full pinned workspace build and axiom audit passed; the independent blind derivation holds at that algebraic scope. Source correspondence is reviewed separately in the attached source report.

#image("diagram.svg", width: 100%)

== Exact machine evidence

Target: `CryptoResearch.PrimeField.BatchedPairs.a15_algebraic_joints`. Producer proof commit: `bafd5233baef85efa1afa5a385fe3d5cc5d3235f`. Source base: `d4cf45f012a0208b179d947052cb47b82f06ee09`. Lean 4.35.0; Mathlib `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`; CryptoLean `60952c696ded7f3da4f4517006d9af6482662487`.

The passing `verify-passed.json` records `build_passed=true`, `axiom_audit_passed=true`, no forbidden constructs, and axioms `propext`, `Classical.choice`, `Quot.sound`. Its `needs_semantic_review=true` is why the separate reports were commissioned. An earlier full verification timed out after 120 seconds and its receipt has empty logs; the cached retry passed. The source reviewer matched all 104 workspace and 10 verifier input hashes in the passing receipt. Its separate fresh Lean command did not reach elaboration because the pinned toolchain was absent.

== Claim and controls

For nonzero x and y in a field, one inverse of x*y recovers the two child inverses by multiplying by the opposite child. The formula slope `(yk-yj)/(xk-xj)` changes sign when both y inputs change sign; its candidate X stays fixed and candidate Y changes sign. Therefore the four signed formula outputs can be formed from two directly evaluated slopes.

The blind reviewer derived the identities independently and exhaustively checked 208 inverse input pairs and 17,764 formula quadruples in five small prime fields. Controls with exactly one zero child break joint inverse recovery. Equal-x inputs retain the formal sign identities under totalized inversion but fail the geometric point-addition reading: on `y²=x³+x+1` over F5, P=(0,1) and -P=(0,4) must sum to infinity, while the secant formula returns a finite coordinate.

== Scope and next bridge

This packet validates the scoped field identities and inspected local source correspondence. The target does not establish the complete product-tree recursion, NumPy uint64 refinement, curve-point validity, operation counts, timing, or authentication of A15 execution rows. The source review rejects a widened run-parity interpretation. The precommitted Markdown plan omits the final `e` of the Lean SHA-256; `review-summary.md` preserves the correction. The structured independence consistency check passed on a post-review transcription of that plan and reviewer-authored attestations, with the timing limitation stated there. No official hypothesis or evidence status is changed by this technical packet.

== Sources and custody

See `review-plan.md`, `blind-input.md`, `reviews/blind/report.md`, `reviews/source/report.md`, and both immutable verifier receipts in `evidence/`. The source files are `research/prime_field_a15_execution_20261107/pairbuild15.py` at SHA-256 `c8cbe4ab864157ff4c4c4f0b0414950847e7de0355585199629778c50280f55a` and `research/prime_field_a12_execution_20261106/batch_query.py` at SHA-256 `30f20fc9c8c276d2c2f90881b48f8a33ca6d32d9b67ec60a70580a241b30f72b`. The diagram is explanatory; no performance metric is graphed for this pure proof review.
