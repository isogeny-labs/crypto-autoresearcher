# SA-12b deviations
1. 1200 s per run instead of 1500 s (6 runs sequential, single process, nice 10). Episode counts differ widely by seed (477 to 16930) because host load varied; budgets are equal in wall clock, not in episodes.
2. No SA-01 MILP "exact convex optimum". Its certification metric differs from cert.py's (it picks leading monomials), so differences against it would not be matched. Matched reference = best convex-mode search over 3 seeds plus a deterministic convex grid (grid_convex.py) under the same cert.py metric. The grid crashed on first run (tuple compare with None), was fixed and re-run with a 300 s budget; it reached 0.1193 (n=196), below the convex searches, so it is not a tight optimum.
3. Search settings: BMAX=9, TMAX=5, NROWS=400, NCAP=300, evolutionary search only, instance seed 1, 48-bit p cert instance (cert.py unchanged).
4. Planted fpylll validation (plant.py) not run at 20 trials: the SUCCESS precondition (full > convex + 0.005 on >= 2 seeds) was not met. plant.py was only smoke-tested on a small box family.
5. Per-seed mapping: seed s of full is paired with seed s of convex, and also with the best convex over all seeds; both reported.
6. The .resume checkpoint of CLAUDE.md was not filled (brief forbids touching the repository).
7. A pkill of the chain was denied by the classifier at one point; the chain was left to finish and exited normally (done.flag).
