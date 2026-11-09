# PFDR pilot: command provenance rejection

EXP-PFDR-fa915a / RUN-PFDR-54a452
H-PFDR-ed7ccf / GOAL-PFDR-fd09e0

The pilot driver wrote 960 rows and exited 0. The supervisor recorded invalid_output before invoking the scientific checker because the driver recorded an absolute python3 executable while command normalization used the supervisor interpreter. All four dependent stages remained unstarted. Requested stages: 5; attempted: 1; output-validated: 0; invalid: 1; timed out: 0.

Measured driver wall time: 142.175 s. Measured driver CPU time: 561.590 s. Supervisor interval: 142.524296 s, derived by subtracting receipt timestamps. Host: ip-172-31-21-148.us-east-2.compute.internal; Python 3.12.15. No timing comparison is made. Live scope readback enforced memory.max 4294967296, cpu.max 400000 100000, runtime 107570 s and stop grace 30 s, SIGINT, control-group shutdown. Scope is now inactive.

The driver reported 30 cells marked okay, 40 plant entries and 20151 planned census curves. These remain unaccepted driver summaries. No census, slope estimate or accepted calibration result was produced.

Launch source: 888d7046e12055cacca042825907400457c2f200; owner executor-pfdr-fa915a-20261109, epoch 1. Frozen plan SHA256: 498e1c39572d1623d7af5d160723919333a64892603619eed344fa85b9298014. The source was committed at launch; the driver recorded dirty=False at completion. All 11 receipt-listed artifact hashes were checked for this report. Raw pilot data: 454355 bytes, SHA256 93f945934b83e2f8d71407f963701780d2fd785a62e4b77eb02aa5dd3d94a29a; durable artifact-store manifest in the run directory, remotely verified.

Command: bash experiments/EXP-PFDR-fa915a/launch-recovery.sh executor-pfdr-fa915a-20261109 1

Frozen conditions: bits 16,20,24,28,32; theta 0.30,0.35; d 1,2,3; h=2; 32 pilot curves per cell; 20 null replicates. Original seed namespace EXP-PFDR-ada71b; seed blocks pilot12000000, main12100000, replication12200000, selftest12900000. Scientific plan retains structured/null arms, planted controls, Z/N interval and A/A controls. The checker did not accept their outputs in this attempt.

Four historical attempts have now been consumed across the linked study. No retry is authorized under this contract. Next diagnostic: exercise actual supervisor and child interpreter spellings in a subprocess regression, then seek prospective Coordinator approval for any continuation. Preserve this receipt and do not silently promote its design input.

The diagram shows the execution stop because there is one rejected stage rather than comparable accepted measurements. No canonical scientific graph changes: this report records an operational failure only. Sources: run execution-receipt.json, manifest.yaml, launch.json, raw-result.json and pilot-jobs.jsonl; specification.yaml, trial-plan.json, protocol.json; approved launcher and coordination/recovery/20261109/pfdr-fa915a-resource-probe.json. Exact rejection text is in report-inputs.json and the receipt.
