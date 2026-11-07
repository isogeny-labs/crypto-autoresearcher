# Independent acceptance gate for a possible original n51 D5 candidate

No original polynomial-00 D5 candidate exists yet. If the queued V2 producer
emits one, first preserve its terminal result, exact-count and producer
receipts, candidate byte count, and SHA-256. A `projection_kills_one`,
failed, or timed-out producer supplies no candidate for this gate.

The [native D5 check runner](run_n51_poly00_native_d5_check.py) is source
prepared, not launched. After a candidate exists, create and publish a
write-once `semaev.original-d5-native-check-plan/v1` with exact paths and
hashes for the candidate, producer result, producer finish, count finish,
count stdout, independent original generators, native checker binary, and
runner dependencies. Fix the memory cap, reserve, timeout, deadline, dollar
reservation, one-attempt limit, launch command, and output root before any
checker run. Recheck live budget and host capacity, the two frontier locks,
the exact GitHub revision, and any EKS frontier jobs before launching once.
Do not infer readiness from the earlier D4 control's measured memory or time.

The runner requires a producer `candidate_unchecked` status, a fresh exact
count of six, exact candidate size and hash agreement, successful count and
producer finish receipts, and the pinned independently exported equations.
It runs the separate C0–C3 native checker with the candidate hash as an
argument. Only an exit-zero checker result matching degree 5, 52 variables,
51 generators, both input hashes, and the candidate's quotient dimension
becomes `native_certificate_verified`. A failed or timed-out checker leaves
degree-five nonmembership unknown; there is no automatic retry.

The mathematical inference is separate from the producer and runner:
native C0–C3 acceptance gives a quotient map whose kernel contains W5 by
Proposition 1.5 of the theorem dossier. If its codimension is at least
seven, and the exact zero set has size six, Proposition 1.4 gives
`d_LFD >= 6` for this named satisfiable system. A verified codimension of
six or less does not establish that bound. A source-audited or direct W4
rank result is not a premise of this positive certificate argument.

The native checker already passed a degree-five fixture with a multiword
quotient and rejected a targeted C2 mutation. It also accepted the
original polynomial-00 D4 quotient against the independently exported
equations at full n51 size; see
[that control report](reports/n51-poly00-native-d4-control-20261105/report.md).
These qualifications do not pre-accept an unknown future D5 map.
