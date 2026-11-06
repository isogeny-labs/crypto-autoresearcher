# A14: paid known16 helpers on the original norm base

Implementation in progress; no native A14 curves, targets or relations have
been generated, and no execution protocol or release exists yet.

The next comparison keeps norm32, adds16 separately constructed public-log
helpers, and retains source-free known32 and known48 controls. Known48 matches
the hybrid's nominal atom count; see [control refinement](controls-refinement.md).
See [design](design.md), [sources](literature.md) and
[A13's ranked lead](../prime_field_a13_execution_20261106/next-leads.md).

Implemented components:

- `partial_solver.py` substitutes an explicitly supplied set of native unit
  equations, preserves the signed order of all remaining original coordinates,
  solves target functionals and lifts certificates back to all native rows.
- `check_partial.py` separately checks dense native/reduced spans, positive
  and negative target membership and original-row certificates.
- `geometry.py` keeps native coefficient slots while querying one representative
  per geometric sign class. A helper/norm coincidence supplies a paid equation
  on the old coordinate. That coordinate remains in the original unknown basis.
- `query_index.py` and `check_query.py` build the paid geometric pair/batch
  index and compare native equations against a complete signed-triple/miss
  oracle. Partial failures retain pair and accepted-row prefixes; native
  parameters require admission before index work.
- `public_base.py` constructs16/32/48 labelled points with independent paid
  constructor choices and caches. `target_cache.py` reuses geometric responses
  without importing affine labels. `source_construct.py` selects full AP/hash
  source programs using public scalar inputs and owned paid caches, with a
  separately coded integer/group checker.
- `mixed_collection.py` executes owned fixed prerequisites, preserves the old norm
  basis, collects AP/hash native equations and retains source-free known controls.
  Its plain checker reconstructs paid cache scope and every geometric query.
- `affine_branch.py` constructs symbolic target combinations using the same paid
  cache rules for every program. `native_case.py` retains native supplied units,
  cache matches and collected rows, with an incremental4096-row guard that
  retains failed prefixes. Partial-substitution and full-joint certificates
  agree under the small public-group controls.
- `information.py` meters old-base substitution, outside cancellation and native
  unit lifting. The dense checker verifies the exact rank identity and action
  on the old kernel, separately attributing supplied, collected and target gains.
- The tiny software controls exercise signed/permuted bases, native48/helper16
  dimensions, incomplete target spans, JSON roundtrips and corruptions. The
  all-known specialization is compared with A13's executed direct solver,
  including its Fr operation counters.

```sh
/workspace/factor-base-venv/bin/python -m pytest \
  research/prime_field_a14_execution_20261106/test_partial.py \
  research/prime_field_a14_execution_20261106/test_geometry.py \
  research/prime_field_a14_execution_20261106/test_query.py \
  research/prime_field_a14_execution_20261106/test_base.py \
  research/prime_field_a14_execution_20261106/test_cache.py \
  research/prime_field_a14_execution_20261106/test_construct.py \
  research/prime_field_a14_execution_20261106/test_mixed.py \
  research/prime_field_a14_execution_20261106/test_native.py \
  research/prime_field_a14_execution_20261106/test_information.py \
  research/prime_field_a14_execution_20261106/test_runner14.py -q
```

Latest complete pipeline receipt: [127 software controls](validation/runnable-source-software-status.json).
Earlier additive component receipt: [122 software controls](validation/mixed-native-information-component-status.json).
The small known48 budget3 row-cap refusal is retained in the adjacent preparation
failure receipt; it changes no future native limits.

`driver14.py`, `analyze14.py`, `custody14.py`, `cold14.py`, `prepare14.py`,
`streams14.py` and `supervise14.py` now implement the admitted runner, raw
journals, full export, cold counter references and one-attempt custody.
The tiny mocked-admission control covers all four programs, both solver arms,
information audits, counter conservation and altered-row refusal.
See [the exact implementation handoff](execution-plan.md).

Still required: publish and assess exact source/input/protocol bytes, prospectively
freeze, current actual S3/root release and ordinary admission. No helper labels or
known-base certainty may be counted as learned rank. No cross-base Delta is
used against known32. One existing worker/thread,2GiB,21600CPU/wall seconds,
one future attempt with no automatic retry or new paid capacity.
