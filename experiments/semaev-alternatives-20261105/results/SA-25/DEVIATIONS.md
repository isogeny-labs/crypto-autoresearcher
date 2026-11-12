# SA-25 deviations and interpretations (executor log)

1. Resume-checkpoint rule (CLAUDE.md): not performed by this executor. The brief says not to touch the git repository
   and to work only in /home/user/semaev-runs/SA-25/; `.resume/RESUME.md` lives in the repository. Main session to handle.
2. Points with x = 16 are excluded as the prereg says (2 affine points at x=16: the cusp (16,-61) and (16,60)).
   (16,60) is non-cuspidal but the j-formulas have denominator x-16 there; its Atkin-Lehner partner therefore has no AL relation
   (1 point per prime, counted as AL_no_partner).
3. Ambiguous (j,j') keys (two distinct points of X0(11)(F_p) with identical (j,j'): the plane model Phi_11 has nodes) and
   j in {0,1728} are excluded from classes and relations, per step 2 ("recorded separately"). Their fraction is
   reported per prime (14% at p=1009, falling fast with p). Relations with a neighbour that is excluded are dropped
   (not "uniquely matched").
4. Hecke search prefilter: T_l is attempted only at points in classes with l^2 | D (necessary for a full rational
   l-neighbourhood). Validated: filtered and unfiltered runs give identical per-class relation counts and coranks at p = 1009, 4001, 10007.
5. n (largest prime factor of #E11(F_p)) is often tiny (7..23197 across the 20 primes) because #E11(F_p)=5*(smooth part). The prereg
   only replaces a prime when n=5 or n^2 | #E; that rule was applied literally for the 20 base primes. Consequence: rho on E11[n] costs sqrt(pi n/4),
   far below p^(1/2) for small n.
6. Class chosen for end-to-end solve: the prereg says "the class of smallest c_t". Classes with c_t = 0 have true log vector forced to 0
   (all n-components zero), so aP+bQ+T can never land in them: unusable. Rule used: among classes with c_t >= 1 and at least one point with
   nonzero n-component, take the smallest c_t, ties by smallest projected cost. Literal minima are also reported.
7. "Number of Cl(D0)-orbits" computed as the number of divisors of the conductor f of Z[pi] (one Cl(D0)-orbit per volcano level / order between Z[pi] and O_K).
8. Extra primes beyond 1e6: 1500007, 2200013, 3300001, 4600003, 6800033, 10000019 (first prime >= 1.5e6, 2.2e6, 3.3e6, 4.6e6, 6.8e6, 1e7 with valid n) and three chosen for n >= #E/12 (3000199, 6000823, 10000169), because n is often tiny (item 5). All 9 enter every fit and table.
9. End to end run at the three largest primes used (6800033, 10000019, 10000169) and also at the three largest base primes (483317, 695207, 1000003), two classes each: smallest usable c_t (item 6) and smallest projected cost.
10. Rho baseline: distinguished-point rho, 32 adding steps, same C addition routine; wall time includes its step-table setup. Rho times in the report come from results/rho_times.json (separate run, fresh targets). First e2e run (work/e2e_run1_badrho.jsonl) had an oversized rho hash table and a bug in rho step selection (negative index); fixed in src/ec.c, the reported runs use the fixed library. Stage-1 results were produced before these fixes and do not use rho.
11. v1 -> v2 refactor of stage1 (compact arrays instead of Python lists for 1e7 primes): per-class sizes and coranks identical at all 20 base primes; only the count of Hecke rows reduced to zero differs by a few at t = 0 and a few classes (rank unaffected).
