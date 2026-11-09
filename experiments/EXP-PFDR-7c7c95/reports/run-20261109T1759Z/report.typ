#set page(paper: "a4", margin: 17mm)
#set text(size: 10pt)
= PFDR recovery pilot: manifest admission failure
*EXP-PFDR-7c7c95 / RUN-PFDR-1e5d2b* H-PFDR-ed7ccf · GOAL-PFDR-fd09e0

The pilot wrote *960 job records* and exited 0. The supervisor recorded *invalid_output* before invoking the checker because the frozen plan omitted hypothesis_id. Four downstream stages were not started. The driver's own completed-valid label is not supervisor acceptance.

#image("pipeline.svg", width: 100%)

#table(columns: (2fr, 1fr), [Recorded item], [Value], [Requested stages], [5], [Attempted / output-validated], [1 / 0], [Invalid / unstarted], [1 / 4], [Driver-reported cells / plants], [30 / 40], [Driver-reported planned census curves], [20,151], [Driver wall time (recorded)], [138.781 s], [Supervisor interval (derived)], [139.258580 s], [Driver CPU time (recorded)], [548.207 s])

No census was performed. Driver summaries are preserved, unaccepted outputs. Three attempts are consumed across the linked study; its seven-attempt ceiling and zero-retry rule remain in force. CPU time sums the driver and its children.

*Custody.* Launch authority 95ff8c4f46738b620eb1ce2f01a4bb987c894268; owner executor-pfdr-recovery-20261109, epoch 1. Bundle published at d751c23c60. All receipt-listed artifact hashes were checked. The supervisor interval is the difference between its recorded start and finish timestamps.

*Conditions.* Bits 16/20/24/28/32, theta 0.30/0.35, d 1/2/3, h=2; 20 random-symmetric null bases, planted controls and A/A calibration. Original seed namespace EXP-PFDR-ada71b and seed blocks 12000000/12100000/12200000/12900000 retained. Python 3.12.15 on ip-172-31-21-148.us-east-2.compute.internal. Live aggregate memory limit 4 GiB, CPU quota four cores; total scope wall ceiling 108000 s including shutdown. No scientific controls or solve certificates were accepted by the skipped checker.

*Additional custody finding.* The frozen protocol arms retain driver hash 567e18b9..., while the executed plan binds 96ba0604.... Protocol adherence is unresolved; preserve the frozen record and correct identity prospectively.

*Next action.* Independently validate a derivative input from the preserved pilot rows, if the frozen evidence supports it; test every manifest identity field before proposing the four remaining stages. Preserve the invalid receipt and do not rerun the pilot. No scientific conclusion or canonical scientific graph changes follow from this failure.

*Sources.* runs/RUN-PFDR-1e5d2b/{execution-receipt.json, launch.json, manifest.yaml, raw-result.json, pilot-jobs.jsonl}; specification.yaml; protocol-resource-v2.json; DEC-20261109-6f42d4. Exact command, plan hash, numeric inputs and derivation are in report.md and report-inputs.json.
