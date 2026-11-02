#set page(paper: "a4", margin: 16mm)
#set text(size: 9.7pt)
= Independently replayable quotient certificates
2026-11-02 | EXP-PEXT-bf8f96 | H-PEXT-c3a11d

A Rust serializer now emits a complete single-curve standard-structure unit. A Python checker independently reconstructs finite-field arithmetic, points, cosets, charts and square-class relations. The experiment remains review_required and unapproved; zero scientific census trials ran.

#image("certificate-flow.svg", width: 100%)

*Coverage:* complete rational points and quotient partitions with P=R+2Q witnesses; all nonzero-T chart images with inverse/involution and full target-point coverage; exact ordered conjugates, every relation mask, constant square-class flags and both ranks. The baseline T=O cubic chart is explicit.

*Independent implementation:* Python imports no Rust arithmetic. It verifies irreducibility and log-table consistency, computes in the polynomial basis and checks square relations through polynomial products and a descending square-root construction. External input binds the expected prime, degree, modulus and actual model.

*Software validation:* source-bound software-tests.txt records rustc1.99.1/Python3.9.25. Four Rust groups and six Python methods pass, zero failures: five fixed certificates, eleven mutation variants, field/expected-input checks, scalar/projective controls, strict JSON and CLI acceptance/rejection. Fixed point/coset counts6/2,9/1,4/4,12/4,108/4 exercise software fixtures; they are not planned census measurements. The harmless unused-reexports warning is retained.

*Scope:* no blocking source defect identified for this interface; no independent scientific review or status promotion. Standard structure is one structure. Primitive/T canonical ordering is certificate-bound; future census inputs must freeze exact identities. Full curve/structure coverage, descent, original cohorts, exports and runnable packet remain next work.

*Sources:* #link("https://eprint.iacr.org/2015/805.pdf")[Iijima-Momose-Chao2015/805 sections3.1-3.3]; #link("https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf")[Chao ECC2007 slides25-26]. Full static review and boundaries: report.md. Archive TASK-20261102-dfd547 preserves previous snapshots. Canonical scientific graph edges remain unchanged.
