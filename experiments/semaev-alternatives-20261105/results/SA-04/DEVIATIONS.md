# DEVIATIONS (SA-04)

1. **msolve not used (substitution allowed by the task statement).** `pip install msolve` failed (no such distribution). A
   `passagemath-msolve` wheel was downloaded, but running the extracted binary was refused by the sandbox classifier
   ("code from external"), so it was deleted unexecuted and not worked around. Substitute: a hand-built dense Macaulay-matrix
   engine over F_p (`scripts/macaulay.py`, float64-BLAS exact arithmetic, p < 2^16, incremental RREF, grevlex column order).
   The reported "solving degree" D_sol is the least D such that the Macaulay space of degree D leaves a quotient of constant
   dimension K (= cols - rank, constant over the last >= 4 degrees and equal to the plateau value for all computed D' >= D).
   This is the full-Macaulay degree (an upper bound on the degree an F4 run with the normal selection strategy reaches),
   not msolve's internal "max degree". Absolute values are therefore not comparable with the quoted 4+floor(s/2) (digit)
   or d_F (PKM tower) numbers, whose exact definitions are not reproduced here. To keep the comparison meaningful, the
   digit-coded single polynomial S_{m+1} was run through the SAME engine on the SAME planted instances as a local baseline.
2. **cuso / flatter / the sumset, Ehrhart and LP certificate calculators were not used** (Sage / external-binary dependent,
   not installable in the time box). Part (a) uses my own Jochemsz-May-style determinant-bound calculator
   (`scripts/jm.py`, shift set = lattice points of k*Newt(f), best admissible leading vertex, extrapolation in 1/k). It is a
   HEURISTIC determinant bound, not a certificate; it was calibrated on S_3 (-> 0.1666 = 1/6) and S_4 (-> 0.0415 ~ 1/24),
   which reproduces the repository's single-polynomial values, and checked by planted LLL runs for m = 2.
3. **Un-eliminated (alpha, e) lattice not computed.** Because e_k = Q_k(alpha) is an explicit quadratic map, eliminating alpha
   is exact (hypersurface F(e_1..e_m) = 0 of total degree 2, 4, 8 for m = 2, 3, 4, found by kernel computation mod p). The
   bound is computed on F with weights (1,..,m). The reach of a lattice that keeps the full-size alpha as unknowns is
   argued (not computed) to be no better (see REPORT limitations).
4. **Scale of part (b).** Memory cap (about 700 MB) limits the dense engine to about 9000 columns: digit-coded norm system at
   m = 2 reaches B = 16 (B = 32 aborted at the column cap), m = 3 only B = 4; vanishing-polynomial version m = 2 to B about 16,
   m = 3 to B about 8. The prereg range B = 8..64 was therefore not reached for the norm system; the single-polynomial
   baseline (fewer variables) was run further. Primes are small (p = nextprime(8 B^m) < 2^16).
5. Digit base is x in [0, 2^s - 1] (x = 0 allowed); vanishing-polynomial base is x in [1, B].

## Resumed run (2026-11-05, afternoon)

6. **Interrupted and resumed by a different model.** The original executor (Sonnet tier) was cut off by an API usage limit.
   The run was resumed by Claude Opus 5.5 under /home/user/semaev-runs/RESUME_BRIEF.md. Finished results from the first
   session (part (a) reach computations, planted LLL at m = 2, Macaulay-engine sweeps in out/*.jsonl) were reused, not redone.
7. **Deviation 1 is partly reversed: msolve was used for part (b).** On the resumed host msolve 0.10.1 is installed
   system-wide by the `passagemath-msolve` package (/usr/local/lib/python3.13/dist-packages/sage_wheels/bin/msolve; SA-14
   used the same binary). Degree = largest "deg" in the F4 round table of `msolve -g 2 -v 2 -t 1` (grevlex reduced GB),
   the same parse as SA-14. The Macaulay-engine numbers from the first session are kept as a secondary, differently defined
   quantity (full-Macaulay degree), not mixed with the msolve degrees.
8. **Primes for msolve runs are not capped at 2^16** (p = nextprime(8 B^m) for every B; the float64 engine needed the cap,
   msolve does not). For B <= 16 (m = 2) and B <= 8 (m = 3) the primes coincide with the first session's.
9. **Scale reached with msolve** (time limit 120-250 s per instance, memory ~330 MB at the largest completed cell):
   m = 2 digit B = 4..128 (6 doublings; B = 256 timed out at 250 s); m = 2 vanishing base B = 8..128;
   m = 3 digit B = 4, 8, 16 (B = 32 timed out at 250 s; a retry under `ulimit -v 1000000` segfaulted at allocation, so the
   cell was abandoned rather than exceed the ~700 MB rule); m = 3 vanishing base B = 8, 16, 32 (B = 64 timed out at 120 s).
   The prereg range B = 8..64 at m = 3 is therefore covered only to B = 16 (digit) / 32 (vanishing); fewer than the 4
   doublings asked for an exponent fit at m = 3 in the digit cell. All seeds agree exactly at every cell, so no CI is given.
10. **Exact reach formula added.** Part (a) is now also computed with the SA-06 closed form delta = 1/((n+1) sum_i w_i g_i)
    (g = centroid of the Newton polytope, weights w_k = k for e_k), `scripts/reach_formula.py`, in addition to the first
    session's extrapolated JM determinant sums. It is still the JM-basic (automated-shift) bound, not a strategy-independent
    certificate.
11. `gb_len` in out/ms/*.jsonl is a comma count of the msolve output file (over-counts); the true GB sizes for the
    known-answer checks are in out/ms/planted_gb_check.json. Not used for any conclusion.
12. **REPORT.md not written by the executor.** The Write tool refused REPORT.md in the resumed session; per
    RESUME_BRIEF.md the full report text was returned in the executor's final message for the main session to save.
