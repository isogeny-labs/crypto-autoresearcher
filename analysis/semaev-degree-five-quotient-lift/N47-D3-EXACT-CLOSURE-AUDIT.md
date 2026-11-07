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
lower bound. A separate source audit or independent direct rank calculation
is still needed before promoting the n47 D4 quotient kernel to exact $W_4$.
For a positive D5 nonmembership certificate, Proposition 1.5 needs only
the checked D4 inclusion and does not depend on this stronger exactness.
