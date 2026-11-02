# Affine-sliced certificate route

Proposition 2.5b of the [theorem dossier](../semaev-m2-last-fall-degree/theorem-dossier.md)
proves that, when the equation span contains any nonconstant affine
equation, substituting one Boolean variable preserves every degree-at-most-$d$
closure for $d\ge2$. A degree-five nonmembership certificate for the sliced
system therefore proves the same nonmembership for the original system. A
fresh zero-solution count then gives LFD at least six for that named original
presentation. The proposition is a written proof, still awaiting external
mathematical review; the scripts below are a prospective instrument, not a
completed frontier certificate.

The [n50 polynomial03 frozen plan](n50-poly03-d5-local-no-checkpoint-plan-002.json)
(SHA-256 `88a92372e9466b0e9ecbb11b1bf5554533955844068f4aa378b79e21e6da3730`)
has trace zero on all 25 basis vectors. Its trace consequence is constant
zero. However, exact elimination of the quadratic parts of its 50 independently
descended equations has rank 48. One of the two dependencies is the zero
polynomial; the other, selected by coefficient mask
`0x13c4f635ad45c` in the independent descent's polynomial-bit coordinate
order, is the nonzero affine equation

$$\sum_{j\in J}(a_j+b_j)=0,\qquad
J=\{0,3,5,6,9,10,12,14,15,17,18,20,23\}.$$

The checker recomputes this combination from the pinned field record and
rejects it unless it is affine and contains the eliminated variable. Thus
**n50 polynomial03 can be sliced using this different relation**: eliminate
variable 25 ($b_0$), leaving 49 variables. Projecting its accepted D4 map
with codimension 38,629 would have 231,526 monomial rows and a calculated
1,120,585,872-byte file, versus the retained 1,215,691,872-byte original.
These sizes follow from the certificate format; no frontier projection or
D5 run has occurred. The existing n50 D5 continuation retains its original
memory, checkpoint, and cost gates until a new sliced protocol is frozen.
The nonzero affine equation also supplies $r=1$ in Proposition 2.5a, so the
fresh zero count and accepted D4 certificate give the rigorous named-instance
interval $5\le d_{\rm LFD}\le26$ ($k=25$). This upper bound does not resolve
whether the last fall degree is five or at least six.
The short [affine-relation certificate](n50-poly03-affine-relation-001.json)
is independently reconstructed by [its checker](check_affine_relation.py).
The [accepted result](validation/n50-poly03-affine-001/result.json), SHA-256
`02244547686a97894cfd05a6aa3926aafe66ec107754793f214baceadbb6ccc9`,
binds the plan, independent descent source, relation mask, quadratic rank 48,
and verifier source. A tampered pair list is rejected by the focused test.

The [n51 polynomial01 request](n51-poly01-d5-stream-request-001.json)
(SHA-256 `d74ea19216814bcfa2f316fb70a3d785e9be99fc7820c15222d609e093fd5684`)
has trace vector `(1,0,...,0)` on its 26 basis vectors. Eliminate Boolean
variable 26, the first $b$ coordinate. The independently rebuilt equation
span gives the exact substitution
$b_0=a_0+\operatorname{Tr}(a_6/z^2)$; the checker recomputes this identity
from the field record before testing any certificate. This leaves 51
variables and preserves the named system's Boolean solution count.
The quadratic coefficient matrix has rank 50 across 51 equations, so the
trace relation spans its entire affine-dependency space. Likewise, n50's
quadratic rank 48 leaves two dependencies: one zero polynomial and the single
nonzero relation above. Degree-two equation combinations therefore provide
one affine elimination on each of these named inputs; further size reductions
would require a different algebraic relation or a different presentation.
Proposition 2.5d explains the quadratic ranks: with
$P=\operatorname{span}\{uv:u,v\in V\}$, the quadratic rank is
$\dim P-\mathbf1_{z\in P}$. Exact field multiplication on these plans gives
$(\dim P,z\in P)=(49,\mathrm{true})$ at n50 and $(51,\mathrm{true})$ at n51,
hence ranks 48 and 50. This predicts the number of affine-or-zero equation
dependencies before doing the full Boolean descent; their nonzero affine
content still has to be checked.

Corollary 2.5c extends exact slicing to any affine relation in $W_d$, so a
degree-three fall could have supplied another eliminable variable at D5.
The exact [degree-three closure check](check_affine_w3.py) processes every
new degree-at-most-two fall and its variable products until no row is added.
On the named n50 plan it obtains $\dim W_3=8130$, low-degree intersection
dimension 196, and affine dimension one, with the relation above as its sole
affine basis element. On the named n51 plan the corresponding dimensions are
10970, 254, and one, with only the trace relation. The focused test replays
both calculations from independently descended named equations. Thus $W_3$
does not enable a second slice on these inputs; affine falls first appearing
at D4 or D5 require a separate check.

The accepted D4 quotient maps rule out a new affine fall at D4 as well. The
[affine-row checker](check_affine_d4_rows.py) rehashes each full certificate,
the original checker's named-input argv and acceptance transcript, then reads
only the constant and variable rows. For n50, the 51 affine rows have rank 50,
and their unique kernel vector is the already certified relation
`0x25b59a52dacd2` in constant-first variable coordinates. For n51, the 53
affine rows have rank 52, with only the trace relation `0x8000002`. The
[n50 result](validation/n50-affine-d4-rows-001.json) and
[n51 result](validation/n51-affine-d4-rows-001.json) pin the exact certificate,
checker, argument, transcript, plan and row-checker hashes. Since the full
checker accepted each map, $W_4$ lies in its kernel; the known affine relation
already spans the one-dimensional affine kernel. Therefore each named system
has **exactly one affine relation in $W_4$**, and no second D4 affine slice is
available. This uses the retained full-certificate acceptance, not just the
small row check. A new affine relation in $W_5$ remains possible.

`slice_trace_certificate.py` copies the accepted D4 map rows that do not
contain the eliminated variable, renumbering monomials and retaining the
quotient coordinates. It checks the source digest and shape but does not
claim to verify closure. `check_trace_slice_certificate.py` reconstructs the
named Semaev equations with the original independent descent, checks either
the trace consequence or an explicit equation-combination mask, substitutes
the variable, and checks surjectivity, all
equations, nonzero constant, and every low-kernel variable product. It tests
surjectivity by rank because a projected map need not retain a literal unit
row for every quotient coordinate. A passing D4 check supplies a smaller
accepted seed for a separately frozen D5 continuation. A later D5 map must
pass the same checker and the count-versus-codimension gate before any LFD
at least six claim.

The retained odd-$n$ software fixture `odd-a2-0` has an original-checker
accepted 944-byte D4 certificate, SHA-256
`d8552a13d300bcbec10966b52092d3754975716fd50062bab3b347b85dfbc6a9`.
The focused test projects it to a five-variable certificate with SHA-256
`dc7c6c6f6f9594f1b33963a431d63c310d3780ea7337fc8902cd84dcb5920838`
and the new checker accepts the independently sliced equations at D4 with
codimension one. This validates a real named control for the instrument; its
solution count is also one, so it establishes no new LFD lower bound.

The separate retained n6 `cascade-20261029-v2/0` control exercises the
**nontrace affine-combination path** needed by n50. All three basis traces
vanish, but the independently descended equation combination `0x24` is
$a_0+b_0=0$. Its original-checker-accepted D4 certificate has SHA-256
`cfe306125fef4482fb86b15966c7be5ec6e26ed5ca09d5addafd2c5f9e079c4a`.
Projection gives a five-variable D4 map with SHA-256
`59cd20d3de0fde08b5d34490a9895a0f7c3d14830b8136e78e926260f28741e0`;
the new checker accepts codimension three after reconstructing the six named
equations. The fixture's count is three, so this is qualification of the
nontrace instrument, not a new LFD bound.

The retained original n50 D4 certificate has SHA-256
`6a25ce310435e564b5487975c17de90f2903a401e8721d95781cf7049f688719`
and was accepted with codimension at least 38,629 against a fresh zero count;
see the [D4 report](reports/n50-poly03-bounded-d4-publication-001/report.md).
The prospective n50 projection/check commands, after custody and budget
admission, are:

```sh
python3 analysis/semaev-degree-five-quotient-lift/slice_trace_certificate.py \
  /path/to/accepted-n50-degree4.bin /path/to/sliced-n50-degree4.bin \
  --variable 25 \
  --expect-source-sha256 6a25ce310435e564b5487975c17de90f2903a401e8721d95781cf7049f688719
python3 analysis/semaev-degree-five-quotient-lift/check_trace_slice_certificate.py \
  /path/to/sliced-n50-degree4.bin \
  --plan analysis/semaev-degree-five-quotient-lift/n50-poly03-d5-local-no-checkpoint-plan-002.json \
  --expect-plan-sha256 88a92372e9466b0e9ecbb11b1bf5554533955844068f4aa378b79e21e6da3730 \
  --expect-descent-source-sha256 b6e28168091986b3cb04790f51889723db0ec5838633767bb80a6dc4ac97bd70 \
  --variable 25 --affine-combination-mask 0x13c4f635ad45c
```

The retained original n51 D4 certificate has SHA-256
`c160792a7530b20dd17affcdabafb8d95494eed51c8ee6d818af3212f3e304f6`
and was accepted with codimension at least 45,615 against a fresh zero count;
see the [D4 report](reports/n51-poly01-d4-20261101/report.md). The intended
projection/check commands, after custody and budget admission, are:

```sh
python3 analysis/semaev-degree-five-quotient-lift/slice_trace_certificate.py \
  /path/to/accepted-degree4.bin /path/to/sliced-degree4.bin \
  --variable 26 \
  --expect-source-sha256 c160792a7530b20dd17affcdabafb8d95494eed51c8ee6d818af3212f3e304f6
python3 analysis/semaev-degree-five-quotient-lift/check_trace_slice_certificate.py \
  /path/to/sliced-degree4.bin \
  --plan analysis/semaev-degree-five-quotient-lift/n51-poly01-d5-stream-request-001.json \
  --expect-plan-sha256 d74ea19216814bcfa2f316fb70a3d785e9be99fc7820c15222d609e093fd5684 \
  --expect-descent-source-sha256 b6e28168091986b3cb04790f51889723db0ec5838633767bb80a6dc4ac97bd70 \
  --variable 26
```

Before a native D5 run, freeze a new protocol with the checked sliced seed,
source and checker digests, resource envelope, exact count, and independent
acceptance threshold. Existing unsliced n50 and n51 protocols are not silently
repurposed. The current daily Spot budget readback exceeds its $25 limit;
no projection or native frontier run was started under this packet.
