# Exact LFD 5 on `fresh-n33-tr0-01`

The named n33 trace-zero system has last fall degree **exactly 5** by the
Boolean-closure definition in the theorem dossier. Its independently checked
D4 quotient map sends 1 to a nonzero value, proving `1 not in W4`. Both fixed
restrictions `a0=0` and `a0=1` have `1 in W4`, so Lemma 1.3 gives `1 in W5`
for the original system. The independent checker replay of the D4 map passed
again with codimension at least 4,888; the retained exact count is zero.
Proposition 1.2 identifies the refutation degree with the last fall degree
for this unsatisfiable Boolean presentation.

The two branch computations were frozen before data under protocol v1. Each
native D4 closure finished with dimensions `[1, 34, 562, 6018, 46938]`,
`W4_one=1`, and all 46,938 degree-at-most-four columns spanned. The independent
Python implementation reconstructs the Semaev descent by Möbius interpolation
and uses a separate integer-row closure. Its early-stop runs found 1 with
rank 46,735; these did not meet protocol v2's full-rank matching rule because
the checker stops on finding 1. Protocol v3 added `FULL_CLOSURE=1` before any
full replay. Both full independent runs then matched every native dimension
and found 1. The independent descent checker also compared every polynomial
of the original and both restricted inputs exactly, not just at sampled points.

| Branch | Native `W4_one` | Full independent `contains_one` | Complete `W4` dimensions |
| --- | ---: | ---: | --- |
| `a0=0` | 1 | 1 | `[1, 34, 562, 6018, 46938]` |
| `a0=1` | 1 | 1 | `[1, 34, 562, 6018, 46938]` |

The original D4 certificate is SHA-256
`b12d74605a9df9147d89d10191a36fa644cdd5fa70ce610c56e26d870a9fe813`.
The input system is SHA-256
`25d5079098df3c122d39b0decd89713256e9bc78b18af461eb3226c47467c05e`.
The branch inputs have SHA-256
`35554a5a2930d6d2c50f54b703fee5567d1ee0d9d9a7adc9acd6af664a8f9616`
and `d9e4ef12bf6970533d28552aa4ad052c8185560f962f3755522031ebe3ccf8ab`.
All six run results, transcript hashes, elapsed times and protocol digests are
in [evidence.json](evidence.json). The small raw transcripts, restricted
inputs, count inference and checker replay are copied under [raw](raw/);
their retained producer copies are under
`/home/ec2-user/fall-degree-data-20261029/n33-branch-d4-screen-20261102/`.
The quantitative [figure](figure.svg) is derived only from those checked
values. `render_figure.py` is its editable source.

The full independent arms in frozen protocol v3 retain a stale
`instrument.commit` value copied from v2. Their actual source file is pinned by
SHA-256 `d44608877d0731646978a52dd4143d04fe51c0d3359d3317d2bdb9d299b2b875`
and committed with the full-closure switch; the frozen record and raw results
are preserved. This result is independently reproduced exact computation,
not a separately exported W4 membership witness. Such a witness would be a
stronger compact certificate for the upper bound.

The previously frozen n33 D5 attempt should not be launched: `1 in W5` means
no valid D5 nonmembership certificate for this named input can separate 1.
The degree-six search therefore moves to other named candidates, with n47–51
remaining unclassified at D5. This report makes no claim about them or an
asymptotic LFD lower bound.
The [named obstruction record](../../../../problems/semaev-n33-d5-nonmembership-impossible.md)
keeps the frozen n33 request from being retried as a degree-six search.
