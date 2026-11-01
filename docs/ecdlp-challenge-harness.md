# ECDLP challenge harness

The harness exposes six index-calculus engineering frontiers backed by the
native `crypto` verifier: relation generation, factor-base selection, sparse
linear algebra, descent, transfer certification, and orbit-folded relations.
The first committed fixture is a deterministic 19-point known-answer subgroup.
It tests the contribution and verification path; it does not measure a
standard curve or establish a speedup.

The tracks attach to existing named obstructions rather than declaring them
solved:

| Track | Existing research problems it can exercise |
| --- | --- |
| RelationForge | [prime-field arity-3 oracle](../problems/prime-field-arity3-relation-oracle.md), [holdout rank/coverage](../problems/prime-field-holdout-rank-and-target-coverage.md) |
| FactorBaseLab | [natural P-256 relations](../problems/p256-natural-useful-factor-base-relations.md), [PKM decomposition](../problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md) |
| MatrixSmash | [sparse LA adoption](../problems/icex-sparse-la-source-adoption-and-matched-matrix-gap.md), [independent x-rank replay](../problems/staged-xrank-independent-arithmetic-verification.md) |
| DescentTree | [descent-tree slope grid](../problems/dtree-slope-grid-design-infeasible.md) |
| TransferAudit | [graph-wide isogeny solve](../problems/isogeny-graph-wide-relation-solver.md), [P-224 point maps](../problems/p224-degree3-point-maps-not-certified.md) |
| OrbitRelations | [rotation controls](../problems/rotation-factor-base-controls-not-density-matched.md), [RM/Kummer FFT counts](../problems/rm-kummer-fft-counts-unverified.md) |

Passing the public fixture changes none of those problem statuses.

The integration deliberately reuses `python -m harness.run`, the repository's
existing public experiment program. For `EXP-ECDLP-CHALLENGES-001`, the program
asks the native binary to generate a baseline submission when no external
submission is supplied, asks the same binary to verify the submission, then
stores the receipt in an immutable run record. The Python layer never
reimplements or weakens the mathematical checks.

Each verified receipt retains a direction-tagged six-coordinate frontier.
There is no aggregate score because independent rank, decomposition yield,
matrix coverage, descent size, transfer recovery, and orbit compression use
different units. Performance remains `not_measured`, security impact remains
`not_established`, and transfer advantage remains `unknown`.

## Contribution interface

1. Build `ecdlp-challenges` from the sibling `crypto` repository.
2. Generate or implement a submission against the committed fixture.
3. Run the verifier directly while iterating.
4. Use `python -m harness.run --experiment EXP-ECDLP-CHALLENGES-001` to retain
   a verified immutable record. Pass `--submission` for contributed output.

```sh
../crypto/target/release/ecdlp-challenges baseline \
  --fixture harness/fixtures/ecdlp_challenges_v1.json \
  --out /tmp/submission.json
../crypto/target/release/ecdlp-challenges verify \
  --fixture harness/fixtures/ecdlp_challenges_v1.json \
  --submission /tmp/submission.json
python -m harness.run --experiment EXP-ECDLP-CHALLENGES-001 \
  --crypto-bin ../crypto/target/release/ecdlp-challenges \
  --submission /tmp/submission.json --out /tmp/ecdlp-challenge-run
```

The adapter accepts an explicit `--crypto-bin`; otherwise it checks
`ECDLP_CHALLENGES_BIN`, a sibling checkout's release/debug binary, and finally
`PATH`. It never downloads or silently substitutes a verifier.
The committed fixture copy is pinned at SHA-256
`0399b42507f2c0c410bf801935ece4c00d5d7a16dc9b7276cfebf77f0115eb65`;
the default path refuses byte drift before invoking the verifier.

Official Curvesmash files under `config/curvesmash/` remain protected and are
not inputs to this internal challenge. Scientific execution beyond the public
toy control must be separately frozen, admitted, run, reviewed, and archived
under the repository contracts.
