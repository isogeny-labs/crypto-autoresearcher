# Exact last fall degree three for the no-wrap r=6 family

2026-11-09. Independent symbolic derivation, prepared before receiving any degree-three execution result. No solver, full-closure computation, build, or cloud job was run for this note.

## Statement

For every irreducible field modulus of degree n>24, take V=span(1,t,...,t^6) and the m=2 Semaev system with z=a6=1. In the strict Boolean closure convention used by the study,

                         d_LFD = 3.

The lower bound is the independent polynomial-gcd proof in no-wrap-r6-symbolic-obstruction.md. This note proves the matching upper bound through two cubic trace functionals and degree-three gates.

## Reduced system and the two trace functionals

After the five affine consequences already available at cap two, use

 q=b Q1+c Q2,   Q1=T+T³,   Q2=T²+T³,
 E=A(x)+x A(q)+q²,         A(p)=p²+p,
 x=x0+x1 T+...+x6 T^6.

The polynomials P1=Q1+1=T³+T+1 and P2=Q2+1=T³+T²+1 are irreducible over F2: neither cubic has a root in F2. For j=1,2 define the F2-linear functional on coefficient polynomials

 lambda_j(f)=Tr_(F2[T]/Pj / F2)(f mod Pj).

This is a fixed linear combination of the coefficient rows, not a multiplication by a rational function or a field extension of the Boolean variables. The identity Tr(A(w))=0 follows directly from the three-term Frobenius trace, and Tr(1)=1 since the extension degree is three.

On the slice c=0, q=b Q1. Modulo P1 we have Q1=1, so q=b, A(q)=0 and q²=b. Thus

                       lambda_1(E|_(c=0))=b.                (1)

Likewise, on b=0 the second functional gives

                       lambda_2(E|_(b=0))=c.                (2)

These are literal polynomial identities in the remaining Boolean coordinates. In particular they are constant-row combinations of the respective sliced equations; no multiplication step is hidden in (1) or (2).

## Degree-three gates derive a new affine consequence

Each lambda_j(E) is a degree-at-most-two consequence of the original reduced equations. Multiplication by the affine gate 1+c or 1+b is permitted at cap three. Since Boolean reduction gives c(1+c)=b(1+b)=0, equations (1)-(2) imply

 (1+c)lambda_1(E) = b+bc in W3,
 (1+b)lambda_2(E) = c+bc in W3.

Their sum gives

                           b+c in W3.                      (3)

This is the crucial new affine consequence absent from W2. The gates are essential: the two slice identities are not treated as simultaneous unconditional equations.

## Reduction to the previously solved one-bit system

Use (3) to eliminate c=b. Correcting a quadratic equation under this affine substitution uses only variable multiples of b+c; these lie in W3. Therefore we may now work with

                        q=b(T+T²).

Then A(q)=b(T+T4). The coefficient of T12 in E is exactly x6, because x A(q) has degree at most10. Thus x6 belongs to W3. The coefficient of T10 is x5+b x6; multiplying the known linear x6 by b and adding derives x5 within W3.

Removing x6,x5 leaves exactly the r=4 one-bit system. For completeness write x=a+pT+dT²+eT³+fT4. Its useful coefficient rows are

 R1=p+ba,
 R2=p+d+b+bp,
 R3=e+bd,
 R5=bp+bf,
 R7=be,
 R8=f+bf.

R2+R5+R8 gives the affine relation L=p+d+f+b. Substituting d=p+f+b gives R2'=f+bp and R3'=e+bp+bf+b. Their sum with R8 derives e+b. Multiply e+b by b and add R7=be to derive b, using b²=b. Then R1,R2,R3,R8 derive p,d,e,f. Every step after the gates uses only addition and multiplication of an available linear by a variable, so remains within W3.

We have derived b,c and all x_i for i>0. The eliminated affine relations give every positive y_i and y0=x0+1. These generate the complete affine ideal of the two constant solutions. Affine elimination gives degree-controlled representations of every polynomial in that ideal; since its affine generators are in W3, this proves d_LFD<=3. Combining the prior full-W2 obstruction proves equality.

## Scope and next consequence

The proof holds uniformly over all n>24 because the no-wrap coefficient presentation is independent of the chosen irreducible modulus. It proves an exact degree for this explicit member size, rather than an asymptotic growing bound. Larger no-wrap members inherit the lower bound three by restriction; this argument does not supply their matching upper bounds.

The concrete mechanism is an odd-degree factor of Q_j+1 furnishing a field-trace affine consequence on a coordinate slice. Two such gated consequences collapse the surviving two-dimensional q-space to the one-bit case. Generalizing this to growing q-dimension requires controlling the number and degrees of selector gates; it cannot be inferred from the existence of trace functionals on individual slices alone.
