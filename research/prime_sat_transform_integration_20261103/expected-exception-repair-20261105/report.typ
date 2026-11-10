#set page(paper: "a4", margin: 18mm)
#set text(size: 10pt)
#set par(justify: false)
= Exact exception checks for final adapter controls
*UNVALIDATED source only* — TASK-20261105-1befe5 · 2026-11-07

The source adds an optional exact-message condition to `Controls.rejects` and updates two final-adapter negative controls. The contract names `Context.rejects`; the actual class is `Controls`. This document describes authored source, not execution results.

#image("diagram.svg", width: 100%)

When `expected_message` is supplied, acceptance requires both exact exception type membership in `expected` and exact string equality before the control record is written. A caught subclass or wrong message records failure and raises. An exception outside `expected` propagates; a normal return records failure. Existing no-message callers retain their previous behavior.

#table(columns: (1fr, 2fr), inset: 5pt,
  [*Control / layer*], [*Required rejection*],
  [Multiplier / `final_adapter_multiplier`], [Exact `ValueError`: certificate identity is not one],
  [Projection / `final_adapter_projection`], [Exact `ValueError`: prefix clause does not match its cylinder],
)

The mutations remain the same: replace the multiplier certificate with coefficient 2, or replace the projection clause with `[1]`. The valid literal-transcript positive control, adapter, transform, fixtures and all other controls are unchanged. Canonical and versioned source copies are byte-identical; root custody records their hashes.

== Preserved failure and execution boundary
The internal first-producer report records that RUN-PNEXT-201c3c stopped at the multiplier assertion after 404 accepted partial observations; its suite did not complete. The adapter raised where that assertion expected an invalid return flag. The second mismatch is identified from adapter source, not a new run.

*Zero candidate execution in this task:* no imports, syntax tests, suites, solvers, census, builds, installs or cloud jobs. Source authoring is bounded by 1800 seconds, 1 CPU, 2 GiB and concurrency one. Host and inference costs are not claimed zero. The approved native-Codex amendment leaves model identity and effective capacities unverified; no Bedrock route was used.

Separate admission is required for the remaining producer slot. Two producer plus one independent attempts, 600 seconds each, and independently authored controls remain mandatory. Full 106 coordinate and 6 coefficient cells, complete projected sets and charts, and reconstruction/certificate costs remain downstream. This repair does not adjudicate the encoding comparison or coefficient-prefix pruning.

== Source provenance
Internal sources: `../validation_20261105/producer/report.md`; adapter `../../prime_sat_prefix_adapter_20261030/adapter.py`; source contract, input bindings and policy refresh under `coordination/prime_sat_transform_expected_exception_repair_20261105/`; independent and downstream review plans linked in `report.md`. All eleven source bindings matched before editing with only the approved AGENTS.md overlay.

Root retrieved #link("https://docs.python.org/3.12/tutorial/errors.html#handling-exceptions")[Python 3.12 exception-handling documentation] on 2026-11-07: handler subclass matching motivates the explicit exact-type guard. This is language semantics, not candidate validation. Exact messages are adapter-specific and require reconciliation if changed. The control-flow diagram changes no canonical mathematical or performance graph. Root owns PDF rendering and `report-inputs.json`.
