# Independent finite scalar-prefix harness source

Status: **source_only_unvalidated**. Task TASK-20261107-20d288.

Authored an independent truth-table oracle, finite-difference residual reconstruction, typed deterministic manifest builder, semantic/counter checker, durable first-failure runner and external resource gate. These are source artifacts only. No candidate, oracle, builder or harness module was imported or executed; no cases were materialized, no tests or scientific calls were made. Five authored Python files were checked with `ast.parse` only. There are no runtime outcome records.

## Construction and fixed workload

The oracle evaluates original monomials by explicitly multiplying Boolean variable values at every suffix point. It scans depths and generator indices directly. For each free subset S it reconstructs coefficients with the sum over U contained in S of (-1)^(|S|-|U|) times the truth-table entry. Free masks return to their original variable positions. This does not share the candidate's binary restriction or incidence sweep. Boolean evaluation injectivity follows by induction from A+xB having values A and A+B; only addition/subtraction and unit 1 are needed. The modulus-4 control is structural arithmetic, with no inverse/certificate interpretation.

The locked prospective workload is 419 single-generator cases, 207 ordered pairs, 14 empty-generator cases and 9 named controls: 649 base cases. Their 1680 depth queries and two extractor calls are crossed with two insertion orders, two list/tuple containers and two identical repetitions: 8*(2*649+1680)=23824 valid calls. Twenty global malformed mutations through three APIs and four depth-only mutations, each repeated twice, add 2*(20*3+4)=128 calls. Total: 23952. These are specification counts, not completed cases/calls. The builder will calculate exact original-polynomial truth-table evaluation workload as sum over cases of s*(2^(n+1)-1), without evaluating a polynomial; runtime checks this metadata against oracle accounting.

Typed trees distinguish bool/int/float/null and list/tuple; dictionaries retain ordered key/value pairs. Equal/empty realizations remain separate rows. The runner loads and hashes the pre-materialized manifest and checks canonical representations, family/count totals, the full call schedule, valid case-to-realization bindings and malformed typed-tree round trips/arity before candidate import. It never imports the builder or generates replacement cases. Expected answers come only from the independent oracle. Every individual call has a type-aware ordered input snapshot; both expected and unexpected exceptions are checked for mutation. Identical repeats compare complete returned outputs/counters; permutations compare semantic witnesses/residuals while all actual counters remain in the journal. The manual insertion-sensitive control requires deletion counts 0/1 only for restriction at depth 2. Counter names overlap and are not a cost sum.

## Execution boundary and custody design

Source authoring is the current boundary. A separately authorized metadata step must run the reviewed builder, retain exact bytes/counts and a generation receipt, and bind the manifest digest before native freeze. A later separately approved standalone invocation would load that manifest, compute the oracle, import the candidate exactly once, check every row and finalize within the same external 60-second deadline. Both original producer slots remain consumed, and the reserved independent software review slot remains untouched.

The wrapper requires an independently frozen native admission verifier which validates authoritative protocol/run/claim records and atomically consumes a sole invocation. It requires an existing owned dedicated cgroup v2 domain with one-CPU quota, memory.max=536870912, memory.swap.max=0, whole-worker OOM kill and pids.max=1. It checks these actual files and exclusive membership before releasing a blocked child. The parent stays outside the worker group. No cgroups are created, no privileges expanded, no RLIMIT substitute used, and no alternate route or retries exist. Continuous readback and an independently prearmed external deadline remain required. The native adapter and external deadline/supervisor integration are future bindings, not implemented or authenticated here.

The future budget proposal explicitly separates five seconds of parent startup and five seconds of parent custody/cleanup from the 60-second worker limit, for a 70-second outer bound. A separately enforced one-CPU/512-MiB/no-swap parent envelope and journal cap up to 128 MiB must be approved and accounted. These are additional future resource prerequisites, not current authority or extra worker time. The child writes fsynced incremental before/completed/failure rows; the parent retains a separate terminal receipt even on worker kill, checks journal hashes, and refuses pass if enforcement, deadline, termination or custody is uncertain. First mismatches preserve the exact case/input/expected/actual and completed prefix. Expected malformed ValueError is a passing check, not a global failure.

## Unresolved public interface and admission bindings

The published interface says restriction returns residuals and counters but does not name its Python container. The harness therefore requires an explicit frozen layout selection: tuple_pair_v1 or mapping_v1, with no auto-detection. Extraction mapping fields are likewise explicit. Neither layout is asserted to match the unseen implementation. An independent public-interface clarification must fix this before runtime admission.

Remaining requirements: independent static review; separately admitted manifest materialization and its exact workload/digest; exact public return layouts; real native specification/protocol/run/claim validation and freeze; interpreter/environment/source/command hashes; an authoritative one-shot native verifier; existing authorized controller delegation and external deadline/parent envelope; finite supervisor/storage accounting; remote publication/readback; then exact execution approval. The draft has execution_authorized=false and no invented EXP/RUN IDs, manifest hash or freeze approval.

All 106 coordinate plus 6 coefficient comparisons, all five leads, complete charts and projected models, witness reconstruction, independent all-original-generator restriction, certificate checks and their costs remain downstream and unchanged. This source work prepares finite software semantics only.

## Author identity, blindness and actual reads

Native source-only executor claim supplied by root: owner executor-prime-scalar-harness, epoch 1, acquired 2026-11-07T22:57:15Z, expires 2026-11-07T23:27:15Z; no renewal. Inference is the approved degraded native mode: provider/model/tier/effective effort and context/output capacities are unauthenticated. No runtime or scientific acceptance follows.

The fresh author received only the delegated task and public input paths. No extractor source, producer controls/results, prior implementation reviews, unrelated repository source or other agent history was read. The exact actual-read inventory below includes the task handoff, all thirteen public inputs, and self-authored outputs. Broad linked AGENTS references, memory and unrelated skills were not opened because the explicit blind-read contract restricts inputs. The initial concatenated AGENTS/coordinator read was truncated in tool output; focused rereads completed their visible text. Input byte hashing read only this same allowlist. Own-source parsing/hashing is also counted as reading.

| Actual input read | SHA-256 |
| --- | --- |
| `ledger/handoffs/TASK-20261107-20d288.yaml` | `52dcb8e82c3507b942f3d6f9e55c8417b5a485f879a29b067facbbd2ea5533e3` |
| `AGENTS.md` | `1d51ede564b94fd52d54b4c835c17e74eb8830dd1f01c3cc6d9c739240c8c663` |
| `agents/coordinator.md` | `410b3be4737a58dbf31c469b6b2d103740598e2b3c0a86610fa64af0b80128ad` |
| `research/prime_sat_scalar_prefix_source_20261107/interface.json` | `7f958ad6f49eb8b152cd737ce84215fe3e05935492a1bd239436fef04d4ed9f6` |
| `coordination/prime_scalar_prefix_source_20261107/derivation-v2.md` | `b38ace70f8683920d3bdad2342fc1b1b81d018ceb8417cfcce2d393794a93364` |
| `coordination/prime_scalar_prefix_source_20261107/refinement-v2.md` | `5dded5bb38b4d11260875bf705b58be3a94f8d48f65627d63b73ab122f8cc79c` |
| `coordination/prime_scalar_validation_harness_source_20261107/design-lock.json` | `560361d90f95c8c519cbedd7537ab781f0dec873c4bc701d5d8bbeb92da7841c` |
| `coordination/prime_scalar_validation_harness_source_20261107/design.json` | `aba8b514a695b216cfa974252e6c0dd299f4f22576e7c7e031a03fd619419e5e` |
| `coordination/prime_scalar_validation_harness_source_20261107/case-generation-spec.json` | `7f68929cedcf12965554d96eefe7b1aeddef82f0f1bb182e6e37113e16d5e9dc` |
| `coordination/prime_scalar_validation_harness_source_20261107/oracle-and-checker-spec.md` | `90b6bf8585d98aa14ba9dc330f7b14ff2147975a59cc7b4a732617465126f893` |
| `coordination/prime_scalar_validation_harness_source_20261107/NEXT-ADMISSION.md` | `9a9d9f3a59bc89e53c1e7b2b24555c1a4ecfa074ea06174145c9cfcf53840880` |
| `coordination/prime_scalar_validation_harness_source_20261107/source-contract.json` | `b87c0e75d258d07fb3a6164d33df8a2b94b7f31f64c8dbd5e1497798dcd0d296` |
| `coordination/prime_scalar_validation_harness_source_20261107/input-bindings.json` | `33f9c796d999fc960355c1ca5b54274b963225bcf53926cff23a9e3747c24895` |
| `coordination/prime_scalar_validation_harness_source_20261107/inference-amendment.yaml` | `ff62785d7f01cae82675a8c93aa029528847f5563f06eb8ed302c3bec3c39277` |

Self-read scope: oracle.py, manifest_builder.py, checks.py, runner.py, resource_wrapper.py, interface.json, validation-protocol-draft.json, report.md, diagram.svg and report.typ in this report's directory. Source authoring uses only direct patching or standard-library file writing; `ast.parse` inspects source text without importing or executing authored modules. Root owns report.pdf and report-inputs.json, including rendering/visual inspection and final all-artifact hash binding.

## Source hashes at author handoff

These hashes identify the authored source and interface/draft. The root report-inputs manifest must bind the final whole packet and every public design input; if static review causes edits, regenerate this table before snapshot.

| Artifact | SHA-256 |
| --- | --- |
| `oracle.py` | `2e126694666edb2b4333baa2be3bd205739b70314320c38fb7369bcdc0350cc2` |
| `manifest_builder.py` | `26b91af10fb3170ccc3b15df92aea0ca215d6ecaf4bdbd8dad546ae8a3969bdc` |
| `checks.py` | `a88b40d3db77ba0183ea20f21755b2b2177766a06362f14cf5c46cddb2ff0ad5` |
| `runner.py` | `d9c76d4bd037cfa284ae4369ce0c6ac50ad2640be0f6ddcf24ac31319e923862` |
| `resource_wrapper.py` | `37b75cb05926058620ef386bc05a41be8725041b08f2e126dc0a1922947c8f21` |
| `interface.json` | `4da38e5bbdd96b52e784781a8947f3d51554eaf5a2199f7d497f2ccb195c6dfb` |
| `validation-protocol-draft.json` | `99037efc996c6cc100f36949e610cc5b72c3690fa74030088427199c4e93cc86` |

## Static custody correction

Before runtime, static review identified that the supervisor retained wait status only locally. The source now records each actual nonzero-PID waitpid observation immediately, including the raw status, observed reap, WIFEXITED/exit code and WIFSIGNALED/terminating signal, on both ordinary monitoring and cleanup paths. No-child, unobserved and unavailable statuses remain null with explicit availability/reason fields; ChildProcessError does not invent a reap or signal. Signalled, uncertain or cleanup-killed workers remain incomplete. This correction received syntax parsing only, with no runtime check.

## Manifest coverage boundary from static review

Runtime structural checks do not independently rederive the exhaustive coefficient-code and assignment enumeration, every registered control value, or every malformed mutation value/type from the locked specification. The frozen manifest digest binds reviewed bytes, not a proof that those bytes match all prescribed values. A separately recorded independent prefreeze metadata audit must check the full exhaustive enumeration and every registered control and malformed mutation/type before native freeze. Runtime then loads that audited immutable manifest without regenerating cases. Static reasoning found no concrete oracle, counter-check or typed-builder semantic defect; this is not runtime validation or a completed metadata audit.
