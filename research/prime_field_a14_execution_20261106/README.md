# A14: paid known16 helpers on the original norm base

Implementation in progress; no native A14 curves, targets or relations have
been generated, and no execution protocol or release exists yet.

The next comparison keeps norm32, adds16 separately constructed public-log
helpers, and retains source-free known32 as its implemented generic control.
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
- The tiny software controls exercise signed/permuted bases, native48/helper16
  dimensions, incomplete target spans, JSON roundtrips and corruptions. The
  all-known specialization is compared with A13's executed direct solver,
  including its Fr operation counters.

```sh
/workspace/factor-base-venv/bin/python -m pytest \
  research/prime_field_a14_execution_20261106/test_partial.py \
  research/prime_field_a14_execution_20261106/test_geometry.py -q
```

Still required: geometry-aware collection/query caches and independent complete
triple/miss controls; own paid helper16 and known32 constructor/cache paths;
source/target/native-row assembly and cost references; exact original-base
information attribution; complete driver/export/source bindings, prospective
protocol/current S3/root release and ordinary admission. No helper labels or
known-base certainty may be counted as learned rank. No cross-base Delta is
used against known32. One existing worker/thread,2GiB,21600CPU/wall seconds,
one future attempt with no automatic retry or new paid capacity.
