# SA-16 report (saved by the main session from the executor's hand-back; the harness blocks subagents from writing report files)

## Summary
**Verdict: KILL** of the frozen prediction "all solvers show exponent ≤ 0.5 on the controls". The control instrument works; the solvers named in the pre-registration (`L3`, raw bivariate Coppersmith on S_3) do not pass and are flagged uncalibrated.

## Deciding numbers (p = 2^128; 96-bit runs give the same δ values)
- Harness check: brute-force enumeration exponent 1.01 [0.93, 1.08].
- Control (i), degenerate conic (R a rational 2-torsion point; S_3 is exactly the square of a bilinear form, conic determinant −32 f(x_R)²): `vieta_cvp` (2-D Gauss/Babai) reaches B = 2^44 (δ 0.344) with exponent 0.01 [−0.00, 0.02]; Coppersmith on the radical form reaches 2^42; best generic solver only 2^16.
- Control (ii), R = [2]P_1: univariate Coppersmith on the degree-4 doubling polynomial reaches 2^26 (δ 0.203, exponent 0.03 [0.03, 0.03]) vs 2^16 for the best generic solver. Diagonal-aware 2-D lattice `L2diag` reaches 2^18 (exponent −0.10 [−0.18, −0.00]).
- Raw solvers: `L3` and raw bivariate Coppersmith on S_3 reach 2^12–2^16 on (ii), identical to the null. On (i), `L3` recovers nothing at any B and raw bivariate has fewer than 5 qualifying points. Flagged uncalibrated.
- Control (iii), anomalous curve (#E = p): Smart's log costs exponent 0.01 per query, but decomposition is not free. Log-table scanning costs 0.88 [0.82, 0.94] per query with setup exponent 1.01; the pair-sum table has query exponent 0.01 but setup 2.24. Lattice solvers see no benefit. Valid as a DLP control only, not as a decomposition-oracle control.
- Generic planted instances: no solver recovers beyond δ ≈ 0.09–0.125; recovery 0/20 at B = 2^18–2^22.

## Key findings
- Wherever a lattice solver succeeds, its exponent in B is about 0 (±0.15), even on generic instances below its reach. The pre-registered exponent test alone cannot discriminate, so a reach-gain-over-null comparison was added (DEVIATIONS.md item 2).
- Control (i) forces a and b of size p, which confounds `L3` there; `L3` also fails on the large-coefficient null. Its failure on (ii) is clean.
- Smart's attack needs a non-canonical lift: j = 0 curves lift canonically for any b (ψ = 0), so a was lifted as well.
- A bug that reduced g^k mod p in the radical-form lattice was fixed; affected rows were deleted and re-run.
- Idea 7 (integer programming) and Idea 12 (learned shifts) solvers were not run because none existed in the repository at run time; `SOLVERS` in run_sweep.py is the hook.

## Limitations
Reach resolution is 2–3 doublings. Host load average 25–32 during sweeps, so only slopes and recovery rates are used, not absolute times.

## Suggested lead-atlas update (LEAD-EXO-weak-class-instrument-calibration, oracle arm)
- Require any new oracle solver to reach δ ≥ 0.20 on control (ii) and δ ≥ 0.30 on control (i), or be flagged uncalibrated.
- Flag `L3` and generic bivariate Coppersmith as uncalibrated.
- Drop control (iii) as an oracle control.
