# Independent review of the inside-subfield alternate system

Date: 2026-11-09. Source-only review of `inside-subfield-next-obligation.md`; no experiments, builds, or fresh replay. Verdict: displayed identities and solution correspondence are correct, and both finite-closure inclusions are justified **at D≥2**. The publication copy has been qualified accordingly following this review.

## Algebraic identities

Write P=xy, s=x+y, r=sqrt(P/z), c=sqrt(a6)/z. Then sqrt(F)/z=P/z+sqrt(P/z)+s+c=r²+r+s+c, proving (1). Under y=x+r²+r+c, write P=G+zr². Expanding P²+zP+z²s²+a6 gives G²+zG because z²c²=a6 and s²=r⁴+r²+c². This proves (3). Direct substitution of zr²=xy into G gives x(r²+r+x+y+c)=x sqrt(F)/z, proving (4).

The composition formulas also follow: sqrt(x(x+r²+r+c)/z)=r+sqrt(G/z), and x+r²+r+c=y+sqrt(F)/z. They give mutually inverse maps on the exact finite zero sets. The valid universal SAT witness is x=0,y=c, corresponding to x=r=0 in G. No diagonal witness or variable division is needed.

## Strict-closure simulations and the necessary low-cap qualification

For tau, coordinate substitution is affine and does not increase degree. Every initial coordinate of F(tau) is a scalar F2 combination of G coordinates, by G²+zG. At **D≥2**, all quadratic-or-lower G coordinate inputs are eligible. Each permitted source multiplication by a variable becomes multiplication by an affine polynomial, which can be simulated by scalar combinations and individual variable multiplication at the same cap. This establishes tau*(W_D(F))⊂W_D(G).

The argument from equation-row-span equality alone does **not** justify D=0 or1: affine input rows on one side might be combinations of quadratic rows on the other, which are not eligible at those caps. Therefore the recommended publication statement is D≥2, without an unsupported universal low-cap claim. It leaves all growing-degree reasoning unchanged. A specialized D1 result might be established separately using the trace row, but is unnecessary here.

For sigma, every substituted G coordinate is a scalar combination of x-coordinate multiples of F coordinates, by x sqrt(F)/z, and is derivable in W3(F). For D≥2, this initialization fits W_(2D). If a source row has actual degree≤D−1, its substituted multilinear polynomial has degree≤2D−2; multiplication by a substituted coordinate of degree≤2 uses at most two variable multiplications, with intermediate degree≤2D. Scalar combinations and Boolean normalization preserve the asserted membership. This establishes sigma*(W_D(G))⊂W_(2D)(F) under the strict source-degree rule.

The degree-dropping case creates no hidden issue: the source row is considered in its actual multilinear form before substitution. Its substituted degree is bounded by twice that actual degree, even when its earlier derivation used higher-degree lines. Conversely, one must not authorize a multiplication merely because its final reduced product has low degree; the argument here explicitly bounds every intermediate source degree.

## Scope of the simulation

The factor-two simulation establishes a finite-cap inclusion, not a uniform LFD transfer. For a desired original ideal polynomial of degree e, a cap proportional to2e does not satisfy the requirement max(C,e) with a constant C. The note correctly leaves the high-degree correction problem unresolved. The existing k+2 inside-subfield upper bound remains available; “no bounded result” should be read as “no new uniform constant bound,” not as denying that existing growing upper bound.

## Rational/trace transformation

For s=r²+r+c≠0, t=x/s and q=sqrt(z)r/s satisfy t²+t=q². Then u=t+q gives u²+u=q, exactly the displayed Artin–Schreier equation. Exceptional s=0 values must remain separate and give x=sqrt(z)r.

Because c≠0 and z≠0, the denominator has two distinct nonzero roots over an algebraic closure and the numerator does not vanish there. The resulting right side has two simple poles, consistent with the standard genus-one Artin–Schreier calculation. This does not furnish a rational parametrization or a degree lower bound. The high binary exponent weight of an explicit inversion formula is a cost of that formula, not a proof that every closure derivation has high degree.

## Outcome

No mathematical error was found in (1)–(4), the finite zero-set bijection, or inclusions (5)–(6) after the D≥2 qualification. No constant-LFD theorem, unbounded-LFD theorem, formal verification, or runtime check is established by this review.
