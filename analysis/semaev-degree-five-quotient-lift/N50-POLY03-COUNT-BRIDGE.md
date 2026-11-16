# n50 polynomial-03: retained zero-count and D4 proof bridge

`check_n50_poly03_count_bridge.py` checks the named frozen panel plan, the
retained terminal result and stage outputs, the invoked `count_by_sum` binary
and its published source/binary provenance, the accepted original-system D4
map, and its public certificate-readback receipt. Its machine-readable output
is `validation/n50-poly03-count-bridge-custody-001.json`. It reports zero
ordered solutions, `1 not in W_4(F)` with certified codimension at least
38,629, and no independent count rerun or binary rebuild. Thus Proposition
1.2 of the theorem dossier gives the named computer-verified LFD lower bound
five on the retained computation; a D5 lower bound six still needs a new
checker-accepted D5 map.

The field polynomial is `0x400000000001d`, of degree 50. Rabin's criterion
has two proper prime-divisor checks because `50=2*5`. Repeated squaring
modulo this polynomial gives `X^(2^50)=X`; Euclidean gcds with
`X^(2^25)-X` and `X^(2^10)-X` are both one. The 25 factor-base values are
exactly `1,X,...,X^24`, so they are independent in the resulting field.

The source-level count argument applies equally to even degree 50. For
`s=x1+x2 in V`, put `u=x1*x2/z` and `alpha=a6/z^2`. The Semaev equation is
equivalent to `u^2+u=s^2+alpha`. The Artin–Schreier map has kernel `{0,1}`
and image the trace-zero subspace in every finite binary field, including
`GF(2^50)`. For each of its zero or two `u` roots, `s=0` gives the unique
square root `x1=x2=sqrt(z*u)`. When `s!=0`, the remaining equation
`x1^2+s*x1=z*u` has zero or two roots by the same trace test; each yields
the ordered pair `(x1,s+x1)`, and both coordinates belong to `V` exactly
when `x1` does. Exhausting all `2^25` values of `s` therefore counts every
ordered solution once. The retained counter source enumerates this split;
the detailed source audit for the same binary is in
`N47-RAND00-SOLUTION-COUNT-BRIDGE.md`.

The accepted D4 map has SHA-256
`6a25ce310435e564b5487975c17de90f2903a401e8721d95781cf7049f688719`.
Its compressed [release asset](https://github.com/isogeny-labs/crypto-autoresearcher/releases/download/semaev-closure-certificates-20261029/fresh-n50-poly-03-D5-cascade01-bounded-D4-001.D4.cert.gz)
and hash-checked anonymous download are bound in
`bounded-d4-archive-001/fresh-n50-poly-03-D5-cascade01-bounded-D4-001.publication.json`.
The D5 profile in `validation/n50-poly03-d5-4096-preflight-001/result.json`
is allocation arithmetic, not a D5 certificate or measured peak memory.
