# Candidate proof for review

All degrees here refer to multilinear representatives in B=F_p[A,B]/(T^2-T)
unless the ordinary polynomial ring is stated. Set r=floor(s/2), delta=4,
D=r+3, N=2s. The corresponding graded algebra is
A=F_p[A,B]/(T^2). The exact top of f is 4 e2(w_i A_i) e2(w_i B_i), w_i=2^i.
It follows by expanding S3(x,y,z): only x^2*y^2 has total unknown degree four;
the other terms have unknown degree at most three. All weights and 4 are units.

## 1. Injectivity of low-degree top multiplication

In one s-variable square-zero block, multiplication by e2 on homogeneous
degree j has matrix the inclusion map from j-subsets to (j+2)-subsets.
For j<r, 2j+2<=s. Wilson's rank formula, reproduced with proof as Theorem 4.1
of Frankl 1990, gives full column rank: its diagonal factors are
binom(j+2-i,2), 0<=i<=j; their factors are nonzero modulo p since p>s.
Diagonal rescaling handles all nonzero weights. In the tensor product of
two blocks, on a bihomogeneous piece (i,j) with i+j<r both block maps are
injective. Their tensor product is injective over a field. Distinct source
bidegrees have distinct image bidegrees. Thus multiplication by f_top is
injective on every homogeneous total degree <r.

Consequently, every nonzero h of degree <=r-1 satisfies
    deg(NF(h*f)) = deg(h)+4.
This statement uses the associated-graded product, not multiplication of
the top forms in the idempotent function algebra.

## 2. A fully closed space, not a plain-Macaulay lower-bound inference

Let U={NF(h*f): deg(h)<=D-4=r-1}. It is a linear space of dimension
sum_(j=0)^(r-1) binom(N,j), by the previous injectivity.
It contains f. If g=NF(h*f) in U has degree <=D-1 and g!=0, the degree identity
forces deg(h)<=r-2. Thus NF(T*g)=NF(NF(T*h)*f) is again in U for every digit
variable T. The zero case is immediate. This proves FULL closure on every
low-degree combination. Hence W_D subset U. Conversely every monomial
cofactor of degree <=D-4 can be applied to f at cap D one variable at a time,
so U subset W_D. Therefore W_D=U exactly.

## 3. A missing ideal consequence exists, even on SAT inputs

For any fixed digit value x, S3(x,Y,z) has at most two roots in Y. If x!=z its
quadratic coefficient is (x-z)^2. If x=z=t, it is
    -4*c(t)*Y + c'(t)^2 -8*t*c(t),  c(T)=T^3+a*T+b.
When c(t)!=0 it is nonzero linear. When c(t)=0 its constant is c'(t)^2!=0
by nonsingularity. Thus it is never identically zero. The digit maps are
injective because 2^s<=p, so the Boolean zero set has at most 2^(s+1) points.

The codimension of W_D in B_<=D is
    sum_(j=r)^min(r+3,2s) binom(2s,j),
which is greater than 2^(s+1). It suffices to use the first two summands.
For s=2r, binom(4r,r)>=4^r and the ratio of the next binomial to it is
3r/(r+1)>=3/2, giving a sum >=(5/2)4^r>2^(s+1).
For s=2r+1, binom(4r+2,r)>=(4+2/r)^r>=(3/2)4^r by Bernoulli,
and the next ratio (3r+2)/(r+1)>=5/2, giving sum >=(21/4)4^r>2^(s+1).
Here r>=1, so all inequalities include s=2,3.

Evaluation of B_<=D on the Boolean zero set has rank at most its cardinality.
The generated Boolean ideal is its vanishing ideal, by assignment indicators.
Thus its degree-at-most-D part has codimension at most 2^(s+1), strictly less
than W_D. There is an ideal consequence q of degree <=D absent from W_D.
The ordinary/Boolean bounded-closure bridge with explicit bit equations
therefore gives q absent from V_(F,D), proving d_F>=D+1=4+r.
This does not use a first-fall-to-last-fall heuristic.

## 4. Uniform upper bound and solving-degree link

For any N-variable system of normalized Boolean inputs with all bit equations,
W_(N+1) is the full Boolean ideal: every representative has degree <=N, so
all variable products are permitted at cap N+1. Lifting its elements by the
bounded Boolean repair identities and normalizing arbitrary higher-degree
ideal consequences at their own degrees gives d_F<=N+1.

For a degree-compatible order the initial ideal contains every T_i^2.
A minimal monomial generator is either a square T_i^2 or squarefree;
therefore every reduced Groebner basis element has degree <=max(N,2).
Caminata--Gorla Theorem 3.1 gives sd=max(d_F,maxGBdegree), hence
    d_F <= sd <= N+1=2s+1.
This uses the stated mathematical solving-degree convention, not an arbitrary
F4 run's maximum degree under arbitrary selection or Boolean preprocessing.

The raw and normalized S3 generators differ by bit-equation consequences
available at cap four, so their ordinary V_D agree for D>=4. All caps used in
the lower and upper proof are at least four. The same sandwich follows for
both generating presentations.

## 5. Nonvacuity and scope

For any s choose a prime p>=max(2^s,37); the curve y^2=x^3+x+1 is nonsingular
because its discriminant factor is 31. It has the rational point P=(0,1);
2P is affine since P is not two-torsion. Its abscissa z=1/4 gives a rational
target and a SAT digit input (X,Y)=(0,0). This constructs actual fixed-degree
families for arbitrarily growing s without assuming curve/group-order hardness.
The result does not require special j, a planted target, or UNSAT, although
this elementary nonvacuity example uses a known decomposition. It is about
the specified polynomial systems, not discrete-log complexity or all encodings.

No characteristic-two growing lower bound follows: multiplication by e2 in
a square-zero algebra of characteristic two is not covered by the same
full-rank argument. Binary growth and its full formal upper-bound proof remain
separate obligations. This document is a candidate for independent review,
not a scientific-status transition or a complete Lean formalization.
