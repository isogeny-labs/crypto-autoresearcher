#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Uniform first- and last-fall bounds for a Semaev family
2026-11-09. Independently reviewed written proofs and finite certificate checks.

For z=a6=1, V=span(1,t,...,t^r), and every irreducible field modulus of degree n>4r, the two ordered solutions are (0,1) and (1,0). This is the no-wrap coefficient presentation of fixed-m=2 Semaev descent.

#table(columns: (1fr, 1.6fr), inset: 8pt,
[Claim], [Established scope],
[First fall degree = 2], [Every r>=1; original rows and stated conventions],
[Last fall degree <= 4], [Every r; uniform selector-peeling proof],
[3 <= last fall degree <= 4], [Every r>=6; combines the restriction lower bound],
[Last fall degree = 3], [r=6; symbolic proof and complete certificate replay])

*Uniform upper bound:* After affine reduction, E=A(x)+xA(q)+q². Fixing the highest surviving coefficient of q to1 gives a cap3 refutation by two leading-x branches. One additional selector derives that q coefficient at cap4. Previously derived higher coefficients can be removed without raising the cap, so descending through all coordinates stays at4.

*First-fall witness:* A dyadic chain of original quadratic coefficient rows telescopes to a new nonzero affine relation. The only original affine row is x0+y0+1, so no earlier nonzero fall occurs. This establishes the two stated FFD conventions, not a presentation-invariant or syzygy-based claim.

*Exact finite check:* The r6cap3 certificate has rank468, eligible dimension104, affine dimension13, and no missing ideal generators. Its proof was independently reviewed before execution; a separately invoked verifier reproduced the result. The previous cap2 symbolic obstruction proves the matching lower bound.

*Arithmetic cost:* A dense incremental cap4 closure needs at most O(N^12) binary operations and O(N^8) bits, N=2(r+1), under the explicit indexed-bit-access model, plus input conversion. This is not native instructions or wall time. The solutions of this particular family are already explicit.

*Research consequence:* This explicit infinite family is bounded and cannot prove unbounded LFD. Modular-reduction families and the half-dimensional factor-base regime are outside this theorem. The broader dataset, solver-cost, and unboundedness objectives remain open.

*Evidence:* no-wrap-uniform-cap-four.md and review; no-wrap-first-fall-two.md and review; no-wrap-r6-exact-degree-three.md and review; no-wrap-w3/attempt-1 and independent replay. Written proofs are not Lean kernel certification.
