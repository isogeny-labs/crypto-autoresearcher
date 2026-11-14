# SA-09c deviations

1. Rank computed by exact sparse elimination mod 2147483629 in C++ (`rank_sparse.cpp`), not by the random projection of SA-09b. Reason: the projection needs a dense matrix, too large for B above about 750 within the memory cap. Reproduces SA-09b's ranks at B = 15, 65, 130, 300, 500.
2. B extended beyond the prereg's 2000 to 4000 for 37a1 (extra, cheap). 43a1 and 53a1 both run to B = 2000 (prereg: one of them, to 1000).
3. Two controls for the rank code (random nonzero a_l; shuffled fibres) added at B up to 500.
4. Descent primes: five primes near 2^30 split completely in the ring class field of conductor 195; the three with cyclic E(F_p) were used (the two with E(F_p) = Z/4 x ... and Z/6 x ... would limit the span of the Heegner points). Selected on group structure before any hit was computed. Primes: 1073805769, 1073816251, 1073820199.
5. Control: 100 random sets of 49 points per prime on the same 20000 targets (prereg did not give a number).
6. Added after seeing that the primary run had 16 hits against 9.1 expected (nominal p = 0.046 two-sided): an independent replication with fresh target seeds (SEED=1000003), 200000 targets per prime, 40 control sets, and an exact-rate comparison |U(S)|/#E. The primary result is reported as run; the replication is supplementary, not a replacement.
7. Heegner points: only conductors {1, 3, 5, 13, 15} (49 points) are F_p-verified, as in SA-09b. Levels 39 and above were not algebraised.
8. No second-curve Heegner points were computed (ranks only).
9. No git or parent-directory edits. Row files (`rows_*.bin`, 60 MB total) were deleted after use; SHA-256 prefixes of their concatenation are in `rows_sha256.txt`, and they regenerate in about 100 s with `gen_rows.py`.
