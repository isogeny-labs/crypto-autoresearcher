# Independent review: low-solution-count Semaev existence families

Date: 2026-11-09. Source-only mathematical review of `low-solution-count-family.md`, including its optional Section 10. No computation, sampling, build, solver, or cloud execution was performed.

**Verdict: the two-solution existence theorem and the optional unsatisfiable existence theorem are correct with the stated parameters and existential scope.** They provide infinite families with known solution counts; neither proof provides a growing closure obstruction or an efficient basis construction.

## Exact algebra and geometric hypotheses

For odd n, the only zeros of F(x,y)=x²y²+xy+x²+y²+1 for which {1,x,y} is linearly dependent are (0,1) and (1,0). Substitution at x=0 or 1 gives these pairs. Otherwise dependence forces y=x or x+1 (besides the excluded constants); the resulting polynomials are (x²+x+1)² and x⁴+x. Their roots belong to F4, whose intersection with an odd-degree binary field is F2. This also proves absence of diagonal zeros and hence evenness of every restricted ordered solution count.

The normal-form correspondence can be checked without invoking an earlier report. Given a zero, put rho=sqrt(xy). Its equation is rho⁴+rho²+(x+y)²+1=0; unique square roots imply x+y=rho²+rho+1. Substitution gives G(x,rho)=x²+x(rho²+rho+1)+rho²=0. Conversely G=0 and y=x+rho²+rho+1 imply xy=rho² and then F=0. Thus the correspondence includes every affine zero.

The homogenized cubic and all three partial derivatives in the note are correct. The condition XT=0 indeed excludes every projective singularity, over the algebraic closure as well as over K. Its infinity locus consists of precisely the two stated rational points.

More directly, expanding Y=(x+1)rho+1 gives

    Y²+xY+x³+1=(x+1)G(x,rho).

For x unequal to 1, division by x+1 is legitimate and supplies the inverse. At x=1, G=rho, mapping its sole point to (1,1); the omitted elliptic-curve points are exactly (1,0) and O. Therefore N=#E(K)-2 is exact, without relying on a generic birational-point-count assertion. The Weierstrass curve E:Y²+xY=x³+1 is nonsingular (normalized discriminant 1).

Hasse's bound applies in characteristic two and gives N<=q-1+2sqrt(q). I checked the statement and displayed proof of Theorem 7.3 in [Sutherland, MIT 18.783 Lecture 7](https://math.mit.edu/classes/18.783/2023/LectureNotes7.pdf). The subsequent arguments use only this imported finite-field bound and the explicitly verified correspondences.

## Averaging with 1 included

For n=2r+1, k=r+1, quotienting by F2*1 gives uniform r-dimensional subspaces in dimension 2r. Every nonexceptional zero contributes an independent pair in this quotient. Its inclusion probability is exactly

    p=((a-1)(a-2))/((a²-1)(a²-2)),  a=2^r.

This follows by incidence counting of ordered independent pairs; independence between different zeros is unnecessary. At r=1, p=0, and the argument remains valid.

The identity

    2(a²-1)(a²-2)-(2a²+3a-1)(a-1)(a-2)
      =3(a-1)²(a+2)>0

is correct. Hasse and 2sqrt(2)<3 therefore imply E[N_V]<4. Every count is even and at least two, proving existence of a qualifying V for every odd n>=3.

## Optional averaging with 1 excluded

Section 10 correctly changes the conditional population. Every nonexceptional pair has independent x,y and 1 outside their span. With q=2a² and b=2a, unconditional containment probability is (b-1)(b-2)/((q-1)(q-2)). Conditional on containing their two-dimensional span, the probability of excluding 1 is (q-b)/(q-4); unconditionally it is (q-b)/(q-1). Dividing gives

    p_excl=(b-1)(b-2)/((q-2)(q-4))
          =(2a-1)/(2(a+1)(a²-2)).

Both exceptional zeros disappear because 1 is excluded. The stronger exact-count Hasse bound yields N-2<=2a²+3a-3. The identity

    4(a+1)(a²-2)-(2a²+3a-3)(2a-1)=a-11

is correct. For a>=16, equivalently odd n>=9, the expected count is strictly below two. Even nonnegative counts then force an empty restricted zero set. No claim for the smaller omitted n follows from this particular estimate.

## Target and degree scope

The point R=(1,0) has order four: characteristic-two doubling gives 2R=(0,1), a nonidentity point equal to its inverse. The theorem is consequently within the unrestricted fixed-m=2 family but supplies no prime-order-target or generic-target statement. The two retained solutions in the first population use the coordinate zero. Removing that coordinate changes the allowed domain.

Since k cannot divide n=2k-1 for k>=2, the selected V cannot be the full subfield of dimension k. This excludes applicability of that particular constant-upper-bound theorem; it does not demonstrate hardness of these V.

For the two-solution family, a basis beginning with 1 makes the vanishing ideal explicit: all a_i,b_i for i>=2, together with a_1+b_1+1, plus Boolean field equations. Failure to derive one such linear generator at increasing caps, or checked closure codimension greater than two at increasing caps, would supply the missing LFD lower bound. The unsatisfiable population instead requires nonderivability of 1. Neither event is furnished by the counting argument.

The construction remains existential: lexicographically selecting a qualifying subspace defines a sequence after fixing field representations, but is not an efficient algorithm or an explicit closed-form basis. The bounded-positive-count transfer with M=2 has the stated constants; it transfers a lower bound only after one has been established on one presentation.

No correction to the mathematical statements is required. Publication should retain the exact solution-count/existence label, the low-order-target qualification, and the independent outstanding closure-obstruction obligation.
