# Post-test coverage audit

A read-only inspection using the same F101 fixture returned:

```text
subgroup 13 base sizes [2, 0]
internal relation tuples 0
internal relation tuples 0
```

These values were displayed by the exact group operations in constructions.py,
not estimated. This establishes a vacuous row-normalization loop in the passing
#69 unit test. Both dual compositions, all-point-pair homomorphism checks and
subgroup inverse normalization were separately exercised and remain covered.
The rank routine was tested on two explicit matrices. The three-invocation
unit-test allowance was exhausted; no fourth suite invocation was made. The
next round must assert nonzero normalized relation rows before claiming row
coverage. The README, problem record and PDF have been corrected accordingly.
