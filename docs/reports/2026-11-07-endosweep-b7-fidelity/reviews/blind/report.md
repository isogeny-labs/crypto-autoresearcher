# Independent blind arithmetic review

**Arithmetic verdict: HOLDS.** The supplied integers satisfy `q + 1 - t = h*n`, the proposed factor product equals positive `N = 4*q - t*t`, and the mechanically constructed `s`, `D`, and `d` satisfy the requested exact bounds. The unique integer in `2^L <= |D| < 2^(L+1)` is **L = 512**. This report evaluates these arithmetic statements only.

**Fundamental-discriminant certification: INCONCLUSIVE in this review.** The two large proposed factors have not been certified prime or squarefree here. Their primality is unnecessary for the arithmetic verdict. No assertion about a named curve's actual trace or cardinality is made from the supplied integers.

## Input and independent method

The sole supplied task input was `docs/reports/2026-11-07-endosweep-b7-fidelity/blind-input.md`, whose SHA-256 is `7a31209c5ababaa1f8786fb5e24b8fa166c96e93209e72d717186c42fdf9d4fa`.

The input integers were transcribed directly into an original Python script, [independent_arithmetic.py](independent_arithmetic.py). It uses Python 3.9.25 arbitrary-precision integer arithmetic, `math.prod`, `math.gcd`, `math.isqrt`, and integer `bit_length`; it does not use floating-point logarithms, the producer's implementation, external data, or a primality-testing library. [independent-output.json](independent-output.json) is the complete output, including exact residuals and assertion results. The process exited with status 0.

All exponents in the supplied factor list are 1. Therefore the mechanical odd-exponent product `s` equals the complete listed product, regardless of whether the bases are prime. For positive `s`, the candidate construction used is `D = -s` if `s % 4 == 3`, and `D = -4*s` otherwise. Euclidean remainders use Python's `%` with positive modulus; in particular, the negative odd candidate has `D % 2 == 1`.

## Exact results

The order-shaped integer identity is:

```text
q + 1 - t = h*n = n =
8948962207650232551656602815159153422162609644098354511344597187200057010413418528378981730643524959857451398370029280583094215613882043973354392115544169
```

The independently calculated discriminant magnitude and factor product agree exactly:

```text
N = 4*q - t*t = factor_product = s =
17863548565954307441941406889656077155667958808835207116490401702324728995784608238347442801873591918020244561841276732336347795144160599880952413486884947

s mod 4 = 3

D =
-17863548565954307441941406889656077155667958808835207116490401702324728995784608238347442801873591918020244561841276732336347795144160599880952413486884947

D mod 2 = 1

d = (|D| + 1)/4 =
4465887141488576860485351722414019288916989702208801779122600425581182248946152059586860700468397979505061140460319183084086948786040149970238103371721237
```

An additional arithmetic identity, `d = q - (t*t - 1)/4`, holds exactly. The division is integral because `t` is odd.

The exact bounding powers are:

```text
2^512 =
13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084096

2^513 =
26815615859885194199148049996411692254958731641184786755447122887443528060147093953603748596333806855380063716372972101707507765623893139892867298012168192

2^510 =
3351951982485649274893506249551461531869841455148098344430890360930441007518386744200468574541725856922507964546621512713438470702986642486608412251521024
```

Thus `2^512 <= |D| < 2^513`, `|D|` has 513 bits, and `L = 512`. The integer satisfying both inequalities is unique. The second requested bound holds with the positive exact margin:

```text
d - 2^(L-2) = d - 2^510 =
1113935159002927585591845472862557757047148247060703434691710064650741241427765315386392125926672122582553175913697670370648478083053507483629691120200213
```

The lower bound on `d` also follows directly from its definition and the first bound: `D mod 2 >= 0` gives `d >= |D|/4 >= 2^(L-2)`. It supplies no additional squarefreeness evidence.

## What needs primality or squarefreeness

| Conclusion | Required evidence |
| --- | --- |
| `q + 1 - t = h*n`, positivity of `N`, exact factor multiplication | Integer arithmetic only. |
| Mechanical odd-exponent product, candidate `D`, Euclidean remainder, `d`, and both bounds | Integer arithmetic only. |
| `N = s*a^2`, where `a` is the product of listed bases to their halved exponents | Holds algebraically for arbitrary integer bases and nonnegative exponents. Here `a = 1`. It does not prove that `s` is squarefree. |
| The listed bases form a prime factorization | Each listed base must actually be proved prime, with distinctness and the complete product established. |
| Mechanical `s` is the squarefree part of `N` | Distinct prime bases suffice. For this all-exponent-one input, pairwise coprime squarefree bases also suffice; primality is stronger than necessary. |
| Candidate `D` is the fundamental discriminant of `Q(sqrt(-N))` | Squarefreeness of the positive `s` is needed in addition to the checked decomposition and residue rule. A proof that the bases are distinct primes would supply it. |
| Supplied `t` is a particular curve's trace and `h*n` its cardinality | Requires a connection to the actual curve and a cardinality/trace argument. Even proving every proposed factor prime would not establish this connection. |

All three pairwise gcds are exactly 1. The base 557 is prime by exhaustive divisibility checks for every integer from 2 through `floor(sqrt(557)) = 23`. No primality or squarefreeness claim is made for the two larger bases. Consequently the fundamental-discriminant conclusion remains conditional on their squarefreeness in this review.

The elementary discriminant rule used above is: for squarefree positive `s`, the field `Q(sqrt(-s))` has fundamental discriminant `-s` when `s == 3 (mod 4)` and `-4*s` otherwise. Applying the same expression to nonsquarefree `s` does not retain that conclusion.

## Negative controls

**One-digit mutation: BREAKS the exact factor-product identity.** Replacing only the first listed factor `557` by `558`, with the supplied `q`, `t`, and other factors fixed, produces:

```text
mutated_factor_product =
17895619568765715534296777458578260418065926418904929211852143895686173751611869653497079144426327271553494552077975613363881633196484047995639940261547218

mutated_factor_product - N =
32071002811408092355370568922183262397967610069722095361742193361444755827261415149636342552735353533249990236698881027533838052323448114687526774662271
```

The nonzero residual equals the exact product of the unchanged second and third factors, as the one-unit change predicts. The control tests this review's multiplication check only.

**Composite-factor logical counterexample: BREAKS the implication from arithmetic checks to fundamental discriminant.** Take `q = 16`, `t = 1`, and the distinct, coprime proposed bases `(9, 1)` and `(7, 1)`. Then:

```text
N = 4*16 - 1^2 = 63 = 9*7
s = 63, s mod 4 = 3
D_candidate = -63, D_candidate mod 2 = 1, d_candidate = 16
L = 5, 32 <= 63 < 64
d_candidate = 16 >= 2^(5-2) = 8
gcd(9, 7) = 1
```

Every displayed arithmetic check holds, yet `s` is divisible by `3^2` and is not squarefree. Since `Q(sqrt(-63)) = Q(sqrt(-7))`, its fundamental discriminant is `-7`, and `-63 = 3^2 * (-7)` is not fundamental. This is a counterexample to the logical implication; it does not allege that any supplied large factor is composite. The toy `q` is an integer as allowed by the blind input and is not being used as a field cardinality or curve instance.

## Commands, artifacts, and isolation

Working directory for every command was `/var/tmp/endosweep-b7-fidelity-20261107`. Exact shell commands executed, in sequence except the final two independent checks which ran concurrently, were:

```bash
cat docs/reports/2026-11-07-endosweep-b7-fidelity/blind-input.md
mkdir -p docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind
python3 docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/independent_arithmetic.py > docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/independent-output.json
cat docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/independent-output.json
python3 --version
sha256sum docs/reports/2026-11-07-endosweep-b7-fidelity/blind-input.md docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/independent_arithmetic.py docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/independent-output.json
```

The original script and this report were authored with `tools.apply_patch`; the script's complete source is included as an artifact. No existing implementation was copied. Artifact SHA-256 values are:

```text
be4d5740d72d6921550607b7febb5d88e78a574e35165cea0f28f0ee2f5e96e3  independent_arithmetic.py
ae14cfbc107040e4a79ab82aa11af68198e7b53377562b7a58bba873bb0cdc0b  independent-output.json
```

Complete list of task/workspace file paths read by inspection, execution, or hashing:

1. `/var/tmp/endosweep-b7-fidelity-20261107/docs/reports/2026-11-07-endosweep-b7-fidelity/blind-input.md`
2. `/var/tmp/endosweep-b7-fidelity-20261107/docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/independent_arithmetic.py` — original scratch script from this review, read by Python and SHA-256.
3. `/var/tmp/endosweep-b7-fidelity-20261107/docs/reports/2026-11-07-endosweep-b7-fidelity/reviews/blind/independent-output.json` — original scratch output from this review, read by `cat` and SHA-256.

Ordinary operating-system, shell, Python interpreter, and standard-library loading was not traced; the path list records all task/workspace inputs, not the runtime's system library accesses. No generic reference or web source was consulted.

**Isolation attestation:** I inspected only the designated blind input and my own arithmetic artifacts. I did not read `review-plan.md`, the producer's README or data, Lean source or target, receipts, sibling reports, repository history, prior conversation, or memory files. I made no git commit, push, cloud submission, or external write. The verdict is independent of the producer's implementation and any claimed Lean result.
