# SA-12 deviations
1. The GPU policy-gradient learner in the pre-registration was replaced by CPU evolutionary, simulated-annealing and random search with the same certified-reward definition. Reason: no GPU on the host.
2. Lattice dimension capped at n ≤ 90. Reason: host shared by 18 executors on 4 cores.
3. First-batch output logs were deleted by the executor when it restarted; only the numbers quoted in REPORT.md survive.
4. The second batch was stopped by the main session (host load 12 on 4 cores) before producing output.
5. REPORT.md and DEVIATIONS.md were written by the main session from the executor's final message, because the executor stopped before writing them.
6. Final run capped at n <= 150 with wall-clock caps (full 1100 s, convex 400 s), one seed each, so it may have completed fewer than 2000 episodes; the two modes also had unequal budgets.
7. No planted-instance LLL validation, no bootstrap CI, no figure (results_table.md only).
