# Prior-art and definition gate for the binary Semaev paper

Focused primary-source review, 2026-11-08. This note records the sections
that constrain the current claims; it does **not** assert that every page of
each paper has been read. The manuscript should use one explicit last-fall
definition and cite the corresponding source.

## Last-fall definition and open problem

Huang–Kosters–Yeo, [*Last Fall Degree, HFE, and Weil Descent Attacks on
ECDLP*](https://www.iacr.org/archive/crypto2015/92160209/92160209.pdf),
CRYPTO 2015, Definition 1 defines `V_{F,i}` as the least vector space
containing eligible inputs and closed under products whose degree stays at
most `i`; Definition 2 defines `d_F` by membership of every ideal element
in `V_{F,max(d_F,deg f)}`. This is the definition used in the theorem dossier
after its Boolean-to-polynomial bridge. Section 5.3 expressly asks for a
rigorous estimate of last fall degrees of multivariate Weil-descent
systems arising from summation polynomials. The paper's Remark 5 says the
then-existing zero-dimensional result does not directly apply to
summation-polynomial systems without field equations.

The same paper's §5.2 reports first fall degree 2 in its computations and
points to the subsequent Kosters–Yeo proof. Its Remark 4 says the n=40
Magma computation did not finish before submission; subsequent computations
indicated increasing degree of regularity. These are observations and
context for the open problem, not certified LFD lower bounds.

## First fall 2 and observed degree 5 were already known

Kosters–Yeo, [*Notes on summation
polynomials*](https://arxiv.org/pdf/1503.08001), 2015, Corollary 4.11
derives a linear trace combination of the descended third summation
polynomial for an ordinary curve and a rational point outside the
2-torsion. Remark 4.12 explains why the first fall degree is usually 2
when the coordinate equations have quadratic degree. This already covers
the core m=2 first-fall phenomenon; the dossier's exact-presentation proof
is not a priority novelty claim. Corollary 4.11 fixes `z=x(P)` for a rational
point outside 2-torsion, whereas the dossier's algebraic identity is stated
for every nonzero `z`; this hypothesis difference should be stated without
implying that the value 2 itself is new. Section 5 reports a completed n=45,
m=t=2 computation on Semaev's default factor subspace with degree of
regularity 5. It is an observed solver step degree, not a proof of LFD 5.
The same section discusses a splitting system whose first fall degree is
2; its exact relation to the chained presentation in this dossier needs
line-by-line comparison before asserting a new chained first-fall fact.

Kousidis–Wiemers, [*On the First Fall Degree of Summation
Polynomials*](https://eprint.iacr.org/2015/1121.pdf), Journal of
Mathematical Cryptology 2019, Remark 3.3 explicitly cites Kosters–Yeo
Corollary 4.11/Remark 4.12 for m=2 first fall degree 2. Table 1 reports
average observed regularity 5 for its random-subspace m=2 experiments
from n=37 through 48. Section 4 says its open approximation question is
about `Dreg` versus first fall degree as parameters grow. It does not, in
that section, formulate the same last-fall theorem as HKY §5.3. The
manuscript should attribute those two questions accurately rather than
saying both sources state one identical open problem.

## Claim rule for the present work

State HKY's `V_{F,d}`/`d_F` convention, the Boolean closure bridge, and the
UNSAT or exact-solution-count condition whenever a quotient certificate is
used to infer an LFD lower bound. Attribute first fall 2 and previously
observed regularity 5 to the papers above. Describe the new finite result
as a checker-accepted full-closure lower bound on a named input, with the
independent solution-count bridge where required. Do not convert an
observed `Dreg` into an exact LFD value or a finite collection of lower
bounds into asymptotic growth.

The focused primary-source check here does not discharge the submission
item to read HKY and Kousidis–Wiemers in full. Their complete proofs,
definitions, experiment setup, and any later versions still need a full
page-by-page novelty and citation audit before submission.

## Method-transfer check for the degree-six proof

HKY §§3–4 transfer a **univariate** polynomial to a fake Weil-descent
system with cyclic Frobenius equations, construct a gcd by Euclidean
division, and bound its last fall degree. Their §5.3 explicitly separates
that setting from multivariate summation-polynomial systems. The n47
factor-base restriction leaves two interacting variables before descent;
the univariate remainder argument does not supply a D5 full-closure
separator for it.

Kousidis–Wiemers §§2–3 work in the associated graded square-zero algebra
and use a top monomial to produce a first-fall syzygy. The argument
certifies the existence of a low-degree fall, not the absence of later
mutant rows. The n47 joint top-form computation and independent D3 replay
in this repository extend that graded analysis to a complete **degree-one
multiplier** syzygy layer and its actual D3 closure, but the D5 question
still requires controlling all legal lower-degree products through cap 5.
