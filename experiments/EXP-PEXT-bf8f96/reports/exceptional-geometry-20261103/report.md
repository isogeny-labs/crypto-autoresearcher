# EXP-PEXT-bf8f96: exact geometry of overlapping branch supports

The support calculator now resolves the geometric rank, union size, connected quotient cover and genus when Frobenius-conjugate quartic branch supports overlap. It forms the finite squarefree support of each quartic, records infinity separately, and closes their symmetric differences. The number of distinct parity supports is `2^m`, where `m` is the geometric square-class rank. The union has `r` projective branch points. For `m >= 2`, Riemann–Hurwitz gives `g = 1 + 2^(m-2)(r-4)`; for `m = 1`, `g = (r-2)/2`. A character-subcover genus sum is checked separately against that formula. These statements apply to a verified conjugate, squarefree family with its quotient provenance bound externally.

On the complete fixed F27 join **software fixture** (1,638 positions), the existing generic classifier found 1,358 disjoint and 280 overlapping positions. The 280 overlapping positions split as follows; the columns are geometric rank `m`, projective union size `r`, geometric genus `g`, and fixture count:

| m | r | g | count |
|---:|---:|---:|---:|
| 1 | 4 | 1 | 2 |
| 3 | 8 | 9 | 18 |
| 3 | 9 | 11 | 52 |
| 3 | 10 | 13 | 208 |

For every overlapping fixture position, the separate polynomial-product square-relation checker gives exactly `2^(n-m)` geometric relation masks, matching the support rank. Duplicate-branch and broken-conjugacy mutations reject; the all-identical family gives rank one. [The source-bound test log](software-tests.json) records the command, versions, output and source digests. The fixture is an instrument check, not a P1–P4 cohort result. The table is not stratified by nonzero T branch type and cannot decide P2.

The new result discharges the geometric rank/genus computation for an emitted exceptional row. The remaining throughput dependency is an exact generator of **all** exceptional structure indices with an independent completeness certificate. Constant square classes, coefficient twists, Frobenius descent, Type2 and full-cohort analysis remain separate checks. EXP-PEXT-bf8f96 remains `review_required`; no protocol was frozen and no scientific trial was launched.
