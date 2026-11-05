# Prospective local software validation admission

This packet is staged only. No candidate import or validation has run. The protocol schema checker passed on draft04; it is not yet frozen, published or execution-approved. Earlier schema failures are retained. [pcc:unverified]

Bind the already published source16 and terminal snapshot31. The fixed source is UNVALIDATED. This stage evaluates the existing implementation; it adds no theorem gate and changes none of the original106+6 cells or five leads.

## Local launch route

Use the existing systemd252 system manager and existing sudo permission solely to create a local transient unit running as ec2-user. Do not change permissions, grant access, launch EKS or provision a machine. CPUQuota100% throttles to one CPU equivalent; it is not affinity. MemoryMax2GiB and MemorySwapMax0 are required. RuntimeMaxSec600 starts before the worker and therefore includes candidate imports. The worker reads cgroupv2 CPU/memory/swap constraints before importing candidate code. Parent launcher retains Result/ExecMainStatus/MainPID, stdout/stderr and all partial files even after timeout/OOM. RemainAfterExit preserves successful exit state until collection; root then stops the empty unit and checks termination. No probe unit has been launched. Existing host and inference costs are not asserted zero.

`launch.py --authorization <published-local-authorization.json>` is the exact launcher entry point. The template is execution_authorized=false. Root fills actual native task IDs, output/campaign scopes, source/launcher hashes, terminal snapshot binding, protocol freeze and publication receipts, then obtains exact admission before setting true. Do not invoke a false template as a probe.

The cross-attempt exclusive lock and write-once slot reservations permit slots1/2 for producer and3 for independent review. An ambiguous or refused launch consumes its slot pending explicit reconciliation; never automatically retry. A second producer attempt needs the terminal first receipt hash and explicit remaining-budget approval. It cannot silently use modified source; republish changed source first. Three slots at600s bound1800s of admitted attempt runtime, with system-manager termination/receipt collection charged separately as administrative overhead and reported. No additional solver work is permitted during collection.

The source already bounds12native instances/192calls,8tiny censuses/64assignments, fixed seed0/options and supplied witnesses. Preserve all detailed PC/native bounds in the copied plan. Parent deadlines include imports; the source's internal timer is not the outer authority. All child processes belong to the unit control group. The launcher is prospective, statically inspected only, not behaviorally tested. Any admission/launch failure is recorded without calling it mathematical evidence. [pcc:unverified]

## Native chain and review

VALIDATE01 -> RESULT_SNAPSHOT -> REVIEW -> LEDGER, each sequential, after source SNAPSHOT release. Producer is review_required=true. RESULT_SNAPSHOT publishes exact raw bundles/manifests and producer report before REVIEW. Reviewer independently authors controls, never reads or executes producer software_controls.py or producer results/reports as evidence. It may receive their hashes and candidate functions may hash package files without displaying them; this hash-only runtime operation is explicitly distinct from reading hidden test contents. No blindness lift. Root publishes the reviewer's independently authored control source and hashes before its one600s execution, while preserving the existing reviewer claim; this is source custody within the review task, not another theoretical review.

The conditional second producer attempt is not pre-authorized. If needed, retain first attempt and remaining cap, create exact repair/source-publication/attempt02 cards and actual source version, then snapshot both attempts before independent review. Do not reopen a terminal task or reallocate native cases.

Producer first invokes `software_controls.run_suite(...,run_native=True)` only via the admitted worker. Independent reviewer implements `run_independent(directory,admission=token)` under the same fixed resource/instance/census ceilings using its own controls and counter guard; it does not call producer run_suite. Root checks its frozen control allocation before its single execution. Native enforcement cannot be inferred from a Python token alone.

## Outcomes and export

Preserve actual partial nested attempt files in raw-artifacts.tar plus content hashes/byte counts. results.json is absent when the worker did not return; record absence, never synthesize a passing result. Final native archive artifact list must bind the actual result bundle, not require a fabricated result. All required control coverage, appropriate rejection layers, original checker semantics and censored disposition appear in the export/report. No performance claim or clock comparison is permitted.

The protocol uses experiment.protocol/v1 exact_computation and out_of_scope claims. Reporting must emit experiment.export/v1 against its actual frozen hash, plus per-control raw records, artifact inventory and review report. No export, successful check or outcome is written by this preparation. Do not treat the draft protocol's source commit as its later publication commit; freeze.commit is null until actual metadata publication. Statistical power is not asserted; alpha is an unused schema field.

Remaining admission requirements: exact native IDs/cards and queue, frozen protocol/publication, bound reviewer plan/amendment and root-selected result paths, static launcher/export integration checks, actual source/snapshot and runtime identities, current local resource authorization/readback, and passing applicable native preapproval. No cloud path is admitted. The original full106+6 comparison follows software acceptance under its own complete protocol; it is not replaced by these controls.

Collection custody: launcher-preliminary.json is explicitly preliminary; authoritative launcher-receipt.json is written after raw bundle/manifest collection and binds the manifest hash. A campaign terminal receipt records any subsequent custody failure. Root archive binds final receipts. Required command persistence failure consumes a reservation but launches no worker. SIGKILL at the outer deadline permits no scientific grace period.
