# Trace-sliced certificate route

Proposition 2.5b of the [theorem dossier](../semaev-m2-last-fall-degree/theorem-dossier.md)
proves that, when the equation span contains a nonconstant affine trace
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
zero, so **this reduction does not apply to n50 polynomial03**. The existing
n50 D5 continuation retains its original memory, checkpoint, and cost gates.

The [n51 polynomial01 request](n51-poly01-d5-stream-request-001.json)
(SHA-256 `d74ea19216814bcfa2f316fb70a3d785e9be99fc7820c15222d609e093fd5684`)
has trace vector `(1,0,...,0)` on its 26 basis vectors. Eliminate Boolean
variable 26, the first $b$ coordinate. The independently rebuilt equation
span gives the exact substitution
$b_0=a_0+\operatorname{Tr}(a_6/z^2)$; the checker recomputes this identity
from the field record before testing any certificate. This leaves 51
variables and preserves the named system's Boolean solution count.

`slice_trace_certificate.py` copies the accepted D4 map rows that do not
contain the eliminated variable, renumbering monomials and retaining the
quotient coordinates. It checks the source digest and shape but does not
claim to verify closure. `check_trace_slice_certificate.py` reconstructs the
named Semaev equations with the original independent descent, checks their
trace consequence, substitutes the variable, and checks surjectivity, all
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
acceptance threshold. The existing unsliced n51 protocol is not silently
repurposed. The current daily Spot budget readback exceeds its $25 limit;
no projection or native frontier run was started under this packet.
