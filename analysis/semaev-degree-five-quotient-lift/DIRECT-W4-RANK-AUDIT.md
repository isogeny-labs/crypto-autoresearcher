# Why the queued direct n51 calculation targets the exact W4 rank

This is a source-level audit of the
[direct Boolean closure algorithm](../semaev-m2-last-fall-degree/code/lfdclose2.c).
The terminal n51 calculation and its hashed receipts are in the
[rank report](reports/n51-direct-w4-rank-terminal-20261105/report.md). The
fixed sliced input has 51 variables and 51 quadratic generators, with
15,189 term masks checked term by term against the independent generator
export. Its degree-at-most-four monomial universe has 272,052 columns.
The initial degree-four Macaulay span has 51 times
(1 + 51 + 1,275) = 67,677 generator multiples. These counts follow from
the committed input and the source's monomial enumeration.

Let M4 be the span of all generator multiples whose unreduced degree is at
most four. Every such multiple belongs to W4: multiply a generator by
its monomial one variable at a time, never passing degree four. The source
starts with an echelon basis of M4, then repeatedly multiplies newly found
rows of degree at most three by every variable and adds their products.
Every added row is therefore a valid W4 consequence. Conversely, when no
new low-degree row remains to multiply, the final rowspace contains the
generators and is closed under every allowed multiplication. Minimality of
W4 then gives equality.

The source orders columns by decreasing total degree. In an echelon
rowspace, rows whose pivots have degree at most three span exactly its
intersection with the degree-at-most-three subspace: a combination
containing a row with a degree-four pivot cannot cancel its earliest such
pivot. This justifies multiplying only the low-pivot rows. The source
marks pivots of M3 as already multiplied. For a marked pivot, its M3
representative has every variable product in M4. The current low-pivot
representative differs from it by a combination of later low-pivot rows.
Descending induction on pivot order shows that multiplying those later
rows suffices for the difference; the same argument applies after each
echelon update. Thus the mark skips redundant products, not closure steps.

This audit establishes the mathematical invariant implemented by the
direct fixed-point algorithm, conditional on its recorded input,
arithmetic and successful termination. A numeric rank printed by one
native process remains an observed computation until its input and binary
hashes, stdout, exit and resource receipt are checked; an independent
rank replay or proof object would strengthen the machine evidence.
The SHA-pinned n51 D4 quotient already proves that W4 is contained in a
226,437-dimensional kernel. Hence a successful direct rank of 226,437
would give equality of that kernel and W4. A smaller rank would quantify
the seed's excess kernel dimension. A rank above 226,437 or a reported
constant in W4 would contradict the accepted quotient certificate and
require input or implementation diagnosis.

The first pretrial build failed because its default include path lacked
M4RI; zero rank trials ran at that stage. The
[amended protocol](n51-poly01-direct-w4-rank-protocol-002.json) reused the
prior SHA-pinned runtime binary under the same cumulative budget. Its
single direct trial exited zero after 6,636.46 seconds and reported rank
226,437, `W4_one 0`, and three fixed-point iterations. The finish hashes
match the archived streams and the input hash matches the independently
reconstructed equations. Consequently the direct algorithm's computed W4
dimension equals the accepted quotient kernel dimension. This checks
seed equality on the sliced polynomial-01 instance under the source
invariant above; it neither checks the original polynomial-00 seed nor
supplies an LFD-six certificate.
