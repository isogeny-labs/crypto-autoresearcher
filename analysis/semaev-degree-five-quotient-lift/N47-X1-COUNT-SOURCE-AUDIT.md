# n47 random00: source audit of the independent ordered-pair counter

The frozen `n47-rand00-x1-count-local-002` plan builds
`../semaev-m2-last-fall-degree/code/s3count2.c`, SHA-256
`fc8010f395a18b88b0739abfac3e4b6349be5c6be96ce5070e20f60364d98217`.
This note checks the counting argument for the named n47 input. It is a
source audit, not a target execution or an independently accepted count.

The theorem dossier fixes

`S3(x,y,z) = (xy+xz+yz)^2 + xyz + a6`.

For fixed `x=X1`, the source forms the quadratic in `y=X2`

`A*y^2 + B*y + C = 0`, with
`A=(x+z)^2`, `B=x*z`, and `C=(x*z)^2+a6`.

This expansion is exact in characteristic two. The source visits `2^24`
successive Gray-code states, toggling basis vector `ctz(g)` at step `g`.
Consequently every element of the 24-dimensional factor base occurs once
as `X1`. The pinned record's basis independence and field-element range are
checked separately by `verify_n47_x1_count_run.py`.

For each `X1`, the branches exhaust the possible quadratics:

| Condition | Roots counted in `V` |
| --- | --- |
| `A=B=0` | All `2^24` elements if `C=0`; none otherwise. |
| `A=0`, `B!=0` | The unique root `C/B`. |
| `A!=0`, `B=0` | The unique root `sqrt(C/A)`, computed by 46 squarings in `GF(2^47)`. |
| `A*B!=0` | After `y=(B/A)Y`, solve `Y^2+Y=(C/A)/(B/A)^2`; test both roots `Y` and `Y+1` in `V`. |

`as_setup` eliminates the images of the 47 coordinate basis elements under
the linear map `L(Y)=Y^2+Y`, retaining a preimage for each pivot.
`as_solve` applies the same pivots to the right-hand side. Therefore it
returns a root exactly for right-hand sides in the image of `L`. Because the
named modulus is irreducible of degree 47, `ker L={0,1}`, so these are all
two roots. `inV` performs exact binary linear elimination against the input
basis. For nonzero divisors, `inv` raises to `2^47-2`; carry-less
multiplication followed by reduction modulo the named polynomial implements
field multiplication. The independent receipt checker verifies the named
prime-degree irreducibility test and pins the target argv to this record.

The count accumulator cannot overflow a signed 64-bit integer: it counts at
most `|V|^2=2^48` ordered pairs. The two roots in the last branch are
distinct, and each is counted separately. Thus, assuming the recorded build
implements this source and the bounded target execution completes, a `0`
output means the named Boolean system has no zero. The queued run still must
produce its write-once receipt, pass all frozen controls, and pass the
independent receipt checker. The historical `count_by_sum` zero is a separate
algorithmic observation and does not replace that pending readback.
