# J3 blind review: BSGS coverage and finite curve count

Task: `TASK-20261103-016b84` / Conductor `T-1470`. First-phase joint owned: J3 blind coverage and exceptional-case derivation. Verdict: **holds** for the mathematical coverage statement and the concrete curve premises specified in `blind-input.yaml`.

## Exact index coverage

For a natural width `m > 0`, the division algorithm gives the unique pair

`i = floor(k/m)`, `j = k mod m`, with `k = i*m + j` and `0 <= j < m`.

The extra bound `i < m` holds exactly when `k < m*m`. Thus the represented natural exponents are precisely `0, ..., m*m-1`. Both endpoints are sharp: `k=m*m-1` has `(i,j)=(m-1,m-1)`, while `k=m*m` has unique quotient/remainder `(m,0)` and fails the giant-index bound. For `m=0` there are no admissible indices, including at `k=0`; division by `m` is unavailable. For `m=1`, only `k=0` is represented.

For any group point `G`, the points reached by these pairs are exactly `{[k]G : 0 <= k < m*m}`. If `G` has finite order `r`, these exhaust `<G>` exactly when `m*m >= r`: the canonical exponents `0, ..., r-1` are all present, and if `m*m < r` their points remain distinct, so `[m*m]G` is a missing point. Reaching every point of an ambient group additionally requires the premise that the ambient group equals `<G>`; a larger table cannot reach a point outside that subgroup.

The exact-exponent and point statements have different boundaries. An integer `k=m*m` never has a valid pair, yet its point can coincide with one at a smaller exponent when the order of `G` permits wraparound.

## Independent arithmetic for the supplied curve

I used the short-Weierstrass curve `E: y^2 = x^3 + 3*x + 20` over `F_1048571`. The attached standard-library script checks primality of `p=1048571` by trial division through `floor(sqrt(p))`, and checks `4*a^3 + 27*b^2 = 10908 (mod p) != 0`, so the curve is nonsingular. For each of all `p` values of `x`, it uses Euler's criterion to compute the quadratic character of `x^3+3*x+20`; a zero contributes one affine point, a square two, and a nonsquare none. The 16 consecutive block subtotals are retained in `arithmetic.json`.

The character sum is `-883`, with zero right-hand sides `0`, giving `#E(F_p) = p + 1 - 883 = 1047689`. Trial division through `floor(sqrt(1047689))` establishes this order is prime. The supplied `G=(2,199837)` has `y^2 = x^3+3*x+20 = 34 (mod p)` and is not infinity. Independent double-and-add also returns `[1047689]G=O`. Since the finite curve group has prime order, every nonidentity point, in particular this `G`, has order `1047689`; consequently `<G>=E(F_p)`. These are the premises connecting the index result to **every** curve point.

The least width with complete point coverage is `m=1024`: `1023^2=1046529 < 1047689 <= 1024^2=1048576`. At width `1023`, exactly `1160` curve points are missing, with `[1046529]G=(111890,936064)` an explicit first missing point. At width `1024`, all `1047689` points are present and `887` of the `1048576` exponent positions repeat earlier points. The exact-exponent control `k=1024^2` fails with quotient/remainder `(1024,0)`, while its point is `[887]G=(198823,583449)` and is already represented.

## Controls and claim scope

| Control | Result |
| --- | --- |
| `m=0`, `k=0` | No admissible `i` or `j`; coverage is empty. |
| `m>0`, `k=m*m-1` | Covered by the unique pair `(m-1,m-1)`. |
| `m>0`, `k=m*m` | No admissible pair; quotient is `m`. Point reachability must be checked modulo `ord(G)` separately. |
| Width `1023` on the supplied curve | `[1046529]G` is absent, since this exponent is less than prime order `1047689`. |
| Point outside a chosen subgroup | Impossible in the verified instance with the supplied `G`, because `<G>=E(F_p)`. As a premise check on this same curve, choose instead `G'=O` and `Q=(2,199837)`: `Q` is outside `<G'>={O}` and no width reaches it. |

This verdict concerns the stated mathematics and the independently enumerated finite curve. It is not an assessment of producer proof or solver files, which were outside the blind inputs.

## Reproduction and evidence

From the isolated snapshot root, run `python3 output/count_and_controls.py > output/arithmetic.json` using Python 3.8 or newer. The script uses constant-size state plus 16 block records, asserts the supplied order and boundary checks, and prints the raw enumeration summaries. No scientific trial, cloud job, or memory-heavy build was run.

Before this first report was frozen, the substantive inputs read were only the snapshot `README.md`, `blind-input.yaml`, and `TASK-20261103-016b84.yaml`, plus public mathematical definitions recalled without consulting another source. The read attestation records the complete access list and sibling isolation.
