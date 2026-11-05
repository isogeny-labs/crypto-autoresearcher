# Rho distinguished-point destination cutover is unverified

- **Status:** `investigating`
- **Kind:** access limit and operational validation gap
- **Affected work:** [rho operations dashboard](../ui/README.md#database-load-rho-dp), [temporary-credential repair](https://github.com/isogeny-labs/crypto-autoresearcher/pull/3004)
- **Next action owner:** rho migration operator with a scoped source-account read role
- **Last updated:** 2026-11-03

## Problem

The public rho operations panel cannot be called current while destination RDS
`rho-dp` in account `104186811093`, region `us-west-2`, is stopped and the
source-to-destination data and writer cutover have not been verified. The owner
authorized migration with a brief outage, but the current host's managed role
only establishes read access to the destination. The source account was named
as `590183823895`; its live RDS configuration and active writers still require
an authenticated, read-only source inspection before any cutover step.

## Evidence and uncertainty

- **Observed:** A read-only `DescribeDBInstances` call on 2026-11-03 using the
  host's managed temporary credentials returned destination `rho-dp`, account
  `104186811093`, `us-west-2`, status `stopped`. The patched `ui/ops.py` also
  authenticated a read-only CloudWatch `DatabaseConnections` query with that
  role and received no samples in the most recent hour.
- **Observed:** The public [ops snapshot](https://isogeny-labs.github.io/crypto-autoresearcher/data/ops.json), read on 2026-11-03, reports `sampled_at` =
  `2026-11-03T18:30:15Z`, `available: true`, `stale: true`, destination status
  `stopped`, no latest CloudWatch point, and `object_store: null`. This is a
  truthful stale snapshot, not evidence of current ingest.
- **Derived or proved:** The destination's stopped state and absent recent
  metrics block a live-panel validation. Data equality, source writer state,
  and cutover completion are not established.
- **Suspected explanation:** Unknown. A prior stop event alone does not identify
  the operator's intent or show whether the source is still accepting writes.
- **Missing capability:** A scoped managed source-account role or equivalent
  secure credential source for read-only RDS, KMS, writer and archive inspection.
  No access key should be put in the repository or a chat message.
- **What this evidence does not establish:** It does not show data loss, a
  completed migration, an approved write freeze, or that starting the
  destination is safe. The absent S3 size metric may have a separate bucket,
  region or permission cause.

## What would unblock it

- [ ] Authenticate to account `590183823895` with a scoped read role and
  record the live `rho-dp` source identity, region, encryption/KMS and snapshot
  settings, and the MacBook and EC2 writer endpoints without exposing secrets.
- [ ] Freeze or redirect all source writers under the authorized brief-outage
  window, capture a final source watermark and independently verify destination
  row/count and content integrity against that watermark before switching
  consumers.
- [ ] Verify the destination is serving the intended writers and readers, then
  publish a fresh `ops.json` with a recent CloudWatch point and correct source
  account and object-store interpretation. Record post-cutover rollback and
  readback evidence.

These conditions establish this destination's cutover and panel freshness;
they do not validate cryptanalytic claims or historic experiment results.

## Next discriminating step

- **Action or proof obligation:** Use a scoped source-account read role to
  inspect the RDS instance and current writer connections, then compare the
  source's finalizable snapshot/watermark with the destination archive manifest.
- **Inputs and controls:** Exact source and destination account/region/instance
  identities, source snapshot metadata, destination manifest, and both writer
  configurations. Keep the present stopped destination as an observed baseline.
- **Execution limits and stop condition:** Read-only discovery first; no new
  Spot instances, quota increase, database start, writer stop, or cutover from
  this diagnostic step. Preserve the $25/day Spot experiment budget and live
  services. Stop on missing source authority or inconsistent identities.
- **Outcomes and next actions:** A matched source identity and watermark allow
  a concrete cutover plan. A mismatch requires source or archive repair. A
  permission denial requires the scoped role; it is not a negative data result.
- **Recheck trigger:** Source-account read access, destination state change, or
  a new published ops snapshot.

A planned step is not a completed migration. Apply the existing budget,
admission, and archival rules before execution.

## Resolution and history

- 2026-11-03: Opened from the destination RDS and public-panel readbacks above.
  The temporary-credential signing fix is a separate code prerequisite and
  does not itself perform the cutover. Unresolved.
