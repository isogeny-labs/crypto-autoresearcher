# IC arity/oracle semantic review packet

Date: 2026-11-01. Goal: GOAL-ECDLP-001. Lane: BATCH-a68666.
Fresh hosted verification and narrow target-receipt custody checked; verification
snapshot publication pending. Neither semantic reviewer has run.

Workflow [41275109694](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/41275109694),
attempt 1, succeeded at its pinned published head
`7e1827b530349c633d98c96185e8196669812cb4`. GitHub confirms that the actual
formal-workspace job ran root generation, dependency checks, build, complete
formal gate and artifact upload. Independent replay of the committed capture
finds no strict-checker errors: all 191 tracked snapshot blobs match the pinned
commit; the complete 75-entry workspace and 10-entry verifier maps match.
Semantic fidelity remains pending; a build certifies the stated formal object.

Exactly six sidecars are committed at
`e887f4cd75b16db6e47342d1f319bf393888707c`, parent the pinned workflow head.
They contain a lossless base64 copy of the exact 67,574-byte native target receipt,
SHA-256 `75e52bc6bb7a034f81103166cf463d3f660b39b863177b797f7039f58394bc0a`.
This receipt remains `semantic_review: pending`. Its source identity is not
relabeled as the branch's later evidence/claim commits.

Custody is accepted narrowly for that committed target receipt, its embedded
build/named-audit logs and six provenance sidecars, together with independently
checked GitHub artifact ID 13072015323 and digest
`55289254e49c26fbe6c2a3258cbc2bec50afc56c2a46236305b4bc9f1aaea600`.
GitHub retention expires `2027-01-30T04:58:42Z`. Raw ZIP S3 archival is
`unavailable_not_attempted`; temporary ZIP copies are not durable.
No S3 success or permanent retention of the entire artifact/log ZIP is claimed.

The native archive verifier passes for the six producer sidecars and both task
IDs in their commit message. Full TASK-20261101-6fd5e3 archival also requires its
two new task-owned [snapshot receipt](../../../coordination/goals/GOAL-ECDLP-001/batches/BATCH-a68666/archives/TASK-20261101-6fd5e3/snapshot-receipt.json)
and [current-head gate](../../../coordination/goals/GOAL-ECDLP-001/batches/BATCH-a68666/archives/TASK-20261101-6fd5e3/current-head-gate.json).
Those files are authored but not committed/published yet. Therefore
`allows_reviewers=false`: this is a publication blocker, not a failed custody
or mathematical result. Commit/publish the two files and control metadata with
both verification task IDs in the message, then bind and pass the full
eight-artifact archive check before opening the gate. No extra workflow is
authorized.

PR [#2892](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2892) is
currently draft at `7ecd8396c797d2e8e591bed461ac3401b98e469a`, two
claim/release commits after the sidecar commit. The source workflow claim was
released completed; the verification-snapshot epoch-1 claim remains live and
has not been released by this task.

The earlier source packet remains frozen at
`f87479876dae4b04ef95e2118e2b57f129373412`; its 31-path archive verified
under attestation `a1bfa648c68f2572be959bfa8d00ca559df61bbb`.
The historical PR2854 receipt is retained unchanged in
`receipts/ic-arity-oracle-threshold-20261024.json` and
[receipt-manifest.json](receipt-manifest.json). Its original strict map mismatch
is preserved as history; the fresh receipt supplies the later exact source
closure. Neither receipt proves H1-H4 describe a full ECDLP algorithm.

[review-plan.yaml](review-plan.yaml) and [blind-input.md](blind-input.md) retain
their original hashes:
`2ce285e77cd85699f47a9ee4826775fdfc2a077168000fbae30e805b81813e92` and
`a109fc6cdf7df0e6b52e0e3717d54bb20ec0803687d8602afda065ada4f79914`.
The [prospective addendum](review-plan-addendum-01-current-head.yaml) changes
prerequisites and widens protected inputs; it changes no joint, claim, owner
or blind mathematical input. B receives only the three-file isolated input,
never receipts, producer proof, this README, full plan, history or sibling output.
Reviewers remain mutually blind. Archive both outputs before Coordinator synthesis.

| Task | Role |
| --- | --- |
| TASK-20261101-3b23eb | Historical receipt/input preparation |
| TASK-20261101-510074 | Published source snapshot |
| TASK-20261101-9a4a63 | One hosted workflow, completed release |
| TASK-20261101-6fd5e3 | Fresh verification snapshot, publication pending |
| TASK-20261101-bd53ca | Independent declaration/scope review |
| TASK-20261101-e90be2 | Independent blind derivation |
| TASK-20261101-4b30bd | Review output snapshot |
| TASK-20261101-bc06d9 | Coordinator synthesis |
| TASK-20261101-7e3b01 | Final snapshot/publication |

The queue is `coordination/goals/GOAL-ECDLP-001/batches/BATCH-a68666/dispatch_queue.json`. Ready-task selection does not
override publication, archive, claim or independence gates. No reviewers,
scientific trials, source/proof edits, EV/DEC/H transitions or goal completion
are part of this archive turn. Full corpus ledger validation remains unavailable
in the sparse checkout; scoped card/queue/plan checks do not replace it.
