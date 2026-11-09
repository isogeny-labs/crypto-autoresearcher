# Prospective field-level candidate worker

**Scope:** Source-only design increment for EXP-PEXT-bf8f96 and H-PEXT-c3a11d. The experiment remains `review_required`, `frozen: false`, and without a trial plan or approval. No scientific cohort or performance benchmark ran.

## Sources and assumption check

The draft contract binds the retrieved [square-class and descent source](https://eprint.iacr.org/2015/805.pdf), sections 3.1–3.3, and [Type-II branch slides](https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), slides 25–26. This refactor changes process and artifact construction, not their mathematical claims. The existing C3 reverse-order check and scalar-preserving candidate definitions remain the required semantics.

## Static cost and construction

The published q11/n3 join plan has 2,662 classes, 5,322 curve/T units, and 1,786,323 structures per unit. A per-unit process repeated 9,506,811,006 cocycle index entry constructions and 114,081,732,072 rational-image bucket insertions across that plan, before its reverse index checks. These are source-level operation counts from the plan and loops, not measured runtime. The field-level worker builds those indices and checks reverse cocycle construction once per cohort, then restores candidate-order views after each form. It retains canonical and reversed candidate-summary equality per unit.

The supervised adapter starts one worker after the existing admission check, caps its address space at 3 GiB, enforces finite stage and unit wall/CPU limits, and keeps the fixed class-major/T-minor unit order. Each unit binds exact worker argv, form request, startup attestation, binary and plan hashes in write-once input/receipt/gzip/stderr files. The existing 16-unit tar chunks and complete index remain. The independent checker validates those bindings and the worker's clean final exit. Startup, unit, and between-unit failures retain records and cannot produce a complete index; no retry or resume is introduced.

## Checks and remaining qualification

The Rust suite passed 20 tests. A combined Python suite passed 22 focused candidate, driver, stage, independent-checker, reducer, campaign and analysis tests. Two fixed F27 worker responses matched the prior committed one-shot output byte for byte. Fixture failure tests retained partial evidence and refused a complete index. These checks establish software fixture behavior only.

Full q11/n3 and other cohort throughput, peak RSS including the Python supervisor, checker reserve, compressed artifact sizes, available storage, and the six-stage 24 CPU-hour/4 GB/24-hour fit remain unmeasured. Certified full-cohort descent/counterexample metadata, final C5 blind custody, H1 q13, remaining controls and final analysis, lawful lane, Executor route, trial-plan/RUN allocation, runbook, preapproval packet, and protocol freeze/approval also remain open.
