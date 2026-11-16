# Degree-five native quotient-checker control

The already-built native C0–C3 checker accepted a deterministic degree-five
evaluation-map fixture. A separately implemented Python checker agreed on
degree 5, 8 variables, quotient codimension 73, one annihilated generator,
and low-kernel dimension 90. Native stderr records all eight variable
multiplications. This exercises the D5 and multiword paths before any n51
D5 candidate is supplied; it does not validate a frontier certificate.

The input and protocol were committed and pushed at
`eb1a971d18f11669355485a2777ad3b168da91b2` before the single native
attempt. The pinned certificate is 5,288 bytes, SHA-256
`216b3772ea8559c3b7cff8100666aab528aa5f92766e5684119e5e2cd2650c65`;
the 40-byte generator file is SHA-256
`7b184be37c88fc36736565fa14e417372f4a65b0f26bcfbc9b22cc149a0bb9a4`.
The native binary SHA-256 is
`5adf9d71ceef5810774a833f8e18ecb0ae4a5656d5c23899db4e190178ef3b27`.
The reference Python source SHA-256 is
`ca5a760e138e667a687418bb5d69c31c9b462b32029295b15a50e70c56f77e89`.

The map evaluates all Boolean monomials of degree at most five on 73
distinct points of weight at most three. The 73 corresponding low-degree
monomials form a triangular evaluation submatrix, proving surjectivity.
Degree-at-most-four polynomials form a 163-dimensional space, so the
restriction has a 90-dimensional kernel. Evaluation commutes with Boolean
variable multiplication. The nonzero generator `x0*x1*x2*x3` vanishes on
all points. These facts supply an independent mathematical expectation for
the native fields and exercise a nontrivial closure condition.

The native attempt completed in 0.890 seconds, exit 0, under a 1 GiB
address-space and 120-second timeout cap. The frozen additional cost
reservation was USD 0.25 with one attempt and no retry. At launch the
two shared daily AWS budget readbacks were USD 104.44 and USD 48.383
against separate USD 200 alert thresholds; they are not additive.
The monthly account readback was USD 538.72 against USD 1,000. These
budget observations are delayed and are not a measured per-attempt bill.
The fixture used the existing binary, so it incurred no new build.

Raw [start](raw/check5.started.json), [finish](raw/check5.finished.json),
[native stdout](raw/check5.stdout.txt), [native stderr](raw/check5.stderr.txt),
and [Python reference](raw/python-reference.json) are retained here.
The pinned [fixture protocol](../../validation/d5-checker-fixture-protocol-001.json)
and [generator](../../validation/make_d5_checker_fixture.py) reproduce the inputs.
The fixture generator initially failed during pre-freeze preparation because
the host's Python 3.9 lacks `int.bit_count`; it was corrected before the
inputs, protocol, and attempt were frozen. No scientific checker attempt
preceded the frozen one.

A frontier D5 result still requires binding the exact candidate bytes,
freshly reconstructed n51 generators, and a separate full-size C0–C3
check. The n8 control cannot supply that result or an LFD-six lower bound.
