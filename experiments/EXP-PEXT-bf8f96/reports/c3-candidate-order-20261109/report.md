# Prospective C3 candidate-order A/A

**Scope:** Source-only design increment for EXP-PEXT-bf8f96, H-PEXT-c3a11d. No scientific cohort was run. The experiment remains `review_required`, `frozen: false`, and without a trial plan or approval.

## Source and assumption review

The draft specification binds the retrieved [square-class and descent source](https://eprint.iacr.org/2015/805.pdf), sections 3.1–3.3, and [Type2 branch-pattern slides](https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), slides 25–26. Their recorded assumptions concern square classes, coefficient-sensitive descent, and a four-root Type2 pattern. This change implements the already specified C3 order control; it introduces no new mathematical prediction or novelty claim. The source review and assumption boundary in `specification.yaml` remain authoritative.

## Construction

Each future candidate unit computes its canonical checked exceptional-candidate summary, reverses the nonrational representative stream and every rational image bucket in place, and recomputes with reversed nonrational branch-root pair traversal. It compares the full summary before emitting the unit. Canonical structure ordinals and their matrices are retained. The emitted `candidate_order_aa` marker is required by the independent unit checker and geometric reducer. The prospective C3 sealed-data artifact checks marker coverage for every retained curve/T unit and T block while comparing canonical and reverse reduction rows, coverage, and minima.

This adds a second candidate check using existing indices; it does not rebuild the field or cocycle index. Reversal of cocycle-index construction order is still an open C3 obligation. Full-cohort runtime and memory effects remain unqualified against the six-run, 4 GB, 24 CPU-hour, 24-hour, zero-cloud-dollar, no-retry ceilings.

## Checks and outcome

Fixed F27 software fixtures included two forms with 279 and 1 exceptional candidates, including an irreducible four-cycle case. Focused candidate/independent/reducer tests passed (8), candidate census driver tests passed (4), and C3/reducer/campaign/analysis tests passed (8); some tests overlap between invocations. Missing-marker cases were rejected. These are software fixture checks, not P1–P4 or C0–C7 cohort observations.

The C3 unit traversal and sealed-reduction checks are prospective components. Certified descent/counterexample metadata, final C5 blind custody, H1 q13, complete controls and analysis, full-cohort qualification, lawful lane, Executor runtime, trial-plan/RUN allocation, runbook, preapproval packet, and protocol freeze/approval remain unresolved.
