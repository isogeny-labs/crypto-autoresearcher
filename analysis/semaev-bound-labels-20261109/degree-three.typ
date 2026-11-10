#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Degree-three proof obligations and SAT certificates
2026-11-09. Fixed-m=2 Semaev continuation.

#image("degree-three.svg", width: 100%)

*Derived:* For the qualifying two-point family, trace elimination gives H=(uv)²+uv+u+v² on the trace-zero subspace. The original LFD lies between the branch LFD h and h+1. Coordinate-one refutation degrees e satisfy e<=h<=max(3,e+1).

*Obstruction:* The exact degree-three closure is the least stable low-degree space under all variable products and degree falls. A non-Semaev two-point family has the same quadratic closure dimension as the selected Semaev family and exact LFD3 at every size. Growing quadratic codimension therefore cannot establish unbounded LFD.

*Implementation:* Deterministic bounded DIMACS export reconstructs the GF2 feasibility system. A supplied complete model is checked against every CNF clause, every original equation, and the independent closed-kernel/capacity checker. Five tests pass. The hand-derived F8 model gives a checked lower bound3. No SAT solver or cloud experiment ran; bare UNSAT reports are rejected as unverified.

*Remaining proof:* Construct field-specific full-closure obstructions at increasing degrees on infinitely many qualifying subspaces. Neither unboundedness nor a uniform constant upper bound follows from this packet.

*Evidence:* degree-three-family-analysis.md; degree-three-certificate-obligation.md; degree-three-continuation-review.md; sat-translation-audit.md; sat-control/receipt.json. These are reviewed written arguments and software controls, not Lean certification.
