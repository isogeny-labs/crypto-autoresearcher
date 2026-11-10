# An infinite fixed-m=2 Semaev family with exactly two solutions: existence proof

Date: 2026-11-09. Source-only derivation using finite-field algebra, subspace counting and Hasse's theorem. No random sampling, solver run, compilation or cloud job occurred. This establishes the existence of bounded-positive-solution-count families outside the previously bounded full-subfield class. It does **not** establish growing LFD.

## 1. Result and precise constructive status

For every odd n=2r+1>=3, put K=F_(2^n) and k=r+1=ceil(n/2). There exists an F2-subspace V of K of dimension k, containing 1, such that the normalized m=2 Semaev equation with

 z=1, a6=1,
 F(x,y)=x²y²+xy+x²+y²+1=0, x,y in V,

has exactly the two ordered solutions

 (x,y)=(0,1), (1,0).

This is a family of the exact normalized S3 systems, not an arbitrary quadratic encoding. One can take the original curve model y_curve²+x_curve*y_curve=x_curve³+1 (a2=0,a6=1); its nonsingularity follows from a6!=0, and x-coordinate z=1 is a rational target (curve ordinates 0 and 1).

The proof is existential by averaging over all V containing 1. It does not supply a closed formula for a basis V_n or an efficient algorithm for finding one. A mathematically definite computable sequence can be specified by fixing a canonical field representation and choosing the lexicographically first qualifying subspace, but evaluating that specification may require exhaustive search. No such subspace search was run here.

These V are not full subfields: k=(n+1)/2 cannot divide odd n>=3, because k divides n only if it divides 2k-n=1. Consequently the earlier constant LFD<=3 theorem for a full quadratic-extension subfield does not apply.

## 2. Only two solutions have dependent coordinates relative to 1

Let (x,y) be a full-field zero of F. If x=0, then y²+1=0, hence y=1. If x=1, then F(1,y)=y, hence y=0. By symmetry the same handles y in F2.

Now assume x not in F2 and dim_F2 span{1,x,y}<=2. Then y is one of 0,1,x,x+1. The first two cases have already been excluded.

- If y=x, then F(x,x)=x^4+x²+1=(x²+x+1)². Its roots lie in F4\F2. An odd-degree binary extension contains no F4, so this case is impossible.
- If y=x+1, then F(x,x+1)=x^4+x. The roots lie in F4, whose intersection with K is F2; this contradicts x not in F2.

Therefore the only full-field zeros with dependent {1,x,y} are (0,1) and (1,0). Every other zero spans a three-dimensional F2 space together with 1.

There are no diagonal zeros anywhere in K. Because the equation is symmetric, the number of ordered zeros inside any V is therefore even. Every V containing 1 has at least the displayed two zeros.

## 3. Full-field zero count is controlled by a smooth cubic

For a full-field zero, let rho=sqrt(xy). The normal-form identities specialize to the exact bijection

 (x,y) <-> (x,rho),
 y=x+rho²+rho+1,
 G(x,rho)=x²+x(rho²+rho+1)+rho²=0.

The forward inverse identities from `inside-subfield-next-obligation.md` prove this correspondence on all finite zeros, with no exceptional denominator or missing affine point.

Homogenize G to the plane cubic

 C(X,R,T)=X²T+XR²+XRT+XT²+R²T.

Its partial derivatives in characteristic two are

 C_X=R²+RT+T²,
 C_R=XT,
 C_T=X²+XR+R².

There is no simultaneous projective zero of these derivatives. Indeed C_R=0 forces X=0 or T=0. If T=0, C_X=R² forces R=0 and then C_T=X² is nonzero at a projective point. If X=0, C_T=R² forces R=0 and then C_X=T² is nonzero. Thus C is geometrically smooth. A smooth plane cubic has genus one, and C has rational points, including [1:0:0]; it is an elliptic curve after choosing such a point as origin.

The points at infinity are exactly [1:0:0] and [0:1:0], both K-rational. If N is the number of full-field ordered zeros of F, the bijection above gives

 N=#C(K)-2.

Hasse's theorem therefore yields

 N <= 2^n-1+2 sqrt(2^n).

For the averaging inequality below it is enough to use the slightly weaker bound N<=2^n+1+2 sqrt(2^n).

Primary source checked for the precise finite-field bound: Andrew Sutherland, MIT 18.783 Lecture 7 (2023), Theorem 7.3, https://math.mit.edu/classes/18.783/2023/LectureNotes7.pdf . The theorem and its proof were opened and read. Smoothness and the point correspondence above are derived here; no empirical point count is used.

## 4. Exact subspace-containment probability

Choose V uniformly among all k-dimensional F2-subspaces of K containing 1. Quotienting by the line F2*1 gives a uniformly random r-dimensional subspace of a 2r-dimensional binary vector space.

For every nontrivial full-field zero (x,y), the images of x,y in K/F2 are independent by Section 2. The probability that both lie in V is therefore

 p_r=((2^r-1)(2^r-2))/((2^(2r)-1)(2^(2r)-2)).

This is the standard exact containment probability for a fixed ordered independent pair in a uniformly random subspace: the ratio of the counts of ordered independent pairs in dimensions r and 2r. It also follows by counting pairs (subspace,contained independent pair) in two ways. At r=1 the numerator is zero, as it should be.

Let N_V count the ordered solutions in V². By linearity of expectation, without assuming independence among different solution pairs,

 E[N_V]=2+(N-2)p_r.

## 5. The expectation is below four

Put a=2^r>=2, so q=2^n=2a². Define

 A=(a-1)(a-2)=a²-3a+2,
 B=(a²-1)(a²-2)=a^4-3a²+2,
 p_r=A/B.

Using the weaker Hasse bound from Section 3 and 2 sqrt(2)<3,

 N-2 <= 2a²-1+2 sqrt(2)*a <= 2a²+3a-1.

Consequently

 E[N_V] <= 2+((2a²+3a-1)A)/B <4.

The strict final inequality is elementary:

 2B-(2a²+3a-1)A = 3(a-1)²(a+2)>0.

Every N_V is an even integer at least two. If every V had at least four solutions, the expectation would be at least four. Therefore some V has exactly two solutions. This proves the result for every odd n>=3, without a sampling experiment or an asymptotic heuristic.

## 6. What this adds to the lower-bound program

The family has uniformly bounded positive solution count M=2, so the one-bit SAT-transfer theorem applies with b(M)=2. For the corresponding original and normal-form presentations,

 d_F <= max(d_G,2)+2,
 d_G <= max(d_F,3).

Thus if growing LFD can be proved on either presentation along a qualifying sequence of V, it transfers to the other. This removes the growing-solution-count obstruction present in the unrestricted full-subfield case.

The ideal is especially concrete. Choose a V basis with first element 1, and write x=a_1+sum_(i>=2) a_i v_i and y=b_1+sum_(i>=2) b_i v_i. For a qualifying V, the entire Boolean solution set is the affine line

 a_i=b_i=0 (i>=2), a_1+b_1+1=0.

Its vanishing ideal is generated by these affine-linear polynomials and the Boolean field equations. Therefore a degree-D lower bound can be witnessed by failure to derive at least one of these known linear ideal generators in W_D. Alternatively, a full-closure codimension bound greater than two suffices. One no longer needs a separate unknown exact-solution count for the mathematically selected family; the remaining problem is its derivation degree.

This is not evidence that those linear generators are hard to derive. It remains possible that every qualifying V admits a small-degree derivation. The averaging argument controls the solution set, not the saturated closure, and no monotonic relationship between fewer solutions and larger LFD is assumed.

## 7. Remaining explicit obligations

1. Independently review the smooth-cubic correspondence, the dependent-pair classification, and the exact probability calculation.
2. Find a structural, efficiently describable sequence of qualifying V, or strengthen the averaging argument to impose a growing-degree closure obstruction simultaneously with N_V=2.
3. Construct a quotient map or dual closure certificate showing a named affine ideal generator is absent from W_D for D growing with n. The existing degree-five examples suggest possible mechanisms but do not establish this joint event.
4. Keep full-field point counts, restricted solution counts, and LFD certificates separate in any future implementation. A small solution count alone is not an LFD certificate.

No independent review or computational validation of the newly stated existence theorem is claimed in this note. No novelty claim is made.

## 8. Low-order target scope

The selected target x-coordinate z=1 on E:y²+xy=x³+1 is represented by R=(1,0). It has order four. The characteristic-two tangent formula has slope lambda=x+y/x=1 at R, giving x(2R)=lambda²+lambda+a2=0 and y(2R)=1. Thus 2R=(0,1), the nonidentity two-torsion point (its inverse (x,x+y) equals itself). Therefore R has order four.

This is a deliberate mathematical-family construction using a low-order target. It does not establish a bounded-count family for prime-order target subgroups or for uniformly random cryptographic targets. The two surviving decompositions involve the x=0 two-torsion coordinate. Removing that coordinate from an application factor base would change the polynomial-system domain; it is not part of this theorem. The fixed-m=2 Semaev family stated in the task allows these parameters, but any narrower target/subgroup requirement must be declared separately.

## 9. A direct Weierstrass point-count check

The point-count step can also avoid importing a general plane-cubic genus formula. Define

 Y=(x+1)rho+1.

A direct identity is

 Y²+xY+x³+1=(x+1)G(x,rho).

Thus every affine G-zero maps to the nonsingular Weierstrass curve E:Y²+xY=x³+1. For x!=1 this map is invertible with rho=(Y+1)/(x+1). At x=1, G(1,rho)=rho, so its unique point rho=0 maps to (1,1); the other E-point (1,0) has no affine preimage. The point at infinity of E has no affine preimage either. Therefore this map proves directly

 N=#E(K)-2.

The original curve E has discriminant a6=1 in its normalized characteristic-two model, so Hasse's theorem applies directly to E. This independently checks the counting step used above and explains the two omitted points without any generic birational-point-count assumption.

Additional primary finite-field reference opened: CTNT Summer School, *Curves over Finite Fields*, Definition 1.1 and Exercise 2 for the smooth-cubic/genus-one conventions, https://ctnt-summer.math.uconn.edu/wp-content/uploads/sites/1632/2020/06/Notes__Curves_over_Finite_Fields_Final.pdf . The direct map just given makes the averaging proof rely only on the verified normalized elliptic curve and Hasse's bound, rather than on a separate Artin–Schreier genus calculation.

## 10. Optional companion: an infinite unsatisfiable existence family

The same argument yields a complementary existence result, with care about the rank-one exceptional pairs. For odd n=2r+1>=9, there exists a k=r+1 dimensional V *not containing 1* for which F has no zero in V². This is again existential, not a basis formula or an LFD lower bound.

Choose V uniformly conditioned on 1 not in V. The two rank-one zeros (0,1),(1,0) are now absent. Every other zero has x,y independent and 1 outside their span. Let q=2a² and b=2a=2^k. Double counting gives its conditional inclusion probability

 p_excl=((b-1)(b-2))/((q-2)(q-4))
       =(2a-1)/(2(a+1)(a²-2)).

For completeness, start with unconditional containment probability p_2=(b-1)(b-2)/((q-1)(q-2)); conditioned on containing span{x,y}, the probability of excluding 1 is (q-b)/(q-4). The unconditional probability of excluding 1 is (q-b)/(q-1). Their ratio gives the displayed expression.

Using the stronger bound N=#E(K)-2<=q-1+2sqrt(q),

 E[N_V]=(N-2)p_excl
       <=(2a²+3a-3)(2a-1)/(2(a+1)(a²-2)) <2

whenever a>=16, since

 4(a+1)(a²-2)-(2a²+3a-3)(2a-1)=a-11>0.

All N_V are even nonnegative integers. An expectation below two therefore forces some V with N_V=0. The earlier positive-count theorem and this unsatisfiable theorem concern different conditional subspace populations; neither conclusion is obtained by ignoring the exceptional rank-one pairs.

This supplies an infinite pool with a proved existential unsatisfiability property, but it still supplies no growing closure obstruction. The relevant next joint-existence question is whether one can require N_V=0 (or N_V=2 in the first population) simultaneously with 1 not in W_D (or an absent linear vanisher) for D tending to infinity.

### Scope caution for optional Section 10

The optional UNSAT existence result includes trace-zero subspaces V contained in ker Tr_K. For odd n and a6=z=1 these have the immediate constant trace consequence 1, so that result alone is only a counting/capacity sanity check, not a hardness result. The separate `trace-active-unsat-family.md` excludes that subfamily on an infinite subsequence of odd n. It still supplies no growing LFD lower bound and does not exclude other degree-two refutations. The main exactly-two-solution theorem is unchanged.
