# Proposed n50 polynomial03 D5 admission after the n47 terminal result

**Status: prepared, not authorized, not launched.** The named original-system
target is `fresh-n50-poly-03` (50 Boolean variables), with retained exact
zero count and an independently accepted D4 quotient of dimension 38,629.
The D4 seed SHA-256 is
`6a25ce310435e564b5487975c17de90f2903a401e8721d95781cf7049f688719`;
it was rehashed locally on 2026-11-10. The output root
`/home/ec2-user/fall-degree-data-20261029/n50-poly03-d5-local-no-checkpoint-002`
was absent at this review. The prior n47 attempt is terminal and published
in `N47-D5-RESULT-20261110.md`.

The existing scientific plan
`n50-poly03-d5-local-no-checkpoint-plan-002.json` has SHA-256
`88a92372e9466b0e9ecbb11b1bf5554533955844068f4aa378b79e21e6da3730`.
Its frozen `experiment.protocol/v1` record
`n50-poly03-d5-local-no-checkpoint-protocol-002.json` has file SHA-256
`c18b0041ad35b4902ff97da97fc3d1fbc1faa5953bcb77a1bdea63c3b8091420`
and internally binds the plan hash. The committed runner
`run_local_d5_no_checkpoint.py` has SHA-256
`5660da176f486ec540865de8c67a9b3986bbbadd859249560f328612e8f45e6f`.
The existing V2 protocol validated with zero findings using the repository's
`tools/experiment_protocol.py` under Python 3.11 and `jsonschema` 4.23.0;
the host's system `jsonschema` 3.2.0 cannot run that validator.
Those records fix the one target, 4,096-row blocked lift, no checkpoint or
restore, one total attempt, a 39 GiB child limit plus 2 GiB host reserve,
32 GiB output capacity, and stage watchdogs of 3,600 seconds for D4 check,
600 for the fresh count, 21,600 for the producer, and up to 3,600 more for
the D5 check if a candidate exists. The source-derived D5
envelope is 38,017,488,971 bytes under the 39 GiB child cap; the maximum
candidate file implied by the pinned profile is 23,604,562,592 bytes. A
positive D5 map still needs an independently accepted degree-five checker
and the exact zero-count bridge before any LFD-at-least-six statement.

## Proposed operational cap

The proposed one-attempt reservation is **USD 20 all-in**, covering the
shared Spot host for the maximum 8h10m stage watchdogs, failed attempt,
storage and transfer, with zero retries. The last observed m8i.8xlarge
Spot price in us-east-2b was USD 0.8029/hour at 2026-11-10 20:00 UTC;
8h10m at that rate is about USD 6.56 for the whole host before the rest of
the reservation. This is a preflight estimate, not a measured charge or a
speed claim. The proposed absolute first-attempt deadline is
**2026-11-13T23:30:00Z**. It must contain all stage watchdogs and admission
overhead when the launch is attempted; if it expires, amend before any run.

The 2026-11-10 23:47 UTC AWS monthly Budget readback showed USD 1,360.114
actual against the owner-authorized USD 1,300 limit (last updated 17:52
UTC). The shared daily Budget showed USD 102.811 actual against USD 200
(last updated 17:47 UTC). These delayed figures are account totals, not an
incremental n47 charge. A proposed **one-time USD 1,500 monthly ceiling for
this n50 attempt** would leave USD 119.886 after the USD 20 reservation at
that stale monthly readback. Neither the ceiling increase nor this n50
reservation is authorized yet, so the launch is refused. Do not borrow a
different account, region, pool or retry to bypass this gate.

At a fresh admission, re-read both shared daily Budget objects and the
monthly Budget, including other reservations and delayed charges. Verify the
exact GitHub revision of the plan, protocol, runner, binary, input manifest,
seed, and launch command; materialize the tracked runner and protocol in this
sparse checkout before use. Recheck the named frontier locks, any existing
local output root and EKS job identity, host memory/disk and the deadline.
The runner itself enforces the scientific hashes, exclusive locks, memory,
disk, and one-write output root, but its V2 source does not enforce the
account Budget or absolute deadline; the external admission record must
enforce those before invoking the pinned command. Retain every exit, OOM,
timeout and partial file. No n50 launch occurred while preparing this note.
