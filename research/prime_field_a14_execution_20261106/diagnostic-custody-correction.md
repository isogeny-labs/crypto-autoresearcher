# Information diagnostic custody correction

The [first assessment](implementation-readiness.md) found a prospective failure
path in source e2d414d332f7d92333de5d206921b5b97a332de6: diagnostic results and
paid counters were appended only after independent checking. No native A14
attempt had run. That assessment and the old source/preview remain unchanged.

The corrected runner retains a named ProgressMeter which flushes each complete
or failed diagnostic phase immediately. It appends producer results, native
cancellation certificates and counters to information.jsonl before invoking
the checker. Successful checks have a separate information-checks.jsonl stream
and byte/hash-bound journal receipt. Failures retain the output receipt when
available and all diagnostic phase prefixes. The analyzer binds both streams,
counts phase work once and keeps checker-failed outputs unverified.

The full marked tiny suite passes129controls in37.31seconds; its additive
receipt is validation/diagnostic-custody-software-status.json. Two injected
software failures exercise a mid-phase paid Fr addition and checker rejection.
They assert immediate phase retention, output-before-check, unchanged producer
output after rejection, partial-export noncompletion and exact physical prefix
counts. Software admission is mocked only at p211; resource fields are explicit
synthetic fixtures. These are engineering controls, not native observations or
trusted signed scientific/replay evidence.

The prospective sample, matrix limits,129 software controls and scientific
methods are not inferred from native outcomes; no A14 native data exist yet.
The fixed native census remains1248systems/2496target-solver calls and576
separate information diagnostics. Exact corrected source/input publication,
additive preview and administrative reassessment precede any freeze/release.
