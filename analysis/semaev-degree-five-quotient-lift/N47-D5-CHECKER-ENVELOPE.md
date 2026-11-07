# n47 sliced D5 certificate: checker admission envelope

The candidate checker `check_sliced_certificate_factorized.py` reads the
standard dense quotient-map file without copying its row payload into a
Python list. Its default `pread` mode reads one row at a time without mapping
the payload; `--row-access mapped` retains the earlier read-only whole-file
mapping. Both modes keep an elimination pivot pair for each independent image
of a degree-at-most-four monomial. This is a source-derived size screen,
**not** a measured peak-memory or runtime result.

The CLI now has two explicit scopes. `--variable` checks an affine-sliced
certificate in 47 variables; `--full-original` independently descends the
named original system in 48 variables, the format produced by the frozen
`n47-rand00-d5-local-002` attempt. The full mode accepts the retained n6 D5
map and rejects a slice-only mask. At the illustrative quotient dimension
61,196, an original-system D5 map has 1,925,357 columns and occupies
14,755,936,080 bytes (13.743 GiB); its actual D5 dimension is unknown.

For 47 variables and degree five there are exactly

```
C5 = sum(binomial(47, i), i=0..5) = 1,729,648
C4 = sum(binomial(47, i), i=0..4) =   195,709.
```

At quotient dimension `q`, the format uses
`row_bytes = 8 * ceil(q / 64)` and
`file_bytes = 32 + 8*C5 + C5*row_bytes`. In mapped mode the file contributes
`file_bytes` to virtual address space even if not all pages are resident.
In `pread` mode the complete file still must exist on disk, but it contributes
no whole-file mapping.
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
codimension because degree-five monomials enlarge the domain.
For a genuinely unsatisfiable instance, Proposition 1.10 of the theorem
dossier also rules out a degree-five nonmembership quotient with fewer
than five coordinates. This is a mathematical floor, not an estimate of
the actual n47 quotient size.

A 16-GiB address-space limit cannot use mapped mode when `q > 79,360`,
and at that threshold the mapping alone nearly fills the limit. `pread` mode
removes that address-space gate. It does not establish a peak-RSS or runtime
bound: the monomial index and pivot values remain in memory, and repeated row
reads may be costly. A sparse-file fixture with logical size above 256 MiB
opened and read in `pread` mode under a 256-MiB address-space cap, while
whole-file mapping was refused; retained degree-four and degree-five
certificates gave the same checker results in both modes. A future D5 checker
protocol must read the actual header, compute the exact file and pivot sizes,
reserve room for allocations and disk, and stop before verification if its
finite cap cannot accommodate them.
The protocol must also bind the checker, closure helper, descent and slice
source hashes, and the certificate hash. The CLI now verifies the plan,
descent, slice, closure-helper, and certificate digests it consumes, and
rehashes the certificate after checking to detect in-place changes during
verification.

Reproduce the table with the integer formulas above; no frontier closure,
producer, or frontier-scale checker run was used for this screen. The frozen
D4 checker and its 16-GiB stage limit are unchanged.
