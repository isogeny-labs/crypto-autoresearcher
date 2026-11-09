#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Infinite constant lower bounds and an exact F8 control
2026-11-09. Reviewed written proofs and deterministic certificate verification.

The count-controlled fixed-m=2 families now have a proved lower bound of three. Every qualifying two-solution subspace containing1 satisfies it. A symplectic exceptional-set count also proves it for infinitely many trace-active UNSAT subspaces. These lower bounds are constant; no growth beyond three is established.

#image("degree-two.svg", width: 100%)

*Exact dimension:* For N=2k Boolean variables on the nonexceptional odd diagonal, dim(W2)=2N-2, so the exact degree-two quotient dimension is (N²-3N+6)/2. Its growth at fixed cap does not prove growing LFD.

*Positive verification control:* Over F8 with t³+t+1=0 and V=span(1,t), the input rows are a+c+1; ad+bc+bd; ad+bc+b+d. Their latter sum g=b+d+bd satisfies b*g=b and d*g=d in the Boolean ring. The checked rank-five quotient at D=2 exceeds capacity four; the cap-three identities derive the entire affine ideal. Thus this fixed normalized input has exact LFD3. Three controls and actual CLI verification pass. No search campaign ran.

*Next proof obligation:* On a verified two-point instance, LFD>D is equivalent to a known affine generator missing from W_D and to exact codimension greater than two. The density note gives an explicit sufficient bound on the set of degree-D easy subspaces. That bound is still missing for increasing D; the next closure cap to analyze is three.

*Evidence:* degree-two-family-obstruction.md and independent review; degree-two-codimension-addendum.md and review; two-point-lfd-characterization.md and review; closure-exception-density.md; degree-three-control/validation.json. The target remains order four and family basis selection remains existential. These are written proofs and finite checks, not Lean certification.
