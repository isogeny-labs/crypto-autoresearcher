[pcc:unverified] Observer deadline implementation — TASK-20261104-61a371 [pcc:unverified]

[pcc:unverified] Observed: native fixtures 3; actual calls 3; supervisor return code 0. Shared control span 155.924607 seconds against the frozen420 second ceiling. All setup/imports/control gaps occur inside that one clock.

[pcc:unverified] Measured long-control STOP lower bound: 125.00014708200251 seconds. The marker precedes possible sleep entry. The actual stopped interval alone lower-bounds the observer quiet interval; no sleep-start or observer internal monotonic timestamp is inferred.

[pcc:unverified] Implementation: one finite monotonic deadline covers send and newline-framed receive. Remaining time is set before each socket operation; received bytes cannot restart the budget. The1MiB framing bound and strict JSON remain. Stage quiet receive uses validated DEFAULT_LIMITS merged with partial frozen limits: seconds + terminate_grace_seconds + exactly5 seconds. Default127 seconds; declared long stage207 seconds. Client coordination stays5 seconds.

[pcc:unverified] Scope: only observer.py and its source-manifest entry change. Accepted load_custody AST is byte-location-independent AST-identical. Other14core and57capture members retain exact bytes;59-key closure is unchanged. Actual new source publication is PENDING_ROOT, separate from source context fffc2f1b5082440ebd2f510e4b124810c9f46dab and prior publication e74e8e5e245166aa4e077898a574393eda0484d9.

[pcc:unverified] Control design: long disclosed baseline hang follows prospective amendment; candidate hang cannot complete under unchanged exact-seven candidate guard because its diagnostic marker remains. No marker relocation, candidate/native/checker/math change, or pre-amendment test was used. Stage200 seconds, grace2 seconds, native outer260 seconds.

[pcc:unverified] Socket controls recorded: 12. Benign split completes; slow trickle, open peer, EOF/partial EOF, malformed, duplicate, nonfinite/overflow JSON, oversize frame, and blocked send retain their actual outcomes/errors. Positive finite stage and API timeout validation use actual implementation calls.

[pcc:unverified] Trust: unchanged native execute_trial/static checker under explicit fixture authority; direct native parent remains alive for same-path rechecks. Root-custody is the held-fixed trusted observer file, not hostile-same-UID isolation or cryptographic authentication of arbitrary replacement. Direct driver child waits and observer wait records are retained; no adopted wait is inferred.

[pcc:unverified] Limits: all curves are disclosed fixed F11/F23 r<=29 with zero nonce. No scientific production positive, draw, entropy, cohort, benchmark, timing qualification, total attack cost, or fit conclusion. Source acceptance belongs to fresh independent review after root publication. No executor PCC claim/signature is created.

[pcc:unverified] History: prior TASK-fb3825 first-to-last producer span198.681973 seconds exceeded its180 second contract despite93.814976 seconds of logged helper execution; this operational deviation remains recorded and is not reset or relabeled by this task.

[pcc:unverified] Evidence: observations.json lossless capsule retains new logical files, raw source snapshots, all helpers, captured runtime/argv/environment/OS/wait facts, stdout/stderr, failures, report editables and extraction verification. Previous large archives are immutable references, not duplicated. Read-only source input verification covered97bindings, initial24 and exact59 before authoring.

[pcc:unverified] Standing: every empirical result in this report is [pcc:unverified]. Root must register actual native PCC result evidence before public citation/publication. Reviewer TASK-20261104-996070 is a later independent stage.
