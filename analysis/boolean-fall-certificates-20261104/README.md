# Boolean/digit last-fall proof work, 2026-11-04

User request: carry out review items 1--4 for the fixed-degree Boolean/digit
systems used in the experiments. This is the first implementation/proof
tranche, not a completion claim for the entire research request.

| Track | Delivered here | Remaining requirement |
| --- | --- | --- |
| 1. Encoding/closure bridge | Coefficient-generic written bridge with explicit raw/normalized hypotheses; exact ordinary-polynomial normalization repairs; fixed historical full-closure control | Generic Lean normal-form bridge; audits of each production encoding |
| 2. Two-sided certificates | Bounded prime/binary checker: primal row DAGs plus full closure; no seed-kernel oracle; explicit SAT missing-consequence witnesses | Large-instance provenance integration, independent review and replay of named large packets |
| 3. Binary formalization | Nine ordinary-ring Lean theorems: certificate composition, exact LFD from adjacent bounds, SAT lower witness, assignment partition and final localization assembly | Support-aware localization degree proof, generic binary descent, full 3 ell+1 theorem and characteristic-two classification |
| 4. Growing lower bounds | Exact finite separator acceptance criterion, explicit missing-consequence extraction and a tested obstruction to the one-pass shortcut | A parameter-uniform separator construction or degree-controlled reduction; no growth law proved |

## Validation performed

- Nine deterministic regression tests pass, including the historical
  source-bound eight-variable Semaev draw, malformed/tampered certificates,
  a closed superspace without primal provenance, composite moduli,
  prime-field two-sided refutation, and explicit field-equation repairs.
- The historical closure ranks reproduced are **1,11,79**; 53 is the old
  selected degree-three row rank, not the complete closure rank.
- The target module builds with pinned Lean 4.35.0 and Mathlib
  `cfc55fc58714a59dc06e6e79edc6d1d95140d3c2`. The imported CryptoLean revision
  is unchanged. The transitive axiom audit checks nine new theorems with zero
  failures and no compiler-trusting axioms. This is a scoped module build,
  not a full-workspace or independent semantic review.
- Failed build and audit attempts are retained in `validation/`, followed
  by the corrected successful attempts. No scientific parameter sweep,
  benchmark, cloud job, hypothesis promotion or historical-evidence edit ran.

The checker is deliberately finite: at most 12 Boolean variables, prime
coefficients at most 65537, and at most 200,000 primitive proof steps. It
exhaustively checks the Boolean zero set. This is a test instrument, not a
replacement for the large certificate producers. The parser and finite-field
arithmetic are software-tested; they have not been refined to the Lean model.

## Reproduce

```sh
python -m unittest discover -s analysis/boolean-fall-certificates-20261104 -v
python tools/formal_task.py formal/targets/closure-two-sided-certificates-20261104.yaml --validate-only
cd formal
lake build +CryptoResearch.FallDegree.ClosureCertificates
lake env lean --run .lake/packages/CryptoLean/tools/AuditAxioms.lean CryptoResearch.FallDegree.ClosureCertificates
lake env leanchecker --fresh CryptoResearch.FallDegree.ClosureCertificates
```

`certificate.py CERTIFICATE --system-sha256 EXPECTED` accepts externally
supplied certificates only when bound to the caller's expected system hash.
`fixture_builder.py` is a separate deterministic small producer; the checker
never imports it. The checker tests every low-degree kernel direction after
RREF, including combinations of high-degree literal rows.

Read [the mathematical arguments and exact gaps](THEORY.md), the
[proof map](proof-map.json) and [report](report.pdf). The generic written
Boolean bridge is not silently labeled Lean-proved. The prime and binary
ordinary-membership theorems in the sibling repository remain unchanged.
Canonical frontier and performance graphs were checked for relevance and left
unchanged: no new large-instance, family-growth or performance claim is made.

## Continuation

First instantiate the normal-form and support-localization proofs in Lean,
then bind the independent checker to each retained binary/prime digit input.
For the n47 quotient-lift path, emit primitive provenance for seed-kernel rows
before using them for an unconditional upper certificate. For a growing lower
bound, construct pi_D for arbitrarily increasing parameters and prove its
kernel closure, rather than extrapolating a finite table.
The existing [finite-profile problem](../../problems/lastfall-finite-profile-completeness.md)
and [Semaev semantic bridge problem](../../problems/semaev-degree-two-fall-nonzero-bridge.md)
remain open with additive follow-up links. These steps preserve the original
acceptance criteria; the report is not a substitute for their completion.
