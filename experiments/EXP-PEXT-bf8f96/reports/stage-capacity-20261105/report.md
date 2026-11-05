# EXP-PEXT-bf8f96: exact stage-capacity design check

The [capacity checker](../../implementation/stage_capacity.py) rederives all four published join plans from their pinned class inputs and manifest, then counts every class/T unit and logical join position assigned to each census stage. The check is prospective design arithmetic; it does not run the census or measure throughput.

| Stage | Cohorts | T units | Logical positions | Watchdog | Best-case average time per T unit |
| --- | --- | ---: | ---: | ---: | ---: |
| `n3core` | q5/n3, q7/n3 | 1,882 | 173,699,022 | 21,600 s | 10,800/941 s (11.48 s) |
| `n3ext` | q11/n3 | 5,322 | 9,506,811,006 | 28,800 s | 4,800/887 s (5.41 s) |
| `n5` | q3/n5 | 974 | 582,316,614 | 21,600 s | 10,800/487 s (22.18 s) |

The total is 8,178 T units and 10,262,826,642 logical positions. These per-unit averages consume the entire stage watchdog; building, checking, writing, and supervisor overhead require a stricter operational limit. The earlier q11 figure of roughly 330,098 logical positions per second is a **coverage rate**, not an inner-loop throughput requirement: the sparse collision algorithm can certify generic intervals without visiting each position. A source-bound full-cohort runtime and checker-reserve qualification is still missing, so this calculation does not establish admission within the finite 24-hour local budget.

An [independent read-only review](fixed-model-review-notes.md) of the fixed-algebra component found no fixture counterexample, but found that its product reconstruction shares the producer's radical multiplication table. The separate rank replay checks square relations and dimension, not each multiplication coefficient or the source-generator embedding. The next checker must use independent finite-field and polynomial arithmetic to verify the serialized fixed basis, every product and unit after scalar extension, and `Y0²=f0`; it must independently derive component count and genus. This is a design gate, not an adverse scientific result.

EXP-PEXT-bf8f96 remains `review_required` and unfrozen. The six-stage launcher, C0-C7 controls, qualified execution route, trial plan, runbook, preapproval packet and approval remain to be completed before any scientific cohort trial.
