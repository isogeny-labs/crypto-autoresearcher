# n51 polynomial-01 sliced degree-five attempt

The one authorized n51 D5 producer attempt ended normally with
`projection_kills_one`. Its provisional degree-five relation rank was
103877, equal to its 103877 working coordinates, so it exported no D5
certificate. The fresh exact solution counter returned zero. These are
terminal results of the frozen attempt, not a proof that the constant
belongs to the true `W5`: the checked degree-four seed kernel may be
larger than `W4`. Lemma 1.6 and `SEED-EXACTNESS-GATE.md` give the exact
logical distinction.

The original degree-four map was independently accepted. The sliced,
selectively rebased 1,553,961,056-byte input has SHA-256
`be38aff828d9d3c73e70ea78914727fdca1305edbf5f99e99b28aa747cc396d8`,
51 variables and quotient dimension 45615. The D5 [plan](../../n51-poly01-sliced-d5-local-plan-001.json)
and [protocol](../../n51-poly01-sliced-d5-local-protocol-001.json) were
frozen and pushed before launch. The child had a 64 GiB address-space
cap, 8 GiB host reserve, a six-hour watchdog, USD 12 reservation, and
no retry or checkpoint. The native process PID was 874406; both it and
its parent runner had exited when terminal receipts were reconciled.
The last live RSS observation was about 38.3 GiB, not a peak measure.

The [producer start](raw/produce5.started.json),
[finish](raw/produce5.finished.json), [stdout](raw/produce5.stdout.txt),
[stderr](raw/produce5.stderr.txt), [count output](raw/count.stdout.txt),
[admission](raw/admission.json), and [result](raw/result.json) are preserved
with the remaining raw receipts in this directory. The producer exit
code was zero and `timed_out` was false. The result file SHA-256 is
`c095cc43f97292e1ac7ae3178f7a568864655ea02bc0f2eee04c67a204147a25`.
No D5 certificate bytes or checkpoint files exist for this attempt.

The pre-frozen direct-W4 fallback passed its exact-source, budget,
memory, disk, lock, and terminal-status gates at 19:09:59 UTC and began
its single 32 GiB-address-space rank trial at 19:10:01 UTC, within the
original 23:30 UTC deadline. Its admission and live child belong to
`n51-poly01-direct-w4-rank-001`; they are not a second D5 attempt.
The target rank is 226437, the checked seed-kernel dimension in the
272052-column sliced degree-four universe. Equality would establish
seed exactness under the separately audited direct-closure algorithm;
a smaller rank would show that the current D5 seed discarded genuine
quotient directions. Even equality does not turn this producer status
into an independently checked D5 membership derivation.
