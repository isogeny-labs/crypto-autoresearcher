# Blind mathematical card: raw coordinate decomposition

Let `F = F_5`, `K = F_5`, and let `W` be the nonsingular short Weierstrass curve `y² = x³ + x + 1` over `K`. More generally, let `F` be a finite field, `K` a field with an `F`-algebra structure and decidable equality, and `W` a nonsingular affine Weierstrass curve over `K`. Fix a finite family `basis : Fin b -> K`, a tuple `xy : Fin m -> K × K`, and a typed target `R : W.Point`.

Define `Span(x)` by existence of coefficients `c : Fin b -> F` with `sum_i c_i • basis_i = x`. Define `Equation(x,y)` by the Weierstrass equation. Define `pointOfRaw(x,y)` to be the curve point `(x,y)` when `Equation(x,y)` holds and the group identity otherwise. Define `ValidRaw(xy;R)` by `Equation(x_i,y_i) ∧ Span(x_i)` for every tuple member, together with `sum_i pointOfRaw(x_i,y_i)=R`.

Independently derive whether `ValidRaw` is equivalent to every pair satisfying the curve equation and `x_i` belonging to the declared span, plus equality of the reified group sum to `R`. Examine the finite F5 curve above with valid and invalid coordinates, a declared zero span, correct and wrong targets. Also examine `b=0`, `m=0`, and an invalid pair mapped by `pointOfRaw` to identity. State what, if anything, follows about an untrusted serialized record, a producer's actual curve/field, or runtime cost.

This card contains no producer theorem source, proof text, receipt, or sibling review. Do not open them for the blind joint.
