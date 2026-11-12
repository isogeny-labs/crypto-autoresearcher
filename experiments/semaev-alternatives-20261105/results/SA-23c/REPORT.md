# SA-23c REPORT: held-out test of the post-hoc Frobenius law, and enumeration at p = 229

## Verdict: SUCCESS

- RJ: 0 exceptions in 17,190 held-out primes (1e5 < p < 1e6).
- L48: 0 exceptions (0.000%, limit 0.1%).
- p = 229: Gram rank 8 (in {7,8}), S = 224, as required.
- Frozen protocol file SHA-256 5aa86e98...a4938e4 and table SHA-256 d7391376...e888a verified before use.

## Part 1: held-out law test

- Re-run of p < 1e5 with src/jac.py (canonical mode, unchanged; copy of the SA-23b file): 2374 primes, output byte-identical to SA-23b jacobi.jsonl (same SHA-256 c4ab8016...c72).
- Held-out set: all p = 1 mod 12 with 100057 <= p <= 999961, n = 17,190, exact Z[zeta12] arithmetic.

| Check | Result |
|---|---|
| |J|^2 = p^2 exactly, all 20 pieces | 17190 / 17190 primes |
| exactly 16 root-of-unity pieces | 17190 / 17190 primes |
| L48 exact 20-exponent string | 0 exceptions |
| RJ closed form for R_J | 0 exceptions |
| R_J implied by the L48 string = actual R_J | 0 exceptions |

No exceptions exist to list. Every L48 cell was in the table.

R_J frequencies (bootstrap 2000 resamples, seed 23, 95% CI):

| R_J | count | fraction | CI | frozen target | target inside CI |
|---|---|---|---|---|---|
| 4 | 8610 | 0.5009 | 0.4929 to 0.5086 | 1/2 | yes |
| 8 | 4264 | 0.2481 | 0.2414 to 0.2546 | 1/4 | yes |
| 12 | 2866 | 0.1667 | 0.1607 to 0.1724 | 1/6 | yes |
| 16 | 1450 | 0.0844 | 0.0802 to 0.0885 | 1/12 | yes |

No other R_J value occurs.

## Part 2: enumeration at (229, 12)

- Jacobi sum: R_J(229) = 8 (agrees with the RJ prediction of 8).
- enum_r.c unchanged (identical to the SA-23b source, recompiled), 24 leading-coefficient ranges plus the fallback chunk, at most two concurrent, nice -n 10.
- 25 chunks completed, all rc = 0, longest 2283 s, total 35,276 CPU-s (9.8 core-h), host load at chunk start 1.2 to 3.3 (shared). No timings enter any result.

| p | S (signed) | Gram rank | lattice determinant | min height | R_J |
|---|---|---|---|---|---|
| 229 | 224 | 8 | 256 | 4 | 8 |
| 109 (SA-23b) | 224 | 8 | 256 | 4 | 8 |

- verify_sections.py (independent): 112 listed sections, 0 equation or degree failures, 224 distinct signed sections, Gram rank 8, off-diagonal inner products in {-4,-2,0,2}.
- The prediction that S depends only on R_J holds at both R_J = 8 cells.

## Flagged readings and limitations

- Both laws were fitted on p < 1e5 and tested on 17,190 unseen primes in one pass; there was no refitting and no second look.
- RJ and L48 are verified numerically up to 1e6, not proved. The Gram rank equals R_J here (rank 8), unlike the rank 3 at R_J = 4 cells; that is consistent with the SA-23b reading but nothing new was tested about non-integral generators.
- "S depends only on R_J" rests on two R_J = 8 cells (109, 229) and, from SA-23b, one cell each at R_J = 12 and 16; rank-4 cells all had S = 8.
- Enumeration covers integral sections of the stated shape only.
- Chunk 229_10_19 was killed when I freed a CPU slot for Part 1 and rerun; see DEVIATIONS.md.
- This concerns the surface y^2 = x^3 + t^12 + 1 only. SA-23's ECDLP verdict covers every prime and does not depend on it.

## Suggested lead-atlas line

SA-23c (2026-11-12): held-out test of the post-hoc law for MW rank of y^2=x^3+t^12+1 over F_p(t), p = 1 mod 12: R_J = 4 + 4[2 cube] + 8[3|b and ((a=1 mod 3) != (p=5 mod 8))] and the 48-cell (a,b mod 3; (2/p)_3,(2/p)_4) exponent table have 0 exceptions in 17,190 primes 1e5 < p < 1e6; R_J frequencies 1/2, 1/4, 1/6, 1/12 within 95% CIs. Enumeration at p = 229: S = 224, Gram rank 8, det 256, same as p = 109 (S depends on R_J only). SUCCESS (surface only; no ECDLP consequence).
