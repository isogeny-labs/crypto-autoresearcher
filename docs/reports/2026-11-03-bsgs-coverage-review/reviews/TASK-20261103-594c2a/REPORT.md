# J1 review: frozen curve and source-to-code bridge

**Task:** TASK-20261103-594c2a / T-1468
**Pinned source:** `7c028ce9ccdec6c1ee7d4c2b3b60120ed3dcbd9e`
**Verdict on J1:** **breaks** for the asserted curve-wide solver and executed-operation bridge. The frozen 14-unit runbook panel and the mathematical curve/subgroup premise hold at their stated scope.

## Independent curve checks

`check_j1.py` reads the pinned files with `git show`. It trial-divides every possible divisor through the square root of each claimed prime and enumerates all `x` in `F_p`, adding `1 + χ(x³+3x+20)` points per `x` and the identity. Its arithmetic does not call either pinned curve implementation.

| Check | Result |
| --- | ---: |
| `p=1048571` prime; `n=1047689` prime | both true by trial division |
| Nonsingular: `−16(4a³+27b²) mod p` | `874043`, nonzero |
| `G=(2,199837)` on curve and nonidentity | true |
| Independently computed `nG` | identity |
| Exhaustive point count `#E(F_p)` | `1047689` |
| `m=⌊√(n−1)⌋+1`; `m²` | `1024`; `1048576` |

Because `#E=n` is prime and `G` is nonidentity, `G` has order `n` and every curve point is in `<G>`. The inequality `n≤m²` covers each canonical scalar `0≤k<n`. This is the needed mathematical bridge from index coverage to the frozen group; the source theorem alone does not prove the Python path.

## Pinned source and frozen modes

The frozen plan has 12 `search` seeds, one `known-k=123456` positive control, and one `off-curve` negative control. Its source hashes match pinned `solve.py`, `check.py`, and `curve.json`; its README hash, seed derivation, and every checker mode/value pair also match. Every one of the 14 pinned driver calls exited 0; every pinned checker call exited 0. The 13 valid instances reported the prescribed logarithm, and the off-curve point was rejected with no logarithm. The raw per-unit results are in `raw_checks.json`.

The affine `solve.add` and independently written projective `check.Curve.add` agree with a separate Fermat-inversion implementation for 25 pairs chosen from the identity, `G`, `−G`, `2G`, and `(n−1)G`. This directly exercises identity, doubling, inverse, and mixed additions; it is a finite exceptional-case check, not a proof of either implementation.

Direct `known-k` boundary controls at `1`, `1023`, `1024`, `1025`, and `n−1` solve and pass the checker. **At `k=0`**, which is within the coverage theorem's domain, the driver computes `Q=O` and raises `TypeError` at `list(Q)` before writing a raw result. `k=n` produces the same serialization failure, though it is outside the canonical `[0,n)` input range. Thus the curve-wide statement that every on-curve input returns a solved trial fails for the identity point. Direct `bsgs(G,O,...)` can return zero; the failure is in the driver/output representation, and the checker also assumes an affine `Q` when it forms `list(expected_q)`.

The outside-subgroup control uses a separate small nonsingular curve `y²=x³+1` over `F_17`: `#E=18`, `G=(0,1)` has order 3, and `Q=(1,6)` is on the curve but outside `<G>`. Direct `bsgs` returns `None`. There is no outside-subgroup point on the pinned prime-order curve, so this control checks the necessity of the order premise rather than presenting a counterexample to that premise.

## Cost and checker controls

`solve.bsgs` builds `m` table entries and reports `giant_steps=i+1` for the number of lookup rounds through the hit at index `i`. It performs only `i` giant-step additions before that hit. For `known-k=123456`, `i=120`; a wrapped `solve.add` counted **1156** calls across table construction, setup multiplication, and giant updates, while `group_ops+setup_ops` reports **1157**. Thus `group_ops` combines table entries and lookup rounds; it is not the number of executed group additions indicated by its name and README description.

The checker rejects a `group_ops+1` mutation and rejects a `giant_steps+1` mutation even when `group_ops` is adjusted to preserve the sum. It accepts an arbitrary `setup_ops=987654`, because that field is unchecked. It also accepts an independently constructed `raw-result.json` containing the correct `Q`, `k_found`, and prescribed count fields, with `elapsed_ms=0` and fabricated `setup_ops`, in a fresh directory where the solver never ran. These checks show exact consistency with a prescribed trace, but cannot attest that those operations were executed. The synthetic control writes a minimal `manifest.yaml`; the checker tests only that this file exists, not its content.

## Scope and next repair

The frozen example's 14 planned units satisfy their checker and the curve order premise is independently confirmed. The J1 break concerns the broader source-to-code bridge for **every** curve point, plus the interpretation of reported `group_ops` and checker acceptance as execution evidence. Encode the identity point consistently in driver and checker, then rerun `known-k=0`. Define separate metrics for group additions, table entries, and lookup rounds; assert or independently measure any claimed executed count. Preserve the frozen plan and its existing outcomes when making those repairs.

Reproduce the J1 checks from this checkout with:

```sh
python3 docs/reports/2026-11-03-bsgs-coverage-review/reviews/TASK-20261103-594c2a/check_j1.py > /tmp/j1-raw-checks.json
```

The script uses only Python's standard library, `git show`, the pinned toy files, and temporary directories. It launches no runbook session, build, or cloud job.
