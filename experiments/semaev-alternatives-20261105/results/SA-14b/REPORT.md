# SA-14b: PKM tower F4 degree at t = 10 (and m = 3)

## Summary
**Verdict: KILL** against the frozen criterion. At t = 10 (m = 2, q = 2) the msolve F4 degree is 6 on all 3 seeds, and the matched random-support null also gives 6 (identical largest matrix, 73315 rows). The frozen prediction 4 + floor((t-2)/4) = 6 is confirmed. SUCCESS (degree 5 at t = 10, 11, 12) is excluded at t = 10. t = 11, 12 were not run (DEVIATIONS 1); the KILL clause does not need them.

## What was run
Scripts: `drv.py` (SA-14 encoding via `msolve_sd.py`, `kummer_sd.py` copied from SA-14, msolve -g 2 -v 2 -t 1, nice 10, RLIMIT_AS 2.2 GB), `drv3.py` (m = 3 via S_4 resultant, and support-matched null), `chain1.sh`, `chain2.sh`. p = 12289, q = 2. Raw: `out/t10_all.jsonl`, `out/null_m2.txt`, `out/m3.txt`, `out/m3_null.txt`, `out/log_*.txt`. Figure: `fig_f4_degree_b.png`.

## Results
| cell | seeds | F4 degree | largest matrix rows | wall |
|---|---|---|---|---|
| m=2 t=10 planted | 1,2,3 | 6,6,6 | 73315 (all) | 762 / 687 / 499 s |
| m=2 t=10 null (random coeffs, same support) | 1 | 6 | 73315 | 448 s |
| m=2 t=9 (SA-14) | 1 | 5 | 23644 | 412 s |

Rows grow x3.1 from t=9 to t=10 (x2.1 earlier); peak RSS about 0.66 GB.

m = 3 (q = 2, S_4 reduced mod tower, planted, 2 seeds; identical across seeds in degree):
| t | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| F4 degree | 4 | 7 | 7 | 7 | 7 |
| max rows | 22 | 267 | 2206-2244 | 16140 | 62138 |
| null (1 seed) degree | 4 | 7 | 7 | 7 | not run |
| null rows | 22 | 267 | 2427 | 15073 | |

The repository's m=3 medians (5,6,6,7 for t=1..4) differ from mine (4,7,7,7); different encoding, so no direct comparison is claimed. Within t <= 5 the m=3 degree is flat at 7, with no step visible, and rows x3.8 per level at t=5, comparable with m=2 near t=10. The scale is too small to read a slope for m=3.

## Verdict reasoning
KILL = degree 6 at t=10 on all seeds (3/3) and null matches the real tower degree (6 = 6, also same matrix size). Both hold. Note the null matching means the degree is set by the tower-ideal structure plus a generic quadratic, not by anything Semaev-specific; this supports the "no special structure to exploit" reading but it also means the degree step 5 -> 6 occurs on schedule (steps at t = 2, 6, 10: period 4, slope 1/4).

## Limitations
One null seed, only at t=10. t=11, 12 not run, so the next step (predicted 6 through t=13, then 7 at t=14) is unobserved; a 4-periodic step pattern rests on three steps (t=2, 6, 10). m=3 only to t=5 with no t=6 and no t=5 null; own S_4 encoding. Break-even note from SA-14 (slope 1/4 loses to rho for q=2, m<=4 in the dense model) stands.

## Suggested lead-atlas update
LEAD-ICP-pkm-tower-algebraic-oracle: disposition toward closed/negative for the m=2, q=2 Kummer tower under F4. Deciding number: msolve F4 degree 6 at t=10 on 3/3 seeds, null also 6, largest matrix 73315 rows (x3.1 over t=9), confirming the 4+floor((t-2)/4) fit with steps at t=2,6,10 (slope 1/4). m=3 flat at 7 for t=2..5 (inconclusive on slope). Remaining open: only a polynomial-calculus degree argument or q>2/m>=4 cells where the dense break-even model allows slope 1/4.
