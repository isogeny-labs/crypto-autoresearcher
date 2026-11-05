#set page(width: 210mm, height: 297mm, margin: 18mm)
#set text(font: "Liberation Sans", size: 10pt)
#set heading(numbering: none)

= Exact LFD 5 on `fresh-n33-tr0-01`

The named n33 trace-zero Boolean Semaev system has last fall degree exactly
*5*. The independent D4 quotient checker verifies that the image of 1 is
nonzero and the quotient has dimension at least 4,888. Both restrictions
`a0=0` and `a0=1` contain 1 in their degree-four closure. The dossier's
branching lemma therefore puts 1 in the original degree-five closure.
The exact solution count is zero, so the refutation degree equals the last
fall degree for this presentation.

#image("figure.svg", width: 100%)

Both native branches and both complete independent Python replays found
`1 in W4` and the same cumulative dimensions
`[1, 34, 562, 6018, 46938]`. The independent code reconstructs the
descended system by Möbius interpolation. A separate polynomial-by-polynomial
check matched the original and both restricted inputs. Early-stop independent
runs found 1 at rank 46,735; their smaller rank reflects their stated stop
condition and was preserved in protocol v2. Protocol v3 fixed complete
replays before they were run.

The original D4 certificate SHA-256 is
`b12d74605a9df9147d89d10191a36fa644cdd5fa70ce610c56e26d870a9fe813`.
The raw transcripts and their hashes are indexed by `evidence.json` beside
this report. Frozen protocol v3 has a stale `instrument.commit` field for
the full independent arms; the actual source is pinned by SHA-256
`d44608877d0731646978a52dd4143d04fe51c0d3359d3317d2bdb9d299b2b875`.
The upper bound is independently reproduced exact computation; an explicit
standalone membership witness has not been exported.

This named n33 D5 nonmembership attempt should not run: the verified branch
computations imply 1 is already in W5. The degree-six search continues on
other named inputs, including the still-unclassified n47–51 frontier.
