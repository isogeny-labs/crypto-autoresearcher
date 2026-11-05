# Prime chart transform integration — UNVALIDATED SOURCE

This package is source-only TASK-20261105-07e2d4, admitted at e998ddb35b3dcb78eb85390edef4fbe1b1451b4a. No candidate import, compilation, solver, census, suite, CAS or benchmark was executed during authoring. Importability and control outcomes are unknown. Source is intended for separately admitted validation, followed by a fresh independent source-aware reviewer. [pcc:unverified]

Use package-qualified imports (`research.prime_sat_transform_integration_20261103`). The directory is a Python namespace package; no extra `__init__.py` is required by the source design. The frozen baseline depends on python-sat/Cadical195. No dependency installation belongs to this stage. Runtime source identity includes all eight Python modules plus source-provenance.json and software-contract.json. The future launcher must additionally verify the complete published source snapshot, frozen plan/baseline hashes, interpreter, native binary and exact dependency versions. [pcc:unverified]

## Public interfaces

| Module | Interface | Contract |
|---|---|---|
| transform | `build_transform(trusted_descriptor, mode)` | Rebuild original chart, original range document, exact operation and transformed range source. Modes: `identity`, `k2_raw_A0`, `k2_addrow_A0`. Nonapplicable requested transforms return `status=not_applicable`; no silent fallback. |
| transform | `authenticate_transform(document, trusted_descriptor, mode)` | Full typed comparison against a fresh descriptor-rooted rebuild, including exact original bytes, variable roles, row map, certificate, range/CNF, baseline hashes and construction counts. |
| transport | `reconstruct_original_assignment(document, assignment, descriptor, mode, *, attempt=None)` | Strict full reduced assignment; reconstruct A0 canonically and preserve all original auxiliary values. This inverse alone does not assert root validity. |
| transport | `project_original_coefficients(...)` | Return ordered original coefficient names/values, never compare raw reduced masks with original masks. |
| transport | `encode_transformed_assignment(document, original_assignment, descriptor, mode, *, attempt=None)` | Require original root, exact inverse roundtrip, encode canonical original and transformed value/state bits; retain both. |
| transport | `decode_and_check_original(document, bits, descriptor, mode, *, attempt=None)` | Authenticate, decode canonical range states, check transformed residuals, reconstruct original assignment and bits, run unchanged original aggregate/recovery/signed checks, reencode transformed bits. |
| chart_solver | `convert_range(range_document)` | Strict canonical mask-string to integer conversion with exact n/p/projected bits, generic CountedRing, all polynomial rows and exact domain CNF. |
| chart_solver | `solve_chart(document, descriptor, mode, limits, strategy, checkpoint, *, refuter_mode='baseline', solver_factory=None)` | `checkpoint` is a fresh output directory or open AttemptReceipt. Emit begin before native allocation, then counted generic search and independent final verification. `solver_factory` is a deterministic failure-control seam, not a search oracle. |
| chart_solver | `verify_chart_answer(document, descriptor, mode, answer, *, attempt=None)` | Identity uses unchanged complete_chart_transcript; transformed range uses trusted rebuilt compile_range descriptor and unchanged complete_transcript/final adapter, followed by original signed-model reconstruction. Preserve raw/augmented transcripts and gaps. |
| engine_counted | `solve(..., *, attempt=None, solver_factory=None)` | Frozen prefix engine search/certificate/clause methods, with exclusive `_charge` finally accounting and native stats before explicit teardown. Explicit integer limits only. |
| bridge_counted | `solve(..., *, refuter_mode, attempt=None, solver_factory=None)` | Private per-solve refuter namespace, exact encoding import path guard, sidecars, shared-state guard and secondary-error preservation. |
| attempt_receipt | `AttemptReceipt(directory, bindings, *, attempt_id=None)` | Fresh exclusive directory and atomic immutable sequence records. `checkpoint`, `phase`, `failure`, `secondary`, `seal` retain attempted work. |
| census_v2 | `canonical_costs`, `costs_equal`, `produce_census`, `verify_census_record` | Closed nine-counter schema; only known absent/zero counts become equal. Preserve raw dictionaries and canonical vectors. Wire projections are ordered pairs represented as lists. |
| census_v2 | `run`, `verify`, `verify_envelope` | Versioned prospective wrapper around original producer and semantic verifier. Never rewrite original files or historical invalid-output runs. Full-cohort execution is not a software-control action. |
| software_controls | `run_suite(directory, *, run_native=False, admission=None)` | Explicit separately approved exact-source execution token required. Fixed original regressions, transformations, mutations, injected failures, tiny counters and optionally twelve fixed native instances. No CLI autorun. |

These describe intended behavior of unexecuted source, not observed correctness. [pcc:unverified]

## Transformation document

`prime-chart-transform/v1` binds: operation, exact public descriptor; original compiled document and source/range digests; frozen baseline file hashes; transformed source/range/digests and arithmetic labels; original/transformed variable and projection orders; forward map; inverse-pivot expression; every original/appended row's map including literal zeros; and ordinary appended-row certificate. The mathematical all-variable field augmentation is explicitly absent from the Boolean export. [pcc:unverified]

Finite k2 constant B uses original projected variables `[chart.A0, chart.A1]`, with q=`chart.A1`. Literal N0/N1/N2/N3/L polynomial content is checked against the builder, not only row labels. All other rows must be independent of A0 and q in this exact stratum. Added-row mode appends N1+2aN2 before A0=b−a*q substitution in every row. Every nonzero row and duplicate remains. Raw mode performs the same substitution without the added row. Identity preserves all original source bytes, including literal zero rows. Transformed projection remains `[chart.A1]`. [pcc:unverified]

`accepted` denotes a valid transcript at its declared status and can hold for a censored partial answer. `verified_complete` additionally requires original declared status `complete` and no range-completion gaps. Native false, solver status, checked partial transcript and certified complete coverage are distinct fields. Original coefficient projections and signed auxiliary witnesses are retained per returned model. [pcc:unverified]

## Limits and counted units

Generic-engine limits are positive integer `outer_calls`, `native_conflicts_per_call`, `native_decisions_per_call`, and nonnegative integer PC `degree`, `rows`, `pc_calls`. The software plan fixes 16, 1000, 10000, 2, 256, 32 respectively, seed0, one thread, baseline refuter, model_only strategy, prefix depths sorted/deduplicated `[0, projected_bits, n]`. No string exponent alias is accepted. [pcc:unverified]

`search_events.sat_calls` counts native solve_limited calls. `model_checks` counts propagator candidate callbacks. `accepted_models` counts accepted projected witnesses. Legacy `sat_candidates` is a separate unit used only by the original coordinate wrapper. Native conflicts/decisions/propagations/restarts are reported as available, partial or unknown, never inferred zero. PC attempts, row attempts and certificate counters remain separate. Named arithmetic operations, event counts and elapsed nanoseconds are not combined into one synthetic work score. [pcc:unverified]

Engine `_charge` records exclusive disjoint arithmetic deltas in finally, with inclusive child deltas subtracted once. Receipt phases record both inclusive/exclusive elapsed nanoseconds; nested counter scopes require explicit scope IDs when both have counters. Unknown child counts make parent exclusive allocation unknown. Repeated checkpoints add no mathematical operations. Original successful-return costs remain nested diagnostic receipts and must not be summed again with overlapping engine/phase totals. [pcc:unverified]

Opaque frozen baseline operations do not expose their interrupted local counters. Their phases therefore say unknown; the source does not claim complete all-operation accounting. Available q.EVENTS, ring arithmetic, attempted events, successful-return costs and elapsed phase time remain recorded. A later comparison must preserve these coverage gaps rather than report incomplete costs as complete. Existing host/inference cost is not asserted zero. [pcc:unverified]

## Receipt semantics

A directory is allocated with `exist_ok=False`. Events use write/flush/fsync, atomic hard link without overwrite, unlink of temporary file and directory fsync. A record contains only the previously confirmed durable sequence; successful current durability is returned and recorded in memory, then becomes visible in the next snapshot. Serialization/storage errors retain in-memory diagnostics and the previous durable sequence. Forced termination may leave only that previous checkpoint. The API does not claim durability when fsync fails. [pcc:unverified]

Envelope statuses: `failed`, `interrupted`, `censored`, `invalid_output`, `complete_unverified`, `verified_complete`. Primary exception objects are reraised with traceback; statistics/teardown/checkpoint failures become secondary when a primary already exists. Reported native status is not changed to UNSAT by exception handling. Receipt objects/partial transcripts are attached to exceptions when possible. Failure of an attachment or persistence operation is itself retained where possible. [pcc:unverified]

## Census v2 scope map

The nine metric names are coefficient_additions, coefficient_multiplications, evaluation_term_visits, restriction_term_visits, membership_transform_subtractions, legendre_pow_calls, membership_curve_tests, domain_clauses, boolean_assignments_visited. Unknown names including zero, booleans, negative or noninteger values are rejected. A supplied canonical vector must contain all nine names with typed nonnegative integer values. [pcc:unverified]

The original encoding.verify body is copied as `_verify_semantics`; its original per-arm body is mechanically relocated into `_verify_arm` to allow bounded direct controls. Within that body only `got['costs'] != arm['census']['costs']` changes to `not costs_equal(...)`. A side-effect-only append records both raw dictionaries and vectors after equality succeeds. All original exact construction equality, complete_models, projection/order, search-budget contradictions, verify_search certificate/model checks, reconstructed lifted set and witness/cost comparisons retain their original predicates and delegated baseline functions. The full verifier still independently builds and recomputes every census; `_verify_arm` is not a precomputed-result shortcut. The producer wrapper keeps the original payload verbatim and places its canonical vectors beside it. [pcc:unverified]

## Later validation and preserved comparison

The copied downstream-validation-plan.md is normative. The launcher must enforce one CPU/2GiB, one worker, at most two producer and one independent attempts of600 seconds each (1800 aggregate), no automatic retry, exact source publication and finite cost authorization. The source's process timer and per-instance counters cannot enforce cross-process/cross-attempt or kernel memory/CPU limits; this is an explicit launcher responsibility. Admission tokens are launch metadata, not an authorization mechanism against an adversarial caller. [pcc:unverified]

The suite retains135 original chart descriptors, eight nilpotent/eight guard cases, signed F1 branches,12 added k2 boundary descriptors, source/row/range/certificate mutations, primary/secondary failure injections and eight tiny census calls with n≤3 and total≤64 Boolean assignments. Three native sentinels, three identity-zero chart cases and six finite-two-repeat identity/transformed cases consume at most12 instances and192 calls per attempt. Censored repeated-chart outputs remain censored; no substitute fixtures or budget reassignment. Controls are source, not pass records. [pcc:unverified]

The original106 coordinate cells and separate6 coefficient cells, all five leads, original arms/targets/controls/limits, complete projections/fibers, signed outputs, reconstruction and certificate costs remain mandatory. This software subset cannot substitute for them. No unchanged partial-matrix/two-bit backdoor scaling, k3 sharing or target normalization was added. [pcc:unverified]
