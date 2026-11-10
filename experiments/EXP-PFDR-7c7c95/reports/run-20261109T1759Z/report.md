# PFDR recovery pilot: manifest admission failure

EXP-PFDR-7c7c95 · H-PFDR-ed7ccf · GOAL-PFDR-fd09e0 · RUN-PFDR-1e5d2b

The pilot driver wrote 960 job records and exited 0. The supervisor marked the attempt `invalid_output` before invoking its checker: driver manifest run.hypothesis_id='H-PFDR-ed7ccf' has no source: the frozen plan names no hypothesis. Four downstream stages were not launched. The driver's own completed-valid label is not supervisor acceptance.

The receipt binds launch authority `95ff8c4f46738b620eb1ce2f01a4bb987c894268`, owner `executor-pfdr-recovery-20261109`, epoch 1. The preserved bundle was published at `d751c23c60`; all 11 receipt-listed artifact hashes were checked for this report. The frozen plan SHA is `ad2ef87c68721f70765e8821805a2e3749a00580d2ac26e76b96bab263424814`.

The driver reported 30 cells, 30 cells marked okay, 40 plants and 20,151 planned census curves. These are unaccepted driver outputs; no census was performed. Of five requested stages, one produced invalid output, zero are output-validated and four remain unstarted. Three attempts have now been consumed across the linked study; the seven-attempt ceiling and zero-retry rule remain in force.

The supervisor interval was 139.258580 seconds (derived by subtracting its recorded timestamps). Driver wall time was 138.781 seconds (recorded). Host: ip-172-31-21-148.us-east-2.compute.internal; Python 3.12.15. Aggregate live limits were read back as memory.max=4294967296 and cpu.max=400000 100000; the scope's maximum wall interval including shutdown is 108000 seconds. The driver recorded 548.207 CPU seconds (self plus children).

Command: `bash experiments/EXP-PFDR-7c7c95/launch-recovery.sh executor-pfdr-recovery-20261109 1`. Scientific conditions and controls remain in specification.yaml and protocol-resource-v2.json: bits 16/20/24/28/32, theta 0.30/0.35, d 1/2/3, h=2, 20 random-symmetric null bases, planted controls and A/A calibration. Original seed namespace EXP-PFDR-ada71b and seed blocks 12000000/12100000/12200000/12900000 were retained. No scientific controls or solve certificates were accepted by the skipped checker.

The diagram shows the stop point because only one trial ran and its outputs were not accepted. No canonical scientific graph changes: no scientific verdict was issued. Next: independently establish whether a derivative pilot input can be validated from preserved rows, and test the complete manifest contract before proposing four-stage continuation. Do not alter this run, silently mark it valid, or rerun the pilot.

Sources: runs/RUN-PFDR-1e5d2b/execution-receipt.json, launch.json, manifest.yaml, raw-result.json and pilot-jobs.jsonl; approval DEC-20261109-6f42d4; resource readback coordination/recovery/20261109/pfdr-resource-guard-probe.json.

Additional custody finding: the frozen protocol arms retain driver hash 567e18b9..., while the executed plan and manifest bind 96ba0604.... This mismatch prevents a clean protocol-adherence claim and must be addressed prospectively; the frozen protocol is preserved.
