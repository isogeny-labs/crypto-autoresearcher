# A uniform cap-four derivation for the no-wrap polynomial-subspace family

2026-11-09. Source-only proof; no solver execution, measurements, native builds, or cloud jobs. This note supersedes the open uniform-cap question for this particular family in `no-wrap-coefficient-progress.md`, subject to independent proof review.

## Scope and statement

Let K=F2[t]/P(t), with P irreducible of degree n>4r, let V=span(1,t,...,t^r), and take z=a6=1. Let F_r be the Boolean coefficient descent of S3(x,y,1)=(xy)^2+xy+(x+y+1)^2. Use the strict filtered closure W_D, allowing products of a derived polynomial of degree at most D-1 by a variable and linear combinations. Then

**Theorem. Every affine generator of the two-point solution ideal is in W_4(F_r), and d_F(F_r)<=4.**

For r>=6, the previously certified and independently reviewed restriction lower bound combines with this theorem to give 3<=d_F(F_r)<=4. This is a bounded-degree result for this no-wrap family. Here dim V=r+1 and n>4r; this is not the half-dimensional factor-base family.

## Cap-two affine reduction

Use the affine chain reduction in `no-wrap-coefficient-progress.md`. Put A(h)=h^2+h. After deriving linear chain constraints at cap two, choose remaining affine coordinates x_0,...,x_r and q_1,...,q_d, d=floor(r/2), so

q(0)=0, deg(q)<=d, y=x+1+A(q), xy=q^2.

The remaining quadratic coefficient equations are those of

E(x,q)=A(x)+x A(q)+q^2.

Squaring a polynomial with Boolean coefficients is linear in those coefficients. Thus these substitutions are affine coordinate operations, not substitutions of degree two in the Boolean variables. Quadratic substitutions differ from original rows by products of already-derived affine constraints with affine forms; these corrections are available at cap two. Conversely derivations in the reduced affine coordinate ring lift at every cap at least two, using the same corrections. Coefficients above the actual polynomial degree are zero by convention.

## Leading-q lemma

For 1<=j<=d, impose q_h=0 for h>j and q_j=1. In this restricted quadratic system, 1 is derivable at cap three.

First derive x_i=0 for i>2j in descending order from the coefficient of t^(2i) in E. The x^2 term is x_i. All terms of x A(q) have x-index at least 2i-2j>i; the possible x_(2i) term also has higher index. The q^2 term vanishes. Removing known higher x coordinates and their products by q coordinates is legal at cap two.

Branch on b=x_(2j).

* If b=0, descend through i=2j-1,...,1 using the coefficient of t^(i+2j). The leading coefficient of A(q) is one, so this row contains x_i. All other product terms have x-index greater than i. The possible x^2 contribution has index j+i/2>i, and the x contribution has index i+2j>i; these are already zero. There is no q^2 contribution at this index. Consequently x=x_0. Now E=x_0 A(q)+q^2. Its coefficient at 2j gives x_0+1; after deriving x_0=1, E reduces to q and its coefficient at j is 1.
* If b=1, make the invertible affine coordinate change u=x+A(q). It preserves coefficient degree, and direct expansion gives E=A(u)+u A(q)+q. The high u coordinates vanish, including u_(2j)=x_(2j)+q_j=0. The same descending coefficient argument makes u constant. Then the coefficient at 2j gives u_0=0, and the coefficient at j gives 1.

Each branch has a cap-two refutation: removing a known affine coordinate from a quadratic requires only its product with an affine form. The two branches of b lift with selectors 1+b and b, respectively, to cap-three derivations; adding their conclusions derives 1.

## One-sided lifting and uniform peeling

A cap-three refutation after fixing q_j=1 lifts by the selector q_j to a cap-four derivation of q_j before that restriction. Indeed multiplying each restricted generator correction and every step by q_j increases the degree bound by at most one; the selector annihilates q_j+1. This is the ordinary Boolean selector lifting argument and does not require a refutation of the q_j=0 branch.

Proceed downwards from j=d to j=1. If the higher q_h are already in W_C, C>=2, substitute them to zero in E. Differences between the substituted and original quadratic rows are sums of those known linears times affine forms, hence belong to W_C. The resulting quadratic rows are therefore already available at cap C. The leading-q lemma followed by one-sided lifting is a cap-four derivation of q_j from these rows, so q_j belongs to W_max(C,4) of the original system.

In particular, after the first step all successive eliminations remain inside W_4. There is no accumulating selector cost. **The substituted quadratic rows need not be in original W_2 or W_3:** they are in W_4, and every operation in the cap-four derivation stays there because the actual polynomials multiplied have degree at most three.

Once all q_j are in W_4, remove the x A(q) and q^2 terms to obtain the coefficients of A(x) at the same cap. Descending high coefficients, or following the doubling chains, derives x_i=0 for every i>0. The affine substitution for y then gives y_i=0 for i>0 and y_0+x_0+1=0.

These are the affine generators of the ideal of (x,y)=(0,1),(1,0). Reduction by affine ideal generators never increases polynomial degree. Multiplying their cap-four derivations as needed therefore derives every ideal element f at cap max(4,deg f); equivalently the last fall degree is at most four. Cases r=0,1, where q has no positive coordinates, follow immediately from A(x) and the affine reduction (and existing stronger cap-two proofs cover r=1).

## Deterministic arithmetic-cost corollary

This theorem also supplies an elementary polynomial-time algorithm for this scoped family. Let N=2(r+1), and M_e=sum_{i=0}^{min(e,N)} binomial(N,i). Represent Boolean polynomials through degree four as dense bit vectors of length M_4. Fix a monomial order decreasing first by degree. Maintain an incremental row-echelon basis with immutable inserted rows. A newly inserted basis row whose leading monomial has degree at most three has actual degree at most three; enqueue that row once and attempt to insert each of its N variable multiples.

At any stage the low-leading rows span precisely the intersection of the current row span with degree-at-most-three polynomials: in a nonzero combination, the earliest selected pivot cannot cancel, and all higher-degree pivots precede all lower-degree pivots. This remains true when new rows arrive; old rows need not be rewritten or reprocessed. Linearity of multiplication implies that multiplying the queued low rows suffices to multiply every member of that intersection. At most M_3 low-leading rows can ever be inserted, since every row has a distinct pivot. Thus at most N M_3 variable-multiple insertions occur, in addition to O(r) initial coefficient rows.

A straightforward dense Gaussian insertion takes O(M_4^2) binary arithmetic operations, including worst-case row XORs. The resulting conservative total bound is

O((r+N M_3) M_4^2)=O(N^12)

binary operations, with O(M_4^2)=O(N^8) stored bits, plus indexing and input conversion. This is an arithmetic bound in a unit indexed-bit-access model, not an exact machine-instruction count or a wall-clock estimate. Direct polynomial-coefficient representation avoids performing extension-field arithmetic in the closure. Reading an explicitly supplied field representation and any basis conversion has an additional representation-dependent polynomial cost; the bound is not a claim independent of input length n.

The closure contains the displayed affine ideal, so solution extraction requires only solving those linear equations. For this explicit family the solutions are already given by its definition; the closure algorithm corollary records the cost of a generic bounded-degree derivation, not a necessary way to find them.

## Sources and remaining distinctions

Sources: `no-wrap-coefficient-progress.md` (affine reduction); `polynomial-subspace-candidate.md` and its review (exact two solutions); `no-wrap-fixed-obstruction-transfer.md` (independently certified cap-two obstruction and all-r restriction transfer); `two-point-lfd-characterization.md` (affine-ideal/LFD bridge).

No exact distinction between degrees three and four for general r is asserted here. The existing all-r lower bound is constant three. Modular-reduction families outside n>4r are not covered by this argument.
