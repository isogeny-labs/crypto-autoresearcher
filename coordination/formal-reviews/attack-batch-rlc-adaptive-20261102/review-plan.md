# ATTACK-BATCH-RLC-ADAPTIVE-CANCELLATION review plan

Producer input: crypto-autoresearcher PR #2955, head `4018237b567f1a565b3f7296c8c6175b3703cd2e`; frozen target `formal/targets/attack-batch-rlc-adaptive.yaml`; source `research/cryptographic_assumption_attack_corpus_20261101/README.md`; theorem `CryptoResearch.AttackCorpus.AdaptiveBatching.adaptive_rlc_cancellation`.

Prior: The adaptive cancellation is a field identity. Fixed nonzero linear errors should have at most one root in a field. Lean syntax, the finite-cardinality encoding, and exact source fidelity remain unchecked. No probability, transcript or protocol result should be inferred.

Load-bearing joints:

1. Source reviewer: compare theorem type and proof with target and source; test whether adaptive half applies to arbitrary fields, finite half applies only to finite fields and fixed a,b, and the cardinality is actually bounded. Attack by dropping fixedness and by allowing the zero pair. Check imports, no holes/custom axioms, and named declaration. No local heavy build.
2. Blind reviewer: re-derive the two mathematical claims from the statement alone, without reading producer code, target file, source README, PR diff or source review. Test the zero pair, F2, composite ring ZMod4 as a field-boundary control, and a challenge-adaptive error choice. Identify what is needed to turn a root count into probability or protocol security.

Machine gate: exact PR-head hosted `formal workspace (lake build + axiom audit)` including named target receipt, source/toolchain hashes, elaborated type and transitive axioms. Distinguish any failure from semantic mismatch. Do not run a local heavy build while other host workloads are active.

Synthesis: no `validated_scoped` verdict until current-head machine and both independent review dimensions pass. Leave source_status STATED and all experiment/hypothesis statuses unchanged. Archival reviewer tasks and separate reports are required before any claim transition.
