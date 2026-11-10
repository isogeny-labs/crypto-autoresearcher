#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Fixed-m=2 Semaev: lower-bound transfer and finite search contract
2026-11-09. Written proof review and bounded software controls.

*Derived:* A codimension-t affine restriction with UNSAT refutation degree d greater than t transfers a lower bound d to the original system's LFD (with the degree-two convention threshold). After trace elimination, the alternate quadratic model is a single quadratic definitional extension. For UNSAT reduced systems, its refutation degree differs by at most two. Neither result constructs an infinite hard family.

*Implemented:* A finite quadratic GF(2) encoding of full closed-kernel certificates, including partial multiplication and a right inverse. Seven encoder controls and seven inspector controls pass. An emitted rank-two software example satisfies all 24 equations under its hand-specified assignment. No search solver, native build or scientific draw ran.

#image("search-contract.svg", width: 100%)

*Integration boundary:* Reconstructing a full vector space from parameters does not authenticate a dataset's finite point-list system. Dataset admission stays false. Written bounds, exact degrees, nonmembership and solution-count/UNSAT bridges remain distinct fields.

*Evidence:* certificate-feasibility-contract.md; lower-bound-transfer-obligation.md; lower-bound-transfer-audit.md; inspector-integration-audit.md; encoder-validation-001/receipt.json; examples/cli-receipt.json. The new infinite-family lower bound remains unproved.
