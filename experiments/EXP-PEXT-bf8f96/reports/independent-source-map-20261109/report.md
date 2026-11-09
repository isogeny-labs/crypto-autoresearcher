# Independent source-map replay for one exceptional PEXT row

**Scope:** Source-only design increment for EXP-PEXT-bf8f96 and H-PEXT-c3a11d. The experiment remains `review_required`, `frozen: false`, and without a trial plan or approval. No scientific cohort ran.

## Literature and assumption check

The draft's retrieved [square-class and descent paper](https://eprint.iacr.org/2015/805.pdf), sections 3.1–3.2 and Example 3.2, distinguishes square-class conditions from an actual order-n Frobenius descent. Its cubic rank-two irreducible-module square-coefficient condition is a special case, so this source-coordinate check makes no general admissibility claim. The bound [Type-II branch slides](https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), slides 25–26, concern a separate hyperellipticity criterion. Existing repository sources `source_map_binding.py`, `source_fixed_unit.py`, and `independent_source_fixed_check.py` supplied the exact source and checker interfaces.

## Construction

`independent_source_map_check.py` implements separate exact arithmetic for rational functions `(a(x)+b(x)y)/d(x)` over the named nonsingular elliptic model. It recomputes the original and scalar-preserving moved quartics, reads the serialized forward x/y maps as exact functions, and checks both quartic equations and the projective and elliptic inverse identities. `source_fixed_unit.py` now also checks published cohort, class, T, ordinal, plan hash, offset, and independently unranked matrix against `CandidateBinder` before it accepts the map check. The existing independent fixed-algebra and character-genus checks remain required for this one-row result.

## Checks and boundary

Seven focused source-map, source-fixed-unit, and independent fixed-model tests passed. Fixed F27 tests cover zero and nonzero T, identity and nonidentity projective matrices, map-byte mutations, source-identity mutation, incorrect ordinal matrix, and incorrect genus. The updated status explicitly says `one_exceptional_source_fixed_row_checked; full_descent_and_minimum_pending`.

This establishes a checked source boundary for supplied exceptional rows. It does not establish complete class/T/structure coverage, certified full-cohort descent statuses, counterexample metadata, final C5 blind custody, H1 q13, all controls, runtime qualification, a lawful lane, trial-plan/RUN allocation, a runbook, or protocol freeze/approval. The read-only preapproval probe remains `approvable:false` with those prospective execution records absent.
