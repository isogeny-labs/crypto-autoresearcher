#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Infinite count-controlled Semaev families and the capacity bridge
2026-11-09. Reviewed written existence arguments and fixed software controls.

For z=a6=1, the normalized equation is x²y²+xy+x²+y²+1=0. A direct point correspondence with E: Y²+xY=x³+1, Hasse's bound and exact subspace probabilities establish the following results.

#image("family-bridge.svg", width: 100%)

*Why the SAT existence proof works:* All full-field zeros except (0,1),(1,0) have 1,x,y linearly independent over F2 for odd n. Averaging over subspaces containing1 gives an expected count below four. Every count is even and at least two, so some subspace has exactly two zeros. This does not certify an arbitrary input subspace.

*Why the UNSAT refinement helps:* Removing trace-zero subspaces before averaging yields a trace-active UNSAT subspace whenever the elliptic Frobenius trace is nonnegative. The irrational Frobenius angle supplies infinitely many suitable odd extensions. No growing closure obstruction has been constructed.

*Implemented bridge:* A bounded CLI reruns direct kernel verification, reconstructs structural solution capacities and requires strict q>U. Six software controls pass; the known two-solution control remains inconclusive at q=U. No positive scientific lower-bound fixture was exercised. Code and proof hashes are bound in results. No scientific trial, solver search, native build or cloud job ran.

*Evidence:* low-solution-count-family.md and its review; trace-active-unsat-family.md and its review; capacity-bridge-audit.md; capacity-bridge-validation/receipt.json. Hasse source: MIT 18.783 (2023), Lecture 7, Theorem 7.3. These are written proofs, not Lean-certified theorems or a novelty claim.
