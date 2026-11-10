# Trace-slice closure and exact finite-selector labels

2026-11-09. Continued source-level research.


## Exact trace-slice feedback and finite-selector CLI

The trace-slice note replaces x,y by independent x in V and t in W=V intersect kerTr. Its exact affine-multiplier conditions characterize the complete first quadratic feedback step. The epsilon multiplier space (VW)^perp has dimension at most one, with an exact rank-one trace-form characterization. Full iterative stability remains open. The inverse-Gold note supplies an F8 counterexample to blanket exclusion of inverse-power invariant subspaces, an exact subspace-polynomial divisibility criterion, and the inverse-cube necessary condition c2*c0^2=c1^3. None is a growing LFD lower bound.

`python3 join_finite_selector.py PARAMETERS.json WEIL-SYSTEM.json --output NEW.json` checks the exact cyclic sorted-code producer format, including repeated/nonlinear selectors and zero selector bits. Parameters use schema semaev.finite-selector-parameters/v1 with n,modulus,a6,z. It independently reconstructs maps and every original S3 row by field evaluation and Mobius inversion, then labels only LFD<=N+1. No solution count, exact LFD, FFD or whole-dataset admission is inferred. Wire limits are1MiB, n3..64 and selector bits0..6 per summand.

Seven new symbolic software controls and four existing retained-join controls pass. The accepted artifact in finite-selector-controls is a hand-constructed software fixture, not a production record. The saved CLI46 audit was inspected: its m2 cases are enumeration/PKM/double-large-prime; F4/F5 cases are m3. It therefore does not provide a production m2 Weil artifact for this join. No new scientific trial, solver run, native build or cloud job occurred.

Sources: trace-slice-cubic-parametrization.md and review; inverse-gold-subspace-obstruction.md and review; finite-selector-bounds-and-transfer.md and review; current producer boolean_solve in solvers.rs. This continues the retained literature/definition audit without a novelty claim.

Next: classify the quadratic tops produced by the first feedback step and prove or refute their stability. The counterexample rules out a blanket inverse-power impossibility claim, not an asymptotic obstruction for n>=5.
