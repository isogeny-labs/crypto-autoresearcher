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

This is a read-only screen of tracked artifacts, not a new closure run. The
maps' headers and hashes do not substitute for independently checking each
map; the accepted n=6 dimension-three map was rerun through
`verify/cert_check.py` with its named parameters.
