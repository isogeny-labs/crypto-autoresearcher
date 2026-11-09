#set page(paper: "a4", margin: 17mm)
#set text(size: 10pt)
= Independent PFDR pilot-input review
*DEC-20261109-efb6f9 · EXP-PFDR-7c7c95 · RUN-PFDR-1e5d2b*

The validator verified the raw grid and independently reproduced the pilot design. *Derivative use is held:* the manifest hypothesis lacks a frozen-plan binding, and all six protocol arms name a different driver hash from the executed source. The original invalid_output receipt remains unchanged. This is a technical admission decision, not a hypothesis outcome.

#image("pipeline.svg", width: 100%)

#table(columns: (2fr,1fr), [Independent check], [Recorded result], [Expected unique raw-grid keys], [960 / 960], [Shared curve identities], [160], [Sizing cells / plant configurations matched], [30 / 40], [Sample b16-t0.30-d1-c23: reported / recounted], [2 / 2], [Sample b16-t0.35-d2-c7: reported / recounted], [6 / 6], [Scientific trial attempts during review], [0])

*Custody and scope.* Eleven receipt-listed artifact hashes and the separately hashed receipt were checked. Independent JSON content equals the producer design, but no derived-design.json was emitted because the predefined provenance gate failed. Neither numerical agreement nor two replays supplies the missing frozen bindings.

*Replay limits.* Two nonce-selected 16-bit rows, one null replicate each; shared pinned curve generator and seed mapping, independently implemented base lift, affine arithmetic and pair count. One invocation under 300 s timeout, one CPU, 300 CPU-s and 2 GiB address-space limits; recorded wall time 0.397596085 s. CPU usage and peak RSS were not sampled. This sample does not establish all-row or full point-order correctness.

*Recorded deviation.* An initial guarded metadata recompute failed because git could not mmap a large pack. Read-only arithmetic was rerun without that guard; the scientific replay retained hard guards. The validator report preserves this failure and limits.

*Disposition.* Three of seven study attempts consumed; four stages remain held, with no retry or increased cap. The software-only manifest candidate passes four candidate and five historical-envelope tests, including four generated stage envelopes and 19 contradiction mutations. Its scientific functions/constants are unchanged by AST comparison. It remains unapproved for scientific execution.

*Evidence.* Independent report SHA256 bae694922bd2b22207d3fd0c0a0819d089395d74441e867c737c52b03fc2d3af; validator session, recompute and replay files under coordination/goals/GOAL-PFDR-fd09e0/recovery-20261109/independent-validation/. Decision DEC-20261109-efb6f9. Prior run report: reports/run-20261109T1759Z/report.pdf. Full paths, scope and inputs appear in report.md and report-inputs.json. No canonical scientific graph or hypothesis status changed.
