#set page(margin: 0.7in)
#set text(font: "Liberation Sans", size: 10pt)
#set heading(numbering: none)

= A checked 49-variable seed for the n50 degree-five search

The affine-sliced n50 polynomial03 quotient map has been rebased into the unit-triangular format required by the degree-five worker. The 1,120,585,872-byte output has SHA-256 `2f0facb6b047c857908e7f44e8558248af426dae10454263294df1a93d39cce8`. An independent checker accepted degree-4 nonmembership with codimension at least 38,629, including a nonzero image of 1.

#image("flow.svg", width: 100%)

The #link("https://github.com/isogeny-labs/crypto-autoresearcher/releases/download/semaev-closure-certificates-20261029/fresh-n50-poly-03-D5-cascade01-bounded-D4-001.D4.cert.gz")[published original certificate] has raw SHA-256 `6a25ce310435e564b5487975c17de90f2903a401e8721d95781cf7049f688719`. The certified affine equation with combination mask `0x13c4f635ad45c` eliminates variable 25. Projection produced an independently accepted 49-variable degree-4 map. The projected map retained 37,687 literal unit coordinates and lacked 942; the accelerated rebase solved those 942 coordinates and the independent checker accepted the output again. The transfer statement is Proposition 2.5b of the theorem dossier.

== Conversion records

#table(
  columns: (2fr, 2fr, 1fr),
  inset: 5pt,
  [Attempt], [Terminal outcome], [Wall time],
  [Python full basis], [Terminated; no output], [1,337.1 s],
  [Native full basis], [One-hour timeout; no output], [3,600.3 s],
  [Native missing-coordinate], [Output independently accepted], [29.6 s],
)

These attempts have different completion states and are not a matched speed comparison. The fast code matched the generic rebase on an exhaustive 11-row kernel fixture and a 73-coordinate multiword fixture. A wrong hash was refused. The migrated host's n6 checkpoint-free control reproduced its retained hash, emitted no checkpoints, and refused a bad seed hash.

The capacity profile gives 40,927 degree-five border coordinates and 79,556 working coordinates. Its bounded-export formula estimated 34,760,782,170 bytes; the running worker binary reported 35,385,141,521 bytes at admission. Both are below the frozen 36 GiB child cap. These figures are allocation bounds, not measured peak RSS. The degree-five result is recorded separately under protocol V2 and requires a separate checker before any LFD lower-bound claim.

The complete local file paths, byte counts, SHA-256 values, and process receipts are in `evidence.json`. The published original certificate and committed source provide a replay route for the rebased seed.
