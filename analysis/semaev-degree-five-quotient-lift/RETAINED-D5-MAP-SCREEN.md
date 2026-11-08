# Retained degree-five map screen for the degree-six search

At commit `521f0d04f9ac323922fe6faa3d4be57db0e5e2af`, I read every
tracked `degree5.bin` and `certificate.bin` under
`analysis/semaev-degree-five-quotient-lift/validation/`, plus the retained
`reports/n51-poly01-d5-stream-001/preflight/candidate.bin`. The 89
validation files include maps of other degrees and one deliberately malformed
certificate. Filtering by a degree-five header and exact SHA-256 leaves only
the following three distinct maps (21 copies total):

| Variables | Quotient dimension | SHA-256 | Copies |
| ---: | ---: | --- | ---: |
| 6 | 1 | `95a21c42135f0eb6d9b6d2f50beaea4c54d281027e61f2611e40495f8f0dfd69` | 9 |
| 6 | 3 | `7cf2d46d96fe00dfddd1277935c7f0b6577c7ab9cbdc774151c81f56fee82d73` | 7 |
| 8 | 1 | `c8daa04c3c8b55e52e6366335c7c9e09e7e8af3dcbb9e8c378856648711a726c` | 5 |

The dimension-three map is the named n=6 instance with modulus `0x43`,
`a2=0`, `a6=3`, target `z=2`, and factor-base basis `(1,2,4)`.
`verify/cert_check.py` accepts that exact map as `1 not in W_5` with
codimension at least three. I independently enumerated all 64 ordered
factor-base pairs using the field equation

```
((x*y + x*z + y*z)^2 + x*y*z + a6) mod (X^6+X+1) = 0,
```

where addition is XOR and multiplication is polynomial multiplication
reduced modulo `0x43`. The only zero pairs, expressed as factor-base values,
are `(0,4)`, `(1,1)`, and `(4,0)`. The independent descended Boolean
equations also have exactly the three assignment masks `0x4`, `0x9`, and
`0x20`. Thus this map's **certified codimension lower bound of three equals
the exact solution count of three**; it does not satisfy Proposition 1.4's
strict-inequality premise for an LFD-at-least-six claim. This does not prove
that its full `W_5` has codimension exactly three.

The direct field check can be replayed without the descent or certificate
code:

```python
def mul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 0x40:
            a ^= 0x43
    return out

V = range(8)  # basis (1,2,4)
zeros = []
for x in V:
    for y in V:
        s = mul(x, y) ^ mul(x, 2) ^ mul(y, 2)
        if mul(s, s) ^ mul(mul(x, y), 2) ^ 3 == 0:
            zeros.append((x, y))
assert zeros == [(0, 4), (1, 1), (4, 0)]
```

For either one-dimensional map, a valid nonmembership certificate with
nonzero image of one is scalar. Remark 1.5a shows that this map is evaluation
at a Boolean solution, so its certified codimension lower bound of one cannot
exceed the solution count. The archive screen therefore contains no retained
degree-five quotient map that, together with its named solution count,
already establishes the sought degree-six lower bound. The n47 D5 producer
and independent zero-count replay remain the direct path.

## Local high-memory n47 polynomial-subspace D5 maps

The tracked-file screen above did not include three retained local results in
`/home/ec2-user/fall-degree-data-20261029/frontier-highmem-001/`. I checked
their D5 headers, SHA-256 digests, recorded count output, and independent
`check5.stdout.txt` terminal line on 2026-11-07. All have 48 Boolean
variables, degree five, 1,925,357 columns, and a two-dimensional quotient.

| Named run | D5 SHA-256 | Count output | Checker terminal result |
| --- | --- | ---: | --- |
| `fresh-n47-poly-01-D5-cascade01-highmem01` | `89e859e7397ee2c3ab3745c8c112e7c4d79f6e32a4f6e7400ed5642c7b07a781` | 2 | `VALID: 1 not in W_5`, codimension at least 2 |
| `fresh-n47-poly-02-D5-cascade01-highmem01` | `c15ab4eb2cfb6dd3080ca28f784abded2c0c44d4da135e91335f0e0ab6c4f3d3` | 2 | `VALID: 1 not in W_5`, codimension at least 2 |
| `fresh-n47-poly-04-D5-cascade01-highmem01` | `bdf5052f2a135f9276531523eef4153b4147236171235ed59453aa36b220cab8` | 2 | `VALID: 1 not in W_5`, codimension at least 2 |

These are additional checked nonmembership results, not three degree-six
lower bounds. Their certified codimension lower bound equals the recorded
exact solution count, so Proposition 1.4's strict-inequality bridge does
not apply. This inspection reuses the retained run receipts and checker
outputs; it does not claim a fresh independent count replay or a new D5 run.

The local `native-lift-historical-001` directory also contains two named n35
degree-five maps omitted from the tracked-file screen. `Q35a-D5-lift01` has
SHA-256 `a3ffa75b43e8e6a5ceffa44c4e26fa37e435bb80b00ff506f5627a8d371fff89`,
checker-accepted codimension at least six, and recorded count six.
`Q35b-D5-lift01` has SHA-256
`ae57630b8ffb2c5d282ca1c17ab1467e24c44891c915fcf7ee52e7236ea26691`,
checker-accepted codimension at least two, and recorded count two. Both are
36-variable degree-five maps with 443,704 columns. Again, each certified
codimension lower bound equals its recorded count; neither supplies the
strict gap needed for an LFD-at-least-six claim.

The original screen above was a read-only screen of tracked artifacts, not a
new closure run. The
maps' headers and hashes do not substitute for independently checking each
map; the accepted n=6 dimension-three map was rerun through
`verify/cert_check.py` with its named parameters.

## Mainline proof and candidate update (2026-11-08)

The newer mainline report
`reports/n33-branch-d4-screen-001/report.md` proves **exact LFD 5** for the
fresh trace-zero n33 instance. Both fixed restrictions `a0=0` and `a0=1`
have independently reproduced full D4 closure containing one, while the
original D4 quotient certificate excludes one. The branch restriction lemma
then gives `1 in W5` for the original input. Its frozen n33 D5 request is
therefore not a degree-six candidate and must not be launched for that aim.
This conclusion is specific to that n33 input; it does not classify n47.

Mainline also contains `analysis/rigorous-lfd-solving-20261105/THEOREM.md`:
an independently reviewed written proof of
`4+floor(s/2) <= d_F <= sd_sigma(F) <= 2s+1` for the specified prime-field
two-block digit presentation of one S3 equation. Its full-closure step uses
injectivity of multiplication by the degree-four top form in a low-degree
range, then bounds the Boolean zero set to exhibit an ideal consequence
outside the closure. At `s=4` this gives a rigorous LFD lower bound of six
for that **prime-field presentation**. It is not a characteristic-two result:
`problems/remaining-binary-obligations.md` identifies the missing binary
top-form/injectivity invariant and requires exact full-closure separators for
an unbounded binary family. The review is mathematical prose, with no full
Lean formalization of the prime theorem and no official scientific-status
transition.

For the present binary degree-six search, prioritize the named n47 random00
input's independent exact count and full D5 quotient check under its frozen
plans. The three checked n47 polynomial-subspace D5 maps above already have
codimension lower bound two and recorded count two, so they cannot supply the
strict-gap bridge as currently certified. A branch-D4 screen can rule out a
candidate if **both** restrictions contain one, as at n33, but it is only an
additional upper-bound route; it does not replace the n47 D5/count checks.
Proposition 2.5e in the theorem dossier gives another lower-bound route:
a degree-five nonmembership certificate for *any* affine restriction of
the n47 system lifts to the original system. Unlike the exact trace slice,
this one-way transfer does not require the restriction to be a consequence
of the original equations. Fixing four variables would reduce the
degree-at-most-five monomial domain from 1,925,357 (48 variables) to
1,235,994 (44 variables); whether such a restricted system retains
degree-five nonmembership is unknown. The original exact-zero bridge
still requires the queued independent recount.
