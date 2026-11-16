# SA-05b REPORT: Kummer ladders with the global floor subtracted

## Summary
**Verdict: KILL.** Corrected ratio (wrapped relations / generic expectation) is 0.84, 0.95, 0.90 at p ~ 2^32, 2^36, 2^40, inside [0.8, 1.25] at every p; slope in log2 p = 0.008 (95% bootstrap CI -0.011 to 0.033), so no growth. Random-target yield / generic = 0.98 to 1.01 (struct/control 0.997-1.022, CIs include 1), not above generic.

## What was run
- Reused SA-05 conclusion (global relations ~ C(h), flat in p); no SA-05 cell recomputed.
- New `sumset2.cpp` + `run2.py`: for each of 4 primes p = 3 mod 4 just above 2^32, 2^36, 2^40, structured base (x = a/b, |a|,b <= h on the curve) with B = 5 p^(1/3) (h = 116, 182-184, 292; B = 8.3k, 20.6k, 52k), a random base and an integer base of equal B. All B(B-1) sums x(P+-Q) streamed; hits in base = 3-in-base relations (deduplicated as unordered triples), classified global (S_3 = 0 over Q, exact) or wrapped. Same stream counts hits of 10^5 random targets (distinct targets), each recomputed by group addition in Python.
- `analyze.py` -> results.json, table_main.md, fig_ratio.png.

## Results
| k | h | B | primes | wrapped | global | generic E | wrapped/E (Poisson 95%) | random ctrl/E | integer/E | target hits struct/ctrl/int | target struct/ctrl (95%) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 32 | 116 | 8256 | 4 | 292 | 42 | 349.3 | 0.836 (0.74-0.94) | 0.93 | 1.00 | 12506/12518/12558 | 0.999 (0.98-1.02) |
| 36 | 182 | 20611 | 4 | 322 | 56 | 339.7 | 0.948 (0.85-1.06) | 1.05 | 0.92 | 4996/4889/4823 | 1.022 (0.99-1.05) |
| 40 | 292 | 51955 | 4 | 306 | 109 | 340.1 | 0.900 (0.80-1.01) | 1.11 | 1.11 | 1932/1938/1996 | 0.997 (0.95-1.04) |

Target yield / analytic generic: 1.01 (2^36), 0.98 (2^40); 2^32 within 1%. All target hits verified (0 failures). Raw: `main.jsonl`, `raw/`. Figure: `fig_ratio.png`.

## Verdict reasoning
KILL needs the ratio in [0.8, 1.25] at every p (point estimates 0.84, 0.95, 0.90: yes) and random-target yield not above generic (1.0: yes). SUCCESS needs ratio > 1.25 or yield > 2x: neither. With the global floor removed (it rises with h: 42, 56, 109 total, as expected), nothing remains. A mild deficit (~0.9, struct/ctrl 0.81 at 2^40) is the wrong sign for a gain.

## Limitations
- Only three p, 4 primes each; the 2^32 Poisson CI (0.74-0.94) lies partly below 0.8, judged on point estimates as the criterion is written. Deficit may be real (collisions among sums) but is not a benefit.
- Filter-based arm not usable at this scale (Deviations 1); 2^48/2^56 filter result is SA-05's (0 passes).
- Toy scale p <= 2^40; nothing about 256 bits. Base is small-height only; other ladder-closed bases untested.

## Suggested lead-atlas update
LEAD-ICP-kummer-ladder-height-closure: disposition `closed_no_ic_value` (confirmed, no longer pending criterion review). With global relations subtracted and B = 5 p^(1/3), wrapped relations equal the generic count (ratio 0.84/0.95/0.90 at 2^32/2^36/2^40, slope 0.008 CI -0.011..0.033) and random-target yield equals generic (0.98-1.01). Same reasoning closes LEAD-TRF-global-lift-small-height unless it supplies a base with many points per twist class. No next action.
