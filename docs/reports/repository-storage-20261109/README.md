# Repository clone size and archive inventory

The current tree contains 9,700,442,379 tracked bytes in 177,922 files. The
local clone's Git packfiles occupy 2,763,200,494 bytes even though it began as a
shallow checkout. Experiment outputs, coordination copies and research archives
dominate the tree. Git already compresses its objects; recompressing the pack
alone cannot remove the current archive payload.

A real GitHub clone using the new `code` profile, shallow history and a blobless
filter succeeded. It materialized 4,652 files: 85,711,122 worktree-file bytes and
30,143,692 Git packfile bytes. This profile intentionally selects source, tools,
skills, tests and documentation. It does not claim an equivalent full research
checkout, and campaign execution refuses the profile while research state is
absent. The source revision and exact counts are in `summary.json`.

The clone helper now defaults to one commit, one branch and no tags, applying
its sparse rules before the first checkout. `--full-history` opts into the
selected branch's history; the existing `harness` profile remains available
for execution and retains trial-plan coverage receipts. Whole-ledger
coordination still needs a full checkout. The README provides a bootstrap
command that works before any checkout exists.

The existing artifact policy selects 3,146 files totaling 7,359,114,826 bytes
for lossless movement into the shared content-addressed S3 store. The estimated
remaining tip payload is 2,341,327,553 bytes, before generated manifests/ignore
rules. Directory totals and the source revision are recorded in `summary.json`.
No archive has been deleted, rewritten, or declared migrated. After installing
the AWS CLI, a read-only bucket check returned `Unable to locate credentials`.
Actual offload must use `tools/artifacts/artifacts.py push` followed by remote
verification before committing manifests and removals. Git history is retained
under the current owner policy; old blobs remain in ordinary unfiltered
full-history clones.

Sources reviewed: `docs/artifacts.md`, `docs/artifact-storage.md`,
`docs/sparse-checkout.md`, `tools/artifacts/artifacts.py`,
`tools/sparse_checkout.py`, its real-Git tests and the clone commands documented
by `git clone -h`. The audit uses Git tree sizes, actual packfile sizes and a
real filtered clone. These are operational storage observations, not research
performance or cryptanalytic claims.

Readiness checks also found a new upstream `autoresearch` entry skill missing
the direct default-loop reference; both skill surfaces now link it. Its upstream
agent-contract growth put `audit-curve` 17 words over the wake budget; the
redundant loop-context paragraphs were compacted without changing the audit
procedure. The live Codex probe remains blocked by an expired refresh token;
code readiness does not establish authenticated live execution.
