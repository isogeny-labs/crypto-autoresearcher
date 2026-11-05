# Rigorous last-fall and solving-degree bounds

5 November 2026. Written proofs below concern the exact stated generating
sets. New prime growing-family proof: see CLAIM.md and PRIME-PROOF.md and the
independent review. Kernel verification has the separate, narrower scope in
formal-status.md. No first-fall-to-solving-degree inference is used.

## Definitions and the normalization bridge

Let P=k[T_1,...,T_N], J=(T_i^2-T_i), B=P/J, and let NF denote the unique
multilinear representative. For an ordinary input set F containing J's
explicit generators, V(F,D) is the smallest k-linear space containing every
input of degree <=D and closed under multiplication when the sum of factor
degrees is <=D. The last fall degree is the least d such that every q in (F)
belongs to V(F,max(d,deg q)).

For normalized non-bit inputs define W_D inside B: contain eligible inputs,
close under linear combinations and T_i*w whenever deg(w)+1<=D. The ordinary
and quotient definitions agree:

    V(F,D)={q in P_<=D: NF(q) in W_D},  D>=2.

Here all non-bit inputs are multilinear. For raw inputs a sufficient extra
condition is D>=maximum raw input degree. This qualification matters.

Proof. Reducing a monomial m*T_i^a with a>=2 subtracts
m*T_i^(a-2)*(T_i^2-T_i), and lowers its degree. Iteration proves
q-NF(q) in V(J,deg q). Ordinary derivations project into W_D: split any
multiplier into monomials and apply variables successively, never exceeding
the sum of factor degrees. Conversely lift a quotient derivation by ordinary
multiplication, then subtract the just-proved bit repair. This establishes
both inclusions, including all low-degree combinations, not merely products
of literal inputs. At caps0,1 the statement follows from the affine spans.

## A general Boolean bound, including SAT systems

For N>=1 and normalized inputs with all bit equations, set U=W_(N+1).
Every multilinear representative has degree <=N. Thus every variable
multiplication of every element of U is permitted at cap N+1. Consequently U
is an ideal of B containing the inputs; conversely all its derivations are
ideal consequences. Hence U is exactly the generated Boolean ideal.
If q is an ordinary ideal consequence, NF(q) is in U and its multilinear
lift lies in V(F,N+1). Repair q at its own degree and use monotonicity to get

    q in V(F,max(N+1,deg q)),  hence d_F<=N+1.

For raw inputs the same proof gives d_F<=max(N+1,d_raw,2), provided their
normal forms are the intended inputs. For N=0 use the direct constant case.

Let sigma be degree compatible and use Caminata--Gorla's iterated Macaulay
solving degree. Since the initial ideal contains every T_i^2, any minimal
monomial generator is either one of these squares or squarefree: every other
nonsquarefree monomial has a square as a proper divisor. Thus a reduced
Groebner basis has degree at most max(N,2). Theorem3.1 of Caminata--Gorla gives

    sd_sigma(F)=max(d_F, maximum reduced-GB degree).

In particular for normalized inputs N>=1,

    d_F<=sd_sigma(F)<=N+1.

On an UNSAT Boolean system the ideal is the unit ideal and its reduced GB is
{1}; therefore sd_sigma(F)=d_F. These assertions are about the stated
mathematical solving-degree convention, not every possible F4 implementation
or an execution that changes generators by implicit preprocessing.

## Binary support-aware localization, with the complete degree accounting

Work over F2. Let b=(b_1,...,b_s) be base bits, t arbitrary auxiliary bits,
and p_i(b,t) multilinear and affine in the entire tuple t. Let A_i be the
base-variable support, s_i=|A_i|. Assume the p_i have been derived in ordinary
V(F,D), all bit equations belong to F, and

    D>=max(2,s+1,max_i(s_i+2)).

If no Boolean (b,t) satisfies every p_i, then 1 is in V(F,D).

Proof. For a fixed full base assignment a let

    delta_(a,A)=product_(j in A) [b_j if a_j=1, else (1-b_j)].

Start with p_i and multiply by the factors for A_i one at a time, taking NF
after EACH multiplication. Every intermediate multilinear row is affine in
t and supported on at most s_i base bits, so has degree at most s_i+1. Each
next ordinary product has degree at most s_i+2, within D; the normalization
repair also fits D. At the end the exact multilinear polynomial is

    delta_(a,A_i)*p_i(a,t).

This identity follows by evaluating its base coefficients at every Boolean
base assignment, using uniqueness of multilinear interpolation, with t left
as indeterminates. Multiplying by the complementary indicator is allowed:
the sum of factor degrees is at most (s_i+1)+(s-s_i)=s+1. This derives the
FULL localized row delta_a*p_i(a,t), rather than assuming its derivability.

The affine system p_i(a,t)=0 is inconsistent over F2, since an affine
solution over F2 would give a Boolean full solution. Gaussian elimination
therefore supplies constant coefficients lambda_(a,i) such that
sum_i lambda_(a,i)*p_i(a,t)=1. Their same linear combination of derived rows
is delta_a. Summing over a uses the exact polynomial identity

    sum_a delta_a = product_j [b_j+(1-b_j)] = 1.

Thus 1 is derived at D. Multiplying this constant by any polynomial q at cap
max(D,deg q) proves the full last-fall upper bound; it does not just prove a
single low-degree consequence. Unit-ideal solving degree equals last fall.
The proof can use 2^s fibres and makes no proof-size bound.

The characteristic-two restriction on affine-fibre inconsistency is
essential. Over an odd field, an affine system can have solutions while
having no Boolean solutions, so the same inference would be false.

## Exact binary two-S3 presentation

Let K=F_(2^n), ell>=1. Use three disjoint ell-bit linear forms x,y,z over K,
one full n-bit linear form u and optional independent n-bit v. Fix r,a6 in K.
Use all F2 coefficient equations of

    S3(x,y,u)=0, S3(u,z,r)=0,
    optional v*(x+y)+1=0,
    S3(A,B,C)=(A*B+A*C+B*C)^2+A*B*C+a6,

and ALL explicit bit equations. Raw equations have degree <=4. With
L^[2]=sum_j c_j^2*B_j for L=sum_j c_j*B_j, their normal forms are

    x^[2]*y^[2]+(x^[2]+y^[2])*u^[2]+x*y*u+a6,
    (z^[2]+r^2)*u^[2]+r*z*u+r^2*z^[2]+a6,
    optional v*(x+y)+1.

They are affine in all u,v bits. Base supports are at most 2ell, ell and
2ell. The preceding lemma applies with s=3ell and

    D=max(4,3ell+1,2ell+2)=3ell+1.

Consequently every UNSAT input in this EXACT presentation satisfies

    d_F=sd_sigma(F)<=3ell+1.

This holds with or without the guard, for raw or normalized inputs, and
independently of n. Rational-lift and nonsingularity hypotheses are needed
for some relation interpretations, but are not needed for this syntactic
upper bound. Extra nonlinear auxiliary relations require a fresh proof.
For SAT inputs the general bound still applies, with N=3ell+n or3ell+2n.

The two-block binary m=2 system with 2k bits and one fixed target is affine
in either block after Boolean normalization (it is quadratic overall).
The same lemma with s=k proves UNSAT d_F=sd_sigma(F)<=k+2 for NORMALIZED
inputs. Raw inputs give <=max(4,k+2). This distinction includes k=1 and
prevents an invalid small-cap transfer.

## What now grows, and the exact open boundary

PRIME-PROOF.md constructs, for every s>=2, fixed-degree-four prime digit
systems with explicit bit equations satisfying

    4+floor(s/2)<=d_F<=sd_sigma(F)<=2s+1.

It treats both SAT and UNSAT, and provides an infinite SAT rational-target
family. It gives no characteristic-two growing lower bound. There the top
form and inclusion-matrix argument are different; the prime proof cannot be
transferred by changing coefficient fields. The binary support lemma and complete raw two-S3 coefficient-descent
instantiation now compile in Lean: BinaryLocalization.lean and
BinaryCoefficientDescent.lean. BINARY-FORMAL.md names the exact final theorem,
which derives every structural and degree condition from the source forms.
The prime growth theorem remains a written proof; a growing binary lower
bound is still a separate open obligation. Broader whole-workspace checks
hit an existing rank-certificate resource failure; scoped new-module checks
are reported separately in formal-status.md.

## Sources, read and scope

- Internal, read: analysis/boolean-fall-certificates-20261104/THEORY.md,
  ordinary/quotient bridge and SAT missing-consequence argument.
- Internal, read: analysis/semaev-m2-last-fall-degree/theorem-dossier.md,
  Theorem2.5 and normalized conventions.
- Internal, read: sibling crypto research/guarded_fall_degree_20261028/
  extensions/characteristic_two/boolean_upper_bound.txt, full two-S3 proof.
- Retrieved primary: Caminata--Gorla, arXiv:2112.05579v2, Theorem3.1 and
  definitions; independent review checks exact convention and hypotheses.
- Retrieved primary in earlier review: Semaev arXiv:1504.01175; Kosters--Yeo
  arXiv:1503.08001; Huang--Kosters--Yang--Yeo arXiv:1505.02532. These supply
  context, not an asserted literature proof of this particular new sandwich.
- Frankl1990 inclusion-rank theorem is contextual; the independent review
  supplies an elementary induction for the precise needed rank claim.
