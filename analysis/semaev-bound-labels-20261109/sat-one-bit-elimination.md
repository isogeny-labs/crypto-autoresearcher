# SAT last fall degree under one quadratic definitional extension

Date: 2026-11-09. Source-only mathematical analysis. No builds, experiments, or new certificate replay. The unrestricted constant-additive SAT-LFD transfer sought by the parent is not proved. This note obtains a solution-count-sensitive theorem and an explicit obstruction to claiming general additive invariance.

## 1. Setup

Let F be a Boolean polynomial system in x_1,...,x_N, with Boolean field equations, and let q(x) have Boolean degree at most two. Introduce one Boolean variable epsilon and define

 G=F union {epsilon+q(x)} plus the epsilon field equation.

The zero sets have the same cardinality M: every F-solution has the unique extension epsilon=q(x). The normal-form reduction in `lower-bound-transfer-obligation.md` has exactly this shape after affine trace elimination.

Write d_F,d_G for last fall degrees with the strict Boolean closure/polynomial closure conventions in the dossier. We assume M>0 in the SAT statements below. Let

 b(M)=max(2,floor(log_2(M+1))).

## 2. Boolean point-count bounds the reduced GB degree

For any finite Boolean zero set of size M, a reduced Gröbner basis under a degree-compatible order has degree at most b(M).

Reason: Boolean field equations put x_i² in the initial ideal. A minimal initial generator of degree greater than two must therefore be squarefree. If its degree is d, all its 2^d-1 proper divisors are standard monomials. There are exactly M standard monomials, so 2^d-1<=M and d<=floor(log_2(M+1)). Degree-two square generators account for the max with 2. Degree compatibility bounds the whole reduced basis polynomial by its leading-monomial degree.

This is an upper bound. It does not claim that a particular Gröbner basis actually reaches this degree.

## 3. A rigorous solution-count-sensitive transfer theorem

The following bounds hold:

 d_F <= max(d_G,b(M))+2,                        (A)
 d_G <= max(d_F,b(M)+1).                        (B)

The constants are conservative and incorporate strict-closure intermediate-degree accounting. No equality or optimality claim is made.

**Proof of (A).** Choose a degree-compatible reduced Gröbner basis of I(F); every element h has degree at most b(M). Since h belongs to I(G), the definition of d_G provides a G-derivation within D=max(d_G,b(M)). The substitution epsilon=q fixes h. As established in the preceding note, every degree-D Boolean derivation in G can be simulated in F within degree D+2: each multilinear line has only one possible epsilon factor; its substitution increases degree by at most one; simulating multiplication by epsilon through a quadratic q costs at most two intermediate degrees. Therefore every element of the chosen F Gröbner basis lies in W_(max(d_G,b(M))+2)(F). Degree-compatible standard representations of arbitrary ideal elements give the LFD bound (A).

**Proof of (B).** Choose a degree-compatible reduced Gröbner basis of I(G), with degrees at most b(M). Reduce any basis element h modulo Boolean field equations at no degree increase, and write

 h=h_0(x)+epsilon h_1(x).

Its substitution h_hat=h_0+q h_1 belongs to I(F) and has degree at most b(M)+1. Hence it can be derived from F, and thus from G, within max(d_F,b(M)+1). Also

 h+h_hat=(epsilon+q) h_1,

whose derivation directly from the defining equation needs degree at most b(M)+1, since deg h_1<=b(M)-1. Reinsert any Boolean-field reduction terms within degree b(M). Thus every G Gröbner-basis element is available at max(d_F,b(M)+1), proving (B) by standard representations.

**Consequences.**

- If a family has uniformly bounded solution count M, then bounded LFD is equivalent for F and G. Any unbounded LFD sequence on one side is unbounded on the other.
- If d_F>b(M)+2, then (A) forces d_G>=d_F-2.
- If d_G>b(M)+1, then (B) forces d_F>=d_G.
- In particular, SAT examples with at most four solutions have b(M)=2, so d_F<=max(d_G,2)+2 and d_G<=max(d_F,3).

For the full inside-subfield Semaev family, M can grow exponentially with k. The theorem therefore does not give a uniform constant transfer there. It does give a rigorous criterion for a prospective low-solution-count family.

## 4. Explicit failure of general additive invariance

One cannot assert that adding a single quadratic definitional bit always changes SAT LFD by a universal additive constant for arbitrary Boolean input systems.

For n>=3, let

 F_n={x_i²+x_i : 1<=i<=n} union {m_n},
 m_n=x_1 x_2 ... x_n.

This satisfiable system has all Boolean points except the all-ones point. Its displayed generators form a Gröbner basis for every degree-compatible order: the leading monomials are x_i² and m_n; a field-polynomial/m_n S-pair reduces to m_n or zero, and the field-polynomial S-pairs reduce to zero. Because the Gröbner basis is the generating set itself, every ideal polynomial has a standard representation without increasing its own degree. Therefore

 d_LFD(F_n)=0.

Now add the quadratic definition epsilon+x_1x_2 and the epsilon Boolean field equation, obtaining G_n. The polynomial

 h_n=epsilon x_3...x_n

has degree n-1 and belongs to I(G_n), because

 h_n=m_n+(epsilon+x_1x_2)x_3...x_n.

But h_n is not in W_(n-1)(G_n). At that degree the generator m_n, of degree n, is not admitted. Every admitted generator is a field equation or epsilon+x_1x_2, all of which vanish at the assignment x_1=...=x_n=epsilon=1. Every element of the closure also vanishes there, whereas h_n evaluates to 1. Thus h_n requires degree at least n, and

 d_LFD(G_n)>=n.

This is an unbounded SAT-LFD increase caused by adding one quadratic definitional bit. It exactly illustrates the high-degree-output obstruction: the extension compresses a degree-n ideal relation into degree n-1, creating a late fall that the original presentation does not have.

**Scope limitation.** F_n has a degree-n generator. This counterexample rules out an unrestricted theorem for arbitrary Boolean systems; it does not rule out a stronger theorem for systems generated entirely in degree two, nor a special theorem for the Semaev family. No quadratic-generator counterexample was obtained in this analysis.

The M-dependent theorem is consistent with the example: M=2^n-1 gives b(M)=n, so (B) allows d_G=n while d_F=0.

## 5. The affine case is genuinely different

If q is affine, the change epsilon'=epsilon+q(x) is an invertible affine coordinate change. It takes the extension to F union {epsilon'}, and all ideal elements decompose as a base ideal element plus epsilon' times a polynomial without increasing degree. Projection epsilon'=0 gives the reverse closure inclusion. Thus adjoining an affine definitional bit preserves LFD exactly under these conventions. The quadratic case is not an innocuous affine coordinate change.

## 6. Remaining sharp question for Semaev

After trace elimination, Semaev's transformed family has only quadratic generators and one quadratic definition. The general counterexample does not settle that restricted case. To remove b(M) from (A) or (B), a proof must show that high-degree Gröbner-basis elements do not acquire arbitrarily late compression falls when epsilon represents the particular Semaev quadratic q. The exact q is tied to field multiplication; replacing it by an arbitrary new symbol loses that structure.

A concrete sufficient condition would be a degree-compatible normal-form theorem for the original ideal that bounds the degree of every relevant minimal relation independently of k, or shows that every compression-induced relation of degree e can be derived within max(C,e). The current one-bit substitution simulation only supplies e+2, and the explicit example above demonstrates why that gap cannot be dismissed in general.

For the unboundedness route, another sufficient avenue is a family with uniformly bounded M and growing full-closure lower bounds in the normal form. Then Section 3 transfers unboundedness rigorously. Establishing bounded M and constructing the growing certificates remain separate proof obligations.

## 7. Literature boundary

Primary-source discovery revisited Huang–Kosters–Yeo, https://eprint.iacr.org/2015/573.pdf, and the definitions/theorems of Caminata–Gorla, *Solving degree, last fall degree, and related invariants* (ePrint 2021/1611). The proof above uses the dossier's explicit LFD definition and degree-compatible standard representations; it does not import an auxiliary-variable invariance theorem. The search did not establish such a theorem. This is not a novelty claim, and absence from the searched results is not evidence that none exists in the literature.
