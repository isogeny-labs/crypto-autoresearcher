# Mandatory field-specific degree-three falls in the modular presentation

2026-11-09. Source-only analysis; no execution, instance search, build, or cloud job. This note gives explicit quadratic consequences that any proposed W3 obstruction must include. It does not claim a complete W3 description or a growing lower bound.

## Presentation valid also when 1 is outside V

Let n be odd, dim V=(n+1)/2, and let the trace be nonzero on V. V need not contain1; this includes the trace-active UNSAT existence family. Put s=x+y+1 and ell=Tr(s). Let pi(s)=s+ell, the projection onto K0=ker Tr, and let J invert A(w)=w²+w on K0. Define the affine K-valued map

 B(x,y)=J(pi(x+y+1))².

With an auxiliary Boolean bit epsilon, use

 ell=0,       G(x,y,epsilon)=xy+B(x,y)+epsilon=0.             (1)

This is the exact one-bit extension of the original system, with epsilon=Tr(xy). In fact Tr G=Tr(xy)+epsilon and A(G)=F+ell, where F=A(xy)+(x+y+1)². Thus both directions are explicit field-linear row operations once the bit definition is included. The correction pi is essential outside the trace slice; J is not silently applied to a vector outside its domain.

## Explicit quadratic falls at cap three

Every coordinate of G has Boolean degree at most two. Multiply its coordinates by the linear coordinate expressions of x and combine according to field multiplication. This is a valid strict cap-three operation and yields the field equation

 xG=x²y+x B(x,y)+epsilon x.                                  (2)

Each coordinate of (2) has Boolean degree at most two: Frobenius x->x² is linear, and B is affine. Similarly

 yG=xy²+y B(x,y)+epsilon y                                   (3)

is a quadratic consequence in W3. These are genuine cubic-to-quadratic falls induced by the field tensor, even though the initial input row span need not contain them.

The same statements hold after eliminating ell. Therefore a proposed stable quadratic space Q certifying a W3 lower bound must contain all coordinates of G,xG,yG (and the known affine ideal multiples), not just the initial coefficient span. If these consequences yield further linears or quadratics, strict closure also requires multiplying those and iterating.

This supplies an explicit reason why a normal-form rank calculation by itself is insufficient: the multiplication identities impose degree-three feedback for every field and every V, without a genericity assumption.

## Which field-valued linear multipliers give this cancellation?

Before eliminating ell, take independent x,y in V and epsilon in F2. Consider a K-valued affine multiplier

                 m=a+L(x)+M(y)+c epsilon,

where L,M:V->K are F2-linear. Its product mG has Boolean degree at most two as a K-valued polynomial precisely when

 L(x)=alpha x,   M(y)=beta y,   c=0                          (4)

for scalars alpha,beta in K. Here V is nonzero. To verify this, the cubic terms from xy L(x) have bidegree(2,1) in x,y. Their vanishing is equivalent to

 x L(z)+z L(x)=0 for all x,z in V.

Choose any nonzero z in V to obtain L(x)=L(z)x/z. The y argument is identical. The epsilon-cubic term is c epsilon xy, which is nonzero for c!=0 by taking nonzero x,y. The three types of cubic monomials cannot cancel each other because their variable groups differ. Conversely (4) gives precisely the falls (2)-(3) and constant row combinations.

This classifies field-valued product cancellations, NOT all scalar-output syzygies. Trace can annihilate a nonzero field-valued cubic, so the latter class is larger.

## Exact trace-level multiplier conditions before the trace slice

For a scalar consequence Tr(mG), cancellation of its cubic part is equivalent to

 x L(z)+z L(x) in V_perp for all x,z in V,
 y M(z)+z M(y) in V_perp for all y,z in V,
 c in (span(VV))_perp.                                      (5)

These equations follow by polarizing the two same-variable factors and pairing the remaining independent variable with the field trace. They involve the exact multiplication tensor and trace-orthogonal subspace, rather than arbitrary MQ matrices.

On the half diagonal span(VV)=K. Indeed if a nonzero c annihilated every product, cV would be contained in V_perp, impossible since dim V=(n+1)/2>dim V_perp=(n-1)/2. Hence the last condition in (5) forces c=0. The remaining conditions are an explicit linear-algebraic classification problem for L and M modulo trace annihilation.

A full W3 analysis with ell=0 must impose the analogous condition after affine elimination of ell. Conditions (5) are not asserted complete for that quotient: products with the known trace relation may cancel additional cubic terms. The universally valid consequences (2)-(3), however, remain mandatory in the quotient.

## Exact next obstruction, with the failed shortcut recorded

The tempting construction Q=span of the initial quadratic equations fails as a proposed generic invariant unless it also contains (2)-(3) and every subsequent quadratic fall. These falls cannot be discarded because multiplication by x or y was described as a field operation: their implementation is precisely a sum of permitted Boolean variable multiplications at cap three.

For trace-active UNSAT subspaces the useful next lemma would classify the trace-slice version of (5), then prove that the resulting quadratic space is stable under all further linear multiplications while omitting1. The current note does not establish that stability. Equally, (2)-(3) do not by themselves imply a uniform refutation bound; their affine consequences depend on V and the map B.

This narrows the proof obligation to explicit trace-orthogonality identities of the actual restricted field multiplication tensor, and records mandatory feedback that any growing lower-bound certificate must respect.
