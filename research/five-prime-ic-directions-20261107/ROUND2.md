# Round 2: nonvacuous transport and collector integration

The user authorized continuation after the first construction round. The first
invocation in CHECKS-round2.md passed all seven strengthened tests; its raw log
is checks/round2-attempt1.txt. No timing or relation-yield claim is made.

## Checked changes

- **69:** replace the empty coordinate-window control with every nonidentity
  point of each endpoint subgroup. Both endpoint row lists must be nonempty and
  have positive rank. Every normalized row satisfies its scalar equation and
  the combined rank remains bounded by the number of global columns minus one.
  This closes the vacuous-loop coverage gap. Because the complete subgroups
  normalize to the same point set, it does not test new factors from digit bases.
- **71:** membership_circuit shares homogeneous N,D evaluations without expanding
  a polynomial. Explicit endpoint selection preserves individual membership
  answers. Every F101 input agrees with symbolic factors at levels 0 through 3;
  poles exclude all later endpoints. Operation-count instrumentation is pending.
- **56:** the sufficient integer-zero certificate now rejects nonpositive or
  noninteger bounds/moduli, missing variable bounds and rational coefficients.
  This prevents silently truncated zip products from certifying an invalid box.
- **87:** each existing fixed-base control now calls the repository's real scalar
  decompose_all and arity-2 TailTable collector, with acceleration disabled.
  Their canonical relation sets agree and are nonempty, and every returned row
  belongs to the exhaustive planted multiset oracle and passes the group check.
  The collector's documented nonzero-remainder restriction is retained; full
  recall of arbitrary cancelling tuples and first-rejection instrumentation are
  not asserted. Three factor-base families and arities 3 and 4 are covered.
- **58:** previous exact elimination and lift regressions remain passing.

## Delivery repair

PR 3125's original head passed benchmark-record, runtime, ledger and formal
checks. Both failed artifact jobs identified the same 70,922-byte report.pdf.
The unchanged PDF was uploaded using the repository artifact tool; its SHA-256
and byte count are in .artifacts.json. Hydrate with:

    python3 tools/artifacts/artifacts.py pull research/five-prime-ic-directions-20261107

The original PDF and earlier check/coverage logs describe round 1 and are
preserved. This note supersedes their outstanding row-coverage statement.
See NEXT.md for remaining work. No experiment or external generator was started.
