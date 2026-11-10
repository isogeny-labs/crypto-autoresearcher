# Exact reference LFD analysis and mandatory feedback dimension

2026-11-09. Software implementation and source-level proof continuation.


## Bounded exact Boolean LFD reference checker

`python3 inspect_retained_lfd.py PARAMETERS.json WEIL-SYSTEM.json --operation-limit 1000000 --output NEW.json` first verifies the exact finite-selector equation join, then enumerates the actual Boolean zero set and saturates every cap0..N+1. Evaluation ranks give the dimensions of the vanishing ideal in each cap. Exact LFD is one plus the last deficient cap, or zero when none is deficient. This preserves the normalized strict-closure convention and literal input presentation.

The core supports N<=12 and has explicit input/operation limits. CLI operation limits are1..10000000; the budget covers the reference analysis, separately from bounded loading/join/hashing/I/O. Exhaustion leaves exact_lfd null and retains completed cap summaries. Results are computed reference outputs, not standalone independently checked certificates; group-lift, authenticated producer, native-instruction and whole-dataset admission remain false. FFD is not inferred.

Twenty-four software controls pass across the core, CLI, finite-selector join and existing retained join. A hand-constructed F8 repeated-selector fixture produces six completed cap rows, four code solutions and reference LFD4, using36481 charged arithmetic units. These units are not retired instructions. The cutoff1 control produces no exact label. No production artifact or new scientific sample was executed. Source snapshots and outputs are in exact-lfd-controls/.

The parallel proof note shows every half-diagonal first-feedback space has at least r independent pure-x quadratic projections when n=2r+1. This rules out adding only a bounded number of such directions to the original rectangular ansatz. It is dimension growth at fixed degree3, not growth of LFD. A full stable linked-block space remains missing.

Sources: generic-strict-closure-operation-bound.md and review; exact-boolean-lfd-criterion-review.md; exact-boolean-lfd-source-review.md; feedback-pure-block-dimension.md and review. The source-level derivations continue the retained literature/definition audit; no novelty priority claim.


The single independent set-span software cross-check failed before validation: Python3.12 raised MemoryError importing pathlib under the fixed128MiB address-space limit. The fixture was not read and no closure computed. No retry or limit increase occurred. Source, logs and failure receipt are preserved in exact-lfd-controls/independent-attempt/. The reference LFD4 output therefore has source review but no successful independent-method computational confirmation.
