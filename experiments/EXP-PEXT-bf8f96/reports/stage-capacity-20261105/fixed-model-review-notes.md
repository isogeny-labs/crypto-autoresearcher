# Read-only fixed-model design review, 2026-11-05

Reviewer: separate coordinator subagent `/root/coordinator_fixed_model_review`. Scope: source-bound radical algebra, invariant basis, fixed-field multiplication and component geometry; source inspection only. No scientific cohort was run and no research status was changed.

The reviewer found no counterexample on the inspected fixture arithmetic. The semilinear descent principle applies to a finite Galois action on a vector space; the implementation checks order n and constructs fixed vectors. This supports the route as a design, not an independent verification of the complete algebra.

Open checks:

1. `fixed_field_multiplication.py` computes and reconstructs products through the same producer radical-algebra multiplication table. A separate arithmetic implementation has not verified every structure coefficient.
2. `fixed_model_geometry.py` replays square-class relations and compares ranks and dimension, but reads no multiplication coefficient or source-generator embedding. Its branch genus path calls the existing `generic_disjoint` implementation.
3. A standalone verifier should consume serialized model bytes, check every basis vector, product and unit after base change to K(x), verify `Y0²=f0`, and derive geometric component count and genus independently.

This review does not approve EXP-PEXT-bf8f96 or certify an admissible minimum.
