# Independent source review: finite-selector equation reconstruction

Date: 2026-11-09. Source-only review of `join_finite_selector.py` and `test_finite_selector.py`, against the previously inspected Rust producer `boolean_solve`/`polys_json` at commit 4be27eee881663c44318ed2d9debfad05d071538. No tests, finite enumeration, production join, native build, or scientific execution by this reviewer.

**The reconstructed equation/domain join and its sole LFD upper-bound label are sound. No correctness defect was identified.**

The checker validates the finite parameter schema, irreducible degree-3-through-64 polynomial field, canonical a6/z, and nonsingular a6. Unlike the earlier specialized inspector, z=0 is allowed here; the universal Boolean bound does not require z nonzero, and the same S3 polynomial is evaluated exactly.

The retained metadata uses strict integer and Boolean checks. For k in 0,...,6, the selector table must have exactly 2^k entries, canonical in-field codes, the correct minimal bit width for its number of distinct values, and exactly the producer's sorted cyclic padding. This handles repeated codes faithfully rather than replacing their images by a span. The constant-map k=0 case remains valid: the table has one entry, both selector blocks have zero variables, and the polynomial masks can only be constant.

The subset-XOR Mobius transform reconstructs the unique field-valued ANF of the selector table. Shifting masks by side*k embeds the maps in their separate variable blocks, including constant masks. Every coordinate map is compared with the literal retained row. The checker then evaluates the normalized S3 expression on the entire bounded 2^(2k) code domain, transforms that truth table to ANF, and compares every field-coordinate equation with the retained polynomial rows. Squaring is evaluated in the verified field. There is no span substitution, sampling, or ignored padding code.

The largest assignment domain is 4096 and the field degree is at most64; the map and equation reconstruction allocations are bounded. The inherited CLI loader limits each wire input to one MiB and rejects duplicate JSON keys. The inherited polynomial parser accepts exactly the required masks for at most12 variables, rejects duplicate monomials and inconsistent declarations, and canonicalizes term order without reordering output rows. Output is exclusive and binds input bytes, canonical values, implementation sources, and theorem/review files.

The output upper bound is N+1 for the reconstructed normalized Boolean system. This is safe also at N=0, where the bound one may be loose. Lower bound, exact LFD, FFD, and solution count remain unknown. Although evaluating all assignments could support an additional count implementation, this checker does not emit such a claim. Dataset, group-lift, and authenticated-producer admission remain false; bound_labels_admission applies only to the matched mathematical artifact.

The seven fixed controls use a separate symbolic F8 polynomial construction for a nonlinear repeated-code map and a zero-bit constant case, plus equation/map/policy/parameter/format mutations. I inspected these controls but did not rerun their reported passes. No actual production artifact was shown to pass this checker by this review.
