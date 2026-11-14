# SA-21 REPORT: end-to-end ECDLP solve time, every campaign oracle in a full index calculus against matched rho

(Saved by the main session verbatim from the executor's final message; the harness refused the executor's own write. Full tables and CIs are in results/analysis.md.)

## Summary

**Verdict: INCONCLUSIVE by the letter of the frozen criteria. The substance is a KILL. SUCCESS is refuted at every size and pricing.**
- One KILL clause is unmet: IC-pair is statistically tied with rho at k = 20, 22, 24 under pricing π = 1. The ratios are 1.10 [0.89, 1.34], 0.93 [0.72, 1.22] and 1.10 [0.91, 1.34], and every solve there costs under 3 ms.
- The other KILL clause holds: every measured arm's α CI lies entirely above rho's under all four pricings.
- The frozen clause was not reinterpreted.

## What was run

Single thread, `nice -n 10`, load 0.2 to 1.06 recorded per solve.
- One C binary, `ic.c`, with a shared Montgomery field and affine group law. t_GAE is 12.7 to 17 ns.
- Every solve verified by [k]G = Q.
- rho: 3 curves × 5 targets, Weierstrass (W) and twisted-Edwards (E) families, k = 20..40 in steps of 2.
- IC-pair: W curves, k = 20..40, 15 solves per size.
- IC-lattice-W: k = 22..32. IC-lattice-E: k = 20..32. B is the planted 50% recovery point, calibrated per curve. 3 to 15 solves per size, 3 at k = 32.
- IC-coppersmith-E (arm 5) was modelled, not run end to end. Measured: LLL alone 0.30 ms per call (dim 13); planted recovery 20/20, 20/20, 19/20, 12/20 at δ = 0.10, 0.12, 0.14, 0.16 on a 32-bit prime. Modelled total ≥ 5.6e5 × rho at k = 20 and ≥ 3.7e8 × at k = 40, about 350× slower than the form-lattice-E arm at the same size.

## Results

### α (95% two-level bootstrap CI, π = 0, i.e. counted group additions)

| arm | sizes | α |
|---|---|---|
| rho W | k ≥ 28 | 0.52 [0.47, 0.56] |
| rho W | k = 20..40 | 0.46 [0.44, 0.48] |
| rho E | k = 20..40 | 0.48 [0.46, 0.50] |
| IC-pair | k ≥ 28 | 0.65 [0.64, 0.67] |
| IC-pair | k = 20..40 | 0.65 [0.63, 0.66] |
| IC-lattice-W | k = 22..32 | 0.86 [0.80, 0.92] |
| IC-lattice-E | k = 20..32 | 0.83 [0.76, 0.90] |

- The IC-pair α is 0.57 to 0.72 across pricings.
- The lattice α values are identical across pricings because their cost is the wall-priced oracle.
- Rho at π = 1 and in total wall is flattened by fixed setup cost at small k.
- Predictions: rho 0.50 ± 0.03 holds at k ≥ 28. IC-pair near 2/3 holds. Lattice arms are at or above 0.85 for W; for E the point estimate is 0.83 with the CI containing 0.85.

### Ratio to rho (mean cost)

IC-pair:

| k | π = 0 | π = 1 | total wall |
|---|---|---|---|
| 20 | 5.3 | 1.1 | 2.4 |
| 24 | 9.3 | 1.1 | 4.2 |
| 28 | 19.5 | 2.7 | 12 |
| 32 | 33 | 11 | 42 |
| 36 | 49 | 41 | 136 |
| 40 | 57 | 88 | 147 |

IC-lattice-W, π = 0 (π = 1 in brackets): k = 24: 2.3e4 (819); k = 28: 1.6e5 (8.6e3); k = 32: 2.8e5 (4.1e4). k = 22 and 26 are in results/analysis.md; k = 20 was not run.

IC-lattice-E, π = 0 (π = 1 in brackets): k = 20: 1.4e4 (438); k = 24: 3.9e4 (1.4e3); k = 28: 1.3e5 (6.9e3); k = 32: 4.2e5 (6.4e4).

Lattice sizes 34 to 40 are model only: wall ratio about 6e5 at k = 36 and 2.1e6 to 2.2e6 at k = 40.

### Phase breakdown at the largest size

- IC-pair, k = 40, mean wall 5.09 s against 0.036 s for rho: setup 36.5% (a 2.66e7-entry pair table), collection 21%, hash lookups 41%, linear algebra 0.05%, final [k]G = Q check 1.2 ms.
- IC-lattice-W, k = 32, 358 s: collection 3.5%, lattice oracle 96.3% (596 ns per attempt over 5.8e8 attempts), linear algebra about 10 μs.
- IC-lattice-E, k = 32, 559 s: collection 2.3%, oracle 97.6% (850 ns per attempt), linear algebra about 12 μs.
- Linear algebra is negligible everywhere. The descent phase is only the final check; Q is placed in every relation, which favours IC (DEVIATIONS item 2).

### Other findings

- At its own 50% reach the lattice oracle works with a factor base of only 3 to 40 points, so a pair table with the same base would answer each attempt in a lookup. The oracle costs 50 to 65 times a group addition per attempt, and the hit probability does not improve.
- Edwards against Weierstrass is a constant factor: wall time E/W is 2.0, 1.8, 0.77, 0.74, 1.1, 1.6 at k = 22..32, with no trend.

## Limitations and caveats

- The lattice arms were measured only up to k = 32. Several lattice calibration cells have no admissible B (5 of 18 W curve-size pairs).
- Pair-arm wall times at k ≥ 34 are memory-bound and carry host noise; timings at k ≤ 24 are sub-millisecond.
- A large setup overhead in rho was fixed and all rho rows re-run. One censored latE k = 32 solve was re-run with the same seed and a larger cap; it completed in 839 s.

**What would decide the letter:** a rerun at k ≤ 24 with setup cost below noise, or a pricing rule that excludes the sub-millisecond setup.

## Suggested lead-atlas update

End-to-end IC with decomposition oracles is killed for solve time, with no further action. Deciding number: IC-pair at k = 40 is 57 to 147 times rho, α 0.65 against rho's 0.52. Reopen only for an oracle that reaches beyond p^(1/3) at a per-call cost within a small multiple of one group addition.

## Files

DEVIATIONS.md; results/analysis.md (full tables and CIs); results/summary.json; results/rho.jsonl, pair.jsonl, lat.jsonl, calib.jsonl, lat_rerun_E32.jsonl; fig_sa21.png; ic.c, analyze.py, gen_curves.py, run_rho.sh, run_pair.sh, run_lat.py, run_lat2.py; cop/ (Coppersmith measurement); curves.json.
