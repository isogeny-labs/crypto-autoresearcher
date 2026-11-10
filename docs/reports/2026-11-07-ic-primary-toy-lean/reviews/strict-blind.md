# T-1868: strict-blind scalar rederivation

## Input and access boundary

I used only `docs/reports/2026-11-07-ic-primary-toy-lean/blind-input.json` at SHA-256 `f698ef19770b457919060a1b06cc62fd82c314362618a42e11305722993f02c4` as mathematical input. The complete list of repository files whose contents I read is that one JSON file. I did not read an expected-output file, producer implementation, sibling review, review plan, addendum, archive, workload, or Git history. I did not access the web. I ran `conductor --help`, `conductor task --help`, and `conductor task claim T-1868` for task administration; these commands did not supply mathematical data. My Python arithmetic was supplied ephemerally through standard input and was not read from a file.

## Independent arithmetic

The field is represented by 13-bit integers, with addition as XOR and multiplication as carryless polynomial multiplication reduced modulo

`m(z) = z^13 + z^5 + z^2 + z + 1` (`0x2027`).

For nonzero `a`, inversion used `a^8190`; multiplication verified `a * a^8190 = 1` on each division. For distinct points `P=(x,y)`, `Q=(u,v)` on `y^2 + xy = x^3 + 1`, I used

`lambda = (y+v)/(x+u)`, `X = lambda^2 + lambda + x + u`, `Y = lambda*(x+X) + X + y`.

For doubling with `x != 0`, I used

`lambda = x + y/x`, `X = lambda^2 + lambda`, `Y = x^2 + (lambda+1)*X`.

The identity was represented by `None`; vertical pairs and a point with `x=0` doubled to the identity. I computed every successive multiple up to the largest requested scalar by repeated addition, then checked each requested result with a separate binary double-and-add schedule. All ten schedules agreed. The generator `(2995,1571)` has curve residual zero.

## Results

| Scalar `k` | `k*(2995,1571)` | Curve residual for finite result |
|---:|---:|---:|
| 2003 | point at infinity | not applicable |
| 1045 | `(1082,7387)` | 0 |
| 1046 | `(2659,1282)` | 0 |
| 1047 | `(7851,3095)` | 0 |
| 605 | `(560,1201)` | 0 |
| 606 | `(6749,6034)` | 0 |
| 607 | `(6721,2942)` | 0 |
| 860 | `(3537,3092)` | 0 |
| 861 | `(4412,6211)` | 0 |
| 862 | `(5120,5987)` | 0 |

For the additional point `(2659,1283)`, the equation's left side `y^2 + xy` is `1922`, and its right side `x^3 + 1` is `3552`. Their XOR residual is `2658` (`0x0a62`), so this point is **not on the curve**.

These are independent results from the supplied definitions. No comparison with expected outputs was performed.
