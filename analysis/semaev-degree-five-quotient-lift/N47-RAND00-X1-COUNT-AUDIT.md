# Independent x1 count: source-level completeness audit

The frozen independent replay uses the existing `s3count2.c` source with
SHA-256 `fc8010f395a18b88b0739abfac3e4b6349be5c6be96ce5070e20f60364d98217`.
Its named input is the 24-dimensional random-00 factor space in
`n47-rand00-x1-count-plan-001.json`. The protocol's canonical SHA-256 is
`2c90501ab8618772a1bb37137b4520f773dd3ee00cb2191223dc95f6a21485b8`.
This note audits the algorithm before its one allowed run; it records no new
n47 count.

For fixed `a=x1`, write the binary Semaev equation as a polynomial in
`b=x2`:

```
S3(a,b,z) = A*b^2 + B*b + C,
A=(a+z)^2,  B=a*z,  C=(a*z)^2+a6.
```

The source enumerates `a` by Gray-code transitions across all `2^24`
combinations of the supplied independent basis. Its `addbasis` routine
rejects a dependent basis. Every `a in V` is therefore visited once.
For each `a`, the following source branches exhaust all roots in the field:

- If `A=0`, the equation is linear. For `B!=0` the sole root is `C/B`;
  if `B=0`, every `b in V` works exactly when `C=0`. The named target has
  `z!=0`, so `A=0` actually implies `a=z` and `B=z^2!=0`.
- If `A!=0` and `B=0`, the sole root is the square root of `C/A`.
  The source obtains it by `n-1` squarings in `GF(2^n)`.
- If `A*B!=0`, put `c1=B/A`, `c0=C/A`, and `b=c1*y`. The equation becomes
  `y^2+y=c0/c1^2`. The source constructs an F2-linear section of
  `y -> y^2+y` by Gaussian elimination. It either rejects a right-hand
  side outside the image or returns one root `y`; the only other root is
  `y+1`, and the two corresponding `b` values are distinct.

The source's `inV` elimination counts each returned field root only if it
lies in the named factor space. Thus a successful complete run counts each
ordered pair `(a,b) in V x V` once and omits none. Inversion is called only
on nonzero branch coefficients; the exponent `2^n-2` is the inverse
exponent in the independently verified irreducible field. The count fits a
signed 64-bit integer because at most `2^48` ordered pairs exist.

The two fixed GF(8) controls can be checked directly from the formula:
with `V={0,1}` and `z=1`, the polynomial without `a6` has value one at
`(0,1)` and `(1,0)`, and value zero at `(0,0)` and `(1,1)`. Hence `a6=1`
gives count two and `a6=X` gives count zero. The frozen run stops before
the n47 target if either control fails. These controls exercise the
branching and field arithmetic, but they do not replace complete n47
execution and custody checks.

This route enumerates `x1` and solves a quadratic in `x2`. The retained
`count_by_sum` result enumerated `x1+x2` and solved two successive
Artin–Schreier equations. The different decomposition provides a useful
independent replay once the new binary, controls, and target have run and
`verify_n47_x1_count_run.py` accepts their exact outputs. The zero-solution
premise then transfers to the checked 47-variable affine slice because
Proposition 2.5b gives a bijection of zero sets. A checked D5 quotient map
is still the separate degree-six lower-bound gate.
