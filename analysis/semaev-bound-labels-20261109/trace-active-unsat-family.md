# An infinite trace-active unsatisfiable existence family

Date: 2026-11-09. Derived source-only result, pending independent review. No experiment, search run, compilation or cloud job. This note strengthens the optional unsatisfiable averaging observation in `low-solution-count-family.md` by excluding trace-zero subspaces. It does not establish any growing LFD lower bound, nor exclude all degree-two refutations.

## 1. Scope

Use the same fixed normalized Semaev parameters

 K=F_(2^n), n odd, k=(n+1)/2, z=a6=1,
 F(x,y)=x²y²+xy+x²+y²+1,
 E:Y²+xY=x³+1.

For infinitely many odd n>=3, there exists a k-dimensional F2-subspace V with

 1 not in V,
 Tr_(K/F2)|V nonzero,
 no zeros of F in V².

The target z=1 corresponds to a point of order four on E, as documented in the companion note. This is not a prime-order-target theorem. Subspace selection remains existential or lexicographically defined by finite exhaustive search; no efficient basis formula is supplied.

The extra trace condition excludes the immediate contradiction Tr(x+y)+1=1 that occurs for V contained in ker Tr. It does not prove that every other degree-two combination fails to refute the system.

## 2. Why the earlier easy UNSAT population is insufficient

The optional Section 10 of `low-solution-count-family.md` averaged over V with 1 not in V. That population includes subspaces contained in ker Tr. Because n is odd, Tr(1)=1, and for such V the original trace consequence is the constant 1. Those systems refute at degree two. Therefore that easy UNSAT existence argument should be treated only as a capacity/counting sanity check, not evidence of hardness.

The calculation below removes this particular easy subfamily before applying the probabilistic method.

## 3. Exact fraction of trace-zero subspaces

Let q=2^n, b=2^k, and choose V uniformly among k-dimensional subspaces conditioned on 1 not in V. Since Tr(1)=1, any V contained in the hyperplane H0=ker Tr automatically satisfies 1 not in V.

Among all k-subspaces of an n-dimensional binary space,

 Pr(V subset H0)=(2^(n-k)-1)/(2^n-1),
 Pr(1 not in V)=(2^n-2^k)/(2^n-1).

The first formula is the ratio of Gaussian binomial coefficients [n-1 choose k]_2/[n choose k]_2; the second follows by counting nonzero vectors in a uniform subspace. Dividing gives

 Pr(V subset H0 | 1 not in V)=1/b.

Put n=2r+1, a=2^r, so q=2a² and b=2a. The trace-zero fraction is exactly 1/(2a), not an asymptotic approximation.

## 4. Conditional solution-count expectation

Let N be the number of full-field ordered zeros. The direct Weierstrass correspondence in the companion note proves

 N=#E(K)-2=q-1-t_n,

where t_n is the Frobenius trace over F_(2^n).

Every zero other than (0,1),(1,0) has 1,x,y F2-linearly independent, and the exceptional two are absent when 1 not in V. The exact inclusion probability for any remaining zero is

 p_excl=(2a-1)/(2(a+1)(a²-2)).

Thus over the population conditioned only on 1 not in V,

 E_0[N_V]=(q-3-t_n)p_excl.

Every trace-zero subspace contributes N_V=0. Conditioning further on trace being nonzero therefore gives

 E_active[N_V]=E_0[N_V]/(1-1/(2a))
             =a(N-2)/((a+1)(a²-2)).

This conditioning argument uses only the exact zero contribution of the removed subfamily. It does not assume independence between trace activity and the solution count.

## 5. A sufficient Frobenius-trace condition

If t_n>=0, then E_active[N_V]<2 for every a>=2.

Using the simplified expectation from Section 4, it suffices to check

 a(2a²-3-t_n) < 2(a+1)(a²-2).

The difference of right and left sides is

 2a²-a-4+a*t_n.

For a>=2 the first part is positive: at a=2 it equals 2, and it increases thereafter. The last term is nonnegative when t_n>=0. Thus the expectation is strictly below two.

There are no diagonal F-zeros for odd n. Therefore every N_V is an even nonnegative integer. An expectation below two implies that at least one trace-active V in this population has N_V=0.

## 6. Infinitely many odd extensions have t_n>0

The curve E over F2 has exactly four rational points: O, (0,1), (1,0), (1,1). Hence its base Frobenius trace is t_1=2+1-4=-1. Its Frobenius eigenvalues are the roots of

 T²+T+2,

namely alpha=(-1+i sqrt(7))/2 and its complex conjugate. Write alpha=sqrt(2) exp(i theta). Over F_(2^n),

 t_n=alpha^n+conj(alpha)^n=2*2^(n/2) cos(n theta).

Equivalently these integer traces satisfy t_0=2, t_1=-1, and t_n=-t_(n-1)-2t_(n-2).

The angle theta/pi is irrational. Indeed

 exp(2i theta)+exp(-2i theta)=-3/2.

If exp(2i theta) were a root of unity, its sum with its inverse would be an algebraic integer. A rational algebraic integer is an integer, contradicting -3/2. Thus theta/pi is irrational.

The sequence (2r+1)theta modulo 2pi is an irrational rotation orbit, hence dense in the circle. In particular it visits the open set where cosine is positive infinitely often. For those infinitely many odd n=2r+1, t_n>0, so Section 5 provides a trace-active unsatisfiable V.

The density fact can be obtained by the elementary pigeonhole proof for irrational rotations: arbitrarily small nonzero multiples modulo 1 give arbitrarily fine orbit meshes; translation by the initial angle preserves density. No statistical equidistribution assumption is required.

The standard Frobenius-extension trace formula is the sole arithmetic input beyond the companion point-count theorem. Primary references: Andrew Sutherland's MIT 18.783 Lecture 7, Theorem 7.3 and Frobenius discussion, https://math.mit.edu/classes/18.783/2023/LectureNotes7.pdf ; CTNT *Curves over Finite Fields*, Frobenius/Tate-module discussion, https://ctnt-summer.math.uconn.edu/wp-content/uploads/sites/1632/2020/06/Notes__Curves_over_Finite_Fields_Final.pdf . Both were opened in this source-only proof round. The exact counting of E(F2), irrationality calculation and averaging algebra are derived explicitly here.

## 7. What this does and does not furnish

This is an infinite existential family satisfying the correct fixed-m=2 diagonal dimension and avoiding the single constant trace refutation. It does not supply an explicit efficiently computable basis sequence, a certificate of nonmembership in W_D, or any positive lower bound growing with n. Other degree-two or degree-three refutations may still exist on every selected V.

A complete unboundedness proof must impose an additional growing full-closure obstruction simultaneously with this unsatisfiability condition. The expectation argument does not control that event. A lexicographically first V satisfying only the conditions above could systematically select easy instances; it is not justified to assume otherwise.
