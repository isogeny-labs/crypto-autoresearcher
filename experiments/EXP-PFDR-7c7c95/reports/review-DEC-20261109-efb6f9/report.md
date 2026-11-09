# Independent PFDR pilot-input review

Decision DEC-20261109-efb6f9; EXP-PFDR-7c7c95 / RUN-PFDR-1e5d2b / GOAL-PFDR-fd09e0.

The independent validator verified all 960 expected raw-grid keys, 160 consistent curve identities, 30 sizing cells and 40 plant configurations. Independently derived JSON content matched the producer design. Eleven receipt-listed artifact hashes plus the separately hashed receipt were checked. The original receipt remains invalid_output, with no checker invocation.

Derivative input was withheld: the manifest hypothesis is absent from the frozen plan, and six frozen protocol arms bind driver hash 567e18b9... instead of executed 96ba0604.... The predefined full-provenance gate failed. No derived-design.json was written; no new scientific stage is authorized. This is a technical input-admission decision, not a hypothesis outcome.

Two nonce-selected 16-bit rows were independently recounted: b16-t0.30-d1-c23 reported/recounted 2/2; b16-t0.35-d2-c7 reported/recounted 6/6. Each used one null replicate. The replay shared the pinned curve generator and seed mapping, while independently implementing point arithmetic, lift/base construction and unordered-pair counting. It does not establish all-row or full point-order correctness.

The replay ran once under timeout 300 s, one-core affinity, CPU 300 s and address-space 2 GiB limits, taking 0.397596085 s wall time as recorded by the tool. CPU usage and peak RSS were not sampled. An earlier guarded metadata recompute failed when git could not mmap a large pack; read-only arithmetic was rerun without that guard. This deviation is preserved in the validator report.

Three of seven study attempts are consumed; four remain but are held. No retry or cap increase follows. The unapproved software candidate run_manifest_v3.py fixes explicit identity/input binding and quoted argv; four candidate tests and five historical-envelope tests pass, including all four generated prospective stage envelopes and 19 contradiction mutations. Scientific functions/constants match the frozen source by AST comparison. Software tests do not admit a research input.

Scope: supplied pilot rows and bounded recount only. No slope, growth, control, cost or hypothesis verdict. No canonical scientific graph was changed. The diagram shows the technical admission path; numerical entries are direct records from the independent report.

Sources: independent-validation/report.json (SHA256 bae694922bd2b22207d3fd0c0a0819d089395d74441e867c737c52b03fc2d3af), session-receipt.json, recompute-result.json and replay/; ledger/decisions/DEC-20261109-efb6f9.yaml; prior report reports/run-20261109T1759Z/report.pdf; immutable source receipt and data. Raw rows are stored by SHA256 with a fresh remote-download readback at diagnostics/pilot-admission-failure/storage-readback.json. Full per-file hashes and unperformed checks are in the validator report.
