#set page(paper: "a4", margin: 20mm)
#set text(size: 10pt)
#text(size: 18pt, weight: "bold")[Prime SAT transform validation: first attempt]
#parbreak()
#image("diagram.svg", width: 100%)

#text("Producer01 recorded 404 accepted control observations, then stopped on an exception in a negative-control assertion. The certificate adapter raised `ValueError: certificate identity is not one` for the mutated multiplier. The control expected a returned `valid: false`, so the exception terminated the suite. These are partial producer observations, not an independently checked suite result.")
#parbreak()

#text("Experiment EXP-PNEXT-6558d8; goal GOAL-PFDR-fd09e0; run RUN-PNEXT-201c3c; producer TASK-20261105-f5b52d. This is software validation of the exact shared-chart k=2 transformation, with original, raw-A0, appended-row-A0, positive and negative arms. It does not replace the original 106 coordinate and 6 coefficient comparison cells.")
#parbreak()

#text("One attempt started, one failed, zero completed successfully, zero timed out. Native status is `infrastructure_error`; the recorded cause is a control-harness implementation failure. The failed mutation is not one of the 404 accepted records. Failure-injection, tiny-census and native-smoke stages were not reached. Recorded native instances, native calls and census assignments visited are all zero. `results.json` is absent. Certificate and complete projected-set validation remain incomplete; no independent review occurred.")
#parbreak()

#text("The launcher recorded 101.5076938860002 seconds; the final raw receipt recorded 99,344,080,507 elapsed nanoseconds. These are different accounting boundaries, not comparative measurements. CPU time, maximum RSS, exact hardware identity and exclusive-host timing are unavailable. Live resource readback recorded cpu.max=100000 100000 (one CPU-equivalent quota), memory.max=2147483648 bytes and memory.swap.max=0. The 600-second attempt ceiling was retained. The unit terminated; slot1 is consumed and no automatic retry is allowed. Campaign allocation remains two producer slots plus one independent slot, aggregate 1800 seconds, concurrency one.")
#parbreak()

#text("The admitted source commit was cb19afa73bd93b9e9fb2b785aa21f5d474684a99; the instrument source commit was 4cfbf920488fdcb2eef3d61104318c60aac665c7. Source hashes are in the sealed environment.json. Dirty state and runtime model identity were not captured and remain unknown. Seed0, one fixed suite, fixed control order; native ceilings were 12 instances / 192 calls and tiny census 8 fixtures / 64 assignments. The recorded command is in command.txt and reproduced below.")
#parbreak()

#text("The export contains one failed terminal negative-control row. It deliberately omits unavailable per-arm control_records. Its schema and file hashes are checked separately from protocol coverage: the latter is incomplete because four arms lack export rows and the suite ended early. No unexecuted rows are manufactured to satisfy the coverage checker. All cumulative observations remain in the native compressed bundle.")
#parbreak()

#text("The native run directory is sealed and unchanged. Its partial manifest omits required schema fields; a separate hash-bound superseding envelope records the failure without replacing the original bytes. The compressed bundle is 34,576,744 bytes with SHA-256 db10e77728bd51c0c938c68f8a150b37b30d181446b7c5f6072d26c83afbde59; its logical tar is 707,645,440 bytes with SHA-256 52d5a0557816f9308897f3d89e76128de90089c7f8a4343fd2a6e1d318ca08cc. Producer custody references this stored artifact rather than duplicating it.")
#parbreak()

#text("Next diagnostic step: separately admit a narrow control repair requiring the exact expected exception type and message for multiplier and blocker mutations, retaining the valid literal-certificate control. Publish the correction and exact admission before considering the remaining producer slot. This report neither authorizes nor performs that repair or retry.")
#parbreak()

#text("A pipeline diagram is used because this failed attempt has no pair of comparable performance measurements. Canonical mathematical and performance graphs are unchanged: this record adds a software failure observation, not a new evidence verdict. No cloud job was submitted for this report.")
#parbreak()

#text("## Evidence and command")
#parbreak()

#text("All evidence references are internal captured artifacts. Run directory: experiments/EXP-PNEXT-6558d8/runs/RUN-PNEXT-201c3c/. Primary files: execution-receipt.json, environment.json, raw-result.json, manifest.yaml, attempt-files.tar.gz. Within the bundle under actual-attempt/: worker-error.json, launcher-receipt.json, resource-readback.json and raw/30aef03f30c0441aaac3b07d4dcceef1/00000407.json. Frozen protocol: coordination/prime_sat_transform_validation_20261105/protocol.json, canonical digest 4cf22c61d3a07e1d0f52254641f2a21e0d0e201c39a95005e30fddfea866e93f.")
#parbreak()

#text("[\"/home/ec2-user/prime-sat-research-venv/bin/python\", \"coordination/prime_sat_transform_validation_20261105/trial-adapter.py\", \"--run-dir\", \"/home/ec2-user/crypto-prime-sat-ideas-20261029/experiments/EXP-PNEXT-6558d8/runs/RUN-PNEXT-201c3c\", \"--config\", \"experiments/EXP-PNEXT-6558d8/config.json\"]\n")
#parbreak()
