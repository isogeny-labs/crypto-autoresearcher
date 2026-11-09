# Prospective C3 reverse cocycle construction

**Scope:** Source-only design increment for EXP-PEXT-bf8f96 and H-PEXT-c3a11d. The experiment remains `review_required`, `frozen: false`, and without a trial plan or approval. No scientific cohort ran.

## Sources and assumptions

The [square-class and descent source](https://eprint.iacr.org/2015/805.pdf), sections 3.1–3.3, and [Type2 branch-pattern slides](https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), slides 25–26, remain the draft contract's retrieved primary sources. The existing [candidate-order report](../c3-candidate-order-20261109/report.md) recorded their assumptions and the C3 software scope. This increment implements the already declared C3 reversed representative/enumeration control; it adds no mathematical prediction or novelty claim.

## Construction

The cocycle index now has a reverse rebuild path. After the canonical map is constructed and the canonical candidate summary is checked, the path clears the map while retaining its allocation. It visits canonical transversal ordinals in reverse, checks each yielded matrix against its stored canonical ordinal, and inserts the cocycle at that ordinal. It then recomputes all canonical matrix cocycles and checks that each maps to its original ordinal. Duplicate, coverage, field identity, and entry-limit errors abort before unit output. The future unit then reverses representative and rational-image candidate streams and nonrational branch-root traversal, compares the complete exceptional-candidate summary, and emits a strengthened marker required downstream.

The method reuses the existing cocycle map allocation, but adds reverse traversal, cocycle computation, and a full ordinal check per index. Full-cohort time and peak-memory effects are not yet qualified against the six-run, 4 GB, 24 CPU-hour, 24-hour, zero-cloud-dollar, no-retry ceilings.

## Fixture checks

The combined focused Python suite passed 15 tests. A Rust test checked all 819 F27 structure ordinals after reverse rebuild and confirmed rejection below the declared entry limit. The two fixed F27 candidate forms retained 279 and 1 exceptional candidates. These checks are software fixtures, not P1–P4 or C0–C7 cohort observations.

C3 remains prospective until full-cohort qualification and independent review. Certified descent/counterexample metadata, final C5 blind custody, H1 q13, complete controls and analysis, lawful lane, Executor runtime, trial-plan/RUN allocation, runbook, preapproval packet, and protocol freeze/approval remain unresolved.
