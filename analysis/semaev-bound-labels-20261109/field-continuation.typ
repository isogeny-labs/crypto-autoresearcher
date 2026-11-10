#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Explicit families and limits of degree amplification
2026-11-09. Parallel written derivations and independent review.

#table(columns: (1fr, 1fr), inset: 8pt,
[Construction or criterion], [Established implication],
[Retain V in a larger field], [Same closure at caps at least two],
[Disjoint satisfiable systems], [LFD is the maximum of component LFDs],
[Slice dual separator of degree c], [Slice refutes at cap at most c+2],
[Polynomial V of degree at most r; n>4r], [Exactly two ordered solutions for every r])

*Explicit family:* With z=a6=1, the Semaev equation is (xy)²+xy+(x+y+1)²=0. No reduction occurs modulo the field polynomial when n>4r. If x and y both have positive polynomial degree, (xy)² has a unique highest-degree term, a contradiction. Constant substitution leaves precisely (0,1) and (1,0). This removes the existential basis-selection issue for this family.

*Degree remains separate:* Its r=1 member has exact LFD2 by an explicit affine-ideal derivation. The earlier odd-diagonal lower bound3 does not apply. Solution-count growth or increasing quotient dimension cannot substitute for a full-closure degree obstruction.

*Field-specific obligation:* For the unique-zero branch H, choose a separator lambda(v) annihilating L_v(W) and pairing to1 with v². If its degree is at most c on each coordinate-one slice, then LFD(H)<=c+3. Excluding low-degree separators alone does not exclude arbitrary refutations using u-dependent multipliers. A normalization theorem is missing.

*Transport:* A degree-s substitution maps source closure at D into target closure at max(sD,c), provided eligible generator images are derived at c. Rank may drop under certificate pullback. Enlarging V additionally requires the named polynomial still to vanish on every new solution. Disjoint products cannot amplify degree.

*Evidence:* polynomial-subspace-candidate.md and review; field-pencil-dual-obligation.md and review; closure-transport-and-amplification.md and review. No new scientific runs or solver executions. The unbounded-LFD theorem remains open.
