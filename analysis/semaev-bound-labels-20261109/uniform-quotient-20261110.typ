#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
= Uniform quotient lower-bound construction
2026-11-10. Reviewed symbolic constraints; no experimental run.

#image("uniform-quotient-20261110.svg", width: 100%)

#table(columns: (1fr, 2fr), inset: 8pt,
[Failed block ansatz], [Tensor-factorized x/y images imply actual solutions],
[Failed operator ansatz], [Global commutation alone forces a Boolean solution representation],
[Necessary size], [Actual quotient rank q is at least 2^(D-1)],
[Remaining construction], [Coupled images, truncated boundary defects and full kernel closure])

The exact Semaev coefficient tensor must annihilate the proposed quotient columns. Every lower-degree kernel relation must remain in the kernel after every legal variable multiplication. This includes feedback from newly derived consequences; an initial-matrix annihilator does not suffice.

The tensor obstruction follows already from block-bilinear input containment: normalized dual functionals on the two factors give actual Boolean assignments satisfying every generator. The operator obstruction needs only global commutation: idempotence on the cyclic vector then propagates to the entire spanned quotient.

The exponential size lemma uses a degree-compatible multiplicative monomial order. Leading kernel monomials are upward closed under squarefree multiplication within the cap. Standard monomials form a downset. An early filtration plateau would create a global solution module, so a useful separator retains a standard monomial of degree D-1 and all its2^(D-1) divisors.

The same divisor argument gives $dim(Q_e)-dim(Q_(e-1)) >= binom(D-1,e)$ for $0 <= e <= D-1$, with $Q_(-1)=0$. This constrains every layer of a proposed uniform filtration.

This bound concerns certificate representation size, not existence or LFD growth. Implicit exponential-dimensional constructions remain possible; polynomial rank in field size can still support logarithmic degree growth. A valid quotient must keep nonzero commutation defects at the truncated boundary, outside the lower-degree subspace where Boolean identities hold.

No explicit infinite growing-degree family was constructed. The next obligation is a coupled symbolic quotient for actual non-subfield factor bases, with a proof of full closure and a separate missing-consequence bridge. No new experiment, replay, build or cloud job ran.

Evidence: uniform-quotient-algebraic-20261110.md and review; uniform-quotient-operator-20261110.md and review; quotient-exponential-rank-review.md. These are written derivations, not formal-kernel certification.
