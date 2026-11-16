# n50 sliced D4 rebase: kernel-preservation source audit

The n50 polynomial03 affine slice was checked as a degree-four quotient
before and after a fast rebase. This note audits what the rebase source
computes. It is a mathematical/source audit tied to retained build and
output receipts, **not** an independent full-size replay of all rebase rows.

The input `degree4-sliced.bin` has 49 variables, degree four, 231,526 rows,
codomain dimension 38,629, and SHA-256
`e15eaf5f9b314637fed9421f4d1526f193d3e8202b500e94dd5c6523be8484b6`.
The output `degree4-rebased.bin` has the same dimensions and SHA-256
`2f0facb6b047c857908e7f44e8558248af426dae10454263294df1a93d39cce8`.
An independent full-size check has now verified an invertible codomain
change of basis across all 231,526 rows. See
`N50-REBASE-FULL-ROW-VERIFICATION.md` for the separate checker and terminal
receipt. The source audit below remains a distinct argument about the
producer's implementation.
The build receipt records source SHA-256
`937609a04115abbca2a683e5894449e13005e345e3e965d079a78b088d967fa1`
for `rebase_quotient_certificate_fast.cpp` and binary SHA-256
`9a3c29874f38024886e511386207f3a10ce90895f90ef79bb2483bbc8f1d120f`.
The tracked source at the pushed revision and the retained binary rehash to
those values. The start receipt names exactly that binary and input;
the terminal receipt records exit zero and the output digest. The separate
slice checker accepted the output.

The code retains 37,687 old coordinates whose selected monomial rows are
literal unit vectors. It marks the other 942 coordinates as missing. For
each source row $v$, write $v_M$ for its projection onto those missing
coordinates. Reverse elimination selects 942 source rows $p_i$ whose
projections $(p_i)_M$ form a basis of the missing-coordinate space. The
code refuses if it cannot select all 942. Its `pivot_value` and
`pivot_expression` arrays compute the unique coefficient vector $c(v)$
such that $v_M=\sum_i c_i(v)(p_i)_M$.

The row written by the implementation is precisely

$$T(v)=v+\sum_i c_i(v)p_i+\sum_i c_i(v)e_{m_i},$$

where $e_{m_i}$ is the new unit vector assigned to the $i$th missing
coordinate. The first two terms cancel every old missing coordinate; the
last term writes the coefficient vector there. For a retained unit vector
$e_r$, $c(e_r)=0$ and $T(e_r)=e_r$. For a selected $p_i$,
$c(p_i)=e_i$ and $T(p_i)=e_{m_i}$. The 37,687 retained units together with
the 942 selected $p_i$ form a basis of the old codomain: their projections
span the missing coordinates, and the retained units span the complement.
Therefore $T$ maps one basis to another and is invertible. **If the binary
executed the audited source on the pinned input**, every output row is
$T$ of the corresponding input row and the two quotient maps have exactly
the same kernel. The later independent full-row check confirms kernel
equivalence directly from the retained input and output bytes.

Proposition 2.5f then identifies the original and sliced *seeded* D5
closure quotients using this verified kernel equivalence. The sliced D5
producer's full-rank report would predict a killed constant for the queued
original n50 run from the same D4 seed. That report lacks a separately
checkable relation transcript, and the D4 seed has not been independently
proved exact $W_4$. Neither exact LFD 5 nor an LFD-six lower bound is
claimed here. A checked D5 relation transcript and exact W4 seed evidence
remain necessary to turn
the prediction into a rigorous original-system membership result.
