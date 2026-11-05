# Remaining binary proof obligations

Raised 2026-11-05; original requirement retained: prove rigorous last-fall and
solving-degree bounds for the fixed-degree Boolean/digit systems used in the
research, including full characteristic-two formalization and growing-family
lower bounds. This record does not resolve those requirements.

## Exact completed deltas

The prime digit candidate proves an unbounded lower bound for the exact
single-S3, two s-bit-block presentation; its semantic independent review is
recorded separately. It is not a binary result. The previous closure checker
and SAT missing-consequence method remain usable at their finite limits.
New generic Boolean repair and binary S3-shape kernel checks have their exact
statements and verification evidence in formal-status.md.

## Obstruction A: full binary upper-bound formalization

The written support-aware proof is complete in BOUNDS.md and the cited
binary note, including the actual staged derivation of every localized row.
The original Lean assembly lemma assumed those rows; merely applying it does
not prove their derivability. The new S3-shape module proves the raw repair
and degree bounds but does not implement coefficient extraction from K/F2,
multilinear interpolation with unassigned auxiliary indeterminates, or the
support-preserving staged localization. A successful build cannot supply
these missing hypotheses.

Exit: a hole-free Lean theorem for the exact F2 coefficient equations with
all bit equations, ell>=1, one shared n-bit auxiliary (optional independent
inverse-guard block), deriving 1 in ordinary V(F,3ell+1) from UNSAT. Its
statement must not assume the localized rows or the desired degree bound.
Next: compose the concrete Boolean normalizer with a base-support filtration,
prove the single-indicator multiplication step at support-size+2, then prove
coefficient descent and instantiate affine-fibre Gaussian elimination.

## Obstruction B: growing characteristic-two lower bound

The prime proof's square-zero top multiplication is injective in a low-degree
range because the needed inclusion factors are invertible in odd large
characteristic. Binary S3 has a different normalized top form, and the same
injectivity assertion is unavailable. Exact finite witnesses and growing
upper bounds imply no unbounded lower bound. A high-degree membership
polynomial in an ordinary-field model is not a fixed-degree Boolean input.

Exit: specify an arbitrarily growing family of the actual fixed-degree
binary S3 systems and construct exact full-closure separators at caps tending
to infinity, plus either UNSAT or a missing SAT ideal consequence. Every
variable multiplication of the entire low-degree kernel must be controlled;
first-fall observations and plain-Macaulay rank alone do not meet the exit.
Next: analyze the binary quadratic multiplication map and its trace-derived
low-degree falls before proposing a closed separator; certify the small
members with the existing two-sided checker as controls, then prove a
parameter-uniform invariant. No such invariant is claimed here.

## Status distinction

These are mathematical/formal coverage gaps, not a runtime failure and not
evidence that the requested theorems are impossible. No official goal,
hypothesis or evidence status is changed by this local proof work. Prior
historical reports remain immutable and link forward to this new record.
