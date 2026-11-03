#set page(paper: "a4", margin: 16mm)
#set text(size: 10pt)
= Degree-two quotient construction and census design
2026-11-02 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d

An explicit quotient quartic preserves the actual elliptic curve on its affine chart. The residual, discriminant, inverse and removable-point identities were checked symbolically by the root session (SymPy 1.14.0). This is a construction component; zero scientific trials ran.

#image("construction.svg", width: 100%)

*Design:* n=3 with q=5,7,11; n=5 with q=3, preserving complete curve/twist cohorts. Abstract n=7 placements are separate.

*Sources:* Iijima, Momose and Chao, ePrint 2015/805, sections 3.1-3.3 (#link("https://eprint.iacr.org/2015/805.pdf")[primary PDF]); Chao, ECC2007, slides 25-26 (#link("https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf")[slides]). The coefficient restrictions require descent checks beyond branch rank. Type2 signature and the hyperelliptic exception are separate predicates.

*Readiness:* review_required and unapproved. Complete quotient charts, T cosets, square classes, descent witnesses, exhaustive structure coverage, independent checker and frozen analysis are still required. Exact source/input hashes, trial plan, handoff, queue, lawful lane and permitted Executor runtime precede approval. Two existing PEXT lanes fill cap2; no third lane was opened.

*Next:* complete projective quotient and square-class checks, then full cohorts and exact-byte preapproval. Detailed formulas, assumptions and obligations: design-obligations.md. Canonical lead graphs were inspected; no verified scientific edge changes in this design-only round.


Scope clarification: P3 tests the original geometric genus minima. Descent-admissible minima are a separate descriptive output, never a strengthened P3 criterion. The original H1 configuration/curve-count ratio arm retains q=5,7,11,13, with q=13 separate from the P3 cohort. H1 equidistribution is not asserted or gated. Symbolic replay command: `python implementation/degree2_identity.py`; four checks PASS, recorded in symbolic-check.json. The root is the producer; this is no independent scientific review.
