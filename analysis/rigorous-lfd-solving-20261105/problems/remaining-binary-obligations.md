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

## Obligation A: raw binary upper-bound formalization now compiles

The 2026-11-05 continuation now implements the actual support-aware proof
in BinaryLocalization.lean and the full raw coefficient-descent/S3
instantiation in BinaryCoefficientDescent.lean. The exact source theorem
`lastFallDegree_binary_two_S3_chain_le` derives LFD<=3ell+1 from actual
Boolean UNSAT, with arbitrary additive coordinate projections K->F2,
linear source forms and all explicit bit equations. It assumes no localized
row, normalized-support condition, supplied fibre refutation or finite LFD.
The earlier missing-step description is superseded at this exact syntactic
scope. See BINARY-FORMAL.md, independent review files and formal-status.md
for exact source hashes, checks and review standing. This does not close
unrelated encoding-refinement or relation-semantics requirements.

The full-workspace verifier remains separately resource-blocked in an old
80-row degree-three rank certificate (exit137, cgroupOOM). No full-workspace
success is inferred from the successful scoped new-module builds/audits.

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
