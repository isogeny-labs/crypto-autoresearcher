# n47 random00: exactness of the direct D3 seed

Proposition 1.8 in the theorem dossier proves the pivot-marked direct
closure algorithm exact when it reaches a fixed point without an early
constant. This audit applies that source argument to the retained n47
random00 degree-three seed. It does **not** assert that the subsequent
degree-four quotient-lift map is an exact $W_4$ quotient.

The original `fresh-n47-rand-00-D5-cascade01/attempt-001` recorded a
successful `produce3` invocation of `lfdclose2` at degree three, followed
by an independent `cert_check.py` acceptance of the resulting map. Its
terminal stdout says:

```
M3_dims 0 1 140 2302 M3_one 0
W3_dims 0 1 141 5546 W3_one 0 iters 2 ncols 18473
```

The iteration log gives ranks 2302, 5499 and 5546; the last iteration
found `new_low 0`. The certificate header is `(48, 3, 18473, 12927)`,
and `18473 - 5546 = 12927`. These are the hypotheses and numerical
conclusion of Proposition 1.8, assuming the retained executable faithfully
implements the published source.

| Retained item | SHA-256 |
| --- | --- |
| named `input.sys` | `b8ee56830e9b7f064c4cfe17579b512dd3f7b01e62fd0575b6632a37f2ec936c` |
| D3 certificate | `ee92818caa402f34b9ffe8f61d00db95f1ab73d74b8bed120fbfb08d353a5bb1` |
| `produce3.stdout.txt` | `82ede70ba5ebc6a6e1f7414077f628e641ff718ac631a4d83a8899e7d36141e3` |
| `produce3.stderr.txt` | `1041d30334e27c1094808dd23a21bc2a6f959e67f8f56f9303a65bd687da8b4e` |
| terminal `result.json` | `4f7ac8cc8cb1060d50344ecddf591e2c64d7dbabafac2a2c5044982381dc3cd4` |
| `code/lfdclose2.c` at source commits `3965c88d` and `fdd9cb0b` | `2413e3a3f34d0fdda8a53b0d62acff53aeaabc593b1c55fe42a3d7db8af3cc4f` |
| invoked `lfdclose2` executable | `f7f920e697b263129e91b44814e18c32b228392496770c29869ab4d00a9e6f04` |
| published `runtime-provenance.json` | `91050ba4ff9b361f98d80864e6a8e2635d552bba66f93c43dc9c0f969f4cb9e7` |

The published runtime provenance names that executable hash, GCC 11.5.0,
and source revision `fdd9cb0b...`. The original attempt records source
revision `3965c88d...`; the `lfdclose2.c` blob has the same hash at both
revisions. The provenance is a published source/binary custody record, not
an independent bit-for-bit rebuild. The independent checker establishes
that the map is onto, annihilates the named equations, is closed, and keeps
one nonzero. Proposition 1.8 plus the direct producer's terminal rank
supports the stronger exact-seed reading

```
dim W_3(F) = 5546,  codim(W_3(F) in B_<=3) = 12927,
```

under the usual source-to-executable and retained-execution assumptions.
The independently checked quotient alone proves only the codimension
lower bound. The D4 quotient kernel still needs its own exactness audit;
the D3 computation below does not establish it.

## Independent exact D3 replay, 2026-11-08

`replay_binary_d3_closure.py` reconstructs the named Boolean equations from
the frozen `n47-rand00-d5-local-plan-002.json` field parameters. It checks
all 1,177 degree-at-most-two coefficients by Boolean interpolation of the
original S3 expression, then matches every monomial of every row in the
retained original-coordinate `input.sys`. The input SHA-256 is
`b8ee56830e9b7f064c4cfe17579b512dd3f7b01e62fd0575b6632a37f2ec936c`,
the same hash recorded above. It computes the Macaulay rank and the full
iterated Boolean D3 closure in the invertible `(a,c=a+b)` coordinates using
a separate Python integer-row echelon implementation. Every newly found
degree-at-most-two row is multiplied by all 48 variables until the queue
is empty; no degree-three row is multiplied above the cap.

The independent replay gives `M3=2302`, `M3_low=140`, `W3=5546`,
`W3_low=141`, `W3_contains_one=false`, and 18,473 D3 columns. It therefore
reproduces the native full-closure dimensions, not just its accepted
quotient. The result and plan/input hashes are recorded in
`validation/n47-rand00-d3-independent-replay-001.json`. The two different
implementations now support exact `dim W3=5546` without a source-to-native-
executable equivalence premise. This is still a finite named-input result;
it does not prove n47 D4/D5 exactness or LFD at least six.

The replay also finds the 47 input equations independent. Therefore the
94-dimensional top-form linear-multiplier syzygy space classified in
`BINARY-BILINEAR-TOP-HOMOLOGY.md` yields 93 independent degree-at-most-two
falls modulo those input equations: `M3_low - rank(F) = 140 - 47 = 93`.
The single dependency has a structural representative. The trace relation
is the affine Boolean polynomial `ell_0=L(c)+epsilon`, with nonzero linear
part `L(c)=Tr(s)` on this named factor base. Boolean idempotence gives
`ell_0*L(c)=(1+epsilon)*L(c)`, which is either zero or `ell_0` modulo the
input span. Thus its linear-variable products have one relation modulo the
inputs. Since the rank calculation loses exactly one dimension, this
accounts for the entire loss from 94 top syzygies to 93 new low rows.
Iterating the closure adds one further independent low-degree row, reaching
141. These counts identify the exact degree-three mutation budget that a
parameter-uniform lower-bound argument must account for; they do not say
that analogous counts hold for other inputs or at higher caps.
For a positive D5 nonmembership certificate, Proposition 1.5 needs only
the checked D4 inclusion and does not depend on this stronger exactness.
