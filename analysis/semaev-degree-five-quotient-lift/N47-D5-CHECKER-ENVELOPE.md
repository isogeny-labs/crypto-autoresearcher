# n47 sliced D5 certificate: checker admission envelope

The candidate checker `check_sliced_certificate_factorized.py` reads the
standard dense quotient-map file without copying its row payload into a
Python list. It maps the entire file read-only and keeps an elimination pivot
pair for each independent image of a degree-at-most-four monomial. This is a
source-derived size screen, **not** a measured peak-memory or runtime result.

For 47 variables and degree five there are exactly

```
C5 = sum(binomial(47, i), i=0..5) = 1,729,648
C4 = sum(binomial(47, i), i=0..4) =   195,709.
```

At quotient dimension `q`, the format uses
`row_bytes = 8 * ceil(q / 64)` and
`file_bytes = 32 + 8*C5 + C5*row_bytes`. The file mapping contributes
`file_bytes` to virtual address space even if not all pages are resident.
The factorized closure test retains at most `min(q,C4)` paired pivots, each
holding two `q`-bit values. Its two bit-vector payloads therefore use at most
`2 * min(q,C4) * ceil(q/8)` bytes before Python object, tuple, dictionary,
monomial-mask, field-descent, and interpreter overhead. This expression is
an allocation envelope for the pivot values, not a total RSS estimate.

| q | Exact file bytes | File GiB | Paired-pivot bit payload GiB |
| ---: | ---: | ---: | ---: |
| 61,196 (the existing sliced D4 codimension, for scale only) | 13,256,022,304 | 12.346 | 0.872 |
| 79,360 | 17,171,945,376 | 15.993 | 1.466 |
| 100,000 | 21,641,355,808 | 20.155 | 2.328 |
| 158,848 | 34,357,727,904 | 31.998 | 5.875 |

The D5 codimension is **unknown**; it need not be bounded by the D4
codimension because degree-five monomials enlarge the domain. A 16-GiB
address-space limit cannot even map the file when `q > 79,360`, and at that
threshold the mapping alone nearly fills the limit. Even at `q=61,196`,
the remaining address space does not by itself prove that Python's other
objects and pivot values fit. A future D5 checker protocol must read the
actual header, compute the exact file size, reserve room for all allocations,
and stop before verification if the chosen finite cap cannot accommodate it.
The protocol must also bind the checker, closure helper, descent and slice
source hashes, and the certificate hash. The CLI now verifies the plan,
descent, slice, closure-helper, and certificate digests it consumes.

Reproduce the table with the integer formulas above; no frontier closure,
producer, or checker run was used for this screen. The frozen D4 checker and
its 16-GiB stage limit are unchanged.
