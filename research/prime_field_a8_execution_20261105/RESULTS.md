# Cold cancellation-first recovery matches the full joint solver

A8 completed **288 paired systems / 576 cold solver calls**, with zero unknowns.
Both methods identified exactly the same target slots and scalars in every case,
matched the original A7 joint outcomes, and produced independently valid target
unit certificates over the **original joint rows**. This completes the requested
implementation comparison on all four observed curves/bases and 32 fixed public
target points. No new relation collection, curve or target draw was performed.

The methods each identified 486 target slots summed over dependent systems.
Every schedule/budget/scope reuses the same targets; this is not 486 independent
recoveries or newly identified targets beyond A7.

| Recorded logical Fr calls, all arm phases | Full joint | Cancellation first |
|:--|--:|--:|
| Addition | 1,097,774 | 322,672 |
| Subtraction | 537,790 | 506,680 |
| Multiplication | 1,616,582 | 813,356 |
| Inversion | 5,508 | 4,428 |

These are component vectors for the exact implementations, including construction,
elimination, complete kernels, identification, certificate lifting and original-row
verification. Scalar-field addition and subtraction use distinct counters in both
arms. Inversion internals, Python traversal, allocation, sorting, serialization,
OS work and independent dense checking are not a complete primitive cost model.
Diagnostic wall time is invalid for performance comparison. No weighted cost,
runtime, full-S, end-to-end or novelty advantage is asserted.

Candidate subtraction counts were **higher in 50 of 288 cases**; those adverse
cases remain in raw data and plotted inputs. Lower/equal/higher case counts,
derived from retained per-case values, are 288/0/0 for addition, multiplication
and inversion, and 238/0/50 for subtraction. These four units are not combined
using invented weights.

## What was built and paid

Full joint constructs and eliminates `[M,0;B,-E]` at width U+8. The candidate
chooses the first original-order row for each represented target and **freshly
constructs every additional same-target difference**, across all target groups,
before solving `[M;C]` at width U. It computes the full base-only kernel and tests
representative functionals against it. Missing target groups stay unidentifiable.
No A7 cancellation, kernel, pivot, solved scalar or certificate is a solver input.

For representative j, if `v_j = lambda M + mu C`, lifted weights on original
joint rows are lambda on source rows, plus `sum mu_i(e_i-e_j)-e_j` on target
rows. The weighted coefficient vector must be `[0,+e_t]`, and the weighted RHS
must equal the recovered target scalar. Separate public `[k]P=Q` checks follow.

| Phase, summed over all fixed cases | Full-joint Fr multiplication | Candidate Fr multiplication |
|:--|--:|--:|
| Elimination | 508,756 | 428,154 |
| Complete kernel | 136,564 | 57,630 |
| Identification | 938,580 | 294,890 |
| Original-row certificate verification | 32,682 | 32,682 |

Candidate construction used 13,824 Fr subtractions for 432 cancellation rows;
lifting used 78 additions and 564 subtractions. It emitted the same 25,396 total
original-row certificate coefficients as the baseline and checked 486 original-row
and 486 public target certificates. Public group/field checks have identical
recorded vectors in both arms. Shared projection, outside arm totals, used 21,326
Fr additions, 6,752 subtractions and 22,048 multiplications, once per case.
Historical relation collection stays referenced in A7; it is not replayed or free.

A material implementation boundary is visible in
[the existing identification routine](../prime_field_a4_execution_20261030/core.py):
it evaluates `vN` with dense dot products, including zero products, even when the
joint query is a target unit vector. The candidate also uses that same routine
on representative base functionals, with different width and missing-group
handling. Identification accounts for much of the count difference. The new
comparison therefore measures these exact solver paths; it does not isolate a
representation benefit after sparsity-aware functional evaluation.

The next controlled implementation test is **sparse functional evaluation in both
solvers** on these same immutable cases. Target units can read kernel coordinates;
representatives can evaluate only nonzero coefficients. Preserve complete kernels,
original-row certificates and all phase counters, compare against A8, and retain
adverse cases. This successor is proposed, not executed here.

## Execution, checks and custody

Run **a8-cold-solvers-7f32b1**, source
**a49d03dd5e19c402820484bc39e2373dd27e0589**, protocol
**c8b1bd1c7e6daadf691a1c79772654a380576491185b74226823cfe179c11074**.
One supervised native process executed both arms cold for every case; no warm
starts, rank/recovery stop, automatic retry or paid capacity submission. Limits
were one existing workstation process/thread, 2 GiB, 21,600 CPU/wall seconds,
4,096 original rows and 64 joint columns.

Prospective exact source/input publication, delegated administrative assessment,
frozen protocol, actual canonical S3 checkpoint, explicit root release and lease
preceded mathematics. Exit 0, no timeout/exception, source unchanged. Started
2026-11-05T04:01:51.755406Z, finished 04:02:05.983883Z. Diagnostic wall
14.228479984s, CPU user 12.613978s/system 1.268334s, peak RSS 105,558,016 B;
wall_valid=false.

**39 software controls passed** in 1.49s. They include tiny cancellation-required
deficient recovery, empty/width-zero/absent targets, actual public checks,
inconsistent/shape refusal, deterministic A/A, distinct primitive counters and
corruption controls. An injected second-arm failure verifies immediate retention
of the completed baseline and failed candidate phase/counter. Administrative
inspection found and resolved that retention gap before source publication.

The separate implementation checked plain projection, dense affine rank and
consistency, complete kernel spans and dense unit-row identifiability, exact
representative/difference construction, lifted original coefficients/RHS,
independent public multiplication and every A7 joint outcome. Phase sums and
all 576 export identities/seeds passed. Export `--verify-files` has zero findings;
3,457 A8 metric samples were emitted from committed Git blobs. These are
separate implementation checks, not staffed scientific review or an independent
primitive-counter audit. Configured coordinator model/provider remain unverified.
Full-ledger validation refused 112,982 sparse off-disk files; no full pass is claimed.

All eight closed raw snapshots/journals were losslessly gzip encoded, officially
S3-stored and remote-verified. [Raw data and export](runs/a8-cold-solvers-7f32b1/export.json)
were committed/pushed as **f41d2ad00a61960de7d14975695a97b7feb3e226** before report
rendering. The inspected [three-page PDF](reports/a8-cold-solvers-7f32b1/report.pdf),
[primitive graph](reports/a8-cold-solvers-7f32b1/primitive-counts.svg),
[budget graph](reports/a8-cold-solvers-7f32b1/budget-counts.svg) and
[plotted data](reports/a8-cold-solvers-7f32b1/plotted-data.json) preserve the measured
vectors. This text and the observation sidecar add the explicit dense-functional
boundary and adverse subtraction counts; the PDF remains the original generated
record, with its full phase table.

[v11 database receipt](database/v11-cold-solvers/generation-v11.json) confirms
unchanged v10 parent bytes, preservation of every inherited table row,
integrity/FKs and gzip roundtrip. It adds one study, 288 cases and 576 solver/
certificate records. Historical totals remain 10 curves/bases and now 12 physical
executions, with zero new independent curve/target draws. PDF and database are
stored through the official artifact tool. Hydrate using
`python3 tools/artifacts/artifacts.py pull research/prime_field_a8_execution_20261105`.
The final closed benchmark uses actual supervisor command/times/counters;
prospective registration is retained separately, without a benchmark-wrapper claim.

Sources: [literature.md](literature.md), [design.md](design.md), all original A7
rows bound in inputs.json, and retrieved PKM2016 primary §§3.1–3.4. No previous
raw output, frozen protocol, closed benchmark or official scientific state changed.
A7 historical graphs retain their original question and are unchanged; A8 adds
its own exact paired component graph without moving an attack-cost frontier.
