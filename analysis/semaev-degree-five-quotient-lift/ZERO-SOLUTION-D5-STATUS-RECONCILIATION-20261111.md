# Retained zero-solution D5 status reconciliation, 2026-11-11

This is a read-only reconciliation of **six named completed attempts**, not
an exhaustive inventory of every n47–n51 input. I read each retained count
output, producer stdout, terminal result, and candidate-file presence. Each
count output is `0`; each producer reports full provisional relation rank
and `projection_kills_one`; none has `degree5.bin`. The producer reports
are observations of their pinned runs, not independent primal certificates
of `1 in W_5` and not D5 nonmembership certificates.

| Named attempt | Presentation | Provisional rank / coordinates | Result SHA-256 | Producer stdout SHA-256 |
| --- | --- | ---: | --- | --- |
| `fresh-n47-poly-00-D5-cascade01-highmem01` | original 48-variable | 30,546 / 30,546 | `e48f69f3458c4a945b6b278553b338f24841bc5411afbcad7f536fb7de7d84a3` | `855b8a4144b57fdfef109ee66c8f5e74e3c89119acb6703ea873f9f00fdd90a1` |
| `fresh-n47-poly-03-D5-cascade01-highmem01` | original 48-variable | 30,546 / 30,546 | `9197e84688425c7df18c1cc3ef9423d3c05eb5f16e51fb624fc844436709b21b` | `855b8a4144b57fdfef109ee66c8f5e74e3c89119acb6703ea873f9f00fdd90a1` |
| `n47-rand00-d5-local-002` | original 48-variable | 187,583 / 187,583 | `ef3b976ca2d1783419508ec5a6ece0901028a5a966b9a2374043963e8882a947` | `13e7e1540b79ac715ff98da1455fefc7e15485d601b1c9e4185043506e9a9e3d` |
| `n48-poly04-D5-local-001` | original 48-variable | 42,791 / 42,791 | `d95cf75b50d3215dca96a077b49df91d94b8853798873a711e63708a272677e2` | `fcdbca66f3912510d62cf4e1145d6f43e6534748e3a0edf0a1706a6de33c4922` |
| `n50-poly03-sliced-D5-local-002` | affine slice, 49-variable | 79,556 / 79,556 | `94cf8b22290449a15f89f76bd2d1f5be4b8b2b403d80e6ae6504eea28d09179f` | `966cf07362d2bada0464e336d9bf7968fa63adc961bbb05e79cadf25f8c39684` |
| `n51-poly01-sliced-D5-local-001` | affine slice, 51-variable | 103,877 / 103,877 | `c095cc43f97292e1ac7ae3178f7a568864655ea02bc0f2eee04c67a204147a25` | `fb9b443bcb353532c7bb25224817633dfc4251216ab1e360bd64f8b0d4333b6d` |

The two n47 polynomial attempts have return code zero in their retained
`result.json` stage records. The other four have separate terminal producer
receipts recording return code zero and no timeout; the n48 receipt marks
`wall_valid=false`, so its elapsed seconds are not used here. The n47
random attempt also has a separately rebuilt zero count, as recorded in
`N47-D5-RESULT-20261110.md`. The other counts in this table are retained
run outputs and need their own independent recounts for a paper claim.

The three retained n47 polynomial D5 *candidate maps* are a different
set of inputs with two recorded solutions each. Their row-by-row audit in
`RETAINED-D5-MAP-SCREEN.md` shows that those particular dimension-two maps
are exactly two-point evaluation and give no strict codimension gap. The
original n50 polynomial03 attempt remains unlaunched, but its internal
affine slice above has already killed the constant in the **same intended
D4-seeded construction**, subject to the kernel-equivalence and producer
verification boundaries in `N50-REBASE-KERNEL-SOURCE-AUDIT.md` and
Proposition 2.5f. Repeating that seed on the original system should be
reviewed before spending the proposed reservation.

The unlaunched n51 polynomial00 six-solution system remains a distinct
candidate: a checked D5 quotient with codimension at least seven would
establish LFD at least six by Proposition 1.4. Its old D5 and solution-factor
gate deadlines have expired, so neither can be launched under those frozen
authorizations. The n50 random00 zero-solution D5 source envelope is about
152.4 GB, above the current host admission. These are the material
unresolved target choices after the six reconciled negative producer reports.
