# Two exact ordered-pair counts for the named n47 S3 input

This is a source-level proof of the two counting algorithms, not a new
count result. The retained `count_by_sum` run printed zero for the named
input, with custody checked by `check_n47_count_bridge.py`. The separately
frozen `count_x1` run in `n47-rand00-x1-count-plan-002.json` has not been
launched. Its output and `verify_n47_x1_count_run.py` remain the independent
execution bridge required by the D5 lower-bound decision rule.

Work in the irreducible named field `K=GF(2^47)`, with nonzero `z`, target
`a6`, and a 24-dimensional `F2`-subspace `V`. The original summation
polynomial is

    S3(x,y,z) = (xy+z(x+y))^2 + zxy + a6.

Both programs count **ordered** pairs `(x,y) in V*V` satisfying `S3=0`.
There are at most `2^48` such pairs, so both 64-bit integer accumulators
cannot overflow on this named input.

## Count by the first coordinate

The frozen independent source `../semaev-m2-last-fall-degree/code/s3count2.c`
enumerates each `x in V` once using the reflected-Gray-code update
`x ^= basis[ctz(g)]` for `g=1,...,2^24-1`. For fixed `x`, expansion gives

    A*y^2 + B*y + C = 0,
    A=(x+z)^2, B=zx, C=(zx)^2+a6.

The four source branches exhaust every possibility:

* `A=B=0`: all `2^24` values of `y in V` are roots exactly when `C=0`.
* `A=0, B!=0`: the unique field root is `y=C/B`; count it iff `y in V`.
* `A!=0, B=0`: the unique field root is
  `y=(C/A)^(2^46)`; count it iff `y in V`.
* `A!=0, B!=0`: with `c1=B/A` and `c0=C/A`, set `t=y/c1`.
  Then `t^2+t=c0/c1^2`. The precomputed echelon section of the
  `F2`-linear map `t -> t^2+t` rejects values outside its image and
  returns one root otherwise. The two distinct roots `t` and `t+1`
  are checked separately for membership of `c1*t` and `c1*(t+1)` in `V`.

The section is built from all 47 basis images of `t^2+t`; row reduction
retains a preimage for each pivot. Consequently a successful reduction
of a right-hand side returns a genuine preimage, and a missing pivot
correctly means no root. Polynomial-basis field multiplication uses
carryless multiplication followed by reduction modulo the named
irreducible polynomial. Inversion uses exponent `2^47-2`. Every `x`
appears once, and each branch counts exactly its roots `y in V`, proving
the source's final integer is the exact ordered-pair count if its named
run completes correctly.

## Count by the sum coordinate

The retained source `../semaev-m2-last-fall-degree/submission-20261029/count_by_sum.c`
enumerates each `s=x+y in V` once. Set `u=xy/z` and `alpha=a6/z^2`.
Dividing the S3 equation by `z^2` gives

    u^2+u = s^2+alpha.                                  (1)

The trace of the right side must vanish, so the program buffers only
`s` with `Tr(s)=Tr(alpha)`. Its precomputed linear section gives one
root `u0` of (1), and the other is `u0+1`. Its batch inversion computes
`s^-1` for every buffered nonzero `s` using prefix products and one
field inverse per batch; independent subspace coordinates ensure no
nonzero Gray-code index yields `s=0`.

For `s=0`, the two possible `u` values lead to `x=y` and
`x^2=zu`; each square root is unique in `K` and counted once iff it
belongs to `V`. For `s!=0`, use `y=x+s` and put `t=x/s`. Then

    t^2+t = zu/s^2.                                     (2)

The section rejects an unsolvable right side of (2). Otherwise the two
roots `t,t+1` yield `x` and `x+s`; because `s in V`, either both lie in
`V` or neither does. Each successful `u` therefore contributes two
ordered pairs. The two `u` roots are distinct because `z!=0`, so their
pair sets do not overlap. The `s=0` case and all nonzero `s` partition
`V*V`, proving the source's total exact on a correctly completed run.

The two algorithms share the mathematical S3 identity and named field
record but differ in enumeration coordinate, quadratic reduction and
membership path. The retained sum-coordinate zero is a historical
source/binary-custody result; the first-coordinate zero is still an
unperformed independent check. Neither algorithm by itself constructs
the required D5 nonmembership certificate.
