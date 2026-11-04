# Canonical range compiler

Additive implementation of the published fixed software contract in
`coordination/prime_sat_range_compiler_20261031/`. `compile_block` rebuilds the
trusted rationality circuit and substitutes little-endian field bits.
`compile_range` supports a caller-authenticated generic layout. Document
comparison includes types; witness evaluation is separate from authentication.

Range equations use compressed prefix-product states. The bootstrap CNF uses
value bits only. `complete_transcript` retains the original records and appends
range-empty prefix certificates, then calls the unchanged prefix adapter over
the full cube. Missing domain-valid branches remain explicit gaps. Censored
transcripts retain their status. The compiler does not implement chart-wide
collection or invoke SAT.

The producer suite consists of the 18 frozen fixed obligation groups. The first bounded attempt passed 246 assertions across all 18 groups. Exact
command, source snapshots and hashes, checkpoint receipt, stdout, stderr and
exit status are retained in `software-results.json`. Independent review is
pending; these are producer software checks.
Prime field validity and the reviewed symbolic builders are explicit premises.
