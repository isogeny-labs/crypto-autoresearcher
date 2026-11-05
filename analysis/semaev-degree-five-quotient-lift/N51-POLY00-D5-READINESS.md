# n51 polynomial-00 as the next degree-five candidate

The retained original-system D4 attempt for `fresh-n51-poly-00` has a
checker-accepted quotient of dimension 45615, SHA-256
`90878ee8bc6bda02957f25728380a9e677cd13b0f46c9eed1828349da796f115`.
Its local seed file is present at 1,680,493,280 bytes. The exact counter
returned six solutions. These values come from the published
`bounded-d4-archive-001/fresh-n51-poly-00-D5-cascade01-bounded-D4-001.receipt.json`
and the retained local stdout, not from a D5 run.

Lemma 1.7 gives a useful gate. If the D4 kernel on this instance is
exactly W4, then its D5 lift cannot kill one and its quotient dimension
is at least six. A separately checked D5 quotient of dimension seven
or more exceeds the six-solution count and proves LFD at least six.
Dimension six would not. The D4 checker alone establishes containment
of W4 in its kernel, so this prediction is conditional on seed exactness;
even without exactness, a surviving independently checked D5 quotient
of dimension at least seven would still prove the lower bound.

The published profile predicts 2,893,164 degree-at-most-five monomial
columns, 103,867 working coordinates and 58,252 border coordinates.
Applying the blocked-rewrite source's exact allocation formula at
`chunk_rows=4096` gives a payload of 45,294,452,256 bytes and an
admission envelope of 61,214,619,409 bytes, below a 64 GiB child cap
by 7,504,857,327 bytes. This is a **source-derived admission estimate**,
not measured RSS or a guarantee that a run fits. The profile's older
60,000-row formula is not a launch authorization. A launch still needs
the exact seed hash checked in place, fresh count, published source and
protocol, live lock/budget/capacity checks, one bounded attempt, and an
independent D5 certificate check if a candidate survives.

For replay, the source hash is
`b9cbe65514244d15b2a4de1c653783d50322ba18e9334eb5891f348dd487c0cf`.
Set `stride = ((103867+63)//64+2)*8` and
`seedstride = ((45615+63)//64+2)*8`. The payload is
`(2893164+4096)*stride + 294204*seedstride +
(3*103867+4*4096+45615)*stride + (45615+4096)*seedstride +
2893164*40 + 52*45615*8 + 52*4096*8 +
(45615+4096)*stride + 4096*seedstride`; the envelope is
`payload*135//100 + 64*2**20`.
As an arithmetic control, substituting the completed n51 polynomial-01
slice's values (`N=51`, 2,621,112 next-degree columns, 272,052 seed
columns, 103,877 working coordinates, 45,615 quotient coordinates)
reproduces its native admission printout exactly:
56,287,272,208 bytes. This checks the formula against one real producer
admission, not the poly00 memory peak or future feasibility.

The current n51 polynomial-01 direct-W4 rank trial owns the frontier
high-memory slot. This note does not authorize a concurrent poly00 D5
trial or change any existing deadline, reservation or retry ceiling.
