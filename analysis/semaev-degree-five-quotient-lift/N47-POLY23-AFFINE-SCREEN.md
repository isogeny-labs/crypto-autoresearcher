# n47 polynomial factor space: affine screen

For the field defined by `X^47 + X^5 + 1`, let
`V = span_GF(2){1, X, ..., X^22}` and set `z=1`. This was a candidate for
reducing the number of variables before a degree-five certificate search.
It is a structural screen only; no instance or closure was run.

The product space `P=span{uv:u,v in V}` has basis `1,X,...,X^44`, so
`dim P=45`. In the Semaev polynomial
`S_3(a,b,1)=(ab+a+b)^2+ab+a_6`, the quadratic coefficient map is
`T:P -> K`, `T(u)=u^2+u`. Its kernel is `{0,1}`, hence its rank is 44.
Theorem-dossier Proposition 2.5d therefore gives three independent
combinations of the 47 descended equations whose quadratic parts vanish.

Only **one** of those three combinations has an independent nonconstant
linear part. After removing the quadratic image, the linear part is the
image of `(a+b)^2`, and the exact GF(2) calculation gives
`rank(T(P) + V^2) - rank(T(P)) = 45 - 44 = 1`. If `a_6` is outside
`T(P)+V^2`, one of the remaining combinations is a nonzero constant,
giving a degree-two refutation. If `a_6` is inside that space, the other
two combinations are zero identities, so they cannot eliminate further
variables. Thus this polynomial-basis choice does not supply three useful
affine slices for the degree-six search.

Replay the exact rank calculation with
`python3 analysis/semaev-degree-five-quotient-lift/n47_poly23_affine_screen.py`.
The script reduces squares modulo the displayed field polynomial and
performs bitwise Gaussian elimination. A separate repeated-multiply
implementation gave the same ranks `45, 44, 45` for `P`, `T(P)`, and
`T(P)+V^2`. This screen does not determine the last fall degree of any
polynomial-basis instance; the existing random-00 slice remains the
bounded certificate route.
