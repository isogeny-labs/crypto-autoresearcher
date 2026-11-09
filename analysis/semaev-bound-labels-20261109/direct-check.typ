#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Direct closed-kernel checking and SAT extension bounds
2026-11-09. Written proof review and fixed software controls.

*Checked implementation:* The bounded CLI directly reconstructs the quadratic coordinate equations and tests a basis of the entire eligible kernel. A map satisfying the input equations but failing kernel multiplication is rejected. Eight software controls pass. Acceptance, predicate rejection and capacity refusal have distinct retained JSON artifacts. No search solver ran.

#image("direct-check.svg", width: 100%)

*Derived SAT bound:* For one quadratic definitional extension G of F with M greater than zero solutions, let b = max(2, floor(log2(M+1))). The reviewed arguments give dF <= max(dG,b)+2 and dG <= max(dF,b+1). Consequently uniformly bounded solution counts permit transfer of LFD boundedness or unboundedness.

*Scope of the counterexample:* A generic family with a degree-n input monomial has LFD zero before extension and at least n after adding one quadratic definition. That family rules out unrestricted additive invariance. Its high-degree generator means it does not settle the quadratic Semaev case.

*Remaining obligation:* Construct growing full-closure witnesses for actual Semaev inputs and supply the required UNSAT, solution-count or missing-consequence bridge. No infinite hard Semaev family has been established.

*Evidence:* direct-checker-audit.md; direct-checker-final-validation/receipt.json; sat-one-bit-elimination.md; sat-one-bit-elimination-review.md. Input limits and vector-operation accounting are explicit; they are not native instruction measurements. The first test-file path failure and earlier source snapshots are preserved.
