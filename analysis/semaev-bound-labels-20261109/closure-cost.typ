#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Saturated closure: work bounds and algebraic frontier
2026-11-09. Theorem-derived algorithm counts; no native timing claim.

#image("closure-cost.svg", width: 100%)

#table(columns: (1fr, 2fr), inset: 8pt,
[Start], [Insert R normalized Boolean input rows],
[Queue], [At most L eligible immutable pivot rows],
[Feedback], [At most N L variable-product insertion attempts],
[Stop], [Queue empty implies full strict degree-D closure])

M is the number of monomials through degree D; L counts those through D-1. A degree-first echelon basis makes low-pivot rows span the entire eligible intersection. Thus feedback does not require reprocessing old rows. Total insertion attempts are at most R+NL; whole-row XORs are at most (R+NL)M. Dense coefficient storage is at most M² bits. Indexing, metadata, input reconstruction, solution extraction and provenance have separate costs.

For the complete Boolean ideal, D=N+1 and M=L=2^N. The finite-selector CLI labels these combinatorial maxima for the stated reference algorithm after verifying every original polynomial. It does not report executed work, native instructions, wall time, or training-eligible measured cost.

The modular proof now calculates every first-feedback polynomial. Pure-x, pure-t, mixed and epsilon-coupled blocks have linked coefficients and affine tails. The mandatory multiplier a*x creates a genuine pure-x quadratic term for some a, so the original rectangular-plus-affine class is not invariant. A larger space stable under all feedback remains missing.

Validation: eight selector controls and four existing join controls pass. Earlier control outputs are preserved. No scientific trial, native build or cloud job ran. Source and independent reviews are retained alongside operation-bound-controls/.

Evidence: generic-strict-closure-operation-bound.md; trace-feedback-top-structure.md; their independent reviews; finite-selector-operation-bound-contract.md. These are written proofs and a software label implementation, not formal-kernel certification or native backend runtime bounds.
