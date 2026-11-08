# Degree-six frontier target triage, 2026-11-08

This is a comparison of retained, named inputs and source-derived D5
allocation profiles. It is not a new closure run or a degree-six bound.

| Original system | Recorded exact count | Checked D4 quotient dimension | D5 source-derived envelope | Current D5 state |
| --- | ---: | ---: | ---: | --- |
| `fresh-n47-rand-00`, 48 variables | 0 | 61,196 | 86,599,881,493 bytes | Frozen one-shot local plan, USD 20 reserved, output root absent |
| `fresh-n50-poly-03`, 50 variables | 0 | 38,629 | 38,017,488,971 bytes at 4096-row chunks | Frozen one-shot local plan, output root absent; finite USD reservation still a launch gate |
| `fresh-n51-poly-01`, 52-variable original system | 0 | 45,615 | 64,677,063,002 bytes at 60000-row chunks | Prior cloud D5 attempt failed after seed checking, with no candidate object |

For n47, the accepted original D4 map has SHA-256
`3bdad807113e43ec41ac6e9edcb2a282ffa486c7a694eba0dd3e0e9b0fa5162f`.
Its retained zero count has source/binary custody but no independent second
enumeration; `n47-rand00-x1-count-plan-002.json` freezes that replay. The
D5 memory figure and USD 20 reservation are in
`n47-rand00-d5-local-plan-002.json`.

For n50 polynomial-03, the separate checker accepted `1 not in W_4` with
codimension at least 38,629, and the recorded count is zero. The D4 map has
SHA-256 `6a25ce310435e564b5487975c17de90f2903a401e8721d95781cf7049f688719`;
`validation/n50-poly03-count-bridge-custody-001.json` now independently
checks the degree-50 field polynomial, named count command and output,
source/binary provenance, D4 checker, and publication custody. It does not
rerun the counter or rebuild its binary; the detailed argument is in
`N50-POLY03-COUNT-BRIDGE.md`.
`bounded-d4-archive-001/fresh-n50-poly-03-D5-cascade01-bounded-D4-001.publication.json`
records public certificate readback. The 38,017,488,971-byte D5 figure is
from `validation/n50-poly03-d5-4096-preflight-001/result.json`, whose SHA-256
is `60b9265ddcd71839c4f9cc78dbefeb9207cadac6f466018a03dbe86bb431d6f7`.
The frozen `n50-poly03-d5-local-no-checkpoint-plan-002.json` permits one
attempt with 39 GiB native memory, 2 GiB admission reserve, 32 GiB disk,
and a 21,600-second producer timeout. It requires a finite charged/reserved
local Spot allowance and fresh account-budget headroom before launch. No
such additional dollar reservation is asserted here.

For n51 polynomial-01, the original-system D4 map has SHA-256
`c160792a7530b20dd17affcdabafb8d95494eed51c8ee6d818af3212f3e304f6`.
Its zero count, checker acceptance, and original-system D5 estimate are in
`reports/n51-poly01-d4-20261101/report.md`, with public readback recorded in
`bounded-d4-archive-001/fresh-n51-poly-01-D5-cascade01-bounded-D4-001.publication.json`.
The prior cloud D5 attempt has terminal evidence in
`reports/n51-poly01-d5-stream-001/terminal-report.md`: it produced no D5
candidate, and the pod's underlying failure reason was not retained.
There is also a distinct 51-variable affine-slice D4 seed whose D5 profile
is 55,355,297,148 bytes at 4096-row chunks
(`validation/n51-poly01-sliced-d5-envelope-001.json`); its old local plan
deadline has expired. A D5 bound on the slice does not by itself transfer
to the original presentation's LFD, so the slice is not used in the table.

The n50 polynomial-03 input is the smallest *source-estimated memory*
candidate among these three, and it uses a polynomial factor base. That does
not predict its D5 outcome or runtime. The already authorized n47 count and
D5 attempts retain their frozen identities. Any n50 D5 launch needs its own
finite dollar reservation, current budget admission, exact source and input
readback, and an independent D5 checker acceptance before an LFD-at-least-six
claim. The three candidates must not run concurrently on the shared host.
