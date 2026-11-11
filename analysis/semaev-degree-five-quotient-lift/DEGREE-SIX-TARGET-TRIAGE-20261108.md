# Degree-six frontier target triage, 2026-11-08

This is a comparison of retained, named inputs and source-derived D5
allocation profiles. It is not a new closure run or a degree-six bound.
`ZERO-SOLUTION-D5-STATUS-RECONCILIATION-20261111.md` separately binds six
completed zero-count D5 producer attempts, all of which reported a killed
projection and emitted no D5 certificate.

| Target presentation | Recorded exact count | Checked D4 quotient dimension | D5 source-derived envelope | Current D5 state |
| --- | ---: | ---: | ---: | --- |
| `fresh-n47-rand-00`, 48 variables | 0, independently repeated | 61,196 | 86,599,881,493 bytes | One-shot lift terminal: `projection_kills_one`; no D5 certificate |
| `fresh-n50-poly-03`, 50 variables | 0 | 38,629 | 38,017,488,971 bytes at 4096-row chunks | Frozen one-shot local plan, output root absent; finite USD reservation still a launch gate |
| Affine restriction of `fresh-n50-poly-03`, 49 variables | 0, inherited from unsatisfiable original | 38,629 | 34,760,782,170 bytes at 4096-row chunks (source profile) | One-shot lift terminal: `projection_kills_one`; no D5 certificate |
| `fresh-n51-poly-01`, 52-variable original system | 0 | 45,615 | 64,677,063,002 bytes at 60000-row chunks | Prior cloud D5 attempt failed after seed checking, with no candidate object |
| Affine restriction of `fresh-n51-poly-01`, 51 variables | 0, inherited from unsatisfiable original | 45,615 | 55,355,297,148 bytes at 4096-row chunks | Checked sliced D4 seed; D5 local-plan deadline expired without a run |
| `fresh-n51-poly-00`, 52-variable original system | 6 | 45,615 | 64,638,795,838 bytes at 60000-row chunks | Original D4 map accepted; direct D5 deadline expired; bounded solution-factor gate V3 frozen and pending owner spending authorization |

For n47, the accepted original D4 map has SHA-256
`3bdad807113e43ec41ac6e9edcb2a282ffa486c7a694eba0dd3e0e9b0fa5162f`.
Its retained zero count now has an independently rebuilt and checked
second enumeration, published in `N47-X1-COUNT-RESULT-20261109.md`
(receipt SHA-256
`3a45f84b50c4aeefcc6e1e75d341d60a24c551b25238efb170dbc3425ab0f778`).
The D5 memory figure and USD 20 reservation are in
`n47-rand00-d5-local-plan-002.json`.
The terminal result, checked receipt hashes and claim boundary are in
`N47-D5-RESULT-20261110.md`. The producer did not emit a D5 map; its status
does not independently prove degree-five membership.

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

The earlier 49-variable n50 slice is material to whether that original
attempt is worth its reservation. Its affine equation eliminates variable
25 and is a checked combination of original generators. The projected D4
map was rebased into a checked 38,629-coordinate seed. Its frozen D5 run
reported full provisional relation rank 79,556 of 79,556 after about 3,110
seconds, with `projection_kills_one` and no candidate; the source profile
was 34,760,782,170 bytes and the binary admission report was
35,385,141,521 bytes. The retained reports are
`reports/n50-sliced-seed-rebase-20261105/report.md` and
`reports/n50-sliced-d5-local-20261105/report.md`. Proposition 2.5f now
proves that one-step closure of a checked D4 kernel is unchanged by slicing
along an affine relation inside that kernel. The conversion's kernel
equivalence has both a source-level proof and an independent full-size
row check (`N50-REBASE-KERNEL-SOURCE-AUDIT.md` and
`N50-REBASE-FULL-ROW-VERIFICATION.md`). If the sliced producer's full-rank
status is independently verified, the original D4-seeded lift would also
kill one. That D5 check has not been completed, and the D4 kernel has not
been proved exact W4. Thus the sliced result neither proves
`1 in W_5` nor rules out a different certificate. It is a strong reason to
review the proposed original n50 run before spending its USD 20 reservation.
An independent Python direct closure now verifies exact W3 rank 8,130 in
20,876 columns and matches every equation mask against the separate
Möbius-interpolation descent. The retained 12,746-coordinate D3 map passed
the independent certificate checker; equality of dimensions proves its
kernel is W3 (`N50-POLY03-W3-EXACTNESS.md`). The D3 map SHA-256 is
`d5e27dbe345b6a5f3100f41d6be1df4702be2de0a52b07dbfec3907d5425a94d`.
The D4 lift reports four rounds ending at relation rank 58,955 in 97,584
working coordinates; its checked quotient has dimension 38,629. Thus an
independent direct W4 rank of **212,547 in 251,176 columns** would establish
that the current original D4 kernel is exact W4. Together with a checked
sliced D5 relation transcript, Proposition 2.5f and Corollary 1.9a would
then prove exact LFD 5 for this named zero-solution input. The D3-to-D4
source and fixed-point receipts are now mapped to Proposition 1.9 in
`N50-POLY03-D4-LIFT-EXACTNESS-AUDIT.md`; this is conditional source-and-
execution evidence, not an independent primal D4 rank certificate.

For n51 polynomial-01, the original-system D4 map has SHA-256
`c160792a7530b20dd17affcdabafb8d95494eed51c8ee6d818af3212f3e304f6`.
Its zero count, checker acceptance, and original-system D5 estimate are in
`reports/n51-poly01-d4-20261101/report.md`, with public readback recorded in
`bounded-d4-archive-001/fresh-n51-poly-01-D5-cascade01-bounded-D4-001.publication.json`.
The prior cloud D5 attempt has terminal evidence in
`reports/n51-poly01-d5-stream-001/terminal-report.md`: it produced no D5
candidate, and the pod's underlying failure reason was not retained.
There is also a distinct 51-variable affine-restriction D4 seed (SHA-256
`be38aff828d9d3c73e70ea78914727fdca1305edbf5f99e99b28aa747cc396d8`)
whose D5 profile is 55,355,297,148 bytes at 4096-row chunks
(`validation/n51-poly01-sliced-d5-envelope-001.json`); its old local-plan
deadline has expired. Proposition 2.5e of the theorem dossier gives a
one-way transfer under any affine restriction: a checked D5 nonmembership
certificate for this slice would prove nonmembership for the original.
Since the original exact count is zero, that would prove original-system
LFD at least six. A killed projection, timeout or unchecked slice candidate
does not give that positive transfer. No D5 slice certificate exists yet.

For n51 polynomial-00, the original-system D4 map (SHA-256
`90878ee8bc6bda02957f25728380a9e677cd13b0f46c9eed1828349da796f115`)
passed independent Python and native C0–C3 checks against exported generators.
Its retained D3 seed kernel is now independently exact W3: a separate direct
closure rank of 10,970 in 23,479 columns matches the accepted D3 map's
12,509-dimensional quotient (`N51-POLY00-W3-EXACTNESS.md`).
The D3-to-D4 source and terminal fixed-point receipts are mapped to
Proposition 1.9 in `N51-POLY00-D4-LIFT-EXACTNESS-AUDIT.md`. The conditional
exact-W4 dimension is 248,589; an independent direct rank would remove the
producer-rank premise.
Its recorded exact count is six, so a checked D5 quotient of codimension at
least seven would prove LFD at least six for this named input. The 64,638,795,838-byte
envelope is the retained source-derived profile, not measured D5 usage.
Proposition 1.4a now gives the converse decision once the **true** degree-five
closure dimension is known: if `codim W5 = 6`, the checked `codim W4 > 6`
and six-solution count prove exact LFD 5. If `codim W5 >= 7`, Proposition
1.4 proves LFD at least 6. Thus an independently exact W5 rank resolves
this named target in either direction. A six-dimensional checked D5
quotient by itself is only a lower bound on `codim W5`; the equality case
needs a completed exact-seed lift or a separate primal rank check.
The `n51-poly00-original-d5-local-003` output root is absent and its
2026-11-10 23:30 UTC deadline has expired. The separate solution-factor
gate's earlier V1/V2 roots are absent and their deadlines expired. A fresh
V3 first-attempt packet is frozen in `N51-POLY00-FACTOR-GATE-V3-ADMISSION.md`,
with an absent write-once root and 2026-11-13 23:30 UTC deadline. Its
operational authorization remains pending. That gate checks whether solution
evaluations factor through the D4 seed; without it, a killed producer
projection could reflect an overbroad seed. Even a successful gate would
not establish a seventh D5 quotient direction.

The n50 polynomial-03 original input is the smallest *source-estimated memory*
unlaunched original-system candidate in this table, and it uses a polynomial
factor base. That does not predict its D5 outcome or runtime; the completed
n50 slice is a relevant negative producer observation. The completed n47 count and D5 attempt
retain their frozen identities. Any n50 D5 launch needs its own
finite dollar reservation, current budget admission, exact source and input
readback, and an independent D5 checker acceptance before an LFD-at-least-six
claim. The November 10 monthly Budget readback is already above the
owner-authorized USD 1,300 ceiling; no new experiment is admitted under it.
