# An unbounded last-fall lower bound for fixed-degree prime digit S3 systems

5 November 2026. A self-contained written derivation of the mathematical
claim frozen in CLAIM.md. Semantic review is in prime-independent-review.md;
formal-status.md distinguishes the Lean-checked components. No novelty,
scientific-status transition, or complexity claim is made.

## The exact statement

Let s>=2, p>3 prime, B=2^s<=p. Let
E/F_p: y^2=x^3+a*x+b be nonsingular, that is 4*a^3+27*b^2!=0, and z in F_p.
With 2s independent bit variables A_i,B_i, put

    X=sum_(i=0)^(s-1)2^i*A_i, Y=sum_(i=0)^(s-1)2^i*B_i,
    S3(X,Y,z)=(X-Y)^2*z^2
      -2*((X+Y)*(X*Y+a)+2*b)*z+(X*Y-a)^2-4*b*(X+Y),
    f=NF(S3(X,Y,z)),
    F={f} union {T^2-T : every one of the 2s bit variables}.

For every degree-compatible monomial order sigma, and the iterated Macaulay
solving degree of Caminata--Gorla, one has

    4+floor(s/2) <= d_F <= sd_sigma(F) <= 2s+1.                (1)

The same bounds hold with raw S3 in place of f. Both input presentations have
non-bit degree exactly four. The statement includes SAT inputs; no asserted
UNSAT distribution or first-fall-to-last-fall inference is needed.

## 1. Elementary inclusion-matrix lemma

For n>=2j+2, let coefficients c_S in a field of characteristic zero or prime
p>j+2 be indexed by j-subsets of [n]. If

    sum_(S subset T, |S|=j) c_S=0 for every (j+2)-subset T,   (2)

then all c_S=0.

Proof by induction on j. If j=0 every equation is c_empty=0. For j>=1 fix
distinct indices a,b. Subtract (2) for T=R union{a} and T=R union{b}, where
R ranges over (j+1)-subsets avoiding a,b. The terms lying wholly in R cancel,
leaving

    sum_(H subset R, |H|=j-1) (c_(H union{a})-c_(H union{b}))=0.

The induction hypothesis applies on n-2 indices, because
n-2>=2(j-1)+2 and p>j+2>(j-1)+2. Hence every displayed coefficient difference
vanishes. Adjacent j-subsets differ by precisely one exchanged index, and
the graph of such exchanges is connected. All c_S therefore equal c.
Equation(2) gives binom(j+2,2)*c=0. This binomial is nonzero because p>j+2
(and in characteristic zero). Thus c=0. This proves the lemma without a
rank-formula assumption. The lemma is also a special case of the classical
inclusion-matrix rank theorem recorded by Frankl1990.

## 2. No degree falls before a controlled cap

Let N=2s, r=floor(s/2), D=r+3, and work in the filtered Boolean algebra
B=F_p[A,B]/(T^2-T). Its associated graded algebra is square-zero:
A=F_p[A,B]/(T^2). Since p>3 and weights w_i=2^i are nonzero, the degree-four
component of f is exactly

    f_4=4*e2(w_i*A_i)*e2(w_i*B_i).                          (3)

All other S3 terms have degree at most three in these unknowns. In a single
s-variable square-zero block, multiplying a homogeneous degree-j form by
e2 has the inclusion matrix in section1. Nonzero weights are removed by
diagonal scaling (scale a subset column by product_(i in S)w_i and a row by
product_(i in T)w_i). For j<r we have s>=2j+2 and p>j+2, so this map is
injective. The last inequality follows from p>=2^s and s>=2.

For a bihomogeneous source piece of bidegree(i,j) and i+j<r, both block
multiplications are injective. Their tensor product over a field is
injective. Different source bidegrees have different image bidegrees.
Multiplication by f_4 is therefore injective on every homogeneous component
of total degree <r. Taking the leading component of any nonzero Boolean h
of degree <r proves the exact degree identity

    deg NF(h*f)=deg h+4.                                  (4)

This is an associated-graded argument; treating the idempotent quotient as
homogeneous would be incorrect.

## 3. Compute the entire iterated bounded closure

Let W_D use the strict variable-multiplication convention of BOUNDS.md and
set U={NF(h*f):deg h<=r-1}. Identity(4) shows that the multiplication map is
injective, so dim U=sum_(j=0)^(r-1)binom(N,j). It contains f.

If nonzero g=NF(h*f) in U has deg g<=D-1=r+2, (4) forces deg h<=r-2.
Then NF(T*g)=NF(NF(T*h)*f) belongs to U for every variable T. For r=1 there
is no such nonzero g, so closure is vacuous; the zero case is always immediate.
This proves every required multiplication of every low-degree combination.
Thus minimality gives W_D subset U. Conversely apply each monomial cofactor
of degree <=r-1 to f one variable at a time; the cap never exceeds
4+(r-1)=D. Their span gives U subset W_D. Consequently

    W_D=U, dim W_D=sum_(j=0)^(r-1)binom(2s,j).              (5)

Unlike a plain-Macaulay rank count, (5) explicitly rules out new mutant rows.

## 4. A missing ideal consequence, also for SAT systems

For each fixed x, S3(x,Y,z) has at most two roots in Y. When x!=z the
quadratic coefficient is (x-z)^2!=0. When x=z=t, put c(T)=T^3+a*T+b; then

    S3(t,Y,t)=-4*c(t)*Y+c'(t)^2-8*t*c(t).                  (6)

If c(t)!=0 this is nonzero linear. If c(t)=0, nonsingularity gives
c'(t)!=0 and it is a nonzero constant. There is no identically zero fibre.
The s-bit digit maps are injective since 2^s<=p. Hence the full Boolean zero
set Z satisfies |Z|<=2*2^s=2^(s+1).

By(5), codim(W_D in B_<=D)=sum_(j=r)^min(r+3,2s)binom(2s,j).
It exceeds 2^(s+1). To see this using only the first two summands:

- s=2r: binom(4r,r)>=4^r, and the next/first ratio is
  3r/(r+1)>=3/2. Their sum is >=(5/2)4^r>2^(s+1).
- s=2r+1: binom(4r+2,r)>=(4+2/r)^r>=(3/2)4^r by Bernoulli;
  the next/first ratio is (3r+2)/(r+1)>=5/2. Their sum is
  >=(21/4)4^r>2^(s+1). Here r>=1.

Evaluation of B_<=D on Z has rank <=|Z|. The Boolean ideal (f) is exactly the
kernel of evaluation on Z: the assignment indicators delta_a form a basis
of B; f*delta_a=f(a)*delta_a, so delta_a belongs to(f) precisely when
f(a)!=0. Thus (f) intersect B_<=D has codimension <=|Z|, strictly smaller
than that of W_D. There exists q in(f) of degree <=D outside W_D.

The ordinary/Boolean bounded-closure bridge sends q to an ordinary ideal
consequence outside V(F,D). If d_F<=D, the definition of last fall degree
would place q in V(F,max(d_F,deg q)) subset V(F,D), a contradiction. Therefore

    d_F>=D+1=4+floor(s/2).                                (7)

The finite upper bound proved next ensures the least last-fall cap exists;
no unproved finiteness premise is being used implicitly.

## 5. Upper bound, solving degree and raw input

At cap N+1 every Boolean representative has degree <=N and every variable
multiplication is allowed. W_(N+1) is therefore the full Boolean ideal.
Normalize any ordinary ideal consequence q, lift its derivation at N+1,
and repair q at its own degree. This proves d_F<=N+1, including SAT systems.
This upper bound and the original-degree repair are also proved generically
in BooleanNormalization.lean; see the precise formal statements and receipts.

Because T_i^2 belongs to the initial ideal, every minimal initial monomial
generator is either T_i^2 or squarefree. A reduced Groebner basis for any
degree-compatible order therefore has degree <=max(N,2). Combining this
with Caminata--Gorla Theorem3.1,

    sd_sigma(F)=max(d_F,maxGBdegree_sigma(F)),

proves(1). The input f has degree four by(3). The raw input also has degree
four; its difference from f is a bit-equation consequence available at cap
four. Ordinary bounded closures for the two presentations therefore agree
at all D>=4. The lower cap r+3 and upper cap N+1 used above are both >=4,
so the same sandwich applies to raw inputs.

## 6. An actual infinite SAT family with rational targets

For each s choose any prime p>=max(2^s,37). The curve y^2=x^3+x+1 has
nonzero discriminant since its discriminant factor is31. It contains
P=(0,1); the tangent slope there is1/2 and 2P has x-coordinate z=1/4.
With X=Y=0, S3(0,0,z)=1-4z=0, so all-zero digits give a SAT instance with
an affine rational target. This construction works for arbitrarily large s.
All non-bit input degrees stay four, whereas (7) tends to infinity.

The lower bound does not require this planted example; it holds for every
nonsingular curve and every z under the statement's hypotheses. The example
only proves that the rational-target SAT scope is nonempty at every width.
No discrete-log hardness, proof-size or attack-cost conclusion is claimed.

## 7. An infinite UNSAT family, also with rational targets

For each width s let B=2^s and choose a prime p>2*B^2+3. Set b=1,z=0.
The point R=(0,1) is rational on every curve y^2=x^3+a*x+1. For fixed digits
x,y in{0,...,B-1}, the equation

    S3(x,y,0)=(x*y-a)^2-4*(x+y)=0

excludes at most two choices of a. All B^2 pairs together exclude at most
2*B^2 choices. The singularity equation 4*a^3+27=0 excludes at most three
more. Since p>2*B^2+3, choose any remaining a (the least residue is a
deterministic rule). The curve is nonsingular and the exact digit system
has no Boolean solution. It still has an affine rational target R.
Thus for every width there are actual UNSAT presentations with

    4+floor(s/2)<=d_F=sd_sigma(F)<=2s+1.

This is an existence/counting proof with a finite deterministic parameter
selection rule, not a claimed efficient curve-construction algorithm or
an experimental result. It does not change the universal theorem's scope.

## Precise boundary

This proves growth for F_p-coefficient digit systems. It neither proves the
characteristic-two analogue nor covers extra chain, carry, membership or
sign generators: adding inputs can lower the bounded closure degree.
The full theorem above is a written theorem with independent source review,
not a full Lean formalization. BOUNDS.md supplies the separate binary UNSAT
upper bound, and formal-status.md names every verified and unverified joint.
