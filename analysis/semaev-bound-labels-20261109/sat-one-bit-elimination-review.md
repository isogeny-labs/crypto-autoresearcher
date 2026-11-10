# Independent review of SAT one-bit definitional extension bounds

Date: 2026-11-09. Source-only mathematical review of `sat-one-bit-elimination.md`; no builds, experiments, or certificate replay. Verdict: the count-sensitive inequalities and high-degree-generator counterexample are correct under the normalized Boolean/polynomial-with-bit-equations convention. The all-quadratic Semaev case remains unresolved by the counterexample.

## 1. Gröbner-basis degree bound

For a Boolean zero set of M>0 points, quotient dimension is M because the ideal includes all bit equations and is its radical vanishing ideal. The initial ideal contains every x_i², so a minimal initial generator of degree>2 is squarefree. Every proper divisor of such a degree-d generator is standard, giving 2^d−1≤M and hence d≤floor(log2(M+1)). A degree-compatible order bounds the complete reduced-basis polynomial by the degree of its leading monomial. Therefore b(M)=max(2,floor(log2(M+1))) is a valid, possibly loose, upper bound.

No assumption that the input equations themselves form a Gröbner basis is used for this count bound. The restriction to degree-compatible order is essential for controlling tail degrees from leading-monomial degrees.

## 2. Inequality d_F≤max(d_G,b(M))+2

A reduced basis element h of I(F) has degree≤b(M) and is also in I(G). Its derivation in G is available at D=max(d_G,b(M))≥2. In the Boolean quotient, substituting epsilon=q into any multilinear proof line increases its actual degree by at most1. A permitted epsilon multiplication can require two ordinary-variable products after substitution, with safe capD+2. Thus the existing refutation simulation applies to each low-degree basis element, even though the final desired polynomial is not1.

The polynomial field-equation lift is safe here: D≥2, and the substituted epsilon bit equation q²+q has degree≤4 and is repaired within capD+2. For base-variable field equations the repair costs no more than2. If h itself is not multilinear, normalize it and reinsert its field-equation repair at degree≤b(M).

All F reduced-basis elements therefore belong to V_(F,max(d_G,b(M))+2). Degree-compatible standard representations extend this to every ideal polynomial at max(the stated bound,its own degree), proving the LFD claim. It is not the invalid inference that an arbitrary degree-e substitution cap e+2 alone is already a constant LFD bound; the crucial intermediate basis degree is bounded by b(M).

## 3. Inequality d_G≤max(d_F,b(M)+1)

For a multilinear reduced-basis element h of I(G), write h=h0+epsilon*h1 with deg h1≤b(M)−1. The substitution hhat=h0+q*h1 lies in I(F): substitution sends the defining equation to0 and the epsilon bit equation into the original bit ideal. Its degree is≤b(M)+1.

The original F derivation supplies hhat at max(d_F,b(M)+1). Independently, the identity

h+hhat=(epsilon+q)h1

uses the defining equation with product degree≤2+(b(M)−1)=b(M)+1. This respects strict multiplication and does not require a degree-dropping product shortcut. The basis-element field-equation repairs fit the same cap. Standard representations then establish the stated LFD upper bound.

The bounded-M consequence is correct. When M is unbounded, b(M) can grow, so the theorem does not supply a uniform additive invariance claim for arbitrary SAT families.

## 4. Counterexample verification

For n≥3, F_n consists of all bit equations and m_n=x1...xn. The bit equations are a Gröbner basis of their own ideal. For each i, the S-polynomial of x_i²+x_i with m_n is m_n (up to the characteristic-two sign convention), so it reduces to0 by the m_n generator. Thus the full displayed set is a Gröbner basis for every degree-compatible order.

Every ideal member then has a standard representation whose products do not exceed its own degree. Therefore d_LFD(F_n)=0 when last fall degree is minimized over nonnegative integers, as in the dossier. This is consistent even though the input includes a degree-n generator: input degree and last fall degree are different invariants.

In G_n, h_n=epsilon*x3...xn belongs to the ideal by

h_n=m_n+(epsilon+x1x2)x3...xn.

At capn−1, m_n is not eligible. All eligible inputs vanish at the all-ones assignment, whereas h_n evaluates to1. Every strict-closure derivation from those inputs also vanishes there, so h_n∉W_(n−1), proving d_LFD(G_n)≥n.

The argument does not depend on the eventual high-degree generator being absent from the ideal; it depends on its absence from the **eligible input list at that cap**, which is precisely the degree-filtration mechanism. This is a genuine counterexample to universal constant-additive SAT-LFD invariance for arbitrary Boolean presentations.

The high-degree-generator qualification must remain prominent: F_n has degree-n input m_n. This does not refute an all-quadratic definitional-extension theorem and is not an unbounded fixed-m=2 Semaev family.

## 5. Affine definitions and final scope

For affine q, replacing epsilon by epsilon+q is an invertible affine change. In the resulting F∪{epsilon'}, restriction to epsilon'=0 gives one closure direction; the decomposition of an ideal member into its base part plus epsilon' times a polynomial gives the other without degree increase. Exact LFD invariance is therefore appropriate for this specifically affine extension. It does not follow for quadratic q.

No mathematical correction is required to the reviewed theorem statements. Keep the normalized-input convention explicit, M>0 for the SAT theorem, degree-compatible orders for the basis argument, the natural-number convention allowing LFD0, and the high-degree-input limitation of the counterexample. No formal proof or runtime verification is claimed by this written review.
