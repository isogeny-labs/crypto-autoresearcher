# n33 trace-zero D5 candidate, read-only preflight

The named `fresh-n33-tr0-01` instance has zero solutions in its retained exact
count and an independently accepted D4 nonmembership certificate of codimension
at least 4,888. The certificate is published in the
[Semaev certificate release](https://github.com/isogeny-labs/crypto-autoresearcher/releases/tag/semaev-closure-certificates-20261029).
I downloaded the published 28,803,551-byte gzip, verified SHA-256
`3699fdc61c0d46e39fa89993d834ec0dc89b0cc5be1c4f853e1cae32af928bf7`,
decompressed it, and verified the 33,044,576-byte certificate SHA-256
`b12d74605a9df9147d89d10191a36fa644cdd5fa70ce610c56e26d870a9fe813`.
The [inference record](../../../semaev-m2-last-fall-degree/submission-20261029/archive/fresh-n33-tr0-01.inference.json)
pins the input and zero count; the [original receipt](../../../semaev-m2-last-fall-degree/submission-20261029/archive/fresh-n33-tr0-01.receipt.json)
includes the separate D4 checker acceptance.

The existing `capacity_profile.py` rechecked the retained certificate hash,
monomial universe, triangular rewriting and two independently enumerated border
counts. Its [exact output](result.json) gives 34 Boolean variables, 4,888
working coordinates and **zero degree-five border coordinates**. The D5
monomial universe has 331,212 members; its provisional map bit payload is
204,026,592 bytes. The existing 4,096-row bounded-export allocation formula
gives a 454,586,900-byte envelope. These are representation-derived sizes,
not measured peak RSS, runtime or a completed D5 closure.

The [candidate preflight](../../n33-tr0-01-d5-preflight-001.json) names one
future exact-computation attempt using the already qualified worker, a fresh
count and an independent D4/D5 checker. It is **not a frozen or authorized
launch**: a validated `experiment.protocol/v1`, exact command, fresh
job/lock/capacity reconciliation and finite cost allowance with account-budget
headroom are still required. The current `spot-experiments-daily-25` budget
readback exceeds its $25 limit, so no D5 producer was started. A verified D5
certificate with codimension greater than the fresh exact count would prove
LFD at least six for this named presentation; every other outcome remains
unknown at degree five.
