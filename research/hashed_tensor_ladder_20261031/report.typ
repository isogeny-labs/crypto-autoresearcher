#set page(margin: 1.6cm, numbering: "1")
#set text(size: 10pt)
#set par(justify: true)
#set heading(numbering: none)

= Hashed-factor-base tensor ECDL at 40--80-bit prime fields

_Observation record, 2026-10-31. Analysis and compile-only measurement; no contraction, count, solve or attack
was run. Hidden constants of every bound are set to 1, which favours the algorithm. Not independently reviewed._

== Result

The Bochum hashed-factor-base ECDL counts a Boolean network of N variables in time 2^(N/√log2 N).
Beating rho needs that exponent below (1/2 − 1/m)·ℓ. The compiled prime-field relation networks have
1.7·10^5 to 3.1·10^6 variables, so the exponent is *1,480 to 10,110 times* rho's at every size from 40 to 131
bits and every slot count from 2 to 7 (figure, table).

#figure(image("exponents.svg", width: 100%), caption: [Counting exponent over rho exponent, from `compile-stats.json`.])

#figure(
  table(columns: 5, align: (right,)*5, stroke: 0.4pt + luma(180),
    [ℓ], [m], [Variables N], [E = N/√log2 N], [E/(ℓ/2)],
    [40],
    [2],
    [170 440],
    [40 885],
    [2 044],
    [40],
    [4],
    [422 644],
    [97 764],
    [4 888],
    [40],
    [7],
    [800 950],
    [180 864],
    [9 043],
    [64],
    [2],
    [199 204],
    [47 478],
    [1 484],
    [64],
    [4],
    [486 952],
    [112 029],
    [3 501],
    [64],
    [7],
    [918 574],
    [206 387],
    [6 450],
    [80],
    [2],
    [338 352],
    [78 947],
    [1 974],
    [80],
    [4],
    [839 020],
    [189 138],
    [4 728],
    [80],
    [7],
    [1 590 022],
    [350 318],
    [8 758],
    [131],
    [2],
    [654 523],
    [148 909],
    [2 273],
    [131],
    [4],
    [1 622 421],
    [357 205],
    [5 454],
    [131],
    [7],
    [3 074 268],
    [662 216],
    [10 110]),
  caption: [Selected rows. All 42 rows, edges, degrees and multiplication blocks are in `compile-stats.json`.])

== Encoding-independent floor

With full ℓ-bit coordinate unknowns N ≥ m·ℓ, so the condition needs
√log2(m·ℓ) > 2m²/(m−2), minimised at m = 4: ℓ > 2^254 at unit constants
(`crossover.py`, tested). Index-valued unknowns do not escape: one big vertex pads to ℓ^(10/9) edges or needs
2^ℓ evaluations, and split vertices carry ℓ-bit partial sums.

== Size floors in the proofs

Bochum/OpenAI: saving only for networks of size at least 2^(2^17). Kintali: N0(s) ≥ 2^(3·10^7).
Anthropic: beats 2^n only for n > 10^10,000. Every compiled network is below all of these, so the code runs
its exact-summation fallback, which is enumeration over free input bits.

== Scope

Descriptive. No speedup or attack-cost advantage is claimed, so no progress-fidelity record is added. Sources,
provenance and the unfiled known-result drafts are in `HASHED_TENSOR_REVIEW.md` and `KR_DRAFTS.md`.
