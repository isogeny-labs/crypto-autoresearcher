#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 10pt)
#set heading(numbering: "1.")
#align(center)[#text(size: 21pt, weight: "bold")[Independent scalar-prefix validation harness]]
#align(center)[Source authoring record · TASK-20261107-20d288]
#v(5mm)
#block(fill: rgb("e8eef5"), inset: 10pt)[*Status: source_only_unvalidated.* No candidate, oracle, builder or harness imports or executions; no case materialization, tests or runtime outcomes. Five Python files parsed as syntax only.]

= Constructed source
An independent oracle evaluates original monomials at Boolean suffix points, scans depths and generator indices, and reconstructs residual coefficients using subset finite differences. A typed manifest builder preserves integer/Boolean/float distinctions, dictionary insertion order, list/tuple containers and duplicate realizations. The checker compares witnesses, canonical residuals and residual evaluations, exact repeats, input immutability and structural identities.

The prospective locked workload is 419 single-generator cases, 207 ordered pairs, 14 empty-generator cases and 9 controls: 649 base cases. There are 1680 depth queries. Eight realizations give 8 × (2 × 649 + 1680) = 23824 valid API calls; 2 × (20 × 3 + 4) = 128 malformed calls give 23952 total. These counts are specified, not observed.

#image("diagram.svg", width: 100%)

= Source and execution phases
The current task authors source only. Separately admitted metadata generation must materialize the reviewed builder's manifest without oracle or candidate execution, retaining exact bytes, counts, workload and digest before native freeze. Runtime loads the frozen manifest and never imports the builder or regenerates cases. Its checks cover digest, canonical representation, counts, schedule and realization bindings. An independent prefreeze metadata audit must establish exhaustive coefficient-code/assignment coverage and every registered control and malformed mutation/type; runtime does not independently rederive those values.

#pagebreak()
= Fail-closed gate and custody
The future wrapper requires an independently pinned native verifier to validate real protocol, run and claim records and atomically consume one invocation. It requires an existing authorized owned cgroup v2 domain with one-CPU quota, 512 MiB memory, no swap, whole-worker OOM kill and one process. The parent reads actual controls and singleton membership before releasing a pipe-blocked child. An independent external deadline is already armed before release. There is no resource creation, privilege expansion, substitution or retry.

All worker imports, oracle computations, API calls, checks and finalization fit inside a single proposed 60-second deadline. Five seconds of parent startup and five seconds of custody/cleanup form a separately accounted 70-second outer envelope. A separately enforced parent CPU/memory/no-swap budget and a finite journal allowance require future approval. Parent custody remains outside the worker kill boundary. Actual waitpid observations retain raw status, reap, exit and signal details on monitoring and cleanup paths; unavailable status is never invented. Durable incremental rows and a separate supervisor terminal record retain failures, timeout and OOM. Any uncertainty about enforcement, termination, hashes or complete counts prevents pass.

= Explicit unresolved bindings
The public candidate interface leaves the exact Python return container unspecified. The harness requires a future explicit public layout binding, without auto-detection; no mapping/pair layout is asserted to match the unseen candidate. Remaining prerequisites include independent static review, exact materialized manifest and oracle-workload metadata, native protocol/run/claim validation and freeze, interpreter/environment/source/command hashes, authoritative admission-verifier implementation, existing delegated controllers, external deadline and parent budget, artifact/storage accounting and remote publication/readback.

The validation protocol is deliberately a draft with execution_authorized=false, no invented native execution IDs, no manifest digest and no freeze approval. Producer slots remain consumed 2/2; the reserved independent software slot is unchanged. All 106 coordinate plus 6 coefficient comparisons, all five leads, complete charts and projected models, witness reconstruction, independent all-generator restriction and certificate checks/costs remain downstream.

= Blindness and provenance
The author read the exact task handoff and thirteen public inputs only: AGENTS.md; agents/coordinator.md; candidate interface.json; derivation-v2.md and refinement-v2.md; design-lock.json, design.json, case-generation-spec.json, oracle-and-checker-spec.md, NEXT-ADMISSION.md, source-contract.json, input-bindings.json and inference-amendment.yaml. Own ten outputs were read for source/document inspection, hashing and syntax parsing. No candidate source, producer results, previous implementation review or unrelated repository source was read. The complete paths and SHA-256 inventory are in report.md; root binds the final packet in report-inputs.json.

Native source claim: executor-prime-scalar-harness, epoch 1, acquired 2026-11-07T22:57:15Z, expires 2026-11-07T23:27:15Z, without renewal. Approved degraded inference leaves actual provider/model/tier/effective effort and capacity unauthenticated. Root owns PDF rendering and visual inspection. This record reports source construction only.
