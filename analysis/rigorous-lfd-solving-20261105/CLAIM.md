# Candidate theorem: growing prime-digit last fall and solving degree

2026-11-05. Candidate written proof, not yet independently adjudicated.
No scientific state or novelty claim. Reviewer should rederive the statement
before reading PRIME-PROOF.md.

Let s>=2, p>3 prime, 2^s<=p, E/F_p: y^2=x^3+a*x+b nonsingular, and z any
field element (in particular an affine rational target abscissa). Put

    X=sum_(i=0)^(s-1) 2^i A_i,  Y=sum_(i=0)^(s-1) 2^i B_i,
    f=NF(S3(X,Y,z)),
    F={f} union {T^2-T : all 2s digit variables T}.

The normalized non-bit generator has degree exactly four. For every
degree-compatible monomial order sigma, the proposed rigorous bounds are

    4+floor(s/2) <= d_F <= sd_sigma(F) <= 2s+1.

They include SAT and UNSAT inputs. The SAME bounds are claimed for the raw
single-generator S3 substitution with the explicit bit equations, since raw
and normalized input degrees are four and the relevant cap is at least four.
No additional chain, membership, rational-lift, carry, sign, or range equations
are part of this exact presentation.

This is a fixed-degree family as s grows. There are infinitely many such
prime-field presentations, including rational targets, and no assertion of
small running time follows. The coefficient-characteristic-two analogue does
not follow from this statement.

Source ingredients to check independently: Frankl 1990, Proposition 1.2 or
Theorem 4.1 (Wilson), https://www.renyi.hu/~pfrankl/j62.pdf; Caminata--Gorla
Theorem 3.1, https://arxiv.org/html/2112.05579v2; the exact S3 polynomial and
Boolean closure convention already present in the repository. Existing
H-PFDR-4148b8 discusses a top-form first-fall rank calculation; the proposed
claim concerns LAST fall and solving degree, not equality to first fall.
