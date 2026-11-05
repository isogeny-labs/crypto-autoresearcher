# EXP-PEXT-bf8f96: fixed candidate batch layout and custody

The [batch sealer](../../implementation/candidate_batch.py) now places every published cohort/class/T candidate unit in a deterministic class-major, T-minor slot. It seals at most 16 write-once unit directories per tar, binds each member's SHA-256 in a manifest and each tar/manifest in a receipt, fsyncs the tar and receipt, and reads every member back before deleting its source directory. A failed or partial attempt is retained for reconciliation. The complete index is written only after all fixed chunks pass readback; verification rejects a missing, extra, changed or partial chunk, a changed index, and leftover unit directories. The reader handles the repository artifact store's raw and compressed forms.

The [layout inventory](layout-inventory.json) recomputed the full original published input plans without emitting any candidate rows:

| Cohort | Classes | T units | Fixed chunks | Per-cohort storage ceiling |
| --- | ---: | ---: | ---: | ---: |
| q3/n5 | 488 | 974 | 61 | 2.92 GiB |
| q5/n3 | 252 | 504 | 32 | 1.53 GiB |
| q7/n3 | 690 | 1,378 | 87 | 4.16 GiB |
| q11/n3 | 2,662 | 5,322 | 333 | 15.93 GiB |

These ceilings derive from 49 MiB per tar and are not measured output sizes. The four ceilings total 24.54 GiB, above the 20 GiB currently free on the local `/var/tmp` filesystem. `/home/ec2-user` is a separate NFS mount; a final execution location and durable artifact path must be verified prospectively against the six-run, 4 GiB, 24 CPU-hour, zero-cloud budget. The sealer's 3 MiB per-unit gzip allowance is a stop condition: an oversized actual unit leaves its source and partial attempt rather than silently changing the layout.

The [software test log](software-tests.log) records 11 passing tests for batch custody, the unit artifact, independent artifact replay and published input binding. The batch tests seal two F27 fixture units, restore and independently replay their exact members, refuse a changed tar and index, refuse a stray partial chunk, retain an oversized source, and read back a repository-compressed chunk. They are software fixtures, not scientific cohort trials.

The production driver still needs to build and bind the binary, iterate the fixed slots under the supervisor, invoke a persistent independent checker, and produce the remaining stage artifacts. Coefficient-aware descent, Type2, C0–C7, analysis, the six-stage trial plan and preapproval packet remain. The contract stays `review_required` and unfrozen; no scientific cohort trial was launched.
