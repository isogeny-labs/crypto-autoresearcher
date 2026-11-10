# Blind mathematics card: decomposition certificate

Derive a decision procedure, from the definitions below, for the validity of
an arbitrary finite tuple of affine points on a Weierstrass curve. Derive the
exact iff statement for the decision result. Do not read the producer's source,
Lean proof, prior report, receipts, review plan, Git history, or other reviewers'
work. Record every file read and any departure from this boundary.

Let `F` be finite, `K` a field with decidable equality and an `F`-algebra
structure, `basis : Fin b -> K`, and `V` the `F`-span of its range. Let `W` be
a Weierstrass curve over `K`, `P : Fin m -> W.Point` a tuple of nonsingular
points (including the group identity as a possible value), and `R : W.Point`.
A valid certificate has affine summands, each satisfies the curve equation,
each x-coordinate lies in `V`, and the group sum of the tuple equals `R`.
Also consider raw `(x,y)` pairs that must be checked before conversion to
curve points.

Work both general reasoning and small-field cases. For the latter use
`F = K = F_5` and the curve `y^2 = x^3 + x + 1`. Consider empty and
one-element spanning families, tuple lengths zero and one, coordinates
`(0,0)`, `(0,1)`, `(2,1)`, and targets chosen as either the group identity
or one of the corresponding valid points. State what each case establishes
about the predicate, and which assumptions it actually uses.
