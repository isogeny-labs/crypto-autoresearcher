# EXP-PEXT-bf8f96: published four-cohort all-T join plans

The four [join-plan inputs](../../inputs/join-plans-20261103/) now bind every original geometric cohort to the published compact class manifest. Each canonical plan records the exact field, curve models, T representatives and structure-ordinal offsets. `join_plan.py build` generated each plan and immediately recomputed it with `verify_plan`; the retained [build log](../../inputs/join-plans-20261103/build-log.jsonl) records the four verified SHA-256 values. The [set receipt](../../inputs/join-plans-20261103/receipt.json) binds those bytes to the earlier layout inventory, source and input manifest hashes. Build and verification use the same join-plan implementation.

| Cohort | Curve classes | Class/T blocks | Structures per block | Total structure ordinals |
| --- | ---: | ---: | ---: | ---: |
| q3/n5 | 488 | 974 | 597,861 | 582,316,614 |
| q5/n3 | 252 | 504 | 16,275 | 8,202,600 |
| q7/n3 | 690 | 1,378 | 120,099 | 165,496,422 |
| q11/n3 | 2,662 | 5,322 | 1,786,323 | 9,506,811,006 |

The totals are **4,092 curve classes, 8,178 class/T blocks and 10,262,826,642 structure ordinals**. The plan hashes match the earlier layout inventory exactly. The input preparation ran with a 4 GiB address-space cap and a 300-second timeout per cohort. The join-plan and published-binding [software tests](software-tests.log) check canonical T/offset and mutation refusal at their fixture scope.

The [draft specification](../../specification.yaml) now names the four concrete plan paths and removes its stale claim that the full-cohort manifest is absent. These files are prospective inputs. They do not contain candidate, genus, descent or scientific trial rows. The six-stage launcher still needs to bind their hashes in a frozen trial plan, then complete coefficient-aware descent, Type2, C0–C7 controls, analysis and approval. EXP-PEXT-bf8f96 remains `review_required` and unfrozen.
